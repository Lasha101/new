// Authentication through the real login form: the browser fills the same inputs
// a user does and posts to the same endpoint. Only the server behind it changes
// between mocked and live runs.
import { expect } from '@playwright/test';
import { SELECTORS, TEXT } from './selectors.js';
import { APP_BASE } from './appBase.js';

/** How long to wait out the server's login throttle before trying again. */
const RATE_LIMIT_WINDOW_MS = Number(process.env.E2E_LOGIN_RETRY_MS || 62_000);

/** Credentials, from the environment so no password is committed. */
export function credentials() {
    return {
        username: process.env.E2E_USERNAME || 'alice',
        password: process.env.E2E_PASSWORD || 'test-password',
    };
}

/**
 * Logs in and waits for the dashboard.
 *
 * @param {import('@playwright/test').Page} page
 * @param {{username?:string, password?:string, expectFailure?:boolean, retries?:number}} [options]
 *   `expectFailure: true` submits and returns as soon as the form settles,
 *   without waiting for a dashboard — for the bad-credentials test.
 *
 * POST /token is rate limited to 5 per minute per IP (backend/main.py), which a
 * live suite hits within a couple of specs. When the app shows that message this
 * helper waits the window out and submits again, instead of reporting a
 * throttled run as a broken login. It never triggers against the mock.
 */
export async function login(page, options = {}) {
    const { username, password } = { ...credentials(), ...options };
    const retries = options.retries ?? 2;

    if (!page.url().startsWith('http')) await page.goto(APP_BASE);
    await expect(page.locator(SELECTORS.loginForm)).toBeVisible();

    await page.getByPlaceholder(TEXT.usernamePlaceholder).fill(username);
    await page.getByPlaceholder(TEXT.passwordPlaceholder).fill(password);

    const dashboard = page.locator(SELECTORS.creditBadge);
    const throttled = page.locator(SELECTORS.errorMessage).filter({ hasText: TEXT.rateLimited });

    for (let attempt = 0; ; attempt++) {
        await page.getByRole('button', { name: TEXT.loginSubmit }).click();

        if (options.expectFailure) {
            // The button re-enables when the request settles, success or failure.
            await expect(page.getByRole('button', { name: TEXT.loginSubmit })).toBeEnabled();
        } else {
            await expect(dashboard.or(throttled).first()).toBeVisible({ timeout: 20_000 });
            if (await dashboard.count() > 0) return;
        }

        // A throttled attempt says nothing about the credentials, so it is not a
        // result either way: wait the window out and submit again.
        if (await throttled.count() === 0) return;
        if (attempt >= retries) {
            throw new Error(
                `login: rate limited after ${attempt + 1} attempt(s). POST /token allows 5 per minute `
                + 'per IP; run live suites with --workers=1, or fewer specs per minute.',
            );
        }
        await page.waitForTimeout(RATE_LIMIT_WINDOW_MS);
    }
}

/** Logs out through the header button and waits for the login form. */
export async function logout(page) {
    await page.getByRole('button', { name: TEXT.logout }).click();
    await expect(page.locator(SELECTORS.loginForm)).toBeVisible();
}

/**
 * The session token as JAVASCRIPT can see it — which, since package C, is
 * nothing at all.
 *
 * The JWT lives in an HttpOnly cookie now, so `document.cookie` and
 * `localStorage` both come back empty by design. This helper keeps its name
 * and its contract ("what a script on this page could steal") and therefore
 * returns null on a healthy session: that is the security property, and the
 * specs assert it.
 *
 * Use `hasSessionCookie(page)` to ask whether a session actually exists.
 */
export async function storedToken(page) {
    return page.evaluate(() => {
        const stored = window.localStorage.getItem('token')
            || window.sessionStorage.getItem('token');
        if (stored) return stored;
        // document.cookie cannot see an HttpOnly cookie; this is here so a
        // regression that dropped the flag would be caught rather than pass.
        const readable = document.cookie
            .split(';')
            .map(part => part.trim())
            .find(part => part.startsWith('scanid_session='));
        return readable ? readable.slice('scanid_session='.length) : null;
    });
}

/** Whether the browser holds the session cookie, HttpOnly included. */
export async function hasSessionCookie(page) {
    const cookies = await page.context().cookies();
    return cookies.some(cookie => cookie.name === 'scanid_session' && cookie.value);
}

/** The session cookie itself, for asserting on its flags. */
export async function sessionCookie(page) {
    const cookies = await page.context().cookies();
    return cookies.find(cookie => cookie.name === 'scanid_session') || null;
}

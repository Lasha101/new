// Authentication through the real login form: the browser fills the same inputs
// a user does and posts to the same endpoint. Only the server behind it changes
// between mocked and live runs.
import { expect } from '@playwright/test';
import { SELECTORS, TEXT } from './selectors.js';

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

    if (!page.url().startsWith('http')) await page.goto('/');
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

/** The JWT the app stored, or null. */
export async function storedToken(page) {
    return page.evaluate(() => window.localStorage.getItem('token'));
}

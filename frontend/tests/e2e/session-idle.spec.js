// Automatic logout after 12 hours of inactivity (action list item 9).
// The server side — a 12 h session renewed only by POST /session/refresh, and
// refused once expired — is proven in backend/tests/test_session_idle.py.
// Here: the app renews on real activity only, and returns to the login screen
// once 12 h have passed without any.
import { test, expect, LIVE } from './test-base.js';
import { login, SELECTORS } from '../helpers/index.js';

const refreshes = api => api.requests.filter(r => r.method === 'POST' && r.path === '/session/refresh').length;
const userChecks = api => api.requests.filter(r => r.method === 'GET' && r.path === '/users/me').length;

test.describe('Déconnexion automatique après 12 h d’inactivité', () => {
    test.skip(LIVE, 'avance l’horloge et pilote la session du mock');

    test('après 12 h sans activité, l’écran de connexion annonce « Votre session a expiré »', async ({ page, context, api }) => {
        await page.clock.install();
        await login(page);
        await expect(page.locator(SELECTORS.uploadCard)).toBeVisible();

        // Twelve hours later the server has let the session expire.
        api.session = false;
        await context.clearCookies({ name: 'scanid_session' });
        await page.clock.fastForward('11:59:00');
        await expect(page.locator(SELECTORS.uploadCard)).toBeVisible();
        await page.clock.fastForward('02:00');

        await expect(page.locator(SELECTORS.loginForm)).toBeVisible();
        await expect(page.locator(SELECTORS.sessionExpired)).toContainText('Votre session a expiré');
    });

    test('l’activité renouvelle la session, au plus toutes les 5 minutes, et garde l’utilisateur connecté', async ({ page, api }) => {
        await page.clock.install();
        await login(page);
        await expect(page.locator(SELECTORS.uploadCard)).toBeVisible();

        await page.keyboard.press('Shift');
        await expect.poll(() => refreshes(api)).toBe(1);
        await page.keyboard.press('Shift');                 // within 5 minutes: no second renewal
        await page.clock.fastForward('05:00');
        await page.keyboard.press('Shift');
        await expect.poll(() => refreshes(api)).toBe(2);

        // Used again after 11 h, then 2 h without activity: 13 h after login,
        // but only 2 h idle — the app does not even ask whether the session is over.
        await page.clock.fastForward('11:00:00');
        await page.locator(SELECTORS.uploadCard).dispatchEvent('pointerdown');
        await expect.poll(() => refreshes(api)).toBe(3);
        const checksBefore = userChecks(api);
        await page.clock.fastForward('02:00:00');
        await page.clock.runFor(60_000);
        await expect(page.locator(SELECTORS.uploadCard)).toBeVisible();
        await expect(page.locator(SELECTORS.sessionExpired)).toHaveCount(0);
        expect(userChecks(api)).toBe(checksBefore);
    });

    test('« Déconnexion » l’emporte sur le renouvellement que ce même clic déclenche', async ({ page, api }) => {
        await login(page);
        await expect(page.locator(SELECTORS.uploadCard)).toBeVisible();
        // The click on « Déconnexion » is the first activity: it sends a renewal,
        // answered slowly here, alongside the logout. The renewal must not win.
        api.refreshDelayMs = 800;
        const answered = Promise.all([
            page.waitForResponse(r => r.url().endsWith('/session/refresh')),
            page.waitForResponse(r => r.url().endsWith('/logout')),
        ]);
        await page.getByRole('button', { name: 'Déconnexion' }).click();
        await expect(page.locator(SELECTORS.loginForm)).toBeVisible();
        await answered;                                      // both answers are in, whatever their order
        expect(refreshes(api)).toBe(1);

        await page.reload();
        await expect(page.locator(SELECTORS.loginForm)).toBeVisible();
        await expect(page.locator(SELECTORS.uploadCard)).toHaveCount(0);
    });
});

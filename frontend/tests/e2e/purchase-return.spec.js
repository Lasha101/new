// Back from Stripe after an « à la carte » payment (Alex, 06/10/2026): the unit
// link's « After payment » redirects to /app/?achat=unite, and the login screen
// says what comes next — a first purchase has no password yet, its link is in
// the welcome e-mail. The marker is read once and leaves the address bar.
import { test, expect, LIVE } from './test-base.js';
import { login, logout, SELECTORS, APP_BASE } from '../helpers/index.js';

const BACK_FROM_STRIPE = `${APP_BASE}?achat=unite`;

test.describe('Retour de Stripe après un achat à l’unité', () => {
    test('un visiteur non connecté voit le message, le formulaire, et une adresse nettoyée', async ({ page }) => {
        await page.goto(BACK_FROM_STRIPE);
        const notice = page.locator(SELECTORS.purchaseReturn);
        await expect(notice).toBeVisible();
        await expect(notice).toContainText('Paiement reçu, merci !');
        await expect(notice).toContainText('Vos documents sont ajoutés à votre espace ScanID.');
        await expect(notice).toContainText('Premier achat ? Un e-mail de devis@scanid.fr vous est envoyé avec le lien pour choisir votre mot de passe');
        await expect(notice).toContainText('pensez à regarder dans vos courriers indésirables');
        await expect(notice).toContainText('Déjà client ? Connectez-vous ci-dessous.');
        await expect(notice).toHaveAttribute('role', 'status');
        await expect(page.locator(SELECTORS.loginForm)).toBeVisible();
        await expect(page.locator(SELECTORS.sessionExpired)).toHaveCount(0);
        await expect.poll(() => new URL(page.url()).search).toBe('');
        expect(new URL(page.url()).pathname).toBe(APP_BASE);
    });

    test('sans le marqueur, l’écran de connexion reste tel quel', async ({ page }) => {
        await page.goto(APP_BASE);
        await expect(page.locator(SELECTORS.loginForm)).toBeVisible();
        await expect(page.locator(SELECTORS.purchaseReturn)).toHaveCount(0);
        await page.goto(`${APP_BASE}?achat=pack`);
        await expect(page.locator(SELECTORS.loginForm)).toBeVisible();
        await expect(page.locator(SELECTORS.purchaseReturn)).toHaveCount(0);
    });

    test('après la connexion le message disparaît ; une déconnexion ne le ramène pas', async ({ page }) => {
        await page.goto(BACK_FROM_STRIPE);
        await expect(page.locator(SELECTORS.purchaseReturn)).toBeVisible();
        await login(page);
        await expect(page.locator(SELECTORS.uploadCard)).toBeVisible();
        await logout(page);
        await expect(page.locator(SELECTORS.purchaseReturn)).toHaveCount(0);
    });

    test('un client déjà connecté (le lien de l’application) arrive sur son tableau de bord', async ({ page }) => {
        await login(page);
        await page.goto(BACK_FROM_STRIPE);
        await expect(page.locator(SELECTORS.uploadCard)).toBeVisible();
        await expect(page.locator(SELECTORS.purchaseReturn)).toHaveCount(0);
        await expect.poll(() => new URL(page.url()).search).toBe('');
    });

    test('une session expirée : le message d’achat remplace « Votre session a expiré »', async ({ page }) => {
        test.skip(LIVE, 'simule la fin de session par le mock');
        await login(page);
        await page.route(url => url.pathname.endsWith('/users/me'), route => route.fulfill({
            status: 401, contentType: 'application/json',
            body: JSON.stringify({ detail: "Impossible de valider les informations d'identification" }),
        }));
        await page.goto(BACK_FROM_STRIPE);
        await expect(page.locator(SELECTORS.loginForm)).toBeVisible();
        await expect(page.locator(SELECTORS.purchaseReturn)).toBeVisible();
        await expect(page.locator(SELECTORS.sessionExpired)).toHaveCount(0);
    });
});

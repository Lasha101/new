// « Mot de passe oublié ? » and the page a password link opens
// (/app/mot-de-passe#token=…). The email itself is proven server-side
// (backend/tests/test_password_reset.py); here, what the person sees and does.
import { test, expect, LIVE } from './test-base.js';
import { SELECTORS, TEXT, APP_BASE } from '../helpers/index.js';

const NEW_PASSWORD = 'Girafe!!12Nuage';

test.describe('Mot de passe oublié', () => {
    test.skip(LIVE, 'pilote le lien valide du mock ; le parcours réel est prouvé contre le vrai backend');

    test('le lien de la page de connexion mène au formulaire, qui répond sans rien révéler', async ({ page, api }) => {
        await page.goto(APP_BASE);
        await expect(page.locator(SELECTORS.loginForm)).toBeVisible();
        await page.getByRole('button', { name: 'Mot de passe oublié ?' }).click();

        await expect(page.getByRole('heading', { name: 'Mot de passe oublié' })).toBeVisible();
        await page.getByLabel("Email ou nom d'utilisateur").fill('alice@example.com');
        await page.getByRole('button', { name: 'Recevoir le lien' }).click();

        await expect(page.locator('.sid-alert--ok')).toHaveText(/Le lien est valable 48 heures\./);
        expect(api.forgotPasswordRequests).toEqual(['alice@example.com']);

        await page.getByRole('button', { name: 'Retour à la connexion' }).click();
        await expect(page.locator(SELECTORS.loginForm)).toBeVisible();
    });

    test('le lien reçu permet de choisir un mot de passe puis de se connecter avec', async ({ page }) => {
        await page.goto(`${APP_BASE}mot-de-passe#token=jeton-valide-de-test`);
        await expect(page.getByRole('heading', { name: 'Choisir votre mot de passe' })).toBeVisible();
        // The token is read once and removed from the address bar.
        await expect.poll(() => new URL(page.url()).hash).toBe('');

        const [first, second] = await page.locator('.sid-password-page input[type="password"]').all();
        await first.fill(NEW_PASSWORD);
        await second.fill(`${NEW_PASSWORD}x`);
        await page.getByRole('button', { name: 'Enregistrer le mot de passe' }).click();
        await expect(page.locator('.sid-alert--err')).toHaveText('Les deux mots de passe ne correspondent pas.');

        await second.fill(NEW_PASSWORD);
        await page.getByRole('button', { name: 'Enregistrer le mot de passe' }).click();
        await expect(page.locator('.sid-alert--ok')).toContainText('Votre mot de passe est enregistré');
        await page.getByRole('button', { name: 'Se connecter' }).click();

        await expect(page).toHaveURL(new RegExp(`${APP_BASE}$`));
        await expect(page.getByPlaceholder(TEXT.usernamePlaceholder)).toHaveValue('alice');
        await page.getByPlaceholder(TEXT.passwordPlaceholder).fill(NEW_PASSWORD);
        await page.getByRole('button', { name: TEXT.loginSubmit }).click();
        await expect(page.locator(SELECTORS.creditBadge)).toBeVisible();
    });

    test('un lien expiré ou déjà utilisé propose d’en demander un nouveau', async ({ page }) => {
        await page.goto(`${APP_BASE}mot-de-passe#token=jeton-perime`);
        const [first, second] = await page.locator('.sid-password-page input[type="password"]').all();
        await first.fill(NEW_PASSWORD);
        await second.fill(NEW_PASSWORD);
        await page.getByRole('button', { name: 'Enregistrer le mot de passe' }).click();

        await expect(page.locator('.sid-alert--err')).toContainText("n'est plus valide");
        await page.getByRole('button', { name: 'Demander un nouveau lien' }).click();
        await expect(page.getByRole('heading', { name: 'Mot de passe oublié' })).toBeVisible();
        await expect(page).toHaveURL(new RegExp(`${APP_BASE}$`));
    });

    test('une adresse sans jeton annonce tout de suite un lien invalide', async ({ page }) => {
        await page.goto(`${APP_BASE}mot-de-passe`);
        await expect(page.locator('.sid-alert--err')).toContainText("Ce lien n'est pas valide");
    });
});

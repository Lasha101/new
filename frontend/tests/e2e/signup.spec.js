// /app/inscription?pack=… — account before payment (Spec v3). Crediting by the
// Stripe webhook is proven server-side (backend/tests/test_pack_purchase.py);
// here, the page: summary, form, and the redirect to the pack's Payment Link.
import { test, expect, LIVE } from './test-base.js';
import { login, credentials, SELECTORS, TEXT, APP_BASE } from '../helpers/index.js';

const STRONG = 'Girafe!!12Nuage';
const LINK_1000 = 'https://buy.stripe.com/8x27sK0rtbFi8Apgvbebu01';
const LINK_100 = 'https://buy.stripe.com/9B64gy8XZfVycQFdiZebu00';

/** Stops at Stripe's door: the navigation is recorded, never sent. */
async function captureCheckout(page) {
    await page.route('https://buy.stripe.com/**', route => route.fulfill({ status: 200, contentType: 'text/html', body: '<title>Stripe (stub)</title>' }));
}

const validSiret = () => ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    .map(d => `7328293200007${d}`)
    .find((candidate) => {
        let total = 0;
        [...candidate].reverse().forEach((c, i) => { let n = Number(c); if (i % 2) { n *= 2; if (n > 9) n -= 9; } total += n; });
        return total % 10 === 0;
    });

async function fillSignup(page, overrides = {}) {
    const values = {
        Prénom: 'Claire', Nom: 'Achat', 'Société / agence': 'Agence Test Voyages', 'Email professionnel': 'claire@agence-test.fr',
        Téléphone: '+33 1 00 00 00 00', Rue: "1 rue de l'Essai", 'Code postal': '75001', Ville: 'Paris',
        SIRET: validSiret(), 'N° de TVA intracommunautaire (facultatif)': 'FR12345678901', ...overrides,
    };
    for (const [label, value] of Object.entries(values)) await page.getByLabel(label, { exact: true }).fill(value);
    await page.getByLabel('Mot de passe', { exact: true }).fill(STRONG);
    await page.getByRole('checkbox').check();
}

test.describe('Inscription avant paiement', () => {
    test.skip(LIVE, 'le mock simule /signup et intercepte Stripe');

    test('le résumé du pack, le formulaire, puis Stripe avec l’email et l’identifiant', async ({ page, api }) => {
        await captureCheckout(page);
        await page.goto(`${APP_BASE}inscription?pack=1000`);

        const summary = page.locator('.sid-pack-summary');
        await expect(summary.getByRole('heading')).toHaveText('Pack 1 000');
        await expect(summary).toContainText('690,00 €');
        await expect(summary).toContainText('138,00 €');
        await expect(summary).toContainText('828,00 €');
        await expect(summary).toContainText('0,69 € HT le scan');
        await expect(page.getByLabel('Pays', { exact: true })).toHaveValue('France');

        await fillSignup(page, { SIRET: '12345678901234' });
        await page.getByRole('button', { name: 'Créer mon compte et payer' }).click();
        await expect(page.locator('.sid-alert--err')).toHaveText('Le SIRET doit comporter 14 chiffres valides.');
        expect(api.signups).toBeUndefined();                  // refused before any request

        await page.getByLabel('SIRET', { exact: true }).fill(validSiret());
        await page.getByRole('button', { name: 'Créer mon compte et payer' }).click();
        await page.waitForURL(url => url.href.startsWith(LINK_1000));

        const url = new URL(page.url());
        expect(url.searchParams.get('prefilled_email')).toBe('claire@agence-test.fr');
        expect(url.searchParams.get('client_reference_id')).toBe('u-new');
        expect(api.signups).toHaveLength(1);
        expect(api.signups[0]).toMatchObject({ pack: 1000, company: 'Agence Test Voyages', billing_city: 'Paris', consent: true });
    });

    test('un pack inconnu n’affiche pas de formulaire', async ({ page }) => {
        await page.goto(`${APP_BASE}inscription?pack=250`);
        await expect(page.getByRole('heading', { name: "Ce pack n'existe pas." })).toBeVisible();
        await expect(page.getByRole('link', { name: 'scanid.fr/#tarifs' })).toHaveAttribute('href', 'https://scanid.fr/#tarifs');
        await expect(page.getByRole('button', { name: 'Créer mon compte et payer' })).toHaveCount(0);
    });

    test('un client déjà connecté va directement au paiement', async ({ page, api }) => {
        await captureCheckout(page);
        await login(page);
        await page.goto(`${APP_BASE}inscription?pack=100`);
        await expect(page.getByText(`Vous êtes connecté en tant que ${api.user.user_name}.`)).toBeVisible();
        await page.getByRole('button', { name: 'Continuer vers le paiement' }).click();
        await page.waitForURL(url => url.href.startsWith(LINK_100));
        const url = new URL(page.url());
        expect(url.searchParams.get('prefilled_email')).toBe(api.user.email);
        expect(url.searchParams.get('client_reference_id')).toBe(api.user.id);
    });

    test('« Déjà client ? Se connecter » ramène au pack une fois connecté', async ({ page }) => {
        await page.goto(`${APP_BASE}inscription?pack=3000`);
        await page.getByRole('button', { name: 'Déjà client ? Se connecter' }).click();
        await expect(page.locator(SELECTORS.loginForm)).toBeVisible();
        // By hand: login() waits for the dashboard, and this login must NOT land there.
        const { username, password } = credentials();
        await page.getByPlaceholder(TEXT.usernamePlaceholder).fill(username);
        await page.getByPlaceholder(TEXT.passwordPlaceholder).fill(password);
        await page.getByRole('button', { name: TEXT.loginSubmit }).click();
        await expect(page.locator('.sid-pack-summary').getByRole('heading')).toHaveText('Pack 3 000');
        await expect(page.getByRole('button', { name: 'Continuer vers le paiement' })).toBeVisible();
        await page.getByRole('button', { name: 'Retour à mon espace' }).click();
        await expect(page.locator(SELECTORS.uploadCard)).toBeVisible();
        await expect(page).toHaveURL(new RegExp(`${APP_BASE}$`));
    });

    test('la page tient dans un écran de téléphone', async ({ page }) => {
        await page.setViewportSize({ width: 360, height: 740 });
        await page.goto(`${APP_BASE}inscription?pack=5000`);
        await expect(page.getByRole('button', { name: 'Créer mon compte et payer' })).toBeVisible();
        expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(360);
    });
});

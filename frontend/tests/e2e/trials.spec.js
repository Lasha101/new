// « Demandes d'essai » — the admin page of the free-trial automation (Spec v2 §1).
// The request itself, the emails and the purge are proven server-side
// (backend/tests/test_trial_requests.py); here, what Alex sees and clicks.
import { test, expect, LIVE } from './test-base.js';
import { login, SELECTORS, APP_BASE } from '../helpers/index.js';

const trialRequest = (id, overrides = {}) => ({
    id, user_id: `u-${id}`, nom: 'Marie Dupont-Test', societe: 'Agence Horizon Test',
    email: 'Marie.Test@agence-horizon.fr', telephone: '+33 6 00 00 00 00', volume: '50 à 200 documents / mois',
    message: 'Agence groupes.', siret: '12345678901234', tva: 'FR12345678901', status: 'pending',
    created_at: '2026-09-14T08:30:00Z', decided_at: null, ...overrides,
});

test.describe('Demandes d’essai', () => {
    test.skip(LIVE, 'pilote les demandes du mock');

    test('un client ne voit pas l’onglet', async ({ page }) => {
        await login(page);
        await expect(page.locator(SELECTORS.navButtons).filter({ hasText: 'Demandes d' })).toHaveCount(0);
    });

    test('l’administrateur valide une demande et en refuse une autre', async ({ page, api }) => {
        api.user.role = 'admin';
        api.trialRequests = [trialRequest('t-1'), trialRequest('t-2', { nom: 'Paul Refus', email: 'paul@example.com', societe: null })];
        await login(page);

        await page.locator(SELECTORS.navButtons).filter({ hasText: "Demandes d'essai" }).click();
        await expect(page.getByRole('heading', { name: "Demandes d'essai" })).toBeVisible();
        const cards = page.locator('.sid-trial-request');
        await expect(cards).toHaveCount(2);
        await expect(cards.first()).toContainText('Marie Dupont-Test — Agence Horizon Test');
        // Details keep their case (the result cards uppercase their values).
        await expect(cards.first().getByText('Marie.Test@agence-horizon.fr', { exact: true })).toBeVisible();
        await expect(cards.first()).toContainText('50 à 200 documents / mois');

        await cards.first().getByRole('button', { name: 'Valider' }).click();
        await expect(page.locator('.sid-alert--ok')).toContainText("Marie.Test@agence-horizon.fr reçoit l'email de bienvenue");
        await expect(cards).toHaveCount(1);
        expect(api.trialRequests[0].status).toBe('validated');

        page.once('dialog', dialog => dialog.accept());
        await cards.first().getByRole('button', { name: 'Refuser' }).click();
        await expect(page.locator('.sid-alert--ok')).toContainText('Demande de Paul Refus refusée.');
        await expect(page.locator('.sid-trials .sid-empty')).toHaveText("Aucune demande d'essai en attente.");
        expect(api.trialRequests[1].status).toBe('rejected');
    });

    test('le lien de l’email de notification ouvre directement l’onglet', async ({ page, api }) => {
        api.user.role = 'admin';
        api.trialRequests = [trialRequest('t-9')];
        await page.goto(`${APP_BASE}#demandes-essai`);
        await login(page);
        await expect(page.locator('.sid-trial-request')).toHaveCount(1);
        await expect(page.locator(SELECTORS.navButtons).filter({ hasText: "Demandes d'essai" })).toHaveClass(/active/);
    });
});

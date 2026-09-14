// « Mon Compte » — billing identity fields and « Mes achats » (action list item 7).
// Server-side validation and storage: backend/tests/test_account_billing.py.
import { test, expect, LIVE } from './test-base.js';
import { login, SELECTORS } from '../helpers/index.js';

const validSiret = () => ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    .map(d => `4400000000001${d}`)
    .find((candidate) => {
        let total = 0;
        [...candidate].reverse().forEach((c, i) => { let n = Number(c); if (i % 2) { n *= 2; if (n > 9) n -= 9; } total += n; });
        return total % 10 === 0;
    });

const openAccount = async (page) => {
    await page.locator(SELECTORS.navButtons).filter({ hasText: 'Mon Compte' }).click();
    await expect(page.getByRole('heading', { name: 'Modifier Mon Compte' })).toBeVisible();
};

test.describe('Mon Compte — facturation et achats', () => {
    test.skip(LIVE, 'pilote l’état du mock');

    test('les champs de facturation sont enregistrés et réaffichés après rechargement', async ({ page, api }) => {
        await login(page);
        await openAccount(page);

        const values = {
            'Société / agence': 'Agence Compte Test', SIRET: validSiret(), 'N° de TVA intracommunautaire': 'FR99123456789',
            Rue: '2 place de la Facture', 'Code postal': '69002', Ville: 'Lyon', Pays: 'France',
        };
        for (const [label, value] of Object.entries(values)) await page.getByLabel(label, { exact: true }).fill(value);
        await page.getByRole('button', { name: 'Enregistrer les modifications' }).click();
        await expect(page.locator('.sid-alert--ok')).toHaveText('Compte mis à jour avec succès !');
        expect(api.user.company).toBe('Agence Compte Test');

        await page.reload();
        await openAccount(page);
        for (const [label, value] of Object.entries(values)) {
            await expect(page.getByLabel(label, { exact: true })).toHaveValue(value);
        }
    });

    test('un SIRET invalide est refusé avant tout envoi', async ({ page, api }) => {
        await login(page);
        await openAccount(page);
        await page.getByLabel('SIRET', { exact: true }).fill('12345678901234');
        const puts = () => api.requests.filter(r => r.method === 'PUT' && r.path === '/users/me').length;
        const before = puts();
        await page.getByRole('button', { name: 'Enregistrer les modifications' }).click();
        await expect(page.locator('.sid-alert--err')).toHaveText('Le SIRET doit comporter 14 chiffres valides.');
        expect(puts()).toBe(before);
    });

    test('« Mes achats » liste pack, date d’achat et fin de validité', async ({ page, api }) => {
        api.purchases = [
            { id: 'pu-2', pack: 1000, credits: 1000, amount_ht_cents: 69000, paid_at: '2026-09-14T10:00:00Z', expires_at: '2027-09-14T10:00:00Z' },
            { id: 'pu-1', pack: 100, credits: 100, amount_ht_cents: 9900, paid_at: '2026-08-01T10:00:00Z', expires_at: '2027-08-01T10:00:00Z' },
        ];
        await login(page);
        await openAccount(page);
        const rows = page.locator('.sid-purchases tbody tr');
        await expect(rows).toHaveCount(2);
        await expect(rows.nth(0).locator('td')).toHaveText(['Pack 1 000', '14/09/2026', '14/09/2027']);
        await expect(rows.nth(1).locator('td')).toHaveText(['Pack 100', '01/08/2026', '01/08/2027']);
    });

    test('sans achat, un état vide en français', async ({ page }) => {
        await login(page);
        await openAccount(page);
        await expect(page.locator('.sid-purchases .sid-empty')).toHaveText("Aucun achat pour l'instant.");
    });
});

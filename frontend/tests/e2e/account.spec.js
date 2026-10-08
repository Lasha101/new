// « Mon compte » — billing identity fields and « Mes achats » (action list item 7).
// Server-side validation and storage: backend/tests/test_account_billing.py.
import { readFileSync } from 'node:fs';
import { test, expect, LIVE } from './test-base.js';
import { login, SELECTORS } from '../helpers/index.js';

const validSiret = () => ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    .map(d => `4400000000001${d}`)
    .find((candidate) => {
        let total = 0;
        [...candidate].reverse().forEach((c, i) => { let n = Number(c); if (i % 2) { n *= 2; if (n > 9) n -= 9; } total += n; });
        return total % 10 === 0;
    });

// Alex, 03/10/2026 (« à la carte »): the « Acheter à l'unité » link of tarifs.html.
const UNIT_LINK = 'https://buy.stripe.com/8x2eVc3DF4cQcQF2Elebu05';

const openAccount = async (page) => {
    await page.locator(SELECTORS.navButtons).filter({ hasText: 'Mon compte' }).click();
    await expect(page.getByRole('heading', { name: 'Modifier mon compte' })).toBeVisible();
};

test.describe('Mon compte — facturation et achats', () => {
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
        // « Facture »: « — » for a purchase without an invoice (bought before invoices).
        await expect(rows.nth(0).locator('td')).toHaveText(['Pack 1 000', '14/09/2026', '14/09/2027', '—']);
        await expect(rows.nth(1).locator('td')).toHaveText(['Pack 100', '01/08/2026', '01/08/2027', '—']);
    });

    test('« Mes achats » nomme un achat à la carte par ses documents', async ({ page, api }) => {
        // The server stores an « à la carte » purchase as pack 0, the documents bought in `credits`.
        api.purchases = [
            { id: 'pu-3', pack: 0, credits: 37, amount_ht_cents: 5550, paid_at: '2026-10-02T10:00:00Z', expires_at: '2027-10-02T10:00:00Z' },
            { id: 'pu-2', pack: 0, credits: 1, amount_ht_cents: 150, paid_at: '2026-09-20T10:00:00Z', expires_at: '2027-09-20T10:00:00Z' },
            { id: 'pu-1', pack: 1000, credits: 1000, amount_ht_cents: 69000, paid_at: '2026-09-14T10:00:00Z', expires_at: '2027-09-14T10:00:00Z' },
        ];
        await login(page);
        await openAccount(page);
        const rows = page.locator('.sid-purchases tbody tr');
        await expect(rows).toHaveCount(3);
        await expect(rows.nth(0).locator('td')).toHaveText(['À la carte · 37 documents', '02/10/2026', '02/10/2027', '—']);
        await expect(rows.nth(1).locator('td')).toHaveText(['À la carte · 1 document', '20/09/2026', '20/09/2027', '—']);
        await expect(rows.nth(2).locator('td')).toHaveText(['Pack 1 000', '14/09/2026', '14/09/2027', '—']);
    });

    // Alex, 08/10/2026 (« Invoices issued by the app »): a link on each line,
    // the invoice and then the credit notes of the purchase, each its PDF.
    test('« Mes achats » : la facture et l’avoir de chaque achat se téléchargent', async ({ page, api }) => {
        api.purchases = [
            { id: 'pu-2', pack: 100, credits: 100, amount_ht_cents: 9900, paid_at: '2026-10-08T16:10:00Z', expires_at: '2027-10-08T16:10:00Z',
                documents: [{ id: 'inv-2', kind: 'invoice', number: 'F-2026-00002' }, { id: 'cn-1', kind: 'credit_note', number: 'AV-2026-00001' }] },
            { id: 'pu-1', pack: 0, credits: 3, amount_ht_cents: 450, paid_at: '2026-10-08T09:00:00Z', expires_at: '2027-10-08T09:00:00Z',
                documents: [{ id: 'inv-1', kind: 'invoice', number: 'F-2026-00001' }] },
            { id: 'pu-0', pack: 1000, credits: 1000, amount_ht_cents: 69000, paid_at: '2026-09-14T10:00:00Z', expires_at: '2027-09-14T10:00:00Z', documents: [] },
        ];
        api.invoicePdfs = {
            'inv-2': { filename: 'Facture-F-2026-00002.pdf', body: Buffer.from('%PDF-1.7 facture 2') },
            'cn-1': { filename: 'Avoir-AV-2026-00001.pdf', body: Buffer.from('%PDF-1.7 avoir 1') },
            'inv-1': { filename: 'Facture-F-2026-00001.pdf', body: Buffer.from('%PDF-1.7 facture 1') },
        };
        await login(page);
        await openAccount(page);
        const rows = page.locator('.sid-purchases tbody tr');
        await expect(page.locator('.sid-purchases thead th')).toHaveText(['Pack', 'Acheté le', "Valable jusqu'au", 'Facture']);
        await expect(rows.nth(0).locator('td').nth(3).getByRole('button')).toHaveText(['F-2026-00002', 'Avoir AV-2026-00001']);
        await expect(rows.nth(1).locator('td').nth(3).getByRole('button')).toHaveText(['F-2026-00001']);
        await expect(rows.nth(2).locator('td').nth(3)).toHaveText('—');

        for (const [name, filename, body] of [
            ['Télécharger F-2026-00002 (PDF)', 'Facture-F-2026-00002.pdf', '%PDF-1.7 facture 2'],
            ['Télécharger Avoir AV-2026-00001 (PDF)', 'Avoir-AV-2026-00001.pdf', '%PDF-1.7 avoir 1'],
        ]) {
            const downloadPromise = page.waitForEvent('download', { timeout: 30_000 });
            await page.locator('.sid-purchases').getByRole('button', { name }).click();
            const download = await downloadPromise;
            expect(download.suggestedFilename()).toBe(filename);
            const path = test.info().outputPath(filename);
            await download.saveAs(path);
            expect(readFileSync(path, 'utf8')).toBe(body);
        }
        expect(api.requests.filter(r => r.path.startsWith('/invoices/')).map(r => r.path))
            .toEqual(['/invoices/inv-2/pdf', '/invoices/cn-1/pdf']);
        await expect(page.locator('.sid-purchases .sid-alert--err')).toHaveCount(0);
    });

    test('« Mes achats » : un téléchargement en échec le dit en français', async ({ page, api }) => {
        api.purchases = [{ id: 'pu-1', pack: 100, credits: 100, amount_ht_cents: 9900, paid_at: '2026-10-08T16:10:00Z',
            expires_at: '2027-10-08T16:10:00Z', documents: [{ id: 'inv-perdue', kind: 'invoice', number: 'F-2026-00001' }] }];
        await login(page);
        await openAccount(page);
        await page.locator('.sid-purchases').getByRole('button', { name: 'Télécharger F-2026-00001 (PDF)' }).click();
        await expect(page.locator('.sid-purchases .sid-alert--err')).toHaveText('Le téléchargement a échoué. Réessayez dans un instant.');
    });

    // PDF § 4 « Optional, more robust »: Stripe sends client_reference_id back,
    // so the webhook credits this account whatever the e-mail.
    test('« Mes achats » propose l’achat à l’unité, lié au compte par son identifiant et son e-mail', async ({ page }) => {
        await page.route('https://buy.stripe.com/**', route => route.fulfill({ status: 200, contentType: 'text/html', body: '<title>Stripe (stub)</title>' }));
        await login(page);
        await openAccount(page);
        const buy = page.locator('.sid-purchases').getByRole('link', { name: "Acheter des documents à l'unité" });
        await expect(buy).toHaveAttribute('href', `${UNIT_LINK}?client_reference_id=u-alice&locked_prefilled_email=alice%40example.com`);
        await expect(page.locator('.sid-purchases__buy')).toContainText('1,50 € HT le document, ajouté à ce compte dès le paiement confirmé.');

        // The saved e-mail, never a field still being typed.
        await page.locator('input[name="email"]').fill('Alice.Achats+unite@example.com');
        await expect(buy).toHaveAttribute('href', /locked_prefilled_email=alice%40example\.com$/);
        await page.getByRole('button', { name: 'Enregistrer les modifications' }).click();
        await expect(page.locator('.sid-alert--ok')).toHaveText('Compte mis à jour avec succès !');
        await expect(buy).toHaveAttribute('href', `${UNIT_LINK}?client_reference_id=u-alice&locked_prefilled_email=Alice.Achats%2Bunite%40example.com`);

        await buy.click();
        await page.waitForURL(url => url.href.startsWith(UNIT_LINK));
        expect([...new URL(page.url()).searchParams]).toEqual([['client_reference_id', 'u-alice'], ['locked_prefilled_email', 'Alice.Achats+unite@example.com']]);
    });

    test('l’administrateur ne voit pas le lien d’achat', async ({ page, api }) => {
        api.user.role = 'admin';
        await login(page);
        await openAccount(page);
        await expect(page.getByRole('heading', { name: 'Mes achats' })).toBeVisible();
        await expect(page.getByRole('link', { name: "Acheter des documents à l'unité" })).toHaveCount(0);
    });

    test('sans achat, un état vide en français', async ({ page }) => {
        await login(page);
        await openAccount(page);
        await expect(page.locator('.sid-purchases .sid-empty')).toHaveText("Aucun achat pour l'instant.");
    });
});

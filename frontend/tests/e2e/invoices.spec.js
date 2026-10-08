// « Factures » (Alex, « Invoices issued by the app », 08/10/2026): the admin's
// list of every invoice and credit note the app issued, and the monthly CSV for
// the accountant. Server side: backend/tests/test_invoices.py.
import { readFileSync } from 'node:fs';
import { test, expect, LIVE } from './test-base.js';
import { login, SELECTORS } from '../helpers/index.js';

const DOCUMENTS = [
    { id: 'cn-1', kind: 'credit_note', number: 'AV-2026-00001', issue_date: '2026-10-09', livemode: true,
        client_name: 'Agence Test Voyages', client_siren: '732829320', client_email: 'claire@agence-test.fr',
        total_ht_cents: 9900, total_vat_cents: 1980, total_ttc_cents: 11880, stripe_payment_intent: 'pi_live_2',
        stripe_session_id: 'cs_live_2', credited_invoice_number: 'F-2026-00002', purchase_id: 'pu-2', user_id: 'u-claire' },
    { id: 'inv-2', kind: 'invoice', number: 'F-2026-00002', issue_date: '2026-10-08', livemode: true,
        client_name: 'Agence Test Voyages', client_siren: '732829320', client_email: 'claire@agence-test.fr',
        total_ht_cents: 9900, total_vat_cents: 1980, total_ttc_cents: 11880, stripe_payment_intent: 'pi_live_2',
        stripe_session_id: 'cs_live_2', credited_invoice_number: null, purchase_id: 'pu-2', user_id: 'u-claire' },
    { id: 'inv-1', kind: 'invoice', number: 'F-2026-00001', issue_date: '2026-09-30', livemode: true,
        client_name: 'Agence Unité SAS', client_siren: null, client_email: 'marc@agence-unite.fr',
        total_ht_cents: 189000, total_vat_cents: 37800, total_ttc_cents: 226800, stripe_payment_intent: null,
        stripe_session_id: 'cs_live_1', credited_invoice_number: null, purchase_id: 'pu-1', user_id: 'u-marc' },
];

const openInvoices = async (page) => {
    await page.locator(SELECTORS.navButtons).filter({ hasText: 'Factures' }).click();
    await expect(page.getByRole('heading', { name: 'Factures' })).toBeVisible();
};

test.describe('Factures — la liste de l’administrateur et l’export du mois', () => {
    test.skip(LIVE, 'pilote l’état du mock');

    test('l’administrateur voit chaque facture et chaque avoir, du plus récent au plus ancien', async ({ page, api }) => {
        api.user.role = 'admin';
        api.invoices = DOCUMENTS;
        await login(page);
        await openInvoices(page);
        await expect(page.locator('.sid-invoices thead th')).toHaveText(
            ['Type', 'Numéro', 'Date', 'Client', 'SIREN', 'Total HT', 'TVA', 'Total TTC', 'Référence Stripe']);
        const rows = page.locator('.sid-invoices tbody tr');
        await expect(rows).toHaveCount(3);
        await expect(rows.nth(0).locator('td')).toHaveText(
            ['Avoir', 'AV-2026-00001', '09/10/2026', 'Agence Test Voyages', '732829320', '99,00 €', '19,80 €', '118,80 €', 'pi_live_2']);
        await expect(rows.nth(1).locator('td')).toHaveText(
            ['Facture', 'F-2026-00002', '08/10/2026', 'Agence Test Voyages', '732829320', '99,00 €', '19,80 €', '118,80 €', 'pi_live_2']);
        await expect(rows.nth(2).locator('td')).toHaveText(
            ['Facture', 'F-2026-00001', '30/09/2026', 'Agence Unité SAS', '—', '1 890,00 €', '378,00 €', '2 268,00 €', 'cs_live_1']);
        // Names and Stripe ids as typed, not in the results table's capitals.
        await expect(rows.nth(0).locator('td').nth(3)).toHaveCSS('text-transform', 'none');

        const downloadPromise = page.waitForEvent('download', { timeout: 30_000 });
        api.invoicePdfs = { 'inv-2': { filename: 'Facture-F-2026-00002.pdf', body: Buffer.from('%PDF-1.7 F2') } };
        await rows.nth(1).getByRole('button', { name: 'Télécharger F-2026-00002 (PDF)' }).click();
        expect((await downloadPromise).suggestedFilename()).toBe('Facture-F-2026-00002.pdf');
    });

    test('« Exporter le mois (CSV) » télécharge le fichier du mois choisi pour le comptable', async ({ page, api }) => {
        api.user.role = 'admin';
        api.invoices = DOCUMENTS;
        await login(page);
        await openInvoices(page);
        const month = page.getByLabel('Mois à exporter');
        await expect(month).toHaveValue(/^\d{4}-\d{2}$/);             // the current month in Paris
        await month.fill('2026-10');

        const downloadPromise = page.waitForEvent('download', { timeout: 30_000 });
        await page.getByRole('button', { name: 'Exporter le mois (CSV)' }).click();
        const download = await downloadPromise;
        expect(download.suggestedFilename()).toBe('factures_2026-10.csv');
        const path = test.info().outputPath('factures_2026-10.csv');
        await download.saveAs(path);
        expect(readFileSync(path, 'utf8')).toBe('﻿'
            + 'Type;Numéro;Date;Client;SIREN;Total HT;TVA;Total TTC;Référence Stripe;Facture d\'origine\r\n'
            + 'Facture;F-2026-00002;08/10/2026;Agence Test Voyages;732829320;99,00;19,80;118,80;pi_live_2;\r\n'
            + 'Avoir;AV-2026-00001;09/10/2026;Agence Test Voyages;732829320;-99,00;-19,80;-118,80;pi_live_2;F-2026-00002\r\n');
        expect(api.requests.filter(r => r.path === '/admin/invoices/export').map(r => r.search)).toEqual(['?month=2026-10']);
    });

    test('sans facture, un état vide en français', async ({ page, api }) => {
        api.user.role = 'admin';
        await login(page);
        await openInvoices(page);
        await expect(page.locator('.sid-invoices .sid-empty')).toHaveText("Aucune facture pour l'instant.");
    });

    test('un client ne voit pas « Factures »', async ({ page }) => {
        await login(page);
        await expect(page.locator(SELECTORS.navButtons).filter({ hasText: 'Factures' })).toHaveCount(0);
    });
});

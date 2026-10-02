// Column « Sexe » (02/10/2026). The holder's sex — F or M as read from the MRZ —
// sits right after « Prénom » in the results table, the mobile cards, the
// Aperçu and both downloads, under the rules of every other column (header and
// values uppercase, centered). A sex that could not be read is an empty cell.
//
// Mock data (tests/mock/data.js): p-1 F, p-2 M, p-3 F, p-4 none (a new CNI read
// from its front, which carries no MRZ), p-5 M.
import { test, expect, LIVE } from './test-base.js';
import { login, resultsTable, resultsCards, readCsv, readXlsx, TEXT } from '../helpers/index.js';
import { MOCK_PASSPORTS } from '../mock/data.js';

const MOCK_DATA_ONLY = 'compare aux valeurs du jeu de données du mock : sur un vrai backend les données diffèrent';

/** Expected Sexe per document number ('' = not read). */
const EXPECTED_SEX = Object.fromEntries(MOCK_PASSPORTS.map(row => [row.passport_number, row.sex ?? '']));

/** { document number -> Sexe } of a table whose rows carry data-field cells. */
const sexByNumber = table => table.locator('tbody tr').evaluateAll(rows => Object.fromEntries(rows.map(row => [
    row.querySelector('[data-field="passport_number"]').textContent.trim(),
    row.querySelector('[data-field="sex"]').textContent.trim(),
])));

/** text-transform and text-align of every element the locator matches. */
const renderRules = locator => locator.evaluateAll(nodes => nodes.map(node => ({
    textTransform: getComputedStyle(node).textTransform,
    textAlign: getComputedStyle(node).textAlign,
})));

/** The row of one document, by its number. */
const rowOf = (page, number) => resultsTable(page).locator('tbody tr')
    .filter({ has: page.locator('td[data-field="passport_number"]', { hasText: number }) });

test.describe('Tableau « Mes documents »', () => {
    // The table is the view above 720 px, in every browser project.
    test.use({ viewport: { width: 1280, height: 900 } });

    test('« Sexe » suit « Prénom », en majuscules et centré comme les autres colonnes', async ({ page }) => {
        await login(page);
        const table = resultsTable(page);
        await expect(table).toBeVisible();

        const labels = await table.locator('thead th.sortable .header-content > span:not(.sort-indicator)')
            .allTextContents();
        expect(labels.indexOf('Sexe')).toBe(labels.indexOf('Prénom') + 1);
        const fields = await table.locator('tbody tr').first().locator('td[data-field]')
            .evaluateAll(cells => cells.map(cell => cell.dataset.field));
        expect(fields.indexOf('sex')).toBe(fields.indexOf('first_name') + 1);

        // What the user sees: « SEXE », like « PRÉNOM » next to it.
        const header = label => table.locator('thead th.sortable')
            .filter({ has: page.locator('.header-content > span', { hasText: new RegExp(`^${label}$`) }) });
        await expect(header('Sexe').locator('.header-content > span').first()).toHaveText('SEXE', { useInnerText: true });
        expect(await renderRules(header('Sexe'))).toEqual(await renderRules(header('Prénom')));
        expect(await renderRules(header('Sexe'))).toEqual([{ textTransform: 'uppercase', textAlign: 'center' }]);

        const sexCells = await renderRules(table.locator('tbody td[data-field="sex"]'));
        expect(sexCells.length).toBeGreaterThan(0);
        for (const rules of sexCells) expect(rules).toEqual({ textTransform: 'uppercase', textAlign: 'center' });
        expect(sexCells[0]).toEqual((await renderRules(table.locator('tbody td[data-field="first_name"]')))[0]);
    });

    test('les valeurs sont F ou M, et vides quand le sexe n’a pas été lu', async ({ page }) => {
        test.skip(LIVE, MOCK_DATA_ONLY);
        await login(page);
        await expect(resultsTable(page)).toBeVisible();
        expect(await sexByNumber(resultsTable(page))).toEqual(EXPECTED_SEX);
        // An empty cell, never « null » or « undefined ».
        await expect(rowOf(page, 'X4RTBPFW4').locator('td[data-field="sex"]')).toHaveText('');
    });

    test('la colonne se trie comme les autres, les cellules vides en dernier', async ({ page }) => {
        test.skip(LIVE, MOCK_DATA_ONLY);
        await login(page);
        const label = resultsTable(page).locator('thead th.sortable .header-content > span', { hasText: /^Sexe$/ });
        const column = () => resultsTable(page).locator('tbody td[data-field="sex"]')
            .evaluateAll(cells => cells.map(cell => cell.textContent.trim()));

        await label.click();
        await expect.poll(column).toEqual(['F', 'F', 'M', 'M', '']);
        await label.click();
        await expect.poll(column).toEqual(['M', 'M', 'F', 'F', '']);
    });

    test('« Modifier » garde le sexe, et enregistre aussi un document sans sexe', async ({ page, api }) => {
        test.skip(LIVE, 'pilote l’état du mock (api.*) : sur un vrai backend il n’y a pas de mock à piloter');
        await login(page);
        const edit = async (number, firstName) => {
            await rowOf(page, number).getByRole('button', { name: 'Modifier' }).click();
            await expect(page.getByRole('heading', { name: 'Modifier' })).toBeVisible();
            await page.locator('input[name="first_name"]').fill(firstName);
            const put = page.waitForRequest(request => request.method() === 'PUT' && /\/passports\//.test(request.url()));
            await page.getByRole('button', { name: 'Enregistrer' }).click();
            const body = (await put).postDataJSON();
            await expect(resultsTable(page)).toBeVisible();
            return body;
        };

        // A passport read as F: the form sends its sex back, the row still shows it.
        expect((await edit('12AB34567', 'Renommée')).sex).toBe('F');
        await expect(rowOf(page, '12AB34567').locator('td[data-field="first_name"]')).toHaveText('Renommée');
        await expect(rowOf(page, '12AB34567').locator('td[data-field="sex"]')).toHaveText('F');

        // A card whose sex was not read: nothing in the form requires it.
        expect((await edit('X4RTBPFW4', 'Modifiée')).sex).toBeNull();
        await expect(rowOf(page, 'X4RTBPFW4').locator('td[data-field="first_name"]')).toHaveText('Modifiée');
        await expect(rowOf(page, 'X4RTBPFW4').locator('td[data-field="sex"]')).toHaveText('');
        expect(api.passports.find(row => row.passport_number === 'X4RTBPFW4').sex).toBeNull();
    });
});

test.describe('Cartes (mobile)', () => {
    test.use({ viewport: { width: 375, height: 667 } });

    test('chaque carte montre « Sexe » juste après « Prénom », en majuscules', async ({ page }) => {
        test.skip(LIVE, MOCK_DATA_ONLY);
        await login(page);
        const cards = resultsCards(page);
        await expect(cards.first()).toBeVisible();

        const seen = {};
        for (const card of await cards.all()) {
            const labels = await card.locator('.sid-card-item__label').allTextContents();
            expect(labels.indexOf('Sexe')).toBe(labels.indexOf('Prénom') + 1);
            const number = (await card.locator('[data-field="passport_number"]').textContent()).trim();
            seen[number] = (await card.locator('[data-field="sex"]').textContent()).trim();
            const rules = await renderRules(card.locator('[data-field="sex"]'));
            expect(rules[0].textTransform).toBe('uppercase');
            expect(rules).toEqual(await renderRules(card.locator('[data-field="first_name"]')));
        }
        expect(seen).toEqual(EXPECTED_SEX);
    });
});

test.describe('Aperçu et téléchargements', () => {
    test.use({ viewport: { width: 1280, height: 900 } });

    test('l’aperçu montre « Sexe » après « Prénom »', async ({ page }) => {
        test.skip(LIVE, MOCK_DATA_ONLY);
        await login(page);
        await page.getByRole('button', { name: TEXT.preview }).click();
        const preview = page.locator('div', { has: page.getByRole('heading', { name: 'Aperçu' }) })
            .locator('table').first();
        await expect(preview).toBeVisible();

        const headers = await preview.locator('thead th').allTextContents();
        const prenom = headers.indexOf('Prénom');
        expect(headers[prenom + 1]).toBe('Sexe');
        const numero = headers.indexOf('Numéro de document');
        const rows = await preview.locator('tbody tr').evaluateAll(trs => trs.map(tr =>
            [...tr.querySelectorAll('td')].map(td => td.textContent.trim())));
        expect(Object.fromEntries(rows.map(cells => [cells[numero], cells[prenom + 1]]))).toEqual(EXPECTED_SEX);
    });

    test('Excel et CSV : « Sexe » juste après « Prénom », F / M ou vide', async ({ page }, testInfo) => {
        test.skip(LIVE, MOCK_DATA_ONLY);
        await login(page);
        for (const [label, extension, read] of [[TEXT.downloadExcel, 'xlsx', readXlsx], [TEXT.downloadCsv, 'csv', readCsv]]) {
            const downloadPromise = page.waitForEvent('download', { timeout: 30_000 });
            await page.getByRole('button', { name: label }).click();
            const path = testInfo.outputPath(`sexe.${extension}`);
            await (await downloadPromise).saveAs(path);

            const [headers, ...rows] = read(path);
            const prenom = headers.indexOf('Prénom');
            expect(headers[prenom + 1], extension).toBe('Sexe');
            const numero = headers.indexOf('Numéro de document');
            expect(Object.fromEntries(rows.map(cells => [cells[numero], cells[prenom + 1]])), extension)
                .toEqual(EXPECTED_SEX);
        }
    });
});

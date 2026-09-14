// Rows with a confidence score below 0.8 are highlighted (action list item 9),
// in the table and in the mobile cards. The rule itself: isLowConfidence in
// src/resultsHelpers.js (unit-tested). Mock rows: p-4 0.5 and p-5 0.66 are
// low; p-1 0.8734, p-2 0.91 and p-3 (no score) are not.
import { test, expect, LIVE } from './test-base.js';
import { login, resultsTable, resultsCards, getComputedColorPair } from '../helpers/index.js';

const LOW = ['Noé Petit', 'Camille Moreau'];
const NOT_LOW = ['Élodie Dupont-Lévy', 'Jean Martin', 'Chloé Bernard'];
const TITLE = 'Score de confiance inférieur à 80 % : vérifiez ce document.';

const rowOf = (page, name) => resultsTable(page).locator('tbody tr')
    .filter({ has: page.getByLabel(`Sélectionner ${name}`, { exact: true }) });
const cardOf = (page, name) => resultsCards(page)
    .filter({ has: page.getByLabel(`Sélectionner ${name}`, { exact: true }) });

test.describe('Score de confiance inférieur à 0,8', () => {
    test.skip(LIVE, 'repose sur les lignes du mock');

    test('tableau : seules les lignes sous 80 % sont signalées, et restent lisibles', async ({ page }) => {
        await page.setViewportSize({ width: 1280, height: 900 });
        await login(page);
        for (const name of LOW) {
            await expect(rowOf(page, name)).toHaveClass(/\bis-low-confidence\b/);
            await expect(rowOf(page, name)).toHaveAttribute('title', TITLE);
        }
        for (const name of NOT_LOW) {
            await expect(rowOf(page, name)).toBeVisible();
            await expect(rowOf(page, name)).not.toHaveClass(/\bis-low-confidence\b/);
            await expect(rowOf(page, name)).not.toHaveAttribute('title', /.*/);
        }

        const low = rowOf(page, 'Noé Petit');
        const plain = rowOf(page, 'Jean Martin');
        const background = locator => locator.evaluate(node => getComputedStyle(node).backgroundColor);
        expect(await background(low)).toBe('rgb(255, 243, 196)');                 // --sid-warn-bg
        expect(await low.locator('td').first().evaluate(node => getComputedStyle(node).boxShadow))
            .toContain('rgb(146, 64, 14)');                                         // --sid-warn edge
        expect(await background(plain)).not.toBe('rgb(255, 243, 196)');
        const text = await getComputedColorPair(page, '.sid-table tbody tr.is-low-confidence td[data-field="last_name"]');
        expect(text.passesAA, `${text.ratio.toFixed(2)}:1`).toBe(true);
        const action = await getComputedColorPair(page, '.sid-table tbody tr.is-low-confidence .sid-btn-ghost');
        expect(action.passesAA, `« Modifier » ${action.ratio.toFixed(2)}:1`).toBe(true);

        // A selected row still reads as selected.
        await page.getByLabel('Sélectionner Noé Petit', { exact: true }).first().check();
        await expect(low).toHaveClass(/\bselected-row\b/);
        expect(await background(low)).not.toBe('rgb(255, 243, 196)');
    });

    test('cartes mobiles : les mêmes documents sont signalés', async ({ page }) => {
        await page.setViewportSize({ width: 375, height: 800 });
        await login(page);
        for (const name of LOW) {
            await expect(cardOf(page, name)).toBeVisible();
            await expect(cardOf(page, name)).toHaveClass(/\bis-low-confidence\b/);
            await expect(cardOf(page, name)).toHaveAttribute('title', TITLE);
        }
        for (const name of NOT_LOW) {
            await expect(cardOf(page, name)).not.toHaveClass(/\bis-low-confidence\b/);
        }
        const edge = await cardOf(page, 'Camille Moreau').evaluate(node => getComputedStyle(node).borderLeft);
        expect(edge).toContain('3px solid rgb(146, 64, 14)');
        const action = await getComputedColorPair(page, '.sid-card-item.is-low-confidence .sid-btn-ghost');
        expect(action.passesAA, `« Modifier » ${action.ratio.toFixed(2)}:1`).toBe(true);
    });
});

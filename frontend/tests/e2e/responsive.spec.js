// Package A — the mobile half of the design system.
//
// The results screen renders twice: a table above 720 px and stacked cards
// below, both from the SAME column definition (PASSPORT_COLUMN_ORDER) and the
// SAME cell function (resultCellValue). The parity spec is the one that matters:
// it is what stops the two views drifting apart as columns change.
import { test, expect } from './test-base.js';
import {
    login, uploadFiles, waitForProcessing, resultsTable, resultsCards,
    hasHorizontalOverflow, findOverflowingElements, SELECTORS, TEXT,
} from '../helpers/index.js';
import { fixturePath } from '../fixtures/index.js';
import { PASSPORT_COLUMN_ORDER } from '../../src/resultsHelpers.js';

const NARROW_VIEWPORTS = [{ width: 360, height: 640 }, { width: 375, height: 667 }];

/** Every field of row `index` as the TABLE renders it, keyed by column name. */
const fromTable = (page, index) => resultsTable(page)
    .locator('tbody tr').nth(index).locator('td[data-field]')
    .evaluateAll(cells => Object.fromEntries(
        cells.map(cell => [cell.dataset.field, (cell.textContent || '').trim()]),
    ));

/** Every field of row `index` as the CARD renders it, keyed by column name. */
const fromCard = (page, index) => resultsCards(page).nth(index)
    .locator('[data-field]')
    .evaluateAll(nodes => Object.fromEntries(
        nodes.map(node => [node.dataset.field, (node.textContent || '').trim()]),
    ));

test.describe('Bascule tableau / cartes', () => {
    test('à 719 px les cartes, à 721 px le tableau', async ({ page }) => {
        await login(page);
        await expect(resultsTable(page)).toBeAttached();

        await page.setViewportSize({ width: 719, height: 800 });
        await expect(page.locator(SELECTORS.cardList)).toBeVisible();
        await expect(resultsTable(page)).toBeHidden();

        await page.setViewportSize({ width: 721, height: 800 });
        await expect(resultsTable(page)).toBeVisible();
        await expect(page.locator(SELECTORS.cardList)).toBeHidden();

        // Both stay mounted across the switch: CSS alone decides, so no state
        // is lost on a rotation or a resize.
        await expect(page.locator(SELECTORS.cardList)).toBeAttached();
    });

    test('un aller-retour autour du point de bascule ne perd pas la sélection', async ({ page }) => {
        await login(page);
        await page.setViewportSize({ width: 1000, height: 800 });

        const firstCheckbox = resultsTable(page).locator('tbody tr').first().locator('input[type="checkbox"]');
        await firstCheckbox.check();
        await expect(page.getByRole('button', { name: /^Supprimer \(1\)$/ })).toBeVisible();

        await page.setViewportSize({ width: 700, height: 800 });
        await expect(page.locator(SELECTORS.cardList)).toBeVisible();
        await page.setViewportSize({ width: 1000, height: 800 });

        await expect(firstCheckbox).toBeChecked();
        await expect(page.getByRole('button', { name: /^Supprimer \(1\)$/ })).toBeVisible();
    });
});

test.describe('Parité tableau / cartes', () => {
    test('après un téléversement, chaque champ est identique dans les deux vues', async ({ page }) => {
        await login(page);
        await uploadFiles(page, [fixturePath('smallJpeg')], { submit: true });
        await waitForProcessing(page, { timeout: 30_000 });

        // The finished job puts a fresh row at the top of both views.
        await expect.poll(() => resultsCards(page).count(), { timeout: 15_000 })
            .toBeGreaterThan(0);
        await expect.poll(() => resultsTable(page).locator('tbody tr[class], tbody tr').count())
            .toBe(await resultsCards(page).count());

        const rowCount = await resultsCards(page).count();
        for (let index = 0; index < rowCount; index++) {
            const table = await fromTable(page, index);
            const card = await fromCard(page, index);

            // Same keys, same values — and they are the shared column definition.
            expect(Object.keys(table).sort()).toEqual([...PASSPORT_COLUMN_ORDER].sort());
            expect(card).toEqual(table);
        }
        expect(rowCount).toBeGreaterThan(0);
    });

    test('le filtre de type garde les deux vues d’accord', async ({ page }) => {
        await login(page);
        await page.locator(SELECTORS.typeFilter).locator('button[value="PASS"]').click();

        const rowCount = await resultsCards(page).count();
        expect(rowCount).toBeGreaterThan(0);
        for (let index = 0; index < rowCount; index++) {
            expect(await fromCard(page, index)).toEqual(await fromTable(page, index));
        }
    });
});

test.describe('Majuscules et centrage', () => {
    test('les cellules du tableau sont en majuscules et centrées', async ({ page }) => {
        await login(page);
        const cells = resultsTable(page).locator('tbody td[data-field]');
        await expect(cells.first()).toBeAttached();

        const styles = await cells.evaluateAll(nodes => nodes.map(node => ({
            text: (node.textContent || '').trim(),
            textTransform: getComputedStyle(node).textTransform,
            textAlign: getComputedStyle(node).textAlign,
        })));
        expect(styles.length).toBeGreaterThan(0);
        for (const style of styles) {
            expect(style.textTransform).toBe('uppercase');
            expect(style.textAlign).toBe('center');
        }
    });

    test('les valeurs des cartes sont en majuscules', async ({ page }) => {
        await login(page);
        const values = page.locator('.sid-card-item__value');
        await expect(values.first()).toBeAttached();

        const transforms = await values.evaluateAll(nodes =>
            nodes.map(node => getComputedStyle(node).textTransform));
        expect(transforms.length).toBeGreaterThan(0);
        for (const transform of transforms) expect(transform).toBe('uppercase');
    });
});

test.describe('Pas de débordement horizontal', () => {
    for (const viewport of NARROW_VIEWPORTS) {
        test(`${viewport.width} px : connexion, import et résultats tiennent dans l’écran`, async ({ page }) => {
            await page.setViewportSize(viewport);

            await page.goto('/');
            await expect(page.locator(SELECTORS.loginForm)).toBeVisible();
            expect(await findOverflowingElements(page)).toEqual([]);
            expect(await hasHorizontalOverflow(page)).toBe(false);

            await login(page);
            await expect(page.locator(SELECTORS.uploadCard)).toBeVisible();
            expect(await findOverflowingElements(page)).toEqual([]);
            expect(await hasHorizontalOverflow(page)).toBe(false);

            await expect(page.locator(SELECTORS.cardList)).toBeVisible();
            expect(await findOverflowingElements(page)).toEqual([]);
            expect(await hasHorizontalOverflow(page)).toBe(false);

            // scrollWidth must not exceed the viewport, as the brief puts it.
            const { scrollWidth, clientWidth } = await page.evaluate(() => ({
                scrollWidth: document.body.scrollWidth,
                clientWidth: document.documentElement.clientWidth,
            }));
            expect(scrollWidth).toBeLessThanOrEqual(clientWidth);
        });
    }
});

test.describe('Écran vide', () => {
    test('sans donnée, l’état vide s’affiche dans les deux vues', async ({ page, api }) => {
        api.passports = [];
        await login(page);

        await page.setViewportSize({ width: 1000, height: 800 });
        await expect(resultsTable(page).locator(SELECTORS.emptyState)).toContainText(TEXT.noData);

        await page.setViewportSize({ width: 700, height: 800 });
        await expect(page.locator(`${SELECTORS.cardList} .sid-empty`)).toContainText(TEXT.noData);
    });
});

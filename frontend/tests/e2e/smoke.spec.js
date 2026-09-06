// Regression baseline: the behaviour of the app *as it is today*, before any
// refactor. Every assertion here describes something the app already does — if
// one of these ever goes red after a change, the change broke it.
//
// Nothing in this file may be weakened to make it pass. An application bug gets
// reported, not accommodated.
import { test, expect, LIVE, EXPECTED_ROW_COUNTS } from './test-base.js';
import {
    login, storedToken, uploadFiles, waitForProcessing, countResultRows, resultsRows,
    SELECTORS, TEXT,
} from '../helpers/index.js';
import { fixturePath } from '../fixtures/index.js';

test.describe('ScanID — baseline', () => {
    test('la connexion aboutit au tableau de bord', async ({ page }) => {
        await login(page);

        await expect(page.locator(SELECTORS.creditBadge)).toBeVisible();
        await expect(page.getByRole('button', { name: TEXT.logout })).toBeVisible();
        await expect(page.locator(SELECTORS.loginForm)).toHaveCount(0);
        expect(await storedToken(page)).toBeTruthy();
    });

    test('des identifiants incorrects affichent le message d’erreur existant', async ({ page }) => {
        await login(page, { password: 'mauvais-mot-de-passe', expectFailure: true });

        const error = page.locator(SELECTORS.errorMessage);
        await expect(error).toBeVisible();
        await expect(error).toHaveText(TEXT.badCredentials);

        // Still on the login screen, and nothing was stored.
        await expect(page.locator(SELECTORS.loginForm)).toBeVisible();
        expect(await storedToken(page)).toBeNull();
    });

    test('le compteur de crédits s’affiche', async ({ page, api }) => {
        await login(page);

        const badge = page.locator(SELECTORS.creditBadge);
        await expect(badge).toBeVisible();
        await expect(badge).toHaveText(/^Crédits\s*:\s*\d+$/);
        if (!LIVE) await expect(badge).toHaveText(`Crédits : ${api.user.page_credits}`);

        await expect(page.locator('.credit-display')).toContainText('Pages Traitées :');
    });

    test('le filtre Tous/PASS/PI change le nombre de lignes visibles', async ({ page }) => {
        await login(page);

        const filter = page.locator(SELECTORS.typeFilter);
        await expect(filter).toBeVisible();
        await expect(resultsRows(page).first()).toBeVisible();

        const total = await countResultRows(page);
        expect(total).toBeGreaterThan(0);

        await filter.selectOption('PASS');
        const passCount = await countResultRows(page);

        await filter.selectOption('PI');
        const idCardCount = await countResultRows(page);

        await filter.selectOption('');
        expect(await countResultRows(page)).toBe(total);

        // Every row is one type or the other, and filtering really narrows.
        expect(passCount + idCardCount).toBe(total);
        expect(passCount).toBeLessThan(total);
        expect(idCardCount).toBeLessThan(total);

        if (!LIVE) {
            expect(total).toBe(EXPECTED_ROW_COUNTS['']);
            expect(passCount).toBe(EXPECTED_ROW_COUNTS.PASS);
            expect(idCardCount).toBe(EXPECTED_ROW_COUNTS.PI);
        }

        // The filter narrows on the document number, which is what PASS means.
        await filter.selectOption('PASS');
        for (const cells of await resultsRows(page).all()) {
            await expect(cells).toContainText(/\d{2}[A-Z]{2}\d{5}/);
        }
    });

    test('le téléversement d’un document aboutit à un résultat', async ({ page }) => {
        test.slow(); // OCR takes real time in live mode.
        await login(page);

        const before = await countResultRows(page);

        await uploadFiles(page, [fixturePath('smallJpeg')], { submit: true });
        await expect(page.locator(SELECTORS.jobMonitor)).toBeVisible();

        const statuses = await waitForProcessing(page, { timeout: LIVE ? 180_000 : 30_000 });

        if (LIVE) {
            // Against a real backend the page really goes to Google Vision, and a
            // synthetic fixture carries no readable MRZ — so what is provable here
            // is that the job runs to a terminal state and the UI reports it.
            // Extraction accuracy needs a specimen document and a human; see
            // tests/README.md.
            expect(statuses.some(status => [TEXT.jobDone, TEXT.jobFailed].includes(status))).toBe(true);
            return;
        }

        expect(statuses).toContain(TEXT.jobDone);
        // The finished job refreshes the table: a new row is on screen.
        await expect.poll(() => countResultRows(page), { timeout: 15_000 })
            .toBeGreaterThan(before);
    });

    test('les deux boutons de téléchargement produisent un fichier', async ({ page }) => {
        await login(page);
        await expect(resultsRows(page).first()).toBeVisible();

        for (const [label, extension] of [[TEXT.downloadCsv, 'csv'], [TEXT.downloadExcel, 'xlsx']]) {
            const downloadPromise = page.waitForEvent('download', { timeout: 30_000 });
            await page.getByRole('button', { name: label }).click();
            const download = await downloadPromise;

            expect(download.suggestedFilename()).toMatch(new RegExp(`\\.${extension}$`));

            const savedTo = await download.path();
            const { size } = await import('node:fs').then(fs => fs.promises.stat(savedTo));
            expect(size).toBeGreaterThan(0);
        }
    });
});

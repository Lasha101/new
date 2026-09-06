// Driving the real upload path: the same hidden <input type="file"> the drop
// zone clicks, the same submit button, the same job monitor.
import { expect } from '@playwright/test';
import { SELECTORS, TEXT, TERMINAL_JOB_LABELS } from './selectors.js';

/**
 * Puts files on the real file input.
 *
 * @param {import('@playwright/test').Page} page
 * @param {string[]} paths Absolute paths, e.g. from tests/fixtures.
 * @param {{submit?:boolean, destination?:string}} [options]
 *   `submit` also clicks « Lancer l'analyse ».
 *
 * The input is display:none (the drop zone forwards clicks to it), which
 * setInputFiles handles; it carries no `multiple` attribute, so more than one
 * path is rejected here with a clear message instead of a Playwright internal
 * error.
 */
export async function uploadFiles(page, paths, options = {}) {
    const list = Array.isArray(paths) ? paths : [paths];
    if (list.length === 0) throw new Error('uploadFiles: no file given');

    const input = page.locator(SELECTORS.fileInput);
    await expect(input).toBeAttached();

    if (list.length > 1) {
        const multiple = await input.evaluate(node => node.hasAttribute('multiple'));
        if (!multiple) {
            throw new Error(
                `uploadFiles: ${list.length} files given, but the upload input accepts one at a time `
                + '(no `multiple` attribute on .drop-zone input[type="file"]). '
                + 'Upload them one by one, or update this helper when multi-file upload ships.',
            );
        }
    }

    if (options.destination !== undefined) {
        await page.locator(SELECTORS.destinationInput).fill(options.destination);
    }

    await input.setInputFiles(list);
    await expect(page.locator(SELECTORS.uploadCard)).toContainText('Fichier prêt');

    if (options.submit) {
        await page.getByRole('button', { name: TEXT.startAnalysis }).click();
    }
}

/**
 * Waits until every job in the monitor has reached a terminal state
 * (« Terminé » or « Échoué »), and returns the labels seen, newest first.
 *
 * The default timeout is generous because a real OCR run over a multi-page PDF
 * takes tens of seconds; pass a smaller one for mocked runs when a fast failure
 * is more useful than a slow one.
 */
export async function waitForProcessing(page, { timeout = 120_000 } = {}) {
    const monitor = page.locator(SELECTORS.jobMonitor);
    await expect(monitor).toBeVisible({ timeout });

    await expect.poll(async () => {
        const labels = await page.locator(SELECTORS.jobProgressText).allTextContents();
        if (labels.length === 0) return 'no-jobs';
        return labels.every(label => TERMINAL_JOB_LABELS.includes(label.trim())) ? 'terminal' : 'busy';
    }, {
        timeout,
        message: `no job reached ${TERMINAL_JOB_LABELS.join(' / ')} within ${timeout} ms`,
    }).toBe('terminal');

    return (await page.locator(SELECTORS.jobProgressText).allTextContents()).map(label => label.trim());
}

/** The results table: the last .table-container, so an open export preview
    (which renders its own table above) is never counted by mistake. */
export function resultsTable(page) {
    return page.locator(SELECTORS.tableContainer).last();
}

/** Its body rows, including the single « Aucune donnée trouvée. » placeholder. */
export function resultsRows(page) {
    return resultsTable(page).locator('tbody tr');
}

/** Rows currently rendered in the results table (« Aucune donnée trouvée. » = 0). */
export async function countResultRows(page) {
    const rows = resultsRows(page);
    const count = await rows.count();
    if (count === 1 && (await rows.first().textContent() || '').includes(TEXT.noData)) return 0;
    return count;
}

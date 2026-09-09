// Package A — the design system as it is driven by the app's own data.
//
// Badge and chip classes must come from values that already exist: the document
// type derived in resultsHelpers.js, and the job.status the backend writes. No
// new field, status or derived value was introduced to make these pass.
import { test, expect } from './test-base.js';
import {
    login, resultsTable, resultsCards, selectDocType, readCsv, readXlsx,
    SELECTORS, TEXT, APP_BASE } from '../helpers/index.js';
import { DOC_TYPE_PASSPORT, DOC_TYPE_ID_CARD } from '../../src/resultsHelpers.js';

/**
 * The export columns exactly as they were BEFORE Package A: the French headers
 * of EXPORT_COLUMNS in backend/main.py, in order, with the derived Type column
 * between the document number and the destination. Recorded here so a later
 * change to the results screen cannot silently reorder the downloaded files.
 */
const BASELINE_EXPORT_HEADERS = [
    'Nom de famille', 'Prénom', 'Date de Naissance', "Date d'Expiration", 'Nationalité',
    'Numéro de Passeport', 'Type', 'Destination', 'Score de Confiance',
];

/** English words that must never appear in this French UI. */
const ENGLISH_WORDS = ['Upload', 'Download', 'Loading', 'Failed', 'Retry', 'Submit', 'Cancel', 'Search', 'Settings'];

/** Visible text of the page, minus the elements a spec names as exempt. */
const visibleText = (page, exclude = []) => page.evaluate((selectors) => {
    const skip = new Set();
    for (const selector of selectors) {
        for (const node of document.querySelectorAll(selector)) skip.add(node);
    }
    const walk = (node) => {
        if (skip.has(node)) return '';
        if (node.nodeType === Node.TEXT_NODE) return node.textContent;
        if (node.nodeType !== Node.ELEMENT_NODE) return '';
        const style = getComputedStyle(node);
        if (style.display === 'none' || style.visibility === 'hidden') return '';
        return [...node.childNodes].map(walk).join(' ');
    };
    return walk(document.body).replace(/\s+/g, ' ');
}, exclude);

test.describe('Badges de type de document', () => {
    test('un passeport rend --pp, une pièce d’identité rend --pi', async ({ page }) => {
        await login(page);

        await selectDocType(page, DOC_TYPE_PASSPORT);
        let badges = resultsTable(page).locator('td[data-field="document_type"] .sid-badge');
        await expect(badges.first()).toBeAttached();
        for (const badge of await badges.all()) {
            await expect(badge).toHaveClass(/sid-badge--pp/);
            await expect(badge).toHaveText(DOC_TYPE_PASSPORT);
        }

        await selectDocType(page, DOC_TYPE_ID_CARD);
        badges = resultsTable(page).locator('td[data-field="document_type"] .sid-badge');
        await expect(badges.first()).toBeAttached();
        for (const badge of await badges.all()) {
            await expect(badge).toHaveClass(/sid-badge--pi/);
            await expect(badge).toHaveText(DOC_TYPE_ID_CARD);
        }
    });

    test('la carte mobile porte le même badge que le tableau', async ({ page }) => {
        await login(page);
        const count = await resultsCards(page).count();
        expect(count).toBeGreaterThan(0);

        for (let index = 0; index < count; index++) {
            const tableClass = await resultsTable(page).locator('tbody tr').nth(index)
                .locator('td[data-field="document_type"] .sid-badge').getAttribute('class');
            const cardClass = await resultsCards(page).nth(index)
                .locator('.sid-badge').getAttribute('class');
            expect(cardClass).toBe(tableClass);
        }
    });
});

test.describe('Chips d’état de traitement', () => {
    test('chaque statut renvoyé par l’API rend sa classe', async ({ page, api }) => {
        const job = (id, status, name) => ({
            id, user_id: api.user.id, file_name: name, status, progress: 100,
            created_at: new Date().toISOString(), committed: true, successes: [], failures: [],
        });
        api.jobs = [
            job('job-1', 'processing', 'encours.pdf'),
            job('job-2', 'complete', 'termine.pdf'),
            job('job-3', 'failed', 'echec.pdf'),
        ];
        // Keep the processing job from ageing into 'complete' mid-test.
        api.jobs[0].startedAt = Date.now() + 600_000;
        api.jobs[0].progress = 40;

        await login(page);
        await expect(page.locator(SELECTORS.jobMonitor)).toBeVisible();

        for (const [status, modifier, label] of [
            ['processing', 'sid-chip--processing', 'En cours'],
            ['complete', 'sid-chip--done', 'Terminé'],
            ['failed', 'sid-chip--failed', 'Échoué'],
        ]) {
            const chip = page.locator(`.${modifier}`);
            await expect(chip, `no chip for status "${status}"`).toHaveCount(1);
            await expect(chip).toHaveText(label);
        }
    });
});

test.describe('Téléchargements', () => {
    test('les deux fichiers gardent l’ordre des colonnes et les accents', async ({ page }, testInfo) => {
        await login(page);
        await expect(page.locator(SELECTORS.downloadGroup)).toBeVisible();

        const saved = {};
        for (const [label, extension] of [[TEXT.downloadExcel, 'xlsx'], [TEXT.downloadCsv, 'csv']]) {
            const downloadPromise = page.waitForEvent('download', { timeout: 30_000 });
            await page.getByRole('button', { name: label }).click();
            const download = await downloadPromise;
            expect(download.suggestedFilename()).toMatch(new RegExp(`\\.${extension}$`));
            saved[extension] = testInfo.outputPath(`export.${extension}`);
            await download.saveAs(saved[extension]);
        }

        const csv = readCsv(saved.csv);
        const xlsx = readXlsx(saved.xlsx);

        // Column set AND order, in both files, identical to the pre-refactor baseline.
        expect(csv[0]).toEqual(BASELINE_EXPORT_HEADERS);
        expect(xlsx[0]).toEqual(BASELINE_EXPORT_HEADERS);

        // Accented French survived both encodings (UTF-8 BOM / shared strings).
        for (const header of ['Prénom', 'Nationalité', "Date d'Expiration"]) {
            expect(csv[0]).toContain(header);
            expect(xlsx[0]).toContain(header);
        }
        const csvBody = csv.slice(1).flat().join(' ');
        const xlsxBody = xlsx.slice(1).flat().join(' ');
        expect(csvBody).toMatch(/DUPONT-LÉVY|ÉLODIE|CHLOÉ|NOÉ/);
        expect(xlsxBody).toMatch(/DUPONT-LÉVY|ÉLODIE|CHLOÉ|NOÉ/);
        expect(csvBody).not.toContain('Ã');   // the classic UTF-8-read-as-latin1 tell
        expect(xlsxBody).not.toContain('Ã');

        // Both files describe the same rows.
        expect(csv.length).toBe(xlsx.length);
    });

    test('le groupe de téléchargement porte les deux styles et l’icône', async ({ page }) => {
        await login(page);
        const group = page.locator(SELECTORS.downloadGroup);
        await expect(group.locator('.sid-btn')).toHaveText(/Excel/);
        await expect(group.locator('.sid-btn-outline')).toHaveText(/CSV/);

        // 4e: the arrow was scoped to .sid-btn, so the outline button had none.
        for (const selector of ['.sid-btn', '.sid-btn-outline']) {
            const content = await group.locator(selector).evaluate(node =>
                getComputedStyle(node, '::before').content);
            expect(content, `${selector} has no download glyph`).toContain('⬇');
        }
    });
});

test.describe('Interface en français', () => {
    // ProgressBar renders « 12% - Upload » for a job under 15% (App.jsx). That
    // string predates Package A and the brief forbids rewording existing text,
    // so it is excluded by selector — narrowly, so an "Upload" anywhere else
    // still fails this test. Reported in the handover as a pre-existing finding.
    const EXEMPT = ['.progress-text'];

    test('aucun mot anglais visible sur la connexion', async ({ page }) => {
        await page.goto(APP_BASE);
        await expect(page.locator(SELECTORS.loginForm)).toBeVisible();

        const text = await visibleText(page, EXEMPT);
        for (const word of ENGLISH_WORDS) {
            expect(text, `"${word}" is visible on the login screen`).not.toMatch(new RegExp(`\\b${word}\\b`));
        }
    });

    test('aucun mot anglais visible sur le tableau de bord', async ({ page }) => {
        await login(page);
        await expect(page.locator(SELECTORS.uploadCard)).toBeVisible();

        for (const tab of ['Passeports', 'Mon Compte']) {
            await page.getByRole('button', { name: tab, exact: true }).click();
            await expect(page.locator(SELECTORS.navButtons).filter({ hasText: tab })).toHaveClass(/active/);

            const text = await visibleText(page, EXEMPT);
            for (const word of ENGLISH_WORDS) {
                expect(text, `"${word}" is visible on the ${tab} tab`).not.toMatch(new RegExp(`\\b${word}\\b`));
            }
        }
    });
});

test.describe('Barre d’application', () => {
    test('le logo et le compteur de crédits sont dans la barre', async ({ page, api }) => {
        await login(page);

        const topbar = page.locator(SELECTORS.topbar);
        await expect(topbar.locator(SELECTORS.logo)).toHaveText('ScanID');
        await expect(topbar.locator(`${SELECTORS.logo} span`)).toHaveText('ID');
        await expect(topbar.locator(SELECTORS.creditBadge)).toHaveText(`Crédits : ${api.user.page_credits}`);
        await expect(topbar.locator(SELECTORS.logoutButton)).toHaveText(TEXT.logout);
    });

    test('le filtre segmenté marque l’option active', async ({ page }) => {
        await login(page);
        const group = page.locator(SELECTORS.typeFilter);

        await expect(group.locator('button[value=""]')).toHaveClass(/is-active/);
        await selectDocType(page, DOC_TYPE_PASSPORT);
        await expect(group.locator('button[value=""]')).not.toHaveClass(/is-active/);
        await expect(group.locator(`button[value="${DOC_TYPE_PASSPORT}"]`)).toHaveClass(/is-active/);
        await expect(group.locator('button')).toHaveCount(3);
    });
});

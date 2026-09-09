// Package A — self-hosted fonts.
//
// The product's selling point is that documents are never stored; sending every
// visitor's IP to Google to fetch a webfont contradicts that. These specs prove
// the fonts really are served from this origin and really are the ones the
// design system asks for — a wrong @fontsource path resolves to nothing and the
// browser silently falls back to a system font, which looks like success.
import { test, expect } from './test-base.js';
import { login, uploadFiles, resultsRows, selectDocType, SELECTORS, TEXT, APP_BASE } from '../helpers/index.js';
import { fixturePath } from '../fixtures/index.js';

/** Hosts that would mean a font request left this origin. */
const THIRD_PARTY_FONT_HOSTS = ['googleapis.com', 'gstatic.com'];

/** Every URL the page requested, recorded from before the first navigation. */
function recordRequests(page) {
    const urls = [];
    page.on('request', request => urls.push(request.url()));
    return urls;
}

const offenders = urls => urls.filter(url => THIRD_PARTY_FONT_HOSTS.some(host => url.includes(host)));

test.describe('Polices auto-hébergées', () => {
    test('les deux familles sont réellement chargées', async ({ page }) => {
        await login(page);
        await page.evaluate(() => document.fonts.ready);

        // Poll: font loading is asynchronous and finishes shortly after layout.
        await expect.poll(
            () => page.evaluate(() => document.fonts.check('700 1rem "Space Grotesk"')),
            { message: 'Space Grotesk 700 never reported as loaded' },
        ).toBe(true);

        await expect.poll(
            () => page.evaluate(() => document.fonts.check('400 1rem "Inter"')),
            { message: 'Inter 400 never reported as loaded' },
        ).toBe(true);
    });

    test('les titres rendent en Space Grotesk et le texte en Inter', async ({ page }) => {
        await page.goto(APP_BASE);
        await expect(page.locator(SELECTORS.loginForm)).toBeVisible();
        await page.evaluate(() => document.fonts.ready);

        const heading = await page.locator('h1').first()
            .evaluate(node => getComputedStyle(node).fontFamily);
        expect(heading).toContain('Space Grotesk');

        const paragraph = await page.locator('.sid-appfoot p').first()
            .evaluate(node => getComputedStyle(node).fontFamily);
        expect(paragraph).toContain('Inter');
    });

    test('les fichiers de police viennent de cette origine', async ({ page }) => {
        const urls = recordRequests(page);
        await login(page);
        await page.evaluate(() => document.fonts.ready);

        const fontRequests = urls.filter(url => /\.woff2?(\?|$)/.test(url));
        expect(fontRequests.length).toBeGreaterThan(0);

        const origin = new URL(page.url()).origin;
        for (const url of fontRequests) expect(url.startsWith(origin)).toBe(true);
    });

    test('une session complète ne contacte jamais googleapis ni gstatic', async ({ page }) => {
        const urls = recordRequests(page);

        // A full session: login, the whole dashboard, an upload, the filter,
        // both downloads, the other tabs, then logout.
        await login(page);
        await expect(resultsRows(page).first()).toBeVisible();

        await uploadFiles(page, [fixturePath('smallJpeg')], { submit: true });
        await expect(page.locator(SELECTORS.jobMonitor)).toBeVisible();

        await selectDocType(page, 'PASS');
        await selectDocType(page, '');

        for (const label of [TEXT.downloadExcel, TEXT.downloadCsv]) {
            const download = page.waitForEvent('download', { timeout: 30_000 });
            await page.getByRole('button', { name: label }).click();
            await download;
        }

        for (const name of ['Mon Compte', 'Passeports']) {
            await page.getByRole('button', { name, exact: true }).click();
            await expect(page.locator(SELECTORS.navButtons).filter({ hasText: name })).toHaveClass(/active/);
        }

        await page.getByRole('button', { name: TEXT.logout }).click();
        await expect(page.locator(SELECTORS.loginForm)).toBeVisible();

        expect(urls.length).toBeGreaterThan(5);
        expect(offenders(urls), `third-party font requests: ${offenders(urls).join(', ')}`).toEqual([]);
    });
});

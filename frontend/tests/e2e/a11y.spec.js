// Package A — the accessibility criteria the design system was written against:
// 44 px tap targets, no iOS input zoom, AA contrast, a visible focus ring.
//
// Every contrast number here is measured on the rendered page (the element's
// own colour against the background actually painted behind it), not read off
// the stylesheet — a token that passes on white can fail on a tinted card, and
// that is exactly what happened to the v1.0 palette.
import { test, expect } from './test-base.js';
import {
    login, uploadFiles, measureTapTargets, getComputedColorPair, SELECTORS, TEXT,
} from '../helpers/index.js';
import { fixturePath } from '../fixtures/index.js';

const BUTTON_SELECTOR = '.sid-btn, .sid-btn-outline, .sid-btn-ghost';
const SEGMENT_SELECTOR = '.sid-seg button';
const MIN_TAP_PX = 44;
const MIN_INPUT_FONT_PX = 16;

/** Text inputs Safari would zoom into. Checkboxes and files have no text. */
const TEXT_INPUT_SELECTOR = [
    'input[type="text"]', 'input[type="email"]', 'input[type="password"]',
    'input[type="number"]', 'input[type="date"]', 'input[type="search"]',
    'input[type="tel"]', 'input:not([type])', 'textarea', 'select',
].join(', ');

/** Renders one contrast row for the report table. */
const row = r => `| ${r.selector.padEnd(30)} | ${r.ratio.toFixed(2).padStart(6)}:1 | `
    + `${String(r.fontSizePx).padStart(5)}px | ${String(r.fontWeight).padStart(4)} | `
    + `${r.aaThreshold.toFixed(1)} | ${r.passesAA ? 'PASS' : 'FAIL'} |`;

test.describe('Cibles tactiles', () => {
    test('tout bouton du système de design mesure au moins 44 px de haut', async ({ page }) => {
        await login(page);
        await expect(page.locator('.sid-btn').first()).toBeVisible();

        const targets = [
            ...await measureTapTargets(page, BUTTON_SELECTOR),
            ...await measureTapTargets(page, SEGMENT_SELECTOR),
        ];
        expect(targets.length).toBeGreaterThan(4);

        const tooSmall = targets.filter(target => target.height < MIN_TAP_PX);
        expect(
            tooSmall,
            `under ${MIN_TAP_PX}px tall: ${tooSmall.map(t => `"${t.text}" ${t.height}px`).join(', ')}`,
        ).toEqual([]);
    });

    test('les boutons de l’écran de connexion aussi', async ({ page }) => {
        await page.goto('/');
        await expect(page.locator(SELECTORS.loginForm)).toBeVisible();

        const targets = await measureTapTargets(page, BUTTON_SELECTOR);
        expect(targets.length).toBeGreaterThanOrEqual(2);
        expect(targets.filter(target => target.height < MIN_TAP_PX)).toEqual([]);
    });
});

test.describe('Zoom des champs sur iOS', () => {
    test('aucun champ texte sous 16 px, connexion et tableau de bord', async ({ page }) => {
        const measure = async () => page.$$eval(TEXT_INPUT_SELECTOR, nodes => nodes.map(node => ({
            name: node.getAttribute('name') || node.getAttribute('placeholder') || node.tagName,
            fontSizePx: parseFloat(getComputedStyle(node).fontSize),
        })));

        await page.goto('/');
        await expect(page.locator(SELECTORS.loginForm)).toBeVisible();
        const onLogin = await measure();
        expect(onLogin.length).toBeGreaterThan(0);

        await login(page);
        await expect(page.locator(SELECTORS.uploadCard)).toBeVisible();
        const onDashboard = await measure();
        expect(onDashboard.length).toBeGreaterThan(0);

        // And the CRUD form, which is the only place type="number" and
        // type="date" inputs are rendered.
        await page.getByRole('button', { name: 'Mon Compte', exact: true }).click();
        await expect(page.getByRole('button', { name: 'Enregistrer les modifications' })).toBeVisible();
        const onAccount = await measure();

        const small = [...onLogin, ...onDashboard, ...onAccount]
            .filter(field => field.fontSizePx < MIN_INPUT_FONT_PX);
        expect(
            small,
            `under ${MIN_INPUT_FONT_PX}px: ${small.map(f => `${f.name}=${f.fontSizePx}px`).join(', ')}`,
        ).toEqual([]);
    });
});

test.describe('Contraste WCAG AA', () => {
    test('chaque élément mesuré atteint son seuil', async ({ page, api }) => {
        // Seed one job per terminal status so every chip variant really renders
        // from a job.status the API sends, rather than from a class we invented.
        api.jobs = [
            { id: 'job-done', user_id: api.user.id, file_name: 'termine.pdf', status: 'complete', progress: 100, created_at: new Date().toISOString(), committed: true, successes: [], failures: [] },
            { id: 'job-failed', user_id: api.user.id, file_name: 'echec.pdf', status: 'failed', progress: 100, created_at: new Date().toISOString(), committed: true, successes: [], failures: [] },
            { id: 'job-processing', user_id: api.user.id, file_name: 'encours.pdf', status: 'processing', progress: 40, created_at: new Date().toISOString(), startedAt: Date.now() + 600_000, successes: [], failures: [] },
        ];

        // Contrast is a property of the CSS rules, not of the viewport, but a
        // measurement is only honest on an element that is actually rendered —
        // and below 720 px the design system hides the table. Measure them all
        // at a width where every one of them is on screen.
        await page.setViewportSize({ width: 1024, height: 900 });

        await login(page);
        await expect(page.locator(SELECTORS.uploadCard)).toBeVisible();
        await expect(page.locator('.sid-chip--done')).toBeVisible();
        await expect(page.locator('.sid-table th').first()).toBeVisible();
        await expect(page.locator('.sid-badge--pp').first()).toBeVisible();

        // .sid-chip--queued has no data value behind it: the backend only ever
        // writes processing/complete/failed (backend/crud.py), and inventing a
        // status to render it is forbidden. The rule is still measured, on a
        // probe element placed in the same card context the chips live in.
        await page.evaluate(() => {
            const host = document.querySelector('.job-monitor');
            const probe = document.createElement('span');
            probe.className = 'sid-chip sid-chip--queued';
            probe.id = 'contrast-probe-queued';
            probe.textContent = 'En attente';
            host.appendChild(probe);
        });

        const dashboard = [
            '.sid-dropzone small', '.sid-topbar-right', '.sid-credits', '.sid-table th',
            '.sid-badge--pp', '.sid-badge--pi',
            '#contrast-probe-queued', '.sid-chip--processing', '.sid-chip--done', '.sid-chip--failed',
        ];
        const results = [];
        for (const selector of dashboard) results.push(await getComputedColorPair(page, selector));

        // .sid-empty needs a table with no rows; .sid-appfoot lives on login.
        api.passports = [];
        await page.reload();
        await expect(page.locator(SELECTORS.emptyState).first()).toBeVisible();
        results.push(await getComputedColorPair(page, '.sid-empty'));

        await page.getByRole('button', { name: TEXT.logout }).click();
        await expect(page.locator(SELECTORS.loginForm)).toBeVisible();
        results.push(await getComputedColorPair(page, '.sid-appfoot'));
        results.push(await getComputedColorPair(page, '.sid-appfoot a'));

        console.log('\n| element                        |  ratio   |  size | wgt. | AA  | verdict |');
        console.log('|--------------------------------|----------|-------|------|-----|---------|');
        for (const result of results) console.log(row(result));
        console.log('');

        const failures = results.filter(result => !result.passesAA);
        expect(
            failures.map(f => `${f.selector} ${f.ratio.toFixed(2)}:1 < ${f.aaThreshold}`),
        ).toEqual([]);
    });
});

test.describe('Navigation au clavier', () => {
    /** Focus style of the active element: an outline or a box-shadow ring. */
    const focusRing = page => page.evaluate(() => {
        const node = document.activeElement;
        if (!node || node === document.body) return null;
        const style = getComputedStyle(node);
        const outline = style.outlineStyle !== 'none' && parseFloat(style.outlineWidth) > 0;
        const ring = style.boxShadow !== 'none' && style.boxShadow !== '';
        return {
            tag: node.tagName.toLowerCase(),
            label: (node.textContent || node.getAttribute('placeholder') || '').trim().slice(0, 40),
            visible: outline || ring,
            outline: `${style.outlineStyle} ${style.outlineWidth}`,
            boxShadow: style.boxShadow,
        };
    });

    const tabThrough = async (page, steps) => {
        const seen = [];
        for (let i = 0; i < steps; i++) {
            await page.keyboard.press('Tab');
            const state = await focusRing(page);
            if (state) seen.push(state);
        }
        return seen;
    };

    test('chaque arrêt de tabulation sur la connexion montre un indicateur', async ({ page }) => {
        await page.goto('/');
        await expect(page.locator(SELECTORS.loginForm)).toBeVisible();

        const stops = await tabThrough(page, 8);
        expect(stops.length).toBeGreaterThan(3);

        const invisible = stops.filter(stop => !stop.visible);
        expect(
            invisible.map(s => `${s.tag} "${s.label}" outline=${s.outline} shadow=${s.boxShadow}`),
        ).toEqual([]);
    });

    test('chaque arrêt de tabulation sur l’import montre un indicateur', async ({ page }) => {
        await login(page);
        await uploadFiles(page, [fixturePath('smallJpeg')]);

        await page.locator(SELECTORS.destinationInput).focus();
        const stops = await tabThrough(page, 6);
        expect(stops.length).toBeGreaterThan(2);

        const invisible = stops.filter(stop => !stop.visible);
        expect(
            invisible.map(s => `${s.tag} "${s.label}" outline=${s.outline} shadow=${s.boxShadow}`),
        ).toEqual([]);
    });
});

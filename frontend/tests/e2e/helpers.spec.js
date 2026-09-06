// The helpers are infrastructure later packages build on, so they get their own
// coverage. These tests assert that each helper *reports correctly*; they make
// no claim about whether the app's colours, tap targets or storage use are good
// — that is for the packages that change them.
import { test, expect } from './test-base.js';
import {
    login, logout, getStorageState, isStorageEmpty, measureTapTargets, tapTargetsBelow,
    hasHorizontalOverflow, findOverflowingElements, getComputedColorPair, contrastRatio,
    SELECTORS,
} from '../helpers/index.js';

test.describe('helpers', () => {
    test('getStorageState reports every store, and says so when one is unreadable', async ({ page }) => {
        await page.goto('/');
        const before = await getStorageState(page);

        expect(before).toMatchObject({
            origin: expect.stringContaining('http'),
            localStorage: expect.any(Object),
            sessionStorage: expect.any(Object),
        });
        expect(Array.isArray(before.indexedDB)).toBe(true);
        expect(Array.isArray(before.cacheStorage)).toBe(true);
        expect(Array.isArray(before.serviceWorkers)).toBe(true);
        // An API the browser refuses to enumerate is named, never reported as empty.
        for (const name of before.unavailable) {
            expect(['localStorage', 'sessionStorage', 'indexedDB.databases', 'caches', 'serviceWorker'])
                .toContain(name);
        }

        await login(page);
        const afterLogin = await getStorageState(page);
        expect(afterLogin.localStorage).toHaveProperty('token');
        expect(afterLogin.localStorage.token).toBeTruthy();
        expect(isStorageEmpty(afterLogin)).toBe(false);

        await logout(page);
        const afterLogout = await getStorageState(page);
        expect(afterLogout.localStorage.token).toBeUndefined();
    });

    test('measureTapTargets returns a box per visible match, in DOM order', async ({ page }) => {
        await login(page);

        const targets = await measureTapTargets(page, SELECTORS.navButtons);
        expect(targets.length).toBeGreaterThan(0);

        for (const target of targets) {
            expect(target.tagName).toBe('button');
            expect(target.width).toBeGreaterThan(0);
            expect(target.height).toBeGreaterThan(0);
            expect(target.smallestSide).toBe(Math.min(target.width, target.height));
            expect(target.text.length).toBeGreaterThan(0);
        }
        expect(targets.map(target => target.index)).toEqual(targets.map((_, i) => i));

        // The filter is a plain predicate over the returned boxes.
        expect(tapTargetsBelow(targets, 0)).toHaveLength(0);
        expect(tapTargetsBelow(targets, 10_000)).toHaveLength(targets.length);

        // A selector that matches nothing yields an empty list, not an error.
        expect(await measureTapTargets(page, '.does-not-exist')).toEqual([]);
    });

    test('getComputedColorPair resolves a translucent background down to an opaque one', async ({ page }) => {
        await login(page);

        // .app-header is rgba(255,255,255,0.85) over the body colour, so this
        // only works if the helper composites the layers rather than returning
        // the declared value.
        const pair = await getComputedColorPair(page, '.app-header h1');

        expect(pair.background).toMatch(/^rgb\(\d+, \d+, \d+\)$/);
        expect(pair.foreground).toMatch(/^rgba?\(/);
        expect(pair.ratio).toBeCloseTo(contrastRatio(pair.foreground, pair.background), 10);
        expect(pair.fontSizePx).toBeGreaterThan(0);
        expect(typeof pair.isLargeText).toBe('boolean');
        expect(pair.aaThreshold).toBe(pair.isLargeText ? 3 : 4.5);
        expect(pair.passesAA).toBe(pair.ratio >= pair.aaThreshold);

        // White button text on the indigo primary must resolve to that indigo.
        const button = await getComputedColorPair(page, '.btn-primary');
        expect(button.background).not.toBe('rgb(255, 255, 255)');
        expect(button.ratio).toBeGreaterThan(1);

        await expect(getComputedColorPair(page, '.nope')).rejects.toThrow(/no element matches/);
    });

    test('the overflow helpers describe the layout without judging it', async ({ page }) => {
        await login(page);

        expect(typeof await hasHorizontalOverflow(page)).toBe('boolean');

        const offenders = await findOverflowingElements(page);
        expect(Array.isArray(offenders)).toBe(true);
        for (const offender of offenders) {
            expect(offender.right).toBeGreaterThan(offender.viewportWidth);
            expect(typeof offender.selector).toBe('string');
        }
    });
});

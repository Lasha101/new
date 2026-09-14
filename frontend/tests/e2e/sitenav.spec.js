// The public site's menu inside the app (action list item 8, Spec v2 §2):
// Présentation, Ressources, Tarifs, FAQ, Contact in the top bar, the logo back
// to https://scanid.fr/, and the same links under « Retour au site » on phones.
import { test, expect } from './test-base.js';
import {
    login, getComputedColorPair, hasHorizontalOverflow, findOverflowingElements, SELECTORS, TEXT, APP_BASE,
} from '../helpers/index.js';

const SITE_LINKS = [
    ['Présentation', 'https://scanid.fr/presentation.html'],
    ['Ressources', 'https://scanid.fr/ressources.html'],
    ['Tarifs', 'https://scanid.fr/#tarifs'],
    ['FAQ', 'https://scanid.fr/faq.html'],
    ['Contact', 'https://scanid.fr/contact.html'],
];

/** [text, href] of every link inside `locator`, in order. */
const linksOf = locator => locator.locator('a').evaluateAll(
    anchors => anchors.map(a => [a.textContent.trim(), a.getAttribute('href')]),
);

const DESKTOP = { width: 1280, height: 800 };
const PHONE = { width: 375, height: 667 };

test.describe('Menu du site dans la barre de l’application', () => {
    test('bureau : le logo mène au site et les cinq liens sont dans la barre, connecté ou non', async ({ page }) => {
        await page.setViewportSize(DESKTOP);
        await page.goto(APP_BASE);
        await expect(page.locator(SELECTORS.loginForm)).toBeVisible();

        const topbar = page.locator(SELECTORS.topbar);
        await expect(topbar.locator(`${SELECTORS.logo} a`)).toHaveAttribute('href', 'https://scanid.fr/');
        await expect(topbar.locator(SELECTORS.logo)).toHaveText('ScanID');
        const nav = topbar.getByRole('navigation', { name: 'Site ScanID' });
        await expect(nav).toBeVisible();
        expect(await linksOf(nav)).toEqual(SITE_LINKS);
        await expect(topbar.locator('.sid-sitemenu')).toBeHidden();

        await login(page);
        await expect(nav).toBeVisible();
        expect(await linksOf(nav)).toEqual(SITE_LINKS);
        // « Déconnexion » stays at the right end of the bar, after the links.
        const logout = topbar.locator(SELECTORS.logoutButton);
        await expect(logout).toHaveText(TEXT.logout);
        const [navBox, logoutBox] = [await nav.boundingBox(), await logout.boundingBox()];
        expect(logoutBox.x).toBeGreaterThan(navBox.x + navBox.width);
    });

    test('mobile : les liens sont regroupés sous « Retour au site »', async ({ page }) => {
        await page.setViewportSize(PHONE);
        await login(page);

        const topbar = page.locator(SELECTORS.topbar);
        await expect(topbar.locator('.sid-sitenav')).toBeHidden();
        const summary = topbar.getByText('Retour au site', { exact: true });
        await expect(summary).toBeVisible();
        const panel = topbar.locator('.sid-sitemenu__panel');
        await expect(panel).toBeHidden();
        await expect(topbar.locator(SELECTORS.logoutButton)).toBeVisible();

        await summary.click();
        await expect(panel).toBeVisible();
        expect(await linksOf(panel)).toEqual(SITE_LINKS);
        for (const [name] of SITE_LINKS) await expect(panel.getByRole('link', { name, exact: true })).toBeVisible();
        // The panel spans the screen under the bar, and nothing overflows.
        const box = await panel.boundingBox();
        expect(box.x).toBeGreaterThanOrEqual(0);
        expect(box.x + box.width).toBeLessThanOrEqual(PHONE.width);

        await page.keyboard.press('Escape');
        await expect(panel).toBeHidden();
        await expect(summary).toBeFocused();

        await summary.click();
        await expect(panel).toBeVisible();
        // A tap anywhere outside the menu (low on the screen, below the panel).
        await page.mouse.click(PHONE.width / 2, PHONE.height - 20);
        await expect(panel).toBeHidden();
    });

    test('360 px : ni la barre ni le menu ouvert ne débordent, connecté ou non', async ({ page }) => {
        await page.setViewportSize({ width: 360, height: 640 });
        await page.goto(APP_BASE);
        await expect(page.locator(SELECTORS.loginForm)).toBeVisible();
        await page.getByText('Retour au site', { exact: true }).click();
        await expect(page.locator('.sid-sitemenu__panel')).toBeVisible();
        expect(await findOverflowingElements(page)).toEqual([]);
        expect(await hasHorizontalOverflow(page)).toBe(false);

        await page.keyboard.press('Escape');
        await login(page);
        await page.getByText('Retour au site', { exact: true }).click();
        await expect(page.locator('.sid-sitemenu__panel')).toBeVisible();
        expect(await findOverflowingElements(page)).toEqual([]);
        expect(await hasHorizontalOverflow(page)).toBe(false);
    });

    test('les liens se lisent sur la barre (AA) et montrent un indicateur de focus', async ({ page }) => {
        await page.setViewportSize(DESKTOP);
        await page.goto(APP_BASE);
        await expect(page.locator(SELECTORS.loginForm)).toBeVisible();

        const inline = await getComputedColorPair(page, '.sid-sitenav a');
        expect(inline.passesAA, `${inline.ratio.toFixed(2)}:1`).toBe(true);

        const outlineOf = locator => locator.evaluate((node) => {
            const style = getComputedStyle(node);
            return document.activeElement === node && style.outlineStyle !== 'none' && parseFloat(style.outlineWidth) > 0;
        });
        await page.locator(`${SELECTORS.logo} a`).focus();
        await page.keyboard.press('Tab');
        const first = page.locator('.sid-sitenav a').first();
        await expect(first).toBeFocused();
        expect(await outlineOf(first)).toBe(true);

        await page.setViewportSize(PHONE);
        const summary = page.locator('.sid-sitemenu summary');
        await summary.focus();
        await page.keyboard.press('Enter');
        await expect(page.locator('.sid-sitemenu__panel')).toBeVisible();
        expect(await outlineOf(summary)).toBe(true);
        const menu = await getComputedColorPair(page, '.sid-sitemenu__panel a');
        expect(menu.passesAA, `${menu.ratio.toFixed(2)}:1`).toBe(true);
    });
});

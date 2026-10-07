// The four failure alerts put a space before the colon, as French does — a
// no-break one (U+00A0), so the colon never starts a line (Alex, 07/10/2026).
// Each failure is forced on the network and the dialog's text is compared
// exactly: a plain space, or no space at all, fails.
import { test, expect, LIVE } from './test-base.js';
import { login, resultsTable, TEXT } from '../helpers/index.js';

// The selection checkboxes and the « Supprimer » / « Exporter la sélection »
// buttons are the table's, as in features.spec.js: a desktop width in every
// project.
test.use({ viewport: { width: 1280, height: 900 } });

const NBSP = '\u00A0';
const REFUSED = { status: 400, contentType: 'application/json', body: JSON.stringify({ detail: 'Refus de test' }) };

/** Accepts every dialog (the confirm() first, then the alert) and keeps their texts. */
const recordDialogs = page => {
    const messages = [];
    page.on('dialog', dialog => { messages.push(dialog.message()); dialog.accept(); });
    return messages;
};

const selectFirstRow = page => resultsTable(page).locator('tbody tr').first().locator('input[type="checkbox"]').check();

test.describe('Messages d’erreur : une espace insécable avant les deux-points', () => {
    test.skip(LIVE, 'force une réponse d’erreur à la place du serveur');

    test('suppression multiple refusée', async ({ page }) => {
        await login(page);
        await page.route(url => url.pathname.endsWith('/passports/delete-multiple'), route => route.fulfill(REFUSED));
        const messages = recordDialogs(page);
        await selectFirstRow(page);
        await page.getByRole('button', { name: 'Supprimer (1)' }).click();
        await expect.poll(() => messages.at(-1)).toBe(`Échec de la suppression multiple${NBSP}: Refus de test`);
    });

    test('suppression multiple sans réseau', async ({ page }) => {
        await login(page);
        await page.route(url => url.pathname.endsWith('/passports/delete-multiple'), route => route.abort());
        const messages = recordDialogs(page);
        await selectFirstRow(page);
        await page.getByRole('button', { name: 'Supprimer (1)' }).click();
        // What follows the colon is the browser's own wording (« Failed to fetch », « Load failed »).
        await expect.poll(() => messages.at(-1)).toMatch(new RegExp(`^Une erreur est survenue${NBSP}: \\S`));
    });

    test('« Aperçu » refusé', async ({ page }) => {
        await login(page);
        await page.route(url => url.pathname.endsWith('/export/data'), route => route.fulfill(REFUSED));
        const messages = recordDialogs(page);
        await page.getByRole('button', { name: TEXT.preview }).click();
        await expect.poll(() => messages.at(-1)).toBe(`Échec de la récupération des données${NBSP}: Refus de test`);
    });

    test('export de la sélection refusé', async ({ page }) => {
        await login(page);
        await page.route(url => url.pathname.endsWith('/export/data/selection'), route => route.fulfill(REFUSED));
        const messages = recordDialogs(page);
        await selectFirstRow(page);
        await page.getByRole('button', { name: 'Exporter la sélection en Excel (1)' }).click();
        await expect.poll(() => messages.at(-1)).toBe(`Échec de l'exportation${NBSP}: Refus de test`);
    });
});

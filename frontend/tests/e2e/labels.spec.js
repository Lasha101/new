// Alex's « third check » (02/10/2026): the app's labels in sentence case, as on
// scanid.fr — « Mon compte », « Modifier mon compte », « Gérer les
// utilisateurs », « Filtrer par utilisateur / destination », « Modifier la
// destination », « Exportation des données », « Exporter la sélection en
// Excel / CSV (n) » — and the first tab named like the screen it opens,
// « Mes documents ». His « sentence case everywhere » also covers four labels
// the table does not list: the upload card's « Destination (optionnel) » and
// « Document (image ou PDF) » (as the app mock-ups on scanid.fr write them),
// the users search « Rechercher (nom, e-mail...) » and the sort tooltip.
//
// Every check is case-sensitive on purpose: `filter({ hasText })` and a
// non-exact `name` ignore case, so they would pass with the old labels too.
import { test, expect, LIVE } from './test-base.js';
import { login, resultsRows, resultsTable, hasHorizontalOverflow, SELECTORS } from '../helpers/index.js';

const MOCK_ONLY = 'pilote l’état du mock (api.*) : sur un vrai backend il n’y a pas de mock à piloter';

/** The labels the note replaced, as they were written. None may come back. */
const OLD_LABELS = [
    '>Passeports<', 'Mon Compte', 'Gérer les Utilisateurs', 'Filtrer par Utilisateur', 'Filtrer par Destination',
    'Modifier Destination', 'Exportation des Données', 'Exporter Sélection', 'Destination (Optionnel)',
    'Document (Image ou PDF)', 'Rechercher (Nom', 'Activer/Désactiver',
];

/** Every old label still in the screen's markup, text and attributes alike. */
const oldLabelsIn = async page => {
    const markup = await page.content();
    return OLD_LABELS.filter(label => markup.includes(label));
};

const tabs = page => page.locator(SELECTORS.navButtons);

test.describe('Libellés en casse de phrase (Alex, troisième contrôle)', () => {
    test('client : onglets, import, export, sélection et « Mon compte »', async ({ page }) => {
        test.skip(LIVE, 'sélectionne une ligne du jeu de données du mock');
        await login(page);

        // The first tab is named like the screen it opens, and is the one open.
        await expect(tabs(page)).toHaveText(['Mes documents', 'Mon compte']);
        await expect(tabs(page).first()).toHaveClass(/active/);
        await expect(page.getByRole('heading', { name: 'Mes documents', exact: true })).toBeVisible();

        // « Ajouter un document », as scanid.fr's mock-ups of the app write it.
        const uploadForm = page.locator('form').filter({ has: page.locator(SELECTORS.uploadCard) });
        await expect(uploadForm.locator('.sid-label')).toHaveText(['Destination (optionnel)', 'Document (image ou PDF)']);

        await expect(page.getByRole('heading', { name: 'Exportation des données', exact: true })).toBeVisible();
        await expect(page.locator('input[name="destination_filter"]')).toHaveAttribute('placeholder', 'Filtrer par destination');
        // Both result views are always mounted: the table header is there at every width.
        await expect(resultsTable(page).locator('thead .sort-checkbox').first())
            .toHaveAttribute('title', 'Activer/désactiver le tri sur cette colonne');

        // A selection: its buttons. The export pair is compared on textContent —
        // the accessible name would also carry the CSS « ⬇ » before each label.
        await resultsRows(page).first().locator('input[type="checkbox"]').first().check();
        await expect(page.getByRole('button', { name: 'Modifier la destination', exact: true })).toBeVisible();
        await expect(page.locator(SELECTORS.downloadGroup).locator('button'))
            .toHaveText(['Exporter la sélection en Excel (1)', 'Exporter la sélection en CSV (1)']);
        // The longer labels still fit a phone: they wrap, the page does not scroll sideways.
        expect(await hasHorizontalOverflow(page)).toBe(false);
        expect(await oldLabelsIn(page)).toEqual([]);

        await tabs(page).filter({ hasText: /^Mon compte$/ }).click();
        await expect(page.getByRole('heading', { name: 'Modifier mon compte', exact: true })).toBeVisible();
        expect(await oldLabelsIn(page)).toEqual([]);
    });

    test('administrateur : filtres et « Gérer les utilisateurs »', async ({ page, api }) => {
        test.skip(LIVE, MOCK_ONLY);
        api.user.role = 'admin';
        await login(page);

        await expect(tabs(page)).toHaveText(['Mes documents', 'Administration', "Demandes d'essai", 'Factures', 'Mon compte']);
        await expect(page.locator('input[name="user_filter"]')).toHaveAttribute('placeholder', 'Filtrer par utilisateur');
        await expect(page.locator('input[name="voyage_filter"]')).toHaveAttribute('placeholder', 'Filtrer par destination');
        expect(await oldLabelsIn(page)).toEqual([]);

        await tabs(page).filter({ hasText: /^Administration$/ }).click();
        await expect(page.getByRole('heading', { name: 'Gérer les utilisateurs', exact: true })).toBeVisible();
        await expect(page.locator('input[name="name_filter"]')).toHaveAttribute('placeholder', 'Rechercher (nom, e-mail...)');
        expect(await oldLabelsIn(page)).toEqual([]);
    });
});

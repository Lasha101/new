// Everything the app could already do, exercised end to end.
//
// Package A changed markup and class names across every screen. The baseline
// suite covers login, the type filter, upload and the two downloads; this file
// covers the rest — sorting, selection, bulk edit, multi-delete, manual create,
// edit, job removal, the export preview, selection exports, the password toggle
// and self-registration — so "nothing else broke" is a result, not a claim.
import { test, expect, LIVE } from './test-base.js';
import {
    login, uploadFiles, resultsTable, resultsRows, countResultRows,
    SELECTORS, TEXT, APP_BASE } from '../helpers/index.js';
import { fixturePath } from '../fixtures/index.js';

// Sorting and select-all live in the TABLE header, which the design system
// replaces with the card list below 720 px. These specs therefore run at a
// desktop width in every browser project — that keeps the cross-browser
// coverage (WebKit included) while driving the view the controls belong to.
// What the cards can and cannot do on a phone is covered at the bottom of this
// file, deliberately and separately.
test.use({ viewport: { width: 1280, height: 900 } });

/** Text of one results column, top to bottom, as the table shows it. */
const selectAll = page => resultsTable(page).locator('thead .checkbox-cell input[type="checkbox"]');

/**
 * Text of one results column, top to bottom.
 *
 * NOTE: this is `textContent`, i.e. the value the app renders — the uppercase
 * look comes from `text-transform` in CSS and never reaches the DOM. That the
 * cells *display* uppercase is asserted separately, on computed styles, in
 * responsive.spec.js.
 */
const columnValues = (page, field) => resultsTable(page)
    .locator(`tbody td[data-field="${field}"]`)
    .evaluateAll(cells => cells.map(cell => (cell.textContent || '').trim()));

/** The header cell of one column (the whole <th>, which is the click target). */
const header = (page, field, label) => resultsTable(page)
    .locator('thead th').filter({ hasText: label });

test.describe('Tri du tableau', () => {
    test('cocher une colonne trie, recliquer inverse le sens', async ({ page }) => {
        await login(page);
        const unsorted = await columnValues(page, 'last_name');
        expect(unsorted.length).toBeGreaterThan(2);

        // The checkbox in the header adds the column to the sort stack.
        await header(page, 'last_name', 'Nom de famille').locator('.sort-checkbox').check();
        const ascending = await columnValues(page, 'last_name');
        expect(ascending).toEqual([...ascending].sort((a, b) => a.localeCompare(b)));

        // Clicking the header text toggles the direction.
        await header(page, 'last_name', 'Nom de famille').click();
        const descending = await columnValues(page, 'last_name');
        expect(descending).toEqual([...ascending].reverse());

        // Unchecking removes it from the stack.
        await header(page, 'last_name', 'Nom de famille').locator('.sort-checkbox').uncheck();
        expect(await columnValues(page, 'last_name')).toEqual(unsorted);
    });

    test('le tri multi-colonnes numérote les priorités', async ({ page }) => {
        await login(page);
        await header(page, 'nationality', 'Nationalité').locator('.sort-checkbox').check();
        await header(page, 'last_name', 'Nom de famille').locator('.sort-checkbox').check();

        // Two active columns => each shows its own rank, in the order they were
        // checked (nationality first), not in column order.
        await expect(resultsTable(page).locator('.sort-badge small')).toHaveCount(2);
        await expect(header(page, 'nationality', 'Nationalité').locator('.sort-badge small'))
            .toHaveText('1');
        await expect(header(page, 'last_name', 'Nom de famille').locator('.sort-badge small'))
            .toHaveText('2');

        // Nationality is uniform in the fixture, so last_name decides the order.
        const names = await columnValues(page, 'last_name');
        expect(names).toEqual([...names].sort((a, b) => a.localeCompare(b)));
    });

    test('le tri par date utilise la valeur stockée, pas le texte affiché', async ({ page }) => {
        await login(page);
        await header(page, 'birth_date', 'Date de Naissance').locator('.sort-checkbox').check();

        // Displayed DD/MM/YYYY, but sorted on the ISO value behind it: sorting
        // the *strings* would put 03/11/1982 before 09/07/2001 before 17/05/1990.
        const shown = await columnValues(page, 'birth_date');
        const asIso = shown.map(value => value.split('/').reverse().join('-'));
        expect(asIso).toEqual([...asIso].sort());
    });
});

test.describe('Sélection de lignes', () => {
    test('tout sélectionner, désélectionner, et le compteur suit', async ({ page }) => {
        await login(page);
        const total = await countResultRows(page);
        const selectAllBox = selectAll(page);

        await selectAllBox.check();
        await expect(page.getByRole('button', { name: `Supprimer (${total})` })).toBeVisible();
        await expect(resultsTable(page).locator('tbody tr.selected-row')).toHaveCount(total);

        await selectAllBox.uncheck();
        await expect(page.getByRole('button', { name: /^Supprimer \(/ })).toHaveCount(0);
        await expect(resultsTable(page).locator('tbody tr.selected-row')).toHaveCount(0);
    });

    test('changer de filtre vide la sélection', async ({ page }) => {
        await login(page);
        await resultsTable(page).locator('tbody tr').first().locator('input[type="checkbox"]').check();
        await expect(page.getByRole('button', { name: /^Supprimer \(1\)$/ })).toBeVisible();

        await page.locator(SELECTORS.typeFilter).locator('button[value="PI"]').click();
        await expect(page.getByRole('button', { name: /^Supprimer \(/ })).toHaveCount(0);
    });
});

test.describe('Actions groupées', () => {
    test('la modification groupée de destination écrit chaque ligne', async ({ page, api }) => {
        test.skip(LIVE, 'pilote l’état du mock (api.*) : sur un vrai backend il n’y a pas de mock à piloter');
        await login(page);
        await selectAll(page).check();

        await page.getByRole('button', { name: 'Modifier Destination' }).click();
        await page.getByPlaceholder('Nouvelle destination').fill('Lisbonne 2027');
        await page.getByRole('button', { name: 'OK', exact: true }).click();

        await expect.poll(() => columnValues(page, 'destination'), { timeout: 10_000 })
            .toEqual(Array(api.passports.length).fill('Lisbonne 2027'));
        for (const row of api.passports) expect(row.destination).toBe('Lisbonne 2027');
    });

    test('la suppression multiple retire les lignes choisies', async ({ page }) => {
        await login(page);
        const before = await countResultRows(page);

        await resultsTable(page).locator('tbody tr').first().locator('input[type="checkbox"]').check();
        await resultsTable(page).locator('tbody tr').nth(1).locator('input[type="checkbox"]').check();

        page.once('dialog', dialog => {
            expect(dialog.message()).toContain('2 passeports');
            dialog.accept();
        });
        await page.getByRole('button', { name: 'Supprimer (2)' }).click();

        await expect.poll(() => countResultRows(page), { timeout: 10_000 }).toBe(before - 2);
    });
});

test.describe('Création et modification manuelles', () => {
    test('« + Manuel » crée une ligne qui apparaît dans le tableau', async ({ page }) => {
        test.skip(LIVE, 'suppose un jeu de lignes intact : en live la base est partagée par toute la série, un test qui crée ou supprime des lignes change ce que celui-ci voit ; le mock est réinitialisé à chaque test');
        await login(page);
        const before = await countResultRows(page);

        await page.getByRole('button', { name: '+ Manuel' }).click();
        await expect(page.getByRole('heading', { name: 'Créer' })).toBeVisible();

        for (const [name, value] of [
            ['first_name', 'Manuelle'], ['last_name', 'Saisie'], ['nationality', 'Française'],
            ['passport_number', '55QQ11111'], ['birth_date', '1995-03-08'],
            ['expiration_date', '2031-12-31'],
        ]) {
            await page.locator(`input[name="${name}"]`).fill(value);
        }
        await page.getByRole('button', { name: 'Enregistrer' }).click();

        await expect.poll(() => countResultRows(page), { timeout: 10_000 }).toBe(before + 1);
        expect(await columnValues(page, 'last_name')).toContain('Saisie');
        // The derived Type column classified it from the number it was given.
        const badge = resultsTable(page).locator('tbody tr').first()
            .locator('td[data-field="document_type"] .sid-badge');
        await expect(badge).toHaveText('PP');
    });

    test('« Modifier » ouvre la ligne pré-remplie et enregistre', async ({ page, api }) => {
        test.skip(LIVE, 'pilote l’état du mock (api.*) : sur un vrai backend il n’y a pas de mock à piloter');
        await login(page);
        await resultsTable(page).locator('tbody tr').first()
            .getByRole('button', { name: 'Modifier' }).click();

        await expect(page.getByRole('heading', { name: 'Modifier' })).toBeVisible();
        const firstName = page.locator('input[name="first_name"]');
        await expect(firstName).toHaveValue(api.passports[0].first_name);

        await firstName.fill('Renommée');
        await page.getByRole('button', { name: 'Enregistrer' }).click();

        await expect.poll(() => columnValues(page, 'first_name'), { timeout: 10_000 })
            .toContain('Renommée');
        expect(api.passports[0].first_name).toBe('Renommée');
    });

    test('« Annuler » revient au tableau sans rien écrire', async ({ page, api }) => {
        test.skip(LIVE, 'pilote l’état du mock (api.*) : sur un vrai backend il n’y a pas de mock à piloter');
        await login(page);
        const original = api.passports[0].first_name;

        await resultsTable(page).locator('tbody tr').first()
            .getByRole('button', { name: 'Modifier' }).click();
        await page.locator('input[name="first_name"]').fill('Jetable');
        await page.getByRole('button', { name: 'Annuler' }).click();

        await expect(resultsTable(page)).toBeVisible();
        expect(api.passports[0].first_name).toBe(original);
    });
});

test.describe('Moniteur de jobs', () => {
    test('le bouton X supprime le job après confirmation', async ({ page, api }) => {
        test.skip(LIVE, 'pilote l’état du mock (api.*) : sur un vrai backend il n’y a pas de mock à piloter');
        api.jobs = [{
            id: 'job-x', user_id: api.user.id, file_name: 'a-supprimer.pdf', status: 'complete',
            progress: 100, created_at: new Date().toISOString(), committed: true,
            successes: [], failures: [],
        }];
        await login(page);
        await expect(page.locator(SELECTORS.jobItem)).toHaveCount(1);

        page.once('dialog', dialog => {
            expect(dialog.message()).toContain('supprimer ce job');
            dialog.accept();
        });
        await page.locator(SELECTORS.jobItem).getByRole('button', { name: 'Supprimer ce job' }).click();

        await expect(page.locator(SELECTORS.jobItem)).toHaveCount(0);
        expect(api.jobs).toHaveLength(0);
    });

    test('les échecs d’une page sont listés sous la barre', async ({ page, api }) => {
        test.skip(LIVE, 'pilote l’état du mock (api.*) : sur un vrai backend il n’y a pas de mock à piloter');
        api.jobs = [{
            id: 'job-f', user_id: api.user.id, file_name: 'partiel.pdf', status: 'complete',
            progress: 100, created_at: new Date().toISOString(), committed: true,
            successes: [], failures: [{ page_number: 3, detail: 'MRZ illisible' }],
        }];
        await login(page);

        await expect(page.locator('.failure-list')).toContainText('Échecs détectés (1)');
        await expect(page.locator('.failure-item')).toContainText('Page 3');
        await expect(page.locator('.failure-item')).toContainText('MRZ illisible');
    });

    test('l’envoi peut être annulé pendant qu’il est en vol', async ({ page }) => {
        await login(page);
        await uploadFiles(page, [fixturePath('largeLandscapeJpeg')]);

        await page.getByRole('button', { name: TEXT.startAnalysis }).click();
        // While in flight the submit is disabled and the other button cancels.
        const cancel = page.getByRole('button', { name: "Annuler l'envoi" });
        if (await cancel.count() > 0) {
            await cancel.click();
            await expect(page.getByRole('button', { name: TEXT.startAnalysis })).toBeEnabled();
        }
        // Either way the form recovered and no crash occurred.
        await expect(page.locator(SELECTORS.uploadCard)).toBeVisible();
    });
});

test.describe('Panneau d’exportation', () => {
    test('« Aperçu » affiche un tableau d’aperçu au-dessus des résultats', async ({ page }) => {
        await login(page);
        await page.getByRole('button', { name: TEXT.preview }).click();

        const preview = page.locator('.sid-table-wrap').first();
        await expect(preview).toBeVisible();
        await expect(preview).toContainText('Nom de famille');
        // The preview is its own table, not the results one.
        await expect(page.locator('.sid-table-wrap')).toHaveCount(2);
        await expect(page.getByRole('heading', { name: 'Aperçu' })).toBeVisible();
    });

    test('avec une sélection, les boutons exportent la sélection', async ({ page }) => {
        await login(page);
        await resultsTable(page).locator('tbody tr').first().locator('input[type="checkbox"]').check();

        await expect(page.getByRole('button', { name: 'Exporter Sélection Excel (1)' })).toBeVisible();
        await expect(page.getByRole('button', { name: 'Exporter Sélection CSV (1)' })).toBeVisible();
        // Aperçu is disabled while a selection is active, as before.
        await expect(page.getByRole('button', { name: TEXT.preview })).toBeDisabled();

        const download = page.waitForEvent('download', { timeout: 30_000 });
        await page.getByRole('button', { name: 'Exporter Sélection CSV (1)' }).click();
        expect((await download).suggestedFilename()).toMatch(/\.csv$/);
    });

    test('le filtre de type se propage à la requête d’export', async ({ page, api }) => {
        test.skip(LIVE, 'pilote l’état du mock (api.*) : sur un vrai backend il n’y a pas de mock à piloter');
        await login(page);
        await page.locator(SELECTORS.typeFilter).locator('button[value="PI"]').click();

        const download = page.waitForEvent('download', { timeout: 30_000 });
        await page.getByRole('button', { name: TEXT.downloadCsv }).click();
        await download;

        const exportCall = api.requests.filter(r => r.path === '/export/data').pop();
        expect(exportCall.search).toContain('document_type=PI');
        expect(exportCall.search).toContain('format=csv');
    });
});

test.describe('Formulaires', () => {
    test('l’œil affiche et masque le mot de passe', async ({ page }) => {
        await page.goto(APP_BASE);
        const field = page.locator(SELECTORS.passwordInput);
        await field.fill('secret-visible');
        await expect(field).toHaveAttribute('type', 'password');

        await page.getByRole('button', { name: 'Afficher le mot de passe' }).click();
        await expect(field).toHaveAttribute('type', 'text');

        await page.getByRole('button', { name: 'Cacher le mot de passe' }).click();
        await expect(field).toHaveAttribute('type', 'password');
    });

    test('l’inscription aboutit et signale un identifiant déjà pris', async ({ page }) => {
        await page.goto(APP_BASE);
        await page.getByRole('button', { name: 'Créer un compte' }).click();
        await expect(page.getByRole('heading', { name: 'Créer un nouveau compte' })).toBeVisible();

        const fill = async (values) => {
            for (const [name, value] of Object.entries(values)) {
                await page.locator(`input[name="${name}"]`).fill(value);
            }
        };
        // The username the mock already owns => the server's French error shows.
        await fill({
            first_name: 'Nouvelle', last_name: 'Agence', email: 'nouvelle@example.com',
            // Conforme à la politique du paquet C (12+, 1 majuscule, 2 chiffres,
            // 2 spéciaux) : ce test porte sur les conflits d'identifiant,
            // pas sur le mot de passe.
            phone_number: '0601020304', user_name: 'alice', password: 'Girafe!!12Nuage',
        });
        await page.getByRole('button', { name: "S'inscrire" }).click();
        await expect(page.locator(SELECTORS.errorMessage))
            .toHaveText("Nom d'utilisateur déjà enregistré");

        // A free username succeeds.
        await fill({ user_name: 'agence-lyon' });
        await page.getByRole('button', { name: "S'inscrire" }).click();
        await expect(page.locator('.sid-alert--ok')).toContainText('Inscription réussie');
    });

    test('« Mon Compte » se pré-remplit et enregistre', async ({ page, api }) => {
        test.skip(LIVE, 'pilote l’état du mock (api.*) : sur un vrai backend il n’y a pas de mock à piloter');
        await login(page);
        await page.getByRole('button', { name: 'Mon Compte', exact: true }).click();

        await expect(page.locator('input[name="first_name"]')).toHaveValue(api.user.first_name);
        await expect(page.locator('input[name="email"]')).toHaveValue(api.user.email);
        // Counters stay read-only for a non-admin, as before.
        await expect(page.locator('input[name="page_credits"]')).toBeDisabled();

        await page.locator('input[name="phone_number"]').fill('0699887766');
        await page.getByRole('button', { name: 'Enregistrer les modifications' }).click();
        await expect(page.locator('.sid-alert--ok')).toContainText('Compte mis à jour');
        expect(api.user.phone_number).toBe('0699887766');
    });
});

test.describe('Navigation et session', () => {
    test('les onglets changent de contenu et gardent l’état actif', async ({ page }) => {
        await login(page);
        await expect(page.locator(SELECTORS.uploadCard)).toBeVisible();

        await page.getByRole('button', { name: 'Mon Compte', exact: true }).click();
        await expect(page.getByRole('heading', { name: 'Modifier Mon Compte' })).toBeVisible();
        await expect(page.locator(SELECTORS.uploadCard)).toHaveCount(0);

        await page.getByRole('button', { name: 'Passeports', exact: true }).click();
        await expect(page.locator(SELECTORS.uploadCard)).toBeVisible();
        await expect(resultsRows(page).first()).toBeVisible();
    });

    test('la déconnexion vide le jeton et revient à la connexion', async ({ page }) => {
        await login(page);
        await page.getByRole('button', { name: TEXT.logout }).click();

        await expect(page.locator(SELECTORS.loginForm)).toBeVisible();
        expect(await page.evaluate(() => localStorage.getItem('token'))).toBeNull();
        await expect(page.locator(SELECTORS.creditBadge)).toHaveCount(0);
    });

    test('la liste de destinations alimente le champ d’import', async ({ page }) => {
        test.skip(LIVE, 'suppose un jeu de lignes intact : en live la base est partagée par toute la série, un test qui crée ou supprime des lignes change ce que celui-ci voit ; le mock est réinitialisé à chaque test');
        await login(page);
        const listId = await page.locator(SELECTORS.destinationInput).getAttribute('list');
        const options = page.locator(`#${listId} option`);
        await expect(options.first()).toBeAttached();
        const values = await options.evaluateAll(nodes => nodes.map(n => n.value));
        expect(values).toContain('Rome');
    });
});

test.describe('Ce que les cartes permettent sur mobile', () => {
    test.use({ viewport: { width: 375, height: 800 } });

    test('sélection ligne par ligne, puis suppression multiple', async ({ page }) => {
        await login(page);
        const cards = page.locator(SELECTORS.cardItem);
        await expect(cards.first()).toBeVisible();
        const before = await cards.count();

        await cards.nth(0).locator('input[type="checkbox"]').check();
        await cards.nth(1).locator('input[type="checkbox"]').check();
        await expect(page.getByRole('button', { name: 'Supprimer (2)' })).toBeVisible();

        page.once('dialog', dialog => dialog.accept());
        await page.getByRole('button', { name: 'Supprimer (2)' }).click();
        await expect.poll(() => cards.count(), { timeout: 10_000 }).toBe(before - 2);
    });

    test('« Modifier » depuis une carte ouvre le même formulaire', async ({ page, api }) => {
        test.skip(LIVE, 'pilote l’état du mock (api.*) : sur un vrai backend il n’y a pas de mock à piloter');
        await login(page);
        await page.locator(SELECTORS.cardItem).first()
            .getByRole('button', { name: 'Modifier' }).click();

        await expect(page.getByRole('heading', { name: 'Modifier' })).toBeVisible();
        await expect(page.locator('input[name="first_name"]'))
            .toHaveValue(api.passports[0].first_name);
    });

    test('la modification groupée de destination marche depuis les cartes', async ({ page, api }) => {
        test.skip(LIVE, 'pilote l’état du mock (api.*) : sur un vrai backend il n’y a pas de mock à piloter');
        await login(page);
        await page.locator(SELECTORS.cardItem).first().locator('input[type="checkbox"]').check();

        await page.getByRole('button', { name: 'Modifier Destination' }).click();
        await page.getByPlaceholder('Nouvelle destination').fill('Porto');
        await page.getByRole('button', { name: 'OK', exact: true }).click();

        await expect.poll(() => api.passports[0].destination, { timeout: 10_000 }).toBe('Porto');
    });

    test('le tri et « tout sélectionner » ne sont PAS atteignables sur mobile', async ({ page }) => {
        // Documented consequence of the stacked-card decision: both controls
        // live in the table header, which is display:none here. Recorded as a
        // fact so a later package that adds them has a test to flip, and so the
        // gap cannot be mistaken for an accident. See SCANID-HANDOVER.md.
        await login(page);
        await expect(page.locator(SELECTORS.cardList)).toBeVisible();

        // Nine sort checkboxes exist in the DOM, one per column; none is visible.
        await expect(page.locator('.sort-checkbox')).toHaveCount(9);
        await expect(page.locator('.sort-checkbox:visible')).toHaveCount(0);
        await expect(selectAll(page)).toBeHidden();
    });
});

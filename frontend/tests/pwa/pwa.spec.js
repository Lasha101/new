// Package B — manifeste, service worker, écran hors ligne, et ce qui reste sur
// l'appareil après une session complète.
//
// CETTE SUITE TOURNE SUR L'APPLICATION CONSTRUITE (`vite preview`, projet
// « pwa » dans playwright.config.js). Le service worker, le manifeste et les
// icônes n'existent qu'après un build, et un worker devant le serveur de
// développement masquerait le HMR. Le reste des suites reste sur le dev server.
import { test, expect } from '../e2e/test-base.js';
import { login, uploadFiles, getStorageState, SELECTORS, TEXT } from '../helpers/index.js';
import { fixturePath } from '../fixtures/index.js';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { EXTRACTED_PASSPORT, MOCK_PASSPORTS } from '../mock/data.js';
import { isApiRequest } from '../mock/api.js';

/**
 * Ce qui ne doit jamais se retrouver dans un stockage du navigateur : les noms
 * et numéros réellement affichés pendant la session — ceux du tableau, et ceux
 * que l'extraction produit.
 */
const IDENTITY_STRINGS = [
    ...MOCK_PASSPORTS.flatMap(row => [row.first_name, row.last_name, row.passport_number]),
    EXTRACTED_PASSPORT.first_name, EXTRACTED_PASSPORT.last_name, EXTRACTED_PASSPORT.passport_number,
].filter(Boolean);

/** Une entrée de pré-cache porte ?__WB_REVISION__=... ; seul le chemin compte. */
const pathOf = url => new URL(url).pathname;

/**
 * Le nombre d'entrées que le worker construit DOIT pré-cacher, lu dans le
 * manifeste que Workbox a écrit dans dist/sw.js.
 *
 * Attendre « au moins une entrée » photographierait un cache à moitié rempli,
 * et la comparaison avant/après d'un autre test prendrait la fin du
 * remplissage pour une entrée ajoutée par l'application.
 */
function expectedPrecacheCount() {
    const dist = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', 'dist');
    const source = fs.readFileSync(path.join(dist, 'sw.js'), 'utf8');
    return [...source.matchAll(/url:"/g)].length;
}

/**
 * Attend que le worker CONTRÔLE la page et que le pré-cache soit complet.
 *
 * `expect.poll` et non `page.waitForFunction` : une fonction asynchrone rend
 * une Promise, qui est déjà « truthy », donc waitForFunction s'arrêterait au
 * premier appel sans jamais lire le résultat.
 */
async function waitForServiceWorker(page) {
    // `registration.active` ne suffit pas : tant que le worker ne contrôle pas
    // la page, un rechargement repart sur le réseau — et hors ligne, il échoue
    // avant même d'atteindre le worker.
    await expect.poll(async () => page.evaluate(async () => {
        if (!navigator.serviceWorker) return 'pas de serviceWorker';
        const registration = await navigator.serviceWorker.getRegistration();
        if (!registration?.active) return 'pas encore actif';
        return navigator.serviceWorker.controller ? 'controlee' : 'pas encore controlee';
    }), { timeout: 30_000, message: 'le service worker ne prend pas le contrôle' })
        .toBe('controlee');

    // Et que le pré-cache soit COMPLET, pas seulement commencé : compter « au
    // moins une entrée » photographierait un cache à moitié écrit, et la
    // comparaison avant/après d'un autre test prendrait la fin du remplissage
    // pour une entrée ajoutée par l'application.
    const expected = expectedPrecacheCount();
    await expect.poll(async () => page.evaluate(async () => {
        let total = 0;
        for (const key of await caches.keys()) {
            total += (await (await caches.open(key)).keys()).length;
        }
        return total;
    }), { timeout: 30_000, message: `le pré-cache n'atteint pas ${expected} entrées` })
        .toBe(expected);
}

/** Toutes les entrées de tous les caches, en URLs absolues. */
const cachedUrls = page => page.evaluate(async () => {
    const out = [];
    for (const key of await caches.keys()) {
        const cache = await caches.open(key);
        for (const request of await cache.keys()) out.push(request.url);
    }
    return out;
});

test.describe('Manifeste', () => {
    test('il est lié depuis index.html et servi avec le bon type', async ({ page, baseURL }) => {
        await page.goto('/');
        const href = await page.locator('link[rel="manifest"]').getAttribute('href');
        expect(href).toBeTruthy();

        const response = await page.request.get(new URL(href, baseURL).toString());
        expect(response.status()).toBe(200);
        expect(response.headers()['content-type']).toMatch(/application\/manifest\+json|application\/json/);
    });

    test('les champs requis sont présents et corrects', async ({ page, baseURL }) => {
        await page.goto('/');
        const href = await page.locator('link[rel="manifest"]').getAttribute('href');
        const manifest = await (await page.request.get(new URL(href, baseURL).toString())).json();

        expect(manifest.name).toBe('ScanID');
        expect(manifest.short_name).toBe('ScanID');
        expect(manifest.display).toBe('standalone');
        expect(manifest.background_color.toUpperCase()).toBe('#0B1628');
        expect(manifest.theme_color.toUpperCase()).toBe('#0B1628');
        expect(manifest.start_url).toBeTruthy();
        expect(manifest.lang).toBe('fr');
        expect(Array.isArray(manifest.icons)).toBe(true);
    });

    test('la meta theme-color est dans le document', async ({ page }) => {
        await page.goto('/');
        await expect(page.locator('meta[name="theme-color"]'))
            .toHaveAttribute('content', '#0B1628');
    });

    test('chaque icône répond 200 et fait la taille annoncée', async ({ page, baseURL }) => {
        await page.goto('/');
        const href = await page.locator('link[rel="manifest"]').getAttribute('href');
        const manifestUrl = new URL(href, baseURL).toString();
        const manifest = await (await page.request.get(manifestUrl)).json();

        const required = ['192x192', '512x512'];
        for (const size of required) {
            expect(manifest.icons.some(icon => icon.sizes === size), `icône ${size} déclarée`).toBe(true);
        }
        expect(manifest.icons.some(icon => icon.purpose === 'maskable' && icon.sizes === '512x512'),
            'icône maskable 512x512 déclarée').toBe(true);

        for (const icon of manifest.icons) {
            const url = new URL(icon.src, manifestUrl).toString();
            const response = await page.request.get(url);
            expect(response.status(), `${icon.src} doit répondre 200`).toBe(200);
            const body = await response.body();
            // En-tête PNG : signature, puis la taille dans le chunk IHDR.
            expect(body.subarray(1, 4).toString('ascii')).toBe('PNG');
            const width = body.readUInt32BE(16);
            const height = body.readUInt32BE(20);
            expect(`${width}x${height}`, `${icon.src} doit mesurer ${icon.sizes}`).toBe(icon.sizes);
        }
    });
});

test.describe('Service worker', () => {
    test("il s'enregistre et met en cache la coquille", async ({ page }) => {
        await page.goto('/');
        await waitForServiceWorker(page);

        const urls = await cachedUrls(page);
        expect(urls.length).toBeGreaterThan(0);
        // La coquille : le document, le bundle, la feuille de style.
        const paths = urls.map(pathOf);
        expect(paths, 'le document lui-même').toContain('/index.html');
        expect(paths.some(entry => /^\/assets\/index-.*\.js$/.test(entry)), 'le bundle').toBe(true);
        expect(paths.some(entry => /^\/assets\/index-.*\.css$/.test(entry)), 'la feuille de style').toBe(true);
        expect(urls.length).toBe(expectedPrecacheCount());
        console.log(`  ${urls.length} entrées pré-cachées`);
    });

    test("le décodeur HEIC n'est pas poussé à tout le monde", async ({ page }) => {
        // 1,3 Mo pour une minorité d'envois : il est chargé à la demande.
        await page.goto('/');
        await waitForServiceWorker(page);
        expect((await cachedUrls(page)).filter(url => url.includes('heic2any'))).toEqual([]);
    });

    test('un envoi et une lecture de résultats ne créent aucune entrée de cache', async ({ page }) => {
        await page.goto('/');
        await waitForServiceWorker(page);
        const before = await cachedUrls(page);

        await login(page);
        await uploadFiles(page, [fixturePath('smallJpeg')], { submit: true });
        await expect(page.locator(SELECTORS.queueChip).first())
            .toHaveText(/Traitement|Terminé/, { timeout: 30_000 });
        await page.getByRole('button', { name: TEXT.preview }).click();
        await page.getByRole('button', { name: TEXT.downloadCsv }).click();

        const after = await cachedUrls(page);
        expect(after.sort()).toEqual(before.sort());
        for (const url of after) {
            expect(url).not.toContain('upload-and-extract');
            expect(url).not.toContain('/passports');
            expect(url).not.toContain('/export');
            expect(url).not.toContain('/ocr/jobs');
            expect(url).not.toContain('token');
        }
    });

    test('la deuxième visite se charge encore', async ({ page }) => {
        await page.goto('/');
        await waitForServiceWorker(page);
        await page.reload();
        await expect(page.locator(SELECTORS.loginForm)).toBeVisible();
        await expect(page.locator(SELECTORS.logo)).toBeVisible();
    });
});

test.describe('Hors ligne', () => {
    test("l'écran « hors ligne » apparaît, en français", async ({ page, context }) => {
        await page.goto('/');
        await waitForServiceWorker(page);
        await login(page);

        await context.setOffline(true);
        const offline = page.locator(SELECTORS.offlineScreen);
        await expect(offline).toBeVisible({ timeout: 20_000 });
        await expect(offline).toContainText('Vous êtes hors ligne');
        await expect(offline).toContainText('connexion');
        // Construit avec les classes du design system, pas des styles ad hoc.
        await expect(offline.locator('.sid-card')).toBeVisible();
        await expect(offline.locator('.sid-empty')).toBeVisible();
    });

    test('hors ligne, la coquille se recharge mais AUCUN résultat ne revient du cache', async ({ page, context }) => {
        await page.goto('/');
        await waitForServiceWorker(page);
        await login(page);
        // Les résultats sont bien à l'écran avant la coupure.
        await expect(page.locator(SELECTORS.results))
            .toContainText(MOCK_PASSPORTS[0].last_name);

        await context.setOffline(true);
        // setOffline ne suffit pas ici : l'API est simulée par interception, et
        // une route interceptée répond sans toucher au réseau. Sans cela le
        // faux serveur continuerait de répondre et le test prouverait le
        // contraire de ce qu'il annonce.
        await page.route(url => isApiRequest(url), route => route.abort('internetdisconnected'));
        await page.reload();

        // La coquille vient du service worker : la page se charge.
        await expect(page.locator(SELECTORS.logo)).toBeVisible({ timeout: 30_000 });
        await expect(page.locator(SELECTORS.offlineScreen)).toBeVisible({ timeout: 20_000 });

        // Et rien des documents ne réapparaît : aucune réponse d'API n'est en cache.
        const body = (await page.locator('body').innerText()).toUpperCase();
        for (const secret of IDENTITY_STRINGS) {
            expect(body, `« ${secret} » ne doit pas revenir du cache`).not.toContain(secret.toUpperCase());
        }
        for (const url of await cachedUrls(page)) expect(url).not.toContain('/passports');
    });
});

test.describe('Stockage après une session complète', () => {
    test('rien du document, du MRZ, du nom ni du numéro ne subsiste', async ({ page }) => {
        await page.goto('/');
        await waitForServiceWorker(page);
        await login(page);

        // Dix envois, les résultats consultés, les deux exports déclenchés.
        const batch = [
            'smallJpeg', 'png', 'pdf', 'smallJpeg', 'png',
            'pdf', 'smallJpeg', 'png', 'pdf', 'smallJpeg',
        ].map(key => fixturePath(key));
        await uploadFiles(page, batch, { submit: true });
        await expect(page.locator(SELECTORS.queueItem)).toHaveCount(10);
        await expect(page.locator(SELECTORS.queueItem).nth(9))
            .toHaveAttribute('data-queue-status', /processing|done/, { timeout: 120_000 });

        await expect(page.locator(SELECTORS.results)).toBeVisible();
        await page.getByRole('button', { name: TEXT.downloadCsv }).click();
        await page.getByRole('button', { name: TEXT.downloadExcel }).click();
        await page.waitForTimeout(1000);

        const state = await getStorageState(page);

        // 1. Web storage : le jeton, et rien d'autre.
        // Le jeton a quitté le stockage local pour un cookie HttpOnly
        // (paquet C) : plus aucune clé ne subsiste.
        expect(Object.keys(state.localStorage)).toEqual([]);
        expect(Object.keys(state.sessionStorage)).toEqual([]);
        for (const [key, value] of [...Object.entries(state.localStorage),
            ...Object.entries(state.sessionStorage)]) {
            const blob = `${key}=${value}`.toUpperCase();
            for (const secret of IDENTITY_STRINGS) expect(blob).not.toContain(secret.toUpperCase());
            expect(blob).not.toContain('DATA:IMAGE');
            expect(blob).not.toContain('MRZ');
            expect(blob).not.toContain('BLOB:');
        }

        // 2. IndexedDB : aucune base.
        expect(state.unavailable).not.toContain('indexedDB.databases');
        expect(state.indexedDB).toEqual([]);

        // 3. Cache Storage : la coquille, et rien d'autre. On contrôle les
        //    clés ET le contenu, pas seulement le nombre d'entrées.
        const urls = await cachedUrls(page);
        expect(urls.length).toBeGreaterThan(0);
        const shell = /\.(js|css|html|svg|woff2|png|webmanifest)$|\/$/;
        for (const url of urls) {
            expect(pathOf(url), `${url} n'est pas un fichier de coquille`).toMatch(shell);
            expect(url).not.toContain('upload-and-extract');
            expect(url).not.toContain('/passports');
            expect(url).not.toContain('/export');
            expect(url).not.toContain('/ocr/jobs');
            expect(url).not.toContain('/users/me');
        }

        // Et le contenu de chaque entrée : aucune ne porte de donnée d'identité.
        const tainted = await page.evaluate(async (secrets) => {
            const found = [];
            for (const key of await caches.keys()) {
                const cache = await caches.open(key);
                for (const request of await cache.keys()) {
                    const response = await cache.match(request);
                    if (!response) continue;
                    const type = response.headers.get('content-type') || '';
                    if (/image|font|octet-stream/.test(type)) continue; // binaire
                    const text = (await response.text()).toUpperCase();
                    for (const secret of secrets) {
                        if (text.includes(secret)) found.push(`${request.url} <- ${secret}`);
                    }
                }
            }
            return found;
        }, IDENTITY_STRINGS.map(value => value.toUpperCase()));
        expect(tainted).toEqual([]);

        console.log(`  après 10 envois : localStorage=${Object.keys(state.localStorage)}, `
            + `sessionStorage=0, indexedDB=0, cache=${urls.length} fichiers de coquille`);
    });
});

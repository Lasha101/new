// Package B — ce que l'application laisse derrière elle sur l'appareil.
//
// L'engagement public est que les documents d'identité ne sont jamais stockés.
// Ces tests le vérifient sur le serveur de développement ; leur pendant sur
// l'application construite — celui qui inclut le service worker et le Cache
// Storage — est dans tests/pwa/pwa.spec.js.
import { test, expect } from './test-base.js';
import { login, logout, uploadFiles, storedToken, getStorageState, SELECTORS, TEXT } from '../helpers/index.js';
import { fixturePath } from '../fixtures/index.js';
import { EXTRACTED_PASSPORT } from '../mock/data.js';

/** Les chaînes qui ne doivent apparaître dans aucun stockage. */
const IDENTITY_STRINGS = [
    EXTRACTED_PASSPORT.first_name, EXTRACTED_PASSPORT.last_name,
    EXTRACTED_PASSPORT.passport_number, EXTRACTED_PASSPORT.nationality,
].filter(Boolean);

/** Enregistre chaque createObjectURL / revokeObjectURL de la page. */
async function trackObjectUrls(page) {
    await page.addInitScript(() => {
        window.__objectUrls = { created: [], revoked: [] };
        const create = URL.createObjectURL.bind(URL);
        const revoke = URL.revokeObjectURL.bind(URL);
        URL.createObjectURL = (blob) => {
            const url = create(blob);
            window.__objectUrls.created.push(url);
            return url;
        };
        URL.revokeObjectURL = (url) => {
            window.__objectUrls.revoked.push(url);
            return revoke(url);
        };
    });
}

const objectUrls = page => page.evaluate(() => window.__objectUrls);

test.describe('Jeton de session', () => {
    test("le jeton n'apparaît dans aucune URL, sauf le flux SSE", async ({ page }) => {
        const urls = [];
        page.on('request', request => urls.push(request.url()));

        await login(page);
        await uploadFiles(page, [fixturePath('smallJpeg')], { submit: true });
        await expect(page.locator(SELECTORS.queueChip).first())
            .toHaveText(/Traitement|Terminé/, { timeout: 30_000 });
        await page.getByRole('button', { name: TEXT.preview }).click();
        await page.getByRole('button', { name: TEXT.downloadCsv }).click();

        const token = await storedToken(page);
        expect(token).toBeTruthy();

        const leaking = urls.filter(url => url.includes(token));
        // GET /events est la seule exception, et elle n'est pas réparable ici :
        // EventSource ne sait pas poser d'en-tête, et backend/main.py:570
        // déclare `token: str = Query(...)`, donc la corriger demande une
        // modification du backend — paquet C. Le test la nomme pour qu'elle
        // devienne rouge le jour où elle est corrigée ailleurs.
        for (const url of leaking) {
            expect(new URL(url).pathname).toMatch(/\/events$/);
        }
        expect(leaking.length).toBeGreaterThan(0); // le flux SSE existe bien
        console.log(`  ${urls.length} requêtes ; jeton présent dans ${leaking.length} `
            + '(toutes /events — voir SCANID-HANDOVER.md, paquet C)');
    });

    test('les autres appels portent le jeton en en-tête, pas en query string', async ({ page }) => {
        const authorized = [];
        page.on('request', (request) => {
            const header = request.headers().authorization;
            if (header) authorized.push(new URL(request.url()).pathname);
        });
        await login(page);
        await expect(page.locator(SELECTORS.creditBadge)).toBeVisible();
        expect(authorized.some(path => path.endsWith('/users/me'))).toBe(true);
        expect(authorized.some(path => path.includes('/passports'))).toBe(true);
    });

    test("une coupure réseau ne déconnecte plus la session", async ({ page, context }) => {
        // Avant : toute erreur de /users/me appelait logout(), donc un tunnel
        // vidait le jeton et le travail en cours avec lui.
        await login(page);
        const before = await storedToken(page);

        const offline = page.locator(SELECTORS.offlineScreen);
        await context.setOffline(true);
        await expect(offline).toBeVisible({ timeout: 20_000 });
        // Le jeton reste, et le tableau de bord reste MONTÉ sous la couche :
        // c'est ce qui fait qu'un tunnel ne coûte aucun travail en cours.
        expect(await storedToken(page)).toBe(before);
        await expect(page.locator(SELECTORS.uploadCard)).toBeAttached();
        await expect(offline.getByRole('button', { name: 'Réessayer' })).toBeVisible();

        await context.setOffline(false);
        await expect(offline).toHaveCount(0, { timeout: 20_000 });
        await expect(page.locator(SELECTORS.creditBadge)).toBeVisible();
    });

    test("une session expirée invite à se reconnecter", async ({ page }) => {
        await login(page);
        // Le serveur refuse : la session est réellement finie.
        await page.route(url => url.pathname.endsWith('/users/me'), route => route.fulfill({
            status: 401, contentType: 'application/json',
            body: JSON.stringify({ detail: "Impossible de valider les informations d'identification" }),
        }));
        await page.reload();

        await expect(page.locator(SELECTORS.loginForm)).toBeVisible();
        await expect(page.locator(SELECTORS.sessionExpired)).toContainText('Votre session a expiré');
        expect(await storedToken(page)).toBeNull();
    });
});

test.describe('URLs blob', () => {
    test.beforeEach(async ({ page }) => { await trackObjectUrls(page); });

    test('un export révoque son URL blob', async ({ page }) => {
        await login(page);
        await page.getByRole('button', { name: TEXT.downloadExcel }).click();

        await expect.poll(async () => {
            const { created, revoked } = await objectUrls(page);
            return created.length > 0 && created.every(url => revoked.includes(url));
        }, { timeout: 15_000, message: 'une URL blob créée pour un export est restée vivante' }).toBe(true);

        const { created } = await objectUrls(page);
        expect(created.length).toBeGreaterThan(0);
    });

    test('quitter la vue révoque les URLs blob restantes', async ({ page }) => {
        await login(page);
        await page.getByRole('button', { name: TEXT.downloadCsv }).click();
        await expect.poll(async () => (await objectUrls(page)).created.length,
            { timeout: 15_000 }).toBeGreaterThan(0);

        // Changer d'onglet démonte la vue qui détient les blobs.
        await page.locator(SELECTORS.navButtons).filter({ hasText: 'Mon Compte' }).click();
        await expect(page.getByRole('heading', { name: 'Modifier Mon Compte' })).toBeVisible();

        const { created, revoked } = await objectUrls(page);
        for (const url of created) expect(revoked).toContain(url);
    });

    test("la préparation d'image ne laisse aucune URL blob vivante", async ({ page }) => {
        await login(page);
        await uploadFiles(page, [fixturePath('largeLandscapeJpeg')], { submit: true });
        await expect(page.locator(SELECTORS.queueChip).first())
            .toHaveText(/Traitement|Terminé/, { timeout: 30_000 });

        const { created, revoked } = await objectUrls(page);
        const outstanding = created.filter(url => !revoked.includes(url));
        expect(outstanding, `URLs blob non révoquées : ${outstanding.join(', ')}`).toEqual([]);
    });
});

test.describe('Stockage local', () => {
    test("après une session complète, rien d'identifiant n'est stocké", async ({ page }) => {
        await login(page);
        await uploadFiles(page, [
            fixturePath('smallJpeg'), fixturePath('png'), fixturePath('pdf'),
        ], { submit: true });
        await expect(page.locator(SELECTORS.queueItem).nth(2))
            .toHaveAttribute('data-queue-status', /processing|done/, { timeout: 30_000 });
        await page.getByRole('button', { name: TEXT.preview }).click();
        await page.getByRole('button', { name: TEXT.downloadCsv }).click();
        await page.getByRole('button', { name: TEXT.downloadExcel }).click();

        const state = await getStorageState(page);
        const values = [
            ...Object.entries(state.localStorage), ...Object.entries(state.sessionStorage),
        ];
        // Le jeton a le droit d'être là (voir SCANID-HANDOVER.md) ; rien d'autre.
        expect(Object.keys(state.localStorage)).toEqual(['token']);
        expect(Object.keys(state.sessionStorage)).toEqual([]);
        for (const [key, value] of values) {
            for (const secret of IDENTITY_STRINGS) {
                expect(`${key}=${value}`.toUpperCase()).not.toContain(secret.toUpperCase());
            }
            expect(value).not.toContain('data:image');
            expect(value).not.toContain('blob:');
        }
        expect(state.indexedDB, 'aucune base IndexedDB').toEqual([]);
    });

    test('la déconnexion ne laisse plus rien', async ({ page }) => {
        await login(page);
        await logout(page);
        const state = await getStorageState(page);
        expect(Object.keys(state.localStorage)).toEqual([]);
        expect(Object.keys(state.sessionStorage)).toEqual([]);
        expect(state.indexedDB).toEqual([]);
    });
});

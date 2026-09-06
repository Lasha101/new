// Package B — ce que l'application laisse derrière elle sur l'appareil.
//
// L'engagement public est que les documents d'identité ne sont jamais stockés.
// Ces tests le vérifient sur le serveur de développement ; leur pendant sur
// l'application construite — celui qui inclut le service worker et le Cache
// Storage — est dans tests/pwa/pwa.spec.js.
import { test, expect } from './test-base.js';
import { login, logout, uploadFiles, storedToken, hasSessionCookie, sessionCookie, getStorageState, SELECTORS, TEXT } from '../helpers/index.js';
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
    test("le jeton n'apparaît dans aucune URL — l'exception /events a disparu", async ({ page }) => {
        const urls = [];
        page.on('request', request => urls.push(request.url()));

        await login(page);
        await uploadFiles(page, [fixturePath('smallJpeg')], { submit: true });
        await expect(page.locator(SELECTORS.queueChip).first())
            .toHaveText(/Traitement|Terminé/, { timeout: 30_000 });
        await page.getByRole('button', { name: TEXT.preview }).click();
        await page.getByRole('button', { name: TEXT.downloadCsv }).click();

        // Le jeton est désormais dans un cookie HttpOnly : aucun script ne peut
        // le lire, donc on le récupère depuis le contexte du navigateur.
        const cookie = await sessionCookie(page);
        expect(cookie, 'la session doit exister').toBeTruthy();
        const token = cookie.value;

        // Le paquet B signalait GET /events comme la seule URL portant encore
        // le jeton : EventSource ne sait pas poser d'en-tête et l'endpoint
        // déclarait `token: str = Query(...)`. Le paquet C accepte maintenant
        // le cookie sur /events (withCredentials), donc l'exception a disparu
        // et PLUS AUCUNE URL ne transporte le jeton.
        const leaking = urls.filter(url => url.includes(token));
        expect(leaking, 'aucune URL ne doit transporter le jeton').toEqual([]);

        // Le flux SSE est bien ouvert — sans jeton dans l'URL.
        const sse = urls.filter(url => new URL(url).pathname.endsWith('/events'));
        expect(sse.length, 'le flux SSE doit exister').toBeGreaterThan(0);
        for (const url of sse) expect(new URL(url).search).toBe('');

        console.log(`  ${urls.length} requêtes ; jeton présent dans ${leaking.length} `
            + `(${sse.length} appel(s) /events, sans query string)`);
    });

    test('les appels portent le jeton en cookie, jamais en en-tête ni en query string', async ({ page }) => {
        // Le paquet C a déplacé le jeton de localStorage vers un cookie
        // HttpOnly : plus aucune requête ne pose d'en-tête Authorization, et
        // c'est précisément ce qui rend le jeton illisible par un script.
        const withAuthHeader = [];
        page.on('request', (request) => {
            if (request.headers().authorization) {
                withAuthHeader.push(new URL(request.url()).pathname);
            }
        });
        await login(page);
        await expect(page.locator(SELECTORS.creditBadge)).toBeVisible();

        // Ce qui est observable et qui compte : plus AUCUNE requête ne pose
        // d'en-tête Authorization. C'est ce qui rend le jeton illisible depuis
        // un script.
        expect(withAuthHeader, "aucun en-tête Authorization n'est envoyé").toEqual([]);

        // La présence du cookie se vérifie sur le contexte, pas sur les
        // requêtes : WebKit n'expose pas `cookie` sur une requête INTERCEPTÉE
        // (ni via headers(), ni via allHeaders()), parce que Playwright rapporte
        // les en-têtes avant que la pile réseau ne les ajoute. Chromium l'expose,
        // ce qui masquait la différence. Que le cookie soit bien ce qui
        // authentifie est prouvé côté serveur, contre la vraie application, par
        // backend/tests/test_security_hardening.py.
        const cookie = await sessionCookie(page);
        expect(cookie, 'la session est bien portée par un cookie').toBeTruthy();
        expect(cookie.httpOnly, 'le cookie de session est HttpOnly').toBe(true);
    });

    test("une coupure réseau ne déconnecte plus la session", async ({ page, context }) => {
        // Avant : toute erreur de /users/me appelait logout(), donc un tunnel
        // vidait le jeton et le travail en cours avec lui.
        await login(page);
        const before = await hasSessionCookie(page);
        expect(before).toBe(true);

        const offline = page.locator(SELECTORS.offlineScreen);
        await context.setOffline(true);
        await expect(offline).toBeVisible({ timeout: 20_000 });
        // Le jeton reste, et le tableau de bord reste MONTÉ sous la couche :
        // c'est ce qui fait qu'un tunnel ne coûte aucun travail en cours.
        expect(await hasSessionCookie(page)).toBe(before);
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
        // Depuis le paquet C, le jeton est dans un cookie HttpOnly :
        // le stockage local ne contient plus RIEN du tout.
        expect(Object.keys(state.localStorage)).toEqual([]);
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

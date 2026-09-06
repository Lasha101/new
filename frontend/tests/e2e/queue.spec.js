// Package B — la file d'envoi par lot.
//
// La politique de reprise elle-même est prouvée sans navigateur dans
// src/upload/uploadQueue.test.js, avec des délais simulés. Ici on prouve la
// même chose contre le VRAI transport : le XHR de l'application, le vrai
// endpoint, les vrais délais, et ce que l'utilisateur voit.
import { test, expect } from './test-base.js';
import { login, uploadFiles, SELECTORS } from '../helpers/index.js';
import { fixturePath } from '../fixtures/index.js';

/** Le nom de fichier porté par un corps multipart. */
const uploadedName = request => (request.postData() || '').match(/filename="([^"]*)"/)?.[1] || '';

const isUpload = url => url.pathname.includes('upload-and-extract');

/** Horodatage de chaque POST d'envoi, dans l'ordre. */
function recordUploads(page) {
    const attempts = [];
    page.on('request', (request) => {
        if (request.method() === 'POST' && isUpload(new URL(request.url()))) {
            attempts.push({ at: Date.now(), name: uploadedName(request) });
        }
    });
    return attempts;
}

test.describe("File d'envoi — réseau en échec", () => {
    test('la reprise se déclenche au moins deux fois, avec un délai croissant', async ({ page }) => {
        await login(page);
        const attempts = recordUploads(page);
        await page.route(url => isUpload(url), route => route.abort('failed'));

        await uploadFiles(page, [fixturePath('smallJpeg')], { submit: true });

        const item = page.locator(SELECTORS.queueItem).first();
        await expect(item).toHaveAttribute('data-queue-status', 'failed', { timeout: 30_000 });

        // Trois envois : le premier, puis deux reprises.
        expect(attempts.length).toBe(3);
        const first = attempts[1].at - attempts[0].at;
        const second = attempts[2].at - attempts[1].at;
        expect(first).toBeGreaterThanOrEqual(900);   // ~1 s
        expect(second).toBeGreaterThan(first);       // strictement croissant
        expect(second).toBeGreaterThanOrEqual(2700); // ~3 s
        console.log(`  reprises après ${first} ms puis ${second} ms`);

        // Et l'utilisateur le voit, en français, sur une puce du design system.
        await expect(page.locator(SELECTORS.queueChip).first()).toHaveText('Échoué');
        await expect(page.locator(SELECTORS.queueError).first()).toContainText('Connexion interrompue');
    });

    test('« Réessayer les échecs » ne renvoie que les documents en échec', async ({ page }) => {
        await login(page);
        const attempts = recordUploads(page);
        // Seul document.png échoue ; les deux autres passent. Le prédicat est
        // gardé dans une constante : page.unroute() l'identifie par référence.
        const uploadRoute = url => isUpload(url);
        await page.route(uploadRoute, (route) => {
            if (uploadedName(route.request()).includes('document.png')) return route.abort('failed');
            return route.fallback();
        });

        await uploadFiles(page, [
            fixturePath('smallJpeg'), fixturePath('png'), fixturePath('pdf'),
        ], { submit: true });

        const items = page.locator(SELECTORS.queueItem);
        await expect(items).toHaveCount(3);
        const failed = items.filter({ has: page.locator('[class*="sid-chip--failed"]') });
        await expect(failed).toHaveCount(1, { timeout: 30_000 });

        // Le lot a continué après l'échec : les deux autres sont partis une fois
        // chacun, et sont arrivés au bout.
        const byName = attempts.reduce((acc, a) => ({ ...acc, [a.name]: (acc[a.name] || 0) + 1 }), {});
        expect(byName['small.jpg']).toBe(1);
        expect(byName['document.pdf']).toBe(1);
        expect(byName['document.png']).toBe(3);
        await expect(items.filter({ hasText: 'small.jpg' })).toHaveAttribute(
            'data-queue-status', /processing|done/);

        // Le réseau revient, puis on réessaie.
        await page.unroute(uploadRoute);
        attempts.length = 0;
        await page.locator(SELECTORS.retryFailed).click();

        await expect(items.filter({ hasText: 'document.png' }))
            .toHaveAttribute('data-queue-status', /processing|done/, { timeout: 30_000 });
        // UNIQUEMENT le document en échec : renvoyer les autres créerait un
        // deuxième job et dépenserait un deuxième crédit.
        expect(attempts.map(a => a.name)).toEqual(['document.png']);
    });

    test("un refus du serveur n'est pas réessayé", async ({ page, api }) => {
        // « Crédits insuffisants » est une décision du serveur : la répéter
        // n'y changerait rien et brûlerait des crédits.
        api.user.page_credits = 0;
        await login(page);
        const attempts = recordUploads(page);

        await uploadFiles(page, [fixturePath('smallJpeg')], { submit: true });

        const item = page.locator(SELECTORS.queueItem).first();
        await expect(item).toHaveAttribute('data-queue-status', 'failed', { timeout: 15_000 });
        expect(attempts.length).toBe(1);
        await expect(page.locator(SELECTORS.queueError).first()).toContainText('Crédits insuffisants');
    });
});

test.describe("File d'envoi — marche nominale", () => {
    test('chaque document a son propre état, sa propre progression, en français', async ({ page }) => {
        await login(page);
        await uploadFiles(page, [
            fixturePath('smallJpeg'), fixturePath('png'), fixturePath('pdf'),
        ], { submit: true });

        const items = page.locator(SELECTORS.queueItem);
        await expect(items).toHaveCount(3);
        // Les trois finissent par atteindre « Terminé » (le job OCR simulé
        // aboutit), donc la file suit le job serveur et pas seulement l'envoi.
        for (let index = 0; index < 3; index++) {
            await expect(items.nth(index)).toHaveAttribute('data-queue-status', 'done', { timeout: 30_000 });
        }
        const labels = await page.locator(SELECTORS.queueChip).allTextContents();
        expect(labels).toEqual(['Terminé', 'Terminé', 'Terminé']);
        // Chaque nom de fichier est affiché tel que l'utilisateur l'a choisi.
        await expect(items.nth(0)).toContainText('small.jpg');
        await expect(items.nth(1)).toContainText('document.png');
        await expect(items.nth(2)).toContainText('document.pdf');
    });

    test('un lot de trois crée trois jobs, un par document', async ({ page }) => {
        await login(page);
        const attempts = recordUploads(page);
        await uploadFiles(page, [
            fixturePath('smallJpeg'), fixturePath('png'), fixturePath('pdf'),
        ], { submit: true });

        await expect(page.locator(SELECTORS.queueItem).nth(2))
            .toHaveAttribute('data-queue-status', /processing|done/, { timeout: 30_000 });
        // Un fichier par requête : le contrat de l'API n'a pas changé.
        expect(attempts.map(a => a.name)).toEqual(['small.jpg', 'document.png', 'document.pdf']);
        await expect(page.locator(SELECTORS.jobItem)).toHaveCount(3);
    });

    test("« Réessayer les échecs » n'apparaît que s'il y a un échec", async ({ page }) => {
        await login(page);
        await uploadFiles(page, [fixturePath('smallJpeg')], { submit: true });
        await expect(page.locator(SELECTORS.queue)).toBeVisible();
        await expect(page.locator(SELECTORS.retryFailed)).toHaveCount(0);
    });

    test("« Annuler l'envoi » vide la file", async ({ page }) => {
        await login(page);
        await uploadFiles(page, [fixturePath('largeLandscapeJpeg')], { submit: true });
        const cancel = page.getByRole('button', { name: "Annuler l'envoi" });
        if (await cancel.count() > 0) {
            await cancel.click();
            await expect(page.locator(SELECTORS.queueItem)).toHaveCount(0);
        }
        await expect(page.locator(SELECTORS.uploadCard)).toBeVisible();
    });

    test("la file ne survit pas à un rechargement", async ({ page }) => {
        // Une file persistée serait une file de documents d'identité sur le
        // disque du téléphone.
        await login(page);
        await uploadFiles(page, [fixturePath('smallJpeg')], { submit: true });
        await expect(page.locator(SELECTORS.queueItem)).toHaveCount(1);

        await page.reload();
        await expect(page.locator(SELECTORS.uploadCard)).toBeVisible();
        await expect(page.locator(SELECTORS.queueItem)).toHaveCount(0);
    });
});

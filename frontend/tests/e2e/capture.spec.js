// Package B — capture mobile : contrôles, compression, orientation EXIF, HEIC.
//
// La préparation d'image tourne dans le navigateur (canvas, createImageBitmap,
// décodeur HEIC), donc elle est prouvée ici et non sous `node --test`. La partie
// purement octets — détection par nombres magiques, lecture du tag EXIF, calcul
// des transformations — est prouvée dans src/upload/fileSniff.test.js.
import { test, expect } from './test-base.js';
import {
    login, uploadFiles, SELECTORS, serveFixtures, fixtureUrl, prepareInBrowser,
    findOverflowingElements, measureTapTargets,
} from '../helpers/index.js';
import { fixturePath } from '../fixtures/index.js';

/**
 * Seuil ANNONCÉ pour le fixture de 4,3 Mo une fois compressé.
 *
 * C'est le pire cas mesuré, pas le meilleur : à qualité 0,85 nominale, le
 * codeur JPEG de WebKit rend 1 259 009 octets là où celui de Chromium en rend
 * 1 122 349 pour la même image et les mêmes dimensions. Le seuil doit tenir sur
 * les deux moteurs, donc il est posé au-dessus du plus gourmand.
 */
const COMPRESSED_BUDGET_BYTES = 1_400_000;
const MAX_EDGE = 2500;

test.describe('Contrôles de capture', () => {
    test('le sélecteur accepte plusieurs fichiers, HEIC compris, sans rien retirer', async ({ page }) => {
        await login(page);
        const input = page.locator(SELECTORS.fileInput);
        const accept = await input.getAttribute('accept');

        // Rien de ce qui était accepté ne devient refusé.
        for (const type of ['image/png', 'image/jpeg', 'image/jpg', 'application/pdf']) {
            expect(accept).toContain(type);
        }
        // HEIC/HEIF ajoutés : c'est ce que rend la photothèque d'un iPhone.
        expect(accept).toContain('image/heic');
        expect(accept).toContain('image/heif');
        await expect(input).toHaveAttribute('multiple', '');
    });

    test("le bouton appareil photo demande la caméra arrière", async ({ page }) => {
        await login(page);
        const camera = page.locator(SELECTORS.cameraInput);
        await expect(camera).toBeAttached();
        await expect(camera).toHaveAttribute('capture', 'environment');
        await expect(camera).toHaveAttribute('multiple', '');
        // Le sélecteur, lui, N'A PAS capture : sur un téléphone, capture
        // remplace la photothèque par l'appareil photo, et choisir un fichier
        // existant doit rester possible.
        await expect(page.locator(SELECTORS.fileInput)).not.toHaveAttribute('capture', /.*/);
        await expect(page.locator(SELECTORS.cameraButton)).toBeVisible();
    });

    test('le lien vers le guide photo est en français et ouvre un nouvel onglet', async ({ page }) => {
        await login(page);
        const link = page.locator(SELECTORS.photoGuideLink);
        await expect(link).toBeVisible();
        await expect(link).toHaveAttribute('href', 'https://scanid.fr/guide-photo.html');
        await expect(link).toHaveAttribute('target', '_blank');
        await expect(link).toHaveAttribute('rel', /noopener/);
        await expect(link).toContainText('Guide');
    });

    test("la caméra alimente le même envoi que le sélecteur", async ({ page }) => {
        await login(page);
        await uploadFiles(page, [fixturePath('smallJpeg')], { camera: true, submit: true });
        await expect(page.locator(SELECTORS.queueItem)).toHaveCount(1);
    });
});

test.describe('Compression', () => {
    test.beforeEach(async ({ page }) => {
        await serveFixtures(page);
        await login(page);
    });

    test(`le fichier de 4 Mo descend sous ${COMPRESSED_BUDGET_BYTES} octets, grand côté ≤ ${MAX_EDGE} px`, async ({ page }) => {
        const result = await prepareInBrowser(page, fixtureUrl('largeLandscapeJpeg'));

        expect(result.detectedType).toBe('jpeg');
        expect(result.changed).toBe(true);
        expect(result.reason).toBe('compressed');
        expect(result.originalBytes).toBeGreaterThan(4_000_000);
        expect(result.bytes).toBeLessThan(COMPRESSED_BUDGET_BYTES);
        expect(Math.max(result.width, result.height)).toBeLessThanOrEqual(MAX_EDGE);
        // 3200x2133 -> 2500x1666 : le rapport d'aspect est conservé.
        expect(result.width).toBe(MAX_EDGE);
        expect(result.height).toBe(Math.round(2133 * (MAX_EDGE / 3200)));
        console.log(`  4 Mo : ${result.originalBytes} -> ${result.bytes} octets `
            + `(${result.width}x${result.height})`);
    });

    test('la sortie est un JPEG', async ({ page }) => {
        const result = await prepareInBrowser(page, fixtureUrl('largeLandscapeJpeg'));
        expect(result.outputType).toBe('image/jpeg');
    });

    test('le petit fichier passe sans être touché', async ({ page }) => {
        const result = await prepareInBrowser(page, fixtureUrl('smallJpeg'));
        expect(result.changed).toBe(false);
        expect(result.reason).toBe('below-threshold');
        expect(result.bytes).toBe(result.originalBytes);
    });

    test("le PDF n'est pas compressé", async ({ page }) => {
        const result = await prepareInBrowser(page, fixtureUrl('pdf'));
        expect(result.detectedType).toBe('pdf');
        expect(result.changed).toBe(false);
        expect(result.reason).toBe('pdf');
        expect(result.bytes).toBe(result.originalBytes);
    });

    test('un PNG sous le seuil reste un PNG', async ({ page }) => {
        // Le convertir en JPEG serait une perte sans gain de bande passante.
        const result = await prepareInBrowser(page, fixtureUrl('png'));
        expect(result.detectedType).toBe('png');
        expect(result.changed).toBe(false);
    });

    test("l'envoi réel transporte les octets compressés, pas l'original", async ({ page, browserName }) => {
        // Playwright/WebKit ne restitue pas la taille d'un corps multipart
        // volumineux : postData() rend 193 octets pour 1,2 Mo, postDataBuffer()
        // rend null et sizes().requestBodySize rend 0. L'assertion passerait
        // sans rien mesurer, donc elle est déclarée non couverte plutôt que
        // faussement verte. La compression EST prouvée sur WebKit par le test
        // en page ci-dessus (1 259 009 octets, 2500x1666).
        test.skip(browserName === 'webkit',
            'WebKit : Playwright ne rapporte pas la taille d’un corps multipart volumineux');
        // Bout en bout : ce que le serveur reçoit vraiment, pas ce que la
        // fonction renvoie. La taille vient de request.sizes(), la seule des
        // trois sources qui soit fiable pour un corps multipart.
        const uploads = [];
        page.on('request', (request) => {
            if (request.method() === 'POST' && request.url().includes('upload-and-extract')) {
                uploads.push(request);
            }
        });
        await uploadFiles(page, [fixturePath('largeLandscapeJpeg')], { submit: true });
        await expect(page.locator(SELECTORS.queueChip).first())
            .toHaveText(/Traitement|Terminé/, { timeout: 30_000 });

        expect(uploads.length).toBe(1);
        const bodyBytes = (await uploads[0].sizes()).requestBodySize;
        expect(bodyBytes, 'la taille du corps doit être mesurable').toBeGreaterThan(100_000);
        expect(bodyBytes).toBeLessThan(COMPRESSED_BUDGET_BYTES);
        console.log(`  corps multipart réellement envoyé : ${bodyBytes} octets (original 4 349 263)`);
    });
});

test.describe('Orientation EXIF', () => {
    test.beforeEach(async ({ page }) => {
        await serveFixtures(page);
        await login(page);
    });

    // Le fixture est stocké 1200x1600 (portrait) avec Orientation 6 = rotation
    // de 90° dans le sens horaire. Correctement traité, il sort en 1600x1200,
    // et la bande MRZ — en bas de l'image stockée — se retrouve à GAUCHE.
    const assertRotatedClockwise = (result) => {
        expect(result.changed).toBe(true);
        expect(result.orientation).toBe(6);
        expect(result.width).toBe(1600);
        expect(result.height).toBe(1200);
        // Les dimensions ne suffisent pas : on regarde les pixels.
        expect(result.pixels.left).toBeLessThan(result.pixels.right - 30);
        expect(result.pixels.right).toBeGreaterThan(200); // papier clair à droite
    };

    test('orientation 6 : le portrait sort en paysage, MRZ à gauche', async ({ page }) => {
        const result = await prepareInBrowser(page, fixtureUrl('exifOrientationJpeg'));
        assertRotatedClockwise(result);
        console.log(`  orientation 6 -> ${result.width}x${result.height}, `
            + `bandes L=${result.pixels.left.toFixed(1)} R=${result.pixels.right.toFixed(1)} `
            + `(source: ${result.orientationSource})`);
    });

    test('le repli EXIF explicite donne exactement le même résultat', async ({ page }) => {
        // letBrowserOrient: false décode SANS laisser le navigateur appliquer
        // l'orientation, puis applique la transformation lue dans le tag. C'est
        // le chemin de repli du brief, exercé et non supposé.
        const result = await prepareInBrowser(page, fixtureUrl('exifOrientationJpeg'),
            { letBrowserOrient: false });
        assertRotatedClockwise(result);
        expect(result.orientationSource).toBe('exif');
    });

    test('orientation 3 : les dimensions ne bougent pas, les pixels si', async ({ page }) => {
        // Une rotation de 180° ne change aucune dimension. Si seule la taille
        // était vérifiée, ce cas passerait même sans rotation du tout.
        const result = await prepareInBrowser(page, fixtureUrl('exifOrientationJpeg', { orientation: 3 }));
        expect(result.changed).toBe(true);
        expect(result.orientation).toBe(3);
        expect(result.width).toBe(1200);
        expect(result.height).toBe(1600);
        // La bande MRZ passe du bas vers le HAUT.
        expect(result.pixels.top).toBeLessThan(result.pixels.bottom - 30);
        console.log(`  orientation 3 -> ${result.width}x${result.height}, `
            + `bandes H=${result.pixels.top.toFixed(1)} B=${result.pixels.bottom.toFixed(1)}`);
    });

    test("orientation 1 : l'image n'est pas tournée", async ({ page }) => {
        const result = await prepareInBrowser(page, fixtureUrl('exifOrientationJpeg', { orientation: 1 }));
        // Sous le seuil et déjà droite : elle passe telle quelle.
        expect(result.changed).toBe(false);
        expect(result.reason).toBe('below-threshold');
    });
});

test.describe('HEIC', () => {
    test.beforeEach(async ({ page }) => {
        await serveFixtures(page);
        await login(page);
    });

    test("un HEIC illisible est envoyé tel quel, jamais abandonné", async ({ page }) => {
        // En-tête HEIC authentique (boîte ftyp d'un iPhone) suivi d'octets qui
        // ne sont pas une image : la détection réussit, la conversion échoue.
        // Le fichier doit quand même partir — le serveur sait décoder le HEIC.
        const result = await page.evaluate(async () => {
            const { prepareFileForUpload } = await import('/src/upload/imagePrep.js');
            const header = [
                0x00, 0x00, 0x00, 0x18, 0x66, 0x74, 0x79, 0x70, // size + 'ftyp'
                0x68, 0x65, 0x69, 0x63, 0x00, 0x00, 0x00, 0x00, // 'heic' + minor
                0x68, 0x65, 0x69, 0x63, 0x6d, 0x69, 0x66, 0x31, // 'heic' 'mif1'
            ];
            const bytes = new Uint8Array([...header, ...new Array(4096).fill(0x41)]);
            // Safari reports the type inconsistently; '' is the common case.
            const file = new File([bytes], 'IMG_4021.HEIC', { type: '' });
            const outcome = await prepareFileForUpload(file);
            return {
                detectedType: outcome.detectedType,
                reason: outcome.reason,
                changed: outcome.changed,
                sameObject: outcome.file === file,
                name: outcome.file.name,
                size: outcome.file.size,
            };
        });

        expect(result.detectedType).toBe('heic');       // détecté par les octets
        expect(result.reason).toBe('heic-conversion-failed');
        expect(result.changed).toBe(false);
        expect(result.sameObject).toBe(true);           // le fichier d'origine
        expect(result.name).toBe('IMG_4021.HEIC');
        expect(result.size).toBe(4096 + 24);
    });

    test("un JPEG nommé .heic est traité comme un JPEG", async ({ page }) => {
        // La détection ne consulte ni le nom ni le type annoncé.
        const result = await page.evaluate(async () => {
            const { prepareFileForUpload } = await import('/src/upload/imagePrep.js');
            const response = await fetch('/__fixture/large-landscape.jpg');
            const blob = await response.blob();
            const file = new File([blob], 'IMG_0001.HEIC', { type: 'image/heic' });
            const outcome = await prepareFileForUpload(file);
            return { detectedType: outcome.detectedType, reason: outcome.reason, name: outcome.file.name };
        });
        expect(result.detectedType).toBe('jpeg');
        expect(result.reason).toBe('compressed');
        expect(result.name).toBe('IMG_0001.HEIC'); // extension inchangée : c'était déjà du JPEG
    });
});

test.describe('Atteignabilité', () => {
    test.use({ viewport: { width: 375, height: 667 } });

    test("depuis la session ouverte, le contrôle d'import est à deux taps", async ({ page }) => {
        await login(page);
        // Tap 0 : rien. Le tableau de bord ouvre déjà sur l'onglet Passeports.
        const dropzone = page.locator(SELECTORS.uploadCard);
        await expect(dropzone).toBeAttached();
        await dropzone.scrollIntoViewIfNeeded();
        await expect(dropzone).toBeVisible();
        // Tap 1 : le contrôle lui-même. Aucune navigation intermédiaire.
        const box = await dropzone.boundingBox();
        expect(box.height).toBeGreaterThanOrEqual(44);
        await expect(page.locator(SELECTORS.cameraButton)).toBeVisible();
        const cameraBox = await page.locator(SELECTORS.cameraButton).boundingBox();
        expect(cameraBox.height).toBeGreaterThanOrEqual(44);
    });
});

test.describe('Les ajouts de ce paquet tiennent sur un petit écran', () => {
    test.use({ viewport: { width: 360, height: 640 } });

    test("la file d'envoi ne déborde pas horizontalement à 360 px", async ({ page }) => {
        await login(page);
        await uploadFiles(page, [
            fixturePath('smallJpeg'), fixturePath('png'), fixturePath('pdf'),
        ], { submit: true });
        await expect(page.locator(SELECTORS.queueItem)).toHaveCount(3);

        const overflowing = await findOverflowingElements(page);
        expect(overflowing, `débordent : ${JSON.stringify(overflowing)}`).toEqual([]);
    });

    test("l'écran hors ligne tient dans l'écran et son bouton est tapable", async ({ page, context }) => {
        await login(page);
        await context.setOffline(true);
        await expect(page.locator(SELECTORS.offlineScreen)).toBeVisible({ timeout: 20_000 });

        const overflowing = await findOverflowingElements(page);
        expect(overflowing, `débordent : ${JSON.stringify(overflowing)}`).toEqual([]);

        const targets = await measureTapTargets(page, `${SELECTORS.offlineScreen} .sid-btn`);
        expect(targets.length).toBe(1);
        expect(targets[0].height).toBeGreaterThanOrEqual(44);
    });
});

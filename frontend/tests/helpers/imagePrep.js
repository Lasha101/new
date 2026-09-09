// Driving src/upload/imagePrep.js inside a real browser.
//
// The module needs canvas, createImageBitmap and (for HEIC) a WASM decoder, so
// it cannot be exercised under `node --test` the way fileSniff.js can. These
// helpers serve fixture bytes to the page, import the real module through the
// Vite dev server, and bring back both the result and a description of the
// PIXELS it produced — a rotation is only proven by looking at the image.
import fs from 'node:fs';
import path from 'node:path';
import { FILES_DIR, FIXTURES } from '../fixtures/index.js';
import { appSrc } from './appBase.js';

/** URL prefix the page fetches fixture bytes from. Intercepted, never real. */
export const FIXTURE_URL_PREFIX = '/__fixture';

/**
 * Rewrites the EXIF Orientation value of a JPEG that already carries one.
 *
 * Used to turn the orientation-6 fixture into an orientation-3 one, because a
 * 180° rotation changes no dimension: it is the case where a dimension check
 * proves nothing and only the pixels can.
 */
export function withExifOrientation(buffer, orientation) {
    const marker = Buffer.from('Exif\0\0', 'latin1');
    const at = buffer.indexOf(marker);
    if (at < 0) throw new Error('withExifOrientation: no APP1/Exif segment in this JPEG.');
    const tiff = at + marker.length;
    const little = buffer.toString('ascii', tiff, tiff + 2) === 'II';
    const entries = little ? buffer.readUInt16LE(tiff + 8) : buffer.readUInt16BE(tiff + 8);
    for (let index = 0; index < entries; index++) {
        const entry = tiff + 10 + index * 12;
        const tag = little ? buffer.readUInt16LE(entry) : buffer.readUInt16BE(entry);
        if (tag !== 0x0112) continue;
        const patched = Buffer.from(buffer);
        if (little) patched.writeUInt16LE(orientation, entry + 8);
        else patched.writeUInt16BE(orientation, entry + 8);
        return patched;
    }
    throw new Error('withExifOrientation: no Orientation tag to rewrite.');
}

/**
 * Serves the fixture files to the page under {@link FIXTURE_URL_PREFIX}.
 *
 *   /__fixture/small.jpg            the file as generated
 *   /__fixture/orient-3/<name>      the same file with its EXIF orientation rewritten
 *
 * Interception rather than a static server: it works identically against the
 * dev server and a production preview, and adds no route the app could reach.
 */
export async function serveFixtures(page) {
    await page.route(`**${FIXTURE_URL_PREFIX}/**`, async (route) => {
        const { pathname } = new URL(route.request().url());
        const parts = pathname.split('/').filter(Boolean);
        const name = parts[parts.length - 1];
        const orientMatch = parts[parts.length - 2]?.match(/^orient-(\d)$/);
        const file = path.join(FILES_DIR, name);
        if (!fs.existsSync(file)) {
            await route.fulfill({ status: 404, body: `no fixture named ${name}` });
            return;
        }
        let body = fs.readFileSync(file);
        if (orientMatch) body = withExifOrientation(body, Number(orientMatch[1]));
        const mime = Object.values(FIXTURES).find(entry => entry.file === name)?.mime
            || 'application/octet-stream';
        await route.fulfill({ status: 200, contentType: mime, body });
    });
}

/** The URL the page should fetch for a fixture, optionally re-oriented. */
export function fixtureUrl(fixtureKey, { orientation } = {}) {
    const file = FIXTURES[fixtureKey]?.file;
    if (!file) throw new Error(`Unknown fixture "${fixtureKey}".`);
    return orientation
        ? `${FIXTURE_URL_PREFIX}/orient-${orientation}/${file}`
        : `${FIXTURE_URL_PREFIX}/${file}`;
}

/**
 * Runs prepareFileForUpload() in the page and reports what came out.
 *
 * @returns {Promise<{reason:string, changed:boolean, detectedType:string,
 *   originalBytes:number, bytes:number, outputType:string, outputName:string,
 *   width:number, height:number, orientation:number, orientationSource:string,
 *   pixels:{left:number, right:number, top:number, bottom:number}|null}>}
 *   `pixels` holds the mean luminance of a 15% strip on each edge of the
 *   OUTPUT image — the only way to tell a correct rotation from a plausible one.
 */
export async function prepareInBrowser(page, url, options = {}) {
    // The specifier is a REQUEST to the dev server, not a bundler
    // instruction, and Vite serves nothing outside its base — so the path
    // has to carry the application's base or the import rejects in the page.
    return page.evaluate(async ({ url, options, module }) => {
        const { prepareFileForUpload } = await import(module);

        const response = await fetch(url);
        const blob = await response.blob();
        const name = url.split('/').pop();
        // The type is deliberately left as the server sent it (and is empty for
        // a library HEIC on Safari): detection must not depend on it.
        const file = new File([blob], name, { type: blob.type || '' });

        const result = await prepareFileForUpload(file, options);

        /** Mean luminance of the four edge strips of the produced image. */
        let pixels = null;
        if (result.file.type === 'image/jpeg' || result.file.type.startsWith('image/')) {
            try {
                const bitmap = await createImageBitmap(result.file);
                const canvas = document.createElement('canvas');
                canvas.width = bitmap.width;
                canvas.height = bitmap.height;
                const context = canvas.getContext('2d');
                context.drawImage(bitmap, 0, 0);
                const strip = (x, y, w, h) => {
                    const data = context.getImageData(x, y, Math.max(1, w), Math.max(1, h)).data;
                    let sum = 0;
                    for (let i = 0; i < data.length; i += 4) {
                        sum += 0.2126 * data[i] + 0.7152 * data[i + 1] + 0.0722 * data[i + 2];
                    }
                    return sum / (data.length / 4);
                };
                const bw = Math.round(bitmap.width * 0.15);
                const bh = Math.round(bitmap.height * 0.15);
                pixels = {
                    left: strip(0, 0, bw, bitmap.height),
                    right: strip(bitmap.width - bw, 0, bw, bitmap.height),
                    top: strip(0, 0, bitmap.width, bh),
                    bottom: strip(0, bitmap.height - bh, bitmap.width, bh),
                };
                bitmap.close?.();
            } catch {
                pixels = null;
            }
        }

        return {
            reason: result.reason,
            changed: result.changed,
            detectedType: result.detectedType,
            originalBytes: result.originalBytes,
            bytes: result.bytes,
            outputType: result.file.type,
            outputName: result.file.name,
            width: result.width ?? null,
            height: result.height ?? null,
            orientation: result.orientation ?? null,
            orientationSource: result.orientationSource ?? null,
            pixels,
        };
    }, { url, options, module: appSrc('upload/imagePrep.js') });
}

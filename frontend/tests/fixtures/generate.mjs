#!/usr/bin/env node
// Generates every fixture listed in index.js. Deterministic (seeded noise, fixed
// encoder settings), so two machines produce byte-identical files and a rerun is
// a no-op. Run directly (`node tests/fixtures/generate.mjs`) or let the Playwright
// global setup / the unit-test pretest hook call ensureFixtures().
//
// Nothing here is derived from a real identity document: the "documents" are
// coloured rectangles with a synthetic machine-readable-zone band.
import fs from 'node:fs';
import path from 'node:path';

import { FILES_DIR, FIXTURES, fixturePath } from './index.js';
import { seededRandom } from './lib/bytes.js';
import { encodeJpeg, encodeJpegNearSize, injectExifOrientation } from './lib/jpeg.js';
import { encodePng } from './lib/png.js';
import { encodePdf } from './lib/pdf.js';

// A synthetic MRZ. The name is deliberately nonsense and the document number is
// outside every real French series.
const SPECIMEN_MRZ_1 = 'P<FRASPECIMEN<<TEST<HARNESS<<<<<<<<<<<<<<<<<<';
const SPECIMEN_MRZ_2 = '00XX000000FRA0001019M0001013<<<<<<<<<<<<<<02';

/** RGBA pixel buffer of a fake document: paper, a photo box, an MRZ band, grain. */
function drawSpecimen(width, height, seed) {
    const random = seededRandom(seed);
    const data = Buffer.alloc(width * height * 4);
    const mrzTop = Math.round(height * 0.78);
    const photoBox = {
        x0: Math.round(width * 0.06), x1: Math.round(width * 0.30),
        y0: Math.round(height * 0.15), y1: Math.round(height * 0.62),
    };
    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            const i = (y * width + x) * 4;
            let r, g, b;
            if (y >= mrzTop) {
                // MRZ band: near-white with dark vertical strokes, the highest
                // entropy region of a real scan (and the reason files are large).
                const stroke = (x % 17) < 9 && ((y - mrzTop) % 13) > 2;
                const v = stroke ? 24 + random() * 40 : 235 + random() * 20;
                r = g = b = v;
            } else if (x >= photoBox.x0 && x <= photoBox.x1 && y >= photoBox.y0 && y <= photoBox.y1) {
                const shade = 90 + random() * 110;
                r = shade * 0.95; g = shade * 0.85; b = shade * 0.78;
            } else {
                const grain = random() * 26;
                r = 236 - grain + (x / width) * 12;
                g = 232 - grain + (y / height) * 10;
                b = 214 - grain;
            }
            data[i] = r; data[i + 1] = g; data[i + 2] = b; data[i + 3] = 255;
        }
    }
    return data;
}

function write(key, buffer) {
    const target = fixturePath(key);
    fs.writeFileSync(target, buffer);
    return { key, file: path.basename(target), bytes: buffer.length };
}

function buildLargeLandscapeJpeg() {
    const { width, height, targetBytes } = FIXTURES.largeLandscapeJpeg;
    const data = drawSpecimen(width, height, 0x5eed01);
    const { buffer } = encodeJpegNearSize({ width, height, data, targetBytes });
    return write('largeLandscapeJpeg', buffer);
}

function buildSmallJpeg() {
    const { width, height, maxBytes } = FIXTURES.smallJpeg;
    const data = drawSpecimen(width, height, 0x5eed02);
    let buffer = encodeJpeg({ width, height, data, quality: 70 });
    for (let quality = 60; buffer.length > maxBytes && quality >= 20; quality -= 10) {
        buffer = encodeJpeg({ width, height, data, quality });
    }
    if (buffer.length > maxBytes) throw new Error(`small.jpg is ${buffer.length} B, over the 200 KB budget.`);
    return write('smallJpeg', buffer);
}

function buildExifJpeg() {
    const { width, height, exifOrientation } = FIXTURES.exifOrientationJpeg;
    const data = drawSpecimen(width, height, 0x5eed03);
    const buffer = injectExifOrientation(encodeJpeg({ width, height, data, quality: 78 }), exifOrientation);
    return write('exifOrientationJpeg', buffer);
}

function buildPng() {
    const { width, height } = FIXTURES.png;
    const random = seededRandom(0x5eed04);
    const buffer = encodePng(width, height, (x, y) => {
        if (y > height * 0.8) {
            const stroke = (x % 15) < 8;
            const v = stroke ? 30 : 240;
            return [v, v, v];
        }
        return [230 - Math.round(random() * 20), 226 - Math.round((y / height) * 30), 205];
    });
    return write('png', buffer);
}

function buildPdf() {
    const buffer = encodePdf([
        'SPECIMEN - ScanID test fixture, not a real document',
        'REPUBLIQUE FRANCAISE / PASSEPORT',
        'Nom: SPECIMEN     Prenoms: TEST HARNESS',
        'Date de naissance: 01/01/2000   Expiration: 01/01/2030',
        '',
        SPECIMEN_MRZ_1,
        SPECIMEN_MRZ_2,
    ]);
    return write('pdf', buffer);
}

function buildDisallowed() {
    return write('disallowedType', Buffer.from(
        "Fichier de test ScanID : type non autorise (text/plain).\n"
        + "Sert aux tests de rejet du selecteur de fichiers et du glisser-deposer.\n",
        'utf8',
    ));
}

function buildOversized() {
    const { width, height, targetBytes } = FIXTURES.oversized;
    const data = drawSpecimen(width, height, 0x5eed05);
    const { buffer } = encodeJpegNearSize({ width, height, data, targetBytes });
    return write('oversized', buffer);
}

const BUILDERS = {
    largeLandscapeJpeg: buildLargeLandscapeJpeg,
    smallJpeg: buildSmallJpeg,
    exifOrientationJpeg: buildExifJpeg,
    png: buildPng,
    pdf: buildPdf,
    disallowedType: buildDisallowed,
    oversized: buildOversized,
};

/** Generates any fixture that is missing (or empty). `force` rebuilds all. */
export function ensureFixtures({ force = false, log = () => {} } = {}) {
    fs.mkdirSync(FILES_DIR, { recursive: true });
    const built = [];
    for (const [key, build] of Object.entries(BUILDERS)) {
        const target = fixturePath(key);
        if (!force && fs.existsSync(target) && fs.statSync(target).size > 0) continue;
        const started = Date.now();
        const result = build();
        log(`  ${result.file.padEnd(34)} ${String(result.bytes).padStart(9)} B  (${Date.now() - started} ms)`);
        built.push(result);
    }
    return built;
}

const runDirectly = process.argv[1] && import.meta.url === `file://${path.resolve(process.argv[1])}`;
if (runDirectly) {
    const force = process.argv.includes('--force');
    console.log(`Fixtures → ${FILES_DIR}${force ? ' (forced rebuild)' : ''}`);
    const built = ensureFixtures({ force, log: line => console.log(line) });
    console.log(built.length ? `${built.length} fixture(s) written.` : 'All fixtures already present.');
}

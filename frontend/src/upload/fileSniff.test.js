// Format sniffing, EXIF reading and orientation geometry.
//
// These are the parts of the mobile capture path that can be proven without a
// browser, so they are proven here rather than inside a Playwright run.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

import { fixturePath } from '../../tests/fixtures/index.js';
import {
    sniffFileType, isHeic, readFtypBrands, readExifOrientation, readJpegDimensions,
    stripExifSegments, orientationTransform, swapsAxes, targetDimensions, replaceExtension,
} from './fileSniff.js';

/**
 * The `ftyp` box an iPhone writes at the head of a HEIC photo: box length,
 * 'ftyp', major brand, minor version, then the compatible brands. This is the
 * real byte layout, not a stand-in — the point of magic-byte detection is that
 * it works when Safari reports the type as 'image/heif', 'image/heic' or ''.
 */
const ftypBox = (major, ...compatible) => {
    const brands = [major, ...compatible];
    const size = 8 + 4 + 4 * compatible.length + 4; // header + major + minor + compat
    const buffer = Buffer.alloc(size);
    buffer.writeUInt32BE(size, 0);
    buffer.write('ftyp', 4, 'ascii');
    buffer.write(brands[0], 8, 'ascii');
    buffer.writeUInt32BE(0, 12); // minor version
    compatible.forEach((brand, index) => buffer.write(brand, 16 + index * 4, 'ascii'));
    return buffer;
};

test('sniffFileType — a real iPhone HEIC ftyp box is detected as HEIC', () => {
    const heic = ftypBox('heic', 'heic', 'mif1', 'miaf');
    assert.equal(sniffFileType(heic), 'heic');
    assert.equal(isHeic(heic), true);
    assert.deepEqual(readFtypBrands(heic), ['heic', 'heic', 'mif1', 'miaf']);
});

test('sniffFileType — HEIC whose MAJOR brand is mif1 is still HEIC', () => {
    // iOS writes this variant for photos edited on device; the major brand
    // alone would miss it, so the compatible brands have to be read too.
    assert.equal(sniffFileType(ftypBox('mif1', 'mif1', 'heic', 'miaf')), 'heic');
});

test('sniffFileType — HEIC image sequences (hevc/msf1) count as HEIC', () => {
    assert.equal(sniffFileType(ftypBox('hevc', 'hevc', 'msf1')), 'heic');
});

test('sniffFileType — AVIF is not mistaken for HEIC despite the shared container', () => {
    // AVIF lists mif1 among its compatible brands. Handing one to a HEIC
    // decoder produces a failure, not an image.
    const avif = ftypBox('avif', 'avif', 'mif1', 'miaf');
    assert.equal(sniffFileType(avif), 'avif');
    assert.equal(isHeic(avif), false);
});

test('sniffFileType — an .heic extension over JPEG bytes is JPEG', () => {
    // Detection never consults the name or the browser-reported MIME type.
    const jpeg = fs.readFileSync(fixturePath('smallJpeg'));
    assert.equal(sniffFileType(jpeg), 'jpeg');
    assert.equal(isHeic(jpeg), false);
});

test('sniffFileType — the fixture set is classified correctly', () => {
    assert.equal(sniffFileType(fs.readFileSync(fixturePath('png'))), 'png');
    assert.equal(sniffFileType(fs.readFileSync(fixturePath('pdf'))), 'pdf');
    assert.equal(sniffFileType(fs.readFileSync(fixturePath('largeLandscapeJpeg'))), 'jpeg');
    assert.equal(sniffFileType(fs.readFileSync(fixturePath('disallowedType'))), 'unknown');
});

test('sniffFileType — truncated and empty input do not throw', () => {
    assert.equal(sniffFileType(new Uint8Array(0)), 'unknown');
    assert.equal(sniffFileType(new Uint8Array([0xff, 0xd8])), 'unknown');
    assert.deepEqual(readFtypBrands(new Uint8Array([0, 0, 0, 24, 0x66])), []);
});

test('readExifOrientation — the portrait fixture reports orientation 6', () => {
    const bytes = fs.readFileSync(fixturePath('exifOrientationJpeg'));
    assert.equal(readExifOrientation(bytes), 6);
});

test('readExifOrientation — a JPEG without EXIF, and a non-JPEG, report null', () => {
    assert.equal(readExifOrientation(fs.readFileSync(fixturePath('smallJpeg'))), null);
    assert.equal(readExifOrientation(fs.readFileSync(fixturePath('png'))), null);
    assert.equal(readExifOrientation(fs.readFileSync(fixturePath('pdf'))), null);
});

test('readExifOrientation — reads a big-endian (MM) EXIF block too', () => {
    // Canon and Nikon write MM; iPhones write II. Both must parse.
    const tiff = Buffer.alloc(26);
    tiff.write('MM', 0, 'ascii');
    tiff.writeUInt16BE(42, 2);
    tiff.writeUInt32BE(8, 4);
    tiff.writeUInt16BE(1, 8);
    tiff.writeUInt16BE(0x0112, 10);
    tiff.writeUInt16BE(3, 12);
    tiff.writeUInt32BE(1, 14);
    tiff.writeUInt16BE(3, 18); // orientation 3
    const identifier = Buffer.from('Exif\0\0', 'latin1');
    const app1 = Buffer.alloc(4 + identifier.length + tiff.length);
    app1[0] = 0xff; app1[1] = 0xe1;
    app1.writeUInt16BE(2 + identifier.length + tiff.length, 2);
    identifier.copy(app1, 4);
    tiff.copy(app1, 4 + identifier.length);
    const jpeg = Buffer.concat([Buffer.from([0xff, 0xd8]), app1, Buffer.from([0xff, 0xd9])]);
    assert.equal(readExifOrientation(jpeg), 3);
});

test('readJpegDimensions — the stored size of the portrait fixture is 1200x1600', () => {
    // STORED, not displayed: the file is a portrait bitmap plus a rotate flag.
    const bytes = fs.readFileSync(fixturePath('exifOrientationJpeg'));
    assert.deepEqual(readJpegDimensions(bytes), { width: 1200, height: 1600 });
});

test('readJpegDimensions — matches the manifest for every JPEG fixture', () => {
    assert.deepEqual(readJpegDimensions(fs.readFileSync(fixturePath('smallJpeg'))),
        { width: 640, height: 427 });
    assert.deepEqual(readJpegDimensions(fs.readFileSync(fixturePath('largeLandscapeJpeg'))),
        { width: 3200, height: 2133 });
});

test('stripExifSegments — removes the rotation flag and nothing else', () => {
    // This is how the explicit-orientation path is entered: a decoder handed
    // these bytes cannot rotate the image behind our back.
    const original = fs.readFileSync(fixturePath('exifOrientationJpeg'));
    const stripped = stripExifSegments(original);

    assert.ok(stripped, 'the fixture does carry EXIF, so something must come back');
    assert.equal(readExifOrientation(stripped), null, 'no orientation tag left');
    assert.equal(sniffFileType(stripped), 'jpeg', 'still a JPEG');
    assert.deepEqual(readJpegDimensions(stripped), { width: 1200, height: 1600 },
        'the frame itself is untouched');
    assert.ok(stripped.length < original.length);
    // The scan data must survive byte for byte: the tail after the last
    // segment is where the image actually lives.
    const tail = 4096;
    assert.deepEqual(
        Buffer.from(stripped.subarray(stripped.length - tail)),
        original.subarray(original.length - tail),
    );
});

test('stripExifSegments — a JPEG with no EXIF, and a non-JPEG, return null', () => {
    assert.equal(stripExifSegments(fs.readFileSync(fixturePath('smallJpeg'))), null);
    assert.equal(stripExifSegments(fs.readFileSync(fixturePath('png'))), null);
});

test('swapsAxes — only 5-8 exchange width and height', () => {
    assert.deepEqual([1, 2, 3, 4, 5, 6, 7, 8].map(swapsAxes),
        [false, false, false, false, true, true, true, true]);
});

/** Applies a transform tuple to a point, the way ctx.transform does. */
const apply = ([a, b, c, d, e, f], x, y) => [a * x + c * y + e, b * x + d * y + f];

test('orientationTransform — orientation 6 rotates 90° clockwise', () => {
    // Source 1200x1600 (portrait) displayed as 1600x1200 (landscape).
    const t = orientationTransform(6, 1200, 1600);
    assert.deepEqual(apply(t, 0, 0), [1600, 0]);       // top-left  -> top-right
    assert.deepEqual(apply(t, 1200, 0), [1600, 1200]); // top-right -> bottom-right
    assert.deepEqual(apply(t, 0, 1600), [0, 0]);       // bottom-left -> top-left
    // The MRZ band lives along the source's bottom edge; after the rotation it
    // must run down the LEFT edge of the displayed image.
    assert.deepEqual(apply(t, 600, 1600), [0, 600]);
});

test('orientationTransform — orientation 8 rotates 90° anticlockwise', () => {
    const t = orientationTransform(8, 1200, 1600);
    assert.deepEqual(apply(t, 0, 0), [0, 1200]);
    assert.deepEqual(apply(t, 1200, 1600), [1600, 0]);
});

test('orientationTransform — orientation 3 rotates 180°', () => {
    const t = orientationTransform(3, 100, 50);
    assert.deepEqual(apply(t, 0, 0), [100, 50]);
    assert.deepEqual(apply(t, 100, 50), [0, 0]);
});

test('orientationTransform — 1 and anything unrecognised are the identity', () => {
    assert.deepEqual(orientationTransform(1, 10, 20), [1, 0, 0, 1, 0, 0]);
    assert.deepEqual(orientationTransform(99, 10, 20), [1, 0, 0, 1, 0, 0]);
});

test('targetDimensions — a 3200x2133 landscape is capped at 2500 on the long edge', () => {
    const target = targetDimensions(3200, 2133, 1, 2500);
    assert.equal(target.width, 2500);
    assert.equal(target.height, Math.round(2133 * (2500 / 3200)));
    assert.ok(target.scale < 1);
});

test('targetDimensions — orientation 6 caps the DISPLAYED long edge', () => {
    // Stored 2133x3200; displayed 3200x2133, so the cap applies to the 3200.
    const target = targetDimensions(2133, 3200, 6, 2500);
    assert.equal(target.width, 2500);
    assert.equal(target.height, Math.round(2133 * (2500 / 3200)));
});

test('targetDimensions — a small image is never enlarged', () => {
    assert.deepEqual(targetDimensions(640, 427, 1, 2500), { width: 640, height: 427, scale: 1 });
});

test('replaceExtension — swaps the extension, keeps the rest of the name', () => {
    assert.equal(replaceExtension('IMG_4021.HEIC', 'jpg'), 'IMG_4021.jpg');
    assert.equal(replaceExtension('passeport.de.marie.heif', 'jpg'), 'passeport.de.marie.jpg');
    assert.equal(replaceExtension('sans-extension', 'jpg'), 'sans-extension.jpg');
    assert.equal(replaceExtension('', 'jpg'), 'document.jpg');
});

// Verifies the generated fixtures with parsers written independently of the
// encoders that produced them: nothing here imports lib/jpeg.js, lib/png.js or
// lib/pdf.js, so a bug in a writer cannot be masked by the same bug in a reader.
//
// The EXIF check is the point of this file. exiftool is not installed on this
// machine, so the tag is parsed from the raw bytes here instead of being taken
// on trust; see tests/README.md.
import { test, before } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import zlib from 'node:zlib';

import { FIXTURES, fixturePath } from './index.js';
import { ensureFixtures } from './generate.mjs';

before(() => { ensureFixtures(); });

const read = key => fs.readFileSync(fixturePath(key));

// --- Independent JPEG reader -------------------------------------------------

/** Walks the JPEG marker segments, returning { markers, sof, exif }. */
function parseJpeg(buffer) {
    assert.equal(buffer[0], 0xff, 'JPEG must start with 0xFFD8 (SOI)');
    assert.equal(buffer[1], 0xd8, 'JPEG must start with 0xFFD8 (SOI)');
    const markers = [];
    let exif = null, sof = null;
    let offset = 2;
    while (offset + 4 <= buffer.length) {
        if (buffer[offset] !== 0xff) break;
        const marker = buffer[offset + 1];
        if (marker === 0xd9) { markers.push(marker); break; }          // EOI
        const length = buffer.readUInt16BE(offset + 2);
        const payload = buffer.subarray(offset + 4, offset + 2 + length);
        markers.push(marker);
        if (marker === 0xe1 && payload.subarray(0, 6).toString('latin1') === 'Exif\0\0') {
            exif = payload.subarray(6);
        }
        // SOF0/1/2 carry the true pixel dimensions (SOFn excluding DHT/DAC/RSTn).
        if (marker >= 0xc0 && marker <= 0xcf && ![0xc4, 0xc8, 0xcc].includes(marker)) {
            sof = { height: payload.readUInt16BE(1), width: payload.readUInt16BE(3) };
        }
        if (marker === 0xda) break;                                     // SOS: entropy data follows
        offset += 2 + length;
    }
    return { markers, sof, exif };
}

/** Reads one IFD0 tag out of a raw EXIF/TIFF block. */
function readExifTag(tiff, wantedTag) {
    const byteOrder = tiff.subarray(0, 2).toString('latin1');
    assert.ok(byteOrder === 'II' || byteOrder === 'MM', `Unknown TIFF byte order: ${byteOrder}`);
    const little = byteOrder === 'II';
    const u16 = at => (little ? tiff.readUInt16LE(at) : tiff.readUInt16BE(at));
    const u32 = at => (little ? tiff.readUInt32LE(at) : tiff.readUInt32BE(at));

    assert.equal(u16(2), 42, 'TIFF magic number must be 42');
    const ifd0 = u32(4);
    const entryCount = u16(ifd0);
    for (let i = 0; i < entryCount; i++) {
        const entry = ifd0 + 2 + i * 12;
        if (u16(entry) !== wantedTag) continue;
        const type = u16(entry + 2);
        assert.equal(type, 3, 'Orientation must be stored as a SHORT (type 3)');
        assert.equal(u32(entry + 4), 1, 'Orientation must have a count of 1');
        return u16(entry + 8); // inline value, low half of the 4-byte slot
    }
    return null;
}

test('EXIF fixture: the Orientation tag really is in the bytes, and the image is portrait', () => {
    const expected = FIXTURES.exifOrientationJpeg.exifOrientation;
    const { markers, sof, exif } = parseJpeg(read('exifOrientationJpeg'));

    assert.ok(exif, 'no APP1/Exif segment found in the fixture');
    assert.equal(readExifTag(exif, 0x0112), expected, `EXIF Orientation must be ${expected}`);
    assert.ok([6, 8].includes(expected), 'the brief asks for a non-default orientation of 6 or 8');

    // Placement: Exif follows JFIF/APP0 when the encoder wrote one.
    const app0 = markers.indexOf(0xe0);
    const app1 = markers.indexOf(0xe1);
    assert.ok(app1 >= 0 && (app0 === -1 || app1 > app0), 'APP1/Exif must come after APP0/JFIF');

    // Stored pixels are portrait; orientation 6 means a viewer rotates them 90° CW.
    assert.equal(sof.width, FIXTURES.exifOrientationJpeg.width);
    assert.equal(sof.height, FIXTURES.exifOrientationJpeg.height);
    assert.ok(sof.height > sof.width, 'the fixture must be stored portrait');
});

test('large landscape JPEG: ~4 MB, at least 3000 px on the long edge, landscape', () => {
    const buffer = read('largeLandscapeJpeg');
    const { sof } = parseJpeg(buffer);
    const target = FIXTURES.largeLandscapeJpeg.targetBytes;

    assert.ok(Math.abs(buffer.length - target) / target < 0.1,
        `expected roughly ${target} B, got ${buffer.length} B`);
    assert.ok(Math.max(sof.width, sof.height) >= 3000, `long edge is only ${Math.max(sof.width, sof.height)} px`);
    assert.ok(sof.width > sof.height, 'must be landscape');
});

test('small JPEG: valid and under 200 KB', () => {
    const buffer = read('smallJpeg');
    assert.ok(buffer.length < FIXTURES.smallJpeg.maxBytes, `${buffer.length} B is over the 200 KB budget`);
    const { sof } = parseJpeg(buffer);
    assert.equal(sof.width, FIXTURES.smallJpeg.width);
});

test('oversized fixture: a valid JPEG over the 10 Mo announced in the upload card', () => {
    const buffer = read('oversized');
    assert.ok(buffer.length > 10 * 1024 * 1024, `${buffer.length} B does not exceed 10 Mo`);
    assert.ok(parseJpeg(buffer).sof, 'the oversized fixture must still decode as a JPEG');
});

test('PNG fixture: signature, IHDR, and every chunk CRC checks out', () => {
    const buffer = read('png');
    assert.deepEqual([...buffer.subarray(0, 8)], [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

    // Independent CRC-32, table-free, so it shares no code with the writer.
    const crc = payload => {
        let c = 0xffffffff;
        for (const byte of payload) {
            c ^= byte;
            for (let k = 0; k < 8; k++) c = c & 1 ? (c >>> 1) ^ 0xedb88320 : c >>> 1;
        }
        return (c ^ 0xffffffff) >>> 0;
    };

    const chunks = [];
    let offset = 8;
    while (offset < buffer.length) {
        const length = buffer.readUInt32BE(offset);
        const type = buffer.subarray(offset + 4, offset + 8).toString('ascii');
        const payload = buffer.subarray(offset + 8, offset + 8 + length);
        const stored = buffer.readUInt32BE(offset + 8 + length);
        assert.equal(crc(buffer.subarray(offset + 4, offset + 8 + length)), stored, `bad CRC on ${type}`);
        chunks.push({ type, payload });
        offset += 12 + length;
    }

    const types = chunks.map(c => c.type);
    assert.deepEqual([types[0], types.at(-1)], ['IHDR', 'IEND']);
    const ihdr = chunks[0].payload;
    assert.equal(ihdr.readUInt32BE(0), FIXTURES.png.width);
    assert.equal(ihdr.readUInt32BE(4), FIXTURES.png.height);
    assert.equal(ihdr[8], 8, 'bit depth');
    assert.equal(ihdr[9], 2, 'colour type: truecolour');

    // The pixel data must actually inflate to the expected scanline count.
    const idat = Buffer.concat(chunks.filter(c => c.type === 'IDAT').map(c => c.payload));
    const raw = zlib.inflateSync(idat);
    assert.equal(raw.length, FIXTURES.png.height * (1 + FIXTURES.png.width * 3));
});

test('PDF fixture: header, one page object, and an xref table pointing at real objects', () => {
    const buffer = read('pdf');
    const text = buffer.toString('latin1');
    assert.ok(text.startsWith('%PDF-1.'), 'missing PDF header');
    assert.ok(text.trimEnd().endsWith('%%EOF'), 'missing %%EOF');
    assert.match(text, /\/Type\s*\/Catalog/);
    assert.match(text, /\/Type\s*\/Page[^s]/);
    assert.match(text, /\/Count 1\b/);

    const startxref = Number(text.match(/startxref\s+(\d+)/)[1]);
    assert.equal(text.slice(startxref, startxref + 4), 'xref', 'startxref must point at the xref table');
    for (const [, offset] of text.matchAll(/^(\d{10}) 00000 n $/gm)) {
        assert.match(text.slice(Number(offset), Number(offset) + 12), /^\d+ 0 obj/,
            `xref entry ${offset} does not point at an object header`);
    }
});

test('disallowed-type fixture exists and is not an image or a PDF', () => {
    const buffer = read('disallowedType');
    assert.ok(buffer.length > 0);
    assert.notEqual(buffer.subarray(0, 2).toString('latin1'), '\xff\xd8');
    assert.notEqual(buffer.subarray(0, 5).toString('latin1'), '%PDF-');
});

test('every fixture in the manifest is on disk after generation', () => {
    for (const key of Object.keys(FIXTURES)) {
        assert.ok(fs.existsSync(fixturePath(key)), `${key} is missing`);
        assert.ok(fs.statSync(fixturePath(key)).size > 0, `${key} is empty`);
    }
});

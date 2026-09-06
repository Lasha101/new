// Format detection and EXIF reading — pure functions over bytes.
//
// Nothing here touches the DOM, so it runs unchanged under `node --test`; the
// browser-only half (canvas, createImageBitmap, heic2any) lives in
// imagePrep.js. Detection is by MAGIC BYTES, never by extension or by the
// File.type the browser reports: Safari labels the same HEIC photo
// 'image/heic', 'image/heif' or '' depending on where it came from, and a photo
// picked from the library often arrives with no type at all.
//
// Privacy: these functions read bytes and return facts about them. They never
// persist anything.

/** Bytes of an ISO-BMFF `ftyp` brand that mean "HEIF still image". */
const HEIF_BRANDS = new Set([
    'heic', 'heix', 'heim', 'heis', // HEVC-coded still images
    'hevc', 'hevx', 'hevm', 'hevs', // HEVC-coded image sequences
    'mif1', 'msf1',                 // generic HEIF image / image sequence
]);

/** AVIF shares the HEIF container and lists `mif1` as a compatible brand. */
const AVIF_BRANDS = new Set(['avif', 'avis']);

/** Normalises anything file-shaped into a Uint8Array view of its head. */
function asBytes(input) {
    if (input instanceof Uint8Array) return input;
    if (input instanceof ArrayBuffer) return new Uint8Array(input);
    if (ArrayBuffer.isView(input)) return new Uint8Array(input.buffer, input.byteOffset, input.byteLength);
    throw new TypeError('Expected a Uint8Array, ArrayBuffer or typed array of file bytes.');
}

const ascii = (bytes, start, length) => {
    let out = '';
    for (let i = start; i < start + length && i < bytes.length; i++) out += String.fromCharCode(bytes[i]);
    return out;
};

const startsWith = (bytes, signature) =>
    signature.every((byte, index) => bytes[index] === byte);

/**
 * Every `ftyp` brand the file declares: the major brand plus the compatible
 * brands listed after it. A HEIC from an iPhone is frequently major-brand
 * `mif1` with `heic` further down the list, so the major brand alone is not
 * enough.
 *
 * @returns {string[]} lower-case four-character brands, [] when not ISO-BMFF.
 */
export function readFtypBrands(input) {
    const bytes = asBytes(input);
    if (bytes.length < 12 || ascii(bytes, 4, 4) !== 'ftyp') return [];
    // Box size is big-endian at offset 0; clamp to what we actually hold.
    const declared = (bytes[0] << 24 | bytes[1] << 16 | bytes[2] << 8 | bytes[3]) >>> 0;
    const end = Math.min(bytes.length, declared >= 16 ? declared : bytes.length);
    const brands = [ascii(bytes, 8, 4).toLowerCase()];
    // Major brand (8..12), minor version (12..16), then compatible brands.
    for (let offset = 16; offset + 4 <= end; offset += 4) {
        brands.push(ascii(bytes, offset, 4).toLowerCase());
    }
    return brands.filter(brand => /^[\x20-\x7e]{4}$/.test(brand));
}

/**
 * The format of a file, from its first bytes.
 *
 * @param {Uint8Array|ArrayBuffer} input the head of the file (64 bytes is plenty)
 * @returns {'jpeg'|'png'|'pdf'|'heic'|'avif'|'gif'|'webp'|'tiff'|'unknown'}
 */
export function sniffFileType(input) {
    const bytes = asBytes(input);
    if (startsWith(bytes, [0xff, 0xd8, 0xff])) return 'jpeg';
    if (startsWith(bytes, [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a])) return 'png';
    if (startsWith(bytes, [0x25, 0x50, 0x44, 0x46])) return 'pdf';           // %PDF
    if (startsWith(bytes, [0x47, 0x49, 0x46, 0x38])) return 'gif';           // GIF8
    if (ascii(bytes, 0, 4) === 'RIFF' && ascii(bytes, 8, 4) === 'WEBP') return 'webp';
    if (startsWith(bytes, [0x49, 0x49, 0x2a, 0x00]) || startsWith(bytes, [0x4d, 0x4d, 0x00, 0x2a])) return 'tiff';

    const brands = readFtypBrands(bytes);
    if (brands.length) {
        // AVIF wins when it is declared: it lists mif1 as compatible, and
        // handing an AVIF to a HEIC decoder produces a failure, not an image.
        if (brands.some(brand => AVIF_BRANDS.has(brand))) return 'avif';
        if (brands.some(brand => HEIF_BRANDS.has(brand))) return 'heic';
    }
    return 'unknown';
}

/** True when the bytes are a HEIC/HEIF still image (never for AVIF). */
export const isHeic = input => sniffFileType(input) === 'heic';

// --- EXIF ----------------------------------------------------------------

const APP1 = 0xe1;
const SOS = 0xda;
const ORIENTATION_TAG = 0x0112;

/**
 * The EXIF Orientation tag (0x0112), or null when the file carries none.
 *
 * Canvas re-encoding silently discards EXIF, so a portrait photo that the
 * camera stored landscape-with-a-rotation-flag arrives at the OCR sideways and
 * its MRZ becomes unreadable. Everything that re-encodes must consult this.
 *
 * @param {Uint8Array|ArrayBuffer} input the head of a JPEG (64 KB covers any
 *   real EXIF block; the whole file is fine too)
 * @returns {number|null} 1-8, or null
 */
export function readExifOrientation(input) {
    const bytes = asBytes(input);
    if (!startsWith(bytes, [0xff, 0xd8])) return null; // not a JPEG

    let offset = 2;
    while (offset + 4 <= bytes.length) {
        if (bytes[offset] !== 0xff) return null;       // desynchronised
        const marker = bytes[offset + 1];
        if (marker === SOS || marker === 0xd9) return null;  // image data starts; no EXIF
        // Standalone markers (RSTn, TEM) carry no length field.
        if (marker === 0x01 || (marker >= 0xd0 && marker <= 0xd7)) { offset += 2; continue; }

        const length = (bytes[offset + 2] << 8) | bytes[offset + 3];
        if (length < 2) return null;
        if (marker === APP1 && ascii(bytes, offset + 4, 6) === 'Exif\0\0') {
            const orientation = readOrientationFromTiff(bytes, offset + 10,
                Math.min(bytes.length, offset + 2 + length));
            if (orientation !== null) return orientation;
        }
        offset += 2 + length;
    }
    return null;
}

/** IFD0 walk inside the TIFF block of an APP1 segment. */
function readOrientationFromTiff(bytes, tiffStart, limit) {
    if (tiffStart + 8 > limit) return null;
    const byteOrder = ascii(bytes, tiffStart, 2);
    if (byteOrder !== 'II' && byteOrder !== 'MM') return null;
    const little = byteOrder === 'II';

    const u16 = at => (little ? bytes[at] | (bytes[at + 1] << 8) : (bytes[at] << 8) | bytes[at + 1]);
    const u32 = at => ((little
        ? bytes[at] | (bytes[at + 1] << 8) | (bytes[at + 2] << 16) | (bytes[at + 3] << 24)
        : (bytes[at] << 24) | (bytes[at + 1] << 16) | (bytes[at + 2] << 8) | bytes[at + 3]) >>> 0);

    if (u16(tiffStart + 2) !== 42) return null;
    const ifd0 = tiffStart + u32(tiffStart + 4);
    if (ifd0 + 2 > limit) return null;

    const entries = u16(ifd0);
    for (let index = 0; index < entries; index++) {
        const entry = ifd0 + 2 + index * 12;
        if (entry + 12 > limit) return null;
        if (u16(entry) === ORIENTATION_TAG) {
            const value = u16(entry + 8); // SHORT, stored inline in the value slot
            return value >= 1 && value <= 8 ? value : null;
        }
    }
    return null;
}

/**
 * The same JPEG with every APP1/Exif segment removed.
 *
 * This is how the explicit-orientation path is entered deliberately. Browsers
 * no longer offer a way to ask for an unrotated decode — `createImageBitmap`'s
 * `imageOrientation: 'none'` was dropped from the specification and current
 * Chromium ignores it — so the only reliable way to get the stored pixels is to
 * hand the decoder bytes that carry no rotation flag. What comes back is then
 * rotated by {@link orientationTransform} from the value read BEFORE stripping.
 *
 * @returns {Uint8Array|null} null when there was no EXIF to remove.
 */
export function stripExifSegments(input) {
    const bytes = asBytes(input);
    if (!startsWith(bytes, [0xff, 0xd8])) return null;

    const keep = [bytes.subarray(0, 2)];
    let offset = 2;
    let removed = 0;
    while (offset + 4 <= bytes.length) {
        if (bytes[offset] !== 0xff) break;
        const marker = bytes[offset + 1];
        if (marker === SOS || marker === 0xd9) break;
        if (marker === 0x01 || (marker >= 0xd0 && marker <= 0xd7)) {
            keep.push(bytes.subarray(offset, offset + 2));
            offset += 2;
            continue;
        }
        const length = (bytes[offset + 2] << 8) | bytes[offset + 3];
        if (length < 2) break;
        const end = offset + 2 + length;
        if (marker === APP1 && ascii(bytes, offset + 4, 6) === 'Exif\0\0') removed++;
        else keep.push(bytes.subarray(offset, end));
        offset = end;
    }
    if (removed === 0) return null;
    keep.push(bytes.subarray(offset)); // scan data and everything after it

    const total = keep.reduce((sum, part) => sum + part.length, 0);
    const out = new Uint8Array(total);
    let at = 0;
    for (const part of keep) { out.set(part, at); at += part.length; }
    return out;
}

/** Start-of-frame markers. Every one carries the frame's true pixel size. */
const SOF_MARKERS = new Set([
    0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7,
    0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf,
]);

/**
 * The dimensions a JPEG is STORED at, read from its SOF segment.
 *
 * This is the ground truth against which a decode can be checked: if the
 * browser hands back a bitmap whose width and height are the other way round,
 * it applied the EXIF orientation itself and we must not apply it again.
 *
 * @returns {{width:number, height:number}|null}
 */
export function readJpegDimensions(input) {
    const bytes = asBytes(input);
    if (!startsWith(bytes, [0xff, 0xd8])) return null;

    let offset = 2;
    while (offset + 4 <= bytes.length) {
        if (bytes[offset] !== 0xff) return null;
        const marker = bytes[offset + 1];
        if (marker === 0xd9) return null;
        if (marker === 0x01 || (marker >= 0xd0 && marker <= 0xd7)) { offset += 2; continue; }
        const length = (bytes[offset + 2] << 8) | bytes[offset + 3];
        if (length < 2) return null;
        if (SOF_MARKERS.has(marker)) {
            if (offset + 9 > bytes.length) return null;
            return {
                height: (bytes[offset + 5] << 8) | bytes[offset + 6],
                width: (bytes[offset + 7] << 8) | bytes[offset + 8],
            };
        }
        if (marker === SOS) return null;
        offset += 2 + length;
    }
    return null;
}

// --- Orientation geometry ------------------------------------------------

/** True when the orientation swaps the image's width and height. */
export const swapsAxes = orientation => orientation >= 5 && orientation <= 8;

/**
 * The canvas transform that maps source pixel space onto display space.
 *
 * Returned as the six arguments of `ctx.transform(a, b, c, d, e, f)`, which
 * sends a source pixel (x, y) to (a·x + c·y + e, b·x + d·y + f). Expressed in
 * the SOURCE dimensions, so the caller never has to work out which way round
 * width and height go.
 *
 * @param {number} orientation 1-8
 * @param {number} sourceWidth  stored (unrotated) width
 * @param {number} sourceHeight stored (unrotated) height
 */
export function orientationTransform(orientation, sourceWidth, sourceHeight) {
    const w = sourceWidth;
    const h = sourceHeight;
    switch (orientation) {
        case 2: return [-1, 0, 0, 1, w, 0];      // mirror horizontally
        case 3: return [-1, 0, 0, -1, w, h];     // rotate 180°
        case 4: return [1, 0, 0, -1, 0, h];      // mirror vertically
        case 5: return [0, 1, 1, 0, 0, 0];       // transpose
        case 6: return [0, 1, -1, 0, h, 0];      // rotate 90° clockwise
        case 7: return [0, -1, -1, 0, h, w];     // transverse
        case 8: return [0, -1, 1, 0, 0, w];      // rotate 90° anticlockwise
        default: return [1, 0, 0, 1, 0, 0];      // 1, or anything unknown
    }
}

/**
 * Displayed size after orientation, then scaled so the long edge fits maxEdge.
 * Never enlarges: a small photo keeps its size.
 */
export function targetDimensions(sourceWidth, sourceHeight, orientation, maxEdge) {
    const displayWidth = swapsAxes(orientation) ? sourceHeight : sourceWidth;
    const displayHeight = swapsAxes(orientation) ? sourceWidth : sourceHeight;
    const scale = Math.min(1, maxEdge / Math.max(displayWidth, displayHeight));
    return {
        width: Math.max(1, Math.round(displayWidth * scale)),
        height: Math.max(1, Math.round(displayHeight * scale)),
        scale,
    };
}

/** `photo.heic` + 'jpg' -> `photo.jpg`. Used only when the bytes really changed format. */
export function replaceExtension(name, extension) {
    const safe = String(name || 'document');
    const dot = safe.lastIndexOf('.');
    const stem = dot > 0 ? safe.slice(0, dot) : safe;
    return `${stem}.${extension}`;
}

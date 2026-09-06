// JPEG fixture encoder: pixel data via jpeg-js (pure JS, no native binary), then
// two byte-level operations the encoder does not offer — an EXIF orientation tag
// and size padding — written directly against the JFIF/Exif specs.
import jpeg from 'jpeg-js';

const SOI = 0xd8, APP0 = 0xe0, APP1 = 0xe1, COM = 0xfe, SOS = 0xda;

/** Encodes an RGBA buffer as a baseline JPEG at the given quality. */
export function encodeJpeg({ width, height, data, quality }) {
    return Buffer.from(jpeg.encode({ data, width, height }, quality).data);
}

/**
 * Encodes at a quality chosen so the file lands close to `targetBytes`, then
 * tops the result up with JPEG comment segments if it is still short.
 * Returns { buffer, quality, padded }.
 */
export function encodeJpegNearSize({ width, height, data, targetBytes, tolerance = 0.05, maxSteps = 8 }) {
    let low = 10, high = 100, best = null, bestQuality = 0;
    for (let step = 0; step < maxSteps && low <= high; step++) {
        const quality = Math.round((low + high) / 2);
        const buffer = encodeJpeg({ width, height, data, quality });
        if (best === null || Math.abs(buffer.length - targetBytes) < Math.abs(best.length - targetBytes)) {
            best = buffer; bestQuality = quality;
        }
        if (Math.abs(buffer.length - targetBytes) / targetBytes <= tolerance) break;
        if (buffer.length < targetBytes) low = quality + 1; else high = quality - 1;
    }
    if (best.length >= targetBytes) return { buffer: best, quality: bestQuality, padded: 0 };
    const padded = targetBytes - best.length;
    return { buffer: padJpegToSize(best, targetBytes), quality: bestQuality, padded };
}

/**
 * Grows a JPEG to `targetBytes` by inserting COM (comment) segments in the
 * header, immediately before the start-of-scan marker. Comments after SOS would
 * corrupt the entropy-coded stream, so they go in the header area where the
 * spec allows arbitrary application/comment segments.
 *
 * The size is exact whenever the shortfall is at least 4 bytes (the smallest
 * possible comment segment); a shortfall of 1-3 bytes overshoots by up to 3.
 */
export function padJpegToSize(buffer, targetBytes) {
    if (buffer.length >= targetBytes) return buffer;
    const sosOffset = findMarkerOffset(buffer, SOS);
    if (sosOffset < 0) throw new Error('No SOS marker: not a baseline JPEG.');

    const parts = [buffer.subarray(0, sosOffset)];
    let remaining = targetBytes - buffer.length;
    // Each segment costs 4 bytes of overhead (marker + 2-byte length) and
    // carries at most 65533 payload bytes.
    while (remaining > 0) {
        const payloadSize = Math.max(0, Math.min(65533, remaining - 4));
        const segment = Buffer.alloc(4 + payloadSize);
        segment[0] = 0xff; segment[1] = COM;
        segment.writeUInt16BE(payloadSize + 2, 2);
        segment.fill(0x20, 4); // spaces: the comment stays printable
        parts.push(segment);
        remaining -= segment.length;
    }
    parts.push(buffer.subarray(sosOffset));
    return Buffer.concat(parts);
}

/**
 * Inserts an EXIF APP1 segment carrying only the Orientation tag (0x0112).
 * Placed after APP0/JFIF when present, as Exif requires. Canvas re-encoding in
 * the browser silently drops this segment, which is exactly what the fixture is
 * meant to expose.
 */
export function injectExifOrientation(buffer, orientation) {
    if (![1, 2, 3, 4, 5, 6, 7, 8].includes(orientation)) {
        throw new Error(`Invalid EXIF orientation: ${orientation}`);
    }
    // TIFF header (little endian) + IFD0 with a single SHORT entry.
    const tiff = Buffer.alloc(26);
    tiff.write('II', 0, 'ascii');          // byte order: little endian
    tiff.writeUInt16LE(42, 2);             // TIFF magic
    tiff.writeUInt32LE(8, 4);              // offset of IFD0
    tiff.writeUInt16LE(1, 8);              // one directory entry
    tiff.writeUInt16LE(0x0112, 10);        // tag: Orientation
    tiff.writeUInt16LE(3, 12);             // type: SHORT
    tiff.writeUInt32LE(1, 14);             // count
    tiff.writeUInt16LE(orientation, 18);   // value (inline, low half of the 4-byte slot)
    tiff.writeUInt32LE(0, 22);             // no next IFD

    const identifier = Buffer.from('Exif\0\0', 'latin1');
    const app1 = Buffer.alloc(4 + identifier.length + tiff.length);
    app1[0] = 0xff; app1[1] = APP1;
    app1.writeUInt16BE(2 + identifier.length + tiff.length, 2);
    identifier.copy(app1, 4);
    tiff.copy(app1, 4 + identifier.length);

    const insertAt = exifInsertionPoint(buffer);
    return Buffer.concat([buffer.subarray(0, insertAt), app1, buffer.subarray(insertAt)]);
}

/** Offset just after SOI, or just after APP0/JFIF when the encoder wrote one. */
function exifInsertionPoint(buffer) {
    if (buffer[0] !== 0xff || buffer[1] !== SOI) throw new Error('Not a JPEG (no SOI).');
    if (buffer[2] === 0xff && buffer[3] === APP0) return 4 + buffer.readUInt16BE(4);
    return 2;
}

/** Offset of the first `0xFF <marker>` pair, walking the segment lengths. */
function findMarkerOffset(buffer, marker) {
    let offset = 2; // skip SOI
    while (offset + 4 <= buffer.length) {
        if (buffer[offset] !== 0xff) return -1;
        const current = buffer[offset + 1];
        if (current === marker) return offset;
        offset += 2 + buffer.readUInt16BE(offset + 2);
    }
    return -1;
}

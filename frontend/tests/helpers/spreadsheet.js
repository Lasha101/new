// Reading back what the app downloaded.
//
// The download tests must prove the *content* of the exported files — the column
// set, its order, and that accented French text survived the encoding — so the
// bytes have to be parsed, not merely weighed. Both readers are dependency-free
// and handle what the two backends produce: the mock writes a store-only ZIP of
// inline strings, the real backend (openpyxl) writes a deflated one with a
// shared-string table.
import { readFileSync } from 'node:fs';
import { inflateRawSync } from 'node:zlib';

/** Entries of a ZIP archive, as { name -> Buffer }. Handles stored + deflate. */
export function unzip(buffer) {
    // Locate the end-of-central-directory record, scanning back over any comment.
    let end = -1;
    for (let i = buffer.length - 22; i >= 0 && i > buffer.length - 22 - 65_536; i--) {
        if (buffer.readUInt32LE(i) === 0x06054b50) { end = i; break; }
    }
    if (end < 0) throw new Error('unzip: no end-of-central-directory record (not a ZIP?)');

    const count = buffer.readUInt16LE(end + 10);
    let pointer = buffer.readUInt32LE(end + 16);
    const files = {};

    for (let i = 0; i < count; i++) {
        if (buffer.readUInt32LE(pointer) !== 0x02014b50) throw new Error('unzip: bad central header');
        const method = buffer.readUInt16LE(pointer + 10);
        const compressedSize = buffer.readUInt32LE(pointer + 20);
        const nameLength = buffer.readUInt16LE(pointer + 28);
        const extraLength = buffer.readUInt16LE(pointer + 30);
        const commentLength = buffer.readUInt16LE(pointer + 32);
        const localOffset = buffer.readUInt32LE(pointer + 42);
        const name = buffer.toString('utf8', pointer + 46, pointer + 46 + nameLength);

        // The local header repeats the name/extra lengths, which may differ.
        const localNameLength = buffer.readUInt16LE(localOffset + 26);
        const localExtraLength = buffer.readUInt16LE(localOffset + 28);
        const dataStart = localOffset + 30 + localNameLength + localExtraLength;
        const raw = buffer.subarray(dataStart, dataStart + compressedSize);

        if (method === 0) files[name] = Buffer.from(raw);
        else if (method === 8) files[name] = inflateRawSync(raw);
        else throw new Error(`unzip: unsupported compression method ${method} for ${name}`);

        pointer += 46 + nameLength + extraLength + commentLength;
    }
    return files;
}

const unescapeXml = value => value
    .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'").replace(/&#(\d+);/g, (_, code) => String.fromCodePoint(Number(code)))
    .replace(/&amp;/g, '&');

/** Concatenated <t> text of one XML fragment. */
const textOf = fragment => [...fragment.matchAll(/<t(?:\s[^>]*)?>([\s\S]*?)<\/t>/g)]
    .map(match => unescapeXml(match[1])).join('');

/**
 * Rows of the first worksheet of an .xlsx, as string[][].
 *
 * Understands inline strings (`t="inlineStr"`), the shared-string table
 * (`t="s"`) and plain numeric cells — the three shapes these exports use.
 */
export function readXlsx(pathOrBuffer) {
    const buffer = Buffer.isBuffer(pathOrBuffer) ? pathOrBuffer : readFileSync(pathOrBuffer);
    const files = unzip(buffer);

    const sheetName = Object.keys(files).find(name => /^xl\/worksheets\/sheet1\.xml$/.test(name))
        || Object.keys(files).find(name => name.startsWith('xl/worksheets/'));
    if (!sheetName) throw new Error(`readXlsx: no worksheet in ${Object.keys(files).join(', ')}`);

    const shared = files['xl/sharedStrings.xml']
        ? [...files['xl/sharedStrings.xml'].toString('utf8').matchAll(/<si>([\s\S]*?)<\/si>/g)]
            .map(match => textOf(match[1]))
        : [];

    const sheet = files[sheetName].toString('utf8');
    return [...sheet.matchAll(/<row[^>]*>([\s\S]*?)<\/row>/g)].map(rowMatch =>
        [...rowMatch[1].matchAll(/<c\b([^>]*)>([\s\S]*?)<\/c>/g)].map(([, attributes, body]) => {
            const type = attributes.match(/\bt="([^"]+)"/)?.[1];
            if (type === 'inlineStr') return textOf(body);
            const value = body.match(/<v>([\s\S]*?)<\/v>/)?.[1] ?? '';
            if (type === 's') return shared[Number(value)] ?? '';
            return unescapeXml(value);
        }));
}

/**
 * Rows of a semicolon-separated CSV, as string[][].
 *
 * The backend writes UTF-8 with a BOM, CRLF line endings, and wraps all-digit
 * values as `="0123"` so Excel keeps their leading zeros — all three are undone
 * here so the test compares the values a user would see.
 */
export function readCsv(pathOrBuffer) {
    const text = (Buffer.isBuffer(pathOrBuffer) ? pathOrBuffer : readFileSync(pathOrBuffer))
        .toString('utf8').replace(/^\uFEFF/, '');
    return text.split(/\r?\n/).filter(line => line.length > 0).map(line =>
        line.split(';').map(cell => cell.replace(/^="(.*)"$/, '$1')));
}

// A real, openable .xlsx for the mocked Excel download: a store-only ZIP holding
// the five parts a spreadsheet reader needs. Writing it by hand keeps the
// harness dependency-free, and means the download test asserts on a genuine
// workbook rather than on an opaque blob.
//
// The *content* rules of the real export (French headers, uppercase values,
// DD/MM/YYYY dates, AutoFilter, column widths) are the backend's job and are
// already covered by backend/tests/test_export.py — this file only has to be a
// valid workbook.
import { crc32 } from '../fixtures/lib/bytes.js';

function localHeader(entry, offset) {
    const name = Buffer.from(entry.name, 'utf8');
    const header = Buffer.alloc(30);
    header.writeUInt32LE(0x04034b50, 0);
    header.writeUInt16LE(20, 4);            // version needed
    header.writeUInt16LE(0, 6);             // flags
    header.writeUInt16LE(0, 8);             // stored, no compression
    header.writeUInt16LE(0, 10);            // mod time (fixed: deterministic output)
    header.writeUInt16LE(0x2821, 12);       // mod date: 2020-01-01
    header.writeUInt32LE(entry.crc, 14);
    header.writeUInt32LE(entry.data.length, 18);
    header.writeUInt32LE(entry.data.length, 22);
    header.writeUInt16LE(name.length, 26);
    header.writeUInt16LE(0, 28);            // no extra field
    entry.offset = offset;
    return Buffer.concat([header, name, entry.data]);
}

function centralHeader(entry) {
    const name = Buffer.from(entry.name, 'utf8');
    const header = Buffer.alloc(46);
    header.writeUInt32LE(0x02014b50, 0);
    header.writeUInt16LE(20, 4);            // version made by
    header.writeUInt16LE(20, 6);            // version needed
    header.writeUInt16LE(0, 8);
    header.writeUInt16LE(0, 10);
    header.writeUInt16LE(0, 12);
    header.writeUInt16LE(0x2821, 14);
    header.writeUInt32LE(entry.crc, 16);
    header.writeUInt32LE(entry.data.length, 20);
    header.writeUInt32LE(entry.data.length, 24);
    header.writeUInt16LE(name.length, 28);
    header.writeUInt16LE(0, 30);            // extra
    header.writeUInt16LE(0, 32);            // comment
    header.writeUInt16LE(0, 34);            // disk number
    header.writeUInt16LE(0, 36);            // internal attributes
    header.writeUInt32LE(0, 38);            // external attributes
    header.writeUInt32LE(entry.offset, 42);
    return Buffer.concat([header, name]);
}

/** Builds a ZIP container from [{ name, data }] entries, stored uncompressed. */
export function zip(files) {
    const entries = files.map(file => ({
        name: file.name,
        data: Buffer.isBuffer(file.data) ? file.data : Buffer.from(file.data, 'utf8'),
        crc: 0, offset: 0,
    }));
    for (const entry of entries) entry.crc = crc32(entry.data);

    const locals = [];
    let offset = 0;
    for (const entry of entries) {
        const block = localHeader(entry, offset);
        locals.push(block);
        offset += block.length;
    }

    const centrals = entries.map(centralHeader);
    const centralSize = centrals.reduce((total, block) => total + block.length, 0);

    const end = Buffer.alloc(22);
    end.writeUInt32LE(0x06054b50, 0);
    end.writeUInt16LE(0, 4);
    end.writeUInt16LE(0, 6);
    end.writeUInt16LE(entries.length, 8);
    end.writeUInt16LE(entries.length, 10);
    end.writeUInt32LE(centralSize, 12);
    end.writeUInt32LE(offset, 16);
    end.writeUInt16LE(0, 20);

    return Buffer.concat([...locals, ...centrals, end]);
}

const escapeXml = value => String(value ?? '')
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&apos;');

const columnName = (index) => {
    let name = '', n = index;
    do { name = String.fromCharCode(65 + (n % 26)) + name; n = Math.floor(n / 26) - 1; } while (n >= 0);
    return name;
};

/**
 * A one-sheet workbook of inline strings.
 * @param {string[][]} rows First row is the header row.
 * @param {string} sheetName
 */
export function buildXlsx(rows, sheetName = 'Passeports') {
    const sheetRows = rows.map((row, rowIndex) => {
        const cells = row.map((value, cellIndex) =>
            `<c r="${columnName(cellIndex)}${rowIndex + 1}" t="inlineStr">`
            + `<is><t xml:space="preserve">${escapeXml(value)}</t></is></c>`).join('');
        return `<row r="${rowIndex + 1}">${cells}</row>`;
    }).join('');

    return zip([
        {
            name: '[Content_Types].xml',
            data: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                + '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                + '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                + '<Default Extension="xml" ContentType="application/xml"/>'
                + '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                + '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                + '</Types>',
        },
        {
            name: '_rels/.rels',
            data: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                + '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
                + '</Relationships>',
        },
        {
            name: 'xl/workbook.xml',
            data: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                + '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                + 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                + `<sheets><sheet name="${escapeXml(sheetName)}" sheetId="1" r:id="rId1"/></sheets></workbook>`,
        },
        {
            name: 'xl/_rels/workbook.xml.rels',
            data: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                + '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
                + '</Relationships>',
        },
        {
            name: 'xl/worksheets/sheet1.xml',
            data: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                + '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                + `<sheetData>${sheetRows}</sheetData></worksheet>`,
        },
    ]);
}

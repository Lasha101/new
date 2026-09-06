// Minimal single-page PDF writer: enough structure (catalog, page tree, content
// stream, xref table) for a real PDF reader — the backend opens uploads with
// PyMuPDF — without pulling in a PDF library.

/**
 * @param {string[]} lines Text drawn on the page, one line each. ASCII only:
 *   the base-14 Helvetica encoding used here has no reliable accented glyphs,
 *   and a fixture must not depend on a font file.
 */
export function encodePdf(lines) {
    const content = [
        'BT', '/F1 14 Tf', '1 0 0 1 60 760 Tm', '18 TL',
        ...lines.map(line => `(${line.replace(/([\\()])/g, '\\$1')}) Tj T*`),
        'ET',
    ].join('\n');

    const objects = [
        '<< /Type /Catalog /Pages 2 0 R >>',
        '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
        '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] '
            + '/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>',
        `<< /Length ${Buffer.byteLength(content, 'latin1')} >>\nstream\n${content}\nendstream`,
        '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>',
    ];

    let pdf = '%PDF-1.4\n';
    const offsets = [];
    objects.forEach((body, index) => {
        offsets.push(Buffer.byteLength(pdf, 'latin1'));
        pdf += `${index + 1} 0 obj\n${body}\nendobj\n`;
    });

    const xrefOffset = Buffer.byteLength(pdf, 'latin1');
    pdf += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`;
    for (const offset of offsets) pdf += `${String(offset).padStart(10, '0')} 00000 n \n`;
    pdf += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF\n`;

    return Buffer.from(pdf, 'latin1');
}

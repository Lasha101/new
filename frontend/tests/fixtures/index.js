// The fixture manifest: one entry per file the suites may upload, with the
// property each fixture exists to exercise. The binaries themselves are
// generated (see generate.mjs) rather than committed — they total ~20 MB, and a
// real client document must never be used as a fixture.
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const FIXTURES_DIR = path.dirname(fileURLToPath(import.meta.url));
export const FILES_DIR = path.join(FIXTURES_DIR, 'files');

const MB = 1024 * 1024;

export const FIXTURES = {
    largeLandscapeJpeg: {
        file: 'large-landscape.jpg',
        mime: 'image/jpeg',
        width: 3200, height: 2133,
        targetBytes: 4 * MB,
        purpose: "Photo « telle que sortie du téléphone » : ~4 Mo, 3200 px sur le grand côté. "
            + 'Exercises client-side resizing, upload progress and the 10 Mo notice.',
    },
    smallJpeg: {
        file: 'small.jpg',
        mime: 'image/jpeg',
        width: 640, height: 427,
        maxBytes: 200 * 1024,
        purpose: 'Fast happy path: a valid JPEG under 200 KB, for tests where upload '
            + 'time is noise rather than the subject.',
    },
    exifOrientationJpeg: {
        file: 'portrait-exif-orientation-6.jpg',
        mime: 'image/jpeg',
        width: 1200, height: 1600,
        exifOrientation: 6,
        purpose: 'THE important one. Portrait JPEG whose EXIF Orientation tag is 6 '
            + '(rotate 90° CW). Canvas re-encoding drops EXIF silently, and a rotated '
            + 'MRZ fails OCR — any resize/compress step must be checked against this file.',
    },
    png: {
        file: 'document.png',
        mime: 'image/png',
        width: 900, height: 600,
        purpose: 'PNG branch of the accept list (image/png), including its lossless '
            + 'alpha-free encoding.',
    },
    pdf: {
        file: 'document.pdf',
        mime: 'application/pdf',
        pages: 1,
        purpose: 'PDF branch: the app accepts application/pdf and the backend renders '
            + 'pages with PyMuPDF, so the PDF path must stay covered.',
    },
    disallowedType: {
        file: 'disallowed.txt',
        mime: 'text/plain',
        purpose: 'Rejection test: a type outside accept="image/png, image/jpeg, '
            + 'image/jpg, application/pdf". See tests/README.md — the app rejects it on '
            + 'drag-and-drop only; there is no check on the file picker or the server.',
    },
    oversized: {
        file: 'oversized.jpg',
        mime: 'image/jpeg',
        width: 3200, height: 2133,
        targetBytes: 11 * MB,
        purpose: 'Over the 10 Mo announced in the upload card. See tests/README.md — no '
            + 'size limit is enforced today, so this fixture is for the package that adds one.',
    },
};

/** Absolute path of a fixture by manifest key. */
export function fixturePath(key) {
    const fixture = FIXTURES[key];
    if (!fixture) throw new Error(`Unknown fixture "${key}". Known: ${Object.keys(FIXTURES).join(', ')}`);
    return path.join(FILES_DIR, fixture.file);
}

/** [key, absolutePath] for every fixture. */
export function allFixtures() {
    return Object.keys(FIXTURES).map(key => [key, fixturePath(key)]);
}

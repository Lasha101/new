// The production bundle must not mention Google's font hosts.
//
// This runs under `node --test`, so it is part of the browser-free `npm test`
// that CI already runs after `npm run build` — the check lands on the artefact
// that actually ships, not on the source it was built from. A stale or missing
// dist is built here rather than silently passing on nothing.
import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { readdirSync, readFileSync, statSync, existsSync } from 'node:fs';
import { join, dirname, extname } from 'node:path';
import { fileURLToPath } from 'node:url';

const FRONTEND = dirname(dirname(dirname(fileURLToPath(import.meta.url))));

// THE WHOLE BUILD — both halves.
//
// dist/ has two of them now: dist/app/ is what `vite build` produces, and the
// root of dist/ is the public site that scripts/assemble-site.mjs copies out of
// frontend/site/. This test guards both.
//
// It briefly guarded only the application. The 22 pages in frontend/site/ were
// authored to link fonts.googleapis.com, frontend/site/ is read-only, and
// scanning all of dist/ reported 88 offenders that could not be fixed here — so
// the scan was narrowed rather than deleted. That was a workaround, and it is
// gone: assemble-site.mjs now rewrites the COPY of every page to the
// self-hosted bundle it builds from @fontsource into dist/fonts/, and refuses
// to finish if any page still names a Google host. The source pages are still
// untouched; the shipped ones simply no longer ask Google for anything.
//
// So the guarantee is now the same for both halves, and it is the one the
// product actually sells: opening ANY page of scanid.fr sends no visitor IP to
// a third party.
const DIST = join(FRONTEND, 'dist');
const APP_DIST = join(DIST, 'app');
const FORBIDDEN = ['googleapis.com', 'gstatic.com', 'fonts.googleapis', 'fonts.gstatic'];

/** Newest mtime under a directory, so a dist older than src can be spotted. */
function newestMtime(directory, skip = new Set(['node_modules', 'dist', '.git'])) {
    let newest = 0;
    const walk = (current) => {
        for (const entry of readdirSync(current, { withFileTypes: true })) {
            if (skip.has(entry.name)) continue;
            const full = join(current, entry.name);
            if (entry.isDirectory()) walk(full);
            else newest = Math.max(newest, statSync(full).mtimeMs);
        }
    };
    walk(directory);
    return newest;
}

function ensureBuild() {
    const fresh = existsSync(DIST)
        && newestMtime(DIST, new Set()) >= newestMtime(join(FRONTEND, 'src'), new Set());
    if (fresh) return 'reused the existing dist';
    execFileSync('npm', ['run', 'build'], { cwd: FRONTEND, stdio: 'pipe' });
    return 'built a fresh dist';
}

/** Every file under dist, as [relativePath, Buffer]. */
function distFiles() {
    const files = [];
    const walk = (current, prefix = '') => {
        for (const entry of readdirSync(current, { withFileTypes: true })) {
            const full = join(current, entry.name);
            const relative = prefix ? `${prefix}/${entry.name}` : entry.name;
            if (entry.isDirectory()) walk(full, relative);
            else files.push([relative, readFileSync(full)]);
        }
    };
    walk(DIST);
    return files;
}

test('the build output contains no googleapis/gstatic reference', () => {
    ensureBuild();
    const files = distFiles();
    assert.ok(files.length > 0, 'dist is empty');

    const offenders = [];
    for (const [name, buffer] of files) {
        // Binaries (fonts, images) cannot carry a URL that the browser would
        // follow; scanning text is what matters, and keeps the test fast.
        if (!['.html', '.css', '.js', '.json', '.map', '.svg', '.txt'].includes(extname(name))) continue;
        const text = buffer.toString('utf8');
        for (const needle of FORBIDDEN) {
            if (text.includes(needle)) offenders.push(`${name} -> ${needle}`);
        }
    }
    assert.deepEqual(offenders, [], `third-party font references in the bundle:\n${offenders.join('\n')}`);
});

test('the build really bundles the self-hosted font files', () => {
    ensureBuild();
    const fonts = distFiles().filter(([name]) => /\.woff2?$/.test(name));
    assert.ok(fonts.length > 0, 'no .woff/.woff2 in dist — the fonts are not self-hosted');

    const names = fonts.map(([name]) => name).join(' ');
    assert.match(names, /space-grotesk/, 'Space Grotesk is missing from the bundle');
    assert.match(names, /inter-/, 'Inter is missing from the bundle');
});

test('neither entry document has a Google Fonts link or preconnect', () => {
    ensureBuild();
    // The site homepage AND the application shell: the two documents a visitor
    // can arrive at directly.
    for (const entry of [join(DIST, 'index.html'), join(APP_DIST, 'index.html')]) {
        const html = readFileSync(entry, 'utf8');
        assert.doesNotMatch(html, /fonts\.googleapis\.com|fonts\.gstatic\.com/, entry);
        assert.doesNotMatch(html, /<link[^>]+preconnect[^>]+google/i, entry);
    }
});

test('the public site ships the self-hosted faces it now links', () => {
    ensureBuild();
    // The pages link /fonts/site.css. If the stylesheet or its files went
    // missing the pages would fall back to a system typeface in silence — the
    // exact failure this whole change removed.
    const css = readFileSync(join(DIST, 'fonts', 'site.css'), 'utf8');
    assert.match(css, /@font-face/, 'fonts/site.css carries no @font-face rule');
    for (const family of ['Space Grotesk', 'Inter']) {
        assert.ok(css.includes(`font-family: '${family}'`), `${family} is missing from fonts/site.css`);
    }
    // Every file the stylesheet points at must actually be there.
    const referenced = [...css.matchAll(/url\(\.\/([^)]+)\)/g)].map(m => m[1]);
    assert.ok(referenced.length > 0, 'fonts/site.css references no font file');
    const shipped = new Set(readdirSync(join(DIST, 'fonts')));
    const missing = referenced.filter(name => !shipped.has(name));
    assert.deepEqual(missing, [], `fonts/site.css points at files that were not copied:\n${missing.join('\n')}`);
});

test('no page of the public site carries an inline script', () => {
    ensureBuild();
    // script-src is 'self' on both zones, so an inline block would simply never
    // run — silently. assemble-site.mjs externalises them into dist/scripts/.
    // <script type="application/ld+json"> is structured data, never executed,
    // and deliberately not matched here.
    const offenders = distFiles()
        .filter(([name]) => name.endsWith('.html') && !name.startsWith('app/'))
        .filter(([, buffer]) => buffer.toString('utf8').includes('<script>'))
        .map(([name]) => name);
    assert.deepEqual(offenders, [], `inline <script> survived into the build:\n${offenders.join('\n')}`);
});

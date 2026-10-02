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
import { join, dirname, extname, posix } from 'node:path';
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
    // Read off the pages, not hard-coded: the v4/v5 pages linked /fonts/site.css
    // (built by assemble-site.mjs from @fontsource), the 2026-09-30 site links
    // assets/css/site.css, which carries its own faces. Whatever a page links,
    // the stylesheet must be in the build and so must every font file it points
    // at — otherwise the pages fall back to a system typeface in silence, the
    // exact failure self-hosting removed.
    const shipped = new Map(distFiles());
    const isRemote = ref => /^[a-z][a-z0-9+.-]*:|^\/\//i.test(ref);
    const resolve = (from, ref) => {
        const path = ref.split(/[?#]/)[0];
        return posix.normalize(path.startsWith('/') ? path.slice(1) : posix.join(posix.dirname(from), path));
    };
    const problems = [];
    const sheets = new Set();
    for (const [page, buffer] of shipped) {
        if (!page.endsWith('.html') || page.startsWith('app/')) continue;
        for (const [tag] of buffer.toString('utf8').matchAll(/<link\b[^>]*>/g)) {
            if (!/\brel="stylesheet"/.test(tag)) continue;
            const href = (tag.match(/\bhref="([^"]+)"/) || [])[1] || '';
            if (!href || isRemote(href)) { problems.push(`${page}: stylesheet not served from this origin: ${href}`); continue; }
            const sheet = resolve(page, href);
            if (shipped.has(sheet)) sheets.add(sheet);
            else problems.push(`${page}: links ${href}, which is not in the build`);
        }
    }
    assert.ok(sheets.size > 0, 'no page of the site links a stylesheet');

    let faces = 0;
    for (const sheet of sheets) {
        const css = shipped.get(sheet).toString('utf8');
        faces += (css.match(/@font-face/g) || []).length;
        for (const [, ref] of css.matchAll(/url\(\s*["']?([^"')]+)["']?\s*\)/g)) {
            if (!/\.(woff2?|ttf|otf)(?:[?#].*)?$/i.test(ref)) continue;   // images, data: URIs
            if (isRemote(ref)) problems.push(`${sheet}: font not served from this origin: ${ref}`);
            else if (!shipped.has(resolve(sheet, ref))) problems.push(`${sheet}: points at ${ref}, which is not in the build`);
        }
    }
    assert.ok(faces > 0, `the stylesheets the site links carry no @font-face rule: ${[...sheets].join(', ')}`);
    assert.deepEqual(problems, [], problems.join('\n'));
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

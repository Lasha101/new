// Assembles the public site (frontend/site/) into the build output, in front of
// the application.
//
// WHAT SHIPS, AND WHERE
// ---------------------
// Since the site became the front door of scanid.fr the built tree has two
// halves, and this script is what puts the first one there:
//
//     dist/index.html          <- site/index.html          scanid.fr/
//     dist/presentation.html   <- site/presentation.html   scanid.fr/presentation.html
//     dist/faq.html, guide.html, cgv.html, ... every page of the site
//     dist/iftm/index.html     <- site/iftm/index.html     scanid.fr/iftm/
//     dist/fonts/              <- self-hosted Space Grotesk + Inter  (see below)
//     dist/scripts/            <- the pages' inline <script> blocks, externalised
//     dist/sw.js               <- scripts/legacy-sw-unregister.js  (see below)
//
//     dist/app/                <- vite build (base '/app/')  scanid.fr/app/
//
// `vite build` writes dist/app/ and nothing else (build.outDir in
// vite.config.js); this script owns everything at the root of dist/. The two
// never overlap, which is what lets `npm run build` produce both halves without
// either one clobbering the other.
//
// frontend/site/ IS READ-ONLY.
// Nothing here opens a file under site/ for writing. Every transformation below
// happens on the COPY, in memory, on its way to dist/ — the source pages keep
// the markup their author wrote.
//
// WHY THE TRANSFORMATIONS ARE NOT COSMETIC
// ----------------------------------------
// The pages were authored for shared Apache hosting with no Content-Security-
// Policy. This server sends one. Two of the transformations below exist so the
// pages are correct under a policy of `script-src 'self'` and `font-src 'self'`
// — which means they render correctly EVEN IF nginx is still running an older
// configuration, and it lets the site policy in ops/nginx-site-csp.conf drop
// both `'unsafe-inline'` and the two Google origins entirely.

import { readdirSync, readFileSync, writeFileSync, mkdirSync, copyFileSync, rmSync, existsSync, statSync } from 'node:fs';
import { join, dirname, extname, relative, basename } from 'node:path';
import { fileURLToPath } from 'node:url';

const FRONTEND = dirname(dirname(fileURLToPath(import.meta.url)));
// The site's source of truth. Since v5 it is scanid-site-v5-deploy/, which
// replaces the content of site/; site/ (v4) stays in the repository untouched
// and read-only, and nothing reads it any more. This constant is the only place
// the source directory is named — the rest of this file says "site/" for
// whichever directory it points at.
const SITE = join(FRONTEND, 'scanid-site-v5-deploy');
const DIST = join(FRONTEND, 'dist');
const MODULES = join(FRONTEND, 'node_modules', '@fontsource');

/** The one directory under dist/ that belongs to `vite build`, not to us. */
const APP_DIR = 'app';

/** Where the self-hosted faces and the externalised scripts land, under dist/. */
const FONT_DIR = 'fonts';
const FONT_STYLESHEET = `${FONT_DIR}/site.css`;
const SCRIPT_DIR = 'scripts';

/**
 * Files that must NOT be published, whatever the site directory contains.
 *
 * `.htaccess` configures Apache and means nothing to nginx, but nginx serves
 * dotfiles happily — copying it would publish the site's server configuration
 * at https://scanid.fr/.htaccess for anyone who asks. It is deliberately left
 * behind rather than copied and then forgotten about.
 */
const NEVER_COPY = new Set(['.htaccess', '.DS_Store', 'Thumbs.db']);

/**
 * The faces the pages ask Google for, resolved to the local @fontsource
 * packages instead.
 *
 * Read straight off the pages: 22 of them link
 * `css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:...`, and five
 * of those also ask for `ital,wght@...;1,400`. So: Space Grotesk 400/500/600/700
 * and Inter 400/500 plus Inter 400 italic. Nothing else is requested, so nothing
 * else is shipped.
 */
const FONT_PACKAGES = [
    { pkg: 'space-grotesk', weights: ['400', '500', '600', '700'] },
    { pkg: 'inter', weights: ['400', '500', '400-italic'] },
];

/**
 * The subsets to keep — and this is a like-for-like swap, not a downgrade.
 *
 * Google's css2 endpoint serves exactly these two for a page in French, and the
 * @fontsource unicode-ranges are the same ranges: `latin` covers U+0000-00FF
 * (every accent the pages use), U+0152-0153 (Œ œ), U+20AC (€) and general
 * punctuation; `latin-ext` covers the rest. The other subsets @fontsource ships
 * — cyrillic, greek, vietnamese — are not served to these pages by Google
 * either, so shipping them would add weight for no glyph.
 *
 * The unicode-range on each @font-face is what makes this safe to concatenate:
 * without it, two faces declaring the same family/weight/style would collide
 * and the browser would download only the last one, losing the other subset's
 * glyphs silently.
 */
const FONT_SUBSETS = ['latin-ext', 'latin'];   // longest first — see subsetOf()

/**
 * Rewrites applied to the COPY of every .html page.
 *
 * Each one is here because the page is wrong without it on THIS server. None of
 * them changes what the page says.
 */
const HTML_REWRITES = [
    {
        // The site was authored for a deployment where the application lived on
        // its own subdomain, so its « Connexion » links (40 of them, header and
        // footer of 20 pages) point at https://app.scanid.fr. That name has no
        // DNS record; the application is served from this same origin, under
        // /app/. A same-origin relative URL is used rather than
        // https://scanid.fr/app/ so the assembled tree also works when served
        // from somewhere else — a preview, a staging host.
        from: /https:\/\/app\.scanid\.fr(?![\w.-])/g,
        to: '/app/',
        why: '« Connexion » → the application at /app/',
    },
    {
        // The Google Fonts stylesheet, replaced by the self-hosted bundle built
        // below. `style-src` on this server does not allow fonts.googleapis.com,
        // so left alone every page falls back to a system typeface — silently,
        // because a blocked stylesheet is not a visible error.
        from: /<link href="https:\/\/fonts\.googleapis\.com\/css2\?[^"]*" rel="stylesheet">/g,
        to: `<link href="/${FONT_STYLESHEET}" rel="stylesheet">`,
        why: 'Google Fonts stylesheet → the self-hosted bundle',
    },
    {
        // The preconnects that went with it. Harmless if left, but they would
        // open a connection to a host nothing then uses, and they are the last
        // thing naming Google in the output.
        from: /[ \t]*<link rel="preconnect" href="https:\/\/fonts\.(?:googleapis|gstatic)\.com"[^>]*>\n?/g,
        to: '',
        why: 'Google Fonts preconnect hints removed',
    },
];

/**
 * What must NOT survive the rewrite, and why each one is fatal rather than a
 * warning.
 *
 * If a future revision of the site introduces something this script does not
 * know how to handle, the build stops and says so — rather than shipping 22
 * pages with a dead « Connexion » button, a system typeface, or a calculator
 * that silently does nothing.
 */
const FORBIDDEN_AFTER_REWRITE = [
    { pattern: /app\.scanid\.fr/, why: 'a link shape HTML_REWRITES does not handle — the « Connexion » button would be dead' },
    { pattern: /fonts\.(googleapis|gstatic)\.com/, why: 'a Google Fonts reference the rewrite missed — the page would render in a system typeface' },
    { pattern: /<script>/, why: 'an inline <script> the extractor missed — script-src forbids it, so the code would never run' },
];

/** Text formats the rewrites are applied to. Everything else is copied byte for byte. */
const REWRITABLE = new Set(['.html']);

// ---------------------------------------------------------------------------

/** Every file under `dir`, as paths relative to it. */
function walk(dir, prefix = '') {
    const out = [];
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
        const rel = prefix ? `${prefix}/${entry.name}` : entry.name;
        if (entry.isDirectory()) out.push(...walk(join(dir, entry.name), rel));
        else out.push(rel);
    }
    return out;
}

/**
 * Empties dist/ of everything except the application directory.
 *
 * Without this, a file that used to be produced at the root of dist/ survives
 * for as long as nobody deletes it by hand — and the ones that used to be there
 * are the PREVIOUS build of the application (index.html, assets/, sw.js,
 * manifest.webmanifest). A stale dist/index.html would be served at scanid.fr/
 * ahead of the site, which is exactly the bug this whole change is about.
 * `rsync --delete` in the deploy would then faithfully mirror the mistake.
 */
function clearSiteHalf() {
    if (!existsSync(DIST)) return [];
    const removed = [];
    for (const entry of readdirSync(DIST, { withFileTypes: true })) {
        if (entry.name === APP_DIR) continue;
        rmSync(join(DIST, entry.name), { recursive: true, force: true });
        removed.push(entry.name);
    }
    return removed;
}

/** 'space-grotesk-latin-ext-400-normal.woff2' → 'latin-ext'. Longest match wins. */
const subsetOf = (file) => FONT_SUBSETS.find(s => file.includes(`-${s}-`)) || null;

/**
 * Builds dist/fonts/ — the @font-face rules and the files they point at.
 *
 * Reads the per-weight stylesheets @fontsource ships (which carry the
 * unicode-range each face needs), keeps the latin and latin-ext blocks, copies
 * the woff2/woff they reference, and rewrites `url(./files/x)` to `url(./x)`
 * so the stylesheet works from its own directory.
 */
function buildFontBundle() {
    const outDir = join(DIST, FONT_DIR);
    mkdirSync(outDir, { recursive: true });

    const blocks = [];
    let files = 0;
    let bytes = 0;

    for (const { pkg, weights } of FONT_PACKAGES) {
        for (const weight of weights) {
            const source = join(MODULES, pkg, `${weight}.css`);
            if (!existsSync(source)) {
                console.error(`assemble-site: ${relative(FRONTEND, source)} is missing — run \`npm ci\` (the site's fonts come from @fontsource, not from Google).`);
                process.exit(1);
            }
            const css = readFileSync(source, 'utf8');
            for (const block of css.match(/@font-face\s*\{[^}]*\}/g) || []) {
                const referenced = [...block.matchAll(/url\(\.\/files\/([^)]+)\)/g)].map(m => m[1]);
                if (!referenced.length || !subsetOf(referenced[0])) continue;   // a subset we do not ship
                for (const name of referenced) {
                    const from = join(MODULES, pkg, 'files', name);
                    if (!existsSync(from)) continue;
                    copyFileSync(from, join(outDir, name));
                    bytes += statSync(from).size;
                    files += 1;
                }
                blocks.push(block.replace(/url\(\.\/files\//g, 'url(./'));
            }
        }
    }

    if (!blocks.length) {
        console.error('assemble-site: no @font-face rule was produced — the site would render in a system typeface.');
        process.exit(1);
    }

    writeFileSync(join(DIST, FONT_STYLESHEET),
        '/* ScanID — the public site\'s typefaces, self-hosted.\n' +
        ' *\n' +
        ' * GENERATED by frontend/scripts/assemble-site.mjs from @fontsource. Do not\n' +
        ' * edit: the next build overwrites it.\n' +
        ' *\n' +
        ' * The pages ask Google for these faces. They are served from this origin\n' +
        ' * instead, for two reasons. The policy this server sends is font-src \'self\',\n' +
        ' * so the Google copies are blocked and the pages would quietly fall back to a\n' +
        ' * system typeface. And a French site selling RGPD compliance should not be\n' +
        ' * hotlinking a US font CDN on every page load — that is a transfer of\n' +
        ' * personal data, and it is the application\'s own reason for self-hosting.\n' +
        ' */\n\n' + blocks.join('\n\n') + '\n');

    return { faces: blocks.length, files, bytes };
}

/**
 * Moves a page's inline <script> blocks into files of their own.
 *
 * `script-src 'self'` forbids inline script. The two pages that carry one — the
 * pricing calculator and the checklist's form handler — are simply dead under
 * that policy: no error the visitor can see, the calculator just never
 * recomputes. An external file from the same origin is allowed, runs at exactly
 * the same point in the parse, and needs no CSP concession at all.
 *
 * `<script>` with no attributes is matched deliberately: the 26
 * `<script type="application/ld+json">` blocks on the site are structured data,
 * are never executed, and are not what the policy is about.
 */
function externaliseInlineScripts(html, relPath) {
    const emitted = [];
    const stem = relPath.replace(/\.html$/, '').replace(/[/\\]/g, '-');
    const out = html.replace(/<script>([\s\S]*?)<\/script>/g, (_, code) => {
        const name = `${stem}-${emitted.length + 1}.js`;
        emitted.push({ name, code: code.replace(/^\n/, '') });
        return `<script src="/${SCRIPT_DIR}/${name}"></script>`;
    });
    return { html: out, emitted };
}

// ---------------------------------------------------------------------------

if (!existsSync(SITE) || !statSync(SITE).isDirectory()) {
    console.error(`assemble-site: ${relative(FRONTEND, SITE)} does not exist — nothing to put in front of the app.`);
    process.exit(1);
}

// The application half has to be there already: this script runs after
// `vite build`, and a dist/ holding only the site would deploy a front door
// with no door behind it — every « Connexion » link a 404.
const appEntry = join(DIST, APP_DIR, 'index.html');
if (!existsSync(appEntry)) {
    console.error(`assemble-site: ${relative(FRONTEND, appEntry)} is missing — run \`vite build\` first (npm run build does both).`);
    process.exit(1);
}

const removed = clearSiteHalf();
const fonts = buildFontBundle();
mkdirSync(join(DIST, SCRIPT_DIR), { recursive: true });

let copied = 0;
let rewritten = 0;
let scriptsExtracted = 0;
const rewriteCounts = new Map(HTML_REWRITES.map(r => [r.why, 0]));

for (const rel of walk(SITE)) {
    const name = rel.split('/').pop();
    if (NEVER_COPY.has(name)) continue;

    const source = join(SITE, rel);
    const target = join(DIST, rel);
    mkdirSync(dirname(target), { recursive: true });

    if (!REWRITABLE.has(extname(rel))) {
        copyFileSync(source, target);
        copied += 1;
        continue;
    }

    let html = readFileSync(source, 'utf8');
    let touched = false;
    for (const rule of HTML_REWRITES) {
        const hits = html.match(rule.from);
        if (!hits) continue;
        html = html.replace(rule.from, rule.to);
        rewriteCounts.set(rule.why, rewriteCounts.get(rule.why) + hits.length);
        touched = true;
    }

    const { html: withoutInline, emitted } = externaliseInlineScripts(html, rel);
    html = withoutInline;
    for (const script of emitted) {
        writeFileSync(join(DIST, SCRIPT_DIR, script.name), script.code);
        scriptsExtracted += 1;
        copied += 1;
        touched = true;
    }

    for (const { pattern, why } of FORBIDDEN_AFTER_REWRITE) {
        if (!pattern.test(html)) continue;
        console.error(`assemble-site: ${rel} still matches ${pattern} after rewriting.`);
        console.error(`  ${why}.`);
        console.error('  Teach this script the new shape rather than shipping the page broken.');
        process.exit(1);
    }

    writeFileSync(target, html);
    copied += 1;
    if (touched) rewritten += 1;
}

// The application's own service worker now lives at /app/sw.js, scoped to
// /app/. The one that used to live here, at the root, is still registered in
// the browser of everyone who has opened the app — with a navigation fallback
// that answers scanid.fr/ out of its cache. Left alone it would keep serving
// the old application shell at the address the site is supposed to occupy.
// Shipping a self-unregistering worker at the same URL is what retires it.
const legacyWorker = join(FRONTEND, 'scripts', 'legacy-sw-unregister.js');
copyFileSync(legacyWorker, join(DIST, 'sw.js'));
copied += 1;

const rewriteSummary = [...rewriteCounts]
    .map(([why, n]) => `      ${n} × ${why}`)
    .join('\n');

console.log(
    `assemble-site: ${copied} files into dist/ (${rewritten} pages rewritten)\n` +
    `${rewriteSummary}\n` +
    `      ${scriptsExtracted} × inline <script> → /${SCRIPT_DIR}/ (script-src 'self')\n` +
    `      ${fonts.faces} @font-face, ${fonts.files} files, ${(fonts.bytes / 1024).toFixed(0)} KB → /${FONT_DIR}/ (font-src 'self')\n` +
    `      site  → dist/            (${removed.length} stale root entries cleared)\n` +
    `      app   → dist/${APP_DIR}/  (left untouched)`
);

# SCANID — HANDOVER

Resume file for the "public site becomes the front door" task.
If you are a new session: **read this file top to bottom, then continue at the first
stage whose status is not `DONE`.**

Last updated: 2026-09-12

---

## 1. WHAT WAS DEMANDED

Verbatim constraints given by the user, restated so a fresh session can honour them:

1. **All current functionality must be preserved.** Only what is explicitly demanded
   may change.
2. **`frontend/site/` is READ-ONLY.** It may not be edited, deleted or moved. It is
   the **source of truth**.
3. **`frontend/dist/` is the target.** Its contents may be deleted and rewritten, but
   only to bring it in line with `frontend/site/`.
4. Outside the repository root: reading and running commands is allowed; **editing,
   deleting or installing anything outside the root requires the user's permission.**
5. **The pages in `frontend/site/` must be what a visitor sees FIRST** when they open
   `https://scanid.fr` — they are the head / front part of the app, assembled **in
   logical order**, with the application behind them.
6. **Make only necessary changes.**
7. **Do not `git add`, `git commit` or `git push` anything.**
8. Work in staged order, and **update this file after every stage** so the work can be
   resumed after an interruption.

### What actually changed on disk before this task started

`frontend/site/` was replaced with the **v4** revision of the marketing site (the
directory that arrived as `frontend/scanid-site-v4-deploy/` was renamed over `site/`).
`git status` therefore shows all 21 HTML pages as modified; the binary assets are
byte-identical. `frontend/dist/` still holds the **previous** revision, built on
2026-09-09. The job is to bring `dist/` up to the new `site/`.

---

## 2. WHAT THE REPOSITORY ALREADY PROVIDES

This is **not** a from-scratch job. The front-door pipeline already exists and works:

| Piece | Role |
| --- | --- |
| `frontend/site/` | Source of truth — 22 HTML pages + assets. Read-only. |
| `frontend/scripts/assemble-site.mjs` | Copies `site/` → root of `dist/`, applying CSP-driven rewrites. Never writes into `site/`. |
| `frontend/vite.config.js` | Builds the React app into `dist/app/` and nothing else. |
| `npm run build` | `vite build` **then** `assemble-site.mjs` — produces both halves. |
| `deploy/nginx-travelapp.conf` | Serves `/` from the site half, `/app/` from the app half, `/api/` to the backend on `:8001`. |
| `ops/nginx-site-csp.conf` | The site's own CSP. `script-src 'self'`, `font-src 'self'`, plus `https://formspree.io`. |
| `frontend/tests/build/no-google-fonts.test.js` | Asserts the built tree carries no Google font reference and no inline `<script>`. |
| `ops/verify-front-end.sh` | Read-only post-deploy probe against the live host. |

**Consequence:** the correct implementation is to run the existing assembler, not to
hand-copy pages. Hand-copying would drop the rewrites and ship 22 pages with a system
typeface and two dead forms.

### The two halves must not collide

`vite build` owns `dist/app/` only. `assemble-site.mjs` owns everything at the root of
`dist/` and deliberately skips `dist/app/` when it clears stale files. Running the
assembler **alone** therefore rebuilds the site half and leaves the application
untouched — which is the minimal change this task needs, since only `site/` changed.

---

## 3. THE LOGICAL ORDER TO IMPLEMENT

Derived from the pages' own navigation, the footer, the `ressources.html` hub and
`sitemap.xml` — not invented. This is the order the front door is assembled in.

**Tier 0 — entry point**
- `index.html` → served at `/` — the first page a visitor sees.

**Tier 1 — primary navigation** (identical on all 20 pages that carry a nav, in this order)
1. `presentation.html` — Présentation
2. `ressources.html` — Ressources
3. `index.html#tarifs` — Tarifs (anchor on the home page; confirmed present)
4. `faq.html` — FAQ
5. `index.html#contact` — Contact (anchor confirmed present)
6. `/app/` — **Connexion → the application**
7. `essai.html` — Essai gratuit (the nav call-to-action)

**Tier 2 — resources hub children** (linked from `ressources.html`)
- `guide.html`, `guide-photo.html`, `calculateur.html`, `alternatives.html`,
  `temoignages.html`, `checklist.html`
- Articles: `rgpd-fuite-donnees.html`, `rgpd-conserver-copies-passeport.html`,
  `transfert-donnees-securise.html`, `erreurs-saisie-passeport.html`,
  `apis-agences-voyages.html`

**Tier 3 — trust & legal** (footer order)
- `securite.html`, `politique-confidentialite.html`, `mentions-legales.html`, `cgv.html`

**Tier 4 — standalone**
- `iftm/index.html` → `/iftm/` — campaign landing page, no nav by design
- `404.html` — error document, no nav by design

**Non-page assets:** `favicon.ico`, `favicon.svg`, `apple-touch-icon.png`,
`og-image.png`, `robots.txt`, `sitemap.xml`, `ScanID-Checklist-RGPD.pdf`,
`scanid-presentation.mp4`.
**Deliberately never published:** `.htaccess` (Apache config; nginx would serve it).

---

## 4. STAGES

| # | Stage | Status |
| --- | --- | --- |
| 0 | Survey the repository and fix the order | **DONE** |
| 1 | Write the demand + plan into this file | **DONE** |
| 2 | Pre-flight: check new `site/` against the assembler's contract | **DONE** |
| 3 | Assemble `site/` → `dist/` (site half only; app half untouched) | **DONE** |
| 4 | Verify the built front door | **DONE** |
| 5 | Report residual gaps; hand back | **DONE** |

**The task is complete.** `dist/` now serves the v4 site at `/` and the unchanged
application at `/app/`. What remains is listed in §5 — none of it was demanded, and
none of it was done.

---

### Stage 0 — Survey — **DONE**

Findings that drive everything below:

- `site/` holds **22 HTML pages** (21 at the root incl. `404.html`, plus `iftm/index.html`)
  and 8 non-HTML assets.
- The v4 pages **already point at `/app/`** — `app.scanid.fr` no longer appears anywhere.
  The assembler's first rewrite rule is now a harmless no-op (0 hits, not an error).
- All 22 pages still link Google Fonts (1 stylesheet + 2 preconnects each). The
  assembler's regexes were tested against every page: **22/22 match, 0 leftovers.**
- Inline `<script>` blocks: `calculateur.html`, `checklist.html`, and — **new in v4** —
  `essai.html`. The assembler externalises all three automatically.
- New in v4: four `https://buy.stripe.com/...` **links** in the pricing section of
  `index.html`. These are ordinary navigations, which CSP does not restrict, so **no CSP
  change is needed.** (The v4 source also fixed a doubled `https://buy.stripe.com/https://buy.stripe.com/` URL.)
- New in v4: a centred `.nav-inner` wrapper + `<style id="sid-center">` on every page, a
  redrawn logo SVG, `max(6%,calc((100% - 1200px)/2))` gutters, and revised pricing copy
  (HT pricing, "Passeports et CNI françaises").
- Internal link audit across all 22 pages: **no broken `href`/`src`.** The only
  unresolved target is `/` in `404.html`, which is the site root and correct.

### Stage 1 — Demand + plan recorded — **DONE**

This file.

### Stage 2 — Pre-flight — **DONE**

Every rewrite and every refusal check in `assemble-site.mjs` was replayed against the
new `site/` **in memory, writing nothing**, to prove the assembler would not stop
half-way and leave `dist/` in a mixed state.

Result: **PRE-FLIGHT PASSED — 22/22 pages ok, 0 failures.**

```
22 pages, 8 assets copied byte-for-byte, 3 scripts externalised
  0 × Connexion → /app/          (v4 already uses /app/ — rule is a no-op, not a fault)
 22 × Google Fonts → self-hosted
 44 × preconnect removed
 14 @font-face rules available from @fontsource
```

- `.htaccess` correctly skipped (`NEVER_COPY`).
- The three inline scripts become `/scripts/calculateur-1.js`, `/scripts/checklist-1.js`
  and — new in v4 — `/scripts/essai-1.js`.
- No page trips `FORBIDDEN_AFTER_REWRITE`.

The dry-run script lives in the session scratchpad, not in the repository — it proves a
property of the build, it is not part of it. `tests/build/no-google-fonts.test.js` is the
permanent guard and is run in Stage 4.

### Stage 3 — Assembled — **DONE**

Command run, from `frontend/`:

```
node scripts/assemble-site.mjs
```

`vite build` was **deliberately not run.** Only `site/` changed; the application source
did not. The assembler skips `dist/app/`, so this rebuilds the front door alone and
leaves the application bit-for-bit as it was. Running a full `npm run build` would have
rewritten 91 application files and re-hashed its assets for no reason — the opposite of
"make only necessary changes".

Output:

```
assemble-site: 34 files into dist/ (22 pages rewritten)
      0 × « Connexion » → the application at /app/
     22 × Google Fonts stylesheet → the self-hosted bundle
     44 × Google Fonts preconnect hints removed
      3 × inline <script> → /scripts/ (script-src 'self')
     14 @font-face, 28 files, 644 KB → /fonts/ (font-src 'self')
      site  → dist/            (33 stale root entries cleared)
      app   → dist/app/  (left untouched)
```

The 33 cleared entries are the previous (2026-09-09) revision of the site half. Clearing
them is what stops a page deleted from `site/` surviving in `dist/` and being mirrored
onto the server by `rsync --delete`.

### Stage 4 — Verified — **DONE**

Every check below passed.

**The application is preserved.** SHA-256 over all 91 files of `dist/app/`, before and
after: `1ef1661c60e2431b…` → identical.

**The front door is complete and correct.**

| Check | Result |
| --- | --- |
| Pages in `dist/` vs `site/` | identical set, 22 pages, no extras, no omissions |
| `.htaccess` published? | no — withheld, and `GET /.htaccess` is 404 |
| Inline scripts externalised | `scripts/calculateur-1.js`, `checklist-1.js`, `essai-1.js` |
| `app.scanid.fr` / Google font references left in the site half | none |
| « Connexion » links pointing at `/app/` | 40 (header + footer of the 20 pages with a nav) |
| Pages linking `/fonts/site.css` | 22 / 22 |
| Broken `href`/`src` in the built tree | none |

**Permanent build guards** — `node --test tests/build/no-google-fonts.test.js`:
5 tests, **5 pass, 0 fail** (no Google reference anywhere in `dist/`; self-hosted faces
really bundled; neither entry document links Google; `fonts/site.css` and every file it
points at present; no inline `<script>` in any site page).

**HTTP smoke test** — `dist/` served over a throwaway local server:
all 22 pages `200`; `/` returns the site homepage
(`<title>Scanner de passeports et CNI pour agences de voyages | ScanID</title>`, **not**
the application); `/app/` returns the application; `/iftm/`, `/robots.txt`,
`/sitemap.xml`, `/404.html`, the three extracted scripts and all 28 font files `200`;
`/.htaccess` `404`. Server stopped afterwards.

**Repository state:** nothing was added, committed or pushed. `frontend/site/` is
untouched by this work — `git diff --stat -- frontend/site` still reports exactly the
21 files / 399 insertions / 169 deletions that the v4 drop itself introduced. `dist/` is
gitignored, so it does not appear in `git status` at all.

---

## 5. RESIDUAL GAPS — NOT IMPLEMENTED, BY DESIGN

Found while surveying. None of these was demanded, so **none was acted on.** They are
recorded here so the next session does not have to rediscover them.

1. **`/api/trial-requests` does not exist in the backend.** The v4 `essai.html` carries a
   new inline script that POSTs the trial form to `/api/trial-requests`; nginx maps
   `/api/` to the backend on `:8001`, but no such route exists in `backend/`. The script
   degrades gracefully — a non-OK response is caught and the form falls back to a native
   Formspree submit — so **the form still works today**, it just never reaches the
   backend. Ask the user before adding the endpoint.

2. **The four Stripe checkout links are new** (`buy.stripe.com`, in the pricing section
   of `index.html`). They are ordinary link navigations, which CSP does not restrict, so
   `ops/nginx-site-csp.conf` needs **no change**. Worth a note only because the v4 source
   also corrected a doubled `https://buy.stripe.com/https://buy.stripe.com/` URL that
   would have been a dead button.

3. **Deploying this needs an nginx reload to be fully correct.** Unchanged from before,
   but it applies to this build too: after the files are rsynced, run
   `sudo nginx -t && sudo systemctl reload nginx`, then
   `bash /opt/travelapp/ops/verify-front-end.sh` on the VPS. Until the reload, unknown
   paths answer 200 with the homepage instead of 404, and the Formspree lead forms are
   refused. Fonts and scripts are correct under any policy allowing `'self'`, so those
   are not at risk.

4. **Nothing has been deployed.** This work stops at a correct `frontend/dist/` on this
   machine.

---

## 7. HOW THIS REACHES THE LIVE SITE — READ BEFORE PUSHING

**`frontend/dist/` is NOT what gets deployed.** It is gitignored
(`frontend/.gitignore:11`), so it is never pushed — and even if it were, the deploy
would ignore it.

`.github/workflows/deploy.yml` triggers on **push to `master`** (the trigger is active,
despite the "DISABLED" comment at the top of the file) and does this:

```
npm ci && npm run build          # on the GitHub runner, from the CHECKED-OUT source
rsync -az --delete frontend/dist/  →  /opt/travelapp/frontend-dist/
```

So the runner **rebuilds `dist/` from `frontend/site/`** and ships its own copy. The
`dist/` on this machine is a local verification — proof that the build is correct and
what it will look like — and plays no part in the deploy.

### Therefore: what must be committed is `frontend/site/`, not `dist/`

At the time of writing, the 21 modified v4 pages under `frontend/site/` are **still
uncommitted**. Pushing without committing them makes the runner check out the OLD site,
rebuild the OLD front door, and **visitors see no change at all.**

```
git add frontend/site
git commit -m "..."
git push
```

(Not run here — the user's instructions forbid add/commit/push.)

### Also uncommitted, and worth deciding on

- `ops/verify-front-end.sh` — untracked. `ops/` is rsynced with `--delete`, so until it
  is committed it will not exist on the server.
- `frontend/tests/build/` — untracked, so CI's `npm test` does not run the five build
  guards. The build is still protected: `assemble-site.mjs` refuses to finish on any of
  the same faults.
- Both nginx include targets (`ops/nginx-security-headers.conf`, `ops/nginx-site-csp.conf`)
  **are** committed — the deploy hard-fails without them, so this was checked.

### What the deploy will report

Its own front-end probes assert content, and the new build satisfies them
(`href="/app/"` is present on the homepage, `/fonts/site.css` is served). If nginx has
not been reloaded on the VPS, the 404 probe reports `PENDING` rather than failing, and
the run prints an "ACTION REQUIRED" block: `sudo nginx -t && sudo systemctl reload nginx`.

---

## 6. RULES FOR WHOEVER CONTINUES

- Never write into `frontend/site/`. Every transformation happens on the copy, in
  memory, on the way to `dist/`.
- Do not run a bare `vite build` unless the application source actually changed; it is
  not needed here and would churn the app half for nothing.
- Do not `git add` / `commit` / `push`.
- If the assembler exits non-zero, it is refusing to ship a broken page. Teach it the
  new markup shape — do not weaken its checks and do not edit `site/`.

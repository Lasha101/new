# HANDOVER — the public site as the front of scanid.fr

**Purpose of this file.** A new session should be able to read *only this file*
and carry on. It records what was asked, what has been done and verified, what
is left, and the decisions that are already settled so they are not re-litigated.

**Status:** LIVE AND VERIFIED IN PRODUCTION (2026-09-09). Implementation complete. Two optional items are
awaiting a yes/no from the user (§10); one action is required from the user
before the next push (§8).
**Last updated:** 2026-09-09, after removing the dependency on an nginx reload
(stage 10) — the fonts and the page scripts are now self-hosted.
**Branch:** `master`. **Nothing has been added, committed or pushed** — that is
an explicit standing instruction from the user.

---

## 1. What the user asked for

Verbatim constraints, all still binding:

- **All current functionality must be preserved** except what is explicitly asked for.
- **`frontend/site/` is READ-ONLY.** It may be read and copied. It must never be
  edited or deleted. *(Nothing in this work writes to it — the link rewrite
  happens on the copy, on its way into `dist/`.)*
- Outside the repository root, commands may be **run and read**, but anything that
  **edits, deletes or installs** needs the user's permission first.
- The pages in `frontend/site/` **must be what a visitor sees first** at
  https://scanid.fr — the "head"/front part in front of the existing app.
- The pages must be assembled **in their logical order**, derived by parsing the
  whole directory first.
- **Make only necessary changes.**
- **Do not add, commit or push anything.**

## 2. Decisions the user has already made (do not re-ask)

| Question | Decision |
|---|---|
| Where the React app lives | **`scanid.fr/app/`**. The site's 40 hardcoded `https://app.scanid.fr` « Connexion » links are rewritten to `/app/` **in the build copy only**; `frontend/site/` is untouched. Chosen because `app.scanid.fr` has **no DNS record** and the subdomain route would need a DNS change plus a certificate expansion by the user. |
| How the site reaches production | **Bundled into `frontend/dist/` at build time**, so the existing `deploy.yml` rsync ships it with no workflow change. |

## 3. The layout this produces

```
frontend/site/            READ-ONLY source, 31 files, 22 HTML pages   (never written)
        │  copied + link-rewritten by scripts/assemble-site.mjs
        ▼
frontend/dist/            → rsynced to /opt/travelapp/frontend-dist/
  ├── index.html          site homepage           scanid.fr/
  ├── presentation.html, faq.html, … 20 more pages, 404.html
  ├── iftm/index.html                             scanid.fr/iftm/
  ├── robots.txt, sitemap.xml, favicons, og-image.png, .mp4, .pdf
  ├── sw.js               ← the self-destructing legacy worker (see §5, hazard C)
  └── app/                `vite build` output, base '/app/'   scanid.fr/app/
      ├── index.html  assets/  icons/  manifest.webmanifest  sw.js
```

`.htaccess` is deliberately **not** copied: it is Apache-only, and nginx serves
dotfiles, so copying it would publish the site's server config at
`https://scanid.fr/.htaccess`.

## 4. The site's logical order (derived by parsing, cross-checked against `sitemap.xml`)

Entry point is unambiguous: **`index.html`** — canonical `https://scanid.fr/`,
in-degree 21/21, the only page carrying Organization + WebSite +
SoftwareApplication JSON-LD, and the root of all 17 BreadcrumbList trails.

- **Tier 0 — entry:** `index.html`
- **Tier 1 — the nav, in its canonical order** (`index.html:182-190`):
  Présentation → Ressources → `#tarifs` → FAQ → `#contact` → **Connexion (`/app/`)** → Essai gratuit (CTA, always last)
- **Tier 2 — footer-only, uniform across 20 pages** (`index.html:409-419`):
  Accueil, Présentation, Ressources, Sécurité, Guide, FAQ │ Connexion, Essai gratuit │ Confidentialité, Mentions légales, CGV
- **Tier 3 — reached from the `ressources.html` hub:** guide-photo, calculateur,
  checklist, alternatives, temoignages, apis-agences-voyages,
  erreurs-saisie-passeport, rgpd-fuite-donnees, rgpd-conserver-copies-passeport,
  transfert-donnees-securise
- **Tier 4 — orphans, no inbound links:** `404.html` (correctly absent from the
  sitemap; the only `noindex` page) and `iftm/index.html` (a campaign landing page)

Serving every page at its own path preserves this order exactly: it is the order
the site's own nav, footer and sitemap already encode. No page was reordered,
renamed or merged.

## 5. Hazards found by the audit, and how each is handled

An audit workflow (75 agents, 5 lenses, adversarial verification) raised 64
hazards; 44 survived refutation. The ones that shaped the implementation:

| # | Hazard | Handling | State |
|---|---|---|---|
| A | Two `index.html` collide in one docroot | `build.outDir: 'dist/app'` + `base: '/app/'` — app and site occupy disjoint subtrees of one `dist`, so the single existing rsync still ships both | done |
| B | SPA catch-all made every typo a soft-404 and `404.html` dead code | `location / { try_files $uri $uri/ =404; }` + `error_page 404 /404.html;`; the SPA fallback moved into `location /app/` and points at `/app/index.html` | done |
| C | **The service worker already registered at scope `/`** keeps answering `scanid.fr/` from the cached React shell, for every returning visitor, indefinitely — and with the site at the root, `GET /sw.js` would answer `200 text/html`, which is a guaranteed no-op that keeps the stale worker **forever** | `scripts/legacy-sw-unregister.js` is copied to `dist/sw.js`: it skips waiting, deletes every cache, unregisters itself and re-navigates its clients. Verified served as `application/javascript`. The new app worker is `/app/sw.js`, scoped to `/app/`, so it can never touch the site | done |
| D | Google Fonts, the two inline `<script>` blocks and the Formspree endpoint are all blocked by the app's CSP | Per-zone CSP via the `$scanid_csp` variable — **not** a second `add_header`, because two CSP headers are enforced as their *intersection* and the looser one would be inert | done |
| E | A per-location CSP would silently strip `nosniff`, `X-Frame-Options` and `Referrer-Policy` (`add_header` in a nested block *replaces*, never merges) | `ops/nginx-site-csp.conf` contains **one `set` directive and no `add_header`**, so all server-level headers keep being sent. Verified: 3/3 other headers and exactly one CSP on every route | done |
| F | `no-google-fonts.test.js` scans all of `dist/` → 88 offenders once the site lands there; CI frontend job goes red | scan scoped to `dist/app`, with the reasoning (and the site's own Google Fonts question) recorded in the file | done |
| G | `pwa.spec.js` reads `dist/sw.js` (ENOENT → 7 tests die) and asserts root-absolute precache keys | reads `dist/app/sw.js`; the precache assertions now derive their prefix from the worker's **registration scope**, so they follow a future base change instead of lying | done |
| H | `tests/helpers/imagePrep.js:90` + `capture.spec.js:220,251` import `/src/upload/imagePrep.js`, which Vite 404s under a base — 11 tests × 3 projects | the specifier is passed into `page.evaluate` from `appSrc()`; verified the dev server serves `/app/src/...` (200) and `/src/...` (404) | done |
| I | `tests/global-setup.js` warm-up paths 404 silently → reintroduces a known flake | `WARMUP_PATHS` built from `APP_BASE`/`appSrc()` | done |
| J | `E2E_BASE_URL=https://scanid.fr` can no longer smoke-test production (`/` is the site now); locally masked by Vite's `/`→`/app/` 302 | new `tests/helpers/appBase.js`; all 22 `page.goto('/')` call sites now `page.goto(APP_BASE)`. `tests/README.md` note still **TODO stage 9** | done |
| K | Deploy health checks probe only `/api` — a wrong root, a missing site or a 404ing `/app/` all deploy green | three content-asserting probes added to `deploy.yml`; all three verified for real against the throwaway nginx | done |
| L | `frontend/site/` is **untracked** (`?? frontend/site/`), so CI checks out a tree without it | **user action required** — see §8 | blocked on user |
| M | `www.scanid.fr` serves the whole site under the non-canonical hostname (the `.htaccess` www→apex redirect is inert on nginx) | **not done, deliberately** — see §10. Not a regression (www already served the app with no redirect), every page carries `<link rel=canonical>` to the apex, and a new 443 server block on a live site is real risk for an SEO nicety | flagged |
| N | `robots.txt` says `Allow: /`, so `/app/` becomes crawlable | noted only — `robots.txt` is site-owned and read-only; the app is a login wall with no crawlable content | won't fix |

## 6. Files changed so far

**New**
- `frontend/scripts/assemble-site.mjs` — copies `site/` → `dist/`, rewrites the 40
  « Connexion » links, clears stale root entries, installs the legacy worker,
  and **fails the build** if a page still names `app.scanid.fr` after rewriting
  or if `dist/app/index.html` is missing.
- `frontend/scripts/legacy-sw-unregister.js` — the tombstone worker (hazard C).
- `ops/nginx-site-csp.conf` — the site's CSP, one `set` directive, heavily commented.

**New (stage 6)**
- `frontend/tests/helpers/appBase.js` — `APP_BASE`, `appPath()`, `appSrc()`, and the
  explanation of why keeping `page.goto('/')` would pass locally and fail
  everywhere else. Overridable with `E2E_APP_BASE`.

**Modified**
- `frontend/vite.config.js` — `base: '/app/'`, `build.outDir: 'dist/app'`.
- `frontend/package.json` — `"build": "vite build && node scripts/assemble-site.mjs"`.
- `frontend/src/pwa.js` — `SERVICE_WORKER_URL` derived from `import.meta.env.BASE_URL`.
- `frontend/src/App.jsx` — new `APP_ROOT` constant; both `history.pushState(…, '/')`
  calls now push `APP_ROOT` (logout, and the post-registration redirect that is
  followed by `location.reload()` — that one would otherwise have dropped a new
  user on the marketing homepage).
- `ops/nginx-security-headers.conf` — CSP moved to `set $scanid_csp` + one
  `add_header … $scanid_csp`; the "repeat the include" advice corrected, because
  it is actively wrong for CSP.
- `deploy/nginx-travelapp.conf` — `error_page 404 /404.html`; `location /` serves
  the site with `=404` and includes the site CSP; new `location /app/` holds the
  SPA fallback.
- `frontend/tests/helpers/index.js` — re-exports the three new helpers.
- `frontend/tests/helpers/auth.js`, `tests/e2e/{a11y,design-system,features,fonts,helpers,password-policy,responsive}.spec.js`,
  `tests/pwa/pwa.spec.js` — 22 × `page.goto('/')` → `page.goto(APP_BASE)`.
- `frontend/tests/helpers/imagePrep.js`, `tests/e2e/capture.spec.js` — the
  in-page dynamic import takes its specifier from `appSrc()`.
- `frontend/tests/global-setup.js` — base-aware warm-up paths.
- `frontend/tests/build/no-google-fonts.test.js` — scan scoped to `dist/app`.
- `frontend/tests/pwa/pwa.spec.js` — `dist/app/sw.js`; scope-derived precache assertions.

**Modified (stage 9 — docs)**
- `README.md` — the public site added to Architecture; the dev server now opens
  at `/app/`; what `npm run build` produces.
- `ops/README.md` — a new "Two zones, one server" section explaining the
  intersection trap, plus rows for `nginx-site-csp.conf` and the extended test.
- `frontend/tests/README.md` — `E2E_APP_BASE`, and a note that a production smoke
  test takes an **origin** (`E2E_BASE_URL=https://scanid.fr`), never `/app/`,
  because Playwright resolves `page.goto()` against the origin.

**Modified (stage 7)**
- `.github/workflows/deploy.yml` — three probes after the `/api` checks: the root
  must carry the rewritten `href="/app/"` (proves the site is there *and* that
  `assemble-site.mjs` ran), `/app/` must carry `/app/assets/index-` (proves the
  shell is there *and* was built with the right base), and an unknown path must
  return 404 (guards the `error_page` → 500 cycle if `404.html` ever goes missing).
- `ops/tests/test-nginx-headers.sh` — now builds both zones and asserts on each.

## 7. What has been verified, and how

Verification ran against a throwaway `nginx:alpine` container (already cached
locally; the same approach `ops/tests/test-nginx-headers.sh` uses) mounting the
**real** `ops/` snippets and the **real** `dist/`, with a self-signed cert for
`scanid.fr` and Chromium resolving that name to it — so the browser's origin is
literally `https://scanid.fr` and `'self'` means what it means in production.

- **Build:** `npm run build` → 48 precache entries (app only), 31 files into
  `dist/`, 40 links rewritten across 20 pages, 0 occurrences of `app.scanid.fr`
  left in any output file.
- **Routing, 16 routes:** `/`, `/index.html`, `/presentation.html`, `/faq.html`,
  `/iftm/`, `/404.html`, `/robots.txt`, `/sitemap.xml`, `/sw.js` → site zone;
  `/app/`, `/app/index.html`, `/app/deep/link`, `/app/sw.js`,
  `/app/manifest.webmanifest`, `/api/x` → app zone. **Exactly one** CSP header and
  **all three** other security headers on every one of them. `/nope` → real 404
  serving « Page introuvable ».
- **CSP in a real browser, 23 pages:** all clean — no violation, no page error, on
  either policy. The app's policy is byte-identical to what it was before.
- **Behaviour:** « Connexion » (nav *and* footer) → `/app/`, and clicking it lands
  on the app's login form; the calculator's inline script recomputes on input
  (`2 988 €` → `6 939 €`); the checklist form's `fetch()` reaches Formspree and the
  success panel appears; `/app/` boots and shows the login form.
- `/sw.js` is served as `application/javascript`, not HTML — the condition that
  makes hazard C's tombstone actually replace the stale worker.

**Stage 6 — the full test suite, all green, nothing skipped for convenience:**

| Suite | Result |
|---|---|
| `npm test` (unit + build output) | **79 passed**, 0 failed |
| `playwright --project=desktop` | **109 passed** |
| `playwright --project=mobile-small` | **109 passed** (capture + HEIC included) |
| `playwright --project=mobile-375` (WebKit) | **108 passed**, 1 skipped |
| `playwright --project=pwa` (built app) | **11 passed**, 48 precache entries |

**Stage 7 — deploy and ops:**

- `.github/workflows/deploy.yml`: YAML parses; the remote command passes `bash -n`;
  the single quotes in the `ssh` argument are **balanced (8)**. That last check
  caught a real defect while writing this — an apostrophe in the word "site's"
  inside a comment would have ended the `ssh` quoting and killed every deploy.
  A warning about it now sits in the file. The three probes were then run for
  real against the throwaway nginx: all three pass.
- `ops/tests/test-nginx-headers.sh`: **55 passed, 0 failed.** It now serves both
  zones and asserts, per zone, the four headers, *exactly one* CSP, a non-empty
  CSP value, and HSTS behaviour — plus five **isolation** assertions that the app
  policy never inherits `fonts.googleapis.com`, `fonts.gstatic.com`, `formspree.io`
  or `'unsafe-inline'` in `script-src`, and still carries `'unsafe-eval'`.
- `ops/tests/run-ops-tests.sh` (backups) is untouched by this work — it contains
  no reference to nginx — so it was not re-run.

**Final pass, on a clean `rm -rf dist && npm run build`:**

- `npm test` → **79 passed, 0 failed**.
- `npx playwright test` (all four projects) → **337 passed, 1 skipped, 0 failed**.
- All **29** site pages and assets answer 200; `/app/` answers 200; an unknown
  path answers **404** with « Page introuvable ».
- **Link crawl of all 22 pages, 28 distinct internal targets: no dangling link.**
  `app.scanid.fr` no longer appears among the external hosts at all — the only
  ones left are the site's own: `fonts.googleapis.com` (44), `fonts.gstatic.com`
  (22), `buy.stripe.com` (4), `www.cnil.fr` (2), `www.ionos.fr` (1).
- The guard works: running `scripts/assemble-site.mjs` with no app build exits 1
  with a message naming the missing file.

The precache is still **48 entries and app-only** — the 22 marketing pages were
not swept in, because `globPatterns` is relative to `outDir`, which is now
`dist/app`. That was the largest single risk to the privacy commitment in
`vite.config.js`, and it is closed by construction rather than by a deny-list.

## 8. Action required from the user (blocking for production)

1. **Stage all six untracked paths, not just `site/`.** `git commit -am` stages
   only *tracked* files and would silently leave every one of these out:

   ```
   HANDOVER.md
   frontend/scripts/assemble-site.mjs        <- npm run build calls it; missing = build fails
   frontend/scripts/legacy-sw-unregister.js  <- assemble-site copies it; missing = build fails
   frontend/site/                            <- 31 files; missing = build fails
   frontend/tests/helpers/appBase.js         <- helpers/index.js re-exports it; missing = npm test fails
   ops/nginx-site-csp.conf                   <- the vhost includes it; missing = nginx -t fails
   ```

   `git add -A` covers them. *(Not done here: "do not add, commit or push anything.")*
2. **One command on the VPS, after the first push** (see below). No DNS change,
   no certificate change.

### The nginx reload is NOT automatic — but almost nothing depends on it any more

**Stage 10 removed most of this.** What follows is the residue; the history is
in §11.

`PROGRESS.md:60` and `:361`: the `deploy` account sudo rule covers **only**
`systemctl restart travelapp.service`. It **cannot reload nginx**. Deploys sync
the vhost and print a NOTE. That was already true for every vhost change in this
project; this change touches the vhost, so it applies here.

What that means on the first push, reproduced against the **old** vhost serving
the **new** build:

Measured by serving the **new build** behind the **old vhost** in a container:

| | |
|---|---|
| `scanid.fr/` and all 22 pages | ✅ **work** |
| `/app/` | ✅ **works** |
| Typefaces on every page | ✅ **work** — self-hosted from `/fonts/`, so `font-src 'self'` covers them. Verified with `document.fonts`: Space Grotesk and Inter both actually loaded, on all 22 pages, under the **old** policy |
| Pricing calculator, checklist handler | ✅ **work** — externalised to `/scripts/`, so `script-src 'self'` covers them. Verified: the calculator recomputes, `2 988 €` → `6 939 €`, under the **old** policy |
| The deploy run | ✅ **green**, with an unmissable ACTION REQUIRED banner |
| **The four Formspree lead forms** | ❌ **refused** — `form-action 'self'` and `connect-src 'self' data:`. No static file can make a cross-origin POST allowed; this genuinely needs the new policy |
| An unknown path | 200 with the homepage instead of `404.html`. **Not a regression** — scanid.fr already answers unknown paths with 200 today (the app shell). It is an improvement waiting, not a breakage |

So the residue is: **lead capture, and a real 404 status.** Everything a visitor
reads is correct either way.

**A missing include is now caught.** `deploy/nginx-travelapp.conf` includes two
files from `ops/`. If one were never committed, nothing would look wrong — nginx
keeps serving from the config already in memory — until the next **reboot**, when
a missing include is `[emerg]` and nginx refuses to START, taking the whole site
down. `nginx -t` would catch it but the deploy cannot run it. So the deploy now
checks every include target is readable (no privileges needed) and fails if not.
Verified both ways against a real vhost layout.

The fix for the reload itself, once, from an account with sudo (`lasha`):

```bash
sudo nginx -t && sudo systemctl reload nginx
```

Then confirm it worked, from the same session — no sudo needed:

```bash
bash /opt/travelapp/ops/verify-front-end.sh
```

`ops/verify-front-end.sh` is new: eight read-only HTTPS checks that separate
"the build is wrong" from "nginx has not been reloaded". It was tested against
both vhosts in a container before being committed, and that testing caught a
real defect in it — `curl … | grep -q` under `set -o pipefail` reports a
SUCCESSFUL match as a failure, because `grep -q` exits early and SIGPIPEs curl.
On small responses curl usually finishes first and it passes anyway, so the bug
is an intermittent false alarm rather than a consistent one. Every check now
reads into a variable and greps a here-string; there is not one pipeline left.

Or permanently, one time, so no future deploy ever needs it — `visudo`:

```
deploy ALL=(root) NOPASSWD: /usr/sbin/nginx -t, /bin/systemctl reload nginx
```

After that every probe passes and later deploys are silent. `nginx -t` needs
`/opt/travelapp/ops/nginx-site-csp.conf` to exist, which it will as long as that
file was committed.

**`frontend/site/` MUST STAY TRACKED — do not gitignore it.** This was tried on
2026-09-09 and reverted, after reproducing the outcome against a checkout with
the directory removed:

```
assemble-site: site does not exist — nothing to put in front of the app.
>>> exit code: 1
```

- `ci.yml` → `frontend` job, step 4 *Build production bundle*: **fails**.
- `deploy.yml` → step 3 *Build frontend*: **fails**, so steps 4–6 (SSH, rsync,
  restart) never run. Production is left untouched — no outage, but the front
  page never ships, and **the app stops being deployed too**, because that build
  precedes the rsync.

The build fails on purpose. The alternative — tolerating the missing directory —
is worse: `deploy.yml` rsyncs `frontend/dist/` with `--delete`, so the server
copy is a strict mirror, and a build without the site would **erase the site from
the server** and leave `scanid.fr/` returning 404.

Delivering the site out-of-band is possible but is a real restructure (its own
server directory the deploy never touches, nginx `root` repointed, `location
/app/` on an `alias`, the link rewrite moved from the build into an upload step,
and a manual upload to remember on every server rebuild). The user chose to track
the directory instead.

## 9. Remaining stages

- ~~**Stage 6 — test suite**~~ — done, see §7.
- ~~**Stage 7 — deploy + ops**~~ — done, see §7.
- ~~**Stage 8 — polish**~~ — deliberately NOT done; both items moved to §10 as
  questions for the user, because "make only necessary changes" is a standing
  instruction and neither is necessary.
- ~~**Stage 9 — docs**~~ — done. `PROGRESS.md` was left alone: it is a dated
  status log, and this file is the live record.

## 9b. Audit of `frontend/site/` before committing it (2026-09-09)

Asked: is there anything in `site/` that must not be committed or published?

**Nothing that must be kept secret.** Verified, not assumed:

- **No credentials of any kind.** No API key, token, password, private key or
  service-account file, in any of the 31 files.
- **Git history is clean too** — the only `.env*` ever committed is
  `backend/.env.example`, a template.
- **No real identity documents.** This was the one worth checking properly:
  - the 9 base64-embedded images are 2 distinct files — a stylised ID-card
    illustration with a line-drawn face and grey placeholder bars;
  - `scanid-presentation.mp4` (H.264, 1280×720, 17.4 s, no audio) was decoded
    and sampled at 31 points across its whole length. It is pure motion
    graphics: a cartoon face, a stylised monitor, a results table whose cells
    are blue placeholder bars. No document, no name, no number;
  - `ScanID-Checklist-RGPD.pdf` is an 11-point RGPD checklist, author "ScanID",
    generated by ReportLab. No embedded personal data;
  - `og-image.png` / `apple-touch-icon.png` carry no EXIF or text metadata.
- The Formspree form ID and the `buy.stripe.com` links are public by design —
  they only work as public endpoints.
- Company identifiers in `mentions-legales.html` (RCS/SIREN/TVA, address) are a
  **legal publication requirement** in France, not a leak.

**But four pages are not finished, and would be published as-is:**

| Page | What is visible | Reachable from |
|---|---|---|
| `temoignages.html` | An editor note that literally reads « **Supprimez cette note avant publication** », plus **13 `[…]` placeholders** (`[Nom de l'agence]`, `[X] h économisées`, `[Prénom Nom]`) | `ressources.html`, and listed in `sitemap.xml` |
| `mentions-legales.html` | « ⚠️ **À faire valider** … faites-le relire par un professionnel du droit avant publication » | footer of all 20 pages |
| `cgv.html` | the same banner | footer of all 20 pages |
| `politique-confidentialite.html` | the same banner | footer of all 20 pages |

Also a judgement call: `mentions-legales.html:107` publishes a **personal mobile
number** (+33 6 95 81 18 66). France requires a contact means, not a personal
mobile.

None of this was changed — `frontend/site/` is read-only and this is content, not
code. It is the owner's call. Confirmed after the audit: no file under
`frontend/site/` has been written at any point.

### `.gitignore` review of the rest of the repository

Already covered before this work, and verified: `backend/.env`, `frontend/.env.local`,
`newvenv/`, `dist/`, `__pycache__/`, `*service-account*.json`, and — importantly —
`DUBROVNIK.pdf` and `ITALIE 2 PIECES IDENTITE - copie.pdf`, the two **real identity
documents** in the repository root. None has ever been committed.

Added to the root `.gitignore` (verified to match no tracked or on-disk file):
`*.age`, `*.pem`, `*.crt`, `*.cer`, `*.key`, `*.p12`, `*.pfx`, `id_rsa`,
`id_ed25519`, `scanid-backup.key`, `*.dump`, `*.sql`, `*.sql.gz`. Every one
corresponds to an artefact this repository's own scripts produce or its docs tell
you to create — `ops/backup.sh` writes an age-encrypted dump, `ops/README.md` has
you generate its key with `age-keygen`, `deploy.yml` authenticates with an SSH
key, and the vhost is served by a certbot certificate.

## 11. Stage 10 — removing the dependency on a server action

The four symptoms of "the new config is on disk but not loaded" were addressed
where they could be, in the build rather than in the policy. `frontend/site/`
was **not** touched: every transformation happens on the copy on its way into
`dist/`, the same mechanism as the existing « Connexion » link rewrite.

| Symptom | What was done | Result |
|---|---|---|
| Fonts blocked | `assemble-site.mjs` builds `dist/fonts/site.css` + 28 files from `@fontsource` (Space Grotesk 400/500/600/700, Inter 400/500 + 400 italic, `latin` and `latin-ext` — the exact subsets Google serves a French page), and rewrites all 22 pages to it. 44 preconnect hints removed. | **Fixed under any policy allowing `'self'`** |
| Inline scripts blocked | The two real inline `<script>` blocks are written to `dist/scripts/` and replaced with `src=` references. `<script type="application/ld+json">` is left alone — it is data, never executed. | **Fixed under any policy allowing `'self'`** |
| Unknown path returns 200 | Nothing. A static file cannot change an HTTP status; only `try_files … =404` can. | **Needs the reload** — but it is not a regression |
| Deploy red | Probes are hard assertions when nginx **was** reloaded, and a loud ACTION REQUIRED banner (deploy green) when it **could not be**. Verified by running the extracted probe block against both vhosts. | **Fixed** |

Two things got better rather than merely equal:

- **`ops/nginx-site-csp.conf` is now much tighter.** It grants exactly one
  origin, `https://formspree.io`. Gone: `script-src 'unsafe-inline'` (the most
  dangerous token a policy can carry — neither zone has it now),
  `fonts.googleapis.com`, `fonts.gstatic.com`.
- **`no-google-fonts.test.js` guards the whole build again.** It had been
  narrowed to `dist/app` because the site pages could not be fixed; they can be
  now, so the scan covers both halves — and three new tests were added: both
  entry documents, the self-hosted faces actually being shipped and referenced,
  and no inline `<script>` surviving into any site page.

This also settles the RGPD point raised in §9b: the pages no longer hotlink a US
font CDN, so no visitor IP reaches Google from anywhere on scanid.fr.

**Verified after stage 10:** `npm test` **81 passed** (2 new), `npx playwright
test` **337 passed / 1 skipped**, `ops/tests/test-nginx-headers.sh` **57 passed**,
all 22 pages clean in Chromium under **both** the old and the new policy, and the
real deploy-probe block exercised against both vhosts in all three states.

## 13. LIVE — verified in production, 2026-09-09

`c2cdd23` was deployed and nginx reloaded by hand as root
(`nginx -t && systemctl reload nginx`). Verified **from outside the VPS**, over
the public internet, not just on the loopback:

| Check | Result |
|---|---|
| `https://scanid.fr/` | 200 — « Scanner de passeports et CNI pour agences de voyages \| ScanID » |
| « Connexion » link | `href="/app/"` — the rewrite is live |
| `https://scanid.fr/app/` | 200, `/app/assets/index-D1pk25fW.js` |
| `https://scanid.fr/nope` | **404** — « Page introuvable » |
| `https://scanid.fr/fonts/site.css` | 200 |
| Site CSP | `script-src 'self'` + formspree — the tightened policy is live |
| App CSP | `script-src 'self' 'unsafe-eval'` — unchanged |
| 11 live pages in Chromium | all clean, **Space Grotesk + Inter loaded on every one** |
| Calculator, on the live site | `2 988 €` → `6 939 €` — runs |
| Certificate | `CN = scanid.fr`, Let's Encrypt, valid to **2026-12-07** |

The certificate renewal hook was **confirmed missing** (`renewal-hooks/deploy/`
was empty and the renewal conf had no hook line) and has been created, so §10
item 3 is closed — pending one content check, below.

**The renewal hook is confirmed working.** The first attempt was written with a
heredoc that terminal echo mangled during the paste; it was rewritten with a
single `printf` (which a paste cannot corrupt) and then proven behaviourally,
not by inspection — nginx replaces its worker processes on reload, and running
the hook moved them from `24001 24002` to `24076 24077` while the master stayed
put. Exit status alone would NOT have proved this: a script containing only
`#!/bin/sh` also exits 0, silently, and that is exactly the shape a lost heredoc
body takes.

**NOTHING REMAINS TO BE DONE ON THE VPS.**

## 12. Found after the first push (c2cdd23)

**`frontend/tests/build/` was gitignored — the build guard had never run in CI.**
`.gitignore` carried a generic `build/` under "Build outputs", and that pattern
matches a directory of that name at ANY depth, so it also swallowed
`frontend/tests/build/`. The suite was on disk, passing locally, and
`actions/checkout` had never received it: the pushed tree declares **76** tests,
the working tree **81**.

That matters more than a count. Those five tests are what backs the claim that
no page of either half reaches Google — the guarantee this work introduced — plus
the checks that the self-hosted faces are really bundled and referenced, and that
no inline `<script>` survives into a site page. A guard that only runs on the
author's machine is not a guard.

Fixed with a negation, `!frontend/tests/build/`, and verified three ways: the
file is no longer ignored, a genuine `frontend/build/output.js` is still ignored
by the same generic rule, and a full CI simulation of the next commit builds and
runs **81 passed, 0 failed**.

Pre-existing, not introduced here — but it was hiding the very guard this change
depends on.

**Also verified against the pushed commit itself:** `git archive c2cdd23` was
built and tested exactly as `actions/checkout` would deliver it — the build
succeeds (33 files, 22 pages rewritten, 14 @font-face) and the 76 tests it
contains pass. `ops/nginx-site-csp.conf` IS in the commit, so the vhost include
guard passes and nginx will not fail at a reboot.

## 10. Two things deliberately left undone — ask the user

Neither is a defect introduced by this work, and neither is needed for the site
to be the front of scanid.fr. Both are one-word decisions.

1. **`www.scanid.fr` → `scanid.fr` redirect.** `frontend/site/.htaccess` did this
   on Apache and it is inert on nginx, so `www` now serves the whole site under
   the non-canonical hostname. Every page carries `<link rel="canonical">` to the
   apex, so search engines will consolidate anyway. Doing it properly means a new
   443 server block with its own TLS config, on a live site — real risk for a
   small SEO gain. **Not done.**

2. **The app's four dead footer links.** `frontend/src/App.jsx:471-474` renders
   « Mentions Légales », « Politique de Confidentialité », « CGU » and
   « Contact » as `href="#"`. Those pages now exist on the same origin
   (`/mentions-legales.html`, `/politique-confidentialite.html`, `/cgv.html`,
   `/index.html#contact`). Wiring them is four lines and zero risk — best with
   `target="_blank" rel="noopener"` so the session view is not lost, matching
   how `PHOTO_GUIDE_URL` is already handled at `App.jsx:892`. **Not done**: the
   links were already dead before this work, so fixing them is not part of it.

3. **UNVERIFIED, AND A SITE-DOWN RISK — does anything reload nginx when the
   certificate renews?** Same family as the reload problem, but pre-existing and
   independent of this work. The certificate was issued with
   `certonly --webroot` (PROGRESS.md:33), which does **not** reload the web
   server after a renewal, and there is no renewal hook documented anywhere in
   this repository. If none exists on the VPS, then: the certificate renews
   around **7 November 2026**, nginx keeps serving the OLD one from memory, and
   on **2026-12-07** it expires — every visitor gets a full-page browser
   security warning, with nothing having changed that day to explain it.

   Cannot be checked from here. On the VPS:

   ```bash
   sudo ls -l /etc/letsencrypt/renewal-hooks/deploy/
   sudo grep -i hook /etc/letsencrypt/renewal/scanid.fr.conf
   ```

   If there is no hook, add one:

   ```bash
   sudo tee /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh >/dev/null <<'EOF'
   #!/bin/sh
   systemctl reload nginx
   EOF
   sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh
   sudo /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh   # prove it runs
   sudo certbot renew --dry-run                                  # prove renewal works
   ```

   A useful side effect: that hook reloads nginx on every renewal, which would
   also pick up any vhost change sitting on disk.

4. Worth passing to whoever owns the site content: all 22 pages hotlink Google
   Fonts. That is what forces `fonts.googleapis.com` / `fonts.gstatic.com` into
   `ops/nginx-site-csp.conf`, and it is an EU personal-data transfer on every
   page load — on a French site that sells RGPD compliance. Self-hosting the two
   families would let both origins be deleted from that file. `frontend/site/` is
   read-only, so this cannot be fixed here.

# SCANID — HANDOVER

Resume file for the "public site becomes the front door of scanid.fr" work, and for the
application tasks that followed it.

**If you are a new session: read §0 first and obey it for the whole session. Then read
§A (the current task) and continue at the first stage in §A.4 whose status is not `DONE`.
§1–§9 are the completed v5 task, kept as a record.**

Last updated: 2026-09-14 (task A — credits on success, « Ajouter un Document », credits badge — complete locally, not deployed)

---

## 0. CONSTRAINTS AND PERMISSIONS — BINDING FOR EVERY SESSION

Given by the user, and still in force. They apply to the current task (v5) exactly as
they applied to the previous one (v4).

### Constraints

1. **All current functionality must be preserved**, except what the user explicitly
   demands to change.
2. **Make only necessary changes.**
3. **Do NOT `git add`, `git commit` or `git push` anything.**
4. **`frontend/site/` is READ-ONLY.** It may be read, but never edited, deleted, moved or
   renamed.
5. **The source of truth is now `frontend/scanid-site-v5-deploy/`** — it replaces the
   content of `frontend/site/` as what must be implemented. *(Operating rule derived from
   this, not stated by the user: the source of truth is treated as read-only too. Nothing
   in this work writes into it.)*
6. **`frontend/dist/` is the target.** Its content may be deleted and rewritten, but only
   to bring it in line with the source of truth.
7. **The source pages must be what a visitor sees FIRST at `https://scanid.fr`** — the
   head / front part of the app, assembled in logical order, with the application behind
   them at `/app/`.
8. **Parse the whole directory first**, then decide what the source contains and in which
   order to implement it.
9. **Work in logical stages.** Write the demand into this file **first**, then **update
   this file after every stage**, so an interrupted session can be resumed from it.
10. **This file must state clearly what changed** against the previous version (the
    content of `frontend/site/`), and must carry these constraints at the beginning.

### Permissions

| Where | Read | Run commands / read output | Edit / delete / install |
| --- | --- | --- | --- |
| Inside the repository root `/home/lasha/Public/new` | yes | yes | yes — **except** `frontend/site/` (read-only) and within the limits above |
| `frontend/site/` | yes | yes | **NO** |
| `frontend/dist/` | yes | yes | yes, to match the source of truth |
| Outside the repository root | yes, when needed for the task | yes, when needed for the task | **only with the user's explicit permission — ask first** |

### Housekeeping facts a new session needs

- `frontend/site1/` is the user's **local backup of the revision before v4**. It is
  gitignored (`frontend/.gitignore`: `site[0-9]*/`) and is not part of any build.
- `/home/lasha/Public/new/site.html` and `site1.html` are **local visual-comparison files**
  the user asked for: `site.html` = the v4 build (`frontend/site/`), `site1.html` = the
  build before it (`frontend/site1/`). They do **not** show v5. They are gitignored (root
  `.gitignore`: `/site.html`, `/site[0-9]*.html`), so `git add .` does not stage them.

---

## A. CURRENT TASK (2026-09-14) — THE APPLICATION: CREDITS, HEADING, BADGE

The user: *"you have the same constraints and permissions as they are in
SCANID-HANDOVER.md, but the tasks are different."* §0 therefore applies unchanged.

### A.1 Demand (the user's words, in substance)

1. **Charge only successful extractions — never failures.** Example given: 10 credits,
   an extraction ends with 2 failures and 3 successes → the user pays **3** credits and
   **always** has **7** left.
2. **« Ajouter un Passeport » → « Ajouter un Document »** (heading of the upload card).
3. **The credits badge** (blue pill « Crédits : N », top right of the application bar)
   **moves to just under « Bienvenue, …! »** in the dashboard's welcome card.
4. **Every other current functionality is preserved.**

### A.2 State found before any change (measured)

- `frontend/site/` is **absent from disk** at the start of this session (git shows its 31
  files as deleted in the working tree). Not done by this session; §0.4 forbids touching
  it, so it is left as found. The build does not read it (the assembler reads
  `scanid-site-v5-deploy/`, §3).
- **Charging** — `backend/main.py`, end of `_run_ocr_extraction_job`: after the per-page
  loop, one atomic `UPDATE` subtracts `page_count = len(extraction_results)` from
  `page_credits` — **every page of the file**, including failed pages and the verso of a
  split CNI — and adds the same number to `uploaded_pages_count`. A job that fails as a
  whole (exception in the OCR) returns before this and charges nothing.
- The upload gate (`page_credits <= 0` → 403 « Crédits insuffisants ») is at the upload
  endpoint, before the job.
- `backend/tests/test_ocr_split_cni.py::test_job_skips_verso_entries_and_charges_every_page`
  **pins the old rule** (1 success + 1 verso + 1 failure → 3 credits charged).
- **Heading** — `frontend/src/App.jsx`, `FileUploader`: `<h3>Ajouter un Passeport</h3>`.
  No test references the text.
- **Badge** — `frontend/src/App.jsx`, `App` header: `<span className="sid-credits">` in
  `.sid-topbar-right`, next to « Déconnexion ». Styled in `frontend/src/scanid-app.css`
  (`.sid-credits`: cyan `#0EA5E9` on a 12 % cyan tint, designed for the navy bar).
  `tests/e2e/design-system.spec.js` **asserts the badge is inside the top bar**;
  `a11y.spec.js` measures its contrast; `smoke`, `privacy`, `features` and the `login()`
  helper find it by `.sid-credits` anywhere on the page.
- Baselines before any edit: backend `pytest` **216 passed**; frontend unit **81 passed**;
  e2e desktop project **109 passed**; `eslint src/App.jsx` **12 problems** (7 errors,
  5 warnings — all pre-existing, none on a line this task touches).

### A.3 Decisions (what "only necessary changes" means here)

1. **1 credit = 1 successfully extracted document** = one entry in the job's `successes`
   (a row saved to `passports`). Failures of every kind cost nothing: unreadable page,
   validation error, database error, whole-job failure. The verso of a split CNI merges
   into its recto's single success, so **recto + verso = 1 credit**.
2. **« Pages Traitées » (`uploaded_pages_count`) is not changed** — it still counts every
   processed page. The demand is about what the user *pays*, not about that counter.
3. **The upload gate is not changed** (`page_credits <= 0` refuses the upload).
4. **Badge:** same element, same class (`.sid-credits`), same text « Crédits : N »,
   moved into the welcome card directly under the `<h3>`. On the white card the navy-bar
   cyan measures ≈ 2.5:1 (fails WCAG AA); its text colour becomes the existing
   `--sid-info` token (`#0369a1`, ≈ 5.2:1 on the same tint). « Déconnexion » stays in
   the bar.
5. **Heading:** text only.
6. Tests that encode the **old** behaviour are updated to the demanded one (the split-CNI
   charge assertion, the "badge is in the top bar" assertion); a test for the user's own
   example (3 successes + 2 failures → 7 of 10 left) is added. No other test is touched.

### A.4 Stages

| # | Stage | Status |
| --- | --- | --- |
| A0 | Survey code, tests and baselines (§A.2) | **DONE** |
| A1 | Write demand, findings, decisions and plan into this file | **DONE** |
| A2 | Backend: charge `len(successes)`; update/add tests | **DONE** |
| A3 | Frontend: heading text; badge under « Bienvenue »; e2e assertion | **DONE** |
| A4 | Verify: backend, unit, e2e (desktop + mobile), lint, build, rendering | **DONE** |
| A5 | Record what changed and how to ship | **DONE** |

### Stage A2 — Backend — DONE

`backend/main.py`, end of `_run_ocr_extraction_job` — the only functional change:

```diff
-    # Charge one credit per processed page and track the page counter.
+    # Charge one credit per SUCCESSFUL extraction only — a failed page costs
+    # nothing — and track every processed page in the page counter.
     page_count = len(extraction_results)
+    credits_charged = len(successes)
 ...
-                        page_credits=models.User.page_credits - page_count,
+                        page_credits=models.User.page_credits - credits_charged,
                         uploaded_pages_count=models.User.uploaded_pages_count + page_count,
```

Plus two comments made true again (`SIGNUP_PAGE_CREDITS`, the verso branch). The update is
still one atomic `UPDATE`; the `credit_update` SSE push is unchanged.

Tests:
- `tests/test_ocr_split_cni.py` — the test pinning the old rule renamed
  `…_charges_only_successes`; credits after the job `7` → `9`; `uploaded_pages_count`
  stays `3`.
- **New** `tests/test_credit_charging.py` — the user's example (10 credits; pages
  ok / unreadable / ok / duplicate refused at save / ok → 3 successes, 2 failures →
  **7 left**, 5 pages counted); only failures → 10 left; OCR crash → 10 left.

Result: `pytest` **219 passed** (216 + 3). The same tests run against `HEAD`'s `main.py`
in a scratch copy: **3 fail** (7→5, 10→8, 9→7) — they detect the old charge. The crash
test passes on both (that path never charged).

### Stage A3 — Frontend — DONE

`frontend/src/App.jsx`
- `FileUploader`: `<h3>Ajouter un Passeport</h3>` → `<h3>Ajouter un Document</h3>` (and the
  layout comment that names the card).
- `App` header: the `<span className="sid-credits">` removed from `.sid-topbar-right`;
  « Déconnexion » stays there, alone.
- `Dashboard` nav: the same `<span className="sid-credits">Crédits : {user.page_credits}</span>`
  inserted directly after `<h3>Bienvenue, {user.first_name}!</h3>`, before « Pages
  Traitées ». The nav card is rendered on every tab (Passeports, Mon Compte,
  Administration), so the badge stays visible wherever it was visible before, and still
  refreshes on the `credit_update` SSE event (it reads the same `user` object).
- GlobalStyles, NAVIGATION SIDEBAR: `.dashboard-nav .sid-credits { display: inline-block;
  margin: 0.35rem 0 0.5rem; }` — spacing only.

`frontend/src/scanid-app.css` — `.sid-credits`: `color: var(--sid-cyan)` →
`color: var(--sid-info)` (contrast on the white card, §A.3.4). Shape, tint, border, font
unchanged. Recorded in `CHANGELOG-css.md` v1.2.

`frontend/src/upload/uploadQueue.js` — one comment corrected ("a credit per page" → "a
credit per extracted document"). No code.

`frontend/tests/e2e/design-system.spec.js` — the test asserting the badge is **in the top
bar** now asserts the demanded placement: not in the bar; `.dashboard-nav h3 + .sid-credits`
reads « Crédits : N » on the Passeports and Mon Compte tabs; exactly one badge on the page.

### Stage A4 — Verify — DONE

| Check | Before (baseline) | After |
| --- | --- | --- |
| Backend `pytest` | 216 passed | **219 passed** (3 new) |
| New/changed charge tests against `HEAD`'s `main.py` | — | **3 fail** — they detect the old rule |
| Frontend unit `npm run test:unit` | 81 passed | **81 passed** |
| E2E desktop | 109 passed | **109 passed** |
| E2E all projects (desktop, mobile-small, mobile-375 WebKit, pwa) | — | **337 passed, 1 skipped** (the static WebKit skip in `capture.spec.js`, unrelated) |
| `eslint src/App.jsx` | 12 problems | **12 problems** (identical; none on a touched line); the other two touched JS files clean |
| `.sid-credits` contrast (a11y spec, on the white card) | 5.97:1 in the bar | **5.25:1** — AA pass |
| Build guards `tests/build/no-google-fonts.test.js` | 5 pass | **5 pass** |
| `dist/` rebuilt by `npm run build` (the deploy's command) | — | app half carries « Ajouter un Document », no « Ajouter un Passeport », the new badge rule; **site half: 22 / 22 pages byte-identical to live https://scanid.fr** |

**Rendering** (Chromium, mocked backend, 1280×800 and 375×740): top bar = logo +
« Déconnexion » only (0 badges in it); welcome card = « Bienvenue, Alice! » → pill
« Crédits : 12 » (≈ 10 px under the heading) → « Pages Traitées : 3 » → tabs; upload
card heading « Ajouter un Document »; no horizontal overflow at 375 px.

### Stage A5 — What changed, and how to ship — DONE

**Files changed by task A** (nothing staged, nothing committed):

| File | Change |
| --- | --- |
| `backend/main.py` | charge `len(successes)` instead of every page; 2 comments |
| `backend/tests/test_ocr_split_cni.py` | old-rule assertion updated (7 → 9), test renamed |
| `backend/tests/test_credit_charging.py` | **new** — the user's example + no-charge cases |
| `frontend/src/App.jsx` | heading text; badge moved from top bar to under « Bienvenue »; 1 spacing rule; 1 comment |
| `frontend/src/scanid-app.css` | `.sid-credits` text colour `--sid-cyan` → `--sid-info` (+ comment) |
| `frontend/src/CHANGELOG-css.md` | v1.2 entry |
| `frontend/src/upload/uploadQueue.js` | 1 comment |
| `frontend/tests/e2e/design-system.spec.js` | badge-placement test follows the demand |
| `SCANID-HANDOVER.md` | this section |

**To ship:** `git add` / `git commit` / `git push` to `master` (the user's step, §0.3). The
deploy workflow rebuilds the frontend and restarts the backend service; no database
migration, no nginx change, no new dependency. ⚠️ **`git add .` would now also stage the
deletion of the 31 files of `frontend/site/`** (absent from disk, §A.2) — stage the files
above by name unless that deletion is intended.

**Behaviour notes for the user (not demanded, therefore not changed):**
- The upload gate refuses only at `page_credits <= 0`. A user with 1 credit who uploads a
  10-page PDF that yields 10 successes ends at −9, exactly as before (only failures are
  now free).
- « Pages Traitées » still counts every processed page, failed ones included.
- Charges already taken on past jobs are not refunded.

---

## 1. PREVIOUS TASK (COMPLETE, LIVE) — IMPLEMENT v5 AS THE FRONT DOOR

**Demand (2026-09-13):** use the content of `frontend/scanid-site-v5-deploy/` instead of
the content of `frontend/site/`, under all the constraints in §0.

In practice: `frontend/dist/` must hold the v5 site as the front door, built by the same
pipeline and to the same standard as v4 was, with the application at `/app/` untouched.

---

## 2. WHAT CHANGED — v5 (`scanid-site-v5-deploy/`) AGAINST v4 (`site/`)

Measured file by file, not estimated. After subtracting the four changes common to every
page, each page's remaining difference was diffed individually, so the list below is
complete.

### 2.1 File inventory

| | Count | Files |
| --- | --- | --- |
| **Removed** | 1 | `calculateur.html` — the savings calculator page |
| **Added** | 1 | `contact.html` — a dedicated contact page |
| **Changed** | 20 | 19 HTML pages + `sitemap.xml` |
| **Identical** | 10 | `404.html`, `iftm/index.html`, `robots.txt`, `.htaccess`, `favicon.ico`, `favicon.svg`, `apple-touch-icon.png`, `og-image.png`, `ScanID-Checklist-RGPD.pdf`, `scanid-presentation.mp4` |

Page count stays at **22** (21 at the root + `iftm/index.html`).

### 2.2 Changes common to all 19 nav-bearing pages

Every page that carries the site navigation received the same four changes (verified by
a per-page matrix; `404.html` and `iftm/index.html` have no nav and are unchanged):

1. **New "trial bar"** — a full-width blue banner directly under the navigation, linking to
   `essai.html`:
   *« 20 scans offerts pour tester ScanID sur un vrai dossier groupe · Demander mon essai
   gratuit → »*. Styled by a new `<style>` block (`nav{flex-wrap:wrap}` + `.trial-bar`,
   with a smaller size under 640px).
2. **« Essai gratuit » button removed from the navigation.** The trial bar replaces it as
   the call to action.
3. **« Contact » in the navigation now opens `contact.html`** (it was the `#contact`
   anchor on the home page).
4. **« Contact » link added to the footer**, also → `contact.html`.

Navigation in v5: Présentation · Ressources · Tarifs · FAQ · Contact · Connexion
(six items; v4 had seven, ending with the « Essai gratuit » button).

### 2.3 Page-specific changes

**`contact.html` — NEW**
- Title « Contact | ScanID – Scanner de passeports et CNI pour agences de voyages », h1 « Contact ».
- A contact form posting to Formspree (`https://formspree.io/f/xqeowdvk`, the same form ID
  as the other lead forms): `nom`*, `societe`, `email`*, `telephone`, `message`*,
  `consentement`* (* required), plus the `_subject` / `_gotcha` hidden fields.
- Shows `contact@scanid.fr`, a Paris address and a `+33` telephone number.
- No inline script.

**`calculateur.html` — REMOVED**, and every link to it was removed with it (verified: no
page in v5 references it):
- `alternatives.html` — the parenthetical « (comptez-le avec notre calculateur) » removed
  from a paragraph.
- `erreurs-saisie-passeport.html` — the end-of-article call to action changed from
  « Estimez ce que la saisie manuelle vous coûte… / Ouvrir le calculateur » to
  « Testez ScanID sur un vrai dossier groupe : 20 scans offerts, sans carte bancaire. /
  Demander mes 20 scans offerts » → `essai.html`.
- `ressources.html` — the « Calculateur d'économies » card removed.
- `sitemap.xml` — the `calculateur.html` entry replaced by `contact.html` (lastmod 2026-09-13).

**`index.html` (home page)**
- « Commencer » (À la carte) and « Nous contacter » (Pack 10 000+) → `contact.html`
  (were `#contact`).
- The four « Souscrire » Stripe buttons gained `data-pack="100|1000|3000|5000"` and a
  `js-buy` class — **see the defect in §2.4.**
- **New inline script:** fetches `GET /api/config`; if the response says `signup: true`, a
  « Souscrire » click goes to `/app/inscription?pack=<n>` instead of Stripe. Otherwise the
  Stripe link works as before.

**`essai.html` (free trial)**
- Two new optional form fields: **SIRET** (`name="siret"`, 14 digits, « requis pour la
  facturation électronique ») and **N° de TVA intracommunautaire** (`name="tva"`).
- The inline submit script is byte-identical to v4. It serialises every form field, so the
  two new fields are sent automatically.

**`ressources.html`**
- The RGPD checklist is promoted from a card to a **full-width "feature box"** at the top of
  the page (new `<style>` block, `.feature-box`).
- The five article cards are simplified: `class="card article-card"` → `class="card"`,
  and their inner wrapper `<div>` removed.
- The calculator card removed (above).

### 2.4 Defect found in the v5 source — NOT fixed (the source is the truth)

**`index.html` lines 325, 342, 362, 379 — the four « Souscrire » buttons carry the
`class` attribute twice:**

```html
<a href="https://buy.stripe.com/…" data-pack="100" class="js-buy" class="btn-plan btn-outline">
```

HTML keeps the **first** duplicate attribute and discards the rest. So each button gets
`class="js-buy"` only and **loses `btn-plan btn-outline` / `btn-plan btn-fill`** — the
four buttons render without their button styling. The `js-buy` hook itself still works.

The intended markup is almost certainly `class="js-buy btn-plan btn-outline"`. It is
reported, not repaired: the source of truth is copied faithfully, and correcting it is the
user's call. Stage 4 checks the rendered effect.

### 2.5 What v5 does NOT change

- No new external origin: still only `formspree.io` and `buy.stripe.com`, so
  `ops/nginx-site-csp.conf` needs no change.
- No broken internal link anywhere in v5; `index.html#tarifs` still exists.
- The Google Fonts links keep the shape the assembler rewrites (22/22 pages match).
- « Connexion » still → `/app/`.

---

## 3. HOW THE BUILD PICKS UP v5 — THE ONE NECESSARY CODE CHANGE

The front-door pipeline already exists and is unchanged in design:

| Piece | Role |
| --- | --- |
| `frontend/scripts/assemble-site.mjs` | Copies the source of truth → root of `dist/`, applying the CSP rewrites (Google Fonts → self-hosted `/fonts/`, inline `<script>` → `/scripts/`, `app.scanid.fr` → `/app/`). Never writes into its source. |
| `frontend/vite.config.js` | Builds the React application into `dist/app/` and nothing else. |
| `npm run build` | `vite build` **then** `assemble-site.mjs`. |
| `deploy/nginx-travelapp.conf` | `/` → site half, `/app/` → application, `/api/` → backend `:8001`. |

The assembler reads its source from **one constant**: `assemble-site.mjs:43`,
`const SITE = join(FRONTEND, 'site');`. A search of every script, test, config, workflow
and nginx file found **no other functional reference** to that directory.

Because `frontend/site/` is read-only, v5 cannot be copied into it. So the only way to
honour both "use v5 instead of site" and "site is read-only" is to **repoint that one
constant at `scanid-site-v5-deploy`.** Nothing else in the pipeline changes.

**Consequence for deployment:** the deploy runner builds from the committed repository.
`frontend/scanid-site-v5-deploy/` is currently **untracked** (it is not gitignored). It
must be committed together with `assemble-site.mjs`, or the runner's build fails loudly
(`assemble-site: scanid-site-v5-deploy does not exist`). See §7.

---

## 4. LOGICAL ORDER OF THE v5 FRONT DOOR

Derived from the v5 pages' own navigation, footer, resources hub and `sitemap.xml`.

**Tier 0 — entry point:** `index.html` → `/`

**Tier 1 — primary navigation** (identical on all 19 nav-bearing pages)
1. `presentation.html` — Présentation
2. `ressources.html` — Ressources
3. `index.html#tarifs` — Tarifs
4. `faq.html` — FAQ
5. `contact.html` — Contact *(new target in v5)*
6. `/app/` — Connexion → the application

**Call to action under the nav:** trial bar → `essai.html` *(replaces the nav button)*

**Tier 2 — resources hub** (`ressources.html`)
- Feature box: `checklist.html`
- `guide.html`, `guide-photo.html`, `alternatives.html`, `temoignages.html`
- Articles: `rgpd-fuite-donnees.html`, `rgpd-conserver-copies-passeport.html`,
  `transfert-donnees-securise.html`, `erreurs-saisie-passeport.html`,
  `apis-agences-voyages.html`

**Tier 3 — trust, contact & legal** (footer): `securite.html`, `contact.html`,
`politique-confidentialite.html`, `mentions-legales.html`, `cgv.html`

**Tier 4 — standalone:** `iftm/index.html` → `/iftm/`; `404.html`

**Assets:** favicons, `og-image.png`, `robots.txt`, `sitemap.xml`,
`ScanID-Checklist-RGPD.pdf`, `scanid-presentation.mp4`.
**Never published:** `.htaccess`.

---

## 5. STAGES — v5

| # | Stage | Status |
| --- | --- | --- |
| 0 | Parse the repository; map v5 against v4 file by file | **DONE** |
| 1 | Write constraints, demand, change log and plan into this file | **DONE** |
| 2 | Pre-flight: replay the assembler against v5 in memory | **DONE** |
| 3 | Repoint `assemble-site.mjs` at v5; assemble `dist/` (site half only) | **DONE** |
| 4 | Verify `dist/` against v5 (parity, app untouched, guards, links, HTTP, rendering) | **DONE** |
| 5 | Record residual gaps and deployment steps; hand back | **DONE** |

**The v5 task is complete locally.** `frontend/dist/` holds the v5 site as the front door and
the unchanged application at `/app/`. Nothing is deployed, nothing is committed. What
remains is in §6 (defects in the source, not demanded) and §7 (how to ship it).

### Stage 0 — Survey — DONE

Findings are §2 in full. The facts that drive the build:
- 22 pages in v5, same count as v4; `calculateur.html` out, `contact.html` in.
- Inline `<script>` in v5: `checklist.html`, `essai.html`, and **new** `index.html`.
  (`calculateur.html`'s script disappears with the page.)
- `/api/` endpoints v5 calls: `POST /api/trial-requests` (essai, as in v4) and
  **new** `GET /api/config` (index). **Neither exists in `backend/`.** Both scripts
  degrade gracefully — see §6.
- Only one functional reference to the source directory exists (§3).

### Stage 1 — This file — DONE

### Stage 2 — Pre-flight — DONE

Every rewrite and every refusal check of `assemble-site.mjs` replayed against
`scanid-site-v5-deploy/`, in memory, writing nothing:

```
22 pages, 8 assets, 3 scripts externalised
  0 × Connexion → /app/          (v5 already uses /app/)
 22 × Google Fonts → self-hosted
 44 × preconnect removed
PRE-FLIGHT PASSED — 22/22 ok, 0 failures
```

Scripts will become `/scripts/checklist-1.js`, `/scripts/essai-1.js`, `/scripts/index-1.js`.
`contact.html` rewrites cleanly. `.htaccess` skipped.

### Stage 3 — Repoint and assemble — DONE

**The one code change** — `frontend/scripts/assemble-site.mjs`, the `SITE` constant:

```diff
-const SITE = join(FRONTEND, 'site');
+// The site's source of truth. Since v5 it is scanid-site-v5-deploy/, which
+// replaces the content of site/; site/ (v4) stays in the repository untouched
+// and read-only, and nothing reads it any more. …
+const SITE = join(FRONTEND, 'scanid-site-v5-deploy');
```

Nothing else in the script, the pipeline, nginx, CSP or the workflows was changed.

**Assembled**, from `frontend/`, with `node scripts/assemble-site.mjs` (not `vite build` —
the application source did not change; app half SHA-256 baseline before the run:
`1ef1661c60e2431b…`, 91 files):

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

Effect on `dist/`: `calculateur.html` and `scripts/calculateur-1.js` gone (cleared as
stale); `contact.html` and `scripts/index-1.js` added; every other page rebuilt from v5.

### Stage 4 — Verify — DONE

Every check passed except where marked as a **defect of the v5 source** (reported, not fixed).

**Application preserved.** SHA-256 over the 91 files of `dist/app/`, before and after:
`1ef1661c60e2431b…` → identical.

**Build is exactly v5.**

| Check | Result |
| --- | --- |
| Byte parity: each `dist/` page = v5 page + the assembler's transformations, nothing else | **22 / 22** |
| Externalised scripts byte-identical to the inline code (`index-1`, `essai-1`, `checklist-1`) | **3 / 3** |
| Page set `dist/` vs v5 | identical, 22 pages |
| 8 assets (images, PDF, video, robots, sitemap) | byte-identical to v5 |
| `calculateur.html`, `scripts/calculateur-1.js` | gone from `dist/` (HTTP 404) |
| `.htaccess` | withheld (HTTP 404) |
| Google Fonts / `app.scanid.fr` / inline `<script>` left in the site half | none |
| Broken internal links in the built site half | none |
| Build guards `node --test tests/build/no-google-fonts.test.js` | **5 pass, 0 fail** |

**HTTP smoke test** (`dist/` on a throwaway local server, stopped afterwards): all 22 pages,
`/iftm/`, `/app/`, `/fonts/site.css`, the three scripts, `sitemap.xml`, `robots.txt` → 200.

**Rendering** (Chromium, 1440×900 and 390×844):

| Element | Measured | Verdict |
| --- | --- | --- |
| Navigation | Présentation · Ressources · Tarifs · FAQ · Contact · Connexion | as v5 |
| Trial bar | present under the nav, 1392×30 px at 1440; 342×43 px on mobile; text as §2.2 | as v5 |
| Self-hosted fonts | 6 faces loaded | correct |
| `contact.html` | renders; « Contact » shown active; email, telephone, ScanID SASU Paris address, form | as v5 |
| `ressources.html` | checklist feature box at top, article cards below | as v5 |
| « Commencer » (correctly marked up) | `display:block`, padding 12.8px, 1px solid border | styled button |
| **4 × « Souscrire »** | `className:"js-buy"` only, `display:inline`, padding 0, no border, transparent background — **small default-blue link text, barely visible on the dark card** | **defect of the v5 source, §2.4 — confirmed visually** |
| Mobile width | page 929 px wide on a 390 px screen, offender `div.ft-links` | **pre-existing, worse in v5** (857 px in v4) — §6 |
| Console | one error per home-page load: `GET /api/config` → 404 | expected, §6 |

**Repository state after Stages 3–4:** modified `frontend/scripts/assemble-site.mjs` and
this file; untracked `frontend/scanid-site-v5-deploy/`, `site.html`, `site1.html`; nothing
staged; `frontend/site/` identical to `HEAD` (committed v4). `dist/` is gitignored.

### Stage 5 — Gaps and deployment — DONE

Recorded in §6 (updated with the Stage 4 measurements) and §7 (v5 deployment steps).

---

## 6. KNOWN ISSUES — NOT DEMANDED, THEREFORE NOT ACTED ON

1. **Duplicate `class` on the four « Souscrire » buttons** (v5 source) — §2.4.
2. **`GET /api/config` does not exist** (new in v5). The home-page script treats a failed
   fetch as "signup not ready", so « Souscrire » keeps going to Stripe. The
   `/app/inscription?pack=` path is therefore dormant until the backend provides that
   endpoint. Side effect: **every home-page load logs a 404 in the browser console.**
3. **`POST /api/trial-requests` does not exist** (since v4). The trial form falls back to
   Formspree, so leads arrive by email; nothing is stored and the inline success message
   never shows. v5's new SIRET / TVA fields travel the same way.
4. **`/calculateur.html` is live today and disappears with v5.** Once deployed it answers
   404. Bookmarks and search-engine results pointing at it break unless a redirect is
   added (nginx) — a decision for the user.
5. **Mobile footer overflow — worse in v5.** `footer > .ft-links` does not wrap. On a 390px
   phone the page was 857px wide in v4 (and in the version before it); in v5, which adds a
   « Contact » footer link, it is **929px**. Phones shrink the page or cut the footer
   links off. Fix belongs in the source (e.g. `flex-wrap:wrap` on `.ft-links`).

---

## 7. HOW THIS REACHES THE LIVE SITE

**`frontend/dist/` is not what gets deployed.** It is gitignored. `.github/workflows/deploy.yml`
runs on push to `master`: `npm ci && npm run build` on the GitHub runner, from the
**checked-out** source, then `rsync -az --delete frontend/dist/` to the VPS. The local
`dist/` is a verified preview of what the runner will build.

State of the server as last verified (2026-09-12): v4 live on all 22 pages, nginx
configuration current (site CSP with Formspree live, unknown path → 404). No manual nginx
reload was needed for v4, and v5 needs none either — it adds no origin and no route.

### To ship v5 (for the user — not done here, add/commit/push are forbidden)

The runner builds from the committed source, so **both** of these must be committed
together:

1. `frontend/scanid-site-v5-deploy/` — currently **untracked**. Without it the runner's
   build stops with `assemble-site: scanid-site-v5-deploy does not exist`, and the deploy
   fails before touching the server (the live site stays on v4).
2. `frontend/scripts/assemble-site.mjs` — the repointed `SITE` constant. Without it the
   runner builds v4 from `frontend/site/` again and visitors see no change.

```
git add .
git commit -m "..."
git push
```

**`git add .` is safe** (2026-09-13): the root `.gitignore` now ignores the comparison files
`/site.html` and `/site[0-9]*.html`. A dry run stages exactly 34 files — `.gitignore`,
`SCANID-HANDOVER.md`, `frontend/scripts/assemble-site.mjs` and the 31 files of
`frontend/scanid-site-v5-deploy/` — and nothing else. The v5 folder was scanned before
being cleared for commit: no credential patterns, no file over 1 MB, and its two embedded
images are the same illustrations already committed in `frontend/site/`.

**Decide before shipping:** §2.4 (the four unstyled « Souscrire » buttons — the most
visible purchase call to action) and §6 item 4 (`/calculateur.html` turns into a 404).

After the push, the deploy workflow's own probes apply unchanged: `href="/app/"` is on
the v5 home page (2 occurrences) and `/fonts/site.css` is built, so they pass.

---

### v5 IS LIVE — verified 2026-09-13

The user committed and pushed `4ae4926` ("Deploy the presentation of v5"); `master` is in
sync with `origin/master`. Verified against https://scanid.fr:

- **22 / 22 live pages are byte-exact against the v5 build** (20 differ from v4; `404.html`
  and `iftm/index.html` are identical in both versions). Still v4: **0**.
- `/calculateur.html` and `/scripts/calculateur-1.js` → **404**; `/contact.html` and
  `/scripts/index-1.js` → 200; `/app/` → 200; unknown path → 404; site CSP unchanged.
- Rendered (Chromium): six-item nav, trial bar under it (1392×30 px desktop, 342×43 px
  mobile), 6 font faces loaded.
- **The §2.4 defect is live:** the four « Souscrire » buttons render as `display:inline`,
  no padding, no border — small dark-blue link text on the dark pricing cards — next to a
  correctly styled « Commencer » button.
- Also live, as predicted in §6: `GET /api/config` → 404 logged in the console on every
  home-page load; mobile page 929 px wide on a 390 px screen (`div.ft-links`).

---

## 8. HISTORY — THE v4 TASK (2026-09-12), COMPLETE

Recorded accurately so it is not re-litigated:

- **No new code was written for v4.** The front-door pipeline had been built and committed
  on 2026-09-09 (commit `c2cdd23`). The v4 pages had been placed in `frontend/site/` by
  the user; `dist/` had simply not been rebuilt since. The v4 work was: survey → in-memory
  pre-flight → `node scripts/assemble-site.mjs` (site half only; `dist/app/` SHA-256
  unchanged) → verification.
- Verification: 22/22 pages byte-exact against the transformed source; body markup, CSS,
  text and SVG identical; fonts matched face for face; 5/5 build guards pass.
- One visual difference attributable to the build, not the source: pages whose Google
  Fonts URL omitted the italic face now render true Inter Italic (the shared stylesheet
  carries it) instead of a browser-synthesised slant.
- The user then committed and pushed (`f9290cd`); the live site was verified byte-exact
  against the v4 build on all 22 pages, and pixel-identical on the home page (0 / 1,296,000
  pixels differing with animations frozen).
- Also added on user demand: `frontend/.gitignore` rule `site[0-9]*/` (ignores
  `site1/`; verified `site/` stays tracked), and the comparison files `site.html` /
  `site1.html` at the repository root.

---

## 9. RULES FOR WHOEVER CONTINUES

- Obey §0 before anything else.
- Never write into `frontend/site/` or into `frontend/scanid-site-v5-deploy/`. Every
  transformation happens on the copy, in memory, on its way to `dist/`.
- Run the assembler alone (`node scripts/assemble-site.mjs`), not a bare `vite build` —
  the application source has not changed, and rebuilding it would re-hash it for nothing.
- If the assembler exits non-zero, it is refusing to ship a broken page: teach it the new
  markup shape; do not weaken its checks; do not edit the source.
- Do not fix defects in the source of truth (§2.4, §6) unless the user asks.

# ScanID — package handover notes

The package briefs themselves live outside the repository (`~/Downloads/SCANID-*.md`).
This file, inside the repository, collects the handover note each package is asked
to produce, so the next session finds it next to the code it describes.

---

## Handover — Package 0 — Test harness

- **Branch:** `chore/test-harness`
- **Date:** 2026-09-05
- **Scope:** test infrastructure only. **No application file was modified** —
  `frontend/src/App.jsx` is byte-identical to `master`, and no backend file was
  touched.

### Test suites and their status

| Suite | Command | Result |
|---|---|---|
| Unit (`node --test`) | `npm test` | **25 passed, 0 failed** — 7 pre-existing (`resultsHelpers`), 8 new fixture checks, 10 new contrast checks |
| E2E, mocked API, 3 projects × 10 specs | `npm run test:e2e` | **30 passed, 0 failed** (from a clean checkout state: fixtures regenerated, Vite cache cold) |
| E2E, live backend, desktop | `E2E_MODE=live … --workers=1` | **10 passed, 0 failed** against the real FastAPI app, real login, real Google Vision call |

### What was added

```
frontend/playwright.config.js         3 projects: desktop 1280×800, mobile-small 360×640,
                                      mobile-375 375×667 WebKit DPR 2. Trace/video/screenshot
                                      on failure. Manages the Vite dev server.
frontend/tests/
  README.md                           How to run, env vars, every fixture's purpose, and a
                                      blunt "what these tests cannot cover" section.
  global-setup.js                     Generates fixtures; warms the dev server.
  e2e/smoke.spec.js                   The regression baseline (6 specs).
  e2e/helpers.spec.js                 Proves the helpers themselves work in a browser (4 specs).
  e2e/test-base.js                    `test` extended with the mocked API (auto fixture).
  helpers/                            login, uploadFiles, waitForProcessing, getStorageState,
                                      measureTapTargets, contrastRatio, getComputedColorPair,
                                      layout/overflow helpers, SELECTORS + TEXT.
  fixtures/                           Manifest + deterministic generator + independent verifier.
  mock/                               A stand-in for backend/main.py, plus a real .xlsx writer.
  live/serve.py                       The real app on throwaway SQLite, for E2E_MODE=live.
  scripts/                            WebKit's missing system libraries, vendored without root.
```

Modified, all additive: `package.json` (scripts + 2 devDependencies),
`.gitignore` (generated artefacts), `eslint.config.js` (Node globals scoped to
`tests/`), `package-lock.json`.

### Decisions the next package must know

1. **`npm test` is deliberately browser-free** (it runs `test:unit`). CI's frontend
   job runs `npm test` on a runner with no browsers; making it launch Playwright
   would turn CI red. E2E is `npm run test:e2e`.
2. **The API is mocked by default** (`tests/mock/api.js`) because no staging
   backend exists and every upload costs a Google Vision call. The mock mirrors
   `backend/main.py` — **when the API changes, that file must change with it.**
   An unmocked path returns HTTP 501 with a message, so a hole fails loudly.
3. **A live backend now exists**: `tests/live/serve.py` runs the real FastAPI app
   on a throwaway SQLite file by rebinding `database.engine`/`SessionLocal`
   before `main.py` imports them — the same trick `backend/tests/conftest.py`
   uses. No app file is modified. Package C will want this.
4. **The app has no test ids**, and its `<label>`s are not associated with their
   inputs, so `getByLabel` does not work. Everything goes through
   `tests/helpers/selectors.js`, which leans on French placeholder/button text
   and class names. Add test ids and that one file changes; the suites follow.
5. **Fixtures are generated, not committed** (~20 MB, deterministic).
   `npm run test:fixtures` rebuilds them. **Never** use a real client document.
6. **`POST /token` is rate limited to 5/minute per IP.** `login()` waits the
   window out and retries. Live suites need `--workers=1` and are slow because of it.
7. **WebKit needs `libavif.so.16`**, absent on Ubuntu 24.04 and not fixable via
   `LD_LIBRARY_PATH` (Playwright's launcher overwrites it). `pretest:e2e`
   vendors it into `tests/.browser-libs/` without root and `LD_PRELOAD`s it.
8. **Workers are capped at 4 locally.** Eight browsers against one Vite dev
   server starved requests and produced one flake unrelated to the app; the
   cap plus the global-setup warm-up removed it (verified over repeated cold runs).
9. **The results table is the *last* `.table-container`** — the export preview
   renders its own table above it. Use `resultsRows(page)`, not a raw selector.

### Findings — application issues observed, deliberately not fixed

None of these were touched; they are reported as the brief requires.

1. **No upload size limit anywhere.** The upload card announces "PNG, JPG ou PDF
   jusqu'à 10Mo", but neither the front end nor
   `POST /passports/upload-and-extract/` checks the size. The `oversized.jpg`
   fixture is ready for whoever adds the check.
2. **No file-type validation except on drag-and-drop.** The picker's `accept`
   attribute filters the dialog but validates nothing, and the server accepts any
   `content_type`. `disallowed.txt` is ready.
3. **`npm run lint` fails on 7 pre-existing errors in `src/App.jsx`**
   (unused `err`/`error`/`e` catch bindings at lines 494, 550, 603, 944, 1229,
   1249, 1411). Pre-existing — CI does not run lint, so they were never surfaced.
   The test harness itself is lint-clean.
4. **The 5/minute login throttle is per IP, not per account.** An agency behind
   one NAT gateway shares that budget; six staff logging in at 09:00 will lock
   each other out. Worth a look in Package C.
5. **`backend/.env` holds a live GCP service-account private key in plaintext.**
   It is gitignored, so not in history. Flagged only.

### Anything unresolved

- **The handover note could not be appended to `SCANID-1-TEST-HARNESS.md`**: that
  file is at `~/Downloads/`, outside the repository, and this session was
  instructed not to write outside the project folder. This file is the substitute;
  copy the section above into the brief if you want them together.
- **Nothing is committed.** The branch `chore/test-harness` holds the work in the
  working tree, awaiting review.

### Handed to a human

- Real HEIC from an iPhone; real 4G timing; OCR accuracy against genuine
  specimen documents; iOS Safari behaviour (Playwright's WebKit is an
  approximation). See the "What these tests cannot cover" section of
  `frontend/tests/README.md` for the full list and the reasoning.

---

## Handover — Package A — Design system

- **Branch:** `feat/design-system` (branched from `chore/test-harness`, whose work
  is now committed as `cad92d2` — Package 0 was uncommitted when this session
  started, and `git status` had to be clean before branching).
- **Date:** 2026-09-06
- **Scope:** `frontend/` only. No backend file, service worker, `manifest.json`,
  nginx config or anything under `ops/` was touched. Upload / compression / HEIC
  logic is unchanged.

### Test suites and their status

| Suite | Command | Result |
|---|---|---|
| Unit (`node --test`) | `npm test` | **30 passed, 0 failed** (25 from Package 0 + 2 for `resultCellValue` + 3 for the build output) |
| E2E, mocked API, 3 projects | `npm run test:e2e` | **192 passed, 0 failed** (was 30; 64 specs × 3 browsers) |
| Build | `npm run build` | clean; no `googleapis`/`gstatic` string anywhere in `dist/` |
| Lint | `npm run lint` | the **same 7 pre-existing** errors Package 0 reported. No new ones. |

The regression baseline (`smoke.spec.js`) is green unchanged in substance: the
only edit was replacing `filter.selectOption('PASS')` with `selectDocType()`,
because the Tous/PASS/PI control is now a `.sid-seg` button group. **No
assertion was altered.**

### What changed

```
frontend/src/main.jsx            Fontsource imports (real 5.x paths: <pkg>/<weight>.css)
                                 then scanid-app.css, imported once and globally.
frontend/src/scanid-app.css      v1.0 -> v1.1. Google Fonts @import removed;
                                 4a-4e fixed; 3 further contrast defects fixed;
                                 mobile card-list rules added.
frontend/src/CHANGELOG-css.md    NEW. Every deviation from v1.0 with its reason
                                 and its measured contrast ratio.
frontend/src/App.jsx             GlobalStyles cut 350 -> 125 lines (only what the
                                 design system does not cover survives, retinted to
                                 sid tokens); every component mapped to .sid-* classes;
                                 mobile card list added beside the table.
frontend/src/resultsHelpers.js   NEW resultCellValue() — the single function both
                                 results views render through.
frontend/tests/helpers/          selectors.js remapped to .sid-*; resultsRows() now
                                 follows whichever view CSS is showing; selectDocType()
                                 added; NEW spreadsheet.js (dependency-free xlsx/csv reader).
frontend/tests/e2e/              NEW fonts / a11y / responsive / design-system specs.
frontend/tests/build/            NEW no-google-fonts.test.js (scans the shipped bundle).
```

### Decisions the next package must know

1. **The results table and the mobile cards render from one source.**
   `PASSPORT_COLUMN_ORDER` (already shared) decides the columns; the new
   `resultCellValue(item, field, fieldTypes)` in `resultsHelpers.js` decides every
   cell's text. **Add a column in one place and both views follow.** The parity
   spec in `responsive.spec.js` asserts deep equality field-by-field and will go
   red the moment they diverge.
2. **Both views are always mounted**; only CSS switches them at 720 px. No JS
   breakpoint listener, so a resize or rotation loses no state — there is a spec
   for exactly that.
3. **Table cells and card values carry `data-field="<column>"`.** That is the
   only test hook added to the app; the suites read both views through it.
4. **`resultsRows(page)` returns the rows *on screen*** — table rows above 720 px,
   cards below. Anything asserting on "the rows" keeps working at every viewport.
5. **The credits counter moved from the dashboard sidebar into the top bar**
   (`.sid-credits`), as the brief specifies. « Pages Traitées » stayed in the
   sidebar. `SELECTORS.creditBadge` is now `.sid-credits`.
6. **The `<h1>` is now the ScanID wordmark.** « Gestionnaire de Voyages » is not
   lost — it still reads in the login footer's copyright line.
7. **`.sid-chip--queued` has no data behind it.** The backend only ever writes
   `processing` / `complete` / `failed` (`backend/crud.py`), and inventing a
   status was forbidden, so three chips are data-driven and the fourth is
   CSS-only. Its contrast is still measured, on a probe element, and the spec
   says so in a comment.
8. **`.sid-table-wrap` is used by the export preview too.** The mobile hide rule
   is therefore scoped to `.sid-results`; an unscoped rule would delete the
   preview on every phone. Keep that scoping if you touch the breakpoint.
9. **The stylesheet's own defect list was longer than the brief's.** Four were
   named (4a-4e); three more were found by measuring: `.sid-badge--pi` at 3.53:1,
   `--sid-muted-strong` failing on two of the four tinted backgrounds it was
   assigned to, and `.sid-btn-ghost` at 4.04:1 on the navy bar. All are in
   `CHANGELOG-css.md` with numbers.
10. **One instruction was deliberately not followed to the letter:**
    `.sid-seg button` is `min-height: 44px`, not the `38px` the brief asked for.
    A parent's 3 px padding is not part of a child's hit area, so 38 px would
    have left a 38 px tap target — and the brief's own Step 7 test asserts
    ≥ 44 px on that very selector. The control is 50 px tall instead of 44;
    nothing else about it changed. Reasoning is in `CHANGELOG-css.md §4a`.

### Verified by tests I ran

Measured contrast, every value from the rendered page (`a11y.spec.js` prints
this table on every run):

| element | ratio | size | weight | AA | verdict |
|---|---|---|---|---|---|
| `.sid-dropzone small` | 4.99:1 | 12.5px | 400 | 4.5 | PASS |
| `.sid-topbar-right` | 6.46:1 | 13.6px | 400 | 4.5 | PASS |
| `.sid-credits` | 4.97:1 | 13.12px | 600 | 4.5 | PASS |
| `.sid-table th` | 18.11:1 | 11.84px | 600 | 4.5 | PASS |
| `.sid-badge--pp` | 18.11:1 | 11.52px | 700 | 4.5 | PASS |
| `.sid-badge--pi` | 5.12:1 | 11.52px | 700 | 4.5 | PASS |
| `.sid-chip--queued` (probe) | 4.91:1 | 12.48px | 600 | 4.5 | PASS |
| `.sid-chip--processing` | 5.17:1 | 12.48px | 600 | 4.5 | PASS |
| `.sid-chip--done` | 4.90:1 | 12.48px | 600 | 4.5 | PASS |
| `.sid-chip--failed` | 5.60:1 | 12.48px | 600 | 4.5 | PASS |
| `.sid-empty` | 5.51:1 | 13.76px | 400 | 4.5 | PASS |
| `.sid-appfoot` | 4.98:1 | 12.48px | 400 | 4.5 | PASS |
| `.sid-appfoot a` | 4.98:1 | 12.48px | 400 | 4.5 | PASS |

Also proven by a run, not by inspection: both font families load and resolve
(`h1` → Space Grotesk, `p` → Inter); a full session makes zero requests to
googleapis/gstatic and every `.woff2` comes from this origin; the bundle contains
neither string; every design-system button is ≥ 44 px tall at 360 and 375 px;
every text input computes ≥ 16 px; no horizontal overflow on login, upload or
results at 360/375; the card list shows at 719 px and the table at 721 px with
both still mounted; table and card values are deep-equal per field after an
upload; cells and card values are uppercase and cells centred; PASS → `--pp`,
PI → `--pi`, each job status → its chip; both downloads parse with the
pre-refactor column set and order and accents intact; no English word from the
list is visible; every tab stop on login and upload shows a focus ring.

### Functionality preservation — how it was checked

Asked directly whether everything else still works, I verified it three ways
rather than asserting it.

**1. Mechanical diff of the logic.** With the `<style>` block stripped and every
`className`/`style` value normalised away, `App.jsx`'s JavaScript differs from
`master` in exactly these places, and nowhere else:

- the `resultsHelpers.js` import list;
- the top bar's markup (logo + credits) and the sidebar losing the credits span;
- `<select>` → `.sid-seg` buttons for the type filter;
- the inline cell computation replaced by the identical `resultCellValue()` call;
- the added card list, `rowActions()`, and the two `JOB_STATUS_*` maps.

Compared as sets: **every `useState`/`useEffect`/`useCallback`/`useMemo`/`useRef`
call is identical**, **every function declaration is identical**, **every
`fetch()` call site — endpoint, method, URL — is identical**, and every event
handler binding is identical except the one filter gesture above. No API
contract, request shape, state transition, credit path or export query changed.

**2. A new suite for everything the tests never covered** —
`tests/e2e/features.spec.js`, 26 specs: single and multi-column sorting
(including that dates sort on the stored ISO value, not the displayed
DD/MM/YYYY), select-all, per-row selection, selection cleared by a filter
change, bulk destination edit, multi-delete with its confirm dialog, manual
creation via « + Manuel », edit + save, cancel writing nothing, job deletion,
the per-page failure list, upload cancel, the export preview, selection
exports, the type filter propagating into the export query, the password
toggle, self-registration including the server's French conflict message,
« Mon Compte » pre-fill and save, tab navigation, logout clearing the token,
and the destination datalist.

**3. Two defects it found — both in the harness, not the app.**

- **`POST /users/register` was mocked below the authorisation gate**, so
  registration answered 401. Moved above it, where the real endpoint is
  (`main.py:614` has no auth dependency).
- **`PUT /users/me` applied nothing.** The mock matched `/users/me` for any
  method and always returned the untouched user, so every account edit
  "succeeded" without being checked. It now writes the payload and, like
  `main.py`, refuses to let a non-admin move its own counters.

`POST /passports/` had no mock at all, so manual creation was unreachable in
tests; it is mocked now too. **No application defect was found.**

### One real behaviour change on small screens

Sorting and « tout sélectionner » live in the **table header**, which the design
system replaces with the card list below 720 px. Before Package A the table was
shown at every width (scrolling sideways), so both were reachable on a phone.
**They are not any more.** This follows directly from settled decision #1
(stacked cards on mobile), so it is not a bug to fix here, but it *is* a
capability the phone used to have.

Per-row selection, « Modifier », bulk destination edit and multi-delete all do
work from the cards — there are specs for each. There is also a spec asserting
the two missing controls are absent, so a later package that adds them has a
test to flip rather than a silent gap. **Package B should decide** whether the
card view needs a sort control and a select-all.

### Cannot be automated

- **That the rendered result visually matches scanid.fr.** No reference to diff
  against. I checked screenshots at 1280 px and 375 px and they are coherent, but
  "matches the marketing site" is a human judgement.
- **Real iOS Safari zoom.** Playwright's WebKit approximates Safari; the 16 px
  rule is asserted on computed styles, which is the cause, not the effect. Needs
  a physical iPhone.
- **Subjective layout quality on a real device** — thumb reach, scroll feel,
  whether the 9-row cards are too long in practice.
- **`backdrop-filter: blur(14px)`** on the top bar renders differently per
  browser and is not asserted anywhere.
- **Print / high-contrast / forced-colors modes** were not considered.

### Anything unresolved

- **Nothing is committed on this branch.** `feat/design-system` holds the work in
  the working tree, awaiting review. Package 0 *was* committed (`cad92d2`) so this
  branch had a clean base — that is the one thing this session changed about the
  repository's history.
- **`npm run lint` still fails on the same 7 pre-existing errors** in `App.jsx`
  (unused `err`/`error`/`e` catch bindings). Untouched: out of scope, and already
  reported by Package 0.

### Findings — observed, deliberately not fixed

1. **`index.html` still says `<html lang="en">` and `<title>Vite + React</title>`**
   for a wholly French app. `lang` is a real accessibility defect (screen readers
   pick the wrong voice). Out of this package's scope — the brief limits
   `index.html` work to removing Google Fonts, and there was none to remove.
   Probably Package B, alongside `manifest.json`.
2. **`ProgressBar` renders « 12% - Upload »** — the one English word left in the
   UI. It predates this package and the brief forbids rewording existing strings,
   so the French-UI spec excludes `.progress-text` by selector (narrowly, and it
   says why). Someone should decide whether it becomes « Envoi ».
3. **`src/App.css` is dead** — Vite boilerplate, imported by nothing. Left alone
   under scope discipline.
4. **`GlobalStyles` is still an inline `<style>` in `App.jsx`.** It is now 125
   lines of genuinely app-specific layout, but it re-renders with the component
   and belongs in a `.css` file. Not moved: outside this package.
5. Package 0's findings (no upload size limit, no file-type validation server
   side, per-IP login throttle, plaintext key in `backend/.env`) all still stand.

### Handed to a human

Everything under "Cannot be automated" above, plus Package 0's list in
`frontend/tests/README.md`. See `SCANID-HUMAN-ONLY.md` for the full checklist.

---

## Handover — Package B — Mobile capture & PWA

- **Branch:** `feat/mobile-pwa` (branched from `feat/design-system`, whose work is
  now committed as `05c40e8` — Package A was uncommitted when this session
  started, and `git status` had to be clean before branching. Same situation, and
  same resolution, as Package A faced with Package 0.)
- **Date:** 2026-09-06
- **Scope:** `frontend/` only. No backend file, no `deploy/`, no nginx config, no
  `ops/`. `src/scanid-app.css` is **byte-identical** to Package A's.

### Test suites and their status

| Suite | Command | Result |
|---|---|---|
| Unit (`node --test`) | `npm test` | **67 passed, 0 failed** (30 from Package A + 37 new: 21 `fileSniff`, 16 `uploadQueue`) |
| E2E, 4 projects | `npm run test:e2e` | **310 passed, 1 skipped, 0 failed** (was 192 over 3 projects) |
| Build | `npm run build` | clean; precache 48 entries / 771 KiB |
| Lint | `npm run lint` | the **same 7 pre-existing** errors in `App.jsx`. No new ones. |

The one skip is deliberate and named in the spec — see "Cannot be automated" #1.

**Re-verified after the fact.** Every row above was re-run from the working tree
in a separate pass and reproduced exactly: 67/67 unit, 310 passed + 1 skipped
over the four projects (2.7 min, exit 0), the same 48-entry / 771.45 KiB
precache, the same 7 lint errors. The compression, EXIF-band and storage figures
quoted further down were re-measured in that pass and matched to the byte and to
the decimal; only the retry delays differ run to run, and that is jitter, not
behaviour (see the queue paragraph). Four independent audits were run alongside
the suites, none of which depend on the suites being honest:

- **Every `fetch` / `xhr.open` call site is byte-identical to Package A's**, as
  is the multipart field set, and the top-level declaration list differs only by
  three additions (`formatBytes`, `PHOTO_GUIDE_URL`, `UPLOAD_ACCEPT`) — nothing
  removed, nothing renamed. That is the functionality-preservation claim checked
  mechanically rather than asserted.
- **`src/scanid-app.css` is byte-identical to `05c40e8`** (`git diff --quiet`),
  and `index.html` differs by exactly the two permitted lines.
- **The built `dist/sw.js` registers one route** — the shell NavigationRoute with
  `denylist:[/^\/api\//,/^\/events/]` — and its precache manifest is 48 URLs:
  40 `woff2`, 3 `png`, 1 each of `webmanifest`, `svg`, `js`, `html`, `css`. No
  endpoint, and no `heic2any`.
- **The only storage write in the whole of `src/` is `localStorage['token']`**
  (four call sites in `App.jsx`, all auth). Grepping every storage API across
  `src/` returns nothing else.

### What changed

```
frontend/vite.config.js          VitePWA (generateSW). ALLOW-LIST precache,
                                 runtimeCaching: [] — nothing may grow a strategy
                                 that matches an upload by pattern.
frontend/index.html              +2 lines: theme-color meta, apple-touch-icon.
                                 The manifest <link> is injected by the plugin.
frontend/public/icons/*.png      NEW. 192, 512, 512-maskable.
frontend/scripts/generate-icons.mjs  NEW. Rasterises them with Playwright's
                                 Chromium (already a devDependency). `npm run icons`.
frontend/src/upload/fileSniff.js     NEW, pure/browser-free: magic bytes, EXIF
                                 orientation, EXIF stripping, SOF dimensions,
                                 orientation transforms, resize arithmetic.
frontend/src/upload/imagePrep.js     NEW, browser-only: HEIC→JPEG, downscale,
                                 rotate. Never drops a file.
frontend/src/upload/uploadQueue.js   NEW, framework-free: the batch queue.
frontend/src/pwa.js              NEW: SW registration + update-on-idle, and the
                                 online/offline signal.
frontend/src/OfflineScreen.jsx   NEW: the French « hors ligne » overlay.
frontend/src/mobile-pwa.css      NEW, ~120 lines. Justified in its own header.
frontend/src/main.jsx            +2 imports (mobile-pwa.css, registerServiceWorker).
frontend/src/App.jsx             Uploader: multiple + camera + guide link + queue.
                                 handleUpload: resolves/rejects instead of alerting.
                                 fetchUser: network failure ≠ expired session.
                                 Object URLs registered and revoked.
                                 OcrJobMonitor publishes {jobId: status}.
frontend/playwright.config.js    4th project `pwa` + a second webServer (build+preview).
frontend/eslint.config.js        Node globals extended to src/**/*.test.js, scripts/.
frontend/tests/                  helpers/imagePrep.js NEW; selectors + uploadFiles
                                 extended; e2e/capture, e2e/queue, e2e/privacy,
                                 pwa/pwa.spec.js NEW; README updated.
```

### Decisions the next package must know

1. **`capture="environment"` is on a SECOND input, not the existing one.** The
   brief's snippet puts `capture` on the one file input. On a phone `capture`
   *replaces* the photo library with the camera — so a single input carrying it
   would have removed the ability to pick an existing file, a feature the app
   has today, and would have contradicted the brief's own "HEIC mainly appears
   from the library picker; both paths must work." The drop zone keeps the
   picker (`SELECTORS.fileInput`); a « Prendre une photo » button beside it owns
   the capture input (`SELECTORS.cameraInput`). Both carry `multiple` and the
   same `accept`.
2. **`accept` grew, it never shrank:** `image/png, image/jpeg, image/jpg,
   image/heic, image/heif, application/pdf`. PDFs are still accepted and are
   never compressed.
3. **The compression thresholds are stated, not implicit.** Long edge 2500 px,
   JPEG quality 0.85, and files **≤ 1 Mo that need no rotation are uploaded
   byte-for-byte** (`SKIP_BYTES` in `imagePrep.js`). A file that needs rotating
   is processed at any size — that is a correctness fix, not an optimisation.
4. **The stated compressed budget is WebKit's number, not Chromium's.** The same
   4 349 263-byte fixture at the same 2500×1666 comes out 1 122 349 bytes on
   Chromium and 1 259 009 on WebKit. The spec asserts < 1 400 000 so it holds on
   both. Do not tighten it to the Chromium figure.
5. **EXIF is handled per file, from ground truth, not from a browser sniff.**
   `readJpegDimensions()` reads the SOF segment for the size the file is *stored*
   at; if the decode comes back with those two the other way round, the browser
   applied the orientation and applying it again would rotate twice. Only when
   that comparison cannot decide (a square image, or orientations 2/3/4, which
   leave no dimensional trace) does a cached one-off probe answer.
6. **`createImageBitmap(blob, {imageOrientation: 'none'})` does not work any
   more** — the value was dropped from the specification and current Chromium
   ignores it, returning an oriented bitmap regardless. The explicit fallback is
   therefore entered by **stripping the APP1/Exif segment** (`stripExifSegments`)
   and rotating with our own transform. `prepareFileForUpload(file,
   {letBrowserOrient: false})` forces that path, and a spec asserts it produces
   pixel-identical output to the automatic one.
7. **`onUpload` is now a Promise.** `CrudManager.handleUpload(formData, file,
   onProgress)` resolves `{jobId}` on 2xx and rejects otherwise. A
   `RetriableUploadError` (transport failure or a stalled transfer) is retried
   twice with 1 s then 3 s of backoff; **an HTTP answer is never retried** —
   « Crédits insuffisants » repeated three times would spend credits for nothing.
8. **Three `alert()` calls in the upload path are gone**, replaced by the per-
   document error line in the queue (same French text). With a batch of ten, one
   modal per failure per attempt was not usable. Nothing else about the upload
   changed: same endpoint, same multipart shape, same one-file-per-request.
9. **`OcrJobMonitor` dispatches `ocr-jobs-snapshot`** (a `{jobId: status}` map,
   ids and statuses only) after every poll. That is how a queue item reaches
   « Terminé » rather than stopping at « Traitement ». It uses the same window-
   event bus the SSE code already used, so `CrudManager` does not re-render every
   2 s. If you move the job monitor, keep that event.
10. **The service worker's config is an allow-list and `runtimeCaching` is
    empty.** The built worker registers exactly one route: a NavigationRoute for
    the shell, with `denylist: [/^\/api\//, /^\/events/]`. Adding a runtime
    caching strategy — any at all — is how this stops being true. The
    `heic2any` chunk (1.3 Mo) is excluded via `globIgnores` and fetched on demand.
11. **The PWA suite runs on a production build, on its own port.** Project `pwa`,
    `testDir: tests/pwa`, `baseURL: http://127.0.0.1:4173`, served by a second
    `webServer` entry running `npm run build && npm run preview`. The service
    worker, the manifest and the icons do not exist in dev, and `devOptions` is
    deliberately off.
12. **`page.waitForFunction` with an `async` callback is a trap** and cost real
    debugging time here: the callback returns a Promise, which is truthy, so the
    wait resolves on the first poll without ever reading the result. Every wait
    in `tests/pwa/` uses `expect.poll` instead. Do not "simplify" it back.
13. **The token is still in `localStorage`** — reported, not changed, exactly as
    the brief instructs. Moving it to an HttpOnly cookie is Package C.

### The one thing this package could not fix — Package C owns it

**`GET /events` carries the session token in its query string.**
`App.jsx` opens `new EventSource(\`${API_URL}/events?token=${token}\`)` because
`EventSource` cannot set headers, and `backend/main.py:570` declares
`token: str = Query(...)` — **mandatory server-side**. A front-end-only change to
a `fetch`-based SSE reader with an `Authorization` header would be rejected by
the current endpoint, and touching the backend is outside this package. This is
flagged rather than half-applied, as the "no orphaned work" rule requires.

`tests/e2e/privacy.spec.js` asserts the current, honest state: across a full
session **every** URL carrying the token is `/events`, and nothing else. When
Package C accepts the token from a header or a short-lived ticket, that spec's
`expect(leaking.length).toBeGreaterThan(0)` goes red and is deleted — the test is
written so the fix cannot pass unnoticed.

### Verified by tests I ran

Numbers below are printed by the suites themselves on every run, not quoted from
memory.

**Compression, measured end to end**

| | Chromium | WebKit |
|---|---|---|
| 4 349 263 B, 3200×2133 | → **1 122 349 B**, 2500×1666 | → **1 259 009 B**, 2500×1666 |
| multipart body actually POSTed | **1 122 542 B** | not measurable (see below) |
| `small.jpg` 59 544 B | untouched | untouched |
| `document.pdf` | untouched | untouched |
| `document.png` 339 038 B | untouched (under threshold) | untouched |

**EXIF orientation, proven on pixels and not on dimensions**

| Orientation | Output | Edge-strip luminance | Reading |
|---|---|---|---|
| 6 (90° CW) | 1600×1200 (portrait → landscape) | left **161.5**, right **220.0** | the MRZ band moved from the bottom to the **left**, as a 90° CW rotation requires |
| 3 (180°) | 1200×1600 — **unchanged** | top **161.6**, bottom **220.0** | the dimensions prove nothing here; the band moved bottom → **top** |
| 1 | untouched | — | nothing to rotate |
| 6, fallback forced | identical to row 1, `orientationSource: 'exif'` | | the stripped-EXIF path really ran |

**Queue, against the real XHR**: the configured backoff is `RETRY_DELAYS_MS =
[1000, 3000]`, and the spec asserts *strictly increasing*, not exact values,
because the observed delays carry scheduler jitter — **1064 ms then 3029 ms** on
the implementation run, **1029 ms then 3016 ms** on the verification re-run.
Three attempts either way; the item reached `failed` with
« Connexion interrompue pendant le téléchargement. » on a `.sid-chip--failed`.
In a mixed batch of three, `small.jpg` and `document.pdf` were sent **once each**
and finished, `document.png` was sent three times and failed; « Réessayer les
échecs » then sent **`['document.png']` and nothing else**. A 403
« Crédits insuffisants » was sent **once** and never retried.

**Storage after a full session** (10 uploads, results viewed, both exports
downloaded, on the built app with the worker running):
`localStorage=['token']`, `sessionStorage` empty, **0** IndexedDB databases,
**48** Cache Storage entries — every one matching
`\.(js|css|html|svg|woff2|png|webmanifest)$`, none containing `upload-and-extract`,
`/passports`, `/export`, `/ocr/jobs` or `/users/me`. Each cached response body
was then read and searched for all 18 identity strings the session displayed
(the five seeded names and numbers plus the extracted one): **no match**.

Also proven by a run: the picker accepts HEIC/HEIF and still accepts PNG/JPG/PDF,
and carries `multiple`; the camera input carries `capture="environment"` and the
picker does not; the guide link points at `https://scanid.fr/guide-photo.html`,
opens in a new tab and is `rel="noopener"`; a genuine iPhone `ftyp` box is
detected as HEIC while an AVIF sharing the `mif1` brand is not; a `.HEIC` file
that fails conversion is uploaded **as the original object**, byte count intact;
a JPEG named `.HEIC` is treated as a JPEG; the manifest is served as
`application/manifest+json` with every required field; all three icons return 200
and measure exactly what they declare; the worker precaches exactly the 48 shell
entries in `dist/sw.js` and nothing more; an upload plus a results read plus a
download add **zero** cache entries; a second visit still loads; offline, the
shell reloads from the worker while **no** result comes back; a network blip
keeps the session and the dashboard mounted; a 401 shows
« Votre session a expiré… »; every object URL created by an export or by image
preparation is revoked; the queue is empty after a reload; the upload control is
reachable with no navigation tap at 375 px; and neither the queue nor the offline
screen overflows horizontally at 360 px, with a ≥ 44 px retry button.

### Cannot be automated

1. **The size of a large multipart body on WebKit.** Playwright's WebKit does not
   report it — `postData()` returns 193 bytes for a 1.2 Mo upload,
   `postDataBuffer()` returns `null`, `sizes().requestBodySize` returns 0. The
   end-to-end "the compressed bytes are what is actually sent" assertion is
   therefore **skipped on `mobile-375`**, with that reason in the spec, rather
   than left to pass vacuously. Compression itself *is* proven there, in-page.
2. **A real HEIC from a physical iPhone photo library.** The suite proves the
   *detection* against a genuine `ftyp` box and proves the never-drop failure
   path. `heic2any` has never decoded a real iPhone HEIC in this repository.
3. **Real 4G timing, and the under-ten-second target.** Playwright cannot
   reproduce a cellular link. What is known is the payload: 4.3 Mo → 1.1 Mo.
4. **OCR accuracy on real documents after compression.** Whether Vision still
   reads a genuine MRZ at 2500 px and quality 0.85 needs specimen documents. The
   fixtures carry no readable MRZ by design.
5. **« Add to Home Screen » producing a standalone window**, and everything else
   about installation: Playwright never installs the PWA. The manifest is
   validated field by field and every icon fetched and measured — that is the
   limit of automation here.
6. **iOS Safari storage behaviour.** WebKit in Playwright is not Mobile Safari:
   different eviction rules, different PWA storage limits, no real Photos picker.
7. **Lighthouse PWA and performance scores.** No Lighthouse CI exists in this
   repository and setting one up was outside this package, so **no score is
   claimed**.
8. **The update-on-deploy path end to end.** `registerServiceWorker()` reloads on
   `controllerchange`, deferred while an upload is in flight. The deferral logic
   is small and readable but is not covered by a test: producing a genuine second
   deploy mid-upload inside a Playwright run was not something I could do
   honestly, and a mocked `controllerchange` would only test the mock.

### Findings — observed, deliberately not fixed

1. **`index.html` still says `<html lang="en">` and `<title>Vite + React</title>`.**
   The brief limits this file to the manifest link and the theme-color meta, so
   only those (plus the apple-touch-icon, part of the icon step) were touched.
   The manifest now declares `lang: "fr"` while the document says `en` — a real
   accessibility defect that is now also an inconsistency. It is two lines.
2. **The PWA icons carry Vite's logo.** There is no ScanID mark anywhere in the
   repository, `scanid.fr` answers 403 with no favicon, and inventing one was
   forbidden. Asked, the operator chose to use the existing `public/vite.svg`
   source as-is. `scripts/generate-icons.mjs` carries a note: drop a real logo in
   and rerun `npm run icons`. **This should not ship to production as is.**
3. **`ProgressBar` still renders « 12% - Upload »** — Package A's finding, still
   the one English word in the UI.
4. **The card view still has no sort control and no « tout sélectionner ».**
   Package A asked Package B to decide. This brief says « Do not touch the
   results table or card list. Finished. », so it was not touched. The decision
   is still open, and `features.spec.js` still has the spec that asserts their
   absence, ready to be flipped.
5. **No upload size limit anywhere**, still — Package 0's finding. The upload
   card now says « PNG, JPG, HEIC ou PDF jusqu'à 10Mo » and nothing enforces it.
   Client-side compression makes an oversized *photo* much less likely, but a
   large PDF still goes through untouched.
6. Package 0's other findings (server-side file-type validation, the per-IP login
   throttle, the plaintext key in `backend/.env`) all still stand.

### Anything unresolved

- **Nothing is committed on this branch.** `feat/mobile-pwa` holds the work in the
  working tree, awaiting review. Package A *was* committed (`05c40e8`) so this
  branch had a clean base — the one thing this session changed about history.
- **`npm run lint` still fails on the same 7 pre-existing errors** in `App.jsx`.
  Untouched: out of scope, and reported by both previous packages.

### Handed to a human

Everything under "Cannot be automated", plus finding #2 — **the icons must be
regenerated from a real ScanID logo before this reaches production**. See
`SCANID-HUMAN-ONLY.md` and the "What these tests cannot cover" section of
`frontend/tests/README.md`, which now lists the WebKit multipart limitation, the
install-time gap and the absent Lighthouse numbers.

---

## Handover — Package C — Backend hardening

- **Branch:** `feat/security-app-layer` (branched from `feat/mobile-pwa`, whose
  work is now committed as `f2b5139` — package B was uncommitted when this
  session started and `git status` had to be clean before branching. Third time
  the same situation, same resolution.)
- **Date:** 2026-09-06
- **Scope:** `backend/` plus the two narrow frontend changes this brief
  explicitly owns (the `HttpOnly` token migration and the registration-screen
  password rules). No `ssh`, no `systemctl`, no nginx, no `ufw`, no `certbot`,
  no deployment command, no migration run against any database, nothing under
  `ops/`. `frontend/src/scanid-app.css` is still byte-identical to package A's.

### THE STEP-1 AUDIT — read this first

**The claim "identity documents are never stored" was false as an absolute
statement.** It is now much closer to true, but it was never a lie about
intent — the code always tried to clean up after itself. Three places put
document bytes on disk, found by tracing the upload from the endpoint to the
Vision call and confirmed by reading the installed library source.

| # | Where | Are they real document bytes? | Deleted? |
|---|---|---|---|
| 1 | `main.py` `tempfile.mkstemp(prefix="ocr_upload_")` — the endpoint spools the upload to a **named** file so the bytes are not pinned in RAM for the whole job | **Yes** — the entire document, byte for byte, 0600, for the whole OCR run (tens of seconds, minutes for a large PDF) | In a `finally`, but **four exits missed it** |
| 2 | `starlette/formparsers.py:125`, `max_file_size = 1024 * 1024` — Starlette spools any multipart part over **1 MB** to a `SpooledTemporaryFile` *before the endpoint function is entered* | **Yes** — so a scanned passport was already on disk before the code above wrote it a second time | Yes, reliably: `O_TMPFILE`, an anonymous inode with no directory entry, released on close or process death |
| 3 | `ocr_service.py` logged **the complete OCR text of every page** at INFO, then the fully parsed record on the next line | **Yes, and worse** — MRZ, surname, given names, date of birth, expiry, nationality and document number, in plaintext | **Never.** Under systemd that is the journal: on disk for weeks, and the application had no rotation, redaction or retention control |

**#3 was the strongest disproof of the claim**, because unlike the spooled file
it had no deletion path at all. It is fixed: the call sites now log a length and
a field count, and `log_redaction.py` is a filter behind them.

**#1 is not fixed, deliberately** — removing it means either holding whole
documents in RAM for every concurrent job, or redesigning the OCR pipeline, and
both are architecture changes this package is not allowed to make. What was
fixed is every way it could *leak*:

- `SessionLocal()` was called **outside** the `try`, so a database blip at that
  instant orphaned the document permanently. It is inside now.
- The endpoint caught `Exception`, not `BaseException`, so a client hanging up
  mid-upload (`CancelledError`) left the file behind.
- A **killed process cannot run a `finally` at all** — and `.github/workflows/`
  restarts the service on every push to master, so any job in flight during a
  deploy orphaned a complete identity document, permanently, as routine
  behaviour. `sweep_orphaned_spool_files()` now runs at startup and clears them.

**What the brief asked for and did not get:** a test asserting *no file is
created during the request*. That test cannot pass, for two independent reasons
that are both by design (rows 1 and 2 above) — Starlette alone would defeat it
even if the endpoint never touched a disk. `tests/test_no_document_persistence.py`
therefore tests what is true and what actually matters: **nothing survives.** It
asserts the file exists mid-job (so the finding above cannot go stale unnoticed),
is 0600 while it does, and is gone afterwards — on success, on failure, on a
rejected upload, on a failed session open, and after a simulated kill.

**For the client DPA, the honest sentence is:** documents are held only in a
temporary file, readable by the service account alone, for the duration of the
extraction, and are deleted when it ends — not "never written to disk".

### Test suites and their status

| Suite | Command | Result |
|---|---|---|
| Backend (`pytest`) | `pytest` in `backend/` | **216 passed, 0 failed** — baseline was 104, so 112 new |
| Frontend unit (`node --test`) | `npm test` | **79 passed, 0 failed** (was 67; 12 new for the password rules) |
| Frontend E2E, 4 projects | `npm run test:e2e` | **337 passed, 1 skipped, 0 failed** (2.8 min) — desktop 109, mobile-small 109, mobile-375 109 (1 skipped), pwa 11 |
| Lint | `npm run lint` | the **same 7 pre-existing** errors in `App.jsx`. No new ones. |

The one skip is package B's documented WebKit multipart-size limitation,
unchanged. Every project is green, WebKit included — which took three invalid
runs and a real bug to reach; see "The WebKit failure" below.

The backend baseline was captured **before** any change (104 passed) exactly as
the brief requires, and one of those 104 had to be edited: a registration test
that posted `"password": "pw"`. It asserted behaviour this package deliberately
changes; its actual subject (signup credits, role, the duplicate-email refusal)
is untouched.

### What changed

```
backend/config.py               NEW. Every environment-driven setting.
backend/file_validation.py      NEW. Magic-byte sniffing + safe_filename().
backend/password_policy.py      NEW. The four rules, the blocklist, the messages.
backend/common_passwords.txt    NEW. 385-entry blocklist (see the note below).
backend/log_redaction.py        NEW. The logging filter.
backend/.env.example            NEW. Every key, no values.
backend/main.py                 Docs closed in production, CORS from env, upload
                                validation + rate limit, generic error handler,
                                cookie login + /logout, /events accepts the
                                cookie, password policy on all four write paths,
                                startup sweep of orphaned spool files.
backend/auth.py                 argon2, cookie set/clear, per-account lockout.
backend/ocr_service.py          Vision pinned to the EU endpoint; the two log
                                statements that printed the document removed.
backend/crud.py                 update_user_password_hash(), for the rehash.
backend/requirements.txt        +argon2-cffi, +argon2-cffi-bindings, +zxcvbn.
frontend/src/App.jsx            Token -> HttpOnly cookie (~25 lines), password
                                rules on the two password screens, scoped CSS.
frontend/src/passwordRules.js   NEW. The rules and the example generator.
frontend/tests/                 mock/api.js mirrors the new server behaviour and
                                tracks its own session (WebKit hides cookies on
                                intercepted requests); helpers/auth.js gains
                                hasSessionCookie/sessionCookie; 5 specs updated,
                                1 new.
frontend/playwright.config.js   Both test servers now run with VITE_API_URL=/api,
                                the same-origin topology nginx actually serves.
```

### The WebKit failure — and the deployment constraint it exposed

The first full E2E run after the cookie migration had `desktop` and
`mobile-small` at 109/109 while `mobile-375` — the only **WebKit** project —
had 3 passed and 105 failed, every one a ~22 second timeout. The three that
passed were the only three that never log in. So: login was broken in Safari
and nowhere else.

Two separate causes, and **neither was in the application**:

**1. The suite was testing a topology that does not ship.**
`frontend/.env.local` points `VITE_API_URL` at `http://127.0.0.1:8001` while the
page is served from `:5173` — a **different origin**. Since this package the
session is a cookie, and WebKit refuses to send a cookie on a cross-origin
subresource request (it treats it as third-party). Every request after login
arrived anonymous and answered 401. Chromium is more permissive and passed,
which is precisely the difference the WebKit project exists to catch.

Production is not affected, and that was verified rather than assumed:
`deploy/nginx-travelapp.conf` serves the frontend at `/` and proxies `/api/` to
`127.0.0.1:8001`, so the browser only ever sees **one origin** and the cookie is
first-party. `playwright.config.js` now runs both test servers with
`VITE_API_URL=/api`, so the suite exercises the shipping topology. An explicit
`VITE_API_URL` (as `E2E_MODE=live` sets) still wins.

> **Deployment constraint, for the human checklist.** With an HttpOnly session
> cookie, **the API must stay same-origin with the app.** If it is ever split
> onto its own hostname, Safari and iOS users cannot log in at all — and this is
> a mobile PWA, so that is most of the audience. Nothing in the code will warn
> you; the login form will simply never proceed.

**2. The mock authenticated by reading a header that WebKit does not expose.**
`tests/mock/api.js` checked `request.headers().cookie`. Playwright reports an
**intercepted** request's headers before the network stack attaches cookies, so
on WebKit `cookie` is absent from both `headers()` and `allHeaders()`; Chromium
includes it, which hid the bug. The mock now authorises on the session it
issued at `POST /token` and clears at `POST /logout`, which is what a stand-in
is for. That the cookie is genuinely what authenticates is proven against the
real application, server-side, by
`test_the_cookie_alone_authenticates_a_request` — a request with **no**
`Authorization` header at all.

The privacy spec was adjusted the same way: it asserts what is observable
(**no request carries an `Authorization` header**) plus the cookie's existence
and its `HttpOnly` flag read from the browser context, instead of asserting on a
per-request header WebKit will never show.

**A correction to an earlier claim in this session.** Two intermediate runs were
also polluted by editing source files while Playwright was running — Vite's HMR
fed half-applied changes into the live suite. That was real, but it was *not*
the cause of the original WebKit failure, which predated those edits. The
numbers in the table above come from a clean run with no concurrent edits.

### Decisions the next package must know

1. **The users table could not be reached, so argon2 is not argon2-only.** The
   brief says to confirm the table is empty and then adopt argon2 outright. The
   production database is on the VPS, and this package is forbidden from
   touching the server; the local PostgreSQL is not running. Rather than assume,
   `CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")` makes **every
   new hash argon2** while any bcrypt hash that might exist still verifies and
   is **transparently upgraded to argon2 on that account's next login**. This is
   a strict superset of the requested behaviour and cannot lock anyone out. The
   test asserts a newly registered account stores `$argon2`.
2. **The token is in an HttpOnly cookie, and the Bearer header still works.**
   `get_current_user` reads the header first and falls back to the cookie, so
   every existing non-browser client is unaffected. `POST /token` returns the
   **same response body as before** — the API contract did not move — and
   additionally sets the cookie. The frontend no longer reads that body.
3. **`GET /events` now accepts the cookie — package B's orphan is closed.**
   `token` became `Query(None)`, and the frontend uses
   `new EventSource(url, { withCredentials: true })`. The query parameter is
   still accepted, so nothing that worked stops working. **Package B wrote its
   privacy spec so that fixing this would turn it red** (`expect(leaking.length)
   .toBeGreaterThan(0)`); it did, and it has been rewritten to assert the
   opposite. That is the test doing its job.
4. **There is a second, deliberately readable cookie**, `scanid_has_session=1`,
   holding no secret. With an HttpOnly session cookie, JavaScript cannot tell
   "your session expired" from "you have never logged in" — both are a 401 on
   `/users/me` — and without this marker every first-time visitor would have
   been greeted by « Votre session a expiré ». It outlives the JWT on purpose.
   **This was found by a test, not by inspection**: the existing spec for that
   banner went red.
5. **`POST /logout` is new.** An HttpOnly cookie cannot be cleared from
   JavaScript, so logging out has to be a server round-trip. Additive.
6. **A generic word list was tried for the blocklist and rejected.**
   `/usr/share/dict/cracklib-small` contains `bordeaux` — the example the brief
   itself recommends showing users — and does **not** contain `motdepasse`, the
   password the brief requires be rejected. It is wrong in both directions.
   **zxcvbn alone also fails**: it scores `Motdepasse12!!` a **3**, which would
   pass the brief's own "minimum score 3" gate, because its corpus is English.
   So the blocklist is a bundled French-aware list **plus** zxcvbn — both must
   pass. The list is matched against several normalised forms of the candidate
   (trimmed, de-leeted, letters-only, in both orders), so one entry blocks a
   family: `motdepasse` rejects `Motdepasse12!!`, `M0tD3P@sse20!!` and
   `P@ssw0rd2024!!`.
7. **The upload allow-list is `{jpeg, png, pdf, heic, avif, gif, webp, tiff}`** —
   exactly the set `frontend/src/upload/fileSniff.js` recognises.
   `test_the_allow_list_matches_the_frontend_sniffer` **reads the JavaScript**
   and fails if they ever drift. It is wider than the picker's `accept` because
   the drop zone takes anything `image/*`, and `ocr_service.py` passes any
   `image/*` to Vision — narrowing it would reject something that works today.
8. **The effective content type now comes from the bytes, not the header.** A
   ZIP or a PNG announced as `application/pdf` used to reach `fitz.open()`,
   which sniffs content itself and would open it. The sniffed type is what the
   background task receives.
9. **The upload rate limit is 120/minute, and the arithmetic is asserted, not
   described.** The queue sends one request per document and retries twice
   (`MAX_ATTEMPTS = 3`), so ten documents is 30 requests, and « Réessayer les
   échecs » is 30 more. 120 is that doubled again.
   `test_the_upload_limit_is_sized_for_a_ten_file_batch_with_retries` recomputes
   it, so lowering the limit fails the suite.
10. **Login stays at 5/minute per IP — unchanged — with per-account lockout
    layered on top** (10 failures, 900 s). The lockout is **in-process, so it is
    per gunicorn worker**: with N workers the real budget is N times the limit.
    A shared counter needs Redis, which is infrastructure this package may not
    add. Package D should consider it.
11. **`/docs`, `/redoc` and `/openapi.json` are not registered in production**,
    so they 404 rather than 401 — there is nothing behind them. The test proves
    it by importing `main.py` in a **subprocess** with `ENVIRONMENT=production`,
    because the app decides its routes at construction time and patching
    afterwards would prove nothing about how the real server starts.

### Verified by tests I ran

Backend, 216 passed. The ones worth naming:

- **Docs**: all three routes absent in production, all three present in
  development, and an unrecognised `ENVIRONMENT` value ("prod", "PRODUCTION",
  "") is treated as development — visible, not silently hardened.
- **CORS**: the configured origin is echoed, `https://evil.example.com` is not,
  no response carries `*` (which would be illegal with credentials anyway), and
  neither the method nor the header list is a wildcard.
- **Auth**: a new account stores `$argon2`; it can log in; a wrong password
  cannot; the cookie carries `HttpOnly`, `Secure` and `SameSite=lax`; the cookie
  **alone** authenticates a request with no `Authorization` header anywhere; the
  Bearer header still works; logout clears both cookies; no credential is 401.
- **Password policy**, table-driven, each rejection asserting the French message
  names the failed rule: 11 characters, no uppercase, exactly 1 digit, exactly 1
  special, `Motdepasse12!!` (with the composition rules first asserted to pass,
  which is what proves the blocklist runs *after* them rather than instead), four
  disguised variants, the email local-part, the account name, and
  `Bordeaux42!?` **accepted** — the example the screen shows must satisfy the
  policy it illustrates. Enforced identically when posted straight at the API
  with no frontend in the path, on registration, on `PUT /users/me`, and on both
  admin endpoints. A rejected password appears in **no** log and in **no**
  response body.
- **Uploads**: every type the frontend can send is still accepted (HEIC
  included, which matters because `imagePrep.js` uploads the original HEIC when
  conversion fails); a Windows executable and a ZIP are rejected **even with the
  extension and `Content-Type` forged to look like a PDF**; a PNG announced as a
  PDF is processed as a PNG; oversized is 413 and leaves no spool behind;
  `../../etc/passwd` is stored as `passwd`; a NUL byte is stripped; a 500-character
  name is capped at 120 with its extension intact.
- **Logs**: the filter redacts MRZ lines, passport and CNI numbers, dates,
  bearer tokens and tokens in query strings, catches `%s` arguments and child
  loggers and exception messages, and **leaves job ids, user ids, page numbers
  and log timestamps alone** so the logs stay useful. Separately, and with the
  filter deliberately **disabled**, the real parsing function is driven with
  text containing a full MRZ and none of it reaches the log — which proves the
  call site was fixed rather than that the safety net caught it.
- **Errors**: a forced internal failure returns « Une erreur interne est
  survenue » with no traceback, no exception class and no file path, while the
  detail *does* reach the log.
- **Vision residency**: `eu-vision.googleapis.com`, asserted three ways — the
  configured value, the construction site reading `config.VISION_API_ENDPOINT`
  through `ClientOptions`, and that images are sent as **inline bytes**, never a
  GCS URI (so no bucket acquires its own retention problem).

**Frontend, from the same run** — the token appears in **0** of 54 request URLs
across a full session (`/events` included, which is the one package B could not
fix); no request carries an `Authorization` header; `localStorage` and
`sessionStorage` are **empty**, so the storage audit that used to expect
`['token']` now expects nothing at all; the four password rules are visible
before a key is pressed and each indicator flips only for its own rule; the
displayed example differs across reloads and itself satisfies the policy; and
package B's compression and EXIF figures are unmoved (4 349 263 → 1 122 349
bytes at 2500×1666, orientation 6 → 1600×1200 with edge bands L=161.5/R=220.0,
orientation 3 → 1200×1600 with H=161.6/B=220.0, retries at 1059 ms then
3033 ms).

**The exact Vision line, as the brief asks for it** —
`backend/ocr_service.py`, in the module-level client construction:

```python
vision_client = vision.ImageAnnotatorClient(
    client_options=ClientOptions(api_endpoint=config.VISION_API_ENDPOINT)
)
```

Before this package it was `vision.ImageAnnotatorClient()` with no options,
which means the **global** endpoint: a French identity document could be
processed in any Google region. The absence of a setting was itself the defect.

### Secrets — the good news

`backend/.env` is **not tracked and never has been**: `git log --all` over
`*.env` is empty, no `service-account*.json` or `gcp-creds*.json` was ever
committed, and searching every commit in the repository for
`BEGIN … PRIVATE KEY` / `"private_key":` returns nothing. **No secret needs
rotating for having been committed.** `.env.example` is committed and is
correctly *not* ignored.

### Cannot be automated / needs a human decision

1. **Whether the users table is empty.** No server access, and the local
   database is not running. See decision #1: the chosen scheme is safe either
   way, but *confirming* it is a human step. If it is empty, the bcrypt entry
   can be dropped from `CryptContext` at any time.
2. **Encryption at rest** — a server or database decision, not a code one.
3. **What Google retains on their side.** Must be read from the current Google
   Cloud terms and written into the DPA; nothing in this repository can show it.
4. **That `eu-vision.googleapis.com` is actually reached in production.** The
   endpoint is asserted in code and configuration; proving the packet lands in
   the EU needs a real credentialed call, which would spend money and needs the
   production service account.
5. **The per-worker lockout under real gunicorn concurrency** (decision #10).
6. **Whether `SameSite=Lax` is right for the production topology.** It is
   correct when the app and the API are same-site — which they are, behind one
   nginx. A developer running the page on `localhost` and the API on `127.0.0.1`
   is cross-site and the cookie will not be sent; use one host for both, or set
   `SESSION_COOKIE_SAMESITE=none` with `SESSION_COOKIE_SECURE=1`.
7. **Real HEIC, real 4G, OCR accuracy after compression, iOS Safari** — still
   package B's list, unchanged.

### Out of scope for code — must be done on the server (package D / a human)

None of these can be done from this repository, and none of them is done:

HTTPS and HSTS · UFW · SSH key-only authentication · fail2ban · CloudPanel 2FA ·
restricting port 8443 · binding PostgreSQL to localhost · encryption at rest ·
backups · unattended-upgrades.

Plus, from this package specifically:

- **`ENVIRONMENT=production` must be set in the server `.env`.** Everything in
  step 2 keys off it, and its default is `development`. If it is not set, the
  docs stay open in production. This is the single most important line.
- **`CORS_ORIGINS` must be set to the one real origin.** Its default is the Vite
  dev server.
- `.env` must be outside the web root, `chmod 600`, owned by the service account.
- `SECRET_KEY` and `ADMIN_PASSWORD` should be rotated now that a policy exists —
  and `ADMIN_PASSWORD` must itself satisfy the new policy.
- Consider `PrivateTmp=yes` on the systemd unit, or a tmpfs `TMPDIR`, so the
  spooled document never touches a persistent disk at all. That would close
  finding #1 properly, and it is a one-line unit change.
- **Keep the API same-origin with the app.** `deploy/nginx-travelapp.conf`
  already does this (`/` for the frontend, `/api/` proxied to the backend), and
  it must stay that way: the session is now an HttpOnly cookie, and Safari and
  iOS refuse to send it cross-origin. Moving the API to its own hostname would
  lock every Apple user out of a mobile-first product, silently. See "The WebKit
  failure" above.

### Findings — observed, deliberately not fixed

1. **`index.html` still says `<html lang="en">` and `<title>Vite + React</title>`**
   — package A's finding, then package B's. Still two lines, still nobody's brief.
2. **`ProgressBar` still renders « 12% - Upload »** — the one English word.
3. **The card view still has no sort control and no « tout sélectionner »** —
   package A asked package B to decide, package B's brief forbade touching it,
   and this brief has no frontend scope for it either. Still open.
4. **`GlobalStyles` is still an inline `<style>` in `App.jsx`.** The password-rule
   CSS was added there rather than to `scanid-app.css`, which this brief forbids
   modifying — so the block grew rather than shrank.
5. **5 new eslint *warnings*** (`react-hooks/exhaustive-deps`, "unnecessary
   dependency `token`"): the prop is now a boolean the callbacks no longer read.
   Removing it from the arrays is safe but touches five more places for no
   behaviour change, so it was left. **No new eslint *error*.**

### Anything unresolved

- **Nothing is committed on this branch.** `feat/security-app-layer` holds the
  work in the working tree, awaiting review. Package B *was* committed
  (`f2b5139`) so this branch had a clean base.
- `npm run lint` still fails on the same 7 pre-existing `App.jsx` errors.

### Handed to a human

Everything under "Cannot be automated" and the whole server checklist above.
`ENVIRONMENT=production` and `CORS_ORIGINS` are the two that silently leave the
application unhardened if forgotten.

---
---

## Handover — Package D — Ops scripts

- **Branch:** `feat/ops-scripts` (branched from `feat/security-app-layer`, whose
  work is now committed as `8d19b38` — package C was uncommitted when this
  session started and `git status` had to be clean before branching. Fourth
  time the same situation, same resolution. C is committed on its own branch,
  **not merged**; it is still awaiting review exactly as its handover says.)
- **Date:** 2026-09-06
- **Scope:** a new `ops/` directory and nothing else, plus this handover note.
  No file anywhere else in the repository was created, edited or deleted.
  > **Superseded on 2026-09-07.** The orphaned work listed at the end of this
  > section was subsequently authorised and carried out, which *did* change
  > files outside `ops/`. See **Follow-up — orphaned work closed** at the very
  > bottom of this document for what changed and what it cost.

### Nothing was executed against any server, and nothing was scheduled

Stated plainly, because it is the first rule of this brief:

- No `ssh`, no `scp` to a host, no remote `psql`, no `pg_dump` against anything
  but a throwaway PostgreSQL created and destroyed locally.
- **No cron entry was installed.** No `crontab` was read or written. The
  crontab line exists only as a comment inside `backup.sh` and in the README.
- No `systemctl`, no `nginx -s reload`, no `nginx -t` against a real config, no
  package installed on any server.
- No file was written outside the repository and the test temp directories.
- No real credential, hostname, key or production path appears in `ops/`. Every
  path is a placeholder (`/opt/scanid`, `/etc/scanid`, `/var/backups/scanid`);
  the README flags that the repo actually deploys to `/opt/travelapp`, so the
  human substitutes consistently.

**A human must review these line by line, adapt every variable, and run
`restore-test.sh` against a real backup before go-live. An untested backup is
not a backup.**

### Files created

| File | Lines | What it is |
|---|---|---|
| `ops/backup.sh` | 300 | `pg_dump \| age` nightly backup, off-site copy, retention pruning |
| `ops/restore-test.sh` | 279 | Restore rehearsal into a throwaway database |
| `ops/nginx-security-headers.conf` | 199 | Header snippet incl. CSP. Not applied anywhere. |
| `ops/README.md` | 358 | Prerequisites, variables, manual test procedure, verification |
| `ops/tests/run-ops-tests.sh` | 438 | 94 assertions against a local throwaway PostgreSQL |
| `ops/tests/test-nginx-headers.sh` | 199 | 29 assertions: parses **and** sends what it claims |

### Verified by tests I ran

```
$ shellcheck --shell=bash ops/backup.sh ops/restore-test.sh \
      ops/tests/run-ops-tests.sh ops/tests/test-nginx-headers.sh
  0 warnings across all 4 scripts          # zero suppressions; see note below

$ bash -n <each of the four>
  OK ops/backup.sh
  OK ops/restore-test.sh
  OK ops/tests/run-ops-tests.sh
  OK ops/tests/test-nginx-headers.sh

$ ops/tests/run-ops-tests.sh
  RESULTS: 94 passed, 0 failed

$ ops/tests/test-nginx-headers.sh
  RESULTS: 29 passed, 0 failed
```

shellcheck is clean with **no `# shellcheck disable` anywhere**. Three warnings
appeared in the first draft and all three were fixed rather than justified: two
`SC1090` (the `source=/dev/null` directive was on the line above `set -a;
source …` and so applied to `set`, not to `source` — the lines were split), and
`SC2221/SC2222` (`*prod*` already matched `*production*`, so the second pattern
in the production-lookalike guard was dead code).

`run-ops-tests.sh` builds its own PostgreSQL cluster with `initdb` into a temp
directory, on a random loopback port, with `unix_socket_directories` emptied,
seeds it with a schema mirroring `backend/models.py`, and destroys it. It never
reads `/etc/scanid/backup.env` and never contacts a remote host.

What the 94 assertions actually prove, grouped:

**backup.sh** — preflight refuses a missing env file, an unset required
variable (naming it), an age **private** key pasted into `AGE_RECIPIENT`, and
`/var` as `BACKUP_DIR`. `--dry-run` creates no backup file, no `.part`, and
copies nothing. A real run produces one file, mode 0600, no `.part` left. The
file **starts with the age header, contains no `PGDMP` magic, and contains
none of the seeded surname, email or passport number** — i.e. it is genuinely
not readable as plain text. No unencrypted `.dump` or `.sql` exists anywhere in
the workspace at any point. It **decrypts back to a dump `pg_restore --list`
accepts**, whose listing names the real tables. The off-site copy arrives and
is byte-identical. A dump against an unreachable database exits non-zero, logs
`status=error` with the failing stage, leaves no `.part`, and creates no file.
Retention pruning with a 14-day period **deletes the 30-, 20- and 15-day-old
files, keeps the 13- and 2-day-old ones, keeps a foreign filename however old,
and does not recurse into a subdirectory**. `--no-prune` keeps everything. A
second concurrent run refuses on the lock. Exactly **one** log line per run, on
success and on failure.

**restore-test.sh** — refuses without `--confirm` (exit 2) and creates no
database while printing what it would have done. Refuses when `PGDATABASE`
itself contains the scratch prefix. Refuses a scratch name that looks like
production. With `--confirm` it restores, reports `users=2 passports=3
ocr_jobs=1 voyages=1`, **drops the scratch database**, and leaves the source
database untouched. It picks the newest backup when `--file` is omitted. It
**fails** when a sanity count is not met (naming the table and both numbers),
when a required table is missing, on the wrong decryption key, and on a
corrupted file — and the scratch database is dropped in every one of those
failure paths. An end-to-end cycle proves a row inserted after the previous
backup is present in the restore of the next one.

**nginx snippet** — `nginx -t` passes; then nginx is actually started and a
request made, asserting each of the four headers arrives, that **HSTS does not**
(it ships commented out), and that the CSP contains each of its twelve
directives verbatim and contains **no** `fonts.googleapis.com`,
`fonts.gstatic.com`, any `googleapis.com`, or `'unsafe-eval'`. Finally the
commented-out HSTS line is uncommented **in a copy** and proven to parse and to
send a well-formed header — so a typo in a line that ships disabled cannot lie
in wait.

### The bug that test found — worth knowing about

The first draft wrote the CSP across multiple lines with trailing backslashes,
the way one would in a shell. **nginx is not a shell.** Inside a quoted string a
trailing backslash is a literal backslash and the newline stays in the value.
That version passed `nginx -t` cleanly and then emitted a broken multi-line
header that `curl` rejected outright and a browser would discard — **no policy
at all, silently, on a config that tests green.**

This is exactly the failure the brief warned about for `font-src`, in a place
nobody was looking. It is why `test-nginx-headers.sh` requests a page instead of
trusting `nginx -t`, and why the snippet carries a `KEEP THIS ON ONE LINE`
comment. If anyone later reformats that line for readability, the tests fail.

### The font-src trap — checked against a real build, and the finding

Checked, not assumed:

```
$ npm run build
$ grep -o "url(data:" dist/assets/*.css dist/assets/index-*.js     # no matches
$ find dist/assets -name '*.woff2' -printf '%s %f\n' | sort -n | head -1
  4204 space-grotesk-vietnamese-700-normal-DMty7AZE.woff2
```

**No asset is inlined, so `font-src 'self'` is correct and the CSP stays tight.**

But the margin is **108 bytes**: Vite's `assetsInlineLimit` defaults to 4096 and
the smallest woff2 in the build is 4204. It is the *Vietnamese* subset of Space
Grotesk that is closest to the line. A `@fontsource` bump that drops a few
glyphs from that subset would cross it, the font would be inlined as a `data:`
URI, `font-src 'self'` would block it, and the app would fall back to a system
typeface **with no error anywhere**. The permanent fix is one line in
`frontend/vite.config.js` (`build: { assetsInlineLimit: 0 }`) which this package
must not touch — see below.

### How the CSP was derived

Every non-`'self'` token is traceable to a specific line of application code,
and each is commented in the snippet with that line. No token is there
defensively:

| Directive | Why |
|---|---|
| `style-src 'self' 'unsafe-inline'` | `App.jsx:44` renders a literal `<style>` element and there are ~35 `style={{…}}` props. Without it the app renders unstyled. |
| `img-src 'self' blob: data:` | `blob:` — `upload/imagePrep.js` and `App.jsx` load `URL.createObjectURL()` results into `<img>` to decode/rotate/compress. `data:` — `imagePrep.js:52` embeds a base64 JPEG EXIF-orientation probe. |
| `connect-src 'self' data:` | `'self'` for `/api/` and the `/events` SSE stream, both same-origin. **`data:` because `imagePrep.js` reads that probe with `fetch()`, and `fetch()` on a `data:` URI is governed by connect-src, not img-src.** Easy to miss; fails silently. |
| `worker-src 'self' blob:` | `'self'` for the PWA service worker; `blob:` because heic2any spawns `new Worker(URL.createObjectURL(…))`. |
| `manifest-src 'self'` | Some browsers do not fall back to `default-src` for the PWA manifest. |

And what is deliberately **absent**: no Google Fonts origins (fonts are
self-hosted via `@fontsource`, per decision 2 — there is no third-party font
request to allow), and no Vision API origin (Vision is called server-side; it
does not belong in a policy that only constrains the browser).

### Cannot be automated — reasons, not excuses

Nothing below is tested, and none of it should be described as working.

1. **Everything about the real server.** Nothing here has run against the VPS,
   its PostgreSQL, its nginx or its cron. All of it is text awaiting review.
2. **HEIC upload under this CSP, on a real iPhone.** `heic2any` is an Emscripten
   build of libheif and its glue contains `new Function(…)` (verified by grep on
   `dist/assets/heic2any-*.js`), which `script-src 'self'` blocks exactly as it
   blocks `eval`. **Whether that code path actually executes during a conversion
   was not determined.** Proving it needs a real HEIC photo decoded in a real
   browser under this exact header, and heic2any runs inside a blob-URL Worker
   whose violations do not surface to the page — this session had no way to run
   that. It is reported as unverified rather than assumed either way. The
   snippet documents the narrowest fix (`script-src 'self' 'unsafe-eval'`) and
   says explicitly not to add it pre-emptively. **iPhones shoot HEIC by default
   and this is a mobile-first product, so test it before go-live.**
3. **That the off-site destination works.** Tested with a local directory as the
   rsync target. A real `user@host:/path` needs a credential and a host, neither
   of which exists here.
4. **That `age` is installed on the VPS.** The preflight fails loudly if it is
   not, which is the best a script can do from here.
5. **Restore timing at production data volume.** The test database holds six
   rows. How long a real restore takes, and whether the disk has room for it,
   are numbers only the real server can give.
6. **Whether `SANITY_MIN_ROWS` defaults suit the real database.** The default
   asserts `users>=1` only. A human must set numbers the live data exceeds,
   otherwise the check passes on a near-empty restore.

### Findings — observed, deliberately not fixed

1. `index.html` still says `<html lang="en">` and `<title>Vite + React</title>`.
   Package A's finding, then B's, then C's. Still nobody's brief. Four packages.
2. `ProgressBar` still renders « 12% - Upload ».
3. The card view still has no sort control and no « tout sélectionner ».
4. `GlobalStyles` is still an inline `<style>` in `App.jsx` — and it is now not
   only a tidiness issue but the sole reason `style-src` needs `'unsafe-inline'`.
   It has become a security finding rather than a cosmetic one.

### Anything unresolved

- **Nothing is committed on this branch yet** at the time of writing; `ops/` is
  in the working tree awaiting review, matching how packages A–C were handed
  over.
- `frontend/dist/` was rebuilt to inspect the asset output for the `font-src`
  check. It is gitignored and is not part of the change.

### What the next package must know

There is no next package — D is the last. For a human continuing the work:

- `ops/tests/` is the regression suite for `ops/`. Run both after any edit.
  They need `age`, `age-keygen`, `shellcheck`, PostgreSQL server binaries
  (`initdb`/`pg_ctl`, found automatically under `/usr/lib/postgresql/*/bin`),
  and either a local `nginx` or docker. Each exits 3 and says which tool is
  missing rather than pretending to pass.
- The CSP is derived from the built frontend. **Re-derive it whenever the
  frontend changes**, using the two commands in the "font-src trap" section of
  `ops/nginx-security-headers.conf`.
- `restore-test.sh` needs the age **private** key, which by design is not on the
  VPS. Run it from a workstation against a backup pulled from the off-site
  destination — that tests the copy you would actually reach for.

### Orphaned work — changes required outside this package's scope

Per the "no orphaned work" rule, these are named rather than half-applied. None
of them was made **by package D**.

> **Status as of 2026-09-07:** items 1 and 2 have since been authorised and
> done; item 3 is still open. Item 1 in particular did not go in as written —
> applying the CSP exposed a real defect it would have caused. See **Follow-up —
> orphaned work closed** at the bottom of this document.

1. **`deploy/nginx-travelapp.conf` needs one line:
   `include /opt/scanid/ops/nginx-security-headers.conf;` inside its `server`
   block.** Without it the snippet does nothing at all. That file is the single
   source of truth for the vhost and is rsynced by
   `.github/workflows/deploy.yml`, so it belongs to the deploy configuration,
   not to `ops/`. **This is the one change that makes the whole snippet real,
   and it is deliberately not made.**
   Watch the `add_header` inheritance trap when doing it: an `add_header` inside
   any of that file's four `location` blocks silently drops *every* inherited
   header for that path. The snippet documents this at the top.
2. **`frontend/vite.config.js` — `build: { assetsInlineLimit: 0 }`.** Makes
   `font-src 'self'` permanently safe instead of safe by 108 bytes. Owner:
   whoever owns the frontend build; forbidden here.
3. **`frontend/src/App.jsx` — move `GlobalStyles` into `scanid-app.css` and
   replace the `style={{…}}` props**, to let `'unsafe-inline'` be dropped from
   `style-src`. This is the one real CSP debt. Owner: a frontend package;
   package A's brief forbids modifying `scanid-app.css` outside its changelog
   process, so it needs its own scope.

### Handed to a human

Everything under "Cannot be automated", everything under "Orphaned work", and:

- Create `/etc/scanid/backup.env` (mode 0640, root:scanid, outside the web root)
  and replace every placeholder.
- `age-keygen` the pair **off the server**. Public key to the VPS; **private key
  stored twice**, never on the VPS. Lose it and every backup is landfill.
- Choose and provision the off-site destination and its credential.
- Install the cron entry or systemd timer, and point a monitor at the exit code.
- **Run `restore-test.sh` against a real backup before go-live**, and put a
  quarterly repeat in the calendar.
- Confirm HTTPS works, *then* uncomment HSTS. Not before — it is unrecoverable.

The whole human checklist from packages A–C still stands: HTTPS, UFW, SSH
key-only auth, fail2ban, CloudPanel 2FA, restricting port 8443, binding
PostgreSQL to localhost, encryption at rest, unattended-upgrades — plus
`ENVIRONMENT=production` and `CORS_ORIGINS`, which package C flagged as the two
lines that silently leave the application unhardened if forgotten.

---
---

## Follow-up — orphaned work closed

- **Date:** 2026-09-07
- **Branch:** `feat/ops-scripts`
- **Why this exists:** package D deliberately left three changes unmade because
  they fell outside its scope. Two were then explicitly authorised, along with
  reproducing package D's own test claims on this machine. This section records
  what changed, and the one real defect the work uncovered.

### What changed, and why

| File | Change |
|---|---|
| `deploy/nginx-travelapp.conf` | `include /opt/travelapp/ops/nginx-security-headers.conf;` at **server** level (orphaned item 1) |
| `.github/workflows/deploy.yml` | rsync `ops/` → `/opt/travelapp/ops/`, ordered **before** `deploy/` |
| `frontend/vite.config.js` | `build: { assetsInlineLimit: 0 }` (orphaned item 2) |
| `ops/nginx-security-headers.conf` | `script-src` gained `'unsafe-eval'`; docs rewritten to match reality |
| `ops/tests/test-nginx-headers.sh` | the `'unsafe-eval'` assertion inverted, and `'unsafe-inline'` now checked **within** `script-src` |
| `frontend/tests/e2e/features.spec.js` | 11 `test.skip(LIVE, …)` guards |
| `ops/README.md`, `frontend/tests/README.md` | brought in line with the above |

**The include path is `/opt/travelapp/ops/`, not `/opt/scanid/ops/`.** The
snippet is only real if the file is on the server, and `deploy.yml` runs
`nginx -t` and **fails the deploy** when the config does not parse. So `ops/`
is now rsynced, immediately before `deploy/`, and every `/opt/scanid` reference
in `ops/` was corrected. Do not delete `ops/nginx-security-headers.conf` without
first removing the include line.

### The defect this uncovered — `script-src 'self'` hangs HEIC uploads

Package D flagged the heic2any/`new Function` question as *unverified*. It was
verified here, and the strict policy was not merely suboptimal — it was broken:

```
built bundle served over HTTP, headless Chromium, CSP on vs off
  CSP off:  heic2any settles     -> "ERR_LIBHEIF format not supported"
  CSP on:   NEVER SETTLES (hang) -> EvalError: ... 'unsafe-eval' is not an
                                    allowed source of script
```

heic2any decodes in a blob worker, and a blob worker inherits the document's
CSP. libheif's embind glue calls `new Function` while registering types, so the
worker dies **during script evaluation, before its message handler exists**. The
promise therefore never settles rather than rejecting — so the `try/catch` in
`frontend/src/upload/imagePrep.js` never runs and its "on failure, upload the
original" fallback never fires. `uploadQueue.js` drains serially with `await`
and no timeout, so one HEIC stalls **every document queued behind it** until the
page is reloaded.

`script-src` therefore carries `'unsafe-eval'`. It is a genuine weakening and
the one token in this policy that should not be permanent: removing it means
replacing heic2any with a wasm-based decoder and moving to `'wasm-unsafe-eval'`,
which is far narrower and — importantly — does **not** permit `new Function`, so
it is not a drop-in substitute. The reasoning, the measurement and the removal
path are all in the comment at the foot of `ops/nginx-security-headers.conf`.

**Not measured:** real Safari on a real iPhone. Blob workers inheriting the
document policy is spec-mandated, so Safari is expected to match Chromium, but
that is reasoning, not a measurement. Confirm on a device before go-live.

### Verified by tests I ran

```
frontend unit  (node --test)                     79 passed
backend        (pytest)                          216 passed
frontend E2E   (npm run test:e2e, 4 projects)    337 passed, 1 skipped
                 — identical to the pre-change run
ops suite      (ops/tests/run-ops-tests.sh)      94 passed, 0 failed
ops nginx      (ops/tests/test-nginx-headers.sh) 30 passed, 0 failed
shellcheck     (4 scripts, 0 suppressions)       0 warnings
```

`age` and `shellcheck` are not installable on the dev host (no passwordless
sudo), so the ops suite and shellcheck were run in a throwaway container built
from `ubuntu:24.04` with `age shellcheck postgresql rsync util-linux`, with the
repository mounted **read-only**. This reproduced package D's claimed numbers
exactly (94 and 0) — those claims were previously unverified on this machine.

Additionally, and beyond what package D could do: the **real vhost** was run in
nginx with the real snippet, the real build and the real backend, and the
baseline suite driven through it. All 6 baseline specs passed under the live CSP,
`document.fonts.check` returned true for both self-hosted families, and a full
login-to-dashboard session recorded **zero** `securitypolicyviolation` events.

### Still open

1. **Orphaned item 3 is untouched** — `GlobalStyles` and the ~35 `style={{…}}`
   props in `App.jsx` still force `'unsafe-inline'` in `style-src`. Unchanged.
2. **`'unsafe-eval'`** should go once heic2any is replaced. See above.
3. **`deploy.yml`'s health check is `curl -sf http://127.0.0.1:8001/docs`.**
   That endpoint returns **404 when `ENVIRONMENT=production`** (package C closed
   the docs deliberately), so setting the variable the security work depends on
   will fail the deploy at that line. Not changed here — it is outside what was
   authorised — but it will bite on the first hardened deploy. `/openapi.json`
   is closed in production too; a route that exists in both modes is needed.

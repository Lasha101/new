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

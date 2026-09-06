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

# ScanID — test harness

Automated tests for the ScanID front end. Everything lives under `frontend/`,
the only npm package in the repository; the backend keeps its own pytest suite
in `backend/tests/`.

Two layers:

| Layer | Runner | What it covers |
|---|---|---|
| Unit | `node --test` (the runner already used by `src/resultsHelpers.test.js`) | Pure functions: results helpers, the contrast helper, the generated fixtures |
| End-to-end | Playwright | The real app in a real browser, across three viewports |

---

## Running

```bash
cd frontend
npm install
npx playwright install chromium webkit   # once

npm test              # unit tests only — no browser needed (this is what CI runs)
npm run test:unit     # same thing, explicit
npm run test:e2e      # all four Playwright projects
npm run test:e2e:mobile     # mobile-small + mobile-375 only
npm run test:e2e:desktop    # desktop only
npm run test:e2e:pwa        # the PWA suite, against a production build
npm run test:e2e:ui         # Playwright's interactive UI
npm run test:fixtures       # force-regenerate the fixture binaries
npm run icons               # regenerate public/icons/*.png from public/vite.svg
```

`npm test` is deliberately **browser-free**. The repository's CI workflow runs
`npm test` in the frontend job on a runner with no browsers installed; making
`test` launch Playwright would turn that job red. Run `test:e2e` explicitly.

`test:e2e` starts **two** servers itself (`webServer` in
`playwright.config.js`) and shuts them down afterwards: Vite's dev server on
5173 for the app suites, and `vite build && vite preview` on 4173 for the PWA
suite. Point `E2E_BASE_URL` / `E2E_PREVIEW_URL` at servers you started yourself
to skip either.

### The four projects

| Project | Viewport | Engine | Server | Why |
|---|---|---|---|---|
| `desktop` | 1280×800 | Chromium | dev | The agency-desk baseline |
| `mobile-small` | 360×640 | Chromium | dev | The narrowest phone still in real use |
| `mobile-375` | 375×667, DPR 2 | **WebKit** | dev | iPhone-class. Safari differs from Chromium in file input handling, EXIF, sticky positioning and downloads |
| `pwa` | 390×844 | Chromium | **preview (built)** | The service worker, the manifest and the icons only exist after a build, and a worker in front of Vite's dev server would hide HMR. `testDir: tests/pwa`. |

Traces, videos and screenshots are kept on failure (`test-results/`).

---

## Environment variables

| Variable | Default | Meaning |
|---|---|---|
| `E2E_MODE` | *(unset)* | `live` drives a real backend instead of the mock |
| `E2E_USERNAME` | `alice` | Login used by `login(page)` |
| `E2E_PASSWORD` | `test-password` | Its password |
| `E2E_BASE_URL` | `http://127.0.0.1:5173` | Front end under test; set it to skip the managed dev server |
| `E2E_PREVIEW_URL` | `http://127.0.0.1:4173` | The **built** app the `pwa` project drives; set it to skip the managed `build && preview` server |
| `E2E_MOCK_PROCESSING_MS` | `1200` | How long a mocked OCR job "runs" |
| `E2E_LOGIN_RETRY_MS` | `62000` | How long `login()` waits out the server's login throttle |
| `E2E_SKIP_WEBKIT` | *(unset)* | `1` drops the `mobile-375` project — a real loss of coverage, never silent |
| `VITE_API_URL` | `/api` | Read by the app itself (`frontend/.env.local` sets `http://127.0.0.1:8001` here) |

No credential is committed. The defaults only match the mocked backend and the
disposable live server described below.

---

## Mocked by default, live on demand

**There is no staging backend.** The production API needs PostgreSQL, and every
upload goes to Google Cloud Vision — billable, slow, and non-deterministic. So
the default is a mocked API.

### Mocked mode (default)

`tests/mock/api.js` answers the app's requests through Playwright route
interception. The browser still runs the **real application**: the real login
form, the real hidden file input, the real filter, sort, export and download
code. Only the server is substituted.

It mirrors `backend/main.py` — same paths, same response shapes from
`schemas.py`, same French error strings, same `Content-Disposition`. **When the
API changes, this file must change with it.** An unmocked path returns HTTP 501
with an explicit message rather than an empty success, so a hole in the mock
fails loudly instead of quietly turning a suite green.

The seeded dataset (`tests/mock/data.js`) is entirely synthetic — invented names,
document numbers outside every real French series — and is composed so the
Tous/PASS/PI filter has three distinct row counts: **5 total, 2 PASS, 3 PI**.

### Live mode

```bash
# terminal 1 — a disposable backend: the real FastAPI app on throwaway SQLite
../newvenv/bin/python tests/live/serve.py --seed --fresh --port 8001

# terminal 2
E2E_MODE=live npx playwright test --project=desktop --workers=1
```

`tests/live/serve.py` imports the real app and rebinds `database.engine` /
`database.SessionLocal` to a temporary SQLite file *before* `main.py` binds them
— the same substitution `backend/tests/conftest.py` already performs for pytest.
No application file is modified. It seeds the same five synthetic documents.

Two things to know about live runs:

* **`POST /token` is rate limited to 5 per minute per IP** (`backend/main.py`).
  A suite hits that within two or three specs. `login()` detects the app's
  throttle message, waits the window out and submits again, so a live run is
  slow but correct. Use `--workers=1`.
* **OCR really calls Google Vision.** A synthetic fixture has no readable MRZ, so
  the job legitimately finishes as *Échoué* — "Aucun texte n'a pu être détecté".
  The upload spec therefore asserts, in live mode only, that the job reaches a
  terminal state and the UI reports it. Extraction *accuracy* is not something
  this harness can assert; see "What these tests cannot cover".

---

## Fixtures

Generated, never committed: they total ~20 MB, and **a real client document must
never be used as a fixture**. Generation is deterministic (seeded noise, fixed
encoder settings), so two machines produce identical bytes. `tests/global-setup.js`
and the `pretest:unit` hook create anything missing; `npm run test:fixtures`
rebuilds everything.

The manifest is `tests/fixtures/index.js`; the images are coloured rectangles
with a synthetic machine-readable-zone band, drawn in code.

| Fixture | What it is | Why it exists |
|---|---|---|
| `large-landscape.jpg` | 3200×2133, ~4 MB | The "straight off the phone" photo. Client-side resizing, upload progress, the 10 Mo notice |
| `small.jpg` | 640×427, <200 KB | The fast happy path, where upload time is noise rather than the subject |
| `portrait-exif-orientation-6.jpg` | 1200×1600 portrait, **EXIF Orientation = 6** | **The important one.** Canvas re-encoding drops EXIF silently, and a rotated MRZ fails OCR. Any resize or compress step must be checked against this file |
| `document.png` | 900×600 | The PNG branch of the `accept` list |
| `document.pdf` | 1 page, A4 | The PDF branch. The backend renders pages with PyMuPDF |
| `disallowed.txt` | text/plain | Rejection tests — see the caveat below |
| `oversized.jpg` | ~11 MB | Over the 10 Mo the upload card announces — see the caveat below |

Verification: `tests/fixtures/fixtures.test.js` parses each file with readers
written independently of the writers that produced them — a separate JPEG marker
walker, a separate EXIF/TIFF reader, a table-free CRC-32, a PDF xref check — so a
bug in a writer cannot be masked by the same bug in a reader.

`exiftool` is **not installed on the development machine**, so the EXIF tag is
verified from the raw bytes by that suite rather than taken on trust. It was
additionally cross-checked once, by hand, with Pillow (`getexif()[0x0112] == 6`)
and PyMuPDF, using the backend virtualenv.

**HEIC is not generated.** A real HEIC from an iPhone camera cannot be produced
reliably in CI, and a synthetic one would not reproduce what iOS actually
uploads. HEIC stays a device test.

### Two fixtures that have no test yet, on purpose

`disallowed.txt` and `oversized.jpg` exist because the brief asks for them, but
**the app does not reject either today**:

* The file picker's `accept="image/png, image/jpeg, image/jpg, application/pdf"`
  is only a picker filter — it does not validate a chosen file, and
  `setInputFiles` bypasses it entirely. Only the *drag-and-drop* handler checks
  the type (`OcrUploader.handleDrop`).
* No size limit is enforced anywhere. The upload card says "PNG, JPG ou PDF
  jusqu'à 10Mo", but neither the front end nor `POST /passports/upload-and-extract/`
  checks the size.

Writing rejection tests now would mean writing failing tests for behaviour that
does not exist. The fixtures are ready for the package that adds the checks.

---

## Helpers

`import { … } from '../helpers/index.js'`

| Helper | Returns |
|---|---|
| `login(page, opts)` | Authenticates through the real form; absorbs the server's login throttle |
| `logout(page)`, `storedToken(page)` | Session teardown; the stored JWT |
| `uploadFiles(page, paths, opts)` | Drives the real file input (`opts.submit` also clicks « Lancer l'analyse ») |
| `waitForProcessing(page, opts)` | Waits until every job reaches « Terminé » / « Échoué »; returns the labels |
| `countResultRows(page)`, `resultsRows(page)` | The rows **on screen** — table rows above 720 px, cards below |
| `resultsTable(page)`, `resultsCards(page)` | Each view explicitly, never the export preview's |
| `selectDocType(page, value)` | Sets the Tous/PASS/PI `.sid-seg` filter (`''`, `'PASS'`, `'PI'`) |
| `getStorageState(page)` | localStorage, sessionStorage, IndexedDB names, Cache Storage keys, service workers — plus `unavailable[]` |
| `measureTapTargets(page, selector)` | A box per visible match, with `smallestSide` |
| `tapTargetsBelow(targets, px)` | Those under a size threshold |
| `hasHorizontalOverflow(page)`, `findOverflowingElements(page)` | Sideways-scroll diagnosis |
| `contrastRatio(fg, bg)` | WCAG ratio, 1 to 21. Pure — no browser needed |
| `getComputedColorPair(page, selector)` | Computed foreground and *effective* background, composited through ancestors, plus `ratio`, `aaThreshold`, `passesAA` |
| `parseColor`, `compositeOver`, `relativeLuminance`, `isLargeText`, `wcagAAThreshold` | The pieces, exported for reuse |
| `readCsv(path)`, `readXlsx(path)` | Parsed rows of a downloaded export, `string[][]`. Dependency-free |
| `unzip(buffer)` | ZIP entries as `{ name -> Buffer }`; handles stored and deflate |
| `SELECTORS`, `TEXT` | The DOM handles and French strings the suites depend on |

Two notes for whoever builds on these:

* **`getStorageState().unavailable`** names any API the browser refused to
  enumerate (WebKit does not implement `indexedDB.databases()`; Cache Storage
  needs a secure context). An entry there means *unknown*, never *empty*. Do not
  assert "nothing is stored" without checking that list first.
* **`getComputedColorPair().backgroundImage`** is non-null when a gradient or
  image sits behind the text. The ratio then describes only the colour layers and
  must not be trusted on its own.

The app has **almost no test ids**, and its `<label>` elements are not associated
with their inputs (no `htmlFor`/`id`, no nesting), so `getByLabel` does not work.
`tests/helpers/selectors.js` therefore leans on French placeholder text, button
text and the `.sid-*` class names. If a later package adds test ids or fixes the
label association, change that one file and the suites follow.

The one exception Package A added: **results cells and card values carry
`data-field="<column>"`**, so the table/card parity spec can read both views the
same way instead of counting columns by position.

---

## The suites

| File | What it holds |
|---|---|
| `e2e/smoke.spec.js` | The regression baseline. **Nothing here may be weakened to make it pass.** |
| `e2e/helpers.spec.js` | Proves the helpers themselves work in a real browser |
| `e2e/fonts.spec.js` | Both families load and resolve; a full session makes **zero** requests to googleapis/gstatic; every font file comes from this origin |
| `e2e/a11y.spec.js` | 44 px tap targets, ≥ 16 px inputs, the measured contrast table, a focus ring on every tab stop |
| `e2e/responsive.spec.js` | The 720 px switch, **table/card parity**, uppercase/centring, no horizontal overflow at 360/375 |
| `e2e/design-system.spec.js` | Badges and chips driven by real data, download column order and accents, no English strings, the top bar |
| `e2e/features.spec.js` | Everything else the app can do: sorting, selection, bulk edit, multi-delete, manual create/edit, job removal, export preview and selection exports, password toggle, registration, account edit, navigation — plus what the cards can and cannot do on a phone |
| `e2e/capture.spec.js` | Capture controls (`multiple`, `capture="environment"`, the HEIC accept types, the photo-guide link), compression against a stated byte budget, **EXIF orientation proven on pixels**, HEIC magic-byte detection and its never-drop failure path, two-tap reachability |
| `e2e/queue.spec.js` | The batch queue against the real transport: retry twice with a growing delay, `failed` reached, « Réessayer les échecs » touching only the failures, a mixed batch leaving the successes alone, a server refusal never retried, nothing persisted across a reload |
| `e2e/privacy.spec.js` | The token never in a URL (except the documented `/events` case), blob URLs revoked, a network blip no longer discarding the session, an expired session prompting for re-auth, web storage after a full session |
| `pwa/pwa.spec.js` | **Runs on the built app.** Manifest fields and content type, every icon 200 at its declared size, the worker registering and precaching exactly the shell, uploads and results creating no cache entry, the French offline screen, and the full-session storage audit (key *and* value contents, cache entry bodies included) |
| `build/no-google-fonts.test.js` | Scans the shipped `dist/` — runs under `npm test`, not Playwright |
| `src/upload/fileSniff.test.js` | Magic-byte detection (a real iPhone `ftyp` box, AVIF told apart from HEIC), EXIF orientation in both byte orders, EXIF stripping, the orientation transforms checked corner by corner, the resize arithmetic — all under `node --test`, no browser |
| `src/upload/uploadQueue.test.js` | The retry policy with simulated delays: attempt counts, growing backoff, retriable vs final, `retryFailed` scope, job-status folding — `node --test` |

The parity spec is the load-bearing one: the results table and the mobile card
list render from one column definition (`PASSPORT_COLUMN_ORDER`) and one cell
function (`resultCellValue`), and that spec asserts them field-by-field equal. If
it goes red, the two views have drifted.

---

## WebKit on Linux

Playwright's WebKit build needs `libavif.so.16`, which Ubuntu 24.04 does not
install by default, and its launcher **overwrites** `LD_LIBRARY_PATH` — so the
usual override does not work.

`npm run test:e2e` runs `tests/scripts/ensure-webkit-deps.mjs` first. Without
root, it downloads `libavif16`, `libgav1-1` and `libyuv0` with `apt-get download`
into `tests/.browser-libs/` (gitignored) and `LD_PRELOAD`s them for the WebKit
project only. It is a no-op when the libraries are already installed
system-wide — including on GitHub Actions after `playwright install --with-deps`.

If it cannot fetch them it says so and names the `sudo apt-get install` command.
`E2E_SKIP_WEBKIT=1` drops the project, which is a real loss of coverage.

---

## What these tests **cannot** cover

A green suite here is not full coverage. In particular:

1. **Real HEIC from an iPhone.** Not generatable in CI; a synthetic file would
   not reproduce what iOS actually uploads. The suite proves that a genuine HEIC
   `ftyp` box is *detected* and that a conversion failure uploads the original
   rather than dropping it — it has never decoded a real HEIC. Device test only.
2. **Real 4G / poor-network timing.** Playwright can throttle CPU and stub the
   network, but it cannot reproduce a real cellular link — packet loss, radio
   wake-up latency, a carrier proxy re-encoding images. The 60-second upload
   stall watchdog in `CrudManager.handleUpload` is untested for that reason.
3. **OCR accuracy against real documents.** The fixtures carry no readable MRZ,
   and no real client document may be used. Whether Vision reads a genuine French
   passport or CNI correctly is proven only by `backend/tests/test_ocr_*.py`
   against stored text, and ultimately by a human with specimen documents.
4. **iOS Safari behaviour.** The `mobile-375` project runs Playwright's WebKit,
   which is *not* Mobile Safari: no real iOS camera capture, no Photos picker, no
   iOS `HEIC→JPEG` conversion on upload, different memory limits on large canvas
   operations, and different PWA install and storage-eviction rules. It is a
   useful approximation and nothing more.
5. **The backend, in mocked mode.** Mocked runs prove nothing about FastAPI,
   PostgreSQL, credit accounting or export file *contents*. Those belong to
   `backend/tests/` — `test_export.py` already covers the real xlsx and CSV
   output in detail — and to live mode.
6. **PostgreSQL-specific behaviour**, even in live mode: `tests/live/serve.py`
   runs on SQLite. Close enough for the API contract, silent about anything
   PostgreSQL does differently.
7. **Concurrency and multi-user isolation.** Every suite runs as one user.
   Nothing here proves one agency cannot see another's documents.
8. **Anything visual.** There are no screenshot comparisons. A layout can break
   completely with this suite still green.
9. **The upload rejection paths**, because there is nothing to reject yet — see
   the fixture caveat above.
10. **The size of a large multipart body on WebKit.** Playwright's WebKit does
    not report it: `postData()` returns 193 bytes for a 1.2 Mo upload,
    `postDataBuffer()` returns null and `sizes().requestBodySize` returns 0. The
    end-to-end « the compressed bytes are what is actually sent » assertion is
    therefore **skipped on `mobile-375`**, with the skip reason in the spec.
    Compression itself is still proven there, in the page.
11. **« Add to Home Screen » producing a standalone window**, and every other
    install-time behaviour: Playwright never installs the PWA. The manifest is
    validated field by field and every icon is fetched and measured, which is as
    far as automation goes.
12. **Lighthouse PWA and performance scores.** No Lighthouse CI is set up in
    this repository, and adding one was outside this package.

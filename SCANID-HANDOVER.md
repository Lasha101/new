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

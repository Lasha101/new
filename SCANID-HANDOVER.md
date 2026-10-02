# SCANID — HANDOVER

Resume file for the "public site becomes the front door of scanid.fr" work, and for the
application tasks that followed it.

> ## ▶ NEW SESSION? THIS IS ALL YOU NEED — RESUME PROTOCOL
>
> The user may open a new session with nothing but "READ SCANID-HANDOVER.md". That is an
> instruction to **resume the current task (§E) exactly where it stopped, under the same
> constraints and permissions**. Do this, in order:
>
> 1. Read **§0** and obey it for the whole session (no `git add` / `commit` / `push`;
>    `frontend/scanid-site-v5-deploy/` read-only except the edits the user explicitly demands —
>    task E: three files, §E.3; work in stages; update this file after every stage; outside the
>    repository: read **only when needed for the demand**, write only with permission).
> 2. Read **§E** (the current task, 2026-10-02 — website: three removals) first: §E.0 says which
>    stage is next, §E.4 lists the stages. §B.0.3 still holds the environment and the commands
>    (test suites, e2e, lint, build), all valid for §E.
> 3. Check the working tree matches §E.0 (`git status --short`) and compare.
> 4. Continue at the **first stage of §E.4 not marked DONE**. After each stage, mark it `DONE` in
>    §E.4, append its record below §E.4, and update §E.0.
> 5. Keep answering the user in their conversation language; keep the UI in French.
> 6. **Task D (« Sexe ») is committed `cfbcd58`, pushed and live** (§D.7.4 steps 1–4 ticked). Still
>    open: the user's checks, §D.7.3 steps 5–7 (workflows, journal + column on the VPS, acceptance).
>    Guide them **one command per message** (the user's rule, §D.0) when the user returns to them.
>    Once §D.0 says **SHIPPED**, §D is a record.
>
> §A (task A — committed `a2b235d`, pushed), §B (committed `b3028b4`, live), §C (committed
> `68dde4a`) and §1–§9 (the v5 site task, live) are records only.

Last updated: 2026-10-02 (task E — website, three removals — done and verified, not committed; the user
ships it per §E4. Task D pushed as `cfbcd58` and live; the user's checks §D.7.3 steps 5–7 still open)

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
   in this work writes into it.)* *(Exception demanded explicitly by the user, 2026-10-02,
   task E: the content edits listed in §E.1, in `politique-confidentialite.html`,
   `ressources.html` and `sitemap.xml` of that directory — nothing else in it is written.
   `frontend/site/` no longer exists in the repository.)*
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

## E. CURRENT TASK (2026-10-02) — WEBSITE: THREE REMOVALS

### E.0 State in one line (update after every stage)

**E0–E4 DONE — the three removals are made and verified (source 25/25, dist 10/10, build + guard 5/5,
unit 88, browser desktop + phone, e2e 439 passed / 1 skipped). NEXT: the user ships it — §E4 "how to
ship", then the laptop checks listed there.** Nothing committed (§0.3). Git at the start of task E: `master` = `origin/master` = `cfbcd58`
(task D), only `SCANID-HANDOVER.md` modified (task D's progress ticks). Expected `git status --short` after
E2: ` M SCANID-HANDOVER.md` + ` M` `frontend/scanid-site-v5-deploy/{politique-confidentialite.html,
ressources.html,sitemap.xml}` — nothing else.

### E.1 The demand, verbatim (user, 2026-10-02)

> CRUCIAL you have the same restrictions and permissions!
> Website — three removals!
> Make only these changes:
>     • From politique-confidentialite.html remove the two Georgia mentions (the list item « Développement
>       et maintenance de l’application : prestataire technique situé en Géorgie… » and the sentence « Le
>       prestataire technique en charge du développement (Géorgie)… »); « Dernière mise à jour : septembre
>       2026 ».
>     • From ressources.html remove the « Témoignages » card (it linked to temoignages.html).
>     • From sitemap.xml remove the lines for /iftm/ and /temoignages.html; lastmod 2026-09-30 for the two
>       changed pages.
> CRUCIAL you read outside of the current directory if and only if it is needed to respect my prompt's
> demands!
> CRUCIAL you test after changes to be sure that all is correctly implemented!

### E.2 Findings before touching anything

1. The three files exist in `frontend/scanid-site-v5-deploy/` (tracked; the site's source, the only
   directory `scripts/assemble-site.mjs` reads — constant `SITE`) and in `frontend/dist/` (gitignored,
   regenerated by `npm run build` = `vite build && node scripts/assemble-site.mjs` in « Deploy », then
   rsynced). `frontend/site/` no longer exists. → Only an edit of the source reaches scanid.fr.
2. The assembler's rewrites are technical (« Connexion » links, fonts, inline scripts) — « None of them
   changes what the page says »; non-HTML files (`sitemap.xml`) are copied byte for byte.
3. Targets in the source (line numbers at `cfbcd58`):
   - `politique-confidentialite.html` l.144: `<li><strong>Développement et maintenance de
     l'application</strong>&nbsp;: prestataire technique situé en Géorgie, sans accès … (accès limité au
     code source de l'application).</li>` — 3rd of the 5 items of §5 « Destinataires et sous-traitants »;
     l.150 (§6 « Transferts hors Union européenne »): the sentence « Le prestataire technique en charge du
     développement (Géorgie) n'a pas accès aux données à caractère personnel. » between « …région Union
     européenne. » and « Lorsqu'un prestataire implique… »; l.170: `<p class="upd">Dernière mise
     à jour&nbsp;: juillet 2026.</p>`. « Géorgie » appears nowhere else in the site.
   - `ressources.html` l.179–185: `<a href="temoignages.html" class="card">` … `</a>` (⭐ « Preuves »,
     « Témoignages »), 5th of the 6 cards of `.grid`. It is the **only** link to `temoignages.html` in the
     site (apart from that page's own canonical).
   - `sitemap.xml` (21 `<url>`, one per line): l.6 `/iftm/`, l.11 `/temoignages.html`; `ressources.html`
     and `politique-confidentialite.html` both `<lastmod>2026-07-04</lastmod>`. Nothing in the site links
     to `/iftm/`. `robots.txt` points at the sitemap — unchanged.
4. No test pins any of this content (grep of `src/`, `tests/`, `scripts/`); `sitenav.spec.js` only checks
   the app menu's link to `ressources.html` (kept). The app links to `ressources.html` and
   `politique-confidentialite.html` by URL only.
5. Not demanded, therefore not touched: `temoignages.html` and `iftm/index.html` stay in the build and are
   still served at their URLs — after task E nothing links to them and the sitemap no longer lists them.

### E.3 Decisions

1. **Edit the three files in `frontend/scanid-site-v5-deploy/`** — the only tracked copy, the only one the
   build reads. The "source of truth is read-only" rule of §0.5 / §9 is the assistant's own derived rule
   for the v5 task; the user's explicit demand names these three files, so exactly these edits are made
   there and nothing else in that directory. `frontend/dist/` is rebuilt by `npm run build`, never
   hand-edited.
2. Exact form kept: « Dernière mise à jour&nbsp;: septembre 2026. » (only the month changes); the §6
   paragraph loses exactly that sentence and the space before it; the list item and the card are removed
   with their whole lines.
3. `lastmod` = **2026-09-30** as demanded (not today's date), for `ressources.html` and
   `politique-confidentialite.html` only; the other 17 entries unchanged.

### E.4 Stages

| Stage | Content | Status |
| --- | --- | --- |
| E0 | Survey (files, build path, tests, links) | **DONE** |
| E1 | Write the demand, findings and plan here | **DONE** |
| E2 | The edits — 3 source files | **DONE** |
| E3 | Verification: diff = only the demanded lines; content checks; HTML tag balance HEAD vs new; sitemap well-formed, 19 URLs; `VITE_API_URL=/api npm run build` + the `dist/` copies; build guard; unit; both pages rendered in a browser (desktop + phone); full e2e | **DONE** |
| E4 | Record + how to ship | **DONE** |

### Stage E2 — the edits — DONE

`git diff --stat`: 3 files, 4 insertions, 14 deletions — all in `frontend/scanid-site-v5-deploy/`:
- `politique-confidentialite.html`: the §5 `<li>` « Développement et maintenance de l'application … Géorgie … »
  removed (whole line); in §6 the sentence « Le prestataire technique en charge du développement (Géorgie)
  n'a pas accès aux données à caractère personnel. » removed with its leading space (the paragraph now
  reads « …région Union européenne. Lorsqu'un prestataire… »); « Dernière mise à jour&nbsp;: juillet
  2026. » → « septembre 2026. ».
- `ressources.html`: the 7 lines of the `<a href="temoignages.html" class="card">` card removed.
- `sitemap.xml`: the `/iftm/` and `/temoignages.html` lines removed; `<lastmod>` 2026-07-04 → **2026-09-30**
  for `ressources.html` and `politique-confidentialite.html`.

### Stage E3 — verification (record; e2e last)

- [x] Source checks (`check_site_e.py`, stdlib Python, scratchpad — rebuildable from this list): **25/25**.
      Each file == its `HEAD` version with only the demanded edits applied, **byte for byte**; no « Géorgie »
      (case-insensitive); « Dernière mise à jour&nbsp;: septembre 2026. » once, « juillet 2026 » gone; §5 list
      5 → 4 items; §6 joined with one space; LF kept; HTML tags balanced, 0 issues before and after. The page has
      **two** grids: « Articles » (5 cards) unchanged; « Outils & guides » 6 → 5 cards, same order
      (alternatives, guide, guide-photo, faq, securite). Sitemap well-formed, 21 → 19 `<url>`, entries == `HEAD`
      minus the 2, lastmod 2026-09-30 for the 2 pages, the 17 others identical and in order, every remaining
      `<loc>` is a page of the site; `temoignages.html` and `iftm/index.html` untouched.
- [x] `VITE_API_URL=/api npm run build`: ok — `assemble-site: 34 files into dist/ (22 pages rewritten)`, the
      same figures as the v5 record (§5 Stage 4). `check_site_e.py --dist`: **10/10** (`dist/sitemap.xml`
      byte-identical to the source; both `dist/` pages carry the edits, tags balanced; `temoignages.html` and
      `iftm/` still shipped; `dist/app/` present).
- [x] Build guard `node --test tests/build/no-google-fonts.test.js` **5/5**; `npm run test:unit` **88/88**.
- [x] Browser (`render_e.cjs`, Chromium of `@playwright/test`, `dist/` served by `python3 -m http.server` on
      127.0.0.1:8093 — stopped after): desktop 1280 and phone 375, **all checks ok** — « Outils & guides » 5
      cards (desktop 3 + 2, like « Articles »; phone one column), « Articles » 5 unchanged, no link or text
      « Témoignages », no « Géorgie », §5 = Hébergement · OCR · Formulaires · Paiement, §6 « …région Union
      européenne. Lorsqu'un prestataire… », « Dernière mise à jour : septembre 2026. », no horizontal overflow,
      no console error / failed request. Screenshots looked at (scratchpad; no personal data).
- [x] Full e2e `npx playwright test` (all projects, incl. `pwa` on a fresh build): **439 passed, 1 skipped**
      (3.8 min, exit 0) = after task D. Servers stopped, ports 5173 / 4173 / 8093 free; `git status --short` =
      the 4 files of §E.0, nothing else.

### Stage E4 — how to ship task E — DONE

**Files** (uncommitted, §0.3): ` M SCANID-HANDOVER.md` + ` M frontend/scanid-site-v5-deploy/`
`politique-confidentialite.html`, `ressources.html`, `sitemap.xml`. `git add --dry-run .` must list exactly
these 4. No backend, database, `.env`, nginx or service change; site only.
**`.gitignore` review before the commit (2026-10-02, at the user's request):** `git status --porcelain
--untracked-files=all` = exactly these 4, no untracked file; `git ls-files -ci --exclude-standard` = none;
tracked sensitive-looking names = `backend/.env.example` (empty placeholders) and the site's public
`ScanID-Checklist-RGPD.pdf` only. Ignored, each by an explicit rule and rightly so: the two real identity
PDFs, `backend/.env`, `backend/bench_ocr.py` + `bench_result_*.json` (real data), `frontend/.env.local`,
`dist/`, `test-results/`, `tests/.browser-libs/`, `tests/fixtures/files/` (regenerated by `pretest:unit`),
`newvenv/`, `site.html` / `site1.html`. Nothing to add to `.gitignore`, nothing ignored that must ship.

**The user ships it** (one command per message if guided, as in §D.7):
```bash
git add --dry-run .     # exactly the 4 files
git add .
git commit -m "Site: remove the Georgia mentions, the Témoignages card and two sitemap entries"
git push origin master  # « CI » + « Deploy »: npm run build (assembler) → rsync dist → restart → health checks
```

**After the deploy — checks from the laptop** (public GETs, the assistant may run them):
```bash
curl -s https://scanid.fr/sitemap.xml | grep -c '<url>'                                   # 19
curl -s https://scanid.fr/sitemap.xml | grep -c -E 'iftm|temoignages'                   # 0
curl -s https://scanid.fr/sitemap.xml | grep -E 'ressources|politique'                  # both 2026-09-30
curl -s https://scanid.fr/ressources.html | grep -c -i 'temoignages'                     # 0
curl -s https://scanid.fr/politique-confidentialite.html | grep -c -i -E 'g(é|e)orgie'   # 0
curl -s https://scanid.fr/politique-confidentialite.html | grep -c 'septembre 2026'      # 1
```

**Not demanded, therefore not done:** `temoignages.html` and `/iftm/` are still built and still answer at
their URLs — nothing links to them any more and the sitemap no longer lists them, but a search engine that
already indexed them keeps them until it drops them (deleting the pages or a `noindex` would be a separate
demand). **With task D:** independent; pushing E restarts the backend once more, which is harmless (D's
step 6 searches the whole day for that reason).

---

## D. TASK D (2026-10-02) — NEW COLUMN « SEXE » — PUSHED `cfbcd58`, LIVE; USER CHECKS 5–7 OPEN

### D.0 State in one line (update after every stage)

**CODE DONE AND VERIFIED (D0–D6). PUSHED AND LIVE — the user's checks §D.7.3 steps 5–7 still open.**
Do not re-implement anything. The user runs every deploy step; the assistant never
`git add` / `commit` / `push` (§0.3) and never connects to the VPS without explicit permission.

**Deploy position (2026-10-02): steps 1–4 ticked** (all 7 tables owned by `travelapp` → step 3 not needed;
commit `cfbcd58` pushed — remote `master` = `cfbcd58`). §D.7.5 right after: C = `401`, D =
`/app/assets/index-BPW7hBrE.js` with 1 × « Sexe » → the new backend started (so its startup migration
succeeded: had the ALTER failed, the API would be down) and the new frontend is live. **Open:** step 5 (the
user looks at « CI » / « Deploy »), step 6 (journal + column on the VPS), step 7 (acceptance). The user then
switched to task E (§E) before these. At the
user's request (« CRUCIAL one instruction at a time! ») the deploy is guided **one command per message**:
give exactly one command, wait for the user to paste its output, check it, tick §D.7.4, then give the next.

**A new session opened with "Read SCANID-HANDOVER.md" does exactly this:**
1. Find where the deploy stands **on its own**, read-only: the four checks of §D.7.5 (local commit,
   pushed or not, backend up, new frontend live). Compare with the "before" column there.
2. If nothing is committed yet: `git status --short` must list exactly the 21 files below (any other
   difference: report it, do not "fix" it), and the quick baseline must hold —
   `cd backend && ../newvenv/bin/python -m pytest -q` → **328 passed**;
   `cd frontend && npm run test:unit` → **88 passed**.
3. Ask the user only what cannot be seen from the laptop (the owner check of step 2, the journal of
   step 6, the acceptance of step 7), tick §D.7.4, and guide the **first unticked step of §D.7.3**.
   Update §D.7.4 and this paragraph after every step the user reports.
4. When step 7 is ticked: mark task D **SHIPPED** here (commit hash, date), turn §D into a record, point
   the resume protocol at the top to "wait for the next demand", update the memory note.

Known facts to tell the user when relevant: old documents keep an empty Sexe (scans are not stored); the
Vision-quota observation (§D.6, last paragraph). The 2026-10-02 scratchpad was found **empty** when the
session restarted (~12:00, 2026-10-02): the real identity data used in the tests no longer exists —
nothing to delete.

Git at start of task D: `master` = `origin/master` = `68dde4a`, working tree clean. Baseline reproduced
before any change: backend **295 passed**, frontend unit **87 passed**. At the end: backend **328**, unit
**88**, e2e **439 passed / 1 skipped**, eslint = baseline, build + guard ok. Expected `git status --short`
(all uncommitted, §0.3) — 18 modified, 3 new:
` M` SCANID-HANDOVER.md, backend/{main,models,ocr_service,schema_migrations,schemas}.py,
backend/tests/{conftest,test_account_foundation,test_existing_api,test_export,test_ocr_split_cni}.py,
frontend/src/{App.jsx,resultsHelpers.js,resultsHelpers.test.js},
frontend/tests/e2e/{design-system,features}.spec.js, frontend/tests/mock/{api,data}.js;
`??` backend/tests/{test_ocr_sex,test_sex_column}.py, frontend/tests/e2e/sex-column.spec.js.

### D.1 The demand, verbatim (user, 2026-10-02)

> CRUCIAL for this session you have the same constraints and permissions as they are in
> SCANID-HANDOVER.md, all current functionality must be preserevd except what i will demand to
> change, make only necessary changes, outside of this directory you can run commands and see output
> if it is necessary to respond to my prompt's demand, if you need to install or uninstall or delete
> or edit something you should ask me the permission, without it only run the commands to verify and
> test the things, but no dlelting, editing, installing or uninstalling something!
>
> New column « Sexe »
> - Show the holder's sex in the « Mes documents » table and add it to the XLSX and CSV exports,
>   right after « Prénom », with the header « Sexe » and the same rules as the other columns
>   (uppercase, centered).
> - Values F or M, read from the machine-readable zone: passport, line 2, character 21; new ID card,
>   line 2, character 8; older ID card, line 2, character 35. Leave the cell empty when it cannot be
>   read — never guess.
>
> Finally test added column to db, UI, csv and xlsx if there is new column "Sexe"!

Twice during the task (verbatim): « CRUCIAL when you finish current stage update SCANID-HANDOVER.md in
such way that if i tell you in new coversation read SCANID-HANDOVER.md you can constinue = resume current
work without needing any other instruction! » and « Update the SCANID-HANDOVER.md in such way that in the
new conversation you could resume=continue current work with only this command: Read SCANID-HANDOVER.md! »
— hence the resume steps in §D.0 and the rebuildable harness in §D.5. **Standing rule for every future
task:** keep a §X.0 with the exact resume point, update it after every stage (and before any long step),
and point the resume protocol at the top of this file to the current task.

Constraints and permissions: §0, unchanged.

### D.2 Findings before touching anything

1. **The three positions are already isolated by the existing MRZ regexes** (`backend/ocr_service.py`);
   only one character has to be captured, no new matching logic:
   - passport, line 2 (TD3, 44 characters): the `[MFX<]` between the birth-date check digit
     (character 20) and the expiry date in `_parse_passport`'s line-2 regex; and `([MFX])` in
     `PASSPORT_PARTIAL_LINE2_RE` — a scan cropped on the left loses the start of the line, not
     character 21, and that path already verifies both dates' check digits;
   - new CNI, line 2 (TD1, 30 characters): `TD1_LINE2_RE` group 3;
   - old CNI, line 2 (36 characters): `TD2_LINE2_RE` and `TD2_LINE2_RELAXED_RE` group 6.
   No ICAO check digit covers the sex character itself, in any of the three formats.
2. A new-format CNI read from its **front only** (`_parse_cni_new_visual`) has no MRZ on the page →
   Sexe stays empty (the printed « Sexe F » is not the MRZ).
3. **No DB column exists.** `create_all` never adds a column to an existing table, so production needs
   the additive startup migration of task B (`schema_migrations.ADDED_COLUMNS`); its `ALTER TABLE`
   needs the owner of `passports`.
4. Scans are never stored (`test_no_document_persistence.py`) → documents extracted before this change
   cannot be re-read; their Sexe stays empty.
5. UI: `.sid-table th` / `td` (`scanid-app.css`) are `text-transform: uppercase; text-align: center`
   for every column, and the mobile cards uppercase their values → a new column inherits both rules.
   The table and the cards both render `PASSPORT_COLUMN_ORDER` (`resultsHelpers.js`).
6. `passportFields` (App.jsx) drives the « Modifier » / « + Manuel » form, where every field but the
   destination is `required` → `sex` must **not** go there (saving a document with an empty Sexe would
   be blocked). « Modifier » sends back `{...item}` (the stored sex survives); « Modifier Destination »
   sends an explicit field list and `crud.update_passport` uses `exclude_unset=True` (survives too).
7. Exports: `EXPORT_COLUMNS` / `EXPORT_HEADERS` (main.py) drive CSV, XLSX and the Aperçu;
   `_export_cell_value` uppercases, `_format_export_worksheet` centers every cell and sizes the
   AutoFilter from `max_column`. Pytest keeps `EXPORT_COLUMNS` == `PASSPORT_COLUMN_ORDER` and the
   headers == `columnTranslations`.
8. Tests pinning the 9 columns: backend `test_export.py` (headers, indexes, `A1:I`, hidden `J`, `H2`),
   `test_existing_api.py` (`PASSPORT_KEYS`), `test_account_foundation.py` (its migration test assumes
   every `ADDED_COLUMNS` entry is on `users`), `test_ocr_split_cni.py` (`EXPECTED_IDENTITY` compared
   with `==`; its synthetic line 2 carries `F` at character 35); frontend `resultsHelpers.test.js`,
   `tests/mock/api.js` (mirror of `EXPORT_COLUMNS`), `tests/e2e/design-system.spec.js`
   (`BASELINE_EXPORT_HEADERS`).
9. Real-document baseline: `backend/bench_result_{dubrovnik,italie}_check.json` (2026-09-07, gitignored;
   the OCR code has not changed since `8d19b38`, 2026-09-06): DUBROVNIK 29 pages, 27 ok; ITALIE 71
   pages, 61 ok, 6 versos merged.

### D.3 Decisions

1. Field `sex` (English, like the other columns): DB `passports.sex VARCHAR NULL`; API
   `sex: "F" | "M" | null` on `PassportBase` (create, update, response). Header « Sexe ».
2. Only `F` and `M` are kept; `X`, `<` or anything else → empty. Never taken from the visual zone or
   inferred from a first name.
3. Order everywhere (table, cards, Aperçu, CSV, XLSX): Nom de famille, Prénom, **Sexe**, Date de
   Naissance, …
4. Not demanded, therefore not done: a Sexe field in the « Modifier » / « + Manuel » form (a manual
   document has an empty Sexe); a backfill of existing rows (impossible, finding 4).

### D.4 Stages

| Stage | Content | Status |
| --- | --- | --- |
| D0 | Survey + baseline | **DONE** |
| D1 | Write the demand, findings and plan here | **DONE** |
| D2 | OCR: read the sex from the MRZ (3 formats) + synthetic tests | **DONE** |
| D3 | DB column + migration + API + exports (CSV, XLSX, Aperçu) + tests | **DONE** |
| D4 | Frontend table + cards, mock backend, unit + e2e tests | **DONE** |
| D5 | Verification: all suites, lint, build; real OCR on both PDFs vs the D.2.9 baseline; real stack (PostgreSQL with the pre-change schema → migration → upload in the UI → table → CSV + XLSX) | **DONE** (record: §D.5) |
| D6 | Record + how to ship | **DONE** (§D.6) |

### Stage D2 — OCR — DONE

- `backend/ocr_service.py`: new `_mrz_sex(character)` → `'F'` / `'M'` / `None`. The passport line-2
  regex captures its `[MFX<]` (expiry moves from group 4 to 5); `PASSPORT_PARTIAL_LINE2_RE` group 3
  (cropped scans); `TD1_LINE2_RE` group 3; `TD2_LINE2_RE` and `TD2_LINE2_RELAXED_RE` group 6 — each
  taken from the same match as the birth date. Every parser returns `sex` (`_parse_cni_new_visual`:
  always `None`, no MRZ); the old-CNI recto carrier (`OldCniFrontMissingExpiry.partial_data`)
  includes it, so a recto/verso merge keeps the recto's sex. No other field, regex or message changed.
- **New** `backend/tests/test_ocr_sex.py` (22): per format, F/M kept and X/`<` → empty at exactly
  character 21 / 8 / 35 (the fixtures assert their line length and position); visual zone « Sexe F »
  never used (passport with `<`, new-CNI front without MRZ → extracted, Sexe empty); cropped passport;
  tolerant old-CNI line; recto/verso merge; full page cascade with Vision faked. Against the original
  `ocr_service.py` (scratch copy) **19 of 22 fail** — the 3 that pass are the fixture checks.
- `backend/tests/test_ocr_split_cni.py`: `EXPECTED_IDENTITY` gains `"sex": "F"` (its synthetic line 2
  has `F` at character 35) — the 3 tests comparing with `==` failed without it, as expected.
- OCR suites: **57 passed** (35 existing + 22 new).

### Stage D3 — DB, API, exports — DONE

- `backend/models.py`: `Passport.sex = Column(String, nullable=True)`.
- `backend/schema_migrations.py`: `("passports", "sex", "VARCHAR")` in `ADDED_COLUMNS` + its manual SQL
  in the docstring: `ALTER TABLE passports ADD COLUMN IF NOT EXISTS sex VARCHAR;`.
- `backend/schemas.py`: `PassportBase.sex: Optional[Literal["F", "M"]] = None` — POST/PUT refuse
  anything else (422); a body without `sex` leaves it empty (create) or untouched (update).
- `backend/main.py`: `EXPORT_COLUMNS` gets `"sex"` after `"first_name"`, `EXPORT_HEADERS["sex"] =
  "Sexe"`. Nothing else: uppercase, centering, AutoFilter, widths, CSV rules and the Aperçu all follow
  from these two lists.
- Moved here from D4 because the backend parity tests read them: `frontend/src/resultsHelpers.js`
  `PASSPORT_COLUMN_ORDER` gets `'sex'` after `'first_name'`; `frontend/src/App.jsx`
  `columnTranslations.sex = 'Sexe'`.
- Tests: fixture `user_with_documents` (conftest) gets F / M / F / empty (the new CNI) / F;
  `test_export.py` follows the 10 columns (headers, indexes, `A1:J`, hidden `K…XFD`, letters) and
  asserts the Sexe values in CSV (`""` when unknown), XLSX (empty cell) and the Aperçu, and the order
  `[:3] == last_name, first_name, sex`; `test_existing_api.py` `PASSPORT_KEYS` + `sex`;
  `test_account_foundation.py` migration test filters `ADDED_COLUMNS` on `users`. **New**
  `tests/test_sex_column.py` (11): migration of the exact pre-change `passports` table with a row
  (column added, nullable, row intact with empty Sexe, idempotent), manual SQL listed, API returns
  F / null, manual creation empty, `X` `<` `f` `FEMME` `""` → 422, « Modifier » and « Modifier
  Destination » both keep the sex, an OCR job stores F / M / NULL.
- Mutation check (scratch copy, one file back to `HEAD` at a time): models → 12 failed + 24 errors,
  schemas → 14 failed, schema_migrations → 2 failed, main → 19 failed.
- Backend suite: **328 passed** (295 + 22 + 11).

### Stage D4 — Frontend — DONE

- Production code: only the two lines already done in D3 (`PASSPORT_COLUMN_ORDER`, `columnTranslations`).
  The table and the mobile cards render that list, so both gain « Sexe » after « Prénom »; no CSS change
  (finding 5); `passportFields` untouched (finding 6); sorting works on it like any text column (empty
  cells last).
- `src/resultsHelpers.test.js`: order test (10 columns, Sexe right after Prénom) + new test « Sexe
  shows F / M, empty when not read » → unit **88 passed**.
- Mock backend: `tests/mock/api.js` `EXPORT_COLUMNS` / `EXPORT_HEADERS` mirror + `sex: null` on manual
  creation; `tests/mock/data.js` `sex` on every row (p-1 F, p-2 M, p-3 F, p-4 none, p-5 M, extracted F).
- Specs pinning the old column set: `design-system.spec.js` `BASELINE_EXPORT_HEADERS` + « Sexe »;
  `features.spec.js` mobile sort checkboxes 9 → 10.
- **New** `tests/e2e/sex-column.spec.js` (7 tests): header « SEXE » (innerText) after « Prénom », header
  and cells uppercase + centered with the same computed rules as Prénom; values F / M / empty; sort asc
  F F M M ∅, desc M M F F ∅; « Modifier » sends the sex back (F stays F) and saves a document without
  sex (`sex: null`, no required field); cards: « Sexe » after « Prénom », uppercase, same rules as the
  Prénom value; Aperçu and both downloads: « Sexe » after « Prénom » with the values. desktop +
  mobile-small + mobile-375: **21 passed**. Mutation (HEAD column order back in place, file restored
  byte-identical): **5 of 7 fail** — the 2 that pass are the Aperçu/download tests, which follow the
  export columns, not the table's.
- eslint: `src/App.jsx` 12 problems (the baseline), every other touched file clean.

### D.5 Stage D5 — verification: sub-steps and the harness — DONE

- [x] Suites after D4: backend **328**; unit **88**; `npx playwright test` (all projects) **439 passed, 1 skipped**
      (418/1 + the 21 new); eslint = baseline (App.jsx 12, every other touched file clean);
      `VITE_API_URL=/api npm run build` ok, build guard **5/5**, the bundle contains « Sexe ».
- [x] Real OCR, `DUBROVNIK.pdf` (`ocr_sex_run.py` + `ocr_sex_check.py`): 29 pages, **27 ok / 2 errors =
      baseline**. Sexe: passports 6 F + 11 M, old CNI 1 F + 3 M, new CNI (MRZ) 3 F, 3 new-CNI fronts
      without MRZ → empty. Oracles: literal position **13 agree, 0 disagree** (14 n/a: OCR line not of
      exact length), printed « Sexe » **4 agree, 0 disagree**. Every name, number, date, nationality
      identical to the 2026-09-07 baseline; `confidence_score` differs on 10 pages by 0.0001–0.019 →
      Vision drift suspected (the score reads names/number/nationality only; the diff does not touch
      it) — proven or refuted by the A/B replay below.
- [x] Real OCR, ITALIE PDF, first run: pages 20, 36, 46, 60, 70 failed with Vision « Resource has been
      exhausted (e.g. check quota) » right after the DUBROVNIK run (external quota); the other errors
      (13, 14, 40, 41) and the 6 recto/verso merges = baseline.
- [x] ITALIE rerun ~10 min later, with `RECORD_DIR`: **still one quota failure** (page 68; a single
      71-page PDF now exhausts the per-minute Vision quota — it did not on 2026-09-07; reported to the
      user, out of scope). 60 ok + 4 known errors + page 68 (read in run 1: new CNI, M, position
      oracle agrees) = the 61 of the baseline; 6 versos. Sexe: passports 16 F + 20 M, old CNI 7 F + 5 M,
      new CNI (MRZ) 4 F + 5 M, 3 fronts without MRZ → empty. Oracles: position **49 agree, 0 disagree**,
      printed « Sexe » **12 agree, 0 disagree**; run 1 also 0 disagree. Names, numbers, dates,
      nationality identical to the baseline; confidence differs on 22 pages (same pattern as DUBROVNIK).
- [x] A/B replay ITALIE (78 recorded responses, 0 misses): `HEAD` vs new code **71/71 pages identical
      apart from `sex`**, confidence included; replay of the new code == the live run on 71/71 pages
      (sex and confidence included) → the confidence deltas against 2026-09-07 are Vision's, not the
      change's.
- [x] Real stack: PostgreSQL 16 with the **pre-change** schema + 1 old document → new backend: the
      startup migration added `passports.sex` (`character varying`, nullable, 11th column), old row
      intact with Sexe NULL → UI upload of `DUBROVNIK.pdf`, real OCR, job « Terminé » in 16 s, credits
      100 → 73 (27 documents, task A rule) → `verify_all.py` **26/26 PASS** (multiset of (number, Sexe)
      pairs — DUBROVNIK holds 2 documents scanned front + back, 28 rows / 26 numbers): DB 10 F / 14 M /
      4 empty (the old row + 3 new-CNI fronts without MRZ) = UI table = Aperçu = cards (375 px) = XLSX
      (real empty cell, centered incl. header, AutoFilter `A1:J29`, 10 columns) = CSV (BOM, `;`);
      header rendered « SEXE », header and cells uppercase + centered with the same computed rules as
      Prénom. Screenshots looked at (scratchpad only, real data). `replay_ab.py` on the 35 responses the
      backend recorded: **29/29 pages identical apart from `sex`**, and the replay equals what the live
      backend stored (number, sex, confidence) on all 27 rows.
- [x] Stopped backend, proxy, PostgreSQL (exit 143 = the SIGTERM); ports 8011 / 8080 / 55433 free.
      `git add --dry-run .` lists exactly the 21 files of §D.0 and nothing is staged.

**Harness** — it lives in the session scratchpad, which a new session does NOT have: rebuild it from this.
1. `ocr_sex_run.py <label> <pdf> <out.json>` — run from `backend/` with `PYTHONPATH=.`. Imports `database`
   (writes the Vision credentials of `.env`) and `ocr_service`; wraps `vision_client.annotate_image` and
   `ocr_service._extract_document_data_from_image_bytes` (thread-local) to attach each page's raw OCR text
   as `_raw_text` (also into `OldCniFrontMissingExpiry.partial_data`); with `RECORD_DIR` set, saves every
   Vision response (`type(r).serialize(r)`) as `<RECORD_DIR>/<sha256 of the image bytes>.pb`. Then
   `extract_data_page_by_page(file_path=…, content_type='application/pdf')` → JSON. Real identity data:
   scratchpad only.
2. `ocr_sex_check.py <baseline.json> <run.json>` — against `backend/bench_result_{dubrovnik,italie}_check.json`
   page by page: same status (data / error / verso), same error text, every field but `sex` / `_raw_text`
   identical. Per document: format, sex, literal-position oracle (MRZ-cleaned OCR lines of exact length
   44 / 30 / 36 → index 20 / 7 / 34), printed-« Sexe » oracle
   (`\bSEXE\b(?:\s*/\s*SEX\b)?\s*[:.]?\s*([MF])\b` on the accent-stripped upper text). Prints no name.
3. `replay_ab.py <pdf> <RECORD_DIR> <out.json>` — from `backend/`, `PYTHONPATH=.`: a fake Vision client
   answers each image from `<sha256>.pb` (`vision.AnnotateImageResponse.deserialize`); runs the PDF through
   the current `ocr_service` and through `git show HEAD:backend/ocr_service.py` loaded as a second module;
   compares page by page.
4. Real stack (`stack/`): `start_pg.sh` (`PATH=/usr/lib/postgresql/16/bin:$PATH`; `initdb -U scanid_admin
   --auth=trust`; `pg_ctl` port **55433** with `-c unix_socket_directories='' -c listen_addresses=127.0.0.1`
   — the scratchpad path exceeds the 107-byte socket limit; `CREATE DATABASE travelapp`).
   `old_models.py` = `git show HEAD:backend/models.py`. `seed_old_schema.py` (from backend/, `DATABASE_URL`
   set): `create_all` with the old models (asserts no `sex`), user `agence@example.com` / `Sexe-Test!!2026`
   (id `u-agence`, 100 credits, `auth.get_password_hash`), passport `p-ancien` (`99ZZ99999`). Backend:
   `run_backend.py` (recorder as in 1, then `uvicorn.run('main:app', host='127.0.0.1', port=8011)`), from
   backend/ with `PYTHONPATH=.` and `DATABASE_URL=postgresql+psycopg2://scanid_admin@127.0.0.1:55433/travelapp
   ENVIRONMENT=development ADMIN_PASSWORD='Girafe!!12Nuage-Admin' SECRET_KEY=local-e2e-secret-not-production
   SESSION_COOKIE_SECURE=0 LOGIN_RATE_LIMIT=30/minute` (Vision credentials from `backend/.env`).
   `proxy.cjs 8080 <repo>/frontend/dist 8011` (site at /, SPA fallback for /app/*, /api/* → backend with the
   prefix stripped, upstream destroyed when the client closes — SSE) over a `VITE_API_URL=/api npm run build`.
   `flow.cjs <outDir> <pdf>` (chromium from `frontend/node_modules/@playwright/test`): login, table before
   the upload, upload + « Lancer l'analyse », wait `.sid-chip--done`, table after + styles, screenshot,
   Aperçu, « Télécharger Excel » / « Télécharger CSV », cards at 375 px → `ui.json`. `verify_all.py <outDir>`
   (from backend/, `DATABASE_URL` set): DB column (`character varying`, nullable) and values ↔ UI table ↔
   Aperçu ↔ cards ↔ XLSX (openpyxl: position, values, centered, AutoFilter `A1:J{n}`) ↔ CSV.
5. Stopping: `pgrep -f run_backend.py`, `pgrep -f proxy.cjs`, then `kill <pid>` (never `pkill -f` with a
   pattern your own command line contains); `pg_ctl -D <stack>/pgdata -m fast -w stop`.
6. Every live pass bills Vision on the Google project production uses (~30 calls for DUBROVNIK, ~80 for
   ITALIE): space them a few minutes apart, never loop them.
7. The scratchpad of the session of 2026-10-02 —
   `/tmp/claude-1000/-home-lasha-Public-new/cc0f6758-978a-44cb-b962-44a9b33d01c0/scratchpad` — held
   real identity data (run JSONs, recorded Vision responses, screenshots, exports) and the harness
   scripts. When the session restarted (~12:00, 2026-10-02) it was found **empty** (recreated): that
   data no longer exists, nothing to delete; rebuild the scripts from the descriptions above if needed.

### D.6 How to ship task D (stage D6)

> The exact step-by-step, with the progress checklist, is the runbook **§D.7** below. This section is
> the background it relies on.

**Files** — nothing is committed (§0.3). The 21 files of §D.0 (18 modified, 3 new); `git add --dry-run .`
lists exactly those. No new dependency (Python or npm).

**Before the deploy — database (once, on the VPS).** The startup migration runs
`ALTER TABLE passports ADD COLUMN sex VARCHAR`, which only the **owner** of `passports` (or a superuser)
may run; the app connects as `travelapp`, a role without any attribute (PROGRESS.md §2.4). Read-only
check: `sudo -u postgres psql -l` (database name), then
`sudo -u postgres psql -d <db> -c "SELECT tablename, tableowner FROM pg_tables WHERE schemaname = 'public';"`.
If `passports` belongs to `travelapp` — very likely: task B's `ALTER TABLE users` worked in production
and both tables were created by the same `create_all` — nothing to do. Otherwise, before the push:
`sudo -u postgres psql -d <db> -c "ALTER TABLE passports ADD COLUMN IF NOT EXISTS sex VARCHAR;"`
(additive, instant, idempotent; the app then skips its own step; `travelapp`'s table privileges cover
the new column, no GRANT needed).
**Verified locally (2026-10-02, scratch PostgreSQL: tables owned by another role, app role without
attributes, `ADMIN_PASSWORD` set as in production):** without the column, the new backend does **not
start at all** — « must be owner of table passports », then startup tries to re-create the admin
(« Email déjà enregistré ») and uvicorn exits with code 3: the whole API, login included, is down and the
deploy's health check (`/destinations/` → 401) fails. After the ALTER as the owner: startup complete,
admin login ok, `sex` written and read back as `travelapp`. If it happens anyway: run that ALTER as the
owner, then `sudo systemctl restart travelapp.service`.

**Deploy** = the user's commit + push to `master` (GitHub Actions `deploy.yml`, unchanged). No `.env`
change, no nginx change, no service change. Backups: nothing to do (`pg_dump` carries the column).

**What users will see.** New extractions: Sexe F / M from the MRZ; empty for a new-format CNI read from
its front only (no MRZ) and when the MRZ says `X` / `<`. **Documents extracted before the deploy keep an
empty Sexe** — their scans are not stored, so they cannot be re-read; re-importing the scan fills it.
The XLSX / CSV now have 10 columns: anything that reads them by column letter shifts by one after
« Prénom » (C = Sexe). « Modifier » / « + Manuel » show no Sexe field (not demanded) — a manual document
has an empty Sexe; an edit keeps the stored one.

**Acceptance on https://scanid.fr after the deploy:** import a passport and a CNI (back with MRZ) →
« Sexe » right after « Prénom », F / M, uppercase, centered; an older row → empty; « Télécharger Excel »
and « Télécharger CSV » → « Sexe » after « Prénom », same values, open in Excel.

**Seen during the tests, not acted on (out of scope):** the Google Vision quota of the project is now
exhausted by a single 71-page PDF (« Resource has been exhausted (e.g. check quota) » on 5 pages, then on
1 page after a 10-minute pause; none on 2026-09-07). Such a page fails with « L'API Google Vision a
renvoyé une erreur : … » — not charged (task A), but missing. Worth a look at the Vision quotas in the
Google Cloud console.

### D.7 DEPLOY RUNBOOK — SHIPPING « SEXE » TO https://scanid.fr — RESUME HERE

> Decided by the user on 2026-10-02: « I want to push the changes on github and deploy! ». **The user
> runs every step below.** The assistant guides, checks what can be checked from the laptop (§D.7.5),
> and ticks §D.7.4 as the user reports — it never `git add` / `commit` / `push` (§0.3) and never
> connects to the VPS without the user's explicit permission.

#### D.7.1 What is being shipped

The 21 files of §D.0: the « Sexe » column — F or M read from the MRZ (passport line 2 character 21,
new CNI line 2 character 8, old CNI line 2 character 35), empty when it cannot be read — right after
« Prénom » in « Mes documents » (table, phone cards, Aperçu) and in the XLSX / CSV downloads; the new
database column `passports.sex`. No new dependency, no `.env` change, no nginx change, no service change.

#### D.7.2 The problem to know before deploying — the database column

- Production's `passports` table has no `sex` column. The new backend adds it **itself** at its first
  start (`backend/schema_migrations.py`: `ALTER TABLE passports ADD COLUMN sex VARCHAR`) and logs
  « Schéma mis à jour : colonnes ajoutées passports.sex ».
- PostgreSQL lets only the table's **owner** (or a superuser) run `ALTER TABLE`; reading and writing
  rows is not enough. The app logs in as **`travelapp`**, a role with no attributes (PROGRESS.md
  §2.4). So the automatic step works only if `travelapp` owns `passports`.
- If it does not, the new backend **does not start at all** — verified locally on 2026-10-02 with a
  production-like setup (tables owned by another role, app role without attributes, `ADMIN_PASSWORD`
  set): « must be owner of table passports », then startup tries to re-create the admin
  (« Email déjà enregistré ») and uvicorn exits with code 3. Result: API down — nobody can log in, no
  documents, no exports; the deploy's health check fails (`000` instead of `401`). The public site and
  the app shell still load.
- Prevention: step 2 (a 10-second read-only check) and, **only if needed**, step 3 (add the column by
  hand as the superuser **before** the push). Verified locally the same day:
  - after the column is added by the owner, the new backend starts, the admin logs in, and `travelapp`
    writes and reads `sex` with its existing table privileges (no GRANT needed);
  - the **current production code** (`68dde4a`) runs normally with the hand-added column (starts,
    creates, lists, edits, exports its usual 9 columns; the column stays empty) — so step 3 is safe
    while the old version still runs, and a rollback (step 9) is safe with the column in place.
- Very likely fine anyway: task B added 9 columns to `users` the same way and is live (logins work), and
  `users` and `passports` were created together by the app's first `create_all`, as the same role.

#### D.7.3 Step by step (the user runs every step)

**Step 1 — laptop, pre-flight** (repository root `/home/lasha/Public/new`):
```bash
git status --short                                   # exactly the 21 files of §D.0
cd backend && ../newvenv/bin/python -m pytest -q     # 328 passed
cd ../frontend && npm run test:unit                  # 88 passed
cd ..
```

**Step 2 — VPS, who owns the tables (read-only, changes nothing):**
```bash
ssh lasha@87.106.22.235       # the sudo account (or root@87.106.22.235 as in PROGRESS.md §5)
sudo -u postgres psql -l      # lists the databases: find the app's one, most likely « travelapp »
sudo -u postgres psql -d travelapp -c "SELECT tablename, tableowner FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;"
```
`sudo -u postgres` = run as the PostgreSQL superuser account, which logs in locally without a password
(peer); `-d travelapp` = the app's database (use the name `psql -l` shows); the SELECT prints the owner of
every table. Expected: `passports | travelapp` and `users | travelapp` → **step 3 not needed**. A line
« could not change directory to "/home/lasha": Permission denied » is harmless (postgres cannot enter
lasha's home folder; the query still runs).

**Step 3 — VPS, ONLY if `passports` is not owned by `travelapp`:**
```bash
sudo -u postgres psql -d travelapp -c "ALTER TABLE passports ADD COLUMN IF NOT EXISTS sex VARCHAR;"
sudo -u postgres psql -d travelapp -c "\d passports"      # last row: sex | character varying
```
Adds one empty, optional column: existing rows untouched, instant, harmless to run twice, safe while the
current version runs.

**Step 4 — laptop, commit and push (the push deploys):**
```bash
git add --dry-run .           # must list exactly the 21 files of §D.0, nothing else
git add .
git commit -m "Add the « Sexe » column (read from the MRZ) to Mes documents and the CSV/XLSX exports"
git push origin master
```

**Step 5 — GitHub, watch both workflows:** https://github.com/Lasha101/new/actions
- « CI » — backend tests, boot on a fresh PostgreSQL 16, frontend build and unit tests → green.
- « Deploy » — frontend build, rsync to `/opt/travelapp`, `pip install`, `systemctl restart
  travelapp.service`, health checks → green, last line « Deployed; the site answers /, the app answers
  /app/, and the API proxies. ». A « NOTE: nginx not reloaded … » line is normal (the deploy account may
  only restart `travelapp.service`; task D changes no nginx file).
- « ERROR: backend health check returned 000 » (or `502`) → **step 8**.

**Step 6 — VPS, the column and the startup log:**
```bash
sudo journalctl -u travelapp.service --since "2026-10-02" --no-pager | grep -E "Schéma mis à jour|Database startup check failed|must be owner|startup failed"
sudo -u postgres psql -d travelapp -c "SELECT sex, count(*) FROM passports GROUP BY sex;"
```
(`--since "2026-10-02"`, not "30 min ago": the push of `cfbcd58` was ~09:30 UTC that day, and every later
deploy — e.g. task E's — restarts the backend again without printing that line, the column being there.)
Expected: « Schéma mis à jour : colonnes ajoutées passports.sex » (absent if step 3 added the column by
hand — fine), **no** « Database startup check failed »; every existing row has an empty `sex` (normal:
old scans are not stored, so they cannot be re-read).

**Step 7 — acceptance on https://scanid.fr/app/** (a normal customer account; each import costs one
credit per document and uses Google Vision):
1. Open the app: it reloads itself once onto the new version (service worker); if « SEXE » is not
   there, reload the page once.
2. « Mes documents »: column « SEXE » right after « PRÉNOM », centered; existing rows empty.
3. Import a passport and a CNI back (with its MRZ) → F or M; the front of a new CNI alone → empty.
4. « Télécharger Excel » → column C « Sexe » after « Prénom », centered, F / M / empty, filter
   dropdowns; « Télécharger CSV » → same column and values; both open in Excel.
5. Phone: each card shows « Sexe » after « Prénom ».
6. « Modifier » a document and save → its Sexe is unchanged.

**Step 8 — ONLY if the API is down after the push** (health check `000` / `502`, login fails):
```bash
sudo journalctl -u travelapp.service -n 60 --no-pager     # look for « must be owner of table passports »
sudo -u postgres psql -d travelapp -c "ALTER TABLE passports ADD COLUMN IF NOT EXISTS sex VARCHAR;"
sudo systemctl restart travelapp.service
sleep 3; curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8001/destinations/   # 401 = back up
```
Then (optional) « Re-run jobs » on the failed « Deploy » run so its checks go green, and continue at
step 6. If the journal shows another error, copy it to the assistant before doing anything else.

**Step 9 — rollback, only if something else is wrong and cannot be fixed quickly:**
```bash
git revert --no-edit HEAD && git push origin master       # redeploys the code of 68dde4a
```
The previous code works with the `sex` column present (verified) — leave the column in place.

#### D.7.4 Progress — ticked by the assistant as the user reports each step

- [x] 1 Pre-flight on the laptop — `git status` = the 21 files, backend 328, unit 88 — **done 2026-10-02**
      (run by the assistant on resume: §D.7.5 A–D = the "before" column; 21 files; backend 328 passed; unit
      88 passed)
- [x] 2 Owner of `passports`: **`travelapp`** · owner of `users`: **`travelapp`** · database name:
      **`travelapp`** (the only app database on the server, itself owned by `travelapp`). All 7 public tables
      — auth_tokens, ocr_jobs, passports, purchases, trial_requests, users, voyages — are owned by `travelapp`
      (2026-10-02, the user's output)
- [x] 3 Column added by hand: **not needed** — `travelapp` owns `passports`, so the startup migration adds it
- [x] 4 Commit **`cfbcd58`** (21 files, 1139+ / 79−, parent `68dde4a`; dry run = the 21 files) — committed by
      the user 2026-10-02 · pushed to `master`: **yes** (`git ls-remote`: remote `master` = `cfbcd58`).
      Evidence for step 5 seen from the laptop (not a substitute for the user's look at the workflows):
      API `401`, live bundle `index-BPW7hBrE.js` with « Sexe »
      (From here on `SCANID-HANDOVER.md` shows as modified: these ticks are written after the commit —
      expected, it goes into a later commit; it does not affect the deploy.)
- [ ] 5 « CI » green · « Deploy » green
- [ ] 6 Column present, no startup error, existing rows empty
- [ ] 7 Acceptance on https://scanid.fr (items 1–6)
- [ ] 8 Recovery: not needed / done
- [ ] Shipped → §D.0 marked SHIPPED (hash, date); §D becomes a record; memory note updated

#### D.7.5 How a new session finds the position on its own (read-only, from the laptop)

```bash
cd /home/lasha/Public/new
git log -1 --oneline && git status --short                     # A: local commit and tree
git ls-remote origin refs/heads/master; git rev-parse HEAD      # B: pushed?
curl -s -o /dev/null -w '%{http_code}\n' https://scanid.fr/api/destinations/            # C: backend up?
JS=$(curl -s https://scanid.fr/app/ | grep -o '/app/assets/index-[^"]*\.js' | head -1)  # D: new
echo "$JS"; curl -s "https://scanid.fr$JS" | grep -o 'Sexe' | wc -l                      #    frontend?
```

| Check | Before the deploy (measured 2026-10-02) | After a good deploy |
| --- | --- | --- |
| A — local | `68dde4a`; the 21 files modified | the task-D commit; clean tree |
| B — pushed | remote `master` = `68dde4a…` = local `HEAD` | remote `master` = local `HEAD` = the task-D commit |
| C — backend | `401` | `401` (`502` / `000` → step 8) |
| D — frontend | `/app/assets/index-C_VTLlgs.js`, `0` × « Sexe » (task C's footer present) | another file name, ≥ 1 × « Sexe » |

What the laptop cannot see — the owner (step 2), the journal (step 6), the acceptance (step 7) — is asked
of the user. Then tick §D.7.4 and guide the first unticked step. The checks above are plain GETs on the
public site and read-only git commands; nothing is sent to the VPS from here.

---

## C. TASK C (2026-09-30) — LOGIN-PAGE FOOTER, AND THE TWO `/api/config` SWITCHES — RECORD ONLY

> Committed as `68dde4a` (« Fix the login page footer and identifier label »). The C2 steps (§C.5)
> are still the user's and Alex's.

### C.0 State in one line

**C1 (five login-page fixes): DONE locally, uncommitted.** **C2 (the two switches): no code
change is needed or was made** — both flags are already environment-driven and correct; what
remains is on the server and in Stripe, and only the user and Alex can do it (§C.2).

Task B (§B) is no longer pending: it was committed as **`b3028b4`** (2026-09-14) and is live —
`https://scanid.fr/api/config` answers, which is a task-B endpoint. §B is a record from here on.

### C.1 The demand, verbatim (user, 2026-09-30)

> **1. Five small fixes on the login page.** Seen on https://scanid.fr/app/. Apply the same footer
> wherever it appears in the app.
>
> | Now | Change to |
> | --- | --- |
> | Footer links « Mentions Légales », « Politique de Confidentialité », « CGU », « Contact » all point to `#` | https://scanid.fr/mentions-legales.html · https://scanid.fr/politique-confidentialite.html · https://scanid.fr/cgv.html · https://scanid.fr/contact.html |
> | « © 2026 Gestionnaire de Voyages - Tous droits réservés. » | « © 2026 ScanID — Tous droits réservés. » |
> | « CGU » | « CGV » (the site publishes CGV; there is no CGU page) |
> | « Mentions Légales », « Politique de Confidentialité » | « Mentions légales », « Politique de confidentialité » (French capitalisation) |
> | Login field « Nom d'utilisateur », placeholder « Entrez votre identifiant » | « E-mail », placeholder « vous@agence.fr » — the identifier is the email (Spec v2) |
>
> Test: from /app/, each footer link opens the right page of scanid.fr; the footer reads ScanID.
>
> **2. Two switches in GET /api/config.** Today it returns `{"signup": false, "trial": false}`.
> Turn each one on only after its test:
> - `trial` → `true` — after one real run with Alex: (1) Alex submits https://scanid.fr/essai.html
>   with a test address of his; (2) the notification arrives at contact@scanid.fr and the request
>   appears in « Demandes d'essai »; (3) Valider → welcome email → set-password link works (48 h) →
>   login shows 20 credits; (4) remove the test account, then set `trial` to true. The current trial
>   form already uses the endpoint whatever this flag says; the new site will read the flag to choose
>   its confirmation message.
> - `signup` → `true` — once the Stripe webhook is in place: (1) Alex creates the endpoint in his
>   Stripe dashboard (Développeurs → Webhooks → https://scanid.fr/api/stripe/webhook, event
>   `checkout.session.completed`) and gives the signing secret through the dashboard, never by chat;
>   (2) store it as an environment variable, run one purchase in test mode and replay the webhook —
>   credits are added once; (3) set `signup` to true. The site's « Souscrire » buttons then open
>   /app/inscription?pack=… instead of going straight to Stripe (already handled by
>   `/scripts/index-1.js`).

Constraints and permissions: unchanged, §0 — all current functionality preserved except what is
demanded; only necessary changes; no `git add` / `commit` / `push`; outside the repository, read and
run to verify, but never install/delete/edit without asking.

### C.2 Findings before touching anything

1. **The app has exactly one footer** — `frontend/src/App.jsx`, the `<footer className="sid-appfoot">`
   of the login view. "Wherever it appears in the app" is therefore that one place; no other
   component, page or built HTML file renders it (`grep -rn "sid-appfoot\|legal-links\|<footer"`).
2. **The four target pages exist and answer 200** on https://scanid.fr; `cgu.html` answers **404** —
   which is why « CGU » had to become « CGV ».
3. **The login field must stay `type="text"`.** Customer accounts do have the email as `user_name`
   (`trials.py` and `main.py` both create users with `user_name=email`), but the bootstrap `admin`
   account does not, and `auth.authenticate_user` matches `user_name` exactly. Making the input
   `type="email"` would let the browser refuse « admin » before the request left the page. Only the
   label and the placeholder changed.
4. **The two flags are not stored switches — they are derived from the environment**, and have been
   since task B: `backend/main.py` `public_config()` returns
   `{"signup": bool(config.stripe_webhook_secret()), "trial": mailer.is_configured()}`. So there is
   nothing to change in the code, and **no separate "set it to true" step exists**: the flag flips
   the moment `STRIPE_WEBHOOK_SECRET` (resp. `SMTP_HOST`) is in `/opt/travelapp/backend/.env` and the
   service restarts. Verified live: `curl https://scanid.fr/api/config` → `{"signup":false,"trial":false}`,
   i.e. production currently has neither the SMTP credentials nor the Stripe secret.
5. **Consequence the demand's ordering does not allow for** — reported to the user, no code written
   for it without their decision:
   - `trial`: the test itself needs email (the endpoint answers 503 without it and essai.html falls
     back to Formspree), so `trial` is already `true` while Alex runs steps 1–3. **Harmless today**:
     nothing reads the flag yet — the live essai.html posts to the endpoint regardless, and only the
     future site will use the flag to pick a confirmation message.
   - `signup`: **not harmless.** The live site already reads it —
     `https://scanid.fr/scripts/index-1.js` fetches `/api/config` and, when `signup` is true,
     redirects every « Souscrire » click to `/app/inscription?pack=…`. So storing a **test-mode**
     signing secret to run step 2 switches the real buying flow for real visitors, while the live
     Payment Links stay live and a live webhook would then fail signature verification. Either run
     the test in a short window with `STRIPE_PAYMENT_LINK_*` pointed at the test links
     (`backend/.env.example` documents them), or add a tri-state override
     (`PUBLIC_SIGNUP=0/1`, empty = infer — the pattern `SESSION_COOKIE_SECURE` already uses) so the
     secret can be installed with the flag held off. **The user's call; not implemented.**

### C.3 C1 — what changed (three files, all in the repository)

| File | Change |
| --- | --- |
| `frontend/src/App.jsx` | New `LEGAL_LINKS` constant beside the existing `SITE_LINKS` (same `SITE_URL` base, same shape), rendered by the footer in place of the four `href="#"` anchors; copyright « © {year} ScanID — Tous droits réservés. »; login label « E-mail » and placeholder « vous@agence.fr » |
| `frontend/tests/helpers/selectors.js` | `usernamePlaceholder` follows the new placeholder — `auth.js`, `signup.spec.js` and `password.spec.js` find the login field by it |
| `SCANID-HANDOVER.md` | This §C |

The year stays `new Date().getFullYear()` (it renders « © 2026 » today) rather than a hard-coded
2026: the line was already dynamic, and making it static was not asked for. Note the site's own
pages hard-code « © 2026 ScanID · Tous droits réservés » with a middle dot — the app now follows the
user's wording (em dash, final period), which is deliberate and differs from the site by one glyph.

### C.4 C1 — verification (2026-09-30)

| Check | Result |
| --- | --- |
| `cd backend && ../newvenv/bin/python -m pytest -q` | **295 passed** (baseline) |
| `cd frontend && npm run test:unit` | **87 passed** (baseline) |
| `cd frontend && npx playwright test` (all projects) | **418 passed, 1 skipped** (baseline) |
| `npx eslint .` | **12 problems (7 errors, 5 warnings)** — the documented baseline, none on a touched line; `tests/helpers/selectors.js` clean |
| `npm run build` | ok; `dist/app/assets/*.js` contains the four URLs, « ScanID — Tous droits », « vous@agence.fr » and **no** « Gestionnaire de Voyages », « CGU », « Entrez votre identifiant » |
| Rendered check (`vite preview` + Playwright, screenshot) | footer: Mentions légales → `https://scanid.fr/mentions-legales.html`, Politique de confidentialité → `…/politique-confidentialite.html`, CGV → `…/cgv.html`, Contact → `…/contact.html`; « © 2026 ScanID — Tous droits réservés. »; login label « E-mail », placeholder « vous@agence.fr » |
| Targets live | `mentions-legales.html`, `politique-confidentialite.html`, `cgv.html`, `contact.html` → **200**; `cgu.html` → **404** |

Not yet done: the acceptance test as worded ("from /app/, each footer link opens the right page")
runs on https://scanid.fr and therefore needs the deploy, which is the user's commit + push.

### C.5 C2 — what is left, and who does it

Nothing to write. The steps are the ones already recorded in §B.5 / §B.6.1–2, unchanged:

1. **Email (turns `trial` on).** In `/opt/travelapp/backend/.env`: `SMTP_HOST=smtp.ionos.fr`,
   `SMTP_USERNAME=contact@scanid.fr`, `SMTP_PASSWORD=<mailbox password>`; leave the commented
   defaults out. Restart `travelapp.service`. Then Alex's run: essai.html → « Demandes d'essai » →
   Valider → welcome email → set-password link (48 h) → login → « Crédits : 20 » → delete the test
   account. `/api/config` shows `"trial": true` from the restart, not from the end of the run (§C.2.5).
2. **Stripe (turns `signup` on).** Alex creates the endpoint and hands over the signing secret
   through the dashboard, never by chat; it goes in `STRIPE_WEBHOOK_SECRET`. The code already
   handles `checkout.session.async_payment_succeeded` as well — subscribing to it too is what makes
   a delayed payment (bank transfer) credit; with `checkout.session.completed` alone such a payment
   is never credited automatically. Read §C.2.5 before installing a test-mode secret on production.

---

## B. TASK B (2026-09-14) — THE NINE-ITEM ACTION LIST — RECORD ONLY

> Shipped: committed `b3028b4` and live. The "uncommitted" wording below is the record as it
> stood on 2026-09-14; read it as history. Its §B.5 / §B.6 server steps are still the reference
> for §C.5.

### B.0 RESUME POINT — read this first, keep it current

#### B.0.0 THIS CONVERSATION — WHAT IS DONE, WHAT IS STILL TO IMPLEMENT

Every demand the user made in this conversation (2026-09-14), in order. Keep this table current.

| # | Demand (user's words, short) | Status | Where it is |
| --- | --- | --- | --- |
| A1 | Charge credits only for successful extractions (10 credits, 3 ok + 2 failed → 7 left) | **DONE, committed `a2b235d`, pushed** | §A, `backend/main.py` `_run_ocr_extraction_job`, `backend/tests/test_credit_charging.py` |
| A2 | « Ajouter un Passport » → « Ajouter un Document » | **DONE, committed `a2b235d`** — then superseded by item 4 below | §A |
| A3 | Credits badge from the top bar to just under « Bienvenue, …! » | **DONE, committed `a2b235d`, pushed** | §A, `frontend/src/App.jsx` Dashboard nav, `scanid-app.css` `.sid-credits` |
| B-1 | Actionable failure message under the failed file | **DONE (uncommitted)** | Stage B2 record |
| B-2 | App shell: title « ScanID — Espace client », `lang="fr"`, site favicon | **DONE (uncommitted)** | Stage B3 record |
| B-3 | Password reset: « Mot de passe oublié ? » → email → 48 h link | **DONE (uncommitted)** — real SMTP end-to-end run still in B12 | Stages B5, B6 |
| B-4 | Vocabulary (Alex): heading, « Mes documents », « Documents traités », PP, « Numéro de document », empty state, placeholder | **DONE (uncommitted)** | Stage B4 record |
| B-5 | Trial automation: `POST /api/trial-requests`, pending user 20 credits, email to contact@, « Demandes d'essai » Valider/Refuser, welcome email with set-password link, 30-day purge | **DONE (uncommitted)** — essai.html → email → login run on a real stack still in B12 | Stages B5, B7 |
| B-6 | Account before payment: `/app/inscription`, Stripe Payment Link redirect, signed idempotent webhook, `GET /api/config` | **DONE (uncommitted)** — backend + page + tests; real-stack webhook run in B12; real Stripe test mode needs Alex's keys | Stage B8 record |
| B-7 | Mon Compte: société, SIRET, TVA, adresse de facturation; « Mes achats » | **DONE (uncommitted)** | Stage B9 record |
| B-8 | Site menu in the app top bar, logo → scanid.fr, « Retour au site » on mobile | **DONE (uncommitted)** | Stage B10 record |
| B-9 | 12 h inactivity logout · rate limits login/upload · highlight confidence < 0.8 · daily encrypted pg_dump with tested restore | **DONE (uncommitted)** — rate limits and backups verified, no change to them; a logout/renewal race found in B12 and fixed | Stage B11 + B12 records |
| B-V | Full verification: all suites, lint, build, real end-to-end on PostgreSQL + SMTP sink + local proxy, screenshots | **DONE** — all suites green; every real flow passed on PostgreSQL + SMTP sink + proxy; a logout/renewal race found and fixed | Stage B12 sub-steps in §B.0.2; spec + harness §B.0.4 « B12 » |
| B-R | Final record: changed files, env vars, Stripe/SMTP/DB steps, how to ship | **DONE** | §B.6, `backend/.env.example` |
| H | "Update SCANID-HANDOVER.md so a new session started with only 'READ SCANID-HANDOVER.md' continues seamlessly" (+ "add what is already done and what is to implement"; asked again in the resumed session during B12, "with the current constraints and permissions") | **DONE, kept current after every sub-step** | The resume protocol at the top of this file, this §B.0 |

Not requested, deliberately not done (from the source documents): the « Alex » anomaly investigation,
the DPA answers, « Crédits : N scans », the destination tooltip, invoice links, automatic expiry of
credits (expiry is recorded and shown only). Production steps that only the user/Alex can do: §B.5.

#### B.0.1 The user's message for this task, verbatim

> Implement the following steps:
>
> 1. Actionable failure message. Replace « L’extraction a échoué. » with: « Aucun passeport ou CNI
>    française reconnu sur cette image. Vérifiez la photo (voir le guide) et réessayez — aucun crédit
>    n’a été décompté. » Test: message visible under the failed file.
> 2. App shell. <title>ScanID — Espace client</title>, <html lang="fr">, site favicon (favicon.svg +
>    apple-touch-icon.png from the website). Test: browser tab shows the title and icon.
> 3. Password reset. « Mot de passe oublié ? » link on the login page → email with a 48-hour reset
>    link. Test: complete flow on a test account.
> 4. Vocabulary (decided by Alex). « Ajouter un Passeport » → « Ajouter un document (passeport ou
>    CNI) » · « Mes Passeports » → « Mes documents » · « Pages Traitées » → « Documents traités » ·
>    filter « PASS » → « PP » (keep « PI ») · column « NUMÉRO DE PASSEPORT » → « NUMÉRO DE DOCUMENT »
>    (same in the Excel/CSV header: « Numéro de document ») · empty state → « Aucun document pour
>    l’instant — importez votre premier passeport ou votre première CNI ci-dessus. » · destination
>    placeholder → « Ex : Groupe Lisbonne — octobre 2026 ». Test: strings updated everywhere, exports
>    still open in Excel.
> 5. Trial automation (Spec v2 §1). POST /api/trial-requests accepting nom, societe, email,
>    telephone, volume, message, consentement, siret, tva → pending user with 20 credits +
>    notification email to contact@scanid.fr; admin page « Demandes d’essai » with Valider /
>    Refuser; welcome email with a set-password link (never a plaintext password); purge after 30
>    days. Test: submit the form on https://scanid.fr/essai.html → request appears in admin →
>    Valider → email received → login works with 20 credits.
> 6. Account before payment (Spec v3). /app/inscription?pack=100|1000|3000|5000 (SIRET required,
>    VAT optional, billing address) → user created → redirect to the pack’s Stripe Payment Link
>    with ?prefilled_email=…&client_reference_id=<user_id>; POST /api/stripe/webhook (signature
>    verified, idempotent) credits the pack on checkout.session.completed; GET /api/config →
>    {"signup": true, "trial": true}. Test: full purchase in Stripe test mode + webhook replay →
>    credits added once. Alex will paste the webhook secret in Stripe himself at the last moment.
> 7. Mon Compte. Add editable société, SIRET, n° de TVA, adresse de facturation; add « Mes achats »
>    (pack, date, expiry; invoice link later). Test: fields saved and shown after reload.
> 8. Site menu inside the app (Spec v2 §2): Présentation, Ressources, Tarifs, FAQ, Contact in the
>    top bar, logo → https://scanid.fr/, collapsed under « Retour au site » on mobile.
> 9. Automatic logout after 12 h of inactivity · rate limits on login and upload · highlight rows
>    with a confidence score below 0.8 in the table · daily encrypted pg_dump with a tested restore.
>
> CRUCIAL all constraints and permissions and other implementing conditions remains same as it was
> previously in this conversation!

"Previously in this conversation" = §0 of this file, plus the task-A conditions the user stated:
*"CRUCIAL all current functionalities must be preserved except what i demanded to change"*, and the
same constraints/permissions as §0. Mid-task the user added: *"Update SCANID-HANDOVER.md in such way
that if this session is interrupted and i open a new session with only one command 'READ
SCANID-HANDOVER.md' you can seamlessly continue implementing from where you were interrupted"* —
which is why this §B.0 exists; keep it current after every sub-step.

#### B.0.2 Where things stand (update after every sub-step)

- Git: `master` = `origin/master` = `a2b235d` (task A, pushed by the user; that commit also removed
  `frontend/site/` from the repository). **Everything of task B is uncommitted** in the working tree.
- **Resumed session (same day):** the user opened it with "Read SCANID-HANDOVER.md, resume the implementation after
  verifying what is already made" + the nine items again. Verified at start: working tree = the §B list, backend 289 /
  unit 86 as recorded, items 1–7 present in the code. Then B10 and B11 were done in that session.
- Stages **B0–B13 DONE** (records below §B.4, ship steps §B.6). **Task B is complete locally.** Nothing is left to implement;
  what remains is the user's: server `.env`, Stripe endpoint (Alex), DB owner check, commit/push, acceptance on scanid.fr (§B.6).
  If a new session is opened with this file: verify the working tree matches §B.6, run the quick baseline (backend 295, unit 87),
  and wait for the user's next demand — do not re-implement anything.
- Test counts at the last check (end of B12): backend `pytest` **295 passed**; frontend unit **87 passed**; e2e all
  projects **418 passed, 1 skipped**; build + guard ok; `eslint src/App.jsx`: the 12 pre-existing problems.

**Stage B9 — Mon Compte — sub-steps** (spec in §B.0.4 « B9 »)

- [x] Backend: `schemas.BillingIdentity` (base of `User` and `UserUpdate`); `PUT /users/me` normalises +
      validates a given SIRET/VAT (400 with the `billing_identity` messages), empty clears;
      `GET /users/me/purchases` (`billing.paid_purchases`, `schemas.PurchaseOut`)
- [x] `backend/tests/test_account_billing.py` — 5 passed
- [x] Frontend `AccountEditor`: « Facturation » section + « Mes achats » section
- [x] Mock: `GET /users/me/purchases`; `tests/e2e/account.spec.js` (save → reload → shown; purchases)
- [x] Record stage B9 below §B.4 and set it `DONE`

**Stage B10 — Site menu — sub-steps** (spec in §B.0.4 « B10 »)

- [x] `App` header: logo link, `.sid-sitenav` inline links, `.sid-sitemenu` « Retour au site » disclosure; styles
- [x] `tests/e2e/sitenav.spec.js` (desktop links; mobile disclosure; no overflow; focus ring); existing top-bar / a11y specs still green
- [x] Record stage B10 below §B.4 and set it `DONE`

**Stage B11 — item 9 — sub-steps** (spec in §B.0.4 « B11 »)

- [x] Backend `POST /session/refresh` + tests (token `exp` ≈ 12 h; refresh re-issues the cookie; expired token → 401) — `tests/test_session_idle.py` 4 passed
- [x] Frontend activity tracking + refresh + 12 h idle check; mock `/session/refresh`; e2e with `page.clock` — `tests/e2e/session-idle.spec.js` 6 passed (desktop, mobile-small, mobile-375); mutation check done
- [x] Rate limits: no code change; existing tests only asserted the config values, so **new** `tests/test_rate_limits_enforced.py` (2) proves 6th login → 429 and 121st upload → 429 over HTTP
- [x] Low confidence: `isLowConfidence` + unit test (87 unit); table row + card class/title; style (+ « Modifier » in `--sid-info` on the tint for AA); `tests/e2e/confidence.spec.js` 6 passed
- [x] Backups: `ops/tests/run-ops-tests.sh` 94 passed; real `backup.sh` → `restore-test.sh` round trip on a scratch PG16 cluster with the new schema — ok, 7 tables ≥ 1
- [x] Record stage B11 below §B.4 and set it `DONE`

**Stage B12 — Verification — sub-steps** (spec in §B.0.4 « B12 »)

- [x] Full suites (before the race fix below): backend pytest **295 passed**; unit **87 passed**; `npx playwright test` all projects **415 passed, 1 skipped**; eslint App.jsx 12 (baseline), other changed files clean; `npm run build` ok + build guard 5/5
- [x] Real stack (scratchpad): PG16 with the **pre-change** schema (`git show a2b235d:backend/models.py`) + customer `ancien` (42 credits, 7 pages) + 1 passport → new backend started → **migration verified on PostgreSQL**: `ancien` keeps 42/7, gets `status=active`, `sv=0`; tables `auth_tokens, purchases, trial_requests` created; passport kept. SMTP sink + node proxy over `frontend/dist` (built with `VITE_API_URL=/api`)
- [x] Real flows 0–4 passed: `/api/config` `{"signup":true,"trial":true}`; essai.html → 201 (no Formspree fallback) + notification to contact@scanid.fr; admin « Demandes d'essai » → Valider → welcome email (no plaintext password) → set-password link → login with the email → « Crédits : 20 »; upload with no Vision credentials → actionable message + « voir le guide » link, credits still 20; title / vocabulary / empty state / placeholder / site menu / `/app/favicon.svg`; forgot password → email → reset → old password 401 → new one logs in; DB: trial `validated`, tokens `set`+`reset` used
- [x] **Bug found by the real run, fixed:** clicking « Déconnexion » is itself activity → `POST /session/refresh` raced `POST /logout`; when the renewal answered last it re-set the cookie and the user stayed logged in. Fix in `App.jsx`: `refreshInFlightRef` holds the renewal in flight; `logout` waits for it, then sends `/logout` with `keepalive: true`. Mock `/session/refresh` gains `state.refreshDelayMs` and sets `state.session = true`. Regression e2e « « Déconnexion » l'emporte sur le renouvellement que ce même clic déclenche » in `session-idle.spec.js`: **failed before the fix** (desktop + mobile-375), passes after. `session-idle` + `privacy` + `smoke` + `password` + `trials` + `signup` (desktop, mobile-small, mobile-375): 90 passed. eslint App.jsx 12.
- [x] `VITE_API_URL=/api npm run build`, reset the stack (fresh pre-change DB), re-run ALL real flows 0–8 in one go — **all passed, exit 0** (record in stage B12); stack stopped, ports free: 5 home « Souscrire » → `/app/inscription?pack=1000` → form → Stripe redirect captured (`prefilled_email`, `client_reference_id`) → signed `checkout.session.completed` → `credited`, replay ×2 → `duplicate`, forged signature 400, confirmation email → login « Crédits : 1000 » → « Mes achats » 1 row « Pack 1 000 »; 6 Mon Compte Ville/Société/SIRET survive a reload; 7 `/api/session/refresh` 200 via proxy; 8 screenshots 375 px (dashboard, « Retour au site » open, inscription)
- [x] Final full e2e run (all projects) + unit + backend after the race fix — e2e **418 passed, 1 skipped**; unit 87; backend 295; build guard 5/5; eslint 12 / others clean
- [x] Stop everything (backend, proxy, sink, PG); record stage B12 below §B.4 and set it `DONE`

**Stage B13 — Record and hand back — sub-steps** (spec in §B.0.4 « B13 »)

- [x] `backend/.env.example`: add the new variables (mail, Stripe, public URLs, trial/session settings) — 4 secrets empty, optional ones commented with their defaults (an empty value would override a default)
- [x] §B.6 below: files changed (the `git status` list), env vars for `/opt/travelapp/backend/.env`, Stripe dashboard steps, DB ownership check / manual SQL, restore env note, deploy = the user's commit/push (warn: never `git add .` blindly — see §0 and `frontend/site/`), acceptance tests on https://scanid.fr
- [x] Set B13 `DONE`; mark the task complete at the top of this file

#### B.0.3 Environment and commands (verified in this session)

| What | How |
| --- | --- |
| Python | `/home/lasha/Public/new/newvenv/bin/python` (no new package installed; none needed) |
| Backend tests | `cd backend && ../newvenv/bin/python -m pytest -q` (in-memory SQLite; conftest resets rate limits) |
| Frontend unit | `cd frontend && npm run test:unit` |
| E2E | `cd frontend && npx playwright test [files] [--project=desktop --project=mobile-small --project=mobile-375 --project=pwa] --reporter=line`. Starts Vite dev (5173) and, for `pwa`, `npm run build` + preview (4173) — that rebuilds `frontend/dist/` (allowed by §0.6). |
| Mock backend | `frontend/tests/mock/api.js` must mirror every endpoint the UI calls (unknown paths answer 501). New top-level prefixes go in `API_PATHS`. `test.skip(LIVE, …)` for mock-driven tests. |
| Lint | `cd frontend && npx eslint src/App.jsx` → 12 pre-existing problems is the baseline |
| Build | `cd frontend && npm run build` (vite + `scripts/assemble-site.mjs`); guard `node --test tests/build/no-google-fonts.test.js` |
| Tools present | PostgreSQL 16 server binaries `/usr/lib/postgresql/16/bin` (initdb, pg_ctl), `pg_dump`, `pg_restore`, `psql`, `age`, LibreOffice `soffice` (used to open real exports). **Absent:** nginx, aiosmtpd. |
| Scratchpad | Session-specific; nothing in it survives a new session. Rebuild harness files there (B.0.4 B12). |
| Shell | Parallel Bash calls share the working directory — always use absolute paths. |
| Specs (read-only, outside repo) | `~/Downloads/ScanID-Projet-Complet-v7/technique/ScanID-App-Spec-v2-Essai-Menu.docx`, `…/ScanID-App-Spec-v3-Souscription.docx`, `…/Lasha-Liste-Actions-2026-09-14.docx`; « Email A » in `…/acquisition/ScanID-Emails-Essai.docx`; prices/links in `…/gestion/ScanID-Pilotage.xlsx` sheet « Stripe (à créer) ». Text extraction: unzip `word/document.xml` and strip tags (python `zipfile` + `re`); xlsx via `openpyxl`. |

#### B.0.4 Specification of every remaining step

**B8 (rest) — `/app/inscription`**
- `App.jsx`: `ROUTE_VIEWS` gains `'inscription': 'inscription'`; `renderView` case `inscription` →
  `<PackSignupPage user={user} onLogin={() => setView('login')} onBackToApp={…} />`. Leaving the URL on
  `/app/inscription?pack=N` when « Déjà client ? Se connecter » switches to the login view means
  `fetchUser` (which returns `routeView() || 'dashboard'`) brings the logged-in customer back to the
  pack page. `onBackToApp`: `history.pushState({}, '', APP_ROOT)` then dashboard (or login).
- `PackSignupPage` (use `packSummary`, `formatEuros`, `formatCount`, `normalizeSiret`, `isValidSiret`,
  `normalizeVat`, `isValidVat` from `src/billing.js`; pack from `new URLSearchParams(location.search).get('pack')`):
  - Summary card: « Pack 1 000 », « 1 000 scans de passeports ou CNI françaises — crédits valables
    12 mois », rows « Prix HT » / « TVA 20 % » / « Total TTC » (e.g. 690,00 € / 138,00 € / 828,00 €),
    « soit 0,69 € HT le scan ». Unknown pack → « Ce pack n'existe pas. » + link
    https://scanid.fr/#tarifs, no form.
  - Logged in: « Vous êtes connecté en tant que <user_name>. », button « Continuer vers le paiement »
    → `POST /orders {pack}` → `window.location.assign(checkout_url)`; button « Retour à mon espace ».
  - Not logged in: card « Créer votre compte » with labelled inputs (`htmlFor`/`id`): Prénom, Nom,
    Société / agence, Email professionnel, Mot de passe (+ `<PasswordRules>`), Téléphone, then
    « Adresse de facturation »: Rue, Code postal, Ville, Pays (default « France »), SIRET (required,
    hint « 14 chiffres »), N° de TVA intracommunautaire (optional, placeholder « FR12345678901 »),
    checkbox consent « J'accepte que ScanID utilise ces informations pour créer mon compte et
    établir mes factures. » + link « politique de confidentialité »
    (https://scanid.fr/politique-confidentialite.html). Client-side: invalid SIRET / VAT → the backend's
    exact messages (`billing_identity.SIRET_ERROR` / `VAT_ERROR`). Submit « Créer mon compte et payer »
    → `POST /signup` (body = form + `pack`, numbers) → « Compte créé. Redirection vers le paiement
    sécurisé… » → `window.location.assign(checkout_url)`. Errors: string `detail` shown; 429 → « Trop
    de tentatives. Veuillez réessayer dans une minute. »; other → « Vérifiez les champs saisis. ».
    Button « Déjà client ? Se connecter ».
  - Layout: centred max-width ≈ 760 px; two-column grid for short pairs collapsing on phones
    (`repeat(auto-fit, minmax(220px, 1fr))`); no horizontal overflow at 360 px.
- Mock: `POST /signup` → 400 on unknown pack / email = `state.user.email` (« Un compte existe déjà avec
  cette adresse email. Connectez-vous pour acheter ce pack. »), 422 on weak password, else
  `{checkout_url: <link>?prefilled_email=…&client_reference_id=u-new, purchase_id}` (links as in
  `backend/config.py`), record `state.signups`; `POST /orders` (authorized) → same with `state.user`.
- `tests/e2e/signup.spec.js` (intercept `https://buy.stripe.com/**` with `page.route` → fulfil a stub):
  summary amounts for pack 1000; invalid SIRET blocked client-side; valid form → navigation to the
  1000 link with `prefilled_email` and `client_reference_id`; unknown pack message; logged-in path
  (login, then `goto /app/inscription?pack=100` → « Continuer vers le paiement » → link 100 with
  alice's email); « Déjà client ? Se connecter » → login → back on the pack page logged in.

**B9 — Mon Compte (item 7)**
- Backend: `schemas.User` exposes `company, siret, vat_number, billing_street, billing_postal_code,
  billing_city, billing_country` (Optional[str]); `UserUpdate` accepts them. `PUT /users/me`: a
  non-admin may edit them (not the protected fields); non-empty SIRET/VAT normalised + validated
  (400 with the `billing_identity` messages); empty string clears. New `GET /users/me/purchases` →
  the caller's **paid** purchases `[{id, pack, credits, paid_at, expires_at, amount_ht_cents}]`, newest
  first (`schemas.PurchaseOut`). Tests `backend/tests/test_account_billing.py`.
- Frontend `AccountEditor`: section « Facturation » (Société, SIRET, N° de TVA intracommunautaire, Rue,
  Code postal, Ville, Pays) saved by the existing « Enregistrer les modifications »; client-side
  SIRET/VAT check; section « Mes achats »: one row per purchase « Pack 1 000 », « Acheté le
  DD/MM/YYYY », « Valable jusqu'au DD/MM/YYYY »; empty → « Aucun achat pour l'instant. » (no invoice
  column yet). Mock: `PUT /users/me` already merges; add `GET /users/me/purchases` (`state.purchases`).
  E2E `tests/e2e/account.spec.js`: fill, save, **reload**, values shown; purchases listed.

**B10 — Site menu (item 8)**
- `App` header: `<h1 className="sid-logo"><a href="https://scanid.fr/">Scan<span>ID</span></a></h1>`
  (link inherits the logo colour, no underline); `<nav className="sid-sitenav" aria-label="Site
  ScanID">` with Présentation https://scanid.fr/presentation.html · Ressources
  https://scanid.fr/ressources.html · Tarifs https://scanid.fr/#tarifs · FAQ https://scanid.fr/faq.html ·
  Contact https://scanid.fr/contact.html; « Déconnexion » stays right. At ≤ 900 px the inline links
  hide and `<details className="sid-sitemenu"><summary>Retour au site</summary>…same links…</details>`
  shows. Shown logged in and out. Colours: `--sid-muted` on navy (6.46:1), hover `#fff`, visible
  focus ring (`--sid-focus`). Existing top-bar tests must still pass (logo text « ScanID », logout).
- E2E `tests/e2e/sitenav.spec.js`: desktop hrefs/texts; mobile-375: inline hidden, « Retour au site »
  opens the five links; no horizontal overflow at 360 px; add `.sid-sitenav a` to the a11y contrast
  list if measured on desktop.

**B11 — item 9**
- Inactivity: `POST /session/refresh` (authenticated) re-issues token + cookie with
  `auth.session_claims`. Frontend (`App`, while `token`): listeners `pointerdown`, `keydown`,
  `touchstart`, `wheel`, `scroll` (passive) update `lastActivity`; if more than 5 min since the last
  refresh → `POST /session/refresh`; a 60 s interval calls `fetchUser()` once `now - lastActivity ≥
  12 h` (the server has expired the session → existing « Votre session a expiré » flow). Mock: add
  `/session` to `API_PATHS`, `POST /session/refresh` → 200. Tests: backend (token `exp` ≈ 12 h; refresh
  sets a new cookie; a token past `exp` → 401); e2e with `page.clock` (install before login, advance
  12 h + 1 min with `api.session = false` → login screen shows `.sid-session-expired`; activity
  triggers `/session/refresh` requests).
- Rate limits: already in place and tested (`test_security_hardening.py`: login 5/min + lockout,
  upload 120/min); new endpoints have their own (tests in B6/B7/B8). Record, no change.
- Low confidence: `resultsHelpers.js` `isLowConfidence(item)` (`typeof score === 'number' && score <
  0.8`) + unit test; table `<tr>` and mobile `.sid-card-item` get `is-low-confidence` + `title="Score de
  confiance inférieur à 80 % : vérifiez ce document."`; style: `--sid-warn-bg` background + 3 px
  `--sid-warn` left border (selection background still wins for selected rows). E2E: mock rows p-4
  (0.5) and p-5 (0.66) highlighted, p-1 (0.8734) and p-3 (null) not, table and cards.
- Backups: run `ops/tests/run-ops-tests.sh` (expect 94 passed); then a real round trip in the
  scratchpad: PG16 cluster on a free port, schema from `models.Base.metadata.create_all`, a row in every
  table incl. `trial_requests`, `purchases`, `auth_tokens`; `age-keygen`; `ops/backup.sh` with a scratch
  env file (`OPS_ENV_FILE`), then `ops/restore-test.sh` with `SANITY_MIN_ROWS` listing all seven tables
  ≥ 1. No change to `ops/`. Note for the server: add the new tables to `SANITY_MIN_ROWS` in
  `/etc/scanid/restore.env` if it is set there.

**B12 — Verification**
- Full: backend pytest; `npm run test:unit`; `npx playwright test` (all projects); eslint (12);
  `npm run build` + build guard.
- Real end-to-end on a local stack (scratchpad, all stopped afterwards):
  1. PG16 scratch cluster; create the **pre-change** schema with `git show a2b235d:backend/models.py`
     (+ a row), then start the **new** backend (`uvicorn main:app --port 8001`, `DATABASE_URL`,
     `ENVIRONMENT=development`, `ADMIN_PASSWORD`, `MAIL_BACKEND=smtp SMTP_HOST=127.0.0.1
     SMTP_PORT=<sink> SMTP_STARTTLS=0`, `STRIPE_WEBHOOK_SECRET=whsec_local`,
     `APP_PUBLIC_URL=http://127.0.0.1:8080/app/`) — proves the startup migration on PostgreSQL.
  2. Minimal SMTP sink (python asyncio, writes each message to a file).
  3. Minimal proxy (node `http`): serves `frontend/dist` (site at `/`, SPA fallback `/app/*` →
     `/app/index.html`), `/api/*` → `127.0.0.1:8001` with the prefix stripped (like nginx).
  4. Playwright scripts: essai.html form → success message → admin « Demandes d'essai » → Valider →
     welcome email in the sink → link → password → login with the email → **20 credits**; forgot
     password → email → reset → login; home « Souscrire » (config `signup: true`) → `/app/inscription?pack=1000`
     → form → redirect captured → signed `checkout.session.completed` to `/api/stripe/webhook` →
     **1000 credits** → replay ×2 → still 1000 → « Mes achats » shows it; Mon Compte fields survive a
     reload; failed-file message; vocabulary; screenshots desktop + 375 px.
- **Harness as built in this session (scratchpad `stack/`, rebuild if lost):** `start.sh` (initdb +
  `pg_ctl` port **55433**, `-c unix_socket_directories=''` — the scratchpad path exceeds PostgreSQL's
  107-byte socket limit; `PATH=/usr/lib/postgresql/16/bin:$PATH` — the `pg_dump` on PATH is v14 and
  refuses a v16 server; old schema via `importlib` on `old_models.py` + rows). Backend: `cd backend &&
  env DATABASE_URL=postgresql+psycopg2://scanid_admin@127.0.0.1:55433/travelapp ENVIRONMENT=development
  ADMIN_PASSWORD='Girafe!!12Nuage-Admin' SECRET_KEY=local-e2e-secret-not-production GCP_CREDS_JSON=
  GOOGLE_APPLICATION_CREDENTIALS=/nonexistent/creds.json MAIL_BACKEND=smtp SMTP_HOST=127.0.0.1
  SMTP_PORT=2525 SMTP_STARTTLS=0 SMTP_USERNAME= SMTP_PASSWORD= STRIPE_WEBHOOK_SECRET=whsec_local
  APP_PUBLIC_URL=http://127.0.0.1:8080/app/ SITE_PUBLIC_URL=http://127.0.0.1:8080/ SESSION_COOKIE_SECURE=0
  LOGIN_RATE_LIMIT=30/minute ../newvenv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8011`
  (empty `GCP_CREDS_JSON` stops `backend/.env` from supplying it; no Vision client → every upload is a
  clean failure, no document leaves the machine). `smtp_sink.py 2525 <maildir>` (asyncio, one `.eml`
  per message). `proxy.cjs 8080 frontend/dist 8011` — **must destroy the upstream when the client closes**
  (`res.on('close', () => upstream.destroy())`), otherwise SSE streams keep uvicorn in « Waiting for
  connections to close » forever. `flows.cjs` (Playwright `chromium` required from
  `frontend/node_modules/@playwright/test`; routes `formspree.io` → abort and `https://buy.stripe.com/**`
  → stub; decodes base64/QP emails; signs webhooks with `crypto.createHmac('sha256', 'whsec_local')` over
  `${t}.${payload}`). Script gotchas: after `setInputFiles` click « Lancer l'analyse »; register
  `waitForResponse('/api/config')` **before** `goto('/')`; wait for the `/api/logout` response after
  « Déconnexion ». **Stopping:** never `pkill -f '<pattern>'` from a shell whose own command line contains
  the pattern (it kills that shell, exit 144) — use `pgrep -f '^../newvenv/bin/python -m uvicorn'` then
  `kill <pid>`; `pg_ctl -D <dir> -m fast -w stop`.

**B13 — Record and hand back**
- Files changed (the `git status` list), new environment variables for
  `/opt/travelapp/backend/.env` (`SMTP_HOST=smtp.ionos.fr`, `SMTP_PORT=587`, `SMTP_USERNAME`,
  `SMTP_PASSWORD`, `MAIL_FROM`, `MAIL_ADMIN_TO`, `STRIPE_WEBHOOK_SECRET`; optional
  `STRIPE_PAYMENT_LINK_<pack>`, `APP_PUBLIC_URL`), Stripe dashboard steps (endpoint + both events), DB
  ownership check / manual SQL (B5), deploy = the user's commit/push, acceptance tests to run on
  https://scanid.fr afterwards, `backend/.env.example` updated with the new variables.


The user: *"all constraints and permissions and other implementing conditions remain the same
as previously in this conversation."* §0 applies unchanged (no add/commit/push; `frontend/site/`
and `frontend/scanid-site-v5-deploy/` read-only; stages recorded here; outside the repository:
read when needed, write only with permission).

### B.1 Demand (the user's nine items, verbatim in substance)

1. **Actionable failure message.** « L’extraction a échoué. » → « Aucun passeport ou CNI française
   reconnu sur cette image. Vérifiez la photo (voir le guide) et réessayez — aucun crédit n’a été
   décompté. » Test: visible under the failed file.
2. **App shell.** `<title>ScanID — Espace client</title>`, `<html lang="fr">`, the site favicon
   (`favicon.svg` + `apple-touch-icon.png`). Test: tab shows title and icon.
3. **Password reset.** « Mot de passe oublié ? » on the login page → email with a 48-hour reset
   link. Test: complete flow on a test account.
4. **Vocabulary (Alex).** « Ajouter un Passeport » → « Ajouter un document (passeport ou CNI) » ·
   « Mes Passeports » → « Mes documents » · « Pages Traitées » → « Documents traités » · filter
   « PASS » → « PP » (keep « PI ») · column « NUMÉRO DE PASSEPORT » → « NUMÉRO DE DOCUMENT » (Excel/CSV
   header « Numéro de document ») · empty state → « Aucun document pour l’instant — importez votre
   premier passeport ou votre première CNI ci-dessus. » · destination placeholder → « Ex : Groupe
   Lisbonne — octobre 2026 ». Test: strings updated everywhere, exports still open in Excel.
5. **Trial automation (Spec v2 §1).** `POST /api/trial-requests` {nom, societe, email, telephone,
   volume, message, consentement, siret, tva} → pending user with 20 credits + notification email to
   contact@scanid.fr; admin page « Demandes d’essai » with Valider / Refuser; welcome email with a
   set-password link (never a plaintext password); purge after 30 days. Test: essai.html → admin →
   Valider → email → login with 20 credits.
6. **Account before payment (Spec v3).** `/app/inscription?pack=100|1000|3000|5000` (SIRET required,
   VAT optional, billing address) → user created → redirect to the pack's Stripe Payment Link with
   `?prefilled_email=…&client_reference_id=<user_id>`; `POST /api/stripe/webhook` (signature verified,
   idempotent) credits the pack on `checkout.session.completed`; `GET /api/config` →
   `{"signup": true, "trial": true}`. Test: Stripe test-mode purchase + webhook replay → credited once.
   Alex pastes the webhook secret himself.
7. **Mon Compte.** Editable société, SIRET, n° de TVA, adresse de facturation; « Mes achats » (pack,
   date, expiry; invoice link later). Test: saved and shown after reload.
8. **Site menu in the app (Spec v2 §2).** Présentation, Ressources, Tarifs, FAQ, Contact in the top
   bar; logo → https://scanid.fr/; collapsed under « Retour au site » on mobile.
9. **Automatic logout after 12 h of inactivity · rate limits on login and upload · highlight rows
   with confidence < 0.8 · daily encrypted pg_dump with a tested restore.**

Sources read (outside the repository, read-only, needed for the task):
`~/Downloads/ScanID-Projet-Complet-v7/technique/` — `ScanID-App-Spec-v2-Essai-Menu.docx`,
`ScanID-App-Spec-v3-Souscription.docx`, `Lasha-Liste-Actions-2026-09-14.docx` (the source of the nine
items), `ScanID-App-Audit-2026-09-14.docx`; `acquisition/ScanID-Emails-Essai.docx` (« Email A »);
`gestion/ScanID-Pilotage.xlsx`, sheet « Stripe (à créer) ».

### B.2 State found (measured, before any change)

- **Failure message** — `frontend/src/upload/uploadQueue.js` `applyJobStatuses`: a job whose status is
  `failed` sets the queue item's error to "L'extraction a échoué."; rendered as plain text in
  `.sid-queue__error`. A job is `failed` only when it has **zero successes** (`crud.update_ocr_job_complete`),
  so — since task A — « aucun crédit n’a été décompté » is true for exactly those jobs.
- **Shell** — `frontend/index.html`: `lang="en"`, title « Vite + React », icon `/vite.svg`,
  apple-touch-icon `/icons/icon-192.png`; theme-color `#0B1628` already set.
- **Password reset** — does not exist. **No email capability exists anywhere in the backend.**
- **Session** — `auth.ACCESS_TOKEN_EXPIRE_MINUTES = 30`, fixed, **never renewed**: every session ends
  30 minutes after login whatever the user does. Cookie `max_age` matches.
- **Rate limits already in place** (`config.py`): login 5/min per IP + per-account lockout (10
  failures / 15 min); upload 120/min per IP; registration 5/min. uvicorn's defaults
  (`proxy_headers`, `forwarded_allow_ips=127.0.0.1`) trust nginx's `X-Forwarded-For`, so the limits
  key on the real client IP. One uvicorn worker in production (in-memory SSE).
- **Backups already in place and proven** (PROGRESS.md §2.5): `scanid-backup.timer` daily 03:17,
  `pg_dump | age`, off-site with Object Lock, restore test passed on production data. `pg_dump`
  dumps the whole database, so new tables are included without change.
- **Vocabulary** — « PASS » is itself the result of an earlier rename from « PP »; unit and backend
  tests assert "never the former PP". Type is derived from the document number in
  `backend/main.py` (`DOC_TYPE_PASSPORT`) and `frontend/src/resultsHelpers.js`.
- **Site hooks (v5, live)** — `essai.html` posts JSON (every form field except `_*`, `consentement`
  as a boolean) to `/api/trial-requests` and **falls back to Formspree on any non-2xx**.
  `index.html` switches « Souscrire » to `/app/inscription?pack=N` when `/api/config` says
  `signup: true`. Site CSP `connect-src 'self'` allows both. The four Payment Links in `index.html`
  are the four in the Pilotage sheet. Pack prices HT: 100 → 99 €, 1000 → 690 €, 3000 → 1 890 €,
  5000 → 2 950 €, TVA 20 %, credits valid 12 months.
- **Routing** — nginx `location /app/ { try_files … /app/index.html; }` and the PWA
  `navigateFallback` already serve any `/app/*` path with the app: `/app/inscription` needs no nginx
  change. The app has no router; views are React state.
- **Schema** — `models.Base.metadata.create_all` at startup creates missing **tables** but never adds
  **columns**. New user fields therefore need an explicit, idempotent migration. Whether the
  production role `travelapp` owns `users` (required for `ALTER TABLE`) **cannot be verified from
  here** — see B.5.
- Local tooling: PostgreSQL 16 `initdb` available; no nginx, no SMTP server library.
- Baselines (from §A.4, after task A): backend 219 passed; frontend unit 81 passed; e2e 337 passed /
  1 skipped; `eslint src/App.jsx` 12 pre-existing problems.

### B.3 Decisions

1. **Failure message** — the exact text; « voir le guide » is rendered as a link to the photo guide
   (the text content stays identical). The job monitor's server-side page details are unchanged.
2. **Shell** — `favicon.svg` and `apple-touch-icon.png` copied (read) from
   `scanid-site-v5-deploy/` into `frontend/public/`; the page stops referencing `/vite.svg`. The
   file itself stays: `scripts/generate-icons.mjs` renders the PWA icons from it.
3. **Email** — new `backend/mailer.py`, stdlib `smtplib` (no new dependency), SMTP from environment
   (`smtp.ionos.fr:587` STARTTLS per Spec v2); an `outbox` backend for development/tests. Sends run
   off the request path; failures are logged without content (links are credentials).
4. **Password reset / set-password tokens** — one table `auth_tokens`: random 256-bit token, stored
   as SHA-256 only, purpose `reset`|`set`, valid 48 h, single use, older tokens of the user revoked
   when a new one is issued. The link carries the token in the **URL fragment**
   (`/app/mot-de-passe#token=…`), so it never reaches a server log or a Referer. « Mot de passe
   oublié ? » answers the same generic message whether or not the account exists. A successful
   reset **ends the account's other sessions** (a `session_version` claim).
5. **Vocabulary** — « PP » replaces « PASS » wherever the type is shown (filter, badge, export Type
   column); the export API still accepts `document_type=PASS` as an alias so a cached old app shell
   does not break during a deploy. The tab « Passeports » and the admin users table are not in the
   list and stay as they are. Both destination placeholders (upload card and manual form) change.
6. **Trial** — identifiant = email (Spec v2); `nom` split into prénom / nom; the pending user has no
   usable password and cannot log in; request details kept in `trial_requests`. Valider → active +
   « Email A » (adapted: https://scanid.fr/app/, identifiant = email, set-password link 48 h instead
   of a provisional password). Refuser → rejected, no email. Pending **and** rejected requests (and
   their never-activated users) are purged after 30 days by a daily in-process job. If email is not
   configured the endpoint answers 503, so the site falls back to Formspree and no lead is lost.
   Errors are `{"error": "…"}` as Spec v2 asks.
7. **Account before payment** — identifiant = email; user `active` with 0 credits + a `pending`
   purchase; the server returns the Payment Link URL (links overridable by environment for Stripe
   test mode). Webhook: HMAC-SHA256 over `t.payload` against `STRIPE_WEBHOOK_SECRET`, 5-minute
   tolerance; credits only when `payment_status == "paid"` (and on
   `checkout.session.async_payment_succeeded`, because the Pilotage sheet enables bank transfer);
   pack identified **by the amount paid** (HT subtotal or TTC total), never by what the client asked
   for; credits + purchase row committed together, `stripe_session_id` UNIQUE → a replay credits
   nothing. Unknown user or amount → nothing credited, admin alerted by email. Confirmation email
   to the customer. `GET /api/config`: `signup` is true only when the webhook secret is configured
   (otherwise a paying customer could never be credited), `trial` only when email is configured. A
   visitor already logged in is sent straight to payment for the chosen pack instead of a signup
   form.
8. **Credit validity** — each purchase records `expires_at` = payment + 12 months and « Mes achats »
   shows it. **Automatic expiry of the credits themselves is not implemented** (not in the demand; it
   would change how every credit is counted).
9. **Site menu** — absolute `https://scanid.fr/…` links; Contact → `contact.html` (the live v5
   navigation; Spec v2's `/#contact` predates v5). Desktop: inline in the bar. Narrow screens: a
   « Retour au site » disclosure holding the same links.
10. **12 h inactivity** — the session becomes 12 h long and is **renewed only by real user activity**
    (pointer, key, touch, scroll; at most every 5 minutes, `POST /session/refresh`); background
    polling does not renew it. After 12 h without activity the server refuses the session and the app
    returns to the login screen with its existing « Votre session a expiré » message.
11. **Rate limits** — existing ones verified by test, unchanged; every new unauthenticated endpoint
    gets its own (trial 5/hour, forgot-password 5/hour, reset 10/hour, signup 5/minute).
12. **Confidence < 0.8** — the row (and its mobile card) gets a warning background and a title
    explaining why; a missing score is not highlighted.
13. **Backups** — nothing to deploy; verified locally: `ops/tests/run-ops-tests.sh`, plus a real
    `backup.sh` → `restore-test.sh` round trip on a PostgreSQL 16 cluster carrying the new schema.
14. **Not in scope** (in the source documents but not in the user's nine items): the « Alex »
    anomaly investigation, the DPA answers (§C of the action list), « Crédits : N scans », the
    destination tooltip, invoice links.

### B.4 Stages

| # | Stage | Status |
| --- | --- | --- |
| B0 | Survey code, specs, site hooks, infra; baselines | **DONE** |
| B1 | Write demand, findings, decisions, plan here | **DONE** |
| B2 | Item 1 — failure message | **DONE** |
| B3 | Item 2 — app shell | **DONE** |
| B4 | Item 4 — vocabulary (app + exports) | **DONE** |
| B5 | Backend foundation — user columns + migration, new tables, mailer, tokens, account status | **DONE** |
| B6 | Item 3 — password reset (API + UI) | **DONE** |
| B7 | Item 5 — trial automation (API, admin page, emails, purge) | **DONE** |
| B8 | Item 6 — account before payment (config, signup, Stripe webhook, UI) | **DONE** |
| B9 | Item 7 — Mon Compte fields + « Mes achats » | **DONE** |
| B10 | Item 8 — site menu in the top bar | **DONE** |
| B11 | Item 9 — 12 h inactivity, rate limits, low-confidence rows, backup verification | **DONE** |
| B12 | Verify: all suites, lint, build, real end-to-end flows on PostgreSQL + SMTP sink, rendering | **DONE** |
| B13 | Record what changed, production prerequisites, how to ship | **DONE** (§B.6) |

### Stage B2 — Item 1, failure message — DONE

- `frontend/src/upload/uploadQueue.js`: new export `JOB_FAILED_MESSAGE` (the exact text of the
  demand) replaces "L'extraction a échoué." in `applyJobStatuses`.
- `frontend/src/App.jsx`: `FailedExtractionMessage` renders that message with « voir le guide »
  linked to https://scanid.fr/guide-photo.html; any other queue error still renders as text.
- `frontend/tests/mock/api.js`: a file named `illisible…` yields a failed job (failure detail =
  `_UNRECOGNIZED_DOCUMENT_DETAIL`, page counted, no credit), mirroring the backend.
- Tests: `uploadQueue.test.js` expects the new text (14 pass); new e2e
  `queue.spec.js` « un document illisible affiche le message actionnable sous le fichier, sans
  décompter de crédit » — message under the file, link target, credits unchanged
  (queue spec 18/18 on desktop + mobile-375).

### Stage B3 — Item 2, app shell — DONE

- `frontend/index.html`: `lang="fr"`, `<title>ScanID — Espace client</title>`, icon `/favicon.svg`,
  apple-touch-icon `/apple-touch-icon.png` (Vite prefixes both with `/app/` at build).
- `frontend/public/favicon.svg`, `frontend/public/apple-touch-icon.png`: byte copies of the site's.
- Test: new e2e `design-system.spec.js` « Onglet du navigateur » — title, `lang`, both icons served
  (200) and byte-identical to the site's. PWA suite (built app) 11/11.

### Stage B4 — Item 4, vocabulary — DONE

| Where | Before | After |
| --- | --- | --- |
| Upload card heading (`App.jsx`) | Ajouter un Document *(task A)* | Ajouter un document (passeport ou CNI) |
| Results title | Mes Passeports | Mes documents |
| Sidebar counter, « Mon Compte » label, admin users column | Pages Traitées | Documents traités |
| Type filter, table badge, card badge, export Type column | PASS | PP (`DOC_TYPE_PASSPORT`, backend + frontend) |
| Results column, manual-entry label, export header (XLSX + CSV) | Numéro de Passeport | Numéro de document |
| Documents empty state (table + cards) | Aucune donnée trouvée. | Aucun document pour l’instant — importez votre premier passeport ou votre première CNI ci-dessus. |
| Destination placeholder (upload card and manual form) | Ex: Voyage Japon 2024 / Ex: Voyage 2024 | Ex : Groupe Lisbonne — octobre 2026 |

- Unchanged on purpose: the « Passeports » tab, the admin users table's empty state (« Aucune donnée
  trouvée. »), the export 404 message.
- `backend/main.py`: `DocumentType = Literal["PP", "PI", "PASS"]`, `PASS` mapped to `PP` in
  `_filter_by_document_type` (legacy alias; every value produced is `PP`).
- Tests updated to the new decision (they asserted the old one): `backend/tests/test_export.py`
  (the "former code PP → 422" test now proves the `PASS` alias still filters and yields `PP`),
  `src/resultsHelpers.test.js`, mock `data.js`/`api.js`, `smoke`, `features`, `responsive`, `fonts`,
  `design-system` specs, `helpers/selectors.js` (`TEXT.noData`).
- Results: backend 219 passed; unit 81 passed; e2e smoke + features + responsive + design-system +
  fonts + a11y on desktop and mobile-small: 122 passed.
- "Exports still open in Excel": real XLSX and CSV produced by the API were opened by LibreOffice
  (headless) and re-saved — headers « Numéro de document », Type « PP »/« PI », accents intact.

### Stage B5 — Backend foundation — DONE

- `backend/models.py` — `User` gains `status` (`active`|`pending`|`rejected`, server default
  `'active'`), `session_version` (server default 0), `company`, `siret`, `vat_number`,
  `billing_street`, `billing_postal_code`, `billing_city`, `billing_country`. New tables
  `trial_requests`, `purchases` (`stripe_session_id` UNIQUE), `auth_tokens` (`token_hash` UNIQUE).
- **New** `backend/schema_migrations.py` — `add_missing_columns(engine)`, run at startup right
  after `create_all`: inspects `users` and `ALTER TABLE … ADD COLUMN` for each missing column.
  Additive only, idempotent. **The same change as SQL, for a manual run as the table owner:**

  ```sql
  ALTER TABLE users ADD COLUMN IF NOT EXISTS status VARCHAR NOT NULL DEFAULT 'active';
  ALTER TABLE users ADD COLUMN IF NOT EXISTS session_version INTEGER NOT NULL DEFAULT 0;
  ALTER TABLE users ADD COLUMN IF NOT EXISTS company VARCHAR;
  ALTER TABLE users ADD COLUMN IF NOT EXISTS siret VARCHAR;
  ALTER TABLE users ADD COLUMN IF NOT EXISTS vat_number VARCHAR;
  ALTER TABLE users ADD COLUMN IF NOT EXISTS billing_street VARCHAR;
  ALTER TABLE users ADD COLUMN IF NOT EXISTS billing_postal_code VARCHAR;
  ALTER TABLE users ADD COLUMN IF NOT EXISTS billing_city VARCHAR;
  ALTER TABLE users ADD COLUMN IF NOT EXISTS billing_country VARCHAR;
  ```
- `backend/config.py` — public URLs, mail backend + SMTP settings, `PASSWORD_TOKEN_HOURS` (48),
  trial settings (20 credits, 30-day purge, 5/hour), pack prices + Payment Links (overridable per
  pack), `STRIPE_WEBHOOK_SECRET`, `SESSION_IDLE_MINUTES` (720), new rate limits. All
  environment-driven; secrets read at call time.
- **New** `backend/mailer.py` — `send(to, subject, body, kind)`; backends `smtp` (stdlib `smtplib`,
  STARTTLS, login), `outbox` (memory, optional `.eml` files in `MAIL_OUTBOX_DIR`), `disabled`
  (production default when `SMTP_HOST` is missing). Never raises; logs the kind and outcome only.
- **New** `backend/account_tokens.py` — `issue` (256-bit token, SHA-256 stored, 48 h, revokes the
  account's earlier unused links), `find_valid`, `consume` (sets the password, marks the link used,
  revokes the others, raises `session_version`).
- `backend/auth.py` — `is_active_account` (login and every authenticated request refuse a
  non-active account, with the unchanged generic message), `session_claims` (`sub` + `sv`); a token
  whose `sv` differs from the account's is refused; a token without `sv` counts as 0, so **the
  deploy logs nobody out**. `ACCESS_TOKEN_EXPIRE_MINUTES` now comes from `SESSION_IDLE_MINUTES`
  (renewal on activity arrives in B11). `backend/main.py` `/token` uses `session_claims`; the
  lifespan runs the migration.
- Tests: **new** `backend/tests/test_account_foundation.py` (13) — migration on the pre-change
  `users` table (existing row keeps credits, gets `active`/0; second run is a no-op; new tables
  exist), status refusal on login and on a session, legacy token accepted, session version ends old
  sessions, link hashed / single-use / revoked by a newer one / 48 h expiry / refused for an
  inactive account, backend selection, SMTP STARTTLS + login with nothing sensitive logged, SMTP
  failure never raises, outbox. Full backend suite: **232 passed**.

### Stage B6 — Item 3, password reset — DONE

Backend
- **New** `backend/emails.py` — every French email of the task, plain text: `password_reset`,
  `trial_admin_notification`, `trial_welcome` (« Email A » adapted), `purchase_confirmation`,
  `payment_anomaly`; `password_link()` builds `https://scanid.fr/app/mot-de-passe#token=…`.
- `backend/main.py` — `POST /auth/forgot-password` {identifier} (5/hour per IP): same answer
  whether or not the account exists; an **active** account gets the 48-hour link by email (sent
  after the response). `POST /auth/reset-password` {token, password} (10/hour): invalid / used /
  expired link → 400; password policy → 422; success sets the password, consumes the link, ends
  the other sessions, clears the login lockout, returns the identifiant.
- `backend/crud.py` — `get_user_by_login_identifier` (login name, else email in any letter case).
- `backend/schemas.py` — `ForgotPasswordRequest`, `ResetPasswordRequest`.

Frontend (`frontend/src/App.jsx`)
- Login card: « Mot de passe oublié ? » under the password field (`.sid-linklike`, info colour for
  AA, focus ring).
- `ForgotPasswordPage` (view `forgot`): « Email ou nom d'utilisateur » → « Recevoir le lien » → the
  server's generic answer; 429 has its own message.
- `SetPasswordPage` (view `password`, address `/app/mot-de-passe#token=…`): reads the token once and
  strips the fragment from the address bar; new password + confirmation with the live password
  rules; success → « Se connecter » returns to the login form with the identifiant pre-filled;
  invalid link → « Demander un nouveau lien ».
- `ROUTE_VIEWS` / `routeView()` — the first view with an address of its own; `fetchUser` keeps it
  instead of forcing login/dashboard.

Tests
- **New** `backend/tests/test_password_reset.py` (7): complete flow on a test account (email content,
  48 h, identifiant, link never logged, policy 422, new password logs in, old one refused, session
  opened before the reset refused, link single-use); no account enumeration; email case; no email
  for a pending account; expired and unknown links; rate limit.
- **New** `frontend/tests/e2e/password.spec.js` (4) + mock `/auth/forgot-password`,
  `/auth/reset-password` (a reset changes the mock's accepted password and ends its session).
- Backend 239 passed; `password` + `a11y` + `smoke` specs on desktop + mobile-375: 32 passed.

### Stage B7 — Item 5, trial automation — DONE

Backend
- **New** `backend/billing_identity.py` — SIRET (14 digits + Luhn, La Poste rule) and intra-EU VAT
  (FR + 2-character key + 9 digits; other EU prefixes structurally) normalisation and validation.
- **New** `backend/trials.py` — `parse` (the site's JSON; unknown fields ignored; `nom` required,
  email valid, `consentement` true, SIRET/TVA validated when given, length limits), `create`
  (pending user: identifiant = email lower-cased, `nom` split into prénom/nom, 20 credits, an
  impossible password marker, société/SIRET/TVA stored; + `trial_requests` row; one commit),
  `list_pending`, `validate`, `reject`, `purge` (pending + rejected older than 30 days, with their
  never-activated accounts).
- `backend/main.py` — `GET /config` → `{"signup": <webhook secret set>, "trial": <email configured>}`;
  `POST /trial-requests` (5/hour per IP) → 201 `{"status": "pending"}` or `{"error": "…"}` (400 invalid,
  409 address already known or already pending, 503 when email is not configured — the site then
  falls back to Formspree); notification to `MAIL_ADMIN_TO` with Reply-To = the requester.
  Admin-only `GET /admin/trial-requests`, `POST /admin/trial-requests/{id}/validate` (503 if email is
  not configured, so no account is opened without its email; activates, issues a 48 h `set` link,
  sends « Email A »), `POST …/reject` (no email). Lifespan: `_purge_trial_requests_daily()` at
  startup then every 24 h.
- `backend/schemas.py` — `TrialRequestOut`.

Frontend
- `App.jsx` — admin tab « Demandes d'essai » (`TrialRequestsPage`): pending requests as design-system
  cards (details keep their case), « Valider » / « Refuser » (confirmation), result message, empty
  state; `#demandes-essai` (the link in Alex's email) opens the tab.
- Mock `/admin/trial-requests` (+ validate/reject); **new** `tests/e2e/trials.spec.js` (3).

Tests
- **New** `backend/tests/test_trial_requests.py` (19): the site's exact payload → pending account with
  20 credits that cannot log in + notification content; 7 invalid payloads → `{"error"}` and nothing
  created; optional fields empty; known address / duplicate request → 409; no email → 503; rate
  limit; `/config` both flags; admin-only; **Valider → welcome email → password via its link → login
  with the email → 20 credits**; Refuser → no email, closed, no reset link, cannot be validated
  afterwards; Valider without email → 503 and nothing half-done; unknown id; purge keeps validated
  and recent requests.
- Backend 258 passed; `trials.spec.js` desktop + mobile-small 6 passed.

### Stage B8 — Item 6, account before payment — DONE

Backend
- **New** `backend/billing.py` — `is_known_pack`, `price_ttc_cents`, `checkout_url` (Payment Link +
  `prefilled_email` + `client_reference_id`), `create_pending_purchase`, `add_months`,
  `verify_signature` (Stripe scheme, 300 s tolerance, constant-time compare), `identify_pack` (EUR;
  HT subtotal, or HT/TTC total), `already_processed`, `credit_checkout_session` (paid only; pending
  purchase of that pack updated **conditionally** or a new paid row inserted; credits
  `COALESCE(page_credits,0) + pack` in the same commit; `IntegrityError` on the UNIQUE session id →
  `duplicate`).
- `backend/main.py` — `POST /signup` (5/min): pack, required fields, email, SIRET (required, Luhn),
  VAT (optional), consent, address not already used (asks to log in), password policy → active user
  (identifiant = email, 0 credits, billing fields) + pending purchase → `{checkout_url, purchase_id}`.
  `POST /orders` (authenticated) → pending purchase + link with the account's email/id.
  `POST /stripe/webhook`: 503 without secret; 400 bad/old signature or unreadable body; other events
  → `ignored`; `credited` → confirmation email + SSE `credit_update`; `unmatched` → anomaly email to
  `MAIL_ADMIN_TO`, 200 so Stripe does not retry; `duplicate` / `not_paid` → 200.
- `backend/schemas.py` — `PackSignupRequest`, `OrderRequest`, `CheckoutOut`.

Frontend
- **New** `frontend/src/billing.js` (+ `billing.test.js`, 5): packs, `packSummary` (HT, TVA, TTC, per
  scan), `formatEuros`, `formatCount`, SIRET/VAT checks mirroring the backend.
- `App.jsx` — `ROUTE_VIEWS` gains `inscription`; `PackSignupPage`: summary card; unknown pack
  message; logged-in « Continuer vers le paiement » (`/orders`) + « Retour à mon espace »; signup form
  (labelled fields, billing address fieldset, SIRET/TVA checked before sending, consent with privacy
  link) → `/signup` → redirect; « Déjà client ? Se connecter » returns to the pack page after login.
  `PasswordInput` accepts an optional `id` (label association).
- Mock `/signup`, `/orders`; **new** `tests/e2e/signup.spec.js` (5).

Tests
- **New** `backend/tests/test_pack_purchase.py` (26): account + pending purchase + exact link; test-mode
  link override; 9 refusals (pack, company, postal code, SIRET empty / wrong key, VAT, consent,
  email, weak password) creating nothing; VAT optional; existing customer asked to log in; `/orders`;
  **full purchase then 3 replays → credited once, one purchase, one email, expiry +12 months**; race
  stopped by the database; signature wrong / 301 s old / missing; no secret → 503; other events
  ignored; bank transfer credited on `async_payment_succeeded` only; the pack paid for wins; TTC
  alone identifies; unmatched amount / missing / unknown user → no credit + email to Alex; calendar.
- Backend 284 passed; unit 86 passed; `signup.spec.js` desktop + mobile-375: 10 passed.
- Not possible from here: a purchase in Stripe **test mode** (needs Alex's Stripe account). The webhook
  requests in the tests are signed with Stripe's exact algorithm; B12 repeats it over HTTP on a real
  stack.

### Stage B9 — Item 7, Mon Compte — DONE

- `backend/schemas.py` — `BillingIdentity` (company, siret, vat_number, billing_street,
  billing_postal_code, billing_city, billing_country), now a base of `User` (returned) and `UserUpdate`
  (accepted); `PurchaseOut`.
- `backend/main.py` — `PUT /users/me`: a given SIRET/VAT is normalised and validated (400 with the
  `billing_identity` messages), an empty string clears it; protected fields unchanged.
  **New** `GET /users/me/purchases` → `billing.paid_purchases` (paid only, newest first).
- `frontend/src/App.jsx` — `AccountEditor`: section « Facturation » (7 labelled fields, responsive
  grid, SIRET/VAT checked before sending, server errors shown); **new** `MyPurchases` « Mes achats »
  table: « Pack 1 000 » · « Acheté le » · « Valable jusqu'au » (dates in Europe/Paris), empty state
  « Aucun achat pour l'instant. ».
- Mock `GET /users/me/purchases`.
- Tests: **new** `backend/tests/test_account_billing.py` (5 — save and read back normalised, invalid
  SIRET/VAT refused with nothing changed, empty clears, protected fields still protected, only my paid
  purchases newest first); **new** `frontend/tests/e2e/account.spec.js` (4 — **saved and shown after
  reload**, invalid SIRET blocked before sending, purchases rows, empty state).
- Backend 289 passed; `account` + `features` + `design-system` specs on desktop + mobile-375: 80 passed.

### Stage B10 — Item 8, site menu in the app — DONE

- `frontend/src/App.jsx` — `SITE_URL` + `SITE_LINKS` (Présentation `presentation.html`, Ressources
  `ressources.html`, Tarifs `#tarifs`, FAQ `faq.html`, Contact `contact.html`, all absolute
  `https://scanid.fr/…`, the same targets as the live v5 site's navigation); `SiteLinks`; **new**
  `SiteMenu` — `<details class="sid-sitemenu">` « Retour au site » whose panel holds the same links,
  closed again by Escape (focus back on the summary) or a tap outside. `App` header: the logo is now
  `<a href="https://scanid.fr/">` inside `.sid-logo` (text « ScanID » unchanged), then
  `<nav class="sid-sitenav" aria-label="Site ScanID">`, then the menu, then « Déconnexion » (unchanged,
  right end). Shown logged in and logged out.
- Styles (`GlobalStyles`): links in `--sid-muted` on the navy bar (**6.46:1**), hover white, no
  underline; above 900 px inline, at ≤ 900 px hidden and replaced by the disclosure, whose panel spans
  the full width under the sticky bar (44 px rows). Focus: a **2 px brand-cyan outline** (not the
  `--sid-focus` shadow the plan named — a 25 % cyan shadow is not visible on navy). The bar stays on
  one line at 360 px (67 px high, as before).
- Tests: **new** `tests/e2e/sitenav.spec.js` (4 — desktop texts/hrefs logged out and in, logout after
  the links; phone: inline hidden, « Retour au site » opens the five links inside the viewport, Escape
  and outside tap close; 360 px no overflow with the menu open, logged out and in; AA contrast + visible
  focus outline); `a11y.spec.js` contrast list gains `.sid-sitenav a`.
- Results: `sitenav` + `a11y` + `design-system` + `helpers` + `responsive` + `smoke` on desktop,
  mobile-small, mobile-375: **117 passed**. `eslint src/App.jsx`: the 12 pre-existing problems.

### Stage B11 — Item 9 — DONE

**Automatic logout after 12 h of inactivity**
- `backend/main.py` — **new** `POST /session/refresh` (authenticated): re-issues the token
  (`auth.session_claims`, so the session version still applies) and the HttpOnly cookie for another
  `SESSION_IDLE_MINUTES` (720). An expired session cannot be renewed (401). Same body shape as `/token`.
- `frontend/src/App.jsx` — `SESSION_IDLE_MS` (12 h), `SESSION_REFRESH_EVERY_MS` (5 min),
  `ACTIVITY_EVENTS` (`pointerdown`, `keydown`, `touchstart`, `wheel`, `scroll`; capture, passive). In
  `App`, while there is a session: the first activity and then at most one every 5 minutes send
  `POST /session/refresh`; a 60 s interval calls `fetchUser()` once 12 h have passed without activity
  (re-asked at most every 5 min, in case another tab kept the session alive) → the server refuses → the
  existing « Votre session a expiré » login screen. Background polling never renews.
- Mock: `/session` in `API_PATHS`, `POST /session/refresh` (authorized → 200 + cookie, else 401).
- Tests: **new** `backend/tests/test_session_idle.py` (4 — login token/cookie last 12 h; refresh renews
  for 12 h and the new cookie alone authenticates; a token past `exp` → 401 on `/users/me` and on
  refresh; refresh refused without a session, after a session-version change, for a non-active
  account). **New** `frontend/tests/e2e/session-idle.spec.js` (2, with `page.clock`: 12 h 01 without
  activity → login screen with « Votre session a expiré »; activity renews at most every 5 min and an
  active user 13 h after login is not even re-checked). Mutation check: with the idle check removed the
  first e2e test fails.

**Rate limits on login and upload** — no code change. `config.py`: login 5/min per IP + account lockout
(10 failures / 15 min), upload 120/min per IP; new endpoints: forgot 5/h, reset 10/h, trial 5/h, signup
5/min. The existing tests only asserted the configured values, so **new**
`backend/tests/test_rate_limits_enforced.py` (2) proves it over HTTP: the 6th login within a minute →
429 (even with the right password), the 121st upload → 429.

**Confidence below 0.8**
- `frontend/src/resultsHelpers.js` — `LOW_CONFIDENCE_THRESHOLD` (0.8), `LOW_CONFIDENCE_TITLE`
  (« Score de confiance inférieur à 80 % : vérifiez ce document. »), `isLowConfidence(item)` (finite
  number < 0.8; no score → not flagged) + unit test.
- `App.jsx` — results `<tr>` and mobile `.sid-card-item` get `is-low-confidence` + that `title`.
  Styles: `--sid-warn-bg` background; table: 3 px `--sid-warn` inset edge on the first cell; card: 3 px
  `--sid-warn` left border; a selected row keeps the selection background. « Modifier »
  (`--sid-cyan-dark`, 3.68:1 on the tint) is shown in `--sid-info` on flagged rows (5.33:1).
- Tests: unit **87 passed**; **new** `frontend/tests/e2e/confidence.spec.js` (2 — table: p-4 0.5 and p-5
  0.66 flagged with title, p-1 0.8734 / p-2 0.91 / p-3 null not; colours; AA for text and « Modifier »;
  selection still wins. Cards at 375 px: same rows, border, AA).

**Daily encrypted pg_dump with a tested restore** — no change to `ops/` (already in production,
PROGRESS.md §2.5). `ops/tests/run-ops-tests.sh`: **94 passed**. Real round trip in the scratchpad: PG 16
cluster (TCP only), schema = `create_all` + `schema_migrations`, one row in each of the 7 tables →
`ops/backup.sh` (`status=ok`, file starts `age-encryption.org/v1`, the email and SIRET do not appear in
it) → `ops/restore-test.sh --confirm` with `SANITY_MIN_ROWS` listing all 7 tables → `status=ok`, every
table 1 row, scratch database dropped; negative control (floor 2 on `auth_tokens`) → fails as it must;
no scratch database left; cluster stopped. Notes: the `pg_dump` on this machine's PATH is 14 and refuses
a PG 16 server — the run used `/usr/lib/postgresql/16/bin`. **For the server:** add
`trial_requests`, `purchases`, `auth_tokens` to `SANITY_MIN_ROWS` in the restore env file if it lists
tables (only `purchases`/`trial_requests` will have rows once used; use `=0` until then).

Results: backend **295 passed**; unit **87 passed**; `session-idle` + `privacy` (desktop, mobile-small,
mobile-375) 30 passed + 6; `confidence` + `responsive` + `features` (desktop, mobile-375) 74 passed.
`eslint src/App.jsx`: the 12 pre-existing problems; the other changed files: clean.

### Stage B12 — Verification — DONE

**Suites (final, after every change):** backend `pytest` **295 passed**; `npm run test:unit` **87 passed**;
`npx playwright test` all projects (desktop, mobile-small, mobile-375, pwa) **418 passed, 1 skipped**;
`npm run build` ok + `tests/build/no-google-fonts.test.js` 5/5; `eslint src/App.jsx` the 12 pre-existing
problems, every other changed file clean. (Run Playwright alone, from `frontend/`: started from the repository
root it finds no tests and leaves a stray `test-results/` there — that happened once and was removed.)

**Real stack** (scratchpad; harness described in §B.0.4 « B12 »): PostgreSQL 16 created with the schema of
`a2b235d` (before this task) + customer `ancien` (42 credits, 7 pages, 1 passport); the new backend started on
it with SMTP to a local sink and `STRIPE_WEBHOOK_SECRET=whsec_local`; node proxy serving `frontend/dist`
(`VITE_API_URL=/api`) like nginx.
- **Startup migration on PostgreSQL:** `ancien` kept 42 credits / 7 pages and got `status=active`, `sv=0`;
  `auth_tokens`, `purchases`, `trial_requests` created; the passport kept.
- One run, exit 0, every step asserted:
  1. `GET /api/config` → `{"signup":true,"trial":true}`.
  2. `essai.html` form (all fields, SIRET + TVA) → « Merci ! Votre demande est enregistrée. », **no Formspree
     fallback**; notification « Demande d'essai — Agence Essai » to contact@scanid.fr.
  3. admin → « Demandes d'essai » → Valider → welcome email « Votre espace ScanID est ouvert — 20 scans
     offerts » with a set-password link and no password → link → password chosen → login **with the email** →
     « Crédits : 20 ».
  4. upload of a JPEG (no Vision credentials on this stack) → under the file: « Aucun passeport ou CNI
     française reconnu sur cette image. … aucun crédit n'a été décompté. » + « voir le guide » link; after
     reload « Crédits : 20 » (job `failed`, page counted).
  5. title « ScanID — Espace client », « Ajouter un document (passeport ou CNI) », « Mes documents »,
     « Documents traités », empty state, placeholder, site menu « Tarifs » href, `/app/favicon.svg` 200.
  6. « Mot de passe oublié ? » → email « Réinitialisation de votre mot de passe ScanID » → reset → the old
     password answers 401 → the new one logs in.
  7. site home: « Souscrire » pack 1000 (config `signup: true`) → `/app/inscription?pack=1000` (828,00 €) →
     form → « Créer mon compte et payer » → redirect to `https://buy.stripe.com/8x27sK0rtbFi8Apgvbebu01` with
     `prefilled_email` and `client_reference_id`.
  8. signed `checkout.session.completed` (69 000 / 82 800 cents) → `200 credited`; two replays → `200 duplicate`
     ×2; forged signature → 400; email « Vos 1 000 scans ScanID sont disponibles » → login « Crédits : 1000 » →
     « Mes achats »: one row « Pack 1 000 », 14/09/2026 → 14/09/2027.
  9. Mon Compte: Ville + Société changed, saved, **page reloaded**, values (and SIRET) shown.
  10. `POST /api/session/refresh` with the browser's cookie through the proxy → 200.
  11. Screenshots desktop (trial dashboard, Mon Compte) and 375 px (dashboard, « Retour au site » open,
      inscription pack 3000) — checked by eye.
- Database afterwards: `marc.achat@…` 1000 credits, company « Agence Achat & Fils », city Villeurbanne; one
  purchase `paid` `cs_test_local_1000` 82 800 expires 2027-09-14; trial request `validated`; tokens `set` and
  `reset` both used; `ocr_jobs` one `failed`. Exactly 4 emails in the sink.
- Stack stopped (backend, proxy, sink, PostgreSQL), no port left open.

**Bug found by the real run and fixed (stage B11 code):** the click on « Déconnexion » counts as activity, so
it sent `POST /session/refresh` at the same time as `POST /logout`; when the renewal answered last its new
cookie outlived the logout and the visitor was still logged in on the next page. `App.jsx`: the renewal in
flight is kept in `refreshInFlightRef`; `logout` waits for it, then sends `/logout` (now `keepalive: true`,
so leaving the page at once does not cancel it). Mock `/session/refresh`: optional `state.refreshDelayMs`,
sets `state.session = true`. New e2e « « Déconnexion » l'emporte sur le renouvellement que ce même clic
déclenche » — **failed before the fix on desktop and mobile-375**, passes after.

Observed, not changed (outside the demand): the logout request was already fire-and-forget before this task
— `keepalive` now covers the navigate-away case.

### B.5 Production prerequisites known now (cannot be done from here)

- SMTP credentials for contact@scanid.fr (IONOS) in `/opt/travelapp/backend/.env`.
- Stripe: webhook endpoint `https://scanid.fr/api/stripe/webhook` (events
  `checkout.session.completed` and `checkout.session.async_payment_succeeded`) and its signing
  secret in the `.env` — Alex, via the dashboard.
- Before the first deploy of this task: confirm `travelapp` owns the `users` table
  (`SELECT tableowner FROM pg_tables WHERE tablename = 'users';`), or apply the column migration once
  as the owner — the exact SQL is recorded at stage B5.
- The acceptance tests that name https://scanid.fr need a deploy, which is the user's commit/push.
- Deploy order matters only for Stripe: set `STRIPE_WEBHOOK_SECRET` (and create the endpoint) before
  or together with the deploy; until then `/api/config` keeps `signup: false` and the site keeps
  sending « Souscrire » straight to Stripe, exactly as today.

### B.6 How to ship task B (stage B13 record)

**Files** — nothing is committed (§0.3). `git status --short` at the end of the task:

- Modified (26): `SCANID-HANDOVER.md`, `backend/.env.example`, `backend/auth.py`, `backend/config.py`,
  `backend/crud.py`, `backend/main.py`, `backend/models.py`, `backend/schemas.py`, `backend/tests/test_export.py`,
  `frontend/index.html`, `frontend/src/App.jsx`, `frontend/src/resultsHelpers.js`,
  `frontend/src/resultsHelpers.test.js`, `frontend/src/upload/uploadQueue.js`,
  `frontend/src/upload/uploadQueue.test.js`, `frontend/tests/e2e/{a11y,design-system,features,fonts,queue,responsive,smoke}.spec.js`,
  `frontend/tests/helpers/{selectors,upload}.js`, `frontend/tests/mock/{api,data}.js`.
- New (25): `backend/{account_tokens,billing,billing_identity,emails,mailer,schema_migrations,trials}.py`;
  `backend/tests/test_{account_billing,account_foundation,pack_purchase,password_reset,rate_limits_enforced,session_idle,trial_requests}.py`;
  `frontend/public/{favicon.svg,apple-touch-icon.png}`; `frontend/src/{billing,billing.test}.js`;
  `frontend/tests/e2e/{account,confidence,password,session-idle,signup,sitenav,trials}.spec.js`.
- No new Python or npm dependency (`smtplib`, `hmac`, `hashlib` are stdlib). `frontend/dist/` is a local build
  only (the deploy builds its own).

**1. Before the deploy — on the server** (`/opt/travelapp/backend/.env`, then nothing to restart yet):

```
SMTP_HOST=smtp.ionos.fr
SMTP_USERNAME=contact@scanid.fr
SMTP_PASSWORD=<mailbox password>
STRIPE_WEBHOOK_SECRET=<whsec_… from the Stripe endpoint — Alex>
```
Defaults already right for production (leave them out; an empty `NAME=` line would override the default):
`SMTP_PORT=587`, `SMTP_STARTTLS=1`, `MAIL_FROM=ScanID <contact@scanid.fr>`, `MAIL_ADMIN_TO=contact@scanid.fr`,
`APP_PUBLIC_URL=https://scanid.fr/app/`, `SITE_PUBLIC_URL=https://scanid.fr/`, the four live Payment Links,
`SESSION_IDLE_MINUTES=720`. Everything is also listed in `backend/.env.example`.
- Without `SMTP_*`: `/api/config` → `"trial": false`, the trial endpoint answers 503 and essai.html keeps
  using Formspree (no lead lost). Without `STRIPE_WEBHOOK_SECRET`: `"signup": false`, « Souscrire » keeps going
  straight to Stripe exactly as today. So either can be added later.

**2. Stripe dashboard (Alex):** Developers → Webhooks → endpoint `https://scanid.fr/api/stripe/webhook`,
events `checkout.session.completed` **and** `checkout.session.async_payment_succeeded` (bank transfer) →
copy the signing secret into `STRIPE_WEBHOOK_SECRET`. Nothing else changes in Stripe: the Payment Links are
the existing ones (`client_reference_id` and `prefilled_email` are standard Payment Link parameters).

**3. Database:** the startup migration adds 9 columns to `users` (`ALTER TABLE`, owner required) and
creates 3 tables. Check once as root on the VPS:
`sudo -u postgres psql -d <db> -c "SELECT tableowner FROM pg_tables WHERE tablename = 'users';"` — if it is
not the application role, run the SQL of stage B5 once as the owner before deploying (the app then finds
the columns and skips them). A failed migration would be logged at startup (« Database startup check failed »).

**4. Deploy = the user's commit + push to `master`** (GitHub Actions `deploy.yml` builds, rsyncs, `pip install`,
restarts `travelapp.service`). Checked 2026-09-14: from the repository root, `git add --dry-run .` stages exactly the 51 files above, with no
deletion (`frontend/site/` was already removed in `a2b235d`); `.env`, `newvenv/`, `frontend/dist/` and the
identity-document PDFs are gitignored; no production secret in the 51 files (the harness values in §B.0.4 are
throwaway local ones). So `git add .` is safe **as long as `git status` still shows only that list** — re-check
before committing if anything was added since. The deploy logs nobody out (tokens without `sv` count as 0).
A session opened before the deploy still carries its 30-min expiry; the first activity after the deploy renews it
to 12 h (`/session/refresh` accepts it), otherwise the next login does.

**5. Backups:** nothing to deploy (`pg_dump` dumps the new tables). If the restore env file sets
`SANITY_MIN_ROWS`, append `trial_requests=0,purchases=0,auth_tokens=0` (raise to 1 once they hold data).

**6. Acceptance on https://scanid.fr after the deploy** (the user's nine tests):
1. upload an unreadable photo → the new message under the file, credits unchanged;
2. browser tab « ScanID — Espace client » with the ScanID icon;
3. « Mot de passe oublié ? » on a test account → email → link (48 h) → new password → login;
4. « Ajouter un document (passeport ou CNI) », « Mes documents », « Documents traités », filter PP/PI, column
   « Numéro de document », empty state, placeholder; download XLSX + CSV and open them in Excel;
5. https://scanid.fr/essai.html → admin « Demandes d'essai » → Valider → welcome email → set password → login
   with the email → « Crédits : 20 »;
6. `curl https://scanid.fr/api/config` → `{"signup":true,"trial":true}`; home « Souscrire » →
   `/app/inscription?pack=100` → Stripe **test mode** needs `STRIPE_PAYMENT_LINK_100=<test link>` + the test
   endpoint's secret (or a real 99 € purchase refunded) → credits added once; Stripe dashboard « Resend » of the
   event → still once;
7. Mon Compte: société, SIRET, TVA, address → save → reload → shown; « Mes achats » lists the pack;
8. top bar: Présentation, Ressources, Tarifs, FAQ, Contact, logo → scanid.fr; on a phone « Retour au site »;
9. rows under 80 % confidence tinted; leaving the app untouched 12 h → login screen « Votre session a expiré ».

---

## A. TASK A (2026-09-14, COMPLETE LOCALLY) — THE APPLICATION: CREDITS, HEADING, BADGE

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

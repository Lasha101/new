# Passport & Travel Management Platform — v2

Reimplementation of the travel document management app (React + FastAPI +
PostgreSQL + Google Cloud Vision OCR). The user experience is identical to the
original implementation, with these changes:

1. **Excel and CSV export** — the results screen offers two side-by-side
   downloads, « Télécharger CSV » and « Télécharger Excel » (both for the
   filtered export and for the selection export, `?format=csv|xlsx`, default
   `xlsx`). The results table has a « Type » column — `PASS` (passeport) or
   `PI` (pièce d'identité / CNI), derived from the document-number format since
   the schema has no type column — and a « Tous / PASS / PI » filter; the
   downloads contain exactly the rows on screen (`?document_type=PASS|PI`,
   optional). Columns come in the order of the on-screen table: Nom de
   famille, Prénom, Date de Naissance, Date d'Expiration, Nationalité, Numéro
   de Passeport, Type, Destination, Score de Confiance (shared constant
   `EXPORT_COLUMNS` / `PASSPORT_COLUMN_ORDER`, kept in sync by a test).
   Exported files never contain the internal `id`/`owner_id` columns, use the
   French headers of the on-screen table, and write every text value in
   UPPERCASE. Dates are always `DD/MM/YYYY` (table, preview, CSV text, and the
   number format of the real date cells in XLSX). CSV files are UTF-8 with
   BOM (`;`-separated, so a French Excel opens them correctly); XLSX cells are
   all centered, every column is auto-fitted to its longest value, and an
   Excel AutoFilter covers the whole table so every column header has its
   sort/filter dropdown as soon as the file is opened. The on-screen « Aperçu »
   table mirrors the export and is fed by `GET /export/data?preview=true`
   (JSON). Exported cell values are sanitized against Excel formula
   injection.
2. **Self-registration** — a « Créer un compte » button on the login page lets
   users sign up autonomously via `POST /users/register`. Admin invitation
   links were removed entirely (endpoints, admin UI and the `/register/<token>`
   page); admins can still create accounts directly from « Gérer les
   Utilisateurs ».
3. **Signup credits** — every self-registered account starts with exactly
   **5 page credits** (1 credit = 1 extracted page), enforced server-side
   (`SIGNUP_PAGE_CREDITS` in `backend/main.py`); the client cannot influence it.
4. **French National ID support** — in addition to French passports, the OCR
   pipeline extracts French national identity cards (CNI), both old-format
   (laminated, 2-line MRZ + « Carte valable jusqu'au » expiry on the back) and
   new-format 2021+ cards (3-line TD1 MRZ on the back, visual-zone fallback
   when only the front is on the page). Both document types use the exact same
   schema and fields; the CNI document number is stored in `passport_number`.
   Passport parsing logic is the original one with a single fix: MRZ line 1
   is split on the `<<` that separates the surname from the given names
   (`P<FRALE<FLOCH<<SANDRINE` → `LE FLOCH` / `SANDRINE`; the original greedy
   match put every word but the first into the given names). Every
   non-extracted page gets an explicit technical diagnostic in the job's
   failure list.
5. **PostgreSQL storage** — the data layer was migrated from Google Firestore
   to PostgreSQL (SQLAlchemy). API behavior was verified identical with a full
   before/after end-to-end test (same OCR extraction, credits, exports and
   error messages); Google Cloud is now used only for the Vision OCR API.

## Architecture
- **Frontend:** React (Vite) — `frontend/`
- **Backend:** Python (FastAPI) — `backend/`
- **Database:** PostgreSQL (SQLAlchemy 2.0 + psycopg2; tables and the default
  `admin` user are created automatically at startup)
- **OCR:** Google Cloud Vision API

## Local Development

### 1. Start PostgreSQL and create the database
Any PostgreSQL ≥ 13 works. Create an empty database and point the backend at
it via `DATABASE_URL` in `backend/.env`, e.g.:
```
DATABASE_URL=postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/travelapp
```

### 2. Backend (port 8001, so it can run beside the original on 8000)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --port 8001
```
Configuration lives in `backend/.env` (secret key, admin password — the default
`admin` user is created at startup —, Vision service-account credentials,
`DATABASE_URL`). Using a dedicated database keeps this app fully isolated from
the original, so both can run side-by-side.

### 3. Frontend (port 5174)
```bash
cd frontend
npm install
npm run dev -- --port 5174 --strictPort
```
`frontend/.env.local` points the UI at the backend (`http://127.0.0.1:8001`).

### 4. Tests
```bash
cd backend && pip install -r requirements-dev.txt && python -m pytest -q   # API tests (in-memory SQLite, no PostgreSQL needed)
cd frontend && npm test                                                    # results-screen helper tests (node --test)
```
Both suites also run in CI (`.github/workflows/ci.yml`).

## Deliberate deviations from the original
- **Per-page failure messages** are more precise (they distinguish "no passport
  MRZ / no CNI MRZ / unreadable CNI front" and name the missing fields). The
  original always reported passport-centric messages; with CNI support those
  would be wrong or uninformative.
- **`PUT /users/me`**: in the original, a non-admin submitting the account form
  had `page_credits`/`uploaded_pages_count` written as `null` to Firestore,
  which broke the account (HTTP 500 on every subsequent request). Here the
  protected fields are silently dropped instead.
- **Export preview** shows dates as `DD/MM/YYYY` and blanks for missing values
  (the original rendered raw CSV artifacts such as `1990-05-12 00:00:00+00:00`).
- **Vision calls are retried once** on transient API errors before a page is
  reported as failed.
- **OCR `I`/`1` correction** — the 3rd and 4th characters of a French passport
  number are always letters; when OCR reads a `1` in those positions (as on
  DUBROVNIK.pdf page 14, `231A49194` for `23IA49194`), it is corrected to `I`
  before parsing. The correction only applies in contexts that anchor the token
  as a passport number (MRZ line 2, or the 9-character visual-zone shape with
  at least one real letter).
- **User uniqueness is database-enforced** — `users.email` and
  `users.user_name` carry unique constraints, so the original's
  check-then-create race (a perfectly concurrent duplicate signup slipping
  through) is closed; the loser of the race gets the same French 400 error as
  the normal duplicate case.
- **Editing works end-to-end** — passport and user « Edit » forms save
  correctly: date fields are converted before the database write (the original
  raised a 500 on every passport update), the stored `destination` is returned
  by the API so it can be displayed and changed (single and bulk edit), and
  `user_name`/`role` are updatable by admins (with uniqueness/validity checks;
  non-admins can never change their own role, login name or credits).
- **No horizontal scrolling, full-width layout** — global `border-box` sizing,
  a wrapping legal-links footer, and `min-width: 0` on the dashboard grid
  columns keep every page within the viewport at any screen width; wide tables
  scroll inside their own container (`.table-container`), never the page. The
  sidebar uses `align-self: start` so its `position: sticky` actually works.
  The app uses the whole screen width (`.container` has no max-width cap; the
  original capped it at 1200px), while the login form stays centered.

## Known MVP limitations (shared with the original design)
- Self-registration is protected only by a per-IP rate limit (5/minute), like
  the login endpoint.
- Schema management is `create_all`-based (no migration tool); a future model
  change on an existing database will need Alembic or a manual `ALTER`.

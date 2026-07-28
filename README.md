# Passport & Travel Management Platform — v2

Reimplementation of the travel document management app (React + FastAPI +
Firestore + Google Cloud Vision OCR). The user experience is identical to the
original implementation, with these changes:

1. **Excel export** — data exports download as `.xlsx` (Excel) instead of `.csv`
   (both the filtered export and the selection export). The on-screen « Aperçu »
   table is fed by `GET /export/data?preview=true` (JSON). Exported cell values
   are sanitized against Excel formula injection.
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
   Passport parsing logic is unchanged from the original, so passport pages
   produce identical results. Every non-extracted page gets an explicit
   technical diagnostic in the job's failure list.

## Architecture
- **Frontend:** React (Vite) — `frontend/`
- **Backend:** Python (FastAPI) — `backend/`
- **Database:** Google Firestore (emulator for local development, data
  partition `travel-app-new`)
- **OCR:** Google Cloud Vision API

## Local Development

### 1. Start the Firestore emulator (shared with the original app)
```bash
gcloud beta emulators firestore start --host-port=127.0.0.1:8080
```

### 2. Backend (port 8001, so it can run beside the original on 8000)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --port 8001
```
Configuration lives in `backend/.env` (secret key, admin password — the default
`admin` user is created at startup —, Vision service-account credentials,
emulator host).

**Data partition:** `GOOGLE_CLOUD_PROJECT` defaults to `travel-app-new`, an
isolated emulator partition, so this app runs side-by-side with the original
without mixing data. To operate on the original app's data, set it to the
original project id in `backend/.env`.

### 3. Frontend (port 5174)
```bash
cd frontend
npm install
npm run dev -- --port 5174 --strictPort
```
`frontend/.env.local` points the UI at the backend (`http://127.0.0.1:8001`).

## Deliberate deviations from the original
- **Per-page failure messages** are more precise (they distinguish "no passport
  MRZ / no CNI MRZ / unreadable CNI front" and name the missing fields). The
  original always reported passport-centric messages; with CNI support those
  would be wrong or uninformative.
- **`PUT /users/me`**: in the original, a non-admin submitting the account form
  had `page_credits`/`uploaded_pages_count` written as `null` to Firestore,
  which broke the account (HTTP 500 on every subsequent request). Here the
  protected fields are silently dropped instead.
- **Export preview** shows dates as `YYYY-MM-DD` and blanks for missing values
  (the original rendered raw CSV artifacts such as `1990-05-12 00:00:00+00:00`).
- **Vision calls are retried once** on transient API errors before a page is
  reported as failed.
- **OCR `I`/`1` correction** — the 3rd and 4th characters of a French passport
  number are always letters; when OCR reads a `1` in those positions (as on
  DUBROVNIK.pdf page 14, `231A49194` for `23IA49194`), it is corrected to `I`
  before parsing. The correction only applies in contexts that anchor the token
  as a passport number (MRZ line 2, or the 9-character visual-zone shape with
  at least one real letter).
- **Editing works end-to-end** — passport and user « Edit » forms save
  correctly: date fields are converted before the Firestore write (the original
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
- User uniqueness (email / username) is enforced by check-then-create without a
  transaction; a perfectly concurrent duplicate signup could slip through.
- Self-registration is protected only by a per-IP rate limit (5/minute), like
  the login endpoint.

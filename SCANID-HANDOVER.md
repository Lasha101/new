# SCANID — HANDOVER

Resume file for the "public site becomes the front door of scanid.fr" work, and for the
application tasks that followed it.

> ## ▶ NEW SESSION? THIS IS ALL YOU NEED — RESUME PROTOCOL
>
> The user may open a new session with nothing but "READ SCANID-HANDOVER.md". That is an
> instruction to **resume the current task (§B) exactly where it stopped, under the same
> constraints and permissions**. Do this, in order:
>
> 1. Read **§0** and obey it for the whole session (no `git add` / `commit` / `push`;
>    `frontend/site/` and `frontend/scanid-site-v5-deploy/` read-only; work in stages; update
>    this file after every stage; outside the repository: read when needed, write only with
>    permission).
> 2. Read **§B.0 RESUME POINT** — the exact position (stage and sub-step), the environment, the
>    commands, and the specification of every remaining step. Then §B.1–§B.3 (demand, findings,
>    decisions — decisions are settled, do not re-open them) and the stage records below §B.4.
> 3. Check the working tree matches §B.0 (`git status --short`), run the quick baseline
>    (`backend: pytest -q`, `frontend: npm run test:unit`) and compare with §B.0.
> 4. Continue at the **first unchecked sub-step** of §B.0. After each sub-step, tick it in §B.0;
>    after each stage, set it `DONE` in §B.4 and append its record (same format as B2–B7).
> 5. Keep answering the user in their conversation language; keep the UI in French.
> 6. **If §B.0.2 says task B is complete** (it does since 2026-09-14): do not re-implement anything — verify, report the
>    state and the user-side steps of §B.6, and wait for the user's next demand under the same §0.
>
> §A (task A — committed `a2b235d`, pushed) and §1–§9 (the v5 site task, live) are records only.

Last updated: 2026-09-14 (task B — nine-item action list — **ALL STAGES B0–B13 DONE, complete locally, uncommitted**; how to ship: §B.6)

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

## B. CURRENT TASK (2026-09-14) — THE NINE-ITEM ACTION LIST

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

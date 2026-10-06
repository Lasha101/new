# SCANID — HANDOVER

Resume file for the "public site becomes the front door of scanid.fr" work, and for the
application tasks that followed it.

> ## ▶ NEW SESSION? THIS IS ALL YOU NEED — RESUME PROTOCOL
>
> The user may open a new session with nothing but "READ SCANID-HANDOVER.md". That is an
> instruction to **resume the current task (§K) exactly where it stopped, under the same
> constraints and permissions**. Do this, in order:
>
> 1. Read **§0** and obey it for the whole session (no `git add` / `commit` / `push`; the site's
>    source of truth is read-only — since task F it is
>    `frontend/ScanID-nouveau-site-2026-09-30/nouveau-site/`, §F.3.1; work in stages; update this
>    file after every stage; outside the repository: read **only when needed for the demand**,
>    write only with permission; never connect to the VPS without the user's go-ahead). The user's
>    rule (§F.1, repeated for §G, §H, §I and §K): a demand of the current prompt wins over a restriction
>    of this file.
> 2. **▶ CURRENT TASK (2026-10-06): §K — Alex's PDF « Lasha-Tarifs-Unit-Link-2026-10-03.pdf » (the « à la carte »
>    link on tarifs.html, the Stripe webhook, the crediting rules for unit purchases). Code, verification and ship
>    documentation are COMPLETE (K0–K7). Resume at §K.0 « Ship progress »: the first unticked step — the user ships
>    (§K.5 A), runs the server runbook (§K.5 B, ONE command per message) and forwards §K.5 C to Alex.** §K.1 holds the demand (the PDF in full substance — the PDF itself is in
>    `frontend/payment_scanid/`), §K.2 the findings, §K.3 the decisions, §K.4 the stage records, §K.5 the ship steps,
>    the server runbook and the answers for Alex. Work stage by stage and update §K.0 after every stage (the user's
>    rule for this task).
> 3. Older open items (do not resume them unless the user asks): §J (devis@scanid.fr) is ✅ COMPLETE (2026-10-03 ≈
>    18:34 UTC); §I.0.1 « RESUME HERE » keeps the parked Alex items and « Also open » (task D's steps 6–7; the VPS
>    updates). ONE instruction per message whenever the user runs Git / server commands — the user's rule.
>    **§I** (2026-10-03 — Alex's « third check »): **§I.0.1 « RESUME HERE »
>    is the ordered to-do list, with the exact commands — start there.** §I.0.0 lists every prompt of
>    the session (what is done, what is left); §I.0 holds the state, the checklists and the expected
>    `git status`; §I.5 holds the ship steps, the server runbook and the answers for Alex. §B.0.3
>    still holds the environment and the commands (test suites, e2e, lint, build — use **absolute
>    paths**: parallel shell calls share one working directory); §F.5 holds the real-stack harness.
> 4. Check the working tree matches **§K.0** (`git status --short`) and compare; run §K.0's quick baseline.
>    (§I's checklists: every code stage of §I.4 is DONE and shipped; its open items are the parked ones of §I.0.1 —
>    the user runs every server / Git command; guide **one command per message**, wait for the pasted output.)
>    If a new demand arrives instead, it becomes a new stage: write it here first (§0.9).
> 5. Keep answering the user in their conversation language; keep the UI in French.
> 6. **2026-10-03 ≈ 18:12 UTC: nginx reloaded → tasks F (`e9d527d`), G (`109993f`), H (`c027cfa`) and I (`a769f33`)
>    are ✅ SHIPPED.** History: task H committed `c027cfa`, pushed and live; G and F too — all three except the nginx reload (F: cache headers + the two 301s; G: gzip + `www` → 301 = all
>    of Alex's « optional — server » section, unchanged in his third check). One `sudo nginx -t && sudo
>    systemctl reload nginx` on the VPS covers F, G, H and I (§I.5). **Server state on 2026-10-03:
>    `trial` is ON** (SMTP configured with the user, §I.5 B — its steps 9 and 10 still open); nginx still
>    NOT reloaded; `signup` false (later, with Alex); the account list for Alex not yet read (§H.5 A).
> 7. **Task D (« Sexe ») is committed `cfbcd58`, pushed and live** (§D.7.4 steps 1–4 ticked). Still
>    open: the user's checks, §D.7.3 steps 5–7. Guide them **one command per message** when the
>    user returns to them. (Alex's « after go-live » note confirms « Sexe » live in the list and the
>    XLSX export.)
>
> §A (task A — committed `a2b235d`, pushed), §B (committed `b3028b4`, live), §C (committed
> `68dde4a`), §E (committed `bf7dc3c`, pushed) and §1–§9 (the v5 site task, live) are records only.
> §F (`e9d527d`), §G (`109993f`), §H (`c027cfa`) and §I (`a769f33`) are ✅ SHIPPED (nginx reloaded 2026-10-03).

Last updated: 2026-10-06 (second session) — **task K (§K): K0–K7 COMPLETE (site, à la carte crediting, trial side +
packs, the app; verification: backend 397, unit 90, e2e 460 + 1 skipped, real stack 45 + 19 + 3; §K.5 ship steps, server
runbook, answers for Alex); K8 `.gitignore` (LibreOffice lock files + `frontend/payment_scanid/`). Nothing committed — 21
modified files. Next = the user's shipping: §K.0 « Ship progress », first unticked step.**
Every Playwright run needs `PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1` now (§K.0 K5.5, WebKit note). Before: 2026-10-03 ≈ 18:34 UTC — F, G, H, I ✅ SHIPPED (nginx reloaded); task J (devis@scanid.fr) ✅ COMPLETE.
(Older line, kept as history: 2026-10-03 ≈ 18:15 UTC — task J at §J.0: J1–J3 done, J4 in progress.) Earlier the same evening: resumed session (§I.0.0b) (task I — Alex's « third check »: **code done and verified locally, not committed**;
**`trial` switched ON on the server with the user** (≈ 15:45 UTC); next = §I.0.1 « RESUME HERE ». Task H committed
`c027cfa`, pushed and live except the nginx reload, which also still finishes F and G. Task E committed `bf7dc3c` and
pushed. Task D pushed as `cfbcd58` and live; the user's checks §D.7.3 steps 5–7 still open)

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
   `frontend/site/` no longer exists in the repository.)* *(Task F, 2026-10-02, demanded by the
   user through Alex's deployment notes: the source of truth becomes
   `frontend/ScanID-nouveau-site-2026-09-30/nouveau-site/` — read-only in the same way;
   `scanid-site-v5-deploy/` stays in the repository untouched and is no longer read. §F.3.1.)*
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

## K. TASK K (2026-10-06) — ALEX'S « TARIFS PAGE, À LA CARTE LINK AND WEBHOOK » (PDF of 2026-10-03)

### K.0 State and checklist — update after EVERY stage (the user's rule for this task)

**Where things stand:** **K0–K7 done — task K's code, verification and ship documentation are complete.** Nothing
committed (§0.3: the user commits). **What remains is the user's: §K.5 — A (commit + push), B (the server and Stripe,
ONE command per message), C (forward the answers to Alex).** Resume at the first unticked line of « Ship progress »
just below, give that step's command (§K.5), wait for the pasted output, tick it here, then the next one.

**Ship progress** (§K.5; tick each step as the user reports it — the assistant checks GitHub and the public site itself):
- [ ] A1 `git status --short` == §K.0's list · [ ] A2 `git add -u` + commit + push (hash: …) · [ ] A3 CI + Deploy green
  · [ ] A4 laptop checks (tarifs.html SHA, new bundle, webhook still 503)
- [ ] B0 Stripe: invitation accepted, endpoint URL + event checked, failed deliveries noted, `plink_…`, restricted key,
  secret revealed · [ ] B1 ssh · [ ] B2 look (no Stripe line, 13 lines) · [ ] B3 backup · [ ] B4 `appended`
  · [ ] B5 diff `13a14,17` · [ ] B6 `KEY OK 200` · [ ] B7 restart, `signup` false, public webhook → 400, Alex told
  · [ ] B8 retries / « Resend » → 200 · [ ] B9 test purchase(s) · [ ] B10 `signup` → true · [ ] B11 backup removed
- [ ] C answers forwarded to Alex (§K.5 C, with A's date and B7's time filled in)

**K7 sub-steps** (tick each one as it completes):
- [x] K7.1 §K.5 A — what ships (the 20 files + the decision on `frontend/payment_scanid/`), no new dependency / migration
  / environment variable; the exact `git add` (explicit paths, never the lock file), commit message, push, deploy.
- [x] K7.2 §K.5 B — the server runbook, ONE command per message (the user's rule): the order that avoids the
  double-crediting of finding 11; Stripe invitation → endpoint check (URL + event) → reveal the secret → the plink id →
  the restricted key « Checkout Sessions: Read »; `.env` keys typed at a hidden prompt; restart; `/api/config`; one test
  purchase together; then `signup` → true (`PUBLIC_SIGNUP`).
- [x] K7.3 §K.5 C — the answers for Alex (French-ready text): the three checks confirmed with evidence, the four cases,
  Access, Packs (« yes, until now refused; now it buys »), the optional link done, the switch-over rule.
  **K7.1–K7.3 done:** §K.5 written (A1–A4, B0–B11 with every command and its expected output, C 1–9); B4's `.env`
  command dry-run on a 13-line copy (appended → 17; idempotent; trailing space / `rk_test_` / empty value → STOP); B2's
  and B5's masking checked; §F.6's old « à la carte » steps marked SUPERSEDED (its « no account → nothing credited » is
  no longer true).
- [x] K7.4 Record K7; task K complete; memory file + MEMORY.md line. **Done:** §K.0 « Ship progress » added, the resume
  protocol (top) and « Last updated » point at it; memory `scanid-task-k-unit-link.md` + its MEMORY.md line.

**K8 sub-steps** (new demand, 2026-10-06 — tick each one as it completes):
- [x] K8.1 Root `.gitignore`: `.~lock.*#` under « Editor / OS files »; a commented section for `frontend/payment_scanid/` (patterns tested in a throwaway repo first, §K.0.0 row 8).
- [x] K8.2 Verify: `git check-ignore -v` on the lock file and the folder; `git ls-files -ci --exclude-standard` still empty; `git status --short` = 21 ` M` (+ `.gitignore`), no `??`.
- [x] K8.3 Update §K.0's expected list, §K.5 A1 / A2, « Ship progress » A1, §K.4 K8, the memory note. **K8 DONE** (§K.4 K8).

**K6 sub-steps** (tick each one as it completes):
- [x] K6.1 Backend full suite (expected **397 passed**); frontend unit (**90**); eslint `src/App.jsx` (**11**). **Done:**
  397 passed, 90 / 90, 11 problems (all pre-existing).
- [x] K6.2 Full e2e, from `frontend/`: `PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1 npx playwright test
  --reporter=line` (all 4 projects; `pwa` rebuilds `dist/`). Expected **448 + 4 × 3 = 460 passed, 1 skipped** (task I's
  448 / 1 + the 4 new K5 tests — 2 in `account.spec.js`, 2 in `trials.spec.js` — on desktop, mobile-small, mobile-375).
  **Done: 460 passed, 1 skipped (4.2 min, exit 0)**; ports 5173 / 4173 free afterwards.
- [x] K6.3 Rebuild `dist/` as the deploy does: `VITE_API_URL=/api npm run build`; guard `node --test
  tests/build/no-google-fonts.test.js` (5/5); `dist/tarifs.html` == the source; the folder's 63 files == `dist/`.
  **Done:** 64 files assembled, 0 pages rewritten, no `/fonts/`; guard 5/5; `dist/tarifs.html` == source; 63 / 63 files
  identical; the app bundle carries « Acheter des documents à l'unité », `locked_prefilled_email`, the link, « Compte
  déjà ouvert par un achat »; no localhost URL. `dist/` is now the production build again.
- [x] K6.4 Real stack (§F.5's harness, rebuilt in this session's scratchpad: PostgreSQL 16 on 55433, the backend in
  production mode on 8001 with `STRIPE_WEBHOOK_SECRET=whsec_local`, `STRIPE_UNIT_PAYMENT_LINK_ID=plink_local_unite`,
  `STRIPE_API_KEY=rk_local_checkout_read`, the Stripe stand-in on 12111, `MAIL_BACKEND=outbox`; nginx container
  optional): signed webhooks for Alex's three checks (bad / missing signature → 400; unpaid → nothing; replay →
  `duplicate`) and the four cases (open account; new address → account + welcome + link → password → login; waiting
  trial → opened with N, then « Valider » +20 by the admin API; refused trial → opened with N); the app's link
  (`client_reference_id`, another e-mail typed) → that account; `/signup` for a waiting trial e-mail. Record the
  outcomes; stop everything; ports free.
  **DONE — 45 / 45 API checks, 19 / 19 browser checks, 3 / 3 after-browser checks (details §K.4 K6); the stack is
  stopped: container removed, no harness process, ports 8001 / 8081 / 8443 / 12111 / 55433 free.** (How it was
  stopped, for a future harness: `docker rm -f scanid-nginx-k6`; pids from
  `ps -eo pid,args | grep -E "run_backen[d]|fake_strip[e]"` → `kill <pid>` (never `pkill -f` with the plain name);
  `PATH=/usr/lib/postgresql/16/bin:$PATH pg_ctl -D <scratchpad>/k6/stack/pgdata -m fast -w stop` (a new session has
  another scratchpad: then find the old one with `ps -eo pid,args | grep "[p]ostgres -D"`); ports 8001 / 8081 / 8443 /
  12111 / 55433 free (`ss -ltn`).)
- [x] K6.5 `git status --short` == the expected list below; record K6 (§K.4). **Done:** == the list (20 M + 1 ??);
  `git add --dry-run .` = **24 paths** (before K8) = the 20 + the folder's 4 files, **one of which is LibreOffice's lock file
  `frontend/payment_scanid/.~lock.Lasha-Tarifs-Unit-Link-2026-10-03.docx#` — never to be committed** (§K.5 ship
  steps stage explicit paths).

**K5 sub-steps** (planned 2026-10-06, second session; tick each one as it completes):
- [x] K5.1 `backend/trials.py`: `validate()` and `reject()` return the request with **`account_open` = a purchase had
  opened the account** (validate: the conditional activation found it open; reject: the conditional closing found it
  open). Found in K5's survey: both answers carried the schema's default `false`, so the app could not tell Alex the
  truth when a payment lands between loading the list and the click. `main.py` unchanged (it returns that dict). Tests:
  the K4 tests of `test_unit_purchase.py` assert `account_open` in both answers (true after a purchase, false otherwise).
  **Done:** 6 assertions (`test_unit_purchase.py` Valider / Refuser after a purchase + the two race tests → `True`;
  `test_trial_requests.py` Valider / Refuser → `False`); mutations (scratchpad `k5/mutate.py`, 3 files, control 101
  passed): validate never / always open **2 / 1 failed**, reject never / always open **2 / 1**; full backend **397
  passed** (assertions only, no new test).
- [x] K5.2 `frontend/src/billing.js`: `UNIT_PAYMENT_LINK` (Alex's link, the same as `tarifs.html`), `unitCheckoutUrl(user)`
  = the link + `client_reference_id=<id>&locked_prefilled_email=<e-mail>` (`URLSearchParams`, like the mock's pack
  `checkoutUrl`). `src/billing.test.js`: the exact URL (an e-mail with `+` → `%2B`, `@` → `%40`); the link == the
  « À la carte » button's `href` in `nouveau-site/tarifs.html` (the app and the site cannot drift apart).
  **Done:** frontend unit **90 passed** (89 + 1).
- [x] K5.3 `frontend/src/App.jsx` « Mes achats » (`<MyPurchases user={user} />`): for a customer (not an admin), under
  the list, a link styled `sid-btn-outline` « Acheter des documents à l'unité » → `unitCheckoutUrl(user)` (same tab, like
  the packs' `window.location.assign`), with « 1,50 € HT le document, ajouté à ce compte dès le paiement confirmé. »;
  inline style `.sid-purchases__buy` (flex, wrap, gap). Built from the **saved** account (`/users/me`), not the form.
  **Done** (code; checked in K5.5): + `.sid-purchases__buy a:hover { text-decoration: none; }` (the global `a:hover`
  underlines links — not wanted on a button-styled one).
- [x] K5.4 `App.jsx` « Demandes d'essai »: a chip `sid-chip sid-chip--done` « Compte déjà ouvert par un achat » on a
  request with `account_open`; one sentence added to the intro (« Si un achat a déjà ouvert le compte … « Valider » y
  ajoute les 20 documents offerts … « Refuser » et la suppression après 30 jours ne retirent que la demande, jamais le
  compte. »); « Valider » reads the answer's `account_open`: « Demande validée : les 20 documents offerts sont ajoutés au
  compte de <e-mail>, déjà ouvert par un achat ; un e-mail l'en informe. » (else today's message).
  **Done** (code; checked in K5.5): + `.sid-trials .sid-chip { margin-top: 0.35rem; }`. ESLint `src/App.jsx` still
  **11** (all pre-existing, none on a changed line).
- [x] K5.5 Mock `tests/mock/api.js`: validate / reject answer `account_open` like the server. E2E `account.spec.js` (a
  customer: the link's exact URL, the click reaches `buy.stripe.com` — intercepted; after saving a new e-mail the link
  follows it; an admin: no link), `trials.spec.js` (factory `account_open: false` like the server's list; the chip on the
  open one only; the intro sentence; « Valider » on it → the new message; the race: list says waiting, answer says open
  → the new message). Run both files on all projects; unit; eslint (baseline 11).
  **Done:** the 2 files **36 passed** (12 tests × desktop, mobile-small, mobile-375); mutations (scratchpad copy of
  `frontend/`, `k5/mutate_front.py`, desktop, control 12 passed) **7 / 7 caught**; screenshots looked at (`k5/shots/`:
  the button + price under « Mes achats » at 1280 and 360 px, no page overflow, no underline on hover; the chip under
  the date; the new « Valider » message). **WebKit note:** `mobile-375` first failed to launch (« Host system is
  missing dependencies … libavif16 ») — Playwright 1.63 re-validates the host every 30 days (marker
  `~/.cache/ms-playwright/webkit-2359/DEPENDENCIES_VALIDATED`, dated 2026-09-05) and that check ignores the
  `LD_PRELOAD` of `tests/.browser-libs/`. Fix without writing outside the repository: prefix every Playwright run
  with **`PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1`** (the launch itself still gets the preloaded libraries).
- [x] K5.6 Record K5 (§K.4), this table, the expected `git status`. Also `backend/.env.example`: the app's link credits
  the `client_reference_id` account (the comment said only « the checkout e-mail's account »).

**K4 sub-steps — ALL DONE** (kept as the record of how K4 was built):
- [x] K4.1 `backend/trials.py`: `_pending_request_and_user` accepts a pending request whose account is `pending` **or
  `active`** (opened by a purchase / `/signup`); `validate()` → `(request, user, already_open)`: `pending` → conditional
  activation (`WHERE status = 'pending'`), the 20 already there; already open → `page_credits += TRIAL_CREDITS`; the
  request's own update conditional on `status = 'pending'` (a double click → 409); `reject()`: an open account is left
  untouched, only the request is refused; `list_pending()` adds `account_open`.
- [x] K4.2 `backend/schemas.py` `TrialRequestOut.account_open: bool = False`.
- [x] K4.3 `backend/emails.py` `trial_credits_added(user)` — « 20 documents offerts ajoutés à votre espace ScanID » (no
  link).
- [x] K4.4 `backend/main.py` `validate_trial_request`: already open → `trial_credits_added`, kind `trial_credits`, no
  link; otherwise unchanged (link + `trial_welcome`).
- [x] K4.5 `backend/main.py` `signup_for_pack`: an e-mail whose account is a pending or refused trial account → the
  same account takes the form (names, phone, company, SIRET, VAT, billing address, password), `active`, 0 credits —
  conditional `WHERE status IN ('pending','rejected')`, else 400 as today; the trial request untouched.
- [x] K4.6 Tests: `test_trial_requests.py` (Valider / Refuser after a purchase, the purge keeps the account,
  `account_open`), `test_pack_purchase.py` (`/signup` for a waiting / refused trial e-mail, then the pack webhook, then
  « Valider » +20; an open account still refused), `test_email_wording.py` (`trial_credits_added`).
- [x] K4.7 Full backend suite **397 passed**, mutation checks 10 / 10 caught, K4 recorded in §K.4.

**K3 sub-steps — ALL DONE** (kept as the record of how K3 was built):
- [x] K3.1 `backend/account_tokens.py`: `add(db, user_id, purpose)` = `issue()` without its commit (the link is
  committed with the credits); `issue()` = `add()` + commit (behaviour unchanged).
- [x] K3.2 `backend/billing.py`: imports (`secrets`, `Tuple`, pydantic `EmailStr` / `TypeAdapter` / `ValidationError`,
  `account_tokens`), `UNOPENED_STATUSES = ("pending", "rejected")`, `_EMAIL`; `CreditOutcome.password_token`;
  `UnmatchedPayment`; `unit_buyer(db, session) -> (account | None, e-mail)` (reads only; raises `UnmatchedPayment`: unknown
  `client_reference_id`, no e-mail, invalid e-mail, two accounts, the address = another account's login);
  `checkout_identity(session)` (`individual_name` → `collected_information.individual_name` → `name`, split at the first
  space; `business_name`; `phone`); `_credit_unit_session` (EUR → buyer → quantity → write; `IntegrityError` → rollback →
  `duplicate` if the session is recorded, else one retry with a fresh `unit_buyer`, a second failure re-raises → 500 →
  Stripe retries); `_write_unit_purchase` (one transaction: new account `active` with N credits / conditional opening
  `WHERE status = <read>` setting `active` + N / else `+= N`; the paid purchase row; `account_tokens.add(…, "set")` when
  the purchase opened the account).
- [x] K3.3 `backend/emails.py`: `unit_purchase_welcome(user, raw_token, quantity, expires_at)` — subject « Votre espace
  ScanID est ouvert — N documents disponibles » (« 1 document disponible »).
- [x] K3.4 `backend/main.py` `stripe_webhook`: `password_token` → `unit_purchase_welcome`, kind `purchase_welcome`;
  otherwise unchanged (kind `purchase_confirmation`); docstring.
- [x] K3.5 `backend/tests/test_unit_purchase.py` rewritten (valid tests kept; the helper's amounts now 1,80 € TTC
  VAT-inclusive, no tax line; new: open account = credits only (Access), new address → account + welcome + link → login,
  singular, identity mapping, pending trial → opened with N only (request still pending), refused trial → like no
  account, the three checks (signature, unpaid, replay) for new addresses, three race tests, the unmatched list updated).
  **Before K3.5 the old file gave 7 failures, all from the intended rule changes** (pending, refused, unknown address,
  reasons, race patch).
- [x] K3.6 Run `test_unit_purchase.py` + the related files; fix; full backend suite — **385 passed** (§K.4 K3).
- [x] K3.7 `tests/test_email_wording.py`: `unit_purchase_welcome` (37 and 1) in `TEMPLATES` + the « Mon compte » line.
- [x] K3.8 Mutation checks — 8 / 8 caught (§K.4 K3); docs `.env.example` + README items 2–3; K3 recorded.

| Stage | Content | Status |
| --- | --- | --- |
| K0 | Survey: the PDF, `frontend/payment_scanid/`, git, the live site, the webhook / trial / signup code, the tests, Stripe's docs; baselines | **DONE** |
| K1 | Demand, findings, decisions, plan (this §K) | **DONE** |
| K2 | Website: `nouveau-site/tarifs.html` replaced by Alex's file (LF, his SHA-256); one-line diff; build + guard; `dist/tarifs.html` == the file | **DONE** (§K.4 K2) |
| K3 | Backend, « à la carte » crediting (PDF §4): the four cases, the welcome e-mail with the password link, « Access »; tests | **DONE** (§K.4 K3) |
| K4 | Backend, trial side + packs (PDF §4): « Valider » / « Refuser » / the 30-day purge after a purchase; `/signup` for a pending (and a refused) trial e-mail; `account_open` in the admin list; tests | **DONE** (§K.4 K4) |
| K5 | App (frontend): « Mes achats » → the unit link with `client_reference_id` + `locked_prefilled_email` (PDF §4 « Optional »); « Demandes d'essai » shows an account already opened by a purchase; mock, unit, e2e | **DONE** (§K.4 K5) |
| K6 | Verification: backend, unit, eslint, build + guard, full e2e, real stack (PostgreSQL + production-mode backend + Stripe stand-in, signed webhooks) for the three checks and the four cases | **DONE** (§K.4 K6) |
| K7 | Record + how to ship + the server runbook (Stripe invitation, endpoint check, secret, link id, restricted key, hold, test purchase, `signup` → true) + the answers for Alex | **DONE** (§K.5) |
| K8 | The user (2026-10-06): « Add what should be added to .gitignore! » — root `.gitignore` + `.~lock.*#` (LibreOffice lock files) + `frontend/payment_scanid/` (Alex's delivery folder, kept local) | **DONE** (§K.4 K8) |

**Git at the start of task K:** `master` = `origin/master` = **`82acbd6`** (task J); `git status --short` = ` M
SCANID-HANDOVER.md` (task J's completion notes, never committed) + `?? frontend/payment_scanid/`.
**Baselines at the start (2026-10-06, reproduced):** backend **368 passed**; frontend unit **89 passed**; eslint
`src/App.jsx` **11 problems**. Full e2e last recorded: **448 passed, 1 skipped** (task I).
**Expected `git status --short` now (after K8) — 21 modified, nothing untracked:** ` M` `.gitignore`, `README.md`,
`SCANID-HANDOVER.md`, `backend/{.env.example,account_tokens.py,billing.py,emails.py,main.py,schemas.py,trials.py}`,
`backend/tests/{test_email_wording.py,test_pack_purchase.py,test_trial_requests.py,test_unit_purchase.py}`,
`frontend/ScanID-nouveau-site-2026-09-30/nouveau-site/tarifs.html`, `frontend/src/{App.jsx,billing.js,billing.test.js}`,
`frontend/tests/e2e/{account.spec.js,trials.spec.js}`, `frontend/tests/mock/api.js`. `frontend/payment_scanid/` is
ignored since K8 (`!!` in `git status --ignored`); `git add --dry-run .` = these 21 paths.
Update this line after each stage. **Baselines now: backend 397 passed, frontend unit 90, eslint 11.**
`frontend/dist/`: the K5 e2e runs started the `pwa` web server, which **rebuilt `dist/` with `.env.local`'s API URL** →
K6.3 rebuilds it as the deploy does (gitignored either way).

### K.0.0 THIS SESSION (2026-10-06) — every prompt, what is done, what is left

| # | Prompt (verbatim, or in substance) | Done | Left |
| --- | --- | --- | --- |
| 1 | « Read SCANID-HANDOVER.md to see your restrictions and permissions! Execute prompts from attached pdf file! The same pdf file you will find in frontend/payment_scanid folder with orher needed files! CRUCIAL you implement stage-by-stage what i demand to you! CRUCIAL firstly update SCANID-HANDOVER.md by what you should to do, after each time after implementing the current stage update SCANID-HANDOVER.md in such way that if i iterrupt current session and in new one i tell you read SCANID-HANDOVER.md you could continue implement seamlessly! » + Alex's PDF « Lasha-Tarifs-Unit-Link-2026-10-03.pdf » | K0, K1, K2, K3, K4 | K5–K7 |
| 2 | « Update SCANID-HANDOVER.md as it is demanded in the current prompt! » (during K3) | **DONE:** §K.0 carries K3's sub-steps (done / left), the expected `git status`, « Last updated » and the resume protocol point at them | — |
| 3 | « Finish the carrent stage and update SCANID-HANDOVER.md! » (during K4) | **DONE:** K4 finished (tests, full suite 397, mutations 10 / 10) and recorded (§K.0, §K.4 K4); the session stopped after K4, before K5, as asked | K5–K7 |
| 4 | New session: « Read SCANID-HANDOVER.md! Resume-continue working! » | Baselines reproduced (backend 397, unit 89, eslint 11, `git status` == §K.0); **K5 done** (§K.4 K5); **K6 done** (§K.4 K6) | K7 |
| 5 | (during K6) « CRUCIAL each time after implementing the current stage update SCANID-HANDOVER.md in such way that if i iterrupt current session and in new one i tell you read SCANID-HANDOVER.md you could continue implement seamlessly! » | Applied: §K.0 is updated after every sub-step (K5.x, K6.x, K7.x ticked as each completes), « Last updated » and the resume protocol point at the next unticked sub-step | — (standing rule) |
| 6 | « All what was demanded in the attached pdf file is imlpemented? » (+ the same PDF) | **Answered:** in the code, yes — every item of PDF §1, §2 and §4 is implemented and verified locally (§K.4); **nothing is live**: not committed (checked: HEAD `82acbd6`; live `/tarifs.html` still the old page `f374f97f…`, `/api/config` `signup` false, webhook 503); **PDF §3 is the user's** (Stripe invitation, check URL + event, reveal and install the secret — plus the `plink_…` id and a restricted key the PDF does not mention but « read the line items » needs —, tell Alex, test purchase, `signup` → true) = §K.5 B; the three checks are proven, the confirmation for Alex is written (§K.5 C) but not sent | §K.0 « Ship progress » (A, B, C) |
| 7 | « All what remains to do needs my engagement? » | **Answered:** almost all of it. **The assistant alone:** A1 (done), A3 (CI + Deploy via GitHub), A4 and the public checks after B7 / B10 (read-only), filling C's dates. **The user:** A2 (commit + push — §0.3; the user may lift it for this commit by saying so explicitly), every Stripe step (B0, B8: the user's Stripe login and inbox, the secrets), every server step (B1–B7, B10, B11: `sudo` password, secrets at hidden prompts, §0 « never connect to the VPS without the user's go-ahead »), B9 (the test purchase with Alex, a real card), C (forward to Alex). Advice given: start A only when B can follow the same day | §K.0 « Ship progress » |
| 8 | « Everything that must be in .gitignore is in? » | **Answered — almost; one gap.** Covered: `backend/.env`, `frontend/.env.local` (+ `.env.*` except `.env.example`), keys / certificates / `*.age` / dumps / credentials, `newvenv/`, `node_modules`, `dist`, caches, Playwright output, `tests/.browser-libs/`, the two identity PDFs, `bench_*`, `site*.html`; `git ls-files -ci --exclude-standard` empty (nothing tracked that should be ignored); the 20 files' added lines hold no real secret (only placeholders: `whsec_`, `rk_live_`, `whsec_local`, `rk_local_checkout_read`, `whsec_wrong`). **Gap:** no pattern for LibreOffice lock files — `frontend/payment_scanid/.~lock.Lasha-Tarifs-Unit-Link-2026-10-03.docx#` (user name, host `lasha-HP`, a path; a stale copy: LibreOffice still has the `.docx` open from `~/Downloads/payment_scanid/`). **Proposed, NOT applied (waiting for the user):** root `.gitignore` + `.~lock.*#` and, if the user agrees, `frontend/payment_scanid/` (Alex's delivery folder; its content is recorded in §K.1; past practice: Alex's PDFs never committed) — both tested in a throwaway repo. If applied, `.gitignore` becomes the 21st file of the commit (`git add -u` takes it): update §K.0's expected list and §K.5 A1 → **applied in K8 (row 9)** | — |
| 9 | « Add what should be added to .gitignore! » | **DONE — K8:** both lines (the lock pattern, and the folder — « what should be added » read as the proposal made in row 8); verified; the handover's expected list, §K.5 A1 / A2 and the memory note updated | — |
| 10 | « Can i use git add .? » | **Answered: yes** — checked: `git add --dry-run .` from the repo root == `git add --dry-run -u` (the same 21 paths, nothing of `frontend/payment_scanid/`, no lock file); caveat: run it from the repo root (`git add .` from a subfolder stages only that subfolder) — A2 starts with `cd /home/lasha/Public/new` | — |
| 11 | « Provide a short git commit message! » | **Given:** « À la carte: tarifs link, purchases open accounts, in-app link » — §K.5 A2's command updated to it (with `git add .`) | — |

### K.1 The demand (user, 2026-10-06) and Alex's PDF in substance

The user's message is row 1 above. The PDF (2 pages, « SCANID · FOR LASHA = FOR You-Claude Code! », « Tarifs page, « à
la carte » link and webhook », dated 03/10/2026 22:14) is in `frontend/payment_scanid/` with `tarifs.html` and
`favicon.ico`. « Page 1 is what to do now; page 2 gives the rules for crediting these purchases. »
1. **The link.** `https://buy.stripe.com/8x2eVc3DF4cQcQF2Elebu05` — product « Document à l'unité », one-time payment
   **1,80 € TTC (1,50 € HT)**; « As for the packs, the amount is VAT-inclusive and there is no tax line. » Quantity chosen
   by the customer, **1 to 99**; one unit = one document credit. The page asks for the **e-mail, the full name, the
   business name and a phone number**.
2. **Website — replace one file:** `tarifs.html` (attached), site root, **19 405 bytes, SHA-256
   `b5765cef29aaba26931e108a97ddb61a40f70576fda5b74761ae91dda46a0645`**. One line changes: the « À la carte » button
   (`data-pack="unite"`) opens the link and reads « Acheter à l'unité » (was « Commencer par l'essai » → essai.html).
   Nothing else; same asset version `?v=202609302115`. « Your deployment source too … please replace the file in your
   source as well, or the old page would come back. » « The button has no `js-buy` class: it keeps opening Stripe when
   `signup` becomes true. » **Test:** on /tarifs.html, « Acheter à l'unité » opens the Stripe page « Document à
   l'unité », 1,80 €.
3. **Webhook — your Stripe invitation.** An endpoint created by Alex on 03/10 in Workbench > Webhooks:
   `https://scanid.fr/api/stripe/webhook`, event `checkout.session.completed` — « Please check both. » Alex invited
   Lasha to the ScanID Stripe account on 03/10: accept the invitation, open the endpoint, **reveal its signing secret
   yourself (whsec_…) — never by e-mail or chat**. Then install the secret and tell Alex (« until it is in place,
   Stripe reports a failed delivery for each payment »); **one test purchase together, then `signup` → true**.
   **Three checks — please confirm:** (1) a request without a valid Stripe signature is rejected; (2) credits are
   added only when `payment_status` is `paid`; (3) a session is credited once, even if Stripe sends the event again.
4. **App — crediting unit purchases** (« Until this is live, Alex credits these purchases by hand »):
   - **When:** `checkout.session.completed` for a session whose `payment_link` is this link.
   - **How many:** the quantity of the session's line item, one credit per unit — « read the line items rather than
     dividing the amount ».
   - **Which account:** the one whose e-mail equals `customer_details.email`, case-insensitive. Four cases:
     | This e-mail has… | What the app does |
     | --- | --- |
     | an open account | adds the credits to it |
     | no account | **Decided by Alex:** a buyer needs no validation — the person has paid. Create the account, send the welcome e-mail with its link to choose a password, and credit it. |
     | a trial request still waiting (account « en attente ») | **Validated by Alex:** the purchase opens the account at once, with the welcome e-mail and the purchased credits. The 20 trial documents are not given by the purchase: they are added only when Alex clicks « Valider ». After a purchase, « Refuser » and the 30-day clean-up remove the trial request only, never the account. |
     | a trial request that Alex refused | same as « no account »: the purchase opens an account with the purchased credits only |
   - **Access:** a unit purchase never logs anyone in, and never changes the e-mail or the password of an account that
     is already open; access always comes through the link e-mailed to the account's address — « someone who pays with
     another person's e-mail only gives that person credits ».
   - **Packs:** once `signup` is true, an e-mail whose trial request is still waiting must also be able to buy a pack on
     `/app/inscription`; the account then takes the details typed in that form. « Today, is that e-mail refused as
     already used? »
   - **Optional, more robust:** inside the app, offer the same link with
     `client_reference_id=<id>&locked_prefilled_email=<email>` (the user's id and e-mail): Stripe sends
     `client_reference_id` back in the event, so the right account is credited whatever the e-mail.

Constraints and permissions: §0, with the user's standing rule (the current demand wins over a restriction of this
file) — here it covers writing `tarifs.html` into the read-only site source (PDF §2 « your deployment source too »).

### K.2 Findings (K0, before touching anything)

1. **The attached `tarifs.html`** = 19 627 bytes, **CRLF** line endings (222 lines, 222 `\r` — added in transit). With
   the `\r` removed: **19 405 bytes, SHA-256 `b5765cef…0645` = exactly Alex's**; against
   `nouveau-site/tarifs.html` (19 371 bytes, `f374f97f…`, = the live page, checked) the diff is **one line** (l. 96):
   `href="essai.html">Commencer par l'essai` → `href="https://buy.stripe.com/8x2eVc3DF4cQcQF2Elebu05">Acheter à
   l'unité`. Live `/tarifs.html` today: the old line.
2. **`frontend/payment_scanid/favicon.ico`** (9 662 bytes, one 48×48 icon: a white parallelogram on violet — looks like
   the Stripe checkout page's icon) ≠ the site's `favicon.ico` (1 685 bytes, 16 + 32 px « id » mark, = live). The PDF
   does not mention it → **not used**. **`.~lock.Lasha-Tarifs-Unit-Link-2026-10-03.docx#`** = a LibreOffice lock file
   (not gitignored — `git add .` would stage it). The folder is not read by the build.
3. **Site:** `assets/js/core.js` l. 270–274 rewrites only `a.js-buy` to `/app/inscription?pack=…` when `signup` is
   true; the unit button has no `js-buy` → it keeps opening Stripe (Alex's point confirmed).
4. **Webhook today** (`main.stripe_webhook`, `billing.credit_checkout_session`): no secret → **503**; bad / missing /
   expired signature → **400** (`verify_signature`, 300 s tolerance); `payment_status != "paid"` → `not_paid`, nothing
   read or written; duplicate session → `duplicate` (cheap check + **UNIQUE `purchases.stripe_session_id`** in the
   credit transaction) — **the three checks are already met** for packs and « à la carte » (tests:
   `test_pack_purchase.py` `test_the_signature_is_verified`, `test_without_a_secret_the_webhook_refuses`,
   `test_a_bank_transfer_is_credited_when_the_money_arrives`, `test_full_purchase_then_webhook_replay_credits_once`,
   the race tests; `test_unit_purchase.py` the same for à la carte).
5. **À la carte today (task F4):** recognised by `payment_link == STRIPE_UNIT_PAYMENT_LINK_ID`, before the pack path;
   quantity = the single line item's, read with `STRIPE_API_KEY` (`GET /v1/checkout/sessions/{id}/line_items`); buyer =
   `client_reference_id`, else exactly one account whose `lower(email)` matches. **Differences with Alex's table:**
   no account → **anomaly e-mail, nothing credited** (must now create the account); pending trial → credited **on top of
   the 20** and the account **stays pending** (cannot log in) (must now open it with the purchased credits only);
   refused → **anomaly** (must now open it); open account → credited ✓ (+ the confirmation e-mail, no link).
6. **Trial side today** (`trials.py`): a request creates a `pending` account holding `TRIAL_CREDITS` (20) at once and an
   unusable password; « Valider » (`validate`) requires the account to be `pending` (else 409 « Le compte associé à cette
   demande n'existe plus. »), activates it, then `main` issues a 48 h `set` link + `trial_welcome`; « Refuser »
   (`reject`) sets account and request `rejected` (same 409 rule); `purge` deletes pending / refused requests older than
   30 days **with their account only if it is not `active`** (already right for a purchase-opened account).
7. **Packs today** (`main.signup_for_pack`): an e-mail with any `users` row (including a pending or refused trial
   account) or a pending trial request → **400 « Un compte existe déjà avec cette adresse email. Connectez-vous pour
   acheter ce pack. »** → **answer to Alex's question: yes, today that e-mail is refused** (and a pending / refused
   account cannot log in: a dead end).
8. **Stripe facts (docs.stripe.com, read 2026-10-06):** `customer_details` carries `email`, `name`, `phone`,
   `individual_name`, `business_name` (the last two also under `collected_information`, « Collect customer names »);
   `line_items` are never in the event (expandable only); Payment Link URL parameters `client_reference_id` (letters,
   digits, `-`, `_`, ≤ 200 — our ids are 32 hex characters; returned in `checkout.session.completed`) and
   **`locked_prefilled_email`** (« an uneditable email address », takes precedence over `prefilled_email`). Live mode
   retries a failed webhook delivery for up to 3 days.
9. **Live 2026-10-06:** `/api/config` → `{"signup":false,"trial":true}`; `/tarifs.html` = the old page (19 371 bytes).
10. **No in-app buy entry today:** « Mes achats » (`App.jsx` `MyPurchases`, in « Mon compte ») lists the purchases; packs
    are bought only through `/app/inscription` (`/orders` when logged in). The admin « Demandes d'essai » screen does not
    know whether a request's account is open.
11. **Double-crediting risk at the switch-over (not in the PDF, found here):** while the secret is missing, every unit
    payment's delivery fails (503) and Stripe retries it for up to 3 days; Alex credits those payments by hand. If the
    secret goes in while a retry of such a payment is still pending, the app credits it **a second time** (it cannot see
    a hand-made credit). → ship order and a rule for Alex in §K.5 (no code).
12. **The live Stripe page (rendered read-only in K2, nothing submitted):** « Payer ScanID », « Document à l'unité »,
    « Document lu à l'unité (passeport ou CNI française), crédité dans votre espace ScanID. Prix : 1,50 € HT + TVA 20 %
    (1,80 € TTC) par document. », « Qté 1 », 1,80 €; « Coordonnées »: e-mail, **« Nom complet »**, **« Nom de
    l'entreprise »**, phone (→ `customer_details.individual_name` / `business_name` / `phone`); then card, cardholder,
    billing address and an optional VAT number (« Informations relatives à VAT » → `customer_details.tax_ids` — not used:
    not in Alex's list; the customer can fill « Facturation » in « Mon compte »). **Adaptive Pricing is on** (« Choisir
    la devise »: from this laptop 5,47 GEL or 1,80 €; Stripe: « always enabled for Payment Links »). Stripe's docs: the
    session and the event keep **the integration currency (EUR) and amounts**; the customer's currency is only in
    `presentment_details` → the EUR check and the pack amounts stay right — no code change.

### K.3 Decisions

1. **K2 — `tarifs.html`:** write Alex's bytes (the attached file with the `\r` removed — SHA-256 checked =
   `b5765cef…`) over `nouveau-site/tarifs.html`; nothing else in the source changes. The folder's `favicon.ico` is not
   used. `frontend/payment_scanid/` stays untouched (the user decides at ship time whether it is committed; the lock
   file must not be).
2. **K3 — à la carte, the order of the checks:** currency EUR → the buyer is resolved **without writing** → the
   quantity is read from Stripe → then **one transaction** writes everything. So a Stripe error, a missing quantity or
   an ambiguous e-mail creates nothing (anomaly e-mail to Alex, as today).
   - Buyer: `client_reference_id` when present (unknown id → anomaly, as today); else `customer_details.email` (or
     `customer_email`), validated and lowercased; **two accounts** with that address in different letter case → anomaly
     (as today); an address used as **another account's login name** → anomaly (cannot create it).
   - **Open account** (`active`) → `page_credits += N` + the paid purchase row + today's « Vos N documents… » e-mail
     (no link). Nothing else of the account changes (Access rule).
   - **No account** → a new `active` account: `user_name` = `email` = the checkout e-mail (lowercased); first / last
     name from `individual_name` (else `collected_information.individual_name`, else `name`), split at the first space
     like `trials.create`; `company` = `business_name`; `phone_number` = `phone` (or empty); an unusable password
     (`!unit-purchase-…`, like the trial's); `page_credits` = N; the paid purchase row; **a 48 h `set` link created in
     the same transaction**; e-mail **« Votre espace ScanID est ouvert — N documents disponibles »** (singular for 1:
     « 1 document disponible ») = the welcome (address, identifiant, the link) + « achat à la carte : N documents …
     valables jusqu'au … » + the three first steps + « Mon compte » → « Mes achats ».
   - **Pending trial account** → opened: `status` `active`, `page_credits` **= N** (the 20 provisional trial credits are
     not given by the purchase), purchase row, link, the same welcome e-mail. The trial request **stays pending**.
   - **Refused trial account** (`rejected`, not purged yet) → the same opening (credits = N). The request stays refused.
   - Opening is a **conditional** update (`WHERE status = <the status read>`): if another delivery or `/signup` opened the
     account meanwhile, the credits are added instead. Account creation racing another one (UNIQUE e-mail / login) →
     rollback, one retry (the account then exists); the session already recorded → `duplicate`.
   - Outcome carries the raw link token (memory only) → `main` sends the welcome (kind `purchase_welcome`) or the
     confirmation (kind `purchase_confirmation`).
3. **K4 — trial side:** « Valider » on a pending request whose account is **already open** (opened by a purchase, or by
   `/signup`) → `page_credits += 20` (`TRIAL_CREDITS`), request `validated`, and a short e-mail **« 20 documents offerts
   ajoutés à votre espace ScanID »** (no password link: the account is open; kind `trial_credits`). On a pending account:
   unchanged (activate; the 20 are already there; welcome + link). « Refuser » on a request whose account is open →
   only the request is refused; the account is untouched. Both use conditional updates (an admin click racing a
   payment cannot lose credits). The purge: unchanged (never deletes an active account) — proven by a test.
   `TrialRequestOut` gains **`account_open`** (bool) for the admin screen.
4. **K4 — packs (`/signup`):** an e-mail whose account is a **pending** trial account → accepted: the same account (same
   id) takes the form's details (names, phone, company, SIRET, VAT, billing address, password), becomes `active` with
   **0 credits** (the 20 come only with « Valider »), the pending purchase, the checkout URL; the trial request stays
   pending. **Also a refused trial account** (Alex's table: « same as no account » — otherwise a dead end: « Connectez-
   vous » to an account that cannot log in) — reported to Alex as following his rule. An open account → 400 as today.
   Conditional update (`WHERE status IN ('pending','rejected')`).
5. **K5 — app:** « Mon compte » → « Mes achats » (customers only, not admins): a link « Acheter des documents à l'unité »
   → `https://buy.stripe.com/8x2eVc3DF4cQcQF2Elebu05?client_reference_id=<id>&locked_prefilled_email=<e-mail>`
   (URL-encoded), with « 1,50 € HT le document, ajouté à ce compte dès le paiement confirmé » — built in
   `src/billing.js` (`UNIT_PAYMENT_LINK`, `unitCheckoutUrl`), no new API. « Demandes d'essai »: a request whose account
   is open says « Compte déjà ouvert par un achat » and « Valider » then reports « … les 20 documents offerts sont
   ajoutés à son compte » (no welcome e-mail); one sentence added to the screen's intro.
6. **Docs:** `backend/.env.example` (the à la carte comment: the link exists, the new rules), README items 2–3 (an
   account can also be opened by an à la carte purchase).
7. **Not changed:** the pack path of the webhook (identified by the amount + `client_reference_id`); the 503 without a
   secret (it is what makes Stripe retry until the secret is in place); the trial request form; nginx; no new
   environment variable, no new dependency, no database migration (`purchases` pack 0 already exists).
8. **Server and Stripe:** the user's, in §K.5 (written at K7) — never through the chat: the signing secret and the API
   key are typed at a hidden prompt on the VPS.

### K.4 Stage records

(K6–K8 records are added here as each stage completes.)

**K8 — DONE (2026-10-06).** Root `.gitignore`: `.~lock.*#` (LibreOffice lock files, with a comment) under « Editor / OS
files »; a new last section for `/frontend/payment_scanid/` (Alex's delivery folder, kept on this machine; content in
§K.1). Verified: `git check-ignore -v` → the folder's 4 files by line 117, a lock file elsewhere by line 41;
`git ls-files -ci --exclude-standard` empty; the site source's `tarifs.html` not ignored; `git status --short` = 21
` M`, nothing untracked; `git add --dry-run .` = 21. The build never read the folder (§K.2.2), so nothing else changes.

**K6 — record (2026-10-06, second session; K6.1–K6.4 runs done).** K6.1: backend **397 passed**, unit **90**, eslint
**11**. K6.2: full e2e **460 passed, 1 skipped** (4.2 min). K6.3: `VITE_API_URL=/api npm run build` → 64 files, guard
5/5, 63 / 63 site files == `dist/`, `dist/tarifs.html` == source, the bundle carries the K5 strings, no localhost.
K6.4 real stack — **the harness** (scratchpad `k6/`, rebuild from this if ever needed): `nginx/` = §F.5 item 1 (self-signed
`scanid.fr` cert; the real vhost `deploy/nginx-travelapp.conf` with `listen 8081` / `listen 8443 ssl http2`, IPv6 lines
deleted; container **`scanid-nginx-k6`**, `nginx:1.27-alpine`, `--network host`, mounts as §F.5); `stack/start_pg.sh`
(§F.5 item 2, pg.log); `stack/fake_stripe.py 12111` (§F.5 item 3; answers a full line item, quantity from
`quantities.json`); `stack/run_backend.py` + `stack/backend.sh` (§F.5 item 4, phase B values, plus
`LOGIN_RATE_LIMIT=60/minute TRIAL_RATE_LIMIT=60/hour SIGNUP_RATE_LIMIT=60/minute MAIL_ADMIN_TO=contact@scanid.fr
PUBLIC_SIGNUP=` — `backend/.env` defines only SECRET_KEY, ADMIN_PASSWORD, GCP_CREDS_JSON, DATABASE_URL, all four set
explicitly); `stack/check.py api|after <href>` (httpx → `https://127.0.0.1:8443/api` with `Host: scanid.fr`; webhooks
signed `t=…,v1=HMAC-SHA256(whsec_local)`; state read with psycopg2; mail parsed from `stack/mail/*.eml`);
`stack/app_check.cjs <out> [name] [e-mail]` (Chromium from `frontend/node_modules`, `--host-resolver-rules=MAP scanid.fr
127.0.0.1`, `ignoreHTTPSErrors`, `buy.stripe.com` intercepted; before login exactly two known items are allowed — the
session probe `GET /api/users/me` → 401 + its console line, and « An SSL certificate error occurred when fetching the
script » = the service worker refused over the self-signed cert — after login nothing at all).
**Results:** `/api/config` through nginx `{"signup":true,"trial":true}`; `/tarifs.html` 200, 19 405 bytes.
`check.py api` **45 / 45**: Alex's check 1 — no header / another secret / 1 h old / garbage → **400** ×4, nothing
opened, bought, sent or read; check 2 — `unpaid` → `not_paid`, no account, no Stripe read; then
`async_payment_succeeded` → credited, account opened with 4; check 3 — the same session again (both event types) →
`duplicate`, still 4, 1 purchase, 1 e-mail, 1 Stripe read (with the restricted key). Case « open account » (Marc,
created by the admin with 10): `Marc.Ouvert@Agence-K6.FR` × 7 → 17, password hash / login / status unchanged, no
link, « Vos 7 documents ScanID sont disponibles », his password still logs in. Case « no account » (Nina, ×12,
`individual_name` / `business_name` / `phone`): active, 12, login = e-mail lowercased, « Nina » / « Neuve-K6 » /
« Agence Neuve K6 » / « +33611223344 », no login before the link, welcome « Votre espace ScanID est ouvert — 12 documents
disponibles » → the link sets the password → login → 12 credits, « Mes achats » = (0, 12); `/users/me` id = 32 hex.
Case « waiting trial » (Anne): pending with 20 → ×8 → **active with 8** (not 28), request still pending, welcome « … 8
documents disponibles »; admin list `account_open` true; « Valider » → 200, answer `account_open` true → 28, no new
link, « 20 documents offerts ajoutés à votre espace ScanID ». Case « refused trial » (René): « Refuser » → answer
`account_open` false, account `rejected` → ×5 → active with 5, request stays `rejected`, welcome with link. « Refuser »
after a purchase (Paul ×3): answer `account_open` true, account active with 3, no e-mail. The app's link: Marc's id as
`client_reference_id`, `quelqu.un@ailleurs-k6.fr` typed, ×3 → Marc 20, no account for the typed address, the
confirmation to Marc. Packs: `/signup` for a waiting trial e-mail (Claire) → 200, **the same account id**, active, 0,
the form's names, `client_reference_id` = that id in the checkout URL, request still pending; pack webhook 828,00 € TTC
(subtotal = total, no tax line) → 1 000; « Valider » → `account_open` true → 1 020.
`app_check.cjs` **19 / 19** (production build through nginx): Nina at 1280 and 375 px — « Mes achats » first row « À la
carte · 12 documents »; the link = Alex's link + her 32-hex id + `locked_prefilled_email=nina.neuve%40agence-neuve-k6.fr`
(2 parameters only); the price line; 44 px target, no horizontal overflow; the click → Stripe (intercepted) with that
exact URL; no console error / failed request / 4xx after login. Admin: Lou's card (a second waiting request opened by
a ×2 purchase — Léa's had been validated by the first browser run) shows « Compte déjà ouvert par un achat », the
intro sentence, « Valider » → « Demande validée : les 20 documents offerts sont ajoutés au compte de
lou.second@agence-k6.fr, déjà ouvert par un achat ; un e-mail l'en informe. »; nothing after login. (A first browser
run failed only its three « no error » checks on those two pre-login items → the rule above; its other 13 passed,
Léa validated through the app.) `check.py after <href>` **3 / 3**: Léa 6 + 20 = 26, validated, one « 20 documents
offerts » e-mail; the href Nina's browser built carries her id and locked e-mail; a payment through it with
`autre.adresse@ailleurs-k6.fr` typed → Nina 12 + 9 = 21, no other account. Lou: active 22, `purchase_welcome` +
`trial_credits`, request validated. Outbox: 21 e-mails, kinds `purchase_confirmation`, `purchase_welcome`,
`trial_credits`, `trial_notification`; Stripe stand-in: 10 reads, all with the key.

**K5 — DONE (2026-10-06, second session).** Backend: `trials.validate()` / `reject()` return the request with
**`account_open`** = a purchase had opened the account (the conditional activation / closing found it open) — before,
both answers carried the schema's default `false` (found in K5's survey; the app's message after « Valider » needs the
truth when a payment lands between the list and the click); 6 assertions added (`test_unit_purchase.py` 4 → `True`,
`test_trial_requests.py` 2 → `False`); mutations 4 / 4 caught; full backend 397 passed. `backend/.env.example`: the app's
link credits the `client_reference_id` account. Frontend: `src/billing.js` `UNIT_PAYMENT_LINK` +
`unitCheckoutUrl(user)`; `src/App.jsx` — « Mes achats » (`MyPurchases user={user}`): for a customer, under the list, the
link « Acheter des documents à l'unité » (`sid-btn-outline`, same tab) → `https://buy.stripe.com/8x2eVc3DF4cQcQF2Elebu05
?client_reference_id=<id>&locked_prefilled_email=<saved e-mail, URL-encoded>` + « 1,50 € HT le document, ajouté à ce
compte dès le paiement confirmé. »; admins: no link. « Demandes d'essai »: chip « Compte déjà ouvert par un achat »
(`sid-chip sid-chip--done`) when `account_open`; the intro's new last sentence « Si un achat a déjà ouvert le compte
(« Compte déjà ouvert par un achat »), « Valider » y ajoute les 20 documents offerts et en informe le client par e-mail ;
« Refuser » et la suppression après 30 jours ne retirent alors que la demande, jamais le compte. »; after « Valider »,
from the answer's `account_open`: « Demande validée : les 20 documents offerts sont ajoutés au compte de <e-mail>, déjà
ouvert par un achat ; un e-mail l'en informe. » (else the welcome message as before). Inline styles: `.sid-trials
.sid-chip`, `.sid-purchases__buy` (+ `span`, + `a:hover` no underline). Tests: unit `billing.test.js` +1 (the exact URL;
the link == `tarifs.html`'s « À la carte » `href`) → **90**; mock: list / validate / reject answer `account_open`;
e2e `account.spec.js` +2 (the customer's link, its URL after saving a new e-mail, the click → Stripe intercepted; the
admin has none), `trials.spec.js` +2 (the chip + intro + message; the race) → the 2 files **36 passed** on 3 projects;
frontend mutations **7 / 7** caught; eslint 11 (pre-existing, none on a changed line); screenshots looked at.

**K3 — DONE (2026-10-06).** Code: §K.0's K3 sub-steps 1–4 (`account_tokens.add`; `billing.unit_buyer` /
`checkout_identity` / `_credit_unit_session` / `_write_unit_purchase` / `UnmatchedPayment` / `UNOPENED_STATUSES` /
`CreditOutcome.password_token`; `emails.unit_purchase_welcome`; the webhook's welcome vs confirmation). Docs:
`backend/.env.example` (the link's URL, the new rules), README items 2 (« an « à la carte » purchase » opens an account)
and 3 (its credits). Tests: `test_unit_purchase.py` **44** (was 29) — open account credited only, its e-mail / login /
password hash / session version / identity untouched, no link, no cookie (Access); new address → `active` account
(user name = e-mail lowercased, `individual_name` / `business_name` / `phone`), N credits, purchase, nobody can log in
until the link, welcome « Votre espace ScanID est ouvert — 12 documents disponibles » with the link → password → login
→ 12 credits and « Mes achats »; replays → `duplicate`, one account / purchase / e-mail / Stripe read; singular; the
identity mapping (4 cases, `collected_information` fallback); a waiting trial → `active` with **N only** (not 20 + N),
its identity from the trial form kept, the request still `pending`, welcome + login; a refused trial → `active` with N,
request still `rejected`; Alex's checks for a new address (forged / stale / unsigned → 400, unpaid → `not_paid`, nothing
opened, no Stripe read; then `async_payment_succeeded` → credited); races: duplicate delivery, the same new address twice
at once (one account), an account opened meanwhile by another payment (credited, no second link), a trial account read
« en attente » but opened meanwhile (documents added, one link); 13 unmatched cases (each: nothing credited, **no account
opened**, no link, one anomaly e-mail naming the reason). `test_email_wording.py` **10** (the welcome, plural and
singular). Mutations (scratch copy of `backend/` without `.env`, script `k3/mutate.py`): no-account → anomaly **7
failed**; pending / refused not opened **3**; opening adds to the 20 **3**; no link **5**; a link for an open account
**5**; the webhook never sends the welcome **4**; no retry after losing the account race **1**; the opening not
conditional **1** (a first run left this one uncaught → the « opened meanwhile » test was added); control **44
passed**. Full backend **385 passed** (368 + 15 + 2).

**K4 — DONE (2026-10-06).** Code: `backend/trials.py` — module docstring; `list_pending()` adds `account_open` (the
request's account is `active`); new `unopened_account(db, email)` (a `pending` or `rejected` account for that e-mail);
`_pending_request_and_user` accepts an account `pending` **or `active`**; new `_decide()` (the request's status and
`decided_at`, `WHERE status = 'pending'` — else rollback + 409 « Cette demande a déjà été traitée. »); `validate()` →
`(request, user, already_open)`: conditional activation `WHERE status = 'pending'`, otherwise `page_credits +=
TRIAL_CREDITS`; `reject()`: `rejected` only `WHERE status = 'pending'` (an open account stays as it is); both refresh
the request before returning it. `purge()` unchanged (it already keeps an `active` account). `backend/schemas.py`
`TrialRequestOut.account_open: bool = False`. `backend/emails.py` `trial_credits_added(user)` — subject « 20 documents
offerts ajoutés à votre espace ScanID », body « Votre demande d'essai est validée : 20 documents offerts ont été ajoutés
à votre espace ScanID. », « Votre espace », « Votre identifiant », « Votre mot de passe : celui que vous avez choisi
(sinon, « Mot de passe oublié ? » sur la page de connexion). » (no link). `backend/main.py`:
`validate_trial_request` — already open → that e-mail, kind `trial_credits`, no link; otherwise unchanged;
`reject_trial_request` docstring; `signup_for_pack` — `trials.unopened_account()` first: such an account (waiting or
refused trial) takes the form's names, phone, password (hashed), company, SIRET, VAT, billing address, becomes `active`
with **0 credits** in one conditional `UPDATE … WHERE status IN ('pending','rejected')` (0 rows → rollback + the same
400 « … Connectez-vous pour acheter ce pack. »); the trial request is not touched; an open account → 400 as before; the
new-account branch unchanged (the 7 billing fields via one dict). **Answer to Alex's « Packs » question: yes — until
now that e-mail was refused (« Un compte existe déjà… Connectez-vous… », and the account could not log in); now it
buys.**
Tests (+12): `test_unit_purchase.py` **51** (+7): the admin list's `account_open` (True after a purchase, False
otherwise); « Valider » after a purchase → `validated`, credits 10 + 20, no new link, e-mail `trial_credits` without a
link; « Refuser » after a purchase → request `rejected`, account `active` with its 5, no e-mail, its link kept, a later
« Valider » → 409; the purge 1 year later → both requests (waiting + refused, each followed by a purchase) deleted,
both accounts kept `active` with their credits and purchases; « Valider » / « Refuser » at the moment a purchase opens
the account (the payment lands between the read and the write) → 8 + 20 / still `active` with 8; two decisions at once
→ 409, the account still `pending` with 20. `test_pack_purchase.py` **+4**: a waiting trial e-mail (other letter case)
→ 200, the **same** account (id), `active`, 0 credits, the form's identity / SIRET / VAT / address, its password logs
in, the request still `pending`, the checkout URL's `client_reference_id` = that id; then the pack webhook → 1 000;
then `validate` → `already_open`, 1 020; a refused trial e-mail → 200, `active`, 0, request still `rejected`; a
validated trial = an open account → 400 « Connectez-vous », no purchase; an account opened by a purchase while the
form is sent → 400, the account untouched (7 credits, the trial's name, no password). `test_email_wording.py` **11**
(+ `trial_credits_added`). Mutations (`k4/mutate.py`, 4 test files, control **112 passed**): Valider / Refuser refuse an
open account **3 failed**; Valider does not add the 20 **3**; activation not conditional **3**; Refuser closes an open
account **2**; decision not conditional **1**; `account_open` always False **1**; Valider always sends the welcome +
link **1**; signup refuses a waiting trial e-mail **3**; signup keeps the 20 **2**; signup update not conditional
**1**. Full backend **397 passed** (385 + 12).

**K2 — DONE (2026-10-06).** `tr -d '\r' < frontend/payment_scanid/tarifs.html` → `sha256sum -c` against Alex's
`b5765cef…0645` OK → copied over `frontend/ScanID-nouveau-site-2026-09-30/nouveau-site/tarifs.html` (19 405 bytes, mode
644 kept). `git diff` = **one line** (l. 96, the « À la carte » button); `?v=202609302115` 4 × before and after. Build
`VITE_API_URL=/api npm run build` → 0 pages rewritten, no `/fonts/`; guard **5/5**; `dist/tarifs.html` == the source;
the folder's **63 files == `dist/` byte for byte**. Browser (scratchpad `k2/tarifs_check.cjs`: `dist/` on a local static
server, `/api/config` answered by the script, `buy.stripe.com` intercepted; desktop 1280 + phone 375; `signup` false
**and** true): « Acheter à l'unité » visible, `class="btn btn--line"` (no `js-buy`), href = the unit link, click →
`https://buy.stripe.com/8x2eVc3DF4cQcQF2Elebu05` in all 4 runs; « Commencer par l'essai » 0 × on the page; the Pack 100
button → its Stripe link with `signup` false, `/app/inscription?pack=100` with `signup` true; no console error.
Screenshots looked at (the card « À la carte · 1,50 € HT le document · Acheter à l'unité »). The live Stripe page:
finding 12. Nothing else changed in the site source.

### K.5 How to ship task K — the ship steps, the server runbook, the answers for Alex (stage K7)

**Who does what:** the assistant alone — A1, A3, A4 and the public checks after B7 / B10, C's dates; everything else needs the user (A2 commit + push, §0.3; Stripe B0 / B8; the server B1–B7, B10, B11 — `sudo` and the secrets; B9 with Alex; C forwarded by the user).

**Order, and why:** **A** first — the new code must be live before the secret: with the secret and the old code, an à la
carte purchase by an e-mail without an account would only produce an anomaly e-mail, and a waiting trial's account would
be credited but stay closed. Then **B the same day** — A publishes « Acheter à l'unité » on tarifs.html, and until B7
every payment's delivery fails (503) and Stripe retries it (the switch-over rule, C.8). Then **C** (forward to Alex).
**The user runs every command, ONE per message, and pastes the output** (the user's rule; §0.3: the assistant never
commits). Secrets never in the chat: typed at hidden prompts on the server; nothing pasted back shows them.

**A. Ship**
1. `cd /home/lasha/Public/new && git status --short` → the 21 ` M` of §K.0, no `??` (the folder is ignored since K8).
2. `cd /home/lasha/Public/new && git add . && git commit -m "À la carte: tarifs link, purchases open accounts, in-app link" && git push origin master`
   — `git add .` may replace `git add -u` (the user's habit; checked after K8: from the repo root both stage the same
   21 paths — never from a subfolder, where `.` means only that subfolder). `git add -u` stages the 21 tracked files; since K8 `git add .` stages exactly the same (`.gitignore` ignores
   `frontend/payment_scanid/` — Alex's PDF, a CRLF copy of tarifs.html, an unused favicon, LibreOffice's lock file —
   and every `.~lock.*#`). To keep Alex's PDF in Git anyway: delete the `/frontend/payment_scanid/` line from
   `.gitignore`, then `git add` the PDF by its path.
3. The assistant watches « CI » and « Deploy » (GitHub API) → both green. « Deploy » builds the frontend, syncs `dist/`,
   `ops/`, `deploy/`, `backend/` (never `.env`), `pip install` (no new package), restarts `travelapp.service`. Task K
   changes no nginx file (no reload needed), no model (no migration), no environment variable name (the three Stripe
   variables exist since task F).
4. Laptop checks (the assistant, public, read-only): `/tarifs.html` = 19 405 bytes, SHA-256 `b5765cef…0645`, « Acheter à
   l'unité » → `https://buy.stripe.com/8x2eVc3DF4cQcQF2Elebu05`; `/app/` serves a new bundle containing « Acheter des
   documents à l'unité »; `/api/config` → `{"signup":false,"trial":true}`; `POST /api/stripe/webhook` without a
   signature → **503** (no secret yet → B now). Then mark §K.0 « code SHIPPED » with the commit hash.

**B. Server and Stripe**
- **B0** (browser, Stripe — no command): (a) accept Alex's invitation (Stripe's e-mail of 03/10); (b) Workbench →
  Webhooks → the endpoint: **URL** `https://scanid.fr/api/stripe/webhook` and **event** `checkout.session.completed`
  (Alex's « please check both »); suggest adding `checkout.session.async_payment_succeeded` (a delayed method — SEPA
  debit, bank transfer — is then credited when the money arrives; the app handles both events); (c) note the endpoint's
  **failed deliveries** of the last 3 days (C.8); (d) the unit link's id: Payment Links → « Document à l'unité » →
  `plink_…` (on its page); (e) a **restricted key**: Developers → API keys → « Create restricted key » → **Checkout
  Sessions: Read**, everything else None (if the role Alex gave cannot create keys: Alex grants one that can, or creates
  it himself while B4's prompt waits — the key never travels by e-mail or chat); (f) the signing secret: « Reveal » on
  the endpoint (`whsec_…`). Keep the Stripe tab open for B4.
- **B1.** `ssh -o ServerAliveInterval=30 lasha@87.106.22.235`
- **B2.** look, values hidden: `sudo grep -nE '^\s*#?\s*(STRIPE_|PUBLIC_SIGNUP)' /opt/travelapp/backend/.env | sed -E 's/=.+/=<set>/'; sudo wc -l /opt/travelapp/backend/.env`
  → expected: no line (`signup` false today = no secret) and 13 lines (§I.0.1 server facts + task J). Anything else:
  stop and read it before B4.
- **B3.** backup outside `backend/` (« Deploy » runs `rsync --delete` there): `sudo cp -a /opt/travelapp/backend/.env ~/env-before-stripe && sudo ls -l ~/env-before-stripe`
  → `-rw------- 1 deploy deploy …`.
- **B4.** the four lines — the hold `PUBLIC_SIGNUP=0` (keeps `signup` false until the test purchase, §G.5 C), the secret
  and the key at hidden prompts, the link id at a visible one; checks the characters and the prefixes (a test-mode
  `rk_test_` key is refused); idempotent (a re-run replaces the four lines); owner and mode kept (GNU `sed -i`, `tee -a`).
  **Dry-run in K7 on a 13-line copy: appended → 17 lines; re-run → still 17, values replaced; a trailing space, a
  `rk_test_` key or an empty value → STOP, nothing changed.**
  ```bash
  sudo -v && IFS= read -rsp 'Webhook signing secret (whsec_...): ' W && echo && IFS= read -rsp 'Restricted key (rk_live_...): ' K && echo && IFS= read -rp 'Payment link id (plink_...): ' L && case "$W$K$L" in *[!A-Za-z0-9_]*) echo "STOP: unexpected character - nothing changed";; *) case "$W:$K:$L" in whsec_?*:rk_live_?*:plink_?*) sudo sed -i -E '/^(PUBLIC_SIGNUP|STRIPE_WEBHOOK_SECRET|STRIPE_UNIT_PAYMENT_LINK_ID|STRIPE_API_KEY)=/d' /opt/travelapp/backend/.env && printf 'PUBLIC_SIGNUP=0\nSTRIPE_WEBHOOK_SECRET=%s\nSTRIPE_UNIT_PAYMENT_LINK_ID=%s\nSTRIPE_API_KEY=%s\n' "$W" "$L" "$K" | sudo tee -a /opt/travelapp/backend/.env > /dev/null && echo appended;; *) echo "STOP: a value does not start with whsec_ / rk_live_ / plink_ - nothing changed";; esac;; esac; unset W K L
  ```
  → `appended`.
- **B5.** diff, secrets hidden: `sudo diff ~/env-before-stripe /opt/travelapp/backend/.env | sed -E 's/^> (STRIPE_WEBHOOK_SECRET|STRIPE_API_KEY)=.*/> \1=<hidden>/'; sudo ls -l /opt/travelapp/backend/.env`
  → `13a14,17`, `> PUBLIC_SIGNUP=0`, `> STRIPE_WEBHOOK_SECRET=<hidden>`, `> STRIPE_UNIT_PAYMENT_LINK_ID=plink_…`,
  `> STRIPE_API_KEY=<hidden>`; still `deploy deploy` `-rw-------`.
- **B6.** the key, tested **before** the restart (the running service does not read the new lines until B7):
  ```bash
  sudo -u deploy /opt/travelapp/venv/bin/python -c "from dotenv import dotenv_values; import urllib.request; k = dotenv_values('/opt/travelapp/backend/.env')['STRIPE_API_KEY']; r = urllib.request.urlopen(urllib.request.Request('https://api.stripe.com/v1/checkout/sessions?limit=1', headers={'Authorization': 'Bearer ' + k}), timeout=20); print('KEY OK', r.status)"
  ```
  → `KEY OK 200`. `HTTP Error 401` = a wrong key → redo B4; `HTTP Error 403` = the key lacks « Checkout Sessions:
  Read » → fix it in Stripe → redo B4.
- **B7.** `sudo systemctl restart travelapp.service; sleep 5; systemctl is-active travelapp.service; curl -s http://127.0.0.1:8001/config`
  → `active`, `{"signup":false,"trial":true}` (the hold). The assistant (public): `POST /api/stripe/webhook` without a
  signature → **400** (was 503) = the secret is in place (Alex's check 1, live). **Tell Alex now** (C.2, C.8).
- **B8.** (Stripe, browser) the failed deliveries of B0 c: Stripe retries them by itself (hours apart), or « Resend »
  each now → each must show **200** (this also proves the secret) — **except** a unit purchase Alex already credited by
  hand (C.8). A resent pack from the site's direct link (no account reference) answers `unmatched` → Alex gets the
  « à rattacher » e-mail, as before — no double credit.
- **B9.** the test purchase together (Alex's « one test purchase together »), live card, a test address the user reads
  and that has no account: (a) `https://scanid.fr/tarifs.html` → « Acheter à l'unité » → « Document à l'unité » 1,80 € →
  quantity 1, the address, a name, a business name, a phone → pay → within a minute « Votre espace ScanID est ouvert —
  1 document disponible » → its link (48 h) → a password → login « Crédits : 1 », « Mon compte » → « Mes achats » « À la
  carte · 1 document »; in Stripe « Resend » that event → 200, credits unchanged (check 3, live); (b) from the app:
  « Mon compte » → « Acheter des documents à l'unité » → Stripe shows the address, not editable → 1 → pay → « Crédits :
  2 », e-mail « Votre document ScanID est disponible »; (c) optional — the packs' path has never run live:
  `https://scanid.fr/app/inscription?pack=100` opened directly (the hold keeps the site's buttons on Stripe) → another
  test address → 118,80 € → « Crédits : 100 », « Mes achats » « Pack 100 ». Afterwards: refunds in Stripe if wanted (a
  refund does not remove credits) and delete the test accounts in « Gérer les utilisateurs ».
- **B10.** `signup` → true: `sudo sed -i '/^PUBLIC_SIGNUP=0$/d' /opt/travelapp/backend/.env && sudo systemctl restart travelapp.service; sleep 5; systemctl is-active travelapp.service; curl -s http://127.0.0.1:8001/config`
  → `active`, `{"signup":true,"trial":true}`. The assistant (public): `/api/config` the same; on the site « Choisir ce
  pack » → `/app/inscription?pack=…` (`core.js` rewrites `.js-buy`); « Acheter à l'unité » still → Stripe.
- **B11.** `sudo rm ~/env-before-stripe; ls -l ~/env-before-stripe` → « No such file or directory ».

**C. Answers for Alex** (the user forwards them; English, like his PDF)
1. **Website.** tarifs.html replaced with your file byte for byte (SHA-256 `b5765cef…0645` checked), in our deployment
   source too — live since <A's date>. Your test: on /tarifs.html, « Acheter à l'unité » opens « Document à l'unité »,
   1,80 €.
2. **Webhook.** Endpoint URL and event checked; the signing secret is in place since <B7's time> — payments are credited
   automatically from now on. Suggestion: add `checkout.session.async_payment_succeeded` to the endpoint's events if a
   delayed payment method can be used on the links.
3. **The three checks — confirmed.** (1) A request without a valid Stripe signature — missing, forged, or more than 5
   minutes old — is rejected (HTTP 400); nothing is read or written. (2) Credits are added only when `payment_status` is
   `paid`; a completed but unpaid session is acknowledged and ignored, and credited when
   `checkout.session.async_payment_succeeded` arrives. (3) A session is credited once: its id is stored under a unique
   constraint; a repeated event answers « duplicate »; two simultaneous deliveries credit once. Proven by the automated
   tests and on a production-like stack (nginx, PostgreSQL, events signed like Stripe's).
4. **Crediting unit purchases — as you specified.** When: `payment_link` = this link. How many: the line item's quantity,
   read from Stripe with a read-only restricted key — never the amount. Which account: the checkout e-mail, case-insensitive
   (the app's own link names the account by its id, 7). Open account → credits added + « Vos N documents ScanID sont
   disponibles ». No account → account opened (login = the e-mail; the name, business name and phone typed on Stripe's
   page), credited, welcome e-mail « Votre espace ScanID est ouvert — N documents disponibles » with the link to choose
   the password (48 h; afterwards « Mot de passe oublié ? »). Trial waiting → opened at once with the purchased credits
   only; « Valider » later adds the 20 and sends « 20 documents offerts ajoutés à votre espace ScanID » (no password link —
   the account already has its access); « Demandes d'essai » marks such a request « Compte déjà ouvert par un achat »;
   « Refuser » and the 30-day clean-up remove the request only, never the account. Trial refused → like no account.
   Not credited automatically (you get « Paiement Stripe à rattacher manuellement » with the reason; nothing is created):
   the e-mail belongs to two accounts (different letter case) or is another account's login name, it is missing or
   invalid, the app's link names an unknown account, Stripe cannot be read.
5. **Access — as specified.** A unit purchase never logs anyone in and never changes the e-mail or the password of an
   open account; the password link goes to the account's own address, and only when the purchase opened the account.
6. **Packs — your question.** Yes: until now that e-mail was refused (« Un compte existe déjà avec cette adresse email.
   Connectez-vous pour acheter ce pack. ») and that account could not log in. Now /app/inscription accepts it: the same
   account takes the details and the password typed in the form, opens with 0 credits, the pack arrives with the payment;
   the 20 trial documents still come only with « Valider ». The same for a refused trial's e-mail (your table: « same as
   no account »). An open account is still asked to log in.
7. **Optional — done.** In the app, « Mon compte » → « Mes achats » → « Acheter des documents à l'unité » opens your link
   with `client_reference_id` (the account's id) and `locked_prefilled_email` (its e-mail, not editable on Stripe's page):
   the right account is credited whatever happens. Admins do not see it.
8. **The switch-over — please read before the secret goes in.** A payment whose delivery failed is retried by Stripe
   for up to 3 days; once the secret is in place, each retry is credited automatically. So: from now on, do not credit
   unit purchases by hand. A unit purchase you already credited by hand less than 3 days before the secret went in will
   be credited a second time by its retry: tell us which (customer e-mail, quantity), or lower that account's « Crédits »
   by the quantity in « Gérer les utilisateurs » after the automatic credit (the customer receives « Vos N documents… »).
   Payments older than 3 days are no longer retried: credit those by hand as before. Packs bought on the site while
   `signup` is false carry no account reference: as before you get the « à rattacher » e-mail — no double credit.
9. **Refunds.** A refund in Stripe does not remove credits: adjust « Crédits » by hand.

---

## J. TASK J (2026-10-03, evening) — THE APP'S OWN MAILBOX devis@scanid.fr (§I.0.1 item 7a)

### J.0 State and checklist — ✅ TASK J COMPLETE (2026-10-03 ≈ 18:34 UTC); next work = §I.0.1 item 6, then « Also open »

**The user's rule for this task: ONE instruction per message** (« You provide one instruction each time for me »); the
user runs every Git / server command and pastes the output; the assistant checks GitHub and the public site itself.

- [x] **J1 — code + tests (assistant): DONE** — §J.4; backend **368 passed**
- [x] **J2 — DONE: committed `82acbd6` « Add a second email on to the app on IONOS server » (the user's own message),
  pushed (`origin/master` = `82acbd6`); « CI » #28 ✅ and « Deploy » #23 ✅ (18:04 / 18:03 UTC, read from the API);
  the commit = exactly the 5 paths; `/api/config` after the deploy's restart still `{"signup":false,"trial":true}`
  (still contact@ until J4).** History: the user commits + pushes (its own commit, not mixed with task I's `a769f33`); « CI » / « Deploy » green
  (the assistant reads them from the GitHub API). **Instruction given:** `cd /home/lasha/Public/new && git add . &&
  git commit -m "Mail: MAIL_REPLY_TO setting for the app's own mailbox" && git push origin master` — expected `git status --short` before it: 5 ` M` paths
  (`SCANID-HANDOVER.md`, `backend/.env.example`, `backend/config.py`, `backend/mailer.py`,
  `backend/tests/test_account_foundation.py`)
  The user: « I already pushed what is commited! » → true for task I (`a769f33` = `origin/master`, checked); J's 5
  paths are NOT committed yet (checked) → explained, the same instruction repeated.
- [x] **J3 — DONE ≈ 18:12 UTC (nginx reloaded, ALL CHECKS PASSED; laptop checks green — §J.4)** — §J.5 steps 1–2 (ssh; the nginx reload + `verify-front-end.sh` = task I's item 5 step 3) —
  **instruction given (2026-10-03 ≈ 18:05 UTC): step 2, with step 1 as « connect first if not already in »**
  The user asked what `-o ServerAliveInterval=30` is → answered: optional; the client sends a keep-alive every 30 s
  of silence, so an idle session does not freeze or drop (as on 2026-10-03 during the nano pause); same instruction kept.
- [x] **J4 — DONE (≈ 18:31 UTC): sending as devis@, replies to contact@ (checked in Gmail)** — §J.5 steps 3–7 (backup → swap → diff → test e-mail **before** the restart → restart) — **step 3
  (backup) DONE:** `~/env-before-devis` `-rw------- deploy deploy 2840 Oct 3 15:42` (= the `.env` since B, unchanged).
  **Step 4 (swap) DONE: « swapped »** (no STOP: the password has no `'` / `\`). **Step 5 (masked diff) instruction
  given.** The running service still uses the contact@ lines until step 7's restart.
  **Step 5 DONE:** exactly the expected `10,11c10,13` (the two contact@ lines → the four new lines); `.env` still
  `-rw------- deploy deploy`, 2902 bytes, Oct 3 18:21. **Step 6 (test e-mail before the restart) instruction given.**
  **Step 6 DONE: « SENT »** — arrived in the **inbox** (not spam) of the user's own Gmail address (not recorded here:
  this repository is public) ≈ 18:26 UTC, From « ScanID <devis@scanid.fr> » → the devis@ login works and IONOS
  accepts the From. The `Reply-To` was not looked at yet (the user did not open « Reply ») → checked after step 7.
  **Step 7 DONE (≈ 18:27 UTC):** `active`, `127.0.0.1:8001/config` → `{"signup":false,"trial":true}`; public check by
  the assistant 18:28 UTC: `/api/config` the same, `/`, `/app/`, `/essai.html` 200. **The app now sends as devis@.**
  **Next instruction given: the Reply-To check** (in the test e-mail, « Reply » → the To field must read
  contact@scanid.fr); then step 8 (delete `~/env-before-devis`).
  The user: « now alex can change both passwords as he want? » → answered: **contact@ — yes, freely** (its password
  left the server's `.env` with the swap; contact@ is now only where notifications arrive); **devis@ — no**: the server
  logs in with it — a change makes every app e-mail fail silently until the user redoes §J.5 steps 4 + 7 with the new
  password (handed over safely, the same day); the app's « admin » password is unrelated (free, in « Mon compte »).
  Note: `~/env-before-devis` still holds the old contact@ password → step 8 deletes it. Reply-To check still pending.
  **Step 8 DONE (≈ 18:34 UTC):** `sudo rm ~/env-before-devis` → « No such file or directory » (the old contact@
  password is gone from the server). **✅ TASK J COMPLETE.**
  **Reply-To check DONE (≈ 18:31 UTC):** Gmail's « Reply » box on the test e-mail addresses **contact@scanid.fr**
  (screenshot; nothing sent). **J4 complete. Step 8 (delete `~/env-before-devis`) instruction given.**
- [x] **J5 — DONE (≈ 18:34 UTC): backup deleted (« No such file or directory »); laptop checks green; memory notes
  updated. ✅ TASK J COMPLETE — the app sends as devis@, replies go to contact@.** Was: **J5 — finish:** laptop checks (assistant: §I.5 step 4 + `/api/config`), §J.5 step 8 (delete the backup), mark J
  done, §I.0.1 item 5 → SHIPPED, memory notes

### J.1 The demand, verbatim (user, 2026-10-03, evening)

> Alex has created this email: devis@scanid.fr!
> Now i have the password and we can setup to avoid manual changing each time Alex changes password

Then, mid-turn: « You provide one instruction each time for me ».

### J.2 Findings (read in the code before touching anything)

- `mailer.send(to, subject, body, kind, reply_to=None)`: From = `config.mail_from()` (`MAIL_FROM`, default « ScanID
  <contact@scanid.fr> »); a `Reply-To` only when the caller passes one — only `trial_notification` does (the requester,
  `main.py` ≈ l. 895). The SMTP login = `SMTP_USERNAME` / `SMTP_PASSWORD`; the envelope sender = the From address.
- IONOS sends only under the authenticated mailbox → once the login is devis@, **From must be devis@** too. Without a
  `Reply-To`, customers' replies (the welcome e-mail says « Répondez simplement à cet e-mail ») would then reach devis@
  instead of contact@ — a change of today's behaviour (§0.1) → **the small code change is necessary**.
- The server's `.env` is read by python-dotenv (`main.py` `load_dotenv()`): inside single quotes everything is literal
  except `\\` and `\'` → the swap command refuses a password holding `'` or `\` (nothing changed then; another quoting
  is needed — ask).
- No DNS change: SPF `include:_spf-eu.ionos.com` and the IONOS DKIM keys cover every mailbox of scanid.fr; From stays on
  scanid.fr → DMARC-aligned. `MAIL_ADMIN_TO` (trial requests, payment anomalies) stays contact@ (default).
- Bounces go to the envelope sender = devis@ → **later, with Alex (parked):** forward devis@'s incoming mail to contact@
  in its IONOS settings, so bounces and stray replies are seen.

### J.3 Decisions

- `config.mail_reply_to()` = `MAIL_REPLY_TO`, **default empty = today's behaviour** (no `Reply-To`). `mailer.send`
  applies it when the caller gives no `reply_to` — in both backends (the outbox records the effective value). The
  caller's `reply_to` wins (the trial notification keeps the requester).
- Server lines after J4: `SMTP_HOST=smtp.ionos.fr` (unchanged), `SMTP_USERNAME=devis@scanid.fr`, `SMTP_PASSWORD='<the
  devis@ password>'`, `MAIL_FROM='ScanID <devis@scanid.fr>'`, `MAIL_REPLY_TO=contact@scanid.fr`. Customers then see
  « ScanID <devis@scanid.fr> »; « Répondre » goes to contact@scanid.fr.
- **Rule after J:** contact@'s password can change freely (the server no longer holds it). devis@'s password must not
  change without telling the user (the server holds it) — to say to Alex when item 4 is un-parked (and drop the
  optional-mailbox paragraph from item 4's message: done; answer 1's « one rule » now concerns devis@).

### J.4 Stages — record

- **J1 — DONE (2026-10-03, evening).** `backend/config.py`: `mail_reply_to()` (`MAIL_REPLY_TO`, stripped, default
  empty). `backend/mailer.py` `send()`: `reply_to = reply_to or config.mail_reply_to() or None` before both backends.
  `backend/.env.example`: a commented `# MAIL_REPLY_TO=contact@scanid.fr` line. `backend/tests/test_account_foundation.py`:
  two tests (outbox: unset → `None`, set → contact@, the caller's value wins; SMTP: login devis@, From « ScanID
  <devis@scanid.fr> », Reply-To contact@). Backend **368 passed** (366 + 2); the two new tests **fail without** the
  `mailer.py` line (checked, then restored). No README change (it documents no mail setting).
  **Runbook dry-run (scratchpad copy, `sudo` removed):** step 4 keeps `$ # " % ; & |` and leading / trailing spaces
  exactly (read back with python-dotenv), refuses `'` and `\` with the file unchanged, is idempotent (two runs = one),
  keeps mode 600; step 6's one-liner (outbox backend instead of SMTP) → « SENT », the message carries `From: ScanID
  <devis@scanid.fr>` and `Reply-To: contact@scanid.fr`.
- **J2 — DONE:** `82acbd6` (5 paths), « CI » #28 ✅, « Deploy » #23 ✅.
- **J3 — DONE (≈ 18:12 UTC):** the user's paste — `nginx -t` « syntax is ok » / « test is successful »; `verify-front-
  end.sh` 8 × OK, « ALL CHECKS PASSED ». Laptop checks by the assistant: all green (the list in the SHIPPED line of §I.0).
  → F, G, H, I marked ✅ SHIPPED.

### J.5 Server runbook — the user's, ONE instruction per message

1. `ssh -o ServerAliveInterval=30 lasha@87.106.22.235`
2. nginx (task I item 5 step 3; covers F, G, H, I): `sudo nginx -t && sudo systemctl reload nginx && bash
   /opt/travelapp/ops/verify-front-end.sh` → « syntax is ok », « test is successful », « ALL CHECKS PASSED ». If
   `nginx -t` fails nothing is reloaded and the site keeps running — paste the output.
3. backup outside `backend/` (« Deploy » runs `rsync --delete` there): `sudo cp -a /opt/travelapp/backend/.env
   ~/env-before-devis && sudo ls -l ~/env-before-devis` → `-rw------- 1 deploy deploy 2840 …`
4. swap — `sudo -v` first (so sudo's own prompt, if any, comes before the mailbox prompt), the password at a hidden
   prompt (never on a command line, never in the chat), idempotent (re-running gives the same file), owner and mode kept
   (GNU `sed -i` keeps them; `tee -a` appends):
   ```bash
   sudo -v && IFS= read -rsp 'devis@scanid.fr password: ' P && echo && case "$P" in *\'*|*\\*) echo "STOP: the password contains ' or \\ - nothing changed";; *) sudo sed -i -E '/^(SMTP_USERNAME|SMTP_PASSWORD|MAIL_FROM|MAIL_REPLY_TO)=/d' /opt/travelapp/backend/.env && printf "SMTP_USERNAME=devis@scanid.fr\nSMTP_PASSWORD='%s'\nMAIL_FROM='ScanID <devis@scanid.fr>'\nMAIL_REPLY_TO=contact@scanid.fr\n" "$P" | sudo tee -a /opt/travelapp/backend/.env > /dev/null && echo swapped;; esac; unset P
   ```
5. diff, the passwords hidden: `sudo diff ~/env-before-devis /opt/travelapp/backend/.env | sed -E
   's/(SMTP_PASSWORD=).*/\1<hidden>/'; sudo ls -l /opt/travelapp/backend/.env` → expected `10,11c10,13`, `<` the old
   SMTP_USERNAME (contact@) and SMTP_PASSWORD, `>` the four new lines; still `deploy deploy` `-rw-------`.
6. a real test e-mail **before** the restart (the running service still uses the old lines until step 7), through the
   app's own mailer as the service would send it; the user types the destination address at the prompt (one they read):
   **Only after J2's « Deploy » is green** (the `Reply-To` needs the new `mailer.py`):
   ```bash
   sudo -u deploy env PYTHONPATH=/opt/travelapp/backend /opt/travelapp/venv/bin/python -c "from dotenv import load_dotenv; load_dotenv('/opt/travelapp/backend/.env'); import mailer; print('SENT' if mailer.send(input('Send the test to: '), 'ScanID - test devis@', 'Test of the new sender. Reply to this e-mail: the reply must go to contact@scanid.fr.', 'smtp_test') else 'NOT SENT')"
   ```
   → « SENT »; in the inbox: From « ScanID <devis@scanid.fr> », « Reply » addressed to contact@scanid.fr. « NOT SENT »
   + « Email not sent: kind=smtp_test error=SMTPAuthenticationError » = wrong password → redo step 4 (the service is
   untouched: it still runs on the old lines).
7. `sudo systemctl restart travelapp.service; sleep 5; systemctl is-active travelapp.service; curl -s
   http://127.0.0.1:8001/config` → `active`, `{"signup":false,"trial":true}`
8. once everything works: `sudo rm ~/env-before-devis; ls -l ~/env-before-devis` → « No such file or directory »

---

## I. TASK I (2026-10-03) — ALEX'S « THIRD CHECK » LIST — COMMITTED `a769f33` — ✅ SHIPPED 2026-10-03 (NGINX RELOADED)

### I.0.1 ▶ RESUME HERE — THE OPEN ITEMS, IN ORDER (state of 2026-10-03, evening)

**Where things stand:**
- **Code of task I:** done and verified locally (§I.4, I0–I5), **not committed** — the 14 paths of §I.0.
- **Server:** `trial` is **ON** since 2026-10-03 ≈ 15:45 UTC (17:45 Paris): three SMTP lines appended to
  `/opt/travelapp/backend/.env`, the login tested before the restart, `travelapp.service` restarted, `/api/config` →
  `{"signup":false,"trial":true}` (checked on the server and publicly). nginx still **not reloaded**. Nothing else changed
  on the server.
- **Alex:** has not received §I.5's answers, nor his test steps, yet.

**📄 Alex's PDF « Lasha-Third-Check-2026-10-02.pdf » — every item, done or NOT DONE** (asked 2026-10-03: « Mark in
SCANID-HANDOVER.md all prompts what we have not done from attached pdf of this session! »). ✅ done · ⚠️ done here but
not live / not delivered to Alex · ❌ not done.

| PDF item | What Alex asked | Status | What is missing / who | Item below |
| --- | --- | --- | --- | --- |
| 1 | « Confirmed — nothing to do » (the two texts, login form, register 404, 63 files, forms, Stripe links) | ✅ nothing to do | — | — |
| 2 (a) | « **trial → true**, please » | ✅ **ON since 2026-10-03 ≈ 15:45 UTC** (SMTP on the server, with the user) | ❌ the end-to-end trial test (Alex or the user); ❌ Alex not told yet | 3, 4 |
| 2 (b) | « signup stays false for now: correct » | ✅ stays false (nothing to do now) | later, with Alex (Stripe webhook + test purchase) | 7b |
| 3.1 | **The list of accounts** made by the old « Créer un compte » form (date, e-mail, credits), or « none » | ⚠️ **READ 2026-10-03: « none »** (2 uses, 05/08 and 20/08, before go-live; 0 such accounts today) — **not forwarded** (item 4 parked) | needs the VPS journal + database (`sudo`) — the user (§H.5 A). Known so far: each got **5 credits** | 6 |
| 3.2 | E-mail templates: « documents » and « e-mail » everywhere? | ⚠️ answered (**yes**, all six re-rendered — the « Stage I3 » record below §I.4) — **not forwarded** | the user forwards §I.5 answer 3 | 4 |
| 3.3 | Export headers (XLSX, CSV) in sentence case, as in the table? | ⚠️ answered (**yes**, live since 02/10 18:44; proven on real files) — **not forwarded** | the user forwards §I.5 answer 4 | 4 |
| 4 | **The labels inside the app** (8 rows: « Mon compte », « Modifier mon compte », « Gérer les utilisateurs », « Filtrer par utilisateur / destination », « Modifier la destination », « Exportation des données », « Exporter la sélection en Excel / CSV (n) », tab « Passeports » → « Mes documents ») | ⚠️ **done in code** (+ 4 more under « sentence case everywhere », + « Mon compte » in the purchase e-mails), tested — **NOT LIVE: not committed, not pushed** | the user: commit + push → « Deploy » (§I.5 steps 1–2); then forward §I.5 answer 5 | 5, 4 |
| 5 (a) | Optional — **compression** (gzip for CSS / JS / JSON / SVG / XML) | ❌ **NOT DONE** (already in the vhost on the server since 02/10; needs the reload) | the user: `sudo nginx -t && sudo systemctl reload nginx` on the VPS (§I.5 step 3) | 5 |
| 5 (b) | Optional — **`https://www.scanid.fr` → 301 to `https://scanid.fr`**, same path | ❌ **NOT DONE** (same reload) | same | 5 |
| 5 (c) | Optional — **301 `/temoignages.html` → `/presentation.html`, `/iftm/` → `/essai.html`** | ❌ **NOT DONE** (same reload) | same | 5 |

**▶ STATUS 2026-10-03 ≈ 19:00 UTC (re-verified live, the user asked « All what is demanded in this pdf file is already
accomplished? »): EVERY PDF ITEM IS DONE** — 1 ✅; 2 `trial` true ✅ (`signup` false ✅); 4 ✅ live (`a769f33`, bundle
`index-CJFY_9p8.js`: the 8 rows); 5 ✅ live (nginx reloaded ≈ 18:12 UTC: gzip on CSS, JS, JSON, SVG and XML checked;
`www` → 301 same path; the two 301s). 3.1 (« none »), 3.2 (yes), 3.3 (yes) are answered **but not yet sent to Alex**
(item 4 parked). The table below is the earlier state.
The user then asked what exactly was not sent → answered: the three answers of section 3 (3.1 « none », 3.2 yes, 3.3
yes) — today's message to Alex covered only devis@ + the trial test; the earlier long message (§I.0.0b row 2) was set
aside when the user parked Alex's items (sent or not: not confirmed). A short text with the three answers was given,
ready to forward.
« It if to say to Alex that all is ok? » → answered: yes for every PDF item (done, live, checked today), with one nuance:
the trial's full flow (request → Valider → welcome e-mail → « Crédits : 20 ») is confirmed only when Alex's own test
passes (our test proved the sending: devis@ → inbox, Reply → contact@); `signup` stays off as he asked.

So, from the PDF: **❌ not done = 3.1 and 5 (a, b, c)**; **⚠️ not live / not delivered = 4 (not pushed) and the answers
2, 3.2, 3.3 (not forwarded)**; plus the trial test of 2 (a).

**❌ NOT DONE — everything still open from this session** (asked 2026-10-03: « Mark in SCANID-HANDOVER.md all what we
have not done from this session! »). Done, for contrast: PDF section 4 in code (local), 3.2 and 3.3 answered and proven,
section 2 `trial` ON.

| # | Not done | From | Why not yet / who | Item below |
| --- | --- | --- | --- | --- |
| 1 | Task I's code is **not committed, not pushed → not live** (the labels, « Mon compte » in the e-mails, README, tests) | PDF section 4 | §0.3: the user commits and pushes | 5 |
| 2 | **nginx not reloaded** → gzip, `www` → 301, the 301s of `/temoignages.html` and `/iftm/` still not active | PDF section 5 (and tasks F, G, H) | needs `sudo` on the VPS — the user | 5 |
| 3 | **The list of accounts** created by the old « Créer un compte » form (date, e-mail, credits) — or « none » | PDF section 3.1 | needs the VPS journal + database (`sudo`) — the user; Alex only knows « 5 credits each » so far | 6 |
| 4 | **The answers not forwarded to Alex** (§I.5 « Answers for Alex », answer 1 updated) | PDF sections 2–5 | the user forwards them | 4 |
| 5 | **The end-to-end trial test** (request → notification → Valider → welcome e-mail → password → « Crédits : 20 ») | PDF section 2 / prompt 4 (B step 9) | Alex or the user; Alex's steps to forward are in §I.5 | 3 |
| 6 | ~~The server's backup copy `~/env-before-smtp` not deleted~~ — **DONE 2026-10-03 16:32 UTC** | prompt 4 (B step 10) | — | 1 |
| 7 | **The app's « admin » password not changed** — exposed in the chat (screenshot of the `.env`) | prompt 4 (during step 4) | **Alex**, the admin, in the app (« Mon compte ») — the user tells him why | 2 |
| 8 | **The separate app mailbox** (e.g. noreply@) so contact@ password changes never break the app's e-mails | prompt 4 (agreed: after B) | needs Alex (mailbox + sender address), then code + tests + deploy | 7a |
| 9 | **`signup` → true** (Stripe webhook + test purchase) | PDF section 2 (« stays false for now: correct ») | later, with Alex | 7b |
| 10 | The VPS's « System restart required » + 29 updates | seen at login (prompt 4) | the user's call, at a quiet moment | Also open |
| 11 | Task D's checks §D.7.3 steps 5–7 | earlier session (task D) | the user | Also open |

**Open items, in the recommended order** (tick here and the matching box of §I.0 as the user reports them):

**⏸ 2026-10-03, resumed session — the user: « we will forget the tasks that requires Alex's engagemment and we will
continue to resolve tha task that we can do without Alex! »** → items **2, 3, 4 and 7 are PARKED** (not dropped: they
come back when the user brings Alex in; the message for item 4 was given — §I.0.0b row 2 — sent or not, unknown). The
work goes on **without Alex**: **5** (ship task I), **6** (reading the list on the VPS needs no Alex — only sending it
does, with item 4), then **« Also open »** (task D's checks 5–7; the VPS updates + restart, the user's call).

- [x] **1. Delete the server's backup copy** (§I.5 B step 10) — **DONE 2026-10-03 16:32 UTC** (« No such file or directory »). It holds every secret of the server's `.env`, and what it
  guarded is verified (the diff showed only the four added lines; the service restarted with all its other settings). On
  the VPS (`ssh lasha@87.106.22.235`): `sudo rm ~/env-before-smtp; ls -l ~/env-before-smtp` → « No such file or
  directory ».
- [ ] ⏸ PARKED (needs Alex) **2. Change the app's « admin » password** — exposed in the chat on 2026-10-03 (a screenshot of the `.env`'s
  `ADMIN_PASSWORD` line; the value is NOT recorded anywhere here). Browser: https://scanid.fr/app/ → log in as `admin` →
  « Mon compte » → « Nouveau mot de passe » (≥ 12 characters, ≥ 1 uppercase, ≥ 2 digits, ≥ 2 special characters) →
  « Enregistrer les modifications » → log out, log in with the new one. No server change: `ADMIN_PASSWORD` is read only at
  startup, to create `admin` when it does not exist (`main.py` lifespan) — the stored password is the one that counts.
  **Alex is the admin (the user, 2026-10-03) → Alex changes it himself** (best: the new password never travels); tell
  him why (the old one appeared in a chat). If the user also needs admin access afterwards: his own admin account,
  created by Alex in « Gérer les utilisateurs » → « + Nouveau » (the form has a `role` field: `admin`), rather than a
  shared password. (The password change in « Mon compte » goes through `PUT /users/me`, which enforces the policy.)
  **2026-10-03 (resumed session): the message for Alex given to the user (§I.0.0b row 1); the user: « He will change
  the admin password » → Alex informed, change NOT confirmed yet.** Tick when Alex confirms (ask the user at item 6).
  Consequence: the user has no admin access afterwards → item 3 is Alex's.
- [ ] ⏸ PARKED (needs Alex) **3. The end-to-end trial test** (§I.5 B step 9) — by Alex (« Alex's trial test » in §I.5, to forward) or by the
  user with a test address. An e-mail missing (spam folder first) → on the VPS: `sudo journalctl -u travelapp.service
  --since "30 min ago" --no-pager | grep -iE "email (sent|not sent)"` → « Email sent: kind=trial_notification » /
  « …kind=trial_welcome »; « Email not sent: … error=SMTPAuthenticationError » = the mailbox password changed (§I.5 B,
  « After B »). **2026-10-03 (resumed session): Alex runs it** — « Valider » needs the admin login, which is Alex's (item
  2) → his six steps travel in item 4's message; tick when he reports (or run the journal check above if an e-mail is
  missing).
- [ ] ⏸ PARKED (needs Alex) **4. Forward to Alex** — **before sending, update the message of §I.0.0b row 2 (task J,
  2026-10-03): drop the « Optional — a mailbox just for the app » paragraph (done: devis@scanid.fr) and replace the « One
  rule » of section 2 by: contact@'s password may change freely; devis@'s must not change without telling the user (the
  app sends with it — customers see « ScanID <devis@scanid.fr> », replies go to contact@); optionally ask Alex to forward
  devis@'s incoming mail to contact@ (bounces).** Original text: §I.5 « Answers for Alex » (answer 1 updated: `trial` ON + the password rule) and « Alex's
  trial test », plus two requests: change the admin password himself (item 2 — the old one appeared in a chat), and, if
  you both want it, create the app's own mailbox (item 7a: e.g. notifications@scanid.fr, its own password, forwarding
  to contact@, the password handed over safely — it replaces contact@'s password on the server).
  **2026-10-03 (resumed session): the whole message given to the user, ready to send** (§I.0.0b row 2): in the user's
  voice (first person — no « Lasha … him »), answers 1–7 of §I.5 condensed, « Alex's trial test », the optional
  mailbox request; the admin-password request left out (already sent, item 2); « live with the next deployment — I'll
  confirm » for sections 4 and 5 (the confirmation goes with item 6's list). Waiting for « sent ».
- [x] **5. Ship task I — ✅ DONE 2026-10-03 (all five steps; the reload in §J.5 step 2).** **Steps 1–2 DONE: committed `a769f33` « App: sentence-case labels and « Mes documents » tab »,
  pushed (`origin/master` = `a769f33`), « CI » ✅ and « Deploy » ✅ (both 17:46 UTC, read by the assistant from the GitHub
  API — the repository `Lasha101/new` is public), live bundle `index-CJFY_9p8.js` = task I is LIVE.** Left: step 3 (the
  nginx reload — now done inside §J.5 step 2, same server visit), step 4 (laptop checks), step 5 (SHIPPED marks).
  History: ▶ IN PROGRESS (2026-10-03, resumed session): pre-commit check by the assistant —
  `git status --short` = §I.0 (14 paths, nothing staged), no secret in the handover's diff (only the empty
  `.env.example` lines quoted), the user's commits are one-line messages without a trailer; **step 1a DONE:** `git add .`
  → 14 staged (13 `M ` + `A  frontend/tests/e2e/labels.spec.js`, nothing unstaged — checked by the assistant).
  **Step 1b given** (the user asked for a short message): `git add . && git commit -m "App: sentence-case labels and « Mes documents » tab"`
  (the second `git add .` picks up the handover's latest note). §I.5 steps 1–5: `git add .` → commit (the message is there) → `git push origin master` →
  « CI » / « Deploy » green → the nginx reload on the VPS + `verify-front-end.sh` → the laptop checks (the assistant can
  run them) → mark F, G, H and I SHIPPED + the memory notes.
- [x] **6. The list for Alex — READ ✅ 2026-10-03: « none »** (details below; the sending goes with parked item 4).
  (his question 3.1) — was ▶ **IN PROGRESS (2026-10-03 ≈ 18:35 UTC): §H.5 A steps 1–2 given as
  one command** (the journal's first line, the count of request lines, the `POST /users/register … 200` lines — no
  personal data in that output). For step 3 (the database query: e-mails) the chat gets the e-mails **masked**; the
  full list goes from the server to Alex only when item 4 is un-parked.
  **Steps 1–2 DONE (≈ 18:37 UTC):** the journal starts **2026-08-05 21:32:56 UTC** (the service's first start — before
  go-live 2026-09-08, so it is complete; nginx's logs not needed); 12 704 request lines; **two** `POST /users/register
  … 200`: **2026-08-05 21:38:01 UTC** (5 min after the first start) and **2026-08-20 18:58:16 UTC** — both before
  go-live, both from the same client IP (not recorded: this repository is public) → most likely set-up tests; **none
  since go-live**. **Step 3 instruction given:** the §H.5 A query with the e-mail and the user name **masked** (`left()`
  / `substring()` — no regex escapes; column names checked in `models.py`).
  **Step 3 DONE (≈ 18:40 UTC): `(0 rows)`** — no `user` account without a trial request or a purchase exists today.
  **→ The answer to Alex's 3.1 = « none »:** « The old form was used only twice, on 05/08 and 20/08/2026, before the
  go-live (set-up tests, both from the same address); today the database holds no customer account other than those
  that came from a trial request or a purchase. So: none — nothing to clean up. » Reading DONE; **sending it waits for
  item 4** (add it to that message). Next: « Also open » — task D step 6 (instruction given).
  **Task D step 6 result (≈ 18:43 UTC):** the journal grep since 2026-10-02 printed **nothing** — no « Database startup
  check failed », no « must be owner », but also no « Schéma mis à jour » line; `SELECT sex, count(*) FROM passports
  GROUP BY sex` → **`F | 2`** only: the column exists, and the table holds just 2 documents, both imported after the
  « Sexe » update (no empty `sex` row). The missing INFO line is unexplained (`main.py` `basicConfig(INFO)`; the
  redaction filter never drops a record) → one read-only check over the whole journal, which also answers the user's
  « About emails all is ok? » from the running service: `sudo journalctl -u travelapp.service --no-pager -o short-iso |
  grep -E "Schéma mis à jour|Email (sent|not sent)" | tail -15` (the mailer logs only the kind — never a recipient).
  **The user then (before running it): « Alexandre can change password for wich mail tell me and he wqill test this
  mail with real request! Will it cover all checks that you suggest me? »** → answered: contact@ — freely; devis@ — no
  (or tell the user the same day + hand over safely); the app's « admin » password — freely. Alex's real trial request
  covers **every e-mail check** (and better than the log grep: the RUNNING app sends both e-mails from devis@, the
  notification's Reply → the requester, the welcome's Reply → contact@, « Crédits : 20 ») = §I.0.1 item 3 **un-parked**,
  run by Alex. It does not cover the task D log question (« Schéma mis à jour » missing) — the grep stays **optional,
  pending**. **Instruction given: send Alex a short message** (the password rule + his six test steps, updated for
  devis@; SIRET / TVA may stay empty — `trials.py` validates SIRET only when given). The full answers of item 4 are
  not in it (item 4 stays parked unless the user asks).
  **The user: « i sened the message to Alex! Now we can continue implement the remaining tasks? » (≈ 18:50 UTC)** →
  Alex has the password rule and his six test steps (items 2–3 now in Alex's hands — waiting for his report). Answered:
  **no code is left to implement**; what remains without Alex, in order: (1) the optional task D log grep (now — read-
  only; also shows whether the app's « Email sent » lines are recorded, useful if Alex's test fails) — **instruction
  given**; (2) the VPS's 29 updates + reboot — the user's call, **not while Alex is testing**; (3) item 4's answers to
  Alex (all PDF items now done: a short « everything is done » message can be prepared on request); (4) task D step 7
  in the browser (optional: Alex already confirmed « Sexe » in the list and the XLSX). With Alex, later: `signup`.
  **Log grep result (≈ 18:55 UTC): EMPTY over the whole journal (since 2026-08-05)** — no « Schéma mis à jour » ever
  (not even task B's of 2026-09-14), no « Email sent / not sent ». **Cause found (reproduced locally):** `database.py`
  l. 24 calls the module-level `logging.info(...)` at import time (the GCP credentials message, since `41231e2`,
  2026-08-05); a module-level `logging.*` call runs `basicConfig()` when the root logger has no handler → root gets a
  stderr handler at WARNING → `main.py` l. 53 `logging.basicConfig(level=logging.INFO)` is then a **no-op** → every
  app INFO line is dropped (after `import main`: root WARNING, `mailer` / `schema_migrations` INFO disabled — checked).
  Consequences: **nothing broken for customers**; WARNING / ERROR lines are recorded, so « Email not sent: … » (ERROR)
  would show — **none in the whole journal** (and before 15:45 UTC e-mail was `disabled`, which also logs at ERROR:
  so no app e-mail was ever attempted before today). « Email sent » (INFO) can never show → the handover's checks that
  expect it are wrong: rely on « Email not sent » (failures) and on the recipient's inbox. **Proposed fix (NOT done —
  not demanded, changes the logging output → asked the user):** `main.py` `logging.basicConfig(level=logging.INFO,
  force=True)` (+ a test: after `import main`, root at INFO and its handler carries the `RedactingFilter`); ship only
  after Alex's test (the deploy restarts the backend). — §H.5 A, read-only on the VPS (the journal's range, the `"POST
  /users/register HTTP/1.1" 200` lines, the database query); then send Alex the list, or « none ».
- [ ] **7. (a) ▶ ACTIVE → §J** (Alex created **devis@scanid.fr**, the user has its password — 2026-10-03 evening);
  (b) ⏸ PARKED (needs Alex). Original text: **Later, with Alex:** (a) a mailbox for the app alone (e.g. noreply@scanid.fr), so that a contact@ password
  change never breaks the app's e-mails — needs Alex's mailbox and the sender address customers will see → code change
  (`MAIL_FROM` + a `Reply-To` contact@: the mailer supports it, no caller sets it yet), tests, deploy, then swap the three
  `.env` lines (order agreed with the user: only after B — B is done). Design noted 2026-10-03: a `MAIL_REPLY_TO` setting
  (unset = today's behaviour) applied in `mailer._build` when the caller gives no `reply_to`; the app sends 5 kinds from
  `main.py` (password_reset, purchase_confirmation, payment_anomaly, trial_notification — which already sets
  `reply_to` = the requester —, trial_welcome); the switch then = `SMTP_USERNAME` / `SMTP_PASSWORD` of the new mailbox +
  `MAIL_FROM='ScanID <noreply@scanid.fr>'` + `MAIL_REPLY_TO=contact@scanid.fr`. **Starts with Alex, not with code** —
  without the mailbox the code changes nothing; not urgent (only needed when the contact@ password changes). **Suggested
  to the user (2026-10-03): `notifications@scanid.fr`** (Alex decides; not `noreply@` — the welcome e-mail says « Répondez
  simplement à cet e-mail »). Alex at IONOS: create it with a password used nowhere else, forward its incoming mail to
  contact@, hand the password over safely. No DNS change (SPF `include:_spf-eu.ionos.com` and the IONOS DKIM keys cover
  every mailbox of the domain; From stays on scanid.fr → DMARC-aligned); (b) C, `signup` → true (§G.5 C: the Stripe
  webhook secret with the `PUBLIC_SIGNUP=0` hold, one test purchase, then drop the hold).
- **Also open:** task D's checks (§D.7.3 steps 5–7); the VPS shows « System restart required » and 29 updates (seen at
  login on 2026-10-03) — a reboot restarts the app and nginx (and so would also apply the pending nginx reload); not part
  of any task: the user's call, at a quiet moment. Since 16:32 UTC the login banner also offers « New release '26.04.1 LTS' » — **do not** run `do-release-upgrade` casually (a major upgrade: Python, PostgreSQL, nginx versions change).

**How to guide (learned this session):**
- One command per message; the user pastes the output. When the user pastes only the command (nothing below it), ask
  them to run it in the **server terminal** (prompt `lasha@ubuntu:~$`) and paste what appears below.
- Secrets never in the chat: a password is typed on the server at a hidden prompt (`read -rsp`), never in a command line
  (shell history); `.env` content is shown only with values masked (`| sed -E 's/(SMTP_PASSWORD=).+/\1<hidden>/'`).
- **No interactive editor over SSH** — `sudo nano` froze the session during a long pause (2026-10-03). Edit
  non-interactively (`… | sudo tee -a`); `ssh -o ServerAliveInterval=30 lasha@87.106.22.235` avoids idle drops. A frozen
  SSH: Ctrl+Q, else Enter then `~.`, else kill the terminal (VS Code trash icon) and reconnect; then look for a stale
  `nano` (`pgrep -a nano` → `sudo kill -9 <pid>` — not a plain kill: nano would write an emergency `.env.save`) and its
  lock file `..env.swp` (`sudo rm -f`).
- Server facts: `/opt/travelapp/backend/.env` = `deploy:deploy` `-rw-------`, 11 lines (7 + a blank line + the 3 SMTP
  lines), **no other copy anywhere** (not in Git; `ops/backup.sh` dumps only the database); « Deploy » runs `rsync
  --delete --exclude '.env'` on `backend/` (never keep a file there); venv `/opt/travelapp/venv`; backend on
  `127.0.0.1:8001` (`/config`); the server clock is UTC (Paris = UTC+2); `sudo` asks for the user's own password.

### I.0.0 THIS SESSION (2026-10-03, the session after task H's) — EVERY PROMPT, WHAT IS DONE, WHAT IS LEFT

| # | Prompt (verbatim, or in substance) | Done | Left |
| --- | --- | --- | --- |
| 1 | « Read SCANID-HANDOVER.md to see your restrictions and permissions! CRUCIAL execute the instructions from attached pdf file of this prompt! CRUCIAL after implementing each stage update SCANID-HANDOVER.md! CRUCIAL if executing current instruction violates any restriction from SCANID-HANDOVER.md respect current instruction! » + Alex's PDF « Lasha-Third-Check-2026-10-02.pdf » | **DONE locally (I0–I5).** Section 4: Alex's eight rows + four more labels under « sentence case everywhere » (« Destination (optionnel) », « Document (image ou PDF) » — as on his site's app mock-ups —, « Rechercher (nom, e-mail...) », the sort tooltip); « Mon compte » in the two purchase e-mails; README. Sections 3.2 / 3.3 proven again (six templates rendered; real CSV / XLSX headers == the table's). Sections 2, 3.1 and 5: server-only — runbook §I.5 (= §H.5's, unchanged), answers for Alex in §I.5. Verified: backend 366, unit 89, e2e 448 / 1 skipped, build + guard 5/5, bundle `index-CJFY_9p8.js`, screenshots desktop + 375 px | **The user:** ship (§I.5 steps 1–5: commit + push, workflows, the nginx reload, laptop checks); server steps B (`trial`), A (the list for Alex); forward §I.5's answers to Alex. Nothing committed (§0.3) |
| 2 | « What you don't made from the prompts of the pdf file? Short answer! » | **DONE.** Answered: not done = section 2 (`trial` → true: SMTP password on the server), section 3.1 (the account list: VPS journal + database, `sudo`), section 5 (the nginx reload, `sudo`) — all server-side, runbook §I.5; section 4 is done but not live until the user commits and pushes | — |
| 3 | « Explain about "Section 2, trial → true" is it about payment or what? Answer only current question! » | **DONE.** Answered: not payment (that is `signup`, Stripe) — `trial` = the free-trial request flow of essai.html (20 documents offerts), computed as `mailer.is_configured()`; false today → the form falls back to Formspree and Alex opens accounts by hand; needs the SMTP lines in the server `.env` (§I.5 B) | — |
| 4 | « Let's we will do it! Give me the instructions one at a time! » (and the questions asked during it, below) | **B steps 1–8 DONE — `trial` ON (≈ 15:45 UTC); guided one command per message.** Repository re-checked first (`config.py` names and defaults, `mail_backend()`, `.env.example`'s empty SMTP lines, « Deploy »'s `rsync --delete` on `backend/`) → §I.5 B refined (look with values hidden, backup outside `backend/`, diff before the restart). Steps 1–2 done (logged in 15:11 UTC; `.env` has no mail line); step 3 given — the user asked whether the copy is mandatory: no, but recommended (the `.env` has no other copy: not in Git, not in the nightly backup); then « on my machine? » — no: on the server, `~` = `/home/lasha` there, same owner and mode as the original (`cp -a`); the secrets never leave the server; step 3 done (`deploy:deploy` 600, 2745 bytes); step 4 given. During step 4 the user asked whether « YOUR_PASSWORD » means the `.env`'s `ADMIN_PASSWORD` — **no**: it is the contact@scanid.fr mailbox password. Their screenshot showed the `ADMIN_PASSWORD` line in the chat (value not recorded here) → advised to change the app's « admin » password in « Mon compte » (`main.py` lifespan uses `ADMIN_PASSWORD` only to create « admin » when it does not exist, so the app's stored password is what counts). Then « when Alex changes the contact@ password, will the .env conflict? » — answered: yes, the server's copy goes stale and the e-mails fail silently → rule + check + the separate-mailbox option, recorded under §I.5 B. « Each time I should change it manually? » — yes, with this setup (one line + restart); rare in practice (only when the password is changed); the separate app mailbox removes the manual step (offered, not decided). **Order agreed with the user: finish B now with contact@scanid.fr; the separate app mailbox afterwards** (needs Alex: the IONOS mailbox + the sender address customers see; then the code change, tests, deploy; the switch = the same `.env` lines). **The SSH terminal froze during step 4** → out: Ctrl+Q (XOFF), else Enter `~.`, else close the tab; reconnect. Next, before redoing step 4: was the `.env` saved (diff with the backup)? Any `/opt/travelapp/backend/.env.save` (nano's emergency save on hang-up — may hold the password; delete it — « Deploy »'s `rsync --delete` would also remove it) or a stale `nano` (`pgrep -a nano`)? The user then pasted the three template lines with the literal placeholder `SMTP_PASSWORD='YOUR_PASSWORD'` (no secret) → told: replace it in the file with the real mailbox password, keep the quotes; state check given (password hidden; `grep -c YOUR_PASSWORD`; `.env*` files; `pgrep -a nano`). Result: **the edit was not saved** (no mail line, `.env` still 2745 bytes Sep 8); a stale `nano` (pid 262968, root) still runs with its lock file `..env.swp` (root 644, 1024 bytes — lock metadata, no buffer). Given: `sudo kill -9 262968` (SIGKILL: no emergency `.env.save`, which nano writes on SIGHUP / SIGTERM with a modified buffer — possibly world-readable) + `rm` the lock. Next step 4 without an editor: append the three lines with the password read at a hidden prompt (`read -rsp`, never on the command line → not in the shell history) through `sudo tee -a` (owner and mode kept). Cleanup result: « kill: (262968): No such process » — nano had already exited; the folder holds only `.env` (2745, Sep 8) and `.env.example` — no lock, no `.env.save`. New step 4 given (hidden prompt + `tee -a`) → « appended ». Step 5 given (diff with the password hidden, `ls -l`, and `sudo find / -xdev -name '*.save' -mmin -240` for an emergency copy left by the nano that exited on its own) → `7a8,11` (only the four added lines), `deploy:deploy` 600, no `*.save`. Step 6 given (the SMTP login test before the restart) → « SMTP login OK ». Step 7 given: `sudo systemctl restart travelapp.service; sleep 5; systemctl is-active travelapp.service; curl -s http://127.0.0.1:8001/config` → `active`, `{"signup":false,"trial":true}`; step 8 by the assistant (public): the same, `/app/` and `/essai.html` 200. **`trial` is ON (≈ 15:45 UTC).** §I.5 answer 1 for Alex updated. Step 9 offered (a test request). « How Alex can test it? » → his six steps given for forwarding (essai.html with a test address ≠ contact@ → notification at contact@ → « Demandes d'essai » → Valider → welcome e-mail + password link → « Crédits : 20 » → delete the test account; « Refuser » = no e-mail); reminder: Alex needs the admin password — give him the new one after the change | B step 9 (the trial test) and step 10 (delete `~/env-before-smtp`); the admin password change — §I.0.1 items 1–3 |
| 5 | « Now update the SCANID-HANDOVER.md in such way that with the fresh session you could resume continue what we are doing seamlessly! » | **DONE.** The resume protocol (top) points to the new §I.0.1 « RESUME HERE » (where things stand, the ordered open items with their commands, how to guide, the server facts learned); §I.0's state line; Alex's trial test added to §I.5; « Last updated »; the memory note `scanid-task-i-third-check` | — |
| 6 | « Mark in SCANID-HANDOVER.md all what we have not done from this session! » | **DONE.** §I.0.1 « ❌ NOT DONE » table: 11 items, each with its source (PDF section or prompt), who / why, and its item in the ordered list | — |
| 7 | « Mark in SCANID-HANDOVER.md all prompts what we have not done from attached pdf of this seesion! » | **DONE.** §I.0.1 « 📄 Alex's PDF » table: every PDF item with ✅ / ⚠️ / ❌ — ❌ 3.1 (the list) and 5 a–c (the nginx reload); ⚠️ 4 (done, not pushed) and the answers 2 / 3.2 / 3.3 (not forwarded); ✅ 2 (a) `trial` ON (test pending); pointer added under the PDF summary in §I.1 | — |
| 8 | « what is next step? To implement code changes that make that i do not wiil to change the password each time manually? » | **DONE.** Answered: not next — first §I.0.1 items 1–2 (delete `~/env-before-smtp`; change the admin password), then ship task I (item 5); the separate-mailbox change starts with Alex (mailbox + sender address), then a small code change (`MAIL_REPLY_TO`, design in item 7a) as its own task — not mixed into task I's commit | — |
| 9 | « Alex can not change admin password? » then « he is admin » | **DONE.** Answered: yes — Alex changes it himself in « Mon compte » (best: nothing to pass around); the user tells him why; for the user's own admin access, a separate admin account rather than a shared password. §I.0.1 item 2 and the NOT DONE row 7 updated | — |
| 10 | « Alex should create an another email? what email exactely? » | **DONE.** Answered: optional (only to remove the manual password step); if yes, one mailbox for the app alone — suggested `notifications@scanid.fr` (not noreply@); customers still see « ScanID », replies go to contact@ (the code change); Alex creates it, forwards it to contact@, hands over the password safely; no DNS change. Recorded in §I.0.1 item 7a | — |
| 11 | « Alex creates on ionos another mail with strong password? … which password it is? the password of newly created email? » | **DONE.** Answered: yes — a new address with its own new password; forwarding to contact@ in its IONOS settings; the password handed over = the new mailbox's (it replaces contact@'s on the server); afterwards contact@'s password can change freely | — |
| 12 | « after it we will to made other remainig prompts? » then « and with doing all this all the prompts from pdf will be done? » | **DONE.** Answered: the remaining items do not wait for the mailbox (it depends on Alex) — order = §I.0.1 items 1–7; yes, items 3–6 complete every PDF item (see the « Item below » column of the « 📄 Alex's PDF » table); caveat for 3.1: e-mails and credits come from the database (complete), the creation dates from the logs (may not reach back to go-live, 2026-09-08) | — |
| 13 | « Now if i open a new session and tell you "read SCANID-HANDOVER.md and we resume our work!" it will be ok? » | **DONE.** Answered: yes — the resume protocol leads to §I.0.1; tell the new session what was done since (e.g. « I deleted the backup ») | — |

### I.0.0b RESUMED SESSION (2026-10-03, later) — EVERY PROMPT, WHAT IS DONE, WHAT IS LEFT

| # | Prompt (verbatim, or in substance) | Done | Left |
| --- | --- | --- | --- |
| 1 | « Read SCANID-HANDOVER.md and resume our work exactly where it stopped: start at the first unticked item of §I.0.1 « RESUME HERE », under the same restrictions and permissions recorded there. Guide me one command at a time and update SCANID-HANDOVER.md after each step. » | **Resume check DONE:** `git status --short` = §I.0 exactly (13 ` M` + 1 `??`, `git add --dry-run .` = 14), `HEAD` = `origin/master` = `c027cfa`; backend **366 passed**, unit **89 passed**; live `/api/config` → `{"signup":false,"trial":true}`. Verified in the code before quoting it: `password_policy.py` (12 / 1 uppercase / 2 digits / 2 specials + a zxcvbn strength score ≥ 3), « Nouveau mot de passe (optionnel) » and « Enregistrer les modifications » in « Mon compte » (the live bundle still says « Mon Compte » until task I ships). **Item 2 given:** it is Alex's action (no command) → a short message for the user to send Alex now (security — not held back for item 4's long forward) | Items 2–7 of §I.0.1 |
| 2 | « He will change the admin password tell me what 's next? » | **Item 2:** Alex informed, not confirmed → left unticked (tick on his confirmation). **Item 3:** Alex's (needs the admin login) → rides on item 4. **Item 4 given:** the full message for Alex (texts re-verified in the code first: `emails.py` subjects « Demande d'essai — … » / « Votre espace ScanID est ouvert — 20 documents offerts », `TRIAL_CREDITS` 20, the 48 h link, essai.js « Dès sa validation, vous recevez à … », the App.jsx tabs and buttons) | « sent » → item 5 (ship), one command per message |
| 3 | « we will forget the tasks that requires Alex's engagemment and we will continue to resolve tha task that we can do without Alex! » | **Recorded:** items 2, 3, 4, 7 ⏸ PARKED in §I.0.1 (and the resume protocol skips them). **Item 5 started:** pre-commit check (14 paths, nothing staged, no secret in the diff); step 1a given — `git add . && git status --short` | Item 5 (commit → push → « CI » / « Deploy » → nginx reload + `verify-front-end.sh` → laptop checks → SHIPPED), item 6 (the list, read-only), « Also open » |
| 4 | « there is something outside of .gitignore that must be in? » | **Checked — no, both ways.** `git add .` stages exactly the 14 paths (the only `??` is `labels.spec.js`). Ignored and rightly so: `backend/.env`, `frontend/.env.local` (secrets); the root's `DUBROVNIK.pdf` and « ITALIE 2 PIECES IDENTITE - copie.pdf » (real identity documents); `backend/bench_*` (local OCR benchmarks); `newvenv/`, caches, `frontend/dist/` (built by CI), `test-results/`, `tests/.browser-libs/`, `tests/fixtures/files/` (regenerated by `npm run test:fixtures`); `site.html`, `site1.html`. Nothing ignored is needed: `labels.spec.js` imports only `test-base.js` and `helpers/index.js` (tracked); « CI » runs the build + unit tests only. Tracked env-like file: only `backend/.env.example` (empty values) | Step 1a still to run |
| 5 | « provide a short commit message » | **Step 1a confirmed DONE** (the user had run `git add .`: 14 staged, nothing unstaged). **Step 1b given:** `git add . && git commit -m "App: sentence-case labels and « Mes documents » tab"` — one line, the « App: … » style of `c027cfa`, no trailer (the user's commits carry none) | Paste the commit's output → the hash in §I.0 « Ship progress » 1, then step 1c `git push origin master` |

### I.0 State in one line (update after every stage)

**✅ SHIPPED — 2026-10-03: nginx reloaded by the user (≈ 18:12 UTC; `nginx -t` ok, `verify-front-end.sh` → ALL CHECKS
PASSED) and the laptop checks all green (register 404; `www` → 301 `https://scanid.fr/tarifs.html`; `site.css` gzip +
`max-age=31536000` + `Vary: Accept-Encoding`; `tarifs.html` `no-cache`; `/temoignages.html` → 301 `/presentation.html`;
`/iftm/` → 301 `/essai.html`; bundle `index-CJFY_9p8.js` gzip, the 9 task-I labels, 0 old ones; `/api/config`
`{"signup":false,"trial":true}`) — §J.4. The unticked nginx boxes below are history.**

**I0–I5 DONE — task I's code is complete locally and verified, NOT committed. Server step B DONE up to its step 8:
`trial` is ON since 2026-10-03 ≈ 15:45 UTC. Item 1 done; items 2, 3, 4, 7 ⏸ PARKED (need Alex — the user, resumed
session). NOW: §I.0.1 item 5 — shipping task I, one command per message (then item 6, then « Also open »). Do not
re-implement anything.** Nothing committed yet (§0.3: the user commits).

**Ship progress** (tick as the user reports each §I.5 step; one command per message when guiding):
- [x] 1 committed (hash: **`a769f33`**) and pushed — `git ls-remote origin refs/heads/master` = local `HEAD` (checked)
- [x] 2 « CI » green · « Deploy » green (17:46 UTC) — live bundle `index-CJFY_9p8.js` (checked)
- [x] 3 nginx reloaded on the VPS (2026-10-03 ≈ 18:12 UTC, ALL CHECKS PASSED) · `ops/verify-front-end.sh` → ALL CHECKS PASSED (ticks §F.0 step 4, §G.0 step 3, §H.0
  step 3)
- [x] 4 laptop checks of §I.5 step 4 (all green, §J.4) (= §G.5 step 4 + §F.6 step 5 + task I's bundle check)
- [x] 5 SHIPPED → §F.0, §G.0, §H.0 and §I.0 say SHIPPED (done 2026-10-03) (hashes, date); memory notes updated
- [x] B `trial` **true since 2026-10-03 ≈ 15:45 UTC** (SMTP login OK → restart → `/api/config`) · [ ] Alex's trial run · [ ] A the list sent to Alex ·
  [ ] C `signup` true (later, with Alex) · [ ] §I.5's answers forwarded to Alex
- **B in progress (2026-10-03), §I.5 B steps:** [x] 1 ssh (15:11 UTC; the server shows « System restart required », 29 updates — unrelated, left for later) · [x] 2 look — **no `SMTP_` / `MAIL_` line at all** in the server's `.env` (empty output, no error; so no `MAIL_BACKEND` either) → step 4 **adds** the three lines at the end · [x] 3 backup — `~/env-before-smtp` `-rw------- deploy deploy 2745 Sep 8 13:49` (the `.env` is `deploy:deploy` 600, untouched since go-live) · [x] 4 edit — appended with the hidden prompt + `tee -a` (« appended ») · [x] 5 diff — `7a8,11`: only the blank line + the three mail lines added; `.env` still `deploy:deploy` `-rw-------` (2840 bytes, Oct 3 15:42); no `*.save` anywhere ·
  [x] 6 login test — « SMTP login OK » (port 587 + STARTTLS reachable from the VPS) · [x] 7 restart — `active`, `127.0.0.1:8001/config` → `{"signup":false,"trial":true}` · [x] 8 `/api/config` — from the laptop: `{"signup":false,"trial":true}`; `/app/` and `/essai.html` 200 · [ ] 9 test request · [x] 10 backup removed (16:32 UTC)

**Expected `git status --short` now (nothing staged) — 13 modified, 1 untracked:** ` M` `README.md`,
`SCANID-HANDOVER.md`, `backend/emails.py`, `backend/tests/test_email_wording.py`, `frontend/src/App.jsx`,
`frontend/tests/e2e/{a11y,account,capture,design-system,features,fonts,privacy}.spec.js`, `frontend/tests/mock/api.js`;
`??` `frontend/tests/e2e/labels.spec.js` — `git add --dry-run .` = **14 paths**. Any other difference: report it, do not
« fix » it.
**Quick baseline for a resumed session:** `cd /home/lasha/Public/new/backend && /home/lasha/Public/new/newvenv/bin/python -m pytest -q`
→ **366 passed**; `cd /home/lasha/Public/new/frontend && npm run test:unit` → **89 passed**; `./node_modules/.bin/eslint
src/App.jsx` → **11 problems**; full e2e **448 passed, 1 skipped** (end of I4). Git at the start of task I: `master` =
`origin/master` = `c027cfa`, tree clean; baselines then: backend 365, unit 89, eslint 11.

### I.1 The demand, verbatim (user, 2026-10-03)

> Read SCANID-HANDOVER.md to see your restrictions and permissions!
> CRUCIAL execute the instructions from attached pdf file of this prompt!
> CRUCIAL after implementing each stage update SCANID-HANDOVER.md!
> CRUCIAL if executing current instruction violates any restriction from SCANID-HANDOVER.md respect current instruction!

The PDF was attached to the message (it is **not** in the repository): « Lasha-Third-Check-2026-10-02.pdf », Alex's note,
1 page, headed « SCANID · FOR LASHA = FOR YOU – Claude Code! », « After go-live — third check: what remains », checked
live on 02/10/2026 at 22:10 Paris time « after your deployment of 21:26 » (= `c027cfa`, committed 23:26 +04:00), « by
Claude for Alex », no account used. « What remains: one switch, three answers and a few labels inside the app. Section 5
is optional, as before. » In substance:
1. **Confirmed — nothing to do.** Fixed: « Aucun e-mail ne sera envoyé. » and the link to `scanid.fr/tarifs.html`. Still in
   place: login form only on `/app/`, `/api/users/register` → 404, the 63 website files byte-identical, no console
   error, no CSP violation. Forms and payments: three test messages (22:06) went through; the four Stripe links are right.
2. **One switch — trial.** « **trial → true, please.** `GET /api/config` still returns `{"signup": false, "trial":
   false}`. Requested in the two previous notes; if you are keeping it false for a reason, tell Alex. » « **signup stays
   false for now: correct.** It waits for the Stripe webhook, which Alex creates first, and for one test purchase. »
3. **Three answers for Alex.** (1) Accounts created through the old « Créer un compte » form: the list (date, e-mail,
   credits), or « none ». (2) E-mail templates (welcome, trial, purchase, reset): « documents » and « e-mail »
   everywhere? (3) Export file (XLSX, CSV): headers in sentence case, as in the table? « Before your deployments they
   were still « Date de Naissance », « Date d'Expiration », « Score de Confiance ». »
4. **Labels inside the app — new in this note.** « Read in the JavaScript bundle, not on screen. Sentence case
   everywhere, and one tab to rename: »
   | Where | Now | Change to |
   | --- | --- | --- |
   | Dashboard, tab | « Mon Compte » | « Mon compte » |
   | Account screen, title | « Modifier Mon Compte » | « Modifier mon compte » |
   | Admin, users screen, title | « Gérer les Utilisateurs » | « Gérer les utilisateurs » |
   | Filters | « Filtrer par Utilisateur / Destination » | « Filtrer par utilisateur / destination » |
   | Selection, button | « Modifier Destination » | « Modifier la destination » |
   | Export card, title | « Exportation des Données » | « Exportation des données » |
   | Selection, export buttons | « Exporter Sélection Excel / CSV (n) » | « Exporter la sélection en Excel / CSV (n) » |
   | Dashboard, first tab | « Passeports » | « Mes documents », like the screen it opens |
5. **Optional — server (unchanged).** Compression: CSS and JS still uncompressed (with gzip: home page 162 KB → 40 KB, app
   304 KB → 92 KB) — `gzip_types text/css application/javascript application/json image/svg+xml text/xml;`. www:
   `https://www.scanid.fr` still 200 → 301 to `https://scanid.fr`, same path. Old pages: 301 `/temoignages.html` →
   `/presentation.html`, `/iftm/` → `/essai.html`.

**Status of every item above (2026-10-03, evening): the table « 📄 Alex's PDF » in §I.0.1** — ❌ not done: 3.1, 5 (a, b, c); ⚠️ done but not live / not delivered: 4 (not pushed), the answers to 2, 3.2, 3.3 (not forwarded); ✅ 2 (a) `trial` ON (its end-to-end test still to do).

Constraints and permissions: §0. The user's rule (as for §F–§H): a demand of the PDF wins over a restriction of this file.

### I.2 Findings before touching anything

1. **Git:** `master` = `origin/master` = **`c027cfa`** (task H, committed 2026-10-02 23:26 +04:00 = 21:26 Paris — Alex's
   « deployment of 21:26 », exactly the 7 paths of §H.0); tree clean. Baselines: backend **365**, unit **89**, eslint
   `App.jsx` **11**.
2. **Live (public requests, 2026-10-03):** task H is live — bundle **`index-DvNksTlx.js`** (= H4's build); `POST
   /api/users/register` → 404. `/api/config` → `{"signup":false,"trial":false}`. **nginx is still NOT reloaded:**
   `site.css` → 113 379 bytes, no `Content-Encoding` with `Accept-Encoding: gzip`; `https://www.scanid.fr/tarifs.html`
   → 200; `/temoignages.html` and `/iftm/` → 404. ⇒ Alex's section 5 is still exactly the pending reload (§H.5 step 3):
   no code.
3. **Section 4 — every row is in `frontend/src/App.jsx`** (and once each in the live bundle): tab « Mon Compte » (1043);
   `<h2>Modifier Mon Compte</h2>` (`AccountEditor`, 1217); `CrudManager title="Gérer les Utilisateurs"` (1146);
   « Filtrer par Utilisateur / Destination » = **three** placeholders — admin `'Filtrer par Utilisateur'` (995), client
   `'Filtrer par Destination'` (998), the admin's extra destination filter `"Filtrer par Destination"` (2111); « Modifier
   Destination » (2078); `<h3>Exportation des Données</h3>` (2086); `` `Exporter Sélection Excel (${n})` `` and
   `` `Exporter Sélection CSV (${n})` `` (2098, 2101); tab « Passeports » (1036) — it opens `PassportsPage`, whose
   `CrudManager` title is already « Mes documents » (1056).
4. **« Sentence case everywhere » — survey of every visible string of `src/`** (Babel AST over all 10 source files: JSX
   text, attributes, string and template literals — 967 strings; script `i0/ast_survey.cjs` in the scratchpad): the only
   title-case labels are Alex's rows, plus **four** capitals after a parenthesis or a slash, which his rule also covers:
   « Destination (Optionnel) » (1430) and « Document (Image ou PDF) » (1435) — the « Ajouter un document » card; **Alex's
   own site shows that card as « Destination (optionnel) » and « Document (image ou PDF) »** (the app mock-ups on
   `presentation.html` and `guide.html`, which also show the tabs « Mes documents », « Mon compte » and « Exportation des
   données », « Filtrer par destination »); « Rechercher (Nom, E-mail...) » (2110, admin users search placeholder);
   `title="Activer/Désactiver le tri sur cette colonne"` (2138, the column-header tooltip). Not title case: « ScanID —
   Tous droits réservés. », the example « Ex : Groupe Lisbonne — octobre 2026 » (a name), « Wi-Fi », developer strings.
5. **The e-mails name the tab:** `emails.py` `purchase_confirmation` (109) and `unit_purchase_confirmation` (127) « Le
   détail de vos achats est dans « Mon Compte » → « Mes achats ». » — they send the customer to the tab, so they follow
   it (« Mon compte »). No test pins that line. No other template quotes a label that changes.
6. **Tests pinning the old labels:** e2e `a11y` (1), `account` (2 + titles), `design-system` (2 tab lists), `features`
   (« Modifier Destination » ×2, « Exporter Sélection … (1) » ×3, « Mon Compte » ×2, « Modifier Mon Compte », « Passeports »),
   `fonts` (1 tab list), `privacy` (2); `capture.spec.js` has a comment « l'onglet Passeports ». The nav-button locators
   use `filter({ hasText })` — **case-insensitive substring** — so some would pass unchanged: the new checks must pin the
   case exactly (`exact: true`, `toHaveText`). Backend: nothing pins the e-mail line.
7. **Section 2 — `trial`:** unchanged since §H.2.3 — derived, not stored: `trial = mailer.is_configured()` = SMTP set in
   the server's `.env`, which has no SMTP lines yet. It cannot be set from the repository and must not be forced (no
   notification to contact@, no welcome e-mail, no password link). It needs the IONOS mailbox password of
   contact@scanid.fr typed on the server — never in a chat or in the repository.
8. **Section 3:** (1) the list needs the production journal and database on the VPS (`sudo`) — §H.5 A unchanged; « how
   many credits »: 5. (2) Answered in §H.3 from the six rendered templates — re-rendered after I2's « Mon compte ». (3)
   `EXPORT_HEADERS` == the table's headers since `109993f` (18:44), proven on real CSV / XLSX in §H.3 — re-proven on the
   current code in I3. Alex's « Date de Naissance » export predates 18:44.
9. **Not in the note, seen:** the XLSX export's sheet is named « Passeports » (`main.py` 616, pinned by `test_export.py`) —
   a file detail, not the dashboard tab Alex names.

### I.3 Decisions

1. **Section 4 — Alex's eight rows as written** (the three filter placeholders; both export buttons: « Exporter la
   sélection en Excel (n) », « Exporter la sélection en CSV (n) »).
2. **« Sentence case everywhere » — the same rule on the four other visible labels of I.2.4:** « Destination
   (optionnel) », « Document (image ou PDF) » (= Alex's site), « Rechercher (nom, e-mail...) », « Activer/désactiver le
   tri sur cette colonne ». Reported to Alex as additions under his rule (one line each to undo).
3. **E-mails:** « Mon Compte » → « Mon compte » in the two purchase confirmations. Test: `test_email_wording.py` — they
   name the tab as the app writes it, and no template writes « Mon Compte ».
4. **Tests:** every pinned old label → the new one; Alex's rows and the four additions pinned **case-sensitively**
   (new e2e checks, plus a negative check: none of the old labels left on the screens). Comments and test titles that
   quote a renamed label follow in the files touched, and the `App.jsx` comment above `BILLING_FIELDS`; backend
   docstrings (developer text) unchanged.
5. **Not changed (not in the note):** the XLSX sheet name « Passeports »; the server messages that still write « email »
   (§H.5 answer 6); « Crédits pages »; the straight apostrophe. Reported.
6. **Sections 2, 3.1 and 5 are server-only** — a runbook (§I.5); no VPS connection from here: each needs the user's
   `sudo` password or the mailbox password, and neither goes through a chat. Answers for Alex in §I.5.

### I.4 Stages

| Stage | Content | Status |
| --- | --- | --- |
| I0 | Survey: PDF, git, live state, every label (source, bundle, AST survey, Alex's site mock-ups), e-mails, tests; baselines (backend 365, unit 89, eslint 11) | **DONE** |
| I1 | Demand, findings, decisions, plan here | **DONE** |
| I2 | Section 4: the labels (`App.jsx`), « Mon compte » in the two purchase e-mails, the tests (e2e + backend) | **DONE** |
| I3 | Section 3: export headers re-proven on a real CSV / XLSX; the six e-mail templates re-rendered and read | **DONE** |
| I4 | Verification: backend, unit, eslint, build + guard + bundle strings, e2e (touched specs, then full), screenshots desktop + 375 px | **DONE** |
| I5 | Record + how to ship + the server runbook (nginx reload = section 5; `trial` = SMTP; the list = 3.1) + answers for Alex | **DONE** (§I.5) |

### Stage I2 — section 4: the labels — DONE

- `frontend/src/App.jsx` (16 lines, one string each): Alex's rows — tabs « Mes documents » (was « Passeports ») and « Mon
  compte »; `<h2>Modifier mon compte</h2>`; `CrudManager title="Gérer les utilisateurs"`; placeholders « Filtrer par
  utilisateur », « Filtrer par destination » (client filter **and** the admin's extra one); « Modifier la destination »;
  `<h3>Exportation des données</h3>`; `` `Exporter la sélection en Excel (${n})` ``, `` `Exporter la sélection en CSV
  (${n})` ``. Under « sentence case everywhere » (I.3.2): « Destination (optionnel) », « Document (image ou PDF) »,
  « Rechercher (nom, e-mail...) », `title="Activer/désactiver le tri sur cette colonne"`. The comment above
  `BILLING_FIELDS` follows (« Mon compte »). The AST survey re-run on `src/`: **0** title-case labels left.
- `backend/emails.py`: « Le détail de vos achats est dans « Mon compte » → « Mes achats ». » in `purchase_confirmation` and
  `unit_purchase_confirmation`.
- **Tests written first, run against the old code — red for the right reasons:** `test_email_wording.py`
  `test_the_purchase_e_mails_name_the_tab_as_the_app_writes_it` (the exact line in both purchase e-mails; no template
  writes « Mon Compte ») → **1 failed / 7 passed**. New `frontend/tests/e2e/labels.spec.js` (2 tests, case-sensitive on
  purpose: `toHaveText`, `exact: true`, attributes; the export pair compared on `textContent` — the accessible name also
  carries the CSS « ⬇ »): client — tabs exactly [« Mes documents », « Mon compte »], the first active, heading « Mes
  documents », the upload card's two labels, « Exportation des données », the destination filter, the sort tooltip, a
  selection → « Modifier la destination » + « Exporter la sélection en Excel (1) » / « … en CSV (1) », **no horizontal
  overflow** (the longer labels wrap on a phone), « Mon compte » → « Modifier mon compte »; admin — tabs [« Mes
  documents », « Administration », « Demandes d'essai », « Mon compte »], « Filtrer par utilisateur » / « Filtrer par
  destination », « Administration » → « Gérer les utilisateurs », « Rechercher (nom, e-mail...) »; on every screen the
  markup holds none of the 12 old labels. Old code: both red at the tabs (« Passeports », « Mon Compte »); a temporary
  soft-assertion copy (deleted after the run) showed **every** other check red with the old value, and the markup check
  listing the old labels.
- `frontend/tests/mock/api.js`: `GET /admin/users` (mirrors `main.py` `read_users`, admin only) — the UI calls it when
  the admin opens « Administration », and the mock answered 501 until now (no test had opened that screen).
- Existing specs, old label → new: `a11y` (1), `account` (2 + its header comment and `describe`), `design-system` (2 tab
  lists), `features` (« Modifier la destination » ×2, the export pair ×3, « Mon compte » ×2 + a test title, « Modifier
  mon compte », « Mes documents »), `fonts` (1 tab list), `privacy` (2), `capture` (a comment). Left on purpose:
  `tests/mock/xlsx.js` sheet name « Passeports » (= the backend's, I.3.5).
- Results: e-mail wording **8 passed**; `labels.spec.js` desktop + mobile-small + mobile-375 **6 passed**; the 8 touched
  specs × 3 projects **242 passed, 1 skipped** (2.1 min); backend **366 passed** (365 + 1); eslint `App.jsx` **11** (=
  `HEAD`), the 9 touched test files clean.

### Stage I3 — section 3: the export headers and the e-mail templates, proven again — DONE

No code. Evidence from a throw-away pytest file in the session scratchpad (`i3/test_i3_evidence.py`, run from `backend/`
with `I3_OUT=<scratchpad>/i3 APP_PUBLIC_URL=https://scanid.fr/app/ …/python -m pytest -p tests.conftest <file> -s -q -p
no:cacheprovider --rootdir=/home/lasha/Public/new/backend` — the repository's fixtures; `git status` unchanged afterwards):
- **Export (question 3.3):** the real downloads of `GET /export/data?format=csv` and `?format=xlsx` (fixture
  `user_with_documents`) carry the same header row — « Nom de famille, Prénom, Sexe, Date de naissance, Date
  d'expiration, Nationalité, Numéro de document, Type, Destination, Score de confiance » — which is **exactly the set of
  the table's labels**, read from `App.jsx` `columnTranslations` itself for the export's ten fields; every header in
  sentence case; none of « Date de Naissance », « Date d'Expiration », « Score de Confiance ». CSV with its UTF-8 BOM, 4
  data rows; XLSX sheet « Passeports », 4 data rows; LibreOffice (`soffice --headless --convert-to csv`, profile in the
  scratchpad) reads the XLSX header row identically. Live since `109993f` (2026-10-02 18:44 Paris); Alex's export with
  « Date de Naissance » predates it. Nothing to change.
- **Templates (question 3.2):** all six rendered (« à la carte » in its two forms — `i3/templates.txt`) and read in full:
  password reset « Réinitialisation de votre mot de passe ScanID » (« ignorez simplement cet e-mail »); trial
  notification « Demande d'essai — {société} » (« (20 documents offerts) », « E-mail : »); trial welcome « Votre espace
  ScanID est ouvert — 20 documents offerts »; pack purchase « Vos 1 000 documents ScanID sont disponibles »; à la carte
  « Vos 37 documents ScanID sont disponibles » / « Votre document ScanID est disponible »; payment anomaly « Paiement
  Stripe à rattacher manuellement » (« E-mail du client »). **0** « scan(s) » noun, **0** « email »; the three purchase
  renderings say « Le détail de vos achats est dans « Mon compte » → « Mes achats ». » (I2). The only « scan » forms are
  verbs: « Photographiez ou scannez vos documents » (welcome, step 1) and the signature « Scanner · Vérifier ·
  Sécuriser ».

### Stage I4 — verification — DONE

| Check | Result |
| --- | --- |
| `cd backend && …/newvenv/bin/python -m pytest -q` | **366 passed** (365 + the e-mail tab test) |
| `cd frontend && npm run test:unit` | **89 passed** |
| eslint | `App.jsx` **11** (= `HEAD`); `labels.spec.js`, the 7 touched specs and `tests/mock/api.js` clean |
| Full e2e, all projects (`./node_modules/.bin/playwright test`) | **448 passed, 1 skipped** (4.0 min, exit 0) = 442 + `labels.spec.js` (2 tests × desktop, mobile-small, mobile-375) |
| `VITE_API_URL=/api npm run build` + guard | 64 files, 0 pages rewritten; guard **5/5**; `dist/` root == the folder's 63 files byte for byte + `sw.js`; bundle **`index-CJFY_9p8.js`**: every new label present (`"Mes documents"` ×2 = tab + screen title, `"Mon compte"` ×1, « Filtrer par destination » ×2, the 11 others ×1); **0** × `"Passeports"`, « Mon Compte », « Gérer les Utilisateurs », « Filtrer par Utilisateur », « Filtrer par Destination », « Modifier Destination », « Exportation des Données », « Exporter Sélection », « (Optionnel) », « (Image ou PDF) », « Rechercher (Nom », « Activer/Désactiver », `localhost`; 1 × `"/api"` |
| Screenshots (throw-away specs, copied into `tests/e2e` for one run and deleted; desktop 1280 + mobile-375 WebKit; looked at) | tabs « Mes documents » (active) / « Mon compte »; upload card « Destination (optionnel) », « Document (image ou PDF) »; title row « Mes documents » + « Modifier la destination », « Supprimer (1) », « + Manuel » (wrapping on the phone); « Exportation des données » + « Exporter la sélection en Excel (1) » / « … CSV (1) »; « Modifier mon compte »; admin « Filtrer par utilisateur », « Filtrer par destination », « Gérer les utilisateurs » + « Rechercher (nom, e-mail...) ». **On a 375 px phone the two selection export buttons wrap to three lines each**, side by side (`flex: 1` each, `scanid-app.css`) — no horizontal scroll (asserted in `labels.spec.js`); a consequence of the longer text, not changed (told to Alex). NB a full-page or element capture after a scroll shows the sticky top bar over the content — a capture artifact (the last capture made it static) |
| Found and fixed during I4 | `README.md` item 2 sent admins to « Gérer les Utilisateurs » → « Gérer les utilisateurs » — the only living document quoting a changed label (`.github/`, `ops/`, `deploy/`, `frontend/tests/README.md`: none; `HANDOVER.md` / `PROGRESS.md` are historical records, unchanged) |
| After | ports 5173 / 4173 / 8001 free; `dist/` = the production build above; no `zz-*` spec left; `git status --short` == §I.0 (13 M + 1 ??), nothing staged; `git add --dry-run .` = **14 paths** |

### I.5 How to ship task I — the nginx reload, the server steps, the answers for Alex (stage I5)

**What ships** (nothing committed, §0.3): the 14 entries of §I.0 — `git add --dry-run .` = **14 paths** (checked). No new
dependency, no migration, no `.env` change, **no vhost change** (the server's vhost is still G's, synced at 18:44 on
2026-10-02).

**The user ships it — one command per message when guided:**
1. **Laptop:** `git status --short` (= §I.0) → `git add --dry-run . | wc -l` (14) → `git add .` →
   `git commit -m "App: sentence-case labels, « Mes documents » tab, « Mon compte » in the purchase e-mails"`
   (**used instead, 2026-10-03 — the user asked for a short one: `App: sentence-case labels and « Mes documents » tab`**)
   → `git push origin master`.
2. **GitHub:** « CI » green, « Deploy » green (« NOTE: nginx not reloaded … » is expected — deploy account). The deploy
   restarts the backend (the two purchase e-mails) and ships the bundle `index-CJFY_9p8.js`.
3. **VPS — reload nginx** (unchanged since §H.5 step 3; independent of 1–2, may come first): `ssh lasha@87.106.22.235` →
   `sudo nginx -t && sudo systemctl reload nginx` → `bash /opt/travelapp/ops/verify-front-end.sh` → « ALL CHECKS
   PASSED ». This one reload activates task F (cache headers, `/temoignages.html` and `/iftm/` 301s) and task G (gzip,
   `www` → 301) = **all of Alex's section 5**. `nginx -t` is the safety gate: if it fails, nothing is reloaded and the
   site keeps running.
4. **Laptop checks** (public requests — the assistant may run them): the list of §G.5 step 4 (register 404; `www` → 301
   `https://scanid.fr/tarifs.html`; `site.css` → `content-encoding: gzip`, `max-age=31536000`, `Vary: Accept-Encoding`;
   `tarifs.html` → `no-cache`; the two 301s; `/api/config`), plus task I's (the bundle is minified: a label reads
   `children:"Mon compte"`; both lines tested on 2026-10-03 — the new build gives all 9 / 0, today's live bundle 1 / 13):
   ```bash
   B=$(curl -s https://scanid.fr/app/ | grep -o '/app/assets/index-[^"]*\.js'); echo "$B"     # /app/assets/index-CJFY_9p8.js
   curl -s "https://scanid.fr$B" | grep -o -e '"Mes documents"' -e '"Mon compte"' -e 'Modifier mon compte' -e 'Gérer les utilisateurs' -e 'Filtrer par utilisateur' -e 'Filtrer par destination' -e 'Modifier la destination' -e 'Exportation des données' -e 'Exporter la sélection en' | sort | uniq -c   # all 9, ×1 or ×2 (as I4)
   curl -s "https://scanid.fr$B" | grep -o -e '"Passeports"' -e 'Mon Compte' -e 'Gérer les Utilisateurs' -e 'Filtrer par Utilisateur' -e 'Filtrer par Destination' -e 'Modifier Destination' -e 'Exportation des Données' -e 'Exporter Sélection' -e '(Optionnel)' -e '(Image ou PDF)' | wc -l   # 0
   ```
5. Mark §F.0, §G.0, §H.0 and §I.0 **SHIPPED** (hashes, date); update the memory notes.

**Server steps — the user's (outside the repository; a secret never goes through a chat):** unchanged since §H.5 —
- **B. `trial` → true (PDF section 2)** — §H.5 B, refined 2026-10-03 (row 4 of §I.0.0); one command per message:
  1. `ssh lasha@87.106.22.235`
  2. look, the password hidden (the other values are not secret, and `MAIL_BACKEND`'s must be seen): `sudo grep -nE '^\s*#?\s*(SMTP_|MAIL_)' /opt/travelapp/backend/.env | sed -E 's/(SMTP_PASSWORD=).+/\1<hidden>/'` —
     `.env.example` ships `SMTP_HOST=`, `SMTP_USERNAME=`, `SMTP_PASSWORD=` **empty**: if present, fill those lines (a
     later duplicate would win anyway — python-dotenv keeps the last); a `MAIL_BACKEND=disabled` line would keep `trial`
     false (`config.mail_backend()`: an explicit value wins) — remove it if there is one.
  3. backup **outside** `backend/` (« Deploy » runs `rsync --delete --exclude '.env'` on it: a copy inside would be
     erased): `sudo cp -a /opt/travelapp/backend/.env ~/env-before-smtp` — not mandatory, but the server's `.env` has **no other
     copy anywhere** (not in Git — « Deploy » excludes it —, and `ops/backup.sh` dumps only the database)
  4. **(as done on 2026-10-03, after a frozen nano session)** no editor — the password read at a hidden prompt, never on
     the command line (not in the shell history), three lines appended (a leading blank line in case the file has no
     final newline), owner and mode kept by `tee -a`: `read -rsp 'Mailbox password: ' P; echo; printf
     "\nSMTP_HOST=smtp.ionos.fr\nSMTP_USERNAME=contact@scanid.fr\nSMTP_PASSWORD='%s'\n" "$P" | sudo tee -a
     /opt/travelapp/backend/.env > /dev/null; unset P; echo appended` (a password holding `'` or `\` needs other quoting —
     python-dotenv decodes `\\` and `\'` inside single quotes). The nano way, for the record:
     `sudo nano /opt/travelapp/backend/.env` → `SMTP_HOST=smtp.ionos.fr`, `SMTP_USERNAME=contact@scanid.fr`,
     `SMTP_PASSWORD='<the mailbox password>'` (single quotes: literal for python-dotenv; needed if it holds `#`, a space or
     `$`). Port 587 + STARTTLS, the sender « ScanID <contact@scanid.fr> », the admin address contact@scanid.fr and
     `APP_PUBLIC_URL` https://scanid.fr/app/ are defaults (`config.py`) — no line needed.
  5. only those lines changed, owner and mode kept (the `.env` is `deploy:deploy` `-rw-------` — the service's user must
     still read it; `sudo nano` keeps both when it overwrites): `sudo diff ~/env-before-smtp /opt/travelapp/backend/.env |
     sed -E 's/(SMTP_PASSWORD=).*/\1<hidden>/'; sudo ls -l /opt/travelapp/backend/.env`
  6. the login test **before** the restart (§H.5 B step 2) → « SMTP login OK »
  7. `sudo systemctl restart travelapp.service` → `systemctl is-active travelapp.service` → `active`
  8. laptop: `curl -s https://scanid.fr/api/config` → `{"signup":false,"trial":true}`
  9. a test request on essai.html (Alex's run, §H.5 B step 4) — notification at contact@, « Demandes d'essai », Valider,
     welcome e-mail, password link, « Crédits : 20 »
  10. `sudo rm ~/env-before-smtp` once everything works (the copy holds the server's secrets).
  **After B — the mailbox password lives in two places.** If Alex changes the contact@scanid.fr password at IONOS, the
  server's copy is stale: every e-mail fails (trial notification, welcome + password link, reset, purchase
  confirmations) and **silently** — `mailer.send` never raises (it logs « Email not sent: kind=… error=
  SMTPAuthenticationError »), the e-mails go out after the HTTP response, and `/api/config` keeps `trial` true (it only
  checks that `SMTP_HOST` is set). Rule: Alex tells the user the same day and hands the new password over safely (not
  e-mail / chat); the user redoes steps 4, 6, 7. Check: `sudo journalctl -u travelapp.service --since today --no-pager |
  grep -i "email not sent"`. Alternative, later and only if wanted: a mailbox for the app alone (e.g. noreply@) — needs
  `MAIL_FROM` set to it (IONOS normally sends only under the authenticated address) and a `Reply-To` contact@ (the
  mailer supports it, no caller sets it yet) — a small code change + test.
- **A. The list for Alex (PDF question 3.1)** — exactly §H.5 A (read-only): how far the journal goes back, the `"POST
  /users/register HTTP/1.1" 200` lines (the dates), the database query (e-mails, credits), nginx's logs only if the
  journal starts after go-live. Nothing is changed — Alex decides.
- **C. `signup` → true** — unchanged (§G.5 C), later, with Alex (« stays false for now: correct »).

**Answers for Alex** (the user forwards them; in English, like his note):
1. **Trial (section 2) — done, `trial` is true since 03/10 (≈ 17:45 Paris).** It was not kept false on purpose: `trial`
   is not a setting anyone toggles — the server turns it on by itself once it can send e-mail, and the outgoing mail
   of contact@scanid.fr (IONOS SMTP) is now configured on the server (login tested before the restart). Your test run
   can start: essai.html → your notification « Demande d'essai — … » at contact@scanid.fr → « Valider » in « Demandes
   d'essai » → the welcome e-mail with the password link → « Crédits : 20 ». **One rule from now on:** the server holds
   its own copy of the contact@scanid.fr password — if you change that password at IONOS, tell Lasha the same day
   (and give him the new one safely, not by e-mail or chat): until the server is updated, every e-mail the app sends
   fails, silently.
2. **Question 3.1 — accounts from the old « Créer un compte » form.** Each one received **5 credits**, usable at once,
   with a freely chosen user name. The list (date, e-mail, credits) — or « none » — can only be read on the server (its
   logs and database): Lasha sends it.
3. **Question 3.2 — e-mail templates.** Yes. All six (password reset, your trial notification, trial welcome, pack
   purchase, « à la carte » purchase, payment anomaly) say « documents » and « e-mail » everywhere — re-checked on the
   rendered texts on 03/10: welcome « Votre espace ScanID est ouvert — 20 documents offerts »; notification « (20
   documents offerts) », « E-mail : »; purchase « Vos 1 000 documents ScanID sont disponibles »; à la carte « Vos 37
   documents… » / « Votre document… »; reset « ignorez simplement cet e-mail »; anomaly « E-mail du client ». The only
   « scan » left is a verb: « Photographiez ou scannez vos documents » (welcome, step 1) and the signature « Scanner ·
   Vérifier · Sécuriser ». New with this deployment: the purchase e-mails write « Mon compte » → « Mes achats », like the
   renamed tab.
4. **Question 3.3 — export headers.** Yes, since the deployment of 02/10 at 18:44: the CSV and XLSX headers are exactly
   the table's — « Nom de famille, Prénom, Sexe, Date de naissance, Date d'expiration, Nationalité, Numéro de document,
   Type, Destination, Score de confiance » (checked on real files; the XLSX also opened in LibreOffice). Your export with
   « Date de Naissance » was made before that deployment.
5. **Section 4 — labels.** All eight rows done as written; « Filtrer par destination » exists twice (the client's filter
   and the admin's), both changed. Under your « sentence case everywhere », four labels the table does not list changed
   too: « Destination (optionnel) » and « Document (image ou PDF) » on the « Ajouter un document » card — exactly as the
   app mock-ups on presentation.html and guide.html write them —, the admin users search « Rechercher (nom,
   e-mail...) », and the sorting tooltip of the column headers « Activer/désactiver le tri sur cette colonne ». A scan of
   every label in the app's source finds no other title case. One visible effect of the longer text: on a 375 px phone,
   the two selection export buttons now wrap to three lines each (side by side, no sideways scrolling). Live at the next
   deployment.
6. **Section 5.** Unchanged: gzip, www → scanid.fr and the two 301s have been in the server configuration since 02/10
   18:44; they take effect with one nginx reload, which Lasha does by hand (the deployment account may not reload nginx).
   Checked on 03/10: not reloaded yet.
7. **Not changed — your call:** the XLSX file's sheet is still named « Passeports » (the export's tab, not the
   dashboard's); the server messages that still write « email » (listed in the previous answers); « Crédits pages » in
   the admin users table.

**Alex's trial test** (to forward with the answers; `trial` live since 03/10 ≈ 17:45 Paris):
1. Open https://scanid.fr/essai.html and send a request with a test company name (e.g. « TEST Alex ») and **an e-mail
   address you can read other than contact@scanid.fr**. The page confirms: « Dès sa validation, vous recevez à … le lien
   pour choisir votre mot de passe, avec vos 20 documents offerts… »
2. Within a minute, contact@scanid.fr receives « Demande d'essai — TEST Alex » with the details.
3. Log in at https://scanid.fr/app/ as admin → tab « Demandes d'essai » → « Valider » on the request.
4. The test address receives « Votre espace ScanID est ouvert — 20 documents offerts », with a link to choose a password
   (valid 48 h).
5. Open the link, choose a password, log in with the test address: the badge shows « Crédits : 20 ».
6. Clean up: as admin → « Administration » → « Gérer les utilisateurs » → delete the test account.
(Also possible: « Refuser » at step 3 — no e-mail is sent then.) An e-mail missing (spam folder first): tell Lasha — the
server's log says why (§I.0.1 item 3).

---

## H. TASK H (2026-10-02, evening) — ALEX'S « SECOND CHECK » LIST — COMMITTED `c027cfa` — ✅ SHIPPED 2026-10-03 (NGINX RELOADED)

### H.0.0 THIS SESSION (2026-10-02, the session after task G's) — EVERY PROMPT, WHAT IS DONE, WHAT IS LEFT

| # | Prompt (verbatim, or in substance) | Done | Left |
| --- | --- | --- | --- |
| 1 | « CRUCIAL Read SCANID-HANDOVER.md to see restrictions and permissions for you! CRUCIAL execute the prompts from pdf file attached to this current prompt! If the prompts violates any restriction from SCANID-HANDOVER.md respect current prompt from attached pdf! After each stage is is implemented you update SCANID-HANOVER.md correspondingly! » + Alex's PDF « Lasha-Second-Check-2026-10-02.pdf » | **DONE locally (H0–H5).** Section 4: « Aucun e-mail ne sera envoyé. »; unknown pack → « scanid.fr/tarifs.html » (page + server message); export headers proven == the table's on real CSV / XLSX (already live since 18:44). Section 3.2 answered from the six rendered templates (yes). Section 3.1: 5 credits; the list needs the VPS. Sections 2 and 5: server-only — runbook §H.5 (SMTP login test, then restart; one nginx reload). Verified: backend 365, unit 89, e2e 442 / 1 skipped, build + guard 5/5 | **The user:** ship (§H.5 steps 1–5: commit + push, workflows, the nginx reload, laptop checks); server steps B (`trial`), A (the list for Alex); forward the answers (§H.5). Nothing committed (§0.3) |
| 2 | « verify if there is outside something that must be in .gitignore! » | **DONE — nothing to add, `.gitignore` unchanged.** `git status --untracked-files=all` = only the 7 modified files; `git add --dry-run .` = 7. Everything else on disk is already ignored: the two identity PDFs (by name), `backend/.env`, `frontend/.env.local`, `newvenv/`, `node_modules/`, `dist/`, `test-results/` (this session's Playwright runs), caches, `bench_*`, `tests/fixtures/files/`, `tests/.browser-libs/`, `site.html` / `site1.html`. Tracked side: no tracked file matches an ignore rule (`git ls-files -ci --exclude-standard` empty); no secret pattern in tracked content (Stripe / Google / AWS / GitHub / Slack keys, private keys); `backend/.env.example` = placeholders only; no tracked file > 500 KB; tracked images = app icons + the site's specimen passport / og images / checklist PDF. The empty `static/` at the root (and `backend/static/`): created by the backend's `/static` mount in the directory it starts from — nothing ever writes there (uploads spool to the system temp dir), and git does not track empty folders. This session's own files (scratchpad, LibreOffice profile) are outside the repository. Aside, not a `.gitignore` matter, not changed: `REGISTER_RATE_LIMIT` (`config.py`, `.env.example`) is unused since the register route was removed | — |
| 3 | « can i use git add .? Provide short git commit message! » | **DONE.** Yes — re-checked just before answering: `git status --short` = the 7 files of §H.0, no untracked file, `git add --dry-run .` = 7 (this file included, with this row). Message given: « App: « e-mail » in the trial refusal confirmation, unknown pack links to tarifs.html » (also §H.5 step 1) | **The user:** `git add .` → commit → `git push origin master`; then §H.5 steps 2–5 |

### H.0 State in one line (update after every stage)

**✅ SHIPPED — 2026-10-03: nginx reloaded by the user (≈ 18:12 UTC; `nginx -t` ok, `verify-front-end.sh` → ALL CHECKS
PASSED) and the laptop checks all green (register 404; `www` → 301 `https://scanid.fr/tarifs.html`; `site.css` gzip +
`max-age=31536000` + `Vary: Accept-Encoding`; `tarifs.html` `no-cache`; `/temoignages.html` → 301 `/presentation.html`;
`/iftm/` → 301 `/essai.html`; bundle `index-CJFY_9p8.js` gzip, the 9 task-I labels, 0 old ones; `/api/config`
`{"signup":false,"trial":true}`) — §J.4. The unticked nginx boxes below are history.**

**H0–H5 DONE; committed `c027cfa` by the user and pushed; « Deploy » ran (21:26 Paris) — live (Alex's third check
confirms both texts). Still open: the nginx reload (step 3) and what follows it, and the server steps B and A — all
carried into §I.5 (task I, Alex's « third check »). Do not re-implement anything.**

**Ship progress** (tick as the user reports each §H.5 step; one command per message when guiding):
- [x] 1 committed **`c027cfa`** (« App: « e-mail » in the trial refusal confirmation, unknown pack links to
  tarifs.html », the 7 paths below) and pushed, 2026-10-02 23:26 +04:00 — `git ls-remote origin refs/heads/master` =
  `c027cfa…` = local `HEAD` (checked at the start of task I)
- [x] 2 « Deploy » ran (21:26 Paris): live bundle `index-DvNksTlx.js` = H4's build; Alex's third check §1 confirms « Aucun
  e-mail ne sera envoyé. » and the `tarifs.html` link. (« CI » run page not visible from here — `gh` not installed.)
- [ ] 3 nginx **NOT reloaded** — checked 2026-10-03: no gzip on CSS, `www` → 200, `/temoignages.html` / `/iftm/` →
  404 → **§I.5**
- [ ] 4 laptop checks of §H.5 step 4 (= §G.5 step 4 + §F.6 step 5 + task H's) — after the reload (§I.5)
- [ ] 5 SHIPPED → §F.0, §G.0 and §H.0 say SHIPPED (hashes, date); memory notes updated
- [ ] B `trial` true (SMTP login OK → restart → `/api/config`) · [ ] Alex's trial run · [ ] A the list sent to Alex ·
  [ ] C `signup` true (later, with Alex) — server steps, continued in §I.5

**Expected `git status --short` at the end of task H (nothing staged) — 7 modified — record:** ` M` `SCANID-HANDOVER.md`, `backend/main.py`,
`backend/tests/test_pack_purchase.py`, `frontend/src/App.jsx`, `frontend/tests/e2e/{signup,trials}.spec.js`,
`frontend/tests/mock/api.js`. Any other difference: report it, do not « fix » it.
**Quick baseline for a resumed session:** `cd /home/lasha/Public/new/backend && /home/lasha/Public/new/newvenv/bin/python -m pytest -q`
→ **365 passed**; `cd /home/lasha/Public/new/frontend && npm run test:unit` → **89 passed** (both reproduced at the start of
task H, = §G.0). Git at the start of task H: `master` = `origin/master` = `109993f`, tree clean.

### H.1 The demand, verbatim (user, 2026-10-02)

> CRUCIAL Read SCANID-HANDOVER.md to see restrictions and permissions for you!
> CRUCIAL execute the prompts from pdf file attached to this current prompt!
> If the prompts violates any restriction from SCANID-HANDOVER.md respect current prompt from attached pdf!
> After each stage is is implemented you update SCANID-HANOVER.md correspondingly!

The PDF was attached to the message (it is **not** in the repository): « Lasha-Second-Check-2026-10-02.pdf », Alex's
note, 1 page, headed « SCANID · FOR LASHA = for you – Claude Code! », « After go-live — second check: what remains »,
checked live on 02/10/2026 at 20:40 Paris time « after your deployment of 18:44 » (= `109993f`, committed 20:44 +04:00),
no account used, nothing submitted. In substance:
1. **Confirmed — nothing to do.** « Créer un compte » gone, `/api/users/register` → 404; « scans » → « documents » on
   `/app/inscription` and in « Demandes d'essai », field labels included; « Tarifs » → `/tarifs.html`, table headers in
   sentence case; the 63 website files still byte-identical, no console error, no CSP violation.
2. **One switch — trial.** `GET /api/config` still `{"signup": false, "trial": false}`. **« trial → true, please »** —
   requested « now » in the previous note; Alex's end-to-end trial test works; « If you are keeping it false for a
   reason, tell Alex. » **« signup stays false for now: correct »** — it waits for the Stripe webhook, which Alex creates
   first, and for one test purchase.
3. **Two answers for Alex.** (1) Accounts created through the old « Créer un compte » form between go-live and its
   removal: the list (date, e-mail, credits), or « none ». How many credits did such an account receive? (2) E-mail
   templates (welcome, trial, purchase, password reset): do they say « documents » and « e-mail » everywhere? « We
   cannot see them from outside. »
4. **Small details.**
   | Where | Now | Change to |
   | --- | --- | --- |
   | Admin: confirmation shown when refusing a trial request | « … Aucun email ne sera envoyé. » | « … Aucun e-mail ne sera envoyé. » |
   | `/app/inscription`, unknown pack (« Ce pack n'existe pas. ») | Link « scanid.fr/#tarifs », to `https://scanid.fr/#tarifs` | Link « scanid.fr/tarifs.html », to `https://scanid.fr/tarifs.html` |

   **Export file (XLSX, CSV):** the same sentence-case headers as the table, if not already done — Alex's export made
   before this deployment still had « Date de Naissance », « Date d'Expiration », « Score de Confiance »; he could not
   re-check without an account.
5. **Optional — server (unchanged from the previous note).** Compression: CSS and JS still uncompressed (measured with
   gzip: home page 162 KB → 40 KB, app 304 KB → 92 KB; `gzip_types text/css application/javascript application/json
   image/svg+xml text/xml;`). www: `https://www.scanid.fr/…` still 200 → 301 to the same path on `https://scanid.fr`.
   Removed pages: 301 `/temoignages.html` → `/presentation.html` and `/iftm/` → `/essai.html` (today 404).

Constraints and permissions: §0. The user's rule (as for §F and §G): a demand of the PDF wins over a restriction of this
file.

### H.2 Findings before touching anything

1. **Git:** `master` = `origin/master` = **`109993f`** (task G, « Changes made after go-live demanded from Alex », committed
   2026-10-02 20:44 +04:00 = 18:44 Paris — exactly the 28 paths of §G.0); tree clean. Baselines: backend **365**, unit
   **89**.
2. **Live (public requests, 2026-10-02 evening):** task G's backend and app ARE live — `POST /api/users/register` → 404;
   app bundle `index-CXHlP1c2.js` (the hash of G7's local build), 0 × « Créer un compte » / `users/register` / « HT le
   scan ». **nginx is NOT reloaded:** `site.css` → 113 379 bytes with `Accept-Encoding: gzip` and no `Content-Encoding`;
   `https://www.scanid.fr/tarifs.html` → 200; no `Cache-Control` on `/tarifs.html` or `/assets/…`; `/temoignages.html`
   and `/iftm/` → 404. ⇒ **Alex's section 5 is exactly the pending reload** (§F.0 step 4 + §G.5 step 3): the vhost that
   « Deploy » synced already holds gzip and the www 301 (G6) and the two 301s (F3). No code. `/api/config` →
   `{"signup":false,"trial":false}`.
3. **Section 2 — `trial`** is derived, not stored: `trial = mailer.is_configured()` = `SMTP_HOST` set (§C.2.4). It is
   false because the server's `.env` has no SMTP variables yet (§G.5 step B not done). It cannot be set from the
   repository and must not be forced: without mail the trial flow breaks (no notification to contact@, no welcome
   e-mail, no password link). It needs the IONOS mailbox password of contact@scanid.fr on the server — typed there,
   never in a chat or in the repository.
4. **Section 3.1 — the list** needs the production database and journal on the VPS (§G.5 A): `users` has no creation
   date and its ids are random `uuid4`; the removed route logged nothing but uvicorn's access line `"POST /users/register
   HTTP/1.1" 200`, which `log_redaction` leaves intact. This file forbids connecting to the VPS without the user's
   go-ahead (§D.7), and the commands need `sudo`. « How many credits »: **5** (`SIGNUP_PAGE_CREDITS`, removed in
   `109993f`; already in §G.5).
5. **Section 3.2 — the templates:** `backend/emails.py` has six (password reset, trial notification to Alex, trial
   welcome, pack purchase, « à la carte » purchase, payment anomaly); `main.py` sends only these. Since `109993f` (live
   since 18:44): « documents » and « e-mail » everywhere, pinned by `tests/test_email_wording.py` (every template rendered:
   no `\bscans?\b`, no `\b[Ee]mails?\b`). The only « scan » left are verbs: welcome step 1 « Photographiez ou scannez vos
   documents » (Alex's « Email A ») and the signature's « Scanner · Vérifier · Sécuriser ». The reset e-mail names no
   credits.
6. **Section 4, row 1:** `frontend/src/App.jsx:1087` ``window.confirm(`Refuser la demande de ${request.nom} ? Aucun email
   ne sera envoyé.`)`` — missed in G3; the only visible « email » left in `App.jsx` (the other match is a code comment).
   Not pinned: `trials.spec.js` accepts the dialog without reading it.
7. **Section 4, row 2:** `App.jsx:827` « Choisissez votre pack sur la page des tarifs : `<a href="https://scanid.fr/#tarifs">
   scanid.fr/#tarifs</a>`. » Its server twin `main.py:763` `UNKNOWN_PACK` (« Ce pack n'existe pas. Choisissez un pack sur
   https://scanid.fr/#tarifs. » — `/signup` and `/orders` → 400, shown on the same page by its error line if the server
   refuses a pack) and the mock's copies (`tests/mock/api.js:312, 329`). G.3.4 had kept both and reported them (§G.5
   « Not changed — Alex's call »); Alex now asks for the change. Pinned: `signup.spec.js:72` (the link);
   `test_pack_purchase.py:102` matches only « Ce pack n'existe pas ».
8. **Section 4 — export:** `main.py` `EXPORT_HEADERS` == the table's `columnTranslations` since `109993f` (« Date de
   naissance », « Date d'expiration », « Score de confiance »); Alex's export predates 18:44. Pinned by `test_export.py`.
   Nothing to change — to be proven with real files.

### H.3 Decisions

1. **Row 1:** « Aucun email » → « Aucun e-mail »; `trials.spec.js` reads the dialog and asserts its exact text.
2. **Row 2:** the page's link → text « scanid.fr/tarifs.html », href `https://scanid.fr/tarifs.html`; the server's
   `UNKNOWN_PACK` and the mock's copies → « … sur https://scanid.fr/tarifs.html. » (the same « Ce pack n'existe pas » on
   the same page: one target). Tests: `signup.spec.js` (link); `test_pack_purchase.py` (fragment = the whole message).
3. **Export:** no code; proven with a real CSV and XLSX produced by the backend (H3).
4. **Sections 2, 3.1 and 5 are server-only:** a runbook for the user (§H.5), one command per message when guided; no
   connection to the VPS from here without the user's go-ahead; no secret in a chat.
5. **Not changed (not in this note):** the server error messages that still write « email » (listed in §G.5 « Not
   changed — Alex's call »), « Crédits pages », the straight apostrophe — restated in the answers for Alex.

### H.4 Stages

| Stage | Content | Status |
| --- | --- | --- |
| H0 | Survey: PDF, git, live state, the code of every row, baselines (backend 365, unit 89) | **DONE** |
| H1 | Demand, findings, decisions, plan here | **DONE** |
| H2 | Section 4, rows 1–2: « e-mail » in the refusal confirmation; unknown pack → `tarifs.html` (app, server message, mock, tests) | **DONE** |
| H3 | Section 4 export + section 3.2: real CSV / XLSX headers from the backend; every e-mail template rendered and read | **DONE** |
| H4 | Verification: backend, unit, eslint, build + guard + bundle strings, e2e (touched specs, then full) | **DONE** |
| H5 | Record + how to ship + the server runbook (nginx reload = section 5; `trial` = SMTP; the list = 3.1) + answers for Alex | **DONE** (§H.5) |

### Stage H2 — section 4, rows 1–2 — DONE

- `frontend/src/App.jsx` `TrialRequestsPage.decide`: the confirmation is now « Refuser la demande de {nom} ? Aucun e-mail ne
  sera envoyé. » `PackSignupPage` (unknown pack): « Choisissez votre pack sur la page des tarifs : `<a
  href="https://scanid.fr/tarifs.html">scanid.fr/tarifs.html</a>`. »
- `backend/main.py` `UNKNOWN_PACK` (`/signup`, `/orders`): « Ce pack n'existe pas. Choisissez un pack sur
  https://scanid.fr/tarifs.html. »; `frontend/tests/mock/api.js`: its two copies follow. No `#tarifs` left in `src/`,
  `tests/`, `backend/`.
- Tests written first and run against the old code — **red for the right reasons**: `trials.spec.js` (the dialog's exact
  text, read in the `once('dialog')` handler as `features.spec.js` does) → « Received: … Aucun email ne sera envoyé. »;
  `signup.spec.js` (link « scanid.fr/tarifs.html » → `https://scanid.fr/tarifs.html`) → not found;
  `test_pack_purchase.py` (fragment = the whole message) → 1 failed. After the fix: `test_pack_purchase.py` **26
  passed**; `trials` + `signup` desktop + mobile-375 **16 passed**.
- eslint: `App.jsx` **11** problems (= `HEAD`'s 11); the three touched test files clean.
- NB for the harness: run test commands **sequentially, with absolute paths** — two parallel calls with `cd` share one
  working directory (a parallel `npx playwright` resolved to a stray global copy: « Project "desktop" not found »).

### Stage H3 — the export headers and the e-mail templates, proven — DONE

No code. Evidence from a throw-away pytest file in the session scratchpad (`h3/test_h3_evidence.py`, run from `backend/`
with `pytest -p tests.conftest <file> -s -q -p no:cacheprovider` — the repository's fixtures, nothing written in the
repository; `git status` unchanged afterwards):
- **Export (PDF section 4):** the real downloads of `GET /export/data?format=csv` and `?format=xlsx` (fixture
  `user_with_documents`) both start with exactly the table's headers: « Nom de famille, Prénom, Sexe, Date de naissance,
  Date d'expiration, Nationalité, Numéro de document, Type, Destination, Score de confiance » (CSV with its UTF-8 BOM;
  XLSX sheet « Passeports »). LibreOffice (`soffice --headless --convert-to csv`) reads the XLSX header row identically,
  4 data rows (the other user's document excluded). These headers came with `109993f`, live since 18:44 — Alex's export
  with « Date de Naissance » predates that deployment. Nothing to change.
- **Templates (PDF question 3.2):** all six rendered with `APP_PUBLIC_URL=https://scanid.fr/app/` (`h3/templates.txt`)
  and read in full:
  | Template | Subject | Wording |
  | --- | --- | --- |
  | trial notification (to contact@) | « Demande d'essai — {société} » | « (20 documents offerts) », « E-mail : … » |
  | trial welcome (at « Valider ») | « Votre espace ScanID est ouvert — 20 documents offerts » | « Vous disposez de 20 documents offerts », « Répondez simplement à cet e-mail » |
  | pack purchase | « Vos 1 000 documents ScanID sont disponibles » | « Vos 1 000 documents ont été ajoutés » |
  | « à la carte » purchase | « Vos 37 documents ScanID sont disponibles » / « Votre document ScanID est disponible » | « 37 documents ont été ajoutés » / « 1 document a été ajouté » |
  | password reset | « Réinitialisation de votre mot de passe ScanID » | « ignorez simplement cet e-mail » (names no credits) |
  | payment anomaly (to contact@) | « Paiement Stripe à rattacher manuellement » | « E-mail du client : … » |

  No « scan(s) » noun, no « email » anywhere (also pinned by `tests/test_email_wording.py`). The only « scan » forms are
  verbs: welcome step 1 « Photographiez ou scannez vos documents » (Alex's « Email A ») and the signature tagline
  « Scanner · Vérifier · Sécuriser ». A trial requester gets no e-mail when submitting (only the notification to
  contact@); the welcome comes at « Valider ».

### Stage H4 — verification — DONE

| Check | Result |
| --- | --- |
| `cd backend && …/newvenv/bin/python -m pytest -q` | **365 passed** (count unchanged: one parametrized case now pins the whole message) |
| `cd frontend && npm run test:unit` | **89 passed** |
| eslint | `App.jsx` **11** (= `HEAD`); `signup.spec.js`, `trials.spec.js`, `tests/mock/api.js` clean |
| Full e2e, all projects (`./node_modules/.bin/playwright test`) | **442 passed, 1 skipped** (3.8 min) = the count at the end of task G |
| `VITE_API_URL=/api npm run build` + guard | 64 files, 0 pages rewritten; guard **5/5**; `dist/` root == the folder's 63 files byte for byte + `sw.js`; bundle **`index-DvNksTlx.js`**: 1 × « Aucun e-mail ne sera envoyé », 2 × `scanid.fr/tarifs.html` (the unknown-pack link: href + text); 0 × « Aucun email », `#tarifs`, « Créer un compte », `users/register`, « HT le scan », `localhost`; 1 × `"/api"` |
| Real stack (§F.5 harness) | **not rebuilt — on purpose:** the change is two strings in the app and one server constant; no route, vhost, header or flow changed. The mock e2e reads the rendered dialog and link on desktop + mobile, and the backend test reads the server's answer |
| After | ports 5173 / 4173 / 8001 free; `git status --short` == §H.0 (7 entries), nothing staged |

### H.5 How to ship task H — the nginx reload, the server steps, the answers for Alex (stage H5)

**What ships** (nothing committed, §0.3): the 7 entries of §H.0 — `git add --dry-run .` = **7 paths** (checked). No new
dependency, no migration, no `.env` change, **no vhost change** (the vhost on the server is already G's, synced at 18:44).

**The user ships it — one command per message when guided:**
1. **Laptop:** `git status --short` (= §H.0) → `git add --dry-run . | wc -l` (7) → `git add .` →
   `git commit -m "App: « e-mail » in the trial refusal confirmation, unknown pack links to tarifs.html"`
   → `git push origin master`.
2. **GitHub:** « CI » green, « Deploy » green (« NOTE: nginx not reloaded … » is expected — deploy account). The deploy
   restarts the backend (new `UNKNOWN_PACK`) and ships the bundle `index-DvNksTlx.js`.
3. **VPS — reload nginx** (independent of 1–2, may come first): `ssh lasha@87.106.22.235` → `sudo nginx -t && sudo
   systemctl reload nginx` → `bash /opt/travelapp/ops/verify-front-end.sh` → « ALL CHECKS PASSED ». This one reload
   activates task F (cache headers, `/temoignages.html` and `/iftm/` 301s) and task G (gzip, `www` → 301) = **all of
   Alex's section 5**. `nginx -t` is the safety gate: if it fails, nothing is reloaded and the site keeps running.
4. **Laptop checks** (public requests — the assistant may run them): the list of §G.5 step 4 (register 404; `www` → 301
   `https://scanid.fr/tarifs.html`; `site.css` → `content-encoding: gzip`, `max-age=31536000`, `Vary: Accept-Encoding`;
   `tarifs.html` → `no-cache`; the two 301s; `/api/config`), plus task H:
   ```bash
   B=$(curl -s https://scanid.fr/app/ | grep -o '/app/assets/index-[^"]*\.js'); echo "$B"                       # /app/assets/index-DvNksTlx.js
   curl -s "https://scanid.fr$B" | grep -o -e 'Aucun e-mail ne sera envoyé' -e 'scanid.fr/tarifs.html' | sort | uniq -c   # 1 and 2
   curl -s "https://scanid.fr$B" | grep -c -e 'Aucun email' -e 'scanid.fr/#tarifs'                               # 0
   ```
5. Mark §F.0, §G.0 and §H.0 **SHIPPED** (hashes, date); update the memory notes.

**Server steps — the user's (outside the repository; a secret never goes through a chat):**
- **B. `trial` → true (PDF section 2, « now »)** — mail on the server:
  1. `sudo nano /opt/travelapp/backend/.env` — add three lines (port 587 + STARTTLS, the sender « ScanID
     <contact@scanid.fr> » and the admin address contact@scanid.fr are defaults — no line needed); put the password
     between single quotes if it contains `#`, a space, a quote or `$`:
     ```
     SMTP_HOST=smtp.ionos.fr
     SMTP_USERNAME=contact@scanid.fr
     SMTP_PASSWORD='<the mailbox password, typed on the server>'
     ```
  2. Test the login **before** the restart — sends nothing, never prints the password, reads the file with the same
     parser as the backend (checked locally: a password with `@`, space, `$`, `#` parses; a dead server → clean
     `ConnectionRefusedError`):
     `sudo /opt/travelapp/venv/bin/python -c "from dotenv import dotenv_values as d; import smtplib, ssl; v = d('/opt/travelapp/backend/.env'); s = smtplib.SMTP(v['SMTP_HOST'], int(v.get('SMTP_PORT') or 587), timeout=20); s.starttls(context=ssl.create_default_context()); s.login(v['SMTP_USERNAME'], v['SMTP_PASSWORD']); print('SMTP login OK'); s.quit()"`
     → « SMTP login OK ». `SMTPAuthenticationError` = wrong password (or SMTP not allowed on the mailbox): fix it
     before restarting — with SMTP_HOST set, `trial` turns true at the restart whatever the password.
  3. `sudo systemctl restart travelapp.service` → `curl -s https://scanid.fr/api/config` → `{"signup":false,"trial":true}`.
  4. Alex's run (§C.1): essai.html with his test address → notification « Demande d'essai — … » at contact@scanid.fr
     and the request in « Demandes d'essai » → Valider → « Votre espace ScanID est ouvert — 20 documents offerts » →
     password link (48 h) → login « Crédits : 20 » → delete the test account. An e-mail missing:
     `sudo journalctl -u travelapp.service --since "30 min ago" --no-pager | grep -i "email not sent"`.
  The domain is ready for it (public DNS, 2026-10-02): MX `mx00/mx01.ionos.fr`, SPF `v=spf1
  include:_spf-eu.ionos.com ~all`, IONOS DKIM `s1-ionos` / `s2-ionos._domainkey`, DMARC `p=none`.
- **A. The list for Alex (PDF question 3.1)** — read-only, on the VPS (as §G.5 A):
  1. how far back the journal goes (go-live was 2026-09-08): `sudo journalctl -u travelapp.service --no-pager -o
     short-iso | head -1`; and that it records requests at all: `sudo journalctl -u travelapp.service --no-pager | grep
     -c 'HTTP/1.1"'` (> 0);
  2. the dates — one line per account created by that form: `sudo journalctl -u travelapp.service --no-pager -o
     short-iso | grep '"POST /users/register HTTP/1.1" 200'` — nothing, with a journal reaching back to go-live, means
     **« none »**;
  3. the e-mails and credits — candidates = role `user`, no trial request, no purchase (also lists accounts made by
     hand in Administration): `sudo -u postgres psql -d travelapp -c "SELECT u.email, u.user_name, u.page_credits AS
     credits, u.uploaded_pages_count AS documents, u.status, (SELECT min(j.created_at) FROM ocr_jobs j WHERE j.user_id =
     u.id) AS first_upload FROM users u WHERE u.role = 'user' AND NOT EXISTS (SELECT 1 FROM trial_requests t WHERE
     t.user_id = u.id) AND NOT EXISTS (SELECT 1 FROM purchases p WHERE p.user_id = u.id) ORDER BY u.email;"`;
  4. only if the journal starts after go-live — nginx keeps ~14 days: `sudo zgrep -h 'POST /api/users/register'
     /var/log/nginx/access.log* | grep '" 200 '`.
  Each account got 5 credits at creation (`credits` now = 5 minus what it used). Nothing is changed — Alex decides.
- **C. `signup` → true** — unchanged (§G.5 C); Alex: « stays false for now: correct ».

**Answers for Alex** (the user forwards them; in English, like his note):
1. **Trial (section 2).** Not kept false on purpose: `trial` turns itself on as soon as the server can send e-mail, and
   the outgoing mail of contact@scanid.fr (IONOS SMTP) is not configured on the server yet. It cannot be forced on before
   that — the trial flow sends your notification and the welcome e-mail with the password link. Lasha enters the
   mailbox password on the server (never by e-mail or chat) and restarts; `/api/config` then says `"trial": true` and
   your test run can start. The domain's DNS is ready (SPF, DKIM, DMARC at IONOS).
2. **Question 3.1.** Such an account received **5 credits**, usable at once, with a freely chosen user name. The list
   (date, e-mail, credits) — or « none » — comes from the server's logs and database: Lasha sends it (step A).
3. **Question 3.2.** Yes — all six e-mails, live since 18:44: welcome « Votre espace ScanID est ouvert — 20 documents
   offerts »; your trial notification « (20 documents offerts) », « E-mail : »; pack purchase « Vos 1 000 documents
   ScanID sont disponibles »; à la carte « Vos 37 documents… » / « Votre document… »; password reset « ignorez simplement
   cet e-mail »; payment anomaly « E-mail du client ». The only « scan » left is a verb: « Photographiez ou scannez vos
   documents » (welcome, step 1) and the signature « Scanner · Vérifier · Sécuriser ».
4. **Section 4.** Both rows done as written; the server's own « Ce pack n'existe pas » message points to tarifs.html
   too. Live at the next deployment. **Export:** already done at 18:44 — the CSV and XLSX headers are exactly the
   table's (checked on real files): « Date de naissance », « Date d'expiration », « Score de confiance ».
5. **Section 5.** All three (gzip, www → scanid.fr, the two 301s) are in the server configuration since 18:44 and take
   effect with one nginx reload, which Lasha does by hand (the deployment account may not reload nginx).
6. **Still « email » — your call** (server messages, unchanged): the forgot-password answer « Si un compte correspond à
   cet identifiant, un email contenant un lien de réinitialisation vient de lui être envoyé. »; « L'adresse email n'est
   pas valide. »; « Un compte existe déjà avec cette adresse email. Connectez-vous pour acheter ce pack. »; « Un compte
   ou une demande existe déjà pour cette adresse email. »; admin only: « L'envoi d'emails n'est pas configuré : le
   compte n'a pas été activé. », « Email déjà enregistré ». Also « Crédits pages » (admin users table).

---

## G. TASK G (2026-10-02) — ALEX'S « AFTER GO-LIVE » LIST — COMMITTED `109993f` — ✅ SHIPPED 2026-10-03 (NGINX RELOADED)

### G.0.0 THIS SESSION (2026-10-02, the session after task F's) — EVERY PROMPT, WHAT IS DONE, WHAT IS LEFT

Asked by the user (verbatim): « Wen you finich this stage update the SCANID-HANDOVER.md to mark what is aready done
from the prompts of the current session! » — this table. **Done** = finished and checked in this session; **Left** = what
is still open, and who does it.

| # | Prompt (verbatim, or in substance) | Done | Left |
| --- | --- | --- | --- |
| 1 | « Read SCANID-HANDOVER.md and resume = continue from the interrupted stage! All what you need to implement is in frontend/ScanID-nouveau-site-2026-09-30, but partially it is already implemented, resume = continue where it was interrupted! CRUCIAL if current prompt violates the restriction from SCANID-HANDOVER.md respect current prompt and neglect restriction from SCANID-HANDOVER.md! » + Alex's PDF « Lasha-Deploy-New-Website-2026-09-30.pdf » | **DONE.** Task F was already complete (F0–F6); re-checked: tree == §F.0, `HEAD` = `origin/master` = `bf7dc3c`, folder unchanged (63 files), backend 357, unit 89, `VITE_API_URL=/api npm run build` 64 files / 0 rewrites, guard 5/5, `dist/` root == folder + `sw.js`, no harness leftovers — nothing left to implement; shipping guided (rows 2–6) | — |
| 2 | « Why i need "back up the live site on the server"? » then « it is deployed using github acctions and there is all version of the old codebase! » | **DONE.** Explained (Alex's PDF §3.1 assumes a hand upload; here the web root is rebuilt from Git); §F.6 step 1 **skipped by the user's decision**, ticked in §F.0 | — |
| 3 | « All is tested and confirmed that it works? » | **DONE.** Answered: verified locally (suites, e2e 442/1, real stack 21/21 + 26/26) vs. only after the deploy (nginx 1.24 + reload, the workflow edits, real Formspree / Stripe) | — |
| 4 | « There is nothing that must be in .gitignoe and is not in already? » | **DONE.** The 82 paths checked: no build output, logs, archives, caches or secrets (only fake test values); `backend/.env`, `frontend/.env.local`, `dist`, `node_modules`, `test-results`, `newvenv`, `__pycache__` still ignored → nothing to add | — |
| 5 | « provide short git commit text! only text! » then « ? » | **DONE.** Message given; the user committed **`e9d527d`** « Site: Alex's new website, nginx cache and redirects, « à la carte » credits » | — |
| 6 | « i commited! can push it? » | **DONE.** Commit checked (82 files, tree clean, parent `bf7dc3c`); the user pushed: `origin/master` = `e9d527d`; « Deploy » ran — site live (Alex's note: 63 files byte-identical) | **nginx reload on the VPS** (task F's cache headers + 301s): not done yet — folded into §G.5 step 3 (one reload for F and G) |
| 7 | « CRUCIAL the restrictions and permissions remains same! Execute what is in attached .pdf file! » + Alex's PDF « Lasha-After-Go-Live-2026-10-02.pdf » | **DONE locally (G0–G8).** Section 2: « Créer un compte » + form removed, `POST /users/register` removed (404) — answer to Alex: such an account got **5 credits**. Section 3: « documents » / « e-mail » in the app and all e-mail templates. Section 4: `PUBLIC_SIGNUP=0` hold + runbook. Section 5: gzip, www → scanid.fr, « Tarifs » → `tarifs.html`, sentence-case headers. Verified: backend 365, unit 89, e2e 442 / 1 skipped, real stack 34 + 2 + 2 | **The user:** ship (§G.5 steps 1–5: commit + push, workflows, nginx reload, laptop checks); server steps A (the account list for Alex), B (`trial` = SMTP), C (`signup` = secret + hold + test purchase). Nothing committed (§0.3) |
| 8 | « Wen you finich this stage update the SCANID-HANDOVER.md to mark what is aready done from the prompts of the current session! » | **DONE.** This table; « Last updated » and the resume protocol point here | — |

### G.0 State in one line (update after every stage)

**✅ SHIPPED — 2026-10-03: nginx reloaded by the user (≈ 18:12 UTC; `nginx -t` ok, `verify-front-end.sh` → ALL CHECKS
PASSED) and the laptop checks all green (register 404; `www` → 301 `https://scanid.fr/tarifs.html`; `site.css` gzip +
`max-age=31536000` + `Vary: Accept-Encoding`; `tarifs.html` `no-cache`; `/temoignages.html` → 301 `/presentation.html`;
`/iftm/` → 301 `/essai.html`; bundle `index-CJFY_9p8.js` gzip, the 9 task-I labels, 0 old ones; `/api/config`
`{"signup":false,"trial":true}`) — §J.4. The unticked nginx boxes below are history.**

**G0–G8 DONE; committed `109993f` by the user and pushed; « Deploy » ran (18:44 Paris) — backend and app live. Still
open: the nginx reload (step 3) and what follows it, and the server steps A–C — all carried into §H.5 (task H, Alex's
« second check », which confirms G live). Do not re-implement anything.**

**Ship progress** (tick as the user reports each §G.5 step; one command per message when guiding):
- [x] 1 committed **`109993f`** (« Changes made after go-live demanded from Alex », the 28 paths below) and pushed by the
  user, 2026-10-02 20:44 +04:00 — `git ls-remote origin refs/heads/master` = `109993f…` = local `HEAD` (checked in task H)
- [x] 2 « Deploy » ran (18:44 Paris): `POST /api/users/register` → 404, live bundle `index-CXHlP1c2.js` = G7's build;
  Alex's second check §1 confirms. (« CI » run page not visible from here — `gh` not installed.)
- [ ] 3 nginx **NOT reloaded** — checked 2026-10-02 evening: no gzip on CSS, `www` → 200, no cache headers,
  `/temoignages.html` / `/iftm/` → 404 → **§H.5 step 3**
- [ ] 4 laptop checks of §G.5 step 4 (+ §F.6 step 5) — after the reload (§H.5)
- [ ] 5 SHIPPED → §G.0 and §F.0 say SHIPPED (hash, date); memory notes updated
- [ ] A list for Alex · [ ] B `trial` true · [ ] C `signup` true (server steps — continued in §H.5)

**Expected `git status --short` (nothing staged) — 27 modified, 1 untracked:** ` M` `.github/workflows/ci.yml`,
`README.md`, `SCANID-HANDOVER.md`, `backend/{.env.example,config.py,emails.py,main.py,schemas.py}`,
`backend/tests/{helpers.py,test_existing_api.py,test_export.py,test_pack_purchase.py,test_password_policy.py,
test_security_hardening.py,test_trial_requests.py,test_unit_purchase.py}`, `deploy/nginx-travelapp.conf`,
`frontend/src/App.jsx`, `frontend/tests/e2e/{a11y,design-system,features,password-policy,password,signup,sitenav,
trials}.spec.js`, `frontend/tests/mock/api.js`; `??` `backend/tests/test_email_wording.py`. Any other difference: report
it, do not « fix » it.
**Quick baseline for a resumed session:** `cd backend && ../newvenv/bin/python -m pytest -q` → **365 passed**;
`cd frontend && npm run test:unit` → **89 passed**; full e2e **442 passed, 1 skipped**. If `docker ps` or
`ps -eo pid,args | grep -E "uvicorn mai[n]|postgre[s] -D"` show leftovers of an interrupted G6/G7 run, stop them first
(§F.5 « Stopping »). Git at the start of task G: `master` = `origin/master` = `e9d527d`; `git status --short` = only
` M SCANID-HANDOVER.md`. Baseline before any change: backend **357**, unit **89**.

### G.1 The demand, verbatim (user, 2026-10-02)

> CRUCIAL the restrictions and permissions remains same!
> Execute what is in attached .pdf file!

The PDF was attached to the message (it is **not** in the repository): « Lasha-After-Go-Live-2026-10-02.pdf », Alex's
note, 2 pages, headed « SCANID · FOR LASHA = for you- Claude Code! », « After go-live — confirmed and remaining »
(checked live on 02/10 without an account; three things to do, sections 2–4; section 5 optional). In substance:
1. **Confirmed — nothing to do.** Website (63 files byte-identical, 22 pages clean desktop + mobile, 404 page with
   status 404); removals gone (temoignages.html, /iftm/, images/, og-image.png, the video, /fonts/site.css, /scripts/);
   login page fixes; « Sexe » in the list and the XLSX export, PP / PI; forms reached contact@scanid.fr through
   Formspree, « the trial request works end to end (Alex's test) »; the four Stripe links; `/api/docs` and
   `/api/openapi.json` 404.
2. **« Créer un compte » on the login page — to close.** Under « Se connecter », « Créer un compte » opens « Créer un
   nouveau compte » (Prénom, Nom de famille, Email, Numéro de téléphone, Nom d'utilisateur, Mot de passe) → `POST
   /api/users/register`: anyone can open an account without trial validation or a pack. **Question: how many credits
   does such an account receive?** Requested: (1) remove the button and the form — the two ways in are the trial
   request (validated in « Demandes d'essai ») and `/app/inscription?pack=…` (Spec v3); (2) close `POST
   /api/users/register` to the public (remove it, or admin only) — only this form calls it; (3) if accounts were created
   through it since go-live, send Alex the list (date, e-mail, credits). If self-registration must stay, tell Alex first
   (at least 0 credits, e-mail as identifier). **Test:** `/app/` shows E-mail, Mot de passe, « Mot de passe oublié ? »
   and « Se connecter », nothing else; a POST to `/api/users/register` no longer creates an account.
3. **« scans » → « documents » in the app** (the site says « documents », Alex's decision of 14/09):
   | Where | Now | Change to |
   | --- | --- | --- |
   | /app/inscription, pack summary | « 1 000 scans de passeports ou CNI françaises — crédits valables 12 mois, soit 0,69 € HT le scan. » | « 1 000 documents (passeports ou CNI françaises) — crédits valables 12 mois, soit 0,69 € HT le document. » |
   | /app/inscription, under « Créer votre compte » | « … vos scans y sont ajoutés dès que Stripe confirme le règlement. » | « … vos crédits y sont ajoutés dès que Stripe confirme le règlement. » |
   | Admin, « Demandes d'essai » | « Chaque demande a créé un compte en attente avec 20 scans offerts. » | « … avec 20 documents offerts. » In the same text, « email » → « e-mail ». |
   | Field labels | « Email », « Email professionnel » | « E-mail », « E-mail professionnel » (as on the login page) |

   « Please check the e-mail templates too (welcome, trial, purchase). » Alex updates the four Stripe product
   descriptions himself. **Test:** no « scan » left on `/app/inscription?pack=1000`.
4. **The two switches in `GET /api/config`** (today `{"signup": false, "trial": false}`): **trial → true, now** (only
   effect on the site: the confirmation after a trial request says the password link arrives after validation);
   **signup → true, after three things:** (1) section 3 done; (2) the Stripe webhook — Alex creates the endpoint
   (`https://scanid.fr/api/stripe/webhook`, event `checkout.session.completed`) and gives the signing secret through the
   dashboard, never by chat; (3) one test purchase: credits added once, the purchase in « Mes achats ». From then on the
   site's « Choisir ce pack » opens `/app/inscription?pack=…`; nothing to change on the site.
5. **Optional — server and small details:** compression (`gzip_types text/css application/javascript application/json
   image/svg+xml text/xml;` — CSS and JS are sent uncompressed, site.css 113 KB); `https://www.scanid.fr/…` serves the
   site without redirecting → 301 to `https://scanid.fr/…`; 301 `/temoignages.html` → `/presentation.html` and `/iftm/`
   → `/essai.html` (today 404); app top menu « Tarifs » → `https://scanid.fr/tarifs.html` (today `/#tarifs`, which still
   works); column headers, table and export, in sentence case as on the site: « Date de naissance », « Date
   d'expiration », « Score de confiance ».
   Later, nothing to do now: the « à la carte » payment link (§F.6 a–e).

Constraints and permissions: §0, unchanged (« the restrictions and permissions remains same »); the user's rule of §F.1
still applies. « Execute what is in the pdf » covers section 5 too.

### G.2 Findings before touching anything

1. **Self-registration** = `POST /users/register` (`main.py` `self_register_user`, 5/minute, `schemas.UserRegister`):
   an **active** account with **`SIGNUP_PAGE_CREDITS = 5` credits** (the answer to Alex's question), usable at once,
   with a freely chosen « Nom d'utilisateur » (not the e-mail). Only the login page's « Créer un compte » →
   `SelfRegistrationPage` (view `signup`, no URL of its own) calls it. Other users of the route: the CI smoke test
   (`openapi.json` must contain `"/users/register"`), backend tests (`test_existing_api` 1, `test_password_policy` 4 —
   the server-side policy, `test_security_hardening` 7 — a quick way to create a user with a known password), e2e
   (`features.spec.js` 1 test on that form, `password-policy.spec.js` 9 tests on its live password rules — the same
   `PasswordRules` component is on `/app/inscription`), the e2e mock (route + `API_PATHS`). The remaining ways in:
   `/trial-requests` (validated by Alex), `/signup` (`/app/inscription`, 0 credits + pending purchase), `POST
   /admin/users/` (admin only).
2. **The `users` table has no creation date** → for Alex's list (2.3): e-mail and credits from the database, dates from
   the backend journal (uvicorn logs one `"POST /users/register HTTP/1.1" 200` line per account; production runs
   `uvicorn main:app --port 8001` with its access log) or nginx's access logs (`/api/users/register`, rotated). In the
   data, a self-registered account looks like an admin-created one: candidates = role `user`, no trial request, no
   purchase (the trial and pack flows always leave one).
3. **Visible « scans »:** `App.jsx` pack summary, the line under « Créer votre compte », the admin « Demandes d'essai »
   text. E-mails (`emails.py`): trial notification to Alex (« 20 scans offerts »), welcome (subject + body), purchase
   (subject + body). **Visible « email »:** field labels `columnTranslations.email` (admin users table + admin forms),
   « Email professionnel » (inscription), the trial details « Email », « Mon Compte » « Email », the forgot page label
   « Email ou nom d'utilisateur » and its sentence, the admin search placeholder « Rechercher (Nom, Email...) », the
   admin trial text and its confirmation « … reçoit l'email de bienvenue … »; templates « cet email » (reset, welcome),
   « Email : » (trial notification), « Email du client » (anomaly). The site writes « e-mail » (43×, never « email » in
   text) and « 20 documents offerts ». Server error messages also say « email » (`crud`/`main` « Email déjà
   enregistré », « L'adresse email n'est pas valide. », « Un compte existe déjà avec cette adresse email… », the
   forgot-password answer « un email contenant un lien… », « L'envoi d'emails n'est pas configuré… », `trials.py` ×2).
4. **Switches** (§C.2.4): derived, not stored — `signup = bool(STRIPE_WEBHOOK_SECRET)`, `trial = mailer.is_configured()`
   (SMTP_HOST in production). « trial → true » = the SMTP variables on the server (§C.5.1), no code. « signup »:
   installing the secret turns it on **at once**, i.e. at Alex's step (2), before his test purchase (3) — following his
   order needs a way to hold it off.
5. **Live, 2026-10-02 after the push of `e9d527d`:** site live; **nginx not reloaded** (no `Cache-Control`;
   `/temoignages.html`, `/iftm/` → 404) — Alex's « Removed pages (today: 404) » is exactly task F's pending reload, no
   code. CSS not gzipped (`content-length: 113379` with `Accept-Encoding: gzip`; HTML is: the server's `nginx.conf` has
   `gzip on` with the default `text/html` only). `https://www.scanid.fr/` → 200: the 443 block has `server_name
   scanid.fr www.scanid.fr` and the certificate covers www; port 80 already redirects everything to `https://scanid.fr`.
6. **Column headers:** export `main.py` (French headers dict) and table `App.jsx` `columnTranslations` (« Date de
   Naissance », « Date d'Expiration », « Score de Confiance »; the admin users table also « Numéro de Téléphone »,
   « Nom d'Utilisateur »). Pinned by `test_export.py`, the mock, `design-system.spec.js`, `features.spec.js`.
7. **Tarifs:** `SITE_LINKS` (top bar + the app's site menu) → `https://scanid.fr/#tarifs`. Also `#tarifs`: the « Ce pack
   n'existe pas » page link and the backend's `UNKNOWN_PACK` message (both still work).

### G.3 Decisions

1. **Section 2 — removed, not made admin-only:** the admin path already exists (`POST /admin/users/`). Frontend: the
   button, the `onShowRegistration` prop, the `signup` view, `SelfRegistrationPage`. Backend: the route,
   `schemas.UserRegister`, `SIGNUP_PAGE_CREDITS` → `POST /api/users/register` answers **404** and creates nothing.
   Existing accounts untouched (Alex decides from the list). Tests: the register-based fixtures → `make_user(…,
   password=…)` (same `crud.create_user` every creation path uses); the 4 policy tests → `/signup` (the public form that
   remains); the register test → « the route is closed » (404, no account); e2e: the registration test → Alex's test
   (the login card holds exactly E-mail, Mot de passe, « Mot de passe oublié ? », « Se connecter »); the password-rules
   spec → `/app/inscription?pack=100`; mock route removed; CI smoke → `"/signup"`. Alex's list: read-only commands for
   the user on the VPS (§G ship steps).
2. **Section 3 — Alex's four rows as written;** « email » → « e-mail » in every field label, column header and
   placeholder of the app, the admin trial screen (text + confirmation), the forgot page (label + its sentence, same
   card), and **all** e-mail templates (« check the e-mail templates too »: « scans » → « documents », « email » →
   « e-mail »). Not changed: server error messages (G.2.3 — not labels, not templates; reported to the user), internal
   names (`scans`, `perScanHtCents`, `_scans`), the e-mail signature's tagline.
3. **Section 4 — trial:** no code (SMTP on the server, runbook). **signup:** new `PUBLIC_SIGNUP` — `0` / `false` /
   `no` / `off` keeps `signup` false whatever the secret; unset = today's behaviour (never true without the secret).
   Runbook: secret + `PUBLIC_SIGNUP=0` → test purchase through `/app/inscription?pack=100` → remove the line → `signup`
   true.
4. **Section 5:** nginx 443 block: `gzip on; gzip_vary on; gzip_types text/css application/javascript text/javascript
   application/json image/svg+xml text/xml;` (Alex's list + `text/javascript`, which newer nginx `mime.types` use for
   `.js`) and `if ($host = www.scanid.fr) { return 301 https://scanid.fr$request_uri; }` at server level (one block: an
   HTTP/2 connection reused between the two names cannot bypass it). Removed pages: nothing (the reload). Tarifs:
   `SITE_LINKS` only (the menu Alex names); the pack-not-found link and `UNKNOWN_PACK` keep `#tarifs` (reported).
   Headers: sentence case in the export and the table, including the admin users table's two (same dictionary, same
   rule).
5. **Ship:** one commit; then the nginx reload (covers task F's too); the server steps are the user's.

### G.4 Stages

| Stage | Content | Status |
| --- | --- | --- |
| G0 | Survey (PDF, register route + users, texts, e-mails, switches, live headers, nginx, tests) + baselines (backend 357, unit 89) | **DONE** |
| G1 | Demand, findings, decisions, plan here | **DONE** |
| G2 | Section 2: remove self-registration (app, API, tests, mock, CI) | **DONE** |
| G3 | Section 3: « scans » → « documents », « email » → « e-mail » (app, e-mail templates, tests) | **DONE** |
| G4 | Section 5, app: « Tarifs » → `tarifs.html`; sentence-case headers (table + export, tests) | **DONE** |
| G5 | Section 4: `PUBLIC_SIGNUP` hold (config, `/config`, `.env.example`, tests) | **DONE** |
| G6 | Section 5, nginx: gzip + www → 301; tested on a docker nginx with the real vhost (§F.5 harness) | **DONE** |
| G7 | Verification: backend, unit, lint, build + guard, full e2e, rendered checks of Alex's two tests | **DONE** |
| G8 | Record + how to ship + the server runbook (reload; the list for Alex; trial = SMTP; signup = secret + hold + test purchase) | **DONE** (§G.5) |

### Stage G2 — self-registration removed — DONE

- `frontend/src/App.jsx`: « Créer un compte » button gone from `Login`; its `onShowRegistration` prop, the `signup` view
  and `SelfRegistrationPage` (the « Créer un nouveau compte » form, the only caller of `/users/register`) removed; the
  `APP_ROOT` comment no longer cites the registration reload.
- `backend/main.py`: route `POST /users/register` and `SIGNUP_PAGE_CREDITS` removed; a 3-line comment under « User
  Routes » says where accounts come from. `backend/schemas.py`: `UserRegister` removed; the `UserCreate.role` comment
  names the public signup instead. → `POST /users/register` = **404** (no route, no other `/users/{…}` path matches).
- Tests: `tests/helpers.py` `make_user(…, password=…)` (default unchanged); `test_security_hardening.py` 7 accounts made
  with it (same `crud.create_user` as every creation path); `test_existing_api.py`
  `test_self_registration_is_closed` (404, no user by e-mail or name, absent from `openapi.json`);
  `test_password_policy.py` 4 server-side tests through `/signup` (local `signup()` helper, valid SIRET, only the
  password can fail; « compliant registration » → « compliant signup » + `checkout_url`). E2E: `features.spec.js` —
  the registration test → « l'écran de connexion ne propose que la connexion, sans « Créer un compte » » (Alex's test:
  labels E-mail / Mot de passe, 2 inputs, buttons exactly « Afficher le mot de passe », « Mot de passe oublié ? »,
  « Se connecter »); `password-policy.spec.js` → `/app/inscription?pack=100` (same `PasswordRules`), the server-message
  test fills the inscription form by `name`. Mock: route + `API_PATHS` entry removed. CI smoke: `"/signup"`.
- `README.md` items 2–3 described the removed feature → « No self-registration » / « Starting credits ».
- Results: backend **357 passed** (count unchanged: 1 test replaced one for one); unit **89**; `password-policy` +
  `features` desktop **35 passed**; eslint: `App.jsx` 11 problems (baseline 12 — one unused `err` left with the form),
  the 3 touched test files clean.

### Stage G3 — « documents » and « e-mail » — DONE

- `frontend/src/App.jsx`: Alex's rows as written — pack summary « {n} documents (passeports ou CNI françaises) — crédits
  valables 12 mois, soit {x} HT le document. »; « … vos crédits y sont ajoutés dès que Stripe confirme le règlement. »;
  admin « Demandes d'essai » « … 20 documents offerts. « Valider » … l'e-mail de bienvenue … « Refuser » le ferme sans
  e-mail. »; labels « E-mail » (`columnTranslations.email` — admin users table + admin forms; Mon Compte; trial
  details), « E-mail professionnel » (inscription), « E-mail ou nom d'utilisateur » + its sentence « Indiquez votre
  e-mail… » (forgot page), placeholder « Rechercher (Nom, E-mail...) », admin confirmation « … reçoit l'e-mail de
  bienvenue … ». Internal names (`summary.scans`, `perScanHtCents`) unchanged.
- `backend/emails.py`: trial notification « (20 documents offerts) », « E-mail : »; welcome subject « Votre espace ScanID
  est ouvert — 20 documents offerts », body « Vous disposez de 20 documents offerts », « cet e-mail »; purchase subject
  « Vos 1 000 documents ScanID sont disponibles », body « Vos 1 000 documents ont été ajoutés »; reset « cet e-mail »;
  anomaly « E-mail du client ». Only the module docstring still says « email » (developer text). Server error messages
  not changed (G.3.2).
- Tests: 3 backend asserts follow (`test_pack_purchase`, `test_trial_requests`, `test_unit_purchase`); new
  `tests/test_email_wording.py` (7: every template rendered — no `\bscans?\b`, no `\b[Ee]mails?\b`; the three named
  texts) — against `HEAD`'s `emails.py`: **6 failed / 1 passed** (the à la carte e-mail was already clean), restored →
  7 passed. E2E: `signup.spec.js` label « E-mail professionnel », Alex's pack-summary sentence, the « crédits » line and
  **no `\bscans?\b` in the page text of `/app/inscription?pack=1000`** (Alex's test); `trials.spec.js` the intro text
  (regex) + « l'e-mail de bienvenue »; `password.spec.js` label « E-mail ou nom d'utilisateur ».
- Results: backend **364 passed** (357 + 7); `signup` / `trials` / `password` / `account` desktop **17 passed**, then
  `trials` with the intro check **3 passed**.

### Stage G4 — « Tarifs » and sentence-case headers — DONE

- `frontend/src/App.jsx` `SITE_LINKS`: « Tarifs » → `https://scanid.fr/tarifs.html` (the top bar and the app's site menu
  both render this list). The « Ce pack n'existe pas » link and the backend `UNKNOWN_PACK` message keep `#tarifs`
  (G.3.4 — reported).
- Headers, sentence case: `backend/main.py` `EXPORT_HEADERS` and `App.jsx` `columnTranslations` — « Date de
  naissance », « Date d'expiration », « Score de confiance »; the admin users table's « Numéro de téléphone », « Nom
  d'utilisateur » (same dictionary, same rule). The apostrophe stays the ASCII one the app uses everywhere (the site
  writes « d’expiration » with ’; Alex asked for the case only).
- Tests: `test_export.py` (10 strings — header list, date-column lookup, widths: lengths unchanged), the mock's export
  headers, `design-system.spec.js` (4), `features.spec.js` (1), `sitenav.spec.js` (« Tarifs » href).
- Results: backend **364**, unit **89**; `design-system` / `features` / `sitenav` / `sex-column` / `confidence` desktop
  **49 passed**.

### Stage G5 — the `PUBLIC_SIGNUP` hold — DONE

- `backend/config.py` `public_signup_held()`: `PUBLIC_SIGNUP` = `0` / `false` / `no` / `off` (trimmed, any case) → true.
  `backend/main.py` `public_config`: `signup = bool(STRIPE_WEBHOOK_SECRET) and not public_signup_held()` (docstring
  says why); `trial` unchanged. `/signup` and `/orders` are NOT gated — the test purchase goes through them. Only the
  site reads `/api/config` (`core.js` pack buttons, `essai.js` confirmation); the app never does.
- `backend/.env.example`: `# PUBLIC_SIGNUP=0` under `STRIPE_WEBHOOK_SECRET=` with the three-step use.
- Test `test_trial_requests.py::test_signup_can_be_held_off_while_the_webhook_is_tested` (held values → false; `""`,
  `1`, `on`, unset → true; never true without the secret). Mutation: `/config` ignoring the hold → **1 failed**;
  restored → passed. Backend **365 passed**.

### Stage G6 — nginx: gzip and www → 301 — DONE

- `deploy/nginx-travelapp.conf`, 443 block, right **below** `include …/nginx-security-headers.conf`: `if ($host =
  www.scanid.fr) { return 301 https://scanid.fr$request_uri; }` — below on purpose: the include's `set $scanid_csp`
  must run before the `return` (first placed above it, the www 301 left with **no CSP** — seen in the probe, moved);
  then `gzip on; gzip_vary on; gzip_types text/css application/javascript text/javascript application/json
  image/svg+xml text/xml;` (comments say why; `text/javascript` = RFC 9239's name — nginx 1.27's `mime.types` still
  says `application/javascript` for `.js`, checked). Port 80 block and every location unchanged.
- **Harness** (scratchpad, rebuildable — §F.5 items 1–2 + `nginx/probe.sh`): certs SAN scanid.fr + www.scanid.fr;
  `make_conf.sh`; `scanid-nginx-new` (this vhost, 8081/8443) and `scanid-nginx-head` (`git show HEAD:` vhost,
  8082/8444), `nginx:1.27-alpine`, `--network host`; backend = `stack/backend.sh` (uvicorn on 8001, ENVIRONMENT
  production, scratch PostgreSQL on 55433 — SQLite is refused: production passes PostgreSQL-only connect options).
  `probe.sh <https> <http>`: 43 lines (status, Location, Cache-Control, Content-Type, Content-Encoding, Vary, CSP zone
  + count, nosniff/X-Frame/Referrer) with `Accept-Encoding: gzip` — NB the system `awk` is mawk: headers are matched
  after `tolower`.
- Results: `nginx -t` ok on both (only the old `listen … http2` warning). Diff HEAD → new = exactly: `Content-Encoding:
  gzip` + `Vary: Accept-Encoding` on HTML (site pages, 404 bodies, `/app/`), CSS, JS (site + app bundle + `sw.js`), SVG,
  `sitemap.xml`, `/api/config` JSON; **not** on ico, png, txt, pdf, woff2, jpeg, webmanifest; `www.scanid.fr` `/`,
  `/tarifs.html?x=1`, `/app/`, `/api/config`, `/nope`, a POST → **301 `https://scanid.fr<same path + query>`** with the
  app CSP + the 3 security headers (was 200 / served). Everything else identical (statuses, cache headers, CSP zones,
  security headers; the 301s of `/temoignages.html` and `/iftm*` differ only by the test port in Location); `POST
  /api/users/register` → 404 JSON. Integrity: gunzipped == plain == file (sha256) for site.css, core.js, tarifs.html,
  favicon.svg, sitemap.xml, app/index.html; no `Accept-Encoding` → no encoding header; **site.css 113 379 → 30 832
  bytes**, core.js 14 137 → 5 579, tarifs.html 19 371 → 6 013. Revalidation: gzip's weak ETag `W/"…"` and the plain
  strong one both → **304**.

### Stage G7 — verification — DONE

| Check | Result |
| --- | --- |
| `cd backend && ../newvenv/bin/python -m pytest -q` | **365 passed** (357 + 7 wording + 1 hold; the register test replaced one for one) |
| `cd frontend && npm run test:unit` | **89 passed** |
| eslint, touched files | `App.jsx` **11** problems (baseline 12: one unused `err` left with the form); every touched test file clean. NB `npm run lint` (`eslint .`) also lints Alex's site scripts (`ScanID-nouveau-site-2026-09-30/…/assets/js`, 341 problems — browser globals) since task F; CI runs no lint (only the build); the read-only folder is not touched |
| Full e2e, all projects | first run **439 passed, 3 failed, 1 skipped**: `a11y.spec.js` « les boutons de l'écran de connexion aussi » counted ≥ 2 design-system buttons (« Se connecter » + « Créer un compte ») → now ≥ 1, purpose kept (every one ≥ 44 px); clean rerun **442 passed, 1 skipped** (4.0 min, exit 0) = the pre-task count |
| `VITE_API_URL=/api npm run build` + guard | 64 files, 0 rewrites; guard **5/5**; `dist/` root == the folder + `sw.js`; bundle `index-CXHlP1c2.js`: 0 × « Créer un compte », `users/register`, « HT le scan », « 20 scans », « Email professionnel », the title-case headers, `localhost`; 1 × « HT le document », « vos crédits y sont ajoutés », « 20 documents offerts », « E-mail professionnel », `tarifs.html`, `"/api"`; the one `#tarifs` = the « Ce pack n'existe pas » link (G.3.4) |
| Real stack (docker nginx with the new vhost + uvicorn production mode + scratch PostgreSQL), Chromium (`stack/g7_check.cjs`, `--host-resolver-rules`, `--ignore-certificate-errors` — without it the self-signed test certificate blocks the service worker's script, the 4 « SSL certificate error » console lines of a first pass) | phase **base** (no secret) **34/34**: `/app/` desktop + 375 px — labels exactly « E-mail », « Mot de passe », 2 inputs, buttons exactly eye / « Mot de passe oublié ? » / « Se connecter », no « Créer un compte », every « Tarifs » → `tarifs.html`, no console error / failed request / CSP violation; `POST /api/users/register` from the page → **404** `{"detail":"Not Found"}`, database: 0 probe accounts (only `admin`); `/app/inscription?pack=1000` — **no `\bscans?\b` in the page text** (Alex's test), his sentence, « vos crédits… », « E-mail professionnel »; admin « Demandes d'essai » text, users table headers « E-mail », « Numéro de téléphone », « Nom d'utilisateur », « Crédits pages » (no capital after a space), placeholder « Rechercher (Nom, E-mail...) »; site `/`, `/tarifs.html`, `/presentation.html` — site.css + core.js arrived **gzip**, Mona Sans loaded, clean; `/api/config` signup false, « Choisir ce pack » → the Stripe link. Phase **held** (`STRIPE_WEBHOOK_SECRET` + `PUBLIC_SIGNUP=0`) **2/2**: signup false, button → Stripe; webhook live (bad signature → **400**, not 503). Phase **open** (secret, no hold) **2/2**: signup true, button → `/app/inscription?pack=1000`. Screenshots looked at (login card, inscription) |
| Found and fixed during G7 | « Crédits Pages » — a 3rd title-case header in the same dictionary → « Crédits pages » (no test pinned it) |
| Harness stopped | backend killed, both containers removed, PostgreSQL stopped; ports 8001 / 8081 / 8082 / 8443 / 8444 / 55433 / 5173 / 4173 free; `git status --short` = §G.0 (28 entries), nothing staged |

### G.5 How to ship task G — and the server steps (stage G8)

**What ships** (nothing committed, §0.3): 27 modified files + `backend/tests/test_email_wording.py` — `git add --dry-run .`
= **28 paths** (§G.0 lists them). No new dependency, no database migration, no `.env` change required.

**The user ships it** (one command per message when guided):
1. **Laptop:** `git status --short` (= §G.0) → `git add --dry-run . | wc -l` (28) → `git add .` →
   `git commit -m "App: close self-registration, « documents » and « e-mail » wording, sentence-case headers, Tarifs link; nginx gzip and www to scanid.fr; PUBLIC_SIGNUP hold"`
   → `git push origin master`.
2. **GitHub:** « CI » green (its smoke test now looks for `"/signup"`), « Deploy » green. The deploy restarts the backend
   — `/users/register` disappears at that moment — and syncs the vhost (not yet active).
3. **VPS — reload nginx** (activates task F's cache headers + 301s AND task G's gzip + www): `sudo nginx -t && sudo
   systemctl reload nginx`, then `bash /opt/travelapp/ops/verify-front-end.sh` → « ALL CHECKS PASSED ».
4. **Laptop checks** (public requests — the assistant may run them):
   ```bash
   curl -s -o /dev/null -w '%{http_code}\n' -X POST -H 'Content-Type: application/json' -d '{}' https://scanid.fr/api/users/register   # 404
   curl -sI https://www.scanid.fr/tarifs.html | grep -iE '^(HTTP|location)'                       # 301 → https://scanid.fr/tarifs.html
   curl -sI -H 'Accept-Encoding: gzip' 'https://scanid.fr/assets/css/site.css?v=202609302115' | grep -iE '^(content-encoding|cache-control|vary)'   # gzip, max-age=31536000, Accept-Encoding
   curl -sI https://scanid.fr/tarifs.html | grep -i cache-control                                   # no-cache (task F)
   curl -sI https://scanid.fr/temoignages.html | grep -iE '^(HTTP|location)'                         # 301 → /presentation.html (task F)
   curl -sI https://scanid.fr/iftm/ | grep -iE '^(HTTP|location)'                                   # 301 → /essai.html (task F)
   B=$(curl -s https://scanid.fr/app/ | grep -o '/app/assets/index-[^"]*\.js'); curl -s "https://scanid.fr$B" | grep -c -e 'Créer un compte' -e 'users/register' -e 'HT le scan'   # 0
   curl -s https://scanid.fr/api/config                                                             # {"signup":false,"trial":false} until B / C below
   ```
5. Then task F's §F.0 steps 4–5 and task G are both shipped → mark §F.0 and §G.0 **SHIPPED** (hash, date).

**Server steps — the user's (outside the repository), any time after step 2:**
- **A. The list for Alex (PDF 2.3)** — read-only, on the VPS. The `users` table has no creation date (G.2.2), so:
  - accounts that are neither trial nor pack (self-registered — or created by hand in Administration):
    `sudo -u postgres psql -d travelapp -c "SELECT u.email, u.user_name, u.page_credits AS credits, u.uploaded_pages_count AS documents, u.status, (SELECT min(j.created_at) FROM ocr_jobs j WHERE j.user_id = u.id) AS first_upload FROM users u WHERE u.role = 'user' AND NOT EXISTS (SELECT 1 FROM trial_requests t WHERE t.user_id = u.id) AND NOT EXISTS (SELECT 1 FROM purchases p WHERE p.user_id = u.id) ORDER BY u.email;"`
    (tested on the scratch database: lists a stand-in self-registered account, not the admin);
  - the dates, one line per account created: `sudo journalctl -u travelapp.service --no-pager -o short-iso | grep '"POST /users/register HTTP/1.1" 200'`;
    how far the journal goes back: `sudo journalctl -u travelapp.service --no-pager -o short-iso | head -1`; nginx keeps
    ~14 days: `sudo zgrep -h 'POST /api/users/register' /var/log/nginx/access.log* | grep '" 200 '`.
  Nothing is deleted or changed — Alex decides what happens to those accounts.
- **B. `trial` → true (PDF 4, « now »)** = e-mail on the server (§C.5.1): in `/opt/travelapp/backend/.env`
  `SMTP_HOST=smtp.ionos.fr`, `SMTP_USERNAME=contact@scanid.fr`, `SMTP_PASSWORD=<the mailbox password — typed on the
  server, never in a chat>` → `sudo systemctl restart travelapp.service` → `curl -s https://scanid.fr/api/config` →
  `"trial":true`. Then Alex's run (§C.1): essai.html with his test address → notification at contact@scanid.fr + the
  request in « Demandes d'essai » → Valider → welcome e-mail (« 20 documents offerts ») → password link (48 h) → login
  « Crédits : 20 » → delete the test account.
- **C. `signup` → true (PDF 4, after three things):** (1) section 3 — shipped with this task; (2) Alex creates the
  endpoint `https://scanid.fr/api/stripe/webhook` (event `checkout.session.completed`; add
  `checkout.session.async_payment_succeeded` so a bank transfer credits too, §C.5.2) and the signing secret goes into
  `.env` — never through a chat — **together with `PUBLIC_SIGNUP=0`**: `STRIPE_WEBHOOK_SECRET=whsec_…` +
  `PUBLIC_SIGNUP=0` → restart → `/api/config` still `"signup":false` while the webhook is live (checked in G7: a bad
  signature → 400, not 503); (3) the test purchase: open `https://scanid.fr/app/inscription?pack=100` directly, create an
  account with a test address, pay → « Crédits : 100 » once; in Stripe, « Resend » the event → credits unchanged;
  « Mon Compte » → « Mes achats » shows « Pack 100 »; refund in Stripe if wanted. Then **delete the `PUBLIC_SIGNUP=0`
  line** → restart → `"signup":true` → the site's « Choisir ce pack » opens `/app/inscription?pack=…` (checked in G7).
  Without the hold line the flag turns on at step (2)'s restart.

**Answers for Alex** (the user forwards them):
- « How many credits does an account created this way receive? » — **5**, usable at once, with a freely chosen « Nom
  d'utilisateur » (code: `SIGNUP_PAGE_CREDITS = 5`, now removed).
- Section 2: the button and the form are gone; `POST /api/users/register` no longer exists (404, nothing created);
  the list = step A.
- Section 3: done as written, plus « e-mail » in every field label of the app and in all e-mail templates (welcome,
  trial notification, purchase, password reset, anomaly). The four Stripe product descriptions are Alex's.
- Section 4: `trial` = step B; `signup` = step C (the `PUBLIC_SIGNUP=0` hold makes his order possible).
- Section 5: gzip, www → scanid.fr, « Tarifs » → tarifs.html, sentence-case headers in the table and the exports (also
  « Numéro de téléphone », « Nom d'utilisateur », « Crédits pages » in the admin users table); the two 301s are live
  once nginx is reloaded (step 3).
- **Not changed — Alex's call:** server error messages still write « email » (e.g. « L'adresse email n'est pas
  valide. », « Un compte existe déjà avec cette adresse email… », « Email déjà enregistré »); the « Ce pack n'existe
  pas » page and its server message still link `scanid.fr/#tarifs` (works); « Crédits pages » still says « pages »
  where the site says « documents »; headers keep the app's straight apostrophe (« Date d'expiration »).

---

## F. TASK F (2026-10-02) — ALEX'S NEW WEBSITE (« nouveau-site ») + « À LA CARTE » CREDITS — PUSHED `e9d527d` — ✅ SHIPPED 2026-10-03 (NGINX RELOADED)

### F.0 State in one line (update after every stage)

**✅ SHIPPED — 2026-10-03: nginx reloaded by the user (≈ 18:12 UTC; `nginx -t` ok, `verify-front-end.sh` → ALL CHECKS
PASSED) and the laptop checks all green (register 404; `www` → 301 `https://scanid.fr/tarifs.html`; `site.css` gzip +
`max-age=31536000` + `Vary: Accept-Encoding`; `tarifs.html` `no-cache`; `/temoignages.html` → 301 `/presentation.html`;
`/iftm/` → 301 `/essai.html`; bundle `index-CJFY_9p8.js` gzip, the 9 task-I labels, 0 old ones; `/api/config`
`{"signup":false,"trial":true}`) — §J.4. The unticked nginx boxes below are history.**

**F0–F6 DONE; shipped as `e9d527d` (pushed 2026-10-02, live). Only open: §F.6 step 4, the nginx reload on the VPS
(cache headers + the two 301s), then the laptop checks of step 5 — one reload covers F, G and H: §H.5 step 3.**
« À la carte » is switched on later, with Alex (§F.6 a–e).

**Ship progress** (tick as the user reports each §F.6 step; one command per message when guiding):
- [x] 1 web root backup — **skipped by the user's decision (2026-10-02)**: the web root is rebuilt from Git by « Deploy »
  (`rsync --delete`, no exclusion), so every live version is in the repository; rollback = `git revert` + push
  (~5 min of CI + deploy)
- [x] 2 committed **`e9d527d`** (82 files, tree clean) and pushed by the user, 2026-10-02 — `git ls-remote origin
  refs/heads/master` = `e9d527d…` = local `HEAD` (checked)
- [x] 3 « Deploy » ran: the site is live (Alex's « after go-live » note, 02/10: the 63 files served are byte-identical to
  the folder, `/fonts/site.css` and `/scripts/` gone; checked here: `/` 200, `/assets/css/site.css` 200, new app bundle
  `index-PW3lKQZ5.js`). The run pages themselves are not visible from here (`gh` not installed).
- [ ] 4 **nginx NOT reloaded yet** — checked live 2026-10-02: no `Cache-Control` on `/tarifs.html` or `/assets/…`,
  `/temoignages.html` and `/iftm/` answer **404** (Alex: « Removed pages … today: 404 »). The user runs
  `sudo nginx -t && sudo systemctl reload nginx` on the VPS — one reload covers F, G and H (**§H.5 step 3**). Re-checked
  2026-10-02 evening, after G's deploy: still not reloaded (Alex's « second check » section 5).
- [ ] 5 laptop checks of §F.6 step 5 — after the reload
- [x] 6 Alex's ten-minute check — done by Alex (« after go-live » note §1: pages, forms → contact@scanid.fr, trial end to
  end, Stripe links, login page, « Sexe », `/api/docs` 404); his remaining points are task G
- [ ] 7 SHIPPED → §F.0 says SHIPPED (hash, date); §F becomes a record; memory note updated

**Expected `git status --short` from F4 on (nothing staged) — 18 modified, 2 untracked:**
` M` `.github/workflows/deploy.yml`, `SCANID-HANDOVER.md`, `backend/{.env.example,billing.py,config.py,emails.py,main.py}`,
`deploy/nginx-travelapp.conf`, `frontend/public/{apple-touch-icon.png,favicon.svg}`, `frontend/scripts/assemble-site.mjs`,
`frontend/src/{App.jsx,billing.js,billing.test.js}`, `frontend/tests/build/no-google-fonts.test.js`,
`frontend/tests/e2e/{account,design-system}.spec.js`, `ops/verify-front-end.sh`;
`??` `backend/tests/test_unit_purchase.py`, `frontend/ScanID-nouveau-site-2026-09-30/` (the user's folder — must be
committed with the rest, the build reads it). Any other difference: report it, do not « fix » it.
**Quick baseline for a resumed session:** `cd backend && ../newvenv/bin/python -m pytest -q` → **357 passed**;
`cd frontend && npm run test:unit` → **89 passed**. Then, if `docker ps` or
`ps -eo pid,args | grep -E "run_backen[d]|fake_strip[e]|postgre[s] -D"` show leftovers of an interrupted F5 run, stop
them first (§F.5 « Stopping » — never `pgrep -f` / `pkill -f` with the plain name, it kills your own shell). Git at the start of
task F: `master` = `origin/master` = `bf7dc3c` (task E, pushed); `git status --short` = only
`?? frontend/ScanID-nouveau-site-2026-09-30/`. Baseline reproduced before any change: backend
**328 passed**, frontend unit **88 passed**.

### F.1 The demand, verbatim (user, 2026-10-02)

> CRUCIAL Read SCANID-HANDOVER.md!
> CRUCIAL all the restrictions stays as they are in SCANID-HANDOVER.md, but if i demand you somthing in
> this current prompt that violates any restriction from SCANID-HANDOVER.md you should respect current
> prompts demand and neglect restriction from SCANID-HANDOVER.md!
> Read the pdf file with prompts and all what you will need to make corresponding changes you will find
> in frontend/ScanID-nouveau-site-2026-09-30!

The PDF was attached to the message (it is **not** in the repository): « Lasha-Deploy-New-Website-
2026-09-30.pdf », Alex's deployment notes, 2 pages, headed « SCANID · FOR LASHA = you-Claude Code ».
In substance:
1. **Before you deploy.** « Sexe » is live (task D); the site shows the exported columns in this order:
   Nom de famille, Prénom, Sexe, Date de naissance, Date d'expiration, Nationalité, Numéro de document,
   Type, Destination, Score de confiance. Type: PP passport, PI ID card — « If the list filter in the
   app still reads PASS, please align it to PP ». temoignages.html and /iftm/ are removed; the new site
   no longer links to them.
2. **The folder** `nouveau-site`: 22 pages, same URLs as today + `tarifs.html` and `mrz.html`;
   `404.html` uses absolute links; `assets/css`, `assets/js` (lib.js + core.js on every page + one
   script per page, no inline JavaScript), `assets/fonts` (self-hosted Mona Sans, IBM Plex Mono);
   `assets/docs/ScanID-Specimen-Passeport.jpg`; `og/*.jpg` (1200 × 630); new `favicon.svg`,
   `favicon.ico`, `apple-touch-icon.png`; new `ScanID-Checklist-RGPD.pdf` (same name); `robots.txt`;
   `sitemap.xml` (21 public pages).
3. **Deploy.** Back up the web root; upload the folder's content to it (files 644, folders 755);
   nginx `error_page 404 /404.html;` if not set; cache: HTML without cache, `/assets/` and `/og/` long
   (CSS and JS versioned with `?v=`); no longer used, deletable once checked: `images/`,
   `og-image.png`, `scanid-presentation.mp4`, `.htaccess`; optional 301 redirects `/temoignages.html` →
   `/presentation.html` and `/iftm/` → `/essai.html`. CSP: compatible, no change.
4. **What the pages call.** essai.html: `POST /api/trial-requests` (nom, societe, email, telephone,
   volume, message "", siret "", tva "", consentement true) and `GET /api/config` (`trial` chooses the
   confirmation text); on API failure → Formspree, subject « Demande d'essai · 20 documents offerts ».
   Pack buttons (index, tarifs): `GET /api/config` — `signup` true → `/app/inscription?pack=100|1000|
   3000|5000`, otherwise the current Stripe links. contact.html, checklist.html → Formspree (« Message
   depuis scanid.fr », « Demande de rappel · démonstration », « Téléchargement checklist RGPD »).
   Nothing else: no analytics, no cookies, no third-party script.
5. **New « à la carte » (1,50 € HT per document).** Alex creates a Stripe Payment Link with an
   adjustable quantity (1 unit = 1 document). **App side: on `checkout.session.completed` for this
   link, credit the account with the purchased quantity (the line item quantity).** Site side: until
   the link exists, the « À la carte » button of tarifs.html leads to essai.html; to switch it, in
   tarifs.html the link with `data-pack="unite"`: `href="essai.html"` → the Stripe link, text
   « Commencer par l'essai » → « Acheter à l'unité » (or send the link to Alex, who regenerates the page).
6. **After deploying — ten-minute check:** home, Présentation, Tarifs, Essai, Contact, one article —
   the menu button opens the full menu, no console error; Tarifs slider, « Choisir ce pack » opens
   Stripe (or `/app/inscription` once `signup` = true); Essai: one real request with Alex's test
   address appears in « Demandes d'essai »; Contact: one message + one callback reach
   contact@scanid.fr; `/app/` still opens the login page, a wrong URL shows the new 404; resubmit the
   sitemap in Google Search Console.
7. **Good to know:** the app screens drawn on the site use « Ajouter un document », « Documents
   traités », « Mes documents » — tell Alex if the app interface changes; the site is generated from
   Alex's sources; small text edits can be made in the HTML.

Constraints and permissions: §0, unchanged, except where this demand requires otherwise (the user's
rule above) — the new folder becomes the site's source of truth (§0.5 note).

Twice during the task (verbatim): « Crucial! You finish current stage and update the SCANID-HANDOVER.md in such way
that in the fresh = new cseesion you could resume = continue current work seamlessly in the case if i interrupt this =
current seesion! » and « Crucial! You finish current stage and update the SCANID-HANDOVER.md in such way that in the
fresh = new cseesion you could resume = continue current work seamlessly with only "Read SCANID-HANDOVER.md" prompt in
the case if i interrupt this = current seesion! » — hence §F.0 (exact state, expected tree, quick baseline), the
ticked sub-steps and the rebuildable harness of §F.5, and the ship-progress list in §F.0. Standing rule (§D.1): keep
§X.0 current after every stage, and point the resume protocol at the top to the current task.

### F.2 Findings before touching anything

1. **How the site reaches scanid.fr.** Nothing is uploaded by hand: a push to `master` runs « Deploy »
   — `npm run build` (vite → `dist/app/`, then `scripts/assemble-site.mjs` copies the folder named by
   its `SITE` constant to the root of `dist/`) → `rsync -az --delete frontend/dist/` →
   `/opt/travelapp/frontend-dist` (the nginx root). So « upload the folder to the web root » = point
   `SITE` at the new folder, and « delete what is no longer used » happens by itself (`--delete`):
   temoignages.html, iftm/, og-image.png, scanid-presentation.mp4 disappear at the deploy;
   `.htaccess` was never shipped (`NEVER_COPY`); `images/` is not in today's build.
2. **The new folder** (untracked, 63 files, 3.4 MB): 22 pages; every local reference resolves; every
   `og:image` exists (1200 × 630); sitemap = the 21 public pages (all but 404.html). The pages need
   **none** of the assembler's rewrites: no `app.scanid.fr`, no Google Fonts, no preconnect, no inline
   `<script>` (34 JSON-LD data blocks only); « Connexion » is already `/app/`.
3. **Consequences in today's pipeline:**
   - the assembler always builds `dist/fonts/site.css` (Space Grotesk + Inter from @fontsource) for the
     old pages' Google Fonts links; the new pages link `assets/css/site.css` (their own fonts) → that
     bundle would ship unused (28 files, ~644 KB) and the deploy probe, `ops/verify-front-end.sh` and
     the build guard (« the public site ships the self-hosted faces it now links ») would keep checking a
     file no page uses — while nothing would check the stylesheet the pages really load;
   - `tests/e2e/design-system.spec.js` pins the app's `favicon.svg` / `apple-touch-icon.png` byte-identical
     to the site's (task B item 2: « site favicon »), read from `scanid-site-v5-deploy/` — the new site
     ships **new icons** (the new « id » mark).
4. **CSP:** `ops/nginx-site-csp.conf` already covers the new site — scripts, styles, fonts same-origin;
   images same-origin + `data:` (CSS check marks); `connect-src` / `form-action` formspree.io. The only
   object URL is the sample CSV download (`<a download>`, not governed by CSP). No change.
5. **nginx** (`deploy/nginx-travelapp.conf`): `error_page 404 /404.html;` is **already set**; no cache
   header anywhere; no redirect. A location block must not use `add_header` (it would drop the
   inherited security headers — the vhost's own note); `expires` is not `add_header`. The deploy
   account cannot reload nginx → a vhost change takes effect after the user's
   `sudo nginx -t && sudo systemctl reload nginx`.
6. **The calls of §4 are already served by the backend** (task B): the trial payload parses (empty
   siret / tva / message accepted, volume free text ≤ 100), `/api/config` = `{signup, trial}`,
   `/app/inscription?pack=100|1000|3000|5000`. Production `/api/config` = `{"signup":false,"trial":false}`
   (§C.2.4) → today the essai POST answers 503 and the request goes to Formspree: Alex's check 6.3
   (« it appears in « Demandes d'essai » ») holds only once SMTP is configured (§C.5.1).
7. **App:** the Type filter is already PP (task B, `DOC_TYPE_PASSPORT = 'PP'`) → nothing to align. Export
   column order == the site's list. Header casing differs — export « Date de Naissance », « Date
   d'Expiration », « Score de Confiance », site « Date de naissance »… — not demanded, not changed,
   reported. The app's vocabulary == §7's.
8. **À la carte — the webhook today** (`billing.credit_checkout_session`): pack identified by the
   **amount**, account by `client_reference_id` only. The à la carte link is a plain link from the site
   → no `client_reference_id`; its amounts collide with packs (66 × 1,50 € = 99 € = Pack 100 HT; 460 ×
   = 690 €; 1 260 × = 1 890 €) → the pack path would credit 100 for 66 bought. A
   `checkout.session.completed` payload never carries `line_items` (expandable only) → the quantity
   needs `GET /v1/checkout/sessions/{id}/line_items` with an API key; the backend has none today (only
   the webhook secret). The session carries `payment_link` (the link's id, `plink_…`).
   `purchases.pack` is NOT NULL; « Mes achats » prints « Pack {pack} ». CGV: every acquired credit is
   valid 12 months. `httpx` / `requests` are installed, but no backend module imports either.

### F.3 Decisions

1. **Source of truth:** `frontend/ScanID-nouveau-site-2026-09-30/nouveau-site/`, as placed by the user,
   read-only. `SITE` repointed (one constant, as in v5). `scanid-site-v5-deploy/` stays in the
   repository, untouched, no longer read (deleting it is the user's call).
2. **Assembler:** builds the @fontsource bundle (`dist/fonts/`) only when a page linked Google Fonts, and
   `dist/scripts/` only when a script is externalised; rewrites and refusals unchanged. With the new
   site: neither directory. Deploy probe + `ops/verify-front-end.sh`: `/fonts/site.css` →
   `/assets/css/site.css` (the stylesheet every page links). Build guard: the « faces it now links »
   test becomes site-agnostic (every stylesheet a page links is shipped, every font file it points at
   is shipped, at least one `@font-face`).
3. **App icons follow the site** (task B rule): `frontend/public/favicon.svg` and `apple-touch-icon.png`
   = byte copies of the new site's; the e2e pin reads the new folder.
4. **nginx:** `location /` gets `expires -1` (`Cache-Control: no-cache` — revalidated on every visit,
   never stale after a deploy); new `location /assets/` and `location /og/` with `expires 1y`, the site
   CSP snippet and `try_files $uri =404`; 301 redirects `/temoignages.html` → `/presentation.html`,
   `/iftm` and everything under `/iftm/` → `/essai.html`. `/app/` and `/api/` untouched. Tested on a
   real nginx (docker) with the real vhost and snippets.
5. **À la carte, app side — dormant until configured:**
   - a session is « à la carte » when `session.payment_link == STRIPE_UNIT_PAYMENT_LINK_ID` (the `plink_…`
     id of Alex's link) — checked **before** the pack path (amount collisions);
   - quantity = the single line item's `quantity`, read with `STRIPE_API_KEY` (a restricted key with
     « Checkout Sessions: Read » is enough) from `GET /v1/checkout/sessions/{id}/line_items` (stdlib
     `urllib`, 10 s timeout);
   - account = `client_reference_id` when present, else the checkout e-mail (`customer_details.email`):
     exactly one account, case-insensitive; a refused (`rejected`) account is not credited;
   - stored as `pack = 0` (« à la carte »), `credits = quantity`, `amount_ht_cents = quantity × 150`,
     paid, expiry + 12 months (CGV), same UNIQUE session id → credited once;
   - anything else (link not configured, no key, API error, not exactly one line item, quantity < 1,
     not EUR, no / several / refused account) → the existing « unmatched » path: nothing credited, 200,
     anomaly e-mail to Alex — never a guess;
   - e-mail « Vos N documents ScanID sont disponibles »; « Mes achats » shows « À la carte · N
     documents ». The pack path is unchanged.
6. **Not demanded, not done:** the site-side switch of the à la carte button (the link does not exist
   yet — the steps are kept in §F.6); the export header casing (F.2.7); the app's « Tarifs » link
   (`/#tarifs` still exists on the new home page); deleting `scanid-site-v5-deploy/`; README / ops docs
   (they still describe `frontend/site/`, never updated since v4).

### F.4 Stages

| Stage | Content | Status |
| --- | --- | --- |
| F0 | Survey (folder, pipeline, CSP, nginx, API calls, webhook) + baselines (backend 328, unit 88) | **DONE** |
| F1 | Write the demand, findings, decisions and plan here | **DONE** |
| F2 | Site in the build: `SITE`, assembler (fonts / scripts only when needed), build guard, deploy probe + verify script, app icons + e2e pin; build; `dist/` == the folder | **DONE** |
| F3 | nginx: cache headers + redirects; tested on a docker nginx with the real vhost | **DONE** |
| F4 | À la carte, app side: backend (config, billing, webhook, e-mail), « Mes achats », tests | **DONE** |
| F5 | Verification: all suites, lint, build + guard, full e2e; real stack (PostgreSQL + backend + docker nginx serving `dist/` with the real vhost): the PDF's ten-minute check on all 22 pages, essai → « Demandes d'essai », packs with `signup` off / on, forms → Formspree (intercepted), à la carte webhook against a fake Stripe API, screenshots desktop + phone | **DONE** (§F.5: e2e 442 / 1 skipped; phase A 21/21; phase B 26/26) |
| F6 | Record + how to ship (server backup, nginx reload, the two env vars once Alex's link exists, the site-side switch) | **DONE** (§F.6) |

### Stage F2 — the new site in the build — DONE

- `frontend/scripts/assemble-site.mjs`: `SITE` = `ScanID-nouveau-site-2026-09-30/nouveau-site`; the Google Fonts
  stylesheet rule carries `needsFontBundle`, and `buildFontBundle()` now runs **after** the pages, only if a page
  was rewritten by that rule; `dist/scripts/` is created when the first script is externalised; the summary says
  « no /fonts/ bundle — no page asks Google Fonts for a typeface ». Header comments follow. Rewrites and refusals
  unchanged.
- `frontend/tests/build/no-google-fonts.test.js`: « the public site ships the self-hosted faces it now links » reads
  the `<link rel="stylesheet">` of every site page: each stylesheet local and in the build, each font file it points
  at in the build, ≥ 1 `@font-face` (`posix` imported). Other 4 tests unchanged.
- `.github/workflows/deploy.yml`: probe `/fonts/site.css` → `/assets/css/site.css` (`style_code`; no apostrophe added
  — the remote script and the run block pass `bash -n`; the 4 apostrophes inside are the pre-existing
  `-w '%{http_code}'`); frontend rsync gains `--chmod=D755,F644` (PDF §3.2: files 644, folders 755 whatever the
  runner's umask). `ops/verify-front-end.sh`: same probe change (`bash -n` ok).
- `frontend/public/favicon.svg`, `frontend/public/apple-touch-icon.png`: byte copies of the new site's (sha256
  `d87c0465…`, `9d136e96…`); `tests/e2e/design-system.spec.js` « Onglet du navigateur » reads them from the new
  folder → desktop + mobile-375 **2 passed**.
- `VITE_API_URL=/api npm run build` → `assemble-site: 64 files into dist/ (0 pages rewritten)`, every rewrite 0,
  no `/fonts/`. `dist/` root == the folder **byte for byte** (63/63) + `sw.js` (= `legacy-sw-unregister.js`) +
  `app/`; root dirs `app assets og`; no `fonts/`, `scripts/`, `iftm/`, `temoignages.html`, `og-image.png`,
  `scanid-presentation.mp4`. (Local modes 664 = this laptop's umask 002; the rsync flag makes them 644/755 —
  checked: rsync to a scratch dir → 157 files 644, 10 dirs 755, stale files deleted.)
- Regression: `HEAD`'s assembler and the modified one, both pointed at `scanid-site-v5-deploy`, produce the **same
  63 files, same hashes** (fonts bundle and the 3 scripts included). Build guard **5/5** on the v5 dist and on the
  new dist; mutation: `dist/assets/fonts/mona-sans.woff2` removed → the test fails (« points at
  ../fonts/mona-sans.woff2, which is not in the build »), `dist/assets/css/site.css` removed → fails; restored → 5/5.

### Stage F3 — nginx — DONE

- `deploy/nginx-travelapp.conf`: `location /` + `expires -1;` (→ `Cache-Control: no-cache` + `Expires`); new
  `location /assets/` and `location /og/` (site CSP snippet, `expires 1y;`, `try_files $uri =404;`);
  `location = /temoignages.html { return 301 /presentation.html; }`, `location = /iftm` and `location /iftm/` →
  `return 301 /essai.html;`. Comments follow (no `add_header` anywhere new). `error_page 404` was already there.
- **Test harness** (scratchpad `nginx/`, rebuildable): self-signed cert for scanid.fr mounted at
  `/etc/letsencrypt/live/scanid.fr`; `make_conf.sh <vhost> <out> <http> <https>` = the real vhost with the listen
  ports replaced and the IPv6 listeners dropped; `docker run -d --network host` `nginx:1.27-alpine` (local image;
  production is 1.24 — same directives) with `ops/` at `/opt/travelapp/ops`, `frontend/dist` at
  `/opt/travelapp/frontend-dist`; `HEAD`'s vhost on 8082/8444, the new one on 8081/8443; `probe.sh <https> <http>`
  prints status, Location, Cache-Control, Expires, CSP zone + count, nosniff / X-Frame-Options / Referrer-Policy,
  Content-Type, 404 body, for 34 paths.
- Results: `nginx -t` ok on both (only the pre-existing `listen … http2` deprecation warning of 1.25+). Diff
  `HEAD` vs new = exactly: the 11 root/page files gain `no-cache` + Expires; the 5 `/assets/` + `/og/` files gain
  `max-age=31536000` + Expires; `/temoignages.html` → 301 `/presentation.html`, `/iftm`, `/iftm/`,
  `/iftm/index.html` → 301 `/essai.html` (404 with `HEAD`'s vhost). The 14 other paths identical: missing files
  under `/assets/` / `/og/`, `/nope`, `/faq`, `/calculateur.html`, `/fonts/site.css`, `/scripts/index-1.js` → 404
  with the new 404 page and no cache header; `/app/`, `/app/inscription`, `/app/assets/*.js`, `/app/sw.js`,
  `/app/favicon.svg` → 200 with the app CSP and no cache header (unchanged). Every response keeps nosniff,
  X-Frame-Options, Referrer-Policy and exactly one CSP (site zone on site files, including `/assets/` and `/og/`).
  Revalidation: `If-None-Match` → **304**. Port 80 → 301 `https://scanid.fr/…`. Only error log line: the
  `/api/config` upstream refused (no backend in that run; it proved the `/api` prefix is stripped). Containers
  removed.

### Stage F4 — « à la carte », app side — DONE

- `backend/config.py`: `UNIT_PRICE_HT_CENTS = 150`; `stripe_unit_payment_link_id()` (`STRIPE_UNIT_PAYMENT_LINK_ID`)
  and `stripe_api_key()` (`STRIPE_API_KEY`), read at call time like the webhook secret.
- `backend/billing.py`: `UNIT_PACK = 0`, `STRIPE_API_BASE`, `STRIPE_API_TIMEOUT_SECONDS = 10`; `StripeApiError`;
  `is_unit_session` (`payment_link` == the configured id); `fetch_line_items` (stdlib `urllib`, `Authorization:
  Bearer <key>`, session id URL-quoted, errors → `StripeApiError` worded for Alex, the key never in a message);
  `unit_quantity` (exactly one line item, int quantity ≥ 1); `unit_buyer` (`client_reference_id`, else the checkout
  e-mail — exactly one account, `lower()`); `CreditOutcome.credits`; `credit_checkout_session` dispatches to
  `_credit_unit_session` right after the duplicate check, **before** `identify_pack`. `_credit_unit_session`: EUR,
  buyer (not `rejected`), quantity, then one transaction (paid purchase pack 0 / credits N / `amount_ht_cents` N ×
  150 / expiry + 12 months / `amount_paid_cents` / `eur` + `page_credits += N`); `IntegrityError` → duplicate. The
  pack path is untouched.
- `backend/emails.py`: `unit_purchase_confirmation` — « Vos N documents ScanID sont disponibles » / « Votre document
  ScanID est disponible », body « Merci pour votre achat à la carte : N documents ont été ajoutés … ils sont valables
  jusqu'au … » (singular forms for 1); the pack e-mail unchanged. `backend/main.py` webhook: `pack == UNIT_PACK` →
  that e-mail and log « N documents à la carte crédités »; otherwise exactly as before (docstring updated).
- `backend/.env.example`: `# STRIPE_UNIT_PAYMENT_LINK_ID=` and `# STRIPE_API_KEY=` with their explanation (commented
  out: unset = the feature stays off).
- `frontend/src/billing.js`: `UNIT_PACK`, `purchaseLabel` (« Pack 1 000 » / « À la carte · 37 documents » / « … · 1
  document »); `App.jsx` `MyPurchases` uses it (one cell, one import).
- **Tests.** New `backend/tests/test_unit_purchase.py` (**29**): credited once to the checkout e-mail's account
  (other letter case), purchase row, expiry, e-mail, 2 replays → duplicate with no second Stripe read; **66
  documents = 66 credits, not Pack 100** (same amounts 9 900 / 11 880 and a `client_reference_id`); the
  `client_reference_id` wins over the e-mail; singular e-mail; a pending trial account is credited; bank transfer
  (unpaid → not_paid without reading Stripe → async_payment_succeeded → credited); `/users/me/purchases` shows
  pack 0 / 37 / 5 550; race → duplicate; 11 « unmatched » cases (unknown e-mail, no e-mail, unknown reference, two
  accounts for the address, refused account, USD, API 401, 2 items, 0 items, quantity 0, quantity not an int) →
  200, nothing credited, no purchase, one anomaly e-mail naming the reason and the session; no key → no request,
  « STRIPE_API_KEY » in the e-mail; link not configured → the old behaviour (unmatched without reference; a pack via
  the app still credited by amount, no Stripe read); a pack link never reads line items and keeps the pack e-mail;
  `fetch_line_items` against a local HTTP stand-in for api.stripe.com (path `/v1/checkout/sessions/cs_test_x%2F1/
  line_items?limit=100`, `Bearer` key; 401 / 500 / not JSON / no `data` / unreachable → `StripeApiError`); webhook
  end to end through that stand-in → 250 credited. Mutation (scratch copy, one file back to `HEAD` at a time):
  billing → collection error, main → 2 failed, emails → 9 failed, config → 29 failed; only the dispatch line
  removed → **21 failed** (the 66-documents test among them); control 29 passed.
  `src/billing.test.js` + 1 test (labels); `tests/e2e/account.spec.js` + « « Mes achats » nomme un achat à la carte
  par ses documents » (3 rows: 37 documents, 1 document, Pack 1 000).
- Results: backend **357 passed** (328 + 29); unit **89 passed** (88 + 1); `account.spec.js` desktop + mobile-375
  **10 passed**; eslint `src/App.jsx` = the 12 baseline problems (7 no-unused-vars, 5 exhaustive-deps), every other
  touched file clean.

### F.5 Stage F5 — verification: sub-steps and the harness (tick each one as it completes)

- [x] **F5.1** Full e2e, from `frontend/`: `npx playwright test --reporter=line` (all projects; the `pwa` project runs
      `npm run build` itself). Expected **442 passed, 1 skipped** (439 + 1 before task F, + the new account test on
      desktop, mobile-small, mobile-375). **Done 2026-10-02: 442 passed, 1 skipped (4.2 min, exit 0)**; ports 5173 /
      4173 free afterwards.
- [x] **F5.2** The `pwa` project rebuilt `dist/` with `.env.local`'s API URL → rebuild it as the deploy does:
      `VITE_API_URL=/api npm run build`; build guard `node --test tests/build/no-google-fonts.test.js` 5/5; `dist/` root
      == the folder byte for byte + `sw.js` (as in F2). **Done: 64 files, 0 rewrites, no `/fonts/`; guard 5/5; root ==
      folder (63) + `sw.js`; the app bundle carries `/api`, no localhost URL.**
- [x] **F5.3** (**done: phase A 21/21 checks** — 22 pages × desktop 1280 + phone 375 all clean, menus 22/22 at both
      widths; slider « 1 Pack 1 000 + 2 Packs 100 » → Home « 10 documents à la carte » → End « Un volume sur mesure »;
      packs → `buy.stripe.com/8x27…01` (tarifs, 1000) and `…/9B64…00` (home, 100); essai POST body = exactly the 9
      fields, API 503 → one Formspree POST, subject `Demande d’essai · 20 documents offerts`, confirmation
      « Merci. Votre demande est bien enregistrée : vous recevez vos accès par e-mail à … », the only console line =
      the 503; contact / callback (`moment: L’après-midi`) / checklist subjects exact, the new PDF served; `/app/` login;
      `/cette-page-n-existe-pas` and `/dossier/sous-dossier/page.html` → 404, styled; 3 redirects 301. Screenshots
      looked at. NB the site writes French typographic spaces — `20 documents`, `enregistrée :` — the
      script's expected strings had to use them; not a site defect.)
      Real stack, phase **A = production today** (`/api/config` → `{"signup":false,"trial":false}`): every one of
      the 22 pages at 1280 px and 375 px — no console error, no CSP violation, no failed request, Mona Sans loaded, no
      horizontal overflow; menu button opens / Escape closes the big menu; tarifs slider changes the answer;
      « Choisir ce pack » (tarifs + home) → the Stripe link (intercepted); essai: 3 steps → `POST /api/trial-requests`
      answers 503 → Formspree fallback (intercepted) with subject « Demande d'essai · 20 documents offerts » and the
      confirmation « …vous recevez vos accès par e-mail… »; contact message, callback (`#rappel`, « Le matin » /
      « L'après-midi ») and checklist → Formspree subjects « Message depuis scanid.fr », « Demande de rappel ·
      démonstration », « Téléchargement checklist RGPD »; `/app/` login page; a wrong URL → the new 404 (status 404);
      `/temoignages.html`, `/iftm/` → 301; screenshots.
- [x] **F5.4** (**done: phase B 26/26 checks**, on a fresh database — the 21 checks of A again with `signup`/`trial`
      true, plus: packs → `/app/inscription?pack=1000` (« Pack 1 000 », 828,00 €) and `?pack=100` (118,80 €); essai →
      **201**, no Formspree call, confirmation « Dès sa validation, vous recevez à … le lien pour choisir votre mot de
      passe, avec vos 20 documents offerts… », no console error; admin « Demandes d'essai » lists « Agence Essai B »;
      outbox: `trial_notification` → contact@scanid.fr « Demande d'essai — Agence Essai B »; customer self-registered
      (5 credits) → signed à la carte session (no `client_reference_id`, e-mail `Marc.Unite@Agence-Test.fr`) through
      nginx → `credited`, replay → `duplicate`; the stand-in saw exactly one read
      `/v1/checkout/sessions/cs_local_unite_1/line_items?limit=100` with the key; login → « Crédits : 42 »; « Mes
      achats » = « À la carte · 37 documents · 02/10/2026 · 02/10/2027 » (shown uppercase, like every table cell);
      `purchase_confirmation` → the customer « Vos 37 documents ScanID sont disponibles ». A first B run had stopped on a
      script mistake (the customer's login reused the admin's browser context → no login form; `innerText` returns
      the CSS-uppercased label) — script fixed (own context per user, `textContent`), database reset, full rerun.)
      Phase **B = both switches on** + à la carte configured: packs → `/app/inscription?pack=1000` (the app's
      summary); essai → 201, confirmation « Dès sa validation… le lien pour choisir votre mot de passe… », the request in
      admin « Demandes d'essai », the notification e-mail in the outbox; a signed à la carte `checkout.session.completed`
      (payment_link `plink_local_unite`, no `client_reference_id`, the customer's e-mail) posted **through nginx** →
      the stand-in for api.stripe.com read with the key → `credited` → the customer logs in: credits + 37, « Mon
      Compte » → « Mes achats » « À la carte · 37 documents »; e-mail « Vos 37 documents ScanID sont disponibles ».
- [x] **F5.5** Stop everything (backend, stand-in, nginx container, PostgreSQL); ports 8001 / 8081 / 8443 / 12111 /
      55433 free; `git status --short` == §F.0's list; scratchpad screenshots looked at. **Done:** container removed,
      no harness process, all five ports free; `git status --short` == §F.0 (18 M + 2 ??); `git add --dry-run .` = **82
      paths** (the folder's 63 files + 19), nothing staged; no file of the folder is gitignored (`git check-ignore`
      empty — the checklist PDF, the specimen JPG and the og images all ship); folder scan: no file > 1 MB, no
      credential pattern, no EXIF/GPS in the images.

**The harness** — in the session scratchpad (`<scratchpad>/stack/` and `<scratchpad>/nginx/`), which a new session does
NOT have: rebuild it from this description.
1. `nginx/`: `certs/{fullchain,privkey}.pem` = `openssl req -x509 -newkey rsa:2048 -nodes -days 3 -subj "/CN=scanid.fr"
   -addext "subjectAltName=DNS:scanid.fr,DNS:www.scanid.fr"` (chmod 644); `make_conf.sh <vhost> <out> <http> <https>` =
   `sed` the real vhost: `listen 80 default_server;` → `listen <http> …`, `listen 443 ssl http2 default_server;` →
   `listen <https> …`, delete the two `listen [::]:…` lines; `new/default.conf` from `deploy/nginx-travelapp.conf` on
   8081 / 8443. Container: `docker run -d --name scanid-nginx-new --network host -v <nginx>/new:/etc/nginx/conf.d:ro
   -v <repo>/ops:/opt/travelapp/ops:ro -v <repo>/frontend/dist:/opt/travelapp/frontend-dist:ro -v <nginx>/certs:
   /etc/letsencrypt/live/scanid.fr:ro nginx:1.27-alpine` (local image; `--network host` so the vhost's
   `127.0.0.1:8001` is the backend below). `probe.sh <https> <http>` (F3) prints the headers per path.
2. `stack/start_pg.sh`: `PATH=/usr/lib/postgresql/16/bin:$PATH`; `initdb -D stack/pgdata -U scanid_admin --auth=trust
   -E UTF8`; `pg_ctl -o "-p 55433 -c unix_socket_directories='' -c listen_addresses=127.0.0.1" -w start`;
   `CREATE DATABASE travelapp`.
3. `stack/fake_stripe.py 12111`: `ThreadingHTTPServer` on 127.0.0.1; `GET /v1/checkout/sessions/<id>/line_items` with
   `Authorization: Bearer rk_local_checkout_read` → `{"object":"list","has_more":false,"data":[{"quantity":<q>,…}]}`
   where `<q>` = `stack/quantities.json[<id>]`, else 404; every request appended to `stack/stripe-requests.jsonl`
   (path + whether the key matched).
4. `stack/run_backend.py` (run from `backend/`): `import billing; billing.STRIPE_API_BASE = os.environ["FAKE_STRIPE_BASE"]`,
   then `uvicorn.run("main:app", host="127.0.0.1", port=8001)`. `stack/backend.sh A|B` sets (every variable explicit —
   `backend/.env` supplies SECRET_KEY, ADMIN_PASSWORD, GCP_CREDS_JSON, DATABASE_URL otherwise, and `load_dotenv` never
   overrides a set variable): `DATABASE_URL=postgresql+psycopg2://scanid_admin@127.0.0.1:55433/travelapp
   ENVIRONMENT=production ADMIN_PASSWORD='Girafe!!12Nuage-Admin' SECRET_KEY=local-e2e-secret-not-production
   GCP_CREDS_JSON= GOOGLE_APPLICATION_CREDENTIALS=/nonexistent/creds.json LOGIN_RATE_LIMIT=30/minute
   FAKE_STRIPE_BASE=http://127.0.0.1:12111 APP_PUBLIC_URL=https://scanid.fr:8443/app/ SITE_PUBLIC_URL=https://scanid.fr:8443/`;
   **A** adds `MAIL_BACKEND=disabled STRIPE_WEBHOOK_SECRET= STRIPE_UNIT_PAYMENT_LINK_ID= STRIPE_API_KEY=`; **B** adds
   `MAIL_BACKEND=outbox MAIL_OUTBOX_DIR=stack/mail STRIPE_WEBHOOK_SECRET=whsec_local
   STRIPE_UNIT_PAYMENT_LINK_ID=plink_local_unite STRIPE_API_KEY=rk_local_checkout_read`. No Vision credentials → no
   document ever leaves the machine (no OCR is needed here).
5. `stack/site_check.cjs <A|B> <outDir>`: Chromium from `frontend/node_modules/@playwright/test`, launched with
   `--host-resolver-rules=MAP scanid.fr 127.0.0.1`, `ignoreHTTPSErrors`, base `https://scanid.fr:8443`; routes
   `https://formspree.io/**` → 200 `{"ok":true}` (payload recorded) and `https://buy.stripe.com/**` → a stub page;
   a `securitypolicyviolation` listener added by `addInitScript`; console errors, page errors, failed requests and
   responses ≥ 400 collected per page; the checks of F5.3 / F5.4; `result.json` + screenshots in `<outDir>`. Phase B's
   webhook is signed like Stripe (`t=<unix>,v1=HMAC-SHA256(whsec_local, "<t>.<body>")`) and posted to
   `https://scanid.fr:8443/api/stripe/webhook`; the customer is created by the admin through the API.
6. **Stopping:** `docker rm -f scanid-nginx-new`; find the pids with a pattern that cannot match its own command
   line — `ps -eo pid,args | grep -E "run_backen[d]|fake_strip[e]"` — then `kill <pid>`. **Never** `pgrep -f` /
   `pkill -f` with the plain name in a command line that contains it: it matches (and kills) your own shell — exit
   144, happened once in F5 (harmless: it only cost the backend restart). `PATH=/usr/lib/postgresql/16/bin:$PATH
   pg_ctl -D stack/pgdata -m fast -w stop`.

### F.6 Stage F6 — how to ship task F — DONE

**What ships** (nothing committed, §0.3): the 20 entries of §F.0 — `git add --dry-run .` = **82 paths** (63 files of
`frontend/ScanID-nouveau-site-2026-09-30/nouveau-site/` + 19). No new dependency (Python or npm), no database
migration (an « à la carte » purchase is a `purchases` row with `pack = 0`), no `.env` change required: the site works
as is, and « à la carte » stays off until its two variables exist (below).

**The user ships it** (one command per message if guided, as in §D.7):
1. **Back up the web root (PDF §3.1)**, on the VPS, before the push — reads the web root, writes only in the home
   folder: `ssh lasha@87.106.22.235`, then `tar czf ~/frontend-dist-2026-10-02.tgz -C /opt/travelapp frontend-dist
   && ls -lh ~/frontend-dist-2026-10-02.tgz`. (The usual rollback stays `git revert` + push, which rebuilds v5 from
   the repository; the tarball is the PDF's copy of exactly what was live.)
2. **Laptop:** `git status --short` (= §F.0) → `git add --dry-run . | wc -l` (= 82) → `git add .` →
   `git commit -m "Site: Alex's new website (2026-09-30), nginx cache and redirects, « à la carte » credits on the Stripe webhook"`
   → `git push origin master`.
3. **GitHub:** « CI » green; « Deploy » green — its probes: `/` carries `href="/app/"`, `/app/` is the shell,
   **`/assets/css/site.css` → 200** (was `/fonts/site.css`), an unknown path → 404; « NOTE: nginx not reloaded … » is
   expected (deploy account). The rsync now forces files 644 / folders 755 and, with `--delete`, removes what the new
   site no longer has: temoignages.html, iftm/, og-image.png, scanid-presentation.mp4, fonts/, scripts/ (PDF §3.4;
   `.htaccess` was never shipped).
4. **VPS — reload nginx** (the vhost changed: cache headers + the 301s): `sudo nginx -t && sudo systemctl reload nginx`,
   then `bash /opt/travelapp/ops/verify-front-end.sh` → « ALL CHECKS PASSED ».
5. **Laptop checks** (public GETs — the assistant may run them):
   ```bash
   curl -s https://scanid.fr/ | grep -c 'assets/css/site.css'                         # ≥ 1: the new home page
   curl -sI https://scanid.fr/tarifs.html | grep -i -E '^(HTTP|cache-control)'         # 200 + no-cache (after step 4)
   curl -sI 'https://scanid.fr/assets/css/site.css?v=202609302115' | grep -i cache-control   # max-age=31536000
   curl -sI https://scanid.fr/temoignages.html | grep -i -E '^(HTTP|location)'         # 301 → /presentation.html
   curl -sI https://scanid.fr/iftm/ | grep -i -E '^(HTTP|location)'                   # 301 → /essai.html
   curl -s -o /dev/null -w '%{http_code}\n' https://scanid.fr/une-page-qui-n-existe-pas   # 404 (the new 404 page)
   curl -s https://scanid.fr/sitemap.xml | grep -c '<url>'                            # 21
   curl -s https://scanid.fr/api/config                                               # unchanged: {"signup":false,"trial":false}
   curl -s https://scanid.fr/app/ | grep -o '/app/assets/index-[^"]*\.js'              # a new bundle (App.jsx changed)
   ```
6. **Alex's ten-minute check (PDF §6)** — what to expect on today's production: item 2 « Choisir ce pack » → Stripe
   (`signup` false until `STRIPE_WEBHOOK_SECRET` is set, §C.5.2); **item 3: the essai request arrives by Formspree
   e-mail at contact@scanid.fr, NOT in « Demandes d'essai »** — it can appear there only once SMTP is configured
   (`trial` true, §C.5.1); this is the designed fallback, not a defect (§F.2.6). Item 6 (Search Console) is Alex's /
   the user's. Everything else was verified locally in F5 (21/21).
7. Then mark §F.0 **SHIPPED** (commit hash, date) and turn §F into a record.

**« À la carte » — switching it on later** (needs Alex; the webhook secret of §C.5.2 must already be in place, or the
webhook answers 503 and nothing is credited automatically, packs included): **SUPERSEDED by task K (2026-10-06) —
use §K.5. Item d is done (K2); e's « an e-mail without an account → nothing credited » is no longer true: the purchase
opens the account (§K.3.2).**
- a. Alex creates the Payment Link (1,50 € HT, the same VAT handling as the packs, « adjustable quantity » on, 1 unit
  = 1 document) and sends its URL (`https://buy.stripe.com/…`) **and its id** (`plink_…`, on the link's page). No
  webhook change: the endpoint already receives every Checkout Session of the account.
- b. Alex creates a **restricted key** (Developers → API keys → « Create restricted key »: Checkout Sessions = Read,
  everything else None) and puts it on the server himself — never by chat, like the webhook secret.
- c. Server, `/opt/travelapp/backend/.env`: `STRIPE_UNIT_PAYMENT_LINK_ID=plink_…` and `STRIPE_API_KEY=rk_live_…`, then
  `sudo systemctl restart travelapp.service`.
- d. Site (PDF §5): in `frontend/ScanID-nouveau-site-2026-09-30/nouveau-site/tarifs.html`, the link with
  `data-pack="unite"`: `href="essai.html"` → the link URL, « Commencer par l’essai » → « Acheter à l’unité » — an
  edit of the read-only source, so it needs the user's explicit demand at that time (or Alex regenerates the page);
  then commit + push.
- e. Acceptance: buy 1 document with an e-mail that has a ScanID account → credits + 1, « Mes achats » « À la carte · 1
  document », e-mail « Votre document ScanID est disponible »; an e-mail without an account → nothing credited, Alex
  gets « Paiement Stripe à rattacher manuellement » with the reason. Until c is done, an à la carte payment is never
  lost: it lands in that same anomaly e-mail.

**Reported, not done (not demanded):** the export headers' casing differs from the site's sample (F.2.7);
`scanid-site-v5-deploy/` is no longer read (deleting it = a separate demand); the app's « Tarifs » link still points
at `https://scanid.fr/#tarifs` (that section exists on the new home page; `tarifs.html` is the new dedicated page);
README / ops docs still describe `frontend/site/`; measured on the live server (2026-10-02, `Accept-Encoding: gzip`):
HTML is gzipped, CSS is not (the server's `gzip_types` does not list it) — the new `site.css` (113 KB) and the scripts
will travel uncompressed, a possible later improvement; the Vision quota note of §D.6 still stands.

---

## E. TASK E (2026-10-02) — WEBSITE: THREE REMOVALS — COMMITTED `bf7dc3c`, PUSHED — RECORD ONLY

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
- [x] 6 VPS (2026-10-03): no startup error; column present; `F | 2` (both documents read F from the MRZ). The
      « Schéma mis à jour » line is missing because the app's INFO logs were never recorded (a logging bug since
      2026-08-05, §I.0.1 item 6 notes) — not a failure of the migration
- [~] 7 acceptance: « Sexe » in the list and the XLSX confirmed by Alex (« after go-live » note, 02/10); production
      data shows F read from the MRZ; CSV / phone card / « Modifier » not separately checked (optional)
- [x] 5 « CI » ✅ and « Deploy » ✅ for `cfbcd58` (both 2026-10-02 ≈ 09:40 UTC) — read from the GitHub API by the
      assistant on 2026-10-03 (the repository is public)
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

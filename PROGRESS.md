# ScanID — deployment progress and route to go-live

**Last updated: 2026-09-08.** Written to be read cold: a fresh session (human or
AI) should be able to read this file and know exactly what state the production
system is in, what has been proven rather than assumed, and what still stands
between here and selling the service to clients under French law.

Companion documents:
- `SCANID-HUMAN-ONLY.md` — the original checklist this work follows
- `SCANID-HANDOVER.md` — project handover notes
- `ops/README.md` — operational scripts

---

## 0. Read this first

Three things a newcomer gets wrong about this deployment:

1. **CloudPanel is not installed.** `SCANID-HUMAN-ONLY.md` assumes the CloudPanel
   software throughout. It is not on this server. `cloudpanel.ionos.fr` is
   IONOS's own management website, a different thing entirely. Nothing listens
   on 8443. Every CloudPanel item in that checklist is void: 2FA, restricting
   8443, "CloudPanel may inject a duplicate CSP", "keep CloudPanel current".
   Certificates come from certbot.

2. **The scheduled backup does not run from `/opt/travelapp/ops/`.** It runs from
   `/usr/local/sbin/`, installed by hand, `0700 root:root`. `/opt/travelapp/ops/`
   is an rsync target owned by the `deploy` account, whose private key is a
   GitHub Actions secret — a root cron job reading its script from there would
   turn that key into root access. **A deploy does not update the scheduled
   copies.** Re-run the install lines in §5 when `ops/*.sh` changes.

3. **The certificate was issued with `certonly --webroot`, never the nginx
   plugin.** `certbot --nginx` rewrites `deploy/nginx-travelapp.conf` in place,
   and the deploy's `rsync --delete` over `deploy/` erases that on the next push.
   HTTPS would die silently at the following deploy.

---

## 1. The system as it stands

| | |
|---|---|
| Host | IONOS Core VPS "My VPS", `87.106.22.235`, VPS 2-2-90 |
| OS | Ubuntu 24.04.4 LTS, kernel 6.8.0-139 |
| Location | **France.** RIPE: `country: FR`, netname `fr-nbz-ionos-cloud-nbz`, route `IONOS-PA-5` (Paris). *Not yet confirmed in writing by IONOS — see §4.1* |
| IPv6 | **None.** No global address, no default route, no egress. AAAA records were removed for this reason |
| Domain | `scanid.fr` and `www.scanid.fr` → `87.106.22.235` |
| Public URL | `https://scanid.fr` (this is the answer to Part 3 Q5) |
| Mail | scanid.fr has live IONOS mail — MX `mx00/mx01.ionos.fr`, SPF, DKIM, DMARC. **Do not touch those DNS records** |
| Web stack | nginx 1.24 → uvicorn on `127.0.0.1:8001`, PostgreSQL 16.15 on `127.0.0.1:5432` |
| Deploy | GitHub Actions on push to `master`, as user `deploy` |

### Accounts

| Account | Access | Notes |
|---|---|---|
| `root` | SSH key only | `PermitRootLogin yes` — still to be changed, see §4.3 |
| `lasha` (uid 1001) | SSH key + sudo password | Non-root admin account. Password is for `sudo` only |
| `deploy` (uid 1000) | SSH key, GitHub Actions | sudo limited to `systemctl restart travelapp.service`. **Cannot reload nginx** — deploys sync the vhost but never reload it |

---

## 2. Done and verified

Everything below was checked against the running system, not assumed. Where a
claim is only inferred, it says so.

### 2.1 Application hardening

- **`ENVIRONMENT=production`** in `/opt/travelapp/backend/.env`.
  Before this, `/api/docs`, `/api/openapi.json` and `/api/redoc` all returned
  **200 to the public internet**. Now 404, verified externally.
- **`CORS_ORIGINS=https://scanid.fr,https://www.scanid.fr,http://87.106.22.235`**
- ⚠️ **`SESSION_COOKIE_SECURE=0` is set and is a TEMPORARY workaround.** It was
  needed because `ENVIRONMENT=production` sets the session cookie to `Secure`,
  which breaks login over plain HTTP. HTTPS now works, so **this line should be
  removed** — see §4.2.

### 2.2 TLS and the domain

- DNS A records repointed from the old IONOS webspace (`217.160.0.115`) to the
  VPS. AAAA records **deleted** — they pointed at the dead webspace and, with no
  IPv6 on the VPS, would have sent IPv6 clients to a `403` with no fallback and
  broken ACME validation.
- Certificate for `scanid.fr` + `www.scanid.fr`, expires **2026-12-07**.
  `certbot.timer` enabled — renewal is scheduled.
- `deploy/nginx-travelapp.conf` rewritten:
  - port 80 serves `/.well-known/acme-challenge/` and 301s everything else to
    `https://scanid.fr` (fixed name, so bare-IP requests land on a name the
    certificate covers)
  - port 443 serves the app, TLS 1.2/1.3, ECDHE ciphers only
  - no DHE (needs an `ssl_dhparam` nginx no longer ships) and no OCSP stapling
    (Let's Encrypt retired its responder)
  - `server_tokens off` in both blocks
- **Security headers verified present exactly once each**: `X-Content-Type-Options`,
  `X-Frame-Options`, `Referrer-Policy`, `Content-Security-Policy`.
- The deploy's own health check had to move to HTTPS. It probed
  `http://127.0.0.1/api/destinations/` expecting 401; port 80 now returns 301,
  which would have failed every deploy. It now uses
  `--resolve scanid.fr:443:127.0.0.1`.

### 2.3 SSH, firewall, patching

- **`PasswordAuthentication no`**, via `/etc/ssh/sshd_config.d/01-hardening.conf`.
  The filename matters: `50-cloud-init.conf` sets `PasswordAuthentication yes`,
  and **sshd honours the first occurrence**, so a `99-*.conf` would have done
  nothing. Also `KbdInteractiveAuthentication no`, `MaxAuthTries 3`.
  Context: there had been **81,634 failed password attempts in 14 days**
  (48,681 against `root`), top source `87.106.134.4` with 21,246.
- **fail2ban** active, `sshd` jail, `/etc/fail2ban/jail.local`,
  `ignoreip` includes `212.58.120.147` (the operator's IP) so self-lockout is
  impossible. Banned 8 IPs within minutes of starting.
- **`lasha`** created — sudo group, SSH key, sudo password set.
- **ufw** active: 22, 80, 443 only. Verified from outside that 5432, 8001, 8443,
  3306 and 25 are all filtered.
- Kernel upgraded 6.8.0-137 → **6.8.0-139**, 29 packages, rebooted. Every
  service came back unaided; `unattended-upgrades` was already enabled.

### 2.4 Database

Already correct before this work, verified not changed:

- PostgreSQL bound to `127.0.0.1` only; `pg_hba` requires `scram-sha-256` over
  TCP, `peer` locally, no `trust` anywhere
- App connects as role **`travelapp`** — no attributes at all: not superuser, no
  CREATEDB, CREATEROLE, REPLICATION or BYPASSRLS. 48-character SCRAM password
- Role **`postgres` has NO PASSWORD** — the superuser cannot connect over TCP
- Extra role **`scanid_restore`** exists (LOGIN, CREATEDB, not superuser),
  used only by the restore test. Credentials in `/etc/scanid/restore.env`

### 2.5 Backups — the most thoroughly proven part

Encryption model: the VPS holds only the **age public key**. The private key is
on the operator's laptop at `~/scanid-keys/scanid-backup.key` and in their
password manager. **It must never be on the server.**

Public key (safe to share):
`age1dm9gssz2ftfnr7r5p47zx7ckxqrah5dlgx5fwxpkfnv47etwucaq9lrjzc`

> An earlier key was generated *on the server* by mistake and was destroyed and
> replaced rather than moved — `shred` on a virtual disk is not a guarantee.

| Component | Location |
|---|---|
| Backup script | `/usr/local/sbin/scanid-backup.sh` (0700 root) |
| Restore test | `/usr/local/sbin/scanid-restore-test.sh` (0700 root) |
| Undelete tool | `/usr/local/sbin/scanid-s3-undelete.py` (0700 root) |
| Config | `/etc/scanid/backup.env`, `/etc/scanid/restore.env`, `/etc/scanid/rclone.conf` (all 0600 root) |
| Local copies | `/var/backups/scanid/`, 14-day retention |
| Schedule | `scanid-backup.timer`, `OnCalendar=03:17`, `Persistent=true` |
| Off-site | IONOS Object Storage, bucket `scanid-backups-de`, region `eu-central-4` (**Frankfurt, Germany**), endpoint `s3.eu-central-4.ionoscloud.com` |
| Object Lock | **COMPLIANCE mode, 30 days** |

Proven end to end on real production data:

- dump is genuinely encrypted — `age encrypted file, X25519 recipient`
- **restores to identical data**: `users=1 passports=42 ocr_jobs=2 voyages=0`,
  matching production exactly, sha256 of the file read identical to the one written
- runs unattended under systemd (not just by hand — see the trap in §6)
- uploads off-site and the script **verifies the object size on the remote**
  rather than trusting rclone's exit code
- survives deletion by a compromised server, and can be recovered

**Precise wording for the DPA — do not overstate this:** an attacker holding the
server's credentials **can hide** the backups by writing S3 delete markers, and
**cannot destroy** them. Verified: after `rclone delete`, `rclone ls` showed an
empty bucket while `ListObjectVersions` showed the 13,871-byte version intact
with `IsLatest=false` beneath a delete marker. Recovery is
`scanid-s3-undelete.py --remove`, which was run and worked.

### 2.6 Commits made

| Commit | What |
|---|---|
| `a6e1f98` | HTTPS vhost + deploy health check moved to HTTPS |
| `c70b3fd` | `backup.sh`: survive an unset `HOME` (see §6) |
| `250ce03` | Off-site backups to IONOS Object Storage + `ops/s3-undelete.py` |

`ops/tests/run-ops-tests.sh`: **94 passed, 0 failed** after these changes.
CI does not run that suite — run it by hand after touching `ops/`.

---

## 3. Not done — engineering

### 3.1 Deletion verification — CRITICAL, ~10 minutes

`SCANID-HUMAN-ONLY.md` §1.2. Nobody has confirmed that the app's delete function
actually removes rows from PostgreSQL rather than hiding them from the UI. Until
it is checked with a direct SQL query, every statement to a client about erasure
is unverified.

Method: create a test record, delete it through the UI, then query the database
directly — not through the API. Check derived artefacts too (`ocr_jobs`).

### 3.2 Retention of results — CRITICAL, needs a decision then code

**There is currently no retention period and no enforcement.** The database holds
42 real passport records with no expiry. GDPR Art. 5(1)(e) forbids keeping
personal data longer than necessary; indefinite retention is a live
non-compliance, not a future risk.

Required: decide the period, state it, and **enforce it in code** (a scheduled
purge). Note "documents are never stored" concerns *images*; extracted MRZ
results are personal data with their own retention obligation.

### 3.3 Remove the temporary cookie override — 2 minutes

Delete `SESSION_COOKIE_SECURE=0` from `/opt/travelapp/backend/.env` and restart
`travelapp.service`. It was only needed while the site was HTTP-only. With it in
place the session cookie is **not** marked `Secure`, which is weaker than the
code intends (`backend/config.py`, `cookie_secure()`).

Verify afterwards that login still works over `https://scanid.fr`.

### 3.4 iOS Safari storage after a full session — CRITICAL, needs an iPhone

Part 2 of the checklist, which marks it un-waivable. Run a complete session on a
real iPhone, then inspect storage remotely. Nothing document-related may remain.
This is the evidence behind the central commercial claim; Playwright's WebKit
does not reproduce Safari's storage behaviour.

### 3.5 HSTS — around 15 September

Uncomment the `Strict-Transport-Security` line in
`ops/nginx-security-headers.conf` (line ~47). Start with a short `max-age`, raise
it after a week. Only after HTTPS has been stable — browsers cache it and you
cannot take it back.

### 3.6 `PermitRootLogin no` — low value, do it last

Gate: prove `lasha` can `ssh` in **and** run `sudo` from a second session first.
Honest assessment: with `PasswordAuthentication no` already enforced, an attacker
must already hold a private key, at which point they have `lasha` and sudo too.
This is tidiness and defence in depth, not a real reduction in attack surface.
Do not delay anything else for it.

### 3.7 Review auth and fail2ban logs — around 15 September

`journalctl -u ssh`, `fail2ban-client status sshd`. Nothing depends on it.

### 3.8 Cosmetic, but client-facing

The page `<title>` is still `Vite + React`.

---

## 4. Not done — legal. This is the real gap.

The server is in good shape. If you went live tomorrow the risk would not be a
compromised VPS; it would be processing identity documents without a lawful
basis, a register, a notice, or a signed processor contract.

**Nobody here is a lawyer.** Everything below needs review by a French-qualified
DPO or privacy counsel before it is relied on.

### 4.1 Facts already established, reusable in the documents

- **Hosting**: IONOS SE, VPS in France (Paris region) — RIPE evidence in §1.
  **Open action: get this in writing from IONOS support**, naming the datacentre.
  RIPE's `country:` is a registrant declaration, not a certification.
- **Backups**: IONOS Object Storage, Frankfurt, **Germany**. Intra-EU, so no
  Chapter V transfer mechanism is needed. The bucket is named `-de` deliberately
  so nobody later writes "backups in France" into a signed document.
- **OCR**: Google Cloud Vision, pinned to the EU endpoint
  `eu-vision.googleapis.com` — `backend/config.py` (`VISION_API_ENDPOINT`) and
  `backend/ocr_service.py` (`client_options`), enforced by
  `backend/tests/test_vision_residency.py`. Images are sent as **inline bytes**,
  never via a GCS bucket. Note: **EU ≠ France**; Vision has no French region.
- **EU-US Data Privacy Framework status (checked 2026-09-08)**: the adequacy
  decision stands; the General Court dismissed the Latombe challenge on
  2025-09-03; an appeal is pending at the CJEU (C-703/25 P); on 2026-07-31 the
  EDPB Chair asked the Commission to reassess FTC independence after
  *Trump v. Slaughter*. Usable, but unstable — have SCCs as a fallback rather
  than relying on DPF alone. **Re-check before signing anything.**
- **Encryption at rest**: IONOS documents AES-XTS-256 with per-volume keys for
  **IONOS Cloud Block Storage**. It is **not confirmed** that this covers a Core
  VPS. Ask IONOS in writing. Do not write "the VPS is encrypted" without knowing
  what that covers.

### 4.2 Missing entirely — required by law

| # | Item | Basis |
|---|---|---|
| 1 | **Legal basis for the processing** | Art. 6. Never established. For hotels the *fiche individuelle de police* (CESEDA R.611-42) is a legal obligation; for a travel agency it is more likely contract. **Everything else depends on this** |
| 2 | **Art. 28 processor contract** with each client | Without it the processing is unlawful for both parties. The agency is controller, ScanID is processor — state that explicitly |
| 3 | **Register of processing activities** | Art. 30 |
| 4 | **Information notice / politique de confidentialité** in the app | Art. 13 |
| 5 | **Sub-processor disclosure and authorisation** | Art. 28(2). At minimum **Google** (Vision, image processing) and **IONOS** (hosting + object storage). For each: entity, what it processes, where, transfer basis |
| 6 | **Retention policy for results** | Art. 5(1)(e). See §3.2 — this is both a document and a code change |
| 7 | **Data subject rights process** | How the *traveller*, not the agency, exercises access and erasure, and who they contact |
| 8 | **Breach notification procedure** | Art. 33 — 72 hours to CNIL. Who detects, who decides, who writes |
| 9 | **DPIA / AIPD** | Art. 35. Identity documents at scale. Check the current CNIL list of processing requiring one. If it applies it must be complete **before** go-live |
| 10 | **Mentions légales** on the site | LCEN — publisher identity, SIREN, host name and address, publication director |
| 11 | **What Google Vision retains on their side** | The checklist calls this the most commonly missed item, and it is right. "We do not store documents" is false if your processor does. Check current Google Cloud terms, not memory |
| 12 | **DPA answers 1–6** | `SCANID-HUMAN-ONLY.md` Part 3. Most inputs are in §2 and §4.1 above |

### 4.3 A note on "must be in France"

GDPR does **not** require personal data to stay in France. Art. 1(3) forbids
Member States restricting free movement of personal data within the Union; only
transfers *outside* the EEA are restricted. Germany and Spain are legally
identical to France here.

"Must be in France" is a **commercial or contractual** requirement, not a
statutory one — unless a client contract or a certification (SecNumCloud, HDS,
public-sector doctrine) imposes it. Confirm with whoever drafts the client
contract. As things stand: **application in France, backups in Germany, OCR in
the EU**.

---

## 5. Runbook — commands that will be needed again

```bash
# Reinstall the scheduled scripts after ops/ changes. A deploy does NOT do this.
scp ops/backup.sh      root@87.106.22.235:/tmp/b.sh
scp ops/s3-undelete.py root@87.106.22.235:/tmp/u.py
ssh root@87.106.22.235 'install -m 0700 -o root -g root /tmp/b.sh /usr/local/sbin/scanid-backup.sh;
                        install -m 0700 -o root -g root /tmp/u.py /usr/local/sbin/scanid-s3-undelete.py;
                        rm -f /tmp/b.sh /tmp/u.py'

# Run a backup now, through systemd (the path that matters)
ssh root@87.106.22.235 'systemctl start scanid-backup.service; journalctl -u scanid-backup -n 3 --no-pager'

# Restore test. The private key goes to /run (tmpfs, RAM only) and is destroyed
# in the same command, so it never touches the server's persistent disk.
ssh root@87.106.22.235 'install -d -m 0700 /run/scanid-restore'
scp ~/scanid-keys/scanid-backup.key root@87.106.22.235:/run/scanid-restore/scanid-backup.key
ssh root@87.106.22.235 'chmod 600 /run/scanid-restore/scanid-backup.key;
  OPS_ENV_FILE=/etc/scanid/restore.env /usr/local/sbin/scanid-restore-test.sh --confirm;
  rc=$?; rm -rf /run/scanid-restore; exit $rc'

# Backups hidden by delete markers? List, then restore.
ssh root@87.106.22.235 '/usr/local/sbin/scanid-s3-undelete.py'
ssh root@87.106.22.235 '/usr/local/sbin/scanid-s3-undelete.py --remove'

# External verification
curl -I https://scanid.fr                    # headers, once each
curl -sI https://scanid.fr/api/docs          # must be 404
ssh root@87.106.22.235 'ufw status verbose; ss -tlnp | grep 5432'
ssh root@87.106.22.235 'certbot certificates; certbot renew --dry-run'
```

---

## 6. Traps already hit — do not rediscover these

| Trap | What happened |
|---|---|
| **`HOME` unset under systemd** | `backup.sh` uses `${HOME%/}` under `set -u`. systemd sets no `HOME` for `Type=oneshot`, so it aborted in preflight — **worked by hand, failed every scheduled run**. The timer looked healthy and produced nothing. Fixed in `c70b3fd`. *Always test a unit with `systemctl start`, never only by hand.* |
| **sshd drop-in ordering** | `50-cloud-init.conf` sets `PasswordAuthentication yes`; sshd honours the **first** occurrence. A `99-*.conf` is silently ignored. Ours is `01-hardening.conf` |
| **sshd needs a reload** | Writing the config is not enough. A resident sshd keeps the old config in memory; new connections still offered `password` until `systemctl reload ssh` |
| **AAAA records** | Pointed at the dead webspace. The VPS has no IPv6, so IPv6 clients would connect *successfully* and get 403 — no Happy Eyeballs fallback, because nothing failed |
| **`certbot --nginx`** | Would rewrite the vhost that `rsync --delete` overwrites on the next deploy |
| **Deploy health check** | Probed port 80 expecting 401; the HTTPS redirect made it 301 and would have failed every deploy |
| **rclone and `$HOME`** | Same trap as `backup.sh`. `RCLONE_CONFIG` is now required and checked in preflight |
| **S3 delete markers** | Object Lock does not stop a DELETE — it stops destroying a *version*. `rclone ls` then shows an empty bucket while the data is intact underneath |
| **rclone 1.60** | Cannot address object versions (`--s3-versions` arrived in 1.62). This is why `ops/s3-undelete.py` exists and uses only the standard library |
| **`deploy` cannot reload nginx** | Its sudoers entry allows only `systemctl restart travelapp.service`. Deploys sync the vhost and print a NOTE; reload manually after vhost changes |

---

## 7. The shortest honest route to clients

1. **Deletion verification** (§3.1) — 10 min. Produces evidence the documents cite
2. **Remove `SESSION_COOKIE_SECURE=0`** (§3.3) — 2 min
3. **Decide and implement retention** (§3.2) — the one remaining engineering task
   with legal weight
4. **iOS storage check** (§3.4) — 30 min with an iPhone
5. **Ask IONOS in writing**: VPS datacentre location, and whether Core VPS
   storage is encrypted at rest (§4.1)
6. **Check what Google Vision retains** (§4.2 item 11)
7. **Establish the legal basis** (§4.2 item 1) — everything else describes it
8. **Write the document set**: register → notice → DPA with sub-processors →
   rights process → breach procedure → mentions légales
9. **DPIA** if CNIL's list applies
10. **Review by whoever drafts the client contract**
11. HSTS and `PermitRootLogin no` (§3.5, §3.6) — after a week of stable HTTPS

Steps 1–4 are hours. Steps 5–10 are the real work, and most of it is not code.

#!/usr/bin/env bash
#
# ScanID — nightly encrypted PostgreSQL backup.
#
# GENERATED FILE. Review every line before you run it. Nothing in here has ever
# been executed against your server.
#
# What it does, in order:
#   1. Refuses to start unless every required variable and command is present.
#   2. Pipes `pg_dump` straight into `age`. The plaintext dump never exists as a
#      file — not in $BACKUP_DIR, not in /tmp. That is the whole point of the
#      pipe, so do not "simplify" it into dump-then-encrypt.
#   3. Copies the encrypted file off the VPS.
#   4. Prunes encrypted files older than the retention period.
#   5. Writes exactly one log line, and exits non-zero if anything failed so a
#      monitor (cron MAILTO, healthchecks.io, systemd OnFailure) can see it.
#
# ENCRYPTION MODEL — read this before generating keys.
#   The VPS holds only the age RECIPIENT (public key). The IDENTITY (private
#   key) must NOT be on the VPS: an attacker who takes the server must not also
#   get the means to read every historical backup. Keep the identity in a
#   password manager and on the machine where you run restore-test.sh.
#
#     age-keygen -o scanid-backup.key      # run this OFF the server
#     # -> "Public key: age1..."  put that in AGE_RECIPIENT on the VPS
#     # -> keep scanid-backup.key somewhere the VPS cannot reach
#
#   Lose the identity and every backup is landfill. There is no recovery path.
#
# SCHEDULING — this script does NOT install itself. Add the line yourself:
#
#   # m h dom mon dow  command
#   17 3 * * *  /opt/travelapp/ops/backup.sh >> /var/log/scanid-backup.log 2>&1
#
#   (03:17 rather than 03:00: every naive cron in the world fires on the hour.)
#   Check afterwards with `crontab -l`. If you would rather use systemd, a timer
#   with OnCalendar=03:17 and OnFailure= a mail unit is strictly better, because
#   cron's failure reporting depends on a working local MTA.
#
# Usage:
#   backup.sh                 normal run
#   backup.sh --dry-run       preflight + report what WOULD be pruned; no dump,
#                             no upload, no deletion
#   backup.sh --no-prune      back up, skip retention pruning
#
set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Everything is read from an env file that YOU create on the server. Nothing is
# hardcoded here and no value below is a real credential.
#
#   sudo install -d -m 0750 -o root -g scanid /etc/scanid
#   sudo install -m 0640 -o root -g scanid /dev/null /etc/scanid/backup.env
#
# Contents (all placeholders — replace every one):
#
#   PGHOST=127.0.0.1                  # the LOCAL instance; never a public IP
#   PGPORT=5432
#   PGUSER=REPLACE_ME_DB_USER
#   PGDATABASE=REPLACE_ME_DB_NAME
#   PGPASSWORD=REPLACE_ME_DB_PASSWORD # or leave unset and use ~/.pgpass (0600)
#   BACKUP_DIR=/var/backups/scanid
#   AGE_RECIPIENT=age1REPLACE_ME_PUBLIC_KEY
#   OFFSITE_DEST=REPLACE_ME           # rsync target, e.g. user@host:/srv/scanid
#                                     # or a mounted path; or the literal "none"
#   BACKUP_RETENTION_DAYS=14
#
OPS_ENV_FILE="${OPS_ENV_FILE:-/etc/scanid/backup.env}"

# Only these two have defaults. Everything else must be set explicitly, so a
# typo in the env file stops the run instead of silently backing up the wrong
# thing to the wrong place.
BACKUP_RETENTION_DAYS_DEFAULT=14
FILE_PREFIX="scanid"

# Every file this script creates is 0600 / every directory 0700. Set before any
# file is opened, because an encrypted dump that is world-readable still leaks
# its size, its existence and its schedule.
umask 077

# ---------------------------------------------------------------------------
# Logging and failure handling
# ---------------------------------------------------------------------------
STARTED_AT_EPOCH=$(date -u +%s)

timestamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }

# One line per run, on stdout, so the cron redirect above is the whole logging
# setup. Machine-parseable key=value; `status=` is first so a monitor can grep
# for `status=error` without a parser.
log_line() {
    local status="$1"; shift
    printf '%s scanid-backup status=%s duration_s=%s %s\n' \
        "$(timestamp)" "$status" "$(( $(date -u +%s) - STARTED_AT_EPOCH ))" "$*"
}

# Set as the run proceeds so the failure line says how far it got.
STAGE="startup"
DUMP_FILE=""
PART_FILE=""

# Set once an error line has been emitted, so a run reports its failure exactly
# once. The contract is one log line per run, and a monitor counting
# `status=error` occurrences should count runs, not stack frames.
ERROR_LOGGED=0

die() {
    ERROR_LOGGED=1
    log_line error "stage=${STAGE} message=\"$*\"" >&2
    exit 1
}

on_exit() {
    local rc=$?
    # A partial encrypted file is worse than no file: it looks like a backup and
    # restores as nothing. Never leave one behind.
    if [[ -n "$PART_FILE" && -e "$PART_FILE" ]]; then
        rm -f -- "$PART_FILE"
    fi
    # Only for a failure that bypassed die() — an unexpected non-zero command
    # caught by `set -e`, which would otherwise exit silently.
    if (( rc != 0 && ! ERROR_LOGGED )) && [[ "$STAGE" != "done" ]]; then
        log_line error "stage=${STAGE} message=\"aborted with exit code ${rc}\"" >&2
    fi
    return "$rc"
}
trap on_exit EXIT

# ---------------------------------------------------------------------------
# Arguments
# ---------------------------------------------------------------------------
DRY_RUN=0
PRUNE=1
while (( $# )); do
    case "$1" in
        --dry-run)  DRY_RUN=1 ;;
        --no-prune) PRUNE=0 ;;
        -h|--help)  sed -n '2,60p' "$0"; exit 0 ;;
        *)          die "unknown argument: $1 (see --help)" ;;
    esac
    shift
done

# ---------------------------------------------------------------------------
# Preflight
# ---------------------------------------------------------------------------
STAGE="preflight"

[[ -r "$OPS_ENV_FILE" ]] || die "env file not readable: ${OPS_ENV_FILE} (set OPS_ENV_FILE to override)"

# The env file is operator-authored configuration, not untrusted input, so
# sourcing it is deliberate. shellcheck cannot follow a runtime path.
set -a
# shellcheck source=/dev/null
source "$OPS_ENV_FILE"
set +a

: "${BACKUP_RETENTION_DAYS:=$BACKUP_RETENTION_DAYS_DEFAULT}"

for var in PGHOST PGPORT PGUSER PGDATABASE BACKUP_DIR AGE_RECIPIENT OFFSITE_DEST; do
    [[ -n "${!var:-}" ]] || die "required variable ${var} is empty or unset in ${OPS_ENV_FILE}"
done

for cmd in pg_dump age find flock; do
    command -v "$cmd" >/dev/null 2>&1 || die "required command not found: ${cmd}"
done
if [[ "$OFFSITE_DEST" != "none" ]]; then
    command -v rsync >/dev/null 2>&1 || die "required command not found: rsync"
fi

# Catch the two mistakes that turn pruning into data loss: a BACKUP_DIR that is
# a system root, and a relative path that resolves against cron's $HOME.
[[ "$BACKUP_DIR" = /* ]] || die "BACKUP_DIR must be an absolute path, got: ${BACKUP_DIR}"
case "${BACKUP_DIR%/}" in
    ""|/root|/home|/etc|/var|/usr|/opt|/srv|/tmp|"${HOME%/}")
        die "refusing to use ${BACKUP_DIR} as BACKUP_DIR: use a dedicated directory such as /var/backups/scanid" ;;
esac
[[ -d "$BACKUP_DIR" ]] || die "BACKUP_DIR does not exist: ${BACKUP_DIR} (create it: install -d -m 0700 ${BACKUP_DIR})"
[[ -w "$BACKUP_DIR" ]] || die "BACKUP_DIR is not writable by $(id -un): ${BACKUP_DIR}"

# An age recipient is "age1..." (X25519) or "ssh-rsa/ssh-ed25519 ..." . Catching
# a pasted PRIVATE key here is the point: AGE-SECRET-KEY-... on the VPS is
# exactly what the encryption model above forbids.
case "$AGE_RECIPIENT" in
    AGE-SECRET-KEY-*) die "AGE_RECIPIENT holds a PRIVATE key. Put the public key (age1...) here; the private key must never be on this server." ;;
    age1*|ssh-rsa\ *|ssh-ed25519\ *) : ;;
    *) die "AGE_RECIPIENT does not look like an age recipient (expected age1... or an ssh public key)" ;;
esac

[[ "$BACKUP_RETENTION_DAYS" =~ ^[0-9]+$ ]] || die "BACKUP_RETENTION_DAYS must be a whole number of days, got: ${BACKUP_RETENTION_DAYS}"
(( BACKUP_RETENTION_DAYS >= 1 )) || die "BACKUP_RETENTION_DAYS must be at least 1, got: ${BACKUP_RETENTION_DAYS}"

export PGHOST PGPORT PGUSER PGDATABASE
# `if`, not `[[ ... ]] && export`: under `set -e` a bare test that returns false
# is a failing command and would abort the run whenever PGPASSWORD is unset —
# which is the normal case when ~/.pgpass is used instead.
if [[ -n "${PGPASSWORD:-}" ]]; then
    export PGPASSWORD
fi

# ---------------------------------------------------------------------------
# Serialise runs
# ---------------------------------------------------------------------------
# Two overlapping dumps produce two half-files and double the load. `flock -n`
# makes the second one exit immediately rather than queue behind the first,
# because a backup that starts an hour late is not a backup you want.
# Held on a file descriptor rather than by re-exec'ing under `flock`: an
# `exec flock ... "$0"` replaces this process, so a lock it fails to take exits
# 1 with no log line at all — the one night you most want a log line.
LOCK_FILE="${BACKUP_DIR}/.backup.lock"
exec 9>"$LOCK_FILE" || die "cannot open lock file ${LOCK_FILE}"
flock -n 9 || die "another backup run already holds ${LOCK_FILE} — skipping this run"

# ---------------------------------------------------------------------------
# Dump + encrypt
# ---------------------------------------------------------------------------
RUN_STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DUMP_FILE="${BACKUP_DIR}/${FILE_PREFIX}-${RUN_STAMP}.dump.age"
PART_FILE="${DUMP_FILE}.part"

if (( DRY_RUN )); then
    log_line dry-run "would_write=${DUMP_FILE} db=${PGDATABASE} host=${PGHOST}:${PGPORT} offsite=${OFFSITE_DEST} retention_days=${BACKUP_RETENTION_DAYS}"
else
    STAGE="dump"
    # -Fc  custom format: compressed, and pg_restore can be selective on it.
    # The pipe is the security boundary. `set -o pipefail` above makes a
    # pg_dump failure fail the whole pipeline instead of yielding a perfectly
    # well-formed encryption of an error-truncated dump.
    pg_dump --format=custom --no-owner --no-privileges \
        | age --recipient "$AGE_RECIPIENT" --output "$PART_FILE" \
        || die "pg_dump | age failed for database ${PGDATABASE}"

    STAGE="verify"
    [[ -s "$PART_FILE" ]] || die "encrypted dump is empty: ${PART_FILE}"
    DUMP_BYTES=$(wc -c < "$PART_FILE")
    # An age file with no payload is ~200 bytes of header. Anything near that is
    # an empty database or a dump that died on its first row; both are failures.
    (( DUMP_BYTES > 1024 )) || die "encrypted dump is implausibly small (${DUMP_BYTES} bytes) — treating as a failed dump"

    # Recorded so restore-test.sh can prove it read the same bytes that were
    # written, and so a corrupted off-site copy is provable rather than argued.
    DUMP_SHA256=$(sha256sum < "$PART_FILE" | cut -d' ' -f1)

    # Atomic: the final name only ever exists once the bytes are complete.
    mv -- "$PART_FILE" "$DUMP_FILE"
    PART_FILE=""

    # ---------------------------------------------------------------------
    # Off-site copy
    # ---------------------------------------------------------------------
    STAGE="offsite"
    OFFSITE_STATUS="skipped"
    if [[ "$OFFSITE_DEST" == "none" ]]; then
        # Deliberate opt-out, still surfaced every single night. A backup that
        # only exists on the machine it backs up is not an off-site backup.
        OFFSITE_STATUS="none-configured"
    else
        rsync --archive --partial --chmod=F600 -- "$DUMP_FILE" "${OFFSITE_DEST%/}/" \
            || die "off-site copy to ${OFFSITE_DEST} failed (the local copy at ${DUMP_FILE} is intact)"
        OFFSITE_STATUS="ok"
    fi
fi

# ---------------------------------------------------------------------------
# Retention pruning
# ---------------------------------------------------------------------------
STAGE="prune"
PRUNED=0
if (( PRUNE )); then
    # Narrow by construction, which is why this needs no confirmation flag to be
    # safe: one directory, no recursion (-maxdepth 1), regular files only, and
    # only names this script itself produces. It cannot reach a file it did not
    # write. BACKUP_DIR was rejected above if it were a system root.
    #
    # -mmin, not -mtime: `-mtime +14` floors to whole days and actually spares
    # anything under 15 days old, so a "14 day" retention quietly keeps 15.
    RETENTION_MINUTES=$(( BACKUP_RETENTION_DAYS * 24 * 60 ))
    while IFS= read -r -d '' old; do
        if (( DRY_RUN )); then
            printf '%s scanid-backup would-prune file=%s\n' "$(timestamp)" "$old"
        else
            rm -f -- "$old"
        fi
        PRUNED=$(( PRUNED + 1 ))
    done < <(find "$BACKUP_DIR" -maxdepth 1 -type f \
                  -name "${FILE_PREFIX}-*.dump.age" \
                  -mmin "+${RETENTION_MINUTES}" -print0)
fi

# ---------------------------------------------------------------------------
# One line, then out
# ---------------------------------------------------------------------------
STAGE="done"
if (( DRY_RUN )); then
    log_line dry-run "pruned=${PRUNED} retention_days=${BACKUP_RETENTION_DAYS} note=\"nothing was written, copied or deleted\""
else
    log_line ok "file=${DUMP_FILE} bytes=${DUMP_BYTES} sha256=${DUMP_SHA256} offsite=${OFFSITE_STATUS} pruned=${PRUNED} retention_days=${BACKUP_RETENTION_DAYS}"
fi

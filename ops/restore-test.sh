#!/usr/bin/env bash
#
# ScanID — restore rehearsal. Proves a backup is a backup.
#
# GENERATED FILE. Review every line before you run it.
#
# An untested backup is not a backup, it is a hope. This script takes a real
# encrypted dump, decrypts it, restores it into a throwaway database, counts
# rows in the tables that matter, and drops the throwaway database again. If it
# exits 0, that file can rebuild the application. If it exits non-zero, you have
# found out today rather than on the day you needed it.
#
# WHERE TO RUN IT
#   Not on the production VPS, if you can avoid it. It needs the age IDENTITY
#   (private key), and the whole point of backup.sh's key model is that the
#   private key is never on the server. Run this on a workstation or a scratch
#   host that can reach a PostgreSQL you are willing to write to, with the
#   backup file copied there from your off-site destination — which also tests
#   the off-site copy, which is the copy you will actually reach for.
#
# WHAT IT WRITES
#   One database, named scanid_restoretest_<UTC timestamp>_<pid>, created and
#   dropped by this script. Nothing else. It never writes to PGDATABASE.
#
# Usage:
#   restore-test.sh --confirm                     newest backup in BACKUP_DIR
#   restore-test.sh --confirm --file <path>       a specific backup
#   restore-test.sh --confirm --keep              leave the scratch DB for
#                                                 inspection (drop it yourself)
#   restore-test.sh                               refuses; prints what it would do
#
set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Reuses backup.sh's env file, plus two variables only this script needs:
#
#   AGE_IDENTITY_FILE=/REPLACE_ME/scanid-backup.key   # the PRIVATE key, 0600
#   RESTORE_PGHOST=127.0.0.1     # optional: a different server to restore INTO.
#   RESTORE_PGPORT=5432          # defaults to PGHOST/PGPORT if unset.
#   RESTORE_PGUSER=REPLACE_ME    # needs CREATEDB. Defaults to PGUSER.
#   SANITY_MIN_ROWS="users=1,passports=1,ocr_jobs=0,voyages=0"
#
# SANITY_MIN_ROWS is the actual assertion. A restore that produces four empty
# tables "succeeds" at the pg_restore level and is still a total failure, so
# state the minimum row counts you expect and let the script fail on them.
#
OPS_ENV_FILE="${OPS_ENV_FILE:-/etc/scanid/backup.env}"

# The scratch database name is built from this prefix and cannot be overridden
# by the env file. Every safety check below keys off it.
SCRATCH_PREFIX="scanid_restoretest_"
SANITY_MIN_ROWS_DEFAULT="users=1,passports=0,ocr_jobs=0,voyages=0"

umask 077

# ---------------------------------------------------------------------------
# Logging and failure handling
# ---------------------------------------------------------------------------
timestamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log()  { printf '%s scanid-restore-test %s\n' "$(timestamp)" "$*"; }
die()  { printf '%s scanid-restore-test status=error message="%s"\n' "$(timestamp)" "$*" >&2; exit 1; }

SCRATCH_DB=""
KEEP=0

cleanup() {
    local rc=$?
    # The scratch database is dropped whether the run passed, failed or was
    # interrupted. A restore test that litters half-restored databases across a
    # server is how a "test" becomes an outage.
    if [[ -n "$SCRATCH_DB" ]] && (( ! KEEP )); then
        log "dropping scratch database ${SCRATCH_DB}"
        drop_scratch_db || printf 'WARNING: could not drop %s — drop it by hand\n' "$SCRATCH_DB" >&2
    elif [[ -n "$SCRATCH_DB" ]]; then
        printf 'NOTE: --keep given, %s was left in place. Drop it yourself:\n  dropdb %s\n' \
            "$SCRATCH_DB" "$SCRATCH_DB" >&2
    fi
    return "$rc"
}
trap cleanup EXIT

# ---------------------------------------------------------------------------
# Arguments
# ---------------------------------------------------------------------------
CONFIRMED=0
BACKUP_FILE=""
while (( $# )); do
    case "$1" in
        --confirm) CONFIRMED=1 ;;
        --keep)    KEEP=1 ;;
        --file)    shift; [[ $# -gt 0 ]] || die "--file needs a path"; BACKUP_FILE="$1" ;;
        --file=*)  BACKUP_FILE="${1#--file=}" ;;
        -h|--help) sed -n '2,40p' "$0"; exit 0 ;;
        *)         die "unknown argument: $1 (see --help)" ;;
    esac
    shift
done

# ---------------------------------------------------------------------------
# Preflight
# ---------------------------------------------------------------------------
[[ -r "$OPS_ENV_FILE" ]] || die "env file not readable: ${OPS_ENV_FILE} (set OPS_ENV_FILE to override)"
set -a
# shellcheck source=/dev/null
source "$OPS_ENV_FILE"
set +a

: "${SANITY_MIN_ROWS:=$SANITY_MIN_ROWS_DEFAULT}"

for var in PGUSER PGDATABASE BACKUP_DIR AGE_IDENTITY_FILE; do
    [[ -n "${!var:-}" ]] || die "required variable ${var} is empty or unset in ${OPS_ENV_FILE}"
done

for cmd in age pg_restore psql createdb dropdb; do
    command -v "$cmd" >/dev/null 2>&1 || die "required command not found: ${cmd}"
done

[[ -r "$AGE_IDENTITY_FILE" ]] || die "age identity not readable: ${AGE_IDENTITY_FILE}"
# A private key readable by anyone else on the box is a private key you have to
# assume is copied. Warn rather than fail: the human may be mid-setup.
IDENTITY_MODE=$(stat -c '%a' "$AGE_IDENTITY_FILE" 2>/dev/null || echo "unknown")
[[ "$IDENTITY_MODE" == "600" || "$IDENTITY_MODE" == "400" ]] \
    || printf 'WARNING: %s is mode %s; it holds the key to every backup. chmod 600 it.\n' \
        "$AGE_IDENTITY_FILE" "$IDENTITY_MODE" >&2

# Restore target: a separate server if configured, otherwise the same one.
PGHOST="${RESTORE_PGHOST:-${PGHOST:-}}"
[[ -n "$PGHOST" ]] || die "neither RESTORE_PGHOST nor PGHOST is set in ${OPS_ENV_FILE}"
PGPORT="${RESTORE_PGPORT:-${PGPORT:-5432}}"
PGUSER="${RESTORE_PGUSER:-$PGUSER}"
export PGHOST PGPORT PGUSER
# `if`, not `[[ ... ]] && export`: under `set -e` a false test is a failing
# command and would abort the run whenever the password comes from ~/.pgpass.
if [[ -n "${RESTORE_PGPASSWORD:-}" ]]; then
    export PGPASSWORD="$RESTORE_PGPASSWORD"
elif [[ -n "${PGPASSWORD:-}" ]]; then
    export PGPASSWORD
fi
# PGDATABASE is the PRODUCTION name. Unexport it so that no psql, createdb or
# pg_restore in this script can default to it by accident.
PRODUCTION_DB="$PGDATABASE"
export PGDATABASE=postgres

# ---------------------------------------------------------------------------
# Pick the backup file
# ---------------------------------------------------------------------------
if [[ -z "$BACKUP_FILE" ]]; then
    [[ -d "$BACKUP_DIR" ]] || die "BACKUP_DIR does not exist: ${BACKUP_DIR}"
    # Names are UTC stamps in a sortable format, so the last one lexically is
    # the newest one chronologically. No parsing of `ls -t` output.
    BACKUP_FILE=$(find "$BACKUP_DIR" -maxdepth 1 -type f -name 'scanid-*.dump.age' -print \
                  | sort | tail -n 1)
    [[ -n "$BACKUP_FILE" ]] || die "no scanid-*.dump.age files found in ${BACKUP_DIR}"
fi
[[ -r "$BACKUP_FILE" ]] || die "backup file not readable: ${BACKUP_FILE}"

# ---------------------------------------------------------------------------
# Name the scratch database, and refuse anything that looks like production
# ---------------------------------------------------------------------------
SCRATCH_CANDIDATE="${SCRATCH_PREFIX}$(date -u +%Y%m%d%H%M%S)_$$"

# Four independent refusals. Any one of them is enough on its own; all four are
# here because the failure being prevented is "restore-test overwrote the live
# database", and that is not a mistake you get to make twice.
[[ "$SCRATCH_CANDIDATE" == "${SCRATCH_PREFIX}"* ]] \
    || die "internal error: scratch name '${SCRATCH_CANDIDATE}' lost its mandatory prefix"

[[ "$SCRATCH_CANDIDATE" != "$PRODUCTION_DB" ]] \
    || die "scratch name equals the configured production database (${PRODUCTION_DB})"

# Substring, both directions: catches PGDATABASE=scanid_restoretest_x as well as
# a production name that happens to contain the prefix.
if [[ "$PRODUCTION_DB" == *"$SCRATCH_PREFIX"* ]]; then
    die "PGDATABASE (${PRODUCTION_DB}) itself contains '${SCRATCH_PREFIX}'. Rename it, or this script cannot tell your production database from its own scratch one."
fi

# Names that mean "this is the real thing" in every shop that has ever existed.
# Checked against the scratch name, so a future edit that makes the name
# configurable cannot quietly point it at prod.
case "${SCRATCH_CANDIDATE,,}" in
    *prod*|*live*|*travelapp*|*scanid_app*|postgres|template0|template1)
        die "refusing: scratch name '${SCRATCH_CANDIDATE}' looks like a production database" ;;
esac

SCRATCH_DB="$SCRATCH_CANDIDATE"

drop_scratch_db() {
    # --force terminates leftover connections; without it a psql someone left
    # open in another window makes the drop fail and the "cleanup" a no-op.
    dropdb --if-exists --force "$SCRATCH_DB" 2>/dev/null \
        || dropdb --if-exists "$SCRATCH_DB"
}

# ---------------------------------------------------------------------------
# The confirmation gate
# ---------------------------------------------------------------------------
if (( ! CONFIRMED )); then
    SCRATCH_DB=""   # nothing was created; stop cleanup() from trying to drop it
    cat >&2 <<EOF
$(timestamp) scanid-restore-test status=refused message="--confirm not given"

This run WOULD have:
  restored  ${BACKUP_FILE}
  into      ${SCRATCH_CANDIDATE}
  on        ${PGHOST}:${PGPORT} as ${PGUSER}
  asserted  ${SANITY_MIN_ROWS}
  then dropped ${SCRATCH_CANDIDATE}.

It creates and drops a database. Re-run with --confirm if that is what you want.
EOF
    exit 2
fi

# ---------------------------------------------------------------------------
# Restore
# ---------------------------------------------------------------------------
log "file=${BACKUP_FILE} bytes=$(wc -c < "$BACKUP_FILE") sha256=$(sha256sum < "$BACKUP_FILE" | cut -d' ' -f1)"
log "creating scratch database ${SCRATCH_DB} on ${PGHOST}:${PGPORT}"
createdb "$SCRATCH_DB" || die "could not create scratch database ${SCRATCH_DB}"

log "decrypting and restoring"
# Same pipe discipline as backup.sh: the decrypted dump is never a file. It goes
# from age's stdout into pg_restore's stdin and nowhere else.
#
# age's exit code IS a hard failure: it means the wrong identity or a corrupt
# file, and there is nothing to check afterwards.
#
# pg_restore's is not, on its own. Restoring a --no-owner dump into a fresh
# database emits benign complaints (absent roles, an extension comment it may
# not re-set) and exits 1 for them, so keying pass/fail on it alone would make
# this script cry wolf nightly. It is reported, and the row counts below decide.
set +e
age --decrypt --identity "$AGE_IDENTITY_FILE" < "$BACKUP_FILE" \
    | pg_restore --dbname "$SCRATCH_DB" --no-owner --no-privileges
RESTORE_STATUS=("${PIPESTATUS[@]}")
set -e
(( RESTORE_STATUS[0] == 0 )) \
    || die "age failed to decrypt ${BACKUP_FILE} — wrong identity, or the file is corrupt"
if (( RESTORE_STATUS[1] != 0 )); then
    log "note pg_restore exited ${RESTORE_STATUS[1]} (non-fatal complaints above); the row counts decide"
fi

# ---------------------------------------------------------------------------
# Sanity queries — the actual proof
# ---------------------------------------------------------------------------
log "running sanity queries"
FAILURES=0
COUNTS=""
IFS=',' read -ra EXPECTATIONS <<< "$SANITY_MIN_ROWS"
for expectation in "${EXPECTATIONS[@]}"; do
    expectation="${expectation// /}"
    [[ -n "$expectation" ]] || continue
    table="${expectation%%=*}"
    minimum="${expectation##*=}"
    [[ "$table" =~ ^[a-z_][a-z0-9_]*$ ]] || die "invalid table name in SANITY_MIN_ROWS: ${table}"
    [[ "$minimum" =~ ^[0-9]+$ ]]         || die "invalid minimum in SANITY_MIN_ROWS for ${table}: ${minimum}"

    # to_regclass returns NULL rather than raising when the table is absent, so
    # a missing table is reported as a missing table instead of a query error.
    if [[ "$(psql --dbname "$SCRATCH_DB" -tAc "select to_regclass('public.${table}') is not null")" != "t" ]]; then
        printf 'FAIL table=%s message="table is missing from the restored database"\n' "$table" >&2
        FAILURES=$(( FAILURES + 1 ))
        continue
    fi

    actual=$(psql --dbname "$SCRATCH_DB" -tAc "select count(*) from public.${table}")
    COUNTS="${COUNTS}${table}=${actual} "
    if (( actual < minimum )); then
        printf 'FAIL table=%s rows=%s expected_min=%s\n' "$table" "$actual" "$minimum" >&2
        FAILURES=$(( FAILURES + 1 ))
    fi
done

(( FAILURES == 0 )) || die "${FAILURES} sanity check(s) failed — this backup would NOT rebuild the application"

log "status=ok file=${BACKUP_FILE} scratch_db=${SCRATCH_DB} ${COUNTS}"
log "status=ok message=\"this backup restores and contains data\""

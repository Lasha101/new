#!/usr/bin/env bash
#
# ScanID — test suite for ops/backup.sh and ops/restore-test.sh.
#
# Self-contained and destructive to NOTHING outside its own temp directory:
# it builds a throwaway PostgreSQL cluster of its own (initdb into a temp dir,
# listening on 127.0.0.1 at an unused high port, no unix socket), seeds it with
# a schema mirroring backend/models.py, exercises both scripts against it, and
# tears the cluster down again.
#
# It NEVER contacts a remote host and never reads the real /etc/scanid/backup.env.
#
# Requires: initdb, pg_ctl, pg_dump, pg_restore, psql, createdb, dropdb, age,
#           age-keygen, rsync, flock.
#
# Usage:  ops/tests/run-ops-tests.sh
#         KEEP_WORKDIR=1 ops/tests/run-ops-tests.sh   # leave temp dir for triage
#
set -uo pipefail

OPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_SH="${OPS_DIR}/backup.sh"
RESTORE_SH="${OPS_DIR}/restore-test.sh"

PASS=0
FAIL=0

green() { printf '\033[32m%s\033[0m' "$1"; }
red()   { printf '\033[31m%s\033[0m' "$1"; }

testcase() { printf '\n--- %s\n' "$1"; }
ok()   { PASS=$(( PASS + 1 )); printf '  %s %s\n' "$(green PASS)" "$1"; }
bad()  { FAIL=$(( FAIL + 1 )); printf '  %s %s\n' "$(red FAIL)" "$1"; }

assert_true()     { if eval "$1"; then ok "$2"; else bad "$2 -- [$1] was false"; fi; }
assert_eq()       { if [[ "$1" == "$2" ]]; then ok "$3"; else bad "$3 -- expected '$2', got '$1'"; fi; }
assert_contains() { if grep -qF -- "$2" <<<"$1"; then ok "$3"; else bad "$3 -- output did not contain '$2'"; fi; }

# ---------------------------------------------------------------------------
# Locate the PostgreSQL server binaries (initdb/pg_ctl are not usually on PATH)
# ---------------------------------------------------------------------------
if ! command -v initdb >/dev/null 2>&1; then
    for candidate in /usr/lib/postgresql/*/bin /usr/pgsql-*/bin /opt/homebrew/opt/postgresql*/bin; do
        [[ -x "${candidate}/initdb" ]] && { PATH="${candidate}:${PATH}"; break; }
    done
fi
export PATH
for cmd in initdb pg_ctl pg_dump pg_restore psql createdb dropdb age age-keygen rsync flock; do
    command -v "$cmd" >/dev/null 2>&1 || { printf 'SKIP: required command not found: %s\n' "$cmd" >&2; exit 3; }
done

# ---------------------------------------------------------------------------
# Workspace
# ---------------------------------------------------------------------------
WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/scanid-ops-tests.XXXXXX")"
PGDATA_DIR="${WORKDIR}/pgdata"
BACKUP_DIR="${WORKDIR}/backups"
OFFSITE_DIR="${WORKDIR}/offsite"
ENV_FILE="${WORKDIR}/backup.env"
KEY_FILE="${WORKDIR}/backup.key"
PG_PORT=$(( 55000 + (RANDOM % 2000) ))
TEST_DB="scanid_optest_src"

teardown() {
    if [[ -d "$PGDATA_DIR" ]]; then
        pg_ctl -D "$PGDATA_DIR" -m immediate stop >/dev/null 2>&1 || true
    fi
    if [[ -n "${KEEP_WORKDIR:-}" ]]; then
        printf '\nworkdir kept: %s\n' "$WORKDIR"
    else
        rm -rf "$WORKDIR"
    fi
}
trap teardown EXIT

mkdir -p "$BACKUP_DIR" "$OFFSITE_DIR"
chmod 700 "$BACKUP_DIR"

printf 'workdir: %s\nport:    %s\n' "$WORKDIR" "$PG_PORT"

# ---------------------------------------------------------------------------
# Throwaway PostgreSQL
# ---------------------------------------------------------------------------
printf '\nstarting throwaway PostgreSQL...\n'
initdb -D "$PGDATA_DIR" -U opsuser --auth=trust -E UTF8 >/dev/null 2>&1 \
    || { printf 'initdb failed\n' >&2; exit 3; }
# unix_socket_directories is emptied: the socket path under a long mktemp dir can
# exceed the 107-byte sockaddr limit. TCP on loopback only.
pg_ctl -D "$PGDATA_DIR" \
       -o "-p ${PG_PORT} -h 127.0.0.1 -c unix_socket_directories=" \
       -l "${WORKDIR}/pg.log" start >/dev/null 2>&1
for _ in $(seq 1 30); do
    pg_isready -h 127.0.0.1 -p "$PG_PORT" -q && break
    sleep 0.5
done
pg_isready -h 127.0.0.1 -p "$PG_PORT" -q || { cat "${WORKDIR}/pg.log" >&2; exit 3; }

export PGHOST=127.0.0.1 PGPORT="$PG_PORT" PGUSER=opsuser
createdb "$TEST_DB"

# Schema mirroring backend/models.py, with recognisable seed data. The strings
# below are used later to prove the encrypted file is not plaintext.
CANARY="ZZCANARY_PASSPORT_NUMBER_7391"
psql --dbname "$TEST_DB" -q -v ON_ERROR_STOP=1 <<SQL
CREATE TABLE users (
    id varchar(36) PRIMARY KEY, first_name text NOT NULL, last_name text NOT NULL,
    email text NOT NULL UNIQUE, phone_number text NOT NULL, user_name text NOT NULL UNIQUE,
    hashed_password text NOT NULL, role text NOT NULL DEFAULT 'user',
    uploaded_pages_count integer NOT NULL DEFAULT 0, page_credits integer DEFAULT 0);
CREATE TABLE passports (
    id varchar(36) PRIMARY KEY, owner_id varchar(36) NOT NULL, first_name text NOT NULL,
    last_name text NOT NULL, birth_date date NOT NULL, expiration_date date NOT NULL,
    nationality text NOT NULL, passport_number text NOT NULL, destination text,
    confidence_score double precision);
CREATE TABLE ocr_jobs (
    id varchar(36) PRIMARY KEY, user_id varchar(36) NOT NULL, file_name text NOT NULL,
    status text NOT NULL DEFAULT 'processing', progress integer NOT NULL DEFAULT 0,
    created_at timestamptz NOT NULL, finished_at timestamptz,
    successes json NOT NULL DEFAULT '[]', failures json NOT NULL DEFAULT '[]');
CREATE TABLE voyages (
    id varchar(36) PRIMARY KEY, user_id varchar(36) NOT NULL, destination text NOT NULL,
    passport_ids json NOT NULL DEFAULT '[]');

INSERT INTO users (id, first_name, last_name, email, phone_number, user_name, hashed_password, role)
VALUES ('u1','Admin','ScanID','admin@example.invalid','0000000000','admin','\$2b\$12\$notarealhash','admin'),
       ('u2','Test','User','user@example.invalid','0000000001','tuser','\$2b\$12\$notarealhash','user');
INSERT INTO passports (id, owner_id, first_name, last_name, birth_date, expiration_date, nationality, passport_number, destination)
VALUES ('p1','u1','Jean','Dupont','1980-01-01','2030-01-01','FRA','${CANARY}','Voyage 2026'),
       ('p2','u2','Marie','Martin','1990-06-15','2029-06-15','FRA','19FR44821','Voyage 2026'),
       ('p3','u2','Paul','Bernard','1975-03-20','2028-03-20','FRA','17FR11902',NULL);
INSERT INTO ocr_jobs (id, user_id, file_name, status, progress, created_at)
VALUES ('j1','u1','doc.pdf','done',100, now());
INSERT INTO voyages (id, user_id, destination, passport_ids)
VALUES ('v1','u1','Voyage 2026','["p1","p2"]');
SQL
printf 'seeded: users=2 passports=3 ocr_jobs=1 voyages=1\n'

# ---------------------------------------------------------------------------
# age keypair + env file
# ---------------------------------------------------------------------------
age-keygen -o "$KEY_FILE" 2>/dev/null
chmod 600 "$KEY_FILE"
AGE_RECIPIENT="$(age-keygen -y "$KEY_FILE")"

write_env() {
    cat > "$ENV_FILE" <<EOF
PGHOST=127.0.0.1
PGPORT=${PG_PORT}
PGUSER=opsuser
PGDATABASE=${TEST_DB}
BACKUP_DIR=${BACKUP_DIR}
AGE_RECIPIENT=${AGE_RECIPIENT}
AGE_IDENTITY_FILE=${KEY_FILE}
OFFSITE_DEST=${OFFSITE_DIR}
BACKUP_RETENTION_DAYS=14
SANITY_MIN_ROWS=users=2,passports=3,ocr_jobs=1,voyages=1
$*
EOF
}
write_env

run_backup()  { OPS_ENV_FILE="$ENV_FILE" "$BACKUP_SH"  "$@" 2>&1; }
run_restore() { OPS_ENV_FILE="$ENV_FILE" "$RESTORE_SH" "$@" 2>&1; }

printf '\n===========================================================\n'
printf 'ops/backup.sh\n'
printf '===========================================================\n'

# ---------------------------------------------------------------------------
testcase "backup.sh preflight refuses a missing env file"
out=$(OPS_ENV_FILE="${WORKDIR}/does-not-exist.env" "$BACKUP_SH" 2>&1); rc=$?
assert_true "[[ $rc -ne 0 ]]" "exits non-zero"
assert_contains "$out" "env file not readable" "says which file it could not read"

# ---------------------------------------------------------------------------
testcase "backup.sh preflight refuses an unset required variable"
write_env "AGE_RECIPIENT="
out=$(run_backup); rc=$?
assert_true "[[ $rc -ne 0 ]]" "exits non-zero"
assert_contains "$out" "required variable AGE_RECIPIENT" "names the missing variable"
assert_eq "$(grep -c 'scanid-backup status=' <<<"$out")" "1" "emits exactly one log line"
write_env

# ---------------------------------------------------------------------------
testcase "backup.sh refuses an age PRIVATE key in AGE_RECIPIENT"
write_env "AGE_RECIPIENT=AGE-SECRET-KEY-1QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ"
out=$(run_backup); rc=$?
assert_true "[[ $rc -ne 0 ]]" "exits non-zero"
assert_contains "$out" "PRIVATE key" "explains that the private key must not be on the server"
write_env

# ---------------------------------------------------------------------------
testcase "backup.sh refuses a system directory as BACKUP_DIR"
write_env "BACKUP_DIR=/var"
out=$(run_backup); rc=$?
assert_true "[[ $rc -ne 0 ]]" "exits non-zero"
assert_contains "$out" "refusing to use /var" "refuses /var by name"
write_env

# ---------------------------------------------------------------------------
testcase "backup.sh --dry-run writes, copies and deletes nothing"
# Counts backup files only. A --dry-run does still create the flock lock file,
# which is deliberate: a dry run that ignored the lock could report on a
# directory a real run was busy pruning.
before=$(find "$BACKUP_DIR" -maxdepth 1 -name 'scanid-*.dump.age' | wc -l)
out=$(run_backup --dry-run); rc=$?
after=$(find "$BACKUP_DIR" -maxdepth 1 -name 'scanid-*.dump.age' | wc -l)
assert_eq "$rc" "0" "exits zero"
assert_contains "$out" "status=dry-run" "logs a dry-run status"
assert_eq "$after" "$before" "created no backup file"
assert_eq "$(find "$BACKUP_DIR" -name '*.part' | wc -l)" "0" "created no .part file"
assert_eq "$(find "$OFFSITE_DIR" -type f | wc -l)" "0" "copied nothing off-site"

# ---------------------------------------------------------------------------
testcase "backup.sh produces an encrypted dump"
out=$(run_backup); rc=$?
assert_eq "$rc" "0" "exits zero"
assert_contains "$out" "status=ok" "logs status=ok"
assert_eq "$(grep -c 'scanid-backup status=' <<<"$out")" "1" "emits exactly one log line"
mapfile -t dumps < <(find "$BACKUP_DIR" -maxdepth 1 -name 'scanid-*.dump.age' | sort)
assert_eq "${#dumps[@]}" "1" "exactly one backup file exists"
DUMP="${dumps[0]}"
assert_true "[[ -s '$DUMP' ]]" "the file is non-empty"
assert_eq "$(stat -c '%a' "$DUMP")" "600" "the file is mode 0600"
assert_eq "$(find "$BACKUP_DIR" -name '*.part' | wc -l)" "0" "no .part file was left behind"

# ---------------------------------------------------------------------------
testcase "the encrypted dump is not readable as plain text"
assert_true "head -c 21 '$DUMP' | grep -q 'age-encryption.org'" "starts with the age header"
assert_true "! grep -qF 'PGDMP' '$DUMP'" "does not contain the pg_dump custom-format magic 'PGDMP'"
assert_true "! grep -qaF '$CANARY' '$DUMP'" "does not contain the seeded passport number"
assert_true "! grep -qaF 'Dupont' '$DUMP'" "does not contain a seeded surname"
assert_true "! grep -qaF 'admin@example.invalid' '$DUMP'" "does not contain a seeded email"
assert_true "! grep -qaiF 'CREATE TABLE' '$DUMP'" "does not contain SQL DDL"

# ---------------------------------------------------------------------------
testcase "no plaintext dump was ever left on disk"
assert_eq "$(find "$WORKDIR" -maxdepth 2 -name '*.dump' -o -maxdepth 2 -name '*.sql' | wc -l)" "0" \
    "no unencrypted .dump or .sql anywhere in the workspace"

# ---------------------------------------------------------------------------
testcase "the encrypted dump decrypts back to a valid PostgreSQL dump"
plain="${WORKDIR}/decrypted.check"
age --decrypt --identity "$KEY_FILE" < "$DUMP" > "$plain" 2>/dev/null; rc=$?
assert_eq "$rc" "0" "age decrypts it"
assert_true "head -c 5 '$plain' | grep -q 'PGDMP'" "the plaintext is a custom-format pg_dump (PGDMP magic)"
listing=$(pg_restore --list "$plain" 2>&1); rc=$?
assert_eq "$rc" "0" "pg_restore --list accepts it"
assert_contains "$listing" "TABLE DATA public passports" "the listing contains the passports table data"
assert_contains "$listing" "TABLE DATA public users" "the listing contains the users table data"
rm -f "$plain"

# ---------------------------------------------------------------------------
testcase "the backup was copied off-site"
assert_eq "$(find "$OFFSITE_DIR" -name 'scanid-*.dump.age' | wc -l)" "1" "one file arrived at the off-site destination"
assert_true "cmp -s '$DUMP' '${OFFSITE_DIR}/$(basename "$DUMP")'" "the off-site copy is byte-identical"
assert_contains "$out" "offsite=ok" "the log line records offsite=ok"

# ---------------------------------------------------------------------------
testcase "backup.sh fails loudly when the database is unreachable"
write_env "PGDATABASE=no_such_database_here"
out=$(run_backup); rc=$?
assert_true "[[ $rc -ne 0 ]]" "exits non-zero"
assert_contains "$out" "status=error" "logs status=error"
assert_eq "$(grep -c 'scanid-backup status=' <<<"$out")" "1" "emits exactly one log line on failure too"
assert_contains "$out" "stage=dump" "the log line says which stage failed"
assert_eq "$(find "$BACKUP_DIR" -name '*.part' | wc -l)" "0" "leaves no .part file"
assert_eq "$(find "$BACKUP_DIR" -maxdepth 1 -name 'scanid-*.dump.age' | wc -l)" "1" \
    "creates no new backup file (the good one from before is still the only one)"
write_env

# ---------------------------------------------------------------------------
testcase "retention pruning deletes only what is past the retention period"
# Ages chosen around a 14-day retention. mtimes are set explicitly so the test
# does not depend on wall-clock timing.
touch -d '30 days ago' "${BACKUP_DIR}/scanid-20260101T030000Z.dump.age"
touch -d '20 days ago' "${BACKUP_DIR}/scanid-20260110T030000Z.dump.age"
touch -d '15 days ago' "${BACKUP_DIR}/scanid-20260115T030000Z.dump.age"
touch -d '13 days ago' "${BACKUP_DIR}/scanid-20260117T030000Z.dump.age"
touch -d '2 days ago'  "${BACKUP_DIR}/scanid-20260128T030000Z.dump.age"
# Two files pruning must not touch: a foreign name, and one in a subdirectory.
touch -d '90 days ago' "${BACKUP_DIR}/unrelated-backup.tar.gz"
mkdir -p "${BACKUP_DIR}/archive"
touch -d '90 days ago' "${BACKUP_DIR}/archive/scanid-20250101T030000Z.dump.age"

out=$(run_backup); rc=$?
assert_eq "$rc" "0" "exits zero"
assert_contains "$out" "pruned=3" "reports pruning exactly 3 files"
assert_true "[[ ! -e '${BACKUP_DIR}/scanid-20260101T030000Z.dump.age' ]]" "deleted the 30-day-old file"
assert_true "[[ ! -e '${BACKUP_DIR}/scanid-20260110T030000Z.dump.age' ]]" "deleted the 20-day-old file"
assert_true "[[ ! -e '${BACKUP_DIR}/scanid-20260115T030000Z.dump.age' ]]" "deleted the 15-day-old file"
assert_true "[[ -e '${BACKUP_DIR}/scanid-20260117T030000Z.dump.age' ]]" "kept the 13-day-old file"
assert_true "[[ -e '${BACKUP_DIR}/scanid-20260128T030000Z.dump.age' ]]" "kept the 2-day-old file"
assert_true "[[ -e '${BACKUP_DIR}/unrelated-backup.tar.gz' ]]" "kept a file it does not own, however old"
assert_true "[[ -e '${BACKUP_DIR}/archive/scanid-20250101T030000Z.dump.age' ]]" "did not recurse into a subdirectory"

# ---------------------------------------------------------------------------
testcase "backup.sh --no-prune keeps expired files"
touch -d '40 days ago' "${BACKUP_DIR}/scanid-20251201T030000Z.dump.age"
out=$(run_backup --no-prune); rc=$?
assert_eq "$rc" "0" "exits zero"
assert_contains "$out" "pruned=0" "reports pruning nothing"
assert_true "[[ -e '${BACKUP_DIR}/scanid-20251201T030000Z.dump.age' ]]" "the 40-day-old file survives"
rm -f "${BACKUP_DIR}/scanid-20251201T030000Z.dump.age"

# ---------------------------------------------------------------------------
testcase "a second concurrent run refuses instead of overlapping"
( exec 9>"${BACKUP_DIR}/.backup.lock"; flock -n 9; sleep 5 ) &
holder=$!
sleep 0.5
out=$(run_backup); rc=$?
kill "$holder" 2>/dev/null; wait "$holder" 2>/dev/null
assert_true "[[ $rc -ne 0 ]]" "exits non-zero"
assert_contains "$out" "already holds" "says another run holds the lock"

printf '\n===========================================================\n'
printf 'ops/restore-test.sh\n'
printf '===========================================================\n'

NEWEST=$(find "$BACKUP_DIR" -maxdepth 1 -name 'scanid-*.dump.age' | sort | tail -n 1)

list_scratch_dbs() {
    psql --dbname postgres -tAc \
        "select datname from pg_database where datname like 'scanid_restoretest_%'" | tr -d ' '
}

# ---------------------------------------------------------------------------
testcase "restore-test.sh refuses to run without --confirm"
out=$(run_restore); rc=$?
assert_eq "$rc" "2" "exits 2"
assert_contains "$out" "status=refused" "logs status=refused"
assert_contains "$out" "--confirm not given" "says --confirm is missing"
assert_contains "$out" "This run WOULD have" "explains what it would have done"
assert_eq "$(list_scratch_dbs | grep -c .)" "0" "created no database"

# ---------------------------------------------------------------------------
testcase "restore-test.sh refuses when production shares the scratch prefix"
write_env "PGDATABASE=scanid_restoretest_prod"
out=$(run_restore --confirm); rc=$?
assert_true "[[ $rc -ne 0 ]]" "exits non-zero"
assert_contains "$out" "contains 'scanid_restoretest_'" "explains the name collision"
assert_eq "$(list_scratch_dbs | grep -c .)" "0" "created no database"
write_env

# ---------------------------------------------------------------------------
testcase "restore-test.sh refuses a scratch name that looks like production"
# The scratch name is not configurable, so the production-lookalike guard is
# exercised by pointing SCRATCH_PREFIX at a production-shaped value, which is
# what a careless future edit would do.
tmp_script="${WORKDIR}/restore-test-prodname.sh"
sed 's|^SCRATCH_PREFIX="scanid_restoretest_"$|SCRATCH_PREFIX="travelapp_prod_"|' "$RESTORE_SH" > "$tmp_script"
chmod +x "$tmp_script"
out=$(OPS_ENV_FILE="$ENV_FILE" "$tmp_script" --confirm 2>&1); rc=$?
assert_true "[[ $rc -ne 0 ]]" "exits non-zero"
assert_contains "$out" "looks like a production database" "refuses the production-looking name"
assert_eq "$(psql --dbname postgres -tAc "select count(*) from pg_database where datname like 'travelapp_prod_%'" | tr -d ' ')" "0" \
    "created no database"

# ---------------------------------------------------------------------------
testcase "restore-test.sh restores, verifies row counts, and drops the scratch DB"
out=$(run_restore --confirm --file "$NEWEST"); rc=$?
assert_eq "$rc" "0" "exits zero"
assert_contains "$out" "status=ok" "logs status=ok"
assert_contains "$out" "users=2" "counted 2 users"
assert_contains "$out" "passports=3" "counted 3 passports"
assert_contains "$out" "ocr_jobs=1" "counted 1 ocr_job"
assert_contains "$out" "voyages=1" "counted 1 voyage"
assert_contains "$out" "dropping scratch database" "reports dropping the scratch database"
assert_eq "$(list_scratch_dbs | grep -c .)" "0" "the scratch database no longer exists"
assert_eq "$(psql --dbname "$TEST_DB" -tAc 'select count(*) from passports' | tr -d ' ')" "3" \
    "the source database is untouched"

# ---------------------------------------------------------------------------
testcase "restore-test.sh picks the newest backup when --file is omitted"
out=$(run_restore --confirm); rc=$?
assert_eq "$rc" "0" "exits zero"
assert_contains "$out" "file=${NEWEST}" "chose the newest backup file"
assert_eq "$(list_scratch_dbs | grep -c .)" "0" "the scratch database was dropped"

# ---------------------------------------------------------------------------
testcase "restore-test.sh fails when a sanity count is not met"
write_env "SANITY_MIN_ROWS=users=2,passports=999"
out=$(run_restore --confirm --file "$NEWEST"); rc=$?
assert_true "[[ $rc -ne 0 ]]" "exits non-zero"
assert_contains "$out" "FAIL table=passports rows=3 expected_min=999" "names the table and both counts"
assert_contains "$out" "would NOT rebuild the application" "says the backup is not trustworthy"
assert_eq "$(list_scratch_dbs | grep -c .)" "0" "the scratch database is dropped even on failure"
write_env

# ---------------------------------------------------------------------------
testcase "restore-test.sh fails when a required table is missing"
write_env "SANITY_MIN_ROWS=users=2,table_that_does_not_exist=1"
out=$(run_restore --confirm --file "$NEWEST"); rc=$?
assert_true "[[ $rc -ne 0 ]]" "exits non-zero"
assert_contains "$out" "table is missing from the restored database" "reports the missing table"
assert_eq "$(list_scratch_dbs | grep -c .)" "0" "the scratch database is dropped"
write_env

# ---------------------------------------------------------------------------
testcase "restore-test.sh fails on the wrong decryption key"
age-keygen -o "${WORKDIR}/wrong.key" 2>/dev/null
chmod 600 "${WORKDIR}/wrong.key"
write_env "AGE_IDENTITY_FILE=${WORKDIR}/wrong.key"
out=$(run_restore --confirm --file "$NEWEST"); rc=$?
assert_true "[[ $rc -ne 0 ]]" "exits non-zero"
assert_contains "$out" "failed to decrypt" "reports the decryption failure"
assert_eq "$(list_scratch_dbs | grep -c .)" "0" "the scratch database is dropped"
write_env

# ---------------------------------------------------------------------------
testcase "restore-test.sh detects a corrupted backup"
cp "$NEWEST" "${WORKDIR}/corrupt.dump.age"
printf 'garbage' | dd of="${WORKDIR}/corrupt.dump.age" bs=1 seek=400 conv=notrunc status=none
out=$(run_restore --confirm --file "${WORKDIR}/corrupt.dump.age"); rc=$?
assert_true "[[ $rc -ne 0 ]]" "exits non-zero"
assert_eq "$(list_scratch_dbs | grep -c .)" "0" "the scratch database is dropped"

# ---------------------------------------------------------------------------
printf '\n===========================================================\n'
printf 'end-to-end: a backup taken today rebuilds the application data\n'
printf '===========================================================\n'
testcase "full cycle — mutate source, back up, restore, compare"
psql --dbname "$TEST_DB" -q -c \
  "INSERT INTO passports (id, owner_id, first_name, last_name, birth_date, expiration_date, nationality, passport_number) \
   VALUES ('p4','u1','Claire','Petit','1988-11-02','2031-11-02','FRA','21FR55110')"
write_env "SANITY_MIN_ROWS=users=2,passports=4,ocr_jobs=1,voyages=1"
out=$(run_backup); rc=$?
assert_eq "$rc" "0" "the new backup succeeds"
out=$(run_restore --confirm); rc=$?
assert_eq "$rc" "0" "the newest backup restores"
assert_contains "$out" "passports=4" "the restored copy has the row added after the previous backup"
write_env

# ---------------------------------------------------------------------------
printf '\n===========================================================\n'
printf 'RESULTS: %s passed, %s failed\n' "$PASS" "$FAIL"
printf '===========================================================\n'
(( FAIL == 0 )) || exit 1

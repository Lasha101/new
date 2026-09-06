#!/usr/bin/env bash
#
# ScanID — validates ops/nginx-security-headers.conf.
#
# Two levels of check, LOCAL ONLY. This never touches a real server, never
# reloads anything, and never reads the production vhost.
#
#   1. `nginx -t` against a minimal config that includes the snippet — proves it
#      parses and that every directive is legal where it is used.
#   2. Starts that nginx, requests a page, and asserts the headers actually
#      arrive with the exact expected values — because a config that parses can
#      still send nothing (the add_header inheritance trap the snippet warns
#      about is precisely this class of bug).
#
# Uses a local nginx if there is one, otherwise a throwaway docker container.
#
set -uo pipefail

OPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SNIPPET="${OPS_DIR}/nginx-security-headers.conf"

PASS=0
FAIL=0
ok()  { PASS=$(( PASS + 1 )); printf '  \033[32mPASS\033[0m %s\n' "$1"; }
bad() { FAIL=$(( FAIL + 1 )); printf '  \033[31mFAIL\033[0m %s\n' "$1"; }
assert_contains() { if grep -qiF -- "$2" <<<"$1"; then ok "$3"; else bad "$3 -- not found: $2"; fi; }
assert_absent()   { if grep -qiF -- "$2" <<<"$1"; then bad "$3 -- unexpectedly present: $2"; else ok "$3"; fi; }

[[ -r "$SNIPPET" ]] || { printf 'snippet not found: %s\n' "$SNIPPET" >&2; exit 3; }

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/scanid-nginx-test.XXXXXX")"
trap 'rm -rf "$WORKDIR"; [[ -n "${CONTAINER:-}" ]] && docker rm -f "$CONTAINER" >/dev/null 2>&1' EXIT
CONTAINER=""

mkdir -p "${WORKDIR}/html" "${WORKDIR}/conf"
cp "$SNIPPET" "${WORKDIR}/conf/security-headers.conf"
printf '<!doctype html><title>t</title>ok\n' > "${WORKDIR}/html/index.html"

# A minimal vhost shaped like deploy/nginx-travelapp.conf: the snippet is
# included ONCE at server level, which is how it is meant to be used.
cat > "${WORKDIR}/conf/nginx.conf" <<'NGINX'
worker_processes 1;
error_log /dev/stderr warn;
pid /tmp/nginx-test.pid;
events { worker_connections 16; }
http {
    access_log off;
    default_type text/html;
    server {
        listen 8087;
        server_name _;
        root /usr/share/nginx/html;
        index index.html;
        include /etc/nginx/conf.d/security-headers.conf;
        location / { try_files $uri $uri/ /index.html; }
    }
}
NGINX

printf 'validating %s\n' "$SNIPPET"

# ---------------------------------------------------------------------------
# Pick a runner
# ---------------------------------------------------------------------------
if command -v nginx >/dev/null 2>&1; then
    RUNNER=local
elif command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    RUNNER=docker
else
    printf 'SKIP: neither a local nginx nor a usable docker is available\n' >&2
    exit 3
fi
printf 'runner:  %s\n\n' "$RUNNER"

run_nginx_t() {
    if [[ "$RUNNER" == local ]]; then
        mkdir -p "${WORKDIR}/etc/nginx/conf.d"
        cp "${WORKDIR}/conf/security-headers.conf" "${WORKDIR}/etc/nginx/conf.d/"
        nginx -t -p "${WORKDIR}" -c "${WORKDIR}/conf/nginx.conf" 2>&1
    else
        docker run --rm \
            -v "${WORKDIR}/conf/nginx.conf:/etc/nginx/nginx.conf:ro" \
            -v "${WORKDIR}/conf/security-headers.conf:/etc/nginx/conf.d/security-headers.conf:ro" \
            nginx:alpine nginx -t 2>&1
    fi
}

# ---------------------------------------------------------------------------
printf -- '--- nginx -t\n'
tout=$(run_nginx_t); trc=$?
printf '%s\n' "$tout" | sed 's/^/      /'
if (( trc == 0 )); then ok "the snippet parses (nginx -t exits 0)"; else bad "nginx -t exited ${trc}"; fi
assert_contains "$tout" "syntax is ok" "nginx reports syntax is ok"
assert_contains "$tout" "test is successful" "nginx reports the test is successful"

# ---------------------------------------------------------------------------
printf -- '\n--- headers actually sent on a real request\n'
if [[ "$RUNNER" == docker ]]; then
    CONTAINER=$(docker run -d -p 127.0.0.1:8087:8087 \
        -v "${WORKDIR}/conf/nginx.conf:/etc/nginx/nginx.conf:ro" \
        -v "${WORKDIR}/conf/security-headers.conf:/etc/nginx/conf.d/security-headers.conf:ro" \
        -v "${WORKDIR}/html:/usr/share/nginx/html:ro" \
        nginx:alpine 2>/dev/null)
    for _ in $(seq 1 40); do
        curl -fsS -o /dev/null "http://127.0.0.1:8087/" 2>/dev/null && break
        sleep 0.25
    done
else
    mkdir -p "${WORKDIR}/logs"
    nginx -p "${WORKDIR}" -c "${WORKDIR}/conf/nginx.conf" 2>/dev/null
    sleep 1
fi

HEADERS=$(curl -sS -D - -o /dev/null "http://127.0.0.1:8087/" 2>&1)
printf '%s\n' "$HEADERS" | sed 's/^/      /'

assert_contains "$HEADERS" "X-Content-Type-Options: nosniff" "X-Content-Type-Options: nosniff is sent"
assert_contains "$HEADERS" "X-Frame-Options: DENY" "X-Frame-Options: DENY is sent"
assert_contains "$HEADERS" "Referrer-Policy: strict-origin-when-cross-origin" "Referrer-Policy is sent"
assert_contains "$HEADERS" "Content-Security-Policy:" "a CSP is sent"

# HSTS must be commented out: enabling it before HTTPS works is unrecoverable.
assert_absent "$HEADERS" "Strict-Transport-Security" "HSTS is NOT sent (it ships commented out, by design)"

# --- the CSP itself, directive by directive --------------------------------
CSP=$(grep -i '^Content-Security-Policy:' <<<"$HEADERS" | tr -d '\r')
assert_contains "$CSP" "default-src 'self'"          "default-src 'self'"
assert_contains "$CSP" "script-src 'self'"           "script-src 'self'"
assert_contains "$CSP" "style-src 'self' 'unsafe-inline'" "style-src allows inline (App.jsx <style> + style={{}})"
assert_contains "$CSP" "img-src 'self' blob: data:"  "img-src allows blob: and data: (imagePrep decode + EXIF probe)"
assert_contains "$CSP" "font-src 'self'"             "font-src is 'self' only (fonts are not inlined — verified on the build)"
assert_contains "$CSP" "connect-src 'self' data:"    "connect-src allows data: (fetch() on the EXIF probe URI)"
assert_contains "$CSP" "worker-src 'self' blob:"     "worker-src allows blob: (service worker + heic2any)"
assert_contains "$CSP" "manifest-src 'self'"         "manifest-src 'self' (PWA manifest)"
assert_contains "$CSP" "object-src 'none'"           "object-src 'none'"
assert_contains "$CSP" "base-uri 'self'"             "base-uri 'self'"
assert_contains "$CSP" "form-action 'self'"          "form-action 'self'"
assert_contains "$CSP" "frame-ancestors 'none'"      "frame-ancestors 'none'"
# REQUIRED, and asserted positively so that removing it fails loudly. heic2any's
# libheif/embind glue calls `new Function` while registering types, inside a blob
# worker that inherits this policy. Without 'unsafe-eval' that worker dies during
# script evaluation, heic2any's promise NEVER SETTLES (it does not reject), the
# fallback in imagePrep.js never runs, and the serial upload queue stalls behind
# the HEIC forever. Measured in Chromium, both ways — see the long comment at the
# foot of nginx-security-headers.conf. Remove this only together with heic2any.
assert_contains "$CSP" "script-src 'self' 'unsafe-eval'" "script-src carries 'unsafe-eval' — heic2any hangs the upload queue without it"

# --- what must NOT be there ------------------------------------------------
assert_absent "$CSP" "fonts.googleapis.com" "no Google Fonts stylesheet origin (fonts are self-hosted via npm)"
assert_absent "$CSP" "fonts.gstatic.com"    "no Google Fonts file origin"
assert_absent "$CSP" "googleapis.com"       "no Google origin of any kind"
# Scoped to the script-src directive itself: a bare search for 'unsafe-inline'
# across the whole policy would match style-src, which legitimately carries it.
CSP_SCRIPT_SRC=$(grep -oE "script-src[^;]*" <<<"$CSP")
assert_absent "$CSP_SCRIPT_SRC" "'unsafe-inline'" "no 'unsafe-inline' in script-src (only style-src needs it)"
assert_absent "$CSP" "script-src 'self' 'unsafe-inline'" "script-src does not allow inline script"
assert_absent "$CSP" "font-src 'self' data:" "font-src does not need data: on the current build"

# ---------------------------------------------------------------------------
# The HSTS line ships commented out, so "it is absent" is not enough: a typo in
# a commented line is invisible until the day someone enables it on a live
# site. Uncomment it in a COPY and prove it is a working directive.
printf -- '\n--- the commented-out HSTS line, uncommented\n'
sed 's|^# add_header Strict-Transport-Security|add_header Strict-Transport-Security|' \
    "${WORKDIR}/conf/security-headers.conf" > "${WORKDIR}/conf/security-headers-hsts.conf"
if ! grep -q '^add_header Strict-Transport-Security' "${WORKDIR}/conf/security-headers-hsts.conf"; then
    bad "the snippet has no commented-out HSTS line to uncomment"
else
    ok "the snippet carries a commented-out HSTS line"
    if [[ "$RUNNER" == local ]]; then
        nginx -p "${WORKDIR}" -c "${WORKDIR}/conf/nginx.conf" -s quit 2>/dev/null || true
        sleep 0.5
        cp "${WORKDIR}/conf/security-headers-hsts.conf" "${WORKDIR}/etc/nginx/conf.d/security-headers.conf"
        htout=$(nginx -t -p "${WORKDIR}" -c "${WORKDIR}/conf/nginx.conf" 2>&1); hrc=$?
    else
        docker rm -f "$CONTAINER" >/dev/null 2>&1; CONTAINER=""
        htout=$(docker run --rm \
            -v "${WORKDIR}/conf/nginx.conf:/etc/nginx/nginx.conf:ro" \
            -v "${WORKDIR}/conf/security-headers-hsts.conf:/etc/nginx/conf.d/security-headers.conf:ro" \
            nginx:alpine nginx -t 2>&1); hrc=$?
    fi
    if (( hrc == 0 )); then ok "it parses once uncommented (nginx -t exits 0)"; else bad "nginx -t exited ${hrc} with HSTS enabled: ${htout}"; fi

    if [[ "$RUNNER" == docker ]]; then
        CONTAINER=$(docker run -d -p 127.0.0.1:8088:8087 \
            -v "${WORKDIR}/conf/nginx.conf:/etc/nginx/nginx.conf:ro" \
            -v "${WORKDIR}/conf/security-headers-hsts.conf:/etc/nginx/conf.d/security-headers.conf:ro" \
            -v "${WORKDIR}/html:/usr/share/nginx/html:ro" \
            nginx:alpine 2>/dev/null)
        for _ in $(seq 1 40); do
            curl -fsS -o /dev/null "http://127.0.0.1:8088/" 2>/dev/null && break
            sleep 0.25
        done
        HSTS_HEADERS=$(curl -sS -D - -o /dev/null "http://127.0.0.1:8088/" 2>&1)
    else
        nginx -p "${WORKDIR}" -c "${WORKDIR}/conf/nginx.conf" 2>/dev/null
        sleep 1
        HSTS_HEADERS=$(curl -sS -D - -o /dev/null "http://127.0.0.1:8087/" 2>&1)
        nginx -p "${WORKDIR}" -c "${WORKDIR}/conf/nginx.conf" -s quit 2>/dev/null || true
    fi
    assert_contains "$HSTS_HEADERS" "Strict-Transport-Security: max-age=63072000; includeSubDomains" \
        "it sends a well-formed HSTS header once uncommented"
fi

if [[ "$RUNNER" == local ]]; then
    nginx -p "${WORKDIR}" -c "${WORKDIR}/conf/nginx.conf" -s quit 2>/dev/null || true
fi

printf '\nRESULTS: %s passed, %s failed\n' "$PASS" "$FAIL"
(( FAIL == 0 )) || exit 1

#!/usr/bin/env bash
#
# ScanID — validates ops/nginx-security-headers.conf.
#
# Two levels of check, LOCAL ONLY. This never touches a real server, never
# reloads anything, and never reads the production vhost.
#
#   1. `nginx -t` against a minimal config that includes the snippet — proves it
#      parses and that every directive is legal where it is used.
#   2. Starts that nginx, requests a page FROM EACH OF THE TWO ZONES, and
#      asserts the headers actually arrive with the exact expected values —
#      because a config that parses can still send nothing (the add_header
#      inheritance trap the snippet warns about is precisely this class of bug).
#
# TWO ZONES, because one server now serves two different things:
#
#   /       the public site (frontend/site/), which needs Google Fonts, inline
#           <script> and Formspree — ops/nginx-site-csp.conf overrides
#           $scanid_csp for that location and adds no header of its own.
#   /app/   the application, which keeps the strict policy and must NOT inherit
#           one byte of the site's.
#
# Both zones are checked for the SAME four headers and for EXACTLY ONE CSP each.
# That last count is the point: the tempting fix — a second add_header in the
# location — parses fine, sends two policies, and browsers enforce their
# INTERSECTION, so the looser one silently does nothing.
#
# Uses a local nginx if there is one, otherwise a throwaway docker container.
#
set -uo pipefail

OPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SNIPPET="${OPS_DIR}/nginx-security-headers.conf"
SITE_SNIPPET="${OPS_DIR}/nginx-site-csp.conf"

PASS=0
FAIL=0
ok()  { PASS=$(( PASS + 1 )); printf '  \033[32mPASS\033[0m %s\n' "$1"; }
bad() { FAIL=$(( FAIL + 1 )); printf '  \033[31mFAIL\033[0m %s\n' "$1"; }
assert_contains() { if grep -qiF -- "$2" <<<"$1"; then ok "$3"; else bad "$3 -- not found: $2"; fi; }
assert_absent()   { if grep -qiF -- "$2" <<<"$1"; then bad "$3 -- unexpectedly present: $2"; else ok "$3"; fi; }

[[ -r "$SNIPPET" ]] || { printf 'snippet not found: %s\n' "$SNIPPET" >&2; exit 3; }
[[ -r "$SITE_SNIPPET" ]] || { printf 'snippet not found: %s\n' "$SITE_SNIPPET" >&2; exit 3; }

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/scanid-nginx-test.XXXXXX")"
trap 'rm -rf "$WORKDIR"; [[ -n "${CONTAINER:-}" ]] && docker rm -f "$CONTAINER" >/dev/null 2>&1' EXIT
CONTAINER=""

mkdir -p "${WORKDIR}/html/app" "${WORKDIR}/conf"
cp "$SNIPPET" "${WORKDIR}/conf/security-headers.conf"
cp "$SITE_SNIPPET" "${WORKDIR}/conf/site-csp.conf"
printf '<!doctype html><title>site</title>ok\n' > "${WORKDIR}/html/index.html"
printf '<!doctype html><title>app</title>ok\n' > "${WORKDIR}/html/app/index.html"

# A minimal vhost shaped like deploy/nginx-travelapp.conf: the headers snippet
# is included ONCE at server level, which is how it is meant to be used, and
# the site snippet ONCE inside `location /`, which is how IT is meant to be
# used. Neither location adds a header of its own — that is the whole design.
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
        location / {
            include /etc/nginx/conf.d/site-csp.conf;
            try_files $uri $uri/ =404;
        }
        location /app/ { try_files $uri $uri/ /app/index.html; }
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
        cp "${WORKDIR}/conf/security-headers.conf" "${WORKDIR}/conf/site-csp.conf" "${WORKDIR}/etc/nginx/conf.d/"
        nginx -t -p "${WORKDIR}" -c "${WORKDIR}/conf/nginx.conf" 2>&1
    else
        docker run --rm \
            -v "${WORKDIR}/conf/nginx.conf:/etc/nginx/nginx.conf:ro" \
            -v "${WORKDIR}/conf/security-headers.conf:/etc/nginx/conf.d/security-headers.conf:ro" \
            -v "${WORKDIR}/conf/site-csp.conf:/etc/nginx/conf.d/site-csp.conf:ro" \
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
        -v "${WORKDIR}/conf/site-csp.conf:/etc/nginx/conf.d/site-csp.conf:ro" \
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

# One request per zone. `/` is the public site, `/app/` is the application.
SITE_HEADERS=$(curl -sS -D - -o /dev/null "http://127.0.0.1:8087/" 2>&1)
APP_HEADERS=$(curl -sS -D - -o /dev/null "http://127.0.0.1:8087/app/" 2>&1)
printf '   ZONE / (site)\n'; printf '%s\n' "$SITE_HEADERS" | sed 's/^/      /'
printf '   ZONE /app/ (application)\n'; printf '%s\n' "$APP_HEADERS" | sed 's/^/      /'

# The four headers must reach BOTH zones. This is the add_header inheritance
# trap made into a test: `location /` includes a snippet, and if that snippet
# ever grew an add_header of its own, these three would silently vanish from
# the site while still passing for the application.
for zone in site app; do
    if [[ "$zone" == site ]]; then H="$SITE_HEADERS"; label="/"; else H="$APP_HEADERS"; label="/app/"; fi
    assert_contains "$H" "X-Content-Type-Options: nosniff" "${label} X-Content-Type-Options: nosniff is sent"
    assert_contains "$H" "X-Frame-Options: DENY" "${label} X-Frame-Options: DENY is sent"
    assert_contains "$H" "Referrer-Policy: strict-origin-when-cross-origin" "${label} Referrer-Policy is sent"
    assert_contains "$H" "Content-Security-Policy:" "${label} a CSP is sent"
    # HSTS must be commented out: enabling it before HTTPS works is unrecoverable.
    assert_absent "$H" "Strict-Transport-Security" "${label} HSTS is NOT sent (it ships commented out, by design)"

    # EXACTLY ONE CSP. Two are enforced as their intersection, not as the last
    # one written, so a second add_header in a location would leave the looser
    # policy inert and the page broken with nothing in the config to explain it.
    count=$(grep -ci '^Content-Security-Policy:' <<<"$H")
    if [[ "$count" == "1" ]]; then ok "${label} exactly one Content-Security-Policy header"
    else bad "${label} sends ${count} Content-Security-Policy headers, expected exactly 1"; fi

    # An EMPTY $scanid_csp makes nginx omit the header without complaining, so
    # "a CSP is sent" above would pass on a policy of nothing at all.
    value=$(grep -i '^Content-Security-Policy:' <<<"$H" | tr -d '\r' | sed 's/^[^:]*: *//')
    if [[ -n "$value" ]]; then ok "${label} the CSP value is not empty"
    else bad "${label} the CSP header is present but EMPTY (\$scanid_csp did not reach this location)"; fi
done

# --- the APPLICATION's CSP, directive by directive -------------------------
# Read from /app/, which is where the application is served. The site's own
# policy is asserted separately, further down.
CSP=$(grep -i '^Content-Security-Policy:' <<<"$APP_HEADERS" | tr -d '\r')
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
# The PUBLIC SITE's policy, and the fact that it stays on the public site.
# ---------------------------------------------------------------------------
printf -- '\n--- the site policy at / (ops/nginx-site-csp.conf)\n'
SITE_CSP=$(grep -i '^Content-Security-Policy:' <<<"$SITE_HEADERS" | tr -d '\r')

# What the site genuinely needs. Each of these is here because a real page
# breaks without it — see the reasoning in ops/nginx-site-csp.conf.
assert_contains "$SITE_CSP" "connect-src 'self' https://formspree.io" "/ connect-src allows the Formspree fetch (checklist.html)"
assert_contains "$SITE_CSP" "form-action 'self' https://formspree.io" "/ form-action allows the three posted lead forms"
assert_contains "$SITE_CSP" "style-src 'self' 'unsafe-inline'" "/ style-src allows the pages' inline <style> blocks"
assert_contains "$SITE_CSP" "font-src 'self'" "/ font-src is 'self' — the faces are self-hosted from /fonts/"
assert_contains "$SITE_CSP" "frame-ancestors 'none'" "/ frame-ancestors 'none' — the site is not framed either"
assert_contains "$SITE_CSP" "object-src 'none'" "/ object-src 'none'"
assert_contains "$SITE_CSP" "base-uri 'self'"   "/ base-uri 'self'"

# What the site is NOT granted — each of these was needed until the build
# started fixing the cause instead of widening the policy.
SITE_SCRIPT_SRC=$(grep -oE "script-src[^;]*" <<<"$SITE_CSP")
assert_absent "$SITE_SCRIPT_SRC" "'unsafe-inline'" "/ script-src refuses inline script (assemble-site.mjs externalises the two blocks)"
assert_absent "$SITE_CSP" "fonts.googleapis.com" "/ no Google Fonts stylesheet origin (self-hosted via @fontsource)"
assert_absent "$SITE_CSP" "fonts.gstatic.com"    "/ no Google Fonts file origin"
assert_absent "$SITE_CSP" "'unsafe-eval'" "/ no 'unsafe-eval' — nothing on the site evaluates a string"
assert_absent "$SITE_CSP" "blob:"         "/ no blob: — no site page creates an object URL or a worker"

# THE ISOLATION ASSERTIONS. These are the ones that fail if the two policies
# are ever wired the wrong way round, or if one leaks into the other.
assert_absent "$CSP" "fonts.googleapis.com" "/app/ does NOT inherit the site's Google Fonts origin"
assert_absent "$CSP" "fonts.gstatic.com"    "/app/ does NOT inherit the site's Google Fonts file origin"
assert_absent "$CSP" "formspree.io"         "/app/ does NOT inherit the site's Formspree origin"
APP_SCRIPT_SRC=$(grep -oE "script-src[^;]*" <<<"$CSP")
assert_absent "$APP_SCRIPT_SRC" "'unsafe-inline'" "/app/ script-src still refuses inline script"
assert_contains "$CSP" "'unsafe-eval'" "/app/ still carries 'unsafe-eval' (heic2any)"

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
        cp "${WORKDIR}/conf/site-csp.conf" "${WORKDIR}/etc/nginx/conf.d/"
        cp "${WORKDIR}/conf/security-headers-hsts.conf" "${WORKDIR}/etc/nginx/conf.d/security-headers.conf"
        htout=$(nginx -t -p "${WORKDIR}" -c "${WORKDIR}/conf/nginx.conf" 2>&1); hrc=$?
    else
        docker rm -f "$CONTAINER" >/dev/null 2>&1; CONTAINER=""
        htout=$(docker run --rm \
            -v "${WORKDIR}/conf/nginx.conf:/etc/nginx/nginx.conf:ro" \
            -v "${WORKDIR}/conf/security-headers-hsts.conf:/etc/nginx/conf.d/security-headers.conf:ro" \
            -v "${WORKDIR}/conf/site-csp.conf:/etc/nginx/conf.d/site-csp.conf:ro" \
            nginx:alpine nginx -t 2>&1); hrc=$?
    fi
    if (( hrc == 0 )); then ok "it parses once uncommented (nginx -t exits 0)"; else bad "nginx -t exited ${hrc} with HSTS enabled: ${htout}"; fi

    if [[ "$RUNNER" == docker ]]; then
        CONTAINER=$(docker run -d -p 127.0.0.1:8088:8087 \
            -v "${WORKDIR}/conf/nginx.conf:/etc/nginx/nginx.conf:ro" \
            -v "${WORKDIR}/conf/security-headers-hsts.conf:/etc/nginx/conf.d/security-headers.conf:ro" \
            -v "${WORKDIR}/conf/site-csp.conf:/etc/nginx/conf.d/site-csp.conf:ro" \
            -v "${WORKDIR}/html:/usr/share/nginx/html:ro" \
            nginx:alpine 2>/dev/null)
        for _ in $(seq 1 40); do
            curl -fsS -o /dev/null "http://127.0.0.1:8088/" 2>/dev/null && break
            sleep 0.25
        done
        HSTS_HEADERS=$(curl -sS -D - -o /dev/null "http://127.0.0.1:8088/" 2>&1)
        HSTS_APP_HEADERS=$(curl -sS -D - -o /dev/null "http://127.0.0.1:8088/app/" 2>&1)
    else
        nginx -p "${WORKDIR}" -c "${WORKDIR}/conf/nginx.conf" 2>/dev/null
        sleep 1
        HSTS_HEADERS=$(curl -sS -D - -o /dev/null "http://127.0.0.1:8087/" 2>&1)
        HSTS_APP_HEADERS=$(curl -sS -D - -o /dev/null "http://127.0.0.1:8087/app/" 2>&1)
        nginx -p "${WORKDIR}" -c "${WORKDIR}/conf/nginx.conf" -s quit 2>/dev/null || true
    fi
    # BOTH zones, for the same reason the other headers are checked twice: HSTS
    # protects a hostname, not a path, so a zone that silently dropped it would
    # leave the whole domain half-protected.
    assert_contains "$HSTS_HEADERS" "Strict-Transport-Security: max-age=63072000; includeSubDomains" \
        "/ sends a well-formed HSTS header once uncommented"
    assert_contains "$HSTS_APP_HEADERS" "Strict-Transport-Security: max-age=63072000; includeSubDomains" \
        "/app/ sends a well-formed HSTS header once uncommented"
fi

if [[ "$RUNNER" == local ]]; then
    nginx -p "${WORKDIR}" -c "${WORKDIR}/conf/nginx.conf" -s quit 2>/dev/null || true
fi

printf '\nRESULTS: %s passed, %s failed\n' "$PASS" "$FAIL"
(( FAIL == 0 )) || exit 1

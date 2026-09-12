#!/usr/bin/env bash
#
# ScanID — is the front end actually serving what this repository builds?
#
# READ-ONLY. It sends eight HTTPS requests and prints OK/FAIL. It changes
# nothing, needs no sudo, and never writes a file.
#
# WHAT IT IS FOR
# --------------
# The public site is served at / and the application at /app/, by
# deploy/nginx-travelapp.conf. That vhost is rsynced to the VPS by every deploy,
# but on this server the deploy account sudo rule covers only
# travelapp.service — it CANNOT reload nginx. So there is a window in which the
# new files are on disk and the old configuration is still loaded, and the two
# failures that causes are silent:
#
#   * the four Formspree lead forms are refused (form-action / connect-src),
#     so a visitor fills one in and gets an error;
#   * an unknown path answers 200 with the homepage instead of 404.html, which
#     search engines index as duplicates of the homepage.
#
# Nothing on the page looks wrong in either case. This script is how you tell.
#
# USAGE, on the VPS, after a deploy and after `sudo systemctl reload nginx`:
#
#     bash /opt/travelapp/ops/verify-front-end.sh
#
# It pins the name to the loopback with --resolve, so it tests THIS machine and
# the request never leaves it, while still presenting the right SNI — which
# means a passing run also proves the certificate and the 443 server block.
#
# Overrides, for a staging host or a local container:
#     HOST=scanid.fr PORT=443 TARGET=127.0.0.1 CURL_OPTS=-k bash verify-front-end.sh
#
set -uo pipefail

HOST="${HOST:-scanid.fr}"
PORT="${PORT:-443}"
TARGET="${TARGET:-127.0.0.1}"
CURL_OPTS="${CURL_OPTS:-}"

BASE="https://${HOST}"
[ "$PORT" = "443" ] || BASE="https://${HOST}:${PORT}"
RESOLVE="--resolve ${HOST}:${PORT}:${TARGET}"

FAILED=0
ok()   { printf '  \033[32mOK\033[0m   %s\n' "$1"; }
fail() { printf '  \033[31mFAIL\033[0m %s\n' "$1"; FAILED=1; }

# NOTE ON THE ABSENCE OF PIPELINES BELOW. Every check reads a response into a
# variable and greps it with a here-string, never `curl ... | grep -q`. With
# `pipefail` set, `grep -q` exits as soon as it matches, curl is killed by
# SIGPIPE, and the PIPELINE reports failure even though the match succeeded —
# so a passing check is reported as a failure. On small responses curl often
# finishes first and it passes anyway, which makes it worse than a plain bug:
# it is a race that reports a healthy server as broken, intermittently. This
# was hit for real while writing the script, on the 85 KB homepage.
# shellcheck disable=SC2086
code()    { curl -s $CURL_OPTS $RESOLVE -o /dev/null -w '%{http_code}' "${BASE}$1"; }
# shellcheck disable=SC2086
body()    { curl -s $CURL_OPTS $RESOLVE "${BASE}$1"; }
# shellcheck disable=SC2086
headers() { curl -sI $CURL_OPTS $RESOLVE "${BASE}$1" | tr -d '\r'; }

printf 'verifying %s (resolved to %s)\n\n' "$BASE" "$TARGET"

# --- What the build produces. These pass even before a reload, because they
#     depend on the FILES, which every deploy replaces. -----------------------
c=$(code /)
[ "$c" = "200" ] && ok "the site answers /" || fail "/ returned $c, expected 200"

root_html=$(body /)
grep -q 'href="/app/"' <<<"$root_html" \
  && ok "it is the assembled site (« Connexion » points at /app/)" \
  || fail "/ is not the assembled site — scripts/assemble-site.mjs did not run, or dist is stale"

c=$(code /app/)
[ "$c" = "200" ] && ok "the application answers /app/" || fail "/app/ returned $c, expected 200"

c=$(code /fonts/site.css)
[ "$c" = "200" ] && ok "the self-hosted typefaces are served" \
  || fail "/fonts/site.css returned $c — every page would fall back to a system font"

# --- What the CONFIGURATION produces. These are the two that stay wrong until
#     nginx is reloaded, and they are the reason this script exists. ----------
c=$(code /__verify_unknown_path)
[ "$c" = "404" ] && ok "an unknown path is a real 404" \
  || fail "an unknown path returned $c, expected 404   <-- nginx has NOT been reloaded"

site_headers=$(headers /)
grep -qi 'content-security-policy.*formspree' <<<"$site_headers" \
  && ok "the site policy is live (formspree.io allowed, so the lead forms work)" \
  || fail "the site policy is NOT live, so the four lead forms are refused   <-- nginx has NOT been reloaded"

# --- And the application must keep its own, stricter policy. -----------------
app_headers=$(headers /app/)
grep -qi "content-security-policy.*unsafe-eval" <<<"$app_headers" \
  && ok "the application keeps its own strict policy" \
  || fail "/app/ is not sending the application policy"

n=$(grep -ci '^content-security-policy' <<<"$site_headers")
[ "$n" = "1" ] && ok "exactly one Content-Security-Policy header" \
  || fail "$n Content-Security-Policy headers — two are enforced as their intersection"

echo
if [ "$FAILED" = "0" ]; then
    echo "  ALL CHECKS PASSED — the site, the application and both policies are live."
    exit 0
fi
cat <<'NEXT'
  Some checks failed.

  If the two "nginx has NOT been reloaded" lines are the only failures, the
  build is fine and the configuration simply is not loaded yet. From an account
  with sudo on this machine:

      sudo nginx -t && sudo systemctl reload nginx

  then run this script again. `nginx -t` is the safety gate: if it fails the
  reload never runs and nginx keeps serving from the configuration it already
  has, so the site cannot go down from that command.
NEXT
exit 1

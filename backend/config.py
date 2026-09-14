# /config.py
"""Environment-driven configuration.

Everything that differs between a developer's laptop and the VPS lives here and
is read from the environment, so the two behave differently without a code
change. Defaults are the *development* values: a missing variable must never
silently turn production hardening off, so the few settings where that would be
dangerous (see `is_production`) are keyed off one explicit variable.
"""
import os
from typing import List

# --- Environment ---------------------------------------------------------
# One variable decides every production behaviour. Anything that is not
# exactly "production" (case-insensitive) is treated as development, so a
# typo fails safe towards the *visible* configuration rather than silently
# shipping open docs.
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").strip().lower()


def is_production() -> bool:
    """True only in production. Read through the function, never cached at
    import time, so the test suite can flip the variable per test."""
    return os.getenv("ENVIRONMENT", "development").strip().lower() == "production"


def _env_list(name: str, default: str) -> List[str]:
    """A comma-separated environment variable as a list of non-empty items."""
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


# --- CORS ----------------------------------------------------------------
# A single origin in production, supplied by the environment. The development
# default keeps the Vite dev server (both ports, both host spellings) working
# exactly as before.
DEV_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174"


def cors_origins() -> List[str]:
    return _env_list("CORS_ORIGINS", DEV_ORIGINS)


# The methods and headers the frontend actually uses — no wildcard. GET/POST/
# PUT/DELETE are every verb in main.py; OPTIONS is the preflight itself.
CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
# Authorization is still listed: the Bearer header remains supported alongside
# the cookie so nothing that works today stops working.
CORS_HEADERS = ["Authorization", "Content-Type", "Accept", "X-Requested-With"]
CORS_EXPOSE_HEADERS = ["Content-Disposition"]


# --- Uploads -------------------------------------------------------------
# 15 MB, as the brief specifies. The upload card announces 10 Mo; the server
# limit sits above it so the announced figure is comfortably inside the hard
# limit rather than exactly on it.
MAX_UPLOAD_BYTES = _env_int("MAX_UPLOAD_BYTES", 15 * 1024 * 1024)


# --- Rate limiting -------------------------------------------------------
# Sized against the worst realistic batch, not the happy path.
#
#   The frontend queue (frontend/src/upload/uploadQueue.js) sends ONE request
#   per document and retries a transport failure twice: MAX_ATTEMPTS = 3.
#   A batch of 10 documents is therefore, worst case,
#       10 files x 3 attempts = 30 requests
#   inside the retry window (1 s + 3 s of backoff, so well under a minute).
#   A user who then hits « Réessayer les échecs » can legitimately spend
#   another 30. 120/minute is that worst case doubled again, which leaves
#   room for two people behind one agency NAT gateway uploading at once.
UPLOAD_RATE_LIMIT = os.getenv("UPLOAD_RATE_LIMIT", "120/minute")

# Login stays at the existing 5/minute per IP — unchanged, so no current
# behaviour moves — and per-account lockout is layered on top of it
# (see auth.py: an IP limit alone cannot stop a distributed guess against
# one account, and it punishes a whole agency behind one gateway).
LOGIN_RATE_LIMIT = os.getenv("LOGIN_RATE_LIMIT", "5/minute")
REGISTER_RATE_LIMIT = os.getenv("REGISTER_RATE_LIMIT", "5/minute")

# Per-account lockout: after this many consecutive failures the account is
# refused for the cooldown, regardless of which IP is asking.
LOGIN_MAX_FAILURES = _env_int("LOGIN_MAX_FAILURES", 10)
LOGIN_LOCKOUT_SECONDS = _env_int("LOGIN_LOCKOUT_SECONDS", 900)


# --- Session cookie ------------------------------------------------------
SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "scanid_session")

# A second, deliberately READABLE cookie carrying no secret — just the fact
# that this browser has a session. The real cookie is HttpOnly, so JavaScript
# can no longer tell "your session expired" from "you have never logged in";
# both are a 401 on /users/me. Without this marker the app would greet a
# returning user whose session lapsed with a blank login form instead of
# « Votre session a expiré », which is behaviour that existed before the
# cookie migration and must not be lost. It holds "1" and nothing else.
SESSION_HINT_COOKIE_NAME = os.getenv("SESSION_HINT_COOKIE_NAME", "scanid_has_session")
# Outlives the JWT on purpose: the marker's whole job is to still be there
# after the session it describes has expired.
SESSION_HINT_MAX_AGE = _env_int("SESSION_HINT_MAX_AGE", 30 * 24 * 3600)


def cookie_secure() -> bool:
    """`Secure` in production; off in development so plain-HTTP localhost can
    still log in. Overridable for a staging box that has TLS."""
    raw = os.getenv("SESSION_COOKIE_SECURE")
    if raw is not None:
        return raw.strip().lower() in ("1", "true", "yes", "on")
    return is_production()


SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "lax")


# --- Google Vision -------------------------------------------------------
# Data residency: French identity documents are processed in the EU. This is a
# commitment in the client DPA, so the endpoint is pinned rather than left to
# the library default (which is the global endpoint, vision.googleapis.com).
VISION_API_ENDPOINT = os.getenv("VISION_API_ENDPOINT", "eu-vision.googleapis.com")


# --- Public addresses ----------------------------------------------------
# Used to build the links that go out by email. Production values by default:
# a link in an email must never point at a developer's laptop by accident.
def app_public_url() -> str:
    return os.getenv("APP_PUBLIC_URL", "https://scanid.fr/app/")


def site_public_url() -> str:
    return os.getenv("SITE_PUBLIC_URL", "https://scanid.fr/")


# --- Email ---------------------------------------------------------------
# SMTP through the IONOS mailbox contact@scanid.fr (Spec v2): smtp.ionos.fr,
# port 587, STARTTLS, credentials in the environment only.
#
# MAIL_BACKEND picks how mail leaves:
#   smtp      real delivery (the default as soon as SMTP_HOST is set)
#   outbox    kept in memory (and written to MAIL_OUTBOX_DIR if set) — for
#             development and tests; the default outside production
#   disabled  nothing is sent; the default in production without SMTP_HOST,
#             so a missing configuration is visible instead of silent
def mail_backend() -> str:
    explicit = os.getenv("MAIL_BACKEND", "").strip().lower()
    if explicit in ("smtp", "outbox", "disabled"):
        return explicit
    if os.getenv("SMTP_HOST"):
        return "smtp"
    return "disabled" if is_production() else "outbox"


def smtp_settings() -> dict:
    return {
        "host": os.getenv("SMTP_HOST", ""),
        "port": _env_int("SMTP_PORT", 587),
        "username": os.getenv("SMTP_USERNAME", ""),
        "password": os.getenv("SMTP_PASSWORD", ""),
        "starttls": os.getenv("SMTP_STARTTLS", "1").strip().lower() in ("1", "true", "yes", "on"),
        "timeout": _env_int("SMTP_TIMEOUT_SECONDS", 20),
    }


def mail_from() -> str:
    return os.getenv("MAIL_FROM", "ScanID <contact@scanid.fr>")


def mail_admin_to() -> str:
    """Where trial requests and payment anomalies are reported (Alex)."""
    return os.getenv("MAIL_ADMIN_TO", "contact@scanid.fr")


# --- Password links ------------------------------------------------------
# « Mot de passe oublié ? » and the free-trial welcome email: 48 hours.
PASSWORD_TOKEN_HOURS = _env_int("PASSWORD_TOKEN_HOURS", 48)
FORGOT_PASSWORD_RATE_LIMIT = os.getenv("FORGOT_PASSWORD_RATE_LIMIT", "5/hour")
RESET_PASSWORD_RATE_LIMIT = os.getenv("RESET_PASSWORD_RATE_LIMIT", "10/hour")


# --- Free trial (Spec v2 §1) ---------------------------------------------
TRIAL_CREDITS = _env_int("TRIAL_CREDITS", 20)
# Pending and rejected requests are deleted after this many days (RGPD
# minimisation).
TRIAL_PURGE_DAYS = _env_int("TRIAL_PURGE_DAYS", 30)
TRIAL_RATE_LIMIT = os.getenv("TRIAL_RATE_LIMIT", "5/hour")


# --- Packs and Stripe (Spec v3) ------------------------------------------
# Prices HT in cents, from gestion/ScanID-Pilotage.xlsx « Stripe (à créer) »;
# TVA 20 % on top. The Payment Links default to the live ones published on
# scanid.fr; STRIPE_PAYMENT_LINK_<pack> points a pack at a test-mode link.
VAT_RATE_PERCENT = 20
CREDIT_VALIDITY_MONTHS = 12
PACK_PRICES_HT_CENTS = {100: 9_900, 1000: 69_000, 3000: 189_000, 5000: 295_000}
_DEFAULT_PAYMENT_LINKS = {
    100: "https://buy.stripe.com/9B64gy8XZfVycQFdiZebu00",
    1000: "https://buy.stripe.com/8x27sK0rtbFi8Apgvbebu01",
    3000: "https://buy.stripe.com/6oU8wOa2324I9Eta6Nebu02",
    5000: "https://buy.stripe.com/6oU14mdefaBe3g5gvbebu03",
}


def payment_link(pack: int) -> str:
    return os.getenv(f"STRIPE_PAYMENT_LINK_{pack}", _DEFAULT_PAYMENT_LINKS[pack])


def stripe_webhook_secret() -> str:
    return os.getenv("STRIPE_WEBHOOK_SECRET", "").strip()


STRIPE_WEBHOOK_TOLERANCE_SECONDS = _env_int("STRIPE_WEBHOOK_TOLERANCE_SECONDS", 300)
SIGNUP_RATE_LIMIT = os.getenv("SIGNUP_RATE_LIMIT", "5/minute")


# --- Session lifetime ----------------------------------------------------
# A session ends after this long WITHOUT USER ACTIVITY: the app renews it
# (POST /session/refresh) only when the person actually uses the page, never
# for background polling. 12 hours (action list, 14/09/2026).
SESSION_IDLE_MINUTES = _env_int("SESSION_IDLE_MINUTES", 12 * 60)

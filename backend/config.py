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

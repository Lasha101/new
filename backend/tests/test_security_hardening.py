"""Package C — the hardening itself: docs, CORS, auth, rate limits, errors.

`is_production()` is read through a function rather than captured at import, so
these tests can flip ENVIRONMENT per case. The app object, however, decides its
docs routes when it is CONSTRUCTED, so the production-docs case builds a second
app in a subprocess with the variable already set — patching after the fact
would prove nothing about how the real server starts.
"""
import json
import logging
import os
import subprocess
import sys

import pytest
from fastapi.testclient import TestClient

import auth
import config
from tests.helpers import auth_headers, make_user

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOOD_PASSWORD = "Girafe!!12Nuage"


# --- Step 2: the docs are closed in production ---------------------------

def test_docs_are_open_in_development(client):
    for path in ("/docs", "/redoc", "/openapi.json"):
        response = client.get(path)
        assert response.status_code == 200, f"{path} should be reachable in development"


def _routes_in_environment(environment: str):
    """Imports main.py in a fresh interpreter with ENVIRONMENT set and reports
    which documentation routes the app registered."""
    script = (
        "import os, json;"
        "os.environ['DATABASE_URL']='sqlite://';"
        "import main;"
        "print(json.dumps({"
        "'docs': main.app.docs_url,"
        "'redoc': main.app.redoc_url,"
        "'openapi': main.app.openapi_url,"
        "'paths': [r.path for r in main.app.routes]}))"
    )
    env = dict(os.environ, ENVIRONMENT=environment, PYTHONPATH=BACKEND_DIR)
    output = subprocess.run(
        [sys.executable, "-c", script], cwd=BACKEND_DIR, env=env,
        capture_output=True, text=True, timeout=180,
    )
    assert output.returncode == 0, output.stderr[-3000:]
    return json.loads(output.stdout.strip().splitlines()[-1])


def test_the_three_doc_routes_do_not_exist_in_production():
    """404 rather than 401: the routes are not registered at all, so there is
    nothing behind them to probe."""
    result = _routes_in_environment("production")
    assert result["docs"] is None
    assert result["redoc"] is None
    assert result["openapi"] is None
    for path in ("/docs", "/redoc", "/openapi.json"):
        assert path not in result["paths"], f"{path} is still registered in production"


def test_the_doc_routes_do_exist_in_development():
    result = _routes_in_environment("development")
    assert result["docs"] == "/docs"
    assert result["redoc"] == "/redoc"
    assert result["openapi"] == "/openapi.json"


def test_an_unrecognised_environment_value_is_not_production():
    """A typo must not silently disable the hardening... and must not silently
    enable it either. `is_production` is exact-match, so anything else is
    development, which is the visible, debuggable state."""
    for value in ("Production ", "PRODUCTION", "prod", "", "staging"):
        os.environ["ENVIRONMENT"] = value
        try:
            assert config.is_production() is (value.strip().lower() == "production")
        finally:
            os.environ.pop("ENVIRONMENT", None)


# --- Step 3: CORS --------------------------------------------------------

def test_the_configured_origin_is_accepted(client):
    origin = config.cors_origins()[0]
    response = client.options(
        "/token",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code in (200, 204)
    assert response.headers.get("access-control-allow-origin") == origin


def test_a_disallowed_origin_is_refused(client):
    response = client.options(
        "/token",
        headers={
            "Origin": "https://evil.example.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    # Starlette answers the preflight, but without the allow-origin header the
    # browser refuses the real request — which is the enforcement point.
    assert response.headers.get("access-control-allow-origin") != "https://evil.example.com"


def test_no_response_ever_carries_a_wildcard_origin(client, db_session):
    make_user(db_session, "corsuser")
    origin = config.cors_origins()[0]
    for method, path in (("get", "/users/me"), ("get", "/ocr/jobs/"), ("get", "/destinations/")):
        response = getattr(client, method)(
            path, headers={**auth_headers("corsuser"), "Origin": origin}
        )
        assert response.headers.get("access-control-allow-origin") != "*", (
            f"{path} returned a wildcard origin, which cannot be combined with credentials"
        )


def test_the_method_and_header_allow_lists_are_not_wildcards():
    assert "*" not in config.CORS_METHODS
    assert "*" not in config.CORS_HEADERS
    # Every verb main.py actually implements is present.
    for verb in ("GET", "POST", "PUT", "DELETE"):
        assert verb in config.CORS_METHODS


# --- Step 6: authentication ---------------------------------------------

def test_a_new_account_stores_an_argon2_hash(client, db_session):
    response = client.post("/users/register", json={
        "first_name": "Arg", "last_name": "On", "email": "argon@example.com",
        "phone_number": "0600000000", "user_name": "argonuser", "password": GOOD_PASSWORD,
    })
    assert response.status_code == 200, response.text

    import crud
    stored = crud.get_user_by_username(db_session, username="argonuser")
    assert stored["hashed_password"].startswith("$argon2"), stored["hashed_password"][:20]


def test_a_new_account_can_log_in_and_a_wrong_password_cannot(client, db_session):
    client.post("/users/register", json={
        "first_name": "Log", "last_name": "In", "email": "login@example.com",
        "phone_number": "0600000000", "user_name": "loginuser", "password": GOOD_PASSWORD,
    })

    ok = client.post("/token", data={"username": "loginuser", "password": GOOD_PASSWORD})
    assert ok.status_code == 200, ok.text
    assert ok.json()["token_type"] == "bearer"
    assert ok.json()["access_token"]

    bad = client.post("/token", data={"username": "loginuser", "password": GOOD_PASSWORD + "x"})
    assert bad.status_code == 401


def test_the_session_cookie_carries_all_three_flags(client, db_session):
    client.post("/users/register", json={
        "first_name": "Cook", "last_name": "Ie", "email": "cookie@example.com",
        "phone_number": "0600000000", "user_name": "cookieuser", "password": GOOD_PASSWORD,
    })
    os.environ["SESSION_COOKIE_SECURE"] = "1"   # force the production flag
    try:
        response = client.post("/token", data={"username": "cookieuser", "password": GOOD_PASSWORD})
    finally:
        os.environ.pop("SESSION_COOKIE_SECURE", None)

    assert response.status_code == 200
    raw = response.headers.get("set-cookie", "")
    assert config.SESSION_COOKIE_NAME in raw
    assert "HttpOnly" in raw
    assert "Secure" in raw
    assert "SameSite=lax" in raw.replace("samesite=lax", "SameSite=lax")


def test_a_readable_marker_cookie_accompanies_the_session(client, db_session):
    """The session cookie is HttpOnly, so JavaScript can no longer tell an
    expired session from a first visit — both are a 401. A second, readable
    cookie carrying only "1" restores that distinction without exposing
    anything: it is what keeps « Votre session a expiré » working."""
    client.post("/users/register", json={
        "first_name": "Hint", "last_name": "Cookie", "email": "hint@example.com",
        "phone_number": "0600000000", "user_name": "hintuser", "password": GOOD_PASSWORD,
    })
    response = client.post("/token", data={"username": "hintuser", "password": GOOD_PASSWORD})
    assert response.status_code == 200

    raw = response.headers.get("set-cookie", "")
    assert config.SESSION_HINT_COOKIE_NAME in raw

    # It must NOT be HttpOnly — being readable is its whole purpose...
    hint_directives = [
        chunk for chunk in raw.split(",")
        if f"{config.SESSION_HINT_COOKIE_NAME}=" in chunk
    ]
    assert hint_directives, raw
    assert "HttpOnly" not in hint_directives[0]

    # ...and it must carry no secret.
    token = response.json()["access_token"]
    assert token not in hint_directives[0]
    assert client.cookies.get(config.SESSION_HINT_COOKIE_NAME) == "1"


def test_logout_clears_the_marker_cookie_too(client, db_session):
    client.post("/users/register", json={
        "first_name": "Hint", "last_name": "Out", "email": "hintout@example.com",
        "phone_number": "0600000000", "user_name": "hintout", "password": GOOD_PASSWORD,
    })
    client.post("/token", data={"username": "hintout", "password": GOOD_PASSWORD})
    assert client.cookies.get(config.SESSION_HINT_COOKIE_NAME) == "1"

    client.post("/logout")
    assert not client.cookies.get(config.SESSION_HINT_COOKIE_NAME)


def test_the_cookie_alone_authenticates_a_request(client, db_session):
    """No Authorization header anywhere: the cookie the login set is the only
    credential, which is what makes an HttpOnly session possible."""
    client.post("/users/register", json={
        "first_name": "Only", "last_name": "Cookie", "email": "onlyc@example.com",
        "phone_number": "0600000000", "user_name": "onlycookie", "password": GOOD_PASSWORD,
    })
    login = client.post("/token", data={"username": "onlycookie", "password": GOOD_PASSWORD})
    assert login.status_code == 200

    me = client.get("/users/me")           # TestClient keeps the cookie jar
    assert me.status_code == 200, me.text
    assert me.json()["user_name"] == "onlycookie"
    assert "authorization" not in {k.lower() for k in me.request.headers}


def test_the_bearer_header_still_works(client, db_session):
    """Functionality preservation: every existing client authenticates with a
    header, and must keep doing so."""
    make_user(db_session, "bearer_user")
    response = client.get("/users/me", headers=auth_headers("bearer_user"))
    assert response.status_code == 200
    assert response.json()["user_name"] == "bearer_user"


def test_logout_clears_the_cookie(client, db_session):
    client.post("/users/register", json={
        "first_name": "Bye", "last_name": "Bye", "email": "bye@example.com",
        "phone_number": "0600000000", "user_name": "byeuser", "password": GOOD_PASSWORD,
    })
    client.post("/token", data={"username": "byeuser", "password": GOOD_PASSWORD})
    assert client.get("/users/me").status_code == 200

    out = client.post("/logout")
    assert out.status_code == 200
    assert client.get("/users/me").status_code == 401


def test_no_credential_at_all_is_refused(client):
    assert client.get("/users/me").status_code == 401


# --- Step 4: rate limiting and lockout -----------------------------------

def test_repeated_failures_lock_the_account_and_the_lock_clears(db_session):
    """The per-account counter, exercised directly: going through the endpoint
    would hit the 5/minute per-IP limit first and prove nothing about it."""
    name = "lockme"
    auth.reset_login_failures(name)
    try:
        for _ in range(config.LOGIN_MAX_FAILURES - 1):
            auth.record_login_failure(name)
        assert auth.is_locked_out(name) is False, "locked one failure too early"

        auth.record_login_failure(name)
        assert auth.is_locked_out(name) is True, "the account should be locked"

        # A successful login clears it — this is how the lock is released.
        auth.reset_login_failures(name)
        assert auth.is_locked_out(name) is False
    finally:
        auth.reset_login_failures(name)


def test_the_lockout_window_expires(monkeypatch):
    name = "expiry"
    auth.reset_login_failures(name)
    try:
        for _ in range(config.LOGIN_MAX_FAILURES):
            auth.record_login_failure(name)
        assert auth.is_locked_out(name) is True

        # Advance past the cooldown.
        real_time = auth.time.time
        monkeypatch.setattr(auth.time, "time", lambda: real_time() + config.LOGIN_LOCKOUT_SECONDS + 1)
        assert auth.is_locked_out(name) is False
    finally:
        auth.reset_login_failures(name)


def test_a_locked_account_is_refused_by_the_endpoint(client, db_session, monkeypatch):
    make_user(db_session, "locked_user")
    monkeypatch.setattr(auth, "is_locked_out", lambda username: username == "locked_user")
    response = client.post("/token", data={"username": "locked_user", "password": "whatever"})
    assert response.status_code == 429
    assert "Trop de tentatives" in response.json()["detail"]


def test_the_upload_limit_is_sized_for_a_ten_file_batch_with_retries():
    """The arithmetic, asserted rather than described.

    The frontend queue sends one request per document and retries a transport
    failure twice (MAX_ATTEMPTS = 3 in uploadQueue.js). Ten documents is
    therefore 30 requests inside the retry window, and a « Réessayer les
    échecs » pass is 30 more.
    """
    limit, _, period = config.UPLOAD_RATE_LIMIT.partition("/")
    assert period == "minute"
    worst_case_batch = 10 * 3          # 10 files x 3 attempts
    assert int(limit) >= worst_case_batch * 2, (
        f"{config.UPLOAD_RATE_LIMIT} throttles a legitimate batch: "
        f"a 10-file upload with retries is {worst_case_batch} requests, "
        f"and a retry-failed pass doubles it"
    )


def test_the_login_limit_is_unchanged():
    """5/minute is what the app shipped with; the lockout is layered on top
    rather than replacing it, so no current behaviour moves."""
    assert config.LOGIN_RATE_LIMIT == "5/minute"


# --- Step 9: errors do not leak ------------------------------------------

def test_an_internal_error_returns_a_generic_body_and_logs_the_detail(tolerant_client, db_session, monkeypatch, caplog):
    make_user(db_session, "boom_user")

    marker = "SECRET_INTERNAL_DETAIL_9f3a"

    def explode(*args, **kwargs):
        raise RuntimeError(marker)

    import crud as crud_module
    monkeypatch.setattr(crud_module, "get_user_ocr_jobs", explode)

    with caplog.at_level(logging.ERROR):
        response = tolerant_client.get("/ocr/jobs/", headers=auth_headers("boom_user"))

    assert response.status_code == 500
    body = response.text
    # Generic French message out...
    assert "Une erreur interne est survenue" in body
    # ...with no stack trace and no internal detail.
    assert marker not in body
    assert "Traceback" not in body
    assert "RuntimeError" not in body
    assert BACKEND_DIR not in body
    # ...while the detail does reach the log.
    assert marker in caplog.text

"""Rate limits on login and upload (action list item 9), exercised over HTTP.

test_security_hardening.py asserts the configured values and the per-account
lockout; these prove the per-IP limits are actually enforced by the endpoints."""
import io

import config
from tests.helpers import make_user, auth_headers


def _limit(value):
    count, _, period = value.partition("/")
    return int(count), period


def test_login_is_refused_past_5_attempts_per_minute(client, db_session):
    assert _limit(config.LOGIN_RATE_LIMIT) == (5, "minute")
    make_user(db_session, "guessed")
    for _ in range(5):
        assert client.post("/token", data={"username": "guessed", "password": "wrong"}).status_code == 401
    # The sixth attempt within the minute is refused before the password is even
    # checked — the right password included. (The account lockout needs 10.)
    assert client.post("/token", data={"username": "guessed", "password": "secret-pass"}).status_code == 429


def test_upload_is_refused_past_120_requests_per_minute(client, db_session):
    limit, period = _limit(config.UPLOAD_RATE_LIMIT)
    assert (limit, period) == (120, "minute")
    # No credits: every request is counted by the limiter, then answered 403 at
    # once, so the limit is reached without running a single extraction.
    make_user(db_session, "flooder", page_credits=0)
    headers = auth_headers("flooder")

    def upload():
        return client.post("/passports/upload-and-extract/", headers=headers,
                           files={"file": ("page.jpg", io.BytesIO(b"\xff\xd8\xff"), "image/jpeg")})

    for _ in range(limit):
        assert upload().status_code == 403
    assert upload().status_code == 429

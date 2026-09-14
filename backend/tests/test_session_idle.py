"""Automatic logout after 12 hours of inactivity (action list item 9).

A session lasts SESSION_IDLE_MINUTES after it was last renewed, and only the
app's POST /session/refresh — sent when the person actually uses the page —
renews it. A session left alone past that has expired and cannot be revived."""
from datetime import datetime, timedelta, timezone

from jose import jwt

import auth
import config
import models
import crud
from tests.helpers import make_user

TWELVE_HOURS = 12 * 60 * 60


def _claims(token):
    return jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])


def _seconds_left(token):
    return _claims(token)["exp"] - datetime.now(timezone.utc).timestamp()


def _session_cookie_header(response):
    return next(value for value in response.headers.get_list("set-cookie")
                if value.startswith(f"{config.SESSION_COOKIE_NAME}="))


def test_the_session_lasts_12_hours_from_login(client, db_session):
    assert config.SESSION_IDLE_MINUTES == 12 * 60
    make_user(db_session, "idle")
    response = client.post("/token", data={"username": "idle", "password": "secret-pass"})
    assert response.status_code == 200
    assert TWELVE_HOURS - 60 < _seconds_left(response.json()["access_token"]) <= TWELVE_HOURS
    assert f"Max-Age={TWELVE_HOURS}" in _session_cookie_header(response)


def test_activity_renews_the_session_for_another_12_hours(client, db_session):
    make_user(db_session, "active")
    # A session issued almost 12 hours ago: one minute left.
    ageing = auth.create_access_token(data={"sub": "active", "sv": 0}, expires_delta=timedelta(minutes=1))
    response = client.post("/session/refresh", headers={"Authorization": f"Bearer {ageing}"})
    assert response.status_code == 200
    renewed = response.json()["access_token"]
    assert TWELVE_HOURS - 60 < _seconds_left(renewed) <= TWELVE_HOURS
    assert _claims(renewed)["sub"] == "active" and _claims(renewed)["sv"] == 0
    cookie = _session_cookie_header(response)
    assert f"Max-Age={TWELVE_HOURS}" in cookie and "HttpOnly" in cookie
    # The browser now holds the renewed cookie, and it alone authenticates.
    assert client.cookies.get(config.SESSION_COOKIE_NAME) == renewed
    assert client.get("/users/me").json()["user_name"] == "active"


def test_after_12_hours_without_activity_the_session_is_over(client, db_session):
    make_user(db_session, "gone")
    expired = auth.create_access_token(data={"sub": "gone", "sv": 0}, expires_delta=timedelta(seconds=-1))
    client.cookies.set(config.SESSION_COOKIE_NAME, expired)
    assert client.get("/users/me").status_code == 401
    # Too late to renew it: only a new login opens a session.
    assert client.post("/session/refresh").status_code == 401
    assert client.post("/session/refresh", headers={"Authorization": f"Bearer {expired}"}).status_code == 401


def test_refresh_requires_a_session_and_respects_its_rules(client, db_session):
    assert client.post("/session/refresh").status_code == 401

    user = make_user(db_session, "rules")
    token = auth.create_access_token(data=auth.session_claims(user))
    headers = {"Authorization": f"Bearer {token}"}
    assert client.post("/session/refresh", headers=headers).status_code == 200

    # A password reset (session version raised) ends the session; refresh cannot keep it alive.
    row = db_session.get(models.User, user["id"])
    row.session_version = 1
    db_session.commit()
    assert client.post("/session/refresh", headers=headers).status_code == 401

    # Nor can a session on an account that is no longer active.
    fresh = auth.create_access_token(data=auth.session_claims(crud.get_user_by_username(db_session, "rules")))
    row.status = "rejected"
    db_session.commit()
    assert client.post("/session/refresh", headers={"Authorization": f"Bearer {fresh}"}).status_code == 401

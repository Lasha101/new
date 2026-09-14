"""The account foundation the action list of 14/09/2026 builds on: the additive
schema migration, account status, session versions, one-time password links and
the mailer."""
import logging
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.pool import StaticPool

import account_tokens
import auth
import config
import crud
import mailer
import models
import schema_migrations
from tests.helpers import make_user, auth_headers


# --- Schema migration ----------------------------------------------------------

def _old_users_table(engine):
    """The users table exactly as production has it before this change."""
    with engine.begin() as connection:
        connection.execute(text(
            "CREATE TABLE users (id VARCHAR(36) PRIMARY KEY, first_name VARCHAR NOT NULL, "
            "last_name VARCHAR NOT NULL, email VARCHAR NOT NULL UNIQUE, phone_number VARCHAR NOT NULL, "
            "user_name VARCHAR NOT NULL UNIQUE, hashed_password VARCHAR NOT NULL, role VARCHAR NOT NULL, "
            "uploaded_pages_count INTEGER NOT NULL, page_credits INTEGER)"))
        connection.execute(text(
            "INSERT INTO users VALUES ('u1', 'Alex', 'Client', 'alex@example.com', '0600000000', "
            "'alex', 'hash', 'user', 1, 29)"))


def test_migration_adds_the_new_columns_to_an_existing_users_table():
    engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
    _old_users_table(engine)
    models.Base.metadata.create_all(engine)          # what startup does first: new tables only

    added = schema_migrations.add_missing_columns(engine)

    assert set(added) == {f"users.{c}" for _, c, _ in schema_migrations.ADDED_COLUMNS}
    columns = {c["name"] for c in inspect(engine).get_columns("users")}
    assert columns >= {c.name for c in models.User.__table__.columns}
    with engine.connect() as connection:
        row = connection.execute(text("SELECT status, session_version, page_credits, company FROM users")).one()
    assert tuple(row) == ("active", 0, 29, None)      # the existing account keeps working
    assert schema_migrations.add_missing_columns(engine) == []   # idempotent
    for table in ("trial_requests", "purchases", "auth_tokens"):
        assert table in inspect(engine).get_table_names()


def test_migration_is_a_no_op_on_a_fresh_schema(db_session):
    assert schema_migrations.add_missing_columns(db_session.get_bind()) == []


# --- Account status and session versions -----------------------------------------

def _login(client, user_name, password="secret-pass"):
    return client.post("/token", data={"username": user_name, "password": password})


def test_only_an_active_account_can_log_in_or_use_a_session(client, db_session):
    make_user(db_session, "waiting")
    assert _login(client, "waiting").status_code == 200
    for status in ("pending", "rejected"):
        row = db_session.get(models.User, crud.get_user_by_username(db_session, "waiting")["id"])
        row.status = status
        db_session.commit()
        response = _login(client, "waiting")
        assert response.status_code == 401
        assert response.json()["detail"] == "Nom d'utilisateur ou mot de passe incorrect"
        assert client.get("/users/me", headers=auth_headers("waiting")).status_code == 401


def test_a_token_from_before_session_versions_still_works(client, db_session):
    make_user(db_session, "legacy")
    old_style = auth.create_access_token(data={"sub": "legacy"})     # no "sv" claim
    assert client.get("/users/me", headers={"Authorization": f"Bearer {old_style}"}).status_code == 200


def test_raising_the_session_version_ends_existing_sessions(client, db_session):
    user = make_user(db_session, "rotated")
    token = _login(client, "rotated").json()["access_token"]
    assert client.get("/users/me", headers={"Authorization": f"Bearer {token}"}).status_code == 200
    row = db_session.get(models.User, user["id"])
    row.session_version = 1
    db_session.commit()
    assert client.get("/users/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401
    fresh = _login(client, "rotated").json()["access_token"]
    assert client.get("/users/me", headers={"Authorization": f"Bearer {fresh}"}).status_code == 200


# --- One-time password links -------------------------------------------------------

def test_a_link_token_is_stored_hashed_and_works_once(db_session):
    user = make_user(db_session, "linked")
    raw = account_tokens.issue(db_session, user["id"], account_tokens.PURPOSE_RESET)

    stored = db_session.query(models.AuthToken).one()
    assert raw not in stored.token_hash and len(stored.token_hash) == 64
    found = account_tokens.find_valid(db_session, raw)
    assert found["user"]["id"] == user["id"]

    account_tokens.consume(db_session, found["token"], auth.get_password_hash("Nouveau!!Mot42"))
    assert account_tokens.find_valid(db_session, raw) is None          # used
    refreshed = crud.get_user(db_session, user["id"])
    assert auth.verify_password("Nouveau!!Mot42", refreshed["hashed_password"])
    assert refreshed["session_version"] == 1                          # other sessions ended


def test_a_new_link_revokes_the_previous_one(db_session):
    user = make_user(db_session, "twice")
    first = account_tokens.issue(db_session, user["id"], account_tokens.PURPOSE_RESET)
    second = account_tokens.issue(db_session, user["id"], account_tokens.PURPOSE_RESET)
    assert account_tokens.find_valid(db_session, first) is None
    assert account_tokens.find_valid(db_session, second) is not None


def test_a_link_expires_after_48_hours(db_session):
    assert config.PASSWORD_TOKEN_HOURS == 48
    user = make_user(db_session, "late")
    raw = account_tokens.issue(db_session, user["id"], account_tokens.PURPOSE_SET)
    row = db_session.query(models.AuthToken).one()
    assert timedelta(hours=47, minutes=59) < (row.expires_at - row.created_at) <= timedelta(hours=48)
    row.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db_session.commit()
    assert account_tokens.find_valid(db_session, raw) is None


def test_a_link_for_an_inactive_account_is_refused(db_session):
    user = make_user(db_session, "dormant")
    raw = account_tokens.issue(db_session, user["id"], account_tokens.PURPOSE_RESET)
    db_session.get(models.User, user["id"]).status = "pending"
    db_session.commit()
    assert account_tokens.find_valid(db_session, raw) is None
    assert account_tokens.find_valid(db_session, "") is None
    assert account_tokens.find_valid(db_session, "not-a-token") is None


# --- Mailer ----------------------------------------------------------------------

@pytest.fixture()
def outbox(monkeypatch):
    monkeypatch.setenv("MAIL_BACKEND", "outbox")
    mailer.OUTBOX.clear()
    yield mailer.OUTBOX
    mailer.OUTBOX.clear()


def test_backend_selection(monkeypatch):
    for name in ("MAIL_BACKEND", "SMTP_HOST", "ENVIRONMENT"):
        monkeypatch.delenv(name, raising=False)
    assert config.mail_backend() == "outbox" and mailer.is_configured()
    monkeypatch.setenv("ENVIRONMENT", "production")
    assert config.mail_backend() == "disabled" and not mailer.is_configured()   # visible, not silent
    monkeypatch.setenv("SMTP_HOST", "smtp.ionos.fr")
    assert config.mail_backend() == "smtp" and mailer.is_configured()


def test_smtp_uses_starttls_and_login_and_logs_no_content(monkeypatch, caplog):
    calls = []

    class FakeSMTP:
        def __init__(self, host, port, timeout):
            calls.append(("connect", host, port))
        def __enter__(self):
            return self
        def __exit__(self, *exc):
            return False
        def starttls(self, context):
            calls.append(("starttls",))
        def login(self, username, password):
            calls.append(("login", username))
        def send_message(self, message):
            calls.append(("send", message["To"], message["Subject"], message.get_content()))

    monkeypatch.setattr(mailer.smtplib, "SMTP", FakeSMTP)
    monkeypatch.setenv("MAIL_BACKEND", "smtp")
    monkeypatch.setenv("SMTP_HOST", "smtp.ionos.fr")
    monkeypatch.setenv("SMTP_USERNAME", "contact@scanid.fr")
    monkeypatch.setenv("SMTP_PASSWORD", "not-logged")
    caplog.set_level(logging.INFO)

    assert mailer.send("client@agence.fr", "Sujet secret", "https://scanid.fr/app/mot-de-passe#token=abc", kind="reset")

    assert calls[0] == ("connect", "smtp.ionos.fr", 587)
    assert ("starttls",) in calls and ("login", "contact@scanid.fr") in calls
    assert calls[-1][1:3] == ("client@agence.fr", "Sujet secret")
    for leaked in ("client@agence.fr", "Sujet secret", "token=abc", "not-logged"):
        assert leaked not in caplog.text


def test_a_failing_smtp_server_never_raises(monkeypatch, caplog):
    def boom(*args, **kwargs):
        raise OSError("connection refused to client@agence.fr")
    monkeypatch.setattr(mailer.smtplib, "SMTP", boom)
    monkeypatch.setenv("MAIL_BACKEND", "smtp")
    monkeypatch.setenv("SMTP_HOST", "smtp.ionos.fr")
    assert mailer.send("client@agence.fr", "S", "B", kind="welcome") is False
    assert "client@agence.fr" not in caplog.text


def test_outbox_keeps_the_email(outbox):
    assert mailer.send("a@b.fr", "Objet", "Corps", kind="test")
    assert [(e.to, e.subject, e.body, e.kind) for e in outbox] == [("a@b.fr", "Objet", "Corps", "test")]

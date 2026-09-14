"""« Mot de passe oublié ? » → email with a 48-hour link → new password.

All identities in this file are fictional."""
import logging
import re
from datetime import datetime, timedelta, timezone

import pytest

import mailer
import models
from tests.helpers import make_user

STRONG = "Girafe!!12Nuage"
GENERIC = ("Si un compte correspond à cet identifiant, un email contenant un lien de réinitialisation "
           "vient de lui être envoyé. Le lien est valable 48 heures.")


@pytest.fixture(autouse=True)
def outbox(monkeypatch):
    monkeypatch.setenv("MAIL_BACKEND", "outbox")
    monkeypatch.setenv("APP_PUBLIC_URL", "https://scanid.fr/app/")
    mailer.OUTBOX.clear()
    yield mailer.OUTBOX
    mailer.OUTBOX.clear()


def _token_from(email) -> str:
    match = re.search(r"https://scanid\.fr/app/mot-de-passe#token=([A-Za-z0-9_-]+)", email.body)
    assert match, email.body
    return match.group(1)


def test_complete_flow_on_a_test_account(client, db_session, outbox, caplog):
    make_user(db_session, "oubli")
    caplog.set_level(logging.INFO)
    before = client.post("/token", data={"username": "oubli", "password": "secret-pass"}).json()["access_token"]

    response = client.post("/auth/forgot-password", json={"identifier": "oubli@example.com"})
    assert response.status_code == 200 and response.json()["detail"] == GENERIC

    assert len(outbox) == 1
    email = outbox[0]
    assert email.to == "oubli@example.com"
    assert email.subject == "Réinitialisation de votre mot de passe ScanID"
    assert "valable 48 heures" in email.body and "Votre identifiant : oubli" in email.body
    token = _token_from(email)
    assert token not in caplog.text                                     # the link is a credential

    weak = client.post("/auth/reset-password", json={"token": token, "password": "court"})
    assert weak.status_code == 422                                      # the usual password policy
    done = client.post("/auth/reset-password", json={"token": token, "password": STRONG})
    assert done.status_code == 200, done.text
    assert done.json()["user_name"] == "oubli"

    assert client.post("/token", data={"username": "oubli", "password": STRONG}).status_code == 200
    assert client.post("/token", data={"username": "oubli", "password": "secret-pass"}).status_code == 401
    assert client.get("/users/me", headers={"Authorization": f"Bearer {before}"}).status_code == 401   # old session ended

    again = client.post("/auth/reset-password", json={"token": token, "password": "Autre!!Mot42Long"})
    assert again.status_code == 400                                     # single use
    assert "n'est plus valide" in again.json()["detail"]


def test_the_answer_does_not_reveal_whether_an_account_exists(client, db_session, outbox):
    make_user(db_session, "reel")
    unknown = client.post("/auth/forgot-password", json={"identifier": "personne@example.com"})
    known = client.post("/auth/forgot-password", json={"identifier": "reel"})
    assert unknown.status_code == known.status_code == 200
    assert unknown.json() == known.json()
    assert [e.to for e in outbox] == ["reel@example.com"]


def test_email_lookup_ignores_letter_case(client, db_session, outbox):
    make_user(db_session, "casse")
    client.post("/auth/forgot-password", json={"identifier": "  CASSE@Example.COM "})
    assert [e.to for e in outbox] == ["casse@example.com"]


def test_a_pending_trial_account_gets_no_reset_email(client, db_session, outbox):
    user = make_user(db_session, "attente")
    db_session.get(models.User, user["id"]).status = "pending"
    db_session.commit()
    assert client.post("/auth/forgot-password", json={"identifier": "attente"}).status_code == 200
    assert outbox == []


def test_an_expired_link_is_refused(client, db_session, outbox):
    make_user(db_session, "expire")
    client.post("/auth/forgot-password", json={"identifier": "expire"})
    token = _token_from(outbox[0])
    row = db_session.query(models.AuthToken).one()
    row.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db_session.commit()
    response = client.post("/auth/reset-password", json={"token": token, "password": STRONG})
    assert response.status_code == 400


def test_an_unknown_link_is_refused(client, db_session):
    response = client.post("/auth/reset-password", json={"token": "x" * 43, "password": STRONG})
    assert response.status_code == 400


def test_forgot_password_is_rate_limited(client, db_session):
    for _ in range(5):
        assert client.post("/auth/forgot-password", json={"identifier": "flood"}).status_code == 200
    assert client.post("/auth/forgot-password", json={"identifier": "flood"}).status_code == 429

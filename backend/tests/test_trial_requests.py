"""Free-trial automation (Spec v2 §1): scanid.fr/essai.html → pending account
with 20 credits + email to Alex → « Demandes d'essai » → Valider → welcome email
with a password link → login with 20 credits. Refuser, purge, errors.

All identities and company numbers in this file are fictional."""
import re
from datetime import datetime, timedelta, timezone

import pytest

import billing_identity
import mailer
import models
import trials
from tests.helpers import make_user, auth_headers

STRONG = "Girafe!!12Nuage"


def luhn_siret(first13: str) -> str:
    for check in "0123456789":
        if billing_identity.is_valid_siret(first13 + check):
            return first13 + check
    raise AssertionError("no check digit")


VALID_SIRET = luhn_siret("1234567890123")

# Exactly what frontend/scanid-site-v5-deploy/essai.html sends: every form field
# except the _* ones, consentement as a boolean.
SITE_PAYLOAD = {
    "nom": "Marie Dupont-Test", "societe": "Agence Horizon Test", "email": "Marie.Test@Agence-Horizon.fr",
    "telephone": "+33 6 00 00 00 00", "siret": VALID_SIRET[:3] + " " + VALID_SIRET[3:],
    "tva": "fr 12 345678901", "volume": "50 à 200 documents / mois",
    "message": "Agence groupes, 30 dossiers par an.", "consentement": True,
}


@pytest.fixture(autouse=True)
def outbox(monkeypatch):
    monkeypatch.setenv("MAIL_BACKEND", "outbox")
    monkeypatch.setenv("MAIL_ADMIN_TO", "contact@scanid.fr")
    monkeypatch.setenv("APP_PUBLIC_URL", "https://scanid.fr/app/")
    mailer.OUTBOX.clear()
    yield mailer.OUTBOX
    mailer.OUTBOX.clear()


def _submit(client, **changes):
    return client.post("/trial-requests", json={**SITE_PAYLOAD, **changes})


def test_the_site_form_creates_a_pending_account_with_20_credits_and_notifies_alex(client, db_session, outbox):
    response = _submit(client, _gotcha="", inconnu="ignored")
    assert response.status_code == 201
    assert response.json() == {"status": "pending"}

    user = db_session.query(models.User).one()
    assert (user.status, user.page_credits, user.user_name, user.email) == ("pending", 20, "marie.test@agence-horizon.fr", "marie.test@agence-horizon.fr")
    assert (user.first_name, user.last_name, user.company) == ("Marie", "Dupont-Test", "Agence Horizon Test")
    assert (user.siret, user.vat_number) == (VALID_SIRET, "FR12345678901")
    request = db_session.query(models.TrialRequest).one()
    assert (request.status, request.user_id, request.volume) == ("pending", user.id, "50 à 200 documents / mois")

    # No password exists yet: nothing can log in to this account.
    for attempt in ("", "secret-pass", STRONG, user.hashed_password):
        assert client.post("/token", data={"username": user.user_name, "password": attempt or "x"}).status_code == 401

    assert len(outbox) == 1
    email = outbox[0]
    assert email.to == "contact@scanid.fr" and email.kind == "trial_notification"
    assert email.reply_to == "marie.test@agence-horizon.fr"
    assert email.subject == "Demande d'essai — Agence Horizon Test"
    for expected in ("Marie Dupont-Test", "+33 6 00 00 00 00", "50 à 200 documents / mois", VALID_SIRET,
                     "FR12345678901", "Agence groupes", "https://scanid.fr/app/#demandes-essai"):
        assert expected in email.body


@pytest.mark.parametrize("changes, message", [
    ({"consentement": False}, "Le consentement est obligatoire."),
    ({"consentement": None}, "Le consentement est obligatoire."),
    ({"email": "pas-un-email"}, "L'adresse email n'est pas valide."),
    ({"nom": "  "}, "Le nom est obligatoire."),
    ({"siret": "12345678901234"}, billing_identity.SIRET_ERROR),
    ({"tva": "FR123"}, billing_identity.VAT_ERROR),
    ({"message": "x" * 2001}, "Le champ « message » est trop long."),
])
def test_invalid_requests_answer_an_error_and_create_nothing(client, db_session, outbox, changes, message):
    response = _submit(client, **changes)
    assert response.status_code == 400
    assert response.json() == {"error": message}
    assert db_session.query(models.User).count() == 0
    assert db_session.query(models.TrialRequest).count() == 0
    assert outbox == []


def test_optional_fields_may_be_left_empty(client, db_session):
    response = _submit(client, telephone="", siret="", tva="", message="")
    assert response.status_code == 201
    user = db_session.query(models.User).one()
    assert (user.phone_number, user.siret, user.vat_number) == ("", None, None)


def test_an_address_already_known_is_refused(client, db_session):
    make_user(db_session, "existant")
    assert client.post("/trial-requests", json={**SITE_PAYLOAD, "email": "EXISTANT@example.com"}).status_code == 409
    assert _submit(client).status_code == 201
    duplicate = _submit(client)
    assert duplicate.status_code == 409 and "error" in duplicate.json()


def test_without_email_the_endpoint_refuses_so_the_site_falls_back_to_formspree(client, db_session, monkeypatch):
    monkeypatch.setenv("MAIL_BACKEND", "disabled")
    response = _submit(client)
    assert response.status_code == 503 and "error" in response.json()
    assert db_session.query(models.User).count() == 0


def test_trial_requests_are_rate_limited_per_ip(client, db_session):
    for index in range(5):
        assert _submit(client, email=f"volume{index}@example.com").status_code == 201
    assert _submit(client, email="sixieme@example.com").status_code == 429


def test_public_config(client, monkeypatch):
    monkeypatch.delenv("STRIPE_WEBHOOK_SECRET", raising=False)
    assert client.get("/config").json() == {"signup": False, "trial": True}
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test")
    assert client.get("/config").json() == {"signup": True, "trial": True}
    monkeypatch.setenv("MAIL_BACKEND", "disabled")
    assert client.get("/config").json() == {"signup": True, "trial": False}


# --- « Demandes d'essai » --------------------------------------------------------

@pytest.fixture()
def admin(db_session):
    make_user(db_session, "chef", role="admin")
    return auth_headers("chef")


def _pending_id(client, admin):
    listed = client.get("/admin/trial-requests", headers=admin)
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    return listed.json()[0]["id"]


def test_only_an_admin_sees_and_decides(client, db_session, admin):
    _submit(client)
    make_user(db_session, "client")
    request_id = _pending_id(client, admin)
    for method, path in (("get", "/admin/trial-requests"),
                         ("post", f"/admin/trial-requests/{request_id}/validate"),
                         ("post", f"/admin/trial-requests/{request_id}/reject")):
        assert getattr(client, method)(path, headers=auth_headers("client")).status_code == 403


def test_valider_sends_the_welcome_email_and_the_client_logs_in_with_20_credits(client, db_session, admin, outbox):
    _submit(client)
    request_id = _pending_id(client, admin)
    outbox.clear()

    decided = client.post(f"/admin/trial-requests/{request_id}/validate", headers=admin)
    assert decided.status_code == 200 and decided.json()["status"] == "validated"
    assert client.get("/admin/trial-requests", headers=admin).json() == []

    assert len(outbox) == 1
    welcome = outbox[0]
    assert welcome.to == "marie.test@agence-horizon.fr" and welcome.kind == "trial_welcome"
    assert welcome.subject == "Votre espace ScanID est ouvert — 20 scans offerts"
    assert "Adresse : https://scanid.fr/app/" in welcome.body
    assert "Identifiant : marie.test@agence-horizon.fr" in welcome.body
    assert "Bonjour Marie," in welcome.body and "guide-photo.html" in welcome.body
    assert "provisoire" not in welcome.body                      # never a password by email
    token = re.search(r"https://scanid\.fr/app/mot-de-passe#token=([A-Za-z0-9_-]+)", welcome.body).group(1)

    assert client.post("/auth/reset-password", json={"token": token, "password": STRONG}).status_code == 200
    login = client.post("/token", data={"username": "marie.test@agence-horizon.fr", "password": STRONG})
    assert login.status_code == 200
    me = client.get("/users/me", headers={"Authorization": f"Bearer {login.json()['access_token']}"}).json()
    assert me["page_credits"] == 20


def test_refuser_sends_nothing_and_the_account_stays_closed(client, db_session, admin, outbox):
    _submit(client)
    request_id = _pending_id(client, admin)
    outbox.clear()

    refused = client.post(f"/admin/trial-requests/{request_id}/reject", headers=admin)
    assert refused.status_code == 200 and refused.json()["status"] == "rejected"
    assert outbox == []
    assert db_session.query(models.User).filter_by(user_name="marie.test@agence-horizon.fr").one().status == "rejected"
    assert client.post("/auth/forgot-password", json={"identifier": "marie.test@agence-horizon.fr"}).status_code == 200
    assert outbox == []                                          # no reset link for a refused request either
    assert client.post(f"/admin/trial-requests/{request_id}/validate", headers=admin).status_code == 409


def test_valider_needs_email_to_be_configured(client, db_session, admin, monkeypatch):
    _submit(client)
    request_id = _pending_id(client, admin)
    monkeypatch.setenv("MAIL_BACKEND", "disabled")
    assert client.post(f"/admin/trial-requests/{request_id}/validate", headers=admin).status_code == 503
    assert db_session.query(models.User).filter_by(status="pending").count() == 1   # nothing half-done


def test_unknown_request(client, db_session, admin):
    assert client.post("/admin/trial-requests/nope/validate", headers=admin).status_code == 404


# --- Purge after 30 days -------------------------------------------------------

def test_pending_and_refused_requests_are_purged_after_30_days(client, db_session, admin):
    now = datetime.now(timezone.utc)
    for index, email in enumerate(["vieux-attente@example.com", "vieux-refus@example.com",
                                   "vieux-valide@example.com", "recent@example.com"]):
        assert _submit(client, email=email).status_code == 201
    requests = {r.email: r for r in db_session.query(models.TrialRequest).all()}
    trials.reject(db_session, requests["vieux-refus@example.com"].id)
    trials.validate(db_session, requests["vieux-valide@example.com"].id)
    for email in ("vieux-attente@example.com", "vieux-refus@example.com", "vieux-valide@example.com"):
        requests[email].created_at = now - timedelta(days=31)
    requests["recent@example.com"].created_at = now - timedelta(days=29)
    db_session.commit()

    assert trials.purge(db_session) == 2

    left = {r.email for r in db_session.query(models.TrialRequest).all()}
    assert left == {"vieux-valide@example.com", "recent@example.com"}
    users = {u.email for u in db_session.query(models.User).filter(models.User.role == "user").all()}
    assert users == {"vieux-valide@example.com", "recent@example.com"}

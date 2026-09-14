"""Account before payment (Spec v3): /app/inscription → account + pending
purchase → Stripe Payment Link → signed webhook → credits added once.

Stripe itself cannot be reached from the test suite; the webhook requests below
are signed exactly as Stripe signs them (HMAC-SHA256 over "<t>.<payload>").
All identities and company numbers are fictional."""
import hashlib
import hmac
import json
import time
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlsplit

import pytest

import billing
import billing_identity
import mailer
import models
from tests.helpers import make_user, auth_headers

SECRET = "whsec_test_secret_for_the_suite"
STRONG = "Girafe!!12Nuage"


def luhn_siret(first13: str) -> str:
    return next(first13 + d for d in "0123456789" if billing_identity.is_valid_siret(first13 + d))


SIRET = luhn_siret("7328293200007")


@pytest.fixture(autouse=True)
def environment(monkeypatch):
    monkeypatch.setenv("MAIL_BACKEND", "outbox")
    monkeypatch.setenv("MAIL_ADMIN_TO", "contact@scanid.fr")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", SECRET)
    for pack in (100, 1000, 3000, 5000):
        monkeypatch.delenv(f"STRIPE_PAYMENT_LINK_{pack}", raising=False)
    mailer.OUTBOX.clear()
    yield
    mailer.OUTBOX.clear()


def signup_payload(**changes):
    payload = {
        "pack": 1000, "first_name": "Claire", "last_name": "Achat", "company": "Agence Test Voyages",
        "email": "Claire.Achat@Agence-Test.fr", "password": STRONG, "phone_number": "+33 1 00 00 00 00",
        "billing_street": "1 rue de l'Essai", "billing_postal_code": "75001", "billing_city": "Paris",
        "billing_country": "France", "siret": f"{SIRET[:3]} {SIRET[3:6]} {SIRET[6:9]} {SIRET[9:]}",
        "vat_number": "FR 12 345678901", "consent": True,
    }
    payload.update(changes)
    return payload


def signed(client, event: dict, at: float = None, secret: str = SECRET):
    body = json.dumps(event).encode()
    timestamp = int(time.time() if at is None else at)
    signature = hmac.new(secret.encode(), f"{timestamp}.".encode() + body, hashlib.sha256).hexdigest()
    return client.post("/stripe/webhook", content=body,
                       headers={"Stripe-Signature": f"t={timestamp},v1={signature}", "Content-Type": "application/json"})


def completed(user_id, session_id="cs_test_a1", subtotal=69_000, total=82_800, paid="paid", kind="checkout.session.completed"):
    return {"id": f"evt_{session_id}", "type": kind, "data": {"object": {
        "id": session_id, "object": "checkout.session", "client_reference_id": user_id,
        "payment_status": paid, "amount_subtotal": subtotal, "amount_total": total, "currency": "eur",
        "customer_details": {"email": "claire.achat@agence-test.fr"},
    }}}


def test_signup_creates_the_account_and_redirects_to_the_packs_payment_link(client, db_session):
    response = client.post("/signup", json=signup_payload())
    assert response.status_code == 200, response.text

    user = db_session.query(models.User).one()
    assert (user.user_name, user.email, user.status, user.page_credits) == (
        "claire.achat@agence-test.fr", "claire.achat@agence-test.fr", "active", 0)
    assert (user.company, user.siret, user.vat_number) == ("Agence Test Voyages", SIRET, "FR12345678901")
    assert (user.billing_street, user.billing_postal_code, user.billing_city, user.billing_country) == (
        "1 rue de l'Essai", "75001", "Paris", "France")
    purchase = db_session.query(models.Purchase).one()
    assert (purchase.user_id, purchase.pack, purchase.credits, purchase.amount_ht_cents, purchase.status) == (
        user.id, 1000, 1000, 69_000, "pending")

    url = urlsplit(response.json()["checkout_url"])
    assert f"{url.scheme}://{url.netloc}{url.path}" == "https://buy.stripe.com/8x27sK0rtbFi8Apgvbebu01"
    assert parse_qs(url.query) == {"prefilled_email": ["claire.achat@agence-test.fr"], "client_reference_id": [user.id]}

    # The password chosen on the page is the account's password.
    assert client.post("/token", data={"username": "claire.achat@agence-test.fr", "password": STRONG}).status_code == 200


def test_each_pack_has_its_own_link_and_a_test_mode_link_can_replace_it(client, db_session, monkeypatch):
    monkeypatch.setenv("STRIPE_PAYMENT_LINK_100", "https://buy.stripe.com/test_fake100")
    url = client.post("/signup", json=signup_payload(pack=100)).json()["checkout_url"]
    assert url.startswith("https://buy.stripe.com/test_fake100?prefilled_email=")


@pytest.mark.parametrize("changes, status, fragment", [
    ({"pack": 250}, 400, "Ce pack n'existe pas"),
    ({"company": " "}, 400, "la société"),
    ({"billing_postal_code": ""}, 400, "le code postal"),
    ({"siret": ""}, 400, "14 chiffres"),
    ({"siret": "73282932000075"}, 400, "14 chiffres"),
    ({"vat_number": "FR1234"}, 400, "TVA"),
    ({"consent": False}, 400, "accepter"),
    ({"email": "pas-un-email"}, 400, "email n'est pas valide"),
    ({"password": "court"}, 422, "12 caractères"),
])
def test_signup_refuses_incomplete_or_invalid_details(client, db_session, changes, status, fragment):
    response = client.post("/signup", json=signup_payload(**changes))
    assert response.status_code == status
    assert fragment in response.json()["detail"]
    assert db_session.query(models.User).count() == 0 and db_session.query(models.Purchase).count() == 0


def test_vat_number_is_optional(client, db_session):
    assert client.post("/signup", json=signup_payload(vat_number="")).status_code == 200
    assert db_session.query(models.User).one().vat_number is None


def test_an_existing_customer_is_asked_to_log_in(client, db_session):
    make_user(db_session, "claire")
    response = client.post("/signup", json=signup_payload(email="CLAIRE@example.com"))
    assert response.status_code == 400 and "Connectez-vous" in response.json()["detail"]


def test_a_logged_in_customer_orders_without_the_form(client, db_session):
    user = make_user(db_session, "fidele")
    assert client.post("/orders", json={"pack": 3000}).status_code == 401
    response = client.post("/orders", json={"pack": 3000}, headers=auth_headers("fidele"))
    assert response.status_code == 200
    query = parse_qs(urlsplit(response.json()["checkout_url"]).query)
    assert query == {"prefilled_email": ["fidele@example.com"], "client_reference_id": [user["id"]]}
    assert db_session.query(models.Purchase).one().pack == 3000
    assert client.post("/orders", json={"pack": 7}, headers=auth_headers("fidele")).status_code == 400


# --- Webhook ------------------------------------------------------------------------

def _signed_up(client, db_session, pack=1000):
    client.post("/signup", json=signup_payload(pack=pack))
    return db_session.query(models.User).one()


def test_full_purchase_then_webhook_replay_credits_once(client, db_session):
    user = _signed_up(client, db_session)
    mailer.OUTBOX.clear()

    first = signed(client, completed(user.id))
    assert first.status_code == 200 and first.json() == {"received": True, "result": "credited"}
    db_session.expire_all()
    assert db_session.get(models.User, user.id).page_credits == 1000

    purchase = db_session.query(models.Purchase).one()
    assert (purchase.status, purchase.stripe_session_id, purchase.amount_paid_cents, purchase.currency) == (
        "paid", "cs_test_a1", 82_800, "eur")
    paid_at = purchase.paid_at.replace(tzinfo=timezone.utc) if purchase.paid_at.tzinfo is None else purchase.paid_at
    expires = purchase.expires_at.replace(tzinfo=timezone.utc) if purchase.expires_at.tzinfo is None else purchase.expires_at
    assert (expires.year - paid_at.year) * 12 + expires.month - paid_at.month == 12

    assert [(e.to, e.kind) for e in mailer.OUTBOX] == [("claire.achat@agence-test.fr", "purchase_confirmation")]
    assert "Vos 1 000 scans ont été ajoutés" in mailer.OUTBOX[0].body

    # Stripe « Resend »: a new delivery, freshly signed, of the same event.
    for _ in range(3):
        replay = signed(client, completed(user.id))
        assert replay.status_code == 200 and replay.json()["result"] == "duplicate"
    db_session.expire_all()
    assert db_session.get(models.User, user.id).page_credits == 1000
    assert db_session.query(models.Purchase).count() == 1
    assert len(mailer.OUTBOX) == 1


def test_a_race_between_two_deliveries_is_stopped_by_the_database(client, db_session, monkeypatch):
    user = _signed_up(client, db_session)
    assert signed(client, completed(user.id)).json()["result"] == "credited"
    billing.create_pending_purchase(db_session, user.id, 1000)          # a second, later order of the same pack
    monkeypatch.setattr(billing, "already_processed", lambda db, session_id: False)   # both deliveries got past the check

    outcome = billing.credit_checkout_session(db_session, completed(user.id)["data"]["object"])

    assert outcome.status == "duplicate"
    db_session.expire_all()
    assert db_session.get(models.User, user.id).page_credits == 1000
    assert sorted(p.status for p in db_session.query(models.Purchase).all()) == ["paid", "pending"]


def test_the_signature_is_verified(client, db_session):
    user = _signed_up(client, db_session)
    assert signed(client, completed(user.id), secret="whsec_wrong").status_code == 400
    assert signed(client, completed(user.id), at=time.time() - 301).status_code == 400    # an old request replayed
    unsigned = client.post("/stripe/webhook", json=completed(user.id))
    assert unsigned.status_code == 400
    db_session.expire_all()
    assert db_session.get(models.User, user.id).page_credits == 0


def test_without_a_secret_the_webhook_refuses(client, db_session, monkeypatch):
    monkeypatch.delenv("STRIPE_WEBHOOK_SECRET")
    assert client.post("/stripe/webhook", content=b"{}").status_code == 503


def test_other_events_are_acknowledged_and_ignored(client, db_session):
    user = _signed_up(client, db_session)
    response = signed(client, {"id": "evt_x", "type": "payment_intent.created", "data": {"object": {}}})
    assert response.json() == {"received": True, "result": "ignored"}


def test_a_bank_transfer_is_credited_when_the_money_arrives(client, db_session):
    user = _signed_up(client, db_session, pack=5000)
    waiting = signed(client, completed(user.id, "cs_virement", 295_000, 354_000, paid="unpaid"))
    assert waiting.json()["result"] == "not_paid"
    db_session.expire_all()
    assert db_session.get(models.User, user.id).page_credits == 0
    arrived = signed(client, completed(user.id, "cs_virement", 295_000, 354_000, kind="checkout.session.async_payment_succeeded"))
    assert arrived.json()["result"] == "credited"
    db_session.expire_all()
    assert db_session.get(models.User, user.id).page_credits == 5000


def test_the_pack_credited_is_the_one_paid_for(client, db_session):
    user = _signed_up(client, db_session, pack=5000)                   # asked for 5000…
    assert signed(client, completed(user.id, "cs_cheap", 9_900, 11_880)).json()["result"] == "credited"   # …paid for 100
    db_session.expire_all()
    assert db_session.get(models.User, user.id).page_credits == 100
    statuses = {(p.pack, p.status) for p in db_session.query(models.Purchase).all()}
    assert statuses == {(5000, "pending"), (100, "paid")}


def test_the_total_alone_identifies_the_pack(client, db_session):
    user = _signed_up(client, db_session, pack=3000)
    assert signed(client, completed(user.id, "cs_ttc", None, 226_800)).json()["result"] == "credited"


@pytest.mark.parametrize("session_changes, reason", [
    ({"amount_subtotal": 12_345, "amount_total": 14_814}, "montant"),
    ({"client_reference_id": None}, "client_reference_id"),
    ({"client_reference_id": "inconnu"}, "client_reference_id"),
])
def test_what_cannot_be_matched_is_reported_to_alex_and_credits_nothing(client, db_session, session_changes, reason):
    user = _signed_up(client, db_session)
    mailer.OUTBOX.clear()
    event = completed(user.id)
    event["data"]["object"].update(session_changes)
    response = signed(client, event)
    assert response.status_code == 200 and response.json()["result"] == "unmatched"
    db_session.expire_all()
    assert db_session.get(models.User, user.id).page_credits == 0
    assert [(e.to, e.kind) for e in mailer.OUTBOX] == [("contact@scanid.fr", "payment_anomaly")]
    assert reason in mailer.OUTBOX[0].body and "cs_test_a1" in mailer.OUTBOX[0].body


def test_add_months_keeps_the_calendar():
    assert billing.add_months(datetime(2026, 9, 14, tzinfo=timezone.utc), 12) == datetime(2027, 9, 14, tzinfo=timezone.utc)
    assert billing.add_months(datetime(2028, 2, 29, tzinfo=timezone.utc), 12) == datetime(2029, 2, 28, tzinfo=timezone.utc)

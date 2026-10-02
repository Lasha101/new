"""« À la carte » (the site's deployment notes of 2026-09-30, §5): one Stripe
Payment Link with an adjustable quantity, 1 unit = 1 document at 1,50 € HT. On
checkout.session.completed for THIS link, the account is credited with the
purchased quantity — the line item's quantity.

Stripe cannot be reached from the suite. The webhooks are signed exactly as
Stripe signs them; the line items come from a stand-in for
billing.fetch_line_items, or — for the request itself — from a local HTTP
server playing api.stripe.com. All identities are fictional."""
import hashlib
import hmac
import json
import threading
import time
from datetime import timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

import billing
import crud
import mailer
import models
import schemas
from tests.helpers import auth_headers

SECRET = "whsec_test_secret_for_the_suite"
LINK = "plink_test_a_la_carte"
KEY = "rk_test_checkout_sessions_read"


@pytest.fixture(autouse=True)
def environment(monkeypatch):
    monkeypatch.setenv("MAIL_BACKEND", "outbox")
    monkeypatch.setenv("MAIL_ADMIN_TO", "contact@scanid.fr")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", SECRET)
    monkeypatch.setenv("STRIPE_UNIT_PAYMENT_LINK_ID", LINK)
    monkeypatch.setenv("STRIPE_API_KEY", KEY)
    mailer.OUTBOX.clear()
    yield
    mailer.OUTBOX.clear()


@pytest.fixture
def stripe_items(monkeypatch):
    """Stands in for billing.fetch_line_items: `answers[session_id]` is what
    Stripe returns (or the StripeApiError it fails with); `calls` records each read."""
    answers, calls = {}, []

    def fake(session_id):
        calls.append(session_id)
        answer = answers.get(session_id, [])
        if isinstance(answer, Exception):
            raise answer
        return answer

    monkeypatch.setattr(billing, "fetch_line_items", fake)
    fake.answers, fake.calls = answers, calls
    return fake


class _StripeStandIn(BaseHTTPRequestHandler):
    """api.stripe.com for one test: records each request, answers `reply`."""
    reply = (200, b"{}")
    requests = []

    def do_GET(self):
        type(self).requests.append({"path": self.path, "authorization": self.headers.get("Authorization")})
        status, body = type(self).reply
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


@pytest.fixture
def stripe_api(monkeypatch):
    handler = type("Handler", (_StripeStandIn,), {"requests": [], "reply": (200, b"{}")})
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setattr(billing, "STRIPE_API_BASE", f"http://127.0.0.1:{server.server_address[1]}")
    yield handler
    server.shutdown()
    server.server_close()


def item(quantity, unit_amount=150):
    return {"id": "li_test_1", "object": "item", "quantity": quantity, "currency": "eur",
            "amount_subtotal": quantity * unit_amount, "description": "Document à la carte",
            "price": {"id": "price_test_unite", "unit_amount": unit_amount, "currency": "eur"}}


def customer(db, user_name, email, status="active", credits=10):
    user = crud.create_user(db=db, user=schemas.UserCreate(
        first_name="Marc", last_name="Unité", email=email, phone_number="0102030405",
        user_name=user_name, password="secret-pass", page_credits=credits,
    ), role="user")
    if status != "active":
        db.get(models.User, user["id"]).status = status
        db.commit()
    return user


def signed(client, event, secret=SECRET):
    body = json.dumps(event).encode()
    timestamp = int(time.time())
    signature = hmac.new(secret.encode(), f"{timestamp}.".encode() + body, hashlib.sha256).hexdigest()
    return client.post("/stripe/webhook", content=body,
                       headers={"Stripe-Signature": f"t={timestamp},v1={signature}", "Content-Type": "application/json"})


def unit_session(session_id="cs_test_unite_1", quantity=37, email="Marc.Unite@Agence-Test.fr", link=LINK,
                 client_reference_id=None, paid="paid", kind="checkout.session.completed", currency="eur"):
    """A Checkout Session of the à la carte link as the webhook receives it: no line items."""
    subtotal = quantity * 150
    return {"id": f"evt_{session_id}", "type": kind, "data": {"object": {
        "id": session_id, "object": "checkout.session", "payment_link": link,
        "client_reference_id": client_reference_id, "payment_status": paid,
        "amount_subtotal": subtotal, "amount_total": subtotal * 120 // 100, "currency": currency,
        "customer_details": {"email": email},
    }}}


def credits_of(db, user):
    db.expire_all()
    return db.get(models.User, user["id"]).page_credits


def test_the_quantity_bought_is_credited_once_to_the_account_of_the_checkout_email(client, db_session, stripe_items):
    marc = customer(db_session, "marc.unite@agence-test.fr", "marc.unite@agence-test.fr")
    stripe_items.answers["cs_test_unite_1"] = [item(37)]

    first = signed(client, unit_session())          # the checkout e-mail in another letter case
    assert first.status_code == 200 and first.json() == {"received": True, "result": "credited"}
    assert credits_of(db_session, marc) == 10 + 37

    purchase = db_session.query(models.Purchase).one()
    assert (purchase.user_id, purchase.pack, purchase.credits, purchase.amount_ht_cents, purchase.status) == (
        marc["id"], billing.UNIT_PACK, 37, 37 * 150, "paid")
    assert (purchase.stripe_session_id, purchase.amount_paid_cents, purchase.currency) == ("cs_test_unite_1", 6_660, "eur")
    paid_at = purchase.paid_at.replace(tzinfo=timezone.utc)
    assert purchase.expires_at.replace(tzinfo=timezone.utc) == billing.add_months(paid_at, 12)   # CGV: 12 months

    assert [(e.to, e.kind) for e in mailer.OUTBOX] == [("marc.unite@agence-test.fr", "purchase_confirmation")]
    assert mailer.OUTBOX[0].subject == "Vos 37 documents ScanID sont disponibles"
    assert "achat à la carte : 37 documents ont été ajoutés à votre espace ScanID ; ils sont valables jusqu'au" in mailer.OUTBOX[0].body

    for _ in range(2):                              # Stripe retries, or Alex presses « Resend »
        replay = signed(client, unit_session())
        assert replay.status_code == 200 and replay.json()["result"] == "duplicate"
    assert credits_of(db_session, marc) == 47
    assert db_session.query(models.Purchase).count() == 1
    assert len(mailer.OUTBOX) == 1
    assert stripe_items.calls == ["cs_test_unite_1"]  # a replay never reaches Stripe again


def test_66_documents_are_66_credits_not_the_pack_100_their_price_equals(client, db_session, stripe_items):
    # 66 × 1,50 € = 99 € HT, 118,80 € TTC: exactly Pack 100's amounts. Identified
    # by the amount, as packs are, this payment would credit 100.
    marc = customer(db_session, "marc", "marc@agence-test.fr", credits=0)
    stripe_items.answers["cs_test_66"] = [item(66)]
    event = unit_session("cs_test_66", quantity=66, email="marc@agence-test.fr", client_reference_id=marc["id"])
    assert (event["data"]["object"]["amount_subtotal"], event["data"]["object"]["amount_total"]) == (9_900, 11_880)

    assert signed(client, event).json()["result"] == "credited"
    assert credits_of(db_session, marc) == 66
    assert db_session.query(models.Purchase).one().pack == billing.UNIT_PACK


def test_client_reference_id_names_the_account_when_present(client, db_session, stripe_items):
    payer = customer(db_session, "payeur", "payeur@agence-test.fr")
    other = customer(db_session, "autre", "autre@agence-test.fr")
    stripe_items.answers["cs_test_ref"] = [item(5)]
    event = unit_session("cs_test_ref", quantity=5, email="autre@agence-test.fr", client_reference_id=payer["id"])
    assert signed(client, event).json()["result"] == "credited"
    assert (credits_of(db_session, payer), credits_of(db_session, other)) == (15, 10)


def test_one_document_is_said_in_the_singular(client, db_session, stripe_items):
    customer(db_session, "solo", "solo@agence-test.fr")
    stripe_items.answers["cs_test_one"] = [item(1)]
    assert signed(client, unit_session("cs_test_one", quantity=1, email="solo@agence-test.fr")).json()["result"] == "credited"
    assert mailer.OUTBOX[0].subject == "Votre document ScanID est disponible"
    assert "achat à la carte : 1 document a été ajouté à votre espace ScanID ; il est valable jusqu'au" in mailer.OUTBOX[0].body


def test_a_pending_trial_account_is_credited_too(client, db_session, stripe_items):
    # Its owner cannot log in until Alex validates the trial; the documents
    # bought are waiting there when they do.
    pending = customer(db_session, "attente@agence-test.fr", "attente@agence-test.fr", status="pending", credits=20)
    stripe_items.answers["cs_test_pending"] = [item(10)]
    assert signed(client, unit_session("cs_test_pending", quantity=10, email="attente@agence-test.fr")).json()["result"] == "credited"
    assert credits_of(db_session, pending) == 30


def test_a_bank_transfer_is_credited_when_the_money_arrives(client, db_session, stripe_items):
    marc = customer(db_session, "marc", "marc@agence-test.fr", credits=0)
    stripe_items.answers["cs_test_virement"] = [item(200)]
    waiting = signed(client, unit_session("cs_test_virement", quantity=200, email="marc@agence-test.fr", paid="unpaid"))
    assert waiting.json()["result"] == "not_paid"
    assert credits_of(db_session, marc) == 0 and stripe_items.calls == []
    arrived = signed(client, unit_session("cs_test_virement", quantity=200, email="marc@agence-test.fr",
                                          kind="checkout.session.async_payment_succeeded"))
    assert arrived.json()["result"] == "credited"
    assert credits_of(db_session, marc) == 200


def test_mes_achats_lists_the_unit_purchase(client, db_session, stripe_items):
    customer(db_session, "marc", "marc@agence-test.fr")
    stripe_items.answers["cs_test_unite_1"] = [item(37)]
    assert signed(client, unit_session(email="marc@agence-test.fr")).json()["result"] == "credited"
    response = client.get("/users/me/purchases", headers=auth_headers("marc"))
    assert response.status_code == 200
    [row] = response.json()
    assert (row["pack"], row["credits"], row["amount_ht_cents"]) == (0, 37, 5_550)


def test_a_race_between_two_deliveries_is_stopped_by_the_database(client, db_session, stripe_items, monkeypatch):
    marc = customer(db_session, "marc", "marc@agence-test.fr", credits=0)
    stripe_items.answers["cs_test_unite_1"] = [item(37)]
    assert signed(client, unit_session(email="marc@agence-test.fr")).json()["result"] == "credited"
    monkeypatch.setattr(billing, "already_processed", lambda db, session_id: False)   # both got past the check
    outcome = billing.credit_checkout_session(db_session, unit_session(email="marc@agence-test.fr")["data"]["object"])
    assert outcome.status == "duplicate"
    assert credits_of(db_session, marc) == 37
    assert db_session.query(models.Purchase).count() == 1


@pytest.mark.parametrize("setup, session_changes, answer, reason", [
    (None, {"customer_details": {"email": "inconnu@agence-test.fr"}}, [item(5)], "aucun compte ScanID unique"),
    (None, {"customer_details": {}}, [item(5)], "aucun compte ScanID unique"),
    (None, {"client_reference_id": "compte-inconnu"}, [item(5)], "aucun compte ScanID unique"),
    ("twins", {}, [item(5)], "aucun compte ScanID unique"),
    ("rejected", {}, [item(5)], "le compte de ce client a été refusé"),
    (None, {"currency": "usd"}, [item(5)], "une autre devise que l'euro"),
    (None, {}, billing.StripeApiError("l'API Stripe a répondu 401 à la lecture des articles"), "répondu 401"),
    (None, {}, [item(5), item(2)], "un seul article"),
    (None, {}, [], "un seul article"),
    (None, {}, [item(0)], "un seul article"),
    (None, {}, [{"id": "li_x", "quantity": "5"}], "un seul article"),
])
def test_what_cannot_be_established_is_reported_to_alex_and_credits_nothing(
        client, db_session, stripe_items, setup, session_changes, answer, reason):
    status = "rejected" if setup == "rejected" else "active"
    marc = customer(db_session, "marc", "marc@agence-test.fr", status=status)
    if setup == "twins":   # the same address twice, in two letter cases: whose credits?
        customer(db_session, "marc2", "Marc@Agence-Test.fr")
    stripe_items.answers["cs_test_unite_1"] = answer
    event = unit_session(email="marc@agence-test.fr")
    event["data"]["object"].update(session_changes)

    response = signed(client, event)
    assert response.status_code == 200 and response.json()["result"] == "unmatched"
    assert credits_of(db_session, marc) == 10
    assert db_session.query(models.Purchase).count() == 0
    assert [(e.to, e.kind) for e in mailer.OUTBOX] == [("contact@scanid.fr", "payment_anomaly")]
    assert reason in mailer.OUTBOX[0].body and "cs_test_unite_1" in mailer.OUTBOX[0].body


def test_without_an_api_key_nothing_is_asked_and_alex_is_told(client, db_session, monkeypatch, stripe_api):
    monkeypatch.delenv("STRIPE_API_KEY")
    marc = customer(db_session, "marc", "marc@agence-test.fr")
    assert signed(client, unit_session(email="marc@agence-test.fr")).json()["result"] == "unmatched"
    assert stripe_api.requests == []
    assert credits_of(db_session, marc) == 10
    assert "STRIPE_API_KEY" in mailer.OUTBOX[0].body


def test_until_the_link_is_configured_the_pack_path_is_unchanged(client, db_session, stripe_items, monkeypatch):
    monkeypatch.delenv("STRIPE_UNIT_PAYMENT_LINK_ID")
    marc = customer(db_session, "marc", "marc@agence-test.fr", credits=0)
    # Without client_reference_id nothing can be credited — reported, as before.
    assert signed(client, unit_session(email="marc@agence-test.fr")).json()["result"] == "unmatched"
    assert "client_reference_id" in mailer.OUTBOX[0].body
    # A pack bought through the app (client_reference_id) is still identified by its amount.
    pack = unit_session("cs_test_pack", email="marc@agence-test.fr", client_reference_id=marc["id"])
    pack["data"]["object"].update({"amount_subtotal": 69_000, "amount_total": 82_800})
    assert signed(client, pack).json()["result"] == "credited"
    assert credits_of(db_session, marc) == 1000
    assert stripe_items.calls == []


def test_a_pack_link_never_reads_line_items(client, db_session, stripe_items):
    marc = customer(db_session, "marc", "marc@agence-test.fr", credits=0)
    pack = unit_session("cs_test_pack", email="marc@agence-test.fr", link="plink_test_pack_1000",
                        client_reference_id=marc["id"])
    pack["data"]["object"].update({"amount_subtotal": 69_000, "amount_total": 82_800})
    assert signed(client, pack).json()["result"] == "credited"
    assert credits_of(db_session, marc) == 1000
    assert db_session.query(models.Purchase).one().pack == 1000
    assert mailer.OUTBOX[0].subject == "Vos 1 000 scans ScanID sont disponibles"   # the pack e-mail, unchanged
    assert stripe_items.calls == []


def test_the_line_items_are_asked_of_stripe_with_the_key(stripe_api):
    stripe_api.reply = (200, json.dumps({"object": "list", "data": [item(12)], "has_more": False}).encode())
    assert billing.fetch_line_items("cs_test_x/1") == [item(12)]
    assert stripe_api.requests == [{"path": "/v1/checkout/sessions/cs_test_x%2F1/line_items?limit=100",
                                    "authorization": f"Bearer {KEY}"}]


@pytest.mark.parametrize("reply, fragment", [
    ((401, b'{"error": {"type": "invalid_request_error"}}'), "a répondu 401"),
    ((500, b"oops"), "a répondu 500"),
    ((200, b"<html>not json</html>"), "illisible"),
    ((200, b'{"object": "list"}'), "ne contient pas les articles"),
])
def test_a_failed_read_is_a_stripe_api_error(stripe_api, reply, fragment):
    stripe_api.reply = reply
    with pytest.raises(billing.StripeApiError, match=fragment):
        billing.fetch_line_items("cs_test_x")


def test_an_unreachable_stripe_is_a_stripe_api_error(monkeypatch):
    monkeypatch.setattr(billing, "STRIPE_API_BASE", "http://127.0.0.1:9")   # discard port: nothing listens
    with pytest.raises(billing.StripeApiError, match="injoignable"):
        billing.fetch_line_items("cs_test_x")


def test_end_to_end_the_webhook_reads_the_quantity_from_stripe(client, db_session, stripe_api):
    marc = customer(db_session, "marc", "marc@agence-test.fr", credits=0)
    stripe_api.reply = (200, json.dumps({"object": "list", "data": [item(250)], "has_more": False}).encode())
    response = signed(client, unit_session("cs_test_e2e", quantity=250, email="marc@agence-test.fr"))
    assert response.json()["result"] == "credited"
    assert credits_of(db_session, marc) == 250
    assert [r["path"] for r in stripe_api.requests] == ["/v1/checkout/sessions/cs_test_e2e/line_items?limit=100"]

"""« À la carte » (the site's deployment notes of 2026-09-30, §5, and Alex's
« Tarifs page, à la carte link and webhook » of 2026-10-03): one Stripe Payment
Link with an adjustable quantity, 1 unit = 1 document at 1,50 € HT (1,80 € TTC,
VAT-inclusive, no tax line). On checkout.session.completed for THIS link, the
account of the checkout e-mail is credited with the purchased quantity — the
line item's quantity. An open account is credited; otherwise the purchase opens
it (no account yet, a trial request still waiting, or one Alex refused) with the
documents bought only, and the welcome e-mail carries the link to choose its
password. A purchase never logs anyone in and never changes the e-mail or the
password of an open account.

Stripe cannot be reached from the suite. The webhooks are signed exactly as
Stripe signs them; the line items come from a stand-in for
billing.fetch_line_items, or — for the request itself — from a local HTTP
server playing api.stripe.com. All identities are fictional."""
import hashlib
import hmac
import json
import re
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
import trials
from sqlalchemy import update as sa_update
from tests.helpers import auth_headers, make_user

SECRET = "whsec_test_secret_for_the_suite"
LINK = "plink_test_a_la_carte"
KEY = "rk_test_checkout_sessions_read"
STRONG = "Girafe!!12Nuage"
LINK_TOKEN = re.compile(r"https://scanid\.fr/app/mot-de-passe#token=([A-Za-z0-9_-]+)")
TRIAL = {"nom": "Anne Attente-Test", "societe": "Agence Attente Test", "email": "Attente@Agence-Test.fr",
         "telephone": "+33 6 00 00 00 01", "consentement": True}


@pytest.fixture(autouse=True)
def environment(monkeypatch):
    monkeypatch.setenv("MAIL_BACKEND", "outbox")
    monkeypatch.setenv("MAIL_ADMIN_TO", "contact@scanid.fr")
    monkeypatch.setenv("APP_PUBLIC_URL", "https://scanid.fr/app/")
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


def item(quantity, unit_amount=180):
    return {"id": "li_test_1", "object": "item", "quantity": quantity, "currency": "eur",
            "amount_subtotal": quantity * unit_amount, "amount_total": quantity * unit_amount,
            "description": "Document à l'unité",
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


def signed(client, event, secret=SECRET, at=None):
    body = json.dumps(event).encode()
    timestamp = int(time.time() if at is None else at)
    signature = hmac.new(secret.encode(), f"{timestamp}.".encode() + body, hashlib.sha256).hexdigest()
    return client.post("/stripe/webhook", content=body,
                       headers={"Stripe-Signature": f"t={timestamp},v1={signature}", "Content-Type": "application/json"})


def unit_session(session_id="cs_test_unite_1", quantity=37, email="Marc.Unite@Agence-Test.fr", link=LINK,
                 client_reference_id=None, paid="paid", kind="checkout.session.completed", currency="eur",
                 details=None):
    """A Checkout Session of the à la carte link as the webhook receives it: no
    line items; 1,80 € TTC per document, VAT-inclusive, no tax line (Alex)."""
    amount = quantity * 180
    return {"id": f"evt_{session_id}", "type": kind, "data": {"object": {
        "id": session_id, "object": "checkout.session", "payment_link": link,
        "client_reference_id": client_reference_id, "payment_status": paid,
        "amount_subtotal": amount, "amount_total": amount, "currency": currency,
        "customer_details": {"email": email, **(details or {})},
    }}}


def credits_of(db, user):
    db.expire_all()
    return db.get(models.User, user["id"]).page_credits


def welcome_token(email):
    return LINK_TOKEN.search(email.body).group(1)


def logs_in_with(client, user_name, token, password=STRONG):
    """Chooses the password through the e-mailed link, logs in, returns
    /users/me and the session's headers (choosing the password ends every
    earlier session, so only this login's token is valid)."""
    assert client.post("/auth/reset-password", json={"token": token, "password": password}).status_code == 200
    login = client.post("/token", data={"username": user_name, "password": password})
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    return client.get("/users/me", headers=headers).json(), headers


# --- An open account: credited, nothing else ---------------------------------------

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


def test_paying_with_an_open_accounts_e_mail_only_gives_it_credits(client, db_session, stripe_items):
    """Alex's « Access »: no login, and the e-mail and the password of an open
    account never change — whoever paid, the owner of the address keeps it."""
    owner = customer(db_session, "titulaire", "titulaire@agence-test.fr", credits=3)
    before = db_session.get(models.User, owner["id"])
    hashed, version = before.hashed_password, before.session_version
    stripe_items.answers["cs_test_tiers"] = [item(2)]

    response = signed(client, unit_session("cs_test_tiers", quantity=2, email="Titulaire@Agence-Test.fr",
                                           details={"individual_name": "Quelqu'un d'Autre", "business_name": "Autre",
                                                    "phone": "+33 9 99 99 99 99"}))
    assert response.json() == {"received": True, "result": "credited"}
    assert "set-cookie" not in response.headers               # nobody is logged in
    db_session.expire_all()
    after = db_session.get(models.User, owner["id"])
    assert after.page_credits == 5
    assert (after.email, after.user_name, after.hashed_password, after.session_version, after.status) == (
        "titulaire@agence-test.fr", "titulaire", hashed, version, "active")
    assert (after.first_name, after.last_name, after.phone_number, after.company) == ("Marc", "Unité", "0102030405", None)
    assert db_session.query(models.AuthToken).count() == 0     # no password link for an open account
    [confirmation] = mailer.OUTBOX
    assert confirmation.kind == "purchase_confirmation" and "mot-de-passe" not in confirmation.body
    assert client.post("/token", data={"username": "titulaire", "password": "secret-pass"}).status_code == 200


def test_66_documents_are_66_credits_not_the_pack_100_their_price_equals(client, db_session, stripe_items):
    # 66 × 1,80 € = 118,80 € TTC: exactly Pack 100's price (99 € HT). Identified
    # by the amount, as packs are, this payment would credit 100.
    marc = customer(db_session, "marc", "marc@agence-test.fr", credits=0)
    stripe_items.answers["cs_test_66"] = [item(66)]
    event = unit_session("cs_test_66", quantity=66, email="marc@agence-test.fr", client_reference_id=marc["id"])
    assert event["data"]["object"]["amount_total"] == billing.price_ttc_cents(100) == 11_880

    assert signed(client, event).json()["result"] == "credited"
    assert credits_of(db_session, marc) == 66
    assert db_session.query(models.Purchase).one().pack == billing.UNIT_PACK


def test_client_reference_id_names_the_account_when_present(client, db_session, stripe_items):
    # Alex's « more robust » link: the app sends client_reference_id, so the
    # right account is credited whatever e-mail was typed at checkout.
    payer = customer(db_session, "payeur", "payeur@agence-test.fr")
    other = customer(db_session, "autre", "autre@agence-test.fr")
    stripe_items.answers["cs_test_ref"] = [item(5)]
    event = unit_session("cs_test_ref", quantity=5, email="autre@agence-test.fr", client_reference_id=payer["id"])
    assert signed(client, event).json()["result"] == "credited"
    assert (credits_of(db_session, payer), credits_of(db_session, other)) == (15, 10)
    assert [e.to for e in mailer.OUTBOX] == ["payeur@agence-test.fr"]


def test_one_document_is_said_in_the_singular(client, db_session, stripe_items):
    customer(db_session, "solo", "solo@agence-test.fr")
    stripe_items.answers["cs_test_one"] = [item(1)]
    assert signed(client, unit_session("cs_test_one", quantity=1, email="solo@agence-test.fr")).json()["result"] == "credited"
    assert mailer.OUTBOX[0].subject == "Votre document ScanID est disponible"
    assert "achat à la carte : 1 document a été ajouté à votre espace ScanID ; il est valable jusqu'au" in mailer.OUTBOX[0].body


# --- No account: the purchase opens one ---------------------------------------------

def test_an_address_without_an_account_gets_one_with_its_documents_and_the_welcome_e_mail(client, db_session, stripe_items):
    stripe_items.answers["cs_test_new"] = [item(12)]
    event = unit_session("cs_test_new", quantity=12, email="Nadia.Nouvelle@Agence-Test.fr",
                         details={"individual_name": "Nadia Nouvelle-Cliente", "name": "N NOUVELLE",
                                  "business_name": "Agence Nouvelle Test", "phone": "+33 1 00 00 00 12"})

    response = signed(client, event)
    assert response.status_code == 200 and response.json() == {"received": True, "result": "credited"}
    assert "set-cookie" not in response.headers               # a purchase never logs anyone in

    user = db_session.query(models.User).one()
    assert (user.email, user.user_name, user.status, user.role, user.page_credits, user.uploaded_pages_count) == (
        "nadia.nouvelle@agence-test.fr", "nadia.nouvelle@agence-test.fr", "active", "user", 12, 0)
    assert (user.first_name, user.last_name, user.company, user.phone_number) == (
        "Nadia", "Nouvelle-Cliente", "Agence Nouvelle Test", "+33 1 00 00 00 12")
    purchase = db_session.query(models.Purchase).one()
    assert (purchase.user_id, purchase.pack, purchase.credits, purchase.amount_ht_cents, purchase.status,
            purchase.stripe_session_id) == (user.id, billing.UNIT_PACK, 12, 1_800, "paid", "cs_test_new")

    # No password exists until the owner of the address chooses one.
    for attempt in ("secret-pass", STRONG, user.hashed_password):
        assert client.post("/token", data={"username": user.user_name, "password": attempt}).status_code == 401

    [welcome] = mailer.OUTBOX
    assert (welcome.to, welcome.kind) == ("nadia.nouvelle@agence-test.fr", "purchase_welcome")
    assert welcome.subject == "Votre espace ScanID est ouvert — 12 documents disponibles"
    for expected in ("Bonjour Nadia,", "Merci pour votre achat à la carte : 12 documents ont été ajoutés à votre espace ScanID ; ils sont valables jusqu'au",
                     "Adresse : https://scanid.fr/app/", "Identifiant : nadia.nouvelle@agence-test.fr",
                     "valable 48 heures, utilisable une seule fois", "guide-photo.html",
                     "Le détail de vos achats est dans « Mon compte » → « Mes achats »."):
        assert expected in welcome.body
    assert "provisoire" not in welcome.body                    # never a password by e-mail

    me, headers = logs_in_with(client, "nadia.nouvelle@agence-test.fr", welcome_token(welcome))
    assert me["page_credits"] == 12
    purchases = client.get("/users/me/purchases", headers=headers).json()
    assert [(row["pack"], row["credits"]) for row in purchases] == [(0, 12)]

    for _ in range(2):                                         # Stripe sends the event again
        assert signed(client, event).json()["result"] == "duplicate"
    assert db_session.query(models.User).count() == 1
    assert db_session.query(models.Purchase).count() == 1
    assert len(mailer.OUTBOX) == 1
    assert stripe_items.calls == ["cs_test_new"]


def test_one_document_opens_the_account_in_the_singular(client, db_session, stripe_items):
    stripe_items.answers["cs_test_new_one"] = [item(1)]
    assert signed(client, unit_session("cs_test_new_one", quantity=1, email="une@agence-test.fr")).json()["result"] == "credited"
    [welcome] = mailer.OUTBOX
    assert welcome.subject == "Votre espace ScanID est ouvert — 1 document disponible"
    assert "achat à la carte : 1 document a été ajouté à votre espace ScanID ; il est valable jusqu'au" in welcome.body


@pytest.mark.parametrize("session_changes, expected", [
    ({"customer_details": {"email": "x@agence-test.fr", "individual_name": "Léa Marie Dubois", "name": "LEA DUBOIS",
                           "business_name": "Agence Léa", "phone": "+33 6 11 22 33 44"}},
     ("Léa", "Marie Dubois", "Agence Léa", "+33 6 11 22 33 44")),
    ({"customer_details": {"email": "x@agence-test.fr"},
      "collected_information": {"individual_name": "Paul Collecte", "business_name": "Agence Collecte"}},
     ("Paul", "Collecte", "Agence Collecte", "")),
    ({"customer_details": {"email": "x@agence-test.fr", "name": "Jean Carte"}}, ("Jean", "Carte", None, "")),
    ({"customer_details": {"email": "x@agence-test.fr"}}, ("", "", None, "")),
])
def test_the_new_account_takes_the_name_business_name_and_phone_typed_at_checkout(session_changes, expected):
    identity = billing.checkout_identity(session_changes)
    assert (identity["first_name"], identity["last_name"], identity["company"], identity["phone_number"]) == expected


# --- A trial request: still waiting, or refused ---------------------------------------

def test_a_trial_request_still_waiting_is_opened_with_the_documents_bought_only(client, db_session, stripe_items):
    assert client.post("/trial-requests", json=TRIAL).status_code == 201
    pending = db_session.query(models.User).one()
    assert (pending.status, pending.page_credits) == ("pending", 20)
    mailer.OUTBOX.clear()
    stripe_items.answers["cs_test_attente"] = [item(10)]

    response = signed(client, unit_session("cs_test_attente", quantity=10, email="ATTENTE@agence-test.fr",
                                           details={"individual_name": "Autre Nom", "business_name": "Autre"}))
    assert response.json()["result"] == "credited"

    db_session.expire_all()
    user = db_session.get(models.User, pending.id)
    # Open at once, with the documents bought: not 30 — the 20 trial documents
    # come only with Alex's « Valider ».
    assert (user.status, user.page_credits) == ("active", 10)
    assert (user.first_name, user.last_name, user.company) == ("Anne", "Attente-Test", "Agence Attente Test")
    assert db_session.query(models.TrialRequest).one().status == "pending"   # still Alex's to decide
    [welcome] = mailer.OUTBOX
    assert (welcome.to, welcome.kind, welcome.subject) == (
        "attente@agence-test.fr", "purchase_welcome", "Votre espace ScanID est ouvert — 10 documents disponibles")
    assert logs_in_with(client, "attente@agence-test.fr", welcome_token(welcome))[0]["page_credits"] == 10


def test_a_trial_request_alex_refused_is_like_no_account(client, db_session, stripe_items):
    assert client.post("/trial-requests", json=TRIAL).status_code == 201
    trials.reject(db_session, db_session.query(models.TrialRequest).one().id)
    mailer.OUTBOX.clear()
    stripe_items.answers["cs_test_refus"] = [item(4)]

    assert signed(client, unit_session("cs_test_refus", quantity=4, email="attente@agence-test.fr")).json()["result"] == "credited"

    db_session.expire_all()
    user = db_session.query(models.User).one()
    assert (user.status, user.page_credits) == ("active", 4)            # the purchased documents only
    assert db_session.query(models.TrialRequest).one().status == "rejected"
    [welcome] = mailer.OUTBOX
    assert welcome.kind == "purchase_welcome"
    assert logs_in_with(client, "attente@agence-test.fr", welcome_token(welcome))[0]["page_credits"] == 4


# --- « Demandes d'essai » after a purchase: Valider adds the 20, Refuser and the purge keep the account ---

@pytest.fixture()
def admin(db_session):
    make_user(db_session, "chef", role="admin")
    return auth_headers("chef")


def _trial_then_purchase(client, db_session, stripe_items, quantity, session_id="cs_test_attente"):
    """A trial request still waiting, then an « à la carte » purchase from its e-mail."""
    assert client.post("/trial-requests", json=TRIAL).status_code == 201
    stripe_items.answers[session_id] = [item(quantity)]
    assert signed(client, unit_session(session_id, quantity=quantity, email="attente@agence-test.fr")).json()["result"] == "credited"
    mailer.OUTBOX.clear()
    return db_session.query(models.TrialRequest).one().id


def _account(db_session):
    db_session.expire_all()
    return db_session.query(models.User).filter(models.User.role == "user").one()


def test_the_admin_list_says_which_accounts_a_purchase_has_opened(client, db_session, stripe_items, admin):
    _trial_then_purchase(client, db_session, stripe_items, 10)
    assert client.post("/trial-requests", json={**TRIAL, "email": "seul@agence-test.fr"}).status_code == 201
    listed = client.get("/admin/trial-requests", headers=admin).json()
    assert {(row["email"], row["account_open"]) for row in listed} == {
        ("attente@agence-test.fr", True), ("seul@agence-test.fr", False)}


def test_valider_after_a_purchase_adds_the_20_trial_documents_without_a_new_link(client, db_session, stripe_items, admin):
    request_id = _trial_then_purchase(client, db_session, stripe_items, 10)
    links = db_session.query(models.AuthToken).count()

    decided = client.post(f"/admin/trial-requests/{request_id}/validate", headers=admin)
    assert decided.status_code == 200
    # The app's message reads `account_open`: the 20 documents, not a welcome.
    assert (decided.json()["status"], decided.json()["account_open"]) == ("validated", True)
    assert client.get("/admin/trial-requests", headers=admin).json() == []
    account = _account(db_session)
    assert (account.status, account.page_credits) == ("active", 10 + 20)
    assert db_session.query(models.AuthToken).count() == links         # the purchase's link stays the only one
    [email] = mailer.OUTBOX
    assert (email.to, email.kind, email.subject) == (
        "attente@agence-test.fr", "trial_credits", "20 documents offerts ajoutés à votre espace ScanID")
    assert "20 documents offerts ont été ajoutés à votre espace ScanID" in email.body
    assert "Votre identifiant : attente@agence-test.fr" in email.body and "mot-de-passe#token" not in email.body


def test_refuser_after_a_purchase_refuses_the_request_only(client, db_session, stripe_items, admin):
    request_id = _trial_then_purchase(client, db_session, stripe_items, 5)
    [link] = db_session.query(models.AuthToken).all()

    refused = client.post(f"/admin/trial-requests/{request_id}/reject", headers=admin)
    assert refused.status_code == 200
    assert (refused.json()["status"], refused.json()["account_open"]) == ("rejected", True)
    account = _account(db_session)
    assert (account.status, account.page_credits) == ("active", 5)     # the account stays open, with its documents
    assert mailer.OUTBOX == []
    assert client.post(f"/admin/trial-requests/{request_id}/validate", headers=admin).status_code == 409
    assert db_session.query(models.AuthToken).one().id == link.id      # its password link still works


def test_the_30_day_clean_up_after_a_purchase_removes_the_requests_only(client, db_session, stripe_items, admin):
    _trial_then_purchase(client, db_session, stripe_items, 6)
    assert client.post("/trial-requests", json={**TRIAL, "email": "refus@agence-test.fr"}).status_code == 201
    refused_id = db_session.query(models.TrialRequest).filter_by(email="refus@agence-test.fr").one().id
    trials.reject(db_session, refused_id)
    stripe_items.answers["cs_test_refus"] = [item(2)]
    assert signed(client, unit_session("cs_test_refus", quantity=2, email="refus@agence-test.fr")).json()["result"] == "credited"
    for request in db_session.query(models.TrialRequest).all():
        request.created_at = request.created_at.replace(year=request.created_at.year - 1)
    db_session.commit()

    assert trials.purge(db_session) == 2
    assert db_session.query(models.TrialRequest).count() == 0
    db_session.expire_all()
    accounts = {u.email: (u.status, u.page_credits) for u in db_session.query(models.User).filter(models.User.role == "user")}
    assert accounts == {"attente@agence-test.fr": ("active", 6), "refus@agence-test.fr": ("active", 2)}
    assert db_session.query(models.Purchase).count() == 2


def test_valider_at_the_moment_a_purchase_opens_the_account_still_adds_the_documents(client, db_session, stripe_items, monkeypatch):
    # Alex clicks « Valider » while the payment's webhook opens the account:
    # the request was read « en attente », the account is open when written.
    assert client.post("/trial-requests", json=TRIAL).status_code == 201
    request_id = db_session.query(models.TrialRequest).one().id
    stripe_items.answers["cs_test_course"] = [item(8)]
    real_decide = trials._decide

    def payment_lands_first(db, request, status):
        assert signed(client, unit_session("cs_test_course", quantity=8, email="attente@agence-test.fr")).json()["result"] == "credited"
        real_decide(db, request, status)

    monkeypatch.setattr(trials, "_decide", payment_lands_first)
    request, user, already_open = trials.validate(db_session, request_id)
    assert (request["status"], request["account_open"], already_open) == ("validated", True, True)
    account = _account(db_session)
    assert (account.status, account.page_credits) == ("active", 8 + 20)


def test_refuser_at_the_moment_a_purchase_opens_the_account_leaves_it_open(client, db_session, stripe_items, monkeypatch):
    assert client.post("/trial-requests", json=TRIAL).status_code == 201
    request_id = db_session.query(models.TrialRequest).one().id
    stripe_items.answers["cs_test_course"] = [item(8)]
    real_decide = trials._decide

    def payment_lands_first(db, request, status):
        assert signed(client, unit_session("cs_test_course", quantity=8, email="attente@agence-test.fr")).json()["result"] == "credited"
        real_decide(db, request, status)

    monkeypatch.setattr(trials, "_decide", payment_lands_first)
    refused = trials.reject(db_session, request_id)
    assert (refused["status"], refused["account_open"]) == ("rejected", True)
    account = _account(db_session)
    assert (account.status, account.page_credits) == ("active", 8)


def test_two_decisions_at_once_decide_once(client, db_session, monkeypatch):
    # « Valider » read the request as waiting; another click refused it before
    # this one writes: 409, and nothing of the validation happens.
    assert client.post("/trial-requests", json=TRIAL).status_code == 201
    request_id = db_session.query(models.TrialRequest).one().id
    real_read = trials._pending_request_and_user

    def other_click_first(db, rid):
        found = real_read(db, rid)
        db.execute(sa_update(models.TrialRequest).where(models.TrialRequest.id == rid).values(status="rejected"))
        db.commit()
        return found

    monkeypatch.setattr(trials, "_pending_request_and_user", other_click_first)
    with pytest.raises(trials.TrialRequestError, match="déjà été traitée"):
        trials.validate(db_session, request_id)
    account = _account(db_session)
    assert (account.status, account.page_credits) == ("pending", 20)


# --- Alex's three checks, for the accounts a purchase opens --------------------------

def test_a_request_without_a_valid_stripe_signature_opens_and_credits_nothing(client, db_session, stripe_items):
    stripe_items.answers["cs_test_unite_1"] = [item(5)]
    event = unit_session(email="nouveau@agence-test.fr")
    assert signed(client, event, secret="whsec_wrong").status_code == 400
    assert signed(client, event, at=time.time() - 301).status_code == 400      # an old request replayed
    assert client.post("/stripe/webhook", json=event).status_code == 400        # no signature at all
    assert db_session.query(models.User).count() == 0
    assert db_session.query(models.Purchase).count() == 0
    assert mailer.OUTBOX == [] and stripe_items.calls == []


def test_an_unpaid_session_opens_and_credits_nothing(client, db_session, stripe_items):
    stripe_items.answers["cs_test_attendu"] = [item(5)]
    event = unit_session("cs_test_attendu", quantity=5, email="nouveau@agence-test.fr", paid="unpaid")
    assert signed(client, event).json()["result"] == "not_paid"
    assert db_session.query(models.User).count() == 0
    assert mailer.OUTBOX == [] and stripe_items.calls == []
    arrived = unit_session("cs_test_attendu", quantity=5, email="nouveau@agence-test.fr",
                           kind="checkout.session.async_payment_succeeded")
    assert signed(client, arrived).json()["result"] == "credited"
    assert db_session.query(models.User).one().page_credits == 5


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


# --- Races -------------------------------------------------------------------------

def _first_call_returns(monkeypatch, name, value):
    """billing.<name> answers `value` on its first call, then for real: two
    deliveries racing each other both got past that first look."""
    real, calls = getattr(billing, name), []

    def raced(*args):
        calls.append(args)
        return value if len(calls) == 1 else real(*args)

    monkeypatch.setattr(billing, name, raced)


def test_a_race_between_two_deliveries_is_stopped_by_the_database(client, db_session, stripe_items, monkeypatch):
    marc = customer(db_session, "marc", "marc@agence-test.fr", credits=0)
    stripe_items.answers["cs_test_unite_1"] = [item(37)]
    assert signed(client, unit_session(email="marc@agence-test.fr")).json()["result"] == "credited"
    _first_call_returns(monkeypatch, "already_processed", False)
    outcome = billing.credit_checkout_session(db_session, unit_session(email="marc@agence-test.fr")["data"]["object"])
    assert outcome.status == "duplicate"
    assert credits_of(db_session, marc) == 37
    assert db_session.query(models.Purchase).count() == 1


def test_the_same_new_address_delivered_twice_at_once_opens_one_account(client, db_session, stripe_items, monkeypatch):
    stripe_items.answers["cs_test_new"] = [item(6)]
    event = unit_session("cs_test_new", quantity=6, email="double@agence-test.fr")
    assert signed(client, event).json()["result"] == "credited"
    _first_call_returns(monkeypatch, "already_processed", False)
    _first_call_returns(monkeypatch, "unit_buyer", (None, "double@agence-test.fr"))   # it found no account either
    assert billing.credit_checkout_session(db_session, event["data"]["object"]).status == "duplicate"
    assert db_session.query(models.User).one().page_credits == 6
    assert db_session.query(models.Purchase).count() == 1


def test_an_account_opened_meanwhile_by_another_payment_is_credited(client, db_session, stripe_items, monkeypatch):
    # Two payments from the same new address at the same moment: both find no
    # account; the second one's account loses on the UNIQUE e-mail, looks again
    # and credits the account the first one opened.
    stripe_items.answers.update({"cs_test_a": [item(3)], "cs_test_b": [item(4)]})
    assert signed(client, unit_session("cs_test_a", quantity=3, email="duo@agence-test.fr")).json()["result"] == "credited"
    _first_call_returns(monkeypatch, "unit_buyer", (None, "duo@agence-test.fr"))
    outcome = billing.credit_checkout_session(db_session, unit_session("cs_test_b", quantity=4, email="duo@agence-test.fr")["data"]["object"])
    assert (outcome.status, outcome.password_token) == ("credited", None)   # already open: no second link
    assert db_session.query(models.User).one().page_credits == 7
    assert db_session.query(models.Purchase).count() == 2


def test_a_trial_account_opened_meanwhile_keeps_the_documents_already_bought(client, db_session, stripe_items, monkeypatch):
    # Read « en attente », but another payment (or /signup) opened the account
    # before this one writes: the documents are added, not put in place of the
    # others, and no second password link is made.
    assert client.post("/trial-requests", json=TRIAL).status_code == 201
    stale = crud.get_user(db_session, db_session.query(models.User).one().id)
    assert stale["status"] == "pending"
    stripe_items.answers.update({"cs_test_a": [item(3)], "cs_test_b": [item(4)]})
    assert signed(client, unit_session("cs_test_a", quantity=3, email="attente@agence-test.fr")).json()["result"] == "credited"
    _first_call_returns(monkeypatch, "unit_buyer", (stale, "attente@agence-test.fr"))
    outcome = billing.credit_checkout_session(db_session, unit_session("cs_test_b", quantity=4, email="attente@agence-test.fr")["data"]["object"])
    assert (outcome.status, outcome.password_token) == ("credited", None)
    db_session.expire_all()
    user = db_session.query(models.User).one()
    assert (user.status, user.page_credits) == ("active", 3 + 4)
    assert db_session.query(models.AuthToken).count() == 1           # the first purchase's link only


# --- What cannot be established is reported to Alex ------------------------------------

@pytest.mark.parametrize("setup, session_changes, answer, reason", [
    (None, {"customer_details": {}}, [item(5)], "le paiement ne porte aucune adresse e-mail"),
    (None, {"customer_details": {"email": "pas-une-adresse"}}, [item(5)], "l'adresse e-mail du paiement n'est pas valide"),
    (None, {"client_reference_id": "compte-inconnu"}, [item(5)], "client_reference_id ne correspond à aucun compte ScanID"),
    ("twins", {}, [item(5)], "plusieurs comptes ScanID ont cette adresse e-mail"),
    ("login", {"customer_details": {"email": "identifiant@agence-test.fr"}}, [item(5)],
     "cette adresse e-mail est l'identifiant d'un autre compte ScanID"),
    (None, {"currency": "usd"}, [item(5)], "une autre devise que l'euro"),
    (None, {}, billing.StripeApiError("l'API Stripe a répondu 401 à la lecture des articles"), "répondu 401"),
    (None, {"customer_details": {"email": "nouveau@agence-test.fr"}},
     billing.StripeApiError("l'API Stripe a répondu 401 à la lecture des articles"), "répondu 401"),
    (None, {}, [item(5), item(2)], "un seul article"),
    (None, {"customer_details": {"email": "nouveau@agence-test.fr"}}, [item(5), item(2)], "un seul article"),
    (None, {}, [], "un seul article"),
    (None, {}, [item(0)], "un seul article"),
    (None, {}, [{"id": "li_x", "quantity": "5"}], "un seul article"),
])
def test_what_cannot_be_established_is_reported_to_alex_and_credits_nothing(
        client, db_session, stripe_items, setup, session_changes, answer, reason):
    marc = customer(db_session, "marc", "marc@agence-test.fr")
    if setup == "twins":   # the same address twice, in two letter cases: whose credits?
        customer(db_session, "marc2", "Marc@Agence-Test.fr")
    if setup == "login":   # an account whose login name is that address, with another e-mail
        customer(db_session, "identifiant@agence-test.fr", "ailleurs@agence-test.fr")
    accounts = db_session.query(models.User).count()
    stripe_items.answers["cs_test_unite_1"] = answer
    event = unit_session(email="marc@agence-test.fr")
    event["data"]["object"].update(session_changes)

    response = signed(client, event)
    assert response.status_code == 200 and response.json()["result"] == "unmatched"
    assert credits_of(db_session, marc) == 10
    assert db_session.query(models.User).count() == accounts           # no account opened either
    assert db_session.query(models.Purchase).count() == 0
    assert db_session.query(models.AuthToken).count() == 0
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
    assert db_session.query(models.User).count() == 1                   # and no account is opened
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
    assert mailer.OUTBOX[0].subject == "Vos 1 000 documents ScanID sont disponibles"   # the pack e-mail, not the à la carte one
    assert stripe_items.calls == []


# --- The line items, read from Stripe --------------------------------------------------

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

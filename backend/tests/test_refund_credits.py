"""A refund takes the credits back (Alex, « After the deployment of 08/10 »,
09/10/2026, §3): on a FULL refund, the unused credits of that purchase are
removed — never below zero — and « Mes achats » marks the line « Remboursé le
JJ/MM/AAAA »; on a partial refund nothing changes automatically and Alex is
told. The same charge.refunded event issues the credit note (invoices, 08/10),
whose switch is its own.

Stripe cannot be reached from the suite: the webhooks are signed as Stripe signs
them, and billing.session_for_payment_intent (a purchase paid before
08/10/2026 is found through its Checkout Session) is a stand-in. All
identities are fictional."""
import io
import json
import urllib.error
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import billing
import invoicing
import mailer
import main
import models
import schema_migrations
from tests.helpers import auth_headers
from tests.test_invoices import (LINK, SECRET, item, pack_event, plain, refund_event, signed, signup, unit_event,
                                 user_id_of)

CLAIRE = "claire.achat@agence-test.fr"
ALEX = "contact@scanid.fr"
REAL_LOOKUP = billing.session_for_payment_intent      # kept before the fixture stands in for it


@pytest.fixture(autouse=True)
def environment(monkeypatch):
    monkeypatch.setenv("MAIL_BACKEND", "outbox")
    monkeypatch.setenv("MAIL_ADMIN_TO", ALEX)
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", SECRET)
    monkeypatch.setenv("STRIPE_UNIT_PAYMENT_LINK_ID", LINK)
    monkeypatch.setenv("STRIPE_API_KEY", "rk_test_checkout_sessions_read")
    monkeypatch.delenv("INVOICES_ENABLED", raising=False)
    mailer.OUTBOX.clear()
    yield
    mailer.OUTBOX.clear()


@pytest.fixture(autouse=True)
def stripe_sessions(monkeypatch):
    """Stands in for billing.session_for_payment_intent: `answers[pi]` is the
    session Stripe names (or the StripeApiError it fails with); `calls` records
    each question. Unknown payments: no session."""
    answers, calls = {}, []

    def fake(payment_intent):
        calls.append(payment_intent)
        answer = answers.get(payment_intent)
        if isinstance(answer, Exception):
            raise answer
        return answer

    monkeypatch.setattr(billing, "session_for_payment_intent", fake)
    return answers, calls


@pytest.fixture
def stripe_items(monkeypatch):
    answers = {}
    monkeypatch.setattr(billing, "fetch_line_items", lambda session_id: answers.get(session_id, []))
    return answers


@pytest.fixture
def pushes(monkeypatch):
    """The live updates sent to open pages (SSE), instead of the connections."""
    sent = []

    async def record(user_id, message):
        sent.append((user_id, message))

    monkeypatch.setattr(main.manager, "send_update", record)
    return sent


def _claire_with_pack(client, db, pushes=None, **event):
    """Claire's account (/app/inscription) and her Pack 100, paid and credited —
    its e-mail and its live update left out of what the test then looks at."""
    signup(client)
    claire = user_id_of(db, CLAIRE)
    assert signed(client, pack_event(claire, **event)).json()["result"] == "credited"
    mailer.OUTBOX.clear()
    if pushes is not None:
        pushes.clear()
    return claire


def _balance(db, user_id):
    db.expire_all()
    return db.get(models.User, user_id).page_credits


def _purchase(db, session_id="cs_live_pack_1"):
    db.expire_all()
    return db.query(models.Purchase).filter(models.Purchase.stripe_session_id == session_id).one()


def _set_balance(db, user_id, credits):
    db.get(models.User, user_id).page_credits = credits
    db.commit()


def _as_utc(value):
    """SQLite gives naive UTC datetimes back."""
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


# --- A full refund -------------------------------------------------------------------

def test_a_full_refund_takes_the_pack_back_and_marks_the_purchase_once(client, db_session, pushes, stripe_items):
    claire = _claire_with_pack(client, db_session, pushes)
    assert _balance(db_session, claire) == 100
    yesterday = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(days=1)

    response = signed(client, refund_event(11_880, created=int(yesterday.timestamp())))
    assert response.status_code == 200
    assert response.json() == {"received": True, "result": "disabled", "credits": "taken_back"}
    assert _balance(db_session, claire) == 0
    purchase = _purchase(db_session)
    assert (purchase.status, _as_utc(purchase.refunded_at), purchase.credits_taken_back) == ("paid", yesterday, 100)
    assert mailer.OUTBOX == []                       # Alex made the refund: nothing to tell him
    assert pushes == [(claire, {"type": "credit_update"})]   # her open page shows the new balance

    [row] = client.get("/users/me/purchases", headers=auth_headers(CLAIRE)).json()
    assert row["pack"] == 100 and _as_utc(datetime.fromisoformat(row["refunded_at"])) == yesterday

    # Stripe delivers again — after new credits were bought: they stay.
    stripe_items["cs_live_unit_1"] = [item(3)]
    assert signed(client, unit_event(3, email=CLAIRE)).json()["result"] == "credited"
    for _ in range(2):
        assert signed(client, refund_event(11_880)).json()["credits"] == "duplicate"
    assert _balance(db_session, claire) == 3
    assert _purchase(db_session).credits_taken_back == 100 and mailer.OUTBOX[-1].kind == "purchase_confirmation"


def test_used_credits_cannot_come_back_the_balance_never_goes_below_zero(client, db_session):
    claire = _claire_with_pack(client, db_session)
    _set_balance(db_session, claire, 70)             # 30 documents read since the purchase
    assert signed(client, refund_event(11_880)).json()["credits"] == "taken_back"
    assert _balance(db_session, claire) == 0 and _purchase(db_session).credits_taken_back == 70


def test_a_balance_already_below_zero_is_left_as_it_is(client, db_session):
    claire = _claire_with_pack(client, db_session)
    _set_balance(db_session, claire, -5)             # a job read more pages than the balance held
    assert signed(client, refund_event(11_880)).json()["credits"] == "taken_back"
    assert _balance(db_session, claire) == -5 and _purchase(db_session).credits_taken_back == 0
    assert _purchase(db_session).refunded_at is not None


def test_a_refunded_unit_purchase_takes_its_documents_back_and_the_pack_stays(client, db_session, stripe_items):
    claire = _claire_with_pack(client, db_session)
    stripe_items["cs_live_unit_1"] = [item(3)]
    assert signed(client, unit_event(3, email=CLAIRE)).json()["result"] == "credited"
    assert _balance(db_session, claire) == 103

    assert signed(client, refund_event(540, payment_intent="pi_live_unit_1", amount=540)).json()["credits"] == "taken_back"
    assert _balance(db_session, claire) == 100
    assert (_purchase(db_session, "cs_live_unit_1").credits_taken_back, _purchase(db_session).refunded_at) == (3, None)
    rows = {r["pack"]: r["refunded_at"] for r in client.get("/users/me/purchases", headers=auth_headers(CLAIRE)).json()}
    assert rows[0] is not None and rows[100] is None   # only the unit purchase says « Remboursé le … »


def test_an_account_deleted_since_is_marked_refunded_and_nothing_is_taken(client, db_session, pushes):
    claire = _claire_with_pack(client, db_session, pushes)
    db_session.delete(db_session.get(models.User, claire))      # what « Supprimer » does (crud.delete_user)
    db_session.commit()
    assert signed(client, refund_event(11_880)).json()["credits"] == "taken_back"
    purchase = _purchase(db_session)
    assert purchase.refunded_at is not None and purchase.credits_taken_back == 0
    assert pushes == [] and mailer.OUTBOX == []


# --- A partial refund ----------------------------------------------------------------

def test_a_partial_refund_changes_nothing_and_alex_is_told_then_the_rest_takes_the_credits(client, db_session):
    claire = _claire_with_pack(client, db_session)

    assert signed(client, refund_event(2_000)).json() == {"received": True, "result": "disabled", "credits": "partial"}
    assert _balance(db_session, claire) == 100
    purchase = _purchase(db_session)
    assert (purchase.refunded_at, purchase.credits_taken_back) == (None, None)
    [mail] = mailer.OUTBOX
    assert (mail.to, mail.kind, mail.subject) == (ALEX, "refund_partial", "Remboursement partiel — crédits non modifiés")
    body = plain(mail.body)
    paid_on = invoicing.date_fr(invoicing.to_paris(purchase.paid_at).date())
    for line in ("l'application ne retire aucun crédit : corrigez le solde du client à la main si nécessaire "
                 "(Administration → Gérer les utilisateurs → Crédits pages)",
                 f"Achat : Pack 100, payé le {paid_on}", "Montant payé (TTC) : 118,80 €",
                 "Total remboursé sur ce paiement : 20,00 €",
                 f"Client : Agence Test Voyages — Claire Achat — {CLAIRE}", "Crédits du client à cet instant : 100",
                 "Paiement Stripe : pi_live_pack_1", "Opération Stripe : ch_live_1",
                 "Si le reste du paiement est remboursé plus tard, l'application retirera alors les crédits"):
        assert line in body, line
    assert client.get("/users/me/purchases", headers=auth_headers(CLAIRE)).json()[0]["refunded_at"] is None

    # The rest, later: the payment is now refunded in full.
    mailer.OUTBOX.clear()
    assert signed(client, refund_event(11_880)).json()["credits"] == "taken_back"
    assert _balance(db_session, claire) == 0 and mailer.OUTBOX == []
    # A partial event Stripe delivers late: already done, nobody told twice.
    assert signed(client, refund_event(2_000)).json()["credits"] == "duplicate"
    assert _balance(db_session, claire) == 0 and mailer.OUTBOX == []


# --- With the invoices switched on: the credit note goes with it ---------------------

def test_with_invoices_on_the_same_refund_issues_the_credit_note_and_takes_the_credits(client, db_session, monkeypatch, pushes):
    monkeypatch.setenv("INVOICES_ENABLED", "1")
    claire = _claire_with_pack(client, db_session, pushes)
    assert signed(client, refund_event(11_880)).json() == {"received": True, "result": "issued", "credits": "taken_back"}
    assert _balance(db_session, claire) == 0
    kinds = [row.kind for row in db_session.query(models.Invoice).order_by(models.Invoice.issued_at)]
    assert kinds == ["invoice", "credit_note"]
    assert [(m.to, m.kind) for m in mailer.OUTBOX] == [(CLAIRE, "credit_note")]
    assert pushes == [(claire, {"type": "credit_update"})]


# --- Purchases paid before 08/10/2026: found through Stripe --------------------------

def test_an_old_purchase_is_found_through_its_session_and_keeps_the_payment_intent(client, db_session, monkeypatch,
                                                                                    stripe_sessions):
    answers, calls = stripe_sessions
    claire = _claire_with_pack(client, db_session, payment_intent=None)      # paid before 08/10: no pi_…
    assert _purchase(db_session).stripe_payment_intent is None
    answers["pi_old"] = "cs_live_pack_1"
    monkeypatch.setenv("INVOICES_ENABLED", "1")

    # The credit note now finds the purchase too: « refused » (no invoice was issued for it), not « unmatched ».
    assert signed(client, refund_event(11_880, payment_intent="pi_old")).json() == {
        "received": True, "result": "refused", "credits": "taken_back"}
    assert _balance(db_session, claire) == 0
    assert (_purchase(db_session).stripe_payment_intent, calls) == ("pi_old", ["pi_old"])
    [mail] = mailer.OUTBOX
    assert mail.subject == "Remboursement Stripe sans avoir automatique — à traiter à la main"
    assert "Raison : l'achat n'a pas de facture émise par l'application" in mail.body

    assert signed(client, refund_event(11_880, payment_intent="pi_old")).json()["credits"] == "duplicate"
    assert calls == ["pi_old"]                       # found by its PaymentIntent now: Stripe not asked again


def test_a_payment_no_purchase_matches_is_one_e_mail_to_alex(client, db_session, monkeypatch, stripe_sessions):
    answers, calls = stripe_sessions
    response = signed(client, refund_event(11_880, payment_intent="pi_inconnu"))
    assert response.json() == {"received": True, "result": "disabled", "credits": "unmatched"}
    [mail] = mailer.OUTBOX
    assert (mail.to, mail.kind) == (ALEX, "refund_not_taken_back")
    assert mail.subject == "Remboursement Stripe à traiter à la main — crédits non retirés"
    body = plain(mail.body)
    for line in ("Un remboursement Stripe a été reçu, mais l'application n'a pas retiré les crédits de l'achat.",
                 "Raison : aucun achat ScanID ne correspond à ce paiement (payé hors de l'application, ou enregistré "
                 "à la main)", "Paiement Stripe : pi_inconnu", "Opération Stripe : ch_live_1",
                 "Total remboursé sur ce paiement : 118,80 € (remboursement total)",
                 "Corrigez le solde du client à la main si nécessaire (Administration → Gérer les utilisateurs → "
                 "Crédits pages)."):
        assert line in body, line
    assert "avoir" not in body                       # invoices off: no credit note was due
    assert calls == ["pi_inconnu"]

    # Invoices on: the credit note fails for the same cause — still ONE e-mail, saying both.
    monkeypatch.setenv("INVOICES_ENABLED", "1")
    mailer.OUTBOX.clear()
    assert signed(client, refund_event(500, payment_intent="pi_inconnu", event_id="evt_2")).json() == {
        "received": True, "result": "unmatched", "credits": "unmatched"}
    [mail] = mailer.OUTBOX
    assert mail.kind == "refund_not_taken_back"
    body = plain(mail.body)
    assert "n'a pas retiré les crédits de l'achat et n'a pas émis d'avoir." in body
    assert "(remboursement partiel)" in body and body.endswith("Crédits pages), et établissez l'avoir à la main.")


def test_when_stripe_cannot_be_asked_alex_is_told_why(client, db_session, stripe_sessions):
    answers, _ = stripe_sessions
    answers["pi_x"] = billing.StripeApiError("l'API Stripe a répondu 401 à la recherche de la session")
    assert signed(client, refund_event(11_880, payment_intent="pi_x")).json()["credits"] == "unmatched"
    assert ("Raison : aucun achat ScanID ne correspond à ce paiement (Stripe n'a pas pu être interrogé : l'API "
            "Stripe a répondu 401 à la recherche de la session)") in plain(mailer.OUTBOX[0].body)

    mailer.OUTBOX.clear()
    assert signed(client, refund_event(11_880, payment_intent=None)).json()["credits"] == "unmatched"
    assert "Raison : le remboursement ne porte pas de paiement Stripe lisible" in mailer.OUTBOX[0].body


def test_an_unexpected_error_is_told_to_alex_and_the_credit_note_is_still_issued(client, db_session, monkeypatch):
    monkeypatch.setenv("INVOICES_ENABLED", "1")
    claire = _claire_with_pack(client, db_session)
    monkeypatch.setattr(billing, "take_back_credits", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("DB")))
    assert signed(client, refund_event(11_880)).json() == {"received": True, "result": "issued", "credits": "error"}
    assert _balance(db_session, claire) == 100
    assert [(m.to, m.kind) for m in mailer.OUTBOX] == [(CLAIRE, "credit_note"), (ALEX, "refund_not_taken_back")]
    assert ("Raison : erreur inattendue (RuntimeError) ; aucun crédit n'a été retiré"
            in plain(mailer.OUTBOX[1].body))
    assert "n'a pas émis d'avoir" not in mailer.OUTBOX[1].body   # it was issued


# --- The question to Stripe ------------------------------------------------------------

class _Answer(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_the_session_of_a_payment_intent_is_asked_with_the_restricted_key(monkeypatch):
    asked = []

    def urlopen(request, timeout):
        asked.append((request.full_url, request.get_header("Authorization"), timeout))
        return _Answer(json.dumps({"object": "list", "data": [{"id": "cs_live_old", "object": "checkout.session"}],
                                   "has_more": False}).encode())

    monkeypatch.setattr(billing.urllib.request, "urlopen", urlopen)
    assert REAL_LOOKUP("pi_old") == "cs_live_old"
    assert asked == [("https://api.stripe.com/v1/checkout/sessions?payment_intent=pi_old&limit=1",
                      "Bearer rk_test_checkout_sessions_read", billing.STRIPE_API_TIMEOUT_SECONDS)]

    monkeypatch.setattr(billing.urllib.request, "urlopen", lambda request, timeout: _Answer(b'{"data": []}'))
    assert REAL_LOOKUP("pi_unknown") is None


@pytest.mark.parametrize("failure, message", [
    (urllib.error.HTTPError("u", 403, "Forbidden", {}, None), "l'API Stripe a répondu 403 à la recherche de la session"),
    (OSError("down"), "API Stripe injoignable, ou sa réponse est illisible"),
    (b"not json", "API Stripe injoignable, ou sa réponse est illisible"),
    (b'{"error": {}}', "la réponse de l'API Stripe ne contient pas les sessions"),
])
def test_a_failing_question_to_stripe_says_why(monkeypatch, failure, message):
    def urlopen(request, timeout):
        if isinstance(failure, Exception):
            raise failure
        return _Answer(failure)

    monkeypatch.setattr(billing.urllib.request, "urlopen", urlopen)
    with pytest.raises(billing.StripeApiError, match=message):
        REAL_LOOKUP("pi_x")


def test_without_the_key_stripe_is_not_asked(monkeypatch):
    monkeypatch.delenv("STRIPE_API_KEY")
    monkeypatch.setattr(billing.urllib.request, "urlopen", lambda *a, **k: pytest.fail("Stripe asked"))
    with pytest.raises(billing.StripeApiError, match="clé API Stripe non configurée"):
        REAL_LOOKUP("pi_x")


# --- The database ---------------------------------------------------------------------

def test_the_migration_adds_the_two_refund_columns_to_the_purchases_of_08_10():
    engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
    with engine.begin() as connection:       # `purchases` as production has it since 08/10/2026
        connection.execute(text(
            "CREATE TABLE purchases (id VARCHAR(36) PRIMARY KEY, user_id VARCHAR(36) NOT NULL, pack INTEGER NOT NULL,"
            " credits INTEGER NOT NULL, amount_ht_cents INTEGER NOT NULL, status VARCHAR NOT NULL,"
            " created_at DATETIME NOT NULL, paid_at DATETIME, expires_at DATETIME, stripe_session_id VARCHAR UNIQUE,"
            " amount_paid_cents INTEGER, currency VARCHAR, stripe_payment_intent VARCHAR)"))
        connection.execute(text(
            "INSERT INTO purchases (id, user_id, pack, credits, amount_ht_cents, status, created_at, paid_at,"
            " stripe_session_id, amount_paid_cents, currency, stripe_payment_intent) VALUES ('p1', 'u1', 100, 100,"
            " 9900, 'paid', '2026-10-08 20:00:00', '2026-10-08 20:00:00', 'cs_live_1', 11880, 'eur', 'pi_1')"))
    models.Base.metadata.create_all(engine)
    assert schema_migrations.add_missing_columns(engine) == ["purchases.refunded_at", "purchases.credits_taken_back"]
    session = sessionmaker(bind=engine)()
    try:
        old = session.get(models.Purchase, "p1")
        assert (old.stripe_payment_intent, old.refunded_at, old.credits_taken_back) == ("pi_1", None, None)
    finally:
        session.close()
    assert schema_migrations.add_missing_columns(engine) == []          # idempotent
    assert {"refunded_at", "credits_taken_back"} <= {c["name"] for c in inspect(engine).get_columns("purchases")}


def test_the_refund_columns_are_listed_with_their_manual_sql():
    assert ("purchases", "refunded_at", "TIMESTAMP WITH TIME ZONE") in schema_migrations.ADDED_COLUMNS
    assert ("purchases", "credits_taken_back", "INTEGER") in schema_migrations.ADDED_COLUMNS
    for line in ("ALTER TABLE purchases ADD COLUMN IF NOT EXISTS refunded_at TIMESTAMP WITH TIME ZONE;",
                 "ALTER TABLE purchases ADD COLUMN IF NOT EXISTS credits_taken_back INTEGER;"):
        assert line in schema_migrations.__doc__

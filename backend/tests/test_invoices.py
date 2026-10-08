"""Invoices issued by the app (Alex, « Invoices issued by the app », 08/10/2026):
one French PDF invoice for every purchase the Stripe webhook credits, numbered
in one continuous series, kept as issued, and a credit note for every refund.

Stripe cannot be reached from the suite: the webhooks are signed exactly as
Stripe signs them, and the line items of an « à la carte » session come from a
stand-in for billing.fetch_line_items. All identities and company numbers are
fictional."""
import hashlib
import hmac
import json
import time

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import billing
import billing_identity
import mailer
import models
import schema_migrations

SECRET = "whsec_test_secret_for_the_suite"
LINK = "plink_test_a_la_carte"
STRONG = "Girafe!!12Nuage"


def luhn_siret(first13: str) -> str:
    return next(first13 + d for d in "0123456789" if billing_identity.is_valid_siret(first13 + d))


SIRET = luhn_siret("7328293200007")


@pytest.fixture(autouse=True)
def environment(monkeypatch):
    monkeypatch.setenv("MAIL_BACKEND", "outbox")
    monkeypatch.setenv("MAIL_ADMIN_TO", "contact@scanid.fr")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", SECRET)
    monkeypatch.setenv("STRIPE_UNIT_PAYMENT_LINK_ID", LINK)
    monkeypatch.setenv("STRIPE_API_KEY", "rk_test_checkout_sessions_read")
    monkeypatch.delenv("INVOICES_ENABLED", raising=False)
    for pack in (100, 1000, 3000, 5000):
        monkeypatch.delenv(f"STRIPE_PAYMENT_LINK_{pack}", raising=False)
    mailer.OUTBOX.clear()
    yield
    mailer.OUTBOX.clear()


@pytest.fixture
def stripe_items(monkeypatch):
    """Stands in for billing.fetch_line_items: `answers[session_id]` is the
    session's line items."""
    answers = {}
    monkeypatch.setattr(billing, "fetch_line_items", lambda session_id: answers.get(session_id, []))
    return answers


def item(quantity, unit_amount=180):
    return {"id": "li_test_1", "object": "item", "quantity": quantity, "currency": "eur",
            "amount_subtotal": quantity * unit_amount, "amount_total": quantity * unit_amount,
            "description": "Document à l'unité",
            "price": {"id": "price_test_unite", "unit_amount": unit_amount, "currency": "eur"}}


def signed(client, event, secret=SECRET):
    body = json.dumps(event).encode()
    timestamp = int(time.time())
    signature = hmac.new(secret.encode(), f"{timestamp}.".encode() + body, hashlib.sha256).hexdigest()
    return client.post("/stripe/webhook", content=body,
                       headers={"Stripe-Signature": f"t={timestamp},v1={signature}", "Content-Type": "application/json"})


def pack_event(user_id, pack=100, session_id="cs_live_pack_1", livemode=True, total=None, details=None,
               payment_intent="pi_live_pack_1", kind="checkout.session.completed"):
    """A pack's Checkout Session as the webhook receives it (a « Snapshot » payload)."""
    ht = {100: 9_900, 1000: 69_000, 3000: 189_000, 5000: 295_000}[pack]
    return {"id": f"evt_{session_id}", "type": kind, "livemode": livemode, "data": {"object": {
        "id": session_id, "object": "checkout.session", "livemode": livemode,
        "client_reference_id": user_id, "payment_status": "paid", "payment_intent": payment_intent,
        "amount_subtotal": ht, "amount_total": ht * 6 // 5 if total is None else total, "currency": "eur",
        "customer_details": details if details is not None else {"email": "claire.achat@agence-test.fr"},
    }}}


def unit_event(quantity=37, session_id="cs_live_unit_1", email="Marc.Unite@Agence-Test.fr", livemode=True,
               client_reference_id=None, details=None, payment_intent="pi_live_unit_1"):
    """The « à la carte » link's session: 1,80 € TTC per document, no line items."""
    amount = quantity * 180
    return {"id": f"evt_{session_id}", "type": "checkout.session.completed", "livemode": livemode,
            "data": {"object": {
                "id": session_id, "object": "checkout.session", "livemode": livemode, "payment_link": LINK,
                "client_reference_id": client_reference_id, "payment_status": "paid",
                "payment_intent": payment_intent, "amount_subtotal": amount, "amount_total": amount,
                "currency": "eur", "customer_details": {"email": email, **(details or {})},
            }}}


def signup(client, **changes):
    """/app/inscription for a pack: the account with its billing identity."""
    payload = {
        "pack": 100, "first_name": "Claire", "last_name": "Achat", "company": "Agence Test Voyages",
        "email": "claire.achat@agence-test.fr", "password": STRONG, "phone_number": "+33 1 00 00 00 00",
        "billing_street": "1 rue de l'Essai", "billing_postal_code": "75001", "billing_city": "Paris",
        "billing_country": "France", "siret": SIRET, "vat_number": "FR 12 345678901", "consent": True,
    }
    payload.update(changes)
    response = client.post("/signup", json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def user_id_of(db, email):
    return db.query(models.User).filter(models.User.email == email).one().id


# --- Q2: the data model ------------------------------------------------------------

def _old_purchases_table(engine):
    """`purchases` as production has it before 08/10/2026: no PaymentIntent."""
    with engine.begin() as connection:
        connection.execute(text(
            "CREATE TABLE purchases (id VARCHAR(36) PRIMARY KEY, user_id VARCHAR(36) NOT NULL, pack INTEGER NOT NULL,"
            " credits INTEGER NOT NULL, amount_ht_cents INTEGER NOT NULL, status VARCHAR NOT NULL,"
            " created_at DATETIME NOT NULL, paid_at DATETIME, expires_at DATETIME, stripe_session_id VARCHAR UNIQUE,"
            " amount_paid_cents INTEGER, currency VARCHAR)"))
        connection.execute(text(
            "INSERT INTO purchases (id, user_id, pack, credits, amount_ht_cents, status, created_at, paid_at,"
            " stripe_session_id, amount_paid_cents, currency) VALUES ('p1', 'u1', 100, 100, 9900, 'paid',"
            " '2026-10-06 20:41:00', '2026-10-06 20:41:00', 'cs_live_old', 11880, 'eur')"))


def test_migration_adds_the_payment_intent_to_an_existing_purchases_table():
    engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
    _old_purchases_table(engine)
    models.Base.metadata.create_all(engine)          # what startup does first: new tables only
    assert {"invoices", "invoice_counters"} <= set(inspect(engine).get_table_names())
    assert "stripe_payment_intent" not in {c["name"] for c in inspect(engine).get_columns("purchases")}

    assert schema_migrations.add_missing_columns(engine) == ["purchases.stripe_payment_intent"]

    session = sessionmaker(bind=engine)()
    try:
        old = session.get(models.Purchase, "p1")      # the purchase paid before keeps everything
        assert (old.pack, old.stripe_session_id, old.stripe_payment_intent) == (100, "cs_live_old", None)
    finally:
        session.close()
    assert schema_migrations.add_missing_columns(engine) == []   # idempotent


def test_the_payment_intent_migration_is_listed_with_its_manual_sql():
    assert ("purchases", "stripe_payment_intent", "VARCHAR") in schema_migrations.ADDED_COLUMNS
    assert "ALTER TABLE purchases ADD COLUMN IF NOT EXISTS stripe_payment_intent VARCHAR;" in schema_migrations.__doc__


def test_pack_and_unit_purchases_keep_the_payment_intent_that_a_refund_will_name(client, db_session, stripe_items):
    signup(client)
    claire = user_id_of(db_session, "claire.achat@agence-test.fr")
    assert signed(client, pack_event(claire)).json()["result"] == "credited"
    stripe_items["cs_live_unit_1"] = [item(3)]
    assert signed(client, unit_event(3)).json()["result"] == "credited"

    rows = {row.stripe_session_id: row.stripe_payment_intent for row in db_session.query(models.Purchase).all()}
    assert rows == {"cs_live_pack_1": "pi_live_pack_1", "cs_live_unit_1": "pi_live_unit_1"}


def test_an_expanded_payment_intent_is_read_by_its_id():
    assert billing.payment_intent_id({"payment_intent": {"id": "pi_x", "object": "payment_intent"}}) == "pi_x"
    assert billing.payment_intent_id({"payment_intent": None}) is None
    assert billing.payment_intent_id({}) is None


def test_the_switch_is_off_unless_set(monkeypatch):
    import config
    assert config.invoices_enabled() is False
    for value in ("1", "true", "YES", " on "):
        monkeypatch.setenv("INVOICES_ENABLED", value)
        assert config.invoices_enabled() is True
    for value in ("0", "false", "", "off", "maybe"):
        monkeypatch.setenv("INVOICES_ENABLED", value)
        assert config.invoices_enabled() is False


# --- Q3: what an invoice says, its number, its PDF ----------------------------------

import re  # noqa: E402
from datetime import date, datetime, timedelta, timezone  # noqa: E402

import fitz  # noqa: E402

import config  # noqa: E402
import invoicing  # noqa: E402

NB = " "
YEAR = datetime.now(invoicing.PARIS).year


def plain(text: str) -> str:
    """PDF or e-mail text with every kind of space as one plain space."""
    return " ".join(text.replace(NB, " ").split())


def pdf_text(data: bytes) -> str:
    with fitz.open(stream=data, filetype="pdf") as document:
        return plain(" ".join(page.get_text() for page in document))


def purchase_row(pack, credits=None, paid_at=datetime(2026, 10, 8, 16, 10, tzinfo=timezone.utc)):
    return models.Purchase(pack=pack, credits=credits if credits is not None else pack, paid_at=paid_at,
                           expires_at=billing.add_months(paid_at, 12))


@pytest.mark.parametrize("pack, credits, ht, vat, ttc", [
    (0, 1, 150, 30, 180), (0, 37, 5_550, 1_110, 6_660), (0, 99, 14_850, 2_970, 17_820),
    (100, 100, 9_900, 1_980, 11_880), (1000, 1000, 69_000, 13_800, 82_800),
    (3000, 3000, 189_000, 37_800, 226_800), (5000, 5000, 295_000, 59_000, 354_000),
])
def test_the_amounts_are_alexs_table(pack, credits, ht, vat, ttc):
    """« Amounts to check »: unit × n = n × 1,50 / 0,30 / 1,80 €; Pack 100 = 99,00 /
    19,80 / 118,80 €; 1000 = 690 / 138 / 828 €; 3000 = 1 890 / 378 / 2 268 €;
    5000 = 2 950 / 590 / 3 540 €."""
    line = invoicing.invoice_line(purchase_row(pack, credits))
    assert (line["total_ht_cents"], line["total_vat_cents"], line["total_ttc_cents"]) == (ht, vat, ttc)
    assert line["line_vat_rate_percent"] == 20 and line["currency"] == "EUR"
    if pack:
        assert (line["line_quantity"], line["line_unit_price_ht_cents"]) == (1, ht)
    else:
        assert (line["line_quantity"], line["line_unit_price_ht_cents"]) == (credits, 150)


def test_the_lines_say_what_was_bought_and_until_when():
    pack = invoicing.invoice_line(purchase_row(100))["line_description"]
    assert plain(pack) == ("Pack 100 — 100 documents (passeports ou CNI françaises), crédits valables 12 mois, "
                           "jusqu’au 08/10/2027")                       # Alex's example, word for word
    assert plain(invoicing.invoice_line(purchase_row(1000))["line_description"]).startswith(
        "Pack 1 000 — 1 000 documents (passeports ou CNI françaises)")
    unit = invoicing.invoice_line(purchase_row(0, 3))["line_description"]
    assert plain(unit) == ("Document à l’unité (passeport ou CNI française), crédit valable 12 mois, "
                           "jusqu’au 08/10/2027")
    # Bought at 23:30 in Paris on 31/12: the validity runs from that Paris day.
    late = datetime(2026, 12, 31, 22, 30, tzinfo=timezone.utc)
    assert invoicing.invoice_line(purchase_row(100, paid_at=late))["line_description"].endswith("31/12/2027")


def test_french_formats():
    assert invoicing.euros(123_456) == f"1{NB}234,56{NB}€"
    assert invoicing.euros(9_900) == f"99,00{NB}€" and invoicing.euros(5) == f"0,05{NB}€"
    assert invoicing.euros(-11_880) == f"-118,80{NB}€"
    assert invoicing.euros(354_000) == f"3{NB}540,00{NB}€"
    assert invoicing.date_fr(date(2026, 1, 5)) == "05/01/2026"
    assert invoicing.count_fr(5000) == f"5{NB}000" and invoicing.siren_fr("107858557") == f"107{NB}858{NB}557"
    assert [invoicing.vat_cents(v) for v in (1, 2, 3, 150, 5_550)] == [0, 0, 1, 30, 1_110]


@pytest.mark.parametrize("typed, code", [
    ("France", "FR"), ("FRANCE", "FR"), (" france ", "FR"), ("Fr", "FR"), ("FR", "FR"), ("République française", "FR"),
    ("France métropolitaine", "FR"), ("Belgique", "Belgique"), ("Monaco", "Monaco"), ("Guadeloupe", "Guadeloupe"),
    ("BE", "BE"), ("", None), (None, None),
])
def test_the_country_of_the_billing_address(typed, code):
    assert invoicing.country_code(typed) == code


ACCOUNT = {"first_name": "Claire", "last_name": "Achat", "email": "claire.achat@agence-test.fr",
           "company": "Agence Test Voyages", "siret": SIRET, "vat_number": "FR12345678901",
           "billing_street": "1 rue de l'Essai", "billing_postal_code": "75001", "billing_city": "Paris",
           "billing_country": "France"}
STRIPE_DETAILS = {"email": "marc@agence-unite.fr", "business_name": "Agence Unité SAS", "individual_name": "Marc Unité",
                  "name": "Marc Unité", "address": {"line1": "5 avenue du Paiement", "line2": "Bâtiment B",
                                                    "postal_code": "69002", "city": "Lyon", "country": "FR"},
                  "tax_ids": [{"type": "eu_vat", "value": "FR40303265045"}]}


def test_the_client_is_the_accounts_billing_identity_first():
    client = invoicing.client_block(ACCOUNT, {"customer_details": STRIPE_DETAILS})
    assert client == {
        "client_name": "Agence Test Voyages", "client_attention": "Claire Achat", "client_street": "1 rue de l'Essai",
        "client_postal_code": "75001", "client_city": "Paris", "client_country": "FR",
        "client_siren": SIRET[:9], "client_vat_number": "FR12345678901", "client_email": "claire.achat@agence-test.fr",
    }


def test_a_unit_buyer_without_an_address_in_the_app_gets_the_one_typed_on_stripe():
    """The account a unit purchase opened: names and company from Stripe, no
    address, no SIRET. The address comes whole from Stripe; the SIREN from the
    French VAT number typed there (FR + key + SIREN, key checked)."""
    opened = {"first_name": "Marc", "last_name": "Unité", "email": "marc@agence-unite.fr", "company": "Agence Unité SAS"}
    client = invoicing.client_block(opened, {"customer_details": STRIPE_DETAILS})
    assert client == {
        "client_name": "Agence Unité SAS", "client_attention": "Marc Unité",
        "client_street": "5 avenue du Paiement, Bâtiment B", "client_postal_code": "69002", "client_city": "Lyon",
        "client_country": "FR", "client_siren": "303265045", "client_vat_number": "FR40303265045",
        "client_email": "marc@agence-unite.fr",
    }
    # Half an address in the app is not mixed with Stripe's.
    half = dict(opened, billing_street="12 rue Incomplète")
    assert invoicing.client_block(half, {"customer_details": STRIPE_DETAILS})["client_street"] == "5 avenue du Paiement, Bâtiment B"


def test_the_siren_is_only_printed_when_it_is_known_for_sure():
    no_siret = dict(ACCOUNT, siret=None, vat_number=None)
    assert invoicing.client_block(no_siret, {})["client_siren"] is None
    wrong_key = dict(ACCOUNT, siret=None, vat_number="FR41303265045")       # key 41 ≠ 40
    assert invoicing.client_block(wrong_key, {})["client_siren"] is None
    foreign = dict(ACCOUNT, siret=None, vat_number="BE0123456789")
    assert invoicing.client_block(foreign, {})["client_siren"] is None


def test_without_a_company_the_person_is_the_client():
    person = {"first_name": "Marc", "last_name": "Seul", "email": "marc@seul.fr"}
    client = invoicing.client_block(person, {"customer_details": {"address": STRIPE_DETAILS["address"]}})
    assert (client["client_name"], client["client_attention"]) == ("Marc Seul", None)


def _session(total=11_880, country=None, currency="eur"):
    details = {"address": {"country": country}} if country else {}
    return {"amount_total": total, "currency": currency, "customer_details": details}


def test_only_a_french_billing_address_paying_the_app_price_is_invoiced_automatically():
    amounts = invoicing.invoice_line(purchase_row(100))
    france = invoicing.client_block(ACCOUNT, {})
    assert invoicing.refusal(france, _session(), amounts) is None
    assert invoicing.refusal(france, _session(country="FR"), amounts) is None

    belgium = invoicing.client_block(dict(ACCOUNT, billing_country="Belgique"), {})
    assert invoicing.refusal(belgium, _session(), amounts).startswith("pays de facturation hors de France (Belgique)")
    typed_abroad = invoicing.refusal(france, _session(country="BE"), amounts)
    assert typed_abroad.startswith("pays de l'adresse saisie sur Stripe : BE")
    assert invoicing.refusal(invoicing.client_block(dict(ACCOUNT, billing_country=""), {}), _session(), amounts).startswith(
        "pays de facturation hors de France (non renseigné)")
    assert invoicing.refusal(france, _session(currency="usd"), amounts) == "paiement dans une autre devise que l'euro"
    mismatch = invoicing.refusal(france, _session(total=9_900), amounts)
    assert plain(mismatch) == ("le montant payé (99,00 €) n'est pas le total TTC calculé avec les prix de "
                               "l'application (118,80 €)")


# Issuing, through the database.

def _credited_pack(client, db, pack=100, session_id="cs_live_pack_1", livemode=True, **changes):
    signup(client, pack=pack, email=changes.pop("email", "claire.achat@agence-test.fr"))
    user_id = user_id_of(db, "claire.achat@agence-test.fr")
    session = pack_event(user_id, pack=pack, session_id=session_id, livemode=livemode,
                         payment_intent=f"pi_{session_id}", **changes)["data"]["object"]
    outcome = billing.credit_checkout_session(db, session)
    assert outcome.status == "credited"
    return outcome.purchase_id, session


def test_nothing_is_issued_while_the_switch_is_off(client, db_session):
    purchase_id, session = _credited_pack(client, db_session)
    assert invoicing.issue_invoice(db_session, purchase_id, session).status == "disabled"
    assert db_session.query(models.Invoice).count() == 0
    assert db_session.query(models.InvoiceCounter).count() == 0


def test_an_issued_invoice_stores_every_mention_and_its_pdf(client, db_session, monkeypatch):
    monkeypatch.setenv("INVOICES_ENABLED", "1")
    purchase_id, session = _credited_pack(client, db_session, pack=1000, total=82_800)
    outcome = invoicing.issue_invoice(db_session, purchase_id, session)
    assert outcome.status == "issued"

    row = db_session.query(models.Invoice).one()
    purchase = db_session.get(models.Purchase, purchase_id)
    paid_on = invoicing.to_paris(purchase.paid_at).date()
    assert (row.kind, row.number, row.series, row.sequence, row.livemode) == (
        "invoice", f"F-{YEAR}-00001", f"F-{YEAR}", 1, True)
    assert row.issue_date == paid_on == row.service_date == row.payment_date
    assert (row.purchase_id, row.user_id) == (purchase_id, purchase.user_id)
    assert {k: getattr(row, k) for k in invoicing.SELLER} == invoicing.SELLER
    assert (row.client_name, row.client_attention, row.client_siren, row.client_vat_number, row.client_country) == (
        "Agence Test Voyages", "Claire Achat", SIRET[:9], "FR12345678901", "FR")
    assert (row.line_quantity, row.line_unit_price_ht_cents, row.line_vat_rate_percent, row.line_total_ht_cents) == (
        1, 69_000, 20, 69_000)
    assert (row.total_ht_cents, row.total_vat_cents, row.total_ttc_cents, row.currency) == (69_000, 13_800, 82_800, "EUR")
    assert (row.nature, row.payment_method) == ("Prestation de services", "carte bancaire (Stripe)")
    assert (row.stripe_session_id, row.stripe_payment_intent) == ("cs_live_pack_1", "pi_cs_live_pack_1")
    assert row.pdf.startswith(b"%PDF") and invoicing.filename(row) == f"Facture-F-{YEAR}-00001.pdf"
    assert db_session.get(models.InvoiceCounter, f"F-{YEAR}").last_number == 1


def test_the_pdf_carries_every_mention_alex_listed(client, db_session, monkeypatch):
    monkeypatch.setenv("INVOICES_ENABLED", "1")
    purchase_id, session = _credited_pack(client, db_session, pack=100)
    row = invoicing.issue_invoice(db_session, purchase_id, session).invoice
    text = pdf_text(row.pdf)
    day = invoicing.date_fr(row.issue_date)
    until = invoicing.date_fr(invoicing.to_paris(db_session.get(models.Purchase, purchase_id).expires_at).date())
    for mention in (
        # Seller (Alex's line, in the footer) and its block at the top.
        "ScanID, SASU au capital de 1 000 € — 169 avenue de Choisy, 75013 Paris — RCS Paris 107 858 557 — "
        "N° de TVA FR76107858557 — contact@scanid.fr",
        "SASU au capital de 1 000 €", "169 avenue de Choisy", "75013 Paris", "RCS Paris 107 858 557",
        "N° de TVA : FR76107858557",
        # The document.
        "FACTURE", f"N° F-{YEAR}-00001", f"Date de facture : {day}", f"Date de la prestation : {day}",
        # Client.
        "CLIENT", "Agence Test Voyages", "À l’attention de Claire Achat", "1 rue de l'Essai", "75001 Paris", "France",
        f"SIREN : {SIRET[0:3]} {SIRET[3:6]} {SIRET[6:9]}", "N° de TVA : FR12345678901",
        # The line and the totals.
        "Désignation", "Quantité", "Prix unitaire HT", "TVA", "Total HT",
        f"Pack 100 — 100 documents (passeports ou CNI françaises), crédits valables 12 mois, jusqu’au {until}",
        "99,00 €", "20 %", "TVA 20 %", "19,80 €", "Total TTC", "118,80 €",
        # Nature and payment.
        "Nature de l’opération : Prestation de services",
        f"Facture acquittée le {day} par carte bancaire (Stripe)",
        "Escompte pour paiement anticipé : néant",
        "Pénalités de retard : taux de la BCE majoré de 10 points ; indemnité forfaitaire pour frais de recouvrement : "
        "40 € (art. L441-10 du Code de commerce)",
    ):
        assert mention in text, mention
    assert "SPÉCIMEN" not in text

    with fitz.open(stream=row.pdf, filetype="pdf") as document:
        assert document.page_count == 1
        assert document.metadata["title"] == f"Facture F-{YEAR}-00001" and document.metadata["author"] == "ScanID"
        fonts = document[0].get_fonts(full=True)
        assert fonts and all(font[1] != "n/a" for font in fonts)       # every font embedded


def test_numbers_follow_each_other_without_a_gap_even_after_a_failure(client, db_session, monkeypatch, stripe_items):
    monkeypatch.setenv("INVOICES_ENABLED", "1")
    first_id, first_session = _credited_pack(client, db_session, pack=100, session_id="cs_live_a")
    assert invoicing.issue_invoice(db_session, first_id, first_session).invoice.number == f"F-{YEAR}-00001"

    stripe_items["cs_live_b"] = [item(2)]
    second = unit_event(2, session_id="cs_live_b", email="claire.achat@agence-test.fr")["data"]["object"]
    second_id = billing.credit_checkout_session(db_session, second).purchase_id

    real_render = invoicing.render_pdf
    monkeypatch.setattr(invoicing, "render_pdf", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("PDF")))
    with pytest.raises(RuntimeError):
        invoicing.issue_invoice(db_session, second_id, second)
    assert db_session.query(models.Invoice).count() == 1                         # nothing stored…
    assert db_session.get(models.InvoiceCounter, f"F-{YEAR}").last_number == 1   # …and the number given back

    monkeypatch.setattr(invoicing, "render_pdf", real_render)
    assert invoicing.issue_invoice(db_session, second_id, second).invoice.number == f"F-{YEAR}-00002"
    numbers = [row.number for row in db_session.query(models.Invoice).order_by(models.Invoice.sequence)]
    assert numbers == [f"F-{YEAR}-00001", f"F-{YEAR}-00002"]


def test_each_year_and_each_mode_has_its_own_series(client, db_session, monkeypatch):
    monkeypatch.setenv("INVOICES_ENABLED", "1")
    db_session.add(models.InvoiceCounter(series=f"F-{YEAR - 1}", last_number=41))   # last year's series
    db_session.commit()
    assert invoicing.series_for("invoice", 2027, True) == "F-2027"
    assert invoicing.series_for("credit_note", 2027, True) == "AV-2027"
    assert invoicing.series_for("invoice", 2027, False) == "TEST-F-2027"

    purchase_id, session = _credited_pack(client, db_session, livemode=False)
    row = invoicing.issue_invoice(db_session, purchase_id, session).invoice
    assert (row.number, row.livemode) == (f"TEST-F-{YEAR}-00001", False)     # Stripe test mode: no real number
    assert db_session.get(models.InvoiceCounter, f"F-{YEAR}") is None
    assert "SPÉCIMEN — paiement Stripe en mode test, sans valeur comptable" in pdf_text(row.pdf)
    assert db_session.get(models.InvoiceCounter, f"F-{YEAR - 1}").last_number == 41


def test_a_missing_livemode_is_never_taken_for_a_live_payment(client, db_session, monkeypatch):
    monkeypatch.setenv("INVOICES_ENABLED", "1")
    purchase_id, session = _credited_pack(client, db_session)
    session.pop("livemode")
    assert invoicing.issue_invoice(db_session, purchase_id, session).invoice.number.startswith("TEST-F-")


def test_a_refused_invoice_uses_no_number(client, db_session, monkeypatch):
    monkeypatch.setenv("INVOICES_ENABLED", "1")
    purchase_id, session = _credited_pack(client, db_session, total=9_900)       # HT paid, no VAT
    outcome = invoicing.issue_invoice(db_session, purchase_id, session)
    assert outcome.status == "refused" and "118,80" in outcome.reason
    assert db_session.query(models.Invoice).count() == 0 and db_session.query(models.InvoiceCounter).count() == 0


# --- Q4: the webhook issues the invoice and the purchase e-mail carries it ----------

def _customer_emails():
    return [e for e in mailer.OUTBOX if e.to != "contact@scanid.fr"]


def _alex_emails():
    return [e for e in mailer.OUTBOX if e.to == "contact@scanid.fr"]


def test_a_pack_paid_gets_its_invoice_attached_to_the_purchase_e_mail(client, db_session, monkeypatch):
    monkeypatch.setenv("INVOICES_ENABLED", "1")
    signup(client, pack=1000)
    claire = user_id_of(db_session, "claire.achat@agence-test.fr")
    response = signed(client, pack_event(claire, pack=1000))
    assert response.status_code == 200 and response.json() == {"received": True, "result": "credited"}

    row = db_session.query(models.Invoice).one()
    assert row.number == f"F-{YEAR}-00001" and row.total_ttc_cents == 82_800
    [mail] = mailer.OUTBOX
    assert (mail.to, mail.kind, mail.subject) == ("claire.achat@agence-test.fr", "purchase_confirmation",
                                                  "Vos 1 000 documents ScanID sont disponibles")
    assert f"Votre facture F-{YEAR}-00001 est jointe à cet e-mail. Le détail de vos achats est dans « Mon compte » → « Mes achats »." in mail.body
    assert mail.attachments == [(f"Facture-F-{YEAR}-00001.pdf", row.pdf, "application/pdf")]

    for _ in range(2):                                  # Stripe delivers again: nothing more
        assert signed(client, pack_event(claire, pack=1000)).json()["result"] == "duplicate"
    assert db_session.query(models.Invoice).count() == 1 and len(mailer.OUTBOX) == 1


def test_unit_purchases_get_theirs_too_also_when_the_purchase_opens_the_account(client, db_session, monkeypatch, stripe_items):
    monkeypatch.setenv("INVOICES_ENABLED", "1")
    signup(client)                                       # an open account: credited, invoiced
    stripe_items["cs_live_unit_1"] = [item(3)]
    assert signed(client, unit_event(3, email="Claire.Achat@Agence-Test.fr")).json()["result"] == "credited"
    stripe_items["cs_live_unit_2"] = [item(1)]           # a new address: the purchase opens the account
    opened = unit_event(1, session_id="cs_live_unit_2", email="marc@agence-unite.fr", payment_intent="pi_live_unit_2",
                        details={k: v for k, v in STRIPE_DETAILS.items() if k != "email"})
    assert signed(client, opened).json()["result"] == "credited"

    first, second = db_session.query(models.Invoice).order_by(models.Invoice.sequence).all()
    assert (first.number, first.line_quantity, first.total_ttc_cents, first.client_name) == (
        f"F-{YEAR}-00001", 3, 540, "Agence Test Voyages")
    assert (second.number, second.line_quantity, second.total_ttc_cents) == (f"F-{YEAR}-00002", 1, 180)
    assert (second.client_name, second.client_street, second.client_city, second.client_siren) == (
        "Agence Unité SAS", "5 avenue du Paiement, Bâtiment B", "Lyon", "303265045")

    confirmation, welcome = mailer.OUTBOX
    assert confirmation.kind == "purchase_confirmation" and f"Votre facture F-{YEAR}-00001 est jointe" in confirmation.body
    assert confirmation.attachments == [(f"Facture-F-{YEAR}-00001.pdf", first.pdf, "application/pdf")]
    assert (welcome.kind, welcome.to) == ("purchase_welcome", "marc@agence-unite.fr")
    assert f"Votre facture F-{YEAR}-00002 est jointe à cet e-mail." in welcome.body
    assert welcome.attachments == [(f"Facture-F-{YEAR}-00002.pdf", second.pdf, "application/pdf")]


def test_with_the_switch_off_the_purchase_is_exactly_as_before(client, db_session):
    signup(client)
    claire = user_id_of(db_session, "claire.achat@agence-test.fr")
    assert signed(client, pack_event(claire)).json()["result"] == "credited"
    [mail] = mailer.OUTBOX
    assert mail.attachments == [] and "facture" not in mail.body.lower()
    assert db_session.query(models.Invoice).count() == 0 and db_session.query(models.InvoiceCounter).count() == 0


def test_a_billing_address_abroad_is_not_invoiced_and_alex_is_told(client, db_session, monkeypatch):
    monkeypatch.setenv("INVOICES_ENABLED", "1")
    signup(client, billing_country="Belgique")
    claire = user_id_of(db_session, "claire.achat@agence-test.fr")
    assert signed(client, pack_event(claire)).json()["result"] == "credited"     # the credits, as always

    assert db_session.query(models.Invoice).count() == 0 and db_session.query(models.InvoiceCounter).count() == 0
    [mail] = _customer_emails()
    assert mail.attachments == [] and "facture" not in mail.body.lower()
    [notice] = _alex_emails()
    assert (notice.kind, notice.subject) == ("invoice_not_issued", "Facture non émise automatiquement — à établir à la main")
    body = plain(notice.body)
    assert "Raison : pays de facturation hors de France (Belgique) : autres règles de TVA, facture à établir à la main" in body
    assert "Achat : Pack 100" in body and "Montant payé (TTC) : 118,80 €" in body
    assert "Client : Agence Test Voyages — Claire Achat — claire.achat@agence-test.fr" in body
    assert "Session Stripe : cs_live_pack_1" in body and "Paiement Stripe : pi_live_pack_1" in body


def test_a_payment_that_is_not_the_app_price_is_not_invoiced_and_alex_is_told(client, db_session, monkeypatch):
    monkeypatch.setenv("INVOICES_ENABLED", "1")
    signup(client)
    claire = user_id_of(db_session, "claire.achat@agence-test.fr")
    assert signed(client, pack_event(claire, total=9_900)).json()["result"] == "credited"   # paid HT, without VAT
    assert db_session.query(models.Invoice).count() == 0
    [notice] = _alex_emails()
    assert "le montant payé (99,00 €) n'est pas le total TTC calculé avec les prix de l'application (118,80 €)" in plain(notice.body)


def test_an_unexpected_failure_keeps_the_credits_uses_no_number_and_alex_is_told(client, db_session, monkeypatch):
    monkeypatch.setenv("INVOICES_ENABLED", "1")
    monkeypatch.setattr(invoicing, "render_pdf", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("PDF")))
    signup(client)
    claire = user_id_of(db_session, "claire.achat@agence-test.fr")
    response = signed(client, pack_event(claire))
    assert response.status_code == 200 and response.json()["result"] == "credited"
    db_session.expire_all()
    assert db_session.get(models.User, claire).page_credits == 100
    assert db_session.query(models.Invoice).count() == 0 and db_session.query(models.InvoiceCounter).count() == 0
    assert _customer_emails()[0].attachments == []
    [notice] = _alex_emails()
    assert "erreur inattendue à l'émission (RuntimeError) ; aucun numéro n'a été utilisé" in notice.body


def test_a_stripe_test_mode_payment_never_uses_a_real_number(client, db_session, monkeypatch):
    monkeypatch.setenv("INVOICES_ENABLED", "1")
    signup(client)
    claire = user_id_of(db_session, "claire.achat@agence-test.fr")
    assert signed(client, pack_event(claire, livemode=False, session_id="cs_test_pack_1")).json()["result"] == "credited"
    row = db_session.query(models.Invoice).one()
    assert row.number == f"TEST-F-{YEAR}-00001" and not row.livemode
    assert mailer.OUTBOX[0].attachments[0][0] == f"Facture-TEST-F-{YEAR}-00001.pdf"
    assert db_session.get(models.InvoiceCounter, f"F-{YEAR}") is None


def test_the_attachment_travels_in_the_real_message(monkeypatch, tmp_path):
    """MAIL_OUTBOX_DIR writes the message SMTP would send: the text, then the PDF."""
    monkeypatch.setenv("MAIL_OUTBOX_DIR", str(tmp_path))
    pdf = b"%PDF-1.7 test"
    assert mailer.send("claire@agence-test.fr", "Sujet", "Texte", "purchase_confirmation",
                       attachments=[("Facture-F-2026-00001.pdf", pdf, "application/pdf")])
    import email
    [path] = list(tmp_path.iterdir())
    message = email.message_from_bytes(path.read_bytes())
    parts = [part for part in message.walk() if not part.is_multipart()]
    assert [p.get_content_type() for p in parts] == ["text/plain", "application/pdf"]
    assert parts[1].get_filename() == "Facture-F-2026-00001.pdf" and parts[1].get_payload(decode=True) == pdf


# --- Q5: « Mes achats », the PDF, the admin list and the accountant's CSV ------------

from tests.helpers import auth_headers, make_user  # noqa: E402

CLAIRE = "claire.achat@agence-test.fr"


def _invoiced_pack(client, db, monkeypatch, pack=100):
    monkeypatch.setenv("INVOICES_ENABLED", "1")
    signup(client, pack=pack)
    claire = user_id_of(db, CLAIRE)
    assert signed(client, pack_event(claire, pack=pack)).json()["result"] == "credited"
    return claire, db.query(models.Invoice).one()


def _copy(db, row, **changes):
    """Another stored document shaped like `row` (a credit note, another month…)."""
    fields = invoicing.document_fields(row)
    fields.pop("id")
    fields.update(changes)
    copy = models.Invoice(**fields, pdf=row.pdf)
    db.add(copy)
    db.commit()
    return copy


def test_mes_achats_links_each_purchase_to_its_invoice(client, db_session, monkeypatch, stripe_items):
    signup(client)
    claire = user_id_of(db_session, CLAIRE)
    assert signed(client, pack_event(claire)).json()["result"] == "credited"          # before invoices
    monkeypatch.setenv("INVOICES_ENABLED", "1")
    stripe_items["cs_live_unit_1"] = [item(2)]
    assert signed(client, unit_event(2, email=CLAIRE)).json()["result"] == "credited"   # after

    purchases = client.get("/users/me/purchases", headers=auth_headers(CLAIRE)).json()
    invoice = db_session.query(models.Invoice).one()
    assert [(p["pack"], p["documents"]) for p in purchases] == [
        (0, [{"id": invoice.id, "kind": "invoice", "number": f"F-{YEAR}-00001"}]),
        (100, []),
    ]


def test_the_pdf_is_downloaded_exactly_as_it_was_issued(client, db_session, monkeypatch):
    claire, row = _invoiced_pack(client, db_session, monkeypatch)
    issued = bytes(row.pdf)
    # The client changes the billing identity afterwards: the invoice does not move.
    assert client.put("/users/me", json={"company": "Nouvelle Raison Sociale"}, headers=auth_headers(CLAIRE)).status_code == 200

    response = client.get(f"/invoices/{row.id}/pdf", headers=auth_headers(CLAIRE))
    assert response.status_code == 200
    assert response.content == issued
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"] == f"attachment; filename=Facture-F-{YEAR}-00001.pdf"
    db_session.expire_all()
    assert db_session.get(models.Invoice, row.id).client_name == "Agence Test Voyages"
    assert "Agence Test Voyages" in pdf_text(response.content) and "Nouvelle Raison" not in pdf_text(response.content)


def test_only_its_client_or_an_admin_gets_an_invoice(client, db_session, monkeypatch):
    _, row = _invoiced_pack(client, db_session, monkeypatch)
    make_user(db_session, "bob")
    make_user(db_session, "boss", role="admin")
    url = f"/invoices/{row.id}/pdf"
    assert client.get(url, headers=auth_headers("bob")).status_code == 404
    assert client.get(url, headers=auth_headers("bob")).json() == {"detail": "Facture introuvable."}
    assert client.get(url, headers=auth_headers("boss")).status_code == 200
    assert client.get("/invoices/inconnue/pdf", headers=auth_headers(CLAIRE)).status_code == 404
    assert client.get(url).status_code == 401


def test_the_admin_list_shows_every_document_newest_first(client, db_session, monkeypatch):
    _, row = _invoiced_pack(client, db_session, monkeypatch)
    later = _copy(db_session, row, kind="credit_note", number=f"AV-{YEAR}-00001", series=f"AV-{YEAR}", sequence=1,
                  issued_at=row.issued_at + timedelta(minutes=5), credited_invoice_id=row.id,
                  credited_invoice_number=row.number)
    make_user(db_session, "boss", role="admin")
    listed = client.get("/admin/invoices", headers=auth_headers("boss")).json()
    assert [d["number"] for d in listed] == [later.number, row.number]
    assert set(listed[1]) == {"id", "kind", "number", "issue_date", "livemode", "client_name", "client_siren",
                              "client_email", "total_ht_cents", "total_vat_cents", "total_ttc_cents",
                              "stripe_payment_intent", "stripe_session_id", "credited_invoice_number", "purchase_id",
                              "user_id"}                                  # never the PDF
    assert listed[1]["client_siren"] == SIRET[:9] and listed[1]["total_ttc_cents"] == 11_880
    assert listed[0]["credited_invoice_number"] == row.number
    assert client.get("/admin/invoices", headers=auth_headers(CLAIRE)).status_code == 403
    month = row.issue_date.strftime("%Y-%m")
    assert len(client.get(f"/admin/invoices?month={month}", headers=auth_headers("boss")).json()) == 2
    assert client.get("/admin/invoices?month=1999-01", headers=auth_headers("boss")).json() == []


def test_the_monthly_csv_for_the_accountant(client, db_session, monkeypatch):
    _, row = _invoiced_pack(client, db_session, monkeypatch, pack=1000)
    month = row.issue_date.strftime("%Y-%m")
    previous = (row.issue_date.replace(day=1) - timedelta(days=1))
    _copy(db_session, row, kind="credit_note", number=f"AV-{YEAR}-00001", series=f"AV-{YEAR}", sequence=1,
          issued_at=row.issued_at + timedelta(minutes=5), credited_invoice_id=row.id, credited_invoice_number=row.number,
          total_ht_cents=10_000, total_vat_cents=2_000, total_ttc_cents=12_000)
    _copy(db_session, row, number="F-0000-00001", purchase_id="older", issue_date=previous)       # another month
    _copy(db_session, row, number=f"TEST-F-{YEAR}-00001", purchase_id="test", livemode=False)       # Stripe test mode
    _copy(db_session, row, number=f"F-{YEAR}-00099", purchase_id="formula", client_name="=HYPERLINK(1)",
          issued_at=row.issued_at + timedelta(minutes=9), stripe_payment_intent=None)
    make_user(db_session, "boss", role="admin")

    response = client.get(f"/admin/invoices/export?month={month}", headers=auth_headers("boss"))
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert response.headers["content-disposition"] == f"attachment; filename=factures_{month}.csv"
    assert response.content.startswith(b"\xef\xbb\xbf")
    lines = response.content[3:].decode("utf-8").split("\r\n")
    day = invoicing.date_fr(row.issue_date)
    assert lines == [
        "Type;Numéro;Date;Client;SIREN;Total HT;TVA;Total TTC;Référence Stripe;Facture d'origine",
        f"Facture;F-{YEAR}-00001;{day};Agence Test Voyages;{SIRET[:9]};690,00;138,00;828,00;pi_live_pack_1;",
        f"Avoir;AV-{YEAR}-00001;{day};Agence Test Voyages;{SIRET[:9]};-100,00;-20,00;-120,00;pi_live_pack_1;F-{YEAR}-00001",
        f"Facture;F-{YEAR}-00099;{day};'=HYPERLINK(1);{SIRET[:9]};690,00;138,00;828,00;cs_live_pack_1;",
        "",
    ]
    assert client.get("/admin/invoices/export?month=2026-13", headers=auth_headers("boss")).status_code == 400
    assert client.get("/admin/invoices/export", headers=auth_headers("boss")).json() == {"detail": "Choisissez un mois (AAAA-MM)."}
    assert client.get(f"/admin/invoices/export?month={month}", headers=auth_headers(CLAIRE)).status_code == 403


def test_deleting_the_account_keeps_its_invoices(client, db_session, monkeypatch):
    claire, row = _invoiced_pack(client, db_session, monkeypatch)
    make_user(db_session, "boss", role="admin")
    assert client.delete(f"/admin/users/{claire}", headers=auth_headers("boss")).status_code == 200
    db_session.expire_all()
    kept = db_session.get(models.Invoice, row.id)
    assert kept is not None and kept.client_name == "Agence Test Voyages" and kept.pdf == row.pdf
    assert [d["number"] for d in client.get("/admin/invoices", headers=auth_headers("boss")).json()] == [row.number]
    assert client.get(f"/invoices/{row.id}/pdf", headers=auth_headers("boss")).content == row.pdf


def test_no_route_changes_or_deletes_an_invoice():
    """Kept as issued: the API only reads invoices."""
    from main import app
    for route in app.routes:
        if "invoice" in getattr(route, "path", ""):
            assert getattr(route, "methods", set()) <= {"GET", "HEAD"}, route.path


# --- Q7a: a refund gets its credit note (« avoir ») ----------------------------------

def refund_event(cumulative, payment_intent="pi_live_pack_1", charge_id="ch_live_1", amount=11_880, livemode=True,
                 created=None, event_id=None):
    """charge.refunded: one event per refund; `amount_refunded` is the running total."""
    return {"id": event_id or f"evt_refund_{cumulative}", "type": "charge.refunded", "livemode": livemode,
            "created": int(time.time()) if created is None else created,
            "data": {"object": {"id": charge_id, "object": "charge", "payment_intent": payment_intent,
                                "amount": amount, "amount_captured": amount, "amount_refunded": cumulative,
                                "refunded": cumulative == amount, "currency": "eur", "livemode": livemode}}}


def _notes(db):
    return db.query(models.Invoice).filter(models.Invoice.kind == "credit_note").order_by(models.Invoice.sequence).all()


def test_a_full_refund_gets_one_credit_note_for_the_whole_invoice(client, db_session, monkeypatch):
    _, invoice = _invoiced_pack(client, db_session, monkeypatch)
    mailer.OUTBOX.clear()
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    response = signed(client, refund_event(11_880, created=int(yesterday.timestamp())))
    assert response.status_code == 200 and response.json() == {"received": True, "result": "issued"}

    [note] = _notes(db_session)
    assert (note.number, note.series, note.livemode) == (f"AV-{YEAR}-00001", f"AV-{YEAR}", True)
    assert (note.credited_invoice_id, note.credited_invoice_number) == (invoice.id, invoice.number)
    assert (note.purchase_id, note.user_id) == (invoice.purchase_id, invoice.user_id)
    assert (note.line_description, note.line_quantity, note.line_unit_price_ht_cents) == (
        invoice.line_description, 1, 9_900)
    assert (note.total_ht_cents, note.total_vat_cents, note.total_ttc_cents) == (9_900, 1_980, 11_880)
    assert note.payment_date == invoicing.to_paris(yesterday).date()            # the refund's date
    assert note.issue_date == datetime.now(invoicing.PARIS).date()
    assert (note.stripe_charge_id, note.refunded_cumulative_cents, note.stripe_payment_intent) == (
        "ch_live_1", 11_880, "pi_live_pack_1")
    for name in list(invoicing.SELLER) + ["client_name", "client_attention", "client_siren", "client_vat_number",
                                          "client_street", "client_city", "client_country", "nature", "payment_method"]:
        assert getattr(note, name) == getattr(invoice, name), name              # the same blocks

    text = pdf_text(note.pdf)
    for mention in ("AVOIR", f"N° AV-{YEAR}-00001", f"Date de l’avoir : {invoicing.date_fr(note.issue_date)}",
                    f"Avoir sur la facture {invoice.number}", "Agence Test Voyages", "À l’attention de Claire Achat",
                    f"SIREN : {SIRET[0:3]} {SIRET[3:6]} {SIRET[6:9]}", "Total HT", "99,00 €", "19,80 €", "118,80 €",
                    "Nature de l’opération : Prestation de services",
                    f"Montant remboursé le {invoicing.date_fr(note.payment_date)} par carte bancaire (Stripe)",
                    "ScanID, SASU au capital de 1 000 € — 169 avenue de Choisy, 75013 Paris — RCS Paris 107 858 557 — "
                    "N° de TVA FR76107858557 — contact@scanid.fr"):
        assert mention in text, mention
    assert "Facture acquittée" not in text and "Pénalités" not in text and "FACTURE" not in text

    [mail] = mailer.OUTBOX
    assert (mail.to, mail.kind, mail.subject) == (CLAIRE, "credit_note", f"Votre avoir AV-{YEAR}-00001 — remboursement ScanID")
    assert (f"voici l'avoir AV-{YEAR}-00001 sur la facture {invoice.number}, d'un montant de 118,80 € TTC. "
            "Il est joint à cet e-mail") in plain(mail.body)
    assert mail.attachments == [(f"Avoir-AV-{YEAR}-00001.pdf", note.pdf, "application/pdf")]

    for _ in range(2):                                   # Stripe delivers again
        assert signed(client, refund_event(11_880)).json()["result"] == "duplicate"
    assert len(_notes(db_session)) == 1 and len(mailer.OUTBOX) == 1
    purchases = client.get("/users/me/purchases", headers=auth_headers(CLAIRE)).json()
    assert purchases[0]["documents"] == [{"id": invoice.id, "kind": "invoice", "number": invoice.number},
                                         {"id": note.id, "kind": "credit_note", "number": note.number}]


def test_partial_refunds_add_up_to_the_invoice_whatever_order_stripe_delivers_them(client, db_session, monkeypatch, stripe_items):
    monkeypatch.setenv("INVOICES_ENABLED", "1")
    signup(client)
    stripe_items["cs_live_unit_1"] = [item(3)]                                   # 4,50 + 0,90 = 5,40 €
    assert signed(client, unit_event(3, email=CLAIRE)).json()["result"] == "credited"
    invoice = db_session.query(models.Invoice).one()
    assert (invoice.total_ht_cents, invoice.total_vat_cents, invoice.total_ttc_cents) == (450, 90, 540)

    partial = dict(payment_intent="pi_live_unit_1", amount=540)
    assert signed(client, refund_event(200, **partial)).json()["result"] == "issued"       # 2,00 €
    assert signed(client, refund_event(540, **partial)).json()["result"] == "issued"       # the rest, 3,40 €
    assert signed(client, refund_event(360, **partial)).json()["result"] == "duplicate"    # late: already covered

    first, second = _notes(db_session)
    assert (first.total_ht_cents, first.total_vat_cents, first.total_ttc_cents) == (167, 33, 200)   # 200 ÷ 1,2 = 166,67
    assert (second.total_ht_cents, second.total_vat_cents, second.total_ttc_cents) == (283, 57, 340)
    assert first.total_ht_cents + second.total_ht_cents == invoice.total_ht_cents
    assert first.total_vat_cents + second.total_vat_cents == invoice.total_vat_cents
    assert plain(first.line_description).startswith("Remboursement partiel — Document à l’unité")
    assert (first.line_quantity, first.line_unit_price_ht_cents, first.line_total_ht_cents) == (1, 167, 167)
    assert [n.number for n in (first, second)] == [f"AV-{YEAR}-00001", f"AV-{YEAR}-00002"]
    assert [n.refunded_cumulative_cents for n in (first, second)] == [200, 540]
    assert "Remboursement partiel" in pdf_text(first.pdf)


def test_the_note_that_completes_a_refund_takes_what_is_left_not_its_own_rounding(client, db_session, monkeypatch, stripe_items):
    """3 cents ÷ 1,2 = 2,5 → 3 HT twice; 534 ÷ 1,2 would give 445 HT, one cent
    more than the invoice has left."""
    monkeypatch.setenv("INVOICES_ENABLED", "1")
    signup(client)
    stripe_items["cs_live_unit_1"] = [item(3)]
    assert signed(client, unit_event(3, email=CLAIRE)).json()["result"] == "credited"
    partial = dict(payment_intent="pi_live_unit_1", amount=540)
    for cumulative in (3, 6, 540):
        assert signed(client, refund_event(cumulative, **partial)).json()["result"] == "issued"
    notes = _notes(db_session)
    assert [(n.total_ht_cents, n.total_vat_cents, n.total_ttc_cents) for n in notes] == [(3, 0, 3), (3, 0, 3), (444, 90, 534)]
    assert sum(n.total_ht_cents for n in notes) == 450 and sum(n.total_vat_cents for n in notes) == 90


def test_a_refund_the_app_cannot_credit_note_is_told_to_alex(client, db_session, monkeypatch):
    signup(client)
    claire = user_id_of(db_session, CLAIRE)
    assert signed(client, pack_event(claire)).json()["result"] == "credited"     # paid before invoices: no invoice
    monkeypatch.setenv("INVOICES_ENABLED", "1")
    mailer.OUTBOX.clear()

    assert signed(client, refund_event(11_880)).json()["result"] == "refused"
    assert signed(client, refund_event(500, payment_intent="pi_inconnu", event_id="evt_x")).json()["result"] == "unmatched"
    assert _notes(db_session) == [] and db_session.query(models.InvoiceCounter).count() == 0
    first, second = mailer.OUTBOX
    assert {m.to for m in mailer.OUTBOX} == {"contact@scanid.fr"}
    assert first.subject == "Remboursement Stripe sans avoir automatique — à traiter à la main"
    assert "Raison : l'achat n'a pas de facture émise par l'application" in first.body
    assert "Paiement Stripe : pi_live_pack_1" in first.body and "Total remboursé sur ce paiement : 118,80" in plain(first.body)
    assert "Raison : aucun achat ScanID ne correspond à ce paiement" in second.body


def test_a_refund_beyond_the_invoice_is_not_credited_automatically(client, db_session, monkeypatch):
    _invoiced_pack(client, db_session, monkeypatch)
    mailer.OUTBOX.clear()
    assert signed(client, refund_event(20_000, amount=20_000)).json()["result"] == "refused"
    assert _notes(db_session) == []
    assert "le total remboursé (200,00 €) dépasse la facture" in plain(mailer.OUTBOX[0].body)


def test_refunds_change_nothing_while_the_switch_is_off(client, db_session):
    assert signed(client, refund_event(11_880)).json() == {"received": True, "result": "disabled"}
    assert mailer.OUTBOX == []


def test_a_test_mode_invoice_gets_a_test_mode_credit_note(client, db_session, monkeypatch):
    monkeypatch.setenv("INVOICES_ENABLED", "1")
    signup(client)
    claire = user_id_of(db_session, CLAIRE)
    assert signed(client, pack_event(claire, livemode=False, session_id="cs_test_1", payment_intent="pi_test_1")).json()["result"] == "credited"
    assert signed(client, refund_event(11_880, payment_intent="pi_test_1", livemode=False)).json()["result"] == "issued"
    [note] = _notes(db_session)
    assert note.number == f"TEST-AV-{YEAR}-00001" and not note.livemode
    assert "SPÉCIMEN — paiement Stripe en mode test" in pdf_text(note.pdf)


def test_a_failing_credit_note_uses_no_number_and_alex_is_told(client, db_session, monkeypatch):
    _invoiced_pack(client, db_session, monkeypatch)
    mailer.OUTBOX.clear()
    monkeypatch.setattr(invoicing, "render_pdf", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("PDF")))
    assert signed(client, refund_event(11_880)).json()["result"] == "refused"
    assert _notes(db_session) == [] and db_session.get(models.InvoiceCounter, f"AV-{YEAR}") is None
    assert "erreur inattendue à l'émission de l'avoir (RuntimeError) ; aucun numéro n'a été utilisé" in mailer.OUTBOX[0].body

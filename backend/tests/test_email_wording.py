"""The wording of every e-mail the application sends (Alex, after go-live,
2026-10-02): the site says « documents », never « scans », and writes
« e-mail » with its hyphen, as on the login page."""
import re
from datetime import datetime, timezone

import pytest

import emails

USER = {"first_name": "Claire", "user_name": "claire@agence-test.fr", "email": "claire@agence-test.fr"}
EXPIRY = datetime(2027, 10, 2, tzinfo=timezone.utc)
SESSION = {"id": "cs_test_1", "customer_details": {"email": "claire@agence-test.fr"},
           "amount_subtotal": 9_900, "amount_total": 11_880, "currency": "eur"}
TRIAL = {"nom": "Claire Achat", "societe": "Agence Test", "email": "claire@agence-test.fr"}

TEMPLATES = {
    "password_reset": lambda: emails.password_reset(USER, "raw-token"),
    "trial_admin_notification": lambda: emails.trial_admin_notification(TRIAL),
    "trial_welcome": lambda: emails.trial_welcome(USER, "raw-token"),
    "trial_credits_added": lambda: emails.trial_credits_added(USER),
    "purchase_confirmation": lambda: emails.purchase_confirmation(USER, 1000, EXPIRY),
    "unit_purchase_confirmation": lambda: emails.unit_purchase_confirmation(USER, 37, EXPIRY),
    "unit_purchase_welcome": lambda: emails.unit_purchase_welcome(USER, "raw-token", 37, EXPIRY),
    "unit_purchase_welcome_one": lambda: emails.unit_purchase_welcome(USER, "raw-token", 1, EXPIRY),
    "payment_anomaly": lambda: emails.payment_anomaly("raison", SESSION),
    # Invoices (Alex, 08/10/2026): the sentence when the invoice is attached, and Alex's notice.
    "purchase_confirmation_invoice": lambda: emails.purchase_confirmation(USER, 1000, EXPIRY, invoice_number="F-2026-00001"),
    "unit_purchase_confirmation_invoice": lambda: emails.unit_purchase_confirmation(USER, 37, EXPIRY, invoice_number="F-2026-00002"),
    "unit_purchase_welcome_invoice": lambda: emails.unit_purchase_welcome(USER, "raw-token", 1, EXPIRY, invoice_number="F-2026-00003"),
    "invoice_not_issued": lambda: emails.invoice_not_issued("raison", USER, 100, 100, SESSION),
    "credit_note": lambda: emails.credit_note(USER, "AV-2026-00001", "F-2026-00001", 11_880),
    "refund_without_credit_note": lambda: emails.refund_without_credit_note(
        "raison", {"id": "ch_1", "payment_intent": "pi_1", "amount_refunded": 11_880}),
    # Refunds and credits (Alex, 09/10/2026): Alex's two notices.
    "refund_partial": lambda: emails.refund_partial(
        {"pack": 100, "credits": 100, "paid_at": EXPIRY}, dict(USER, company="Agence Test", page_credits=100),
        {"id": "ch_1", "payment_intent": "pi_1", "amount": 11_880, "amount_refunded": 2_000}),
    "refund_not_taken_back": lambda: emails.refund_not_taken_back(
        "raison", {"id": "ch_1", "payment_intent": "pi_1", "amount_refunded": 11_880, "refunded": True}),
    "refund_not_taken_back_nor_credit_note": lambda: emails.refund_not_taken_back(
        "raison", {"id": "ch_1", "payment_intent": "pi_1", "amount_refunded": 500}, no_credit_note=True),
}


@pytest.mark.parametrize("name", TEMPLATES)
def test_no_scans_and_e_mail_with_its_hyphen(name):
    subject, body = TEMPLATES[name]()
    text = f"{subject}\n{body}"
    assert not re.search(r"\bscans?\b", text, re.IGNORECASE), text
    assert not re.search(r"\b[Ee]mails?\b", text), text


def test_the_documents_are_named_as_alex_asked():
    assert emails.trial_welcome(USER, "t")[0] == "Votre espace ScanID est ouvert — 20 documents offerts"
    assert emails.purchase_confirmation(USER, 1000, EXPIRY)[0] == "Vos 1 000 documents ScanID sont disponibles"
    assert "(20 documents offerts)" in emails.trial_admin_notification(TRIAL)[1]


def test_the_purchase_e_mails_name_the_tab_as_the_app_writes_it():
    """Alex's third check (2026-10-02): the tab is « Mon compte », in sentence
    case. The purchase e-mails send the customer to it, so they write it the same."""
    line = "Le détail de vos achats est dans « Mon compte » → « Mes achats »."
    assert line in emails.purchase_confirmation(USER, 1000, EXPIRY)[1]
    assert line in emails.unit_purchase_confirmation(USER, 37, EXPIRY)[1]
    assert line in emails.unit_purchase_welcome(USER, "raw-token", 37, EXPIRY)[1]
    for name, render in TEMPLATES.items():
        assert "Mon Compte" not in "\n".join(render()), name


def test_the_attached_invoice_is_named_in_the_purchase_e_mails():
    line = "Votre facture F-2026-00001 est jointe à cet e-mail. Le détail de vos achats est dans « Mon compte » → « Mes achats »."
    assert line in emails.purchase_confirmation(USER, 1000, EXPIRY, invoice_number="F-2026-00001")[1]
    assert line in emails.unit_purchase_confirmation(USER, 37, EXPIRY, invoice_number="F-2026-00001")[1]
    assert line in emails.unit_purchase_welcome(USER, "raw-token", 37, EXPIRY, invoice_number="F-2026-00001")[1]
    for render in (lambda: emails.purchase_confirmation(USER, 1000, EXPIRY),
                   lambda: emails.unit_purchase_confirmation(USER, 37, EXPIRY)):
        assert "facture" not in render()[1].lower()     # no invoice: the e-mail of before, word for word

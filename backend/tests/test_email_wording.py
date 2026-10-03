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
    "purchase_confirmation": lambda: emails.purchase_confirmation(USER, 1000, EXPIRY),
    "unit_purchase_confirmation": lambda: emails.unit_purchase_confirmation(USER, 37, EXPIRY),
    "payment_anomaly": lambda: emails.payment_anomaly("raison", SESSION),
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
    for name, render in TEMPLATES.items():
        assert "Mon Compte" not in "\n".join(render()), name

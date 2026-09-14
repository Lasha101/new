"""« Mon Compte »: billing identity fields and « Mes achats ».

All identities and company numbers in this file are fictional."""
from datetime import datetime, timedelta, timezone

import billing
import billing_identity
import models
from tests.helpers import make_user, auth_headers


def luhn_siret(first13: str) -> str:
    return next(first13 + d for d in "0123456789" if billing_identity.is_valid_siret(first13 + d))


SIRET = luhn_siret("4400000000001")
FIELDS = {
    "company": "Agence Compte Test", "vat_number": "fr 99 123456789",
    "billing_street": "2 place de la Facture", "billing_postal_code": "69002",
    "billing_city": "Lyon", "billing_country": "France",
}


def test_a_client_saves_the_billing_fields_and_reads_them_back(client, db_session):
    make_user(db_session, "compta")
    response = client.put("/users/me", json={**FIELDS, "siret": f"{SIRET[:3]} {SIRET[3:]}"}, headers=auth_headers("compta"))
    assert response.status_code == 200, response.text

    me = client.get("/users/me", headers=auth_headers("compta")).json()      # what a reload shows
    assert me["company"] == "Agence Compte Test"
    assert me["siret"] == SIRET                                               # stored without spaces
    assert me["vat_number"] == "FR99123456789"
    assert (me["billing_street"], me["billing_postal_code"], me["billing_city"], me["billing_country"]) == (
        "2 place de la Facture", "69002", "Lyon", "France")


def test_invalid_siret_or_vat_is_refused_and_nothing_changes(client, db_session):
    make_user(db_session, "erreur")
    bad_siret = client.put("/users/me", json={"company": "Changée", "siret": "12345678901234"}, headers=auth_headers("erreur"))
    assert bad_siret.status_code == 400 and bad_siret.json()["detail"] == billing_identity.SIRET_ERROR
    bad_vat = client.put("/users/me", json={"vat_number": "FR1"}, headers=auth_headers("erreur"))
    assert bad_vat.status_code == 400 and bad_vat.json()["detail"] == billing_identity.VAT_ERROR
    assert client.get("/users/me", headers=auth_headers("erreur")).json()["company"] is None


def test_an_empty_value_clears_a_field(client, db_session):
    make_user(db_session, "efface")
    client.put("/users/me", json={"siret": SIRET, "vat_number": "FR99123456789"}, headers=auth_headers("efface"))
    client.put("/users/me", json={"siret": "", "vat_number": ""}, headers=auth_headers("efface"))
    me = client.get("/users/me", headers=auth_headers("efface")).json()
    assert (me["siret"], me["vat_number"]) == ("", "")


def test_the_protected_fields_stay_protected(client, db_session):
    make_user(db_session, "malin", page_credits=3)
    me = client.put("/users/me", json={**FIELDS, "page_credits": 999, "role": "admin"}, headers=auth_headers("malin")).json()
    assert (me["page_credits"], me["role"], me["company"]) == (3, "user", "Agence Compte Test")


def test_mes_achats_lists_only_my_paid_purchases_newest_first(client, db_session):
    me = make_user(db_session, "acheteur")
    other = make_user(db_session, "voisin")
    now = datetime.now(timezone.utc)
    for owner, pack, status, days_ago in ((me, 100, "paid", 40), (me, 1000, "paid", 2), (me, 3000, "pending", 1), (other, 5000, "paid", 1)):
        paid_at = now - timedelta(days=days_ago) if status == "paid" else None
        db_session.add(models.Purchase(
            user_id=owner["id"], pack=pack, credits=pack, amount_ht_cents=1, status=status, created_at=now,
            paid_at=paid_at, expires_at=billing.add_months(paid_at, 12) if paid_at else None,
            stripe_session_id=f"cs_{pack}" if status == "paid" else None,
        ))
    db_session.commit()

    assert client.get("/users/me/purchases").status_code == 401
    rows = client.get("/users/me/purchases", headers=auth_headers("acheteur")).json()
    assert [row["pack"] for row in rows] == [1000, 100]
    assert set(rows[0]) == {"id", "pack", "credits", "amount_ht_cents", "paid_at", "expires_at"}
    assert rows[0]["expires_at"][:4] == str((now - timedelta(days=2)).year + 1)
    assert client.get("/users/me/purchases", headers=auth_headers("voisin")).json()[0]["pack"] == 5000

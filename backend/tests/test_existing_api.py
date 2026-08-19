"""Regression tests: existing behaviour of the API that the results-screen
export changes must leave intact (authentication, passport CRUD, RBAC, list
contract, quotas, voyages, OCR jobs)."""
import pytest

from tests.helpers import make_user, make_passport, auth_headers

PASSPORT_KEYS = {"id", "owner_id", "first_name", "last_name", "birth_date", "expiration_date",
                 "nationality", "passport_number", "destination", "confidence_score", "voyages"}


def test_authentication_still_required_and_token_login_works(client, db_session):
    make_user(db_session, "alice")
    assert client.get("/users/me").status_code == 401
    assert client.get("/passports/").status_code == 401

    me = client.get("/users/me", headers=auth_headers("alice"))
    assert me.status_code == 200
    assert me.json()["user_name"] == "alice"
    assert me.json()["page_credits"] == 10

    login = client.post("/token", data={"username": "alice", "password": "secret-pass"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    assert client.get("/users/me", headers={"Authorization": f"Bearer {token}"}).status_code == 200
    bad = client.post("/token", data={"username": "alice", "password": "wrong"})
    assert bad.status_code == 401
    assert bad.json()["detail"] == "Nom d'utilisateur ou mot de passe incorrect"


def test_passports_list_contract_unchanged(client, user_with_documents):
    response = client.get("/passports/", headers=user_with_documents["headers"])
    assert response.status_code == 200
    rows = response.json()
    assert len(rows) == 4                                   # only the owner's rows
    assert set(rows[0].keys()) == PASSPORT_KEYS             # no new field leaked into the API
    assert "document_type" not in rows[0]
    assert {row["owner_id"] for row in rows} == {user_with_documents["user"]["id"]}
    # destination filter of the results table
    rome = client.get("/passports/?destination_filter=Rome", headers=user_with_documents["headers"]).json()
    assert {row["passport_number"] for row in rome} == {"98ZY12345", "123456789012"}


def test_admin_passports_list_and_filters(client, db_session, user_with_documents):
    make_user(db_session, "root", role="admin")
    rows = client.get("/passports/", headers=auth_headers("root")).json()
    assert len(rows) == 5
    bob = user_with_documents["other"]["id"]
    rows = client.get(f"/passports/?user_filter={bob}", headers=auth_headers("root")).json()
    assert [row["passport_number"] for row in rows] == ["11CD22222"]
    rows = client.get("/passports/?voyage_filter=Rome", headers=auth_headers("root")).json()
    assert len(rows) == 3


def test_passport_crud_flow(client, db_session):
    make_user(db_session, "alice")
    headers = auth_headers("alice")
    payload = {"first_name": "Léa", "last_name": "Roux", "birth_date": "1992-02-03", "expiration_date": "2031-04-05",
               "nationality": "Française", "passport_number": "12AB34567", "destination": "Oslo", "confidence_score": None}
    created = client.post("/passports/", json=payload, headers=headers)
    assert created.status_code == 200, created.text
    passport_id = created.json()["id"]
    assert created.json()["destination"] == "Oslo"

    # duplicate number for the same destination is refused (409)
    duplicate = client.post("/passports/", json=payload, headers=headers)
    assert duplicate.status_code == 409

    updated = client.put(f"/passports/{passport_id}", json={**payload, "destination": "Bergen"}, headers=headers)
    assert updated.status_code == 200
    assert updated.json()["destination"] == "Bergen"

    # a foreign user can neither update nor delete it
    make_user(db_session, "mallory")
    assert client.put(f"/passports/{passport_id}", json=payload, headers=auth_headers("mallory")).status_code == 403
    assert client.delete(f"/passports/{passport_id}", headers=auth_headers("mallory")).status_code == 403

    deleted = client.delete(f"/passports/{passport_id}", headers=headers)
    assert deleted.status_code == 200
    assert client.get("/passports/", headers=headers).json() == []
    assert client.delete(f"/passports/{passport_id}", headers=headers).status_code == 404


def test_delete_multiple_respects_ownership(client, user_with_documents):
    docs = user_with_documents["docs"]
    response = client.post("/passports/delete-multiple",
                           json={"passport_ids": [docs["pp1"]["id"], docs["other_pp"]["id"]]},
                           headers=user_with_documents["headers"])
    assert response.status_code == 200
    assert response.json() == {"deleted_count": 1}
    remaining = client.get("/passports/", headers=user_with_documents["headers"]).json()
    assert len(remaining) == 3
    assert len(client.get("/passports/", headers=user_with_documents["other_headers"]).json()) == 1


def test_admin_routes_require_admin(client, db_session):
    make_user(db_session, "alice")
    make_user(db_session, "root", role="admin")
    assert client.get("/admin/users/", headers=auth_headers("alice")).status_code == 403
    listing = client.get("/admin/users/", headers=auth_headers("root"))
    assert listing.status_code == 200
    assert {u["user_name"] for u in listing.json()} == {"alice", "root"}
    assert client.get("/admin/filterable-users", headers=auth_headers("root")).status_code == 200


def test_user_cannot_raise_own_credits(client, db_session):
    make_user(db_session, "alice", page_credits=3)
    response = client.put("/users/me", json={"page_credits": 999, "first_name": "Alicia"}, headers=auth_headers("alice"))
    assert response.status_code == 200
    assert response.json()["page_credits"] == 3
    assert response.json()["first_name"] == "Alicia"


def test_upload_refused_without_credits(client, db_session):
    make_user(db_session, "broke", page_credits=0)
    response = client.post("/passports/upload-and-extract/", files={"file": ("doc.pdf", b"%PDF-1.4 fake", "application/pdf")},
                           headers=auth_headers("broke"))
    assert response.status_code == 403
    assert response.json()["detail"] == "Crédits insuffisants. Veuillez contacter l'administrateur."


def test_destinations_voyages_and_jobs(client, user_with_documents):
    headers = user_with_documents["headers"]
    destinations = client.get("/destinations/", headers=headers)
    assert destinations.status_code == 200
    assert set(destinations.json()) == {"Dubrovnik été", "Rome"}

    voyage = client.post("/voyages/", json={"destination": "Rome", "passport_ids": [user_with_documents["docs"]["pp2"]["id"]]}, headers=headers)
    assert voyage.status_code == 200
    voyages = client.get("/voyages/", headers=headers).json()
    assert len(voyages) == 1 and voyages[0]["destination"] == "Rome"

    jobs = client.get("/ocr/jobs/", headers=headers)
    assert jobs.status_code == 200 and jobs.json() == []
    assert client.get("/ocr/jobs/does-not-exist", headers=headers).status_code == 404


def test_self_registration_gives_signup_credits(client):
    response = client.post("/users/register", json={
        "first_name": "New", "last_name": "User", "email": "new@example.com",
        "phone_number": "0600000000", "user_name": "newbie", "password": "pw",
    })
    assert response.status_code == 200, response.text
    assert response.json()["page_credits"] == 5
    assert response.json()["role"] == "user"
    again = client.post("/users/register", json={
        "first_name": "New", "last_name": "User", "email": "new@example.com",
        "phone_number": "0600000000", "user_name": "newbie2", "password": "pw",
    })
    assert again.status_code == 400
    assert again.json()["detail"] == "Email déjà enregistré"

"""The « Sexe » column in the database and the API (02/10/2026): the
`passports.sex` column reaches an existing database through the startup
migration, holds 'F', 'M' or NULL, is saved by the OCR job, returned by the
API, and survives every edit the results screen makes.

All identities in this file are fictional.
"""
import asyncio
import uuid

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import crud
import main
import models
import ocr_service
import schema_migrations
import schemas
from tests.helpers import make_user, make_passport, auth_headers


# --- Startup migration ------------------------------------------------------------

def _old_passports_table(engine):
    """The passports table exactly as production has it before this change,
    with one document already extracted."""
    with engine.begin() as connection:
        connection.execute(text(
            "CREATE TABLE passports (id VARCHAR(36) PRIMARY KEY, owner_id VARCHAR(36) NOT NULL, "
            "first_name VARCHAR NOT NULL, last_name VARCHAR NOT NULL, birth_date DATE NOT NULL, "
            "expiration_date DATE NOT NULL, nationality VARCHAR NOT NULL, passport_number VARCHAR NOT NULL, "
            "destination VARCHAR, confidence_score FLOAT)"))
        connection.execute(text(
            "INSERT INTO passports VALUES ('p1', 'u1', 'CLAIRE', 'MARTIN', '1990-02-15', '2032-06-05', "
            "'Française', '07XY12345', 'Rome', 0.93)"))


def test_migration_adds_sex_to_an_existing_passports_table():
    engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
    _old_passports_table(engine)
    models.Base.metadata.create_all(engine)          # what startup does first: new tables only
    assert "sex" not in {c["name"] for c in inspect(engine).get_columns("passports")}

    assert schema_migrations.add_missing_columns(engine) == ["passports.sex"]

    column = {c["name"]: c for c in inspect(engine).get_columns("passports")}["sex"]
    assert column["nullable"] is True
    # The document extracted before the change keeps everything, with an empty Sexe.
    session = sessionmaker(bind=engine)()
    try:
        rows = crud.get_passports_by_user(session, "u1")
        assert len(rows) == 1
        assert rows[0]["passport_number"] == "07XY12345" and rows[0]["sex"] is None
        assert schemas.Passport.model_validate(rows[0]).sex is None
    finally:
        session.close()
    assert schema_migrations.add_missing_columns(engine) == []   # idempotent


def test_sex_migration_is_listed_with_its_manual_sql():
    assert ("passports", "sex", "VARCHAR") in schema_migrations.ADDED_COLUMNS
    assert "ALTER TABLE passports ADD COLUMN IF NOT EXISTS sex VARCHAR;" in schema_migrations.__doc__


# --- API ------------------------------------------------------------------------------

DOCUMENT = {
    "first_name": "Claire", "last_name": "Martin", "birth_date": "1990-02-15",
    "expiration_date": "2032-06-05", "nationality": "Française", "passport_number": "07XY12345",
    "destination": "Rome", "confidence_score": 0.93,
}


def test_api_returns_the_stored_sex_and_empty_when_unknown(client, db_session):
    user = make_user(db_session, "claire")
    make_passport(db_session, user["id"], passport_number="07XY12345", sex="F")
    make_passport(db_session, user["id"], passport_number="X4RTBPFW4")
    rows = client.get("/passports/", headers=auth_headers("claire")).json()
    assert {row["passport_number"]: row["sex"] for row in rows} == {"07XY12345": "F", "X4RTBPFW4": None}


def test_manual_creation_without_sex_leaves_it_empty(client, db_session):
    make_user(db_session, "manuel")
    created = client.post("/passports/", json=DOCUMENT, headers=auth_headers("manuel"))
    assert created.status_code == 200, created.text
    assert created.json()["sex"] is None


@pytest.mark.parametrize("value", ["X", "<", "f", "FEMME", ""])
def test_only_f_m_or_null_are_accepted(client, db_session, value):
    make_user(db_session, "strict")
    response = client.post("/passports/", json=dict(DOCUMENT, sex=value), headers=auth_headers("strict"))
    assert response.status_code == 422


def test_every_edit_of_the_results_screen_keeps_the_sex(client, db_session):
    user = make_user(db_session, "editrice")
    headers = auth_headers("editrice")
    doc = make_passport(db_session, user["id"], passport_number="07XY12345", sex="M")

    # « Modifier »: the form sends back the whole row it loaded, sex included.
    row = next(r for r in client.get("/passports/", headers=headers).json() if r["id"] == doc["id"])
    edited = client.put(f"/passports/{doc['id']}", json=dict(row, first_name="Renommé"), headers=headers)
    assert edited.status_code == 200, edited.text
    assert (edited.json()["first_name"], edited.json()["sex"]) == ("Renommé", "M")

    # « Modifier Destination »: an explicit field list without the sex.
    bulk = {key: row[key] for key in ("first_name", "last_name", "birth_date", "expiration_date",
                                      "nationality", "passport_number", "confidence_score")}
    moved = client.put(f"/passports/{doc['id']}", json=dict(bulk, destination="Lisbonne"), headers=headers)
    assert moved.status_code == 200, moved.text
    assert (moved.json()["destination"], moved.json()["sex"]) == ("Lisbonne", "M")
    assert crud.get_passport(db_session, doc["id"])["sex"] == "M"


# --- OCR job → database ----------------------------------------------------------------

def test_ocr_job_saves_the_sex_read_from_the_mrz(db_session, monkeypatch):
    user = make_user(db_session, "ocrsexe", page_credits=10)
    identity = {"first_name": "CLAIRE", "last_name": "MARTIN", "nationality": "Française",
                "birth_date": "1990-02-15", "expiration_date": "2032-06-05", "confidence_score": 0.93}

    async def fake_extract(file_path, content_type, progress_callback=None):
        return [
            {"page_number": 1, "data": dict(identity, passport_number="07XY12345", sex="F")},
            {"page_number": 2, "data": dict(identity, passport_number="08XY12345", sex="M")},
            {"page_number": 3, "data": dict(identity, passport_number="X4RTBPFW4", sex=None)},
        ]

    job_id = str(uuid.uuid4())
    crud.create_ocr_job(db=db_session, job_id=job_id, user_id=user["id"], file_name="lot.pdf")
    monkeypatch.setattr(ocr_service, "extract_data_page_by_page", fake_extract)
    asyncio.run(main._run_ocr_extraction_job(
        db_session, job_id, "/tmp/unused", "application/pdf", "Rome", user["id"]))

    job = crud.get_ocr_job(db_session, job_id)
    assert [s["data"]["sex"] for s in job["successes"]] == ["F", "M", None]
    stored = {row["passport_number"]: row["sex"] for row in crud.get_passports_by_user(db_session, user["id"])}
    assert stored == {"07XY12345": "F", "08XY12345": "M", "X4RTBPFW4": None}

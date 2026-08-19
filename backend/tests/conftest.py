"""Shared fixtures: the FastAPI app wired to an in-memory SQLite database
(the schema is created from the SQLAlchemy models, exactly as on PostgreSQL),
so no test depends on a running PostgreSQL server."""
import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
# main.py creates/mounts the ./static directory relative to the working
# directory, so the suite must run from backend/.
if os.getcwd() != BACKEND_DIR:
    os.chdir(BACKEND_DIR)

import models  # noqa: E402
from database import get_db  # noqa: E402
from main import app  # noqa: E402
from tests.helpers import make_user, make_passport, auth_headers  # noqa: E402


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    models.Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        app.dependency_overrides.pop(get_db, None)
        engine.dispose()


@pytest.fixture()
def client(db_session):
    # No `with` block: the lifespan (PostgreSQL bootstrap) must not run.
    return TestClient(app)


@pytest.fixture()
def user_with_documents(db_session):
    """A regular user owning 2 passports and 2 identity cards (old and new
    CNI formats), plus another user's passport that must never leak."""
    user = make_user(db_session, "alice")
    other = make_user(db_session, "bob")
    docs = {
        "pp1": make_passport(db_session, user["id"], first_name="Élodie", last_name="Dupont-Lévy",
                             passport_number="12AB34567", destination="Dubrovnik été", confidence_score=0.8734),
        "pp2": make_passport(db_session, user["id"], first_name="Jean", last_name="Martin",
                             passport_number="98ZY12345", destination="Rome", confidence_score=0.91),
        "pi_old": make_passport(db_session, user["id"], first_name="Chloé", last_name="Bernard",
                                passport_number="123456789012", destination="Rome", confidence_score=None),
        "pi_new": make_passport(db_session, user["id"], first_name="Noé", last_name="Petit",
                                passport_number="X4RTBPFW4", destination=None, confidence_score=0.5),
        "other_pp": make_passport(db_session, other["id"], first_name="Zoé", last_name="Autre",
                                  passport_number="11CD22222", destination="Rome", confidence_score=0.7),
    }
    return {"user": user, "other": other, "docs": docs, "headers": auth_headers("alice"),
            "other_headers": auth_headers("bob")}

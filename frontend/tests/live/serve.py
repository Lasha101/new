#!/usr/bin/env python
"""A disposable ScanID backend for end-to-end runs (E2E_MODE=live).

The real FastAPI app, its real routes, its real auth — but on a throwaway SQLite
file instead of PostgreSQL, seeded with synthetic documents. No application file
is modified: `database.engine` / `database.SessionLocal` are rebound *before*
main.py imports them, which is the same substitution backend/tests/conftest.py
performs for pytest.

    python tests/live/serve.py --port 8001 --seed

Then, from frontend/:

    E2E_MODE=live VITE_API_URL=http://127.0.0.1:8001 \
    E2E_USERNAME=alice E2E_PASSWORD=test-password npm run test:e2e

Caveats, in full:
  * OCR still goes to Google Cloud Vision — real calls, real cost, real latency,
    and no useful text in a synthetic fixture. The upload spec therefore only
    asserts that a job reaches a terminal state in live mode.
  * SQLite is not PostgreSQL. It is close enough for the API contract (the
    backend's own pytest suite runs on SQLite too) but proves nothing about
    PostgreSQL-specific behaviour.
"""
import argparse
import os
import sys
import tempfile
from datetime import date

FRONTEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPO_ROOT = os.path.dirname(FRONTEND_DIR)
BACKEND_DIR = os.path.join(REPO_ROOT, "backend")
sys.path.insert(0, BACKEND_DIR)
# main.py creates ./static relative to the working directory.
os.chdir(BACKEND_DIR)

os.environ.setdefault("SECRET_KEY", "e2e-only-secret-key")
os.environ.setdefault("ADMIN_PASSWORD", "e2e-only-admin-password")

from sqlalchemy import create_engine          # noqa: E402
from sqlalchemy.orm import sessionmaker       # noqa: E402

import database                               # noqa: E402

DB_PATH = os.path.join(tempfile.gettempdir(), "scanid-e2e.sqlite3")


def use_sqlite(fresh: bool) -> None:
    """Points the app at a throwaway SQLite file, before main.py binds them."""
    if fresh and os.path.exists(DB_PATH):
        os.unlink(DB_PATH)
    engine = create_engine(
        f"sqlite:///{DB_PATH}",
        connect_args={"check_same_thread": False},  # background OCR tasks use other threads
    )
    database.engine = engine
    database.SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def seed(username: str, password: str) -> None:
    import crud
    import models
    import schemas

    models.Base.metadata.create_all(database.engine)
    db = database.SessionLocal()
    try:
        if crud.get_user_by_username(db, username=username):
            print(f"[serve] user {username!r} already seeded")
            return
        user = crud.create_user(db=db, user=schemas.UserCreate(
            first_name="Alice", last_name="Testeuse", email="alice@example.com",
            phone_number="0102030405", user_name=username, password=password, page_credits=12,
        ), role="user")

        # Same synthetic mix as tests/mock/data.js: 2 passports, 3 identity cards.
        documents = [
            ("Élodie", "Dupont-Lévy", "12AB34567", "Dubrovnik été", 0.8734, date(1990, 5, 17)),
            ("Jean", "Martin", "98ZY12345", "Rome", 0.91, date(1982, 11, 3)),
            ("Chloé", "Bernard", "123456789012", "Rome", None, date(1975, 2, 28)),
            ("Noé", "Petit", "X4RTBPFW4", None, 0.5, date(2001, 7, 9)),
            ("Camille", "Moreau", "D2H6862M2", "Dubrovnik été", 0.66, date(1968, 12, 24)),
        ]
        for first, last, number, destination, score, birth in documents:
            crud.create_user_passport(db=db, user_id=user["id"], passport=schemas.PassportCreate(
                first_name=first, last_name=last, birth_date=birth,
                expiration_date=date(2030, 1, 2), nationality="Française",
                passport_number=number, destination=destination, confidence_score=score,
            ))
        print(f"[serve] seeded {username!r} with {len(documents)} documents, 12 credits")
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--seed", action="store_true", help="create the test user and documents")
    parser.add_argument("--fresh", action="store_true", help="delete the SQLite file first")
    parser.add_argument("--username", default=os.getenv("E2E_USERNAME", "alice"))
    parser.add_argument("--password", default=os.getenv("E2E_PASSWORD", "test-password"))
    args = parser.parse_args()

    use_sqlite(fresh=args.fresh)
    if args.seed:
        seed(args.username, args.password)

    import uvicorn
    import main as app_module  # imported last: it binds engine/SessionLocal at import time

    assert app_module.SessionLocal is database.SessionLocal, "SQLite substitution did not take"
    print(f"[serve] ScanID API on http://{args.host}:{args.port} (SQLite at {DB_PATH})")
    uvicorn.run(app_module.app, host=args.host, port=args.port, log_level="warning")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

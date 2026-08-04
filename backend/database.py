# /database.py
import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

# --- GCP Credential Loading ---
# Google Vision only accepts credentials as a file path, so when the service
# account key is provided inline (GCP_CREDS_JSON) we write it to a temp file.
# This must run BEFORE the Vision client is instantiated (ocr_service import).
GCP_CREDS_JSON_CONTENT = os.getenv("GCP_CREDS_JSON")
if GCP_CREDS_JSON_CONTENT:
    try:
        creds_path = "/tmp/gcp-creds-new.json"
        # Owner-only permissions: the key must not be readable by other users.
        fd = os.open(creds_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(GCP_CREDS_JSON_CONTENT)
        os.chmod(creds_path, 0o600)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
        logging.info("Successfully loaded GCP credentials from env var.")
    except Exception as e:
        logging.error(f"Failed to write GCP credentials from env var: {e}")

# PostgreSQL connection string; in production (VPS) this points at the local
# PostgreSQL instance and lives in the server-side .env, never in git.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres@127.0.0.1:5432/travelapp",
)

# pool_pre_ping transparently replaces connections dropped by a database
# restart, so the app survives PostgreSQL maintenance without a redeploy.
# The session timezone is pinned to UTC so timestamptz values serialize with
# 'Z' offsets regardless of the server's locale (Firestore always spoke UTC).
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"options": "-c timezone=UTC"},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

logging.info("🐘 PostgreSQL engine initialized.")


def get_db():
    """Yields a request-scoped SQLAlchemy session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# /database.py
import os
import logging
import google.cloud.firestore as firestore  # type: ignore
from dotenv import load_dotenv

load_dotenv()

# --- GCP Credential Loading ---
# Google clients only accept credentials as a file path, so when the service
# account key is provided inline (GCP_CREDS_JSON) we write it to a temp file.
# This must run BEFORE any Google client is instantiated.
GCP_CREDS_JSON_CONTENT = os.getenv("GCP_CREDS_JSON")
if GCP_CREDS_JSON_CONTENT:
    try:
        creds_path = "/tmp/gcp-creds-new.json"
        with open(creds_path, "w") as f:
            f.write(GCP_CREDS_JSON_CONTENT)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
        logging.info("Successfully loaded GCP credentials from env var.")
    except Exception as e:
        logging.error(f"Failed to write GCP credentials from env var: {e}")

# The project id acts as the data partition when running against the
# Firestore emulator, so the new app keeps its own default partition.
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT") or "travel-app-new"
EMULATOR_HOST = os.getenv("FIRESTORE_EMULATOR_HOST")

# Initialize the client once so the whole app benefits from connection pooling.
db_client = firestore.Client(project=PROJECT_ID)

if EMULATOR_HOST:
    logging.info(f"✨ Firestore client initialized using EMULATOR at {EMULATOR_HOST} (Project: {db_client.project})")
else:
    logging.info(f"☁️ Firestore client initialized for PRODUCTION (Project: {db_client.project})")


def get_db():
    """Yields the shared Firestore client instance."""
    yield db_client

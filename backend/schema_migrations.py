# /schema_migrations.py
"""Idempotent, additive schema changes for a database that already exists.

`Base.metadata.create_all` creates missing TABLES but never adds a COLUMN to a
table that is already there, and the production `users` table predates the
columns below. Without this, the first query on `users` after the deploy
would fail with "column users.status does not exist" and nobody could log in.

Additive only: a column is added when it is missing, never altered or dropped.
Every column is nullable or carries a constant default, which PostgreSQL 11+
and SQLite both add in place. Runs at startup, after create_all.

The same change as plain SQL, for applying it by hand as the table owner:

    ALTER TABLE users ADD COLUMN IF NOT EXISTS status VARCHAR NOT NULL DEFAULT 'active';
    ALTER TABLE users ADD COLUMN IF NOT EXISTS session_version INTEGER NOT NULL DEFAULT 0;
    ALTER TABLE users ADD COLUMN IF NOT EXISTS company VARCHAR;
    ALTER TABLE users ADD COLUMN IF NOT EXISTS siret VARCHAR;
    ALTER TABLE users ADD COLUMN IF NOT EXISTS vat_number VARCHAR;
    ALTER TABLE users ADD COLUMN IF NOT EXISTS billing_street VARCHAR;
    ALTER TABLE users ADD COLUMN IF NOT EXISTS billing_postal_code VARCHAR;
    ALTER TABLE users ADD COLUMN IF NOT EXISTS billing_city VARCHAR;
    ALTER TABLE users ADD COLUMN IF NOT EXISTS billing_country VARCHAR;
"""
import logging
from typing import List

from sqlalchemy import inspect, text

logger = logging.getLogger(__name__)

# (table, column, SQL type and constraint). Constant defaults only.
ADDED_COLUMNS = [
    ("users", "status", "VARCHAR NOT NULL DEFAULT 'active'"),
    ("users", "session_version", "INTEGER NOT NULL DEFAULT 0"),
    ("users", "company", "VARCHAR"),
    ("users", "siret", "VARCHAR"),
    ("users", "vat_number", "VARCHAR"),
    ("users", "billing_street", "VARCHAR"),
    ("users", "billing_postal_code", "VARCHAR"),
    ("users", "billing_city", "VARCHAR"),
    ("users", "billing_country", "VARCHAR"),
]


def add_missing_columns(engine) -> List[str]:
    """Adds every column of ADDED_COLUMNS the database lacks. Returns the
    'table.column' names it added (empty when the schema is current)."""
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    added = []
    with engine.begin() as connection:
        for table, column, ddl in ADDED_COLUMNS:
            if table not in tables:
                continue  # create_all builds it complete
            existing = {c["name"] for c in inspect(connection).get_columns(table)}
            if column in existing:
                continue
            connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}"))
            added.append(f"{table}.{column}")
    if added:
        logger.info("Schéma mis à jour : colonnes ajoutées %s", ", ".join(added))
    return added

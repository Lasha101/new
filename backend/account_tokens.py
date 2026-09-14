# /account_tokens.py
"""One-time password links: « Mot de passe oublié ? » and the free-trial
welcome email.

- 256 random bits (secrets.token_urlsafe(32)), shown once, in the email.
- Only the SHA-256 is stored: a database dump or a backup holds no usable link.
- Valid config.PASSWORD_TOKEN_HOURS (48 h), usable once.
- Issuing a new link revokes the account's earlier unused ones, so only the
  most recent email works.
"""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

import config
import crud
import models

PURPOSE_RESET = "reset"
PURPOSE_SET = "set"


def _digest(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def issue(db: Session, user_id: str, purpose: str) -> str:
    """Creates a link token for the user and returns the raw value (for the
    email only — it is not retrievable afterwards)."""
    now = datetime.now(timezone.utc)
    db.query(models.AuthToken).filter(
        models.AuthToken.user_id == str(user_id),
        models.AuthToken.used_at.is_(None),
    ).delete(synchronize_session=False)
    raw = secrets.token_urlsafe(32)
    db.add(models.AuthToken(
        user_id=str(user_id), token_hash=_digest(raw), purpose=purpose,
        created_at=now, expires_at=now + timedelta(hours=config.PASSWORD_TOKEN_HOURS),
    ))
    db.commit()
    return raw


def _as_aware(value: datetime) -> datetime:
    # SQLite hands timestamps back naive; PostgreSQL keeps the zone.
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def find_valid(db: Session, raw_token: str) -> Optional[Dict[str, Any]]:
    """The token row and its active user, or None when the link is unknown,
    used, expired, or its account can no longer log in."""
    if not raw_token or len(raw_token) > 200:
        return None
    row = db.query(models.AuthToken).filter(models.AuthToken.token_hash == _digest(raw_token)).first()
    if row is None or row.used_at is not None:
        return None
    if _as_aware(row.expires_at) <= datetime.now(timezone.utc):
        return None
    user = crud.get_user(db, row.user_id)
    if user is None or user.get("status", "active") != "active":
        return None
    return {"token": row, "user": user}


def consume(db: Session, token_row: models.AuthToken, hashed_password: str) -> None:
    """Sets the new password, marks the link used, revokes the account's other
    links and ends its open sessions — all in one commit."""
    now = datetime.now(timezone.utc)
    user = db.get(models.User, token_row.user_id)
    user.hashed_password = hashed_password
    user.session_version = (user.session_version or 0) + 1
    token_row.used_at = now
    db.query(models.AuthToken).filter(
        models.AuthToken.user_id == token_row.user_id,
        models.AuthToken.used_at.is_(None),
        models.AuthToken.id != token_row.id,
    ).delete(synchronize_session=False)
    db.commit()

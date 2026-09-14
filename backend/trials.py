# /trials.py
"""Free-trial requests from scanid.fr/essai.html (Spec v2 §1).

A request creates a PENDING account holding the trial credits and no usable
password, plus a TrialRequest row with what the form said. Alex validates or
refuses it from « Administration → Demandes d'essai ». Validation activates the
account and emails a one-time link to choose the password; a password is never
sent. Pending and refused requests are deleted after TRIAL_PURGE_DAYS.
"""
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from pydantic import EmailStr, TypeAdapter, ValidationError
from sqlalchemy import func
from sqlalchemy.orm import Session

import billing_identity
import config
import crud
import models

STATUS_PENDING = "pending"
STATUS_VALIDATED = "validated"
STATUS_REJECTED = "rejected"

_EMAIL = TypeAdapter(EmailStr)
_TEXT_LIMITS = {"nom": 200, "societe": 200, "telephone": 40, "volume": 100, "message": 2000}


class TrialRequestError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _text(body: Dict[str, Any], field: str) -> str:
    value = body.get(field)
    if value is None:
        return ""
    if not isinstance(value, str):
        raise TrialRequestError(f"Le champ « {field} » est invalide.")
    value = value.strip()
    if len(value) > _TEXT_LIMITS[field]:
        raise TrialRequestError(f"Le champ « {field} » est trop long.")
    return value


def parse(body: Any) -> Dict[str, Any]:
    """Validates the JSON the site sends. Unknown fields are ignored."""
    if not isinstance(body, dict):
        raise TrialRequestError("Requête invalide.")
    data = {field: _text(body, field) for field in _TEXT_LIMITS}
    if not data["nom"]:
        raise TrialRequestError("Le nom est obligatoire.")

    try:
        data["email"] = str(_EMAIL.validate_python(str(body.get("email") or "").strip())).lower()
    except ValidationError:
        raise TrialRequestError("L'adresse email n'est pas valide.")

    consent = body.get("consentement")
    if not (consent is True or (isinstance(consent, str) and consent.strip().lower() in ("true", "oui", "on", "1"))):
        raise TrialRequestError("Le consentement est obligatoire.")

    siret = billing_identity.normalize_siret(body.get("siret") if isinstance(body.get("siret"), str) else "")
    if siret and not billing_identity.is_valid_siret(siret):
        raise TrialRequestError(billing_identity.SIRET_ERROR)
    vat = billing_identity.normalize_vat(body.get("tva") if isinstance(body.get("tva"), str) else "")
    if vat and not billing_identity.is_valid_vat(vat):
        raise TrialRequestError(billing_identity.VAT_ERROR)
    data["siret"], data["tva"] = siret, vat
    return data


def _email_taken(db: Session, email: str) -> bool:
    if db.query(models.User).filter(
        (func.lower(models.User.email) == email) | (func.lower(models.User.user_name) == email)
    ).first():
        return True
    return db.query(models.TrialRequest).filter(
        func.lower(models.TrialRequest.email) == email,
        models.TrialRequest.status == STATUS_PENDING,
    ).first() is not None


def _row(request: models.TrialRequest) -> Dict[str, Any]:
    return crud._row_to_dict(request)


def create(db: Session, data: Dict[str, Any]) -> Dict[str, Any]:
    """The pending account and its request, committed together."""
    if _email_taken(db, data["email"]):
        raise TrialRequestError("Un compte ou une demande existe déjà pour cette adresse email.", 409)

    now = datetime.now(timezone.utc)
    first_name, _, last_name = data["nom"].partition(" ")
    user = models.User(
        first_name=first_name, last_name=last_name.strip(), email=data["email"],
        phone_number=data["telephone"], user_name=data["email"],
        # Not a hash of anything: no password can ever match it. The account
        # gets a real password only through the link sent on validation.
        hashed_password=f"!pending-trial-{secrets.token_hex(8)}",
        role="user", uploaded_pages_count=0, page_credits=config.TRIAL_CREDITS,
        status=STATUS_PENDING, company=data["societe"] or None,
        siret=data["siret"] or None, vat_number=data["tva"] or None,
    )
    db.add(user)
    db.flush()
    request = models.TrialRequest(
        user_id=user.id, nom=data["nom"], societe=data["societe"] or None, email=data["email"],
        telephone=data["telephone"] or None, volume=data["volume"] or None,
        message=data["message"] or None, siret=data["siret"] or None, tva=data["tva"] or None,
        status=STATUS_PENDING, consent_at=now, created_at=now,
    )
    db.add(request)
    db.commit()
    return _row(request)


def list_pending(db: Session) -> List[Dict[str, Any]]:
    rows = (db.query(models.TrialRequest)
            .filter(models.TrialRequest.status == STATUS_PENDING)
            .order_by(models.TrialRequest.created_at.desc())
            .all())
    return [_row(row) for row in rows]


def _pending_request_and_user(db: Session, request_id: str) -> Tuple[models.TrialRequest, models.User]:
    request = db.get(models.TrialRequest, str(request_id))
    if request is None:
        raise TrialRequestError("Demande d'essai introuvable.", 404)
    if request.status != STATUS_PENDING:
        raise TrialRequestError("Cette demande a déjà été traitée.", 409)
    user = db.get(models.User, request.user_id) if request.user_id else None
    if user is None or user.status != STATUS_PENDING:
        raise TrialRequestError("Le compte associé à cette demande n'existe plus.", 409)
    return request, user


def validate(db: Session, request_id: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Activates the account. Returns (request, user); the caller issues the
    password link and sends the welcome email."""
    request, user = _pending_request_and_user(db, request_id)
    user.status = "active"
    request.status = STATUS_VALIDATED
    request.decided_at = datetime.now(timezone.utc)
    db.commit()
    return _row(request), crud.get_user(db, user.id)


def reject(db: Session, request_id: str) -> Dict[str, Any]:
    request, user = _pending_request_and_user(db, request_id)
    user.status = "rejected"
    request.status = STATUS_REJECTED
    request.decided_at = datetime.now(timezone.utc)
    db.commit()
    return _row(request)


def purge(db: Session, now: Optional[datetime] = None) -> int:
    """Deletes pending and refused requests older than TRIAL_PURGE_DAYS, with
    the accounts they created as long as those never became active. Returns the
    number of requests deleted."""
    cutoff = (now or datetime.now(timezone.utc)) - timedelta(days=config.TRIAL_PURGE_DAYS)
    stale = (db.query(models.TrialRequest)
             .filter(models.TrialRequest.status.in_([STATUS_PENDING, STATUS_REJECTED]),
                     models.TrialRequest.created_at < cutoff)
             .all())
    for request in stale:
        user = db.get(models.User, request.user_id) if request.user_id else None
        if user is not None and user.status != "active":
            db.query(models.AuthToken).filter(models.AuthToken.user_id == user.id).delete(synchronize_session=False)
            db.delete(user)
        db.delete(request)
    db.commit()
    return len(stale)

# /crud.py
from datetime import datetime, timezone, date
from typing import Optional, List, Dict, Any
from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import models
import schemas


def _row_to_dict(row) -> Optional[Dict[str, Any]]:
    """Plain-dict view of an ORM row (the API layer works on dicts with an
    'id' key, exactly like the Firestore documents did)."""
    if row is None:
        return None
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}


def _escape_like(term: str) -> str:
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


# --- Users ---

def get_user(db: Session, user_id: str):
    return _row_to_dict(db.get(models.User, str(user_id)))


def get_user_by_username(db: Session, username: str):
    row = db.query(models.User).filter(models.User.user_name == username).first()
    return _row_to_dict(row)


def get_user_by_email(db: Session, email: str):
    row = db.query(models.User).filter(models.User.email == email).first()
    return _row_to_dict(row)


def get_users(db: Session, skip: int = 0, limit: int = 100, name_filter: Optional[str] = None):
    query = db.query(models.User)
    if name_filter:
        # Prefix search on the login name; 'admin' is dropped from the results
        # afterwards (same post-filter the Firestore version applied).
        query = query.filter(models.User.user_name.like(_escape_like(name_filter) + "%", escape="\\"))
    else:
        query = query.filter(models.User.user_name != "admin")

    # Firestore's inequality/range filters implicitly ordered by user_name;
    # the explicit ORDER BY keeps the list alphabetical and pagination stable.
    query = query.order_by(models.User.user_name, models.User.id)
    results = [_row_to_dict(row) for row in query.offset(skip).limit(limit).all()]
    if name_filter:
        results = [u for u in results if u.get("user_name") != "admin"]
    return results


def create_user(db: Session, user: schemas.UserCreate, role: str = "user") -> Optional[Dict[str, Any]]:
    import auth
    hashed_password = auth.get_password_hash(user.password)
    user_data = user.model_dump(exclude={"password"})
    user_data.update({"hashed_password": hashed_password, "role": role, "uploaded_pages_count": 0})
    row = models.User(**user_data)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        # Loser of a concurrent-registration race on the unique columns:
        # report the same 400 the endpoint pre-checks would have produced.
        db.rollback()
        if get_user_by_email(db, email=user_data["email"]):
            raise HTTPException(status_code=400, detail="Email déjà enregistré")
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà enregistré")
    return {**user_data, "id": row.id}


def update_user(db: Session, user_id: str, user_update: schemas.UserUpdate) -> Optional[Dict[str, Any]]:
    import auth
    update_data = user_update.model_dump(exclude_unset=True)
    # An explicit null never means "erase the field": every User field is
    # required, so writing null would corrupt the record (and 500 every
    # endpoint that returns this user from then on).
    update_data = {key: value for key, value in update_data.items() if value is not None}

    # The login name can never be blanked (the account would become
    # unreachable), and a renamed account must not collide with another
    # user's login name.
    if "user_name" in update_data and not update_data["user_name"]:
        update_data.pop("user_name")
    new_username = update_data.get("user_name")
    if new_username:
        existing = get_user_by_username(db, username=new_username)
        if existing and existing["id"] != str(user_id):
            raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà enregistré")

    # Same for the email address, which must stay unique across accounts.
    new_email = update_data.get("email")
    if new_email:
        existing = get_user_by_email(db, email=new_email)
        if existing and existing["id"] != str(user_id):
            raise HTTPException(status_code=400, detail="Email déjà enregistré")

    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = auth.get_password_hash(update_data["password"])
    update_data.pop("password", None)
    # With nothing left to change (e.g. a non-admin sent only protected
    # fields) the current user is returned as-is.
    if update_data:
        row = db.get(models.User, str(user_id))
        if row is not None:
            for key, value in update_data.items():
                setattr(row, key, value)
            try:
                db.commit()
            except IntegrityError:
                # Loser of a concurrent rename/email race on the unique columns.
                db.rollback()
                existing = get_user_by_username(db, username=new_username) if new_username else None
                if existing and existing["id"] != str(user_id):
                    raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà enregistré")
                raise HTTPException(status_code=400, detail="Email déjà enregistré")
    return get_user(db, user_id)


def update_user_password_hash(db: Session, user_id: str, hashed_password: str) -> None:
    """Replaces a stored password hash in place.

    Used only by the transparent argon2 upgrade in auth.authenticate_user: the
    password itself has just been verified, so this writes the new hash without
    touching any other column. Never logs anything.
    """
    row = db.get(models.User, str(user_id))
    if row is None:
        return
    row.hashed_password = hashed_password
    db.commit()


def delete_user(db: Session, user_id: str) -> Optional[Dict[str, Any]]:
    row = db.get(models.User, str(user_id))
    if row is not None:
        data = _row_to_dict(row)
        db.delete(row)
        db.commit()
        return data
    return None


def get_all_users_for_filtering(db: Session):
    rows = db.query(models.User).order_by(models.User.user_name, models.User.id).all()
    return [_row_to_dict(row) for row in rows]


# --- Passports (documents: French passports and national identity cards) ---

def get_passport(db: Session, passport_id: str):
    return _row_to_dict(db.get(models.Passport, str(passport_id)))


def get_passports(db: Session, skip: int = 0, limit: int = 100, user_filter: Optional[str] = None, voyage_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    query = db.query(models.Passport)
    if user_filter:
        query = query.filter(models.Passport.owner_id == user_filter)
    if voyage_filter:
        query = query.filter(models.Passport.destination == voyage_filter)
    # Deterministic order so offset/limit windows are stable across updates
    # (Firestore's default document-id ordering gave the same guarantee).
    return [_row_to_dict(row) for row in query.order_by(models.Passport.id).offset(skip).limit(limit).all()]


def get_passports_by_user(db: Session, user_id: str, destination: Optional[str] = None) -> List[Dict[str, Any]]:
    query = db.query(models.Passport).filter(models.Passport.owner_id == str(user_id))
    if destination:
        query = query.filter(models.Passport.destination == destination)
    return [_row_to_dict(row) for row in query.all()]


def get_passports_by_ids(db: Session, passport_ids: List[str]) -> List[Dict[str, Any]]:
    results = []
    for passport_id in passport_ids:
        passport = get_passport(db, passport_id)
        if passport:
            results.append(passport)
    return results


def _normalize_dates(passport_data: Dict[str, Any]) -> None:
    """The date columns store plain dates; tz-aware datetimes (the historical
    Firestore representation) are reduced to their date part."""
    for field in ("birth_date", "expiration_date"):
        value = passport_data.get(field)
        if isinstance(value, datetime):
            passport_data[field] = value.date()


def create_user_passport(db: Session, passport: schemas.PassportCreate, user_id: str) -> Optional[Dict[str, Any]]:
    # Reject a duplicate document number for the same user and destination.
    if passport.destination:
        existing = (
            db.query(models.Passport)
            .filter(models.Passport.owner_id == user_id)
            .filter(models.Passport.passport_number == passport.passport_number)
            .filter(models.Passport.destination == passport.destination)
            .first()
        )
        if existing is not None:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail=f"Le passeport numéro '{passport.passport_number}' est déjà enregistré pour la destination '{passport.destination}'.",
            )

    passport_data = passport.model_dump()
    passport_data["owner_id"] = str(user_id)
    _normalize_dates(passport_data)
    row = models.Passport(**passport_data)
    db.add(row)
    db.commit()
    return {**passport_data, "id": row.id}


def update_passport(db: Session, passport_id: str, passport_update: schemas.PassportCreate) -> Optional[Dict[str, Any]]:
    update_data = passport_update.model_dump(exclude_unset=True)
    _normalize_dates(update_data)
    row = db.get(models.Passport, str(passport_id))
    if row is not None:
        for key, value in update_data.items():
            setattr(row, key, value)
        db.commit()
    return get_passport(db, passport_id)


def delete_passport(db: Session, passport_id: str):
    # The deleted document is returned (response_model=Passport needs the
    # full record, not just the id).
    row = db.get(models.Passport, str(passport_id))
    data = _row_to_dict(row)
    if row is not None:
        db.delete(row)
        db.commit()
    return {**data, "id": passport_id} if data else None


def delete_multiple_passports(db: Session, passport_ids: List[str], user_id: str, role: str) -> int:
    deleted_count = 0
    for passport_id in passport_ids:
        row = db.get(models.Passport, str(passport_id))
        if row is not None:
            if role == "admin" or row.owner_id == user_id:
                db.delete(row)
                deleted_count += 1
    db.commit()
    return deleted_count


def filter_data(db: Session, destination: Optional[str], user_id: Optional[str], first_name: Optional[str], last_name: Optional[str]) -> List[Dict[str, Any]]:
    query = db.query(models.Passport)
    if user_id:
        query = query.filter(models.Passport.owner_id == user_id)
    if destination:
        query = query.filter(models.Passport.destination == destination)
    if first_name:
        query = query.filter(models.Passport.first_name == first_name)
    if last_name:
        query = query.filter(models.Passport.last_name == last_name)

    results = []
    for row in query.all():
        data = _row_to_dict(row)
        data["destination"] = data.get("destination", "N/A")
        results.append(data)
    return results


def get_destinations_by_user_id(db: Session, user_id: str) -> List[str]:
    rows = db.query(models.Passport.destination).filter(models.Passport.owner_id == user_id).all()
    destinations = set()
    for (destination,) in rows:
        if destination:
            destinations.add(destination)
    return list(destinations)


# --- OCR jobs ---

def create_ocr_job(db: Session, job_id: str, user_id: str, file_name: str):
    job_data = {
        "user_id": str(user_id), "file_name": file_name, "status": "processing",
        "progress": 0, "created_at": datetime.now(timezone.utc),
        "successes": [], "failures": []
    }
    row = models.OcrJob(id=job_id, **job_data)
    db.add(row)
    db.commit()
    return {**job_data, "id": job_id}


def get_ocr_job(db: Session, job_id: str):
    return _row_to_dict(db.get(models.OcrJob, job_id))


def update_ocr_job_progress(db: Session, job_id: str, progress: int):
    row = db.get(models.OcrJob, job_id)
    if row is not None:
        row.progress = progress
        db.commit()


def update_ocr_job_complete(db: Session, job_id: str, successes: list, failures: list):
    status = "complete" if not (len(successes) == 0 and len(failures) > 0) else "failed"
    row = db.get(models.OcrJob, job_id)
    if row is not None:
        row.status = status
        row.progress = 100
        row.finished_at = datetime.now(timezone.utc)
        row.successes = successes
        row.failures = failures
        db.commit()


def get_user_ocr_jobs(db: Session, user_id: str):
    rows = (
        db.query(models.OcrJob)
        .filter(models.OcrJob.user_id == str(user_id))
        .order_by(models.OcrJob.created_at.desc())
        .all()
    )
    return [_row_to_dict(row) for row in rows]


def delete_ocr_job(db: Session, job_id: str) -> Optional[Dict[str, Any]]:
    row = db.get(models.OcrJob, job_id)
    if row is not None:
        data = _row_to_dict(row)
        db.delete(row)
        db.commit()
        return data
    return None


# --- Voyages ---

def get_voyage(db: Session, voyage_id: str):
    return _row_to_dict(db.get(models.Voyage, str(voyage_id)))


def get_voyages(db: Session, skip: int = 0, limit: int = 100, user_filter: Optional[str] = None):
    query = db.query(models.Voyage)
    if user_filter:
        query = query.filter(models.Voyage.user_id == user_filter)
    return [_row_to_dict(row) for row in query.order_by(models.Voyage.id).offset(skip).limit(limit).all()]


def get_voyages_by_user(db: Session, user_id: str):
    rows = db.query(models.Voyage).filter(models.Voyage.user_id == str(user_id)).all()
    return [_row_to_dict(row) for row in rows]


def create_user_voyage(db: Session, voyage: schemas.VoyageCreate, user_id: str, passport_ids: List[str]) -> Dict[str, Any]:
    voyage_data = voyage.model_dump(exclude={"passport_ids"})
    voyage_data["user_id"] = user_id
    voyage_data["passport_ids"] = passport_ids
    row = models.Voyage(**voyage_data)
    db.add(row)
    db.commit()
    return {**voyage_data, "id": row.id}


def update_voyage(db: Session, voyage_id: str, voyage_update: schemas.VoyageCreate, passport_ids: List[str]) -> Optional[Dict[str, Any]]:
    update_data = voyage_update.model_dump(exclude_unset=True, exclude={"passport_ids"})
    update_data["passport_ids"] = passport_ids
    row = db.get(models.Voyage, str(voyage_id))
    if row is not None:
        for key, value in update_data.items():
            setattr(row, key, value)
        db.commit()
    return get_voyage(db, voyage_id)


def delete_voyage(db: Session, voyage_id: str):
    row = db.get(models.Voyage, str(voyage_id))
    if row is not None:
        data = _row_to_dict(row)
        db.delete(row)
        db.commit()
        return data
    return None

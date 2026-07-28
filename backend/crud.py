# /crud.py
from datetime import datetime, timezone, date
from typing import Optional, List, Dict, Any
from http import HTTPStatus

from fastapi import HTTPException
import google.cloud.firestore as firestore  # type: ignore
from google.cloud.firestore import FieldFilter  # type: ignore

import schemas


# --- Users ---

def get_user(db: firestore.Client, user_id: str):
    doc = db.collection("users").document(str(user_id)).get()
    return {**doc.to_dict(), "id": doc.id} if doc.exists else None


def get_user_by_username(db: firestore.Client, username: str):
    users = db.collection("users").where(filter=FieldFilter("user_name", "==", username)).limit(1).stream()
    for u in users:
        return {**u.to_dict(), "id": u.id}
    return None


def get_user_by_email(db: firestore.Client, email: str):
    users = db.collection("users").where(filter=FieldFilter("email", "==", email)).limit(1).stream()
    for u in users:
        return {**u.to_dict(), "id": u.id}
    return None


def get_users(db: firestore.Client, skip: int = 0, limit: int = 100, name_filter: Optional[str] = None):
    if name_filter:
        # Firestore limitation: range filters must stay on a single field, so we
        # search by name prefix and drop 'admin' from the results afterwards.
        query = db.collection("users").where(filter=FieldFilter("user_name", ">=", name_filter)).where(filter=FieldFilter("user_name", "<=", name_filter + ''))
    else:
        query = db.collection("users").where(filter=FieldFilter("user_name", "!=", "admin"))

    docs = query.offset(skip).limit(limit).stream()
    results = [{**d.to_dict(), "id": d.id} for d in docs]
    if name_filter:
        results = [u for u in results if u.get("user_name") != "admin"]
    return results


def create_user(db: firestore.Client, user: schemas.UserCreate, role: str = "user") -> Optional[Dict[str, Any]]:
    import auth
    hashed_password = auth.get_password_hash(user.password)
    user_data = user.model_dump(exclude={"password"})
    user_data.update({"hashed_password": hashed_password, "role": role, "uploaded_pages_count": 0})
    _, doc_ref = db.collection("users").add(user_data)
    return {**user_data, "id": doc_ref.id}


def update_user(db: firestore.Client, user_id: str, user_update: schemas.UserUpdate) -> Optional[Dict[str, Any]]:
    import auth
    update_data = user_update.model_dump(exclude_unset=True)
    # An explicit null never means "erase the field": every User field is
    # required, so writing null would corrupt the document (and 500 every
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
    # Firestore rejects an empty update; with nothing left to change (e.g. a
    # non-admin sent only protected fields) the current user is returned as-is.
    if update_data:
        db.collection("users").document(str(user_id)).update(update_data)
    return get_user(db, user_id)


def delete_user(db: firestore.Client, user_id: str) -> Optional[Dict[str, Any]]:
    user_doc_ref = db.collection("users").document(str(user_id))
    user_doc = user_doc_ref.get()
    if user_doc.exists:
        data = user_doc.to_dict()
        user_doc_ref.delete()
        return {**data, "id": user_doc.id} if data else None
    return None


def get_all_users_for_filtering(db: firestore.Client):
    docs = db.collection("users").stream()
    return [{**d.to_dict(), "id": d.id} for d in docs]


# --- Passports (documents: French passports and national identity cards) ---

def get_passport(db: firestore.Client, passport_id: str):
    doc = db.collection("passports").document(str(passport_id)).get()
    if doc.exists:
        data = doc.to_dict()
        return {**data, "id": doc.id} if data else None
    return None


def get_passports(db: firestore.Client, skip: int = 0, limit: int = 100, user_filter: Optional[str] = None, voyage_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    query = db.collection("passports")
    if user_filter:
        query = query.where(filter=FieldFilter("owner_id", "==", user_filter))
    if voyage_filter:
        query = query.where(filter=FieldFilter("destination", "==", voyage_filter))
    docs = query.offset(skip).limit(limit).stream()
    return [{**d.to_dict(), "id": d.id} for d in docs]


def get_passports_by_user(db: firestore.Client, user_id: str, destination: Optional[str] = None) -> List[Dict[str, Any]]:
    query = db.collection("passports").where(filter=FieldFilter("owner_id", "==", str(user_id)))
    if destination:
        query = query.where(filter=FieldFilter("destination", "==", destination))
    return [{**d.to_dict(), "id": d.id} for d in query.stream()]


def get_passports_by_ids(db: firestore.Client, passport_ids: List[str]) -> List[Dict[str, Any]]:
    results = []
    for passport_id in passport_ids:
        passport = get_passport(db, passport_id)
        if passport:
            results.append(passport)
    return results


def _convert_dates_for_firestore(passport_data: Dict[str, Any]) -> None:
    """Firestore stores dates as timestamps, so plain dates become UTC midnight
    datetimes (writing a bare `date` raises TypeError in the Firestore client)."""
    for field in ("birth_date", "expiration_date"):
        value = passport_data.get(field)
        if isinstance(value, datetime):
            value = value.date()
        if isinstance(value, date):
            passport_data[field] = datetime.combine(value, datetime.min.time(), tzinfo=timezone.utc)


def create_user_passport(db: firestore.Client, passport: schemas.PassportCreate, user_id: str) -> Optional[Dict[str, Any]]:
    # Reject a duplicate document number for the same user and destination.
    if passport.destination:
        existing_passport_query = db.collection("passports").where(filter=FieldFilter("owner_id", "==", user_id)).where(filter=FieldFilter("passport_number", "==", passport.passport_number)).where(filter=FieldFilter("destination", "==", passport.destination)).limit(1).stream()
        for _ in existing_passport_query:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail=f"Le passeport numéro '{passport.passport_number}' est déjà enregistré pour la destination '{passport.destination}'.",
            )

    passport_data = passport.model_dump()
    passport_data["owner_id"] = str(user_id)
    _convert_dates_for_firestore(passport_data)
    _, doc_ref = db.collection("passports").add(passport_data)
    return {**passport_data, "id": doc_ref.id}


def update_passport(db: firestore.Client, passport_id: str, passport_update: schemas.PassportCreate) -> Optional[Dict[str, Any]]:
    update_data = passport_update.model_dump(exclude_unset=True)
    _convert_dates_for_firestore(update_data)
    db.collection("passports").document(passport_id).update(update_data)
    return get_passport(db, passport_id)


def delete_passport(db: firestore.Client, passport_id: str):
    # The deleted document is returned (response_model=Passport needs the
    # full record, not just the id).
    doc_ref = db.collection("passports").document(str(passport_id))
    doc = doc_ref.get()
    data = doc.to_dict() if doc.exists else None
    doc_ref.delete()
    return {**data, "id": passport_id} if data else None


def delete_multiple_passports(db: firestore.Client, passport_ids: List[str], user_id: str, role: str) -> int:
    deleted_count = 0
    batch = db.batch()
    for passport_id in passport_ids:
        passport_ref = db.collection("passports").document(passport_id)
        passport_doc = passport_ref.get()
        if passport_doc.exists:
            passport_data = passport_doc.to_dict()
            if role == "admin" or passport_data.get("owner_id") == user_id:
                batch.delete(passport_ref)
                deleted_count += 1
    batch.commit()
    return deleted_count


def filter_data(db: firestore.Client, destination: Optional[str], user_id: Optional[str], first_name: Optional[str], last_name: Optional[str]) -> List[Dict[str, Any]]:
    query = db.collection("passports")
    if user_id:
        query = query.where(filter=FieldFilter("owner_id", "==", user_id))
    if destination:
        query = query.where(filter=FieldFilter("destination", "==", destination))
    if first_name:
        query = query.where(filter=FieldFilter("first_name", "==", first_name))
    if last_name:
        query = query.where(filter=FieldFilter("last_name", "==", last_name))

    results = []
    for doc in query.stream():
        data = doc.to_dict()
        data["id"] = doc.id
        data["destination"] = data.get("destination", "N/A")
        results.append(data)
    return results


def get_destinations_by_user_id(db: firestore.Client, user_id: str) -> List[str]:
    query = db.collection("passports").where(filter=FieldFilter("owner_id", "==", user_id)).stream()
    destinations = set()
    for doc in query:
        d = doc.to_dict().get("destination")
        if d:
            destinations.add(d)
    return list(destinations)


# --- OCR jobs ---

def create_ocr_job(db: firestore.Client, job_id: str, user_id: str, file_name: str):
    job_data = {
        "user_id": str(user_id), "file_name": file_name, "status": "processing",
        "progress": 0, "created_at": datetime.now(timezone.utc),
        "successes": [], "failures": []
    }
    db.collection("ocr_jobs").document(job_id).set(job_data)
    return {**job_data, "id": job_id}


def get_ocr_job(db: firestore.Client, job_id: str):
    doc = db.collection("ocr_jobs").document(job_id).get()
    if doc.exists:
        data = doc.to_dict()
        return {**data, "id": doc.id} if data else None
    return None


def update_ocr_job_progress(db: firestore.Client, job_id: str, progress: int):
    db.collection("ocr_jobs").document(job_id).update({"progress": progress})


def update_ocr_job_complete(db: firestore.Client, job_id: str, successes: list, failures: list):
    status = "complete" if not (len(successes) == 0 and len(failures) > 0) else "failed"
    db.collection("ocr_jobs").document(job_id).update({
        "status": status, "progress": 100, "finished_at": datetime.now(timezone.utc),
        "successes": successes, "failures": failures
    })


def get_user_ocr_jobs(db: firestore.Client, user_id: str):
    docs = db.collection("ocr_jobs").where(filter=FieldFilter("user_id", "==", str(user_id))).order_by("created_at", direction="DESCENDING").stream()
    return [{**d.to_dict(), "id": d.id} for d in docs]


def delete_ocr_job(db: firestore.Client, job_id: str) -> Optional[Dict[str, Any]]:
    job_doc_ref = db.collection("ocr_jobs").document(job_id)
    job_doc = job_doc_ref.get()
    if job_doc.exists:
        data = job_doc.to_dict()
        job_doc_ref.delete()
        return {**data, "id": job_doc.id} if data else None
    return None


# --- Voyages ---

def get_voyage(db: firestore.Client, voyage_id: str):
    doc = db.collection("voyages").document(str(voyage_id)).get()
    if doc.exists:
        data = doc.to_dict()
        return {**data, "id": doc.id} if data else None
    return None


def get_voyages(db: firestore.Client, skip: int = 0, limit: int = 100, user_filter: Optional[str] = None):
    query = db.collection("voyages")
    if user_filter:
        query = query.where(filter=FieldFilter("user_id", "==", user_filter))
    docs = query.offset(skip).limit(limit).stream()
    return [{**d.to_dict(), "id": d.id} for d in docs]


def get_voyages_by_user(db: firestore.Client, user_id: str):
    docs = db.collection("voyages").where(filter=FieldFilter("user_id", "==", str(user_id))).stream()
    return [{**d.to_dict(), "id": d.id} for d in docs]


def create_user_voyage(db: firestore.Client, voyage: schemas.VoyageCreate, user_id: str, passport_ids: List[str]) -> Dict[str, Any]:
    voyage_data = voyage.model_dump(exclude={"passport_ids"})
    voyage_data["user_id"] = user_id
    voyage_data["passport_ids"] = passport_ids
    _, doc_ref = db.collection("voyages").add(voyage_data)
    return {**voyage_data, "id": doc_ref.id}


def update_voyage(db: firestore.Client, voyage_id: str, voyage_update: schemas.VoyageCreate, passport_ids: List[str]) -> Optional[Dict[str, Any]]:
    update_data = voyage_update.model_dump(exclude_unset=True, exclude={"passport_ids"})
    update_data["passport_ids"] = passport_ids
    db.collection("voyages").document(voyage_id).update(update_data)
    return get_voyage(db, voyage_id)


def delete_voyage(db: firestore.Client, voyage_id: str):
    voyage_doc_ref = db.collection("voyages").document(voyage_id)
    voyage_doc = voyage_doc_ref.get()
    if voyage_doc.exists:
        data = voyage_doc.to_dict()
        voyage_doc_ref.delete()
        return {**data, "id": voyage_doc.id} if data else None
    return None



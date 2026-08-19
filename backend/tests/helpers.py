"""Test data helpers: users, bearer tokens and documents created directly
through the CRUD layer (no login round-trip, so the /token rate limit never
interferes)."""
from datetime import date

import auth
import crud
import schemas


def make_user(db, user_name: str, role: str = "user", page_credits: int = 10):
    user = schemas.UserCreate(
        first_name=user_name.capitalize(), last_name="Test", email=f"{user_name}@example.com",
        phone_number="0102030405", user_name=user_name, password="secret-pass", page_credits=page_credits,
    )
    return crud.create_user(db=db, user=user, role=role)


def auth_headers(user_name: str):
    token = auth.create_access_token(data={"sub": user_name})
    return {"Authorization": f"Bearer {token}"}


def make_passport(db, owner_id: str, **overrides):
    data = {
        "first_name": "Élodie", "last_name": "Dupont", "birth_date": date(1990, 5, 17),
        "expiration_date": date(2030, 1, 2), "nationality": "Française",
        "passport_number": "12AB34567", "destination": "Dubrovnik", "confidence_score": 0.8734,
    }
    data.update(overrides)
    return crud.create_user_passport(db=db, passport=schemas.PassportCreate(**data), user_id=owner_id)

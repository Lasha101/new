# /models.py
import uuid

from sqlalchemy import Column, Date, DateTime, Float, Integer, JSON, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def _new_id() -> str:
    """Random string primary key, mirroring Firestore's auto document ids so
    every id stays an opaque string for the API and the frontend."""
    return uuid.uuid4().hex


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=_new_id)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    phone_number = Column(String, nullable=False)
    user_name = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")
    uploaded_pages_count = Column(Integer, nullable=False, default=0)
    page_credits = Column(Integer, nullable=True, default=0)


class Passport(Base):
    """Identity documents (French passports and CNI), one row per extracted or
    manually created document."""
    __tablename__ = "passports"

    id = Column(String(36), primary_key=True, default=_new_id)
    owner_id = Column(String(36), nullable=False, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    expiration_date = Column(Date, nullable=False)
    nationality = Column(String, nullable=False)
    passport_number = Column(String, nullable=False, index=True)
    destination = Column(String, nullable=True, index=True)
    confidence_score = Column(Float, nullable=True)


class OcrJob(Base):
    __tablename__ = "ocr_jobs"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    file_name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="processing")
    progress = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    successes = Column(JSON, nullable=False, default=list)
    failures = Column(JSON, nullable=False, default=list)


class Voyage(Base):
    __tablename__ = "voyages"

    id = Column(String(36), primary_key=True, default=_new_id)
    user_id = Column(String(36), nullable=False, index=True)
    destination = Column(String, nullable=False)
    passport_ids = Column(JSON, nullable=False, default=list)

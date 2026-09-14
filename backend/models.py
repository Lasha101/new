# /models.py
import uuid

from sqlalchemy import Column, Date, DateTime, Float, Integer, JSON, String, text
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
    # Added 14/09/2026. An existing database gains these columns through
    # schema_migrations.py (create_all never adds a column to a table that
    # already exists), so every one of them is nullable or has a server default.
    #
    # 'active' | 'pending' (a free-trial request awaiting Alex) | 'rejected'.
    # Only an active account can log in.
    status = Column(String, nullable=False, default="active", server_default=text("'active'"))
    # Carried in the session token as "sv"; raising it ends every session the
    # account has open (done by a password reset).
    session_version = Column(Integer, nullable=False, default=0, server_default=text("0"))
    # Billing identity (needed on French B2B invoices).
    company = Column(String, nullable=True)
    siret = Column(String, nullable=True)
    vat_number = Column(String, nullable=True)
    billing_street = Column(String, nullable=True)
    billing_postal_code = Column(String, nullable=True)
    billing_city = Column(String, nullable=True)
    billing_country = Column(String, nullable=True)


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


class TrialRequest(Base):
    """A free-trial request from scanid.fr/essai.html. The account it created
    stays 'pending' until an admin validates or rejects the request."""
    __tablename__ = "trial_requests"

    id = Column(String(36), primary_key=True, default=_new_id)
    user_id = Column(String(36), nullable=True, index=True)
    nom = Column(String, nullable=False)
    societe = Column(String, nullable=True)
    email = Column(String, nullable=False)
    telephone = Column(String, nullable=True)
    volume = Column(String, nullable=True)
    message = Column(String, nullable=True)
    siret = Column(String, nullable=True)
    tva = Column(String, nullable=True)
    # 'pending' | 'validated' | 'rejected'
    status = Column(String, nullable=False, default="pending", index=True)
    consent_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, index=True)
    decided_at = Column(DateTime(timezone=True), nullable=True)


class Purchase(Base):
    """A pack order. Created 'pending' when the customer is sent to Stripe,
    'paid' when the Stripe webhook confirms the payment and the credits land."""
    __tablename__ = "purchases"

    id = Column(String(36), primary_key=True, default=_new_id)
    user_id = Column(String(36), nullable=False, index=True)
    pack = Column(Integer, nullable=False)
    credits = Column(Integer, nullable=False)
    amount_ht_cents = Column(Integer, nullable=False)
    # 'pending' | 'paid'
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), nullable=False)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    # UNIQUE: what makes a replayed webhook credit nothing.
    stripe_session_id = Column(String, nullable=True, unique=True)
    amount_paid_cents = Column(Integer, nullable=True)
    currency = Column(String, nullable=True)


class AuthToken(Base):
    """A one-time link to choose a password: 'reset' (« Mot de passe oublié ? »)
    or 'set' (a validated free trial). Only the SHA-256 of the token is stored,
    so a database dump holds no usable link."""
    __tablename__ = "auth_tokens"

    id = Column(String(36), primary_key=True, default=_new_id)
    user_id = Column(String(36), nullable=False, index=True)
    token_hash = Column(String(64), nullable=False, unique=True)
    purpose = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)

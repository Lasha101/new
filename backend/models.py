# /models.py
import uuid

from sqlalchemy import Boolean, Column, Date, DateTime, Float, Index, Integer, JSON, LargeBinary, String, text
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
    # Added 02/10/2026 (column « Sexe »): 'F' or 'M' as read from the MRZ, NULL
    # when it could not be read. An existing database gains the column through
    # schema_migrations.py.
    sex = Column(String, nullable=True)


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
    # Added 08/10/2026 (invoices): the session's PaymentIntent (pi_…), which a
    # refund event (charge.refunded) names. NULL for purchases paid before.
    stripe_payment_intent = Column(String, nullable=True)
    # Added 09/10/2026 (refunds): when the purchase was refunded IN FULL —
    # « Remboursé le … » in « Mes achats » — and how many credits that took
    # back from the balance (billing.take_back_credits). NULL otherwise.
    refunded_at = Column(DateTime(timezone=True), nullable=True)
    credits_taken_back = Column(Integer, nullable=True)


class Invoice(Base):
    """An invoice, or a credit note (« avoir »), issued by the app for a Stripe
    purchase (Alex, 08/10/2026). Kept as issued: no code path updates or deletes
    a row, and `pdf` is the very file that was sent — never generated again.
    Every mention is also stored in its own column, not only inside the PDF, for
    the electronic invoicing of September 2027. The seller and client blocks are
    copies taken when the document was issued: a later change of the account, or
    its deletion, does not touch them."""
    __tablename__ = "invoices"
    __table_args__ = (
        # One invoice per purchase; a purchase may get several credit notes.
        Index("uq_invoices_one_invoice_per_purchase", "purchase_id", unique=True,
              sqlite_where=text("kind = 'invoice'"), postgresql_where=text("kind = 'invoice'")),
        # A refund already covered by a credit note is never credited twice.
        Index("uq_invoices_one_credit_note_per_refund", "credited_invoice_id", "refunded_cumulative_cents", unique=True,
              sqlite_where=text("kind = 'credit_note'"), postgresql_where=text("kind = 'credit_note'")),
    )

    id = Column(String(36), primary_key=True, default=_new_id)
    # 'invoice' | 'credit_note'
    kind = Column(String, nullable=False)
    # « F-2026-00001 »: `series` (« F-2026 ») and its gapless `sequence`.
    number = Column(String, nullable=False, unique=True)
    series = Column(String, nullable=False)
    sequence = Column(Integer, nullable=False)
    # False: a Stripe test-mode payment, numbered in a TEST- series.
    livemode = Column(Boolean, nullable=False)
    issued_at = Column(DateTime(timezone=True), nullable=False)
    # Calendar dates in Europe/Paris, as printed.
    issue_date = Column(Date, nullable=False)
    service_date = Column(Date, nullable=False)
    payment_date = Column(Date, nullable=False)
    purchase_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), nullable=True, index=True)
    # A credit note: the invoice it credits.
    credited_invoice_id = Column(String(36), nullable=True, index=True)
    credited_invoice_number = Column(String, nullable=True)

    seller_name = Column(String, nullable=False)
    seller_legal_form = Column(String, nullable=False)
    seller_share_capital = Column(String, nullable=False)
    seller_street = Column(String, nullable=False)
    seller_postal_code = Column(String, nullable=False)
    seller_city = Column(String, nullable=False)
    seller_country = Column(String, nullable=False)
    seller_rcs = Column(String, nullable=False)
    seller_siren = Column(String, nullable=False)
    seller_vat_number = Column(String, nullable=False)
    seller_email = Column(String, nullable=False)

    client_name = Column(String, nullable=False)
    client_attention = Column(String, nullable=True)
    client_street = Column(String, nullable=True)
    client_postal_code = Column(String, nullable=True)
    client_city = Column(String, nullable=True)
    # ISO 3166 code (« FR »).
    client_country = Column(String, nullable=True)
    client_siren = Column(String, nullable=True)
    client_vat_number = Column(String, nullable=True)
    client_email = Column(String, nullable=True)

    line_description = Column(String, nullable=False)
    line_quantity = Column(Integer, nullable=False)
    line_unit_price_ht_cents = Column(Integer, nullable=False)
    line_vat_rate_percent = Column(Integer, nullable=False)
    line_total_ht_cents = Column(Integer, nullable=False)
    total_ht_cents = Column(Integer, nullable=False)
    total_vat_cents = Column(Integer, nullable=False)
    total_ttc_cents = Column(Integer, nullable=False)
    currency = Column(String, nullable=False)
    # « Prestation de services ».
    nature = Column(String, nullable=False)
    # « carte bancaire (Stripe) ».
    payment_method = Column(String, nullable=False)

    stripe_session_id = Column(String, nullable=True)
    stripe_payment_intent = Column(String, nullable=True)
    # A credit note: the refunded Charge, and its cumulative refunded amount
    # once this note is counted (what makes a replayed refund issue nothing).
    stripe_charge_id = Column(String, nullable=True)
    refunded_cumulative_cents = Column(Integer, nullable=True)

    pdf = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)


class InvoiceCounter(Base):
    """The last number used in each series (« F-2026 », « AV-2026 »,
    « TEST-F-2026 »…). Raised in the same transaction as the document that
    uses it, so a failure before the commit leaves no gap."""
    __tablename__ = "invoice_counters"

    series = Column(String, primary_key=True)
    last_number = Column(Integer, nullable=False)


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

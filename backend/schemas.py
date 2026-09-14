# /schemas.py
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List, Literal, Optional, Any, Dict
from datetime import date, datetime


class VoyageBase(BaseModel):
    destination: str


class VoyageCreate(VoyageBase):
    passport_ids: List[str] = []


class Voyage(VoyageBase):
    id: str
    user_id: str
    model_config = ConfigDict(from_attributes=True)


class PassportBase(BaseModel):
    """Identity document data. The same schema and fields are used for French
    passports and French national identity cards (CNI); for a CNI the document
    number is stored in `passport_number`."""
    first_name: str
    last_name: str
    birth_date: date
    expiration_date: date
    nationality: str
    passport_number: str
    confidence_score: Optional[float] = None


class PassportCreate(PassportBase):
    destination: Optional[str] = None


class Passport(PassportBase):
    id: str
    owner_id: Optional[str] = None
    # Returned so the edit form can display and update the stored destination.
    destination: Optional[str] = None
    voyages: List[Voyage] = []
    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    user_name: str


class UserCreate(UserBase):
    password: str
    page_credits: Optional[int] = 0
    # Honored only on the admin create endpoint; self-registration builds its
    # UserCreate server-side and never exposes this field.
    role: Literal["user", "admin"] = "user"


class UserRegister(UserBase):
    """Self-registration payload. Deliberately has no `page_credits` field:
    the signup credit amount is fixed server-side."""
    password: str


class BillingIdentity(BaseModel):
    """The invoice fields of an account (« Mon Compte » → Facturation)."""
    company: Optional[str] = None
    siret: Optional[str] = None
    vat_number: Optional[str] = None
    billing_street: Optional[str] = None
    billing_postal_code: Optional[str] = None
    billing_city: Optional[str] = None
    billing_country: Optional[str] = None


class UserUpdate(BillingIdentity):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    user_name: Optional[str] = None
    role: Optional[Literal["user", "admin"]] = None
    password: Optional[str] = None
    uploaded_pages_count: Optional[int] = None
    page_credits: Optional[int] = None


class User(UserBase, BillingIdentity):
    id: str
    role: str
    uploaded_pages_count: int
    page_credits: int = 0
    passports: List["Passport"] = []
    voyages: List[Voyage] = []
    model_config = ConfigDict(from_attributes=True)


class TrialRequestOut(BaseModel):
    id: str
    user_id: Optional[str] = None
    nom: str
    societe: Optional[str] = None
    email: str
    telephone: Optional[str] = None
    volume: Optional[str] = None
    message: Optional[str] = None
    siret: Optional[str] = None
    tva: Optional[str] = None
    status: str
    created_at: datetime
    decided_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class PackSignupRequest(BaseModel):
    """/app/inscription (Spec v3). Plain strings: every rule is checked in the
    endpoint so each refusal can be one French sentence."""
    pack: int
    first_name: str = ""
    last_name: str = ""
    company: str = ""
    email: str = ""
    password: str = ""
    phone_number: str = ""
    billing_street: str = ""
    billing_postal_code: str = ""
    billing_city: str = ""
    billing_country: str = ""
    siret: str = ""
    vat_number: str = ""
    consent: bool = False


class OrderRequest(BaseModel):
    pack: int


class PurchaseOut(BaseModel):
    id: str
    pack: int
    credits: int
    amount_ht_cents: int
    paid_at: datetime
    expires_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class CheckoutOut(BaseModel):
    checkout_url: str
    purchase_id: str


class ForgotPasswordRequest(BaseModel):
    # Email or nom d'utilisateur, whichever the person remembers.
    identifier: str


class ResetPasswordRequest(BaseModel):
    token: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class OcrJob(BaseModel):
    id: str
    user_id: str
    file_name: str
    status: str
    progress: int
    created_at: datetime
    finished_at: Optional[datetime] = None
    successes: List[Dict[str, Any]] = []
    failures: List[Dict[str, Any]] = []
    model_config = ConfigDict(from_attributes=True)


class PassportDeleteMultiple(BaseModel):
    passport_ids: List[str]


class PassportExportSelection(BaseModel):
    passport_ids: List[str]


User.model_rebuild()

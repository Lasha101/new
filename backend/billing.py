# /billing.py
"""Packs, Stripe Payment Links and the Stripe webhook (Spec v3).

Buying a pack: the account is created first (credits 0) with a pending
purchase, then the customer is sent to the pack's Payment Link carrying
?prefilled_email=…&client_reference_id=<user id>. Stripe calls
POST /stripe/webhook when the payment completes; only then are credits added.

Three rules make crediting safe:
- the request is Stripe's: HMAC-SHA256 signature over "<t>.<payload>" with the
  webhook secret, timestamp within STRIPE_WEBHOOK_TOLERANCE_SECONDS;
- the pack is the one PAID FOR, identified by the amount — never the one the
  customer said they wanted;
- a Checkout Session credits at most once: purchases.stripe_session_id is
  UNIQUE and the credit is in the same transaction, so a replay, or two
  deliveries racing each other, add nothing.

« À la carte » (2026-09-30) is the one exception to « identified by the
amount »: its link sells N documents at 1,50 € HT, and N × 1,50 € can equal a
pack's price (66 documents = 99 € = Pack 100). Its sessions are recognised by
their Payment Link instead, before any amount is looked at, and credited with
the quantity bought — see _credit_unit_session. Its buyer needs no account
beforehand (Alex, 03/10/2026): the purchase opens one when there is none yet.

A refund (charge.refunded, Alex, 09/10/2026): when the whole payment is
refunded, the purchase's credits are taken back — never below zero — and the
purchase is marked refunded, once; a partial refund changes nothing. See
take_back_credits.
"""
import calendar
import hashlib
import hmac
import json
import secrets
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote, urlencode

from pydantic import EmailStr, TypeAdapter, ValidationError
from sqlalchemy import func, update as sa_update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import account_tokens
import config
import crud
import models

PAID_EVENTS = ("checkout.session.completed", "checkout.session.async_payment_succeeded")
# A refund, full or partial (its credits: take_back_credits; its credit note:
# invoicing.issue_credit_note).
REFUND_EVENT = "charge.refunded"

# An « à la carte » purchase has no pack: it is stored as pack 0, with the
# number of documents bought in `credits`.
UNIT_PACK = 0
STRIPE_API_BASE = "https://api.stripe.com"
STRIPE_API_TIMEOUT_SECONDS = 10
# Accounts an « à la carte » purchase opens instead of only crediting: a trial
# request still waiting for Alex, or one he refused (users.status).
UNOPENED_STATUSES = ("pending", "rejected")

_EMAIL = TypeAdapter(EmailStr)


def is_known_pack(pack: Any) -> bool:
    return isinstance(pack, int) and not isinstance(pack, bool) and pack in config.PACK_PRICES_HT_CENTS


def price_ttc_cents(pack: int) -> int:
    ht = config.PACK_PRICES_HT_CENTS[pack]
    return ht + ht * config.VAT_RATE_PERCENT // 100


def checkout_url(pack: int, email: str, user_id: str) -> str:
    """The pack's Payment Link with the two parameters Payment Links accept:
    the email pre-filled (read-only at checkout) and our user id, returned to
    us by the webhook."""
    link = config.payment_link(pack)
    separator = "&" if "?" in link else "?"
    return f"{link}{separator}{urlencode({'prefilled_email': email, 'client_reference_id': user_id})}"


def create_pending_purchase(db: Session, user_id: str, pack: int) -> Dict[str, Any]:
    row = models.Purchase(
        user_id=str(user_id), pack=pack, credits=pack,
        amount_ht_cents=config.PACK_PRICES_HT_CENTS[pack], status="pending",
        created_at=datetime.now(timezone.utc),
    )
    db.add(row)
    db.commit()
    return crud._row_to_dict(row)


def paid_purchases(db: Session, user_id: str):
    """« Mes achats »: the account's paid packs, newest first."""
    rows = (db.query(models.Purchase)
            .filter(models.Purchase.user_id == str(user_id), models.Purchase.status == "paid")
            .order_by(models.Purchase.paid_at.desc())
            .all())
    return [crud._row_to_dict(row) for row in rows]


def add_months(value: datetime, months: int) -> datetime:
    month_index = value.month - 1 + months
    year, month = value.year + month_index // 12, month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


def verify_signature(payload: bytes, header: str, secret: str, now: Optional[float] = None) -> bool:
    """Stripe's scheme: header "t=<unix>,v1=<hex>[,v1=…]"."""
    if not secret or not header:
        return False
    timestamp, signatures = None, []
    for part in header.split(","):
        key, _, value = part.strip().partition("=")
        if key == "t":
            timestamp = value
        elif key == "v1":
            signatures.append(value)
    if not timestamp or not signatures:
        return False
    try:
        issued = int(timestamp)
    except ValueError:
        return False
    if abs((time.time() if now is None else now) - issued) > config.STRIPE_WEBHOOK_TOLERANCE_SECONDS:
        return False
    expected = hmac.new(secret.encode("utf-8"), f"{timestamp}.".encode("utf-8") + payload, hashlib.sha256).hexdigest()
    return any(hmac.compare_digest(expected, candidate) for candidate in signatures)


def identify_pack(session: Dict[str, Any]) -> Optional[int]:
    """The pack whose price was paid: the HT subtotal, or the total HT or TTC."""
    if str(session.get("currency") or "").lower() != "eur":
        return None
    subtotal, total = session.get("amount_subtotal"), session.get("amount_total")
    for pack, ht in config.PACK_PRICES_HT_CENTS.items():
        if subtotal == ht or total in (ht, price_ttc_cents(pack)):
            return pack
    return None


@dataclass
class CreditOutcome:
    status: str                      # credited | duplicate | not_paid | unmatched
    reason: str = ""
    user: Optional[Dict[str, Any]] = None
    pack: Optional[int] = None
    expires_at: Optional[datetime] = None
    credits: Optional[int] = None    # « à la carte »: the documents bought
    # « à la carte »: the purchase opened the account — the raw one-time link to
    # choose its password, for the welcome e-mail only (never stored as is).
    password_token: Optional[str] = None
    purchase_id: Optional[str] = None  # the paid purchase (its invoice: invoicing.py)


class StripeApiError(Exception):
    """The line items of a session could not be read — worded for Alex."""


class UnmatchedPayment(Exception):
    """An « à la carte » payment whose account cannot be established for
    certain — worded for Alex's anomaly e-mail."""


def is_unit_session(session: Dict[str, Any]) -> bool:
    """Paid through the « à la carte » Payment Link."""
    link_id = config.stripe_unit_payment_link_id()
    return bool(link_id) and session.get("payment_link") == link_id


def fetch_line_items(session_id: str) -> List[Dict[str, Any]]:
    """GET /v1/checkout/sessions/{id}/line_items. A webhook payload never
    carries the line items, so the quantity bought has to be asked for."""
    key = config.stripe_api_key()
    if not key:
        raise StripeApiError("clé API Stripe non configurée (STRIPE_API_KEY)")
    url = f"{STRIPE_API_BASE}/v1/checkout/sessions/{quote(str(session_id), safe='')}/line_items?limit=100"
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(request, timeout=STRIPE_API_TIMEOUT_SECONDS) as response:
            body = json.load(response)
    except urllib.error.HTTPError as exc:
        raise StripeApiError(f"l'API Stripe a répondu {exc.code} à la lecture des articles") from None
    except (OSError, ValueError):
        raise StripeApiError("API Stripe injoignable, ou sa réponse est illisible") from None
    items = body.get("data") if isinstance(body, dict) else None
    if not isinstance(items, list):
        raise StripeApiError("la réponse de l'API Stripe ne contient pas les articles")
    return items


def session_for_payment_intent(payment_intent: str) -> Optional[str]:
    """GET /v1/checkout/sessions?payment_intent=… — the Checkout Session a
    payment was made through (None when Stripe knows none). A purchase paid
    before 08/10/2026 did not keep its PaymentIntent, so a refund, which names
    only the PaymentIntent, finds it through its session."""
    key = config.stripe_api_key()
    if not key:
        raise StripeApiError("clé API Stripe non configurée (STRIPE_API_KEY)")
    url = f"{STRIPE_API_BASE}/v1/checkout/sessions?{urlencode({'payment_intent': payment_intent, 'limit': 1})}"
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(request, timeout=STRIPE_API_TIMEOUT_SECONDS) as response:
            body = json.load(response)
    except urllib.error.HTTPError as exc:
        raise StripeApiError(f"l'API Stripe a répondu {exc.code} à la recherche de la session") from None
    except (OSError, ValueError):
        raise StripeApiError("API Stripe injoignable, ou sa réponse est illisible") from None
    sessions = body.get("data") if isinstance(body, dict) else None
    if not isinstance(sessions, list):
        raise StripeApiError("la réponse de l'API Stripe ne contient pas les sessions")
    first = sessions[0] if sessions and isinstance(sessions[0], dict) else {}
    return str(first["id"]) if first.get("id") else None


def unit_quantity(items: List[Dict[str, Any]]) -> Optional[int]:
    """The documents bought: the quantity of the link's one line item."""
    if len(items) != 1 or not isinstance(items[0], dict):
        return None
    quantity = items[0].get("quantity")
    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 1:
        return None
    return quantity


def unit_buyer(db: Session, session: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], str]:
    """(account, e-mail) an « à la carte » payment is for; the account is None
    when the purchase must open a new one. Reads only — nothing is written here.

    The app's own link carries client_reference_id (the account's id), so the
    right account is credited whatever e-mail was typed. The site's plain link
    does not: the e-mail typed at checkout names the account, whatever the
    letter case (Alex, 03/10/2026)."""
    user_id = session.get("client_reference_id")
    if user_id:
        user = crud.get_user(db, str(user_id))
        if user is None:
            raise UnmatchedPayment("à la carte : client_reference_id ne correspond à aucun compte ScanID")
        return user, user["email"]
    typed = ((session.get("customer_details") or {}).get("email") or session.get("customer_email") or "").strip()
    if not typed:
        raise UnmatchedPayment("à la carte : le paiement ne porte aucune adresse e-mail")
    try:
        email = str(_EMAIL.validate_python(typed)).lower()
    except ValidationError:
        raise UnmatchedPayment("à la carte : l'adresse e-mail du paiement n'est pas valide") from None
    rows = db.query(models.User).filter(func.lower(models.User.email) == email).limit(2).all()
    if len(rows) > 1:
        raise UnmatchedPayment("à la carte : plusieurs comptes ScanID ont cette adresse e-mail")
    if rows:
        return crud._row_to_dict(rows[0]), email
    if db.query(models.User).filter(func.lower(models.User.user_name) == email).first() is not None:
        # Every account logs in with its e-mail; this one cannot be created.
        raise UnmatchedPayment("à la carte : cette adresse e-mail est l'identifiant d'un autre compte ScanID")
    return None, email


def checkout_identity(session: Dict[str, Any]) -> Dict[str, Any]:
    """What the « à la carte » page asks besides the e-mail — the full name, the
    business name and the phone — for an account the purchase creates. The name
    is split at its first space, as a trial request's « nom » is."""
    details = session.get("customer_details") or {}
    collected = session.get("collected_information") or {}
    full_name = str(details.get("individual_name") or collected.get("individual_name") or details.get("name") or "").strip()
    first_name, _, last_name = full_name.partition(" ")
    company = str(details.get("business_name") or collected.get("business_name") or "").strip()
    return {"first_name": first_name, "last_name": last_name.strip(), "company": company or None,
            "phone_number": str(details.get("phone") or "").strip()}


def payment_intent_id(session: Dict[str, Any]) -> Optional[str]:
    """The session's PaymentIntent id (pi_…) — an id, or the object when expanded."""
    value = session.get("payment_intent")
    if isinstance(value, dict):
        value = value.get("id")
    return str(value) if value else None


def already_processed(db: Session, session_id: str) -> bool:
    """The cheap check. The UNIQUE constraint below is the guarantee."""
    return db.query(models.Purchase).filter(models.Purchase.stripe_session_id == session_id).first() is not None


def credit_checkout_session(db: Session, session: Dict[str, Any]) -> CreditOutcome:
    session_id = session.get("id")
    if not session_id:
        return CreditOutcome("unmatched", reason="session sans identifiant")
    if session.get("payment_status") != "paid":
        # e.g. a bank transfer not received yet: async_payment_succeeded follows.
        return CreditOutcome("not_paid")
    if already_processed(db, session_id):
        return CreditOutcome("duplicate")
    if is_unit_session(session):
        return _credit_unit_session(db, session)

    pack = identify_pack(session)
    if pack is None:
        return CreditOutcome("unmatched", reason="le montant payé ne correspond à aucun pack")
    user_id = session.get("client_reference_id")
    user = crud.get_user(db, str(user_id)) if user_id else None
    if user is None:
        return CreditOutcome("unmatched", reason="client_reference_id absent ou inconnu")

    now = datetime.now(timezone.utc)
    expires_at = add_months(now, config.CREDIT_VALIDITY_MONTHS)
    paid = {"status": "paid", "paid_at": now, "expires_at": expires_at, "stripe_session_id": session_id,
            "amount_paid_cents": session.get("amount_total"), "currency": str(session.get("currency")).lower(),
            "stripe_payment_intent": payment_intent_id(session)}
    try:
        pending = (db.query(models.Purchase)
                   .filter(models.Purchase.user_id == user["id"], models.Purchase.pack == pack,
                           models.Purchase.status == "pending")
                   .order_by(models.Purchase.created_at.desc())
                   .first())
        matched, purchase_id = 0, None
        if pending is not None:
            # Conditional: a delivery racing this one finds the row already paid
            # (rowcount 0) and falls through to the INSERT, which the UNIQUE
            # session id then refuses.
            matched = db.execute(
                sa_update(models.Purchase)
                .where(models.Purchase.id == pending.id, models.Purchase.status == "pending")
                .values(**paid)
            ).rowcount
            purchase_id = pending.id
        if not matched:
            row = models.Purchase(user_id=user["id"], pack=pack, credits=pack,
                                  amount_ht_cents=config.PACK_PRICES_HT_CENTS[pack], created_at=now, **paid)
            db.add(row)
            db.flush()
            purchase_id = row.id
        db.execute(
            sa_update(models.User)
            .where(models.User.id == user["id"])
            .values(page_credits=func.coalesce(models.User.page_credits, 0) + pack)
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        return CreditOutcome("duplicate")
    return CreditOutcome("credited", user=crud.get_user(db, user["id"]), pack=pack, expires_at=expires_at,
                         purchase_id=purchase_id)


def _credit_unit_session(db: Session, session: Dict[str, Any]) -> CreditOutcome:
    """« À la carte »: the quantity of the session's line item, credited once
    (Alex, 03/10/2026). The checkout e-mail's account is credited when it is
    open; otherwise the purchase opens it — no account yet, a trial request
    still waiting, or one Alex refused — with the documents bought only, and a
    link to choose its password goes to that address. A purchase never touches
    the e-mail or the password of an open account, and never logs anyone in.

    The account and the quantity are both established before anything is
    written; whatever cannot be established for certain is reported to Alex
    rather than guessed."""
    if str(session.get("currency") or "").lower() != "eur":
        return CreditOutcome("unmatched", reason="à la carte : paiement dans une autre devise que l'euro")
    try:
        user, email = unit_buyer(db, session)
    except UnmatchedPayment as exc:
        return CreditOutcome("unmatched", reason=str(exc))
    try:
        quantity = unit_quantity(fetch_line_items(session["id"]))
    except StripeApiError as exc:
        return CreditOutcome("unmatched", reason=f"à la carte : {exc}")
    if quantity is None:
        return CreditOutcome("unmatched", reason="à la carte : la session ne porte pas un seul article avec sa quantité")

    for attempt in (1, 2):
        try:
            return _write_unit_purchase(db, session, user, email, quantity)
        except IntegrityError:
            db.rollback()
            if already_processed(db, session["id"]):
                return CreditOutcome("duplicate")
            if attempt == 2:
                raise   # 500: Stripe delivers again later; nothing was written
            # The account was created meanwhile (another payment from the same
            # new address): look again — it now exists and is credited.
            try:
                user, email = unit_buyer(db, session)
            except UnmatchedPayment as exc:
                return CreditOutcome("unmatched", reason=str(exc))


def _write_unit_purchase(db: Session, session: Dict[str, Any], user: Optional[Dict[str, Any]],
                         email: str, quantity: int) -> CreditOutcome:
    """One transaction: the account (created or opened if need be), the paid
    purchase, the credits and — for an account this purchase opens — its
    password link. The UNIQUE session id makes a replay roll all of it back."""
    now = datetime.now(timezone.utc)
    expires_at = add_months(now, config.CREDIT_VALIDITY_MONTHS)
    if user is None:
        identity = checkout_identity(session)
        row = models.User(
            first_name=identity["first_name"], last_name=identity["last_name"], email=email,
            phone_number=identity["phone_number"], user_name=email, company=identity["company"],
            # Not a hash of anything: no password can match it until the
            # owner of the address chooses one through the e-mailed link.
            hashed_password=f"!unit-purchase-{secrets.token_hex(8)}",
            role="user", uploaded_pages_count=0, page_credits=quantity, status="active",
        )
        db.add(row)
        db.flush()
        user_id, opened = row.id, True
    else:
        user_id, opened = user["id"], False
    purchase = models.Purchase(
        user_id=user_id, pack=UNIT_PACK, credits=quantity,
        amount_ht_cents=quantity * config.UNIT_PRICE_HT_CENTS, created_at=now,
        status="paid", paid_at=now, expires_at=expires_at, stripe_session_id=session["id"],
        amount_paid_cents=session.get("amount_total"), currency="eur",
        stripe_payment_intent=payment_intent_id(session),
    )
    db.add(purchase)
    db.flush()
    if user is not None:
        if user.get("status") in UNOPENED_STATUSES:
            # Conditional: if another payment or /signup opened it meanwhile, the
            # documents are added below instead. The trial's provisional credits
            # are not given by a purchase — Alex's « Valider » adds them.
            opened = db.execute(
                sa_update(models.User)
                .where(models.User.id == user_id, models.User.status == user["status"])
                .values(status="active", page_credits=quantity)
            ).rowcount == 1
        if not opened:
            db.execute(
                sa_update(models.User)
                .where(models.User.id == user_id)
                .values(page_credits=func.coalesce(models.User.page_credits, 0) + quantity)
            )
    token = account_tokens.add(db, user_id, account_tokens.PURPOSE_SET) if opened else None
    db.commit()
    return CreditOutcome("credited", user=crud.get_user(db, user_id), pack=UNIT_PACK,
                         expires_at=expires_at, credits=quantity, password_token=token,
                         purchase_id=purchase.id)


# --- Refunds (charge.refunded, Alex, 09/10/2026) ---------------------------------

@dataclass
class RefundOutcome:
    status: str                      # taken_back | partial | duplicate | unmatched | error
    reason: str = ""
    purchase: Optional[Dict[str, Any]] = None
    user: Optional[Dict[str, Any]] = None   # the account (None once deleted)
    taken: int = 0                          # the credits a full refund removed from its balance


def _refunded_purchase(db: Session, payment_intent: str) -> Tuple[Optional[str], str]:
    """The id of the paid purchase a refund's PaymentIntent belongs to, or None
    and why. A purchase paid before 08/10/2026 is found through its Checkout
    Session, and keeps the PaymentIntent from then on — the credit note of the
    same refund finds it too."""
    found = (db.query(models.Purchase.id)
             .filter(models.Purchase.stripe_payment_intent == payment_intent, models.Purchase.status == "paid")
             .first())
    if found is not None:
        return found.id, ""
    unknown = "aucun achat ScanID ne correspond à ce paiement"
    try:
        session_id = session_for_payment_intent(payment_intent)
    except StripeApiError as exc:
        return None, f"{unknown} (Stripe n'a pas pu être interrogé : {exc})"
    if session_id:
        db.execute(
            sa_update(models.Purchase)
            .where(models.Purchase.stripe_session_id == session_id, models.Purchase.status == "paid",
                   models.Purchase.stripe_payment_intent.is_(None))
            .values(stripe_payment_intent=payment_intent)
        )
        db.commit()
        found = (db.query(models.Purchase.id)
                 .filter(models.Purchase.stripe_payment_intent == payment_intent, models.Purchase.status == "paid")
                 .first())
        if found is not None:
            return found.id, ""
    return None, f"{unknown} (payé hors de l'application, ou enregistré à la main)"


def take_back_credits(db: Session, charge: Dict[str, Any], refunded_at: datetime) -> RefundOutcome:
    """A FULL refund — Stripe's `refunded`: the whole payment, refunded at once
    or by the refund that completes it — takes the purchase's credits back from
    the balance. The balance is one counter, so it takes as many as are left,
    never going below zero (100 bought, 30 used: the 70 left). The purchase is
    marked refunded in the same transaction, which makes it happen once. A
    partial refund changes nothing: the caller tells Alex."""
    payment_intent = payment_intent_id(charge)
    if not payment_intent:
        return RefundOutcome("unmatched", reason="le remboursement ne porte pas de paiement Stripe lisible")
    purchase_id, reason = _refunded_purchase(db, payment_intent)
    if purchase_id is None:
        return RefundOutcome("unmatched", reason=reason)
    # Locked until the commit: the same refund delivered twice at once waits,
    # then finds the purchase marked (populate_existing: read it again).
    purchase = (db.query(models.Purchase).filter(models.Purchase.id == purchase_id)
                .with_for_update().populate_existing().one())
    if purchase.refunded_at is not None or charge.get("refunded") is not True:
        row = crud._row_to_dict(purchase)
        db.rollback()
        if row["refunded_at"] is not None:
            return RefundOutcome("duplicate", purchase=row)
        return RefundOutcome("partial", purchase=row, user=crud.get_user(db, row["user_id"]))
    user = (db.query(models.User).filter(models.User.id == purchase.user_id)
            .with_for_update().populate_existing().first())
    balance = (user.page_credits or 0) if user is not None else 0
    taken = min(purchase.credits, max(balance, 0))
    if taken:
        user.page_credits = balance - taken   # the row is locked: the balance read is the balance
    purchase.refunded_at, purchase.credits_taken_back = refunded_at, taken
    db.commit()
    return RefundOutcome("taken_back", purchase=crud._row_to_dict(purchase), user=crud._row_to_dict(user),
                         taken=taken)

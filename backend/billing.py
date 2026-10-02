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
the quantity bought — see _credit_unit_session.
"""
import calendar
import hashlib
import hmac
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import quote, urlencode

from sqlalchemy import func, update as sa_update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import config
import crud
import models

PAID_EVENTS = ("checkout.session.completed", "checkout.session.async_payment_succeeded")

# An « à la carte » purchase has no pack: it is stored as pack 0, with the
# number of documents bought in `credits`.
UNIT_PACK = 0
STRIPE_API_BASE = "https://api.stripe.com"
STRIPE_API_TIMEOUT_SECONDS = 10


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


class StripeApiError(Exception):
    """The line items of a session could not be read — worded for Alex."""


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


def unit_quantity(items: List[Dict[str, Any]]) -> Optional[int]:
    """The documents bought: the quantity of the link's one line item."""
    if len(items) != 1 or not isinstance(items[0], dict):
        return None
    quantity = items[0].get("quantity")
    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 1:
        return None
    return quantity


def unit_buyer(db: Session, session: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """The account an « à la carte » payment is for. The link is a plain link
    on the site, so there is usually no client_reference_id: the e-mail typed
    at checkout names the account — exactly one, whatever the letter case."""
    user_id = session.get("client_reference_id")
    if user_id:
        return crud.get_user(db, str(user_id))
    email = ((session.get("customer_details") or {}).get("email") or session.get("customer_email") or "").strip()
    if not email:
        return None
    rows = db.query(models.User).filter(func.lower(models.User.email) == email.lower()).limit(2).all()
    return crud._row_to_dict(rows[0]) if len(rows) == 1 else None


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
            "amount_paid_cents": session.get("amount_total"), "currency": str(session.get("currency")).lower()}
    try:
        pending = (db.query(models.Purchase)
                   .filter(models.Purchase.user_id == user["id"], models.Purchase.pack == pack,
                           models.Purchase.status == "pending")
                   .order_by(models.Purchase.created_at.desc())
                   .first())
        matched = 0
        if pending is not None:
            # Conditional: a delivery racing this one finds the row already paid
            # (rowcount 0) and falls through to the INSERT, which the UNIQUE
            # session id then refuses.
            matched = db.execute(
                sa_update(models.Purchase)
                .where(models.Purchase.id == pending.id, models.Purchase.status == "pending")
                .values(**paid)
            ).rowcount
        if not matched:
            db.add(models.Purchase(user_id=user["id"], pack=pack, credits=pack,
                                   amount_ht_cents=config.PACK_PRICES_HT_CENTS[pack], created_at=now, **paid))
            db.flush()
        db.execute(
            sa_update(models.User)
            .where(models.User.id == user["id"])
            .values(page_credits=func.coalesce(models.User.page_credits, 0) + pack)
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        return CreditOutcome("duplicate")
    return CreditOutcome("credited", user=crud.get_user(db, user["id"]), pack=pack, expires_at=expires_at)


def _credit_unit_session(db: Session, session: Dict[str, Any]) -> CreditOutcome:
    """« À la carte »: the quantity of the session's line item, credited once.
    Whatever cannot be established for certain — the account, the quantity —
    is reported to Alex rather than guessed."""
    if str(session.get("currency") or "").lower() != "eur":
        return CreditOutcome("unmatched", reason="à la carte : paiement dans une autre devise que l'euro")
    user = unit_buyer(db, session)
    if user is None:
        return CreditOutcome("unmatched", reason="à la carte : aucun compte ScanID unique pour ce client (client_reference_id ou e-mail)")
    if user.get("status") == "rejected":
        return CreditOutcome("unmatched", reason="à la carte : le compte de ce client a été refusé")
    try:
        quantity = unit_quantity(fetch_line_items(session["id"]))
    except StripeApiError as exc:
        return CreditOutcome("unmatched", reason=f"à la carte : {exc}")
    if quantity is None:
        return CreditOutcome("unmatched", reason="à la carte : la session ne porte pas un seul article avec sa quantité")

    now = datetime.now(timezone.utc)
    expires_at = add_months(now, config.CREDIT_VALIDITY_MONTHS)
    try:
        db.add(models.Purchase(
            user_id=user["id"], pack=UNIT_PACK, credits=quantity,
            amount_ht_cents=quantity * config.UNIT_PRICE_HT_CENTS, created_at=now,
            status="paid", paid_at=now, expires_at=expires_at, stripe_session_id=session["id"],
            amount_paid_cents=session.get("amount_total"), currency="eur",
        ))
        db.flush()
        db.execute(
            sa_update(models.User)
            .where(models.User.id == user["id"])
            .values(page_credits=func.coalesce(models.User.page_credits, 0) + quantity)
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        return CreditOutcome("duplicate")
    return CreditOutcome("credited", user=crud.get_user(db, user["id"]), pack=UNIT_PACK,
                         expires_at=expires_at, credits=quantity)

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
"""
import calendar
import hashlib
import hmac
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from urllib.parse import urlencode

from sqlalchemy import func, update as sa_update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import config
import crud
import models

PAID_EVENTS = ("checkout.session.completed", "checkout.session.async_payment_succeeded")


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

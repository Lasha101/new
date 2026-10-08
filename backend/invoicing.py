# /invoicing.py
"""Invoices issued by the app (Alex, « Invoices issued by the app », 08/10/2026).

Every purchase the Stripe webhook credits gets one French invoice, as a PDF and
as data: each mention is also stored in its own column of `invoices`, because
the electronic invoicing of September 2027 will be built from the data, not
from the PDF.

Four rules:
- nothing happens until INVOICES_ENABLED is set (config.invoices_enabled): no
  number is used before Alex's accountant has validated the sample;
- one chronological, continuous series per kind of document and per year
  (F-2026-00001…): the number comes from `invoice_counters` in the same
  transaction as the document, so a failure before the commit leaves no gap; a
  Stripe test-mode payment is numbered in its own TEST- series;
- automatic only for a billing address in France, and only when the TTC computed
  from the app's prices is the amount paid; otherwise nothing is issued and the
  caller tells Alex (other VAT rules, or a price that is not the app's);
- kept as issued: a document is written once, with its PDF, and is never
  updated, deleted or rendered again.
"""
import html
import re
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

import fitz  # PyMuPDF
from sqlalchemy import update as sa_update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, defer

import billing
import billing_identity
import config
import crud
import models

PARIS = ZoneInfo("Europe/Paris")
NBSP = " "   # French digit grouping and the space before « : » (the PDF's font has no U+202F)

KIND_INVOICE = "invoice"
KIND_CREDIT_NOTE = "credit_note"
# « F-2026-00001 »: the prefix, the year of the document's date, 5 digits. The
# accountant chooses the final format before go-live (Alex, §2) — here only.
NUMBER_PREFIXES = {KIND_INVOICE: "F", KIND_CREDIT_NOTE: "AV"}
TEST_PREFIX = "TEST-"
SEQUENCE_DIGITS = 5

# The seller block — Alex's §2, the words of the CGV article 2.
SELLER = {
    "seller_name": "ScanID",
    "seller_legal_form": "SASU",
    "seller_share_capital": f"1{NBSP}000{NBSP}€",
    "seller_street": "169 avenue de Choisy",
    "seller_postal_code": "75013",
    "seller_city": "Paris",
    "seller_country": "FR",
    "seller_rcs": "RCS Paris 107 858 557",
    "seller_siren": "107858557",
    "seller_vat_number": "FR76107858557",
    "seller_email": "contact@scanid.fr",
}
NATURE = "Prestation de services"
PAYMENT_METHOD = "carte bancaire (Stripe)"
DISCOUNT_TERMS = f"Escompte pour paiement anticipé{NBSP}: néant"
# Waits for Alex's accountant: the CGV say « taux légal » (Alex's lawyer checks).
LATE_PAYMENT_TERMS = (f"Pénalités de retard{NBSP}: taux de la BCE majoré de 10 points{NBSP}; indemnité forfaitaire "
                      f"pour frais de recouvrement{NBSP}: 40{NBSP}€ (art. L441-10 du Code de commerce)")
TEST_MODE_BANNER = "SPÉCIMEN — paiement Stripe en mode test, sans valeur comptable"

_FRANCE = {"fr", "fra", "france", "france metropolitaine", "republique francaise"}
_FRENCH_VAT = re.compile(r"FR([0-9]{2})([0-9]{9})")


# --- French formats ------------------------------------------------------------

def to_paris(value: datetime) -> datetime:
    """A stored instant in Paris time (SQLite gives naive UTC datetimes back)."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(PARIS)


def date_fr(value: date) -> str:
    return f"{value.day:02d}/{value.month:02d}/{value.year:04d}"


def count_fr(value: int) -> str:
    """« 1 000 » — the way the site writes the packs."""
    return f"{value:,}".replace(",", NBSP)


def euros(cents: int) -> str:
    """« 1 234,56 € »."""
    sign = "-" if cents < 0 else ""
    whole, rest = divmod(abs(cents), 100)
    return f"{sign}{count_fr(whole)},{rest:02d}{NBSP}€"


def siren_fr(siren: str) -> str:
    """« 107 858 557 »."""
    return NBSP.join((siren[0:3], siren[3:6], siren[6:9]))


def vat_cents(total_ht_cents: int) -> int:
    """20 % of the total HT, rounded half up to the cent (Alex: VAT computed on
    the invoice's total HT)."""
    return int((Decimal(total_ht_cents) * config.VAT_RATE_PERCENT / 100).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def country_code(value: Optional[str]) -> Optional[str]:
    """« FR » for the ways France is written (« France », « FR », any case or
    accents); any other country as typed; None when empty."""
    text = (value or "").strip()
    if not text:
        return None
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return "FR" if " ".join(plain.replace("-", " ").split()) in _FRANCE else text


# --- What the invoice says ------------------------------------------------------

def _siren(siret: Optional[str], vat_number: Optional[str]) -> Optional[str]:
    """The first 9 digits of the SIRET; otherwise the SIREN inside a French VAT
    number (FR + 2-digit key + SIREN, the key checked); otherwise None."""
    siret = billing_identity.normalize_siret(siret)
    if billing_identity.is_valid_siret(siret):
        return siret[:9]
    match = _FRENCH_VAT.fullmatch(billing_identity.normalize_vat(vat_number))
    if match and int(match.group(1)) == (12 + 3 * (int(match.group(2)) % 97)) % 97:
        return match.group(2)
    return None


def client_block(user: Dict[str, Any], session: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """Who the invoice is made out to: the account's « Facturation » fields
    first (typed at /app/inscription or in « Mon compte »), the details typed
    on Stripe's page when the account lacks them — a unit buyer whose account
    the purchase opened has no address in the app. An address is taken whole
    from one side, never mixed."""
    details = session.get("customer_details") or {}
    stripe_address = details.get("address") or {}
    tax_ids = details.get("tax_ids") or []
    stripe_vat = next((str(t.get("value") or "") for t in tax_ids if isinstance(t, dict) and t.get("type") == "eu_vat"), "")
    stripe_person = str(details.get("individual_name") or details.get("name") or "").strip()
    person = f"{user.get('first_name') or ''} {user.get('last_name') or ''}".strip() or stripe_person

    account_address = [str(user.get(f) or "").strip()
                       for f in ("billing_street", "billing_postal_code", "billing_city", "billing_country")]
    if all(account_address):
        street, postal_code, city, country = account_address[0], account_address[1], account_address[2], country_code(account_address[3])
    else:
        lines = [str(stripe_address.get(k) or "").strip() for k in ("line1", "line2")]
        street = ", ".join(line for line in lines if line) or None
        postal_code = str(stripe_address.get("postal_code") or "").strip() or None
        city = str(stripe_address.get("city") or "").strip() or None
        country = country_code(stripe_address.get("country"))

    name = (str(user.get("company") or "").strip() or str(details.get("business_name") or "").strip()
            or stripe_person or person or str(user.get("email") or ""))
    vat_number = billing_identity.normalize_vat(user.get("vat_number")) or billing_identity.normalize_vat(stripe_vat) or None
    return {
        "client_name": name,
        "client_attention": person if person and person != name else None,
        "client_street": street, "client_postal_code": postal_code, "client_city": city,
        "client_country": country,
        "client_siren": _siren(user.get("siret"), vat_number),
        "client_vat_number": vat_number,
        "client_email": user.get("email"),
    }


def invoice_line(purchase: models.Purchase) -> Dict[str, Any]:
    """The purchase's one line, priced from the app's own price list."""
    until = date_fr(to_paris(purchase.expires_at).date())
    if purchase.pack == billing.UNIT_PACK:
        quantity, unit_price = purchase.credits, config.UNIT_PRICE_HT_CENTS
        description = (f"Document à l’unité (passeport ou CNI française), crédit valable "
                       f"{config.CREDIT_VALIDITY_MONTHS} mois, jusqu’au {until}")
    else:
        quantity, unit_price = 1, config.PACK_PRICES_HT_CENTS[purchase.pack]
        description = (f"Pack {count_fr(purchase.pack)} — {count_fr(purchase.pack)} documents (passeports ou CNI "
                       f"françaises), crédits valables {config.CREDIT_VALIDITY_MONTHS} mois, jusqu’au {until}")
    total_ht = quantity * unit_price
    vat = vat_cents(total_ht)
    return {
        "line_description": description, "line_quantity": quantity, "line_unit_price_ht_cents": unit_price,
        "line_vat_rate_percent": config.VAT_RATE_PERCENT, "line_total_ht_cents": total_ht,
        "total_ht_cents": total_ht, "total_vat_cents": vat, "total_ttc_cents": total_ht + vat, "currency": "EUR",
    }


def refusal(client: Dict[str, Any], session: Dict[str, Any], amounts: Dict[str, Any]) -> Optional[str]:
    """Why this invoice may not be issued automatically (worded for Alex's
    e-mail), or None."""
    country = client.get("client_country")
    if country != "FR":
        return (f"pays de facturation hors de France ({country or 'non renseigné'}) : "
                "autres règles de TVA, facture à établir à la main")
    typed = (((session.get("customer_details") or {}).get("address") or {}).get("country") or "").strip()
    if typed and typed.upper() != "FR":
        return (f"pays de l'adresse saisie sur Stripe : {typed} (hors de France) : "
                "autres règles de TVA, facture à établir à la main")
    if str(session.get("currency") or "").lower() != "eur":
        return "paiement dans une autre devise que l'euro"
    paid = session.get("amount_total")
    if paid != amounts["total_ttc_cents"]:
        shown = euros(paid) if isinstance(paid, int) and not isinstance(paid, bool) else "inconnu"
        return (f"le montant payé ({shown}) n'est pas le total TTC calculé avec les prix de l'application "
                f"({euros(amounts['total_ttc_cents'])})")
    return None


# --- Numbering and writing -------------------------------------------------------

class _YearChanged(Exception):
    """New Year's midnight passed while the number was being taken: start again
    in the new year's series."""


def series_for(kind: str, year: int, livemode: bool) -> str:
    return f"{'' if livemode else TEST_PREFIX}{NUMBER_PREFIXES[kind]}-{year}"


def _next_sequence(db: Session, series: str) -> int:
    """Raises the series' counter in the caller's transaction (PostgreSQL locks
    the row until the commit: two documents never get the same number, and a
    rollback gives the number back)."""
    raised = db.execute(
        sa_update(models.InvoiceCounter)
        .where(models.InvoiceCounter.series == series)
        .values(last_number=models.InvoiceCounter.last_number + 1)
    ).rowcount
    if raised:
        return db.query(models.InvoiceCounter.last_number).filter(models.InvoiceCounter.series == series).scalar()
    db.add(models.InvoiceCounter(series=series, last_number=1))
    db.flush()   # the series' first document: a racing one makes this fail, and the caller starts again
    return 1


def _write(db: Session, kind: str, livemode: bool, fields: Dict[str, Any]) -> models.Invoice:
    """Numbers, renders and stores one document, then commits. The date is
    read once the counter is held, so numbers and dates stay in order."""
    year = datetime.now(PARIS).year
    series = series_for(kind, year, livemode)
    sequence = _next_sequence(db, series)
    issued_at = datetime.now(timezone.utc)
    issue_date = to_paris(issued_at).date()
    if issue_date.year != year:
        raise _YearChanged()
    # The seller block and the nature: today's, unless the caller copies them
    # (a credit note repeats its invoice's blocks).
    document = dict(SELLER, nature=NATURE)
    document.update(fields)
    document.update(kind=kind, livemode=livemode, series=series, sequence=sequence,
                    number=f"{series}-{sequence:0{SEQUENCE_DIGITS}d}", issued_at=issued_at, issue_date=issue_date,
                    created_at=issued_at)
    row = models.Invoice(**document, pdf=render_pdf(document, banner=None if livemode else TEST_MODE_BANNER))
    db.add(row)
    db.flush()
    db.commit()
    return row


@dataclass
class InvoiceOutcome:
    status: str                       # issued | refused | disabled
    reason: str = ""
    invoice: Optional[models.Invoice] = None


def issue_invoice(db: Session, purchase_id: str, session: Dict[str, Any]) -> InvoiceOutcome:
    """The invoice of a purchase the webhook has just credited (its own
    transaction: the credits are already committed, whatever happens here).
    Raises on an unexpected failure — nothing is then stored, no number used."""
    if not config.invoices_enabled():
        return InvoiceOutcome("disabled")
    purchase = db.get(models.Purchase, purchase_id)
    user = crud.get_user(db, purchase.user_id) if purchase is not None else None
    if purchase is None or user is None or purchase.status != "paid":
        return InvoiceOutcome("refused", reason="achat ou compte introuvable")
    client = client_block(user, session)
    amounts = invoice_line(purchase)
    reason = refusal(client, session, amounts)
    if reason:
        return InvoiceOutcome("refused", reason=reason)
    paid_on = to_paris(purchase.paid_at).date()
    fields = dict(client, **amounts, purchase_id=purchase.id, user_id=purchase.user_id,
                  service_date=paid_on, payment_date=paid_on, payment_method=PAYMENT_METHOD,
                  stripe_session_id=purchase.stripe_session_id, stripe_payment_intent=purchase.stripe_payment_intent)
    for attempt in range(3):
        try:
            return InvoiceOutcome("issued", invoice=_write(db, KIND_INVOICE, session.get("livemode") is True, fields))
        except (IntegrityError, _YearChanged):
            db.rollback()
            existing = (db.query(models.Invoice)
                        .filter(models.Invoice.purchase_id == purchase.id, models.Invoice.kind == KIND_INVOICE)
                        .first())
            if existing is not None:
                return InvoiceOutcome("issued", invoice=existing)
            if attempt == 2:
                raise
        except Exception:
            db.rollback()   # the number taken is given back with everything else
            raise


# --- Credit notes (« avoirs ») -----------------------------------------------------
# An issued invoice is never cancelled: a refund, full or partial, gets a credit
# note of its own series for the amount refunded (Alex, §3).
_COPIED_FROM_INVOICE = ("nature", "payment_method", "purchase_id", "user_id", "service_date", "stripe_session_id",
                        "stripe_payment_intent", "currency") + tuple(SELLER) + (
    "client_name", "client_attention", "client_street", "client_postal_code", "client_city", "client_country",
    "client_siren", "client_vat_number", "client_email")


@dataclass
class CreditNoteOutcome:
    status: str                       # issued | duplicate | refused | unmatched | disabled
    reason: str = ""
    credit_note: Optional[models.Invoice] = None
    invoice: Optional[models.Invoice] = None


def _charge_payment_intent(charge: Dict[str, Any]) -> Optional[str]:
    value = charge.get("payment_intent")
    if isinstance(value, dict):
        value = value.get("id")
    return str(value) if value else None


def _credit_note_amounts(invoice: models.Invoice, notes: List[models.Invoice], cumulative: int) -> Dict[str, Any]:
    """The note for what was refunded since the last one. The whole invoice at
    once: its own line. Part of it: one « Remboursement partiel » line, HT =
    TTC ÷ 1,2 rounded half up; the note that completes the refund takes exactly
    what is left, so the notes always add up to the invoice."""
    delta = cumulative - sum(note.total_ttc_cents for note in notes)
    if cumulative == invoice.total_ttc_cents:
        ht = invoice.total_ht_cents - sum(note.total_ht_cents for note in notes)
    else:
        rate = invoice.line_vat_rate_percent
        ht = int((Decimal(delta) * 100 / (100 + rate)).quantize(Decimal(1), rounding=ROUND_HALF_UP))
    if not notes and cumulative == invoice.total_ttc_cents:
        line = {"line_description": invoice.line_description, "line_quantity": invoice.line_quantity,
                "line_unit_price_ht_cents": invoice.line_unit_price_ht_cents}
    else:
        line = {"line_description": f"Remboursement partiel — {invoice.line_description}", "line_quantity": 1,
                "line_unit_price_ht_cents": ht}
    return dict(line, line_vat_rate_percent=invoice.line_vat_rate_percent, line_total_ht_cents=ht,
                total_ht_cents=ht, total_vat_cents=delta - ht, total_ttc_cents=delta)


def issue_credit_note(db: Session, charge: Dict[str, Any], refunded_on: Optional[date] = None) -> CreditNoteOutcome:
    """charge.refunded: the credit note for what this refund adds (Stripe sends
    one event per refund, `amount_refunded` being the running total). A replay,
    or an event arriving after a later one, finds the amount already covered
    and issues nothing. Raises on an unexpected failure — nothing is stored."""
    if not config.invoices_enabled():
        return CreditNoteOutcome("disabled")
    payment_intent = _charge_payment_intent(charge)
    cumulative = charge.get("amount_refunded")
    if not payment_intent or not isinstance(cumulative, int) or isinstance(cumulative, bool):
        return CreditNoteOutcome("unmatched", reason="le remboursement ne porte pas de paiement Stripe lisible")
    purchase = db.query(models.Purchase).filter(models.Purchase.stripe_payment_intent == payment_intent).first()
    if purchase is None:
        return CreditNoteOutcome("unmatched", reason="aucun achat ScanID ne correspond à ce paiement "
                                                     "(payé avant les factures, ou enregistré à la main)")
    found = (db.query(models.Invoice.id)
             .filter(models.Invoice.purchase_id == purchase.id, models.Invoice.kind == KIND_INVOICE).first())
    if found is None:
        return CreditNoteOutcome("refused", reason="l'achat n'a pas de facture émise par l'application : "
                                                   "avoir à établir à la main, sur la facture que vous avez faite")
    for attempt in range(3):
        try:
            # Locked until the commit: two refunds of one invoice are numbered one after the other.
            invoice = db.query(models.Invoice).filter(models.Invoice.id == found.id).with_for_update().one()
            notes = (db.query(models.Invoice)
                     .filter(models.Invoice.credited_invoice_id == invoice.id, models.Invoice.kind == KIND_CREDIT_NOTE)
                     .all())
            if cumulative <= sum(note.total_ttc_cents for note in notes):
                db.rollback()
                return CreditNoteOutcome("duplicate", invoice=invoice)
            if cumulative > invoice.total_ttc_cents:
                db.rollback()
                return CreditNoteOutcome("refused", invoice=invoice, reason=(
                    f"le total remboursé ({euros(cumulative)}) dépasse la facture {invoice.number} "
                    f"({euros(invoice.total_ttc_cents)})"))
            fields = {name: getattr(invoice, name) for name in _COPIED_FROM_INVOICE}
            fields.update(_credit_note_amounts(invoice, notes, cumulative),
                          credited_invoice_id=invoice.id, credited_invoice_number=invoice.number,
                          payment_date=refunded_on or datetime.now(PARIS).date(),
                          stripe_charge_id=str(charge.get("id") or "") or None, refunded_cumulative_cents=cumulative)
            return CreditNoteOutcome("issued", invoice=invoice,
                                     credit_note=_write(db, KIND_CREDIT_NOTE, invoice.livemode, fields))
        except (IntegrityError, _YearChanged):
            db.rollback()
            if attempt == 2:
                raise
        except Exception:
            db.rollback()
            raise


def documents_by_purchase(db: Session, purchase_ids: List[str]) -> Dict[str, List[Dict[str, str]]]:
    """« Mes achats »: each purchase's invoice, then its credit notes."""
    if not purchase_ids:
        return {}
    rows = (db.query(models.Invoice.id, models.Invoice.kind, models.Invoice.number, models.Invoice.purchase_id)
            .filter(models.Invoice.purchase_id.in_(purchase_ids))
            .order_by(models.Invoice.issued_at, models.Invoice.sequence)
            .all())
    found: Dict[str, List[Dict[str, str]]] = {}
    for row in rows:
        found.setdefault(row.purchase_id, []).append({"id": row.id, "kind": row.kind, "number": row.number})
    return found


def list_documents(db: Session, month: Optional[Tuple[date, date]] = None, oldest_first: bool = False,
                   live_only: bool = False) -> List[models.Invoice]:
    """Every invoice and credit note (their PDF not loaded), newest first or in
    number order; `month` = (first day, last day) of the documents' date."""
    query = db.query(models.Invoice).options(defer(models.Invoice.pdf))
    if month is not None:
        query = query.filter(models.Invoice.issue_date >= month[0], models.Invoice.issue_date <= month[1])
    if live_only:
        query = query.filter(models.Invoice.livemode.is_(True))
    order = (models.Invoice.issued_at, models.Invoice.sequence)
    return query.order_by(*(order if oldest_first else (o.desc() for o in order))).all()


def filename(document: Any) -> str:
    """« Facture-F-2026-00001.pdf » / « Avoir-AV-2026-00001.pdf »."""
    kind, number = (document["kind"], document["number"]) if isinstance(document, dict) else (document.kind, document.number)
    return f"{'Avoir' if kind == KIND_CREDIT_NOTE else 'Facture'}-{number}.pdf"


def document_fields(row: models.Invoice) -> Dict[str, Any]:
    """Every stored mention of a document — not its PDF."""
    return {column.name: getattr(row, column.name) for column in models.Invoice.__table__.columns if column.name != "pdf"}


# --- The PDF ---------------------------------------------------------------------
# A4 in points. Each block is placed in its own rectangle (MuPDF's HTML engine
# does not honour table widths), and the font — Nimbus Sans, MuPDF's own — is
# embedded and subset, so the file reads the same in ten years.
_WIDTH, _HEIGHT = 595, 842
_LEFT, _RIGHT, _TOP, _BOTTOM = 48, 547, 48, 800
_COLUMNS = ((48, 292, ""), (292, 342, "r"), (342, 424, "r"), (424, 466, "r"), (466, 547, "r"))
_GREY = (0.93, 0.95, 0.97)
_RULE = (0.78, 0.80, 0.84)
_CSS = """
* { font-family: sans-serif; font-size: 9pt; color: #1a1f2b; }
p { margin: 0; line-height: 1.4; }
.r { text-align: right; } .c { text-align: center; } .b { font-weight: bold; }
.brand { font-size: 20pt; font-weight: bold; color: #0b3d91; line-height: 1.2; }
.title { font-size: 20pt; font-weight: bold; line-height: 1.2; }
.label { font-size: 7.5pt; font-weight: bold; color: #5b6475; }
.th { font-size: 8pt; font-weight: bold; color: #3b4352; }
.ttc { font-size: 10.5pt; font-weight: bold; }
.small { font-size: 7.5pt; color: #5b6475; }
.banner { font-size: 10pt; font-weight: bold; color: #b00020; }
"""


def _e(value: Any) -> str:
    return html.escape(str(value), quote=False)


def _box(page: fitz.Page, x0: float, y: float, x1: float, body: str) -> float:
    """Writes `body` (HTML) from (x0, y) between x0 and x1; returns the height used."""
    rect = fitz.Rect(x0, y, x1, _BOTTOM)
    spare, _ = page.insert_htmlbox(rect, body, css=_CSS, scale_low=1)
    if spare < 0:
        raise ValueError("invoice content does not fit on the page")
    return rect.height - spare


def _seller_line(document: Dict[str, Any]) -> str:
    """« ScanID, SASU au capital de 1 000 € — 169 avenue de Choisy, 75013 Paris —
    RCS Paris 107 858 557 — N° de TVA FR76107858557 — contact@scanid.fr »."""
    return (f"{document['seller_name']}, {document['seller_legal_form']} au capital de {document['seller_share_capital']}"
            f" — {document['seller_street']}, {document['seller_postal_code']} {document['seller_city']}"
            f" — {document['seller_rcs']} — N° de TVA {document['seller_vat_number']} — {document['seller_email']}")


def _client_lines(document: Dict[str, Any]) -> List[str]:
    lines = [f'<p class="b">{_e(document["client_name"])}</p>']
    if document.get("client_attention"):
        lines.append(f"<p>À l’attention de {_e(document['client_attention'])}</p>")
    if document.get("client_street"):
        lines.append(f"<p>{_e(document['client_street'])}</p>")
    town = " ".join(v for v in (document.get("client_postal_code"), document.get("client_city")) if v)
    if town:
        lines.append(f"<p>{_e(town)}</p>")
    if document.get("client_country"):
        lines.append(f"<p>{'France' if document['client_country'] == 'FR' else _e(document['client_country'])}</p>")
    if document.get("client_siren"):
        lines.append(f"<p>SIREN{NBSP}: {siren_fr(document['client_siren'])}</p>")
    if document.get("client_vat_number"):
        lines.append(f"<p>N° de TVA{NBSP}: {_e(document['client_vat_number'])}</p>")
    return lines


def _mentions(document: Dict[str, Any]) -> List[str]:
    lines = [f"Nature de l’opération{NBSP}: {document['nature']}"]
    if document["kind"] == KIND_CREDIT_NOTE:
        lines.append(f"Montant remboursé le {date_fr(document['payment_date'])} par {document['payment_method']}")
    else:
        lines += [f"Facture acquittée le {date_fr(document['payment_date'])} par {document['payment_method']}",
                  DISCOUNT_TERMS, LATE_PAYMENT_TERMS]
    return [f"<p>{_e(line)}</p>" for line in lines]


def render_pdf(document: Dict[str, Any], banner: Optional[str] = None) -> bytes:
    """The PDF of a document, from its stored mentions only. `banner` (a red box
    at the top) marks a test-mode document or a sample."""
    credit_note = document["kind"] == KIND_CREDIT_NOTE
    pdf = fitz.open()
    page = pdf.new_page(width=_WIDTH, height=_HEIGHT)
    y = _TOP
    if banner:
        used = _box(page, _LEFT + 8, y + 6, _RIGHT - 8, f'<p class="c banner">{_e(banner)}</p>')
        page.draw_rect(fitz.Rect(_LEFT, y, _RIGHT, y + used + 12), color=(0.69, 0, 0.13), width=1.5)
        y += used + 28

    seller = [f'<p class="brand">{_e(document["seller_name"])}</p>',
              f"<p>{_e(document['seller_legal_form'])} au capital de {_e(document['seller_share_capital'])}</p>",
              f"<p>{_e(document['seller_street'])}</p>",
              f"<p>{_e(document['seller_postal_code'])} {_e(document['seller_city'])}</p>",
              f"<p>{_e(document['seller_rcs'])}</p>",
              f"<p>N° de TVA{NBSP}: {_e(document['seller_vat_number'])}</p>",
              f"<p>{_e(document['seller_email'])}</p>"]
    heading = [f'<p class="r title">{"AVOIR" if credit_note else "FACTURE"}</p>',
               f'<p class="r">N°{NBSP}<b>{_e(document["number"])}</b></p>']
    if credit_note:
        heading += [f"<p class=\"r\">Date de l’avoir{NBSP}: {date_fr(document['issue_date'])}</p>",
                    f"<p class=\"r\">Avoir sur la facture {_e(document['credited_invoice_number'])}</p>"]
    else:
        heading += [f"<p class=\"r\">Date de facture{NBSP}: {date_fr(document['issue_date'])}</p>",
                    f"<p class=\"r\">Date de la prestation{NBSP}: {date_fr(document['service_date'])}</p>"]
    y += max(_box(page, _LEFT, y, 320, "".join(seller)), _box(page, 320, y, _RIGHT, "".join(heading))) + 22

    used = _box(page, _LEFT + 10, y + 8, 330, '<p class="label">CLIENT</p>' + "".join(_client_lines(document)))
    page.draw_rect(fitz.Rect(_LEFT, y, 340, y + used + 16), color=_RULE, width=0.8)
    y += used + 16 + 24

    headers = ("Désignation", "Quantité", "Prix unitaire HT", "TVA", "Total HT")
    tops = [_box(page, x0 + 5, y + 5, x1 - 5, f'<p class="th {align}">{label}</p>')
            for (x0, x1, align), label in zip(_COLUMNS, headers)]
    header_height = max(tops) + 10
    page.draw_rect(fitz.Rect(_LEFT, y, _RIGHT, y + header_height), color=None, fill=_GREY, overlay=False)
    y += header_height
    cells = (document["line_description"], count_fr(document["line_quantity"]),
             euros(document["line_unit_price_ht_cents"]), f"{document['line_vat_rate_percent']}{NBSP}%",
             euros(document["line_total_ht_cents"]))
    heights = [_box(page, x0 + 5, y + 7, x1 - 5, f'<p class="{align}">{_e(text)}</p>')
               for (x0, x1, align), text in zip(_COLUMNS, cells)]
    y += max(heights) + 14
    page.draw_line(fitz.Point(_LEFT, y), fitz.Point(_RIGHT, y), color=_RULE, width=0.8)
    y += 10

    totals = (("Total HT", document["total_ht_cents"], ""),
              (f"TVA {document['line_vat_rate_percent']}{NBSP}%", document["total_vat_cents"], ""),
              ("Total TTC", document["total_ttc_cents"], "ttc"))
    for label, cents, style in totals:
        top = y
        if style:
            page.draw_rect(fitz.Rect(352, top, _RIGHT, top + 24), color=None, fill=_GREY, overlay=False)
            top += 4
        height = max(_box(page, 360, top + 3, 452, f'<p class="{style}">{label}</p>'),
                     _box(page, 452, top + 3, _RIGHT - 6, f'<p class="r {style}">{euros(cents)}</p>'))
        y = top + height + (10 if style else 6)
    y += 22

    _box(page, _LEFT, y, _RIGHT, "".join(_mentions(document)))
    footer = fitz.Rect(_LEFT, _BOTTOM + 8, _RIGHT, _HEIGHT - 12)
    page.insert_htmlbox(footer, f'<p class="c small">{_e(_seller_line(document))}</p>', css=_CSS, scale_low=0.6)

    title = f"{'Avoir' if credit_note else 'Facture'} {document['number']}"
    stamp = document["issued_at"].astimezone(timezone.utc) if document["issued_at"].tzinfo else document["issued_at"]
    pdf.set_metadata({"title": title, "author": "ScanID", "subject": document["client_name"], "creator": "ScanID",
                      "producer": "ScanID", "creationDate": stamp.strftime("D:%Y%m%d%H%M%S+00'00'"),
                      "modDate": stamp.strftime("D:%Y%m%d%H%M%S+00'00'")})
    pdf.subset_fonts()
    data = pdf.tobytes(garbage=4, deflate=True)
    pdf.close()
    return data

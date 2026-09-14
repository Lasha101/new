# /billing_identity.py
"""SIRET and intra-EU VAT number: normalisation and structural validation.

Both appear on French B2B invoices (mandatory buyer mentions with e-invoicing
from September 2026 — Spec v3 §2), so they are checked where they are entered:
the free-trial form, the pack signup page and « Mon Compte ».
"""
import re
from typing import Optional

SIRET_ERROR = "Le SIRET doit comporter 14 chiffres valides."
VAT_ERROR = "Le numéro de TVA intracommunautaire n'est pas au bon format (ex. : FR12345678901)."

# La Poste's establishments share SIREN 356000000 and follow their own rule:
# the digits of the SIRET add up to a multiple of 5 (INSEE).
_LA_POSTE_SIREN = "356000000"


def normalize_siret(value: Optional[str]) -> str:
    """Digits only (spaces, dots and dashes typed for readability dropped)."""
    return re.sub(r"[\s.\-]", "", value or "")


def is_valid_siret(siret: str) -> bool:
    """14 digits passing the Luhn check (or La Poste's rule)."""
    if not re.fullmatch(r"[0-9]{14}", siret or ""):
        return False
    if siret.startswith(_LA_POSTE_SIREN) and siret != "35600000000048":
        return sum(int(d) for d in siret) % 5 == 0
    total = 0
    for index, char in enumerate(reversed(siret)):
        digit = int(char)
        if index % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def normalize_vat(value: Optional[str]) -> str:
    return re.sub(r"[\s.\-]", "", value or "").upper()


def is_valid_vat(vat: str) -> bool:
    """French: FR + 2-character key + 9-digit SIREN (11 characters after FR).
    Another EU country: its 2-letter prefix + 2 to 12 letters or digits."""
    if vat.startswith("FR"):
        return re.fullmatch(r"FR[0-9A-HJ-NP-Z]{2}[0-9]{9}", vat) is not None
    return re.fullmatch(r"(AT|BE|BG|CY|CZ|DE|DK|EE|EL|ES|FI|HR|HU|IE|IT|LT|LU|LV|MT|NL|PL|PT|RO|SE|SI|SK|XI)[0-9A-Z+*]{2,12}", vat) is not None

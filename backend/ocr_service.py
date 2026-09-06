# /ocr_service.py
"""Extraction of identity data from scanned documents via Google Vision OCR.

Two French document families are supported, both mapped onto the same schema
(first_name, last_name, birth_date, expiration_date, nationality,
passport_number, confidence_score):

- French passports: MRZ-first parsing with visual-zone fallbacks. This logic
  is kept identical to the original implementation so passport results stay
  byte-for-byte compatible.
- French national identity cards (CNI), in both formats:
    * new format (2021+, credit-card size): 3-line TD1 MRZ on the back, or
      visual-zone parsing when only the front of the card is on the page;
    * old format (laminated card): 2-line MRZ on the front; the expiration
      date only exists in the visual zone of the back ("Carte valable
      jusqu'au ..."), so it is read from there.

Every parsing failure raises an HTTPException whose detail is a short,
technically explicit diagnostic; callers surface it per page.
"""
import re
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Awaitable, Callable, List, Dict, Optional
from google.cloud import vision
from fastapi import HTTPException

import config
import logging
import fitz  # PyMuPDF
import unicodedata

logger = logging.getLogger(__name__)

# Initialize Vision client at module level for efficiency.
#
# DATA RESIDENCY: the endpoint is pinned to the EU (eu-vision.googleapis.com by
# default, config.VISION_API_ENDPOINT). Left unset, the library uses the global
# endpoint (vision.googleapis.com), which may process the request in any Google
# region — an image of a French identity document could be handled outside the
# EU. Pinning it here is what backs the residency commitment in the client DPA.
try:
    from google.api_core.client_options import ClientOptions

    vision_client = vision.ImageAnnotatorClient(
        client_options=ClientOptions(api_endpoint=config.VISION_API_ENDPOINT)
    )
    logger.info("Google Vision client bound to %s", config.VISION_API_ENDPOINT)
except Exception as e:
    logger.error(f"🔴 Failed to initialize Google Vision client: {e}")
    vision_client = None

# Pages are OCR'd concurrently, bounded by this many in-flight Vision calls.
# A dedicated executor is required: the event loop's default executor is
# capped at min(32, cpu+4) threads (6 on a 2-vCPU host), which would silently
# throttle the fan-out below that bound.
_OCR_MAX_CONCURRENCY = 8
_ocr_executor = ThreadPoolExecutor(max_workers=_OCR_MAX_CONCURRENCY, thread_name_prefix="ocr")


# --- Shared helpers ---

def clean_and_parse_date(date_str: str) -> datetime | None:
    """Cleans a 'DD MM YYYY'-like string (tolerating . , separators and OCR
    noise) and parses it into a datetime, or returns None."""
    if not date_str:
        return None
    cleaned_str = re.sub(r'[.,/]', ' ', date_str)
    cleaned_str = re.sub(r'[^\d\s]', '', cleaned_str)
    cleaned_str = re.sub(r'\s+', ' ', cleaned_str).strip()
    try:
        return datetime.strptime(cleaned_str, "%d %m %Y")
    except ValueError:
        logger.warning("Impossible d'analyser une date du document (%d caractères).", len(date_str or ""))
        return None


def _mrz_check_digit(field: str) -> str:
    """ICAO 9303 check digit of an MRZ field: digits count as themselves,
    letters as A=10..Z=35, '<' as 0; weights cycle 7, 3, 1."""
    values = [int(c) if c.isdigit() else (0 if c == '<' else ord(c) - 55) for c in field]
    weights = (7, 3, 1)
    return str(sum(v * weights[i % 3] for i, v in enumerate(values)) % 10)


def _parse_mrz_date(yymmdd: str, is_birth_date: bool) -> Optional[str]:
    """Parses a 6-digit MRZ date. Birth dates use a sliding century window;
    expiration dates are assumed to be in the 21st century."""
    try:
        if is_birth_date:
            year = int(yymmdd[0:2])
            current_year_short = datetime.now().year % 100
            prefix = "19" if year > current_year_short else "20"
        else:
            prefix = "20"
        return datetime.strptime(f"{prefix}{yymmdd}", "%Y%m%d").strftime("%Y-%m-%d")
    except ValueError:
        logger.warning("Impossible d'analyser une date MRZ (%d caractères).", len(yymmdd or ""))
        return None


def _strip_accents(text: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')


def _mrz_lines(raw_text: str) -> List[str]:
    """Returns each physical OCR line reduced to MRZ characters (A-Z, 0-9, <),
    so MRZ lines can be matched even when Vision inserts spaces."""
    lines = []
    for line in raw_text.splitlines():
        cleaned = re.sub(r'[^A-Z0-9<]', '', line.upper())
        if cleaned:
            lines.append(cleaned)
    return lines


def _mrz_fragment_candidates(lines: List[str]) -> List[str]:
    """Candidate MRZ lines rebuilt from fragments: Vision sometimes splits one
    physical MRZ line at a faint '<' filler run, occasionally emitting the two
    halves out of order. MRZ-looking fragments ('<' present or IDFRA prefix)
    are kept and concatenations of 2-3 consecutive fragments (pairs also in
    reversed order) are added; the anchored MRZ patterns filter out the rest."""
    fragments = [line for line in lines if '<' in line or line.startswith('IDFRA')]
    candidates = list(fragments)
    for size in (2, 3):
        for i in range(len(fragments) - size + 1):
            candidates.append(''.join(fragments[i:i + size]))
    for i in range(len(fragments) - 1):
        candidates.append(fragments[i + 1] + fragments[i])
    return candidates


def _compute_confidence_score(data: dict, full_text_annotation) -> float:
    """Averages Vision word confidences over the words that were actually used
    in the extracted fields (names, document number, nationality)."""
    relevant_confidences = []
    target_words = set()

    def clean_for_match(text: str) -> str:
        text = _strip_accents(text.upper())
        return re.sub(r'[^A-Z0-9]', '', text)

    for field in ("last_name", "first_name", "passport_number", "nationality"):
        value = data.get(field, "")
        if value:
            parts = re.split(r'[\s-]+', value.upper())
            cleaned_parts = [clean_for_match(p) for p in parts if p]
            for part in cleaned_parts:
                target_words.add(part)
            if len(cleaned_parts) > 1:
                target_words.add(''.join(cleaned_parts))

    for page in full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    word_text = ''.join(symbol.text for symbol in word.symbols)
                    if clean_for_match(word_text) and clean_for_match(word_text) in target_words:
                        relevant_confidences.append(word.confidence)

    final_confidence = sum(relevant_confidences) / len(relevant_confidences) if relevant_confidences else 0.0
    return round(final_confidence, 4)


# --- Split-document signals ---
# An old-format CNI prints its MRZ on the front and its expiration date only on
# the back. When the two sides arrive as two separate pages, each page alone
# fails; these HTTPException subclasses keep today's exact error messages while
# carrying the partial information, so extract_data_page_by_page can pair a
# front with the adjacent verso page. A page still never yields more than one
# document.

_OLD_CNI_MISSING_EXPIRY_DETAIL = (
    "CNI (ancien format) détectée via sa MRZ, mais la date d'expiration est introuvable : "
    "la mention 'Carte valable jusqu'au JJ.MM.AAAA' du verso est absente ou illisible sur la page.")
_UNRECOGNIZED_DOCUMENT_DETAIL = (
    "Document non reconnu : aucune MRZ de passeport français (P<FRA...), aucune MRZ de "
    "carte nationale d'identité (IDFRA...) ni aucun recto de CNI exploitable n'a été "
    "détecté sur cette page.")


class OldCniFrontMissingExpiry(HTTPException):
    """Front of an old-format CNI fully identified via its MRZ, but the page
    carries no 'Carte valable jusqu'au' expiration date."""
    def __init__(self, partial_data: dict):
        super().__init__(status_code=422, detail=_OLD_CNI_MISSING_EXPIRY_DETAIL)
        self.partial_data = partial_data


class PotentialOldCniVerso(HTTPException):
    """Unrecognized page whose only exploitable content is the
    'Carte valable jusqu'au' date of an old-format CNI verso."""
    def __init__(self, expiration_date: str):
        super().__init__(status_code=422, detail=_UNRECOGNIZED_DOCUMENT_DETAIL)
        self.expiration_date = expiration_date


# --- Passport parsing (identical behavior to the original implementation) ---

# OCR sometimes reads the letter 'I' as the digit '1'. In a French passport
# number (2 digits + 2 letters + 5 digits) the 3rd and 4th characters are
# always letters, so a '1' in either of those positions must be the letter
# 'I'. The correction is only applied where the surrounding text anchors the
# token as a passport number: the full MRZ line-2 context, or the standalone
# 9-character shape with at least one real letter for the visual zone.
_MRZ_LINE2_DOCNUM_RE = re.compile(r'(\d{2})([A-Z1]{2})(\d{5}\d?FRA\d{6}\d[MFX<]\d{6})')
_VISUAL_DOCNUM_RE = re.compile(r'\b(\d{2})([A-Z]{2}|[A-Z]1|1[A-Z])(\d{5})\b')


def _fix_mrz_passport_number(mrz_text: str) -> str:
    """Restores 'I' letters misread as '1' in the letter positions of the
    document number of a passport MRZ line 2."""
    return _MRZ_LINE2_DOCNUM_RE.sub(
        lambda m: m.group(1) + m.group(2).replace('1', 'I') + m.group(3),
        mrz_text,
    )


# Passport MRZ line 1: 'P<FRA' + SURNAME + '<<' + GIVEN<NAMES + '<' fillers.
# Surname words are separated by a single '<' (LE<FLOCH), the surname and the
# given names by '<<'. The surname group therefore only accepts single '<'
# separators, so the first '<<' of the line is the name separator; a greedy
# [A-Z<]+ would swallow the whole line up to the trailing fillers and leave
# the split to guesswork (LE FLOCH / SANDRINE became LE / FLOCH SANDRINE).
# Stray fillers OCR may insert right after the country code are skipped.
PASSPORT_MRZ_LINE1_RE = re.compile(r'P<FRA<*([A-Z]+(?:<[A-Z]+)*)<<([A-Z<]+)')

# Fallbacks for a scan that crops the left edge of the MRZ (the first
# characters of both lines are physically missing):
# - the right-hand tail of line 2 that survives the crop: 'FRA' + birth
#   date (6) + check digit + sex + expiry date (6) + check digit. Both ICAO
#   check digits are validated before the match is trusted, so ordinary text
#   can never fake it;
# - 'SURNAME<<GIVEN<NAMES' followed by a filler run, matched without the
#   'P<FRA' anchor when that anchor was cropped away.
PASSPORT_PARTIAL_LINE2_RE = re.compile(r'FRA(\d{6})(\d)([MFX])(\d{6})(\d)')
PASSPORT_NAME_FRAGMENT_RE = re.compile(r'([A-Z]+(?:<[A-Z]+)*)<<([A-Z]+(?:<[A-Z]+)*)<{3,}')


def _parse_passport(full_text: str) -> Optional[dict]:
    """Parses French passport data from normalized OCR text. Returns None when
    the page cannot be confirmed as a complete French passport, in which case
    the caller tries the CNI parsers."""
    data = {
        "first_name": "", "last_name": "", "passport_number": "",
        "nationality": "", "birth_date": "", "expiration_date": ""
    }

    # MRZ-first parsing
    mrz_text = _fix_mrz_passport_number(full_text.replace(' ', ''))
    mrz_line1_match = PASSPORT_MRZ_LINE1_RE.search(mrz_text)
    if mrz_line1_match:
        data["last_name"], data["first_name"] = _split_mrz_names(
            mrz_line1_match.group(1) + '<<' + mrz_line1_match.group(2))

    mrz_line2_match = re.search(r'(\d{2}[A-Z]{2}\d{5})\d?(FRA)(\d{2}\d{2}\d{2})\d[MFX<](\d{2}\d{2}\d{2})', mrz_text)
    if mrz_line2_match:
        data["nationality"] = "Française"
        data["passport_number"] = mrz_line2_match.group(1)
        birth = _parse_mrz_date(mrz_line2_match.group(3), is_birth_date=True)
        if birth:
            data["birth_date"] = birth
        expiration = _parse_mrz_date(mrz_line2_match.group(4), is_birth_date=False)
        if expiration:
            data["expiration_date"] = expiration
    else:
        # Line 2 with its left edge cropped out of the scan: dates and
        # nationality from the surviving checksummed tail (the document number
        # is gone from the MRZ; the visual-zone fallback below recovers it).
        partial = PASSPORT_PARTIAL_LINE2_RE.search(mrz_text)
        if partial and _mrz_check_digit(partial.group(1)) == partial.group(2) \
                and _mrz_check_digit(partial.group(4)) == partial.group(5):
            data["nationality"] = "Française"
            birth = _parse_mrz_date(partial.group(1), is_birth_date=True)
            if birth:
                data["birth_date"] = birth
            expiration = _parse_mrz_date(partial.group(4), is_birth_date=False)
            if expiration:
                data["expiration_date"] = expiration

    if not data["last_name"] and not data["first_name"]:
        # Line 1 with its 'P<FRA' anchor cropped: the '<<' separator still
        # splits the names. The fragment may carry residue of the cut anchor
        # (and, in space-stripped text, of preceding words), so the surname is
        # the longest suffix that exists as a standalone word in the visual
        # zone — MRZ tokens (any word containing '<') are excluded so the
        # fragment can never validate itself.
        name_fragment = PASSPORT_NAME_FRAGMENT_RE.search(mrz_text)
        if name_fragment:
            given = ' '.join(name_fragment.group(2).replace('<', ' ').split())
            viz_text = ' '.join(w for w in full_text.split() if '<' not in w)
            surname = None
            for i in range(len(name_fragment.group(1))):
                candidate = ' '.join(name_fragment.group(1)[i:].replace('<', ' ').split())
                if len(candidate.replace(' ', '')) >= 3 and re.search(
                        r'(?<![A-Za-z])' + re.escape(candidate) + r'(?![A-Za-z])', viz_text, re.IGNORECASE):
                    surname = candidate
                    break
            if surname and given:
                data["last_name"], data["first_name"] = surname, given

    # Visual-zone fallbacks
    if not data["passport_number"]:
        passport_match = _VISUAL_DOCNUM_RE.search(full_text)
        if passport_match:
            data["passport_number"] = (passport_match.group(1)
                                       + passport_match.group(2).replace('1', 'I')
                                       + passport_match.group(3))
    if not data["last_name"]:
        last_name_match = re.search(r'(?:Nom|SURNAME)\s+([A-Z\s\'-]+?)(?=\s*Prénom|GIVEN|Nationalité|Date|P<|$)', full_text, re.IGNORECASE)
        if last_name_match:
            data["last_name"] = last_name_match.group(1).strip()
    if not data["first_name"]:
        first_name_match = re.search(r'(?:Prénom\(s\)|Prénoms|GIVEN NAMES)\s+([A-Z][a-zA-Z\s\'-]+?)(?=\s*Nationalité|Date|Sexe|Sex|P<|$)', full_text, re.IGNORECASE)
        if first_name_match:
            data["first_name"] = first_name_match.group(1).strip()
    if data["last_name"] and not data["first_name"] and ' ' in data["last_name"]:
        parts = data["last_name"].split()
        if len(parts) > 1:
            data["last_name"] = parts[0]
            data["first_name"] = " ".join(parts[1:])
    if not data["nationality"]:
        nationality_match = re.search(r'(?:Nationalité|Nationality)\s+([A-Za-zçÇéÉèÈàÀâÂêÊîÎôÔûÛ]+)', full_text, re.IGNORECASE)
        if nationality_match and "française" in nationality_match.group(1).lower():
            data["nationality"] = "Française"

    if data["nationality"] != "Française":
        return None
    if not all([data["passport_number"], data["last_name"], data["first_name"], data["birth_date"], data["expiration_date"]]):
        return None
    return data


# --- CNI parsing ---

# New-format CNI (2021+), TD1 MRZ on the back: 3 lines of 30 characters.
#   Line 1: IDFRA + document number (9) + check digit + optional data
#   Line 2: birth date (6) + check + sex + expiry date (6) + check + FRA + ...
#   Line 3: SURNAME<<GIVEN<NAMES
TD1_LINE1_RE = re.compile(r'^IDFRA([A-Z0-9<]{9})(\d)')
TD1_LINE2_RE = re.compile(r'^(\d{6})(\d)([MFX<])(\d{6})(\d)FRA')
MRZ_NAME_LINE_RE = re.compile(r'^([A-Z]+(?:<[A-Z]+)*)<<([A-Z][A-Z<]*)$')

# Old-format CNI, 2-line MRZ of 36 characters on the front:
#   Line 1: IDFRA + surname (25, '<'-padded) + issuance office (6)
#   Line 2: card number (12) + check + given names (14, '<'-separated)
#           + birth date (6) + check + sex + check
TD2_LINE1_RE = re.compile(r'^IDFRA([A-Z<]{15,30})(\d{4,6})$')
TD2_LINE2_RE = re.compile(r'^(\d{12})(\d)([A-Z<]{5,20}?)(\d{6})(\d)([MFX])(\d?)$')

# Tolerant variants for OCR-damaged MRZ lines, used only on candidates rebuilt
# from fragments when the strict patterns above matched nothing on the page:
#   line 1 with part of its '<' filler run dropped by the OCR,
#   line 2 with the digit '0' misread as the letter 'O' in numeric positions
#   (the mirror of the 'I'-misread-as-'1' passport fix above; 'O' stays a real
#   letter inside the name field).
TD2_LINE1_RELAXED_RE = re.compile(r'^IDFRA([A-Z<]{2,30}?)(\d{4,6})$')
TD2_LINE2_RELAXED_RE = re.compile(r'^([0-9O]{12})([0-9O])([A-Z<]{5,20}?)([0-9O]{6})([0-9O])([MFX])([0-9O]?)$')


def _split_mrz_names(name_field: str) -> tuple[str, str]:
    """Splits 'SURNAME<<GIVEN<NAMES' style fields already separated by '<<'
    into (surname, given names), turning '<' fillers into spaces."""
    surname_part, _, given_part = name_field.partition('<<')
    surname = ' '.join(surname_part.replace('<', ' ').split())
    given = ' '.join(given_part.replace('<', ' ').split())
    return surname, given


def _parse_cni_new_mrz(raw_text: str) -> Optional[dict]:
    """Parses the TD1 MRZ printed on the back of new-format (2021+) cards."""
    lines = _mrz_lines(raw_text)

    doc_number = None
    birth_date = None
    expiration_date = None
    for line in lines:
        m1 = TD1_LINE1_RE.match(line)
        if m1 and doc_number is None:
            candidate = m1.group(1).replace('<', '')
            if len(candidate) == 9:
                doc_number = candidate
        m2 = TD1_LINE2_RE.match(line)
        if m2 and birth_date is None:
            birth_date = _parse_mrz_date(m2.group(1), is_birth_date=True)
            expiration_date = _parse_mrz_date(m2.group(4), is_birth_date=False)

    if not (doc_number and birth_date and expiration_date):
        return None

    last_name, first_name = "", ""
    for line in lines:
        if line.startswith('IDFRA') or line.startswith('P<'):
            continue
        if MRZ_NAME_LINE_RE.match(line.strip('<')):
            last_name, first_name = _split_mrz_names(line.strip('<'))
            break
    if not (last_name and first_name):
        return None

    return {
        "first_name": first_name, "last_name": last_name,
        "passport_number": doc_number, "nationality": "Française",
        "birth_date": birth_date, "expiration_date": expiration_date,
    }


_DATE_PATTERN = r"\d{2}[\s.,/-]*\d{2}[\s.,/-]*\d{4}"


def _find_old_cni_expiration(full_text: str) -> Optional[str]:
    """The old-format card carries its expiration date only in the visual zone
    of the back: 'Carte valable jusqu'au : DD.MM.YYYY'. OCR sometimes drops
    the ''au' or reads the date before the label, so both sides are tried."""
    normalized = _strip_accents(full_text.upper())
    match = re.search(r"VALABLE\s*JUSQU\W{0,4}(?:AU)?\s*:?\s*(" + _DATE_PATTERN + r")", normalized)
    if not match:
        match = re.search(r"(" + _DATE_PATTERN + r")[\s:]*(?:CARTE\s+)?VALABLE\s+JUSQU", normalized)
    if not match:
        return None
    parsed = clean_and_parse_date(match.group(1))
    return parsed.strftime("%Y-%m-%d") if parsed else None


def _find_visual_given_names(full_text: str) -> Optional[str]:
    """Reads the printed 'Prénom(s): X, Y, Z' line, which contains the full
    given names (the old-format MRZ truncates them to 14 characters)."""
    normalized = _strip_accents(full_text.upper())
    # The terminating labels must stand alone as words (whitespace before,
    # word boundary after), otherwise a name like RENEE would be cut at 'NEE'.
    match = re.search(
        r"PRENOM\(?S?\)?(?:\s*/?\s*GIVEN\s*NAMES)?\s*:?\s*([A-Z][A-Z ,'-]*?)"
        r"(?=\s+(?:(?:SEXE|SEX|NEE|NATIONALITE|TAILLE)\b|NE\(E\)|NE\s+LE)|\s*$)",
        normalized,
    )
    if not match:
        return None
    names = ' '.join(match.group(1).replace(',', ' ').split())
    return names or None


def _parse_cni_old_mrz(raw_text: str, full_text: str) -> Optional[dict]:
    """Parses the 2-line MRZ of old-format cards, completing the expiration
    date and full given names from the visual zones. A front whose expiration
    is missing from the page raises OldCniFrontMissingExpiry carrying the
    already-parsed identity, so the caller can complete it from an adjacent
    verso page."""
    lines = _mrz_lines(raw_text)

    surname = None
    card_number = None
    mrz_given_names = None
    birth_date = None
    for line in lines:
        m1 = TD2_LINE1_RE.match(line)
        if m1 and surname is None:
            surname = ' '.join(m1.group(1).replace('<', ' ').split())
        m2 = TD2_LINE2_RE.match(line)
        if m2 and card_number is None:
            card_number = m2.group(1)
            mrz_given_names = ' '.join(m2.group(3).replace('<', ' ').split())
            birth_date = _parse_mrz_date(m2.group(4), is_birth_date=True)

    # Tolerant second pass, only for what the strict pass could not find:
    # candidates rebuilt from MRZ fragments, matched with the relaxed patterns.
    if surname is None or card_number is None:
        for candidate in _mrz_fragment_candidates(lines):
            if surname is None:
                m1 = TD2_LINE1_RELAXED_RE.match(candidate)
                if m1:
                    surname = ' '.join(m1.group(1).replace('<', ' ').split())
            if card_number is None:
                m2 = TD2_LINE2_RELAXED_RE.match(candidate)
                if m2:
                    card_number = m2.group(1).replace('O', '0')
                    mrz_given_names = ' '.join(m2.group(3).replace('<', ' ').split())
                    birth_date = _parse_mrz_date(m2.group(4).replace('O', '0'), is_birth_date=True)

    if not (surname and card_number and birth_date):
        return None

    first_name = _find_visual_given_names(full_text) or mrz_given_names

    expiration_date = _find_old_cni_expiration(full_text)
    if not expiration_date:
        if first_name:
            raise OldCniFrontMissingExpiry({
                "first_name": first_name, "last_name": surname,
                "passport_number": card_number, "nationality": "Française",
                "birth_date": birth_date,
            })
        raise HTTPException(status_code=422, detail=_OLD_CNI_MISSING_EXPIRY_DETAIL)

    if not first_name:
        return None

    return {
        "first_name": first_name, "last_name": surname,
        "passport_number": card_number, "nationality": "Française",
        "birth_date": birth_date, "expiration_date": expiration_date,
    }


# Visual-zone labels of the new-format card front, used both to locate values
# and to know where a value ends. Common OCR misreadings ('SUMAME' for
# 'Surname') are included so they never leak into extracted values.
_CNI_VISUAL_LABELS = (
    "CARTE NATIONALE D'IDENTITE", "CARTE NATIONALE D IDENTITE", "IDENTITY CARD",
    "REPUBLIQUE FRANCAISE", "NOM D'USAGE", "NOM D USAGE", "ALTERNATE NAME",
    "SURNAME", "SUMAME", "NOM", "PRENOMS", "PRENOM", "GIVEN NAMES", "SEXE", "SEX",
    "NATIONALITE", "NATIONALITY", "DATE DE NAISS", "DATE OF BIRTH",
    "LIEU DE NAISSANCE", "PLACE OF BIRTH", "N° DU DOCUMENT", "N DU DOCUMENT",
    "DOCUMENT NO", "DATE D'EXPIR", "DATE D EXPIR", "EXPIRY DATE",
    "SIGNATURE", "TAILLE", "HEIGHT", "ADRESSE", "ADDRESS",
)


# Labels only count when they stand alone (no letter on either side), so real
# names that merely contain a label substring (TAILLEFER, SEXTON, NOMBLOT...)
# are never mistaken for one. Longest labels first so "NOM D'USAGE" wins over "NOM".
_CNI_LABEL_RE = re.compile(
    r"(?<![A-Z])(?:" + "|".join(re.escape(label) for label in sorted(_CNI_VISUAL_LABELS, key=len, reverse=True)) + r")(?![A-Z])"
)


def _visual_value_after(normalized: str, label_pattern: str, value_chars: str) -> Optional[str]:
    """Returns the text following a label: leading label words (e.g. the OCR'd
    'Surname' of a bilingual label) are stripped, and the value is cut at the
    next known label."""
    match = re.search(label_pattern + r"\s*/?\s*:?\s*(" + value_chars + r"+)", normalized)
    if not match:
        return None
    value = match.group(1).strip()

    while True:
        leading = _CNI_LABEL_RE.match(value)
        if not leading:
            break
        value = value[leading.end():].lstrip(" ,:/-.")

    inner = _CNI_LABEL_RE.search(value)
    if inner:
        value = value[:inner.start()]
    value = value.strip(" ,:/-.")
    return value or None


def _parse_cni_new_visual(full_text: str) -> Optional[dict]:
    """Parses the front of a new-format (2021+) card when its back — and thus
    its MRZ — is not on the page."""
    normalized = _strip_accents(full_text.upper())
    if not re.search(r"CARTE NATIONALE D.?IDENTITE|IDENTITY CARD", normalized):
        return None

    doc_match = re.search(r"DOCUMENT\s*(?:NO?)?\W{0,3}\b([A-Z0-9]{9})\b", normalized)
    doc_number = doc_match.group(1) if doc_match else None
    if doc_number is None:
        # Fallback: a 9-character token mixing letters and digits (the
        # new-format document number shape), anywhere on the card.
        for token in re.findall(r"\b[A-Z0-9]{9}\b", normalized):
            if re.search(r"[A-Z]", token) and re.search(r"\d", token):
                doc_number = token
                break

    birth_match = re.search(r"NAISS\w*[\s./]*(?:DATE OF BIRTH)?\s*:?\s*(" + _DATE_PATTERN + r")", normalized)
    birth_dt = clean_and_parse_date(birth_match.group(1)) if birth_match else None

    # The document number sometimes precedes the expiry date on the same OCR
    # line, so an optional alphanumeric token is tolerated before the date.
    expiry_match = re.search(r"EXPIR\w*[\s./]*(?:EXPIRY DATE)?\s*:?\s*(?:[A-Z0-9]{6,12}\s+)?(" + _DATE_PATTERN + r")", normalized)
    expiry_dt = clean_and_parse_date(expiry_match.group(1)) if expiry_match else None

    last_name = _visual_value_after(normalized, r"\bNOM(?!\s*D.?USAGE)\b", r"[A-Z' -]")
    first_name = _find_visual_given_names(full_text)
    if first_name is None:
        first_name = _visual_value_after(normalized, r"\bGIVEN NAMES\b", r"[A-Z ,'-]")
        if first_name:
            first_name = ' '.join(first_name.replace(',', ' ').split())

    missing = [name for name, value in (
        ("numéro de document", doc_number), ("nom", last_name), ("prénoms", first_name),
        ("date de naissance", birth_dt), ("date d'expiration", expiry_dt),
    ) if not value]
    if missing:
        raise HTTPException(
            status_code=422,
            detail=("CNI (nouveau format, recto sans MRZ) détectée, mais des champs de la zone visuelle "
                    f"sont illisibles ou absents : {', '.join(missing)}."),
        )

    return {
        "first_name": first_name, "last_name": last_name,
        "passport_number": doc_number, "nationality": "Française",
        "birth_date": birth_dt.strftime("%Y-%m-%d"), "expiration_date": expiry_dt.strftime("%Y-%m-%d"),
    }


# --- Page-level extraction ---

def _extract_document_data_from_image_bytes(image_bytes: bytes, retry_empty: bool = True) -> dict:
    """Runs Vision OCR on one page image and parses it as a French passport or
    a French national identity card. Raises HTTPException with an explicit
    diagnostic when no supported document can be extracted."""
    if vision_client is None:
        raise HTTPException(status_code=500, detail="Service Google Vision non initialisé.")

    image = vision.Image(content=image_bytes)
    feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)
    image_context = vision.ImageContext(language_hints=['fr'])
    request = vision.AnnotateImageRequest(image=image, features=[feature], image_context=image_context)

    # One retry absorbs transient Vision API errors and — where no render
    # fallback exists (retry_empty=True) — transient empty annotations too.
    # On the embedded fast path the caller passes retry_empty=False: its
    # 300-dpi render retry already provides the second attempt, so genuinely
    # blank pages are no longer billed twice there.
    response = None
    for attempt in (1, 2):
        response = vision_client.annotate_image(request=request)
        if response.error.message:
            logger.warning(f"Erreur de l'API Vision (tentative {attempt}) : {response.error.message}")
            continue
        if retry_empty and not (response.full_text_annotation and response.full_text_annotation.pages):
            logger.warning(f"Réponse Vision sans texte (tentative {attempt}).")
            continue
        break

    if response.error.message:
        raise HTTPException(status_code=400, detail=f"L'API Google Vision a renvoyé une erreur : {response.error.message}")
    full_text_annotation = response.full_text_annotation
    if not full_text_annotation or not full_text_annotation.pages:
        raise HTTPException(status_code=400, detail="Aucun texte n'a pu être détecté dans le document.")

    raw_text = full_text_annotation.text
    clean_text = re.sub(r'[\n/]', ' ', raw_text)
    full_text = re.sub(r'\s+', ' ', clean_text).strip()

    # The OCR text of an identity document is the document: MRZ, names, dates
    # of birth and the document number, all in one string. It used to be logged
    # in full. Only its length is logged now — enough to tell "Vision returned
    # nothing" from "Vision returned a page" while debugging, which is all the
    # line was ever used for.
    logger.info("Texte OCR reçu : %d caractères.", len(full_text))

    # A passport MRZ wins over everything else (one document per page); the
    # CNI parsers are tried from the most to the least reliable source.
    data = _parse_passport(full_text)
    if data is None:
        data = _parse_cni_new_mrz(raw_text)
    if data is None:
        try:
            data = _parse_cni_old_mrz(raw_text, full_text)
        except OldCniFrontMissingExpiry as e:
            # The front's identity is complete: score it here (the annotation
            # only exists in this scope) so a later recto/verso merge carries
            # the same confidence semantics as a single-page extraction.
            e.partial_data["confidence_score"] = _compute_confidence_score(e.partial_data, full_text_annotation)
            raise
    if data is None:
        data = _parse_cni_new_visual(full_text)
        if data is not None:
            # Pure visual-zone parse (no MRZ anywhere on the page): the only
            # parser whose output is sensitive to which image bytes Vision
            # saw. The caller uses this marker to re-check such pages on a
            # 300-dpi render when the fast embedded-image path was used.
            data["_visual_only"] = True
    if data is None:
        # A page carrying only the back of an old-format CNI (address block +
        # 'Carte valable jusqu'au ...') has no MRZ and no recognizable front:
        # keep the standard rejection, but tag the page as a potential verso so
        # the caller can pair it with an adjacent front missing its expiry.
        verso_expiration = _find_old_cni_expiration(full_text)
        if verso_expiration:
            raise PotentialOldCniVerso(verso_expiration)
        raise HTTPException(status_code=422, detail=_UNRECOGNIZED_DOCUMENT_DETAIL)

    data["confidence_score"] = _compute_confidence_score(data, full_text_annotation)
    # Which fields were found, never what they contain.
    logger.info(
        "Données analysées : %s champs renseignés (score %.4f).",
        sum(1 for key, value in data.items() if key != "confidence_score" and value),
        data.get("confidence_score", 0.0),
    )
    return data


def _pair_split_old_cni(results: List[Dict[str, Any]]) -> None:
    """Joins the two pages of an old-format CNI scanned recto and verso on two
    separate, adjacent pages. A page recognized as a front missing its expiry
    ('_pending_front') is merged with an adjacent unrecognized page carrying
    only the verso's 'Carte valable jusqu'au' date ('_pending_verso'): the next
    page is tried first, then the previous one, and each verso is consumed at
    most once. The merged document is reported under the front's page; the
    verso entry becomes an informational {'verso_of_page': N}. Pages left
    unpaired keep their original errors, so behavior is unchanged whenever no
    split card is present. Only the expiration date ever comes from the verso —
    the identity comes exclusively from the front's MRZ, and a page still never
    yields more than one document."""
    by_page = {r.get("page_number"): r for r in results}
    for result in results:
        front = result.get("_pending_front")
        if not front:
            continue
        page_number = result["page_number"]
        for neighbor in (page_number + 1, page_number - 1):
            verso = by_page.get(neighbor)
            if verso and "_pending_verso" in verso:
                result.pop("error", None)
                result.pop("_pending_front", None)
                result["data"] = dict(front, expiration_date=verso.pop("_pending_verso"))
                verso.pop("error", None)
                verso["verso_of_page"] = page_number
                logger.info(f"CNI ancien format fusionnée : recto page {page_number} + verso page {neighbor}.")
                break
    for result in results:
        result.pop("_pending_front", None)
        result.pop("_pending_verso", None)


def _render_page_png(pdf_document, page_num: int, fitz_lock: threading.Lock) -> bytes:
    """300-dpi PNG render of one page. PyMuPDF is not thread-safe, so all
    document access is serialized behind fitz_lock."""
    with fitz_lock:
        pdf_page: Any = pdf_document[page_num]
        pix = pdf_page.get_pixmap(dpi=300)
        return pix.tobytes("png")


def _page_source_image_bytes(pdf_document, page_num: int, fitz_lock: threading.Lock) -> tuple[bytes, bool]:
    """(bytes, used_embedded) to OCR for one page. When the page is exactly
    one safe full-page scan (the common case for scanned documents), the
    original embedded image is reused as-is: no render/encode CPU and ~10x
    smaller Vision upload. Anything else falls back to the 300-dpi render.
    used_embedded tells the caller a render retry is still available: on small
    visual-zone print, the upsampled render can OCR better than the native
    scan, so pages that fail on embedded bytes are retried on a render."""
    try:
        with fitz_lock:
            pdf_page: Any = pdf_document[page_num]
            images = pdf_page.get_images(full=True)
            if (len(images) == 1
                    and images[0][1] == 0            # no soft mask
                    and pdf_page.rotation == 0
                    and not pdf_page.get_text().strip()):  # no text/vector overlay to lose
                info = pdf_document.extract_image(images[0][0])
                if (info.get("ext") in ("jpeg", "jpg", "png")
                        and info.get("width", 0) >= 1000
                        and info.get("colorspace", 3) != 4):  # CMYK JPEGs render unreliably
                    return info["image"], True
    except Exception as e:
        logger.warning(f"Extraction de l'image intégrée impossible (page {page_num + 1}), rendu 300 dpi utilisé : {e}")
    return _render_page_png(pdf_document, page_num, fitz_lock), False


async def extract_data_page_by_page(
    file_content: Optional[bytes] = None,
    content_type: str = "",
    file_path: Optional[str] = None,
    progress_callback: Optional[Callable[[int, int], Awaitable[None]]] = None,
) -> List[Dict[str, Any]]:
    """Splits the upload into pages and extracts one document per page.
    The file is taken either from file_path (preferred: nothing held in RAM)
    or from file_content bytes. Pages are OCR'd concurrently (bounded by
    _OCR_MAX_CONCURRENCY); progress_callback(done, total) is awaited after
    each page completes.
    Each page yields either {'page_number', 'data'} or {'page_number', 'error'}."""
    results: List[Dict[str, Any]] = []
    loop = asyncio.get_event_loop()

    async def _report(done: int, total: int):
        if progress_callback is not None:
            try:
                await progress_callback(done, total)
            except Exception as e:
                logger.warning(f"Échec du rappel de progression : {e}")

    if content_type.startswith("image/"):
        logger.info("Traitement en tant que fichier image unique.")
        try:
            if file_content is None:
                if file_path is None:
                    raise ValueError("file_path ou file_content est requis.")
                with open(file_path, "rb") as f:
                    file_content = f.read()
            image_bytes = file_content
            extracted_data = await loop.run_in_executor(
                _ocr_executor, _extract_document_data_from_image_bytes, image_bytes
            )
            # No render alternative exists for a plain image upload.
            extracted_data.pop("_visual_only", None)
            results.append({"page_number": 1, "data": extracted_data})
        except HTTPException as e:
            logger.warning(f"Échec de l'extraction de l'image : {e.detail}")
            results.append({"page_number": 1, "error": e.detail})
        except Exception as e:
            logger.error(f"Erreur inattendue lors du traitement de l'image : {e}")
            results.append({"page_number": 1, "error": "Une erreur serveur inattendue est survenue lors du traitement."})
        await _report(1, 1)

    elif content_type == "application/pdf":
        logger.info("Traitement en tant que fichier PDF.")
        try:
            def _open_pdf():
                if file_path is not None:
                    return fitz.open(file_path)
                return fitz.open(stream=file_content, filetype="pdf")

            pdf_document = await loop.run_in_executor(_ocr_executor, _open_pdf)
            # PyMuPDF is not thread-safe: every access to the document is
            # serialized behind fitz_lock. Page images are harvested one at a
            # time (fast — usually just the embedded scan bytes); only the
            # Vision calls fan out concurrently. The document stays open until
            # the fan-out ends so failed fast-path pages can be re-rendered.
            fitz_lock = threading.Lock()
            try:
                total_pages = len(pdf_document)
                semaphore = asyncio.Semaphore(_OCR_MAX_CONCURRENCY)

                async def _ocr_page(page_index: int) -> Dict[str, Any]:
                    async with semaphore:
                        logger.info(f"--- Traitement de la page PDF {page_index} ---")
                        try:
                            # Harvested lazily inside the semaphore so at most
                            # _OCR_MAX_CONCURRENCY page images exist at once:
                            # render-path pages are 10-25MB PNGs each, so
                            # pre-collecting a whole large PDF could OOM the
                            # single uvicorn process.
                            image_bytes, used_embedded = await loop.run_in_executor(
                                _ocr_executor, _page_source_image_bytes, pdf_document, page_index - 1, fitz_lock
                            )
                            try:
                                # retry_empty=False on the embedded fast path:
                                # the render retry below is the second attempt.
                                extracted_data = await loop.run_in_executor(
                                    _ocr_executor, _extract_document_data_from_image_bytes, image_bytes, not used_embedded
                                )
                                # Pages parsed purely from the visual zone are
                                # image-sensitive: re-read them on the render
                                # so their fields match the render-only path.
                                if used_embedded and extracted_data.get("_visual_only"):
                                    raise HTTPException(status_code=422, detail="revérification sur rendu")
                            except HTTPException:
                                # The upsampled render sometimes OCRs small
                                # visual-zone print better than the native
                                # scan: redo such pages on a 300-dpi render,
                                # so results never regress versus the
                                # render-only path.
                                if not used_embedded:
                                    raise
                                logger.info(f"Nouvelle tentative de la page {page_index} sur un rendu 300 dpi.")
                                rendered = await loop.run_in_executor(
                                    _ocr_executor, _render_page_png, pdf_document, page_index - 1, fitz_lock
                                )
                                extracted_data = await loop.run_in_executor(
                                    _ocr_executor, _extract_document_data_from_image_bytes, rendered
                                )
                            extracted_data.pop("_visual_only", None)
                            logger.info(f"Données extraites avec succès de la page {page_index}.")
                            return {"page_number": page_index, "data": extracted_data}
                        except OldCniFrontMissingExpiry as e:
                            logger.warning(f"Échec de l'extraction des données de la page {page_index}: {e.detail}")
                            return {"page_number": page_index, "error": e.detail, "_pending_front": e.partial_data}
                        except PotentialOldCniVerso as e:
                            logger.warning(f"Échec de l'extraction des données de la page {page_index}: {e.detail}")
                            return {"page_number": page_index, "error": e.detail, "_pending_verso": e.expiration_date}
                        except HTTPException as e:
                            logger.warning(f"Échec de l'extraction des données de la page {page_index}: {e.detail}")
                            return {"page_number": page_index, "error": e.detail}
                        except Exception as e:
                            logger.error(f"Erreur inattendue sur la page {page_index}: {e}")
                            return {"page_number": page_index, "error": "Une erreur serveur inattendue est survenue."}

                tasks = [asyncio.ensure_future(_ocr_page(i + 1)) for i in range(total_pages)]
                try:
                    done_count = 0
                    for future in asyncio.as_completed(tasks):
                        results.append(await future)
                        done_count += 1
                        await _report(done_count, total_pages)
                except BaseException:
                    for task in tasks:
                        task.cancel()
                    raise
            finally:
                # Close under the lock: a cancelled task's executor thread may
                # still be inside a fitz call; closing concurrently would be a
                # native use-after-free.
                with fitz_lock:
                    pdf_document.close()
            # Pages finish out of order; restore document order for the
            # per-page result list and the credit accounting downstream.
            results.sort(key=lambda r: r.get("page_number", 0))
            _pair_split_old_cni(results)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Échec de l'ouverture ou de la lecture du fichier PDF : {e}")
            raise HTTPException(status_code=500, detail=f"Erreur lors de la lecture du fichier PDF : {e}")
    else:
        raise HTTPException(status_code=400, detail=f"Type de fichier non supporté : {content_type}.")

    if not results:
        raise HTTPException(status_code=500, detail="Échec de la production de résultats à partir du fichier téléchargé.")

    return results

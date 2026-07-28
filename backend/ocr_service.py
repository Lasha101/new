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
from datetime import datetime
from typing import Any, List, Dict, Optional
from google.cloud import vision
from fastapi import HTTPException
import logging
import fitz  # PyMuPDF
import unicodedata

logger = logging.getLogger(__name__)

# Initialize Vision client at module level for efficiency
try:
    vision_client = vision.ImageAnnotatorClient()
except Exception as e:
    logger.error(f"🔴 Failed to initialize Google Vision client: {e}")
    vision_client = None


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
        logger.warning(f"Impossible d'analyser la date : '{date_str}' (nettoyée en: '{cleaned_str}')")
        return None


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
        logger.warning(f"Impossible d'analyser la date MRZ : {yymmdd}")
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
    mrz_line1_match = re.search(r'P<FRA([A-Z<]+)<<([A-Z<]+)', mrz_text)
    if mrz_line1_match:
        data["last_name"] = mrz_line1_match.group(1).replace('<', ' ').strip()
        data["first_name"] = ' '.join(mrz_line1_match.group(2).replace('<', ' ').strip().split())

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
    date and full given names from the visual zones."""
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

    if not (surname and card_number and birth_date):
        return None

    expiration_date = _find_old_cni_expiration(full_text)
    if not expiration_date:
        raise HTTPException(
            status_code=422,
            detail=("CNI (ancien format) détectée via sa MRZ, mais la date d'expiration est introuvable : "
                    "la mention 'Carte valable jusqu'au JJ.MM.AAAA' du verso est absente ou illisible sur la page."),
        )

    first_name = _find_visual_given_names(full_text) or mrz_given_names
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

def _extract_document_data_from_image_bytes(image_bytes: bytes) -> dict:
    """Runs Vision OCR on one page image and parses it as a French passport or
    a French national identity card. Raises HTTPException with an explicit
    diagnostic when no supported document can be extracted."""
    if vision_client is None:
        raise HTTPException(status_code=500, detail="Service Google Vision non initialisé.")

    image = vision.Image(content=image_bytes)
    feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)
    image_context = vision.ImageContext(language_hints=['fr'])
    request = vision.AnnotateImageRequest(image=image, features=[feature], image_context=image_context)

    # One retry absorbs transient Vision API errors, which otherwise surface
    # as a spurious "no text detected" failure on a perfectly readable page.
    response = None
    for attempt in (1, 2):
        response = vision_client.annotate_image(request=request)
        if not response.error.message and response.full_text_annotation and response.full_text_annotation.pages:
            break
        logger.warning(f"Réponse Vision incomplète (tentative {attempt}) : {response.error.message or 'aucun texte'}")

    if response.error.message:
        raise HTTPException(status_code=400, detail=f"L'API Google Vision a renvoyé une erreur : {response.error.message}")
    full_text_annotation = response.full_text_annotation
    if not full_text_annotation or not full_text_annotation.pages:
        raise HTTPException(status_code=400, detail="Aucun texte n'a pu être détecté dans le document.")

    raw_text = full_text_annotation.text
    clean_text = re.sub(r'[\n/]', ' ', raw_text)
    full_text = re.sub(r'\s+', ' ', clean_text).strip()

    logger.info("--- Texte OCR extrait complet ---")
    logger.info(full_text)
    logger.info("-----------------------------")

    # A passport MRZ wins over everything else (one document per page); the
    # CNI parsers are tried from the most to the least reliable source.
    data = _parse_passport(full_text)
    if data is None:
        data = _parse_cni_new_mrz(raw_text)
    if data is None:
        data = _parse_cni_old_mrz(raw_text, full_text)
    if data is None:
        data = _parse_cni_new_visual(full_text)
    if data is None:
        raise HTTPException(
            status_code=422,
            detail=("Document non reconnu : aucune MRZ de passeport français (P<FRA...), aucune MRZ de "
                    "carte nationale d'identité (IDFRA...) ni aucun recto de CNI exploitable n'a été "
                    "détecté sur cette page."),
        )

    data["confidence_score"] = _compute_confidence_score(data, full_text_annotation)
    logger.info(f"--- Données analysées ---\n{data}\n--------------------")
    return data


async def extract_data_page_by_page(file_content: bytes, content_type: str) -> List[Dict[str, Any]]:
    """Splits the upload into pages and extracts one document per page.
    Each page yields either {'page_number', 'data'} or {'page_number', 'error'}."""
    results: List[Dict[str, Any]] = []
    loop = asyncio.get_event_loop()

    if content_type.startswith("image/"):
        logger.info("Traitement en tant que fichier image unique.")
        try:
            extracted_data = await loop.run_in_executor(
                None, lambda: _extract_document_data_from_image_bytes(file_content)
            )
            results.append({"page_number": 1, "data": extracted_data})
        except HTTPException as e:
            logger.warning(f"Échec de l'extraction de l'image : {e.detail}")
            results.append({"page_number": 1, "error": e.detail})
        except Exception as e:
            logger.error(f"Erreur inattendue lors du traitement de l'image : {e}")
            results.append({"page_number": 1, "error": "Une erreur serveur inattendue est survenue lors du traitement."})

    elif content_type == "application/pdf":
        logger.info("Traitement en tant que fichier PDF.")
        try:
            pdf_document = fitz.open(stream=file_content, filetype="pdf")
            for page_num in range(len(pdf_document)):
                if not loop.is_running():
                    break

                page_index = page_num + 1
                logger.info(f"--- Traitement de la page PDF {page_index} ---")
                try:
                    pdf_page: Any = pdf_document[page_num]
                    pix = await loop.run_in_executor(None, lambda: pdf_page.get_pixmap(dpi=300))
                    image_bytes = await loop.run_in_executor(None, lambda: pix.tobytes("png"))
                    extracted_data = await loop.run_in_executor(
                        None, lambda: _extract_document_data_from_image_bytes(image_bytes)
                    )
                    results.append({"page_number": page_index, "data": extracted_data})
                    logger.info(f"Données extraites avec succès de la page {page_index}.")
                except HTTPException as e:
                    logger.warning(f"Échec de l'extraction des données de la page {page_index}: {e.detail}")
                    results.append({"page_number": page_index, "error": e.detail})
                except Exception as e:
                    logger.error(f"Erreur inattendue sur la page {page_index}: {e}")
                    results.append({"page_number": page_index, "error": "Une erreur serveur inattendue est survenue."})
            pdf_document.close()
        except Exception as e:
            logger.error(f"Échec de l'ouverture ou de la lecture du fichier PDF : {e}")
            raise HTTPException(status_code=500, detail=f"Erreur lors de la lecture du fichier PDF : {e}")
    else:
        raise HTTPException(status_code=400, detail=f"Type de fichier non supporté : {content_type}.")

    if not results:
        raise HTTPException(status_code=500, detail="Échec de la production de résultats à partir du fichier téléchargé.")

    return results

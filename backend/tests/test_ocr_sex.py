"""Spec tests of the source of the « Sexe » column: the holder's sex is read
from the machine-readable zone only — passport line 2 character 21, new-format
CNI (TD1) line 2 character 8, old-format CNI line 2 character 35 — and kept
only when it is F or M. Anything else ('X', '<'), or a page without an MRZ,
leaves it empty: it is never guessed, neither from the printed « Sexe » of the
visual zone nor from a first name.

All identities in this file are fictional; every MRZ line carries valid ICAO
check digits.
"""
import re
from types import SimpleNamespace

import pytest

import ocr_service


def _flatten(raw: str) -> str:
    """The page text as the page extraction hands it to the parsers."""
    return re.sub(r"\s+", " ", re.sub(r"[\n/]", " ", raw)).strip()


def _with(line: str, position: int, character: str) -> str:
    """`line` with its character number `position` (counted from 1, as the
    MRZ specification does) replaced by `character`."""
    return line[:position - 1] + character + line[position:]


class _FakeVisionClient:
    """Vision stand-in: answers every page with the given text, so the whole
    page cascade runs without a network call."""
    def __init__(self, text: str):
        self._text = text

    def annotate_image(self, request):
        return SimpleNamespace(
            error=SimpleNamespace(message=""),
            full_text_annotation=SimpleNamespace(text=self._text, pages=[SimpleNamespace(blocks=[])]),
        )


def _extract_page(monkeypatch, text: str) -> dict:
    monkeypatch.setattr(ocr_service, "vision_client", _FakeVisionClient(text))
    return ocr_service._extract_document_data_from_image_bytes(b"fake-image-bytes")


# --- Passport (TD3, 2 x 44): line 2, character 21 -------------------------------

PASSPORT_L1 = "P<FRAMARTIN<<CLAIRE" + "<" * 25
PASSPORT_L2 = "07XY123455FRA9002155F3206054" + "<" * 14 + "06"


def passport_page(line2: str = PASSPORT_L2, visual: str = "") -> str:
    return f"PASSEPORT\nRÉPUBLIQUE FRANÇAISE\n{visual}{PASSPORT_L1}\n{line2}\n"


def test_passport_fixture_is_a_44_character_line_with_the_sex_at_21():
    assert len(PASSPORT_L1) == len(PASSPORT_L2) == 44
    assert PASSPORT_L2[21 - 1] == "F"


@pytest.mark.parametrize("character, expected", [("F", "F"), ("M", "M"), ("X", None), ("<", None)])
def test_passport_sex_is_line2_character_21(character, expected):
    data = ocr_service._parse_passport(_flatten(passport_page(_with(PASSPORT_L2, 21, character))))
    assert data is not None                      # an unspecified sex never fails the page
    assert data["sex"] == expected
    # the characters around it are still read as before
    assert (data["passport_number"], data["birth_date"], data["expiration_date"]) == \
        ("07XY12345", "1990-02-15", "2032-06-05")
    assert (data["last_name"], data["first_name"]) == ("MARTIN", "CLAIRE")


def test_passport_sex_never_taken_from_the_visual_zone():
    page = passport_page(_with(PASSPORT_L2, 21, "<"), visual="Sexe / Sex\nF\n")
    assert ocr_service._parse_passport(_flatten(page))["sex"] is None


def test_cropped_passport_reads_character_21_from_the_checksummed_tail():
    """The crop takes the left of each MRZ line; character 21 is still there,
    in the tail whose two date check digits are verified."""
    cropped = (
        "PASSEPORT\nRÉPUBLIQUE FRANÇAISE\nNom\nMARTIN\nPrénoms\nClaire\n"
        "Passeport\n07XY12345\n"
        + PASSPORT_L1[3:] + "\n"                             # 'P<F' cropped away
        + _with(PASSPORT_L2, 21, "M")[3:] + "\n"             # '07X' cropped away
    )
    data = ocr_service._parse_passport(_flatten(cropped))
    assert data is not None
    assert data["passport_number"] == "07XY12345"            # from the visual zone
    assert data["sex"] == "M"


def test_passport_page_cascade_carries_the_sex(monkeypatch):
    data = _extract_page(monkeypatch, passport_page())
    assert data["passport_number"] == "07XY12345"
    assert data["sex"] == "F"


# --- New-format CNI (TD1, 3 x 30): line 2, character 8 --------------------------

TD1_L1 = "IDFRAX4RTBPFW46" + "<" * 15
TD1_L2 = "9002155F3406050FRA" + "<" * 11 + "4"
TD1_L3 = "MARTIN<<CLAIRE" + "<" * 16


def new_cni_back(line2: str = TD1_L2) -> str:
    return f"RÉPUBLIQUE FRANÇAISE\n{TD1_L1}\n{line2}\n{TD1_L3}\n"


def test_new_cni_fixture_is_three_30_character_lines_with_the_sex_at_8():
    assert len(TD1_L1) == len(TD1_L2) == len(TD1_L3) == 30
    assert TD1_L2[8 - 1] == "F"


@pytest.mark.parametrize("character, expected", [("F", "F"), ("M", "M"), ("X", None), ("<", None)])
def test_new_cni_sex_is_line2_character_8(character, expected):
    data = ocr_service._parse_cni_new_mrz(new_cni_back(_with(TD1_L2, 8, character)))
    assert data is not None
    assert data["sex"] == expected
    assert (data["passport_number"], data["birth_date"], data["expiration_date"]) == \
        ("X4RTBPFW4", "1990-02-15", "2034-06-05")


def test_new_cni_page_cascade_carries_the_sex(monkeypatch):
    data = _extract_page(monkeypatch, new_cni_back(_with(TD1_L2, 8, "M")))
    assert data["passport_number"] == "X4RTBPFW4"
    assert data["sex"] == "M"


def test_new_cni_front_alone_has_no_mrz_so_the_sex_stays_empty(monkeypatch):
    """The front of a new-format card prints « Sexe / Sex F », but carries no
    MRZ: the document is extracted from its visual zone, the sex is not."""
    front = (
        "RÉPUBLIQUE FRANÇAISE\nCARTE NATIONALE D'IDENTITÉ / IDENTITY CARD\n"
        "NOM / Surname\nMARTIN\nPrénoms / Given names\nCLAIRE\nSEXE / Sex\nF\n"
        "NATIONALITÉ / Nationality\nFRA\nDATE DE NAISS. / Date of birth\n15 02 1990\n"
        "N° DU DOCUMENT / Document No\nX4RTBPFW4\nDATE D'EXPIR. / Expiry date\n05 06 2034\n"
    )
    data = _extract_page(monkeypatch, front)
    assert (data["last_name"], data["first_name"], data["passport_number"]) == ("MARTIN", "CLAIRE", "X4RTBPFW4")
    assert data["sex"] is None


# --- Old-format CNI (2 x 36): line 2, character 35 ------------------------------

TD2_L1 = "IDFRAMARTIN" + "<" * 19 + "060123"
TD2_L2 = "0601234567891CLAIRE<<<<<<<<9002153F4"
OLD_FRONT = "RÉPUBLIQUE FRANÇAISE\nCARTE NATIONALE D'IDENTITÉ N°: 060123456789\nNom: MARTIN\nPrénom(s): CLAIRE\n"
OLD_VERSO = "Adresse:\n1 RUE DES LILAS\n75000 PARIS\nCarte valable jusqu'au : 05.06.2030\n"


def old_cni(line2: str = TD2_L2, verso: str = OLD_VERSO) -> str:
    return f"{OLD_FRONT}{TD2_L1}\n{line2}\n{verso}"


def test_old_cni_fixture_is_two_36_character_lines_with_the_sex_at_35():
    assert len(TD2_L1) == len(TD2_L2) == 36
    assert TD2_L2[35 - 1] == "F"


@pytest.mark.parametrize("character, expected", [("F", "F"), ("M", "M"), ("X", None)])
def test_old_cni_sex_is_line2_character_35(character, expected):
    raw = old_cni(_with(TD2_L2, 35, character))
    data = ocr_service._parse_cni_old_mrz(raw, _flatten(raw))
    assert data is not None
    assert data["sex"] == expected
    assert (data["passport_number"], data["birth_date"], data["expiration_date"]) == \
        ("060123456789", "1990-02-15", "2030-06-05")


def test_old_cni_damaged_line2_still_gives_its_sex():
    """The tolerant pass (a '0' read as 'O' in a numeric position) reads the
    same character 35."""
    raw = old_cni("O601234567891CLAIRE<<<<<<<<9002153M4")
    data = ocr_service._parse_cni_old_mrz(raw, _flatten(raw))
    assert data["passport_number"] == "060123456789"
    assert data["sex"] == "M"


def test_old_cni_page_cascade_carries_the_sex(monkeypatch):
    data = _extract_page(monkeypatch, old_cni())
    assert data["passport_number"] == "060123456789"
    assert data["sex"] == "F"


def test_old_cni_split_recto_verso_keeps_the_sex_of_the_recto(monkeypatch):
    """Recto and verso on two pages: the MRZ — hence the sex — is on the recto,
    and the merged document keeps it."""
    with pytest.raises(ocr_service.OldCniFrontMissingExpiry) as front:
        _extract_page(monkeypatch, old_cni(_with(TD2_L2, 35, "M"), verso=""))
    assert front.value.partial_data["sex"] == "M"
    with pytest.raises(ocr_service.PotentialOldCniVerso) as verso:
        _extract_page(monkeypatch, OLD_VERSO)

    results = [
        {"page_number": 1, "error": front.value.detail, "_pending_front": front.value.partial_data},
        {"page_number": 2, "error": verso.value.detail, "_pending_verso": verso.value.expiration_date},
    ]
    ocr_service._pair_split_old_cni(results)
    assert results[0]["data"]["sex"] == "M"
    assert results[0]["data"]["expiration_date"] == "2030-06-05"
    assert results[1] == {"page_number": 2, "verso_of_page": 1}

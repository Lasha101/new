"""Spec tests of the document-treatment enhancements:

- tolerant old-CNI (TD2) MRZ matching: '0' misread as 'O' in numeric positions,
  and MRZ lines split into fragments (sometimes emitted out of order) by the OCR;
- recovery of a passport whose scan crops the left edge of the MRZ (checksummed
  partial line 2 + anchorless name fragment cross-checked in the visual zone);
- pairing of an old-format CNI scanned recto and verso on two separate adjacent
  pages (the front alone has no expiration date, the verso alone is otherwise
  unrecognizable). A page still never yields more than one document.

All identities in this file are fictional.
"""
import asyncio
import uuid
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

import crud
import main
import ocr_service
from tests.helpers import make_user

# Old-format CNI MRZ, fictional holder MARTIN Claire, card 060123456789,
# born 15/02/1990.
TD2_L1 = "IDFRAMARTIN" + "<" * 19 + "060123"
TD2_L2 = "0601234567891CLAIRE<<<<<<<<9002153F4"

FRONT_VISUAL = (
    "RÉPUBLIQUE FRANÇAISE\nCARTE NATIONALE D'IDENTITÉ N°: 060123456789\n"
    "Nom: MARTIN\nPrénom(s): CLAIRE\nNé(e) le: 15.02.1990\n"
)
VERSO_VISUAL = (
    "Adresse:\n1 RUE DES LILAS\n75000 PARIS\n"
    "Carte valable jusqu'au : 05.06.2030\ndélivrée le : 06.06.2015\npar : PREFECTURE\n"
)

EXPECTED_IDENTITY = {
    "first_name": "CLAIRE", "last_name": "MARTIN",
    "passport_number": "060123456789", "nationality": "Française",
    "birth_date": "1990-02-15",
}


def _flatten(raw: str) -> str:
    import re
    return re.sub(r"\s+", " ", re.sub(r"[\n/]", " ", raw)).strip()


def parse_old_cni(raw_text: str):
    return ocr_service._parse_cni_old_mrz(raw_text, _flatten(raw_text))


# --- Tolerant TD2 MRZ matching -------------------------------------------------

def test_complete_single_page_old_cni_still_parses_strictly():
    data = parse_old_cni(FRONT_VISUAL + TD2_L1 + "\n" + TD2_L2 + "\n" + VERSO_VISUAL)
    assert data == dict(EXPECTED_IDENTITY, expiration_date="2030-06-05")


@pytest.mark.parametrize("damaged_line2", [
    "0601234567891CLAIRE<<<<<<<<9002153FO",   # final check digit '0' read as 'O'
    "O601234567891CLAIRE<<<<<<<<9002153F4",   # card-number digit '0' read as 'O'
])
def test_zero_misread_as_letter_o_in_numeric_mrz_positions(damaged_line2):
    data = parse_old_cni(FRONT_VISUAL + TD2_L1 + "\n" + damaged_line2 + "\n" + VERSO_VISUAL)
    assert data is not None
    assert data["passport_number"] == "060123456789"
    assert data["birth_date"] == "1990-02-15"


def test_mrz_line1_split_into_fragments_with_dropped_fillers():
    raw = FRONT_VISUAL + "IDFRAMARTIN<<<\n<<060123\n" + TD2_L2 + "\n" + VERSO_VISUAL
    data = parse_old_cni(raw)
    assert data is not None
    assert data["last_name"] == "MARTIN"


def test_mrz_line2_fragments_emitted_in_reversed_order():
    raw = FRONT_VISUAL + TD2_L1 + "\n<<9002153F4\n0601234567891CLAIRE<<<<<<\n" + VERSO_VISUAL
    data = parse_old_cni(raw)
    assert data is not None
    assert data["passport_number"] == "060123456789"
    assert data["birth_date"] == "1990-02-15"


def test_letter_o_stays_a_letter_inside_the_name_field():
    line2 = "0601234567891CORALIE<<<<<<<9002153F4"
    data = parse_old_cni(FRONT_VISUAL.replace("CLAIRE", "CORALIE") + TD2_L1 + "\n" + line2 + "\n" + VERSO_VISUAL)
    assert data["first_name"] == "CORALIE"


# --- Front missing its expiration date -----------------------------------------

def test_front_without_expiry_raises_carrier_exception_with_identity():
    with pytest.raises(ocr_service.OldCniFrontMissingExpiry) as exc_info:
        parse_old_cni(FRONT_VISUAL + TD2_L1 + "\n" + TD2_L2 + "\n")
    exc = exc_info.value
    assert exc.status_code == 422
    assert exc.detail == ocr_service._OLD_CNI_MISSING_EXPIRY_DETAIL
    assert exc.partial_data == EXPECTED_IDENTITY


def test_front_without_expiry_nor_given_names_keeps_plain_422():
    line2_no_names = "0601234567891<<<<<<<<<<<<<<9002153F4"
    raw = "RÉPUBLIQUE FRANÇAISE\n" + TD2_L1 + "\n" + line2_no_names + "\n"
    with pytest.raises(HTTPException) as exc_info:
        parse_old_cni(raw)
    assert not isinstance(exc_info.value, ocr_service.OldCniFrontMissingExpiry)
    assert exc_info.value.detail == ocr_service._OLD_CNI_MISSING_EXPIRY_DETAIL


# --- Verso detection (full extraction cascade, Vision mocked) ------------------

class _FakeVisionClient:
    def __init__(self, text: str):
        self._text = text

    def annotate_image(self, request):
        return SimpleNamespace(
            error=SimpleNamespace(message=""),
            full_text_annotation=SimpleNamespace(
                text=self._text, pages=[SimpleNamespace(blocks=[])]),
        )


def test_lone_verso_page_raises_potential_verso_with_standard_message(monkeypatch):
    monkeypatch.setattr(ocr_service, "vision_client", _FakeVisionClient(VERSO_VISUAL))
    with pytest.raises(ocr_service.PotentialOldCniVerso) as exc_info:
        ocr_service._extract_document_data_from_image_bytes(b"fake-image-bytes")
    assert exc_info.value.detail == ocr_service._UNRECOGNIZED_DOCUMENT_DETAIL
    assert exc_info.value.expiration_date == "2030-06-05"


def test_lone_front_page_carries_confidence_scored_identity(monkeypatch):
    monkeypatch.setattr(ocr_service, "vision_client",
                        _FakeVisionClient(FRONT_VISUAL + TD2_L1 + "\n" + TD2_L2 + "\n"))
    with pytest.raises(ocr_service.OldCniFrontMissingExpiry) as exc_info:
        ocr_service._extract_document_data_from_image_bytes(b"fake-image-bytes")
    assert exc_info.value.partial_data == dict(EXPECTED_IDENTITY, confidence_score=0.0)


def test_unrecognized_page_without_validity_mention_keeps_plain_422(monkeypatch):
    monkeypatch.setattr(ocr_service, "vision_client", _FakeVisionClient("Page blanche sans document."))
    with pytest.raises(HTTPException) as exc_info:
        ocr_service._extract_document_data_from_image_bytes(b"fake-image-bytes")
    assert not isinstance(exc_info.value, ocr_service.PotentialOldCniVerso)
    assert exc_info.value.detail == ocr_service._UNRECOGNIZED_DOCUMENT_DETAIL


# --- Pairing pass ---------------------------------------------------------------

def _front_result(page, **identity):
    return {"page_number": page, "error": ocr_service._OLD_CNI_MISSING_EXPIRY_DETAIL,
            "_pending_front": dict(EXPECTED_IDENTITY, **identity)}


def _verso_result(page, expiration="2030-06-05"):
    return {"page_number": page, "error": ocr_service._UNRECOGNIZED_DOCUMENT_DETAIL,
            "_pending_verso": expiration}


def test_pairing_merges_front_with_following_verso():
    results = [_front_result(1), _verso_result(2)]
    ocr_service._pair_split_old_cni(results)
    assert results[0] == {"page_number": 1,
                          "data": dict(EXPECTED_IDENTITY, expiration_date="2030-06-05")}
    assert results[1] == {"page_number": 2, "verso_of_page": 1}


def test_pairing_falls_back_to_preceding_verso():
    results = [_verso_result(1), _front_result(2)]
    ocr_service._pair_split_old_cni(results)
    assert results[1]["data"]["expiration_date"] == "2030-06-05"
    assert results[0] == {"page_number": 1, "verso_of_page": 2}


def test_each_verso_is_consumed_at_most_once():
    results = [_front_result(1), _verso_result(2), _front_result(3, last_name="AUTRE")]
    ocr_service._pair_split_old_cni(results)
    assert results[0]["data"]["expiration_date"] == "2030-06-05"
    assert results[1] == {"page_number": 2, "verso_of_page": 1}
    # the second front stays a failure with today's message
    assert results[2]["error"] == ocr_service._OLD_CNI_MISSING_EXPIRY_DETAIL
    assert "_pending_front" not in results[2]


def test_unpaired_pages_keep_their_original_errors_without_markers():
    results = [_front_result(1), {"page_number": 5, "error": "autre échec"}, _verso_result(9)]
    ocr_service._pair_split_old_cni(results)
    assert results[0] == {"page_number": 1, "error": ocr_service._OLD_CNI_MISSING_EXPIRY_DETAIL}
    assert results[2] == {"page_number": 9, "error": ocr_service._UNRECOGNIZED_DOCUMENT_DETAIL}


def test_non_adjacent_verso_is_never_paired():
    results = [_front_result(1), {"page_number": 2, "error": "x"}, _verso_result(3)]
    ocr_service._pair_split_old_cni(results)
    assert "error" in results[0] and "error" in results[2]


# --- Passport with the left edge of the MRZ cropped -----------------------------

CROPPED_PASSPORT = (
    "PASSEPORT\nRÉPUBLIQUE FRANÇAISE\nNom\nDURAND\nPrénoms\nPaul, Henri\n"
    "Passeport\n14CD56789\n"
    "RADURAND<<PAUL<HENRI<<<<<<<<<<<<<<<\n"        # 'P<F' of 'P<FRA' cropped away
    "C123456FRA8503150M3003149<<<<<<<<<<<<04\n"    # document number cropped away
)


def test_mrz_check_digit_matches_icao_hand_computation():
    assert ocr_service._mrz_check_digit("850315") == "0"
    assert ocr_service._mrz_check_digit("300314") == "9"


def test_cropped_passport_recovers_all_fields():
    data = ocr_service._parse_passport(CROPPED_PASSPORT)
    assert data is not None
    assert data["last_name"] == "DURAND"          # anchor residue 'RA' stripped
    assert data["first_name"] == "PAUL HENRI"
    assert data["passport_number"] == "14CD56789"  # from the visual zone
    assert data["birth_date"] == "1985-03-15"
    assert data["expiration_date"] == "2030-03-14"
    assert data["nationality"] == "Française"


def test_partial_mrz_line2_rejected_when_a_check_digit_fails():
    corrupted = CROPPED_PASSPORT.replace("FRA8503150M", "FRA8503151M")
    assert ocr_service._parse_passport(corrupted) is None


# --- Job aggregation: verso entries are neither successes nor failures ----------

def test_job_skips_verso_entries_and_charges_only_successes(db_session, monkeypatch):
    user = make_user(db_session, "ocruser", page_credits=10)
    job_id = str(uuid.uuid4())
    crud.create_ocr_job(db=db_session, job_id=job_id, user_id=user["id"], file_name="split.pdf")

    merged_data = dict(EXPECTED_IDENTITY, expiration_date="2030-06-05", confidence_score=0.91)

    async def fake_extract(file_path, content_type, progress_callback=None):
        return [
            {"page_number": 1, "data": dict(merged_data)},
            {"page_number": 2, "verso_of_page": 1},
            {"page_number": 3, "error": ocr_service._UNRECOGNIZED_DOCUMENT_DETAIL},
        ]

    monkeypatch.setattr(ocr_service, "extract_data_page_by_page", fake_extract)
    asyncio.run(main._run_ocr_extraction_job(
        db_session, job_id, "/tmp/unused", "application/pdf", "Rome", user["id"]))

    job = crud.get_ocr_job(db_session, job_id)
    assert [s["page_number"] for s in job["successes"]] == [1]
    assert [f["page_number"] for f in job["failures"]] == [3]

    saved = job["successes"][0]["data"]
    assert saved["last_name"] == "MARTIN"
    assert saved["expiration_date"] == "2030-06-05"

    updated_user = crud.get_user(db_session, user["id"])
    assert updated_user["page_credits"] == 9          # 1 document charged: no credit for the verso or the failure
    assert updated_user["uploaded_pages_count"] == 3  # every processed page is still counted

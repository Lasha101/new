"""A user pays one credit per successful extraction, and nothing for a failure.

The user's own example: 10 credits, an extraction ending with 2 failures and
3 successes → 3 credits paid, 7 left. « Pages Traitées » still counts every
processed page.

All identities in this file are fictional.
"""
import asyncio
import uuid

import crud
import main
import ocr_service
from tests.helpers import make_user


def _identity(number: str, last_name: str) -> dict:
    return {
        "first_name": "CLAIRE", "last_name": last_name, "passport_number": number,
        "nationality": "Française", "birth_date": "1990-02-15",
        "expiration_date": "2032-06-05", "confidence_score": 0.93,
    }


def _run_job(db_session, monkeypatch, user_id, pages, destination="Rome"):
    async def fake_extract(file_path, content_type, progress_callback=None):
        if isinstance(pages, Exception):
            raise pages
        return pages

    job_id = str(uuid.uuid4())
    crud.create_ocr_job(db=db_session, job_id=job_id, user_id=user_id, file_name="lot.pdf")
    monkeypatch.setattr(ocr_service, "extract_data_page_by_page", fake_extract)
    asyncio.run(main._run_ocr_extraction_job(
        db_session, job_id, "/tmp/unused", "application/pdf", destination, user_id))
    return crud.get_ocr_job(db_session, job_id), crud.get_user(db_session, user_id)


def test_three_successes_two_failures_cost_three_credits(db_session, monkeypatch):
    user = make_user(db_session, "payer", page_credits=10)
    pages = [
        {"page_number": 1, "data": _identity("06AB12345", "MARTIN")},
        {"page_number": 2, "error": ocr_service._UNRECOGNIZED_DOCUMENT_DETAIL},
        {"page_number": 3, "data": _identity("07CD23456", "DURAND")},
        # Same number and destination as page 1: refused at save time.
        {"page_number": 4, "data": _identity("06AB12345", "MARTIN")},
        {"page_number": 5, "data": _identity("08EF34567", "PETIT")},
    ]

    job, updated_user = _run_job(db_session, monkeypatch, user["id"], pages)

    assert [s["page_number"] for s in job["successes"]] == [1, 3, 5]
    assert [f["page_number"] for f in job["failures"]] == [2, 4]
    assert updated_user["page_credits"] == 7
    assert updated_user["uploaded_pages_count"] == 5


def test_only_failures_cost_nothing(db_session, monkeypatch):
    user = make_user(db_session, "unlucky", page_credits=10)
    pages = [
        {"page_number": 1, "error": ocr_service._UNRECOGNIZED_DOCUMENT_DETAIL},
        {"page_number": 2, "error": ocr_service._UNRECOGNIZED_DOCUMENT_DETAIL},
    ]

    job, updated_user = _run_job(db_session, monkeypatch, user["id"], pages)

    assert job["successes"] == []
    assert len(job["failures"]) == 2
    assert updated_user["page_credits"] == 10
    assert updated_user["uploaded_pages_count"] == 2


def test_failed_extraction_costs_nothing(db_session, monkeypatch):
    user = make_user(db_session, "crashed", page_credits=10)

    job, updated_user = _run_job(db_session, monkeypatch, user["id"], RuntimeError("OCR indisponible"))

    assert job["successes"] == []
    assert updated_user["page_credits"] == 10
    assert updated_user["uploaded_pages_count"] == 0

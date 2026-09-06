"""Upload validation: size, type by magic bytes, and the filename.

Every test that reaches the endpoint stubs the background task. The OCR job is
not what is under test here, and letting it run would make a real Google Vision
call — money, and a network dependency in a unit suite.
"""
import os
import re

import pytest

import file_validation
import main
from tests.helpers import auth_headers, make_user

FRONTEND_SNIFFER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "frontend", "src", "upload", "fileSniff.js",
)

# Smallest byte strings that are unambiguously each format.
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 60
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 60
PDF = b"%PDF-1.4\n" + b"0" * 60
GIF = b"GIF89a" + b"\x00" * 60
WEBP = b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 52
TIFF_LE = b"II\x2a\x00" + b"\x00" * 60
TIFF_BE = b"MM\x00\x2a" + b"\x00" * 60
# A real iPhone ftyp box: major brand mif1, with heic among the compatible ones.
HEIC = b"\x00\x00\x00\x20ftypmif1\x00\x00\x00\x00mif1heic" + b"\x00" * 40
# AVIF shares the container and also lists mif1 — it must not be taken for HEIC.
AVIF = b"\x00\x00\x00\x20ftypavif\x00\x00\x00\x00avifmif1" + b"\x00" * 40
NOT_A_DOCUMENT = b"MZ\x90\x00" + b"\x00" * 60          # a Windows executable
ZIP = b"PK\x03\x04" + b"\x00" * 60


@pytest.fixture()
def no_background_ocr(monkeypatch):
    """Replaces the OCR task with a no-op that still deletes the spool file,
    exactly as the real one does."""
    async def fake_task(job_id, file_path, content_type, destination, user_id):
        try:
            os.unlink(file_path)
        except OSError:
            pass

    monkeypatch.setattr(main, "run_ocr_extraction_task", fake_task)
    return fake_task


# --- The sniffer itself --------------------------------------------------

@pytest.mark.parametrize(
    "data, expected",
    [
        (JPEG, "jpeg"), (PNG, "png"), (PDF, "pdf"), (GIF, "gif"),
        (WEBP, "webp"), (TIFF_LE, "tiff"), (TIFF_BE, "tiff"),
        (HEIC, "heic"), (AVIF, "avif"),
        (NOT_A_DOCUMENT, "unknown"), (ZIP, "unknown"), (b"", "unknown"),
    ],
)
def test_the_sniffer_identifies_each_format_from_its_bytes(data, expected):
    assert file_validation.sniff_file_type(data) == expected


def test_avif_is_not_mistaken_for_heic():
    """Both declare the mif1 brand. Reading only the major brand, or only the
    first match, gets this wrong."""
    assert file_validation.sniff_file_type(AVIF) == "avif"
    assert file_validation.sniff_file_type(HEIC) == "heic"


def test_the_allow_list_matches_the_frontend_sniffer():
    """The backend allow-list and the browser's sniffer must recognise the same
    formats. If they drift, a document the app happily compresses is rejected
    on arrival — so this reads the JavaScript rather than trusting a comment."""
    source = open(FRONTEND_SNIFFER, encoding="utf-8").read()
    returned = set(re.findall(r"return '([a-z]+)';", source))
    frontend_types = {t for t in returned if t != "unknown"}
    assert frontend_types == file_validation.ALLOWED_TYPES, (
        f"frontend recognises {sorted(frontend_types)}, "
        f"backend accepts {sorted(file_validation.ALLOWED_TYPES)}"
    )


# --- Through the endpoint ------------------------------------------------

def _upload(client, user, content, filename="doc.pdf", content_type="application/pdf"):
    return client.post(
        "/passports/upload-and-extract/",
        files={"file": (filename, content, content_type)},
        headers=auth_headers(user),
    )


@pytest.mark.parametrize(
    "data, filename, declared",
    [
        (JPEG, "photo.jpg", "image/jpeg"),
        (PNG, "scan.png", "image/png"),
        (PDF, "doc.pdf", "application/pdf"),
        (HEIC, "IMG_0001.HEIC", "image/heic"),
        (GIF, "anim.gif", "image/gif"),
        (WEBP, "shot.webp", "image/webp"),
        (TIFF_LE, "scan.tiff", "image/tiff"),
    ],
)
def test_every_type_the_frontend_can_send_is_still_accepted(
    client, db_session, no_background_ocr, data, filename, declared
):
    """Nothing that works today may become rejected. HEIC matters especially:
    when client-side conversion fails, imagePrep.js uploads the ORIGINAL HEIC
    rather than dropping the file, so the server has to take it."""
    make_user(db_session, "uploader", page_credits=10)
    response = _upload(client, "uploader", data, filename, declared)
    assert response.status_code == 200, f"{filename} was refused: {response.text}"


def test_a_disallowed_type_is_rejected_even_with_forged_extension_and_content_type(
    client, db_session, no_background_ocr
):
    """The two things a client controls are set to look legitimate; only the
    bytes give it away."""
    make_user(db_session, "forger", page_credits=10)
    response = _upload(client, "forger", NOT_A_DOCUMENT, "innocent.pdf", "application/pdf")
    assert response.status_code == 400, response.text
    assert "Type de fichier non supporté" in response.json()["detail"]


def test_a_zip_disguised_as_a_pdf_is_rejected(client, db_session, no_background_ocr):
    """PyMuPDF opens by content, not by extension, and will happily open a ZIP
    as a document — so a ZIP with a .pdf name used to reach the parser."""
    make_user(db_session, "zipper", page_credits=10)
    response = _upload(client, "zipper", ZIP, "report.pdf", "application/pdf")
    assert response.status_code == 400


def test_the_effective_content_type_comes_from_the_bytes_not_the_header(
    client, db_session, monkeypatch
):
    """A PNG announced as a PDF must be processed as a PNG."""
    make_user(db_session, "liar", page_credits=10)
    seen = {}

    async def capture(job_id, file_path, content_type, destination, user_id):
        seen["content_type"] = content_type
        try:
            os.unlink(file_path)
        except OSError:
            pass

    monkeypatch.setattr(main, "run_ocr_extraction_task", capture)
    response = _upload(client, "liar", PNG, "actually.pdf", "application/pdf")
    assert response.status_code == 200, response.text
    assert seen["content_type"] == "image/png"


def test_an_oversized_file_is_rejected(client, db_session, no_background_ocr, monkeypatch):
    make_user(db_session, "bigfile", page_credits=10)
    monkeypatch.setattr(main.config, "MAX_UPLOAD_BYTES", 1024)
    oversized = PDF + b"x" * 4096
    response = _upload(client, "bigfile", oversized, "big.pdf", "application/pdf")
    assert response.status_code == 413, response.text
    assert "trop volumineux" in response.json()["detail"].lower()


def test_an_oversized_file_leaves_no_spool_behind(client, db_session, no_background_ocr, monkeypatch):
    """The rejection happens mid-stream, after the temp file exists. It must
    still be cleaned up."""
    make_user(db_session, "bigfile2", page_credits=10)
    monkeypatch.setattr(main.config, "MAX_UPLOAD_BYTES", 1024)
    before = set(_spool_files())
    _upload(client, "bigfile2", PDF + b"x" * 4096, "big.pdf", "application/pdf")
    assert set(_spool_files()) == before


def test_an_empty_file_is_rejected(client, db_session, no_background_ocr):
    make_user(db_session, "empty", page_credits=10)
    response = _upload(client, "empty", b"", "nothing.pdf", "application/pdf")
    assert response.status_code == 400


# --- The filename --------------------------------------------------------

@pytest.mark.parametrize(
    "raw, expected",
    [
        ("../../etc/passwd", "passwd"),
        ("..\\..\\windows\\system32\\config", "config"),
        ("/etc/shadow", "shadow"),
        ("normal.pdf", "normal.pdf"),
        ("with\x00null.pdf", "withnull.pdf"),
        ("..", "document"),
        (".", "document"),
        ("", "document"),
        (None, "document"),
        ("   ", "   "),
    ],
)
def test_safe_filename(raw, expected):
    assert file_validation.safe_filename(raw) == expected


def test_a_very_long_filename_is_capped_and_keeps_its_extension():
    name = "a" * 500 + ".pdf"
    safe = file_validation.safe_filename(name)
    assert len(safe) <= 120
    assert safe.endswith(".pdf")


def test_a_path_traversal_filename_is_stored_flattened(client, db_session, no_background_ocr):
    """The name is shown in the job list, so it is kept — but only its
    basename, and never in a form that could address a directory."""
    make_user(db_session, "traverse", page_credits=10)
    response = _upload(client, "traverse", PDF, "../../../etc/passwd", "application/pdf")
    assert response.status_code == 200, response.text
    assert response.json()["file_name"] == "passwd"
    assert "/" not in response.json()["file_name"]


def test_a_null_byte_filename_is_accepted_and_sanitised(client, db_session, no_background_ocr):
    make_user(db_session, "nullbyte", page_credits=10)
    response = _upload(client, "nullbyte", PDF, "evil\x00.pdf", "application/pdf")
    assert response.status_code == 200, response.text
    assert "\x00" not in response.json()["file_name"]


def _spool_files():
    import tempfile
    root = tempfile.gettempdir()
    try:
        return [n for n in os.listdir(root) if n.startswith(main.OCR_SPOOL_PREFIX)]
    except OSError:
        return []

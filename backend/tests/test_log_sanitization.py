"""No identity data in the logs.

The finding this fixes: `ocr_service.py` used to log the COMPLETE OCR text of
every page at INFO — surname, given names, date of birth, expiry, nationality,
document number and the raw MRZ, which encodes all of it again — and then log
the fully parsed record on the next line. Under systemd that goes to the
journal, which persists on disk for weeks and which the application never
cleans. It was the strongest disproof of "documents are never stored", because
unlike the spooled file it had no deletion path at all.

Two layers are tested here: the call sites (the real fix) and the redaction
filter (the safety net behind them).
"""
import io
import logging

import pytest

import log_redaction

# A realistic TD3 passport MRZ and the fields it encodes.
MRZ_LINE_1 = "P<FRADUPONT<LEVY<<ELODIE<MARIE<<<<<<<<<<<<<<"
MRZ_LINE_2 = "12AB345670FRA9005174F3001025<<<<<<<<<<<<<<04"
SURNAME = "DUPONT-LEVY"
GIVEN_NAME = "ELODIE"
DOCUMENT_NUMBER = "12AB34567"
CNI_NUMBER = "123456789012"
BIRTH_DATE = "17/05/1990"


@pytest.fixture()
def captured_root_log():
    """Attaches a stream handler to the root logger with the redaction filter
    installed exactly as main.py installs it."""
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.DEBUG)
    root = logging.getLogger()
    previous_level = root.level
    root.setLevel(logging.DEBUG)
    root.addHandler(handler)
    log_redaction.install(root)
    try:
        yield stream
    finally:
        root.removeHandler(handler)
        root.setLevel(previous_level)


# --- The filter ----------------------------------------------------------

@pytest.mark.parametrize(
    "secret",
    [MRZ_LINE_1, MRZ_LINE_2, DOCUMENT_NUMBER, CNI_NUMBER, BIRTH_DATE, "1990-05-17"],
)
def test_the_filter_redacts_every_identity_shape(secret):
    assert secret not in log_redaction.redact(f"job 42: {secret}")


def test_the_filter_catches_interpolated_arguments(captured_root_log):
    """`logger.info("%s", value)` must be caught as surely as an f-string: the
    filter reads the FORMATTED message, not the template."""
    logging.getLogger("test.interp").info("document %s", DOCUMENT_NUMBER)
    assert DOCUMENT_NUMBER not in captured_root_log.getvalue()


def test_the_filter_catches_a_child_logger(captured_root_log):
    """It is installed on the handlers, not on the root logger, because a
    filter on a logger is not consulted for records propagating up from a
    child — which would leave every module's own logger unfiltered."""
    logging.getLogger("ocr_service").warning("MRZ: %s", MRZ_LINE_2)
    assert MRZ_LINE_2 not in captured_root_log.getvalue()


def test_the_filter_redacts_a_token_in_a_url_or_header(captured_root_log):
    logging.getLogger("test.tok").info(
        "GET /events?token=eyJhbGciOiJIUzI1NiJ9.abc.def with Bearer eyJhbGciOiJIUzI1NiJ9.xyz"
    )
    output = captured_root_log.getvalue()
    assert "eyJhbGciOiJIUzI1NiJ9.abc.def" not in output
    assert "eyJhbGciOiJIUzI1NiJ9.xyz" not in output


def test_the_filter_redacts_an_exception_message(captured_root_log):
    try:
        raise ValueError(f"failed on {DOCUMENT_NUMBER}")
    except ValueError:
        logging.getLogger("test.exc").error("boom", exc_info=True)
    assert DOCUMENT_NUMBER not in captured_root_log.getvalue()


def test_the_filter_leaves_operational_detail_alone():
    """It has to stay useful. Job ids, user ids, page numbers, counts and log
    timestamps are how an incident gets diagnosed."""
    line = "[Job 7f3a-91bc] Page 3/12 for user 44 completed in 812 ms at 2026-09-06T11:04:12Z"
    assert log_redaction.redact(line) == line


def test_the_filter_never_raises_on_odd_input():
    for value in ("", "é" * 5000, "\x00\x01", "%s %d %(x)s"):
        log_redaction.redact(value)


# --- The call sites ------------------------------------------------------

def test_the_ocr_parser_no_longer_logs_the_document(captured_root_log, monkeypatch):
    """The real regression: `_extract_data_from_text` used to log `full_text`.

    This drives the actual parsing function with text containing every
    sensitive field and asserts none of them reaches the log — with the
    redaction filter DISABLED, so it proves the call site was fixed rather than
    that the safety net caught it.
    """
    import ocr_service

    # Strip the filter: this test is about the call sites.
    root = logging.getLogger()
    for handler in root.handlers:
        for existing in list(handler.filters):
            if isinstance(existing, log_redaction.RedactingFilter):
                handler.removeFilter(existing)

    text = f"REPUBLIQUE FRANCAISE {SURNAME} {GIVEN_NAME} {BIRTH_DATE} {MRZ_LINE_1} {MRZ_LINE_2}"

    class FakeAnnotation:
        # Assigned below: a class body cannot read a local of the same name
        # from the enclosing function.
        pages = []

    FakeAnnotation.text = text

    try:
        ocr_service._extract_data_from_text(text, FakeAnnotation())
    except Exception:
        # Parsing may or may not succeed on synthetic text; the logging is the
        # subject, not the result.
        pass

    output = captured_root_log.getvalue()
    for secret in (SURNAME, GIVEN_NAME, MRZ_LINE_1, MRZ_LINE_2, DOCUMENT_NUMBER):
        assert secret not in output, f"{secret!r} was written to the log by a call site"


def test_the_source_no_longer_contains_the_offending_statements():
    """A direct guard against the exact lines that leaked, so a future edit
    cannot quietly restore them."""
    import os
    backend = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source = open(os.path.join(backend, "ocr_service.py"), encoding="utf-8").read()
    assert "logger.info(full_text)" not in source
    assert "Texte OCR extrait complet" not in source
    assert 'logger.info(f"--- Données analysées ---' not in source


def test_the_redaction_filter_is_installed_by_main():
    """main.py must actually call install(); an uninstalled filter protects
    nothing."""
    import os
    backend = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source = open(os.path.join(backend, "main.py"), encoding="utf-8").read()
    assert "log_redaction.install()" in source


def test_an_uploaded_filename_is_never_logged_raw(client, db_session, captured_root_log, monkeypatch):
    """The filename is user-controlled and can itself be identifying —
    `Dupont-passeport-2026.pdf` names a person."""
    import os
    import main
    from tests.helpers import auth_headers, make_user

    make_user(db_session, "namer", page_credits=10)

    async def fake_task(job_id, file_path, content_type, destination, user_id):
        try:
            os.unlink(file_path)
        except OSError:
            pass

    monkeypatch.setattr(main, "run_ocr_extraction_task", fake_task)
    client.post(
        "/passports/upload-and-extract/",
        files={"file": ("DUPONT-passeport.pdf", b"%PDF-1.4\n" + b"0" * 100, "application/pdf")},
        headers=auth_headers("namer"),
    )
    assert "DUPONT-passeport.pdf" not in captured_root_log.getvalue()

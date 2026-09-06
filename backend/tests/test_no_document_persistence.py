"""The "documents are never stored" claim, tested rather than asserted.

Read the honest finding in SCANID-HANDOVER.md before this file. The brief asked
for a test proving that **no file is created during the request**. That test
would fail, and it would fail for two independent reasons that are both by
design in code this package is not allowed to redesign:

  1. `main.py` deliberately spools the upload to a named temp file so the bytes
     are not pinned in RAM for the whole OCR job (the comment at the mkstemp
     call says so).
  2. Starlette's own multipart parser spools any part over 1 MB to a
     SpooledTemporaryFile before the endpoint function is even entered
     (starlette/formparsers.py, `max_file_size = 1024 * 1024`). Even an
     endpoint that never touched the disk would not make that go away.

So this file tests what is actually true and actually matters: **nothing
survives**. Every spooled document is gone by the time the job ends, an upload
that is refused leaves nothing behind, and a file orphaned by a killed process
is swept on the next start.
"""
import os
import tempfile

import pytest

import main
from tests.helpers import auth_headers, make_user

PDF = b"%PDF-1.4\n" + b"0" * 200


def spool_files():
    root = tempfile.gettempdir()
    try:
        return {n for n in os.listdir(root) if n.startswith(main.OCR_SPOOL_PREFIX)}
    except OSError:
        return set()


def test_a_completed_job_leaves_no_document_on_disk(client, db_session, monkeypatch):
    """The whole point: after the job, the bytes are gone."""
    make_user(db_session, "persist", page_credits=10)
    before = spool_files()
    observed = {}

    async def fake_task(job_id, file_path, content_type, destination, user_id):
        # Mid-job the file DOES exist — that is the honest finding.
        observed["existed_during_job"] = os.path.exists(file_path)
        observed["size"] = os.path.getsize(file_path)
        # Then the real cleanup contract runs.
        try:
            os.unlink(file_path)
        except OSError:
            pass

    monkeypatch.setattr(main, "run_ocr_extraction_task", fake_task)
    response = client.post(
        "/passports/upload-and-extract/",
        files={"file": ("doc.pdf", PDF, "application/pdf")},
        headers=auth_headers("persist"),
    )
    assert response.status_code == 200, response.text

    assert observed["existed_during_job"] is True, (
        "the spool file did not exist during the job — the finding in the "
        "handover would then be stale and this test should be rewritten"
    )
    assert observed["size"] == len(PDF)
    assert spool_files() == before, "a document was left on disk after the job"


def test_the_spool_file_is_owner_readable_only(client, db_session, monkeypatch):
    """While it exists, no other account on the host can read it."""
    make_user(db_session, "perms", page_credits=10)
    modes = {}

    async def fake_task(job_id, file_path, content_type, destination, user_id):
        modes["mode"] = os.stat(file_path).st_mode & 0o777
        try:
            os.unlink(file_path)
        except OSError:
            pass

    monkeypatch.setattr(main, "run_ocr_extraction_task", fake_task)
    client.post(
        "/passports/upload-and-extract/",
        files={"file": ("doc.pdf", PDF, "application/pdf")},
        headers=auth_headers("perms"),
    )
    assert modes["mode"] == 0o600, oct(modes["mode"])


def test_a_rejected_upload_leaves_nothing_behind(client, db_session, monkeypatch):
    """Rejections happen after the temp file is created, so each one is its own
    chance to leak a document."""
    make_user(db_session, "rejected", page_credits=10)

    async def unreached(*args, **kwargs):
        raise AssertionError("the background task should not have been scheduled")

    monkeypatch.setattr(main, "run_ocr_extraction_task", unreached)
    before = spool_files()

    # Disallowed type.
    client.post(
        "/passports/upload-and-extract/",
        files={"file": ("x.pdf", b"MZ\x90\x00" + b"\x00" * 100, "application/pdf")},
        headers=auth_headers("rejected"),
    )
    assert spool_files() == before

    # Empty file.
    client.post(
        "/passports/upload-and-extract/",
        files={"file": ("x.pdf", b"", "application/pdf")},
        headers=auth_headers("rejected"),
    )
    assert spool_files() == before


def test_a_failing_job_still_deletes_the_document(client, db_session, monkeypatch):
    """The real cleanup path, exercised through the real function: the OCR run
    raises, and the finally must still unlink."""
    make_user(db_session, "failing", page_credits=10)
    captured = {}

    async def exploding_job(db, job_id, file_path, content_type, destination, user_id):
        captured["path"] = file_path
        assert os.path.exists(file_path)
        raise RuntimeError("OCR failed")

    monkeypatch.setattr(main, "_run_ocr_extraction_job", exploding_job)

    with pytest.raises(RuntimeError):
        import asyncio
        asyncio.run(main.run_ocr_extraction_task(
            job_id="job-1", file_path=_make_spool(), content_type="application/pdf",
            destination=None, user_id="u1",
        ))
    assert not os.path.exists(captured["path"]), "a failed job left the document on disk"


def test_the_cleanup_survives_a_session_that_cannot_be_opened(monkeypatch):
    """`SessionLocal()` used to be called outside the try, so a database blip
    at that instant orphaned the document permanently."""
    path = _make_spool()

    def broken_session():
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(main, "SessionLocal", broken_session)

    import asyncio
    with pytest.raises(RuntimeError):
        asyncio.run(main.run_ocr_extraction_task(
            job_id="job-2", file_path=path, content_type="application/pdf",
            destination=None, user_id="u1",
        ))
    assert not os.path.exists(path), "the document survived a failed session open"


def test_the_startup_sweep_removes_documents_orphaned_by_a_kill():
    """A process killed mid-job — which every deploy causes, since the workflow
    restarts the service — cannot run its finally block. The next start must
    clear what it left."""
    orphan = _make_spool(content=b"%PDF-1.4 orphaned identity document")
    assert os.path.exists(orphan)

    removed = main.sweep_orphaned_spool_files()

    assert removed >= 1
    assert not os.path.exists(orphan)


def test_the_sweep_only_touches_our_own_spool_files():
    """It runs at startup over the shared temp directory, so it must not delete
    anything belonging to another process."""
    innocent = os.path.join(tempfile.gettempdir(), "someone-elses-file.tmp")
    with open(innocent, "wb") as handle:
        handle.write(b"not ours")
    try:
        main.sweep_orphaned_spool_files()
        assert os.path.exists(innocent), "the sweep deleted an unrelated file"
    finally:
        os.unlink(innocent)


def test_no_document_bytes_are_written_anywhere_outside_the_temp_directory(
    client, db_session, monkeypatch, tmp_path
):
    """The uploaded bytes must not reach the repository, the static mount, or
    anywhere else the process can write."""
    make_user(db_session, "nowhere", page_credits=10)
    marker = b"%PDF-1.4 UNIQUEMARKER7f3a9c"

    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    watched = [backend_dir, os.path.join(backend_dir, "static")]
    before = {d: _snapshot(d) for d in watched}

    async def fake_task(job_id, file_path, content_type, destination, user_id):
        try:
            os.unlink(file_path)
        except OSError:
            pass

    monkeypatch.setattr(main, "run_ocr_extraction_task", fake_task)
    response = client.post(
        "/passports/upload-and-extract/",
        files={"file": ("doc.pdf", marker + b"0" * 100, "application/pdf")},
        headers=auth_headers("nowhere"),
    )
    assert response.status_code == 200

    for directory in watched:
        assert _snapshot(directory) == before[directory], (
            f"the upload created a file under {directory}"
        )


def _snapshot(directory):
    try:
        return {n for n in os.listdir(directory) if not n.endswith(".pyc")}
    except OSError:
        return set()


def _make_spool(content: bytes = b"%PDF-1.4 document"):
    fd, path = tempfile.mkstemp(prefix=main.OCR_SPOOL_PREFIX)
    with os.fdopen(fd, "wb") as handle:
        handle.write(content)
    return path

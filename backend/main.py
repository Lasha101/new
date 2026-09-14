# /main.py
import os
from dotenv import load_dotenv

# Load environment variables BEFORE any other local imports (like database)
load_dotenv()

import asyncio
import codecs
import csv
import io
import json
import logging
import re
import tempfile
import uuid
from contextlib import asynccontextmanager
from datetime import date, datetime
from typing import Optional, Dict, List, Any, Literal

import pandas as pd
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter
from pydantic import ValidationError
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Query, Form, Request, Response, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from jose import jwt, JWTError
from sqlalchemy import update as sa_update
from sqlalchemy.orm import Session

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import account_tokens
import billing
import billing_identity
import config
import crud, models, schemas, auth
import emails
import mailer
import file_validation
import log_redaction
import ocr_service
import password_policy
import schema_migrations
import trials
from database import get_db, engine, SessionLocal

logging.basicConfig(level=logging.INFO)
# Identity data must not reach the logs. The call sites in the upload and OCR
# paths were reviewed and no longer pass a name, a document number or a raw
# filename; this filter is the safety net behind that review, and it also
# covers third-party libraries, which nobody reviewed.
log_redaction.install()
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

# Every self-registered account starts with exactly this many page credits
# (1 credit = 1 successfully extracted document; failures are not charged).
SIGNUP_PAGE_CREDITS = 5

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
CSV_MEDIA_TYPE = "text/csv"
# French Excel splits a double-clicked CSV on the Windows list separator,
# which is ';' in a French locale (a ',' file lands in a single column).
CSV_DELIMITER = ";"

# --- Document type (PP = passeport, PI = pièce d'identité / CNI) ---
# The passports table has no document-type column, so the type is derived
# from the document number: a French passport number is always 2 digits +
# 2 letters + 5 digits, while a CNI number is 12 digits (old format) or 9
# alphanumeric characters (new format, never in the passport shape). The
# frontend applies exactly the same rule (frontend/src/resultsHelpers.js).
DOC_TYPE_PASSPORT = "PP"
DOC_TYPE_ID_CARD = "PI"
# "PASS" was the passport code until 14/09/2026 (Alex chose « PP »). It is still
# accepted as a filter value, so an app shell cached before the change keeps
# exporting; every value the API produces is "PP".
LEGACY_DOC_TYPE_PASSPORT = "PASS"
DocumentType = Literal["PP", "PI", "PASS"]
ExportFormat = Literal["xlsx", "csv"]
# Dates are displayed the French way (jour/mois/année) everywhere the export is
# seen: on-screen preview, CSV text (_format_display_date) and the number format
# of XLSX date cells.
#
# The casing of this format code is not cosmetic. Excel's number-format grammar
# is case-insensitive, but a spreadsheet viewer built on Unicode/ICU date
# patterns (UTS #35) — which is what iOS uses to preview an .xlsx — reads the
# very same string as a date pattern, and there 'D' means DAY OF THE YEAR and
# 'Y' means the week-numbering year. Written "DD/MM/YYYY", 5 July 1983 rendered
# as "186/07/1983" on an iPhone while Excel showed it correctly. Only 'd' (day
# of the month), 'M' (month) and 'y' (calendar year) mean the same thing in both
# grammars, so this code must stay lowercase-d / uppercase-M / lowercase-y.
XLSX_DATE_NUMBER_FORMAT = "dd/MM/yyyy"
# ASCII digit class on purpose: the frontend regex (JS \d) is ASCII-only, and
# both sides must classify every value identically.
_PASSPORT_NUMBER_RE = re.compile(r"^[0-9]{2}[A-Z]{2}[0-9]{5}$")


def document_type_of(passport_number: Any) -> str:
    """'PP' for a French passport number, 'PI' for any other document number."""
    number = str(passport_number or "").strip().upper()
    return DOC_TYPE_PASSPORT if _PASSPORT_NUMBER_RE.match(number) else DOC_TYPE_ID_CARD


# Exported columns, in order, with the French headers of the on-screen results
# table (columnTranslations in the frontend). The order is the one of the
# on-screen table (PASSPORT_COLUMN_ORDER in frontend/src/resultsHelpers.js):
# the derived Type column sits between the document number and the
# destination. Internal ids are never exported.
EXPORT_COLUMNS = ["last_name", "first_name", "birth_date", "expiration_date", "nationality",
                  "passport_number", "document_type", "destination", "confidence_score"]
EXPORT_HEADERS = {
    "document_type": "Type", "first_name": "Prénom", "last_name": "Nom de famille",
    "birth_date": "Date de Naissance", "expiration_date": "Date d'Expiration",
    "nationality": "Nationalité", "passport_number": "Numéro de document",
    "destination": "Destination", "confidence_score": "Score de Confiance",
}


# --- SSE CONNECTION MANAGER ---
class ConnectionManager:
    def __init__(self):
        # Maps user_id -> List of asyncio.Queue
        self.active_connections: Dict[str, List[asyncio.Queue]] = {}
        self.is_shutting_down = False

    async def connect(self, user_id: str):
        queue = asyncio.Queue()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(queue)
        logger.info(f"User {user_id} connected to SSE. Total connections: {len(self.active_connections.get(user_id, []))}")
        return queue

    def disconnect(self, user_id: str, queue: asyncio.Queue):
        if user_id in self.active_connections:
            if queue in self.active_connections[user_id]:
                self.active_connections[user_id].remove(queue)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"User {user_id} disconnected from SSE.")

    async def send_update(self, user_id: str, message: dict):
        """Push a message to all active connections for a specific user."""
        if not self.is_shutting_down and user_id in self.active_connections:
            data_str = json.dumps(message)
            try:
                queues = list(self.active_connections[user_id])
                for queue in queues:
                    await queue.put(data_str)
                logger.info(f"Sent update to user {user_id}: {message}")
            except Exception as e:
                logger.error(f"Error sending SSE update: {e}")

    async def shutdown(self):
        """Closes all active connections by sending a 'None' poison pill so the
        server can shut down without hanging."""
        logger.info("Shutting down all SSE connections...")
        self.is_shutting_down = True
        for user_id in list(self.active_connections.keys()):
            for queue in list(self.active_connections.get(user_id, [])):
                queue.put_nowait(None)
        self.active_connections.clear()


manager = ConnectionManager()


# --- Background OCR task ---
async def run_ocr_extraction_task(
    job_id: str,
    file_path: str,
    content_type: str,
    destination: Optional[str],
    user_id: str
):
    """Entry point: owns the task's database session (the background task
    outlives the request, so it cannot reuse the request-scoped session) and
    the spooled upload file, which is deleted when the job ends."""
    db = None
    try:
        # Inside the try: if opening the session raises, the outer finally must
        # still run, or the spooled document stays on disk with nothing left
        # holding a reference to it.
        db = SessionLocal()
        await _run_ocr_extraction_job(db, job_id, file_path, content_type, destination, user_id)
    finally:
        # Unlink first: it cannot raise past the except, while db.close (an
        # awaitable) could — the spool file must be reclaimed regardless.
        try:
            os.unlink(file_path)
        except OSError:
            pass
        if db is not None:
            await asyncio.to_thread(db.close)


async def _run_ocr_extraction_job(
    db: Session,
    job_id: str,
    file_path: str,
    content_type: str,
    destination: Optional[str],
    user_id: str
):
    """Runs the full OCR extraction in the background, persisting progress and
    results on the job record. The session is used strictly sequentially."""
    try:
        await asyncio.to_thread(crud.update_ocr_job_progress, db, job_id, 10)
        await asyncio.to_thread(crud.update_ocr_job_progress, db, job_id, 20)

        async def report_page_progress(done: int, total: int):
            # Map page completion onto the 20→80 segment of the progress bar,
            # and push it over SSE so the bar moves without waiting for a poll.
            progress = 20 + int((done / total) * 60) if total > 0 else 20
            await asyncio.to_thread(crud.update_ocr_job_progress, db, job_id, progress)
            await manager.send_update(user_id, {"type": "job_progress", "job_id": job_id, "progress": progress})

        extraction_results = await ocr_service.extract_data_page_by_page(
            file_path=file_path,
            content_type=content_type,
            progress_callback=report_page_progress
        )

        await asyncio.to_thread(crud.update_ocr_job_progress, db, job_id, 80)
    except Exception as e:
        logger.error(f"Error during extraction for job {job_id}: {e}", exc_info=True)
        # A failed flush leaves the session unusable until rolled back.
        await asyncio.to_thread(db.rollback)
        await asyncio.to_thread(crud.update_ocr_job_complete, db, job_id, [], [{"page_number": 0, "detail": f"Traitement global échoué: {str(e)}"}])
        return

    successes = []
    failures = []
    total_pages = len(extraction_results)

    for i, result in enumerate(extraction_results):
        page_number = result.get("page_number")

        if "verso_of_page" in result:
            # Verso of a split old-format CNI, merged into the document of its
            # recto (page result['verso_of_page']): nothing to save, nothing to
            # report as a failure. The page still counts as processed, but it
            # costs no credit: the document is paid once, by its recto's success.
            logger.info(f"[Job {job_id}] Page {page_number} : verso fusionné avec le recto de la page {result['verso_of_page']}.")
            continue

        if "error" in result:
            logger.warning(f"[Job {job_id}] Page {page_number} non extraite : {result['error']}")
            failures.append({"page_number": page_number, "detail": result["error"]})
            continue

        if "data" in result:
            document_data = result["data"]
            try:
                if destination:
                    document_data["destination"] = destination

                passport_create_schema = schemas.PassportCreate(**document_data)

                created_passport_data = await asyncio.to_thread(
                    crud.create_user_passport,
                    db=db, passport=passport_create_schema, user_id=user_id
                )
                if created_passport_data:
                    logger.info(f"💾 Saved document {created_passport_data.get('id')} to table 'passports'")

                    created_passport_schema = schemas.Passport.model_validate(created_passport_data)
                    # mode='json' converts dates to ISO strings so the job
                    # document stays JSON-serializable.
                    serialized_data = created_passport_schema.model_dump(mode='json')
                    successes.append({"page_number": page_number, "data": serialized_data})

            except ValidationError as e:
                first_error = e.errors()[0]
                error_message = f"Validation Error on field '{first_error['loc'][0]}': {first_error['msg']}"
                logger.warning(f"[Job {job_id}] Page {page_number} non extraite : {error_message}")
                failures.append({"page_number": page_number, "detail": error_message})
            except HTTPException as e:
                await asyncio.to_thread(db.rollback)
                logger.warning(f"[Job {job_id}] Page {page_number} non extraite : {e.detail}")
                failures.append({"page_number": page_number, "detail": e.detail})
            except Exception as e:
                # Roll back so a failed page save cannot poison the session
                # for the remaining pages of the job.
                await asyncio.to_thread(db.rollback)
                detail = getattr(e, 'detail', f"A database error occurred: {str(e)}")
                logger.warning(f"[Job {job_id}] Page {page_number} non extraite : {detail}")
                failures.append({"page_number": page_number, "detail": detail})

        if total_pages > 0:
            current_progress = 80 + int((i / total_pages) * 15)
            await asyncio.to_thread(crud.update_ocr_job_progress, db, job_id, current_progress)

    # Charge one credit per SUCCESSFUL extraction only — a failed page costs
    # nothing — and track every processed page in the page counter.
    page_count = len(extraction_results)
    credits_charged = len(successes)
    if page_count > 0:
        try:
            def _charge_credits():
                # One atomic UPDATE — the SQL equivalent of firestore.Increment.
                db.execute(
                    sa_update(models.User)
                    .where(models.User.id == str(user_id))
                    .values(
                        page_credits=models.User.page_credits - credits_charged,
                        uploaded_pages_count=models.User.uploaded_pages_count + page_count,
                    )
                )
                db.commit()

            await asyncio.to_thread(_charge_credits)

            updated_user = await asyncio.to_thread(crud.get_user, db, str(user_id)) or {}
            new_credits = updated_user.get("page_credits", 0)
            await manager.send_update(user_id, {"type": "credit_update", "credits": new_credits})
        except Exception as e:
            await asyncio.to_thread(db.rollback)
            logger.error(f"Failed to update page count/credits: {e}")

    await asyncio.to_thread(crud.update_ocr_job_complete, db, job_id, successes, failures)
    # Push completion over SSE so the dashboard refreshes without poll lag.
    await manager.send_update(user_id, {"type": "job_update", "job_id": job_id})
    logger.info(f"Job {job_id} completed. Saved to DB.")


# The prefix every spooled upload is created with (tempfile.mkstemp below).
# Named here so the startup sweep and the endpoint cannot drift apart.
OCR_SPOOL_PREFIX = "ocr_upload_"


def sweep_orphaned_spool_files() -> int:
    """Deletes spooled documents left behind by a previous process.

    The background task unlinks its own file on every in-process exit path, but
    a process that is killed — and the deploy workflow restarts the service on
    every push — cannot run a finally block. Without this, a document caught
    mid-job stays on disk indefinitely, which is exactly what the product
    promises never happens. Runs once at startup and logs a count only.
    """
    removed = 0
    try:
        spool_dir = tempfile.gettempdir()
        for name in os.listdir(spool_dir):
            if not name.startswith(OCR_SPOOL_PREFIX):
                continue
            path = os.path.join(spool_dir, name)
            try:
                if os.path.isfile(path):
                    os.unlink(path)
                    removed += 1
            except OSError:
                # Another worker booting at the same instant may have won the
                # race, or the file may not be ours to remove. Neither is fatal.
                pass
    except OSError as e:
        logger.warning("Spool sweep could not read the temp directory: %s", e)
    if removed:
        logger.info("Nettoyage au démarrage : %d fichier(s) d'import orphelin(s) supprimé(s).", removed)
    return removed


def _purge_trial_requests_once() -> int:
    db = SessionLocal()
    try:
        removed = trials.purge(db)
        if removed:
            logger.info("Demandes d'essai purgées (plus de %d jours) : %d", config.TRIAL_PURGE_DAYS, removed)
        return removed
    finally:
        db.close()


async def _purge_trial_requests_daily():
    """RGPD minimisation (Spec v2 §1): pending and refused trial requests are
    deleted after TRIAL_PURGE_DAYS. Runs at startup, then every 24 hours, in
    this process (production runs a single worker)."""
    while True:
        try:
            await asyncio.to_thread(_purge_trial_requests_once)
        except Exception as e:
            logger.error("Purge des demandes d'essai en échec : %s", type(e).__name__)
        await asyncio.sleep(24 * 3600)


# --- Lifespan for application startup/shutdown ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        logger.info("🚀 Backend starting up (PostgreSQL).")
        await asyncio.to_thread(sweep_orphaned_spool_files)
        # Create any missing tables on boot (idempotent), add the columns an
        # older database lacks (schema_migrations.py), then look up the admin.
        await asyncio.to_thread(models.Base.metadata.create_all, engine)
        await asyncio.to_thread(schema_migrations.add_missing_columns, engine)
        admin_user = await asyncio.to_thread(crud.get_user_by_username, db, username="admin")
    except Exception as e:
        logger.error(f"🔴 Database startup check failed: {e}")
        admin_user = None

    if not admin_user:
        ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
        if not ADMIN_PASSWORD:
            logger.warning("ADMIN_PASSWORD environment variable not set. Admin user not created.")
        else:
            admin = schemas.UserCreate(
                first_name="Admin",
                last_name="User",
                email="admin@example.com",
                phone_number="1234567890",
                user_name="admin",
                password=str(ADMIN_PASSWORD),
                page_credits=1000
            )
            await asyncio.to_thread(crud.create_user, db=db, user=admin, role="admin")

    await asyncio.to_thread(db.close)

    purge_task = asyncio.create_task(_purge_trial_requests_daily())

    yield

    purge_task.cancel()
    logger.info("Lifespan shutdown: Cleaning up resources...")
    manager.is_shutting_down = True
    await manager.shutdown()

    try:
        await asyncio.to_thread(engine.dispose)
        logger.info("✅ PostgreSQL engine disposed.")
    except Exception as e:
        logger.error(f"🔴 Error disposing PostgreSQL engine: {e}")

    if ocr_service.vision_client:
        try:
            await asyncio.to_thread(ocr_service.vision_client.transport.close)
            logger.info("✅ Google Vision client closed.")
        except Exception as e:
            logger.error(f"🔴 Error closing Vision client: {e}")

    logger.info("Lifespan shutdown complete.")


# --- FastAPI App Initialization ---
# In production the interactive documentation is closed: /docs, /redoc and
# /openapi.json otherwise hand the entire API surface — every route, every
# schema, every field — to anyone who asks. Passing None for all three makes
# FastAPI not register the routes at all, so they 404 rather than 401; there is
# nothing behind them to attack. In development all three stay exactly as they
# were.
_docs_enabled = not config.is_production()
app = FastAPI(
    lifespan=lifespan,
    docs_url="/docs" if _docs_enabled else None,
    redoc_url="/redoc" if _docs_enabled else None,
    openapi_url="/openapi.json" if _docs_enabled else None,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

# --- Serve Static Frontend Files ---
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- CORS Middleware Configuration ---
# The origin list comes from the environment (CORS_ORIGINS, comma separated):
# one origin in production, the Vite dev server in development. Never a
# wildcard — and a wildcard would in any case be refused by the browser now
# that credentials are sent, because `Access-Control-Allow-Origin: *` and
# `allow_credentials=True` are not a legal combination.
#
# Methods and headers are the ones this API actually uses, not "*", so a verb
# or header the app does not implement is not pre-authorised for it.
origins = config.cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=config.CORS_METHODS,
    allow_headers=config.CORS_HEADERS,
    expose_headers=config.CORS_EXPOSE_HEADERS,
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """An unexpected failure returns a generic French message; the detail goes
    to the log.

    Without this, Starlette re-raises and the response depends on how the
    server happens to be run: uvicorn with `--reload`, or any ASGI debug
    middleware, will render the traceback into the response body — file paths,
    source lines, local variables, and whatever identity data those locals held.

    `exc_info=True` keeps the full traceback in the log, where the redaction
    filter has already cleaned it.
    """
    logger.error("Unhandled error on %s %s", request.method, request.url.path, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Une erreur interne est survenue. Veuillez réessayer."},
    )


# --- Export helpers ---

def _safe_excel_value(value: Any) -> Any:
    """Excel-safe cell value: dates instead of tz-aware datetimes (which Excel
    cannot store), and no strings that openpyxl would interpret as formulas
    (formula injection via user-controlled text such as a destination)."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str) and value.startswith("="):
        return "'" + value
    return value


def _export_cell_value(value: Any) -> Any:
    """Export cell value: Excel-safe, and every text value in UPPERCASE."""
    value = _safe_excel_value(value)
    if isinstance(value, str):
        return value.upper()
    return value


def _filter_by_document_type(rows: List[Dict[str, Any]], document_type: Optional[str]) -> List[Dict[str, Any]]:
    """Keeps only the rows of the given document type; no type = all rows."""
    if not document_type:
        return rows
    if document_type == LEGACY_DOC_TYPE_PASSPORT:
        document_type = DOC_TYPE_PASSPORT
    return [row for row in rows if document_type_of(row.get("passport_number")) == document_type]


def _build_export_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Export rows in EXPORT_COLUMNS order: the derived Type column (PP/PI)
    computed from the document number, internal ids (id, owner_id) dropped,
    text values uppercased."""
    export_rows = []
    for row in rows:
        export_row = {}
        for column in EXPORT_COLUMNS:
            if column == "document_type":
                export_row[column] = document_type_of(row.get("passport_number"))
            else:
                export_row[column] = _export_cell_value(row.get(column))
        export_rows.append(export_row)
    return export_rows


def _format_display_date(value: Any) -> str:
    """Date shown to the user: DD/MM/YYYY (explicit zero padding: strftime's
    %Y does not pad years below 1000)."""
    return f"{value.day:02d}/{value.month:02d}/{value.year:04d}"


def _displayed_length(value: Any) -> int:
    """Number of characters Excel displays for a cell value (dates render as
    DD/MM/YYYY, empty cells as nothing)."""
    if value is None:
        return 0
    if isinstance(value, (datetime, date)):
        return 10
    return len(str(value))


def _format_export_worksheet(worksheet) -> None:
    """Centers every cell, auto-fits each column to its longest displayed
    value (header included) so nothing is ever truncated in Excel, and turns
    the header row into filter dropdowns (Excel AutoFilter over the whole
    table) so the downloaded file can be sorted/filtered column by column
    as soon as it is opened."""
    # AutoFilter over the header row + every data row: each header cell gets
    # the dropdown (sort, text/date/number filters) like an Excel table.
    worksheet.auto_filter.ref = f"A1:{get_column_letter(worksheet.max_column)}{worksheet.max_row}"

    center = Alignment(horizontal="center", vertical="center")
    for column_cells in worksheet.columns:
        longest = 0
        for cell in column_cells:
            cell.alignment = center
            if isinstance(cell.value, (datetime, date)):
                # Real date cell (sortable / filterable by date) shown as
                # DD/MM/YYYY. Set here because pandas' openpyxl writer
                # ignores its date_format argument (pandas 2.2).
                cell.number_format = XLSX_DATE_NUMBER_FORMAT
            longest = max(longest, _displayed_length(cell.value))
        # Excel width units are ~one digit wide; uppercase letters and the bold
        # header are wider than digits, hence the factor and the padding. 255
        # is Excel's hard maximum column width.
        width = min(255, max(8, longest * 1.25 + 3))
        worksheet.column_dimensions[get_column_letter(column_cells[0].column)].width = width

    # Hide every grid column after the last data column (one <col> range up to
    # XFD, Excel's last column): the sheet then ends visually at the table
    # instead of showing an endless empty grid to the right.
    first_unused = worksheet.max_column + 1
    if first_unused <= 16384:
        trailing = worksheet.column_dimensions[get_column_letter(first_unused)]
        trailing.min = first_unused
        trailing.max = 16384
        trailing.hidden = True


def _excel_response(export_rows: List[Dict[str, Any]], filename: str) -> StreamingResponse:
    """Builds an .xlsx download from export rows (see _build_export_rows)."""
    df = pd.DataFrame(export_rows, columns=EXPORT_COLUMNS).rename(columns=EXPORT_HEADERS)

    stream = io.BytesIO()
    with pd.ExcelWriter(stream, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Passeports")
        _format_export_worksheet(writer.sheets["Passeports"])
    stream.seek(0)

    response = StreamingResponse(stream, media_type=XLSX_MEDIA_TYPE)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response


# CSV cells Excel would evaluate as formulas (OWASP CSV-injection set); the
# '=' case is already neutralised upstream by _safe_excel_value.
_CSV_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")
_ALL_DIGITS_RE = re.compile(r"^[0-9]+$")


def _csv_cell(value: Any) -> str:
    """CSV cell text: dates as DD/MM/YYYY, None as empty, formula-like text
    neutralised, and all-digit text (12-digit CNI numbers) wrapped as ="…" so
    that Excel keeps it as text instead of re-typing it as a number (which
    drops leading zeros and displays 1.23457E+11)."""
    if value is None:
        return ""
    if isinstance(value, (datetime, date)):
        return _format_display_date(value)
    if isinstance(value, str):
        if _ALL_DIGITS_RE.match(value):
            return f'="{value}"'
        if value.startswith(_CSV_FORMULA_PREFIXES):
            return "'" + value
    return str(value)


def _csv_response(export_rows: List[Dict[str, Any]], filename: str) -> StreamingResponse:
    """Builds a UTF-8 (with BOM, so Excel shows accents correctly) .csv
    download from export rows (see _build_export_rows)."""
    text = io.StringIO()
    writer = csv.writer(text, delimiter=CSV_DELIMITER, lineterminator="\r\n")
    writer.writerow([EXPORT_HEADERS[column] for column in EXPORT_COLUMNS])
    for row in export_rows:
        writer.writerow([_csv_cell(row.get(column)) for column in EXPORT_COLUMNS])
    payload = codecs.BOM_UTF8 + text.getvalue().encode("utf-8")

    response = StreamingResponse(io.BytesIO(payload), media_type=CSV_MEDIA_TYPE)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response


def _export_file_response(rows: List[Dict[str, Any]], filename_stem: str, export_format: str) -> StreamingResponse:
    """Builds the download for the requested format from raw passport rows."""
    export_rows = _build_export_rows(rows)
    if export_format == "csv":
        return _csv_response(export_rows, f"{filename_stem}.csv")
    return _excel_response(export_rows, f"{filename_stem}.xlsx")


def _preview_value(value: Any) -> Any:
    """Preview cell value: dates as DD/MM/YYYY (exactly what the downloaded
    files show), missing values as blank cells (the table renders raw values,
    so None must not appear as 'null')."""
    if isinstance(value, (datetime, date)):
        return _format_display_date(value)
    if value is None:
        return ""
    return value


def _export_rows_for_preview(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Serializes export rows for the JSON on-screen preview."""
    return [{key: _preview_value(value) for key, value in row.items()} for row in rows]


# --- Authentication Routes ---
@app.post("/token", response_model=schemas.Token)
@limiter.limit(config.LOGIN_RATE_LIMIT)
def login_for_access_token(request: Request, response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Per-account lockout, layered on top of the per-IP limit above. The
    # message is deliberately the same shape as a wrong password: telling an
    # attacker "this account is locked" confirms the account exists.
    if auth.is_locked_out(form_data.username):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de tentatives de connexion. Réessayez dans quelques minutes.",
        )

    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        auth.record_login_failure(form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    auth.reset_login_failures(form_data.username)
    access_token = auth.create_access_token(data=auth.session_claims(user))
    # The token now also travels as an HttpOnly cookie, which is what the
    # browser uses from here on. The response body is UNCHANGED — same shape,
    # same fields — so every existing client, and the test suite, keep working.
    auth.set_session_cookie(response, access_token)
    return {"access_token": access_token, "token_type": "bearer"}


# --- Password reset (« Mot de passe oublié ? ») ---
FORGOT_PASSWORD_ANSWER = (
    "Si un compte correspond à cet identifiant, un email contenant un lien de réinitialisation "
    "vient de lui être envoyé. Le lien est valable 48 heures."
)
INVALID_PASSWORD_LINK = (
    "Ce lien n'est plus valide (il a expiré ou a déjà servi). "
    "Demandez un nouveau lien depuis « Mot de passe oublié ? »."
)


@app.post("/auth/forgot-password")
@limiter.limit(config.FORGOT_PASSWORD_RATE_LIMIT)
def forgot_password(request: Request, payload: schemas.ForgotPasswordRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Emails a 48-hour link to choose a new password.

    The answer is the same whether or not the account exists, so the form
    cannot be used to find out who is a customer. Only an active account gets an
    email: a pending trial request is not an account yet.
    """
    user = crud.get_user_by_login_identifier(db, payload.identifier)
    if user and auth.is_active_account(user):
        raw_token = account_tokens.issue(db, user["id"], account_tokens.PURPOSE_RESET)
        subject, body = emails.password_reset(user, raw_token)
        background_tasks.add_task(mailer.send, user["email"], subject, body, "password_reset")
    return {"detail": FORGOT_PASSWORD_ANSWER}


@app.post("/auth/reset-password")
@limiter.limit(config.RESET_PASSWORD_RATE_LIMIT)
def reset_password(request: Request, payload: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    """Sets the password chosen through a one-time link (reset or first
    password of a validated trial). Ends the account's other sessions."""
    found = account_tokens.find_valid(db, payload.token)
    if found is None:
        raise HTTPException(status_code=400, detail=INVALID_PASSWORD_LINK)
    user = found["user"]
    password_policy.assert_valid_password(payload.password, email=user.get("email"), user_name=user.get("user_name"))
    account_tokens.consume(db, found["token"], auth.get_password_hash(payload.password))
    # A locked-out account whose owner just proved control of the mailbox.
    auth.reset_login_failures(user.get("user_name"))
    return {"detail": "Votre mot de passe est enregistré. Vous pouvez vous connecter.", "user_name": user.get("user_name")}


# --- Buying a pack: account first, then Stripe (Spec v3) ---
UNKNOWN_PACK = "Ce pack n'existe pas. Choisissez un pack sur https://scanid.fr/#tarifs."


@app.post("/signup", response_model=schemas.CheckoutOut)
@limiter.limit(config.SIGNUP_RATE_LIMIT)
def signup_for_pack(request: Request, payload: schemas.PackSignupRequest, db: Session = Depends(get_db)):
    """/app/inscription: creates the active account with 0 credits and a pending
    purchase, then returns the pack's Payment Link to redirect to. Credits
    arrive with the Stripe webhook, never before."""
    if not billing.is_known_pack(payload.pack):
        raise HTTPException(status_code=400, detail=UNKNOWN_PACK)
    fields = {name: (getattr(payload, name) or "").strip() for name in (
        "first_name", "last_name", "company", "phone_number",
        "billing_street", "billing_postal_code", "billing_city", "billing_country")}
    labels = {"first_name": "le prénom", "last_name": "le nom", "company": "la société",
              "phone_number": "le téléphone", "billing_street": "la rue de l'adresse de facturation",
              "billing_postal_code": "le code postal", "billing_city": "la ville", "billing_country": "le pays"}
    for name, value in fields.items():
        if not value:
            raise HTTPException(status_code=400, detail=f"Veuillez renseigner {labels[name]}.")
        if len(value) > 200:
            raise HTTPException(status_code=400, detail=f"Le champ {labels[name]} est trop long.")
    try:
        email = str(trials._EMAIL.validate_python(payload.email.strip())).lower()
    except ValidationError:
        raise HTTPException(status_code=400, detail="L'adresse email n'est pas valide.")
    siret = billing_identity.normalize_siret(payload.siret)
    if not billing_identity.is_valid_siret(siret):
        raise HTTPException(status_code=400, detail=billing_identity.SIRET_ERROR)
    vat = billing_identity.normalize_vat(payload.vat_number)
    if vat and not billing_identity.is_valid_vat(vat):
        raise HTTPException(status_code=400, detail=billing_identity.VAT_ERROR)
    if not payload.consent:
        raise HTTPException(status_code=400, detail="Veuillez accepter le traitement de vos données pour créer le compte.")
    if crud.get_user_by_login_identifier(db, email) or trials._email_taken(db, email):
        raise HTTPException(status_code=400, detail="Un compte existe déjà avec cette adresse email. Connectez-vous pour acheter ce pack.")
    password_policy.assert_valid_password(payload.password, email=email, user_name=email)

    user = crud.create_user(db=db, user=schemas.UserCreate(
        first_name=fields["first_name"], last_name=fields["last_name"], email=email,
        phone_number=fields["phone_number"], user_name=email, password=payload.password, page_credits=0,
    ), role="user")
    row = db.get(models.User, user["id"])
    row.company, row.siret, row.vat_number = fields["company"], siret, vat or None
    row.billing_street, row.billing_postal_code = fields["billing_street"], fields["billing_postal_code"]
    row.billing_city, row.billing_country = fields["billing_city"], fields["billing_country"]
    db.commit()
    purchase = billing.create_pending_purchase(db, user["id"], payload.pack)
    return {"checkout_url": billing.checkout_url(payload.pack, email, user["id"]), "purchase_id": purchase["id"]}


@app.post("/orders", response_model=schemas.CheckoutOut)
def order_pack(payload: schemas.OrderRequest, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(auth.get_current_active_user)):
    """A customer who already has an account buys a pack: same pending purchase
    and Payment Link, no signup form."""
    if not billing.is_known_pack(payload.pack):
        raise HTTPException(status_code=400, detail=UNKNOWN_PACK)
    purchase = billing.create_pending_purchase(db, current_user["id"], payload.pack)
    return {"checkout_url": billing.checkout_url(payload.pack, current_user["email"], current_user["id"]), "purchase_id": purchase["id"]}


@app.post("/stripe/webhook")
async def stripe_webhook(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """checkout.session.completed (and async_payment_succeeded, for bank
    transfers) → credits the pack paid for, once. Signature verified with
    STRIPE_WEBHOOK_SECRET. Anything that cannot be credited automatically is
    acknowledged (Stripe would otherwise retry for days) and reported to Alex."""
    secret = config.stripe_webhook_secret()
    if not secret:
        return JSONResponse(status_code=503, content={"detail": "Webhook Stripe non configuré."})
    payload = await request.body()
    if not billing.verify_signature(payload, request.headers.get("stripe-signature", ""), secret):
        return JSONResponse(status_code=400, content={"detail": "Signature Stripe invalide."})
    try:
        event = json.loads(payload)
        event_type = event.get("type")
        session = (event.get("data") or {}).get("object") or {}
    except (ValueError, AttributeError):
        return JSONResponse(status_code=400, content={"detail": "Événement illisible."})
    if event_type not in billing.PAID_EVENTS:
        return {"received": True, "result": "ignored"}

    outcome = await asyncio.to_thread(billing.credit_checkout_session, db, session)
    if outcome.status == "credited":
        logger.info("Stripe: pack %s crédité (session traitée).", outcome.pack)
        subject, text_body = emails.purchase_confirmation(outcome.user, outcome.pack, outcome.expires_at)
        background_tasks.add_task(mailer.send, outcome.user["email"], subject, text_body, "purchase_confirmation")
        await manager.send_update(outcome.user["id"], {"type": "credit_update"})
    elif outcome.status == "unmatched":
        logger.error("Stripe: paiement non crédité automatiquement (%s).", outcome.reason)
        subject, text_body = emails.payment_anomaly(outcome.reason, session)
        background_tasks.add_task(mailer.send, config.mail_admin_to(), subject, text_body, "payment_anomaly")
    return {"received": True, "result": outcome.status}


# --- Public configuration read by the website ---
@app.get("/config")
def public_config():
    """What scanid.fr may switch on (Spec v3 §3). `signup` sends « Souscrire »
    to /app/inscription instead of straight to Stripe, so it is only true once
    the Stripe webhook secret is configured — before that, a paid pack could
    never be credited automatically. `trial` needs email: the request is useless
    if nobody is told about it."""
    return {"signup": bool(config.stripe_webhook_secret()), "trial": mailer.is_configured()}


# --- Free trial (Spec v2 §1) ---
@app.post("/trial-requests", status_code=201)
@limiter.limit(config.TRIAL_RATE_LIMIT)
async def create_trial_request(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """The form of scanid.fr/essai.html. Errors are {"error": "…"} (Spec v2); on
    any of them the site falls back to Formspree, so a lead is never lost —
    including when email is not configured, which is refused here on purpose."""
    if not mailer.is_configured():
        return JSONResponse(status_code=503, content={"error": "Les demandes d'essai sont momentanément indisponibles."})
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Requête invalide."})
    try:
        data = trials.parse(body)
        trial = await asyncio.to_thread(trials.create, db, data)
    except trials.TrialRequestError as e:
        return JSONResponse(status_code=e.status_code, content={"error": e.message})
    subject, text_body = emails.trial_admin_notification(trial)
    background_tasks.add_task(mailer.send, config.mail_admin_to(), subject, text_body, "trial_notification", trial["email"])
    return JSONResponse(status_code=201, content={"status": "pending"})


@app.get("/admin/trial-requests", response_model=List[schemas.TrialRequestOut], dependencies=[Depends(auth.require_admin)])
def list_trial_requests(db: Session = Depends(get_db)):
    return trials.list_pending(db)


@app.post("/admin/trial-requests/{request_id}/validate", response_model=schemas.TrialRequestOut, dependencies=[Depends(auth.require_admin)])
def validate_trial_request(request_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Activates the account and emails the welcome message with a 48-hour link
    to choose the password."""
    if not mailer.is_configured():
        raise HTTPException(status_code=503, detail="L'envoi d'emails n'est pas configuré : le compte n'a pas été activé.")
    try:
        trial, user = trials.validate(db, request_id)
    except trials.TrialRequestError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    raw_token = account_tokens.issue(db, user["id"], account_tokens.PURPOSE_SET)
    subject, text_body = emails.trial_welcome(user, raw_token)
    background_tasks.add_task(mailer.send, user["email"], subject, text_body, "trial_welcome")
    return trial


@app.post("/admin/trial-requests/{request_id}/reject", response_model=schemas.TrialRequestOut, dependencies=[Depends(auth.require_admin)])
def reject_trial_request(request_id: str, db: Session = Depends(get_db)):
    """Refuses the request. No email: Alex answers by hand if useful."""
    try:
        return trials.reject(db, request_id)
    except trials.TrialRequestError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@app.post("/logout")
def logout(response: Response):
    """Clears the session cookie.

    Necessary because the cookie is HttpOnly: the browser cannot delete it from
    JavaScript any more, so logging out has to be something the server does.
    Additive — no existing endpoint changed.
    """
    auth.clear_session_cookie(response)
    return {"detail": "Déconnexion réussie"}


@app.post("/session/refresh", response_model=schemas.Token)
def refresh_session(response: Response, current_user: Dict[str, Any] = Depends(auth.get_current_active_user)):
    """Renews a still-valid session for another SESSION_IDLE_MINUTES (12 h).

    The app calls this only when the person actually uses the page, never from
    background polling, so a session nobody touches for 12 hours expires and
    cannot be renewed afterwards: that is the automatic logout on inactivity.
    """
    access_token = auth.create_access_token(data=auth.session_claims(current_user))
    auth.set_session_cookie(response, access_token)
    return {"access_token": access_token, "token_type": "bearer"}


# --- SSE ROUTE FOR REAL-TIME UPDATES ---
@app.get("/events")
async def events(request: Request, token: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """Server-Sent Events endpoint. Gracefully handles disconnection and
    server shutdown.

    The token may now arrive in the session cookie instead of the query string.
    EventSource cannot set an Authorization header, which is why the token was
    in the URL — where it reached the access log, the browser history and any
    proxy in between. With `new EventSource(url, {withCredentials: true})` the
    cookie is sent instead and the URL carries nothing.

    The query parameter is still accepted, so any client that passes it keeps
    working; it is simply no longer required. Package B flagged this endpoint
    as the one place a token still appeared in a URL — this is the fix.
    """
    if not token:
        token = request.cookies.get(config.SESSION_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid token")
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username = payload.get("sub")
        if not isinstance(username, str):
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await asyncio.to_thread(crud.get_user_by_username, db, username=username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    async def event_generator(user_id):
        queue = await manager.connect(user_id)
        try:
            while not manager.is_shutting_down:
                try:
                    is_disconnected = await asyncio.wait_for(request.is_disconnected(), timeout=0.1)
                except asyncio.TimeoutError:
                    is_disconnected = False

                if is_disconnected:
                    break

                try:
                    data = await asyncio.wait_for(queue.get(), timeout=1.0)
                    # None is the shutdown poison pill.
                    if data is None:
                        break
                    yield f"data: {data}\n\n"
                except asyncio.TimeoutError:
                    yield ": keep-alive\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            manager.disconnect(user_id, queue)

    return StreamingResponse(event_generator(user["id"]), media_type="text/event-stream")


# --- User Routes ---
@app.post("/users/register", response_model=schemas.User)
@limiter.limit("5/minute")
def self_register_user(request: Request, user: schemas.UserRegister, db: Session = Depends(get_db)):
    """Autonomous self-registration: no invitation needed, and the account
    starts with exactly SIGNUP_PAGE_CREDITS page credits."""
    if crud.get_user_by_email(db, email=user.email):
        raise HTTPException(status_code=400, detail="Email déjà enregistré")
    if crud.get_user_by_username(db, username=user.user_name):
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà enregistré")

    # The server is the authority on the password policy. The registration form
    # shows the same four rules live as the user types, but that is convenience
    # only: a request posted straight to this endpoint is held to exactly the
    # same standard. The rejected value is never logged and never echoed back.
    password_policy.assert_valid_password(
        user.password, email=user.email, user_name=user.user_name
    )

    new_user = schemas.UserCreate(**user.model_dump(), page_credits=SIGNUP_PAGE_CREDITS)
    return crud.create_user(db=db, user=new_user, role="user")


@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: Dict[str, Any] = Depends(auth.get_current_active_user)):
    return current_user


@app.put("/users/me", response_model=schemas.User)
def update_user_me(user_update: schemas.UserUpdate, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(auth.get_current_active_user)):
    if current_user.get("role") != "admin":
        # Non-admin users cannot update their own page count, credits, login
        # name or role: those fields are dropped entirely so they are never
        # written to the DB.
        user_update = schemas.UserUpdate(**user_update.model_dump(
            exclude_unset=True, exclude={"uploaded_pages_count", "page_credits", "user_name", "role"}
        ))

    # Billing identity: a SIRET or VAT number that is given must be valid, and is
    # stored normalised (spaces dropped, VAT upper-cased). An empty value clears it.
    identity = {}
    if user_update.siret:
        identity["siret"] = billing_identity.normalize_siret(user_update.siret)
        if not billing_identity.is_valid_siret(identity["siret"]):
            raise HTTPException(status_code=400, detail=billing_identity.SIRET_ERROR)
    if user_update.vat_number:
        identity["vat_number"] = billing_identity.normalize_vat(user_update.vat_number)
        if not billing_identity.is_valid_vat(identity["vat_number"]):
            raise HTTPException(status_code=400, detail=billing_identity.VAT_ERROR)
    if identity:
        user_update = user_update.model_copy(update=identity)

    # A password change goes through the same policy as a registration. The
    # field is optional here — an empty value means "leave it alone", which is
    # what the account form sends when the user edits anything else — so the
    # check runs only when a new password is actually supplied.
    new_password = getattr(user_update, "password", None)
    if new_password:
        password_policy.assert_valid_password(
            new_password,
            email=user_update.email or current_user.get("email"),
            user_name=current_user.get("user_name"),
        )

    return crud.update_user(db=db, user_id=current_user["id"], user_update=user_update)


@app.get("/users/me/purchases", response_model=List[schemas.PurchaseOut])
def read_my_purchases(db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(auth.get_current_active_user)):
    """« Mes achats »: pack, date, expiry of every paid purchase."""
    return billing.paid_purchases(db, current_user["id"])


# --- Admin User Management Routes ---
@app.get("/admin/users/", response_model=list[schemas.User], dependencies=[Depends(auth.require_admin)])
def read_users(skip: int = 0, limit: int = 100, name_filter: Optional[str] = Query(None), db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit, name_filter=name_filter)


@app.delete("/admin/users/{user_id}", response_model=schemas.User, dependencies=[Depends(auth.require_admin)])
def delete_user(user_id: str, db: Session = Depends(get_db)):
    db_user = crud.delete_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return db_user


@app.get("/admin/users/{user_id}", response_model=schemas.User, dependencies=[Depends(auth.require_admin)])
def read_user(user_id: str, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return db_user


@app.put("/admin/users/{user_id}", response_model=schemas.User, dependencies=[Depends(auth.require_admin)])
async def update_user_admin(user_id: str, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    # Same policy when an admin resets somebody's password.
    if getattr(user_update, "password", None):
        target = crud.get_user(db, user_id)
        password_policy.assert_valid_password(
            user_update.password,
            email=user_update.email or (target or {}).get("email"),
            user_name=(target or {}).get("user_name"),
        )
    db_user = crud.update_user(db=db, user_id=user_id, user_update=user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # Notify the updated user so their dashboard refreshes credits.
    await manager.send_update(user_id, {"type": "credit_update"})
    return db_user


@app.post("/admin/users/", response_model=schemas.User, dependencies=[Depends(auth.require_admin)])
def create_user_by_admin(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, email=user.email):
        raise HTTPException(status_code=400, detail="Email déjà enregistré")
    if crud.get_user_by_username(db, username=user.user_name):
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà enregistré")
    # An admin-created account gets the same password policy as a self-service
    # one: an account is only as strong as the password it ships with, and an
    # administrator setting a weak one for a colleague is the likeliest way a
    # weak password enters the system.
    password_policy.assert_valid_password(
        user.password, email=user.email, user_name=user.user_name
    )
    return crud.create_user(db=db, user=user, role=getattr(user, 'role', 'user'))


@app.get("/admin/filterable-users", response_model=list[schemas.User], dependencies=[Depends(auth.require_admin)])
def read_filterable_users(db: Session = Depends(get_db)):
    return crud.get_all_users_for_filtering(db)


# --- Passport / Identity Document Routes ---
@app.post("/passports/", response_model=schemas.Passport)
def create_passport(passport: schemas.PassportCreate, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(auth.get_current_active_user)):
    return crud.create_user_passport(db=db, passport=passport, user_id=current_user["id"])


@app.post("/passports/upload-and-extract/", response_model=schemas.OcrJob)
@limiter.limit(config.UPLOAD_RATE_LIMIT)
async def upload_and_extract_passport(
    request: Request,
    background_tasks: BackgroundTasks,
    destination: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(auth.get_current_active_user)
):
    if current_user.get("page_credits", 0) <= 0:
        raise HTTPException(status_code=403, detail="Crédits insuffisants. Veuillez contacter l'administrateur.")

    # The declared length lets an oversized upload be refused before a single
    # byte of it is read. It is only a hint — a client can lie or omit it —
    # so the real limit is enforced again while streaming, below.
    declared_length = request.headers.get("content-length")
    if declared_length and declared_length.isdigit() and int(declared_length) > config.MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Fichier trop volumineux. La taille maximale est de {config.MAX_UPLOAD_BYTES // (1024 * 1024)} Mo.",
        )

    # The filename is client-controlled and is used for display only. It is
    # sanitised once, here, and the raw value is never stored, never logged and
    # never used to build a path.
    display_name = file_validation.safe_filename(file.filename)

    # Spool the upload to a temp file instead of reading it into memory: the
    # bytes would otherwise stay pinned in RAM for the whole background job.
    # The background task owns the file and deletes it when the job ends.
    fd, tmp_path = tempfile.mkstemp(prefix=OCR_SPOOL_PREFIX)
    file_size = 0
    head = b""
    try:
        with os.fdopen(fd, "wb") as spool:
            while chunk := await file.read(1024 * 1024):
                if not head:
                    head = chunk[:file_validation.SNIFF_LENGTH]
                file_size += len(chunk)
                # Enforced mid-stream so a client that under-declares its
                # Content-Length still cannot fill the disk: the write stops at
                # the limit rather than after it.
                if file_size > config.MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"Fichier trop volumineux. La taille maximale est de {config.MAX_UPLOAD_BYTES // (1024 * 1024)} Mo.",
                    )
                spool.write(chunk)

        if file_size == 0:
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")

        # Type by MAGIC BYTES. The Content-Type header and the extension are
        # both supplied by the client, so neither is consulted: a .pdf header
        # on a ZIP used to reach fitz.open(), which sniffs the content itself
        # and would happily open it as a document.
        sniffed = file_validation.sniff_file_type(head)
        if sniffed not in file_validation.ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Type de fichier non supporté. Veuillez télécharger une image ou un PDF.",
            )
        # Everything downstream branches on this, not on what the client said.
        effective_content_type = file_validation.CANONICAL_MEDIA_TYPE[sniffed]

        job_id = str(uuid.uuid4())
        job = await asyncio.to_thread(crud.create_ocr_job, db=db, job_id=job_id, user_id=current_user["id"], file_name=display_name)
    except BaseException:
        # BaseException, not Exception: a CancelledError — a client that hangs
        # up mid-upload, or a shutdown — is not an Exception, and used to leave
        # the spooled document on disk.
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    # The background task uses the shared client; the request-scoped session is
    # only used to create the job document.
    background_tasks.add_task(
        run_ocr_extraction_task,
        job_id=job_id,
        file_path=tmp_path,
        content_type=effective_content_type,
        destination=destination,
        user_id=current_user["id"]
    )

    return job


@app.get("/ocr/jobs/", response_model=List[schemas.OcrJob])
async def get_ocr_jobs(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(auth.get_current_active_user)
):
    """Get all OCR jobs for the current user."""
    return await asyncio.to_thread(crud.get_user_ocr_jobs, db, user_id=current_user["id"])


@app.get("/ocr/jobs/{job_id}", response_model=schemas.OcrJob)
async def get_ocr_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(auth.get_current_active_user)
):
    """Get the status of a single OCR job."""
    job = await asyncio.to_thread(crud.get_ocr_job, db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.get("user_id") != current_user.get("id"):
        raise HTTPException(status_code=403, detail="Not authorized to view this job.")
    return job


@app.delete("/ocr/jobs/{job_id}", response_model=schemas.OcrJob)
async def delete_ocr_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(auth.get_current_active_user)
):
    """Deletes a job notification."""
    job = await asyncio.to_thread(crud.get_ocr_job, db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.get("user_id") != current_user.get("id"):
        raise HTTPException(status_code=403, detail="Not authorized to delete this job.")

    return await asyncio.to_thread(crud.delete_ocr_job, db, job_id)


# --- Data Export (Excel / CSV) ---
@app.get("/export/data")
def export_data(
    destination: Optional[str] = None, user_id: Optional[str] = None,
    first_name: Optional[str] = None, last_name: Optional[str] = None,
    preview: bool = False,
    document_type: Optional[DocumentType] = Query(None, description="PP = passeports (PASS accepté), PI = cartes d'identité; absent = tous"),
    export_format: ExportFormat = Query("xlsx", alias="format"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(auth.get_current_active_user)
):
    """Exports the filtered documents as an Excel (.xlsx, default) or CSV
    file, or as JSON rows when preview=true (used by the on-screen preview
    table). The optional document_type filter (PP/PI) narrows the rows to one
    document type; without it, every matching row is exported."""
    effective_user_id = current_user.get("id")
    if current_user.get("role") == "admin":
        effective_user_id = user_id

    filtered_data = crud.filter_data(db, destination, effective_user_id, first_name, last_name)
    filtered_data = _filter_by_document_type(filtered_data, document_type)
    if not filtered_data:
        raise HTTPException(status_code=404, detail="Aucune donnée de passeport trouvée pour les critères donnés")

    if preview:
        return _export_rows_for_preview(_build_export_rows(filtered_data))

    filename_parts = ["passeports"]
    if destination:
        filename_parts.append(destination.replace(' ', '_').lower())

    if current_user.get("role") == 'admin':
        if user_id:
            filtered_user = crud.get_user(db, user_id)
            if filtered_user:
                filename_parts.append(f"pour_{filtered_user.get('user_name', 'user').lower()}")
            else:
                filename_parts.append(f"pour_utilisateur_{user_id}")
        else:
            filename_parts.append("rapport_complet")
    else:
        filename_parts.append(f"pour_{current_user.get('user_name', 'user').lower()}")

    return _export_file_response(filtered_data, "_".join(filename_parts), export_format)


@app.post("/export/data/selection")
def export_selected_data(
    payload: schemas.PassportExportSelection,
    export_format: ExportFormat = Query("xlsx", alias="format"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(auth.get_current_active_user)
):
    """Exports the explicitly selected documents as an Excel (.xlsx, default)
    or CSV file, with the same columns and formatting as /export/data."""
    if not payload.passport_ids:
        raise HTTPException(status_code=400, detail="Aucun passeport sélectionné.")

    passports = crud.get_passports_by_ids(db, [str(pid) for pid in payload.passport_ids])
    if current_user.get("role") != "admin":
        passports = [p for p in passports if p.get("owner_id") == current_user.get("id")]
    if not passports:
        raise HTTPException(status_code=404, detail="Aucune donnée de passeport trouvée pour les critères donnés")

    return _export_file_response(passports, "selection_passeports", export_format)


@app.get("/passports/", response_model=list[schemas.Passport])
def read_passports(
    db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(auth.get_current_active_user),
    user_filter: Optional[str] = Query(None),
    voyage_filter: Optional[str] = Query(None),
    destination_filter: Optional[str] = Query(None)
):
    if current_user.get("role") == "admin":
        return crud.get_passports(db=db, user_filter=user_filter, voyage_filter=voyage_filter)

    return crud.get_passports_by_user(
        db=db, user_id=str(current_user["id"]), destination=destination_filter
    )


@app.put("/passports/{passport_id}", response_model=schemas.Passport)
def update_passport(passport_id: str, passport_update: schemas.PassportCreate, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(auth.get_current_active_user)):
    db_passport = crud.get_passport(db, passport_id=passport_id)
    if db_passport is None:
        raise HTTPException(status_code=404, detail="Passeport non trouvé")
    if current_user.get("role") != "admin" and db_passport.get("owner_id") != current_user.get("id"):
        raise HTTPException(status_code=403, detail="Non autorisé à mettre à jour ce passeport")
    return crud.update_passport(db=db, passport_id=str(passport_id), passport_update=passport_update)


@app.delete("/passports/{passport_id}", response_model=schemas.Passport)
def delete_passport(passport_id: str, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(auth.get_current_active_user)):
    db_passport = crud.get_passport(db, passport_id=passport_id)
    if db_passport is None:
        raise HTTPException(status_code=404, detail="Passeport non trouvé")
    if current_user.get("role") != "admin" and db_passport.get("owner_id") != current_user.get("id"):
        raise HTTPException(status_code=403, detail="Non autorisé à supprimer ce passeport")
    return crud.delete_passport(db=db, passport_id=passport_id)


@app.post("/passports/delete-multiple", response_model=dict)
def delete_multiple_passports(
    payload: schemas.PassportDeleteMultiple,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(auth.get_current_active_user)
):
    if not payload.passport_ids:
        return {"deleted_count": 0}

    deleted_count = crud.delete_multiple_passports(
        db=db,
        passport_ids=[str(pid) for pid in payload.passport_ids],
        user_id=current_user["id"],
        role=current_user["role"]
    )
    return {"deleted_count": deleted_count}


# --- Voyage and Destination Routes ---
@app.post("/voyages/", response_model=schemas.Voyage)
def create_voyage(voyage: schemas.VoyageCreate, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(auth.get_current_active_user)):
    return crud.create_user_voyage(db=db, voyage=voyage, user_id=current_user["id"], passport_ids=[str(pid) for pid in voyage.passport_ids])


@app.get("/voyages/", response_model=list[schemas.Voyage])
def read_voyages(db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(auth.get_current_active_user), user_filter: Optional[str] = None):
    if current_user.get("role") == "admin":
        return crud.get_voyages(db=db, user_filter=user_filter)
    return crud.get_voyages_by_user(db=db, user_id=str(current_user["id"]))


@app.put("/voyages/{voyage_id}", response_model=schemas.Voyage)
def update_voyage(voyage_id: str, voyage_update: schemas.VoyageCreate, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(auth.get_current_active_user)):
    db_voyage = crud.get_voyage(db, voyage_id=voyage_id)
    if db_voyage is None:
        raise HTTPException(status_code=404, detail="Voyage non trouvé")
    if current_user.get("role") != "admin" and db_voyage.get("user_id") != current_user.get("id"):
        raise HTTPException(status_code=403, detail="Non autorisé à mettre à jour ce voyage")
    return crud.update_voyage(db=db, voyage_id=voyage_id, voyage_update=voyage_update, passport_ids=[str(pid) for pid in voyage_update.passport_ids])


@app.delete("/voyages/{voyage_id}", response_model=schemas.Voyage)
def delete_voyage(voyage_id: str, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(auth.get_current_active_user)):
    db_voyage = crud.get_voyage(db, voyage_id=voyage_id)
    if db_voyage is None:
        raise HTTPException(status_code=404, detail="Voyage non trouvé")
    if current_user.get("role") != "admin" and db_voyage.get("user_id") != current_user.get("id"):
        raise HTTPException(status_code=403, detail="Non autorisé à supprimer ce voyage")
    return crud.delete_voyage(db=db, voyage_id=voyage_id)


@app.get("/destinations/", response_model=List[str])
def get_unique_destinations(user_id: Optional[str] = Query(None), db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(auth.get_current_active_user)):
    target_user_id = current_user.get("id")
    if current_user.get("role") == "admin" and user_id:
        target_user_id = user_id
    return crud.get_destinations_by_user_id(db, user_id=str(target_user_id))

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
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Query, Form, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from jose import jwt, JWTError
from sqlalchemy import update as sa_update
from sqlalchemy.orm import Session

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import crud, models, schemas, auth
import ocr_service
from database import get_db, engine, SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

# Every self-registered account starts with exactly this many page credits
# (1 credit = 1 extracted page).
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
DocumentType = Literal["PP", "PI"]
ExportFormat = Literal["xlsx", "csv"]
# ASCII digit class on purpose: the frontend regex (JS \d) is ASCII-only, and
# both sides must classify every value identically.
_PASSPORT_NUMBER_RE = re.compile(r"^[0-9]{2}[A-Z]{2}[0-9]{5}$")


def document_type_of(passport_number: Any) -> str:
    """'PP' for a French passport number, 'PI' for any other document number."""
    number = str(passport_number or "").strip().upper()
    return DOC_TYPE_PASSPORT if _PASSPORT_NUMBER_RE.match(number) else DOC_TYPE_ID_CARD


# Exported columns, in order, with the French headers of the on-screen results
# table (columnTranslations in the frontend). Internal ids are never exported.
EXPORT_COLUMNS = ["document_type", "first_name", "last_name", "birth_date", "expiration_date",
                  "nationality", "passport_number", "destination", "confidence_score"]
EXPORT_HEADERS = {
    "document_type": "Type", "first_name": "Prénom", "last_name": "Nom de famille",
    "birth_date": "Date de Naissance", "expiration_date": "Date d'Expiration",
    "nationality": "Nationalité", "passport_number": "Numéro de Passeport",
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
    db = SessionLocal()
    try:
        await _run_ocr_extraction_job(db, job_id, file_path, content_type, destination, user_id)
    finally:
        # Unlink first: it cannot raise past the except, while db.close (an
        # awaitable) could — the spool file must be reclaimed regardless.
        try:
            os.unlink(file_path)
        except OSError:
            pass
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

    # Charge one credit per processed page and track the page counter.
    page_count = len(extraction_results)
    if page_count > 0:
        try:
            def _charge_credits():
                # One atomic UPDATE — the SQL equivalent of firestore.Increment.
                db.execute(
                    sa_update(models.User)
                    .where(models.User.id == str(user_id))
                    .values(
                        page_credits=models.User.page_credits - page_count,
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


# --- Lifespan for application startup/shutdown ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        logger.info("🚀 Backend starting up (PostgreSQL).")
        # Create any missing tables on boot (idempotent), then look up the admin.
        await asyncio.to_thread(models.Base.metadata.create_all, engine)
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

    yield

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
app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

# --- Serve Static Frontend Files ---
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- CORS Middleware Configuration ---
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
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
    return [row for row in rows if document_type_of(row.get("passport_number")) == document_type]


def _build_export_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Export rows in EXPORT_COLUMNS order: the derived Type column first,
    internal ids (id, owner_id) dropped, text values uppercased."""
    export_rows = []
    for row in rows:
        export_row = {"document_type": document_type_of(row.get("passport_number"))}
        for column in EXPORT_COLUMNS[1:]:
            export_row[column] = _export_cell_value(row.get(column))
        export_rows.append(export_row)
    return export_rows


def _displayed_length(value: Any) -> int:
    """Number of characters Excel displays for a cell value (dates render as
    YYYY-MM-DD, empty cells as nothing)."""
    if value is None:
        return 0
    if isinstance(value, (datetime, date)):
        return 10
    return len(str(value))


def _format_export_worksheet(worksheet) -> None:
    """Centers every cell and auto-fits each column to its longest displayed
    value (header included) so nothing is ever truncated in Excel."""
    center = Alignment(horizontal="center", vertical="center")
    for column_cells in worksheet.columns:
        longest = 0
        for cell in column_cells:
            cell.alignment = center
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
    """CSV cell text: dates as YYYY-MM-DD, None as empty, formula-like text
    neutralised, and all-digit text (12-digit CNI numbers) wrapped as ="…" so
    that Excel keeps it as text instead of re-typing it as a number (which
    drops leading zeros and displays 1.23457E+11)."""
    if value is None:
        return ""
    if isinstance(value, (datetime, date)):
        return value.isoformat()[:10]
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
    """Preview cell value: dates as YYYY-MM-DD, missing values as blank cells
    (the table renders raw values, so None must not appear as 'null')."""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if value is None:
        return ""
    return value


def _export_rows_for_preview(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Serializes export rows for the JSON on-screen preview."""
    return [{key: _preview_value(value) for key, value in row.items()} for row in rows]


# --- Authentication Routes ---
@app.post("/token", response_model=schemas.Token)
@limiter.limit("5/minute")
def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.get("user_name")})
    return {"access_token": access_token, "token_type": "bearer"}


# --- SSE ROUTE FOR REAL-TIME UPDATES ---
@app.get("/events")
async def events(request: Request, token: str = Query(...), db: Session = Depends(get_db)):
    """Server-Sent Events endpoint. Gracefully handles disconnection and
    server shutdown."""
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

    return crud.update_user(db=db, user_id=current_user["id"], user_update=user_update)


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
    return crud.create_user(db=db, user=user, role=getattr(user, 'role', 'user'))


@app.get("/admin/filterable-users", response_model=list[schemas.User], dependencies=[Depends(auth.require_admin)])
def read_filterable_users(db: Session = Depends(get_db)):
    return crud.get_all_users_for_filtering(db)


# --- Passport / Identity Document Routes ---
@app.post("/passports/", response_model=schemas.Passport)
def create_passport(passport: schemas.PassportCreate, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(auth.get_current_active_user)):
    return crud.create_user_passport(db=db, passport=passport, user_id=current_user["id"])


@app.post("/passports/upload-and-extract/", response_model=schemas.OcrJob)
async def upload_and_extract_passport(
    background_tasks: BackgroundTasks,
    destination: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(auth.get_current_active_user)
):
    if current_user.get("page_credits", 0) <= 0:
        raise HTTPException(status_code=403, detail="Crédits insuffisants. Veuillez contacter l'administrateur.")

    # Spool the upload to a temp file instead of reading it into memory: the
    # bytes would otherwise stay pinned in RAM for the whole background job.
    # The background task owns the file and deletes it when the job ends.
    fd, tmp_path = tempfile.mkstemp(prefix="ocr_upload_")
    file_size = 0
    try:
        with os.fdopen(fd, "wb") as spool:
            while chunk := await file.read(1024 * 1024):
                spool.write(chunk)
                file_size += len(chunk)

        if file_size == 0:
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")

        job_id = str(uuid.uuid4())
        job = await asyncio.to_thread(crud.create_ocr_job, db=db, job_id=job_id, user_id=current_user["id"], file_name=file.filename or "unknown")
    except Exception:
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
        content_type=file.content_type or "application/octet-stream",
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
    document_type: Optional[DocumentType] = Query(None, description="PP = passeports, PI = cartes d'identité; absent = tous"),
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

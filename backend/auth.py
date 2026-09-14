# /auth.py
import logging
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Dict
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

import config
import schemas
from database import get_db

load_dotenv()

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY", "a_default_fallback_key_if_not_set")
ALGORITHM = "HS256"
# A session lasts this long after it was last renewed. It is renewed only by
# real activity (POST /session/refresh, called by the app when the person uses
# the page), so this is the inactivity timeout: 12 hours. It used to be a fixed
# 30 minutes from login that nothing renewed.
ACCESS_TOKEN_EXPIRE_MINUTES = config.SESSION_IDLE_MINUTES

ACCOUNT_ACTIVE = "active"


def is_active_account(user: Dict[str, Any]) -> bool:
    """Only an active account may log in or hold a session. A free-trial request
    is 'pending' until validated; a refused one is 'rejected'."""
    return (user.get("status") or ACCOUNT_ACTIVE) == ACCOUNT_ACTIVE


def session_claims(user: Dict[str, Any]) -> Dict[str, Any]:
    """The claims of a session token for this account. "sv" is its session
    version: a password reset raises it, which ends every session issued before."""
    return {"sub": user.get("user_name"), "sv": int(user.get("session_version") or 0)}

# argon2 for every new hash. bcrypt stays in the list as a VERIFIER only:
# `deprecated="auto"` marks it legacy, so `needs_update()` is true for any
# bcrypt hash and login re-hashes it to argon2 in place (see
# `authenticate_user`). The application is pre-launch and the users table is
# expected to be empty, in which case no bcrypt hash will ever be seen — but
# the production database could not be reached from here to confirm that
# (see the handover note), and argon2-only would have locked out any account
# that did exist. This costs one list entry and removes that risk entirely.
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
    bcrypt__ident="2b",
)

# `auto_error=False`: a missing Authorization header is no longer an error by
# itself, because the session cookie is now an equally valid way to present
# the token. `get_current_user` decides.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # An unknown or corrupt hash must fail closed, not 500.
        return False


def get_password_hash(password):
    return pwd_context.hash(password)


# --- Per-account lockout --------------------------------------------------
# The existing 5/minute limit is per IP, which cannot stop a guess distributed
# across addresses and punishes a whole agency behind one NAT gateway. This
# counts failures per ACCOUNT instead, and the two run side by side.
#
# In-process and therefore per-worker: with several gunicorn workers the
# effective budget is the limit times the worker count. That is a deliberate
# trade — a shared counter needs Redis, which is infrastructure this package
# is not allowed to add. Documented in the handover.
_failures: Dict[str, list] = {}
_failures_lock = threading.Lock()


def _prune(entries: list, now: float) -> list:
    window = config.LOGIN_LOCKOUT_SECONDS
    return [stamp for stamp in entries if now - stamp < window]


def is_locked_out(username: str) -> bool:
    if not username:
        return False
    now = time.time()
    with _failures_lock:
        entries = _prune(_failures.get(username, []), now)
        _failures[username] = entries
        return len(entries) >= config.LOGIN_MAX_FAILURES


def record_login_failure(username: str) -> None:
    if not username:
        return
    now = time.time()
    with _failures_lock:
        entries = _prune(_failures.get(username, []), now)
        entries.append(now)
        _failures[username] = entries


def reset_login_failures(username: str) -> None:
    if not username:
        return
    with _failures_lock:
        _failures.pop(username, None)


def authenticate_user(db: Session, username: str, password: str) -> Any:
    import crud
    user = crud.get_user_by_username(db, username=username)
    if not user or not verify_password(password, str(user.get("hashed_password"))):
        return False
    if not is_active_account(user):
        # Same answer as a wrong password: the caller learns nothing about the
        # account. (A pending trial account has no usable password anyway.)
        return False

    # Transparent upgrade: a hash produced by a superseded scheme is replaced
    # with an argon2 one on the next successful login, while the plaintext is
    # in hand. Nothing is logged and nothing about the response changes.
    try:
        stored = str(user.get("hashed_password"))
        if pwd_context.needs_update(stored):
            crud.update_user_password_hash(db, user_id=user.get("id"), hashed_password=get_password_hash(password))
    except Exception:
        # A failed re-hash must never fail the login it rode in on.
        logger.warning("Password hash upgrade skipped for one account.")

    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def set_session_cookie(response, token: str) -> None:
    """Puts the session token in an HttpOnly cookie.

    HttpOnly so no script can read it (an XSS then cannot exfiltrate the
    session), Secure in production so it never crosses plain HTTP, SameSite=Lax
    so it is not sent on a cross-site POST. max_age matches the token's own
    expiry, so the cookie and the JWT stop being valid at the same moment.
    """
    response.set_cookie(
        key=config.SESSION_COOKIE_NAME,
        value=token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=config.cookie_secure(),
        samesite=config.SESSION_COOKIE_SAMESITE,
        path="/",
    )
    # Readable by design, and carries no secret: see SESSION_HINT_COOKIE_NAME.
    response.set_cookie(
        key=config.SESSION_HINT_COOKIE_NAME,
        value="1",
        max_age=config.SESSION_HINT_MAX_AGE,
        httponly=False,
        secure=config.cookie_secure(),
        samesite=config.SESSION_COOKIE_SAMESITE,
        path="/",
    )


def clear_session_cookie(response) -> None:
    response.delete_cookie(
        key=config.SESSION_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=config.cookie_secure(),
        samesite=config.SESSION_COOKIE_SAMESITE,
    )
    response.delete_cookie(
        key=config.SESSION_HINT_COOKIE_NAME,
        path="/",
        httponly=False,
        secure=config.cookie_secure(),
        samesite=config.SESSION_COOKIE_SAMESITE,
    )


def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les informations d'identification",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # The cookie is consulted only when no Authorization header was sent, so
    # the existing Bearer flow keeps exactly the precedence it had. Both are
    # supported on purpose: the browser now uses the cookie, while every
    # non-browser client that works today continues to work unchanged.
    if not token:
        token = request.cookies.get(config.SESSION_COOKIE_NAME)
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not isinstance(username, str):
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    if token_data.username is None:
        raise credentials_exception
    import crud
    user = crud.get_user_by_username(db, username=str(token_data.username))
    if user is None or not is_active_account(user):
        raise credentials_exception
    # A token issued before session versions existed carries no "sv"; it counts
    # as version 0, which is what every account had, so the deploy logs nobody out.
    if int(payload.get("sv") or 0) != int(user.get("session_version") or 0):
        raise credentials_exception
    return user


def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    return current_user


def require_admin(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Privilèges d'administrateur requis.")
    return current_user

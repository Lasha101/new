# /mailer.py
"""Outgoing email.

Standard library only (smtplib), so no dependency was added. The backend is
chosen by config.mail_backend(): real SMTP in production, an in-memory outbox in
development and tests.

What is never logged: the recipient, the subject, the body. A password email
carries a working link, which is a credential, and every email carries personal
data. Log lines name the kind of email and the outcome, nothing more.
"""
import logging
import os
import smtplib
import ssl
import threading
import uuid
from dataclasses import dataclass, field
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from typing import List, Optional, Sequence, Tuple

import config

logger = logging.getLogger(__name__)


# (file name, content, MIME type) — an invoice: ("Facture-F-2026-00001.pdf", b"%PDF…", "application/pdf").
Attachment = Tuple[str, bytes, str]


@dataclass
class SentEmail:
    to: str
    subject: str
    body: str
    kind: str
    reply_to: Optional[str] = None
    attachments: List[Attachment] = field(default_factory=list)


# The outbox backend's memory. Tests read it; nothing else should.
OUTBOX: List[SentEmail] = []
_outbox_lock = threading.Lock()


def is_configured() -> bool:
    """True when an email sent now would actually go somewhere."""
    backend = config.mail_backend()
    if backend == "smtp":
        return bool(config.smtp_settings()["host"])
    return backend == "outbox"


def _build(to: str, subject: str, body: str, reply_to: Optional[str],
           attachments: Sequence[Attachment] = ()) -> EmailMessage:
    message = EmailMessage()
    message["From"] = config.mail_from()
    message["To"] = to
    message["Subject"] = subject
    message["Date"] = formatdate(localtime=False)
    message["Message-ID"] = make_msgid(domain="scanid.fr")
    if reply_to:
        message["Reply-To"] = reply_to
    message.set_content(body)
    for filename, data, mime_type in attachments:
        maintype, _, subtype = mime_type.partition("/")
        message.add_attachment(data, maintype=maintype, subtype=subtype, filename=filename)
    return message


def send(to: str, subject: str, body: str, kind: str, reply_to: Optional[str] = None,
         attachments: Optional[Sequence[Attachment]] = None) -> bool:
    """Sends one plain-text email, with its attachments if any (an invoice's
    PDF). Returns True when it was handed over.

    Never raises: callers run it after the HTTP response (BackgroundTasks), where
    an exception would only be swallowed less legibly.
    """
    backend = config.mail_backend()
    # The caller's reply_to wins (the trial notification: the requester).
    reply_to = reply_to or config.mail_reply_to() or None
    attachments = list(attachments or [])
    try:
        if backend == "outbox":
            with _outbox_lock:
                OUTBOX.append(SentEmail(to=to, subject=subject, body=body, kind=kind, reply_to=reply_to,
                                        attachments=attachments))
            outbox_dir = os.getenv("MAIL_OUTBOX_DIR")
            if outbox_dir:
                os.makedirs(outbox_dir, exist_ok=True)
                path = os.path.join(outbox_dir, f"{kind}-{uuid.uuid4().hex}.eml")
                fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                with os.fdopen(fd, "wb") as handle:
                    handle.write(bytes(_build(to, subject, body, reply_to, attachments)))
            logger.info("Email kept in the outbox: kind=%s", kind)
            return True

        if backend == "smtp":
            settings = config.smtp_settings()
            if not settings["host"]:
                logger.error("Email not sent (SMTP_HOST missing): kind=%s", kind)
                return False
            message = _build(to, subject, body, reply_to, attachments)
            with smtplib.SMTP(settings["host"], settings["port"], timeout=settings["timeout"]) as smtp:
                if settings["starttls"]:
                    smtp.starttls(context=ssl.create_default_context())
                if settings["username"]:
                    smtp.login(settings["username"], settings["password"])
                smtp.send_message(message)
            logger.info("Email sent: kind=%s", kind)
            return True

        logger.error("Email not sent (MAIL_BACKEND=disabled or email not configured): kind=%s", kind)
        return False
    except Exception as exc:  # noqa: BLE001 — see the docstring
        # The exception class only: an SMTP error string can echo the recipient.
        logger.error("Email not sent: kind=%s error=%s", kind, type(exc).__name__)
        return False

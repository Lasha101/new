# /log_redaction.py
"""A logging filter that keeps identity data out of the logs.

Two layers, because neither is sufficient alone:

1. **Call sites.** The upload and OCR paths were reviewed and the statements
   that used to interpolate a name, a document number or an uploaded filename
   now log an identifier instead. That is the real fix.

2. **This filter.** A safety net for everything the review did not reach:
   a third-party library, an exception string that happens to carry a
   traceback frame with a local variable in it, a future call site written by
   someone who has not read this file. It rewrites the *formatted* message, so
   it catches interpolated arguments too.

The filter is deliberately pattern-based and conservative. It cannot know that
`DUPONT` is a surname, so it does not try: it redacts the shapes that are
unambiguous (MRZ lines, passport and CNI numbers, dates of birth, long base64
blobs) and the code stops passing it the rest.
"""
import logging
import re
from typing import List, Pattern, Tuple

REDACTED = "[redacted]"

# An MRZ line: TD3 is 2 lines of 44, TD2 2 of 36, TD1 3 of 30. The filler is
# '<', which is what makes these unmistakable in a log line.
_MRZ = re.compile(r"[A-Z0-9<]{20,}<{2,}[A-Z0-9<]*|[A-Z0-9<]*<{3,}[A-Z0-9<]{10,}")

# A French passport number: 2 digits, 2 letters, 5 digits (the same shape
# main.py::document_type_of uses to classify a document as PASS).
_PASSPORT_NUMBER = re.compile(r"\b[0-9]{2}[A-Z]{2}[0-9]{5}\b")

# A CNI number: 12 digits (old format) or 9 alphanumerics (new format).
_CNI_NUMBER = re.compile(r"\b[0-9]{12}\b")

# Dates in the shapes the extractor produces, so a date of birth cannot ride
# out in a log line. Deliberately not applied to ISO timestamps with a time
# component, which are how log lines say *when*.
_DATE = re.compile(r"\b\d{2}[/.-]\d{2}[/.-]\d{4}\b|\b\d{4}-\d{2}-\d{2}(?!T)\b")

# A long run of base64/hex — an image or a token that has escaped into a
# message. Short runs are left alone: job ids and hashes are how a log line is
# made useful, and a uuid is 36 characters.
_BLOB = re.compile(r"\b[A-Za-z0-9+/=]{120,}\b")

# `Bearer eyJ...`, and the query-string form the SSE endpoint still uses.
_BEARER = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]+")
_TOKEN_QS = re.compile(r"(?i)([?&](?:token|access_token|password|pwd)=)[^&\s]+")

_PATTERNS: List[Tuple[Pattern, str]] = [
    (_BEARER, "Bearer " + REDACTED),
    (_TOKEN_QS, r"\1" + REDACTED),
    (_MRZ, REDACTED),
    (_PASSPORT_NUMBER, REDACTED),
    (_CNI_NUMBER, REDACTED),
    (_DATE, REDACTED),
    (_BLOB, REDACTED),
]


def redact(text: str) -> str:
    """Every known identity shape in a string replaced by `[redacted]`."""
    if not text:
        return text
    for pattern, replacement in _PATTERNS:
        text = pattern.sub(replacement, text)
    return text


class RedactingFilter(logging.Filter):
    """Rewrites each record's formatted message in place.

    `record.getMessage()` is used so `logger.info("name %s", name)` is caught
    as surely as an f-string; the arguments are then cleared because they have
    already been folded into the message.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
        except Exception:
            return True

        redacted = redact(message)
        if redacted != message:
            record.msg = redacted
            record.args = ()

        # An exception's own text is formatted separately by the handler, so it
        # would otherwise bypass everything above.
        if record.exc_info and record.exc_info[1] is not None:
            exception = record.exc_info[1]
            original = str(exception)
            cleaned = redact(original)
            if cleaned != original:
                record.exc_info = (
                    record.exc_info[0],
                    type(exception)(cleaned) if _is_reconstructable(exception) else Exception(cleaned),
                    record.exc_info[2],
                )
        return True


def _is_reconstructable(exception: BaseException) -> bool:
    """True when `type(e)(str)` will not blow up. Many exception classes take
    more than one argument, and a filter must never raise."""
    try:
        type(exception)("probe")
        return True
    except Exception:
        return False


def install(root: logging.Logger = None) -> RedactingFilter:
    """Attaches the filter to every handler on the root logger.

    It goes on the HANDLERS rather than the root logger itself: a filter on a
    logger is not consulted for records that propagate up from a child logger,
    which would leave every `logging.getLogger(__name__)` in the codebase — and
    every third-party library — unfiltered.
    """
    logger = root or logging.getLogger()
    redactor = RedactingFilter()
    for handler in logger.handlers:
        if not any(isinstance(existing, RedactingFilter) for existing in handler.filters):
            handler.addFilter(redactor)
    return redactor

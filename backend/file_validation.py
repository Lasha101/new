# /file_validation.py
"""Upload validation: type by magic bytes, and a safe filename.

The `Content-Type` header and the filename extension are both supplied by the
client and are both trivially forged, so neither decides anything here. The
first bytes of the file decide.

The allow-list deliberately mirrors `frontend/src/upload/fileSniff.js`
signature for signature. That file is what the browser uses to decide whether
it can prepare a document, and this one is what the server uses to decide
whether it will accept it — if the two ever disagree, a document the app
happily compresses is rejected on arrival. The two lists are asserted equal by
`tests/test_upload_validation.py::test_allow_list_matches_the_frontend_sniffer`,
which reads the JavaScript.
"""
from typing import Optional, Set

# ISO-BMFF `ftyp` brands meaning "HEIF still image" — the same set, in the same
# order, as HEIF_BRANDS in fileSniff.js.
HEIF_BRANDS: Set[str] = {
    "heic", "heix", "heim", "heis",   # HEVC-coded still images
    "hevc", "hevx", "hevm", "hevs",   # HEVC-coded image sequences
    "mif1", "msf1",                   # generic HEIF image / image sequence
}

# AVIF shares the HEIF container and lists `mif1` as a compatible brand, so it
# must be recognised separately or an AVIF would be taken for a HEIC.
AVIF_BRANDS: Set[str] = {"avif", "avis"}

# What the server accepts. Every one of these can reach the endpoint today:
# the picker offers PNG/JPEG/HEIC/PDF, and the drop zone accepts anything whose
# type starts with `image/` (App.jsx handleDrop), which is how GIF, WebP, TIFF
# and AVIF get in. `ocr_service.py` passes any `image/*` to Vision and Vision
# reads all of them, so none of these is a new capability — narrowing the list
# would REJECT something that works today, which the brief forbids.
ALLOWED_TYPES: Set[str] = {"jpeg", "png", "pdf", "heic", "avif", "gif", "webp", "tiff"}

# The media type each sniffed format is handed onward as. The OCR service
# branches on `image/*` versus `application/pdf`, so this is what makes a file
# with a forged header still take the correct path.
CANONICAL_MEDIA_TYPE = {
    "jpeg": "image/jpeg",
    "png": "image/png",
    "pdf": "application/pdf",
    "heic": "image/heic",
    "avif": "image/avif",
    "gif": "image/gif",
    "webp": "image/webp",
    "tiff": "image/tiff",
}

# 12 bytes is enough for every signature below; the ftyp brand list needs more.
SNIFF_LENGTH = 64


def _ascii(data: bytes, offset: int, length: int) -> str:
    chunk = data[offset:offset + length]
    if len(chunk) != length:
        return ""
    try:
        return chunk.decode("ascii")
    except UnicodeDecodeError:
        return ""


def _ftyp_brands(data: bytes) -> list:
    """Every brand an ISO-BMFF file declares: the major brand plus every
    compatible brand. An iPhone HEIC often declares `mif1` as major with `heic`
    further down, so reading the major brand alone is not enough."""
    if len(data) < 12 or _ascii(data, 4, 4) != "ftyp":
        return []
    brands = [_ascii(data, 8, 4)]
    # The compatible-brands list runs from byte 16 to the end of the box.
    try:
        box_size = int.from_bytes(data[0:4], "big")
    except (ValueError, TypeError):
        box_size = 0
    limit = min(len(data), box_size if box_size >= 16 else len(data))
    offset = 16
    while offset + 4 <= limit:
        brand = _ascii(data, offset, 4)
        if brand:
            brands.append(brand)
        offset += 4
    return [brand for brand in brands if brand]


def sniff_file_type(data: bytes) -> str:
    """The format of a file from its first bytes.

    Returns 'jpeg' | 'png' | 'pdf' | 'heic' | 'avif' | 'gif' | 'webp' | 'tiff'
    | 'unknown'. Mirrors sniffFileType() in fileSniff.js.
    """
    if data.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data.startswith(b"%PDF"):
        return "pdf"
    if data.startswith(b"GIF8"):
        return "gif"
    if _ascii(data, 0, 4) == "RIFF" and _ascii(data, 8, 4) == "WEBP":
        return "webp"
    if data.startswith(b"II\x2a\x00") or data.startswith(b"MM\x00\x2a"):
        return "tiff"

    brands = _ftyp_brands(data)
    if brands:
        # AVIF wins when declared: it lists mif1 as compatible, and handing an
        # AVIF to a HEIC decoder produces a failure, not an image.
        if any(brand in AVIF_BRANDS for brand in brands):
            return "avif"
        if any(brand in HEIF_BRANDS for brand in brands):
            return "heic"
    return "unknown"


def is_allowed(data: bytes) -> bool:
    return sniff_file_type(data) in ALLOWED_TYPES


def safe_filename(raw: Optional[str], fallback: str = "document") -> str:
    """A filename that is safe to store and to log.

    The supplied name is never trusted: it is used for nothing but display, and
    it must not be able to walk a path, terminate a C string, break a log line
    or grow without bound.

    - every directory separator and the whole leading path is dropped, so
      `../../etc/passwd` becomes `passwd`
    - NUL and every other control character is removed
    - the result is capped at 120 characters, extension preserved where it fits
    - an empty or entirely-stripped name falls back to `document`
    """
    if not raw:
        return fallback

    # Take the basename under BOTH separator conventions: a Windows client can
    # send a backslash path that os.path.basename leaves untouched on Linux.
    name = str(raw).replace("\\", "/").split("/")[-1]

    # Strip control characters (NUL included) and anything non-printable.
    name = "".join(ch for ch in name if ch.isprintable() and ch not in '\r\n\t')

    # A name of dots only (`.`, `..`) is a path element, not a name.
    if not name or set(name) <= {"."}:
        return fallback

    if len(name) > 120:
        stem, dot, ext = name.rpartition(".")
        if dot and 0 < len(ext) <= 10:
            name = stem[:120 - len(ext) - 1] + "." + ext
        else:
            name = name[:120]

    return name or fallback

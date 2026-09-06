# /password_policy.py
"""The password policy, enforced on the server.

The frontend shows the same four rules live as the user types, but that display
is a convenience only: every rule here is checked again on every request that
sets a password, so a client that posts directly to the API is held to exactly
the same standard.

Order matters. Composition is checked first and the blocklist afterwards, so a
password that fails both is reported against the concrete rule the user can act
on, and so the blocklist can never be mistaken for the whole policy —
`Motdepasse12!!` satisfies all four composition rules and is still refused.

Nothing in this module logs, echoes or returns the password it was given.
"""
import os
import re
import unicodedata
from typing import Iterable, List, Optional, Set

MIN_LENGTH = 12
MIN_UPPERCASE = 1
MIN_DIGITS = 2
MIN_SPECIALS = 2

# Shown to the user as the illustrative set. Any non-alphanumeric character
# counts, so an unusual but valid choice is never refused for being unusual.
DISPLAYED_SPECIALS = "! ? @ # $ % & * -"

_BLOCKLIST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "common_passwords.txt")

# Digits and symbols people substitute for letters. Applied when normalising a
# candidate for the blocklist so `M0tD3P@sse` collapses onto `motdepasse`.
_LEET = str.maketrans({
    "0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "8": "b", "9": "g",
    "@": "a", "$": "s", "!": "i", "|": "l", "€": "e", "£": "l",
})


def _load_blocklist(path: str = _BLOCKLIST_FILE) -> Set[str]:
    entries: Set[str] = set()
    try:
        with open(path, "r", encoding="utf-8") as handle:
            for line in handle:
                entry = line.strip().lower()
                if entry and not entry.startswith("#"):
                    entries.add(entry)
    except OSError:
        # A missing list must not make every password acceptable; it makes the
        # blocklist empty, and the composition rules still apply. The condition
        # is loud in the logs rather than silent.
        import logging
        logging.getLogger(__name__).error(
            "Common-password blocklist could not be read at %s; composition rules still apply.", path
        )
    return entries


COMMON_PASSWORDS: Set[str] = _load_blocklist()


def _strip_accents(value: str) -> str:
    return "".join(
        ch for ch in unicodedata.normalize("NFKD", value) if not unicodedata.combining(ch)
    )


def normalise_for_blocklist(password: str) -> Set[str]:
    """Every form of a candidate worth testing against the blocklist.

    A blocklist of literals only ever catches the literal. Users do not type
    the literal — they type it with a capital, a year on the end and a couple of
    exclamation marks, which is exactly the shape the composition rules push
    them towards. So the candidate is reduced several ways and every reduction
    is tested.
    """
    lowered = _strip_accents(password.lower())

    def trim(value: str) -> str:
        """Leading and trailing runs of anything that is not a letter."""
        return re.sub(r"^[^a-z]+|[^a-z]+$", "", value)

    def letters_only(value: str) -> str:
        return re.sub(r"[^a-z]", "", value)

    # Both reductions are applied in BOTH orders, because neither order alone
    # is enough. De-leeting first turns the trailing `20!!` of `M0tD3P@sse20!!`
    # into the letters `2oii`, which the trim can then no longer remove; and
    # trimming first leaves `m0td3p@sse`, which only de-leeting resolves. So
    # every seed is de-leeted and every de-leeted form is trimmed again.
    seeds = {lowered, trim(lowered), letters_only(lowered)}

    forms = set()
    for seed in seeds:
        for form in (seed, seed.translate(_LEET)):
            forms.add(form)
            forms.add(trim(form))
            forms.add(letters_only(form))

    return {form for form in forms if form}


def _zxcvbn_score(password: str) -> Optional[int]:
    """zxcvbn's 0-4 strength score, or None when the library is absent.

    Layered on top of the bundled list, not instead of it: the list knows the
    French stems zxcvbn's English corpus does not (it scores `Motdepasse12!!`
    a 3, which would otherwise pass), and zxcvbn knows the structural weakness
    a list cannot enumerate — sequences, repeats, keyboard walks, dates.
    """
    try:
        from zxcvbn import zxcvbn as _zxcvbn
    except Exception:
        return None
    try:
        return int(_zxcvbn(password)["score"])
    except Exception:
        return None


MIN_ZXCVBN_SCORE = 3


def validate_password(
    password: str,
    email: Optional[str] = None,
    user_name: Optional[str] = None,
    extra_terms: Optional[Iterable[str]] = None,
) -> List[str]:
    """Every rule the password breaks, as French messages naming the rule.

    An empty list means the password is acceptable. The password itself never
    appears in a message.
    """
    errors: List[str] = []

    if not isinstance(password, str) or not password:
        return ["Le mot de passe est obligatoire."]

    # --- Composition, checked first so the message is actionable ---
    if len(password) < MIN_LENGTH:
        errors.append(f"Le mot de passe doit contenir au moins {MIN_LENGTH} caractères.")

    if sum(1 for ch in password if ch.isupper()) < MIN_UPPERCASE:
        errors.append("Le mot de passe doit contenir au moins 1 majuscule.")

    digits = sum(1 for ch in password if ch.isdigit())
    if digits < MIN_DIGITS:
        errors.append(f"Le mot de passe doit contenir au moins {MIN_DIGITS} chiffres.")

    specials = sum(1 for ch in password if not ch.isalnum())
    if specials < MIN_SPECIALS:
        errors.append(
            f"Le mot de passe doit contenir au moins {MIN_SPECIALS} caractères spéciaux "
            f"({DISPLAYED_SPECIALS})."
        )

    # --- Identity terms: a password must not be the account it protects ---
    haystack = _strip_accents(password.lower())
    terms: List[str] = []
    if email:
        local_part = str(email).split("@")[0]
        if len(local_part) >= 3:
            terms.append(local_part)
    if user_name and len(str(user_name)) >= 3:
        terms.append(str(user_name))
    for term in (extra_terms or []):
        if term and len(str(term)) >= 3:
            terms.append(str(term))

    if any(_strip_accents(str(term).lower()) in haystack for term in terms):
        errors.append(
            "Le mot de passe ne doit pas contenir votre nom d'utilisateur ni votre adresse e-mail."
        )

    # --- Blocklist, deliberately AFTER composition ---
    if COMMON_PASSWORDS and (normalise_for_blocklist(password) & COMMON_PASSWORDS):
        errors.append(
            "Ce mot de passe est trop courant. Choisissez une combinaison moins prévisible."
        )
    else:
        score = _zxcvbn_score(password)
        if score is not None and score < MIN_ZXCVBN_SCORE:
            errors.append(
                "Ce mot de passe est trop facile à deviner. Choisissez une combinaison moins prévisible."
            )

    return errors


def assert_valid_password(
    password: str,
    email: Optional[str] = None,
    user_name: Optional[str] = None,
) -> None:
    """Raises HTTP 422 naming every rule that failed. Never echoes the value."""
    errors = validate_password(password, email=email, user_name=user_name)
    if errors:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail=" ".join(errors))

"""The password policy — the rules themselves, and the fact that the SERVER is
what enforces them.

The table below has one case per rule, and each rejection asserts that the
French message names the rule that failed: a form that answers "mot de passe
invalide" to every mistake is unusable, so a generic message would be a defect
even though the password was correctly refused.
"""
import io
import logging

import pytest

import password_policy
from tests.helpers import make_user

# A password satisfying all four composition rules and absent from the
# blocklist: 15 chars, 1 uppercase, 2 digits, 2 specials.
GOOD_PASSWORD = "Girafe!!12Nuage"


# --- The rules, one case each -------------------------------------------

@pytest.mark.parametrize(
    "password, expected_fragment",
    [
        # 11 characters — one short.
        ("Abcde12!!xy", "au moins 12 caractères"),
        # No uppercase.
        ("abcdefghij12!!", "au moins 1 majuscule"),
        # Exactly 1 digit.
        ("Abcdefghij1!!", "au moins 2 chiffres"),
        # Exactly 1 special character.
        ("Abcdefghij12!", "au moins 2 caractères spéciaux"),
    ],
)
def test_each_composition_rule_is_rejected_and_named(password, expected_fragment):
    errors = password_policy.validate_password(password)
    assert errors, f"{password!r} should have been rejected"
    assert any(expected_fragment in message for message in errors), (
        f"no message named the failing rule; got {errors}"
    )
    # The rejected value never appears in the explanation.
    assert all(password not in message for message in errors)


def test_a_compliant_password_is_accepted():
    assert password_policy.validate_password(GOOD_PASSWORD) == []


def test_the_brief_s_own_example_is_accepted():
    """`Bordeaux42!?` is what the registration screen shows as an example, so
    it must actually satisfy the policy it illustrates."""
    assert password_policy.validate_password("Bordeaux42!?") == []


def test_a_compliant_but_common_password_is_rejected():
    """`Motdepasse12!!` satisfies every composition rule: 14 characters, an
    uppercase M, two digits and two specials. It must still be refused, which
    is what proves the blocklist runs AFTER the composition rules rather than
    instead of them."""
    password = "Motdepasse12!!"
    # First: it really does pass every composition rule.
    assert len(password) >= password_policy.MIN_LENGTH
    assert sum(1 for c in password if c.isupper()) >= password_policy.MIN_UPPERCASE
    assert sum(1 for c in password if c.isdigit()) >= password_policy.MIN_DIGITS
    assert sum(1 for c in password if not c.isalnum()) >= password_policy.MIN_SPECIALS

    errors = password_policy.validate_password(password)
    assert errors, "a common password satisfying the composition rules was accepted"
    assert any("courant" in message or "deviner" in message for message in errors)


@pytest.mark.parametrize(
    "password",
    [
        "Motdepasse12!!",       # the literal
        "M0tD3P@sse20!!",       # leet-substituted
        "P@ssw0rd2024!!",       # English equivalent, leet + year
        "Azerty123456!!",       # keyboard walk
        "Soleil2024!!",         # common French word + year
    ],
)
def test_the_blocklist_sees_through_the_usual_disguises(password):
    """A blocklist of literals catches only literals. Users do not type the
    literal — they type it capitalised with a year and some punctuation, which
    is precisely the shape the composition rules push them towards."""
    assert password_policy.validate_password(password), f"{password!r} was accepted"


def test_a_password_containing_the_email_local_part_is_rejected():
    errors = password_policy.validate_password(
        "Alexandre99!!x", email="alexandre@differenciel.fr"
    )
    assert errors
    assert any("adresse e-mail" in message or "nom d'utilisateur" in message for message in errors)


def test_a_password_containing_the_account_name_is_rejected():
    errors = password_policy.validate_password("Dupont!!2024ab", user_name="dupont")
    assert errors
    assert any("nom d'utilisateur" in message for message in errors)


# --- The server is the authority ----------------------------------------

def test_the_policy_is_enforced_server_side_bypassing_the_frontend(client):
    """Posted straight at the API — no form, no JavaScript, no frontend
    validation anywhere in the path. The server must still refuse."""
    response = client.post("/users/register", json={
        "first_name": "Test", "last_name": "Direct", "email": "direct@example.com",
        "phone_number": "0600000000", "user_name": "direct", "password": "pw",
    })
    assert response.status_code == 422, response.text
    assert "12 caractères" in response.json()["detail"]


def test_a_compliant_registration_still_succeeds(client):
    response = client.post("/users/register", json={
        "first_name": "Test", "last_name": "Ok", "email": "ok@example.com",
        "phone_number": "0600000000", "user_name": "okuser", "password": GOOD_PASSWORD,
    })
    assert response.status_code == 200, response.text


def test_the_rejection_names_every_broken_rule_at_once(client):
    response = client.post("/users/register", json={
        "first_name": "Test", "last_name": "Multi", "email": "multi@example.com",
        "phone_number": "0600000000", "user_name": "multi", "password": "abcdefghijkl",
    })
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert "majuscule" in detail
    assert "chiffres" in detail
    assert "spéciaux" in detail


def test_a_rejected_password_appears_in_no_log_and_in_no_response(client, caplog):
    """The value must not come back in the body, and must not be written to a
    log — not even truncated or partially masked."""
    secret = "hunter2hunter2"
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    root = logging.getLogger()
    root.addHandler(handler)
    try:
        with caplog.at_level(logging.DEBUG):
            response = client.post("/users/register", json={
                "first_name": "Test", "last_name": "Quiet", "email": "quiet@example.com",
                "phone_number": "0600000000", "user_name": "quiet", "password": secret,
            })
    finally:
        root.removeHandler(handler)

    assert response.status_code == 422
    assert secret not in response.text
    assert secret not in stream.getvalue()
    assert secret not in caplog.text


def test_the_admin_endpoints_apply_the_same_policy(client, db_session):
    make_user(db_session, "root_admin", role="admin")
    from tests.helpers import auth_headers

    response = client.post("/admin/users/", headers=auth_headers("root_admin"), json={
        "first_name": "Weak", "last_name": "Account", "email": "weak@example.com",
        "phone_number": "0600000000", "user_name": "weak", "password": "pw", "page_credits": 5,
    })
    assert response.status_code == 422, response.text
    assert "12 caractères" in response.json()["detail"]


def test_changing_your_own_password_applies_the_policy(client, db_session):
    make_user(db_session, "changer")
    from tests.helpers import auth_headers

    weak = client.put("/users/me", headers=auth_headers("changer"), json={"password": "pw"})
    assert weak.status_code == 422
    assert "12 caractères" in weak.json()["detail"]

    strong = client.put("/users/me", headers=auth_headers("changer"), json={"password": GOOD_PASSWORD})
    assert strong.status_code == 200, strong.text


def test_an_unrelated_account_edit_does_not_require_a_password(client, db_session):
    """Regression: the account form sends the whole object with an empty
    password when the user edits their phone number. That must not be treated
    as a password change and refused."""
    make_user(db_session, "editor")
    from tests.helpers import auth_headers

    response = client.put(
        "/users/me", headers=auth_headers("editor"),
        json={"phone_number": "0700000000", "password": ""},
    )
    assert response.status_code == 200, response.text
    assert response.json()["phone_number"] == "0700000000"

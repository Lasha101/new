"""Spec tests of the French passport MRZ name parsing: line 1 of the MRZ is
'P<FRA' + SURNAME + '<<' + GIVEN<NAMES. The '<<' separates the surname from
the given names; single '<' separate the words inside each part. Every word
must land in its own column (a multi-word surname such as LE<FLOCH must never
leak into the given names, and vice versa)."""
import pytest

import ocr_service

LINE2 = "22IE632781FRA7602206F3211246<<<<<<<<<<<<<<08"


def passport_text(line1: str, line2: str = LINE2) -> str:
    return f"PASSEPORT\nRÉPUBLIQUE FRANÇAISE\n{line1}\n{line2}\n"


@pytest.mark.parametrize("line1, surname, given_names", [
    # single-word surname (the historical happy path, unchanged)
    ("P<FRABEAUCE<<VINCENT<CHARLES<OLIVIER<<<<<<<<<<<<", "BEAUCE", "VINCENT CHARLES OLIVIER"),
    ("P<FRACONNAN<<KARINE<<<<<<<<<<<<<<<<<<<<<<<<<<<<<", "CONNAN", "KARINE"),
    # multi-word surnames: every word before '<<' is the surname
    ("P<FRALE<FLOCH<<SANDRINE<<<<<<<<<<<<<<<<<<<<<<<<<", "LE FLOCH", "SANDRINE"),
    ("P<FRALE<BELLAC<<NATHALIE<<<<<<<<<<<<<<<<<<<<<<<<", "LE BELLAC", "NATHALIE"),
    ("P<FRADE<LA<TOUR<<MARIE<ANNE<<<<<<<<<<<<<<<<<<<<<", "DE LA TOUR", "MARIE ANNE"),
    ("P<FRADUPONT<LEVY<<ELODIE<<<<<<<<<<<<<<<<<<<<<<<<", "DUPONT LEVY", "ELODIE"),
    # no trailing fillers / line exactly filled
    ("P<FRALE<BELLAC<<NATHALIE", "LE BELLAC", "NATHALIE"),
    ("P<FRAPIETO<<SEVERINE<MARIE<FRANCE<BEATRICE<<<<<<", "PIETO", "SEVERINE MARIE FRANCE BEATRICE"),
])
def test_mrz_surname_and_given_names_split_on_double_chevron(line1, surname, given_names):
    data = ocr_service._parse_passport(passport_text(line1))
    assert data is not None
    assert data["last_name"] == surname
    assert data["first_name"] == given_names
    # the rest of the MRZ is still read
    assert data["passport_number"] == "22IE63278"
    assert data["birth_date"] == "1976-02-20"
    assert data["expiration_date"] == "2032-11-24"
    assert data["nationality"] == "Française"


def test_mrz_given_names_never_leak_into_surname_and_vice_versa():
    data = ocr_service._parse_passport(passport_text("P<FRALE<FLOCH<<SANDRINE<MARIE<<<<<<<<<<<<<<<<<<<"))
    assert (data["last_name"], data["first_name"]) == ("LE FLOCH", "SANDRINE MARIE")
    assert "SANDRINE" not in data["last_name"]
    assert "FLOCH" not in data["first_name"]


@pytest.mark.parametrize("line1", [
    "P<FRA LE<FLOCH << SANDRINE <<<<<<<<<<<<<<<<<<<<<<",      # Vision inserts spaces
    "P<FRALE<FLOCH<<<SANDRINE<<<<<<<<<<<<<<<<<<<<<<<<",       # an extra filler after '<<'
    "P<FRA<LE<FLOCH<<SANDRINE<<<<<<<<<<<<<<<<<<<<<<<<",       # a stray filler after the country code (accepted before the fix too)
    "P<FRA<<LE<FLOCH<<SANDRINE<<<<<<<<<<<<<<<<<<<<<<<",
])
def test_mrz_name_split_tolerates_ocr_noise(line1):
    data = ocr_service._parse_passport(passport_text(line1))
    assert (data["last_name"], data["first_name"]) == ("LE FLOCH", "SANDRINE")


def test_mrz_line1_regex_is_anchored_on_first_double_chevron():
    match = ocr_service.PASSPORT_MRZ_LINE1_RE.search("P<FRALE<FLOCH<<SANDRINE<<<<<<<<<<<<<<<<<<<<<<<<<")
    assert match.group(1) == "LE<FLOCH"
    assert match.group(2).strip("<") == "SANDRINE"


def test_visual_zone_fallback_unchanged_without_mrz_line1():
    """Without a readable MRZ line 1 the visual zone still provides the names
    (behaviour preserved)."""
    text = "PASSEPORT\nNom MARTIN\nPrénoms JEAN PIERRE\nNationalité Française\n" + LINE2 + "\n"
    data = ocr_service._parse_passport(text)
    assert data is not None
    assert data["last_name"] == "MARTIN"
    assert data["first_name"] == "JEAN PIERRE"

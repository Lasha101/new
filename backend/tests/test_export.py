"""Spec tests of the results-screen downloads (CSV and XLSX):
document type PASS/PI, filter-aware export, no internal ids, French headers in
the on-screen column order (Type between the document number and the
destination), DD/MM/YYYY dates, uppercase values, CSV UTF-8 BOM, XLSX
centering, auto-fitted widths and AutoFilter dropdowns on every column."""
import codecs
import csv
import io
import re
from datetime import date, datetime, timezone

import pytest
from openpyxl import load_workbook

import main
from tests.helpers import make_user, make_passport, auth_headers
import os

# Column order of the downloaded files = order of the on-screen table.
FRENCH_HEADERS = ["Nom de famille", "Prénom", "Date de Naissance", "Date d'Expiration", "Nationalité",
                  "Numéro de Passeport", "Type", "Destination", "Score de Confiance"]
# Named column indexes, so the assertions read like the table.
NOM, PRENOM, NAISSANCE, EXPIRATION, NATIONALITE, NUMERO, TYPE, DESTINATION, SCORE = range(9)
INTERNAL_COLUMNS = {"id", "owner_id", "ID", "OWNER_ID", "Identifiant", "Propriétaire"}


def read_csv(response):
    assert response.status_code == 200, response.text
    assert response.headers["content-type"].startswith("text/csv")
    body = response.content
    assert body.startswith(codecs.BOM_UTF8), "CSV must start with the UTF-8 BOM"
    text = body.decode("utf-8-sig")
    return list(csv.reader(io.StringIO(text), delimiter=main.CSV_DELIMITER))


def read_xlsx(response):
    assert response.status_code == 200, response.text
    assert response.headers["content-type"].startswith(main.XLSX_MEDIA_TYPE)
    workbook = load_workbook(io.BytesIO(response.content))
    return workbook["Passeports"]


def xlsx_rows(worksheet):
    return [list(row) for row in worksheet.iter_rows(values_only=True)]


def assert_uppercase(values):
    for value in values:
        if isinstance(value, str):
            assert value == value.upper(), f"value not uppercase: {value!r}"


# --- Document type derivation (PASS / PI) ---

@pytest.mark.parametrize("number, expected", [
    ("12AB34567", "PASS"),        # French passport: 2 digits + 2 letters + 5 digits
    (" 12ab34567 ", "PASS"),      # normalised (case / whitespace)
    ("123456789012", "PI"),       # old-format CNI: 12 digits
    ("X4RTBPFW4", "PI"),          # new-format CNI: 9 alphanumeric
    ("D2H6862M2", "PI"),
    ("", "PI"),
    (None, "PI"),
    ("\u0661\u0662AB\u0663\u0664\u0665\u0666\u0667", "PI"),   # Arabic-Indic digits: not ASCII, same verdict as the JS regex
    ("\uff11\uff12AB\uff13\uff14\uff15\uff16\uff17", "PI"),   # fullwidth digits
])
def test_document_type_of(number, expected):
    assert main.document_type_of(number) == expected


# --- CSV cell rules ---

@pytest.mark.parametrize("value, expected", [
    (None, ""),
    (date(1990, 5, 17), "17/05/1990"),                                   # DD/MM/YYYY
    (datetime(1990, 5, 17, 23, 0, tzinfo=timezone.utc), "17/05/1990"),
    (date(2030, 1, 2), "02/01/2030"),                                    # zero-padded day and month
    (date(999, 3, 4), "04/03/0999"),                                     # year always 4 digits
    (0.8734, "0.8734"),
    ("DUPONT", "DUPONT"),
    ("12AB34567", "12AB34567"),
    ("123456789012", '="123456789012"'),     # all-digit text stays text in Excel (no 1.23457E+11, no lost leading zero)
    ("040375901543", '="040375901543"'),
    ("'=HYPERLINK(1)", "'=HYPERLINK(1)"),    # already neutralised upstream, not doubled
    ("+1+1", "'+1+1"),                       # OWASP CSV-injection prefixes are neutralised
    ("-2+3", "'-2+3"),
    ("@SUM(1;1)", "'@SUM(1;1)"),
    ("\tX", "'\tX"),
    ("", ""),
])
def test_csv_cell(value, expected):
    assert main._csv_cell(value) == expected


@pytest.mark.parametrize("value, expected", [
    (None, 0), ("", 0), ("ABC", 3), (0.8734, 6), (date(1990, 5, 17), 10),
    (datetime(1990, 5, 17, 12, 0), 10), ("Score de Confiance", 18),
])
def test_displayed_length(value, expected):
    assert main._displayed_length(value) == expected


def test_filter_by_document_type():
    rows = [{"passport_number": "12AB34567"}, {"passport_number": "123456789012"}]
    assert main._filter_by_document_type(rows, None) == rows
    assert main._filter_by_document_type(rows, "") == rows
    assert main._filter_by_document_type(rows, "PASS") == [rows[0]]
    assert main._filter_by_document_type(rows, "PP") == []               # the former code is no longer a type
    assert main._filter_by_document_type(rows, "PI") == [rows[1]]


# --- CSV download ---

def test_csv_export_all_rows_french_headers_uppercase_no_ids(client, user_with_documents):
    response = client.get("/export/data?format=csv", headers=user_with_documents["headers"])
    assert response.headers["content-disposition"] == "attachment; filename=passeports_pour_alice.csv"
    rows = read_csv(response)

    assert rows[0] == FRENCH_HEADERS
    assert not INTERNAL_COLUMNS & set(rows[0])
    data_rows = rows[1:]
    assert len(data_rows) == 4                       # only alice's documents (all types)
    for row in data_rows:
        assert len(row) == len(FRENCH_HEADERS)
        assert_uppercase(row)
    by_number = {row[NUMERO]: row for row in data_rows}
    assert by_number["12AB34567"][TYPE] == "PASS"
    assert by_number["98ZY12345"][TYPE] == "PASS"
    assert by_number['="123456789012"'][TYPE] == "PI"    # 12-digit CNI number kept as text for Excel
    assert by_number["X4RTBPFW4"][TYPE] == "PI"
    # accents survive the round trip and are uppercased; surname first, then given names
    assert by_number["12AB34567"][NOM:PRENOM + 1] == ["DUPONT-LÉVY", "ÉLODIE"]
    assert by_number["12AB34567"][NATIONALITE] == "FRANÇAISE"
    assert by_number["12AB34567"][DESTINATION] == "DUBROVNIK ÉTÉ"
    # dates are written jour/mois/année with '/'
    assert by_number["12AB34567"][NAISSANCE:EXPIRATION + 1] == ["17/05/1990", "02/01/2030"]
    assert by_number["12AB34567"][SCORE] == "0.8734"
    # empty values stay empty (never 'None')
    assert by_number["X4RTBPFW4"][DESTINATION] == ""
    assert by_number['="123456789012"'][SCORE] == ""
    # no ISO date anywhere in the file
    for row in data_rows:
        assert not any(re.match(r"^\d{4}-\d{2}-\d{2}$", cell) for cell in row)
    # ids never appear anywhere in the file
    text = response.content.decode("utf-8-sig")
    for doc in user_with_documents["docs"].values():
        assert doc["id"] not in text
    assert user_with_documents["user"]["id"] not in text


def test_csv_bom_and_encoding_bytes(client, user_with_documents):
    response = client.get("/export/data?format=csv", headers=user_with_documents["headers"])
    assert response.content[:3] == b"\xef\xbb\xbf"
    assert "Prénom".encode("utf-8") in response.content
    assert "FRANÇAISE".encode("utf-8") in response.content
    # CRLF line endings, no bare LF outside quoted fields
    assert response.content.endswith(b"\r\n")
    assert response.content.count(b"\r\n") == 5
    assert response.content.replace(b"\r\n", b"").count(b"\n") == 0


def test_csv_quoting_round_trip(client, db_session):
    user = make_user(db_session, "frank")
    tricky = 'Rome ; Milan "JJ"\nligne 2'
    make_passport(db_session, user["id"], destination=tricky, first_name="=cmd", last_name="+plus")
    response = client.get("/export/data?format=csv", headers=auth_headers("frank"))
    rows = read_csv(response)
    assert len(rows) == 2
    row = rows[1]
    assert row[DESTINATION] == tricky.upper()       # ';', '"' and newline survive the CSV round trip
    assert row[PRENOM] == "'=CMD" and row[NOM] == "'+PLUS"  # formula-like text neutralised
    assert b'"ROME ; MILAN ""JJ""' in response.content


@pytest.mark.parametrize("document_type, expected_numbers", [
    ("PASS", {"12AB34567", "98ZY12345"}),
    ("PI", {'="123456789012"', "X4RTBPFW4"}),
])
def test_csv_export_respects_type_filter(client, user_with_documents, document_type, expected_numbers):
    response = client.get(f"/export/data?format=csv&document_type={document_type}", headers=user_with_documents["headers"])
    rows = read_csv(response)
    assert rows[0] == FRENCH_HEADERS
    assert {row[NUMERO] for row in rows[1:]} == expected_numbers
    assert {row[TYPE] for row in rows[1:]} == {document_type}


def test_export_invalid_type_filter_is_rejected(client, user_with_documents):
    response = client.get("/export/data?document_type=XX", headers=user_with_documents["headers"])
    assert response.status_code == 422
    response = client.get("/export/data?document_type=PP", headers=user_with_documents["headers"])   # former code
    assert response.status_code == 422
    response = client.get("/export/data?format=pdf", headers=user_with_documents["headers"])
    assert response.status_code == 422


def test_export_type_filter_with_no_match_is_404(client, db_session, user_with_documents):
    lonely = make_user(db_session, "carol")
    make_passport(db_session, lonely["id"], passport_number="12AB34567")
    response = client.get("/export/data?format=csv&document_type=PI", headers=auth_headers("carol"))
    assert response.status_code == 404
    assert response.json()["detail"] == "Aucune donnée de passeport trouvée pour les critères donnés"


def test_csv_export_combines_type_filter_with_destination_filter(client, user_with_documents):
    response = client.get("/export/data?format=csv&destination=Rome&document_type=PASS", headers=user_with_documents["headers"])
    rows = read_csv(response)
    assert [row[NUMERO] for row in rows[1:]] == ["98ZY12345"]


# --- XLSX download ---

def test_xlsx_export_headers_type_column_uppercase_no_ids(client, user_with_documents):
    response = client.get("/export/data", headers=user_with_documents["headers"])   # xlsx is the default
    assert response.headers["content-disposition"] == "attachment; filename=passeports_pour_alice.xlsx"
    ws = read_xlsx(response)
    rows = xlsx_rows(ws)

    assert rows[0] == FRENCH_HEADERS
    assert not INTERNAL_COLUMNS & set(rows[0])
    data_rows = rows[1:]
    assert len(data_rows) == 4
    for row in data_rows:
        assert_uppercase(row)
    by_number = {row[NUMERO]: row for row in data_rows}
    assert by_number["12AB34567"][TYPE] == "PASS"
    assert by_number["123456789012"][TYPE] == "PI"
    assert by_number["X4RTBPFW4"][TYPE] == "PI"
    assert by_number["12AB34567"][NOM:PRENOM + 1] == ["DUPONT-LÉVY", "ÉLODIE"]
    assert by_number["12AB34567"][NATIONALITE] == "FRANÇAISE"
    # dates stay real Excel dates (sortable, filterable), the confidence score a real number
    assert isinstance(by_number["12AB34567"][NAISSANCE], (date, datetime))
    assert by_number["12AB34567"][NAISSANCE].strftime("%Y-%m-%d") == "1990-05-17"
    assert by_number["12AB34567"][EXPIRATION].strftime("%Y-%m-%d") == "2030-01-02"
    assert by_number["12AB34567"][SCORE] == pytest.approx(0.8734)
    assert by_number["X4RTBPFW4"][DESTINATION] is None
    all_values = {str(v) for row in rows for v in row}
    for doc in user_with_documents["docs"].values():
        assert doc["id"] not in all_values


def test_xlsx_dates_displayed_as_dd_mm_yyyy(client, user_with_documents):
    """Every date cell carries the jour/mois/année number format, so a reader
    shows 17/05/1990 (never 1990-05-17) while keeping a real date value.

    The exact casing is asserted on purpose: 'DD'/'YYYY' mean day-of-year and
    week-numbering year in the Unicode/ICU date grammar that iOS uses to preview
    an .xlsx, which showed 5 July 1983 as '186/07/1983' on an iPhone. Only
    'dd/MM/yyyy' reads as day/month/year in both that grammar and Excel's."""
    ws = read_xlsx(client.get("/export/data", headers=user_with_documents["headers"]))
    header = [cell.value for cell in ws[1]]
    date_columns = [header.index("Date de Naissance") + 1, header.index("Date d'Expiration") + 1]
    for row in ws.iter_rows(min_row=2):
        for column in date_columns:
            cell = row[column - 1]
            assert isinstance(cell.value, (date, datetime)), cell.coordinate
            assert cell.number_format == "dd/MM/yyyy", f"{cell.coordinate}: {cell.number_format}"
            assert cell.is_date
    # and no other cell is formatted as a date
    for row in ws.iter_rows(min_row=2):
        for index, cell in enumerate(row, start=1):
            if index not in date_columns:
                assert not cell.is_date, cell.coordinate


def test_xlsx_has_autofilter_dropdowns_on_every_column(client, user_with_documents):
    """The downloaded workbook is 'dynamic': an Excel AutoFilter covers the
    header row and every data row, so each column header gets the dropdown
    (sort / filter) as soon as the file is opened."""
    ws = read_xlsx(client.get("/export/data", headers=user_with_documents["headers"]))
    assert ws.auto_filter.ref == f"A1:I{ws.max_row}"
    assert ws.max_row == 5                                       # header + 4 documents
    assert ws.max_column == len(FRENCH_HEADERS) == 9
    # the selection export is built by the same code path
    docs = user_with_documents["docs"]
    selection = client.post("/export/data/selection", json={"passport_ids": [docs["pp1"]["id"], docs["pi_new"]["id"]]},
                            headers=user_with_documents["headers"])
    ws_selection = read_xlsx(selection)
    assert ws_selection.auto_filter.ref == "A1:I3"
    # the raw XML really contains the autoFilter element (what Excel reads)
    import zipfile
    with zipfile.ZipFile(io.BytesIO(selection.content)) as archive:
        sheet_xml = archive.read("xl/worksheets/sheet1.xml").decode("utf-8")
    assert '<autoFilter ref="A1:I3"' in sheet_xml


def test_xlsx_every_cell_is_centered(client, user_with_documents):
    ws = read_xlsx(client.get("/export/data", headers=user_with_documents["headers"]))
    cells = [cell for row in ws.iter_rows() for cell in row]
    assert cells, "worksheet has cells"
    for cell in cells:
        assert cell.alignment.horizontal == "center", f"{cell.coordinate} not centered horizontally"
        assert cell.alignment.vertical == "center", f"{cell.coordinate} not centered vertically"


def test_xlsx_column_widths_fit_longest_value(client, user_with_documents):
    ws = read_xlsx(client.get("/export/data", headers=user_with_documents["headers"]))
    widths = {letter: dim.width for letter, dim in ws.column_dimensions.items() if not dim.hidden}
    # Independent oracle: the longest displayed text of every column of the fixture.
    longest_expected = {
        "A": len("Nom de famille"), "B": len("ÉLODIE"), "C": len("Date de Naissance"), "D": len("Date d'Expiration"),
        "E": len("Nationalité"), "F": len("Numéro de Passeport"), "G": len("Type"),
        "H": len("Destination"), "I": len("Score de Confiance"),
    }
    assert set(widths) == set(longest_expected)
    for letter, longest in longest_expected.items():
        assert widths[letter] > longest + 1, f"column {letter} width {widths[letter]} does not fit {longest} chars"
    # widths are per column: a column with a longer value is wider than a shorter one
    assert widths["F"] > widths["G"]
    # every column has an explicit (custom) width
    for column_cells in ws.columns:
        assert ws.column_dimensions[column_cells[0].column_letter].width is not None


def test_xlsx_unused_grid_columns_hidden(client, user_with_documents):
    """The sheet ends visually at the last data column: every grid column
    after 'Score de Confiance' is hidden (one J..XFD range)."""
    ws = read_xlsx(client.get("/export/data", headers=user_with_documents["headers"]))
    trailing = ws.column_dimensions["J"]
    assert trailing.hidden is True
    assert (trailing.min, trailing.max) == (10, 16384)          # J .. XFD, Excel's last column
    for letter in "ABCDEFGHI":                                   # data columns stay visible
        assert not ws.column_dimensions[letter].hidden


def test_xlsx_widths_grow_with_long_values(client, db_session):
    user = make_user(db_session, "dave")
    long_destination = "Voyage " + "très long " * 8
    make_passport(db_session, user["id"], destination=long_destination)
    ws = read_xlsx(client.get("/export/data", headers=auth_headers("dave")))
    assert ws.column_dimensions["H"].width > len(long_destination)


@pytest.mark.parametrize("document_type, expected_numbers", [
    ("PASS", {"12AB34567", "98ZY12345"}),
    ("PI", {"123456789012", "X4RTBPFW4"}),
])
def test_xlsx_export_respects_type_filter(client, user_with_documents, document_type, expected_numbers):
    ws = read_xlsx(client.get(f"/export/data?document_type={document_type}", headers=user_with_documents["headers"]))
    rows = xlsx_rows(ws)
    assert rows[0] == FRENCH_HEADERS
    assert {row[NUMERO] for row in rows[1:]} == expected_numbers
    assert {row[TYPE] for row in rows[1:]} == {document_type}
    assert ws.auto_filter.ref == f"A1:I{len(rows)}"


def test_xlsx_formula_injection_guard_kept(client, db_session):
    user = make_user(db_session, "erin")
    make_passport(db_session, user["id"], destination="=HYPERLINK(\"http://evil\")")
    ws = read_xlsx(client.get("/export/data", headers=auth_headers("erin")))
    cell = ws["H2"]
    assert cell.data_type != "f"
    assert str(cell.value).startswith("'=")


# --- Headers match the on-screen table (frontend columnTranslations) ---

def test_export_headers_match_frontend_column_translations():
    app_jsx = os.path.join(os.path.dirname(main.__file__), "..", "frontend", "src", "App.jsx")
    if not os.path.exists(app_jsx):
        pytest.skip("frontend sources not available next to the backend")
    source = open(app_jsx, encoding="utf-8").read()
    block = re.search(r"const columnTranslations = \{(.*?)\};", source, re.S).group(1)
    translations = dict(re.findall(r"""^\s*([a-z_]+):\s*(?:'([^']*)'|"([^"]*)")""", block, re.M) and
                        [(m.group(1), m.group(2) if m.group(2) is not None else m.group(3))
                         for m in re.finditer(r"""^\s*([a-z_]+):\s*(?:'([^']*)'|"([^"]*)")""", block, re.M)])
    for column, header in main.EXPORT_HEADERS.items():
        assert translations.get(column) == header, f"{column}: backend '{header}' vs frontend '{translations.get(column)}'"
    assert [main.EXPORT_HEADERS[c] for c in main.EXPORT_COLUMNS] == FRENCH_HEADERS


def test_export_column_order_and_type_codes_match_frontend():
    """The downloaded files use the column order of the on-screen table
    (PASSPORT_COLUMN_ORDER) and the same type codes (PASS / PI)."""
    helpers_js = os.path.join(os.path.dirname(main.__file__), "..", "frontend", "src", "resultsHelpers.js")
    if not os.path.exists(helpers_js):
        pytest.skip("frontend sources not available next to the backend")
    source = open(helpers_js, encoding="utf-8").read()
    order_block = re.search(r"export const PASSPORT_COLUMN_ORDER = \[(.*?)\];", source, re.S).group(1)
    assert re.findall(r"'([a-z_]+)'", order_block) == main.EXPORT_COLUMNS
    assert re.search(r"export const DOC_TYPE_PASSPORT = '([A-Z]+)'", source).group(1) == main.DOC_TYPE_PASSPORT == "PASS"
    assert re.search(r"export const DOC_TYPE_ID_CARD = '([A-Z]+)'", source).group(1) == main.DOC_TYPE_ID_CARD == "PI"
    # Type sits between the document number and the destination, surname comes first
    assert main.EXPORT_COLUMNS.index("document_type") == main.EXPORT_COLUMNS.index("passport_number") + 1
    assert main.EXPORT_COLUMNS.index("destination") == main.EXPORT_COLUMNS.index("document_type") + 1
    assert main.EXPORT_COLUMNS[:2] == ["last_name", "first_name"]


def test_export_returns_all_rows_beyond_listing_page(client, db_session):
    """'Across all pages': the admin listing is capped at 100 rows, the export is not."""
    make_user(db_session, "root", role="admin")
    owner = make_user(db_session, "many")
    for i in range(120):
        make_passport(db_session, owner["id"], passport_number=f"{i % 100:02d}AB{i:05d}" if i % 2 == 0 else f"{i:012d}",
                      destination=f"D{i}")
    listed = client.get("/passports/", headers=auth_headers("root")).json()
    assert len(listed) == 100                                    # pre-existing listing cap
    rows = read_csv(client.get("/export/data?format=csv", headers=auth_headers("root")))
    assert len(rows) - 1 == 120
    pp = read_csv(client.get("/export/data?format=csv&document_type=PASS", headers=auth_headers("root")))
    pi = read_csv(client.get("/export/data?format=csv&document_type=PI", headers=auth_headers("root")))
    assert len(pp) - 1 == 60 and len(pi) - 1 == 60


# --- Preview (Aperçu) mirrors the export ---

def test_preview_rows_match_export_columns_and_type_filter(client, user_with_documents):
    response = client.get("/export/data?preview=true", headers=user_with_documents["headers"])
    assert response.status_code == 200
    rows = response.json()
    assert len(rows) == 4
    assert list(rows[0].keys()) == main.EXPORT_COLUMNS
    assert "id" not in rows[0] and "owner_id" not in rows[0]
    for row in rows:
        assert row["document_type"] in ("PASS", "PI")
        assert_uppercase(row.values())
    # date and empty values are JSON friendly; dates are shown as DD/MM/YYYY like in the files
    by_number = {row["passport_number"]: row for row in rows}
    assert by_number["12AB34567"]["birth_date"] == "17/05/1990"
    assert by_number["12AB34567"]["expiration_date"] == "02/01/2030"
    assert by_number["12AB34567"]["document_type"] == "PASS"
    assert by_number["X4RTBPFW4"]["destination"] == ""

    filtered = client.get("/export/data?preview=true&document_type=PI", headers=user_with_documents["headers"]).json()
    assert {row["passport_number"] for row in filtered} == {"123456789012", "X4RTBPFW4"}


# --- Selection export (Exporter Sélection) ---

def test_selection_export_xlsx_and_csv_same_format(client, user_with_documents):
    docs = user_with_documents["docs"]
    ids = [docs["pp1"]["id"], docs["pi_old"]["id"], docs["other_pp"]["id"]]   # other_pp is not alice's

    xlsx = client.post("/export/data/selection", json={"passport_ids": ids}, headers=user_with_documents["headers"])
    assert xlsx.headers["content-disposition"] == "attachment; filename=selection_passeports.xlsx"
    ws = read_xlsx(xlsx)
    rows = xlsx_rows(ws)
    assert rows[0] == FRENCH_HEADERS
    assert {row[NUMERO] for row in rows[1:]} == {"12AB34567", "123456789012"}   # bob's row excluded
    assert {row[TYPE] for row in rows[1:]} == {"PASS", "PI"}
    for cell in (c for row in ws.iter_rows() for c in row):
        assert cell.alignment.horizontal == "center"

    csv_response = client.post("/export/data/selection?format=csv", json={"passport_ids": ids}, headers=user_with_documents["headers"])
    assert csv_response.headers["content-disposition"] == "attachment; filename=selection_passeports.csv"
    csv_rows = read_csv(csv_response)
    assert csv_rows[0] == FRENCH_HEADERS
    assert {row[NUMERO] for row in csv_rows[1:]} == {"12AB34567", '="123456789012"'}
    for row in csv_rows[1:]:
        assert_uppercase(row)


def test_selection_export_errors_unchanged(client, user_with_documents):
    empty = client.post("/export/data/selection", json={"passport_ids": []}, headers=user_with_documents["headers"])
    assert empty.status_code == 400
    assert empty.json()["detail"] == "Aucun passeport sélectionné."
    foreign = client.post("/export/data/selection", json={"passport_ids": [user_with_documents["docs"]["other_pp"]["id"]]},
                          headers=user_with_documents["headers"])
    assert foreign.status_code == 404


# --- Admin scope of the export is unchanged ---

def test_admin_export_all_users_and_per_user(client, db_session, user_with_documents):
    make_user(db_session, "root", role="admin")
    all_rows = read_csv(client.get("/export/data?format=csv", headers=auth_headers("root")))
    assert len(all_rows) - 1 == 5
    assert client.get("/export/data", headers=auth_headers("root")).headers["content-disposition"] == "attachment; filename=passeports_rapport_complet.xlsx"

    bob_id = user_with_documents["other"]["id"]
    bob_rows = read_csv(client.get(f"/export/data?format=csv&user_id={bob_id}", headers=auth_headers("root")))
    assert [row[NUMERO] for row in bob_rows[1:]] == ["11CD22222"]
    response = client.get(f"/export/data?user_id={bob_id}", headers=auth_headers("root"))
    assert response.headers["content-disposition"] == "attachment; filename=passeports_pour_bob.xlsx"


def test_export_requires_authentication(client, user_with_documents):
    assert client.get("/export/data").status_code == 401
    assert client.get("/export/data?format=csv").status_code == 401
    assert client.post("/export/data/selection", json={"passport_ids": ["x"]}).status_code == 401

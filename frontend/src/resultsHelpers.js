// Pure helpers of the results screen (no React, no DOM) so they can be unit
// tested with `node --test`.

// Document type of a row: PP = passeport, PI = pièce d'identité (CNI).
// The database has no document-type column, so the type is derived from the
// document number: a French passport number is always 2 digits + 2 letters +
// 5 digits, while a CNI number is 12 digits (old format) or 9 alphanumeric
// characters (new format). Mirrors document_type_of() in backend/main.py.
export const DOC_TYPE_PASSPORT = 'PP';
export const DOC_TYPE_ID_CARD = 'PI';
const PASSPORT_NUMBER_RE = /^\d{2}[A-Z]{2}\d{5}$/;

// Options of the type filter; '' means no filter ("Tous").
export const DOC_TYPE_FILTER_OPTIONS = [
    { value: '', label: 'Tous' },
    { value: DOC_TYPE_PASSPORT, label: DOC_TYPE_PASSPORT },
    { value: DOC_TYPE_ID_CARD, label: DOC_TYPE_ID_CARD },
];

// Columns of the passports screen, in order, shared by the results table, the
// export preview and the downloaded CSV/XLSX files (mirrors EXPORT_COLUMNS in
// backend/main.py): the derived Type column sits between the document number
// and the destination.
export const PASSPORT_COLUMN_ORDER = [
    'last_name', 'first_name', 'birth_date', 'expiration_date', 'nationality',
    'passport_number', 'document_type', 'destination', 'confidence_score',
];

// Date shown to the user: DD/MM/YYYY (jour/mois/année). Accepts the API's
// ISO values ('1990-05-17' or '1990-05-17T00:00:00'); anything else (empty,
// already formatted, free text) is returned untouched. Pure string work, so
// the displayed day never shifts with the browser's time zone.
export function formatDateFR(value) {
    if (value == null || value === '') return '';
    const match = String(value).match(/^(\d{4})-(\d{2})-(\d{2})(?:$|T)/);
    if (!match) return String(value);
    return `${match[3]}/${match[2]}/${match[1]}`;
}

export function getDocumentType(item) {
    const number = String(item?.passport_number ?? '').trim().toUpperCase();
    return PASSPORT_NUMBER_RE.test(number) ? DOC_TYPE_PASSPORT : DOC_TYPE_ID_CARD;
}

// Rows displayed for a given type filter ('' / undefined = all rows).
export function filterByDocumentType(items, docTypeFilter) {
    if (!docTypeFilter) return items;
    return items.filter(item => getDocumentType(item) === docTypeFilter);
}

// The value one results column shows for one row, as a string. The results
// table and the mobile card list both render from this single function, so the
// two views cannot drift: the derived Type column, the confidence percentage and
// the DD/MM/YYYY date formatting are decided here once.
//
// `fieldTypes` is the endpoint's field map (passportFields in App.jsx); a field
// declared 'date' there is formatted, everything else is passed through.
export function resultCellValue(item, field, fieldTypes = {}) {
    let value = field === 'document_type' ? getDocumentType(item) : item?.[field];
    if (field === 'confidence_score' && typeof value === 'number') {
        value = `${(value * 100).toFixed(0)}%`;
    }
    if (fieldTypes[field] === 'date') { value = formatDateFR(value); }
    // Missing values render as an empty cell, never as the text "null".
    return value == null ? '' : String(value);
}

// A row whose OCR confidence is below 80 % is highlighted in the results so the
// user checks it (action list item 9). A row without a score is not.
export const LOW_CONFIDENCE_THRESHOLD = 0.8;
export const LOW_CONFIDENCE_TITLE = 'Score de confiance inférieur à 80 % : vérifiez ce document.';

export function isLowConfidence(item) {
    const score = item?.confidence_score;
    return typeof score === 'number' && Number.isFinite(score) && score < LOW_CONFIDENCE_THRESHOLD;
}

// Query string of GET /export/data, so that the file contains exactly the rows
// on screen: the export panel filters (user_id only for admins), the results
// table's own filters (user_filter -> user_id, voyage_filter/destination_filter
// -> destination; a table filter wins over the panel filter of the same kind
// because the table is what the user sees), the active type filter, the
// requested format and the preview flag.
export function buildExportQuery({ exportFilters = {}, tableFilters = {}, role, docTypeFilter = '', format = 'xlsx', preview = false }) {
    const params = Object.fromEntries(Object.entries(exportFilters).filter(([, v]) => v));
    if (tableFilters.user_filter) { params.user_id = tableFilters.user_filter; }
    const tableDestination = tableFilters.voyage_filter || tableFilters.destination_filter;
    if (tableDestination) { params.destination = tableDestination; }
    if (role !== 'admin') { delete params.user_id; }
    if (docTypeFilter) { params.document_type = docTypeFilter; }
    params.format = format;
    if (preview) { params.preview = 'true'; }
    return new URLSearchParams(params).toString();
}

// Download file name announced by the server (Content-Disposition, sent
// unquoted by the backend), with a format-aware fallback.
export function downloadFilename(contentDisposition, fallbackStem, format) {
    return contentDisposition?.match(/filename="?(.+?)"?$/)?.[1] || `${fallbackStem}.${format}`;
}

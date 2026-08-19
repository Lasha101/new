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

export function getDocumentType(item) {
    const number = String(item?.passport_number ?? '').trim().toUpperCase();
    return PASSPORT_NUMBER_RE.test(number) ? DOC_TYPE_PASSPORT : DOC_TYPE_ID_CARD;
}

// Rows displayed for a given type filter ('' / undefined = all rows).
export function filterByDocumentType(items, docTypeFilter) {
    if (!docTypeFilter) return items;
    return items.filter(item => getDocumentType(item) === docTypeFilter);
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

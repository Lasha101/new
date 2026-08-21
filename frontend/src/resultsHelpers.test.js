// Unit tests of the results-screen helpers (run with `npm test` / `node --test`).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
    getDocumentType, filterByDocumentType, buildExportQuery, downloadFilename, formatDateFR,
    DOC_TYPE_FILTER_OPTIONS, DOC_TYPE_PASSPORT, DOC_TYPE_ID_CARD, PASSPORT_COLUMN_ORDER,
} from './resultsHelpers.js';

const passport = { id: 'p1', passport_number: '12AB34567', first_name: 'A' };
const oldCni = { id: 'c1', passport_number: '123456789012', first_name: 'B' };
const newCni = { id: 'c2', passport_number: 'X4RTBPFW4', first_name: 'C' };
const rows = [passport, oldCni, newCni];

test('document type: French passport number shape is PASS, everything else is PI', () => {
    assert.equal(getDocumentType(passport), 'PASS');
    assert.equal(getDocumentType(oldCni), 'PI');          // old CNI: 12 digits
    assert.equal(getDocumentType(newCni), 'PI');          // new CNI: 9 alphanumeric
    assert.equal(getDocumentType({ passport_number: 'D2H6862M2' }), 'PI');
    assert.equal(getDocumentType({ passport_number: ' 12ab34567 ' }), 'PASS'); // normalised
    assert.equal(getDocumentType({ passport_number: '' }), 'PI');
    assert.equal(getDocumentType({}), 'PI');
    assert.equal(getDocumentType(null), 'PI');
    assert.equal(DOC_TYPE_PASSPORT, 'PASS');              // never the former 'PP'
    assert.equal(DOC_TYPE_ID_CARD, 'PI');
});

test('filter options are Tous (default, no filter) / PASS / PI, in French', () => {
    assert.deepEqual(DOC_TYPE_FILTER_OPTIONS.map(o => o.label), ['Tous', 'PASS', 'PI']);
    assert.deepEqual(DOC_TYPE_FILTER_OPTIONS.map(o => o.value), ['', 'PASS', 'PI']);
});

test('PASS/PI filter controls which rows are displayed', () => {
    assert.deepEqual(filterByDocumentType(rows, ''), rows);          // Tous
    assert.deepEqual(filterByDocumentType(rows, undefined), rows);
    assert.deepEqual(filterByDocumentType(rows, 'PASS'), [passport]);
    assert.deepEqual(filterByDocumentType(rows, 'PI'), [oldCni, newCni]);
    assert.deepEqual(filterByDocumentType(rows, 'PP'), []);          // the former code matches nothing
    assert.deepEqual(filterByDocumentType([], 'PASS'), []);
});

test('column order: surname, given names, dates, nationality, number, Type, destination, score', () => {
    assert.deepEqual(PASSPORT_COLUMN_ORDER, [
        'last_name', 'first_name', 'birth_date', 'expiration_date', 'nationality',
        'passport_number', 'document_type', 'destination', 'confidence_score',
    ]);
    // Type sits between the document number and the destination
    assert.equal(PASSPORT_COLUMN_ORDER.indexOf('document_type'), PASSPORT_COLUMN_ORDER.indexOf('passport_number') + 1);
    assert.equal(PASSPORT_COLUMN_ORDER.indexOf('destination'), PASSPORT_COLUMN_ORDER.indexOf('document_type') + 1);
    // Destination is a column of the table too, right after Type
    assert.equal(PASSPORT_COLUMN_ORDER.indexOf('destination'), PASSPORT_COLUMN_ORDER.indexOf('confidence_score') - 1);
    assert.equal(PASSPORT_COLUMN_ORDER.length, 9);
});

test('dates are displayed as DD/MM/YYYY (jour/mois/année)', () => {
    assert.equal(formatDateFR('1990-05-17'), '17/05/1990');
    assert.equal(formatDateFR('2030-01-02'), '02/01/2030');             // zero-padded
    assert.equal(formatDateFR('1973-05-31T00:00:00'), '31/05/1973');    // ISO datetime from the API
    assert.equal(formatDateFR('2032-04-25T23:30:00+02:00'), '25/04/2032'); // no time-zone shift
    assert.equal(formatDateFR(null), '');
    assert.equal(formatDateFR(undefined), '');
    assert.equal(formatDateFR(''), '');
    assert.equal(formatDateFR('31/05/1973'), '31/05/1973');            // already formatted: untouched
    assert.equal(formatDateFR('N/A'), 'N/A');                          // free text: untouched
});

test('export query is filter-aware: type filter, format, preview, panel filters', () => {
    const q = (opts) => Object.fromEntries(new URLSearchParams(buildExportQuery(opts)));
    // No filter: all rows, xlsx by default, no document_type parameter at all.
    assert.deepEqual(q({ role: 'user' }), { format: 'xlsx' });
    // Active type filter is forwarded so the file contains exactly the rows on screen.
    assert.deepEqual(q({ role: 'user', docTypeFilter: 'PI', format: 'csv' }), { document_type: 'PI', format: 'csv' });
    assert.deepEqual(q({ role: 'user', docTypeFilter: DOC_TYPE_PASSPORT }), { document_type: 'PASS', format: 'xlsx' });
    // Preview flag and export panel filters are preserved.
    assert.deepEqual(q({ role: 'admin', exportFilters: { user_id: 'u1', destination: 'Rome' }, docTypeFilter: 'PASS', preview: true }),
        { user_id: 'u1', destination: 'Rome', document_type: 'PASS', format: 'xlsx', preview: 'true' });
    // Non-admins never send user_id; empty panel filters are dropped.
    assert.deepEqual(q({ role: 'user', exportFilters: { user_id: 'u1', destination: '' } }), { format: 'xlsx' });
    // The results table's own filters narrow the download too (what is on screen is exported)...
    assert.deepEqual(q({ role: 'user', tableFilters: { destination_filter: 'Oslo' }, format: 'csv' }), { destination: 'Oslo', format: 'csv' });
    assert.deepEqual(q({ role: 'admin', tableFilters: { user_filter: 'u9', voyage_filter: 'Rome' } }), { user_id: 'u9', destination: 'Rome', format: 'xlsx' });
    // ...and take precedence over the export panel filter of the same kind, while the panel filter still applies when the table filter is empty.
    assert.deepEqual(q({ role: 'admin', exportFilters: { user_id: 'u1', destination: 'Rome' }, tableFilters: { user_filter: '', voyage_filter: 'Oslo' } }), { user_id: 'u1', destination: 'Oslo', format: 'xlsx' });
    assert.deepEqual(q({ role: 'admin', exportFilters: { destination: 'Rome' }, tableFilters: { user_filter: 'u9', voyage_filter: '' } }), { user_id: 'u9', destination: 'Rome', format: 'xlsx' });
    // a non-admin's table user filter can never widen the scope
    assert.deepEqual(q({ role: 'user', tableFilters: { user_filter: 'u9' } }), { format: 'xlsx' });
});

test('download filename comes from Content-Disposition, with a format-aware fallback', () => {
    assert.equal(downloadFilename('attachment; filename=passeports_pour_bob.csv', 'x', 'csv'), 'passeports_pour_bob.csv');
    assert.equal(downloadFilename('attachment; filename="selection_passeports.xlsx"', 'x', 'xlsx'), 'selection_passeports.xlsx');
    assert.equal(downloadFilename(null, 'selection_passeports', 'csv'), 'selection_passeports.csv');
    assert.equal(downloadFilename(undefined, 'passports_export', 'xlsx'), 'passports_export.xlsx');
    // the backend sends the (destination-derived) name unquoted; ';' or '"' inside it must not truncate the extension away
    assert.equal(downloadFilename('attachment; filename=passeports_rome_;_milan_pour_x.csv', 'x', 'csv'), 'passeports_rome_;_milan_pour_x.csv');
    assert.equal(downloadFilename('attachment; filename=passeports_a"b_pour_x.xlsx', 'x', 'xlsx'), 'passeports_a"b_pour_x.xlsx');
});

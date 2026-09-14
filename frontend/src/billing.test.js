import { test } from 'node:test';
import assert from 'node:assert/strict';
import { PACKS, packSummary, formatEuros, formatCount, normalizeSiret, isValidSiret, normalizeVat, isValidVat } from './billing.js';

test('the four packs and their HT prices match the Stripe sheet', () => {
    assert.deepEqual(Object.keys(PACKS), ['100', '1000', '3000', '5000']);
    assert.deepEqual(Object.values(PACKS).map(p => p.priceHtCents), [9_900, 69_000, 189_000, 295_000]);
});

test('pack summary: HT, TVA 20 %, TTC and price per scan', () => {
    assert.deepEqual(packSummary('1000'), { pack: 1000, scans: 1000, htCents: 69_000, vatCents: 13_800, ttcCents: 82_800, perScanHtCents: 69 });
    assert.equal(packSummary(100).perScanHtCents, 99);
    assert.equal(packSummary('5000').ttcCents, 354_000);
    for (const unknown of ['250', '', null, undefined, '1000abc', '1e3']) assert.equal(packSummary(unknown), null);
});

test('French money and counts', () => {
    assert.equal(formatEuros(9_900), '99,00 €');
    assert.equal(formatEuros(189_000), '1 890,00 €');
    assert.equal(formatEuros(13_805), '138,05 €');
    assert.equal(formatCount(5000), '5 000');
});

test('SIRET: 14 digits and a valid Luhn key, spaces allowed when typing', () => {
    const valid = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'].map(d => `1234567890123${d}`).find(isValidSiret);
    assert.ok(valid);
    assert.equal(isValidSiret(normalizeSiret(`${valid.slice(0, 3)} ${valid.slice(3, 6)} ${valid.slice(6)}`)), true);
    assert.equal(isValidSiret(`${valid.slice(0, 13)}${(Number(valid[13]) + 1) % 10}`), false);
    assert.equal(isValidSiret('1234'), false);
    assert.equal(isValidSiret('35600000000048'), true);   // La Poste head office
});

test('VAT number structure', () => {
    assert.equal(isValidVat(normalizeVat('fr 12 345678901')), true);
    assert.equal(isValidVat('FR1234'), false);
    assert.equal(isValidVat('BE0123456789'), true);
    assert.equal(isValidVat('US123456789'), false);
});

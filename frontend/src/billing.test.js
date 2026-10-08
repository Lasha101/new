import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { PACKS, packSummary, formatEuros, formatCount, purchaseLabel, UNIT_PACK, UNIT_PAYMENT_LINK, unitCheckoutUrl, UNIT_PURCHASE_RETURN_URL, isUnitPurchaseReturn, withoutPurchaseReturn, normalizeSiret, isValidSiret, normalizeVat, isValidVat, invoiceLabel, invoiceStem, parisMonth } from './billing.js';

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

test('« Mes achats »: a pack by its size, « à la carte » by the documents bought', () => {
    assert.equal(UNIT_PACK, 0);                              // backend billing.UNIT_PACK
    assert.equal(purchaseLabel({ pack: 1000, credits: 1000 }), 'Pack 1 000');
    assert.equal(purchaseLabel({ pack: 100, credits: 100 }), 'Pack 100');
    assert.equal(purchaseLabel({ pack: 0, credits: 1250 }), 'À la carte · 1 250 documents');
    assert.equal(purchaseLabel({ pack: 0, credits: 1 }), 'À la carte · 1 document');
});

test('« à la carte » from the app: the site\'s link, tied to the account by its id and e-mail', () => {
    // The site's « Acheter à l'unité » button (tarifs.html, Alex 03/10/2026) opens the same link.
    const tarifs = readFileSync(new URL('../ScanID-nouveau-site-2026-09-30/nouveau-site/tarifs.html', import.meta.url), 'utf8');
    assert.ok(tarifs.includes(`data-pack="unite" href="${UNIT_PAYMENT_LINK}"`));
    const user = { id: '0f3c9a1e2b4d4c6f8a0b1c2d3e4f5a6b', email: 'Marie.Dupont+agence@exemple.fr' };
    assert.equal(unitCheckoutUrl(user), 'https://buy.stripe.com/8x2eVc3DF4cQcQF2Elebu05'
        + '?client_reference_id=0f3c9a1e2b4d4c6f8a0b1c2d3e4f5a6b&locked_prefilled_email=Marie.Dupont%2Bagence%40exemple.fr');
    const url = new URL(unitCheckoutUrl(user));
    assert.deepEqual([...url.searchParams], [['client_reference_id', user.id], ['locked_prefilled_email', user.email]]);
});

test('back from the unit link: the address Stripe redirects to, recognised once, then removed', () => {
    const back = new URL(UNIT_PURCHASE_RETURN_URL);
    assert.equal(back.origin + back.pathname, 'https://scanid.fr/app/');
    assert.equal(isUnitPurchaseReturn(back.search), true);
    for (const other of ['', '?achat=pack', '?achat=UNITE', '?achats=unite', '?pack=100']) assert.equal(isUnitPurchaseReturn(other), false);
    assert.equal(withoutPurchaseReturn({ pathname: '/app/', search: '?achat=unite', hash: '' }), '/app/');
    assert.equal(withoutPurchaseReturn({ pathname: '/app/', search: '?x=1&achat=unite', hash: '#top' }), '/app/?x=1#top');
    assert.equal(withoutPurchaseReturn({ pathname: '/app/inscription', search: '?pack=100', hash: '' }), '/app/inscription?pack=100');
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

test('invoices (Alex, 08/10/2026): the link reads the number, a credit note says it is one', () => {
    assert.equal(invoiceLabel({ kind: 'invoice', number: 'F-2026-00001' }), 'F-2026-00001');
    assert.equal(invoiceLabel({ kind: 'credit_note', number: 'AV-2026-00001' }), 'Avoir AV-2026-00001');
    assert.equal(invoiceStem({ kind: 'invoice', number: 'F-2026-00001' }), 'Facture-F-2026-00001');
    assert.equal(invoiceStem({ kind: 'credit_note', number: 'AV-2026-00001' }), 'Avoir-AV-2026-00001');
});

test('the month proposed for the CSV is the current month in Paris', () => {
    assert.equal(parisMonth(new Date('2026-10-08T16:10:00Z')), '2026-10');
    assert.equal(parisMonth(new Date('2026-10-31T22:30:00Z')), '2026-10');   // 23:30 in Paris (winter time, UTC+1)
    assert.equal(parisMonth(new Date('2026-10-31T23:30:00Z')), '2026-11');   // 00:30 on 01/11 in Paris
    assert.equal(parisMonth(new Date('2026-12-31T22:59:00Z')), '2026-12');   // 23:59 in Paris
    assert.equal(parisMonth(new Date('2026-12-31T23:00:00Z')), '2027-01');   // midnight in Paris
});

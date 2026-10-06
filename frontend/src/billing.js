// Packs and billing identity, framework-free so `node --test` drives them.
// Mirrors backend/config.py (PACK_PRICES_HT_CENTS, VAT_RATE_PERCENT) and
// backend/billing_identity.py (SIRET / VAT checks). The server re-checks
// everything; these only let the page answer before a round trip.

export const VAT_RATE_PERCENT = 20;

/** gestion/ScanID-Pilotage.xlsx, sheet « Stripe (à créer) ». */
export const PACKS = {
    100: { scans: 100, priceHtCents: 9_900 },
    1000: { scans: 1000, priceHtCents: 69_000 },
    3000: { scans: 3000, priceHtCents: 189_000 },
    5000: { scans: 5000, priceHtCents: 295_000 },
};

/** « 1 000 » — thin French thousands grouping, the way the site writes packs. */
export const formatCount = count => String(count).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');

/** An « à la carte » purchase (1 document = 1 credit) has no pack: the server
 * stores it as pack 0 with the documents bought in `credits` (billing.UNIT_PACK). */
export const UNIT_PACK = 0;

/** « Mes achats »: « Pack 1 000 », or « À la carte · 37 documents ». */
export const purchaseLabel = purchase => (purchase.pack === UNIT_PACK
    ? `À la carte · ${formatCount(purchase.credits)} document${purchase.credits > 1 ? 's' : ''}`
    : `Pack ${formatCount(purchase.pack)}`);

/** The « à la carte » Stripe link (Alex, 03/10/2026) — the « Acheter à l'unité »
 * button of the site's tarifs.html: 1,50 € HT the document, quantity 1 to 99. */
export const UNIT_PAYMENT_LINK = 'https://buy.stripe.com/8x2eVc3DF4cQcQF2Elebu05';

/** The same link from inside the app: Stripe sends client_reference_id back
 * in the event, so this account is credited whatever the e-mail; the e-mail
 * is shown and cannot be edited on Stripe's page. */
export const unitCheckoutUrl = user =>
    `${UNIT_PAYMENT_LINK}?${new URLSearchParams({ client_reference_id: user.id, locked_prefilled_email: user.email })}`;

/** « 1 890,00 € » */
export function formatEuros(cents) {
    const euros = Math.floor(cents / 100);
    const rest = String(cents % 100).padStart(2, '0');
    return `${formatCount(euros)},${rest} €`;
}

/** The pack named by ?pack=, with its HT / TVA / TTC amounts, or null. */
export function packSummary(pack) {
    const entry = PACKS[Number(pack)];
    if (!entry || !/^\d+$/.test(String(pack))) return null;
    const vatCents = Math.floor(entry.priceHtCents * VAT_RATE_PERCENT / 100);
    return {
        pack: Number(pack),
        scans: entry.scans,
        htCents: entry.priceHtCents,
        vatCents,
        ttcCents: entry.priceHtCents + vatCents,
        perScanHtCents: Math.round(entry.priceHtCents / entry.scans),
    };
}

export const normalizeSiret = value => String(value ?? '').replace(/[\s.-]/g, '');

/** 14 digits passing the Luhn check (La Poste's establishments: digit sum % 5). */
export function isValidSiret(siret) {
    if (!/^\d{14}$/.test(siret)) return false;
    if (siret.startsWith('356000000') && siret !== '35600000000048') {
        return [...siret].reduce((sum, d) => sum + Number(d), 0) % 5 === 0;
    }
    let total = 0;
    [...siret].reverse().forEach((char, index) => {
        let digit = Number(char);
        if (index % 2 === 1) { digit *= 2; if (digit > 9) digit -= 9; }
        total += digit;
    });
    return total % 10 === 0;
}

export const normalizeVat = value => String(value ?? '').replace(/[\s.-]/g, '').toUpperCase();

/** FR + 2-character key + 9 digits; another EU prefix + 2 to 12 characters. */
export function isValidVat(vat) {
    if (vat.startsWith('FR')) return /^FR[0-9A-HJ-NP-Z]{2}\d{9}$/.test(vat);
    return /^(AT|BE|BG|CY|CZ|DE|DK|EE|EL|ES|FI|HR|HU|IE|IT|LT|LU|LV|MT|NL|PL|PT|RO|SE|SI|SK|XI)[0-9A-Z+*]{2,12}$/.test(vat);
}

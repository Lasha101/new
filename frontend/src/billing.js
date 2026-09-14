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

// The password rules, as the registration screen shows them.
//
// These mirror backend/password_policy.py. The server is the authority — it
// re-checks every rule on every request that sets a password, and a request
// that never touches this file is held to exactly the same standard. What this
// module buys is that the user sees the rules BEFORE typing and watches them
// go green as they type, instead of discovering them from a rejection.

export const MIN_LENGTH = 12;
export const MIN_UPPERCASE = 1;
export const MIN_DIGITS = 2;
export const MIN_SPECIALS = 2;

/** The four rules, in the order the brief lists them. */
export const PASSWORD_RULES = [
    {
        id: 'length',
        label: `au moins ${MIN_LENGTH} caractères`,
        test: (value) => value.length >= MIN_LENGTH,
    },
    {
        id: 'uppercase',
        label: `au moins ${MIN_UPPERCASE} majuscule`,
        test: (value) => (value.match(/\p{Lu}/gu) || []).length >= MIN_UPPERCASE,
    },
    {
        id: 'digits',
        label: `au moins ${MIN_DIGITS} chiffres`,
        test: (value) => (value.match(/\d/g) || []).length >= MIN_DIGITS,
    },
    {
        id: 'specials',
        label: `au moins ${MIN_SPECIALS} caractères spéciaux (! ? @ # $ % & * -)`,
        // Any non-alphanumeric counts, exactly as on the server: the list in
        // the label is illustrative, so an unusual but valid choice is never
        // refused for being unusual.
        test: (value) => (value.match(/[^\p{L}\p{N}]/gu) || []).length >= MIN_SPECIALS,
    },
];

/** `{ length: true, uppercase: false, ... }` for a candidate. */
export function evaluatePassword(value) {
    const password = typeof value === 'string' ? value : '';
    return Object.fromEntries(PASSWORD_RULES.map((rule) => [rule.id, rule.test(password)]));
}

/** True when every rule is satisfied. Composition only — the server also
 *  applies the common-password blocklist, which cannot be mirrored here
 *  without shipping the list to the browser. */
export function satisfiesAllRules(value) {
    return PASSWORD_RULES.every((rule) => rule.test(typeof value === 'string' ? value : ''));
}

// --- The example -------------------------------------------------------
//
// Deliberately GENERATED, never a fixed string. Whatever a public app prints
// as an example is a password real users will type verbatim, which would make
// it a known credential on every account that copied it. A fresh one per page
// load cannot be that.
//
// The words are ordinary concrete nouns, chosen to be absent from the server's
// common-password blocklist (backend/common_passwords.txt) so the generated
// example actually passes the policy it illustrates.
const EXAMPLE_WORDS = [
    'Girafe', 'Nuage', 'Vélo', 'Lampe', 'Rivage', 'Cactus', 'Tuile', 'Brume',
    'Chêne', 'Falaise', 'Marée', 'Plume', 'Sablier', 'Vigne', 'Hibou', 'Ancre',
    'Comète', 'Dune', 'Écorce', 'Fjord', 'Grelot', 'Jardin', 'Kiosque', 'Lagune',
];
const EXAMPLE_SPECIALS = ['!', '?', '@', '#', '$', '%', '&', '*', '-'];

const pick = (list) => list[Math.floor(Math.random() * list.length)];

/**
 * A fresh, policy-compliant example password.
 *
 * Shape: Word + Word + two digits + two specials — comfortably over 12
 * characters, with an uppercase from each word.
 */
export function generateExamplePassword() {
    let first = pick(EXAMPLE_WORDS);
    let second = pick(EXAMPLE_WORDS);
    while (second === first) second = pick(EXAMPLE_WORDS);

    const digits = String(Math.floor(Math.random() * 90) + 10); // 10-99, always 2
    const specials = pick(EXAMPLE_SPECIALS) + pick(EXAMPLE_SPECIALS);

    const example = `${first}${second}${digits}${specials}`;
    // A generator that could emit a non-compliant example would undermine the
    // thing it illustrates; if the shape ever changes, fall back to padding.
    return satisfiesAllRules(example) ? example : `${example}A1!`;
}

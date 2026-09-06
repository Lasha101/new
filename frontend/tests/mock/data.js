// The dataset the mocked API serves. Entirely synthetic: invented names, and
// document numbers outside every real French series.
//
// Composition is deliberate — 2 passports and 3 identity cards — so the
// Tous/PASS/PI filter has three distinct row counts to prove itself with.

export const MOCK_USER = {
    id: 'u-alice',
    first_name: 'Alice',
    last_name: 'Testeuse',
    email: 'alice@example.com',
    phone_number: '0102030405',
    user_name: 'alice',
    role: 'user',
    uploaded_pages_count: 3,
    page_credits: 12,
    passports: [],
    voyages: [],
};

const passport = (id, overrides) => ({
    id,
    owner_id: MOCK_USER.id,
    first_name: 'Prénom',
    last_name: 'Nom',
    birth_date: '1990-05-17',
    expiration_date: '2030-01-02',
    nationality: 'Française',
    passport_number: '00XX00000',
    destination: null,
    confidence_score: 0.87,
    voyages: [],
    ...overrides,
});

// PASS = the French passport shape (2 digits, 2 letters, 5 digits);
// PI = anything else (12-digit old CNI, 9-character new CNI).
export const MOCK_PASSPORTS = [
    passport('p-1', {
        first_name: 'Élodie', last_name: 'Dupont-Lévy', passport_number: '12AB34567',
        destination: 'Dubrovnik été', confidence_score: 0.8734, birth_date: '1990-05-17',
    }),
    passport('p-2', {
        first_name: 'Jean', last_name: 'Martin', passport_number: '98ZY12345',
        destination: 'Rome', confidence_score: 0.91, birth_date: '1982-11-03',
    }),
    passport('p-3', {
        first_name: 'Chloé', last_name: 'Bernard', passport_number: '123456789012',
        destination: 'Rome', confidence_score: null, birth_date: '1975-02-28',
    }),
    passport('p-4', {
        first_name: 'Noé', last_name: 'Petit', passport_number: 'X4RTBPFW4',
        destination: null, confidence_score: 0.5, birth_date: '2001-07-09',
    }),
    passport('p-5', {
        first_name: 'Camille', last_name: 'Moreau', passport_number: 'D2H6862M2',
        destination: 'Dubrovnik été', confidence_score: 0.66, birth_date: '1968-12-24',
    }),
];

/** The row an upload produces once its OCR job finishes. */
export const EXTRACTED_PASSPORT = passport('p-new', {
    first_name: 'Specimen', last_name: 'Harnais', passport_number: '77QW88888',
    destination: null, confidence_score: 0.94, birth_date: '2000-01-01',
    expiration_date: '2030-01-01',
});

export const EXPECTED_ROW_COUNTS = { '': 5, PASS: 2, PI: 3 };

/** Fresh, isolated state for one browser context. */
export function createMockState(overrides = {}) {
    return {
        user: structuredClone(MOCK_USER),
        passports: structuredClone(MOCK_PASSPORTS),
        jobs: [],
        token: 'mock-jwt-token',
        // Whether POST /token has issued a session in this context. The mock
        // authorises on this rather than on the cookie, because WebKit does not
        // expose `cookie` on an intercepted request — see mock/api.js.
        session: false,
        requests: [],
        ...overrides,
    };
}

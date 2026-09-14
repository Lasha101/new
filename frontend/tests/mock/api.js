// A stand-in for the FastAPI backend, served through Playwright route
// interception. The browser still runs the real app: the real login form, the
// real file input, the real filter, sort and export code — only the server is
// substituted, so the suite is deterministic and costs no Vision OCR calls.
//
// Set E2E_MODE=live to skip this entirely and drive a running backend instead.
//
// Everything here mirrors backend/main.py: the same paths, the same response
// shapes (schemas.py), the same French error strings, the same
// Content-Disposition header. When the API changes, this file must change with
// it — the README says so, loudly.
import { createMockState, EXTRACTED_PASSPORT } from './data.js';
import { buildXlsx } from './xlsx.js';

const PASSPORT_NUMBER_RE = /^\d{2}[A-Z]{2}\d{5}$/;

// backend/config.py _DEFAULT_PAYMENT_LINKS — the live links published on scanid.fr.
const PAYMENT_LINKS = {
    100: 'https://buy.stripe.com/9B64gy8XZfVycQFdiZebu00',
    1000: 'https://buy.stripe.com/8x27sK0rtbFi8Apgvbebu01',
    3000: 'https://buy.stripe.com/6oU8wOa2324I9Eta6Nebu02',
    5000: 'https://buy.stripe.com/6oU14mdefaBe3g5gvbebu03',
};
/** billing.checkout_url() */
const checkoutUrl = (pack, email, userId) =>
    `${PAYMENT_LINKS[pack]}?${new URLSearchParams({ prefilled_email: email, client_reference_id: userId })}`;

// ocr_service._UNRECOGNIZED_DOCUMENT_DETAIL. A file whose name starts with
// « illisible » produces a failed job carrying this detail.
const UNRECOGNIZED_DOCUMENT_DETAIL = "Document non reconnu : aucune MRZ de passeport français (P<FRA...), "
    + "aucune MRZ de carte nationale d'identité (IDFRA...) ni aucun recto de CNI exploitable n'a été détecté sur cette page.";
const documentType = number =>
    (PASSPORT_NUMBER_RE.test(String(number ?? '').trim().toUpperCase()) ? 'PP' : 'PI');

// EXPORT_COLUMNS / EXPORT_HEADERS in backend/main.py.
const EXPORT_COLUMNS = ['last_name', 'first_name', 'birth_date', 'expiration_date', 'nationality',
    'passport_number', 'document_type', 'destination', 'confidence_score'];
const EXPORT_HEADERS = {
    last_name: 'Nom de famille', first_name: 'Prénom', birth_date: 'Date de Naissance',
    expiration_date: "Date d'Expiration", nationality: 'Nationalité',
    passport_number: 'Numéro de document', document_type: 'Type',
    destination: 'Destination', confidence_score: 'Score de Confiance',
};

// The session now travels in a cookie, so every request is credentialed — and
// a credentialed response may NOT carry `access-control-allow-origin: *`. The
// browser drops it before the app ever sees it, which looks exactly like a
// network failure. The real server echoes the single configured origin; the
// mock echoes the page's own, which is the same thing under test.
const corsHeaders = (request) => ({
    'access-control-allow-origin': (() => {
        try { return new URL(request.frame().url()).origin; } catch { return 'http://localhost:5173'; }
    })(),
    'access-control-allow-credentials': 'true',
    'access-control-allow-methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'access-control-allow-headers': 'Authorization, Content-Type, Accept, X-Requested-With',
    'access-control-expose-headers': 'Content-Disposition',
});

/** ISO date -> DD/MM/YYYY, as _format_display_date does server-side. */
const displayDate = (value) => {
    const match = String(value ?? '').match(/^(\d{4})-(\d{2})-(\d{2})/);
    return match ? `${match[3]}/${match[2]}/${match[1]}` : String(value ?? '');
};

const exportCell = (row, column) => {
    if (column === 'document_type') return documentType(row.passport_number);
    const value = row[column];
    if (value === null || value === undefined) return '';
    if (column.endsWith('_date')) return displayDate(value);
    return typeof value === 'string' ? value.toUpperCase() : value;
};

function buildCsv(rows) {
    const line = cells => `${cells.join(';')}\r\n`;
    let csv = line(EXPORT_COLUMNS.map(column => EXPORT_HEADERS[column]));
    for (const row of rows) {
        csv += line(EXPORT_COLUMNS.map((column) => {
            const value = exportCell(row, column);
            // Mirrors _csv_cell: all-digit strings are forced to text for Excel.
            if (typeof value === 'string' && /^\d+$/.test(value) && value !== '') return `="${value}"`;
            return String(value);
        }));
    }
    return Buffer.concat([Buffer.from([0xef, 0xbb, 0xbf]), Buffer.from(csv, 'utf8')]); // UTF-8 BOM
}

const buildXlsxExport = rows => buildXlsx([
    EXPORT_COLUMNS.map(column => EXPORT_HEADERS[column]),
    ...rows.map(row => EXPORT_COLUMNS.map(column => String(exportCell(row, column)))),
]);

/** Path within the API, with the '/api' prefix stripped when it is used. */
function apiPath(url) {
    const path = url.pathname.replace(/^\/api(?=\/|$)/, '');
    return path.endsWith('/') && path !== '/' ? path.slice(0, -1) : path;
}

const API_PATHS = [
    '/token', '/logout', '/users/me', '/users/register', '/events', '/destinations', '/auth',
    '/admin/filterable-users', '/admin/users', '/admin/trial-requests', '/passports', '/ocr/jobs', '/export/data',
    '/signup', '/orders', '/session',
];


/**
 * The four composition rules of backend/password_policy.py, with the same
 * French messages. The blocklist is not mirrored — it is a 380-entry file on
 * the server — so the mock refuses only what composition can decide, which is
 * every case the E2E suites exercise.
 */
function passwordPolicyErrors(password) {
    const errors = [];
    if (password.length < 12) errors.push('Le mot de passe doit contenir au moins 12 caractères.');
    if ((password.match(/\p{Lu}/gu) || []).length < 1) errors.push('Le mot de passe doit contenir au moins 1 majuscule.');
    if ((password.match(/\d/g) || []).length < 2) errors.push('Le mot de passe doit contenir au moins 2 chiffres.');
    if ((password.match(/[^\p{L}\p{N}]/gu) || []).length < 2) {
        errors.push('Le mot de passe doit contenir au moins 2 caractères spéciaux (! ? @ # $ % & * -).');
    }
    return errors;
}

/** True for a request the mocked backend owns (never for a Vite asset). */
export function isApiRequest(url) {
    const path = apiPath(url);
    return API_PATHS.some(prefix => path === prefix || path.startsWith(`${prefix}/`));
}

/**
 * Installs the mocked API on a browser context.
 *
 * @param {import('@playwright/test').BrowserContext} context
 * @param {{state?:object, processingMs?:number, credentials?:{username:string,password:string}}} options
 * @returns the mutable state, so a test can seed rows or read what was requested.
 */
export async function installMockApi(context, options = {}) {
    const state = options.state || createMockState();
    const processingMs = options.processingMs ?? 1200;
    // A copy, because a password reset changes the password this mock accepts.
    const credentials = { ...(options.credentials
        || { username: process.env.E2E_USERNAME || 'alice', password: process.env.E2E_PASSWORD || 'test-password' }) };
    // The one password link this mock considers valid (backend: account_tokens.py).
    state.passwordLinkToken = state.passwordLinkToken || 'jeton-valide-de-test';

    const json = (route, status, body, headers = {}) => route.fulfill({
        status,
        contentType: 'application/json',
        headers: { ...corsHeaders(route.request()), ...headers },
        body: JSON.stringify(body),
    });

    // Either credential is accepted, exactly as backend/auth.py does: the
    // cookie is what the browser sends now, and the Bearer header is still
    // honoured for any client that presents one.
    //
    // `allHeaders()`, NOT `headers()`. Playwright's `headers()` returns the
    // non-security view of the headers and OMITS `cookie` — on Chromium it
    // happened to be there anyway, on WebKit it never is. Reading the wrong
    // one made every request after login look anonymous in Safari while
    // passing in Chrome, which is the exact shape of bug the WebKit project
    // exists to catch. `allHeaders()` is async, hence the await below.
    //
    // WebKit does not expose `cookie` on an INTERCEPTED request — neither
    // `headers()` nor `allHeaders()` shows it, because Playwright reports the
    // headers before the network stack attaches them, and a routed request
    // never reaches that stack. Chromium happens to include it, which is why
    // this passed there and failed in Safari. So the mock cannot validate the
    // cookie by reading it; it tracks the session it issued instead, which is
    // what a stand-in is for. That the cookie is genuinely what authenticates
    // is proven server-side, against the real app, by
    // backend/tests/test_security_hardening.py::
    // test_the_cookie_alone_authenticates_a_request.
    const authorized = async (request) => {
        if (state.session) return true;
        const headers = await request.allHeaders();
        if (headers.authorization === `Bearer ${state.token}`) return true;
        const cookie = headers.cookie || '';
        return cookie.split(';').some(part => part.trim() === `scanid_session=${state.token}`);
    };
    const unauthorized = route => json(route, 401,
        { detail: "Impossible de valider les informations d'identification" });

    /** Jobs age into their terminal state, so polling behaves like the real thing. */
    const materializeJobs = () => state.jobs.map((job) => {
        if (job.status !== 'processing') return job;
        const elapsed = Date.now() - job.startedAt;
        if (elapsed < processingMs) {
            return { ...job, progress: Math.min(70, 20 + Math.round((elapsed / processingMs) * 50)) };
        }
        // First observation past the deadline commits the result, exactly once:
        // a row lands in the table, a page is charged, a credit is spent.
        if (!job.committed && job.unreadable) {
            // A page with no recognisable document: the job fails, the page is
            // counted, and no credit is taken (only successes are charged).
            job.committed = true;
            job.status = 'failed';
            job.progress = 100;
            job.finished_at = new Date().toISOString();
            job.failures = [{ page_number: 1, detail: UNRECOGNIZED_DOCUMENT_DETAIL }];
            state.user.uploaded_pages_count += 1;
        }
        if (!job.committed) {
            job.committed = true;
            job.status = 'complete';
            job.progress = 100;
            job.finished_at = new Date().toISOString();
            job.successes = [{ page_number: 1, data: { ...EXTRACTED_PASSPORT } }];
            state.passports = [{ ...EXTRACTED_PASSPORT, destination: job.destination ?? null },
                ...state.passports];
            state.user.page_credits = Math.max(0, state.user.page_credits - 1);
            state.user.uploaded_pages_count += 1;
        }
        return job;
    });

    const publicJob = job => ({
        id: job.id, user_id: job.user_id, file_name: job.file_name, status: job.status,
        progress: job.progress, created_at: job.created_at, finished_at: job.finished_at ?? null,
        successes: job.successes, failures: job.failures,
    });

    await context.route(url => isApiRequest(url), async (route) => {
        const request = route.request();
        const url = new URL(request.url());
        const path = apiPath(url);
        const method = request.method();
        state.requests.push({ method, path, search: url.search });

        if (method === 'OPTIONS') {
            return route.fulfill({ status: 204, headers: corsHeaders(request), body: '' });
        }

        // --- Authentication ---
        if (path === '/token' && method === 'POST') {
            const form = new URLSearchParams(request.postData() || '');
            if (form.get('username') === credentials.username && form.get('password') === credentials.password) {
                // The body is unchanged — the API contract did not move — but
                // the session now also arrives as an HttpOnly cookie, which is
                // what the app actually authenticates with from here on.
                // No `Secure`: the tests run over plain-HTTP localhost.
                // Two cookies, as backend/auth.py sets: the HttpOnly session
                // itself, and the readable marker that lets the app tell an
                // expired session from a first visit.
                state.session = true;
                return json(route, 200, { access_token: state.token, token_type: 'bearer' }, {
                    'set-cookie': [
                        `scanid_session=${state.token}; Path=/; HttpOnly; SameSite=Lax`,
                        'scanid_has_session=1; Path=/; SameSite=Lax; Max-Age=2592000',
                    ].join('\n'),
                });
            }
            return json(route, 401, { detail: "Nom d'utilisateur ou mot de passe incorrect" });
        }

        // POST /auth/forgot-password — the same answer whether or not the account exists.
        if (path === '/auth/forgot-password' && method === 'POST') {
            state.forgotPasswordRequests = [...(state.forgotPasswordRequests || []), JSON.parse(request.postData() || '{}').identifier];
            return json(route, 200, { detail: "Si un compte correspond à cet identifiant, un email contenant un lien de réinitialisation vient de lui être envoyé. Le lien est valable 48 heures." });
        }

        // POST /auth/reset-password — one valid, single-use link; the usual policy.
        if (path === '/auth/reset-password' && method === 'POST') {
            const body = JSON.parse(request.postData() || '{}');
            if (!body.token || body.token !== state.passwordLinkToken) {
                return json(route, 400, { detail: "Ce lien n'est plus valide (il a expiré ou a déjà servi). Demandez un nouveau lien depuis « Mot de passe oublié ? »." });
            }
            const policyErrors = passwordPolicyErrors(body.password || '');
            if (policyErrors.length) return json(route, 422, { detail: policyErrors.join(' ') });
            state.passwordLinkToken = null;
            credentials.password = body.password;
            state.session = false;             // main.py: a reset ends the account's sessions
            return json(route, 200, { detail: 'Votre mot de passe est enregistré. Vous pouvez vous connecter.', user_name: credentials.username });
        }

        // Logging out is a server round-trip now: an HttpOnly cookie cannot be
        // deleted from JavaScript.
        if (path === '/logout' && method === 'POST') {
            state.session = false;
            return json(route, 200, { detail: 'Déconnexion réussie' }, {
                'set-cookie': [
                    'scanid_session=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0',
                    'scanid_has_session=; Path=/; SameSite=Lax; Max-Age=0',
                ].join('\n'),
            });
        }

        // POST /session/refresh — activity renews a still-valid session (main.py).
        if (path === '/session/refresh' && method === 'POST') {
            if (!(await authorized(request))) return unauthorized(route);
            // A slow network, on demand: the renewed cookie lands when the answer does.
            if (state.refreshDelayMs) await new Promise(resolve => setTimeout(resolve, state.refreshDelayMs));
            state.session = true;
            return json(route, 200, { access_token: state.token, token_type: 'bearer' }, {
                'set-cookie': `scanid_session=${state.token}; Path=/; HttpOnly; SameSite=Lax`,
            });
        }

        // --- Server-sent events: an open, silent stream. The app treats a
        // closed stream as a dropped connection and reconnects, which is fine.
        if (path === '/events') {
            return route.fulfill({
                status: 200,
                headers: { ...corsHeaders(request), 'content-type': 'text/event-stream', 'cache-control': 'no-cache' },
                body: ': keep-alive\n\n',
            });
        }

        // POST /users/register — self-registration (main.py:614). Mirrors the two
        // French conflict messages and the 5/minute limit's 429.
        if (path === '/users/register' && method === 'POST') {
            const body = JSON.parse(request.postData() || '{}');
            if (body.email === state.user.email) {
                return json(route, 400, { detail: 'Email déjà enregistré' });
            }
            if (body.user_name === state.user.user_name) {
                return json(route, 400, { detail: "Nom d'utilisateur déjà enregistré" });
            }
            // The password policy is enforced server-side (package C,
            // backend/password_policy.py). The mock mirrors main.py, so it
            // must refuse what the real endpoint refuses — and in the same
            // ORDER: main.py checks the two conflicts first, so a duplicate
            // username is reported as a duplicate even when the password is
            // also weak.
            const policyErrors = passwordPolicyErrors(body.password || '');
            if (policyErrors.length) return json(route, 422, { detail: policyErrors.join(' ') });
            return json(route, 200, {
                ...body, id: 'u-new', role: 'user', password: undefined,
                uploaded_pages_count: 0, page_credits: 10, passports: [], voyages: [],
            });
        }

        // POST /signup — /app/inscription (main.py signup_for_pack).
        if (path === '/signup' && method === 'POST') {
            const body = JSON.parse(request.postData() || '{}');
            if (!PAYMENT_LINKS[body.pack]) {
                return json(route, 400, { detail: "Ce pack n'existe pas. Choisissez un pack sur https://scanid.fr/#tarifs." });
            }
            if (String(body.email || '').toLowerCase() === state.user.email) {
                return json(route, 400, { detail: 'Un compte existe déjà avec cette adresse email. Connectez-vous pour acheter ce pack.' });
            }
            const policyErrors = passwordPolicyErrors(body.password || '');
            if (policyErrors.length) return json(route, 422, { detail: policyErrors.join(' ') });
            state.signups = [...(state.signups || []), body];
            return json(route, 200, { checkout_url: checkoutUrl(body.pack, String(body.email).toLowerCase(), 'u-new'), purchase_id: 'pu-new' });
        }

        if (!(await authorized(request))) return unauthorized(route);

        // POST /orders — a logged-in customer buys a pack (main.py order_pack).
        if (path === '/orders' && method === 'POST') {
            const { pack } = JSON.parse(request.postData() || '{}');
            if (!PAYMENT_LINKS[pack]) {
                return json(route, 400, { detail: "Ce pack n'existe pas. Choisissez un pack sur https://scanid.fr/#tarifs." });
            }
            return json(route, 200, { checkout_url: checkoutUrl(pack, state.user.email, state.user.id), purchase_id: 'pu-order' });
        }

        if (path === '/users/me' && method === 'PUT') {
            const body = JSON.parse(request.postData() || '{}');
            // The server never echoes the password back, and a non-admin cannot
            // move its own counters (main.py update_user_me).
            const { password: _password, uploaded_pages_count, page_credits, ...safe } = body;
            const counters = state.user.role === 'admin'
                ? { uploaded_pages_count, page_credits }
                : {};
            state.user = { ...state.user, ...safe, ...counters };
            return json(route, 200, state.user);
        }

        // GET /users/me/purchases — « Mes achats » (main.py read_my_purchases).
        if (path === '/users/me/purchases' && method === 'GET') {
            return json(route, 200, state.purchases || []);
        }

        if (path === '/users/me') {
            materializeJobs();
            return json(route, 200, state.user);
        }

        if (path === '/destinations') {
            const destinations = [...new Set(state.passports.map(row => row.destination).filter(Boolean))].sort();
            return json(route, 200, destinations);
        }

        // « Demandes d'essai » (main.py list/validate/reject_trial_request).
        if (path.startsWith('/admin/trial-requests')) {
            if (state.user.role !== 'admin') return json(route, 403, { detail: "Privilèges d'administrateur requis." });
            state.trialRequests = state.trialRequests || [];
            if (path === '/admin/trial-requests' && method === 'GET') {
                return json(route, 200, state.trialRequests.filter(row => row.status === 'pending'));
            }
            const [, , , id, action] = path.split('/');
            const row = state.trialRequests.find(candidate => candidate.id === id);
            if (!row) return json(route, 404, { detail: "Demande d'essai introuvable." });
            if (row.status !== 'pending') return json(route, 409, { detail: 'Cette demande a déjà été traitée.' });
            if (method === 'POST' && (action === 'validate' || action === 'reject')) {
                row.status = action === 'validate' ? 'validated' : 'rejected';
                row.decided_at = new Date().toISOString();
                return json(route, 200, row);
            }
        }

        if (path === '/admin/filterable-users') {
            if (state.user.role !== 'admin') return json(route, 403, { detail: "Privilèges d'administrateur requis." });
            return json(route, 200, [state.user]);
        }

        // --- OCR jobs ---
        if (path === '/passports/upload-and-extract' && method === 'POST') {
            if (state.user.page_credits <= 0) {
                return json(route, 403, { detail: "Crédits insuffisants. Veuillez contacter l'administrateur." });
            }
            const body = request.postData() || '';
            const fileName = body.match(/filename="([^"]*)"/)?.[1] || 'document';
            const destination = body.match(/name="destination"\r?\n\r?\n([^\r\n]*)/)?.[1] || null;
            const job = {
                id: `job-${state.jobs.length + 1}`, user_id: state.user.id, file_name: fileName,
                status: 'processing', progress: 20, created_at: new Date().toISOString(),
                finished_at: null, successes: [], failures: [],
                startedAt: Date.now(), committed: false, destination,
                unreadable: /^illisible/i.test(fileName),
            };
            state.jobs.unshift(job);
            return json(route, 200, publicJob(job));
        }

        if (path === '/ocr/jobs' && method === 'GET') {
            return json(route, 200, materializeJobs().map(publicJob));
        }

        if (path.startsWith('/ocr/jobs/') && method === 'DELETE') {
            const id = path.split('/').pop();
            const job = state.jobs.find(candidate => candidate.id === id);
            if (!job) return json(route, 404, { detail: 'Job not found.' });
            state.jobs = state.jobs.filter(candidate => candidate.id !== id);
            return json(route, 200, publicJob(job));
        }

        // --- Exports ---
        if (path === '/export/data' && method === 'GET') {
            materializeJobs();
            const params = url.searchParams;
            let rows = state.passports;
            if (params.get('destination')) rows = rows.filter(row => row.destination === params.get('destination'));
            if (params.get('document_type')) {
                // 'PASS' is the legacy passport code, still accepted (main.py LEGACY_DOC_TYPE_PASSPORT).
                const wanted = params.get('document_type') === 'PASS' ? 'PP' : params.get('document_type');
                rows = rows.filter(row => documentType(row.passport_number) === wanted);
            }
            if (rows.length === 0) {
                return json(route, 404, { detail: 'Aucune donnée de passeport trouvée pour les critères donnés' });
            }
            if (params.get('preview') === 'true') {
                return json(route, 200, rows.map(row => Object.fromEntries(
                    EXPORT_COLUMNS.map(column => [column, exportCell(row, column)]))));
            }
            const format = params.get('format') === 'csv' ? 'csv' : 'xlsx';
            const stem = `passeports_pour_${state.user.user_name}`;
            return sendFile(route, format, `${stem}.${format}`, rows);
        }

        if (path === '/export/data/selection' && method === 'POST') {
            const ids = JSON.parse(request.postData() || '{}').passport_ids || [];
            const rows = state.passports.filter(row => ids.includes(row.id));
            if (rows.length === 0) {
                return json(route, 404, { detail: 'Aucune donnée de passeport trouvée pour les critères donnés' });
            }
            const format = url.searchParams.get('format') === 'csv' ? 'csv' : 'xlsx';
            return sendFile(route, format, `selection_passeports.${format}`, rows);
        }

        // --- Documents ---
        if (path === '/passports' && method === 'GET') {
            materializeJobs();
            const destination = url.searchParams.get('voyage_filter')
                || url.searchParams.get('destination_filter');
            const rows = destination
                ? state.passports.filter(row => row.destination === destination)
                : state.passports;
            return json(route, 200, rows);
        }

        // POST /passports/ — manual creation (main.py:694). The row the server
        // returns is the posted body plus a server-assigned id and owner.
        if (path === '/passports' && method === 'POST') {
            const body = JSON.parse(request.postData() || '{}');
            const created = {
                id: `p-manual-${state.passports.length + 1}`,
                owner_id: state.user.id,
                first_name: '', last_name: '', birth_date: null, expiration_date: null,
                nationality: '', passport_number: '', destination: null,
                confidence_score: null, voyages: [],
                ...body,
            };
            state.passports = [created, ...state.passports];
            return json(route, 200, created);
        }

        if (path.startsWith('/passports/') && method === 'PUT') {
            const id = path.split('/').pop();
            const index = state.passports.findIndex(row => row.id === id);
            if (index === -1) return json(route, 404, { detail: 'Passeport non trouvé' });
            state.passports[index] = { ...state.passports[index], ...JSON.parse(request.postData() || '{}') };
            return json(route, 200, state.passports[index]);
        }

        if (path === '/passports/delete-multiple' && method === 'POST') {
            const ids = JSON.parse(request.postData() || '{}').passport_ids || [];
            state.passports = state.passports.filter(row => !ids.includes(row.id));
            return json(route, 200, { detail: `${ids.length} passeports supprimés.` });
        }

        if (path.startsWith('/passports/') && method === 'DELETE') {
            const id = path.split('/').pop();
            const row = state.passports.find(candidate => candidate.id === id);
            if (!row) return json(route, 404, { detail: 'Passeport non trouvé' });
            state.passports = state.passports.filter(candidate => candidate.id !== id);
            return json(route, 200, row);
        }

        // Anything the app asks for that is not mocked must be loud, not silently
        // empty, or a suite could pass against a hole in this file.
        return json(route, 501, { detail: `Mock API: ${method} ${path} is not implemented.` });
    });

    function sendFile(route, format, filename, rows) {
        const body = format === 'csv' ? buildCsv(rows) : buildXlsxExport(rows);
        return route.fulfill({
            status: 200,
            headers: {
                ...corsHeaders(route.request()),
                'content-type': format === 'csv'
                    ? 'text/csv; charset=utf-8'
                    : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                // Unquoted, exactly as the backend sends it.
                'content-disposition': `attachment; filename=${filename}`,
            },
            body,
        });
    }

    return state;
}

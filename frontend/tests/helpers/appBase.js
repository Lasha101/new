// Where the application answers, as a path.
//
// The public site (frontend/site/) occupies the origin root now, and the
// application moved behind it to /app/ — `base` in frontend/vite.config.js.
// Everything that navigates goes through APP_BASE so that a suite means "the
// application", not "the root of whatever host it was pointed at".
//
// WHY NOT JUST KEEP page.goto('/')
// --------------------------------
// Because it would keep working locally and fail everywhere else, which is the
// worst of both. Vite's dev server AND its preview server answer a request for
// '/' with a 302 to the base, so `page.goto('/')` still lands on the app when
// the suite drives `npm run dev` or `vite preview`. Point the same suite at
// production with E2E_BASE_URL — a documented mode, see tests/README.md — and
// '/' is the French marketing homepage, where not one .sid-* selector exists.
// Every test would fail with "login form not visible" and nothing would say why.
//
// E2E_APP_BASE exists for the deployment that serves the app somewhere else. It
// must keep the leading and trailing slash: it is joined by concatenation.
export const APP_BASE = process.env.E2E_APP_BASE || '/app/';

/** '/app/' + 'src/upload/imagePrep.js' — a path under the application's base. */
export const appPath = (path = '') => APP_BASE + String(path).replace(/^\/+/, '');

/**
 * A SOURCE module, as the dev server serves it.
 *
 * `import('/src/upload/imagePrep.js')` inside page.evaluate() is a request to
 * the server, not a bundler instruction, and Vite serves nothing outside its
 * base — so under /app/ that path 404s and the dynamic import rejects inside
 * the browser, where the failure surfaces as an unrelated evaluate error.
 */
export const appSrc = (module) => appPath(`src/${String(module).replace(/^\/?src\//, '')}`);

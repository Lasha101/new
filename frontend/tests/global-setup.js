// Runs once, after the dev server is up and before any browser opens.
//
// Two jobs:
//  1. the fixtures the suites upload are generated, not committed, so they must
//     exist by now;
//  2. warm the dev server. Vite pre-bundles dependencies and transforms modules
//     on the first request, and that first request triggers a full page reload —
//     which, landing mid-login in a parallel worker, produced a genuine flake.
//     Paying that cost once here, serially, removes the whole class.
import { ensureFixtures } from './fixtures/generate.mjs';
import { FILES_DIR } from './fixtures/index.js';
import { APP_BASE, appSrc } from './helpers/appBase.js';

// Under the application's base, and not at the root: Vite serves nothing outside
// its base, so '/src/main.jsx' is a 404 there. The failure would be invisible —
// every miss here is swallowed by the try/catch below and the `response.ok`
// guard — and the flake described above would quietly come back.
const WARMUP_PATHS = [APP_BASE, appSrc('main.jsx'), appSrc('App.jsx')];

async function warmUpDevServer(baseURL) {
    for (const path of WARMUP_PATHS) {
        for (let attempt = 0; attempt < 3; attempt++) {
            try {
                const response = await fetch(new URL(path, baseURL), { signal: AbortSignal.timeout(30_000) });
                await response.arrayBuffer(); // force the transform to complete
                if (response.ok) break;
            } catch {
                // The server may still be booting, or E2E_BASE_URL may point at a
                // production build with no /src. Neither is fatal.
            }
        }
    }
}

export default async function globalSetup(config) {
    const built = ensureFixtures({ log: line => console.log(line) });
    if (built.length > 0) console.log(`Generated ${built.length} fixture(s) in ${FILES_DIR}`);

    const baseURL = config?.projects?.[0]?.use?.baseURL
        || process.env.E2E_BASE_URL || 'http://127.0.0.1:5173';
    await warmUpDevServer(baseURL);
}

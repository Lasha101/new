import { defineConfig, devices } from '@playwright/test';
import { webkitLaunchEnv } from './tests/scripts/webkit-preload.js';

// Three viewports, because the mobile behaviour of this app is what later
// packages change: a desktop baseline, the narrowest phone still in use, and a
// 375 px iPhone on WebKit — Safari differs from Chromium in ways that matter
// here (file input behaviour, EXIF handling, sticky positioning, downloads).
//
// Set E2E_SKIP_WEBKIT=1 to drop the WebKit project on a machine where it cannot
// launch. That is a real loss of coverage, so it is opt-in and never silent.
const skipWebkit = process.env.E2E_SKIP_WEBKIT === '1';

const projects = [
    {
        name: 'desktop',
        use: { ...devices['Desktop Chrome'], viewport: { width: 1280, height: 800 } },
    },
    {
        name: 'mobile-small',
        use: {
            ...devices['Desktop Chrome'],
            viewport: { width: 360, height: 640 },
            hasTouch: true,
            isMobile: true,
        },
    },
];

if (!skipWebkit) {
    projects.push({
        name: 'mobile-375',
        use: {
            ...devices['iPhone 8'],          // WebKit, 375x667, deviceScaleFactor 2, touch
            viewport: { width: 375, height: 667 },
            deviceScaleFactor: 2,
            browserName: 'webkit',
            launchOptions: { env: webkitLaunchEnv() },
        },
    });
}

// The PWA suite needs the BUILT app: the service worker, the manifest and the
// icons only exist after `vite build`, and a worker in front of Vite's dev
// server would hide HMR updates. It therefore runs against `vite preview` on
// its own port, in its own directory, and is skipped when someone points the
// run at an external server without also providing a built one.
const PREVIEW_URL = process.env.E2E_PREVIEW_URL || 'http://127.0.0.1:4173';
const managedPreview = !process.env.E2E_BASE_URL && !process.env.E2E_PREVIEW_URL;
if (managedPreview || process.env.E2E_PREVIEW_URL) {
    projects.push({
        name: 'pwa',
        testDir: './tests/pwa',
        use: {
            ...devices['Desktop Chrome'],
            viewport: { width: 390, height: 844 },
            baseURL: PREVIEW_URL,
            // A worker registered by one spec must not survive into the next.
            serviceWorkers: 'allow',
        },
    });
}

// The app talks to the API on ITS OWN ORIGIN, at /api — which is what ships:
// deploy/nginx-travelapp.conf serves the frontend at `/` and proxies `/api/` to
// the backend on 127.0.0.1:8001, so the browser only ever sees one origin.
//
// This has to be set here because `frontend/.env.local` points VITE_API_URL at
// http://127.0.0.1:8001 for local development, which is a DIFFERENT ORIGIN, and
// since package C the session travels in a cookie. WebKit (Safari, and the
// mobile-375 project) refuses to send a cookie on a cross-origin subresource
// request — it treats it as third-party — so every request after login arrived
// without credentials and answered 401. Chromium is more permissive and passed,
// which is exactly the kind of difference the WebKit project exists to catch.
//
// Vite gives a real environment variable priority over a .env file, so this
// wins over .env.local without editing it. E2E_MODE=live sets its own value and
// is left alone.
const SERVER_ENV = process.env.VITE_API_URL
    ? { VITE_API_URL: process.env.VITE_API_URL }
    : { VITE_API_URL: '/api' };

export default defineConfig({
    testDir: './tests/e2e',
    globalSetup: './tests/global-setup.js',
    // Suites must not depend on each other's leftovers: every spec logs in itself.
    fullyParallel: true,
    forbidOnly: !!process.env.CI,
    retries: process.env.CI ? 1 : 0,
    // Capped: eight browsers hammering one Vite dev server starved requests and
    // produced flakes that had nothing to do with the app.
    workers: process.env.CI ? 1 : 4,
    reporter: process.env.CI ? [['list'], ['html', { open: 'never' }]] : [['list']],
    // Live runs against a real backend need room for real OCR and for waiting
    // out the server's 5-per-minute login throttle.
    timeout: process.env.E2E_MODE === 'live' ? 240_000 : 60_000,
    expect: { timeout: 10_000 },

    use: {
        baseURL: process.env.E2E_BASE_URL || 'http://127.0.0.1:5173',
        trace: 'retain-on-failure',
        video: 'retain-on-failure',
        screenshot: 'only-on-failure',
        actionTimeout: 15_000,
        navigationTimeout: 30_000,
        locale: 'fr-FR',
        timezoneId: 'Europe/Paris',
    },

    projects,

    // Started automatically unless E2E_BASE_URL points somewhere already running.
    // Two servers: Vite's dev server for the app suites, and a production
    // preview for the PWA suite, which has no service worker without a build.
    webServer: process.env.E2E_BASE_URL ? undefined : [
        {
            command: 'npm run dev -- --port 5173 --strictPort',
            url: 'http://127.0.0.1:5173',
            reuseExistingServer: !process.env.CI,
            timeout: 120_000,
            stdout: 'ignore',
            stderr: 'pipe',
            env: SERVER_ENV,
        },
        ...(managedPreview ? [{
            command: 'npm run build && npm run preview -- --port 4173 --strictPort',
            url: PREVIEW_URL,
            reuseExistingServer: !process.env.CI,
            timeout: 180_000,
            stdout: 'ignore',
            stderr: 'pipe',
            // Baked in at build time for the preview server, so it has to be
            // on the command that builds.
            env: SERVER_ENV,
        }] : []),
    ],
});

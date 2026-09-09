// Retires the service worker that used to be registered at the origin root.
//
// scripts/assemble-site.mjs copies this file to dist/sw.js, i.e. it is served
// at https://scanid.fr/sw.js — the exact URL the application's worker occupied
// while the application was served from the root.
//
// WHY IT HAS TO EXIST
// -------------------
// Every browser that has opened ScanID holds a registration for /sw.js with a
// scope of `/`, a precache containing the old application shell, and
// `navigateFallback: 'index.html'`. That worker answers navigations to
// scanid.fr/ from its own cache. Deleting the file would not undo any of that:
// the registration lives in the browser, not on the server, so those visitors
// would keep being served the old application shell at the address the public
// site now occupies — offline-first, indefinitely, with no error anywhere.
//
// A worker can only be replaced by another worker at the same URL. So this one
// ships, the browser picks it up on its next update check, and it takes itself
// (and every cache the old one filled) away.
//
// The application's own worker is unaffected: it is now /app/sw.js, registered
// by src/pwa.js at a scope of /app/, and nothing here touches it. Deleting
// caches by name is safe for the same reason — the new worker rebuilds its own
// precache under /app/ the next time the application is opened.
//
// Keep this file for as long as any browser might still hold the old
// registration. It costs a few hundred bytes and removing it early puts those
// visitors back in the situation it exists to fix.

self.addEventListener('install', () => {
    // Do not wait for the old worker's clients to close: the point is to take
    // over now, on this visit, not on some future one.
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil((async () => {
        // Every cache on this origin at the root scope belongs to the worker
        // being retired — Workbox's precache and nothing else. The application
        // never cached a document; see vite.config.js.
        const names = await caches.keys();
        await Promise.all(names.map(name => caches.delete(name)));

        // Unregistering is what stops this worker from intercepting anything
        // ever again. Until the page reloads, though, it is still in control.
        await self.registration.unregister();

        // So reload the pages it controls. They go to the network this time,
        // which is where the site now is.
        const clients = await self.clients.matchAll({ type: 'window' });
        for (const client of clients) {
            // navigate() is not available on every client in every browser;
            // one that refuses simply picks the site up on its next load.
            try { await client.navigate(client.url); } catch { /* next load, then */ }
        }
    })());
});

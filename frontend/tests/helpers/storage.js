// Everything the app has left on the client, in one object.
//
// Later packages use this to prove that identity-document data does not outlive
// a session, so the shape must distinguish "empty" from "the browser would not
// tell us" — a silently missing store would read as a clean device.

/**
 * @returns {Promise<{localStorage: Record<string,string>,
 *   sessionStorage: Record<string,string>, indexedDB: string[],
 *   cacheStorage: string[], serviceWorkers: string[],
 *   unavailable: string[], origin: string}>}
 *   `unavailable` lists the APIs this browser refused to enumerate (WebKit does
 *   not implement indexedDB.databases(), and Cache Storage needs a secure
 *   context). An entry there means "unknown", never "empty".
 */
export async function getStorageState(page) {
    return page.evaluate(async () => {
        const unavailable = [];

        const readWebStorage = (name) => {
            try {
                const store = window[name];
                if (!store) { unavailable.push(name); return {}; }
                const entries = {};
                for (let i = 0; i < store.length; i++) {
                    const key = store.key(i);
                    entries[key] = store.getItem(key);
                }
                return entries;
            } catch {
                unavailable.push(name); // private mode / blocked site data
                return {};
            }
        };

        let indexedDBNames = [];
        try {
            if (typeof indexedDB?.databases === 'function') {
                indexedDBNames = (await indexedDB.databases())
                    .map(db => db.name).filter(Boolean).sort();
            } else {
                unavailable.push('indexedDB.databases');
            }
        } catch {
            unavailable.push('indexedDB.databases');
        }

        let cacheKeys = [];
        try {
            if (window.caches) cacheKeys = (await caches.keys()).sort();
            else unavailable.push('caches');
        } catch {
            unavailable.push('caches');
        }

        let serviceWorkers = [];
        try {
            if (navigator.serviceWorker) {
                serviceWorkers = (await navigator.serviceWorker.getRegistrations())
                    .map(registration => registration.scope).sort();
            } else {
                unavailable.push('serviceWorker');
            }
        } catch {
            unavailable.push('serviceWorker');
        }

        return {
            origin: location.origin,
            localStorage: readWebStorage('localStorage'),
            sessionStorage: readWebStorage('sessionStorage'),
            indexedDB: indexedDBNames,
            cacheStorage: cacheKeys,
            serviceWorkers,
            unavailable,
        };
    });
}

/** True when nothing at all is stored (and every store could be read). */
export function isStorageEmpty(state) {
    return state.unavailable.length === 0
        && Object.keys(state.localStorage).length === 0
        && Object.keys(state.sessionStorage).length === 0
        && state.indexedDB.length === 0
        && state.cacheStorage.length === 0
        && state.serviceWorkers.length === 0;
}

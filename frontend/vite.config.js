import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    // --- PWA -------------------------------------------------------------
    // The service worker caches the APPLICATION SHELL and nothing else.
    //
    // The public commitment is that identity documents are never stored, so the
    // configuration is an ALLOW-LIST (globPatterns: exactly these built assets)
    // rather than a deny-list of endpoints. A deny-list fails open: add
    // /passports/exports tomorrow and it would be cached until someone
    // remembers to exclude it. `runtimeCaching` is deliberately empty — with no
    // runtime strategy registered, every request that is not a precached shell
    // asset goes straight to the network and is never written to any cache.
    VitePWA({
      // A deploy must not strand anyone on a stale shell: the new worker takes
      // over as soon as it is installed, and the outdated precaches are dropped.
      registerType: 'autoUpdate',
      // Registration is done by src/pwa.js, so the app controls when it happens.
      injectRegister: null,
      includeAssets: [],
      manifest: {
        name: 'ScanID',
        short_name: 'ScanID',
        description: "Extraction automatique des données de passeports et pièces d'identité.",
        lang: 'fr',
        dir: 'ltr',
        display: 'standalone',
        orientation: 'portrait-primary',
        background_color: '#0B1628',
        theme_color: '#0B1628',
        // The app is served from the domain root and mounts its single route
        // there (App.jsx pushes '/' on logout); '.' keeps it correct under a
        // sub-path deployment too.
        start_url: '.',
        scope: '.',
        icons: [
          { src: 'icons/icon-192.png', sizes: '192x192', type: 'image/png', purpose: 'any' },
          { src: 'icons/icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'any' },
          { src: 'icons/icon-512-maskable.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        // THE ALLOW-LIST. Only these built files are ever put in a cache.
        // The icons are not listed: the plugin already precaches every icon the
        // manifest declares, and naming them here too would add each one twice.
        globPatterns: ['**/*.{js,css,html,svg,woff2}'],
        // heic2any is a 1.3 Mo decoder needed by a minority of uploads; it is
        // fetched on demand rather than pushed to every phone at install.
        globIgnores: ['**/heic2any*', '**/*.map'],
        // Navigations fall back to the cached shell, which is what makes the
        // app open offline. Never for the API: an API path must fail as an API
        // path, not answer with a copy of index.html.
        navigateFallback: 'index.html',
        navigateFallbackDenylist: [/^\/api\//, /^\/events/],
        // NO runtime caching. Nothing here may grow a strategy that matches an
        // upload or a results response by pattern.
        runtimeCaching: [],
        cleanupOutdatedCaches: true,
        skipWaiting: true,
        clientsClaim: true,
      },
      devOptions: {
        // Off in dev: a service worker in front of Vite's HMR hides changes and
        // the shell it would cache is not the shell that ships. The PWA suite
        // runs against a real `vite preview` build instead.
        enabled: false,
      },
    }),
  ],
})

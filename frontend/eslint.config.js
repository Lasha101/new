import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  globalIgnores([
    'dist',
    // Test-harness artefacts: generated fixture binaries, vendored WebKit
    // libraries and Playwright output (see tests/README.md).
    'tests/fixtures/files',
    'tests/.browser-libs',
    'test-results',
    'playwright-report',
  ]),
  {
    files: ['**/*.{js,jsx}'],
    extends: [
      js.configs.recommended,
      reactHooks.configs['recommended-latest'],
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
      parserOptions: {
        ecmaVersion: 'latest',
        ecmaFeatures: { jsx: true },
        sourceType: 'module',
      },
    },
    rules: {
      'no-unused-vars': ['error', { varsIgnorePattern: '^[A-Z_]' }],
    },
  },
  {
    // The test harness: Node scripts and Playwright specs. They run in Node but
    // also contain page.evaluate() callbacks that execute in the browser, so
    // both global sets apply. Nothing here renders a React component.
    // `src/**/*.test.js` and `scripts/` are here for the same reason: unit
    // tests beside the module they cover run under `node --test`, and the icon
    // generator is a Node script.
    files: [
      'tests/**/*.js', 'tests/**/*.mjs', 'playwright.config.js',
      'src/**/*.test.js', 'scripts/**/*.mjs',
    ],
    languageOptions: {
      globals: { ...globals.node, ...globals.browser },
    },
    rules: {
      'react-refresh/only-export-components': 'off',
    },
  },
])



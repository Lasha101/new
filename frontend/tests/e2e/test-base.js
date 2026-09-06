// The `test` every spec imports: Playwright's, plus the mocked backend.
//
//   E2E_MODE=live   drive a real backend instead (see tests/README.md)
//
// The mock is an auto fixture, so a spec cannot forget it and accidentally hit
// the developer's own backend.
import { test as base, expect } from '@playwright/test';
import { installMockApi } from '../mock/api.js';
import { EXPECTED_ROW_COUNTS } from '../mock/data.js';

export const LIVE = process.env.E2E_MODE === 'live';

export const test = base.extend({
    /** The mock's mutable state, or null in live mode. */
    api: [async ({ context }, use) => {
        if (LIVE) { await use(null); return; }
        const state = await installMockApi(context, {
            processingMs: Number(process.env.E2E_MOCK_PROCESSING_MS || 1200),
        });
        await use(state);
    }, { auto: true }],
});

export { expect, EXPECTED_ROW_COUNTS };

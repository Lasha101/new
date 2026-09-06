#!/usr/bin/env node
// Renders the PWA icons from the existing favicon source, public/vite.svg.
//
// Run: npm run icons          (rewrites public/icons/*.png)
//
// The rasteriser is the Chromium that Playwright already installs for the E2E
// suite, so this adds no dependency. The icons are committed rather than
// generated at build time — a build must not need a browser.
//
// NOTE FOR A HUMAN: the source is Vite's scaffolding logo, not a ScanID mark.
// The repository contains no ScanID logo and one must not be invented, so these
// icons carry Vite's. Replace public/vite.svg (or point SOURCE below at a real
// logo) and rerun this script when the brand asset exists.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from '@playwright/test';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SOURCE = path.join(ROOT, 'public', 'vite.svg');
const OUT_DIR = path.join(ROOT, 'public', 'icons');

/** background_color / theme_color of the manifest. */
const BACKGROUND = '#0B1628';

const TARGETS = [
    // A plain icon may fill its square; the platform draws it as given.
    { file: 'icon-192.png', size: 192, inset: 0.14 },
    { file: 'icon-512.png', size: 512, inset: 0.14 },
    // Maskable: the platform may crop to any shape inside the square, and only
    // the middle 80% is guaranteed to survive. The mark is drawn inside a
    // circle of 80% diameter, which means 60% of the edge length.
    { file: 'icon-512-maskable.png', size: 512, inset: 0.20, maskable: true },
];

async function main() {
    const svg = fs.readFileSync(SOURCE, 'utf8');
    fs.mkdirSync(OUT_DIR, { recursive: true });

    const browser = await chromium.launch();
    try {
        for (const target of TARGETS) {
            const page = await browser.newPage({
                viewport: { width: target.size, height: target.size },
                deviceScaleFactor: 1,
            });
            const pad = Math.round(target.size * target.inset);
            await page.setContent(`<!doctype html><html><head><style>
                html, body { margin: 0; padding: 0; width: ${target.size}px; height: ${target.size}px; }
                body { background: ${BACKGROUND}; display: flex;
                       align-items: center; justify-content: center; }
                .mark { width: ${target.size - pad * 2}px; height: ${target.size - pad * 2}px;
                        display: flex; align-items: center; justify-content: center; }
                .mark svg { width: 100%; height: 100%; }
            </style></head><body><div class="mark">${svg}</div></body></html>`);
            await page.waitForLoadState('networkidle');
            const buffer = await page.screenshot({ type: 'png', omitBackground: false });
            fs.writeFileSync(path.join(OUT_DIR, target.file), buffer);
            await page.close();
            console.log(`  ${target.file.padEnd(24)} ${target.size}x${target.size}  ${buffer.length} B`
                + `${target.maskable ? '  (maskable, 80% safe zone)' : ''}`);
        }
    } finally {
        await browser.close();
    }
}

console.log(`Icons from ${path.relative(ROOT, SOURCE)} -> ${path.relative(ROOT, OUT_DIR)}/`);
await main();

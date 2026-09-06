// WebKit on Linux needs libavif.so.16 (and its own dependencies). Playwright
// bundles most system libraries but not that one, and its launcher *overwrites*
// LD_LIBRARY_PATH, so the usual trick does not work — LD_PRELOAD does.
//
// This module only inspects what is already on disk; downloading is the job of
// ensure-webkit-deps.mjs, which the pretest hooks run.
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
export const LOCAL_LIB_DIR = path.join(HERE, '..', '.browser-libs', 'lib');

/** Shared objects WebKit needs that are commonly absent from a desktop Ubuntu. */
export const REQUIRED_SONAMES = ['libavif.so.16', 'libgav1.so.1', 'libyuv.so.0'];

/** Debian/Ubuntu packages providing them, for ensure-webkit-deps.mjs. */
export const PROVIDING_PACKAGES = ['libavif16', 'libgav1-1', 'libyuv0'];

let systemLibsCache = null;

function systemLibraries() {
    if (systemLibsCache) return systemLibsCache;
    try {
        systemLibsCache = execFileSync('ldconfig', ['-p'], { encoding: 'utf8' });
    } catch {
        systemLibsCache = '';
    }
    return systemLibsCache;
}

/** Sonames the system linker cannot resolve on its own. */
export function missingSonames() {
    const installed = systemLibraries();
    return REQUIRED_SONAMES.filter(soname => !installed.includes(soname));
}

/**
 * LD_PRELOAD value for WebKit: absolute paths to the locally vendored copies of
 * whatever the system is missing. Empty string when nothing is missing (the
 * normal case on a machine with libavif16 installed) or when no local copy
 * exists — in which case WebKit will fail to launch with a clear error from
 * Playwright, which is the honest outcome.
 */
export function webkitPreload() {
    const missing = missingSonames();
    if (missing.length === 0) return '';
    return missing
        .map(soname => path.join(LOCAL_LIB_DIR, soname))
        .filter(candidate => fs.existsSync(candidate))
        .join(' ');
}

/** Environment for the WebKit project, or `undefined` when none is needed. */
export function webkitLaunchEnv() {
    const preload = webkitPreload();
    if (!preload) return undefined;
    return {
        ...process.env,
        LD_PRELOAD: [process.env.LD_PRELOAD, preload].filter(Boolean).join(' '),
    };
}

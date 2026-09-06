#!/usr/bin/env node
// Makes WebKit launchable without touching the system.
//
// Playwright's WebKit build needs libavif.so.16, which Ubuntu 24.04 does not
// install by default. Rather than requiring `sudo apt-get install`, this
// downloads the .deb files into tests/.browser-libs/ (no root needed) and
// extracts the shared objects there; webkit-preload.js then LD_PRELOADs them.
//
// A no-op when the libraries are already installed system-wide, which is the
// case on the GitHub Actions ubuntu runners after `playwright install --with-deps`.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { execFileSync } from 'node:child_process';

import { LOCAL_LIB_DIR, PROVIDING_PACKAGES, missingSonames, webkitPreload } from './webkit-preload.js';

const CACHE_DIR = path.join(LOCAL_LIB_DIR, '..', 'deb');

function run(command, args, options = {}) {
    return execFileSync(command, args, { encoding: 'utf8', stdio: 'pipe', ...options });
}

function have(command) {
    try { run('sh', ['-c', `command -v ${command}`]); return true; } catch { return false; }
}

function main() {
    if (os.platform() !== 'linux') {
        console.log('WebKit dependencies: nothing to do on this platform.');
        return 0;
    }

    const missing = missingSonames();
    if (missing.length === 0) {
        console.log('WebKit dependencies: all present system-wide.');
        return 0;
    }

    if (webkitPreload().split(' ').filter(Boolean).length === missing.length) {
        console.log(`WebKit dependencies: using local copies in ${LOCAL_LIB_DIR}`);
        return 0;
    }

    console.log(`WebKit dependencies missing from the system: ${missing.join(', ')}`);

    if (!have('apt-get') || !have('dpkg-deb')) {
        console.error(
            'Cannot fetch them automatically (apt-get/dpkg-deb unavailable).\n'
            + `Install the libraries with your package manager (Debian/Ubuntu: sudo apt-get install ${PROVIDING_PACKAGES.join(' ')}),\n`
            + 'or run without the WebKit project: E2E_SKIP_WEBKIT=1 npm run test:e2e',
        );
        return 1;
    }

    fs.mkdirSync(CACHE_DIR, { recursive: true });
    fs.mkdirSync(LOCAL_LIB_DIR, { recursive: true });

    try {
        console.log(`Downloading ${PROVIDING_PACKAGES.join(', ')} into ${CACHE_DIR} (no root required)…`);
        run('apt-get', ['download', ...PROVIDING_PACKAGES], { cwd: CACHE_DIR });
    } catch (error) {
        console.error(`apt-get download failed: ${error.stderr || error.message}`);
        console.error(`Install them manually instead: sudo apt-get install ${PROVIDING_PACKAGES.join(' ')}`);
        return 1;
    }

    const extractDir = path.join(CACHE_DIR, 'extracted');
    fs.rmSync(extractDir, { recursive: true, force: true });
    for (const file of fs.readdirSync(CACHE_DIR).filter(name => name.endsWith('.deb'))) {
        run('dpkg-deb', ['-x', path.join(CACHE_DIR, file), extractDir]);
    }

    // Flatten every shared object into one directory so LD_PRELOAD paths are simple.
    let copied = 0;
    const walk = (dir) => {
        for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
            const full = path.join(dir, entry.name);
            if (entry.isDirectory()) { walk(full); continue; }
            if (entry.isSymbolicLink() || /\.so(\.\d+)*$/.test(entry.name)) {
                const target = path.join(LOCAL_LIB_DIR, entry.name);
                fs.copyFileSync(full, target); // resolves symlinks, giving real files
                copied += 1;
            }
        }
    };
    walk(extractDir);

    const stillMissing = missingSonames()
        .filter(soname => !fs.existsSync(path.join(LOCAL_LIB_DIR, soname)));
    if (stillMissing.length > 0) {
        console.error(`Still missing after extraction: ${stillMissing.join(', ')}`);
        return 1;
    }

    console.log(`WebKit dependencies: ${copied} file(s) vendored into ${LOCAL_LIB_DIR}`);
    return 0;
}

process.exit(main());

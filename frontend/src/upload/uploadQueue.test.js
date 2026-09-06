// The batch queue: retry policy, per-document status, and "retry failed".
//
// The queue is framework-free precisely so this can run under `node --test`
// with a stubbed transport, instead of waiting on real backoff in a browser.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

import {
    UploadQueue, RetriableUploadError, QUEUE_STATUS, QUEUE_STATUS_CHIP,
    QUEUE_STATUS_LABEL, resetQueueIds,
} from './uploadQueue.js';

/** Stand-in for a File; the queue only reads `name` and `size`. */
const fakeFile = (name, size = 1024) => ({ name, size });

/** A queue whose sleeps are recorded instead of waited on. */
function makeQueue(upload, options = {}) {
    const slept = [];
    const queue = new UploadQueue({
        upload,
        retryDelays: [10, 30],
        sleep: (ms) => { slept.push(ms); return Promise.resolve(); },
        ...options,
    });
    return { queue, slept };
}

test('every status maps to a design-system chip and a French label', () => {
    for (const status of Object.values(QUEUE_STATUS)) {
        assert.ok(QUEUE_STATUS_CHIP[status], `no chip for ${status}`);
        assert.ok(QUEUE_STATUS_LABEL[status], `no label for ${status}`);
        // The label must not be English; it is rendered to the user.
        assert.match(QUEUE_STATUS_LABEL[status], /^[A-ZÉÈÊÀÂÎÔÛÇ]/);
    }
});

test('a clean batch: every document ends processing, in order, one request each', async () => {
    resetQueueIds();
    const sent = [];
    const { queue } = makeQueue(async (item) => {
        sent.push(item.name);
        return { jobId: `job-${item.name}` };
    });
    queue.enqueue([fakeFile('a.jpg'), fakeFile('b.jpg'), fakeFile('c.jpg')]);
    await queue.run();

    assert.deepEqual(sent, ['a.jpg', 'b.jpg', 'c.jpg']);
    assert.deepEqual(queue.snapshot().map(item => item.status),
        [QUEUE_STATUS.processing, QUEUE_STATUS.processing, QUEUE_STATUS.processing]);
    assert.deepEqual(queue.snapshot().map(item => item.jobId),
        ['job-a.jpg', 'job-b.jpg', 'job-c.jpg']);
    assert.deepEqual(queue.snapshot().map(item => item.attempts), [1, 1, 1]);
});

test('a network error is retried twice, with an increasing delay, then fails', async () => {
    let attempts = 0;
    const { queue, slept } = makeQueue(async () => {
        attempts++;
        throw new RetriableUploadError('Connexion perdue.');
    });
    queue.enqueue([fakeFile('a.jpg')]);
    await queue.run();

    assert.equal(attempts, 3, 'first send plus two retries');
    assert.deepEqual(slept, [10, 30]);
    assert.ok(slept[1] > slept[0], 'the second delay must be longer than the first');
    const [item] = queue.snapshot();
    assert.equal(item.status, QUEUE_STATUS.failed);
    assert.equal(item.attempts, 3);
    assert.equal(item.error, 'Connexion perdue.');
});

test('a retry that succeeds leaves the document processing, not failed', async () => {
    let attempts = 0;
    const { queue, slept } = makeQueue(async () => {
        attempts++;
        if (attempts === 1) throw new RetriableUploadError('Connexion perdue.');
        return { jobId: 'job-1' };
    });
    queue.enqueue([fakeFile('a.jpg')]);
    await queue.run();

    assert.equal(attempts, 2);
    assert.deepEqual(slept, [10]);
    assert.equal(queue.snapshot()[0].status, QUEUE_STATUS.processing);
    assert.equal(queue.snapshot()[0].error, '');
});

test('an HTTP rejection is NOT retried — it would spend a credit for nothing', async () => {
    let attempts = 0;
    const { queue, slept } = makeQueue(async () => {
        attempts++;
        throw new Error("Crédits insuffisants. Veuillez contacter l'administrateur.");
    });
    queue.enqueue([fakeFile('a.jpg')]);
    await queue.run();

    assert.equal(attempts, 1);
    assert.deepEqual(slept, []);
    assert.equal(queue.snapshot()[0].status, QUEUE_STATUS.failed);
    assert.equal(queue.snapshot()[0].error, "Crédits insuffisants. Veuillez contacter l'administrateur.");
});

test('a mixed batch: the failure does not stop or disturb the successes', async () => {
    const { queue } = makeQueue(async (item) => {
        if (item.name === 'b.jpg') throw new RetriableUploadError('Connexion perdue.');
        return { jobId: `job-${item.name}` };
    });
    queue.enqueue([fakeFile('a.jpg'), fakeFile('b.jpg'), fakeFile('c.jpg')]);
    await queue.run();

    const byName = Object.fromEntries(queue.snapshot().map(item => [item.name, item]));
    assert.equal(byName['a.jpg'].status, QUEUE_STATUS.processing);
    assert.equal(byName['b.jpg'].status, QUEUE_STATUS.failed);
    assert.equal(byName['c.jpg'].status, QUEUE_STATUS.processing);
    assert.equal(byName['c.jpg'].jobId, 'job-c.jpg', 'the batch continued past the failure');
});

test('retryFailed re-attempts only the failed documents', async () => {
    let failNext = true;
    const sent = [];
    const { queue } = makeQueue(async (item) => {
        sent.push(item.name);
        if (item.name === 'b.jpg' && failNext) throw new RetriableUploadError('Connexion perdue.');
        return { jobId: `job-${item.name}` };
    });
    queue.enqueue([fakeFile('a.jpg'), fakeFile('b.jpg'), fakeFile('c.jpg')]);
    await queue.run();
    assert.deepEqual(sent, ['a.jpg', 'b.jpg', 'b.jpg', 'b.jpg', 'c.jpg']);

    failNext = false;
    sent.length = 0;
    queue.retryFailed();
    await queue.run();

    assert.deepEqual(sent, ['b.jpg'], 'only the failed document is sent again');
    assert.deepEqual(queue.snapshot().map(item => item.status),
        [QUEUE_STATUS.processing, QUEUE_STATUS.processing, QUEUE_STATUS.processing]);
});

test('retryFailed on a queue with nothing failed does nothing', async () => {
    const sent = [];
    const { queue } = makeQueue(async (item) => { sent.push(item.name); return { jobId: 'j' }; });
    queue.enqueue([fakeFile('a.jpg')]);
    await queue.run();
    assert.deepEqual(queue.retryFailed(), []);
    assert.deepEqual(sent, ['a.jpg']);
});

test('progress reported by the transport reaches the item', async () => {
    const seen = [];
    const { queue } = makeQueue(async (item, ctx) => {
        ctx.onProgress(25);
        ctx.onProgress(80);
        return { jobId: 'j' };
    });
    queue.subscribe(items => seen.push(items[0].progress));
    queue.enqueue([fakeFile('a.jpg')]);
    await queue.run();
    assert.ok(seen.includes(25) && seen.includes(80), `progress values seen: ${seen}`);
    assert.equal(queue.snapshot()[0].progress, 100);
});

test('applyJobStatuses moves processing -> done, and a failed job -> failed', async () => {
    const { queue } = makeQueue(async item => ({ jobId: `job-${item.name}` }));
    queue.enqueue([fakeFile('a.jpg'), fakeFile('b.jpg')]);
    await queue.run();

    assert.equal(queue.applyJobStatuses({ 'job-a.jpg': 'processing' }), false);
    assert.equal(queue.applyJobStatuses({ 'job-a.jpg': 'complete', 'job-b.jpg': 'failed' }), true);

    const byName = Object.fromEntries(queue.snapshot().map(item => [item.name, item]));
    assert.equal(byName['a.jpg'].status, QUEUE_STATUS.done);
    assert.equal(byName['b.jpg'].status, QUEUE_STATUS.failed);
    assert.equal(byName['b.jpg'].error, "L'extraction a échoué.");
});

test('a done document is never sent again by retryFailed', async () => {
    const sent = [];
    const { queue } = makeQueue(async (item) => {
        sent.push(item.name);
        if (item.name === 'b.jpg') throw new RetriableUploadError('Connexion perdue.');
        return { jobId: `job-${item.name}` };
    });
    queue.enqueue([fakeFile('a.jpg'), fakeFile('b.jpg')]);
    await queue.run();
    queue.applyJobStatuses({ 'job-a.jpg': 'complete' });
    sent.length = 0;

    queue.retryFailed();
    await queue.run();
    // b is attempted afresh (and fails afresh); a, already done, is not touched.
    assert.deepEqual(new Set(sent), new Set(['b.jpg']));
    assert.equal(queue.snapshot().find(item => item.name === 'a.jpg').status, QUEUE_STATUS.done);
});

test('subscribers are notified and can unsubscribe', async () => {
    const { queue } = makeQueue(async () => ({ jobId: 'j' }));
    let calls = 0;
    const unsubscribe = queue.subscribe(() => { calls++; });
    queue.enqueue([fakeFile('a.jpg')]);
    assert.ok(calls > 0);
    const afterEnqueue = calls;
    unsubscribe();
    await queue.run();
    assert.equal(calls, afterEnqueue, 'no notification after unsubscribe');
});

test('clear empties the queue and stops the drain', async () => {
    const { queue } = makeQueue(async () => ({ jobId: 'j' }));
    queue.enqueue([fakeFile('a.jpg'), fakeFile('b.jpg')]);
    queue.clear();
    assert.deepEqual(queue.snapshot(), []);
});

test('nothing in the queue is ever handed to a storage API', () => {
    // A structural check: the module must not reference persistent storage.
    // The queue holds identity documents; a queue that survived a reload would
    // be a queue of identity documents on disk.
    const text = fs.readFileSync(new URL('./uploadQueue.js', import.meta.url), 'utf8');
    for (const api of ['localStorage', 'sessionStorage', 'indexedDB', 'caches.open']) {
        assert.ok(!text.includes(`${api}.`) && !text.includes(`${api}[`),
            `uploadQueue.js references ${api}`);
    }
});

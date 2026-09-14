// The batch upload queue: framework-free, so `node --test` drives it directly.
//
// One document per request — the API contract is unchanged, a POST still
// carries exactly one file. What is new is that several files can be selected
// at once, each gets its own progress and status, a network failure is retried
// with a growing delay instead of surfacing as an alert, and the ones that end
// up failed can be re-attempted without touching the ones that succeeded.
//
// Privacy: items hold a File reference and a name, in memory, for as long as
// the component that owns the queue is mounted. Nothing is written to
// localStorage, sessionStorage, IndexedDB or the Cache API — a queue that
// survived a reload would be a queue of identity documents on disk.

/** The five states a document passes through. */
export const QUEUE_STATUS = {
    queued: 'queued',
    uploading: 'uploading',
    processing: 'processing',
    done: 'done',
    failed: 'failed',
};

/** French labels shown in the queue list. */
export const QUEUE_STATUS_LABEL = {
    queued: 'En attente',
    uploading: 'Envoi en cours',
    processing: 'Traitement',
    done: 'Terminé',
    failed: 'Échoué',
};

/** Design-system chip modifier for each state (.sid-chip--*, scanid-app.css). */
export const QUEUE_STATUS_CHIP = {
    queued: 'queued',
    uploading: 'processing',
    processing: 'processing',
    done: 'done',
    failed: 'failed',
};

/** Attempts per document, first try included. Two retries after the first send. */
export const MAX_ATTEMPTS = 3;

/** Delay before retry n. Increasing, so a blip and an outage are told apart. */
export const RETRY_DELAYS_MS = [1000, 3000];

const defaultSleep = ms => new Promise(resolve => setTimeout(resolve, ms));

/**
 * An error the queue is allowed to retry.
 *
 * Only transport failures qualify. An HTTP answer — « Crédits insuffisants »,
 * a rejected file — is the server's decision and repeating it would burn the
 * user's credits without changing the outcome.
 */
export class RetriableUploadError extends Error {
    constructor(message) {
        super(message);
        this.name = 'RetriableUploadError';
        this.retriable = true;
    }
}

let sequence = 0;
const nextId = () => `q${++sequence}`;

/** Test seam: makes ids predictable across runs. */
export function resetQueueIds() { sequence = 0; }

export class UploadQueue {
    /**
     * @param {{upload:(item:object, ctx:{onProgress:(p:number)=>void})=>Promise<{jobId?:string}|void>,
     *          maxAttempts?:number, retryDelays?:number[], sleep?:(ms:number)=>Promise<void>,
     *          onItemFailed?:(item:object)=>void, onBatchSettled?:(items:object[])=>void}} options
     */
    constructor({
        upload,
        maxAttempts = MAX_ATTEMPTS,
        retryDelays = RETRY_DELAYS_MS,
        sleep = defaultSleep,
        onItemFailed = () => {},
        onBatchSettled = () => {},
    }) {
        this.upload = upload;
        this.maxAttempts = maxAttempts;
        this.retryDelays = retryDelays;
        this.sleep = sleep;
        this.onItemFailed = onItemFailed;
        this.onBatchSettled = onBatchSettled;
        this.items = [];
        this.listeners = new Set();
        this.running = false;
        this.cancelled = false;
    }

    subscribe(listener) {
        this.listeners.add(listener);
        return () => this.listeners.delete(listener);
    }

    notify() {
        // A fresh array each time, so React sees a new reference.
        const snapshot = this.items.map(item => ({ ...item }));
        this.listeners.forEach(listener => listener(snapshot));
    }

    /** @returns {object[]} a copy; callers must never mutate queue state. */
    snapshot() { return this.items.map(item => ({ ...item })); }

    /** Adds files as `queued`. Returns the ids, in the order given. */
    enqueue(files) {
        const added = Array.from(files).map(file => ({
            id: nextId(),
            file,
            name: file.name,
            size: file.size,
            status: QUEUE_STATUS.queued,
            progress: 0,
            attempts: 0,
            error: '',
            jobId: null,
        }));
        this.items = [...this.items, ...added];
        this.notify();
        return added.map(item => item.id);
    }

    patch(id, changes) {
        this.items = this.items.map(item => (item.id === id ? { ...item, ...changes } : item));
        this.notify();
    }

    /** Everything not yet in a terminal state. */
    get pending() {
        return this.items.filter(item => item.status === QUEUE_STATUS.queued
            || item.status === QUEUE_STATUS.uploading);
    }

    hasFailed() { return this.items.some(item => item.status === QUEUE_STATUS.failed); }

    /**
     * Drains the queue, one document at a time.
     *
     * Sequential on purpose: the backend charges a credit per extracted
     * document and runs the OCR in-process, so three parallel uploads would
     * only queue behind each other server-side while tripling the phone's
     * memory use.
     */
    async run() {
        if (this.running) return;
        this.running = true;
        this.cancelled = false;
        try {
            for (;;) {
                const next = this.items.find(item => item.status === QUEUE_STATUS.queued);
                if (!next || this.cancelled) break;
                await this.sendWithRetries(next.id);
            }
        } finally {
            this.running = false;
            this.onBatchSettled(this.snapshot());
        }
    }

    async sendWithRetries(id) {
        for (let attempt = 1; attempt <= this.maxAttempts; attempt++) {
            if (this.cancelled) return;
            this.patch(id, { status: QUEUE_STATUS.uploading, progress: 0, attempts: attempt, error: '' });
            const item = this.items.find(candidate => candidate.id === id);
            if (!item) return;
            try {
                const outcome = await this.upload(item, {
                    onProgress: progress => this.patch(id, { progress }),
                });
                this.patch(id, {
                    status: QUEUE_STATUS.processing,
                    progress: 100,
                    jobId: outcome?.jobId ?? null,
                    error: '',
                });
                return;
            } catch (error) {
                if (this.cancelled) { this.patch(id, { status: QUEUE_STATUS.queued, progress: 0 }); return; }
                const canRetry = error?.retriable === true && attempt < this.maxAttempts;
                if (!canRetry) {
                    this.patch(id, {
                        status: QUEUE_STATUS.failed,
                        progress: 0,
                        error: error?.message || 'Échec du transfert.',
                    });
                    this.onItemFailed(this.items.find(candidate => candidate.id === id));
                    return;
                }
                const delay = this.retryDelays[Math.min(attempt - 1, this.retryDelays.length - 1)];
                this.patch(id, {
                    status: QUEUE_STATUS.queued,
                    progress: 0,
                    error: `Nouvelle tentative dans ${Math.round(delay / 1000)} s…`,
                });
                await this.sleep(delay);
            }
        }
    }

    /**
     * Re-queues only the failed documents. The ones that went through keep
     * their `processing`/`done` state and are not sent again — a second POST
     * would create a second job and spend a second credit.
     *
     * Requeues but does not drain: the caller calls `run()`, so a test can
     * await the drain rather than race it.
     */
    retryFailed() {
        const failed = this.items.filter(item => item.status === QUEUE_STATUS.failed);
        if (failed.length === 0) return [];
        this.items = this.items.map(item => (item.status === QUEUE_STATUS.failed
            ? { ...item, status: QUEUE_STATUS.queued, attempts: 0, progress: 0, error: '' }
            : item));
        this.notify();
        return failed.map(item => item.id);
    }

    /**
     * Folds the job monitor's view of the server-side jobs back into the queue,
     * so a document reaches `done` when its OCR job actually finished rather
     * than when its bytes left the phone.
     *
     * @param {Record<string,string>} statusByJobId job.id -> 'processing' | 'complete' | 'failed'
     */
    applyJobStatuses(statusByJobId) {
        let changed = false;
        this.items = this.items.map((item) => {
            if (item.status !== QUEUE_STATUS.processing || !item.jobId) return item;
            const jobStatus = statusByJobId[item.jobId];
            if (jobStatus === 'complete') { changed = true; return { ...item, status: QUEUE_STATUS.done }; }
            if (jobStatus === 'failed') {
                changed = true;
                return { ...item, status: QUEUE_STATUS.failed, error: "L'extraction a échoué." };
            }
            return item;
        });
        if (changed) this.notify();
        return changed;
    }

    /** Stops the drain and empties the list. Used on reset and on unmount. */
    clear() {
        this.cancelled = true;
        this.items = [];
        this.notify();
    }
}

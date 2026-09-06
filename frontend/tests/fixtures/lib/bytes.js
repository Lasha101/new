// Byte-level helpers shared by the fixture encoders (PNG chunks, ZIP entries).
// Kept dependency-free so `node --test` can run them without a build step.

const CRC_TABLE = (() => {
    const table = new Int32Array(256);
    for (let n = 0; n < 256; n++) {
        let c = n;
        for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
        table[n] = c;
    }
    return table;
})();

/** CRC-32 (IEEE 802.3), as used by PNG chunks and ZIP local file headers. */
export function crc32(buffer) {
    let c = -1;
    for (let i = 0; i < buffer.length; i++) c = CRC_TABLE[(c ^ buffer[i]) & 0xff] ^ (c >>> 8);
    return (c ^ -1) >>> 0;
}

/** A deterministic pseudo-random source: the fixtures must be byte-identical
    on every machine, so Math.random() is never used. */
export function seededRandom(seed = 0x2f6e2b1) {
    let state = seed >>> 0;
    return () => {
        state ^= state << 13; state >>>= 0;
        state ^= state >>> 17;
        state ^= state << 5; state >>>= 0;
        return state / 0x100000000;
    };
}

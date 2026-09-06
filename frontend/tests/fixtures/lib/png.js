// Minimal PNG writer (truecolour, 8 bits per channel). Node's zlib supplies the
// only compression needed, so the fixtures require no image library.
import zlib from 'node:zlib';
import { crc32 } from './bytes.js';

function chunk(type, payload) {
    const head = Buffer.alloc(8);
    head.writeUInt32BE(payload.length, 0);
    head.write(type, 4, 'ascii');
    const crcInput = Buffer.concat([head.subarray(4), payload]);
    const tail = Buffer.alloc(4);
    tail.writeUInt32BE(crc32(crcInput), 0);
    return Buffer.concat([head, payload, tail]);
}

/**
 * @param {number} width
 * @param {number} height
 * @param {(x:number,y:number)=>[number,number,number]} pixel RGB in 0-255
 */
export function encodePng(width, height, pixel) {
    const ihdr = Buffer.alloc(13);
    ihdr.writeUInt32BE(width, 0);
    ihdr.writeUInt32BE(height, 4);
    ihdr[8] = 8;  // bit depth
    ihdr[9] = 2;  // colour type: truecolour (RGB)
    ihdr[10] = 0; // deflate
    ihdr[11] = 0; // adaptive filtering
    ihdr[12] = 0; // no interlace

    // One filter byte (0 = None) per scanline, then RGB triples.
    const raw = Buffer.alloc(height * (1 + width * 3));
    let offset = 0;
    for (let y = 0; y < height; y++) {
        raw[offset++] = 0;
        for (let x = 0; x < width; x++) {
            const [r, g, b] = pixel(x, y);
            raw[offset++] = r; raw[offset++] = g; raw[offset++] = b;
        }
    }

    return Buffer.concat([
        Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
        chunk('IHDR', ihdr),
        chunk('IDAT', zlib.deflateSync(raw, { level: 9 })),
        chunk('IEND', Buffer.alloc(0)),
    ]);
}

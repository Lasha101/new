// Unit tests for the contrast helper. The reference ratios come from the WCAG
// 2.1 definition of relative luminance and were cross-checked against published
// values; they are hard-coded here so a refactor cannot quietly shift them.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
    parseColor, compositeOver, relativeLuminance, contrastRatio, isLargeText, wcagAAThreshold,
} from './color.js';

const close = (actual, expected, tolerance = 0.0005) =>
    assert.ok(Math.abs(actual - expected) <= tolerance,
        `expected ${expected} ± ${tolerance}, got ${actual}`);

test('the anchor case: white on black is exactly 21', () => {
    assert.equal(contrastRatio('#ffffff', '#000000'), 21);
    assert.equal(contrastRatio('white', 'black'), 21);
    assert.equal(contrastRatio('rgb(255, 255, 255)', 'rgb(0, 0, 0)'), 21);
    assert.equal(contrastRatio('#fff', '#000'), 21);
});

test('the ratio is symmetric and never below 1', () => {
    assert.equal(contrastRatio('#000000', '#ffffff'), 21);
    assert.equal(contrastRatio('#767676', '#767676'), 1);
    assert.equal(contrastRatio('#4f46e5', '#4f46e5'), 1);
});

test('known WCAG reference pairs', () => {
    close(contrastRatio('#767676', '#ffffff'), 4.5422);   // the classic AA-on-white grey
    close(contrastRatio('#949494', '#ffffff'), 3.0335);   // AA large text on white
    close(contrastRatio('#ffffff', '#767676'), 4.5422);   // symmetric
    close(contrastRatio('#0000ff', '#ffffff'), 8.5925);   // blue on white
    close(contrastRatio('#ff0000', '#ffffff'), 3.9985);  // red on white
    close(contrastRatio('#008000', '#ffffff'), 5.1374);   // green on white
    close(contrastRatio('#ffff00', '#000000'), 19.5560);  // yellow on black
});

test("the app's own palette, so a later package has a baseline", () => {
    // Values read from GlobalStyles in src/App.jsx, ratios computed independently.
    close(contrastRatio('#4f46e5', '#ffffff'), 6.2875);   // --primary-color on --surface-color
    close(contrastRatio('#1f2937', '#f3f4f6'), 13.3384);  // --text-color on --background-color
    close(contrastRatio('#6b7280', '#ffffff'), 4.8345);   // --secondary-color on white
    close(contrastRatio('#ffffff', '#4f46e5'), 6.2875);   // white label on a primary button
});

test('relative luminance endpoints', () => {
    assert.equal(relativeLuminance({ r: 0, g: 0, b: 0 }), 0);
    assert.equal(relativeLuminance({ r: 255, g: 255, b: 255 }), 1);
    close(relativeLuminance({ r: 128, g: 128, b: 128 }), 0.215861, 0.000001);
});

test('parseColor accepts every shape getComputedStyle can return', () => {
    assert.deepEqual(parseColor('#ff8800'), { r: 255, g: 136, b: 0, a: 1 });
    assert.deepEqual(parseColor('#f80'), { r: 255, g: 136, b: 0, a: 1 });
    assert.deepEqual(parseColor('rgb(255, 136, 0)'), { r: 255, g: 136, b: 0, a: 1 });
    assert.deepEqual(parseColor('rgba(255, 136, 0, 0.5)'), { r: 255, g: 136, b: 0, a: 0.5 });
    assert.deepEqual(parseColor('rgb(255 136 0 / 0.5)'), { r: 255, g: 136, b: 0, a: 0.5 });
    assert.deepEqual(parseColor('  RGB(255,136,0)  '), { r: 255, g: 136, b: 0, a: 1 });
    assert.deepEqual(parseColor('transparent'), { r: 0, g: 0, b: 0, a: 0 });
    assert.deepEqual(parseColor('rebeccapurple'), { r: 102, g: 51, b: 153, a: 1 });
    assert.deepEqual(parseColor('#ff880080'), { r: 255, g: 136, b: 0, a: 128 / 255 });
});

test('parseColor refuses to guess', () => {
    assert.throws(() => parseColor('chartreuseish'), /unsupported colour/);
    assert.throws(() => parseColor('#12345'), /malformed hex/);
    assert.throws(() => parseColor(''), /empty colour/);
    assert.throws(() => parseColor(null), /empty colour/);
});

test('translucent colours are composited before comparison', () => {
    // 50% black over white is mid-grey, whatever order the caller passes.
    close(contrastRatio('rgba(0, 0, 0, 0.5)', '#ffffff'),
        contrastRatio('rgb(128, 128, 128)', '#ffffff'), 0.05);
    // A fully transparent foreground disappears into its background: ratio 1.
    assert.equal(contrastRatio('rgba(0, 0, 0, 0)', '#ffffff'), 1);
    // A translucent background is resolved against white, not left undefined.
    assert.ok(Number.isFinite(contrastRatio('#000000', 'rgba(255, 255, 255, 0.85)')));
});

test('compositeOver leaves opaque colours untouched', () => {
    assert.deepEqual(
        compositeOver({ r: 10, g: 20, b: 30, a: 1 }, { r: 255, g: 255, b: 255, a: 1 }),
        { r: 10, g: 20, b: 30, a: 1 },
    );
});

test('WCAG large-text thresholds', () => {
    assert.equal(isLargeText(24, 400), true);
    assert.equal(isLargeText(23.9, 400), false);
    assert.equal(isLargeText(19, 700), true);
    assert.equal(isLargeText(19, 600), false);
    assert.equal(wcagAAThreshold(16, 400), 4.5);
    assert.equal(wcagAAThreshold(30, 400), 3);
});

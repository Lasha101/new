// Colour helpers for contrast assertions.
//
// contrastRatio() is a from-scratch implementation of the WCAG 2.x relative
// luminance formula (https://www.w3.org/TR/WCAG21/#dfn-relative-luminance), unit
// tested against known pairs in color.test.js — white on black must return 21.
// It is pure: no browser needed, so later packages can assert on palette values
// as well as on rendered pages.

const NAMED_COLORS = Object.fromEntries(
    ('aliceblue f0f8ff,antiquewhite faebd7,aqua 00ffff,aquamarine 7fffd4,azure f0ffff,beige f5f5dc,'
    + 'bisque ffe4c4,black 000000,blanchedalmond ffebcd,blue 0000ff,blueviolet 8a2be2,brown a52a2a,'
    + 'burlywood deb887,cadetblue 5f9ea0,chartreuse 7fff00,chocolate d2691e,coral ff7f50,'
    + 'cornflowerblue 6495ed,cornsilk fff8dc,crimson dc143c,cyan 00ffff,darkblue 00008b,darkcyan 008b8b,'
    + 'darkgoldenrod b8860b,darkgray a9a9a9,darkgreen 006400,darkgrey a9a9a9,darkkhaki bdb76b,'
    + 'darkmagenta 8b008b,darkolivegreen 556b2f,darkorange ff8c00,darkorchid 9932cc,darkred 8b0000,'
    + 'darksalmon e9967a,darkseagreen 8fbc8f,darkslateblue 483d8b,darkslategray 2f4f4f,'
    + 'darkslategrey 2f4f4f,darkturquoise 00ced1,darkviolet 9400d3,deeppink ff1493,deepskyblue 00bfff,'
    + 'dimgray 696969,dimgrey 696969,dodgerblue 1e90ff,firebrick b22222,floralwhite fffaf0,'
    + 'forestgreen 228b22,fuchsia ff00ff,gainsboro dcdcdc,ghostwhite f8f8ff,gold ffd700,'
    + 'goldenrod daa520,gray 808080,green 008000,greenyellow adff2f,grey 808080,honeydew f0fff0,'
    + 'hotpink ff69b4,indianred cd5c5c,indigo 4b0082,ivory fffff0,khaki f0e68c,lavender e6e6fa,'
    + 'lavenderblush fff0f5,lawngreen 7cfc00,lemonchiffon fffacd,lightblue add8e6,lightcoral f08080,'
    + 'lightcyan e0ffff,lightgoldenrodyellow fafad2,lightgray d3d3d3,lightgreen 90ee90,lightgrey d3d3d3,'
    + 'lightpink ffb6c1,lightsalmon ffa07a,lightseagreen 20b2aa,lightskyblue 87cefa,lightslategray 778899,'
    + 'lightslategrey 778899,lightsteelblue b0c4de,lightyellow ffffe0,lime 00ff00,limegreen 32cd32,'
    + 'linen faf0e6,magenta ff00ff,maroon 800000,mediumaquamarine 66cdaa,mediumblue 0000cd,'
    + 'mediumorchid ba55d3,mediumpurple 9370db,mediumseagreen 3cb371,mediumslateblue 7b68ee,'
    + 'mediumspringgreen 00fa9a,mediumturquoise 48d1cc,mediumvioletred c71585,midnightblue 191970,'
    + 'mintcream f5fffa,mistyrose ffe4e1,moccasin ffe4b5,navajowhite ffdead,navy 000080,oldlace fdf5e6,'
    + 'olive 808000,olivedrab 6b8e23,orange ffa500,orangered ff4500,orchid da70d6,palegoldenrod eee8aa,'
    + 'palegreen 98fb98,paleturquoise afeeee,palevioletred db7093,papayawhip ffefd5,peachpuff ffdab9,'
    + 'peru cd853f,pink ffc0cb,plum dda0dd,powderblue b0e0e6,purple 800080,rebeccapurple 663399,'
    + 'red ff0000,rosybrown bc8f8f,royalblue 4169e1,saddlebrown 8b4513,salmon fa8072,sandybrown f4a460,'
    + 'seagreen 2e8b57,seashell fff5ee,sienna a0522d,silver c0c0c0,skyblue 87ceeb,slateblue 6a5acd,'
    + 'slategray 708090,slategrey 708090,snow fffafa,springgreen 00ff7f,steelblue 4682b4,tan d2b48c,'
    + 'teal 008080,thistle d8bfd8,tomato ff6347,turquoise 40e0d0,violet ee82ee,wheat f5deb3,'
    + 'white ffffff,whitesmoke f5f5f5,yellow ffff00,yellowgreen 9acd32')
        .split(',').map(entry => entry.split(' ')),
);

/**
 * Parses a CSS colour into { r, g, b, a } with channels in 0-255 and alpha 0-1.
 * Accepts what getComputedStyle actually returns (rgb()/rgba(), both the comma
 * and the space syntax) plus hex, CSS named colours and `transparent`.
 * Throws on anything else rather than guessing — a silently wrong contrast
 * number is worse than a failing test.
 */
export function parseColor(value) {
    if (value && typeof value === 'object' && 'r' in value) {
        return { r: value.r, g: value.g, b: value.b, a: value.a ?? 1 };
    }
    const input = String(value ?? '').trim().toLowerCase();
    if (!input) throw new Error('parseColor: empty colour value');
    if (input === 'transparent') return { r: 0, g: 0, b: 0, a: 0 };

    const named = NAMED_COLORS[input];
    if (named) return parseColor(`#${named}`);

    if (input.startsWith('#')) {
        const hex = input.slice(1);
        const expand = part => parseInt(part.length === 1 ? part + part : part, 16);
        if (hex.length === 3 || hex.length === 4) {
            return {
                r: expand(hex[0]), g: expand(hex[1]), b: expand(hex[2]),
                a: hex.length === 4 ? expand(hex[3]) / 255 : 1,
            };
        }
        if (hex.length === 6 || hex.length === 8) {
            return {
                r: parseInt(hex.slice(0, 2), 16), g: parseInt(hex.slice(2, 4), 16),
                b: parseInt(hex.slice(4, 6), 16),
                a: hex.length === 8 ? parseInt(hex.slice(6, 8), 16) / 255 : 1,
            };
        }
        throw new Error(`parseColor: malformed hex colour "${value}"`);
    }

    const functional = input.match(/^rgba?\(([^)]+)\)$/);
    if (functional) {
        const parts = functional[1].replace(/\//g, ' ').split(/[\s,]+/).filter(Boolean);
        if (parts.length < 3) throw new Error(`parseColor: malformed colour "${value}"`);
        const channel = part => (part.endsWith('%')
            ? (parseFloat(part) / 100) * 255
            : parseFloat(part));
        const alpha = parts[3] === undefined
            ? 1
            : (parts[3].endsWith('%') ? parseFloat(parts[3]) / 100 : parseFloat(parts[3]));
        return { r: channel(parts[0]), g: channel(parts[1]), b: channel(parts[2]), a: alpha };
    }

    throw new Error(`parseColor: unsupported colour "${value}". `
        + 'Supported: hex, rgb()/rgba(), CSS named colours, transparent.');
}

/** Paints `top` (which may be translucent) onto opaque `bottom`. */
export function compositeOver(top, bottom) {
    const a = top.a ?? 1;
    if (a >= 1) return { ...top, a: 1 };
    return {
        r: top.r * a + bottom.r * (1 - a),
        g: top.g * a + bottom.g * (1 - a),
        b: top.b * a + bottom.b * (1 - a),
        a: 1,
    };
}

/** WCAG relative luminance of an opaque colour, 0 (black) to 1 (white). */
export function relativeLuminance(color) {
    const linear = channel => {
        const c = channel / 255;
        return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
    };
    return 0.2126 * linear(color.r) + 0.7152 * linear(color.g) + 0.0722 * linear(color.b);
}

/**
 * WCAG contrast ratio between a foreground and a background colour: 1 (identical)
 * to 21 (white on black).
 *
 * Translucent inputs are composited before the comparison, because a ratio is
 * only defined between opaque colours: a translucent foreground is painted onto
 * the background, and a translucent background onto white (the page's ultimate
 * backdrop). Use getComputedColorPair() to obtain an already-resolved background
 * from a live page.
 */
export function contrastRatio(foreground, background) {
    const backdrop = compositeOver(parseColor(background), { r: 255, g: 255, b: 255, a: 1 });
    const front = compositeOver(parseColor(foreground), backdrop);
    const lighter = Math.max(relativeLuminance(front), relativeLuminance(backdrop));
    const darker = Math.min(relativeLuminance(front), relativeLuminance(backdrop));
    return (lighter + 0.05) / (darker + 0.05);
}

/** WCAG "large text": >= 24 px, or >= 18.66 px when bold (weight >= 700). */
export function isLargeText(fontSizePx, fontWeight) {
    const weight = Number(fontWeight) || 400;
    return fontSizePx >= 24 || (fontSizePx >= 18.66 && weight >= 700);
}

/** The AA threshold that applies to a given text size: 3 for large, else 4.5. */
export function wcagAAThreshold(fontSizePx, fontWeight) {
    return isLargeText(fontSizePx, fontWeight) ? 3 : 4.5;
}

/**
 * Resolves the computed foreground and the *effective* background of the first
 * element matching `selector` on a live page, then the contrast between them.
 *
 * The effective background is the element's own background-color composited over
 * each ancestor's, up to the first opaque one — the value a screenshot would
 * show, not the (usually transparent) declared value.
 *
 * @returns {Promise<{selector:string, foreground:string, background:string,
 *   ratio:number, fontSizePx:number, fontWeight:string, isLargeText:boolean,
 *   aaThreshold:number, passesAA:boolean, backgroundImage:string|null,
 *   backgroundImageAncestor:string|null}>}
 *   `backgroundImage` is non-null when a gradient or image sits behind the text;
 *   the ratio then describes only the colour layers and must not be trusted on
 *   its own.
 */
export async function getComputedColorPair(page, selector) {
    const resolved = await page.evaluate((sel) => {
        const element = document.querySelector(sel);
        if (!element) return { missing: true };

        const describe = node => node.tagName.toLowerCase()
            + (node.id ? `#${node.id}` : '')
            + (node.classList.length ? `.${[...node.classList].join('.')}` : '');

        const style = getComputedStyle(element);
        const layers = [];
        let backgroundImage = null;
        let backgroundImageAncestor = null;

        for (let node = element; node; node = node.parentElement) {
            const nodeStyle = getComputedStyle(node);
            if (backgroundImage === null && nodeStyle.backgroundImage !== 'none') {
                backgroundImage = nodeStyle.backgroundImage;
                backgroundImageAncestor = describe(node);
            }
            layers.push(nodeStyle.backgroundColor);
            const alpha = nodeStyle.backgroundColor.match(/rgba?\(([^)]+)\)/);
            const parts = alpha ? alpha[1].replace(/\//g, ' ').split(/[\s,]+/).filter(Boolean) : [];
            const opaque = parts.length < 4 || parseFloat(parts[3]) >= 1;
            if (opaque && nodeStyle.backgroundColor !== 'transparent') break;
        }

        return {
            foreground: style.color,
            layers,
            fontSizePx: parseFloat(style.fontSize),
            fontWeight: style.fontWeight,
            backgroundImage,
            backgroundImageAncestor,
        };
    }, selector);

    if (resolved.missing) throw new Error(`getComputedColorPair: no element matches "${selector}"`);

    // Paint the collected layers back to front, starting from the canvas (white).
    let background = { r: 255, g: 255, b: 255, a: 1 };
    for (const layer of [...resolved.layers].reverse()) {
        background = compositeOver(parseColor(layer), background);
    }

    const backgroundCss = `rgb(${[background.r, background.g, background.b]
        .map(channel => Math.round(channel)).join(', ')})`;
    const ratio = contrastRatio(resolved.foreground, backgroundCss);
    const aaThreshold = wcagAAThreshold(resolved.fontSizePx, resolved.fontWeight);

    return {
        selector,
        foreground: resolved.foreground,
        background: backgroundCss,
        ratio,
        fontSizePx: resolved.fontSizePx,
        fontWeight: resolved.fontWeight,
        isLargeText: isLargeText(resolved.fontSizePx, resolved.fontWeight),
        aaThreshold,
        passesAA: ratio >= aaThreshold,
        backgroundImage: resolved.backgroundImage,
        backgroundImageAncestor: resolved.backgroundImageAncestor,
    };
}

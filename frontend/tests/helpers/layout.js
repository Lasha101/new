// Geometry helpers for touch-target and layout assertions.

/**
 * Bounding boxes of every visible element matching `selector`.
 *
 * @returns {Promise<Array<{index:number, tagName:string, text:string,
 *   x:number, y:number, width:number, height:number, smallestSide:number}>>}
 *   Ordered as the DOM is. Elements with no box (display:none, detached) are
 *   skipped — they cannot be tapped, so they cannot fail a tap-target rule.
 */
export async function measureTapTargets(page, selector) {
    const locator = page.locator(selector);
    const elements = await locator.all();
    const measured = [];

    for (const [index, element] of elements.entries()) {
        const box = await element.boundingBox();
        if (!box) continue;
        measured.push({
            index,
            tagName: (await element.evaluate(node => node.tagName.toLowerCase())),
            text: ((await element.textContent()) || '').trim().replace(/\s+/g, ' ').slice(0, 60),
            x: box.x, y: box.y, width: box.width, height: box.height,
            smallestSide: Math.min(box.width, box.height),
        });
    }
    return measured;
}

/** Targets whose smallest side is under `minPx` (WCAG 2.2 AA uses 24, iOS HIG 44). */
export function tapTargetsBelow(targets, minPx) {
    return targets.filter(target => target.smallestSide < minPx);
}

/** True when the document is wider than the viewport, i.e. it scrolls sideways. */
export async function hasHorizontalOverflow(page) {
    return page.evaluate(() =>
        document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
}

/** Elements sticking out past the right edge of the viewport, with their widths. */
export async function findOverflowingElements(page) {
    return page.evaluate(() => {
        const limit = document.documentElement.clientWidth;
        const offenders = [];
        for (const node of document.querySelectorAll('*')) {
            const rect = node.getBoundingClientRect();
            if (rect.width === 0 && rect.height === 0) continue;
            if (rect.right > limit + 1) {
                offenders.push({
                    selector: node.tagName.toLowerCase()
                        + (node.id ? `#${node.id}` : '')
                        + (node.classList.length ? `.${[...node.classList].join('.')}` : ''),
                    right: Math.round(rect.right),
                    width: Math.round(rect.width),
                    viewportWidth: limit,
                });
            }
        }
        return offenders;
    });
}

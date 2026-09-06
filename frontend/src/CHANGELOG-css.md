# `scanid-app.css` — changelog

Every change to the delivered **v1.0** (04/09/2026), with the reason for each.
Contrast figures are **measured on the rendered page**, not estimated: they come
from `getComputedColorPair()` in `tests/helpers/color.js`, which composites an
element's colour against the background actually painted behind it. The full
measured table is produced by `tests/e2e/a11y.spec.js` on every run.

---

## v1.1 — 06/09/2026 (Package A)

### Fonts

**F1. Removed `@import url('https://fonts.googleapis.com/css2?…')` (line 10).**
Every visitor's IP was being sent to Google to fetch a webfont, which contradicts
the product's own promise that documents are never stored, and would have kept
`default-src 'self'` from ever being a usable CSP. The same two families are now
self-hosted through Fontsource (`@fontsource/space-grotesk`, `@fontsource/inter`)
and imported in `src/main.jsx` — Space Grotesk 400/500/600/700, Inter 400/500/600
and 400-italic, no other weights. Proven by `tests/e2e/fonts.spec.js` (a full
session records zero requests to `googleapis.com` / `gstatic.com`) and
`tests/build/no-google-fonts.test.js` (the shipped bundle contains neither
string).

### The four defects named in the brief

**4a. Tap targets.** `.sid-btn, .sid-btn-outline, .sid-btn-ghost` gained
`min-height: 44px` (were ≈40 px). Both specs require 44 px.

> **Deviation.** The brief asked for `min-height: 38px` on `.sid-seg button`,
> reasoning that the parent's 3 px of padding brings the total to 44. It does
> bring the *control* to 44 px, but a parent's padding is not part of a child's
> hit area — a tap 2 px above the button lands on `.sid-seg` and does nothing, so
> the real target would have stayed 38 px and failed the criterion the brief then
> tests for ("every `.sid-seg button` measures ≥ 44 px in height"). The button
> itself is therefore `min-height: 44px`; `.sid-seg` keeps its 3 px padding, so
> the control is 50 px rather than 44. The visual design is unchanged; only the
> control is 6 px taller.

**4b. iOS input zoom.** `.sid-input`, `.sid-select` and the bare
`input`/`select` rule moved from `.95rem` (15.2 px) to `font-size: 1rem` (16 px).
Safari auto-zooms a focused field under 16 px, which on this form threw the
layout sideways. Also added `.sid-checkbox`, so checkboxes stop inheriting the
text-field rule.

**4c. Contrast — new `--sid-muted-strong` token.** Added, and used in
`.sid-dropzone small`, `.sid-empty`, `.sid-appfoot` (and its `a`) and
`.sid-chip--queued`, exactly as the brief specifies. `.sid-topbar-right` was left
on `--sid-muted`, also as specified (measured 6.46:1 on the translucent navy bar).

> **Deviation — the token's value is `#5A6A80`, not `#64748B`.** `#64748B` is
> 4.76:1 on **white**, as the brief says. But only one of the four rules it was
> assigned to sits on white. Measured on the backgrounds those rules actually
> have:
>
> | rule | background | `#64748B` | verdict |
> |---|---|---|---|
> | `.sid-empty` | `#ffffff` (card) | 4.76:1 | pass |
> | `.sid-dropzone small` | `rgba(14,165,233,.05)` on white → `rgb(243,251,254)` | 4.54:1 | pass |
> | `.sid-appfoot` | `#eef4fb` (page) | **4.30:1** | **fail** |
> | `.sid-chip--queued` | `#eef2f7` (own) | **4.23:1** | **fail** |
>
> `#5A6A80` is the same hue, one step darker, and clears AA on all four:
> 5.51 / 5.26 / 4.98 / 4.91:1. Keeping `#64748B` would have shipped two rules
> below AA while the brief's own acceptance test asserted they were above it.

**4d. Sticky header.** Removed `position: sticky; top: 0;` from `.sid-table th`.
`.sid-table-wrap` has no height constraint, so there was nothing to stick
against; and had one been added, the header would have slid under `.sid-topbar`
(z-index 50).

**4e. Download icon.** `.sid-download-group .sid-btn::before` was scoped to the
filled button only, so the CSV button — the outline one — had no `⬇`. The
selector now also covers `.sid-download-group .sid-btn-outline::before`.

### Further defects found while applying the system

**N1. `.sid-badge--pi` was below AA.** `--sid-cyan-dark` (`#0284C7`) on the
badge's own `rgba(14,165,233,.15)` tint measures **3.53:1** on a white row and
3.37:1 on the `#f7fafd` striped row — well under the 4.5:1 its 11.5 px bold text
requires. Changed to `var(--sid-info)` (`#0369a1`, an existing token): 5.12:1 and
4.89:1. The badge looks the same; the text is one shade deeper.

**N2. The mobile card-list media query is scoped to `.sid-results`.** The brief's
snippet hides `.sid-table-wrap` outright below 720 px. That class also wraps the
**export preview** table, which has no card list to fall back on, so the preview
would have vanished on every phone with nothing in its place. The rule is
therefore `.sid-results .sid-table-wrap { display: none }` /
`.sid-results .sid-card-list { display: block }`. Everything else in the snippet
is verbatim, and only existing tokens are used.

**N3. `.sid-topbar .sid-btn-ghost` is `var(--sid-cyan)`.** The logout button is
the one ghost button on the navy bar. `--sid-cyan-dark` measures **4.04:1**
there (the bar is `rgba(11,22,40,.96)`, so it composites lighter than pure navy,
which makes a dark cyan *worse*, not better). The brand cyan gives 5.97:1 and
matches `.sid-credits` beside it. Hover goes to `#fff`.

### Additions the mapping needed

- **`.sid-card-list`, `.sid-card-item`, `…__head`, `…__row`, `…__label`,
  `…__value`** — the stacked mobile view, added verbatim from the brief, using
  only existing tokens (no new colour, font, radius or shadow).
- **`.sid-checkbox`** — 1.15 rem, `accent-color: var(--sid-cyan-dark)`. The
  system had no checkbox rule, and the results table has one per row.
- **Focus ring extended** to `.sid-btn-ghost`, `.sid-seg button` and `textarea`.
  v1.0 covered `.sid-btn`, `.sid-btn-outline`, `input` and `select` only, so
  three of the app's focusable controls had no visible focus indicator.
  Asserted by the keyboard specs in `tests/e2e/a11y.spec.js`.
- **`justify-content: center`** on the button base rule, so a full-width button
  (the login submit) centres its label instead of hugging the left edge.
- **`.sid-logo { margin: 0 }`** — it is rendered as the `<h1>`, which carries a
  `0 0 .6rem` margin from the base rule and pushed the bar out of alignment.
- **`.sid-credits { white-space: nowrap }`** — « Crédits : 12 » wrapped at 360 px.

(One rule outside this file, in `App.jsx`'s remaining `<style>` block:
`.filter-bar .form-group { min-width: 12rem }`, so the destination field wraps
onto its own line on a phone instead of being squeezed to a few characters.)

### Not changed

`--sid-muted` keeps `#94A3B8`; the brief explicitly leaves `.sid-topbar-right` on
it, and it measures 6.46:1 on the bar. The palette, radii, shadows, spacing scale
and every other rule are v1.0 as delivered.

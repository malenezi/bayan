# Layout: what mirrors, what does not, and how

## Contents
- Logical property map
- What the browser mirrors for you
- What you must handle yourself
- What must not mirror
- Icons
- Motion
- Components that go wrong
- Tailwind and other utility frameworks
- Component libraries

## Logical property map

Think in **inline** (the direction text flows) and **block** (the direction paragraphs stack), **start** and **end**. Never left and right.

| Physical | Logical |
|---|---|
| `margin-left` / `margin-right` | `margin-inline-start` / `margin-inline-end` |
| `margin: 0 auto` (centering) | unchanged, or `margin-inline: auto` |
| `padding-left` / `padding-right` | `padding-inline-start` / `padding-inline-end` |
| `left` / `right` | `inset-inline-start` / `inset-inline-end` |
| `top` / `bottom` | `inset-block-start` / `inset-block-end` (physical is fine: vertical does not flip) |
| `border-left` / `border-right` | `border-inline-start` / `border-inline-end` |
| `border-top-left-radius` | `border-start-start-radius` |
| `border-top-right-radius` | `border-start-end-radius` |
| `border-bottom-left-radius` | `border-end-start-radius` |
| `border-bottom-right-radius` | `border-end-end-radius` |
| `text-align: left` / `right` | `text-align: start` / `end` |
| `float: left` / `right` | `float: inline-start` / `inline-end` |
| `width` / `height` | `inline-size` / `block-size` (optional: these do not flip between LTR and RTL) |
| `scroll-margin-left` | `scroll-margin-inline-start` |

Shorthands: `margin-inline: 1rem 2rem` is start then end. `inset-inline: 0` replaces `left: 0; right: 0`. The four-value `margin`, `padding` and `border-radius` shorthands are **physical** (top, right, bottom, left) and do not flip: use them only when left and right are equal.

## What the browser mirrors for you

Once `dir="rtl"` is on the root and you use logical properties:

- Flex rows start from the right. Grid columns number from the right. `gap` needs nothing.
- `justify-content: flex-start` and `text-align: start` follow direction.
- Tables put the first column on the right. Lists put markers on the right.
- Scrollbars of RTL elements move to the left (the page scrollbar depends on the browser). Horizontal scroll containers start at the right edge.
- Form controls: checkboxes and radios sit to the right of their labels in source order; select arrows move to the left.

So do **not** add `flex-direction: row-reverse` for RTL. That double-flips.

## What you must handle yourself

| Thing | Why | Fix |
|---|---|---|
| `transform: translateX()`, `rotate()` | Transforms are physical | multiply by `--dir`, see Motion |
| `background-position: left`, gradients `to right` | Physical keywords | `[dir="rtl"]` override, or `background-position-x` with a logical-friendly value; gradients: `linear-gradient(to left…)` under `[dir="rtl"]` when the gradient encodes direction |
| `box-shadow` with an x offset | Physical | usually leave; flip only if the shadow implies a light source tied to reading direction |
| `transform-origin: left` | Physical | override under `[dir="rtl"]` |
| Absolutely positioned decorations | Often written with `left` | `inset-inline-start` |
| SVG and canvas drawings | Coordinates are physical | mirror the directional ones with `scaleX(-1)` under `[dir="rtl"]` |
| `clip-path`, `mask` with directional shapes | Physical | provide an RTL variant |
| JS that reads `scrollLeft`, `offsetLeft`, `getBoundingClientRect().left` | Physical; `scrollLeft` is zero or negative in RTL | compute from the inline-start edge; prefer `scrollIntoView({inline: "start"})` |
| Carousels and sliders from libraries | Often assume LTR | use the library's `rtl`/`direction` option |

## What must not mirror

- Media transport controls: play, pause, rewind, fast-forward, and the scrubber. They represent tape direction, not reading direction.
- Clocks, and anything representing clockwise motion (a refresh icon, a circular progress ring).
- Logos and brand marks.
- Checkmarks, plus, close, search, download, upload, share-box, settings.
- Phone numbers, card numbers, code blocks, mathematical expressions, musical notation.
- Photographs and illustrations, unless they visibly point at UI.
- Latin text. A block of English inside an Arabic page stays LTR.
- Charts: keep numeric axes and time series as your audience's analytical tools show them. Most Arabic-language dashboards keep time running left to right; some editorial graphics run right to left. Decide once per product and state it. Legends, labels and titles still follow the page direction.

Progress bars, steppers, sliders, ratings, pagination, breadcrumbs, timelines and tab strips **do** mirror: they express reading-order progress.

## Icons

Mirror an icon when it says "the direction you read in": back and forward arrows, chevrons in lists and accordions, reply and forward, undo and redo, send (paper plane), exit and enter, indent, list bullets, a text-alignment icon, a speech bubble tail, a running figure, a sound icon with waves.

```css
[dir="rtl"] .icon-directional { transform: scaleX(-1); }
```

In Arabic, "back" points right and "next" points left. An arrow character in text behaves the same way: `التالي ←`.

Do not mirror icons containing a question mark glyph by flipping; Arabic has its own `؟`, so swap the glyph. Do not mirror icons that contain text or numerals.

## Motion

Define direction once and use it everywhere something moves sideways:

```css
:root { --dir: 1; }
[dir="rtl"] { --dir: -1; }

.enter { transform: translateX(calc(var(--dir) * 2rem)); opacity: 0; }
.enter.in { transform: none; opacity: 1; transition: transform .5s cubic-bezier(.2,.7,.2,1), opacity .5s; }

@keyframes slide-out { to { transform: translateX(calc(var(--dir) * -100%)); } }
```

Content entering "from the end" comes from the left in RTL. Drawers attached to the inline-start edge slide in from the right. A marquee or ticker of Arabic text moves left to right, so that the start of the sentence appears first.

## Components that go wrong

- **Breadcrumbs**: separators are chevrons; mirror them or use a neutral `/`.
- **Input with an icon or unit**: position with `inset-inline-start` and pad with `padding-inline-start`.
- **Search field with a clear button**: the clear button belongs at the inline end.
- **Toasts and floating buttons**: anchored with `inset-inline-end`.
- **Tooltips and popovers**: placement names from libraries (`left`, `right-start`) are physical; map them (`placement = isRTL ? "left" : "right"`).
- **Tables with numbers**: align numeric columns to the end and keep the digits LTR (they are already).
- **Truncation with a fade**: the fade gradient sits at the inline end: flip the gradient under `[dir="rtl"]`.
- **Avatars stacked with negative margin**: `margin-inline-start: -8px`.
- **Stepper connectors drawn with `::after { left: 100% }`**: use `inset-inline-start: 100%`.
- **Range inputs**: `<input type="range">` follows `dir` natively. Custom sliders computing from `clientX` must invert.
- **Border accent on cards** (`border-left: 4px solid`): `border-inline-start`.
- **Quotes** with a decorative mark at top-left: `inset-inline-start`, and use an Arabic-appropriate mark (`«` or `”`).

## Tailwind and other utility frameworks

Tailwind 3.3+ ships logical utilities. Use them exclusively.

| Physical | Logical |
|---|---|
| `ml-*` / `mr-*` | `ms-*` / `me-*` |
| `pl-*` / `pr-*` | `ps-*` / `pe-*` |
| `left-*` / `right-*` | `start-*` / `end-*` |
| `text-left` / `text-right` | `text-start` / `text-end` |
| `float-left` / `float-right` | `float-start` / `float-end` |
| `rounded-l-*` / `rounded-r-*` | `rounded-s-*` / `rounded-e-*` |
| `rounded-tl-*` | `rounded-ss-*` (then `se`, `es`, `ee`) |
| `border-l-*` / `border-r-*` | `border-s-*` / `border-e-*` |
| `scroll-ml-*` | `scroll-ms-*` |

`space-x-*` and `divide-x-*` are physical: add `rtl:space-x-reverse` / `rtl:divide-x-reverse`, or replace them with `gap-*` on a flex or grid parent. For transforms use the `rtl:` variant: `rtl:-scale-x-100`, `rtl:translate-x-2`. The `rtl:` and `ltr:` variants key off the nearest `dir` attribute.

Bootstrap 5 ships `bootstrap.rtl.min.css` and logical utility names (`ms-`, `me-`, `ps-`, `pe-`, `text-start`). Load the RTL build for Arabic pages.

## Component libraries

- MUI: set `direction: "rtl"` in the theme and add the `stylis-plugin-rtl` cache.
- Chakra, Mantine, Ant Design, Radix: each has a direction provider (`dir="rtl"` / `DirectionProvider` / `ConfigProvider direction="rtl"`); set it at the root alongside `<html dir>`.
- shadcn/ui: components use Tailwind physical classes in places; convert to logical utilities when you add them.
- Swiper, Embla, Splide and similar: pass their RTL option; do not flip them with CSS.

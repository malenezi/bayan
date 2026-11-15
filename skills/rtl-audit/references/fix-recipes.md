# Fix recipes

## Contents
- Root and document
- CSS: physical to logical
- Shorthands that hide physical values
- Tailwind
- Sass and legacy browsers
- Isolation
- Typography
- Icons and motion
- JavaScript
- Component recipes

## Root and document

```html
<!-- before -->
<html>
<!-- after -->
<html lang="ar" dir="rtl">
```

In a framework, set both on the server-rendered `<html>`; setting them in a client effect causes a flash of LTR layout. Remove `body { direction: rtl; text-align: right; }` once `dir` is in markup.

## CSS: physical to logical

| Before | After |
|---|---|
| `margin-left: 16px` | `margin-inline-start: 16px` |
| `margin-right: auto` | `margin-inline-end: auto` |
| `padding: 0 24px 0 12px` | `padding-block: 0; padding-inline: 12px 24px` (start then end; note the order swap from right-then-left) |
| `left: 0` | `inset-inline-start: 0` |
| `right: 16px; left: auto` | `inset-inline-end: 16px` |
| `left: 0; right: 0` | `inset-inline: 0` |
| `border-left: 4px solid` | `border-inline-start: 4px solid` |
| `border-radius: 8px 0 0 8px` | `border-start-start-radius: 8px; border-end-start-radius: 8px` |
| `text-align: left` | `text-align: start` |
| `text-align: right` (numbers column) | `text-align: end` |
| `float: left` | `float: inline-start` |
| `clear: right` | `clear: inline-end` |

Search patterns that find most of it:

```
(margin|padding|border)-(left|right)
(^|[\s;{])(left|right)\s*:
text-align:\s*(left|right)
float:\s*(left|right)
border-(top|bottom)-(left|right)-radius
```

## Shorthands that hide physical values

The scanner cannot see these; search for them.

- Four-value `margin`, `padding`, `inset`, `border-width`, `border-radius`, `border-color` where the second and fourth values differ: `padding: 4px 12px 4px 8px`.
- `background-position: right 12px center`, `background: url(arrow.svg) no-repeat right`.
- `transform-origin: left center`.
- `box-shadow: 4px 0 …` when the shadow separates a sidebar from content.
- `linear-gradient(to right, …)` when it fades text or indicates progress.

Rewrite each with longhand logical properties, or add a `[dir="rtl"]` override where no logical form exists:

```css
.select        { background-position: right 12px center; }
[dir="rtl"] .select { background-position: left 12px center; }

.fade-end        { mask-image: linear-gradient(to right, #000 80%, transparent); }
[dir="rtl"] .fade-end { mask-image: linear-gradient(to left, #000 80%, transparent); }
```

## Tailwind

| Before | After |
|---|---|
| `ml-4` `mr-2` | `ms-4` `me-2` |
| `pl-6` `pr-3` | `ps-6` `pe-3` |
| `left-0` `right-4` | `start-0` `end-4` |
| `text-left` `text-right` | `text-start` `text-end` |
| `rounded-l-lg` `rounded-tr-md` | `rounded-s-lg` `rounded-se-md` |
| `border-l-4` | `border-s-4` |
| `space-x-4` | `gap-4` on a flex parent, or add `rtl:space-x-reverse` |
| `divide-x` | add `rtl:divide-x-reverse` |
| `translate-x-2` | `ltr:translate-x-2 rtl:-translate-x-2` |
| `origin-left` | `ltr:origin-left rtl:origin-right` |
| an arrow icon | add `rtl:-scale-x-100` |
| `tracking-wide` on shared text | `ltr:tracking-wide` or apply only under `lang="en"` |
| `italic` on shared text | `ltr:italic` |

Responsive and state prefixes are unaffected: `md:ml-4` becomes `md:ms-4`.

## Sass and legacy browsers

Logical properties are supported by all current browsers. If the project must support very old ones, compile with a PostCSS logical-properties plugin rather than writing physical CSS by hand. Replace direction mixins (`@include rtl { … }`) with logical properties as you touch each file, not all at once.

## Isolation

```html
<!-- before -->
<p>للاستفسار: +966 11 123 4567 أو support@example.com</p>
<!-- after -->
<p>للاستفسار: <bdi dir="ltr">+966 11 123 4567</bdi> أو <bdi dir="ltr">support@example.com</bdi></p>
```

In components, isolate at the point of interpolation so every caller benefits:

```jsx
<span>{t("orderNumber")} <bdi dir="ltr">{order.id}</bdi></span>
<li><bdi>{user.displayName}</bdi> <time dateTime={iso}>{formatted}</time></li>
```

For plain-text sinks (titles, notifications, `aria-label`), wrap with isolates in a helper:

```js
const ltr = s => "\u2066" + s + "\u2069";
document.title = `طلب رقم ${ltr(order.id)}`;
```

Inputs: add `dir="ltr"` to email, tel, url, number, password and code fields; `dir="auto"` to free-text fields.

## Typography

```css
/* before */
body { font-family: Inter, sans-serif; line-height: 1.4; }
.label { letter-spacing: .08em; text-transform: uppercase; }
em { font-style: italic; }

/* after */
body { font-family: Inter, system-ui, sans-serif; line-height: 1.5; }
[lang|="ar"] { font-family: "IBM Plex Sans Arabic", "Noto Sans Arabic", "Segoe UI", Tahoma, sans-serif; line-height: 1.8; }
:lang(ar) { letter-spacing: 0; font-style: normal; }
[lang|="ar"] :is(h1, h2, h3) { line-height: 1.4; }
.label:lang(en) { letter-spacing: .08em; text-transform: uppercase; }
.label:lang(ar) { font-weight: 600; }
em:lang(ar) { font-style: normal; font-weight: 600; }
```

Use the attribute selector for `font-family` and `line-height`: a bare `:lang(ar)` rule matches every descendant and overrides what headings pass down to their inner spans.

Replace fixed `height` on buttons, inputs and chips with `min-block-size` plus padding so Arabic marks are not clipped.

## Icons and motion

```css
:root { --dir: 1; }
[dir="rtl"] { --dir: -1; }

.icon-back, .icon-next, .icon-chevron, .icon-send { transform: scaleX(var(--dir)); }
.drawer { transform: translateX(calc(var(--dir) * -100%)); }
.drawer.open { transform: none; }
```

If an icon already has a transform, compose it: `transform: rotate(90deg) scaleX(var(--dir))`.

## JavaScript

```js
const isRTL = getComputedStyle(el).direction === "rtl";

// distance scrolled from the inline start, same sign in both directions
const scrolled = Math.abs(scroller.scrollLeft);

// scroll an item into view without left/right maths
item.scrollIntoView({ inline: "start", block: "nearest", behavior: "smooth" });

// pointer position along the inline axis, 0 at the inline start
const rect = track.getBoundingClientRect();
const ratio = isRTL ? (rect.right - e.clientX) / rect.width : (e.clientX - rect.left) / rect.width;

// arrow keys
const forward = isRTL ? "ArrowLeft" : "ArrowRight";

// popover placement
const placement = isRTL ? "left-start" : "right-start";
```

Read direction from the element, not from a global language flag: an LTR widget can live in an RTL page.

## Component recipes

**Input with a leading icon**

```css
.field { position: relative; }
.field .icon { position: absolute; inset-inline-start: 12px; inset-block: 0; margin-block: auto; }
.field input { padding-inline-start: 40px; }
```

**Card with an accent edge**: `border-inline-start: 4px solid var(--accent)`.

**Breadcrumb separator**

```css
.crumb + .crumb::before { content: "›"; display: inline-block; transform: scaleX(var(--dir)); margin-inline: .5em; }
```

**Custom select arrow**: position with `background-position` and a `[dir="rtl"]` override, or use a pseudo-element at `inset-inline-end`.

**Avatar stack**: `.avatar + .avatar { margin-inline-start: -8px; }`

**Notification badge**: `inset-block-start: -4px; inset-inline-end: -4px;`

**Sticky table column**: `position: sticky; inset-inline-start: 0;`

**Progress bar**: grow the fill with `inline-size`; do not use `scaleX` with a `left` origin.

**Off-canvas menu**: anchor with `inset-inline-start: 0` and translate by `calc(var(--dir) * -100%)`.

**Toast stack**: `inset-inline-end: 16px; inset-block-end: 16px;`

**Quote mark**: `inset-inline-start`, and use `«` for Arabic.

**Ordered list with custom counters**: counters print Western digits by default; use `counter(step, arabic-indic)` only if the product uses Arabic-Indic digits everywhere.

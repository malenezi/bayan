# What the scanner cannot see

Static analysis finds patterns in source. These checks need eyes on a rendered page, or a read of the JavaScript. Do them at `dir="rtl"`, at about 375px and 1280px wide. Record each failure with the component name and a one-line description.

## Contents
- Visual direction
- Icons and imagery
- Components and behaviour
- JavaScript assumptions
- Text and content
- Forms
- Accessibility
- Regression check for LTR

## Visual direction

- [ ] The page starts at the right: logo and primary navigation at the inline start, language switcher and account controls at the inline end.
- [ ] Nothing is double-flipped (a row that reads left to right inside an RTL page usually means `row-reverse` plus `dir`).
- [ ] Nothing is flipped that should not be: media controls, charts' numeric axes, logos, photos, code blocks.
- [ ] Sidebars, drawers and off-canvas menus open from the inline-start edge.
- [ ] Decorative offsets (ribbons, badges, accents, shadows that imply direction) sit on the correct side.
- [ ] No horizontal scrollbar on the page. RTL overflow often hides at the left edge.
- [ ] Sticky and fixed elements (chat widgets, back-to-top, cookie banners) are on the expected side and do not cover content.

## Icons and imagery

- [ ] Back, next, breadcrumb, accordion and "read more" arrows point in reading direction (next points left).
- [ ] Send, reply, undo/redo, exit, indent icons are mirrored.
- [ ] Play, clock, search, checkmark, download, settings and brand icons are **not** mirrored.
- [ ] Icons with a question mark or with numerals are replaced, not flipped.
- [ ] Screenshots and illustrations that show UI are the Arabic UI.
- [ ] Images containing text have an Arabic version or real text overlaid.

## Components and behaviour

- [ ] Carousels: first item at the right, swipe and arrows advance leftwards, pagination dots in reading order.
- [ ] Tabs: first tab at the right; Left arrow key moves to the next tab.
- [ ] Steppers, progress bars and sliders fill from the right.
- [ ] Dropdowns, popovers and tooltips open towards available space and align to the inline start of their trigger.
- [ ] Tables: first column at the right; numeric columns align consistently; sticky columns stick to the correct edge.
- [ ] Toasts and snackbars appear at the documented corner for RTL.
- [ ] Modals: close button at the inline end; action buttons ordered primary-first in reading order (or per the design system's rule, applied consistently).
- [ ] Date pickers: week starts on the locale's first day; month navigation arrows mirrored; correct calendar.
- [ ] Charts: titles, legends and tooltips are right-aligned and in Arabic; axis direction matches the product's stated convention.
- [ ] Maps and embedded third-party widgets are set to Arabic where they offer it.
- [ ] Text truncation ends at the left with the ellipsis there; fade masks are on the left.
- [ ] Animations: entrances, slide-overs and page transitions move in reading direction.

## JavaScript assumptions

Search the code for these and review each hit:

- `scrollLeft`, `scrollTo(` with an x value, `offsetLeft`, `getBoundingClientRect().left/right`, `clientX` maths in drag, swipe and slider code. `scrollLeft` is zero or negative in RTL.
- `style.left`, `style.right`, `style.marginLeft`, `style.transform = "translateX(…)"` set from script.
- Placement strings passed to positioning libraries: `"left"`, `"right"`, `"bottom-start"`.
- Keyboard handlers that map ArrowLeft to "previous" and ArrowRight to "next".
- String concatenation that builds sentences (`count + " items"`) and two-form plural logic.
- `toLocaleString()`, `toLocaleDateString()` and `Intl.*` called without an explicit locale, numbering system and calendar.
- Regular expressions using `\w`, `[a-z]` or `\b` on user text: they do not match Arabic letters.
- `toUpperCase()` used for emphasis, `text.split("")` used for per-letter effects.
- Sorting with the default comparator instead of `Intl.Collator`.

## Text and content

- [ ] Everything visible is translated, including error messages, empty states, emails, PDFs and third-party widget text.
- [ ] The Arabic reads naturally. Flag literal translations, inconsistent terms for the same feature, and mixed registers. (Use the `arabic-ux-writing` skill if available.)
- [ ] Mixed Arabic and Latin lines read in the right order at every breakpoint; wrapping can expose problems a single line hides.
- [ ] Numbers, dates, times and currency follow one convention across the product.
- [ ] No text is clipped at the top or bottom: Arabic marks and descenders need room.
- [ ] Headings and buttons do not rely on uppercase for hierarchy.
- [ ] Page `<title>`, meta description and social preview are in Arabic on Arabic pages.

## Forms

- [ ] Labels are right-aligned above fields; required markers and help text follow.
- [ ] Email, phone, URL, password, numeric and code fields are LTR; free text fields flip with the typed language.
- [ ] Validation accepts Arabic letters and Arabic-Indic digits where a human would expect it to.
- [ ] Error messages appear in Arabic, next to the field, at the inline start.
- [ ] Checkboxes and radios sit to the right of their labels.
- [ ] Autofill, input masks and one-time-code inputs still work.

## Accessibility

- [ ] `<html lang="ar" dir="rtl">` is present in the served HTML, not only after hydration.
- [ ] Inline English inside Arabic has `lang="en"`, so screen readers switch voice.
- [ ] `aria-label`, `alt` and `title` values are translated.
- [ ] Focus order follows visual reading order; no `order` or `row-reverse` reorders it.
- [ ] Visible focus outlines are not clipped at the right edge.

## Regression check for LTR

After fixes, load the English version and confirm it is visually unchanged. Logical properties are neutral in LTR; a visible change means a physical value was converted with the wrong mapping or a symmetric pair was converted on one side only.

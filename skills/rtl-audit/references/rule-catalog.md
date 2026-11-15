# Rule catalogue

Generated from `scripts/bidi_lint.py` (version 1.0.0). Do not edit by hand; run `python tools/gen_rule_catalog.py` in the repository.

Severity: **error** fails the run, **warning** fails with `--strict`, **info** asks for a look.

## Contents
- Document structure and text
- CSS
- Utility classes
- Deck profile (`--profile deck`)
- Suppressing a finding

## Document structure and text

### BD101: <html> has no lang attribute

**Severity:** error

Screen readers pick a voice from `lang`, browsers pick fonts and hyphenation from it, and search engines use it.

- Before: `<html>`
- After: `<html lang="ar" dir="rtl">`
- Fix: Declare the language: <html lang="ar" dir="rtl">.
- Not a defect when: Never. HTML fragments without an `<html>` tag are not checked.

### BD102: RTL document without dir on <html>

**Severity:** error

Without `dir`, an Arabic page lays out left to right: alignment, punctuation and every flex row are wrong.

- Before: `<html lang="ar">`
- After: `<html lang="ar" dir="rtl">`
- Fix: Set dir="rtl" on <html>; do not rely on CSS direction or text-align.
- Not a defect when: Never.

### BD103: lang and dir disagree

**Severity:** error

A mismatch means either the wrong voice and fonts or a mirrored layout for the wrong language.

- Before: `<html lang="ar" dir="ltr">`
- After: `<html lang="ar" dir="rtl">`
- Fix: ar/he/fa/ur need dir="rtl"; LTR languages need dir="ltr".
- Not a defect when: Never.

### BD104: language switch without dir

**Severity:** warning

An English phrase inside Arabic keeps RTL punctuation placement unless it gets its own direction.

- Before: `<span lang="en">Terms of Service.</span>`
- After: `<span lang="en" dir="ltr">Terms of Service.</span>`
- Fix: An element whose lang changes script direction also needs dir (e.g. <span lang="en" dir="ltr">).
- Not a defect when: Single words without punctuation render correctly, but adding `dir` is still harmless.

### BD105: LTR-only input not isolated

**Severity:** warning

Emails, phone numbers and URLs typed into an RTL field show their symbols on the wrong side and the caret behaves oddly.

- Before: `<input type="email">`
- After: `<input type="email" dir="ltr">`
- Fix: Add dir="ltr" (or dir="auto") to email/tel/url/number/password inputs inside RTL pages.
- Not a defect when: Fields inside an explicitly LTR form.

### BD106: legacy bidi control characters in source

**Severity:** warning

U+202A to U+202E embed or override direction without isolating, leak past their intended span, and are a known trick for disguising source code.

- Before: `\u202B…\u202C in a string`
- After: `<bdi> in markup, or U+2066…U+2069 isolates in plain text`
- Fix: Replace U+202A-202E embeddings/overrides with <bdi>, dir attributes or isolates (U+2066-2069).
- Not a defect when: Test fixtures that exercise bidi handling.

### BD107: LTR run will reorder inside RTL text

**Severity:** warning

Digits and symbols at the edge of an LTR run are claimed by the RTL paragraph: phone groups reverse, signs and slashes jump sides.

- Before: `<p>اتصل: +966 11 123 4567</p>`
- After: `<p>اتصل: <bdi dir="ltr">+966 11 123 4567</bdi></p>`
- Fix: Wrap it: <bdi dir="ltr">...</bdi> (or <span dir="ltr">). For ranges, words are clearer: من 10 إلى 20.
- Not a defect when: Text that is only ever shown in an LTR context; template placeholders.

### BD108: Latin punctuation after Arabic text

**Severity:** warning

Arabic has its own comma, semicolon and question mark. Latin ones look foreign and the question mark faces the wrong way.

- Before: `مرحبا, كيف حالك?`
- After: `مرحبًا، كيف حالك؟`
- Fix: Use Arabic punctuation: ، (comma) ؛ (semicolon) ؟ (question mark).
- Not a defect when: Code samples and CSV-like data written in running text.

### BD109: mixed digit systems

**Severity:** info

Switching between 0-9 and ٠-٩ inside one product reads as an error and complicates search and copy/paste.

- Before: `٢٥ فرعًا في 30 مدينة`
- After: `25 فرعًا في 30 مدينة`
- Fix: Pick one digit system per product (Western 0-9 or Arabic-Indic ٠-٩) and apply it everywhere.
- Not a defect when: Content that quotes another source verbatim, or teaching material about digits.

### BD110: tatweel (kashida) used to stretch text

**Severity:** info

Tatweel inserted to stretch a word breaks search, copy/paste, spell-checking and screen-reader pronunciation.

- Before: `مرحـــبًا`
- After: `مرحبًا`
- Fix: Remove U+0640 runs; they break search, copy/paste and screen readers. Use CSS for emphasis.
- Not a defect when: Calligraphic logotypes set as text (prefer an SVG).

### BD111: forward arrow points the wrong way in RTL

**Severity:** info

In RTL the reader moves leftwards, so a right-pointing arrow on a 'next' or 'more' link points backwards.

- Before: `<a>التالي →</a>`
- After: `<a>التالي ←</a>`
- Fix: In RTL 'forward/next' points left. Use ← or a mirrored icon; keep → only for literal directions.
- Not a defect when: Arrows that describe a literal direction or a mapping (A → B) in technical text.

### BD113: presentational align attribute

**Severity:** warning

`align` is obsolete and physical.

- Before: `<td align="right">`
- After: `td { text-align: end; }`
- Fix: Replace align="left|right" with CSS text-align: start|end.
- Not a defect when: HTML email templates, where attributes are still required.

### BD115: directional icon may need mirroring

**Severity:** info

Class names like `chevron-right` usually mean a directional icon that should mirror in RTL.

- Before: `<i class="chevron-right">`
- After: `<i class="chevron-right rtl:-scale-x-100">`
- Fix: Mirror back/next/chevron icons in RTL ([dir=rtl] .icon{transform:scaleX(-1)} or Tailwind rtl:-scale-x-100).
- Not a defect when: Icons that are already swapped by a component, or that show a literal direction.

## CSS

### BD201: physical box property

**Severity:** warning

Physical properties stay on the same side in RTL, so spacing, offsets and borders end up on the wrong edge.

- Before: `.card { margin-left: 16px; }`
- After: `.card { margin-inline-start: 16px; }`
- Fix: Use the logical equivalent (margin-inline-start, padding-inline-end, inset-inline-start, border-start-start-radius ...).
- Not a defect when: Deliberately physical UI such as a media scrubber. Symmetric pairs, centering and `[dir]`-scoped rules are already exempt.

### BD202: physical alignment keyword

**Severity:** warning

`left` and `right` alignment does not follow direction.

- Before: `.title { text-align: left; }`
- After: `.title { text-align: start; }`
- Fix: Use start/end (text-align) or inline-start/inline-end (float, clear).
- Not a defect when: A block that is always LTR, such as code. Scope it instead of ignoring.

### BD203: direction set in CSS

**Severity:** warning

CSS `direction` does not tell assistive technology or the bidi algorithm what markup would, and it is lost when styles fail to load.

- Before: `body { direction: rtl; }`
- After: `<html dir="rtl">`
- Fix: Direction is content, not style: use the dir attribute in markup.
- Not a defect when: Rare: styling generated content you cannot add attributes to.

### BD204: letter-spacing reaches Arabic text

**Severity:** warning

Arabic letters join. Letter-spacing pulls the joins apart or leaves gaps in the connecting stroke.

- Before: `h2 { letter-spacing: .1em; }`
- After: `h2:lang(en) { letter-spacing: .1em; }`
- Fix: Tracking breaks Arabic joining. Scope it to Latin (:lang(en), [dir=ltr]) or reset to 0 for :lang(ar).
- Not a defect when: Selectors that can only match Latin text; scope them and the finding goes away.

### BD205: italic reaches Arabic text

**Severity:** info

Arabic has no italic. Browsers synthesise a slant that looks broken.

- Before: `em { font-style: italic; }`
- After: `em:lang(en) { font-style: italic; } em:lang(ar) { font-weight: 600; }`
- Fix: Arabic has no italic; browsers fake a slant. Scope italics to Latin and use weight or colour for Arabic emphasis.
- Not a defect when: Latin-only selectors.

### BD207: line-height too tight for Arabic body text

**Severity:** warning

Arabic has tall ascenders, deep descenders and stacked marks. Tight leading makes lines touch.

- Before: `body { line-height: 1.3; }`
- After: `:lang(ar) { line-height: 1.8; }`
- Fix: Arabic needs roughly 1.6-1.9 for body copy (1.2-1.4 for large headings).
- Not a defect when: Single-line UI labels with fixed padding.

### BD208: font stack has no Arabic-capable family

**Severity:** warning

If no listed family has Arabic glyphs, the browser picks a fallback that varies by device and rarely matches the design.

- Before: `body { font-family: Inter, sans-serif; }`
- After: `:lang(ar) { font-family: "IBM Plex Sans Arabic", Tahoma, sans-serif; }`
- Fix: Name an Arabic typeface first for Arabic content (e.g. 'IBM Plex Sans Arabic', 'Noto Kufi Arabic'), then fallbacks.
- Not a defect when: A stack that relies on a brand font not in the built-in list; the rule is skipped when the value uses a CSS variable.

### BD209: horizontal motion does not mirror

**Severity:** info

Transforms are physical. A panel that slides in from the left in English also slides from the left in Arabic, against reading direction.

- Before: `.drawer { transform: translateX(-100%); }`
- After: `.drawer { transform: translateX(calc(var(--dir) * -100%)); }`
- Fix: translateX keeps its sign in RTL. Multiply by a direction variable (--dir: 1 / -1) or override under [dir=rtl].
- Not a defect when: Centering with -50%, vertical-only motion and symmetric effects (already exempt where detectable).

### BD210: physical keyword in positioning value

**Severity:** info

Keyword positions such as `left center` do not flip.

- Before: `.select { background-position: right 12px center; }`
- After: `[dir="rtl"] .select { background-position: left 12px center; }`
- Fix: background-position/transform-origin/object-position 'left|right' do not flip; add an RTL override if the visual is directional.
- Not a defect when: Decorative backgrounds with no directional meaning.

### BD212: word-break: break-all on Arabic

**Severity:** warning

`break-all` splits Arabic words in the middle. The pieces still render, but as broken words.

- Before: `.cell { word-break: break-all; }`
- After: `.cell { overflow-wrap: anywhere; }`
- Fix: break-all splits Arabic words mid-word. Use overflow-wrap: anywhere or scope break-all to Latin/code.
- Not a defect when: Cells that only contain codes, hashes or URLs; scope them to Latin.

### BD213: bare :lang() sets an inherited text property

**Severity:** info

`:lang(ar)` is not `[lang=ar]`: it matches all descendants. A font or line-height set there overrides what a heading passes to its inner spans.

- Before: `:lang(ar) { font-family: X; line-height: 1.8; }`
- After: `:lang(ar) { --text: X; } [lang] { font-family: var(--text); }`
- Fix: :lang() matches every element in that language, so spans inside headings are reset. Set variables in :lang() and apply font-family/line-height on [lang].
- Not a defect when: Pages with no nested inline elements inside headings; resets such as letter-spacing: 0 are not flagged.

## Utility classes

### BD301: physical utility class

**Severity:** warning

Physical utility classes behave like physical CSS.

- Before: `<div class="ml-4 text-left">`
- After: `<div class="ms-4 text-start">`
- Fix: Use logical utilities: ms-/me-/ps-/pe-, start-/end-, text-start/text-end, rounded-s/e, border-s/e.
- Not a defect when: Classes behind an `rtl:` or `ltr:` variant, symmetric pairs and centering are already exempt.

## Deck profile (`--profile deck`)

### DK401: animations without prefers-reduced-motion

**Severity:** warning

Some people get motion sickness from transitions; the OS setting must be honoured.

- Before: `(no media query)`
- After: `@media (prefers-reduced-motion: reduce) { .slide { transition: none; } }`
- Fix: Add @media (prefers-reduced-motion: reduce) that disables transitions and animations.
- Not a defect when: Decks with no animation at all.

### DK402: no print stylesheet

**Severity:** warning

Decks are shared as PDFs. Without print rules the export shows one slide, or overlapping slides.

- Before: `(no print rules)`
- After: `@media print { .slide { break-after: page; opacity: 1; transform: none; } }`
- Fix: Add @media print so the deck exports to PDF one slide per page.
- Not a defect when: Never for a deliverable deck.

### DK403: no keyboard navigation

**Severity:** warning

A presenter needs keyboard control, and so do keyboard-only users.

- Before: `(click-only navigation)`
- After: `document.addEventListener("keydown", …)`
- Fix: Handle keydown for arrows/space/Home/End; in RTL the Left arrow advances.
- Not a defect when: Scroll-snap decks that rely on native scrolling.

### DK404: slide is text-heavy

**Severity:** info

More than about 75 words means the audience reads instead of listening.

- Before: `(a slide with five paragraphs)`
- After: `(one idea, split across slides, detail in notes)`
- Fix: Cut to one idea per slide; move detail to speaker notes or an appendix.
- Not a defect when: Appendix and read-alone reference slides.

### DK405: slide has no heading

**Severity:** warning

Headings give each slide a name for screen readers and for the outline.

- Before: `<section class="slide"><p>…</p></section>`
- After: `<section class="slide"><h2>…</h2>…</section>`
- Fix: Give every slide an h1-h3 (visually hidden if needed) for structure and screen readers.
- Not a defect when: Full-bleed image slides; add a visually hidden heading instead.

## Suppressing a finding

- One line: put `bidi-lint-ignore` in a comment on that line, followed by the reason.
- One rule for a whole file: `bidi-lint-disable BD201` anywhere in the file. Several ids may follow.
- From the command line: `--ignore BD209,BD210` or `--select BD107`.

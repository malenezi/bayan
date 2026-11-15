# Arabic typography for screens

## Contents
- Choosing a typeface by voice
- Pairing Arabic with Latin
- Size, line-height and measure
- What Arabic does not have
- Emphasis and hierarchy
- CSS setup
- Loading fonts
- Common mistakes

## Choosing a typeface by voice

Arabic type has styles the way Latin has serif and sans. Choose for the voice, then check that the family has the weights you need.

| Voice | Style | Open-licensed families (Google Fonts) |
|---|---|---|
| Modern, institutional, technical | Low-contrast "sans" Naskh | IBM Plex Sans Arabic, Noto Sans Arabic, Readex Pro, Alexandria |
| Bold, geometric, confident headlines | Kufi | Noto Kufi Arabic, Reem Kufi, Kufam, Changa |
| Friendly, approachable product UI | Rounded or humanist | Tajawal, Almarai, Baloo Bhaijaan 2, Zain |
| Editorial, literary, formal documents | Traditional Naskh | Amiri, Noto Naskh Arabic, Scheherazade New, Markazi Text |
| Expressive display | Display and calligraphic | El Messiri, Lemonada, Aref Ruqaa, Rakkas, Lalezar |

Guidance:

- Use at most two Arabic families: one for text, optionally one for display.
- Cairo and Tajawal are everywhere; reach for them only when ubiquity is the point.
- Traditional Naskh at small sizes needs more size and leading than a sans Naskh.
- Kufi display faces are wide: check that long headlines still fit at mobile widths.
- For Persian or Urdu, pick a face designed for that language (Vazirmatn; Noto Nastaliq Urdu) rather than an Arabic one.
- Many institutions have a licensed brand typeface. Ask before substituting.

## Pairing Arabic with Latin

Match stroke contrast, weight and apparent size, not the name.

| Arabic | Latin partner | Notes |
|---|---|---|
| IBM Plex Sans Arabic | IBM Plex Sans | Designed together |
| Noto Sans Arabic / Noto Kufi Arabic | Noto Sans, Inter | Neutral |
| Readex Pro, Alexandria, Rubik, Zain | (same family) | One family covers both scripts |
| Amiri, Noto Naskh Arabic | A transitional serif: Source Serif 4, Newsreader, Fraunces | Matching contrast |
| Reem Kufi, Kufam | A geometric sans: Outfit, Sora | Matching geometry |
| El Messiri | A humanist serif or sans with character | Display use |

Put the Arabic family **first** in the Arabic stack. Otherwise Latin punctuation and digits come from the Latin font and sit at the wrong height and weight inside Arabic text.

## Size, line-height and measure

- Arabic looks smaller than Latin at the same `font-size` because its x-height equivalent is lower. Scale Arabic up about 5 to 15 percent, depending on the pairing, until a mixed line looks even.
- Body text: at least 16px, comfortably 17 to 18px.
- Line-height: 1.7 to 1.9 for body, 1.3 to 1.5 for headings. Arabic has tall ascenders, deep descenders and stacked marks; tight leading makes lines collide.
- Measure: 55 to 75 characters. Arabic words are shorter on average, so a column can be slightly narrower than its English twin.
- Do not justify body text on the web. Browsers justify Arabic by stretching spaces only, which leaves rivers.

## What Arabic does not have

- **Capitals.** `text-transform: uppercase` does nothing. A design that relies on all-caps labels needs another device in Arabic: weight, size, colour or a rule.
- **Italics.** The browser fakes a slant, sometimes in the wrong direction. Turn it off for Arabic.
- **Letter-spacing.** Arabic is cursive: tracking pulls joined letters apart or leaves gaps in the baseline stroke. Always `letter-spacing: 0` for Arabic.
- **Hyphenation.** Arabic words do not break across lines.

Stretching a word with tatweel (`ـ`) is a calligraphic device, not a layout tool. Do not type it into content to fill space or add emphasis; it breaks search, copying and screen readers.

## Emphasis and hierarchy

Without capitals, italics or tracking, build hierarchy from:

- Weight: Arabic reads well at 400 to 500 for body and 600 to 700 for headings. Avoid weights below 300 at text sizes; thin joins disappear.
- Size and space.
- Colour and tint.
- A second typeface for display.
- Rules, numerals and position.

Underlines cut through dots and descenders. If links must be underlined, add `text-underline-offset: .3em` and `text-decoration-thickness: 1px`, or `text-decoration-skip-ink: auto`.

## CSS setup

```css
:root {
  --font-ar: "IBM Plex Sans Arabic", "Noto Sans Arabic", "Segoe UI", Tahoma, sans-serif;
  --font-en: "IBM Plex Sans", system-ui, sans-serif;
}

/* :lang() switches variables only */
:lang(ar) { --text: var(--font-ar); --lh: 1.8; --lh-head: 1.4; letter-spacing: 0; font-style: normal; }
:lang(en) { --text: var(--font-en); --lh: 1.6; --lh-head: 1.15; }

/* fonts are applied where the language changes, and inherited everywhere else */
[lang]     { font-family: var(--text); line-height: var(--lh); }
h1, h2, h3 { line-height: var(--lh-head); }

/* Latin-only refinements */
.eyebrow:lang(en) { letter-spacing: .12em; text-transform: uppercase; }
em:lang(en)       { font-style: italic; }
em:lang(ar)       { font-style: normal; font-weight: 600; }

h1, h2 { text-wrap: balance; }
p      { text-wrap: pretty; }
```

`:lang()` matches every element in that language, not only the one carrying the attribute. That makes it ideal for switching variables and for resets that should hold everywhere (`letter-spacing: 0`), and a trap for inherited properties: a bare `:lang(ar) { font-family: …; line-height: 1.8 }` also hits every `<span>` and `<em>` inside a heading, replacing the heading's display font and forcing body leading onto its lines. Apply `font-family` and `line-height` on `[lang]` (the elements where the language actually changes) and let everything else inherit. A `<span lang="en">` inside an Arabic paragraph then picks up the Latin font, and the whole page switches when the root `lang` changes.

Numerals inside Arabic text come from the Arabic font. If its Western digits look mismatched, check whether the font offers alternates through `font-variant-numeric` or `font-feature-settings`; do not swap fonts just for digits.

## Loading fonts

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
```

- Load only the weights you use. Arabic fonts are large.
- `display=swap` keeps text visible while fonts load. Choose fallbacks with similar width (`Tahoma`, `Segoe UI`, `Geeza Pro`, `Noto Sans Arabic`) so the swap does not reflow the page much.
- For offline or restricted networks, self-host the WOFF2 files and declare `@font-face` with `unicode-range: U+0600-06FF, U+0750-077F, U+08A0-08FF, U+FB50-FDFF, U+FE70-FEFF` for the Arabic face.
- Always end the stack with system fonts that carry Arabic. `Inter, sans-serif` alone leaves Arabic to an unpredictable fallback.

## Common mistakes

| Mistake | Result | Fix |
|---|---|---|
| English design tokens reused unchanged | Arabic looks small and cramped | Arabic-specific size and line-height tokens |
| `letter-spacing` on a shared heading class | Disconnected letters | Scope to `:lang(en)` |
| Latin font first in the stack | Mismatched digits and punctuation | Arabic font first under `:lang(ar)` |
| Weight 300 or lower for body | Hairline joins vanish | 400 or heavier |
| Fixed-height buttons and cards | Diacritics and descenders clipped | Use padding and `min-block-size`, not `height` with tight leading |
| `overflow: hidden` on a heading with tight line-height | Marks cut off | Loosen the line-height or add block padding |
| Bare `:lang(ar) { font-family; line-height }` | Spans inside headings lose the display font and get body leading | Set variables in `:lang()`, apply fonts on `[lang]` |
| All-caps eyebrow labels as the only hierarchy device | Hierarchy disappears in Arabic | Add weight, colour or a rule |

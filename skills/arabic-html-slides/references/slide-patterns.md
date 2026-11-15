# Slide patterns

Each pattern lists when to use it and the markup the starter's CSS expects. All of them live inside `<section class="slide" data-layout="…">`, start with an optional `.kicker` and a title (`h1` on the title slide, `h2` elsewhere), and use paired `data-lang` variants for text.

## Contents
- Title
- Statement
- Numbers
- Chart
- Split
- Comparison
- Timeline
- Ask
- Patterns to add yourself
- Designing the theme

## Title

Opening slide. Subject, occasion, date. Nothing else.

```html
<section class="slide" data-layout="title">
  <p class="kicker"><span data-lang="ar">مراجعة الربع الثالث 2026</span><span data-lang="en">Q3 2026 review</span></p>
  <h1><span data-lang="ar">…</span><span data-lang="en">…</span></h1>
  <div class="meta"><span data-lang="ar">عرض للجنة التوجيهية</span><span data-lang="en">Steering committee briefing</span></div>
</section>
```

## Statement

One sentence at display size. Use for the governing message, for section turns and for the single line you want remembered. Mark the two or three key words with `<mark>`.

```html
<section class="slide" data-layout="statement">
  <h2><span data-lang="ar">تحدّينا الآن <mark>الجودة لا العدد</mark></span><span data-lang="en">The challenge now is <mark>quality, not volume</mark></span></h2>
</section>
```

## Numbers

Two to four headline figures, each with a noun and a comparison. Reveal one at a time with `data-step` when the speaker will discuss each.

```html
<div class="trio">
  <div data-step>
    <span class="num">87%</span>
    <p data-lang="ar">نسبة الإتمام</p><p data-lang="en">completion rate</p>
    <small><span data-lang="ar"><bdi dir="ltr">+9</bdi> نقاط عن الربع الثاني</span><span data-lang="en">+9 points vs Q2</span></small>
  </div>
</div>
```

The figure itself is written once when it is identical in both languages. Isolate signs, slashes and ranges with `<bdi dir="ltr">`.

## Chart

Horizontal bars built in HTML and CSS: they need no library, follow direction, and print cleanly. Set the value with `--v`; add `.hot` to the bar the title is about. Give the group `role="img"` and a translated label that states the data.

```html
<div class="bars" role="img" data-ar-aria-label="…" data-en-aria-label="…">
  <div class="bar hot" style="--v: 64%">
    <span data-lang="ar">الأمن السيبراني</span><span data-lang="en">Cybersecurity</span>
    <span class="track"><i class="fill"></i></span><span class="num">64%</span>
  </div>
</div>
```

For line, area or scatter charts, draw inline SVG. Keep axis numbers in the Latin font, translate labels through `data-lang` variants placed in HTML over the SVG rather than as SVG `<text>`, and decide once whether time runs left to right in both languages (the common choice for data) or follows reading direction. If the SVG must mirror, wrap it and apply `transform: scaleX(var(--dir))` to shapes only, never to text.

## Split

Text on one side, supporting points or a visual on the other. The first grid column is at the inline start: right in Arabic, left in English.

```html
<div class="split">
  <div><p class="kicker">…</p><h2>…</h2></div>
  <ul class="points">
    <li data-step><h3>…</h3><p data-lang="ar">…</p><p data-lang="en">…</p></li>
  </ul>
</div>
```

## Comparison

Before and after, option A and option B, today and proposed. The arrow between them mirrors with `scaleX(var(--dir))`, so "from" is always at the reading start.

```html
<div class="compare">
  <div><h3>…</h3><ul><li>…</li></ul></div>
  <svg class="arrow" viewBox="0 0 64 64" aria-hidden="true">…</svg>
  <div class="to"><h3>…</h3><ul><li>…</li></ul></div>
</div>
```

Keep the two lists parallel: same number of items, same order of topics.

## Timeline

Three to five milestones in reading order. Dates go in `<time datetime="…">` with a translated visible label.

```html
<ol class="timeline">
  <li data-step><time datetime="2027-01"><span data-lang="ar">يناير</span><span data-lang="en">January</span></time>
    <h3>…</h3><p data-lang="ar">…</p><p data-lang="en">…</p></li>
</ol>
```

## Ask

The closing slide: the decisions or next steps requested, numbered, three at most.

```html
<ol class="asks">
  <li data-step><span data-lang="ar">اعتماد …</span><span data-lang="en">Approve …</span></li>
</ol>
```

## Patterns to add yourself

Build these from the same parts when the story calls for them:

- **Quote**: a short quotation at statement size with the speaker's name and role beneath. Use `«…»` in Arabic. Only real, attributable quotes.
- **Image with caption**: full-bleed image, a gradient scrim at the block end, title over it. Check contrast in both languages.
- **Matrix (2 by 2)**: CSS grid with axis labels as variants; the origin sits at the inline start.
- **Process**: numbered steps in a row with mirrored chevrons, or a vertical list when there are more than five.
- **Table**: five rows and four columns at most on a slide; numeric columns aligned to the end; the row the title refers to highlighted.
- **Section divider**: a statement slide in the inverse colour scheme with the section number.
- **Appendix marker**: a plain slide titled «الملاحق» / "Appendix" after the ask.

## Designing the theme

The starter's theme is a neutral placeholder. For each deck:

- Choose two or three colours with a reason tied to the subject or the brand, plus neutrals. One accent carries emphasis; do not spread it.
- Choose an Arabic display face for titles and a text face for everything else, and a Latin partner (see the typography reference in the `arabic-rtl-web` skill if available). Load only the weights used.
- Decide one recurring visual device (a shape, a rule, a numeral treatment) and use it consistently rather than decorating each slide differently.
- Dark themes suit large rooms and screens; light themes suit printing and bright rooms. Ask how it will be shown if that is unknown.
- Keep at least 90px of margin on the 1600 by 900 stage. Projectors crop.
- Check contrast: body text at 4.5:1 or better against its background.

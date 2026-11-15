# Motion

"Cinematic" means controlled: a consistent camera, deliberate pacing, nothing moving without a reason. It does not mean more animation.

## Contents
- Principles
- Direction-aware motion
- Timing
- Step reveals
- Effects worth using
- Effects to avoid
- Reduced motion and print

## Principles

1. **Motion explains.** A transition shows where the next slide sits relative to this one. A reveal shows the order of an argument. A bar growing shows magnitude. If a movement explains nothing, remove it.
2. **One vocabulary.** Pick one slide transition and one entrance for content. Use them everywhere.
3. **The speaker sets the pace.** Nothing auto-advances. Entrances finish within about a second so the speaker is never waiting for the slide.
4. **Stillness is the default.** Once a slide has arrived, it holds still while people read.

## Direction-aware motion

Reading direction is the direction of "forward". In Arabic, the next slide arrives from the left and the previous one leaves to the right; in English the reverse. The engine does this with one variable:

```css
:root { --dir: 1; }
[dir="rtl"] { --dir: -1; }

.slide           { --shift: 70px; transform: translateX(calc(var(--dir) * var(--shift))) scale(var(--scale)); }
.slide.is-past   { --shift: -70px; }
.slide.is-active { --shift: 0px; }
```

Rules:

- Every horizontal `translate` is multiplied by `--dir`.
- `transform-origin`, `translateX`, `rotate` and `skew` are physical. Bars and progress indicators grow with `inline-size`, which follows direction, not with `scaleX` from a `left` origin.
- Arrows and chevrons that mean "next" or "leads to" use `transform: scaleX(var(--dir))`.
- Wipes and clip-path reveals start at the inline start: `clip-path: inset(0 0 0 100%)` reveals from the right edge and needs the opposite inset in English. Set the inset with a `[dir]` selector.
- Staggered items enter in reading order. DOM order already is reading order, so stagger by index.
- Vertical motion, opacity, scale and blur are direction-neutral. Prefer them when in doubt.
- Keyboard and swipe follow the same logic: Left arrow advances in Arabic.

## Timing

| Motion | Duration | Easing |
|---|---|---|
| Slide transition | 500 to 700 ms | `cubic-bezier(.2, .7, .2, 1)` (fast start, soft landing) |
| Content entrance, step reveal | 400 to 500 ms | same, or `ease-out` |
| Stagger between sibling items | 60 to 120 ms | |
| Bar or number growth | 800 to 1000 ms, after a 200 ms delay | same |
| Emphasis (a highlight appearing) | 200 to 300 ms | `ease-out` |

Distances are small: 16 to 70 px on the 1600 by 900 stage. Large travel reads as a gimmick. Do not use bounce or elastic easing in executive material.

## Step reveals

`data-step` hides an element until the speaker advances. Use it when:

- the speaker will talk through items one at a time and showing all of them would let the room read ahead;
- a conclusion should land after its evidence;
- a chart gains a highlight or an annotation at the moment it is discussed.

Do not step every bullet on every slide. A slide read alone, or sent as a PDF, shows all steps, so the slide must also work fully revealed.

To reveal a group together, wrap it in one element with `data-step`. To stagger children within one step:

```css
[data-step].is-shown > * { animation: rise .45s both; }
[data-step].is-shown > :nth-child(2) { animation-delay: .08s; }
[data-step].is-shown > :nth-child(3) { animation-delay: .16s; }
@keyframes rise { from { opacity: 0; transform: translateY(14px); } }
```

## Effects worth using

- **Cross-fade with a short directional shift** between slides (the engine default).
- **Rise and fade** for content entering.
- **Growth** for bars and progress, tied to the slide becoming active.
- **Count-up** on one headline number per deck at most, under a second, ending on the exact formatted value. Format with a fixed numbering system so digits do not change script mid-count.
- **Highlight**: a colour or underline drawn onto the key word of a statement.
- **A slow ambient drift** on a title-slide background shape, under 5 percent of its size, paused when the slide is not active.

## Effects to avoid

- Different transitions on different slides.
- Text that types itself, spins, flips or flies across the stage.
- Letter-by-letter animation of Arabic. Splitting a word into letters breaks the joins and produces isolated letter forms. Animate words or lines.
- Parallax and continuous motion behind text.
- Auto-playing sequences longer than two seconds.
- Any motion on the slide that carries the request for a decision.

## Reduced motion and print

Both are part of the engine and must survive your edits:

```css
@media (prefers-reduced-motion: reduce) {
  .slide, [data-step], .bar .fill { transition: none !important; animation: none !important; }
  .slide { --shift: 0px; }
}
@media print {
  .slide { transform: none; opacity: 1; visibility: visible; break-after: page; }
  [data-step] { opacity: 1; transform: none; }
}
```

Every animated property needs a final state that is correct with no animation at all. Test by printing: if the PDF is right, reduced motion is right.

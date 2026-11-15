---
name: arabic-html-slides
description: Create cinematic, presentation-ready HTML slide decks in Arabic, English or both - a single self-contained file with keyboard navigation that follows reading direction, step reveals, direction-aware motion, a language toggle, speaker notes and clean PDF export. Use when the user asks for an HTML presentation, slides or a deck that includes Arabic or must be bilingual, an executive briefing in Arabic, or mentions عرض تقديمي, شرائح, عرض تنفيذي. Not for PowerPoint (.pptx) files. Includes a deck engine template, a storyline method and scripts that check the result.
license: MIT
compatibility: Bundled scripts need Python 3.9+ (standard library only). The guidance works without them.
metadata:
  author: malenezi
  version: "1.0.0"
---

# Arabic and bilingual HTML presentations

A deck succeeds when the audience can repeat its message afterwards. Animation, typography and layout serve that, in this order: storyline, then slides, then motion. Build in that order too.

## Workflow

1. **Get the brief.** Who decides, what should they do after the last slide, how long is the slot, will it be presented live or read alone, which language is primary. If the user did not say, assume a live executive briefing, Arabic primary, and state the assumption.
2. **Write the storyline before any HTML.** One governing message, then the slide titles as full sentences that read as an argument when listed alone. Method and Arabic examples: [references/storytelling.md](references/storytelling.md). For anything longer than six slides, show the user the title list first if they are present.
3. **Choose a layout per slide** from [references/slide-patterns.md](references/slide-patterns.md). One idea per slide. Vary the layouts; do not repeat the same one three times in a row.
4. **Build from `assets/deck-starter.html`.** Keep the engine (script, `.deck` and `.slide` rules, print and reduced-motion blocks). Replace the theme tokens, fonts and content. Design the theme for this deck's subject; the starter's look is a placeholder.
5. **Add motion last**, following [references/motion.md](references/motion.md): one entrance style, steps only where the speaker needs to pace the room.
6. **Verify** with the scripts below, then page through the whole deck in each language.

## What the engine gives you

- A 1600 by 900 stage scaled to any window, so sizes are in plain pixels and print is predictable.
- Navigation that follows reading direction: in Arabic the Left arrow advances. Space, Page Up/Down, Home, End, touch swipe and click also work.
- `data-step` on any element reveals it on the next advance.
- `L` switches language (and direction), `F` full screen, `N` speaker notes, `P` print. `?lang=en` and `#5` deep-link.
- Paired variants for bilingual content: `<span data-lang="ar">…</span><span data-lang="en">…</span>`; attributes via `data-ar-aria-label` / `data-en-aria-label`.
- Print styles that export one slide per page with all steps shown: print to PDF from the browser, with background graphics on.
- `prefers-reduced-motion` support and a live region announcing each slide title.

For an Arabic-only or English-only deck, delete the other variants and the `L` handler, and set `lang` and `dir` on `<html>`.

## Rules for Arabic decks

- Titles are complete sentences stating the point: «ارتفع الإتمام 9 نقاط بعد تقصير المختبرات», not «نسبة الإتمام».
- Arabic display type needs room: line-height 1.4 or more for headings, 1.7 or more for text. No letter-spacing, italics or uppercase on Arabic; scope those to `:lang(en)`.
- Minimum text size on the 1600 by 900 stage: 28px for content, 20px for source lines and counters. If text does not fit, cut words or split the slide. Never shrink.
- Numbers: one digit system for the whole deck. Isolate anything with a sign, a slash, a range or a unit symbol: `<bdi dir="ltr">+9</bdi>`, `<bdi dir="ltr">4.6 / 5</bdi>`.
- Sequences run in reading order: timelines, process steps and before/after start on the right in Arabic. Flex and grid do this automatically; arrows between items need `transform: scaleX(var(--dir))`.
- Charts: grow bars with `inline-size` from the inline start. Keep time-series axes consistent across the deck and say which way time runs if it could be misread.
- Horizontal motion is multiplied by `--dir`. `transform-origin` and `translateX` are physical.
- Both languages say the same thing with the same numbers. English is written as English, Arabic as Arabic; neither is a word-for-word copy.

## Verify

```bash
python scripts/bidi_lint.py deck.html --profile deck    # direction, bidi, type, plus deck checks
python scripts/i18n_parity.py deck.html                 # bilingual decks: every variant has its pair
```

The deck profile adds: reduced-motion support, print styles, keyboard handling, a heading on every slide, and a flag on slides with too many words. Fix errors and warnings.

Then check by eye, in each language:

- Read only the titles in order. Do they make the argument?
- Does every slide pass the three-second test: is the point visible before the speaker explains it?
- Do steps reveal in the order the speaker will talk?
- Does anything clip, overlap or wrap awkwardly? Arabic and English lengths differ.
- Print preview: one slide per page, nothing cut off.

If the scripts cannot run in the current environment, say so and do the manual checks.

## Reference files

| File | Read it when |
|---|---|
| [references/storytelling.md](references/storytelling.md) | Structuring the argument, writing titles, executive conventions in Arabic |
| [references/slide-patterns.md](references/slide-patterns.md) | Picking and building layouts: statement, numbers, chart, comparison, timeline, quote, ask |
| [references/motion.md](references/motion.md) | Transitions, step reveals, direction-aware animation, restraint |

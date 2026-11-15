# Roadmap

Priorities, not promises. Open an issue to argue for a different order.

## 1.1: sharpen what exists

- `bidi_lint`: optional `--fix` for the safe conversions (`margin-left` to `margin-inline-start`, Tailwind `ml-` to `ms-`, Latin to Arabic punctuation)
- `bidi_lint`: detect four-value shorthands with unequal sides (`padding: 0 8px 0 16px`)
- `bidi_lint`: SARIF output for code-scanning annotations; a pre-commit hook definition
- `i18n_parity`: ICU plural completeness (all six Arabic categories present)
- JavaScript checks: `scrollLeft`, `offsetLeft`, placement strings, arrow-key handlers
- More deck layouts: quote, matrix, table, image with caption; a both-languages-visible print mode

## 1.2: more of the Arabic-first surface

- `arabic-email-html`: bilingual HTML email, where `dir` attributes and table layout are still required
- `arabic-data-viz`: chart direction, axis and legend conventions, number formatting, with SVG templates
- `arabic-docs`: RTL in Markdown, PDF and Word output
- Framework recipes as references: Next.js, Tailwind 4, React Native, Flutter

## 2.0: beyond Arabic

- Hebrew, Persian and Urdu: typography references, glossaries and digit rules per language, with native-speaker maintainers
- Regional Arabic profiles: Gulf, Levant, Egypt and Maghreb terminology and month names as selectable options
- An evaluation set: prompts with scoring scripts, so changes to a skill can be measured rather than judged by eye

## Ongoing

- Glossary growth by sector: government, banking, health, education, e-commerce
- Verifying reference claims against new browser releases
- Keeping pace with the Agent Skills specification

## Not planned

- A runtime JavaScript library. The goal is correct source, not a client-side patch.
- Machine translation. The writing skill is about producing Arabic a writer would sign.

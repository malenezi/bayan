---
name: arabic-rtl-web
description: Build Arabic and bilingual Arabic/English websites, landing pages and web UI that are correct in both directions - RTL/LTR layout with CSS logical properties, bidirectional text isolation, Arabic typography, language switching, numerals and dates. Use when the user asks for an Arabic site or page, a bilingual or multilingual page that includes Arabic (or Hebrew, Persian, Urdu), RTL support, a language toggle, or mentions موقع عربي, صفحة هبوط, ثنائي اللغة, من اليمين إلى اليسار. Includes a starter template and scripts that lint the result.
license: MIT
compatibility: Bundled scripts need Python 3.9+ (standard library only). The guidance works without them.
metadata:
  author: malenezi
  version: "1.0.0"
---

# Arabic and bilingual web

Arabic pages built by translating an English design usually ship the same defects: mirrored where they should not be, not mirrored where they should, phone numbers scrambled, tracked-out headings with broken letter joins, and stiff translated copy. This skill prevents those defects and then proves it with a linter.

Design the Arabic experience first. If Arabic works, English is easy; the reverse is not true.

## Workflow

1. **Pick the architecture** before writing markup. Read [references/architecture.md](references/architecture.md) if the choice is not obvious.
   - One self-contained file with a language toggle: use the paired-variant pattern in `assets/starter-bilingual.html`.
   - A public site that must rank in search: one URL per language (`/ar/`, `/en/`) with `hreflang`.
   - An existing framework app: route-level locale, `dir` on `<html>`, logical utilities.
2. **Set language and direction at the root**: `<html lang="ar" dir="rtl">`. Direction lives in markup, never in CSS `direction`.
3. **Choose the type system** from [references/typography.md](references/typography.md): an Arabic face chosen for the voice of the brand, a Latin partner matched by weight and proportion, Arabic body line-height 1.7 to 1.9.
4. **Lay out with logical properties only** (`margin-inline-start`, `inset-inline-end`, `text-align: start`). Flexbox and grid then mirror by themselves. See [references/layout-mirroring.md](references/layout-mirroring.md) for the full mapping and for what must not mirror.
5. **Isolate every LTR run inside Arabic text**: phone numbers, emails, URLs, code, ranges, handles, product names with symbols. Wrap them in `<bdi dir="ltr">`. Details and edge cases: [references/bidi-text.md](references/bidi-text.md).
6. **Format numbers, dates and currency deliberately**: decide one digit system for the whole product and say so in code. `Intl` with `ar-SA` silently switches to Arabic-Indic digits, and on some browsers to the Hijri calendar. See [references/numbers-dates-forms.md](references/numbers-dates-forms.md).
7. **Write the Arabic copy as Arabic**, not as a translation: natural Modern Standard Arabic, Arabic punctuation (، ؛ ؟), no stretched letters. If the `arabic-ux-writing` skill is available, use it for interface text.
8. **Verify** (next section) and fix everything the tools report before showing the result.

## Rules that are never optional

- `lang` and `dir` on `<html>`; `dir` again on any element whose language changes direction.
- No physical CSS (`left`, `right`, `margin-left`, `text-align: left`, `float: right`) unless it sits under an explicit `[dir]` selector for a reason you can state.
- No `letter-spacing`, no italics, no uppercase styling on Arabic. Scope those to Latin with `:lang(en)`.
- LTR inputs (`email`, `tel`, `url`, `number`, `password`) carry `dir="ltr"`; free-text inputs that may receive either language carry `dir="auto"`.
- Icons that imply direction (back, next, chevrons, progress, reply) mirror. Icons that depict objects or time (play, clock, checkmark, search, logos) do not.
- Horizontal motion is multiplied by a direction variable: `--dir: 1` for LTR, `--dir: -1` for RTL.
- The language switcher names the *other* language in that language (`English` / `العربية`), never a flag, and sets both `lang` and `dir`.
- Both languages carry the same content. Nothing is "English only for now".

## Starter

`assets/starter-bilingual.html` is a complete single-file page: design tokens, direction-aware components, the paired-variant pattern, a toggle that persists the choice and honours `?lang=`, and translated attributes. Copy it, then replace content and restyle; keep the mechanics.

The paired-variant pattern in one line:

```html
<h1><span data-lang="ar">منصة واحدة لكل فريقك</span><span data-lang="en">One platform for your whole team</span></h1>
<input type="search" data-ar-placeholder="ابحث" data-en-placeholder="Search" dir="auto">
```

CSS hides the variant that does not match `<html lang>`; the script copies `data-<lang>-<attr>` into the real attribute.

## Verify

Run both scripts on every page you produce and fix what they report. They need only Python.

```bash
python scripts/bidi_lint.py path/to/page.html          # direction, bidi, typography, CSS
python scripts/i18n_parity.py path/to/page.html        # Arabic and English in step
python scripts/i18n_parity.py --pages ar/index.html en/index.html   # two-page sites
python scripts/i18n_parity.py --json ar.json en.json   # dictionaries
```

`bidi_lint.py --list-rules` prints every rule with its fix. Errors must be fixed. Warnings must be fixed or silenced on purpose with a `bidi-lint-ignore` comment on that line and a reason. Info findings are prompts to look, not defects.

Then check what no script can see, in both directions and at a narrow and a wide width:

- Does anything overlap, clip or wrap badly when Arabic strings are longer or shorter than English?
- Do directional icons point the way the reader moves?
- Do mixed-language lines read in the right order?
- Is the Arabic something a native reader would have written?

If scripts cannot run in the current environment, walk the rule list in [references/bidi-text.md](references/bidi-text.md) and [references/layout-mirroring.md](references/layout-mirroring.md) by hand and say that the automated check was not run.

## Reference files

| File | Read it when |
|---|---|
| [references/architecture.md](references/architecture.md) | Choosing single-file vs two-page vs framework; SEO; language switching |
| [references/bidi-text.md](references/bidi-text.md) | Any mixed Arabic/Latin text, numbers in text, user-generated content |
| [references/layout-mirroring.md](references/layout-mirroring.md) | Writing CSS or Tailwind; deciding what mirrors |
| [references/typography.md](references/typography.md) | Choosing and pairing fonts; sizes, line-height, emphasis |
| [references/numbers-dates-forms.md](references/numbers-dates-forms.md) | Numbers, currency, dates, calendars, plurals, forms, search and sorting |

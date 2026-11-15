---
name: rtl-audit
description: Audit and fix existing websites, apps, components and stylesheets for Arabic and right-to-left support - finds physical CSS and Tailwind classes, missing dir and lang, unisolated phone numbers and Latin runs, letter-spacing and font problems on Arabic, wrong punctuation and digit mixing, then applies fixes and reports. Use when the user asks to add RTL or Arabic support to an existing codebase, review or QA an Arabic or bilingual page, find out why Arabic text or layout looks broken or reversed, convert CSS to logical properties, or mentions تدقيق, مراجعة الواجهة العربية, دعم RTL.
license: MIT
compatibility: Bundled scripts need Python 3.9+ (standard library only). Works on HTML, CSS/SCSS, JSX/TSX/Vue/Svelte class names, and JSON/Markdown/text content.
metadata:
  author: malenezi
  version: "1.0.0"
---

# RTL and Arabic audit

Find what is wrong with an existing interface in Arabic or any right-to-left language, fix it in the right order, and leave a report someone else can act on. The scripts find the mechanical defects; you supply judgment for false positives and for what tools cannot see.

## Workflow

1. **Scope.** Establish what to audit (files, a directory, a built `dist/`), which languages the product must support, and whether you are asked to report only or to fix as well. If unclear, report first and offer the fixes.
2. **Scan.**
   ```bash
   python scripts/bidi_lint.py <paths> --format md        # full report, grouped by rule
   python scripts/bidi_lint.py <paths> --format json      # when you need to process findings
   ```
   Point it at source and, where one exists, at built HTML: templates hide the final markup. Add `--profile deck` for presentations. For bilingual content also run the parity check that matches the project (see the last section).
3. **Triage.** Read [references/rule-catalog.md](references/rule-catalog.md) for any rule you are not sure about. Sort findings into: fix now (errors, then warnings), intentional (keep, and silence with a comment), and look-at-it (info). Do not report a finding you have not understood.
4. **Look at what the scanner cannot see.** Work through [references/manual-checklist.md](references/manual-checklist.md): mirrored and unmirrored icons, component behaviour, JavaScript that assumes left-to-right, content quality. If you can render the page, view it at `dir="rtl"` at a narrow and a wide width.
5. **Fix in dependency order**, because early fixes remove later findings:
   1. Root `lang` and `dir`; `dir` on language switches and LTR inputs.
   2. Physical CSS and utility classes to logical ones. Recipes: [references/fix-recipes.md](references/fix-recipes.md).
   3. Bidi isolation of LTR runs in Arabic text.
   4. Typography: font stack, line-height, letter-spacing and italics scoped to Latin.
   5. Directional icons and motion.
   6. Content: punctuation, digits, tatweel.
6. **Re-scan** until errors and unexplained warnings are gone. Confirm the LTR version still looks the same: logical properties must not change English layout.
7. **Report** using `assets/report-template.md`: what was found, what was fixed, what remains and why, and what needs a human decision.

## Triage guidance

- **Errors** (`BD101` to `BD103`) are always real. Fix them first; several other rules only make sense once direction is declared.
- **Physical CSS** (`BD201`, `BD202`, `BD301`): real unless the rule sits under a direction selector or the value is symmetric. The scanner already exempts `left: 0; right: 0` pairs, centering, and `[dir]`-scoped rules. In third-party or generated CSS, do not edit: override or upgrade the dependency, and say so.
- **`BD107` unisolated runs**: check that the text really is shown in an RTL context. Template placeholders and test fixtures are common false positives.
- **`BD204` letter-spacing, `BD205` italics**: real when the selector can match Arabic text. If the element only ever holds Latin (a code badge, a logo wordmark), scope the selector with `:lang(en)` rather than ignoring the finding.
- **`BD209`, `BD210`, `BD115` (info)**: each needs a look. A decorative background position may not matter; a slide-in drawer does.
- **`BD109` mixed digits**: ask which system the product uses before converting.

Silence an intentional case where it lives, with a reason:

```css
.scrubber { left: 0; } /* bidi-lint-ignore: media timeline stays LTR */
```

`bidi-lint-disable BD201` anywhere in a file turns that rule off for the file. Use it for vendored files only.

## Converting a codebase

For more than a handful of files:

- Convert shared tokens, mixins and base components first; most findings disappear with them.
- Change one category at a time (all margins, then all insets) so each diff is reviewable.
- Do not add an `rtl.css` override sheet or a build-time flipping tool on top of logical properties. Pick one mechanism. Logical properties are the durable one.
- Mechanical replacement is safe for `margin-left` to `margin-inline-start` style changes. It is not safe for `left`/`right` inside animations, for transforms, or for JavaScript that reads `offsetLeft` or `scrollLeft`: review those by hand.
- After conversion, add the scan to CI with `--strict` so regressions fail the build.

## Parity checks for bilingual projects

```bash
python scripts/i18n_parity.py --json locales/ar.json locales/en.json    # message catalogues
python scripts/i18n_parity.py --pages ar/index.html en/index.html       # two-page static sites
python scripts/i18n_parity.py page.html                                 # single file with data-lang pairs
```

It reports missing keys, empty and untranslated strings, placeholder mismatches, and structural differences between language versions.

## Reference files

| File | Read it when |
|---|---|
| [references/rule-catalog.md](references/rule-catalog.md) | Deciding whether a finding is real and how to fix it |
| [references/manual-checklist.md](references/manual-checklist.md) | Reviewing what static analysis cannot see |
| [references/fix-recipes.md](references/fix-recipes.md) | Converting CSS, Tailwind and common components |
| `assets/report-template.md` | Writing the audit report |

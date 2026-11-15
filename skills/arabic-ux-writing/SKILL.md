---
name: arabic-ux-writing
description: Write and review Arabic interface text and transcreate English product copy into natural Modern Standard Arabic - buttons, labels, error and empty states, onboarding, notifications, landing-page and slide copy, and i18n string files, with consistent terminology, correct orthography and punctuation, and plural- and gender-safe phrasing. Use when the user asks to translate or localise a UI, app, website or strings file into Arabic, improve or proofread Arabic copy, build an Arabic glossary or style guide, or mentions تعريب, ترجمة الواجهة, صياغة, تدقيق لغوي, نصوص التطبيق. Not for literary or legal translation.
license: MIT
compatibility: Bundled scripts need Python 3.9+ (standard library only). The guidance works without them.
metadata:
  author: malenezi
  version: "1.0.0"
---

# Arabic UX writing and transcreation

Translated Arabic interfaces are usually understandable and still feel wrong: English sentence shapes, three different words for the same feature, a comma from the wrong alphabet. The goal here is Arabic that a native reader takes for the original.

Work from what the text is for, not from the English words. Read the English to learn the intent, then write the Arabic a good Arabic product writer would have written for that screen.

## Workflow

1. **Establish the context.** Who reads this (public, employees, specialists), which region, how formal the brand is, which digit system, and whether a glossary or earlier Arabic already exists. If the user gave none of this, default to: Modern Standard Arabic, clear and warm without being casual, Western digits, masculine singular address where address is unavoidable. State the defaults you used.
2. **Fix the terminology first.** List every recurring term (features, objects, actions, statuses) and choose one Arabic rendering for each before writing sentences. Start from [references/glossary.md](references/glossary.md); follow an existing product glossary over it. Return the term list with the work.
3. **Write each string by its job.** Pattern and examples for each type are in [references/patterns.md](references/patterns.md): actions, labels, errors, confirmations, empty states, notifications, time and counts.
4. **Apply the style rules** in [references/style-guide.md](references/style-guide.md): register, address and gender, punctuation, numerals, diacritics, Latin terms inside Arabic.
5. **Proofread against** [references/common-mistakes.md](references/common-mistakes.md): hamza, taa marbuta, alef maqsura, tanween, attached particles, and the calques that mark a text as translated.
6. **Check mechanically** (below), then **deliver**: the strings in the format they arrived in, the term list, and a short note of anything you changed in meaning, could not resolve, or that needs a decision.

## Rules that are never optional

- One term per concept, everywhere. If "Dashboard" is «لوحة المعلومات» on one screen, it is never «لوحة التحكم» on another.
- Buttons and menu actions use the verbal noun: «حفظ»، «إلغاء»، «تسجيل الدخول». Not the imperative, not «قم بالحفظ».
- Arabic punctuation: `،` `؛` `؟`. No space before punctuation, one after.
- One digit system throughout.
- Placeholders, variables and markup survive exactly: `{name}`, `%s`, `{{count}}`, `<b>…</b>`. Reorder them to fit Arabic syntax; never translate or drop them.
- A sentence built around a variable must be correct for any value: unknown gender, any number, a Latin or an Arabic name. Rephrase until it is (see patterns: notifications and counts).
- Do not transliterate what has an established Arabic word; do not translate product and brand names.
- No tatweel for stretching, no decorative diacritics, no exclamation marks in errors.
- Never invent facts: if the English is ambiguous (is "Open" a verb or a status?), ask or flag it; do not guess silently.

## Check mechanically

```bash
python scripts/bidi_lint.py strings/ar.json          # punctuation, digit mixing, tatweel, bidi controls
python scripts/i18n_parity.py --json ar.json en.json # missing keys, untranslated strings, placeholder mismatches
python scripts/i18n_parity.py page.html              # HTML with data-lang pairs
```

The parity check reports keys missing on either side, values identical in both languages, Arabic values with no Arabic letters, and placeholders that differ. Fix every finding or explain it.

If scripts cannot run here, check the same four things by reading.

## Delivering a review

When asked to review existing Arabic rather than write it, return a table: the original, the proposed text, and the reason in a few words (terminology, calque, orthography, punctuation, clarity, tone). Group repeated problems once at the top instead of repeating the reason on every row. Do not rewrite strings that are already good.

## Reference files

| File | Read it when |
|---|---|
| [references/style-guide.md](references/style-guide.md) | Deciding register, address, punctuation, numerals, how to handle English terms |
| [references/patterns.md](references/patterns.md) | Writing a specific kind of string |
| [references/glossary.md](references/glossary.md) | Choosing the Arabic for common interface, technology and business terms |
| [references/common-mistakes.md](references/common-mistakes.md) | Proofreading; spotting translated-sounding Arabic |

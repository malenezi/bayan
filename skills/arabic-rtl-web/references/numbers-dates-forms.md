# Numbers, dates, plurals and forms

## Contents
- Decide the digit system first
- Formatting with Intl
- Currency and units
- Dates and calendars
- Plurals
- Forms
- Search and sorting

## Decide the digit system first

Arabic is written with two digit sets: Western `0123456789` and Arabic-Indic `٠١٢٣٤٥٦٧٨٩`. Both are correct Arabic. Usage is regional and institutional:

- North Africa (Morocco, Algeria, Tunisia, Libya) uses Western digits.
- The Gulf and the Levant use both; most digital products, banks and government portals show Western digits.
- Egypt and print media lean towards Arabic-Indic digits.

Ask the user or follow the brand's existing material. If nothing is specified, use Western digits and say so. Then apply that choice to every number on the page, including dates, prices, phone numbers, step counters and charts. Mixing the two sets is the defect; either set alone is fine.

Phone numbers, card numbers, codes and anything the user will retype stay in Western digits regardless.

## Formatting with Intl

Locale defaults differ by region and change between browser versions. `ar-SA` and `ar-EG` default to Arabic-Indic digits; `ar-AE`, the Maghreb locales and bare `ar` default to Western digits, and `ar-MA` also swaps the separators (`1.234.567,5`). Never rely on the default: name the numbering system.

```js
const nf = new Intl.NumberFormat("ar-SA-u-nu-latn");           // 1,234,567.5
const ni = new Intl.NumberFormat("ar-SA-u-nu-arab");           // ١٬٢٣٤٬٥٦٧٫٥
new Intl.NumberFormat("ar-SA-u-nu-latn", { style: "percent" }).format(0.45);        // 45٪ (Arabic percent sign)
new Intl.NumberFormat("ar-SA-u-nu-latn", { notation: "compact" }).format(1250000);  // 1.3 مليون
```

Formatted output contains invisible direction marks. Do not compare formatted strings or parse them back; keep the raw number.

To convert digits in static text:

```js
const toArabicIndic = s => s.replace(/\d/g, d => "٠١٢٣٤٥٦٧٨٩"[d]);
const toWestern    = s => s.replace(/[٠-٩]/g, d => "٠١٢٣٤٥٦٧٨٩".indexOf(d));
```

Accept both sets as input: normalise with `toWestern` before validating a phone number, amount or one-time code.

## Currency and units

- In Arabic the amount comes first and the currency after it: `1,250 ريال`, `1,250 ر.س`. In English: `SAR 1,250`.
- Let Intl place it: `new Intl.NumberFormat("ar-SA-u-nu-latn", { style: "currency", currency: "SAR" })`.
- Use the currency name or its Arabic abbreviation as text. A dedicated Saudi riyal symbol exists, but font support is still uneven; use it only with a font that carries the glyph and keep a text fallback.
- Units follow the number and are translated: `25 كم`, `3 دقائق`. Use `style: "unit"` where it fits.
- Write large round numbers with words: `3 ملايين`, `1.2 مليار`.

## Dates and calendars

Depending on the browser's locale data, `ar-SA` formats dates in the Hijri (Umm al-Qura) calendar or in the Gregorian one: older data gives Hijri, newer data Gregorian. State the calendar you want:

```js
const greg = new Intl.DateTimeFormat("ar-SA-u-ca-gregory-nu-latn", { dateStyle: "long" });   // 15 نوفمبر 2026
const hijri = new Intl.DateTimeFormat("ar-SA-u-ca-islamic-umalqura-nu-latn", { dateStyle: "long" });
const rel = new Intl.RelativeTimeFormat("ar", { numeric: "auto" });                          // rel.format(-1, "day") → أمس
```

- Gregorian month names differ by region: `يناير، فبراير…` in the Gulf and Egypt, `كانون الثاني، شباط…` in the Levant. The locale tag (`ar-SA`, `ar-JO`) selects them.
- Government and religious contexts often show both calendars: `15 نوفمبر 2026 م الموافق 5 جمادى الآخرة 1448 هـ`. Compute the Hijri date; never hard-code a conversion.
- The week starts on Sunday in Saudi Arabia and most of the Gulf, and on Saturday in Egypt. The weekend is Friday and Saturday in most Arab countries. Date pickers must follow the locale, not the library default.
- Time: 12-hour with `ص` and `م` is the usual display; `Intl` handles it.
- Put machine dates in `<time datetime="2026-11-15">` so the visible text can be localised freely.

## Plurals

Arabic has six plural categories: zero, one, two, few (3 to 10), many (11 to 99), other. A two-form `count === 1 ? a : b` produces wrong Arabic.

```js
const pr = new Intl.PluralRules("ar");
const files = { zero: "لا ملفات", one: "ملف واحد", two: "ملفان", few: "{n} ملفات", many: "{n} ملفًا", other: "{n} ملف" };
const label = n => files[pr.select(n)].replace("{n}", nf.format(n));
```

In message catalogues use ICU plural syntax with all six forms. When that is too heavy for the context, rephrase so the noun does not inflect: `عدد الملفات: 12`.

## Forms

- Labels sit above fields. This works in both directions and survives long Arabic labels.
- Field direction:
  - `email`, `tel`, `url`, `number`, `password`, one-time codes, card numbers: `dir="ltr"`. Keep the text aligned with the form by adding `text-align: end` only if the design calls for it; left-aligned LTR values inside an RTL form are normal and readable.
  - Names, addresses, search, comments: `dir="auto"`.
  - Fields that are always Arabic: inherit.
- Placeholders follow the field's direction. An Arabic placeholder in a `dir="ltr"` field aligns left; prefer a format hint (`name@example.com`) there.
- Required markers, help text and errors go at the inline start, under the field.
- Names: do not force first and last name. Arabic names commonly have three or four parts. A single full-name field is safest; if the system needs parts, label them clearly.
- Phone: store in E.164, show in an isolated LTR run, accept Arabic-Indic digits on input.
- Addresses: do not assume a postal code or a street number; national address formats vary.
- Validation that uses `\w` or `[A-Za-z]` rejects Arabic. Use Unicode property escapes: `/^[\p{L}\p{M}\s'.-]+$/u`.
- Multi-step forms: the stepper runs from the inline start; "next" is at the inline end of the button row and its arrow points in the reading direction.
- `maxlength` counts code units: Arabic with diacritics uses more than one per visible letter.

## Search and sorting

Users type Arabic loosely. Normalise both the query and the indexed text before matching:

```js
const normalizeArabic = s => s
  .normalize("NFKC")
  .replace(/[\u064B-\u065F\u0670\u0640]/g, "")   // diacritics and tatweel
  .replace(/[أإآٱ]/g, "ا")
  .replace(/ى/g, "ي")
  .replace(/ة/g, "ه")
  .replace(/ؤ/g, "و").replace(/ئ/g, "ي")
  .replace(/[٠-٩]/g, d => "٠١٢٣٤٥٦٧٨٩".indexOf(d));
```

Apply this to a search key only. Never store or display the normalised form.

Sort with a collator, not with code points: `list.sort(new Intl.Collator("ar").compare)`. The definite article `ال` is normally ignored when alphabetising names and titles; strip it for the sort key if the list calls for it.

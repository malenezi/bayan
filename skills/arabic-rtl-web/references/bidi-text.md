# Bidirectional text in practice

## Contents
- The one idea to hold on to
- What breaks, and the fix
- Choosing the isolation tool
- Plain-text contexts (titles, attributes, JSON)
- User-generated and unknown-direction content
- Punctuation and symbols
- Things that look like bidi bugs but are not

## The one idea to hold on to

The browser stores text in the order it is typed and decides display order per character. Arabic letters are strongly right-to-left, Latin letters strongly left-to-right. Digits, spaces and punctuation are **weak or neutral**: they take their direction from their neighbours and from the paragraph. Almost every bidi defect is a neutral character at the edge of an LTR run being claimed by the RTL paragraph.

The fix is always the same: **isolate** the run so its neutrals resolve against the run, not against the paragraph.

## What breaks, and the fix

All examples sit in an RTL paragraph.

| Content | Typed | Renders without isolation | Fix |
|---|---|---|---|
| International phone | `+966 11 123 4567` | groups reversed, plus at the far end | `<bdi dir="ltr">+966 11 123 4567</bdi>` |
| Spaced digit groups | `4000 1234 5678` | groups reversed | `<bdi dir="ltr">…</bdi>` |
| Range with dash | `10 – 20`, `2024-2026` | `20 – 10`, `2026-2024`: the start is on the right, which is Arabic reading order, but readers cannot tell which convention was meant | write it in words: `من 10 إلى 20`; isolate only when the LTR form is required |
| ISO or dashed date | `2026-11-15` | `15-11-2026` | isolate, or format with `Intl.DateTimeFormat` |
| Arithmetic | `5 + 3 = 8` | `8 = 3 + 5` | isolate |
| Term with symbols | `C++`, `C#`, `.NET` | `++C`, `#C`, `NET.` | `<bdi dir="ltr">C++</bdi>` |
| Handle, hashtag | `@bayan`, `#launch` | `bayan@`, `launch#` | isolate |
| URL or path | `example.com/docs/` | trailing slash jumps to the other side | isolate; in links put `dir="ltr"` on the `<a>` |
| Latin at line end + period | `نستخدم React.` | usually fine | no action |
| Version | `v2.0 (beta)` | bracket misplaced | isolate |
| File name | `report_final.pdf` | usually fine; isolate if followed by punctuation | isolate when in doubt |
| English sentence | a quoted English sentence | internal order fine, final punctuation misplaced | `<span lang="en" dir="ltr">…</span>` |

Plain integers, years, decimals (`3.4`, `1,250.50`), slash dates (`15/11/2026`) and times (`7:30`) are safe without isolation. A percentage typed `45%` shows the sign to the left of the digits, which is where Arabic puts it.

Why digits behave this way: after an Arabic letter, Western digits are treated as "Arabic numbers". A full stop, comma, colon or slash between them keeps the number together; a hyphen, dash, plus or space does not, so the pieces are laid out right to left. The same digits after a Latin letter behave differently, which is why the result can change when surrounding words change. Isolation removes the dependence on context.

The same defects appear in an LTR page when Arabic is embedded in English: isolate the Arabic run with `<bdi dir="rtl" lang="ar">`.

## Choosing the isolation tool

| Tool | Use for |
|---|---|
| `<bdi dir="ltr">` | A known-LTR run inside RTL text. First choice. |
| `<bdi>` (no dir) | A run whose direction you do not know: user names, titles from a database. Direction is taken from its first strong character and it cannot disturb its surroundings. |
| `<span lang="en" dir="ltr">` | A phrase in another language. `lang` also fixes font selection and screen-reader pronunciation. |
| `dir="auto"` on a block or input | A whole field or paragraph of unknown direction. |
| `unicode-bidi: isolate` / `plaintext` in CSS | Only when you cannot touch the markup. `plaintext` on a container gives each paragraph its own direction, useful for chat and comments. |

Do not use `<bdo>` or `unicode-bidi: bidi-override` except to display text deliberately reversed. Do not paste the legacy controls U+202A to U+202E into content; they do not isolate and they are a known source-spoofing vector.

## Plain-text contexts

Markup is unavailable in `<title>`, `alt`, `aria-label`, `placeholder`, `<option>`, push notifications, and strings in JSON. Use the invisible isolate characters there:

| Character | Code point | Meaning |
|---|---|---|
| LRI | U+2066 | start LTR isolate |
| RLI | U+2067 | start RTL isolate |
| FSI | U+2068 | start isolate, direction from first strong character |
| PDI | U+2069 | end isolate |

`"اتصل على \u2066+966 11 123 4567\u2069"` renders correctly anywhere. Insert them in code, not by hand, and keep them out of values that are compared, searched or used as identifiers.

The marks LRM (U+200E) and RLM (U+200F) are a weaker tool: an invisible strong character that pulls one adjacent neutral into line. Prefer isolates.

## User-generated and unknown-direction content

- Text inputs and textareas that can receive either language: `dir="auto"`. The field flips as the user types.
- Rendering stored user text: wrap each item in `<bdi>` or put `dir="auto"` on its block. A list of names then aligns each name by its own script without disturbing counters, timestamps or icons beside it.
- Never infer direction from the UI language. An Arabic interface shows English names all the time.
- When concatenating in code (`name + " " + count`), isolate each inserted value. Templates like `{user} أضاف {count} ملفات` break as soon as `user` is Latin and is followed by a digit.

## Punctuation and symbols

- Arabic uses its own comma `،`, semicolon `؛` and question mark `؟`. The full stop, colon and exclamation mark are shared.
- Parentheses and brackets are mirrored by the renderer. Type them in logical order; never swap `(` and `)` by hand.
- Quotation marks: `«…»` is traditional and reads well; `"…"` is common in digital products. Pick one.
- Percent: `45%` with Western digits. With Arabic-Indic digits use the Arabic percent sign: `٤٥٪`.
- Decimal and thousands separators with Arabic-Indic digits are `٫` and `٬`. With Western digits keep `.` and `,`.
- The ellipsis character `…` works in both directions. In CSS, `text-overflow: ellipsis` truncates at the logical end, which is the left edge in RTL: correct, leave it alone.
- Slashes in dates (`15/11/2026`) stay in typed order; a date written with spaces or dashes may not. Format dates with `Intl.DateTimeFormat` rather than by hand.

## Things that look like bidi bugs but are not

- **The cursor jumps when editing mixed text.** That is logical-order editing; every editor does it.
- **A line that starts with an English word still aligns right.** Alignment follows the paragraph direction, not the first word. Correct.
- **Numbers read left to right inside Arabic.** Arabic numbers are written most-significant digit on the left in both digit systems. Correct.
- **A lone English paragraph inside an Arabic page hugs the right edge.** It inherited RTL. Give that block `lang="en" dir="ltr"`.

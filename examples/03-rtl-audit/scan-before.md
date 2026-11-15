# RTL / bidi audit

1 file(s) checked: 2 error(s), 24 warning(s), 5 info

| Rule | Severity | Count | What | Fix |
|---|---|---:|---|---|
| BD101 | error | 1 | <html> has no lang attribute | Declare the language: <html lang="ar" dir="rtl">. |
| BD102 | error | 1 | RTL document without dir on <html> | Set dir="rtl" on <html>; do not rely on CSS direction or text-align. |
| BD105 | warning | 2 | LTR-only input not isolated | Add dir="ltr" (or dir="auto") to email/tel/url/number/password inputs inside RTL pages. |
| BD107 | warning | 4 | LTR run will reorder inside RTL text | Wrap it: <bdi dir="ltr">...</bdi> (or <span dir="ltr">). For ranges, words are clearer: من 10 إلى 20. |
| BD108 | warning | 2 | Latin punctuation after Arabic text | Use Arabic punctuation: ، (comma) ؛ (semicolon) ؟ (question mark). |
| BD201 | warning | 5 | physical box property | Use the logical equivalent (margin-inline-start, padding-inline-end, inset-inline-start, border-start-start-radius ...). |
| BD202 | warning | 3 | physical alignment keyword | Use start/end (text-align) or inline-start/inline-end (float, clear). |
| BD203 | warning | 1 | direction set in CSS | Direction is content, not style: use the dir attribute in markup. |
| BD204 | warning | 2 | letter-spacing reaches Arabic text | Tracking breaks Arabic joining. Scope it to Latin (:lang(en), [dir=ltr]) or reset to 0 for :lang(ar). |
| BD207 | warning | 1 | line-height too tight for Arabic body text | Arabic needs roughly 1.6-1.9 for body copy (1.2-1.4 for large headings). |
| BD208 | warning | 1 | font stack has no Arabic-capable family | Name an Arabic typeface first for Arabic content (e.g. 'IBM Plex Sans Arabic', 'Noto Kufi Arabic'), then fallbacks. |
| BD212 | warning | 1 | word-break: break-all on Arabic | break-all splits Arabic words mid-word. Use overflow-wrap: anywhere or scope break-all to Latin/code. |
| BD301 | warning | 2 | physical utility class | Use logical utilities: ms-/me-/ps-/pe-, start-/end-, text-start/text-end, rounded-s/e, border-s/e. |
| BD109 | info | 1 | mixed digit systems | Pick one digit system per product (Western 0-9 or Arabic-Indic ٠-٩) and apply it everywhere. |
| BD110 | info | 1 | tatweel (kashida) used to stretch text | Remove U+0640 runs; they break search, copy/paste and screen readers. Use CSS for emphasis. |
| BD111 | info | 1 | forward arrow points the wrong way in RTL | In RTL 'forward/next' points left. Use ← or a mirrored icon; keep → only for literal directions. |
| BD205 | info | 1 | italic reaches Arabic text | Arabic has no italic; browsers fake a slant. Scope italics to Latin and use weight or colour for Arabic emphasis. |
| BD209 | info | 1 | horizontal motion does not mirror | translateX keeps its sign in RTL. Multiply by a direction variable (--dir: 1 / -1) or override under [dir=rtl]. |

## Findings

### `before.html`

- **BD102** line 1 - document is mostly Arabic but <html> has no dir
- **BD101** line 2 - <html> has no lang attribute - `<html>`
- **BD202** line 7 - 'text-align: right' does not flip in RTL - `body { text-align: right }`
- **BD203** line 7 - direction: rtl set in CSS - `body { direction: rtl }`
- **BD207** line 7 - line-height: 1.3 on body text - `body { line-height: 1.3 }`
- **BD208** line 7 - no Arabic-capable family in this stack - `body { font-family: Inter, Helvetica, sans-serif }`
- **BD201** line 10 - 'margin-left' does not flip in RTL - use margin-inline-start - `.header nav a { margin-left: 24px }`
- **BD204** line 11 - letter-spacing: 0.04em is not scoped to Latin text - `h1 { letter-spacing: 0.04em }`
- **BD204** line 12 - letter-spacing: 0.15em is not scoped to Latin text - `.tag { letter-spacing: 0.15em }`
- **BD205** line 14 - font-style: italic is not scoped to Latin text - `.hero em { font-style: italic }`
- **BD201** line 15 - 'border-left' does not flip in RTL - use border-inline-start - `.card { border-left: 4px solid #6a5cff }`
- **BD201** line 15 - 'padding-left' does not flip in RTL - use padding-inline-start - `.card { padding-left: 28px }`
- **BD201** line 16 - 'right' does not flip in RTL - use inset-inline-end - `.card .status { right: 20px }`
- **BD212** line 17 - word-break: break-all reaches Arabic text - `.card .id { word-break: break-all }`
- **BD202** line 19 - 'float: left' does not flip in RTL - `.progress i { float: left }`
- **BD202** line 20 - 'float: left' does not flip in RTL - `.next { float: left }`
- **BD201** line 21 - 'left' does not flip in RTL - use inset-inline-start - `.drawer { left: 0 }`
- **BD209** line 21 - horizontal translate keeps its sign in RTL - `.drawer { transform: translateX(-100%) }`
- **BD108** line 33 - ',' after Arabic text - `اعرف اين شحنتك,`
- **BD108** line 34 - '?' after Arabic text - `هل تبحث عن شحنة? ادخل`
- **BD107** line 38 - range, date or expression (shows end-first in RTL) '2026-00417' is not isolated - `شحنة رقم NQ-2026-00417`
- **BD109** line 39 - 1 Arabic-Indic and 25 Western digits in Arabic text
- **BD107** line 39 - range, date or expression (shows end-first in RTL) '12 - 15' is not isolated - `ن الرياض إلى جدة · الوزن 12 - 15 كجم · الو`
- **BD107** line 41 - phone number '+966 11 555 0199' is not isolated - `للاستفسار اتصل على +966 11 555 0199 أو راسلنا`
- **BD107** line 41 - handle or hashtag '@nuqta_help' is not isolated - `1 555 0199 أو راسلنا على @nuqta_help`
- **BD111** line 42 - '→' in RTL text - `التفاصيل →`
- **BD105** line 46 - <input type="email"> inherits RTL
- **BD105** line 47 - <input type="tel"> inherits RTL
- **BD301** line 48 - 'ml-4' is physical - try the 'ms' form - `ml-4 text-left`
- **BD301** line 48 - 'text-left' is physical - try the 'start' form - `ml-4 text-left`
- **BD110** line 48 - 4 consecutive tatweel characters - `تتبّــــع`

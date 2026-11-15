# Example 03: auditing a broken Arabic page

**Skill:** `rtl-audit` · **Files:** [before.html](before.html), [scan-before.md](scan-before.md), [after.html](after.html)

## Prompt

> Our shipment-tracking page looks off in Arabic: the phone number is backwards and the layout feels like an English page with Arabic pasted in. Find out what's wrong and fix it.

## What the scan found

```bash
python ../../shared/scripts/bidi_lint.py before.html --format md > scan-before.md
```

`1 file(s) checked: 2 error(s), 24 warning(s), 5 info`

What a reader sees, most severe first:

1. The page has no `lang` or `dir`; direction is faked with CSS `direction: rtl`, so assistive technology reads it as an unknown-language LTR document (BD101, BD102, BD203).
2. The phone number renders as `0199 555 11 966+`, the weight range as `15 - 12`, and the support handle as `nuqta_help@` (BD107).
3. The heading is letter-spaced, which pulls Arabic letters apart, and the font stack has no Arabic face (BD204, BD208).
4. The card accent, status badge, progress fill and drawer are pinned with `left`/`right` and do not follow direction (BD201, BD202, BD209).
5. Copy: Latin comma and question mark, missing hamzas («اين»، «ادخل»), mixed digit systems, a stretched «تتبّــــع», and a "details" arrow pointing backwards (BD108, BD109, BD110, BD111).

## What was fixed

In dependency order, as the skill prescribes: root `lang`/`dir`; physical CSS to logical; isolation of the tracking number, phone and handle; an Arabic font stack with body leading and no tracking; direction-aware drawer; copy corrections. The form also gained labels, and the email and phone inputs `dir="ltr"`.

```bash
python ../../shared/scripts/bidi_lint.py after.html
# 1 file(s) checked: 0 error(s), 0 warning(s), 0 info
```

## Left for a human

- The scanner cannot confirm the visual result; the manual checklist in the skill covers icons, component behaviour and JavaScript.
- Digit system: the page mixed `12` and `٣`. The fix chose Western digits; confirm with the product owner.

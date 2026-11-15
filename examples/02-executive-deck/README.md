# Example 02: executive proposal deck

**Skill:** `arabic-html-slides` · **File:** [deck.html](deck.html)

## Prompt

> I'm presenting to our executive committee next week. We want approval to merge our seven customer-service channels into one platform. Fifteen minutes, Arabic, but two members prefer English so I need to be able to switch. Data: 41% of requests are repeated across channels, 3.4 days average to close, satisfaction 62% (down 9 points in two years); a time study showed agents spend 38% re-entering data, 27% looking up status, 22% actually solving, 13% other. Target: one day to close, 80% satisfaction in 12 months. Make it look serious, dark theme.

## What the skill decided

- Structure: situation, complication, resolution. Nine slides for fifteen minutes.
- Governing message on slide 5: «نافذة واحدة: سجلّ موحّد لكل مستفيد، أيًّا كانت القناة التي يختارها».
- Every title is a sentence. Read alone, the titles make the case.
- The chart slide highlights the one bar the title is about (22%).
- The last slide asks for three decisions instead of saying thank you.
- One accent colour, one recurring shape (the window arch on the title slide).
- Negative change is isolated: `<bdi dir="ltr">−9</bdi> نقاط في عامين`.

## Use it

Open `deck.html`. Left arrow advances in Arabic, right arrow in English. `L` switches language, `F` full screen, `N` notes, `P` prints to PDF (enable background graphics).

## Verify

```bash
python ../../shared/scripts/bidi_lint.py deck.html --profile deck
python ../../shared/scripts/i18n_parity.py deck.html
```

```
1 file(s) checked: 0 error(s), 0 warning(s), 0 info
64 pair(s)/element(s) checked: 0 problem(s)
```

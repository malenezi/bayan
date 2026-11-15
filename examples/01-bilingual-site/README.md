# Example 01: bilingual bookshop site

**Skill:** `arabic-rtl-web` · **Pattern:** one URL per language (pattern B)

## Prompt

> Build a small website for Dar Al-Warraq, an independent bookshop and publisher in historic Jeddah. Arabic is the main language, English second, and both need to be found on Google. Sections: hero, three recommended books with prices, weekly evening events, visit and contact with a newsletter signup. Editorial feel, not a tech startup.

## What the skill decided

- "Found on Google in both languages" means one page per language with `hreflang`, not a single toggled file.
- One stylesheet, logical properties only. No RTL override file.
- Naskh display type for Arabic and a matching serif for English, set through `:lang()` variables and applied at language boundaries.
- Western digits throughout; prices as `85 ريالًا` and `SAR 85`.
- Phone and email links carry `dir="ltr"`; times are written in words (`من 10:00 ص إلى 11:00 م`) so no range needs isolating.
- Each language is written natively: «كتبٌ تُقرأ على مهل» and "Books worth reading slowly" share an idea, not a word order.

## Files

```
site/ar/index.html   <html lang="ar" dir="rtl">
site/en/index.html   <html lang="en" dir="ltr">
site/assets/site.css shared
```

## Verify

```bash
python ../../shared/scripts/bidi_lint.py site/
python ../../shared/scripts/i18n_parity.py --pages site/ar/index.html site/en/index.html
```

```
3 file(s) checked: 0 error(s), 0 warning(s), 0 info
32 pair(s)/element(s) checked: 0 problem(s)
```

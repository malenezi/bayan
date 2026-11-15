# Architecture for bilingual sites

## Contents
- Three patterns and when to use each
- Pattern A: one file, paired variants
- Pattern B: one URL per language
- Pattern C: framework applications
- The language switcher
- Accessibility
- SEO checklist

## Three patterns and when to use each

| | A. Single file, paired variants | B. One URL per language | C. Framework with locale routing |
|---|---|---|---|
| Best for | Self-contained deliverables: a microsite sent as one file, a report, a prototype, a deck | Public marketing and institutional sites | Products and large sites |
| Search engines | See one page; the hidden language is poorly indexed | Each language indexed and targeted | Same as B |
| Works without JavaScript | Shows the default language | Yes | Depends on rendering |
| Content lives in | The HTML, both languages side by side | Two HTML files | Message catalogues |
| Check parity with | `i18n_parity.py page.html` | `i18n_parity.py --pages ar.html en.html` | `i18n_parity.py --json ar.json en.json` |

If the user wants "one HTML file" or will open the page from disk or email, use A. If the page must be found through search in both languages, use B or C.

## Pattern A: one file, paired variants

Both languages are in the DOM. Each translatable piece is a pair of siblings marked `data-lang`. CSS hides the pair member that does not match `<html lang>`.

```html
<html lang="ar" dir="rtl">
…
<h2><span data-lang="ar">خدماتنا</span><span data-lang="en">Our services</span></h2>

<p data-lang="ar">نبني منتجات رقمية تخدم الناس بلغتهم.</p>
<p data-lang="en">We build digital products that serve people in their language.</p>

<img src="team.jpg" data-ar-alt="فريق العمل في المكتب" data-en-alt="The team at the office">
<title data-ar-text="بيان | الرئيسية" data-en-text="Bayan | Home">بيان | الرئيسية</title>
```

```css
html[lang="ar"] [data-lang]:not([data-lang="ar"]),
html[lang="en"] [data-lang]:not([data-lang="en"]) { display: none !important; }
```

```html
<script>
(function () {
  var DIRS = { ar: "rtl", en: "ltr" }, root = document.documentElement, KEY = "site-lang";
  function stored() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function apply(lang) {
    if (!DIRS[lang]) lang = "ar";
    root.lang = lang;
    root.dir = DIRS[lang];
    var prefix = "data-" + lang + "-";
    document.querySelectorAll("*").forEach(function (el) {
      Array.prototype.slice.call(el.attributes).forEach(function (a) {
        if (a.name.indexOf(prefix) !== 0) return;
        var name = a.name.slice(prefix.length);
        if (name === "text") el.textContent = a.value; else el.setAttribute(name, a.value);
      });
    });
    try { localStorage.setItem(KEY, lang); } catch (e) {}
  }
  var wanted = new URLSearchParams(location.search).get("lang") || stored() || root.lang;
  root.lang = DIRS[wanted] ? wanted : "ar";          // before first paint
  root.dir = DIRS[root.lang];
  document.addEventListener("DOMContentLoaded", function () {
    apply(root.lang);
    document.querySelectorAll("[data-lang-switch]").forEach(function (b) {
      b.addEventListener("click", function () { apply(root.lang === "ar" ? "en" : "ar"); });
    });
  });
})();
</script>
```

Rules for this pattern:

- Put the script in `<head>` so `lang` and `dir` are set before first paint.
- A pair's members are adjacent siblings with the same tag. Pair at the smallest sensible level: a heading's inner span, a whole paragraph, a whole list item. Do not pair an entire section if only its text differs: shared structure stays shared.
- Variants do not need their own `lang` or `dir`: the visible one always matches the root.
- A phrase that stays in one language in both versions (a brand name, a quoted term) is not a variant. Mark it with `lang` and `dir` instead.
- Numbers, images and icons that are identical in both languages are written once.
- Text injected by script must come from the same pairs or from a small dictionary keyed by `root.lang`.
- The default language in the markup is the one shown without JavaScript. Make it the primary audience's language.

## Pattern B: one URL per language

```
/ar/index.html     <html lang="ar" dir="rtl">
/en/index.html     <html lang="en" dir="ltr">
/assets/site.css   one stylesheet, logical properties, :lang() for type
```

Each page lists every language version, itself included, plus a default:

```html
<link rel="alternate" hreflang="ar" href="https://example.com/ar/">
<link rel="alternate" hreflang="en" href="https://example.com/en/">
<link rel="alternate" hreflang="x-default" href="https://example.com/ar/">
<link rel="canonical" href="https://example.com/ar/">
```

- One stylesheet serves both. No `rtl.css` override file: logical properties make it unnecessary.
- Keep element `id`s identical across languages so anchors, scripts and analytics work in both.
- The switcher links to the same page in the other language, not to the other home page.
- Do not redirect by IP or `Accept-Language` without a visible way back, and never redirect crawlers.
- Arabic slugs (`/ar/خدماتنا`) are valid and readable; percent-encoding makes them ugly when shared. Pick one policy and keep it.

## Pattern C: framework applications

- Locale is a route segment (`/ar/…`, `/en/…`). The root layout renders `<html lang={locale} dir={locale === "ar" ? "rtl" : "ltr"}>` on the server so the first paint is correct.
- Messages live in catalogues (`ar.json`, `en.json`) with ICU plurals; Arabic needs all six plural forms.
- Styles use logical properties or logical utilities only. Do not branch styles on locale in JavaScript.
- Configure the component library's direction provider next to the `<html dir>`.
- Load fonts per locale so English pages do not download Arabic fonts and vice versa.
- Format numbers and dates through one helper that fixes the numbering system and calendar (see numbers-dates-forms.md).
- Test every route in both locales in CI: run `bidi_lint.py` on built HTML and `i18n_parity.py --json` on the catalogues.

## The language switcher

- Label it with the name of the language it switches **to**, written in that language: `English` on the Arabic page, `العربية` on the English page. Give that label the matching `lang` attribute.
- No flags: languages are not countries.
- Place it at the inline end of the header, where it lands on the left in Arabic and the right in English.
- It changes `lang` and `dir` together and keeps the user on the same content and scroll position.
- Remember the choice. Wrap storage access in `try/catch`; it can be unavailable.

## Accessibility

- `lang` drives screen-reader voice selection. A missing or wrong `lang` makes Arabic unreadable by assistive technology.
- Mark inline language changes: `<span lang="en" dir="ltr">`.
- Hidden variants use `display: none`, so they are removed from the accessibility tree. Do not hide them with opacity or off-screen positioning.
- Translate `alt`, `aria-label`, `title` and `placeholder` along with visible text.
- Focus order follows DOM order, which follows reading order in both directions when the layout uses flex and grid without `order` or `row-reverse`.
- Keyboard: in RTL, Left Arrow moves "forward" in horizontal widgets (tabs, carousels, sliders); Right Arrow moves back.

## SEO checklist

- [ ] One indexable URL per language, each with a self-referencing canonical
- [ ] Reciprocal `hreflang` links including `x-default`
- [ ] Translated `<title>`, meta description, Open Graph title, description and `og:locale` (`ar_SA`, `en_US`)
- [ ] Translated structured data
- [ ] Arabic content is real text, not images of text
- [ ] Sitemap lists both language URLs

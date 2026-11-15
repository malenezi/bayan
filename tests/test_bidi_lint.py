"""Unit tests for bidi_lint. Run: python -m unittest discover -s tests -v"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared", "scripts"))
import bidi_lint as bl  # noqa: E402


def lint(content, name="page.html", **kw):
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        return bl.lint_file(path, **kw)


def ids(findings):
    return [f.rule for f in findings]


def page(body="", css="", html_attrs='lang="ar" dir="rtl"'):
    return "<!doctype html><html %s><head><title>t</title><style>%s</style></head><body>%s</body></html>" % (html_attrs, css, body)


GOOD_CSS = "body{font-family:'IBM Plex Sans Arabic',sans-serif;line-height:1.8}"


class Structure(unittest.TestCase):
    def test_clean_page_has_no_findings(self):
        self.assertEqual(ids(lint(page("<p>مرحبًا بكم في المنصة.</p>", GOOD_CSS))), [])

    def test_missing_lang(self):
        self.assertIn("BD101", ids(lint(page("<p>hi</p>", html_attrs=""))))

    def test_rtl_lang_without_dir(self):
        self.assertIn("BD102", ids(lint(page("<p>نص</p>", GOOD_CSS, 'lang="ar"'))))

    def test_mostly_arabic_document_without_dir(self):
        self.assertIn("BD102", ids(lint(page("<p>هذا نص عربي طويل بلا اتجاه محدد</p>", GOOD_CSS, 'lang="en"'))))

    def test_undeclared_arabic_page_is_checked_as_rtl(self):
        f = ids(lint(page("<p>للاستفسار اتصل على +966 11 555 0199 في أي وقت</p>", GOOD_CSS, "")))
        self.assertIn("BD107", f)

    def test_lang_dir_mismatch(self):
        self.assertIn("BD103", ids(lint(page("<p>نص</p>", GOOD_CSS, 'lang="ar" dir="ltr"'))))

    def test_language_switch_needs_dir(self):
        self.assertIn("BD104", ids(lint(page('<p>نص <span lang="en">English phrase</span></p>', GOOD_CSS))))
        self.assertNotIn("BD104", ids(lint(page('<p>نص <span lang="en" dir="ltr">English phrase</span></p>', GOOD_CSS))))

    def test_ltr_inputs(self):
        self.assertIn("BD105", ids(lint(page('<input type="email">', GOOD_CSS))))
        self.assertNotIn("BD105", ids(lint(page('<input type="email" dir="ltr"><input type="tel" dir="auto">', GOOD_CSS))))
        self.assertNotIn("BD105", ids(lint(page('<input type="email">', html_attrs='lang="en" dir="ltr"'))))

    def test_align_attribute(self):
        self.assertIn("BD113", ids(lint(page('<td align="left">x</td>', GOOD_CSS))))

    def test_fragment_is_not_flagged_for_html_attrs(self):
        self.assertNotIn("BD101", ids(lint("<div><p>نص</p></div>")))


class Text(unittest.TestCase):
    def test_phone_number_reorders(self):
        f = lint(page("<p>اتصل بنا: +966 11 123 4567</p>", GOOD_CSS))
        self.assertIn("BD107", ids(f))

    def test_isolated_phone_is_fine(self):
        for wrap in ('<bdi>+966 11 123 4567</bdi>', '<span dir="ltr">+966 11 123 4567</span>', '<a dir="auto">+966 11 123 4567</a>'):
            self.assertNotIn("BD107", ids(lint(page("<p>اتصل بنا: %s</p>" % wrap, GOOD_CSS))), wrap)

    def test_ranges_expressions_handles(self):
        for s in ("من 10 – 20 مقعدًا", "الناتج 5 + 3 = 8", "تابعنا @bayan_dev", "نستخدم C++ يوميًا", "زر https://example.com/docs/", "تغيّر بمقدار -18% هذا الشهر",
                  "الفترة 2024-2026", "التاريخ 2026-11-15"):
            self.assertIn("BD107", ids(lint(page("<p>%s</p>" % s, GOOD_CSS))), s)

    def test_plain_numbers_and_words_are_fine(self):
        for s in ("لدينا 250 موظفًا", "بنسبة 45% هذا العام", "نعمل مع React و Python", "في عام 2026", "السعر 1,250.50 ريال", "في 15/11/2026 الساعة 7:30", "من 10 إلى 20"):
            self.assertNotIn("BD107", ids(lint(page("<p>%s</p>" % s, GOOD_CSS))), s)

    def test_ltr_document_not_checked_for_reordering(self):
        self.assertNotIn("BD107", ids(lint(page("<p>Call +966 11 123 4567</p>", html_attrs='lang="en" dir="ltr"'))))

    def test_english_variant_not_checked(self):
        body = '<p data-lang="ar">اتصل: <bdi dir="ltr">+966 11 123 4567</bdi></p><p data-lang="en">Call +966 11 123 4567</p>'
        self.assertNotIn("BD107", ids(lint(page(body, GOOD_CSS))))

    def test_latin_punctuation(self):
        self.assertIn("BD108", ids(lint(page("<p>مرحبا, كيف حالك?</p>", GOOD_CSS))))
        self.assertNotIn("BD108", ids(lint(page("<p>مرحبًا، كيف حالك؟ السعر 1,200</p>", GOOD_CSS))))

    def test_legacy_bidi_controls(self):
        self.assertIn("BD106", ids(lint(page("<p>نص \u202dABC\u202c</p>", GOOD_CSS))))

    def test_mixed_digits(self):
        self.assertIn("BD109", ids(lint(page("<p>لدينا ٢٥ فرعًا</p><p>و 30 مدينة</p>", GOOD_CSS))))
        self.assertNotIn("BD109", ids(lint(page("<p>لدينا 25 فرعًا</p><p>و 30 مدينة</p>", GOOD_CSS))))

    def test_tatweel_and_arrow(self):
        f = ids(lint(page("<p>مرحـــبًا</p><a>التالي →</a>", GOOD_CSS)))
        self.assertIn("BD110", f)
        self.assertIn("BD111", f)

    def test_code_and_script_are_skipped(self):
        body = "<pre>x = 5 + 3 = 8 #tag</pre><code>a → b</code><script>var a = '+966 11 123 4567';</script>"
        self.assertEqual(ids(lint(page(body, GOOD_CSS))), [])


class Css(unittest.TestCase):
    def css(self, css, **kw):
        return ids(lint(page("<p>نص</p>", GOOD_CSS + css), **kw))

    def test_physical_properties(self):
        f = self.css(".a{margin-left:8px;padding-right:1rem;left:0;border-top-left-radius:4px}")
        self.assertEqual(f.count("BD201"), 4)

    def test_logical_properties_pass(self):
        self.assertEqual(self.css(".a{margin-inline-start:8px;inset-inline-end:0;border-start-start-radius:4px;text-align:start}"), [])

    def test_symmetric_and_centering_exempt(self):
        self.assertEqual(self.css(".a{margin-left:auto;margin-right:auto}.b{left:0;right:0}.c{left:50%;transform:translateX(-50%)}"), [])

    def test_direction_scoped_rules_exempt(self):
        self.assertEqual(self.css('[dir="rtl"] .a{margin-left:8px;text-align:right}html:lang(en) .b{padding-left:4px}'), [])

    def test_text_align_float(self):
        self.assertEqual(self.css(".a{text-align:left}.b{float:right}").count("BD202"), 2)

    def test_direction_in_css(self):
        self.assertIn("BD203", self.css("body{direction:rtl}"))

    def test_letter_spacing(self):
        self.assertIn("BD204", self.css("h1{letter-spacing:.1em}"))
        self.assertNotIn("BD204", self.css("h1{letter-spacing:0}h2:lang(en){letter-spacing:.1em}[dir=ltr] h3{letter-spacing:2px}"))

    def test_letter_spacing_ignored_in_english_only_page(self):
        f = lint(page("<p>Hello</p>", "h1{letter-spacing:.1em}", 'lang="en" dir="ltr"'))
        self.assertNotIn("BD204", ids(f))

    def test_italic_and_break_all(self):
        f = self.css("em{font-style:italic}.x{word-break:break-all}")
        self.assertIn("BD205", f)
        self.assertIn("BD212", f)

    def test_tight_line_height(self):
        self.assertIn("BD207", ids(lint(page("<p>نص</p>", "body{font-family:Cairo;line-height:1.2}"))))
        self.assertNotIn("BD207", ids(lint(page("<p>نص</p>", GOOD_CSS + "h1{line-height:1.2}"))))

    def test_font_stack(self):
        self.assertIn("BD208", ids(lint(page("<p>نص</p>", "body{font-family:Inter,Helvetica,sans-serif;line-height:1.8}"))))
        self.assertIn("BD208", ids(lint(":lang(ar){font-family:Inter,sans-serif}", "a.css")))
        self.assertNotIn("BD208", ids(lint("body{font-family:Inter,sans-serif}[lang=ar]{font-family:'Noto Kufi Arabic',sans-serif}", "a.css")))

    def test_bare_lang_rule(self):
        self.assertIn("BD213", self.css(":lang(ar){font-family:'Cairo',sans-serif;line-height:1.8}"))
        self.assertNotIn("BD213", self.css(":lang(ar){--text:'Cairo';letter-spacing:0}[lang]{font-family:var(--text)}h1:lang(ar){line-height:1.4}"))

    def test_translate_x(self):
        self.assertIn("BD209", self.css(".in{transform:translateX(40px)}"))
        self.assertNotIn("BD209", self.css(".in{transform:translateX(calc(var(--dir)*40px))}.up{transform:translateY(20px)}"))

    def test_keyframes_and_media_are_parsed(self):
        f = self.css("@media (min-width:600px){.a{margin-left:1px}}@keyframes k{from{transform:translateX(-30px)}to{transform:none}}")
        self.assertIn("BD201", f)
        self.assertIn("BD209", f)

    def test_nested_css(self):
        self.assertIn("BD201", self.css(".card{color:red;.title{padding-left:2px}}"))

    def test_font_face_and_urls_do_not_confuse_parser(self):
        css = "@font-face{font-family:X;src:url('data:font/woff2;base64,AA{}==')}.a{background:url(a.png) no-repeat;margin-left:3px}"
        self.assertEqual(self.css(css).count("BD201"), 1)

    def test_inline_style(self):
        self.assertIn("BD201", ids(lint(page('<p style="margin-left:10px">نص</p>', GOOD_CSS))))

    def test_line_numbers(self):
        f = lint("a{color:red}\n\n.b{\n  margin-left: 4px;\n}\n", "s.css")
        self.assertEqual((f[0].rule, f[0].line), ("BD201", 4))

    def test_html_style_line_numbers(self):
        src = "<!doctype html>\n<html lang=\"ar\" dir=\"rtl\">\n<head><style>\nbody{font-family:Cairo;line-height:1.8}\n.x{float:left}\n</style></head><body><p>نص</p></body></html>"
        f = [x for x in lint(src) if x.rule == "BD202"]
        self.assertEqual(f[0].line, 5)


class Utilities(unittest.TestCase):
    def test_tailwind_physical(self):
        f = ids(lint(page('<div class="ml-4 pr-2 text-left rounded-l-lg md:left-4 border-r">نص</div>', GOOD_CSS)))
        self.assertEqual(f.count("BD301"), 6)

    def test_tailwind_logical_and_exemptions(self):
        cls = "ms-4 pe-2 text-start rounded-s-lg start-4 mx-auto ml-auto mr-auto left-0 right-0 left-1/2 rtl:ml-4 ltr:mr-2 placeholder-gray-400 leading-relaxed"
        self.assertNotIn("BD301", ids(lint(page('<div class="%s">نص</div>' % cls, GOOD_CSS))))

    def test_jsx(self):
        self.assertIn("BD301", ids(lint('export const A = () => <div className="pl-4 flex">x</div>', "A.tsx")))

    def test_directional_icon(self):
        self.assertIn("BD115", ids(lint(page('<i class="icon chevron-right"></i>', GOOD_CSS))))
        self.assertNotIn("BD115", ids(lint(page('<i class="icon chevron-right rtl:-scale-x-100"></i>', GOOD_CSS))))


DECK = """<!doctype html><html lang="ar" dir="rtl"><head><title>t</title><style>
body{font-family:Cairo;line-height:1.7}.slide{transition:opacity .3s}%s</style></head><body>
<section class="slide"><h1>عنوان</h1><p>نص قصير</p></section>
<section class="slide"><p>%s</p></section><script>%s</script></body></html>"""


class Deck(unittest.TestCase):
    def test_deck_profile_flags_missing_basics(self):
        f = ids(lint(DECK % ("", "كلمة " * 90, ""), profile="deck"))
        for rule in ("DK401", "DK402", "DK403", "DK404", "DK405"):
            self.assertIn(rule, f)

    def test_good_deck(self):
        css = "@media (prefers-reduced-motion:reduce){*{transition:none}}@media print{.slide{break-after:page}}"
        html = (DECK % (css, "نص", "addEventListener('keydown',()=>{})")).replace("<p>نص</p>", "<h2>ثانٍ</h2><p>نص</p>")
        self.assertEqual(ids(lint(html, profile="deck")), [])

    def test_deck_rules_off_in_web_profile(self):
        self.assertFalse([r for r in ids(lint(DECK % ("", "نص", ""))) if r.startswith("DK")])


class Cli(unittest.TestCase):
    def test_suppressions_select_ignore(self):
        css = "/* bidi-lint-disable BD201 */\n.a{margin-left:1px;float:left}\n.b{float:right} /* bidi-lint-ignore */\n"
        self.assertEqual(ids(lint(css, "a.css")), ["BD202"])
        self.assertEqual(ids(lint(".a{margin-left:1px;float:left}", "a.css", select={"BD202"})), ["BD202"])
        self.assertEqual(ids(lint(".a{margin-left:1px;float:left}", "a.css", ignore={"BD202"})), ["BD201"])

    def test_exit_codes_and_formats(self):
        import contextlib
        import io
        import json
        with tempfile.TemporaryDirectory() as d:
            bad = os.path.join(d, "bad.html")
            ok = os.path.join(d, "ok.css")
            for path, content in ((bad, page("<p>نص</p>", GOOD_CSS, "")), (ok, ".a{margin-left:1px}")):
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(content)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                self.assertEqual(bl.main([bad, "--format", "json"]), 1)
            self.assertIn("BD101", [f["rule"] for f in json.loads(buf.getvalue())["findings"]])
            with contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(bl.main([ok]), 0)
                self.assertEqual(bl.main([ok, "--strict"]), 1)
                self.assertEqual(bl.main([d, "--format", "md"]), 1)
            self.assertIn("| BD201 |", out.getvalue())
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(bl.main([os.path.join(d, "nope.html")]), 2)
                self.assertEqual(bl.main([ok, "--select", "XX999"]), 2)

    def test_every_rule_has_metadata(self):
        for rid, (sev, title, hint) in bl.RULES.items():
            self.assertRegex(rid, r"^(BD|DK)\d{3}$")
            self.assertIn(sev, bl.SEV_ORDER)
            self.assertTrue(title and hint)

    def test_plain_text_files(self):
        self.assertIn("BD108", ids(lint('{"greeting": "مرحبا, بك"}', "ar.json")))
        self.assertIn("BD107", ids(lint("هاتف: +966 11 123 4567\n", "copy.txt")))
        self.assertEqual(ids(lint("Use `a → b` here.\n\n```\nمرحبا, x\n```\n", "doc.md")), [])


if __name__ == "__main__":
    unittest.main()

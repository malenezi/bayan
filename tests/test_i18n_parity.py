"""Unit tests for i18n_parity."""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared", "scripts"))
import i18n_parity as ip  # noqa: E402


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, name, content):
        path = os.path.join(self.tmp.name, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content if isinstance(content, str) else json.dumps(content, ensure_ascii=False))
        return path

    def codes(self, problems):
        return sorted(p.code for p in problems)


class Variants(Base):
    def check(self, body):
        return ip.check_variants(self.write("p.html", "<html><body>%s</body></html>" % body))

    def test_good_pairs(self):
        p, n = self.check('<h1><span data-lang="ar">مرحبًا</span><span data-lang="en">Welcome</span></h1>'
                          '<p data-lang="ar">نص عربي</p><p data-lang="en">English text</p>'
                          '<button data-ar-aria-label="إغلاق" data-en-aria-label="Close">×</button>')
        self.assertEqual((self.codes(p), n), ([], 3))

    def test_missing_sibling(self):
        p, _ = self.check('<p data-lang="ar">نص</p><div><p data-lang="en">Text</p></div>')
        self.assertEqual(self.codes(p), ["P01", "P01"])

    def test_untranslated_and_wrong_script(self):
        p, _ = self.check('<p data-lang="ar">Get started</p><p data-lang="en">Get started</p>'
                          '<p data-lang="ar">Hello there</p><p data-lang="en">Welcome</p>'
                          '<p data-lang="ar">أهلًا</p><p data-lang="en">أهلًا</p>')
        self.assertEqual(self.codes(p), ["P03", "P04", "P05"])

    def test_numbers_and_brands_may_match(self):
        p, _ = self.check('<b data-lang="ar">98%</b><b data-lang="en">98%</b>')
        self.assertEqual(self.codes(p), [])

    def test_empty_and_tag_mismatch(self):
        p, _ = self.check('<p data-lang="ar"></p><p data-lang="en">Text</p><h2 data-lang="ar">عنوان</h2><h3 data-lang="en">Title</h3>')
        self.assertEqual(self.codes(p), ["P02", "P08"])

    def test_hardcoded_attribute(self):
        p, _ = self.check('<p data-lang="ar">نص</p><p data-lang="en">Text</p><input placeholder="Search"><img alt="" src="a.png">')
        self.assertEqual(self.codes(p), ["P09"])

    def test_attribute_pair_missing(self):
        p, _ = self.check('<img data-ar-alt="شعار" src="a.png">')
        self.assertEqual(self.codes(p), ["P01"])

    def test_language_switch_labels_and_ltr_fields_are_exempt(self):
        p, _ = self.check('<button><span data-lang="ar" lang="en">English</span><span data-lang="en" lang="ar">العربية</span></button>'
                          '<input type="email" dir="ltr" placeholder="name@example.com">')
        self.assertEqual(self.codes(p), [])

    def test_no_variants(self):
        p, _ = self.check("<p>Text</p>")
        self.assertEqual(self.codes(p), ["P00"])


class Json(Base):
    def test_two_files(self):
        ar = self.write("ar.json", {"nav": {"home": "الرئيسية", "about": "من نحن"}, "hi": "مرحبًا {name}", "x": "X"})
        en = self.write("en.json", {"nav": {"home": "Home"}, "hi": "Hello {user}", "x": "X", "extra": "Extra"})
        p, n = ip.check_json([ar, en])
        self.assertEqual(self.codes(p), ["P01", "P01", "P06"])
        self.assertEqual(n, 3)

    def test_combined_shapes(self):
        a = self.write("a.json", {"ar": {"t": "عنوان"}, "en": {"t": "Title"}})
        b = self.write("b.json", {"t": {"ar": "عنوان", "en": "Title"}, "s": {"ar": "Save", "en": "Save"}})
        self.assertEqual(self.codes(ip.check_json([a])[0]), [])
        self.assertEqual(self.codes(ip.check_json([b])[0]), ["P03"])

    def test_length_outlier(self):
        a = self.write("c.json", {"k": {"ar": "نص", "en": "A very long English sentence that goes on and on for a while"}})
        self.assertEqual(self.codes(ip.check_json([a])[0]), ["P07"])


class Pages(Base):
    AR = '<html lang="ar" dir="rtl"><head><link rel="alternate" hreflang="ar" href="/ar/"><link rel="alternate" hreflang="en" href="/en/"></head><body><h1 id="top">عنوان</h1>%s</body></html>'
    EN = '<html lang="en" dir="ltr"><head><link rel="alternate" hreflang="ar" href="/ar/">%s</head><body><h1 id="top">Title</h1></body></html>'

    def test_matching_pages(self):
        ar = self.write("ar/index.html", self.AR % "")
        en = self.write("en/index.html", self.EN % '<link rel="alternate" hreflang="en" href="/en/">')
        self.assertEqual(self.codes(ip.check_pages(ar, en)[0]), [])

    def test_divergent_pages(self):
        ar = self.write("ar/index.html", self.AR % '<section id="pricing"><h2>الأسعار</h2></section>')
        en = self.write("en/index.html", (self.EN % "").replace('dir="ltr"', 'dir="rtl"'))
        self.assertEqual(self.codes(ip.check_pages(ar, en)[0]), ["P10", "P11", "P12", "P12", "P13"])


class Cli(Base):
    def test_exit_codes(self):
        import contextlib
        import io
        good = self.write("g.html", '<p data-lang="ar">نص</p><p data-lang="en">Text</p>')
        bad = self.write("b.html", '<p data-lang="ar">نص</p>')
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(ip.main([good]), 0)
            self.assertEqual(ip.main([bad]), 1)
            self.assertEqual(ip.main([]), 2)
            self.assertEqual(ip.main(["--json", os.path.join(self.tmp.name, "missing.json")]), 2)


if __name__ == "__main__":
    unittest.main()

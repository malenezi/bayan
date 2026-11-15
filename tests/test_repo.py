"""Repository-level checks: skills validate, copies are in sync, examples are clean."""
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "shared", "scripts"))
import bidi_lint  # noqa: E402
import i18n_parity  # noqa: E402
import validate_skills  # noqa: E402


def run(*args):
    return subprocess.run([sys.executable] + list(args), cwd=ROOT, capture_output=True, text=True)


class Skills(unittest.TestCase):
    def test_every_skill_passes_validation(self):
        names = [n for n in sorted(os.listdir(os.path.join(ROOT, "skills")))]
        self.assertGreaterEqual(len(names), 4)
        for name in names:
            failed = [c for c, ok, _ in validate_skills.check_skill(name) if not ok]
            self.assertEqual(failed, [], name)

    def test_plugin_manifests(self):
        self.assertEqual([c for c, ok, _ in validate_skills.check_plugin() if not ok], [])

    def test_validator_rejects_bad_frontmatter(self):
        with self.assertRaises(ValueError):
            validate_skills.parse_frontmatter("# no frontmatter\n")
        fm, _ = validate_skills.parse_frontmatter("---\nname: Bad_Name\ndescription: x\nmodel: opus\n---\nbody")
        self.assertEqual(fm["name"], "Bad_Name")
        self.assertIn("model", set(fm) - validate_skills.ALLOWED)

    def test_shared_scripts_are_in_sync(self):
        self.assertEqual(run("tools/sync_shared.py", "--check").returncode, 0)

    def test_rule_catalog_is_current(self):
        self.assertEqual(run("tools/gen_rule_catalog.py", "--check").returncode, 0)


class Examples(unittest.TestCase):
    def lint(self, rel, profile="web"):
        return bidi_lint.lint_file(os.path.join(ROOT, rel), profile=profile)

    def test_templates_and_examples_are_clean(self):
        for rel, profile in (
            ("skills/arabic-rtl-web/assets/starter-bilingual.html", "web"),
            ("skills/arabic-html-slides/assets/deck-starter.html", "deck"),
            ("examples/01-bilingual-site/site/ar/index.html", "web"),
            ("examples/01-bilingual-site/site/en/index.html", "web"),
            ("examples/01-bilingual-site/site/assets/site.css", "web"),
            ("examples/02-executive-deck/deck.html", "deck"),
            ("examples/03-rtl-audit/after.html", "web"),
            ("examples/04-ui-strings/ar.json", "web"),
        ):
            self.assertEqual([(f.rule, f.line) for f in self.lint(rel, profile)], [], rel)

    def test_broken_example_is_caught(self):
        rules = {f.rule for f in self.lint("examples/03-rtl-audit/before.html")}
        for expected in ("BD101", "BD102", "BD105", "BD107", "BD108", "BD201", "BD202", "BD203", "BD204", "BD208", "BD301"):
            self.assertIn(expected, rules)

    def test_parity_of_examples(self):
        ex = os.path.join(ROOT, "examples")
        self.assertEqual(i18n_parity.check_variants(os.path.join(ROOT, "skills/arabic-rtl-web/assets/starter-bilingual.html"))[0], [])
        self.assertEqual(i18n_parity.check_variants(os.path.join(ex, "02-executive-deck/deck.html"))[0], [])
        self.assertEqual(i18n_parity.check_pages(os.path.join(ex, "01-bilingual-site/site/ar/index.html"),
                                                 os.path.join(ex, "01-bilingual-site/site/en/index.html"))[0], [])
        self.assertEqual(i18n_parity.check_json([os.path.join(ex, "04-ui-strings/ar.json"), os.path.join(ex, "04-ui-strings/en.json")])[0], [])
        before = i18n_parity.check_json([os.path.join(ex, "04-ui-strings/ar.before.json"), os.path.join(ex, "04-ui-strings/en.json")])[0]
        self.assertEqual(sorted(p.code for p in before), ["P01", "P03", "P06"])


if __name__ == "__main__":
    unittest.main()

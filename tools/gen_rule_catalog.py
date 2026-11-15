#!/usr/bin/env python3
"""Generate skills/rtl-audit/references/rule-catalog.md from the linter's rule table.

    python tools/gen_rule_catalog.py          # write
    python tools/gen_rule_catalog.py --check  # exit 1 if the file is out of date (CI)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "shared", "scripts"))
import bidi_lint  # noqa: E402

OUT = os.path.join(ROOT, "skills", "rtl-audit", "references", "rule-catalog.md")

# rule id -> (why it matters, bad example, good example, when it is a false positive)
DETAIL = {
    "BD101": ("Screen readers pick a voice from `lang`, browsers pick fonts and hyphenation from it, and search engines use it.",
              "<html>", '<html lang="ar" dir="rtl">', "Never. HTML fragments without an `<html>` tag are not checked."),
    "BD102": ("Without `dir`, an Arabic page lays out left to right: alignment, punctuation and every flex row are wrong.",
              '<html lang="ar">', '<html lang="ar" dir="rtl">', "Never."),
    "BD103": ("A mismatch means either the wrong voice and fonts or a mirrored layout for the wrong language.",
              '<html lang="ar" dir="ltr">', '<html lang="ar" dir="rtl">', "Never."),
    "BD104": ("An English phrase inside Arabic keeps RTL punctuation placement unless it gets its own direction.",
              '<span lang="en">Terms of Service.</span>', '<span lang="en" dir="ltr">Terms of Service.</span>',
              "Single words without punctuation render correctly, but adding `dir` is still harmless."),
    "BD105": ("Emails, phone numbers and URLs typed into an RTL field show their symbols on the wrong side and the caret behaves oddly.",
              '<input type="email">', '<input type="email" dir="ltr">', "Fields inside an explicitly LTR form."),
    "BD106": ("U+202A to U+202E embed or override direction without isolating, leak past their intended span, and are a known trick for disguising source code.",
              "\\u202B…\\u202C in a string", "<bdi> in markup, or U+2066…U+2069 isolates in plain text",
              "Test fixtures that exercise bidi handling."),
    "BD107": ("Digits and symbols at the edge of an LTR run are claimed by the RTL paragraph: phone groups reverse, signs and slashes jump sides.",
              "<p>اتصل: +966 11 123 4567</p>", '<p>اتصل: <bdi dir="ltr">+966 11 123 4567</bdi></p>',
              "Text that is only ever shown in an LTR context; template placeholders."),
    "BD108": ("Arabic has its own comma, semicolon and question mark. Latin ones look foreign and the question mark faces the wrong way.",
              "مرحبا, كيف حالك?", "مرحبًا، كيف حالك؟", "Code samples and CSV-like data written in running text."),
    "BD109": ("Switching between 0-9 and ٠-٩ inside one product reads as an error and complicates search and copy/paste.",
              "٢٥ فرعًا في 30 مدينة", "25 فرعًا في 30 مدينة", "Content that quotes another source verbatim, or teaching material about digits."),
    "BD110": ("Tatweel inserted to stretch a word breaks search, copy/paste, spell-checking and screen-reader pronunciation.",
              "مرحـــبًا", "مرحبًا", "Calligraphic logotypes set as text (prefer an SVG)."),
    "BD111": ("In RTL the reader moves leftwards, so a right-pointing arrow on a 'next' or 'more' link points backwards.",
              "<a>التالي →</a>", "<a>التالي ←</a>", "Arrows that describe a literal direction or a mapping (A → B) in technical text."),
    "BD113": ("`align` is obsolete and physical.", '<td align="right">', "td { text-align: end; }", "HTML email templates, where attributes are still required."),
    "BD115": ("Class names like `chevron-right` usually mean a directional icon that should mirror in RTL.",
              '<i class="chevron-right">', '<i class="chevron-right rtl:-scale-x-100">',
              "Icons that are already swapped by a component, or that show a literal direction."),
    "BD201": ("Physical properties stay on the same side in RTL, so spacing, offsets and borders end up on the wrong edge.",
              ".card { margin-left: 16px; }", ".card { margin-inline-start: 16px; }",
              "Deliberately physical UI such as a media scrubber. Symmetric pairs, centering and `[dir]`-scoped rules are already exempt."),
    "BD202": ("`left` and `right` alignment does not follow direction.",
              ".title { text-align: left; }", ".title { text-align: start; }", "A block that is always LTR, such as code. Scope it instead of ignoring."),
    "BD203": ("CSS `direction` does not tell assistive technology or the bidi algorithm what markup would, and it is lost when styles fail to load.",
              "body { direction: rtl; }", '<html dir="rtl">', "Rare: styling generated content you cannot add attributes to."),
    "BD204": ("Arabic letters join. Letter-spacing pulls the joins apart or leaves gaps in the connecting stroke.",
              "h2 { letter-spacing: .1em; }", "h2:lang(en) { letter-spacing: .1em; }", "Selectors that can only match Latin text; scope them and the finding goes away."),
    "BD205": ("Arabic has no italic. Browsers synthesise a slant that looks broken.",
              "em { font-style: italic; }", "em:lang(en) { font-style: italic; } em:lang(ar) { font-weight: 600; }", "Latin-only selectors."),
    "BD207": ("Arabic has tall ascenders, deep descenders and stacked marks. Tight leading makes lines touch.",
              "body { line-height: 1.3; }", ":lang(ar) { line-height: 1.8; }", "Single-line UI labels with fixed padding."),
    "BD208": ("If no listed family has Arabic glyphs, the browser picks a fallback that varies by device and rarely matches the design.",
              "body { font-family: Inter, sans-serif; }", ':lang(ar) { font-family: "IBM Plex Sans Arabic", Tahoma, sans-serif; }',
              "A stack that relies on a brand font not in the built-in list; the rule is skipped when the value uses a CSS variable."),
    "BD209": ("Transforms are physical. A panel that slides in from the left in English also slides from the left in Arabic, against reading direction.",
              ".drawer { transform: translateX(-100%); }", ".drawer { transform: translateX(calc(var(--dir) * -100%)); }",
              "Centering with -50%, vertical-only motion and symmetric effects (already exempt where detectable)."),
    "BD210": ("Keyword positions such as `left center` do not flip.",
              ".select { background-position: right 12px center; }", '[dir="rtl"] .select { background-position: left 12px center; }',
              "Decorative backgrounds with no directional meaning."),
    "BD212": ("`break-all` splits Arabic words in the middle. The pieces still render, but as broken words.",
              ".cell { word-break: break-all; }", ".cell { overflow-wrap: anywhere; }", "Cells that only contain codes, hashes or URLs; scope them to Latin."),
    "BD213": ("`:lang(ar)` is not `[lang=ar]`: it matches all descendants. A font or line-height set there overrides what a heading passes to its inner spans.",
              ":lang(ar) { font-family: X; line-height: 1.8; }", ':lang(ar) { --text: X; } [lang] { font-family: var(--text); }',
              "Pages with no nested inline elements inside headings; resets such as letter-spacing: 0 are not flagged."),
    "BD301": ("Physical utility classes behave like physical CSS.",
              '<div class="ml-4 text-left">', '<div class="ms-4 text-start">', "Classes behind an `rtl:` or `ltr:` variant, symmetric pairs and centering are already exempt."),
    "DK401": ("Some people get motion sickness from transitions; the OS setting must be honoured.",
              "(no media query)", "@media (prefers-reduced-motion: reduce) { .slide { transition: none; } }", "Decks with no animation at all."),
    "DK402": ("Decks are shared as PDFs. Without print rules the export shows one slide, or overlapping slides.",
              "(no print rules)", "@media print { .slide { break-after: page; opacity: 1; transform: none; } }", "Never for a deliverable deck."),
    "DK403": ("A presenter needs keyboard control, and so do keyboard-only users.",
              "(click-only navigation)", 'document.addEventListener("keydown", …)', "Scroll-snap decks that rely on native scrolling."),
    "DK404": ("More than about 75 words means the audience reads instead of listening.",
              "(a slide with five paragraphs)", "(one idea, split across slides, detail in notes)", "Appendix and read-alone reference slides."),
    "DK405": ("Headings give each slide a name for screen readers and for the outline.",
              "<section class=\"slide\"><p>…</p></section>", "<section class=\"slide\"><h2>…</h2>…</section>", "Full-bleed image slides; add a visually hidden heading instead."),
}

GROUPS = [
    ("Document structure and text", "BD1"),
    ("CSS", "BD2"),
    ("Utility classes", "BD3"),
    ("Deck profile (`--profile deck`)", "DK4"),
]


def build():
    out = [
        "# Rule catalogue",
        "",
        "Generated from `scripts/bidi_lint.py` (version %s). Do not edit by hand; run `python tools/gen_rule_catalog.py` in the repository." % bidi_lint.__version__,
        "",
        "Severity: **error** fails the run, **warning** fails with `--strict`, **info** asks for a look.",
        "",
        "## Contents",
    ]
    out += ["- %s" % title for title, _ in GROUPS]
    out += ["- Suppressing a finding", ""]
    for title, prefix in GROUPS:
        out += ["## %s" % title, ""]
        for rid, (sev, name, fix) in bidi_lint.RULES.items():
            if not rid.startswith(prefix):
                continue
            why, bad, good, fp = DETAIL[rid]
            out += [
                "### %s: %s" % (rid, name),
                "",
                "**Severity:** %s" % sev,
                "",
                why,
                "",
                "- Before: `%s`" % bad,
                "- After: `%s`" % good,
                "- Fix: %s" % fix,
                "- Not a defect when: %s" % fp,
                "",
            ]
    out += [
        "## Suppressing a finding",
        "",
        "- One line: put `bidi-lint-ignore` in a comment on that line, followed by the reason.",
        "- One rule for a whole file: `bidi-lint-disable BD201` anywhere in the file. Several ids may follow.",
        "- From the command line: `--ignore BD209,BD210` or `--select BD107`.",
        "",
    ]
    return "\n".join(out)


def main():
    missing = [r for r in bidi_lint.RULES if r not in DETAIL]
    if missing:
        print("Missing detail for: %s" % ", ".join(missing))
        return 1
    text = build()
    if "--check" in sys.argv:
        current = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if current != text:
            print("rule-catalog.md is out of date: run python tools/gen_rule_catalog.py")
            return 1
        print("rule-catalog.md is up to date")
        return 0
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print("wrote %s (%d rules)" % (os.path.relpath(OUT, ROOT), len(bidi_lint.RULES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

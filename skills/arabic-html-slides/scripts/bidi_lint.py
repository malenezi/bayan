#!/usr/bin/env python3
"""bidi_lint - static checks for Arabic/RTL and bilingual HTML, CSS and text.

Part of Bayan (https://github.com/malenezi/bayan). Standard library only.

Usage:
    python bidi_lint.py page.html styles.css          # human-readable report
    python bidi_lint.py site/ --format md             # Markdown audit report
    python bidi_lint.py deck.html --profile deck      # add presentation checks
    python bidi_lint.py --list-rules                  # rule catalogue

Exit codes: 0 = no errors (warnings allowed unless --strict), 1 = findings at
the failing level, 2 = usage error.

Suppressions:
    bidi-lint-disable BD201 BD204   anywhere in a file disables those rules there
    bidi-lint-ignore                on a line silences that line
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from html.parser import HTMLParser

__version__ = "1.0.0"

ERROR, WARN, INFO = "error", "warning", "info"
SEV_ORDER = {ERROR: 0, WARN: 1, INFO: 2}

# id: (severity, title, fix hint)
RULES = {
    # --- document structure -------------------------------------------------
    "BD101": (ERROR, "<html> has no lang attribute",
              'Declare the language: <html lang="ar" dir="rtl">.'),
    "BD102": (ERROR, "RTL document without dir on <html>",
              'Set dir="rtl" on <html>; do not rely on CSS direction or text-align.'),
    "BD103": (ERROR, "lang and dir disagree",
              'ar/he/fa/ur need dir="rtl"; LTR languages need dir="ltr".'),
    "BD104": (WARN, "language switch without dir",
              'An element whose lang changes script direction also needs dir (e.g. <span lang="en" dir="ltr">).'),
    "BD105": (WARN, "LTR-only input not isolated",
              'Add dir="ltr" (or dir="auto") to email/tel/url/number/password inputs inside RTL pages.'),
    "BD106": (WARN, "legacy bidi control characters in source",
              "Replace U+202A-202E embeddings/overrides with <bdi>, dir attributes or isolates (U+2066-2069)."),
    "BD107": (WARN, "LTR run will reorder inside RTL text",
              'Wrap it: <bdi dir="ltr">...</bdi> (or <span dir="ltr">). For ranges, words are clearer: \u0645\u0646 10 \u0625\u0644\u0649 20.'),
    "BD108": (WARN, "Latin punctuation after Arabic text",
              "Use Arabic punctuation: \u060C (comma) \u061B (semicolon) \u061F (question mark)."),
    "BD109": (INFO, "mixed digit systems",
              "Pick one digit system per product (Western 0-9 or Arabic-Indic \u0660-\u0669) and apply it everywhere."),
    "BD110": (INFO, "tatweel (kashida) used to stretch text",
              "Remove U+0640 runs; they break search, copy/paste and screen readers. Use CSS for emphasis."),
    "BD111": (INFO, "forward arrow points the wrong way in RTL",
              "In RTL 'forward/next' points left. Use \u2190 or a mirrored icon; keep \u2192 only for literal directions."),
    "BD113": (WARN, "presentational align attribute",
              'Replace align="left|right" with CSS text-align: start|end.'),
    "BD115": (INFO, "directional icon may need mirroring",
              "Mirror back/next/chevron icons in RTL ([dir=rtl] .icon{transform:scaleX(-1)} or Tailwind rtl:-scale-x-100)."),
    # --- CSS ----------------------------------------------------------------
    "BD201": (WARN, "physical box property",
              "Use the logical equivalent (margin-inline-start, padding-inline-end, inset-inline-start, border-start-start-radius ...)."),
    "BD202": (WARN, "physical alignment keyword",
              "Use start/end (text-align) or inline-start/inline-end (float, clear)."),
    "BD203": (WARN, "direction set in CSS",
              "Direction is content, not style: use the dir attribute in markup."),
    "BD204": (WARN, "letter-spacing reaches Arabic text",
              "Tracking breaks Arabic joining. Scope it to Latin (:lang(en), [dir=ltr]) or reset to 0 for :lang(ar)."),
    "BD205": (INFO, "italic reaches Arabic text",
              "Arabic has no italic; browsers fake a slant. Scope italics to Latin and use weight or colour for Arabic emphasis."),
    "BD207": (WARN, "line-height too tight for Arabic body text",
              "Arabic needs roughly 1.6-1.9 for body copy (1.2-1.4 for large headings)."),
    "BD208": (WARN, "font stack has no Arabic-capable family",
              "Name an Arabic typeface first for Arabic content (e.g. 'IBM Plex Sans Arabic', 'Noto Kufi Arabic'), then fallbacks."),
    "BD209": (INFO, "horizontal motion does not mirror",
              "translateX keeps its sign in RTL. Multiply by a direction variable (--dir: 1 / -1) or override under [dir=rtl]."),
    "BD210": (INFO, "physical keyword in positioning value",
              "background-position/transform-origin/object-position 'left|right' do not flip; add an RTL override if the visual is directional."),
    "BD212": (WARN, "word-break: break-all on Arabic",
              "break-all splits Arabic words mid-word. Use overflow-wrap: anywhere or scope break-all to Latin/code."),
    "BD213": (INFO, "bare :lang() sets an inherited text property",
              ":lang() matches every element in that language, so spans inside headings are reset. Set variables in :lang() and apply font-family/line-height on [lang]."),
    # --- utility classes ----------------------------------------------------
    "BD301": (WARN, "physical utility class",
              "Use logical utilities: ms-/me-/ps-/pe-, start-/end-, text-start/text-end, rounded-s/e, border-s/e."),
    # --- deck profile -------------------------------------------------------
    "DK401": (WARN, "animations without prefers-reduced-motion",
              "Add @media (prefers-reduced-motion: reduce) that disables transitions and animations."),
    "DK402": (WARN, "no print stylesheet",
              "Add @media print so the deck exports to PDF one slide per page."),
    "DK403": (WARN, "no keyboard navigation",
              "Handle keydown for arrows/space/Home/End; in RTL the Left arrow advances."),
    "DK404": (INFO, "slide is text-heavy",
              "Cut to one idea per slide; move detail to speaker notes or an appendix."),
    "DK405": (WARN, "slide has no heading",
              "Give every slide an h1-h3 (visually hidden if needed) for structure and screen readers."),
}

RTL_LANGS = {"ar", "he", "fa", "ur", "ps", "sd", "ckb", "ug", "yi", "dv"}
AR = "\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF"
RTL_CHAR = re.compile("[%s\u0590-\u05FF]" % AR)
AR_LETTER = "\u0621-\u064A\u066E-\u06D3\u0750-\u077F"
HAS_AR_LETTER = re.compile("[%s]" % AR_LETTER)
LEGACY_BIDI = re.compile("[\u202A-\u202E]")
LATIN_PUNCT_AFTER_AR = re.compile(r"(?<=[%s])[ \u00A0]?[,;?](?=\s|$|[\"'\u00BB)])" % AR_LETTER)
TATWEEL = re.compile("\u0640{2,}")
FWD_ARROW = re.compile("[\u2192\u2794\u279C\u279D\u279E\u27A1\u21D2\u25B6\u25BA]")
AR_DIGIT = re.compile("[\u0660-\u0669\u06F0-\u06F9]")
W_DIGIT = re.compile("[0-9]")

RISKY_LTR = [
    ("phone number", re.compile(r"(?<![\w.])\+\d[\d \u00A0\-()]{5,}\d")),
    ("signed number", re.compile(r"(?<![\w.)\u0660-\u0669])[-+\u2212]\d[\d.,]*%?")),
    ("spaced digit groups", re.compile(r"(?<![\w.,/+\-])\d{2,4}(?:[ \u00A0]\d{2,4}){2,}(?![\w])")),
    ("range, date or expression (shows end-first in RTL)", re.compile(r"\d+(?:\s*[-\u2013\u2014=\u00D7\u00F7<>]\s*\d+)+|\d+\s+[+*/]\s+\d+")),
    ("URL or path", re.compile(r"https?://[^\s<>\"']+|(?<![\w/])~?/[A-Za-z][\w.\-]*/[\w./\-]*")),
    ("handle or hashtag", re.compile(r"(?<![\w&])[@#][A-Za-z]\w+")),
    ("Latin term with symbols", re.compile(r"(?<![A-Za-z])(?:[A-Za-z]\w*(?:\+\+|#)(?!\w)|\.[A-Za-z]{2,}\b(?<=\.NET))")),
]

PHYSICAL_PROPS = re.compile(
    r"^(margin|padding|border|scroll-margin|scroll-padding)-(left|right)(-(width|style|color))?$"
    r"|^(left|right)$"
    r"|^border-(top|bottom)-(left|right)-radius$")
LOGICAL_HINT = {
    "margin-left": "margin-inline-start", "margin-right": "margin-inline-end",
    "padding-left": "padding-inline-start", "padding-right": "padding-inline-end",
    "border-left": "border-inline-start", "border-right": "border-inline-end",
    "left": "inset-inline-start", "right": "inset-inline-end",
    "border-top-left-radius": "border-start-start-radius",
    "border-top-right-radius": "border-start-end-radius",
    "border-bottom-left-radius": "border-end-start-radius",
    "border-bottom-right-radius": "border-end-end-radius",
}
DIR_SCOPED = re.compile(r"\[dir|:dir\(|:lang\(|\[lang|\[data-lang|(?<![\w-])\.(rtl|ltr)\b", re.I)
LATIN_SCOPED = re.compile(
    r":lang\(\s*(en|fr|de|es|latn)|\[lang[|^]?=[\"']?(en|fr|de|es)|\[dir=[\"']?ltr|:dir\(\s*ltr"
    r"|\[data-lang=[\"']?(en|fr)|(?<![\w-])\.(en|latin|ltr|mono|code)\b|\b(code|pre|kbd|samp)\b", re.I)
AR_SCOPED = re.compile(r":lang\(\s*(ar|fa|ur|he)|\[lang[|^]?=[\"']?(ar|fa|ur|he)|\[dir=[\"']?rtl|:dir\(\s*rtl|\[data-lang=[\"']?ar", re.I)
BODY_SEL = re.compile(r"(^|[\s,>])(html|body|p|li|:root)(?=$|[\s,:\[.{])", re.I)
ARABIC_FONTS = (
    "arab", "naskh", "kufi", "plex sans arabic", "tajawal", "cairo", "almarai", "amiri", "readex",
    "rubik", "vazir", "alexandria", "el messiri", "reem", "lemonada", "markazi", "changa", "mada",
    "harmattan", "scheherazade", "lateef", "zain", "kufam", "qahiri", "aref ruqaa", "noto sans",
    "tahoma", "segoe ui", "geeza", "dubai", "sakkal", "traditional arabic", "simplified arabic",
    "arial", "times new roman", "system-ui", "-apple-system", "blinkmacsystemfont", "droid", "thmanyah",
    "29lt", "frutiger", "din next", "greta", "lalezar", "baloo bhaijaan", "noto nastaliq", "gulzar",
    "handjet", "playpen", "fustat", "beiruti", "ruwudu", "rakkas", "jomhuria", "katibeh", "mirza",
    "el-messiri", "ui-sans-serif", "ui-serif", "david", "heebo", "assistant",
)
TW_PHYSICAL = re.compile(
    r"^(?P<variants>(?:[\w\[\]\-.=&>*]+:)*)!?-?"
    r"(?:(?P<box>ml|mr|pl|pr)-|(?P<pos>left|right)-|text-(?P<ta>left|right)$|float-(?P<fl>left|right)$"
    r"|clear-(?P<cl>left|right)$|rounded-(?P<rd>tl|tr|bl|br|l|r)(?:-|$)|border-(?P<bd>l|r)(?:-|$)|scroll-(?P<sc>ml|mr|pl|pr)-)")
TW_HINT = {"ml": "ms", "mr": "me", "pl": "ps", "pr": "pe", "left": "start", "right": "end",
           "l": "s", "r": "e", "tl": "ss", "tr": "se", "bl": "es", "br": "ee"}
ICON_CLASS = re.compile(r"(arrow|chevron|caret|angle)[-_]?(left|right)|(?<![\w])(back|forward|next|prev)[-_]?(icon|arrow)", re.I)
MIRROR_CLASS = re.compile(r"rtl:|flip|mirror|scale-x", re.I)
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
SKIP_TEXT = {"script", "style", "code", "pre", "kbd", "samp", "svg", "math", "textarea", "noscript", "template"}
LTR_INPUT = {"email", "tel", "url", "number", "password"}


@dataclass
class Finding:
    rule: str
    severity: str
    path: str
    line: int
    col: int
    message: str
    hint: str
    snippet: str = ""


@dataclass
class CssRule:
    selector: str
    context: list
    decls: list = field(default_factory=list)  # (prop, value, line)


def _line_of(text: str, idx: int) -> int:
    return text.count("\n", 0, idx) + 1


def _clip(s: str, n: int = 70) -> str:
    s = " ".join(s.split())
    return s if len(s) <= n else s[: n - 1] + "\u2026"


# --------------------------------------------------------------------------- CSS
def parse_css(text: str, line_offset: int = 0) -> list:
    """Tolerant CSS parser: returns style rules with (prop, value, line) declarations."""
    s = re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=re.S)
    out: list = []
    n = len(s)

    def add_decl(rule_decls, a, b):
        chunk = s[a:b]
        if ":" not in chunk:
            return
        lead = len(chunk) - len(chunk.lstrip())
        prop, _, val = chunk.strip().partition(":")
        prop = prop.strip().lower()
        if prop and re.match(r"^-{0,2}[\w-]+$", prop):
            rule_decls.append((prop, val.strip().rstrip(";").strip(), _line_of(s, a + lead) + line_offset))

    def block(i, ctx, sel):
        decls, start = [], i
        while i < n:
            c = s[i]
            if c in "\"'":
                j = i + 1
                while j < n and s[j] != c:
                    j += 2 if s[j] == "\\" else 1
                i = j
            elif c == "(":
                depth, j = 1, i + 1
                while j < n and depth:
                    depth += (s[j] == "(") - (s[j] == ")")
                    j += 1
                i = j - 1
            elif c == ";":
                add_decl(decls, start, i)
                start = i + 1
            elif c == "{":
                prelude = " ".join(s[start:i].split())
                if prelude.startswith("@"):
                    name = prelude.split()[0].lower() if prelude.split() else "@"
                    grouping = name in ("@media", "@supports", "@layer", "@container", "@scope", "@document", "@starting-style")
                    i = block(i + 1, ctx + [prelude], sel if grouping else (None if "keyframes" in name else prelude))
                else:
                    i = block(i + 1, ctx, (sel + " " + prelude) if sel and not sel.startswith("@") else prelude)
                start = i
                continue
            elif c == "}":
                add_decl(decls, start, i)
                i += 1
                break
            i += 1
        else:
            add_decl(decls, start, n)
        if decls and sel is not None:
            out.append(CssRule(sel, ctx, decls))
        return i

    i = 0
    while i < n:
        i = block(i, [], None)
    return out


def _zeroish(v: str) -> bool:
    v = v.lower().replace("!important", "").strip()
    return v in ("0", "normal", "initial", "inherit", "unset", "revert") or bool(re.match(r"^[+-]?0(\.0+)?(em|px|rem|ch|%)?$", v))


def check_css(rules, path, arabic_ctx, emit, inline_latin=False):
    """arabic_ctx: True when these styles are known to reach Arabic content."""
    ar_font_rule = any(AR_SCOPED.search(r.selector or "") and any(p == "font-family" for p, _, _ in r.decls) for r in rules)
    for r in rules:
        sel = r.selector or ""
        in_keyframes = any("keyframes" in c.lower() for c in r.context)
        if sel.startswith("@") and not in_keyframes:  # @font-face, @page
            continue
        dir_scoped = bool(DIR_SCOPED.search(sel))
        latin = inline_latin or (bool(LATIN_SCOPED.search(sel)) and not AR_SCOPED.search(sel))
        props = {p: v for p, v, _ in r.decls}
        bare_lang = bool(re.fullmatch(r"(?:\*|html\s+\*)?:lang\([^)]*\)", sel.strip()))
        for prop, val, line in r.decls:
            if prop.startswith("--"):
                continue
            if bare_lang and prop in ("font-family", "line-height", "font-size", "font-weight"):
                emit("BD213", path, line, 1, "'%s' on a bare %s rule reaches every descendant" % (prop, sel.strip()), "%s { %s }" % (sel.strip(), prop))
            v = val.lower().replace("!important", "").strip()
            where = "%s { %s: %s }" % (_clip(sel, 40), prop, _clip(val, 30))
            if PHYSICAL_PROPS.match(prop) and not dir_scoped:
                twin = prop.replace("left", "\0").replace("right", "left").replace("\0", "right")
                symmetric = twin in props and props[twin].strip().lower() == val.strip().lower()
                centering = prop in ("left", "right") and v in ("50%", "auto")
                if not symmetric and not centering and v not in ("auto", "inherit", "initial", "unset"):
                    base = re.sub(r"-(width|style|color)$", "", prop)
                    hint = LOGICAL_HINT.get(base)
                    emit("BD201", path, line, 1, "'%s' does not flip in RTL%s" % (prop, " - use %s" % hint if hint else ""), where)
            if prop in ("text-align", "float", "clear") and v in ("left", "right") and not dir_scoped:
                emit("BD202", path, line, 1, "'%s: %s' does not flip in RTL" % (prop, v), where)
            if prop == "direction" and v in ("rtl", "ltr"):
                emit("BD203", path, line, 1, "direction: %s set in CSS" % v, where)
            if prop == "letter-spacing" and not _zeroish(v) and not latin and arabic_ctx and not in_keyframes:
                emit("BD204", path, line, 1, "letter-spacing: %s is not scoped to Latin text" % _clip(val, 20), where)
            if prop == "font-style" and v in ("italic", "oblique") and not latin and arabic_ctx:
                emit("BD205", path, line, 1, "font-style: %s is not scoped to Latin text" % v, where)
            if prop == "line-height" and arabic_ctx and not latin and BODY_SEL.search(sel):
                m = re.match(r"^(\d*\.?\d+)$", v)
                if m and float(m.group(1)) < 1.5:
                    emit("BD207", path, line, 1, "line-height: %s on body text" % v, where)
            if prop == "font-family" and not latin and "var(" not in v and v not in ("inherit", "initial", "unset"):
                targets_ar = bool(AR_SCOPED.search(sel))
                if (targets_ar or (arabic_ctx and BODY_SEL.search(sel) and not ar_font_rule)) and not any(f in v for f in ARABIC_FONTS):
                    emit("BD208", path, line, 1, "no Arabic-capable family in this stack", where)
            if prop in ("transform", "translate") and not dir_scoped and "var(" not in v:
                m = re.search(r"translate(?:x|3d)?\(\s*(-?[\d.]+)(px|rem|em|%|vw|vh)?", v) if prop == "transform" else re.match(r"(-?[\d.]+)(px|rem|em|%|vw|vh)?", v)
                if m and float(m.group(1)) != 0 and not (abs(float(m.group(1))) == 50 and m.group(2) == "%"):
                    if prop == "translate" or "translatey" not in v.split("(")[0]:
                        emit("BD209", path, line, 1, "horizontal translate keeps its sign in RTL", where)
            if prop in ("background-position", "transform-origin", "object-position", "background") and not dir_scoped:
                if re.search(r"(?<![\w-])(left|right)(?![\w-])", re.sub(r"url\([^)]*\)|to (left|right)", "", v)):
                    emit("BD210", path, line, 1, "'%s' uses a physical left/right keyword" % prop, where)
            if prop == "word-break" and v == "break-all" and not latin and arabic_ctx:
                emit("BD212", path, line, 1, "word-break: break-all reaches Arabic text", where)


# --------------------------------------------------------------------------- text
def check_text(text, path, line, col, rtl, emit, risky=True):
    """Checks on a run of human-readable text. rtl: effective direction is RTL."""
    def pos(idx):
        nl = text.count("\n", 0, idx)
        return line + nl, (col + idx + 1) if nl == 0 else (idx - text.rfind("\n", 0, idx))

    for m in LEGACY_BIDI.finditer(text):
        emit("BD106", path, *pos(m.start()), "U+%04X in text" % ord(m.group(0)), _clip(text))
    for m in LATIN_PUNCT_AFTER_AR.finditer(text):
        emit("BD108", path, *pos(m.start()), "'%s' after Arabic text" % m.group(0).strip(), _clip(text[max(0, m.start() - 30): m.end() + 5]))
    for m in TATWEEL.finditer(text):
        emit("BD110", path, *pos(m.start()), "%d consecutive tatweel characters" % len(m.group(0)), _clip(text[max(0, m.start() - 20): m.end() + 20]))
    if rtl:
        for m in FWD_ARROW.finditer(text):
            emit("BD111", path, *pos(m.start()), "'%s' in RTL text" % m.group(0), _clip(text[max(0, m.start() - 30): m.end() + 10]))
        if risky:
            taken = []
            for label, rx in RISKY_LTR:
                for m in rx.finditer(text):
                    if any(a < m.end() and m.start() < b for a, b in taken):
                        continue
                    taken.append((m.start(), m.end()))
                    emit("BD107", path, *pos(m.start()), "%s '%s' is not isolated" % (label, _clip(m.group(0), 32)), _clip(text[max(0, m.start() - 25): m.end() + 10]))


# --------------------------------------------------------------------------- HTML
class _Doc(HTMLParser):
    def __init__(self, path, emit, variant_attr):
        super().__init__(convert_charrefs=True)
        self.path, self.emit, self.vattr = path, emit, variant_attr
        self.stack = [dict(tag="#root", dir="ltr", lang="", iso=False, skip=False)]
        self.html_seen = False
        self.html_lang = self.html_dir = None
        self.styles, self.inline_styles, self.scripts = [], [], []
        self.has_arabic = False
        self.ar_digits = self.w_digits = 0
        self.digit_pos = None
        self.slides, self.cur_slide = [], None
        self.has_title = False

    @property
    def top(self):
        return self.stack[-1]

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        line, col = self.getpos()
        parent = self.top
        ctx = dict(tag=tag, dir=parent["dir"], lang=parent["lang"], iso=False,
                   skip=parent["skip"] or tag in SKIP_TEXT)
        lang = a.get("lang", "").lower().split("-")[0]
        d = a.get("dir", "").lower()
        variant = a.get(self.vattr, "").lower().split("-")[0] if self.vattr else ""
        if tag == "html":
            self.html_seen = True
            self.html_lang, self.html_dir = lang or None, d or None
            if not lang:
                self.emit("BD101", self.path, line, col + 1, "<html> has no lang attribute", "<html>")
            if lang in RTL_LANGS and not d:
                self.emit("BD102", self.path, line, col + 1, 'lang="%s" without dir="rtl"' % lang, "<html lang=\"%s\">" % lang)
            if lang and d in ("rtl", "ltr") and (lang in RTL_LANGS) != (d == "rtl"):
                self.emit("BD103", self.path, line, col + 1, 'lang="%s" with dir="%s"' % (lang, d), "")
        elif lang and not d and not variant:
            if (lang in RTL_LANGS) != (parent["lang"] in RTL_LANGS) and parent["lang"]:
                self.emit("BD104", self.path, line, col + 1, '<%s lang="%s"> inside %s content has no dir' % (tag, lang, parent["lang"]), "")
        if lang:
            ctx["lang"] = lang
        if variant:
            ctx["lang"] = variant
            ctx["dir"] = "rtl" if variant in RTL_LANGS else "ltr"
        if d in ("rtl", "ltr"):
            ctx["dir"] = d
        elif d == "auto" or tag == "bdi":
            ctx["iso"] = True
        if tag == "title":
            self.has_title = True
        if a.get("align", "").lower() in ("left", "right"):
            self.emit("BD113", self.path, line, col + 1, '<%s align="%s">' % (tag, a["align"]), "")
        if tag == "input" and a.get("type", "text").lower() in LTR_INPUT and ctx["dir"] == "rtl" and not d:
            self.emit("BD105", self.path, line, col + 1, '<input type="%s"> inherits RTL' % a.get("type"), "")
        cls = a.get("class", "") or a.get("classname", "")
        if cls:
            check_classes(cls, self.path, line, col + 1, self.emit)
            if ICON_CLASS.search(cls) and not MIRROR_CLASS.search(cls):
                self.emit("BD115", self.path, line, col + 1, "class '%s' looks directional" % _clip(cls, 40), "")
        if a.get("style"):
            self.inline_styles.append((a["style"], line, ctx["dir"] == "ltr" and ctx["lang"] not in RTL_LANGS and bool(ctx["lang"])))
        for attr in ("alt", "title", "placeholder", "aria-label"):
            if a.get(attr) and not ctx["skip"]:
                self._text(a[attr], line, col, ctx, risky=False)
        is_slide = tag in ("section", "article", "div") and ("data-slide" in a or re.search(r"(^|\s)slide(\s|$)", cls))
        if is_slide:
            self.cur_slide = dict(line=line, words=0, heading=False, depth=len(self.stack))
            self.slides.append(self.cur_slide)
        if self.cur_slide and tag in ("h1", "h2", "h3"):
            self.cur_slide["heading"] = True
        if tag not in VOID:
            ctx["_type"] = a.get("type", "").lower()
            self.stack.append(ctx)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and len(self.stack) > 1:
            self.stack.pop()

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i]["tag"] == tag:
                del self.stack[i:]
                break
        if self.cur_slide and len(self.stack) <= self.cur_slide["depth"]:
            self.cur_slide = None

    def _text(self, data, line, col, ctx, risky=True):
        if RTL_CHAR.search(data):
            self.has_arabic = True
        if HAS_AR_LETTER.search(data):
            a, w = len(AR_DIGIT.findall(data)), len(W_DIGIT.findall(data))
            self.ar_digits += a
            self.w_digits += w
            if a and self.digit_pos is None:
                self.digit_pos = (line, col + 1)
        check_text(data, self.path, line, col, ctx["dir"] == "rtl", self.emit, risky=risky and not ctx["iso"])

    def handle_data(self, data):
        line, col = self.getpos()
        ctx = self.top
        if ctx["tag"] == "style":
            self.styles.append((data, line - 1))
        elif ctx["tag"] == "script":
            self.scripts.append((data, line, ctx.get("_type", "")))
            if "json" in ctx.get("_type", ""):
                check_text(data, self.path, line, col, False, self.emit, risky=False)
        elif not ctx["skip"] and data.strip():
            self._text(data, line, col, ctx)
            if self.cur_slide is not None and (not self.vattr or ctx["lang"] == (self.html_lang or ctx["lang"])):
                self.cur_slide["words"] += len(data.split())


def check_classes(cls, path, line, col, emit):
    tokens = cls.split()
    plain = set(tokens)
    for t in tokens:
        m = TW_PHYSICAL.match(t)
        if not m:
            continue
        if re.search(r"(^|:)(rtl|ltr)(:|$)", m.group("variants") or ""):
            continue
        key = next(v for v in m.groupdict().values() if v and v != m.group("variants"))
        twin = t.replace(key, {"ml": "mr", "mr": "ml", "pl": "pr", "pr": "pl", "left": "right", "right": "left",
                               "l": "r", "r": "l", "tl": "tr", "tr": "tl", "bl": "br", "br": "bl"}.get(key, key), 1)
        if twin != t and twin in plain:
            continue  # symmetric pair (ml-auto mr-auto, left-0 right-0)
        if m.group("pos") and re.search(r"-(1/2|auto)$", t):
            continue
        emit("BD301", path, line, col, "'%s' is physical - try the '%s' form" % (t, TW_HINT.get(key, "logical")), _clip(cls, 60))


def lint_html(text, path, emit, profile, variant_attr):
    doc = _Doc(path, emit, variant_attr)
    if not re.search(r"<html\b[^>]*\bdir\s*=", text, flags=re.I):
        # No declared direction: if the content is mostly Arabic, check it as the RTL page it is meant to be.
        visible = re.sub(r"<(script|style)\b.*?</\1>|<[^>]+>", "", text, flags=re.S)
        if len(RTL_CHAR.findall(visible)) > len(re.findall(r"[A-Za-z]", visible)):
            doc.stack[0]["dir"] = "rtl"
    doc.feed(text)
    doc.close()
    is_fragment = not doc.html_seen
    rtl_doc = (doc.html_lang in RTL_LANGS) or doc.html_dir == "rtl" or doc.has_arabic
    if doc.html_seen and doc.has_arabic and not doc.html_dir and doc.html_lang not in RTL_LANGS:
        ar_chars = len(RTL_CHAR.findall(text))
        latin_chars = len(re.findall(r"[A-Za-z]", re.sub(r"<(script|style)\b.*?</\1>|<[^>]+>", "", text, flags=re.S)))
        if ar_chars > latin_chars and not variant_attr_used(text, variant_attr):
            emit("BD102", path, 1, 1, "document is mostly Arabic but <html> has no dir", "")
    for css, off in doc.styles:
        check_css(parse_css(css, off), path, rtl_doc, emit)
    for style, line, latin in doc.inline_styles:
        check_css(parse_css("x{%s}" % style, line - 1), path, rtl_doc, emit, inline_latin=latin)
    if doc.ar_digits and doc.w_digits:
        emit("BD109", path, *(doc.digit_pos or (1, 1)),
             "%d Arabic-Indic and %d Western digits in Arabic text" % (doc.ar_digits, doc.w_digits), "")
    if profile == "deck" and not is_fragment:
        css_all = "\n".join(c for c, _ in doc.styles)
        js_all = "\n".join(s for s, _, t in doc.scripts if "json" not in t)
        if re.search(r"animation|transition", css_all) and "prefers-reduced-motion" not in css_all:
            emit("DK401", path, 1, 1, "deck animates but never checks prefers-reduced-motion", "")
        if not re.search(r"@media[^{]*print", css_all):
            emit("DK402", path, 1, 1, "no @media print rules", "")
        if "keydown" not in js_all and "keyup" not in js_all:
            emit("DK403", path, 1, 1, "no keydown handler found", "")
        for n, s in enumerate(doc.slides, 1):
            if s["words"] > 75:
                emit("DK404", path, s["line"], 1, "slide %d has about %d words" % (n, s["words"]), "")
            if not s["heading"]:
                emit("DK405", path, s["line"], 1, "slide %d has no h1-h3" % n, "")


def variant_attr_used(text, attr):
    return bool(attr) and (attr + "=") in text


def lint_css_file(text, path, emit):
    check_css(parse_css(text), path, True, emit)


def lint_markup_classes(text, path, emit):
    for m in re.finditer(r"class(?:Name)?\s*=\s*(?:\{\s*)?[\"'`]([^\"'`]+)[\"'`]", text):
        check_classes(m.group(1), path, _line_of(text, m.start()), 1, emit)


def lint_plain(text, path, emit):
    fenced = False
    ar = w = 0
    first = None
    for n, raw in enumerate(text.split("\n"), 1):
        if raw.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        ln = re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), raw)
        has_ar = bool(HAS_AR_LETTER.search(ln))
        if has_ar:
            a, b = len(AR_DIGIT.findall(ln)), len(W_DIGIT.findall(ln))
            ar, w = ar + a, w + b
            if a and first is None:
                first = n
        check_text(ln, path, n, 0, has_ar, emit, risky=has_ar and not path.endswith((".md", ".markdown")))
    if ar and w:
        emit("BD109", path, first or 1, 1, "%d Arabic-Indic and %d Western digits in Arabic text" % (ar, w), "")


HTML_EXT = (".html", ".htm", ".xhtml")
CLASS_EXT = (".jsx", ".tsx", ".vue", ".svelte", ".astro", ".erb", ".php", ".twig", ".njk", ".hbs")
TEXT_EXT = (".md", ".markdown", ".txt", ".json", ".yaml", ".yml", ".po", ".strings", ".arb", ".xliff", ".csv")
SKIP_DIRS = {".git", "node_modules", "dist", "build", ".next", "vendor", "__pycache__", ".venv", "venv"}


def lint_file(path, profile="web", variant_attr="data-lang", select=None, ignore=None):
    findings: list = []
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except (OSError, UnicodeDecodeError) as exc:
        return [Finding("BD000", ERROR, path, 1, 1, "cannot read file: %s" % exc, "Save the file as UTF-8.")]
    disabled = set()
    for m in re.finditer(r"bidi-lint-disable((?:[ \t,]+(?:BD|DK)\d{3})+)", text):
        disabled.update(re.findall(r"(?:BD|DK)\d{3}", m.group(1)))
    lines = text.split("\n")
    seen = set()

    def emit(rule, p, line, col, message, snippet=""):
        if rule in disabled or (select and rule not in select) or (ignore and rule in ignore):
            return
        if 0 < line <= len(lines) and "bidi-lint-ignore" in lines[line - 1]:
            return
        key = (rule, line, message)
        if key in seen:
            return
        seen.add(key)
        sev, _, hint = RULES[rule]
        findings.append(Finding(rule, sev, p, line, max(col, 1), message, hint, snippet))

    low = path.lower()
    if low.endswith(HTML_EXT):
        lint_html(text, path, emit, profile, variant_attr)
    elif low.endswith((".css", ".scss", ".less", ".pcss")):
        lint_css_file(text, path, emit)
    elif low.endswith(CLASS_EXT):
        lint_markup_classes(text, path, emit)
        for m in re.finditer(r"<style[^>]*>(.*?)</style>", text, flags=re.S):
            check_css(parse_css(m.group(1), _line_of(text, m.start(1)) - 1), path, True, emit)
    elif low.endswith(TEXT_EXT):
        lint_plain(text, path, emit)
    findings.sort(key=lambda f: (f.line, f.col, f.rule))
    return findings


def collect(paths):
    exts = HTML_EXT + CLASS_EXT + TEXT_EXT + (".css", ".scss", ".less", ".pcss")
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith("."))
                for f in sorted(files):
                    if f.lower().endswith(exts) and not f.lower().endswith((".min.css", "package-lock.json")):
                        yield os.path.join(root, f)
        else:
            yield p


def render_text(findings, files):
    out, cur = [], None
    for f in findings:
        if f.path != cur:
            cur = f.path
            out.append("\n" + cur)
        out.append("  %4d:%-3d %-7s %s  %s" % (f.line, f.col, f.severity, f.rule, f.message))
        if f.snippet:
            out.append("           | %s" % f.snippet)
        out.append("           > %s" % f.hint)
    out.append("\n" + summary(findings, files))
    return "\n".join(out).lstrip("\n")


def summary(findings, files):
    c = {s: sum(1 for f in findings if f.severity == s) for s in SEV_ORDER}
    return "%d file(s) checked: %d error(s), %d warning(s), %d info" % (files, c[ERROR], c[WARN], c[INFO])


def render_md(findings, files):
    out = ["# RTL / bidi audit", "", summary(findings, files), ""]
    if not findings:
        return "\n".join(out + ["No findings."])
    by_rule = {}
    for f in findings:
        by_rule.setdefault(f.rule, []).append(f)
    out += ["| Rule | Severity | Count | What | Fix |", "|---|---|---:|---|---|"]
    for rule in sorted(by_rule, key=lambda r: (SEV_ORDER[RULES[r][0]], r)):
        sev, title, hint = RULES[rule]
        out.append("| %s | %s | %d | %s | %s |" % (rule, sev, len(by_rule[rule]), title.replace("|", "\\|"), hint.replace("|", "\\|")))
    out += ["", "## Findings", ""]
    cur = None
    for f in sorted(findings, key=lambda f: (f.path, f.line, f.col)):
        if f.path != cur:
            cur = f.path
            out += ["### `%s`" % cur, ""]
        out.append("- **%s** line %d - %s" % (f.rule, f.line, f.message) + (" - `%s`" % f.snippet.replace("`", "'") if f.snippet else ""))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="bidi_lint", description="Static checks for Arabic/RTL and bilingual HTML, CSS and text.")
    ap.add_argument("paths", nargs="*", help="files or directories")
    ap.add_argument("--profile", choices=("web", "deck"), default="web", help="deck adds presentation checks (DK4xx)")
    ap.add_argument("--format", choices=("text", "json", "md"), default="text")
    ap.add_argument("--select", help="comma-separated rule ids to run")
    ap.add_argument("--ignore", help="comma-separated rule ids to skip")
    ap.add_argument("--min-severity", choices=(ERROR, WARN, INFO), default=INFO)
    ap.add_argument("--strict", action="store_true", help="exit 1 on warnings too")
    ap.add_argument("--variant-attr", default="data-lang", help="attribute marking paired language variants ('' to disable)")
    ap.add_argument("--list-rules", action="store_true")
    ap.add_argument("--version", action="version", version=__version__)
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if args.list_rules:
        if args.format == "json":
            print(json.dumps({k: dict(severity=v[0], title=v[1], fix=v[2]) for k, v in RULES.items()}, ensure_ascii=False, indent=2))
        else:
            for k, (sev, title, hint) in RULES.items():
                print("%s  %-7s  %s\n       %s" % (k, sev, title, hint))
        return 0
    if not args.paths:
        ap.print_usage(sys.stderr)
        return 2
    missing = [p for p in args.paths if not os.path.exists(p)]
    if missing:
        print("bidi_lint: no such file or directory: %s" % ", ".join(missing), file=sys.stderr)
        return 2
    sel = set(args.select.upper().split(",")) if args.select else None
    ign = set(args.ignore.upper().split(",")) if args.ignore else None
    unknown = [r for r in (sel or set()) | (ign or set()) if r not in RULES]
    if unknown:
        print("bidi_lint: unknown rule id(s): %s" % ", ".join(sorted(unknown)), file=sys.stderr)
        return 2
    files, findings = 0, []
    for path in collect(args.paths):
        files += 1
        findings += lint_file(path, args.profile, args.variant_attr, sel, ign)
    findings = [f for f in findings if SEV_ORDER[f.severity] <= SEV_ORDER[args.min_severity]]
    if args.format == "json":
        print(json.dumps(dict(version=__version__, files=files, summary=summary(findings, files),
                              findings=[asdict(f) for f in findings]), ensure_ascii=False, indent=2))
    elif args.format == "md":
        print(render_md(findings, files))
    else:
        print(render_text(findings, files))
    fail = {ERROR, WARN} if args.strict else {ERROR}
    return 1 if any(f.severity in fail for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())

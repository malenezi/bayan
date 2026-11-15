#!/usr/bin/env python3
"""i18n_parity - check that Arabic and English content stay in step.

Part of Bayan (https://github.com/malenezi/bayan). Standard library only.

Three modes, chosen by the arguments:

    python i18n_parity.py page.html                 # paired variants in one file
    python i18n_parity.py --json ar.json en.json    # two dictionaries
    python i18n_parity.py --json strings.json       # one file: {"key": {"ar": "", "en": ""}}
    python i18n_parity.py --pages ar/index.html en/index.html   # two-page site

Paired variants are siblings marked data-lang="ar" / data-lang="en"; translated
attributes are data-ar-<attr> / data-en-<attr> pairs (for example data-ar-aria-label).

Exit codes: 0 = in step, 1 = problems found, 2 = usage error.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from html.parser import HTMLParser

__version__ = "1.0.0"
AR_LETTER = re.compile("[\u0621-\u064A\u066E-\u06D3\u0750-\u077F]")
LATIN_WORD = re.compile(r"[A-Za-z]{2,}")
PLACEHOLDER = re.compile(r"\{\{\s*[\w.]+\s*\}\}|\{[\w.]+\}|%\d*\$?[sdif@]|%\([\w]+\)[sd]|<\d+>|</\d+>")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
TRANSLATABLE_ATTRS = ("alt", "title", "placeholder", "aria-label", "aria-description", "content", "value", "label")
STRUCT_TAGS = ("h1", "h2", "h3", "section", "nav", "form", "img", "button", "a", "input", "table", "li")


class Problem:
    def __init__(self, code, where, message):
        self.code, self.where, self.message = code, where, message

    def __str__(self):
        return "  %-4s %s  %s" % (self.code, self.where, self.message)


def _norm(s):
    return " ".join(s.split())


def _check_pair(key, ar, en, out, allow_same=(), script_checks=True):
    """Shared checks for one ar/en string pair."""
    ar, en = _norm(ar or ""), _norm(en or "")
    if not ar:
        out.append(Problem("P02", key, "Arabic text is empty"))
    if not en:
        out.append(Problem("P02", key, "English text is empty"))
    if not ar or not en:
        return
    if not script_checks:
        return
    translatable = bool(LATIN_WORD.search(PLACEHOLDER.sub("", en)))
    if ar == en and translatable and en not in allow_same:
        out.append(Problem("P03", key, "Arabic and English are identical (untranslated?): '%s'" % en[:50]))
    elif translatable and not AR_LETTER.search(ar) and en not in allow_same:
        out.append(Problem("P04", key, "Arabic variant contains no Arabic letters: '%s'" % ar[:50]))
    if AR_LETTER.search(en):
        out.append(Problem("P05", key, "English variant contains Arabic letters: '%s'" % en[:50]))
    pa, pe = sorted(PLACEHOLDER.findall(ar)), sorted(PLACEHOLDER.findall(en))
    if [re.sub(r"\s", "", p) for p in pa] != [re.sub(r"\s", "", p) for p in pe]:
        out.append(Problem("P06", key, "placeholders differ: ar=%s en=%s" % (pa, pe)))
    la, le = len(ar), len(en)
    if max(la, le) >= 40 and (la > 5 * le or le > 5 * la):
        out.append(Problem("P07", key, "lengths differ a lot (ar=%d, en=%d chars) - one side may be truncated" % (la, le)))


# ----------------------------------------------------------------- paired variants
class _Variants(HTMLParser):
    def __init__(self, attr):
        super().__init__(convert_charrefs=True)
        self.attr = attr
        self.stack = [dict(tag="#root", variant=None, kids=[], line=0)]
        self.attr_pairs = []      # (line, tag, attrname, ar, en)
        self.hard_attrs = []      # (line, tag, attrname, value)
        self.variants_used = False

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        line = self.getpos()[0]
        v = a.get(self.attr, "").lower() or None
        if v:
            self.variants_used = True
        names = set()
        for k in a:
            m = re.match(r"^data-(ar|en)-(.+)$", k)
            if m:
                names.add(m.group(2))
        for n in sorted(names):
            self.attr_pairs.append((line, tag, n, a.get("data-ar-" + n), a.get("data-en-" + n)))
        inside_variant = v or any(f["variant"] for f in self.stack)
        for n in ("alt", "title", "placeholder", "aria-label"):
            val = a.get(n, "").strip()
            if (val and n not in names and not inside_variant and a.get("dir", "").lower() != "ltr"
                    and (LATIN_WORD.search(val) or AR_LETTER.search(val))):
                self.hard_attrs.append((line, tag, n, val))
        node = dict(tag=tag, variant=v, kids=[], line=line, text=[], lang=a.get("lang", "").lower())
        self.stack[-1]["kids"].append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and len(self.stack) > 1:
            self.stack.pop()

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i]["tag"] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        for f in self.stack[1:]:
            if f["tag"] in ("script", "style"):
                return
        for f in self.stack[1:]:
            f["text"].append(data)


def check_variants(path, attr="data-lang"):
    out = []
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    p = _Variants(attr)
    p.feed(text)
    p.close()
    if not p.variants_used and not p.attr_pairs:
        out.append(Problem("P00", path, "no %s variants found - is this the right mode? (see --json / --pages)" % attr))
        return out, 0
    pairs = 0

    def walk(node):
        nonlocal pairs
        seq = [k for k in node["kids"] if k["variant"]]
        i = 0
        while i < len(seq):
            cur = seq[i]
            nxt = seq[i + 1] if i + 1 < len(seq) else None
            where = "%s:%d <%s>" % (os.path.basename(path), cur["line"], cur["tag"])
            if nxt is not None and nxt["variant"] != cur["variant"]:
                ar, en = (cur, nxt) if cur["variant"].startswith("ar") else (nxt, cur)
                pairs += 1
                if cur["tag"] != nxt["tag"]:
                    out.append(Problem("P08", where, "variant pair uses different tags: <%s> vs <%s>" % (cur["tag"], nxt["tag"])))
                # an explicit lang on a variant (language-switch labels) means "intentionally the other language"
                _check_pair(where, "".join(ar["text"]), "".join(en["text"]), out, script_checks=not (ar["lang"] or en["lang"]))
                i += 2
            else:
                other = "en" if cur["variant"].startswith("ar") else "ar"
                out.append(Problem("P01", where, "%s variant has no '%s' sibling next to it" % (cur["variant"], other)))
                i += 1
        for k in node["kids"]:
            if not k["variant"]:
                walk(k)

    walk(p.stack[0])
    for line, tag, name, ar, en in p.attr_pairs:
        where = "%s:%d <%s %s>" % (os.path.basename(path), line, tag, name)
        if ar is None or en is None:
            out.append(Problem("P01", where, "data-%s-%s has no matching data-%s-%s" % ("ar" if en is None else "en", name, "en" if en is None else "ar", name)))
        else:
            pairs += 1
            _check_pair(where, ar, en, out)
    for line, tag, name, value in p.hard_attrs:
        out.append(Problem("P09", "%s:%d <%s>" % (os.path.basename(path), line, tag),
                           "%s=\"%s\" is not translated - add data-ar-%s / data-en-%s" % (name, value[:30], name, name)))
    return out, pairs


# ----------------------------------------------------------------- JSON dictionaries
def _flatten(obj, prefix=""):
    flat = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            flat.update(_flatten(v, "%s.%s" % (prefix, k) if prefix else str(k)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            flat.update(_flatten(v, "%s[%d]" % (prefix, i)))
    else:
        flat[prefix] = "" if obj is None else str(obj)
    return flat


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def check_json(paths):
    out = []
    if len(paths) == 1:
        data = _load(paths[0])
        if isinstance(data, dict) and set(data) >= {"ar", "en"} and all(isinstance(data[k], dict) for k in ("ar", "en")):
            ar, en = _flatten(data["ar"]), _flatten(data["en"])
        else:
            flat = _flatten(data)
            ar = {k[:-3]: v for k, v in flat.items() if k.endswith(".ar")}
            en = {k[:-3]: v for k, v in flat.items() if k.endswith(".en")}
            if not ar and not en:
                out.append(Problem("P00", paths[0], "expected {\"ar\": {...}, \"en\": {...}} or {\"key\": {\"ar\": \"\", \"en\": \"\"}}"))
                return out, 0
    else:
        ar, en = _flatten(_load(paths[0])), _flatten(_load(paths[1]))
    for k in sorted(set(ar) - set(en)):
        out.append(Problem("P01", k, "key missing from English"))
    for k in sorted(set(en) - set(ar)):
        out.append(Problem("P01", k, "key missing from Arabic"))
    shared = sorted(set(ar) & set(en))
    for k in shared:
        _check_pair(k, ar[k], en[k], out)
    return out, len(shared)


# ----------------------------------------------------------------- two-page sites
class _Outline(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.counts = {t: 0 for t in STRUCT_TAGS}
        self.lang = self.dir = None
        self.alternates = {}
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if tag in self.counts:
            self.counts[tag] += 1
        if tag == "html":
            self.lang, self.dir = a.get("lang", "").lower(), a.get("dir", "").lower()
        if tag == "link" and "alternate" in a.get("rel", "").lower() and a.get("hreflang"):
            self.alternates[a["hreflang"].lower()] = a.get("href", "")
        if a.get("id"):
            self.ids.add(a["id"])

    handle_startendtag = handle_starttag


def check_pages(ar_path, en_path):
    out = []
    docs = {}
    for label, path in (("ar", ar_path), ("en", en_path)):
        o = _Outline()
        with open(path, encoding="utf-8") as fh:
            o.feed(fh.read())
        docs[label] = o
    a, e = docs["ar"], docs["en"]
    if not a.lang.startswith("ar") or a.dir != "rtl":
        out.append(Problem("P10", ar_path, 'expected <html lang="ar" dir="rtl">, found lang="%s" dir="%s"' % (a.lang, a.dir)))
    if not e.lang.startswith("en") or e.dir not in ("ltr", ""):
        out.append(Problem("P10", en_path, 'expected <html lang="en" dir="ltr">, found lang="%s" dir="%s"' % (e.lang, e.dir)))
    for label, o, path in (("ar", a, ar_path), ("en", e, en_path)):
        for need in ("ar", "en"):
            if not any(h == need or h.startswith(need + "-") for h in o.alternates):
                out.append(Problem("P11", path, 'missing <link rel="alternate" hreflang="%s"> (each page lists both languages, itself included)' % need))
    for tag in STRUCT_TAGS:
        if a.counts[tag] != e.counts[tag]:
            out.append(Problem("P12", "<%s>" % tag, "count differs: ar=%d en=%d" % (a.counts[tag], e.counts[tag])))
    for missing in sorted(a.ids ^ e.ids):
        out.append(Problem("P13", "#" + missing, "id exists in only one language (anchors and scripts will break)"))
    return out, sum(a.counts.values())


def main(argv=None):
    ap = argparse.ArgumentParser(prog="i18n_parity", description="Check Arabic/English content parity.")
    ap.add_argument("html", nargs="*", help="HTML file(s) using paired data-lang variants")
    ap.add_argument("--json", nargs="+", metavar="FILE", help="one combined dictionary, or AR then EN dictionaries")
    ap.add_argument("--pages", nargs=2, metavar=("AR_HTML", "EN_HTML"), help="two-page site: structural parity and hreflang")
    ap.add_argument("--variant-attr", default="data-lang")
    ap.add_argument("--format", choices=("text", "json"), default="text")
    ap.add_argument("--version", action="version", version=__version__)
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if not (args.html or args.json or args.pages) or (args.json and len(args.json) > 2):
        ap.print_usage(sys.stderr)
        return 2
    problems, checked = [], 0
    try:
        for path in args.html:
            p, n = check_variants(path, args.variant_attr)
            problems += p
            checked += n
        if args.json:
            p, n = check_json(args.json)
            problems += p
            checked += n
        if args.pages:
            p, n = check_pages(*args.pages)
            problems += p
            checked += n
    except (OSError, ValueError) as exc:
        print("i18n_parity: %s" % exc, file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(dict(checked=checked, problems=[vars(p) for p in problems]), ensure_ascii=False, indent=2))
    else:
        for p in problems:
            print(p)
        print("%d pair(s)/element(s) checked: %d problem(s)" % (checked, len(problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

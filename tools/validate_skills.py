#!/usr/bin/env python3
"""Validate every skill in skills/ against the Agent Skills specification
(https://agentskills.io/specification) and this repository's own conventions.

    python tools/validate_skills.py            # human-readable
    python tools/validate_skills.py --markdown # table for VALIDATION.md

Standard library only. If the reference validator is installed
(`pip install skills-ref`), it is run as well.
"""
import filecmp
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")
SHARED = os.path.join(ROOT, "shared", "scripts")
ALLOWED = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
RESERVED_WORDS = ("claude", "anthropic")
RESERVED_NAMES = {"synced", "anthropic-skills"}


def parse_frontmatter(text):
    """Minimal YAML subset: top-level scalars and one level of string maps."""
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with '---' on the first line")
    end = text.find("\n---", 4)
    if end < 0:
        raise ValueError("frontmatter is not closed with '---'")
    data, cur = {}, None
    for raw in text[4:end].split("\n"):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", raw)
        if m and not raw.startswith(" "):
            key, val = m.group(1), m.group(2).strip()
            if val == "":
                data[key] = {}
                cur = key
            else:
                data[key] = val.strip("\"'")
                cur = None
        elif raw.startswith(" ") and cur:
            k, _, v = raw.strip().partition(":")
            data[cur][k.strip()] = v.strip().strip("\"'")
        else:
            raise ValueError("cannot parse frontmatter line: %r" % raw)
    return data, text[end + 4:].lstrip("\n")


def check_skill(name):
    """Return a list of (check, ok, detail)."""
    d = os.path.join(SKILLS, name)
    res = []

    def add(check, ok, detail=""):
        res.append((check, bool(ok), detail))

    path = os.path.join(d, "SKILL.md")
    add("SKILL.md exists", os.path.isfile(path))
    if not os.path.isfile(path):
        return res
    text = open(path, encoding="utf-8").read()
    try:
        fm, body = parse_frontmatter(text)
    except ValueError as exc:
        add("frontmatter parses", False, str(exc))
        return res
    add("frontmatter parses", True)
    n = fm.get("name", "")
    add("name: 1-64 chars, a-z 0-9 hyphen", bool(re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", n)) and len(n) <= 64, n)
    add("name matches directory", n == name, "%s vs %s" % (n, name))
    add("name avoids reserved words", not any(w in n for w in RESERVED_WORDS) and n not in RESERVED_NAMES)
    desc = fm.get("description", "")
    add("description: 1-1024 chars", isinstance(desc, str) and 0 < len(desc) <= 1024, "%d chars" % len(desc))
    add("description says what and when", bool(re.search(r"\bUse when\b", desc)), "contains 'Use when'")
    add("description has no angle brackets", "<" not in desc and ">" not in desc)
    add("description in third person", not re.search(r"\b(I|you can|your)\b", desc))
    extra = set(fm) - ALLOWED
    add("only spec fields in frontmatter", not extra, ", ".join(sorted(extra)) or "name, description, license, compatibility, metadata")
    comp = fm.get("compatibility")
    add("compatibility <= 500 chars", comp is None or 0 < len(comp) <= 500, "%s chars" % (len(comp) if comp else "n/a"))
    meta = fm.get("metadata", {})
    add("metadata is a string map", isinstance(meta, dict) and all(isinstance(v, str) for v in meta.values()))
    lines = text.count("\n") + 1
    add("SKILL.md under 500 lines", lines < 500, "%d lines" % lines)
    tokens = int(len(re.findall(r"\S+", body)) * 1.4)
    add("body under ~5000 tokens", tokens < 5000, "~%d tokens" % tokens)
    links = re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", body) + re.findall(r"`((?:scripts|assets|references)/[\w./-]+)`", body)
    local = sorted({l for l in links if not re.match(r"^[a-z]+:", l)})
    missing = [l for l in local if not os.path.exists(os.path.join(d, l))]
    add("all referenced files exist", not missing, ", ".join(missing) or "%d links" % len(local))
    add("references one level deep", all(l.count("/") <= 1 for l in local))
    refs_dir = os.path.join(d, "references")
    refs = sorted(os.listdir(refs_dir)) if os.path.isdir(refs_dir) else []
    unlinked = [r for r in refs if "references/" + r not in local]
    add("every reference is linked from SKILL.md", not unlinked, ", ".join(unlinked) or "%d files" % len(refs))
    no_toc = [r for r in refs if open(os.path.join(refs_dir, r), encoding="utf-8").read().count("\n") > 100
              and "## Contents" not in open(os.path.join(refs_dir, r), encoding="utf-8").read()]
    add("long references have a contents list", not no_toc, ", ".join(no_toc))
    chained = []
    for r in refs:
        t = open(os.path.join(refs_dir, r), encoding="utf-8").read()
        if re.search(r"\]\((?!https?:)[^)]*\.md\)", t):
            chained.append(r)
    add("no reference-to-reference chains", not chained, ", ".join(chained))
    stale = []
    for f in sorted(os.listdir(SHARED)):
        if f.endswith(".py"):
            dest = os.path.join(d, "scripts", f)
            if not os.path.exists(dest) or not filecmp.cmp(os.path.join(SHARED, f), dest, shallow=False):
                stale.append(f)
    add("bundled scripts match shared/scripts", not stale, ", ".join(stale))
    exe = shutil.which("agentskills") or shutil.which("skills-ref")
    if exe:
        p = subprocess.run([exe, "validate", d], capture_output=True, text=True)
        add("skills-ref reference validator", p.returncode == 0, (p.stdout + p.stderr).strip().split("\n")[-1][:80])
    return res


def check_plugin():
    res = []
    for rel, required in ((".claude-plugin/plugin.json", ("name",)), (".claude-plugin/marketplace.json", ("name", "owner", "plugins"))):
        path = os.path.join(ROOT, rel)
        try:
            data = json.load(open(path, encoding="utf-8"))
            ok = all(k in data for k in required)
            res.append((rel + " parses with required fields", ok, ", ".join(required)))
            if rel.endswith("marketplace.json"):
                res.append(("marketplace has no $schema key", "$schema" not in data, ""))
                for pl in data["plugins"]:
                    src = pl.get("source")
                    res.append(("plugin '%s' source resolves" % pl.get("name"), isinstance(src, str) and os.path.isdir(os.path.join(ROOT, src)), str(src)))
        except (OSError, ValueError) as exc:
            res.append((rel + " parses", False, str(exc)))
    return res


def main():
    md = "--markdown" in sys.argv
    failed = 0
    groups = [(name, check_skill(name)) for name in sorted(os.listdir(SKILLS)) if os.path.isdir(os.path.join(SKILLS, name))]
    groups.append(("plugin manifests", check_plugin()))
    for name, res in groups:
        bad = [r for r in res if not r[1]]
        failed += len(bad)
        if md:
            print("\n### %s\n\n| Check | Result | Detail |\n|---|---|---|" % name)
            for check, ok, detail in res:
                print("| %s | %s | %s |" % (check, "pass" if ok else "**FAIL**", detail))
        else:
            print("%s: %d/%d checks passed" % (name, len(res) - len(bad), len(res)))
            for check, ok, detail in bad:
                print("  FAIL %s %s" % (check, ("(" + detail + ")") if detail else ""))
    if not md:
        print("OK" if not failed else "%d check(s) failed" % failed)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

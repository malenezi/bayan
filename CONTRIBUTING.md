# Contributing

Thank you for helping. The most useful contributions are small and specific.

## What is most valuable

1. **Language corrections** from native speakers: a glossary term that is not what your sector uses, a stiff example, an orthography slip. Open a "language" issue or a pull request with a one-line reason.
2. **Linter reports**: a false positive, or a real defect the linter missed. Include the smallest snippet that shows it.
3. **New lint rules** for defects you have seen in production.
4. **Verified rendering facts**: if a claim in a reference file is wrong in some browser, show the test case.
5. **New languages**: Hebrew, Persian and Urdu guidance (see the roadmap).

Please do not submit new skills that are prompt collections. A skill here needs a workflow, reference material someone would otherwise have to look up, and a way to check its output.

## Setup

```bash
git clone https://github.com/malenezi/bayan && cd bayan
make check        # Python 3.9+, no dependencies
```

Optional: `pip install skills-ref` adds the reference validator to `make validate`.

## Rules of the repository

- **Edit scripts in `shared/scripts/` only**, then run `make sync`. The copies in `skills/*/scripts/` exist so each skill is self-contained; CI fails if they drift.
- **Scripts use the standard library only** and keep non-ASCII characters as `\uXXXX` escapes in source.
- **Every lint rule has**: an entry in `RULES`, a test that triggers it, a test that shows a correct case passing, and a `DETAIL` entry in `tools/gen_rule_catalog.py`. Run `make catalog`.
- **Templates and examples must pass** `bidi_lint.py` and `i18n_parity.py`. If a template needs a physical property, add `bidi-lint-ignore` with the reason on that line.
- **Skills follow the Agent Skills specification**: only spec fields in frontmatter; `SKILL.md` under 500 lines; references one level deep, each linked from `SKILL.md`; a contents list in any reference over 100 lines. `make validate` checks this.
- **Rendering claims are tested, not remembered.** If you write "X renders as Y", check it in a browser first.
- **Examples use invented organisations.** No real brands, logos, people or data.

## Writing for a skill

- `SKILL.md` holds the workflow and the rules that are never optional. Depth goes in `references/`.
- Say why a rule exists; a model that understands the reason applies it to cases the rule did not list.
- Prefer one worked example to three abstract sentences.
- State defaults as defaults ("Western digits unless the product says otherwise").
- Arabic in examples is Modern Standard Arabic unless the point is regional.

## Adding a lint rule

1. Pick the next free id in the right group (`BD1xx` structure and text, `BD2xx` CSS, `BD3xx` utility classes, `DK4xx` decks).
2. Choose the severity honestly: **error** only for things that are always wrong; **warning** for defects with rare exceptions; **info** for "look at this".
3. Build in exemptions for the legitimate cases you know.
4. Add tests, the catalogue entry, run `make sync catalog check`.

## Commit and review

- Conventional commit prefixes are appreciated (`fix:`, `feat:`, `docs:`, `lint:`), not required.
- One topic per pull request.
- Maintainers review language changes for regional neutrality; expect a question about where a usage comes from.

## Conduct

Be respectful and specific. Disagreements about Arabic usage are normal: bring a source or an example, and assume the other person has one too.

# Why Bayan: the opportunity

Research done in November 2026, before any code was written.

## The decision

Build one deep, verifiable toolkit for **Arabic-first digital output** (websites, HTML decks, audits of existing code, interface copy) instead of another broad skill collection.

## What the ecosystem looks like

- **Volume is not the problem.** Automated trackers counted more than 24,000 GitHub repositories containing skill or plugin definitions by mid-2026, up from about 2,000 six months earlier ([Fast.io directory](https://fast.io/resources/awesome-claude-skills-directory-2026/)). The largest collections advertise over a thousand skills each.
- **Quality is.** Reviewers of these collections repeat the same caution: quality varies skill by skill, and many repositories are unfinished ([Ryan Doser's survey](https://ryandoser.com/?p=2012)).
- **The format is settled.** Skills follow the open [Agent Skills specification](https://agentskills.io/specification): a folder with `SKILL.md`, optional `scripts/`, `references/` and `assets/`, loaded progressively. Claude Code distributes them through plugins and marketplaces ([docs](https://code.claude.com/docs/en/skills)).

## The three candidates

| | Bilingual Arabic/English web | Enterprise benchmarking research | Cinematic HTML decks (AR/EN) |
|---|---|---|---|
| Demand | High and recurring: every organisation in the region publishes in both languages | High, but each engagement is bespoke | High among executives and trainers |
| Existing supply | A dozen small skills: usually one `SKILL.md`, no tests, no tooling | Crowded: research and "deep research" skills are among the most common, and first-party research features exist | A few single-file skills |
| Can correctness be checked by a script? | **Yes.** Direction, isolation, logical CSS, punctuation and parity are mechanical | No. Quality is judgment about sources and reasoning | Largely yes: it is the web problem plus deck conventions |
| Differentiation available | Large | Small | Large, and it shares a core with the web skill |

Searching for existing Arabic and RTL skills turned up entries such as `arabic-rtl-ui`, `rtl-support`, `arabic-rtl`, an Arabic presentation skill and an RTL document-translation skill. They confirm demand. None combines depth of guidance with a way to verify output, and most show a handful of installs.

## Why this one

1. **Underserved audience.** Arabic has hundreds of millions of speakers and a fast-growing digital public sector, yet AI-generated Arabic interfaces fail in the same predictable ways.
2. **The failure is checkable.** Most RTL defects are patterns in source: `margin-left`, a phone number without isolation, `letter-spacing` on Arabic. A linter can find them. That turns a skill from advice into a closed loop: generate, check, fix.
3. **One core, several products.** Bidirectional text, logical layout and Arabic typography underlie websites, decks, audits and copy. Building that core once makes four skills cheap to keep consistent.
4. **Useful without Claude.** The linter and parity checker run in any CI pipeline, which gives the repository a second audience and a reason to be starred, forked and wired into builds.
5. **Contribution-friendly.** A glossary term, a lint rule and a false-positive fix are small, reviewable contributions with tests. Hebrew, Persian and Urdu are natural extensions.

Benchmarking research was set aside: it is valuable, but it is crowded and its quality cannot be validated mechanically, so a repository could not prove it was better.

## What "better" means here

| Typical existing skill | Bayan |
|---|---|
| One `SKILL.md` of tips | Workflow in `SKILL.md`, depth in references loaded on demand |
| "Use logical properties" | A linter that reports each physical property with file, line and fix |
| No bilingual mechanics | A paired-variant pattern, a toggle, and a parity checker for three architectures |
| No Arabic language guidance | Style guide, glossary, patterns and an orthography checklist |
| Untested | 74 tests; every template and example linted in CI; rendering claims verified in a browser |

## Risks and how they are handled

- **Heuristic rules produce false positives.** Exemptions are built in (symmetric pairs, centering, `[dir]`-scoped rules, CSS variables), severities are graded, and suppressions are explicit. The audit skill teaches triage rather than blind fixing.
- **Language guidance is opinionated.** Defaults are stated as defaults; product glossaries override them; regional variants are flagged.
- **Model behaviour drifts.** The checks do not depend on the model. If generation gets worse or better, the linter still tells the truth about the output.

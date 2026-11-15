# Validation

How this repository was checked against the official specifications, and the results. Reproduce everything with `make check`.

## Sources

- Agent Skills specification: <https://agentskills.io/specification>
- Claude Code skills documentation: <https://code.claude.com/docs/en/skills>
- Claude Code plugin marketplaces: <https://code.claude.com/docs/en/plugin-marketplaces>
- Reference validator: `skills-ref` (`pip install skills-ref`, command `agentskills validate`)

## Checklist

### Skill format (Agent Skills specification)

- [x] Each skill is a directory containing `SKILL.md`
- [x] Frontmatter starts on line 1 and contains `name` and `description`
- [x] `name`: 1 to 64 characters, lowercase letters, digits and single hyphens, no leading or trailing hyphen
- [x] `name` matches the parent directory name
- [x] `description`: 1 to 1024 characters, states what the skill does and when to use it, includes trigger keywords (English and Arabic)
- [x] Only specification fields in frontmatter (`name`, `description`, `license`, `compatibility`, `metadata`), so the same files upload to the Claude apps and the Skills API, which reject other fields
- [x] `compatibility` under 500 characters; `metadata` is a string-to-string map
- [x] `SKILL.md` under 500 lines and under about 5,000 tokens (largest is 85 lines)
- [x] Detail lives in `references/`, templates in `assets/`, executable code in `scripts/`
- [x] File references are relative, use forward slashes, and are one level deep
- [x] Every reference file is linked from `SKILL.md` with a note on when to read it
- [x] Reference files over 100 lines open with a contents list
- [x] No reference file links to another reference file
- [x] Passes `agentskills validate` (skills-ref 0.1.1)

### Claude-specific conventions

- [x] Names avoid the reserved words "claude" and "anthropic" and the reserved folder names
- [x] Descriptions are written in the third person and contain no angle brackets
- [x] Scripts are self-contained (standard library only), print actionable error messages, and use documented exit codes
- [x] Each skill says what to do when scripts cannot run
- [x] Skills state defaults and ask for missing context instead of guessing silently

### Distribution

- [x] `.claude-plugin/plugin.json` with name, description, version, author, licence
- [x] `.claude-plugin/marketplace.json` with `name`, `owner`, `plugins`; no `$schema` key; marketplace name is not a reserved one
- [x] Skills sit at `skills/<name>/SKILL.md`, the layout Claude Code plugins load
- [x] `tools/build_dist.py` produces one zip per skill with the skill folder at the zip root

### Function

- [x] 74 automated tests pass (linter rules, parity modes, command-line behaviour, repository invariants)
- [x] Both templates and all four examples pass `bidi_lint.py` with zero findings
- [x] All bilingual templates and examples pass `i18n_parity.py`
- [x] The deliberately broken example produces the expected findings (31) and the fixed version produces none
- [x] Templates rendered in Chromium in both languages at 1280 px, and the web starter at 390 px: no script errors, no horizontal overflow, correct `lang`, `dir` and title after switching
- [x] Bidirectional rendering claims in `bidi-text.md` (ranges, dashed dates, phone numbers, signs, percent, handles) confirmed against a Chromium render

### Not verified here

- [ ] Installation through `/plugin marketplace add` (requires the repository to be public on GitHub)
- [ ] Upload of the zips to the Claude apps
- [ ] Python 3.9 to 3.12 (developed and tested on 3.13; the CI matrix covers 3.9 once pushed)
- [ ] Safari and Firefox rendering
- [ ] Review of the Arabic guidance by a second native-speaker editor

## Automated results

Output of `python tools/validate_skills.py --markdown`:

### arabic-html-slides

| Check | Result | Detail |
|---|---|---|
| SKILL.md exists | pass |  |
| frontmatter parses | pass |  |
| name: 1-64 chars, a-z 0-9 hyphen | pass | arabic-html-slides |
| name matches directory | pass | arabic-html-slides vs arabic-html-slides |
| name avoids reserved words | pass |  |
| description: 1-1024 chars | pass | 567 chars |
| description says what and when | pass | contains 'Use when' |
| description has no angle brackets | pass |  |
| description in third person | pass |  |
| only spec fields in frontmatter | pass | name, description, license, compatibility, metadata |
| compatibility <= 500 chars | pass | 90 chars |
| metadata is a string map | pass |  |
| SKILL.md under 500 lines | pass | 73 lines |
| body under ~5000 tokens | pass | ~1078 tokens |
| all referenced files exist | pass | 4 links |
| references one level deep | pass |  |
| every reference is linked from SKILL.md | pass | 3 files |
| long references have a contents list | pass |  |
| no reference-to-reference chains | pass |  |
| bundled scripts match shared/scripts | pass |  |
| skills-ref reference validator | pass | Valid skill: /home/claude/bayan/skills/arabic-html-slides |

### arabic-rtl-web

| Check | Result | Detail |
|---|---|---|
| SKILL.md exists | pass |  |
| frontmatter parses | pass |  |
| name: 1-64 chars, a-z 0-9 hyphen | pass | arabic-rtl-web |
| name matches directory | pass | arabic-rtl-web vs arabic-rtl-web |
| name avoids reserved words | pass |  |
| description: 1-1024 chars | pass | 543 chars |
| description says what and when | pass | contains 'Use when' |
| description has no angle brackets | pass |  |
| description in third person | pass |  |
| only spec fields in frontmatter | pass | name, description, license, compatibility, metadata |
| compatibility <= 500 chars | pass | 90 chars |
| metadata is a string map | pass |  |
| SKILL.md under 500 lines | pass | 86 lines |
| body under ~5000 tokens | pass | ~1143 tokens |
| all referenced files exist | pass | 6 links |
| references one level deep | pass |  |
| every reference is linked from SKILL.md | pass | 5 files |
| long references have a contents list | pass |  |
| no reference-to-reference chains | pass |  |
| bundled scripts match shared/scripts | pass |  |
| skills-ref reference validator | pass | Valid skill: /home/claude/bayan/skills/arabic-rtl-web |

### arabic-ux-writing

| Check | Result | Detail |
|---|---|---|
| SKILL.md exists | pass |  |
| frontmatter parses | pass |  |
| name: 1-64 chars, a-z 0-9 hyphen | pass | arabic-ux-writing |
| name matches directory | pass | arabic-ux-writing vs arabic-ux-writing |
| name avoids reserved words | pass |  |
| description: 1-1024 chars | pass | 614 chars |
| description says what and when | pass | contains 'Use when' |
| description has no angle brackets | pass |  |
| description in third person | pass |  |
| only spec fields in frontmatter | pass | name, description, license, compatibility, metadata |
| compatibility <= 500 chars | pass | 90 chars |
| metadata is a string map | pass |  |
| SKILL.md under 500 lines | pass | 62 lines |
| body under ~5000 tokens | pass | ~902 tokens |
| all referenced files exist | pass | 4 links |
| references one level deep | pass |  |
| every reference is linked from SKILL.md | pass | 4 files |
| long references have a contents list | pass |  |
| no reference-to-reference chains | pass |  |
| bundled scripts match shared/scripts | pass |  |
| skills-ref reference validator | pass | Valid skill: /home/claude/bayan/skills/arabic-ux-writing |

### rtl-audit

| Check | Result | Detail |
|---|---|---|
| SKILL.md exists | pass |  |
| frontmatter parses | pass |  |
| name: 1-64 chars, a-z 0-9 hyphen | pass | rtl-audit |
| name matches directory | pass | rtl-audit vs rtl-audit |
| name avoids reserved words | pass |  |
| description: 1-1024 chars | pass | 587 chars |
| description says what and when | pass | contains 'Use when' |
| description has no angle brackets | pass |  |
| description in third person | pass |  |
| only spec fields in frontmatter | pass | name, description, license, compatibility, metadata |
| compatibility <= 500 chars | pass | 146 chars |
| metadata is a string map | pass |  |
| SKILL.md under 500 lines | pass | 81 lines |
| body under ~5000 tokens | pass | ~1082 tokens |
| all referenced files exist | pass | 4 links |
| references one level deep | pass |  |
| every reference is linked from SKILL.md | pass | 3 files |
| long references have a contents list | pass |  |
| no reference-to-reference chains | pass |  |
| bundled scripts match shared/scripts | pass |  |
| skills-ref reference validator | pass | Valid skill: /home/claude/bayan/skills/rtl-audit |

### plugin manifests

| Check | Result | Detail |
|---|---|---|
| .claude-plugin/plugin.json parses with required fields | pass | name |
| .claude-plugin/marketplace.json parses with required fields | pass | name, owner, plugins |
| marketplace has no $schema key | pass |  |
| plugin 'bayan' source resolves | pass | ./ |

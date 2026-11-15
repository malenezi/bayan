# RTL and Arabic audit: {product or page}

**Date:** {date}  
**Scope:** {files, routes or build audited}  
**Languages:** {e.g. Arabic (primary), English}  
**Method:** `bidi_lint` {version} static scan, plus manual review of {what was rendered or read}

## Summary

{Two or three sentences: overall state, the most important problem, and what was done.}

| | Before | After |
|---|---:|---:|
| Errors | {n} | {n} |
| Warnings | {n} | {n} |
| Info | {n} | {n} |
| Manual findings | {n} | {n} |

## What a reader sees today

{Three to five concrete, user-visible defects, most severe first. Name the screen and describe the symptom, not the rule. Example: "On the contact page the phone number reads 4567 123 11 966+."}

## Findings by category

### 1. Direction and structure
{Finding, where, rule id if any, fix applied or proposed.}

### 2. Layout and CSS
{…}

### 3. Bidirectional text
{…}

### 4. Typography
{…}

### 5. Icons, components and motion
{…}

### 6. Content and translation
{…}

## Fixed in this pass

- {change, files touched}

## Not fixed, and why

| Item | Reason | Owner or next step |
|---|---|---|
| {e.g. carousel direction} | {third-party library needs its RTL option; requires a dependency upgrade} | {team} |

## Decisions needed

- {e.g. Digit system: the site mixes Western and Arabic-Indic digits. Choose one.}
- {e.g. Chart direction: should time series run left-to-right in Arabic?}

## Keeping it fixed

- Add to CI: `python scripts/bidi_lint.py src/ --strict`
- {Parity check command that fits the project}
- {Any convention added, e.g. "logical utilities only; `rtl:` variants for transforms"}

## Appendix: scanner output

{Paste the `--format md` report, or attach it.}

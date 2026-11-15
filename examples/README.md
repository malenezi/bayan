# Examples

Four end-to-end runs. Each folder holds the prompt, the output, and the commands that verify it. All outputs in this folder pass the checks in CI (`tests/test_repo.py`).

| Example | Skill | What it shows |
|---|---|---|
| [01-bilingual-site](01-bilingual-site/) | `arabic-rtl-web` | A two-page Arabic/English site with one shared stylesheet, `hreflang`, and a parity check between the pages |
| [02-executive-deck](02-executive-deck/) | `arabic-html-slides` | A nine-slide executive proposal, Arabic first, English on the `L` key, print-ready |
| [03-rtl-audit](03-rtl-audit/) | `rtl-audit` | A broken Arabic page, the scan that finds 31 problems, and the fixed page |
| [04-ui-strings](04-ui-strings/) | `arabic-ux-writing` | A machine-style Arabic strings file reviewed and rewritten, with the parity check |

Open the HTML files directly in a browser. Fonts load from Google Fonts; offline, the pages fall back to system Arabic fonts.

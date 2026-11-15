PY ?= python3
LINT = $(PY) shared/scripts/bidi_lint.py
PARITY = $(PY) shared/scripts/i18n_parity.py

.PHONY: check test validate sync catalog lint dist

check: sync-check test validate lint   ## everything CI runs

test:            ## unit and repository tests
	$(PY) -m unittest discover -s tests

validate:        ## Agent Skills spec + repository conventions
	$(PY) tools/validate_skills.py

sync:            ## copy shared/scripts into each skill
	$(PY) tools/sync_shared.py

sync-check:
	$(PY) tools/sync_shared.py --check
	$(PY) tools/gen_rule_catalog.py --check

catalog:         ## regenerate the rule catalogue
	$(PY) tools/gen_rule_catalog.py

lint:            ## lint every template and example
	$(LINT) --strict skills/arabic-rtl-web/assets examples/01-bilingual-site examples/03-rtl-audit/after.html examples/04-ui-strings/ar.json
	$(LINT) --strict --profile deck skills/arabic-html-slides/assets examples/02-executive-deck
	$(PARITY) skills/arabic-rtl-web/assets/starter-bilingual.html skills/arabic-html-slides/assets/deck-starter.html examples/02-executive-deck/deck.html
	$(PARITY) --pages examples/01-bilingual-site/site/ar/index.html examples/01-bilingual-site/site/en/index.html
	$(PARITY) --json examples/04-ui-strings/ar.json examples/04-ui-strings/en.json

dist:            ## package each skill as dist/<skill>.zip
	$(PY) tools/build_dist.py

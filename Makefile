SHELL:=/usr/bin/env bash

.PHONY: style
style:
	poetry run black .
	poetry run isort .
	poetry run pycln .
	poetry run mypy --install-types --non-interactive .
	poetry run flake8 .
	poetry run doc8 -q docs

.PHONY: unit
unit:
ifeq ($(ci),1)
		poetry run pytest --no-testmon $(if $(dburi),-- dburi $(dburi),)  # don't add --dburi if it's unset
else
	poetry run pytest --no-cov
endif

.PHONY: package
package:
	poetry check
	poetry run pip check
	poetry run safety check --full-report

.PHONY: translate
translate:
	poetry run pybabel extract -o ./locales/base.pot ./pinger_bot
	poetry run pybabel update -d ./locales -i ./locales/base.pot
	poetry run pybabel compile -d ./locales

.PHONY: test
test: style package unit

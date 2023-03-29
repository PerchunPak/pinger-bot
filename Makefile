SHELL:=/usr/bin/env bash

.PHONY: format
format:
	black .
	isort .
	pycln .

.PHONY: lint
lint:
	mypy .
	flake8 .
	cruft check
	doc8 -q docs

.PHONY: style
style: format lint

.PHONY: unit
unit:
ifeq ($(ci),1)  # don't add --dburi if it's unset
	pytest --no-testmon $(if $(dburi), --dburi $(dburi),)
else
	pytest --no-cov $(if $(dburi), --dburi $(dburi),)
endif

.PHONY: package
package:
	poetry check
	pip check
	safety check --full-report --ignore 51668

.PHONY: translate
translate:
	pybabel extract -o ./locales/base.pot ./pinger_bot
	pybabel update -d ./locales -i ./locales/base.pot
	pybabel compile -d ./locales

.PHONY: test
test: style package unit

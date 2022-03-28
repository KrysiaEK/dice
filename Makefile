SHELL:=/usr/bin/env bash
all: flake wemake-python-styleguide isort pipenv_check django_migrations_linter dotenv_linter vulture safety

flake:
	@echo "Flake8"
	@flake8

wemake-python-styleguide:
	@echo "Wemake python styleguide"
	@flake8 .

isort:
	@echo "Isort"
	@isort . --diff

pipenv_check:
	@echo "Pipenv check"
	@pipenv check

django_migrations_linter:
	@echo "Django Migrations Linter"
	@python manage.py lintmigrations
	@python manage.py makemigrations --dry-run --check

dotenv_linter:
	@echo "Dotenv Linter"
	@dotenv-linter lint dice/config/.env

vulture:
	@echo "Vulture"
	@vulture .

safety:
	@echo "Safety"
	@safety check

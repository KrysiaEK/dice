all: flake isort pipenv_check django_migrations_linter dotenv_linter vulture

flake:
	@echo "Flake8"
	-@flake8

isort:
	@echo "Isort"
	-@isort . --diff

pipenv_check:
	@echo "Pipenv check"
	-@pipenv check

django_migrations_linter:
	@echo "Django Migrations Linter"
	-@python manage.py lintmigrations

dotenv_linter:
	@echo "Dotenv Linter"
	-@dotenv-linter lint dice/config/.env

vulture:
	@echo "Vulture"
	-@vulture .

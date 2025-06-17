# Makefile for A3CP development

# Check that all required environment variables are set
check-env:
	python scripts/check_env.py

# Run pre-commit hooks on all files
pre-commit:
	pre-commit install
	pre-commit run --all-files

# Run tests using pytest
test:
	pytest

# Run linting and formatting checks
lint:
	pre-commit run --all-files

# Run Django development server (if applicable)
devserver:
	python manage.py runserver

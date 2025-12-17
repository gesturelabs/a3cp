# Makefile for A3CP development

# Check that all required environment variables are set
validate-env:
	python scripts/validate_env.py

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

# Run development server (if applicable)
devserver:
	uvicorn apps.ui.main:app --host 127.0.0.1 --port 8000 --reload

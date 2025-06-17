check-env:
	python scripts/check_env.py

pre-commit:
    pre-commit install
    pre-commit run --all-files

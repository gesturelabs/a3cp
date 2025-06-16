# TESTING.md

## Running Tests Locally

To run tests and ensure that all module imports resolve correctly (e.g., `from api.main import app`), you must set the Python module search path to the project root:

    PYTHONPATH=. pytest

### Optional: Shell Alias

To simplify repeated test runs, you can define a shell alias:

    alias test="PYTHONPATH=. pytest"

Then run tests with:

    test

---

## Environment Variables

Tests rely on certain environment variables, especially those required by the `Settings` class. These can be provided through a `.env` file in the project root. For test-specific values, create a `.env.test` file and configure loading behavior in your settings logic if needed.

---

## Project Structure Assumptions

The following structure is assumed:

    A3CP_GestureLabs_WebApp/
    ├── api/
    ├── apps/
    ├── tests/
    ├── .env
    ├── requirements.txt
    └── ...

The `api/` and `apps/` directories are expected to be top-level Python packages.

---

## Running Tests in CI

The GitHub Actions CI pipeline sets:

    PYTHONPATH=.

at the job level. This ensures that test imports work the same way in CI as they do locally. You do not need to manually patch `sys.path` in your test files.

---

## Notes

- The project uses Pydantic v2.
- `Settings` classes use `model_config = ConfigDict(...)` instead of `class Config`.
- Extra environment variables are ignored via `extra = "ignore"`.
- Required fields such as `SECRET_KEY`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD` must be available in the environment or `.env`.


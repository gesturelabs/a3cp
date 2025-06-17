============================================================
 A3CP Developer Setup Guide
============================================================

This guide explains how to set up your development environment
for working on A3CP. It covers repo setup, virtualenv, Python
dependencies, environment variables, environment validation,
Makefile usage, pre-commit hooks, and basic troubleshooting.

------------------------------------------------------------
 1. CLONE THE REPOSITORY
------------------------------------------------------------

    git clone git@github.com:gesturelabs/a3cp.git
    cd a3cp

Note: SSH key access is required. Ask an admin to add your key.

------------------------------------------------------------
 2. PYTHON VIRTUAL ENVIRONMENT
------------------------------------------------------------

A virtual environment isolates your Python dependencies.

To activate the environment (after logging into the server):

    source /opt/a3cp-env/bin/activate

To deactivate:

    deactivate

If the environment does not exist yet (rare):

    python3 -m venv /opt/a3cp-env
    source /opt/a3cp-env/bin/activate
    pip install -r requirements.txt

------------------------------------------------------------
 3. ENVIRONMENT VARIABLES
------------------------------------------------------------

Copy the example file and edit your local `.env`:

    cp .env.example .env

This file is NOT committed to git. Edit values as needed:

    - SECRET_KEY=
    - DEBUG=
    - ALLOWED_HOSTS=
    - INFER_API_URL=
    - UVICORN_PORT=
    - DB_USER=, DB_PASSWORD=, etc.

To validate your `.env`:

    make check-env

This will check that all required variables are present and warn
you about optional ones.

------------------------------------------------------------
 4. INSTALL DEPENDENCIES
------------------------------------------------------------

Activate the virtualenv first:

    source /opt/a3cp-env/bin/activate

Then install required packages:

    pip install -r requirements.txt

To install dev tools (linters, tests, pre-commit):

    pip install -r requirements-dev.txt

------------------------------------------------------------
 5. PRE-COMMIT HOOKS (MANDATORY)
------------------------------------------------------------

To enforce code standards, run:

    pre-commit install
    pre-commit run --all-files

This ensures Black, Ruff, isort, and other checks are run before each commit.

Failing to do this may cause your PRs or CI jobs to fail.

------------------------------------------------------------
 6. MAKEFILE COMMANDS
------------------------------------------------------------

Useful shortcuts:

    make check-env     # Check required env vars
    make test          # Run test suite
    make lint          # Run formatters and linters
    make devserver     # Run Django development server
    make infer         # Run FastAPI inference server (if configured)

------------------------------------------------------------
 7. RUNNING THE DJANGO DEVELOPMENT SERVER
------------------------------------------------------------

Usually done on the Hetzner server, but locally you can:

    python manage.py runserver

Or, for prod-like config:

    ./scripts/dev.sh

------------------------------------------------------------
 8. GIT WORKFLOW
------------------------------------------------------------

Typical development flow:

    git pull origin main
    # make changes
    git add .
    git commit -m "Meaningful message"
    git push origin main

Do not push to `main` if your code fails tests or pre-commit hooks.

------------------------------------------------------------
 9. TESTING
------------------------------------------------------------

Run tests with:

    pytest

Make sure your virtualenv is active and `.env` is loaded.

------------------------------------------------------------
 10. TROUBLESHOOTING
------------------------------------------------------------

Check Gunicorn (if on Hetzner):

    systemctl status a3cp-gunicorn
    systemctl restart a3cp-gunicorn

Restart Nginx:

    systemctl restart nginx

Check environment vars:

    make check-env

------------------------------------------------------------
 MAINTAINED BY: gesturelabs.org team
------------------------------------------------------------

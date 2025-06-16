============================================================
 A3CP Developer Setup Guide
============================================================

This guide explains how to set up your development environment
for working on A3CP. It covers repo setup, virtualenv, Python
dependencies, environment variables, and useful scripts.

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

You must activate the virtualenv before running:

    - python manage.py ...
    - pip install ...
    - pytest
    - scripts/dev.sh

If the environment does not exist yet (rare):

    python3 -m venv /opt/a3cp-env
    source /opt/a3cp-env/bin/activate
    pip install -r requirements.txt

------------------------------------------------------------
 3. ENVIRONMENT VARIABLES
------------------------------------------------------------

Copy the example file and edit your local `.env`:

    cp .env.example .env

Edit values as needed. This file is NOT committed to git.

Important variables:
    SECRET_KEY=
    DEBUG=
    ALLOWED_HOSTS=
    INFER_API_URL=

------------------------------------------------------------
 4. INSTALL DEPENDENCIES
------------------------------------------------------------

Activate the virtualenv first:

    source /opt/a3cp-env/bin/activate

Then install required packages:

    pip install -r requirements.txt

To freeze current packages into the requirements file:

    pip freeze > requirements.txt

------------------------------------------------------------
 5. RUNNING THE DJANGO DEVELOPMENT SERVER
------------------------------------------------------------

Usually this is done on the live Hetzner instance for now.

You can run locally (if needed):

    python manage.py runserver

Or use the development script (for production-like settings):

    ./scripts/dev.sh

Note: HTTPS-only features may not behave correctly in local dev.

------------------------------------------------------------
 6. GIT WORKFLOW
------------------------------------------------------------

Typical flow:

    git pull origin main
    # make changes
    git add .
    git commit -m "Your message here"
    git push origin main

Only push to `main` if your code passes local checks.

------------------------------------------------------------
 7. TESTING
------------------------------------------------------------

Run unit tests with:

    pytest

Coverage reporting and CI will be added later.

------------------------------------------------------------
 8. TROUBLESHOOTING
------------------------------------------------------------

Check Gunicorn status (if running live):

    systemctl status a3cp-gunicorn

Restart Gunicorn:

    systemctl restart a3cp-gunicorn

Restart Nginx:

    systemctl restart nginx

------------------------------------------------------------
 MAINTAINED BY: gesturelabs.org team
------------------------------------------------------------

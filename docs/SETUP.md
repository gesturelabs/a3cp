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
 2. PYTHON ENVIRONMENT
------------------------------------------------------------

----------------------------
 Server (Hetzner)
----------------------------

Activate the server environment:

    source /opt/a3cp-env/bin/activate

To deactivate:

    deactivate

----------------------------
 Local (Recommended)
----------------------------

Use a virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

Install dependencies:

    pip install -r requirements.txt

You can work without a virtualenv, but this is discouraged.

To deactivate:

    deactivate


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
 4. RUNNING THE SERVER
------------------------------------------------------------

----------------------------
 Locally
----------------------------

Run the Django dev server:

    python manage.py runserver

Or use the wrapper script:

    ./scripts/dev.sh

Local URLs:
    Django: http://localhost:8000
    FastAPI (if running): http://localhost:9000

Note: HTTPS-only logic may break locally.

----------------------------
 Production (Admins Only)
----------------------------

To check service status:

    sudo systemctl status a3cp-gunicorn

To restart services:

    sudo systemctl restart a3cp-gunicorn
    sudo systemctl restart nginx


------------------------------------------------------------
 6. GIT WORKFLOW
------------------------------------------------------------

Typical flow:

    git checkout -b feat/your-feature
    # make changes
    git add .
    git commit -m "Describe your change"
    git push origin feat/your-feature
    # Open a pull request into `main`

Never push directly to `main`.

------------------------------------------------------------
 7. TESTING
------------------------------------------------------------

Run unit tests with:

    pytest

More structured coverage and CI integration is planned.

------------------------------------------------------------
 8. SIMULATED MESSAGE TESTING
------------------------------------------------------------

You can simulate message input without deploying live:

    python scripts/simulate_contextual_profiler.py

This is useful for testing modules like the LLM Profiler offline.

------------------------------------------------------------
 9. TROUBLESHOOTING (FOR ADMINS)
------------------------------------------------------------

If working on the production server:

    systemctl status a3cp-gunicorn     # View Django service status
    systemctl restart a3cp-gunicorn    # Restart Django app
    systemctl restart nginx            # Restart web server

Only use these if explicitly permitted.

------------------------------------------------------------
 MAINTAINED BY: gesturelabs.org team
------------------------------------------------------------

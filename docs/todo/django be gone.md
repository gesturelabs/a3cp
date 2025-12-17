# Post-Django FastAPI Consolidation — TODO

## 1. Clean CI Environment Variables
- Remove Django-specific or misleading env vars from CI:
  - `DB_ENGINE=django.db.backends.postgresql`
  - Django-style `SECRET_KEY` naming if no longer used
  - Any `DJANGO_*` variables
- Replace with FastAPI-appropriate variables where needed:
  - `DATABASE_URL` or explicit Postgres vars
  - `APP_ENV`, `LOG_LEVEL`, etc. (as appropriate)

## 2. Enforce “No Django” Guarantee in CI
- Keep a permanent CI guard step that fails if Django becomes importable:
  - `importlib.util.find_spec("django") must be None`
- Prevents accidental re-introduction via dependencies or scripts.

## 3. Verify Deployment Services
- Inspect systemd unit files:
  - `a3cp-ui.service`
  - `a3cp-api.service`
- Confirm:
  - No references to Django, `manage.py`, or `gunicorn config.wsgi`
  - Services use `uvicorn` with FastAPI entrypoints
- Align service naming and restart commands with FastAPI-only stack.

## 4. Plan Postgres Schema & Migration Strategy (No Code Yet)
- Decide on database approach:
  - SQLAlchemy + Alembic
  - SQLModel + Alembic
  - Raw SQL migrations
- Clarify:
  - What data must persist for the A3CP demo vs. production
  - Whether migrations are needed immediately or can be deferred
- Define when and how schema creation will happen in deploy/CI.

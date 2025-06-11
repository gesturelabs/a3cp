# DEPLOYMENT.md — A3CP Production Deployment (2025)

This document describes how the A3CP platform is deployed to the production server using GitHub Actions and a GitHub App. Manual server administration is deprecated except for debugging, rollback, or service monitoring.

====================================================================
 OVERVIEW
====================================================================

A3CP is deployed from the `main` branch on GitHub to a Hetzner VPS.

- Server OS: Ubuntu 24.04 LTS
- Domain: gesturelabs.org
- Stack: Django (port 8000), FastAPI (port 9000)
- Web server: Nginx with HTTPS via Certbot
- App server: Gunicorn (Django) + systemd
- DB: PostgreSQL (localhost)

All deployments are handled through CI/CD.

====================================================================
 DEPLOYMENT WORKFLOW
====================================================================

1. Developer pushes to `main` (via PR with CI pass).
2. GitHub Actions triggers `.github/workflows/deploy.yml`.
3. Workflow does:
   - Auth via GitHub App
   - SSH into VPS
   - Run deploy script:
     ```
     git pull
     pip install -r requirements.txt
     python manage.py migrate --settings=config.settings.prod
     python manage.py collectstatic --noinput --settings=config.settings.prod
     sudo systemctl restart a3cp-gunicorn
     ```

====================================================================
 REQUIRED GITHUB SECRETS
====================================================================

Set these in GitHub → Settings → Secrets → Actions:

- `GH_APP_ID` — GitHub App ID
- `GH_APP_PRIVATE_KEY` — Base64-encoded `.pem` private key
- `VPS_HOST` — Domain or IP of VPS
- `VPS_USER` — SSH user (e.g. `deploy`)
- `VPS_KEY` — Base64-encoded private key for VPS access

====================================================================
 SERVER DIRECTORY STRUCTURE
====================================================================

/opt/a3cp-app/ ← Cloned repo
/opt/a3cp-env/ ← Python virtualenv
/etc/systemd/system/ ← Contains a3cp-gunicorn.service
/etc/nginx/sites-available/ ← Nginx config


====================================================================
 ENVIRONMENT VARIABLES (.env.production)
====================================================================

This file must exist on the server but is never committed.

Example:

DB_ENGINE=django.db.backends.postgresql
DB_NAME=a3cp
DB_USER=a3cp_user
DB_PASSWORD=example_password
DB_HOST=localhost
DB_PORT=5432

SECRET_KEY=***
DEBUG=False
ALLOWED_HOSTS=gesturelabs.org,www.gesturelabs.org


====================================================================
 MANUAL SERVICE COMMANDS
====================================================================

Use these after SSHing into the VPS:

sudo systemctl restart a3cp-gunicorn ← Restart Django app
sudo systemctl restart nginx ← Restart web server
sudo systemctl status a3cp-gunicorn ← View app logs


====================================================================
 ROLLBACK PROCEDURE (PLANNED)
====================================================================

For now:

cd /opt/a3cp-app
git reset --hard <previous_commit>
sudo systemctl restart a3cp-gunicorn


Script `scripts/rollback.sh` is under development.

====================================================================
 LOCAL DEV NOTES
====================================================================

- Use `.env.development` locally
- Never use `runserver` in production
- Use `./scripts/dev.sh <command>` to safely run Django CLI tools on production server

====================================================================
 FASTAPI DEPLOYMENT (PLANNED)
====================================================================

FastAPI app will serve `/api/infer/` on port `9000`.

To prepare:

- Reserve port in Nginx
- Add `fastapi.service` under systemd
- Document in `docs/deploy/FastAPI.md`

====================================================================
 CI STATUS AND TESTING
====================================================================

- CI uses `.github/workflows/test.yml`
- CI expects `.env.example.prod` for required variables
- `.env.production` must exist on VPS

====================================================================
 FUTURE IMPROVEMENTS
====================================================================

- Rollback is currently manual. A rollback script is planned but not required for MVP.
- Add Slack/email failure alerts
- Add versioned release tags

====================================================================
 END OF DEPLOYMENT INSTRUCTIONS
====================================================================
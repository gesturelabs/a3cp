# CHANGELOG.md


## [2025-06-05] A3CP Deployment: Gunicorn + Nginx + Static Files

### Summary
Completed server-side production deployment of A3CP Django app using Gunicorn and Nginx on Hetzner VPS. Verified HTTPS, systemd service, static file delivery, and ownership best practices.

### Changes
- Created PostgreSQL DB and granted schema permissions to `a3cp_admin`
- Created `a3cp` system user for running Gunicorn process securely
- Configured `a3cp-gunicorn.service` systemd unit:
  - Bound Gunicorn to `127.0.0.1:8000`
  - Set working directory, user, and environment file
  - Enabled daemon reload and auto-restart
- Ensured ownership of app and virtualenv:
  - `chown -R a3cp:www-data /opt/a3cp-app /opt/a3cp-env`
- Generated and verified SSL certificates with Certbot for `gesturelabs.org`
- Configured Nginx reverse proxy:
  - Redirect HTTP to HTTPS
  - Proxied `/` to Gunicorn and `/api/infer/` to FastAPI stub
  - Set up `/static/` via `collectstatic` and verified file serving
- Verified application home page and static assets load correctly via `curl` and browser
- Confirmed Nginx config is syntactically valid with `nginx -t`

### Next Steps
- Add support for `/media/` file uploads
- Set up `/api/infer/` FastAPI routing and WSGI/ASGI integration
- Enable production logging and harden error handling


## [2025-06-05] CI/CD Ruleset Lockdown & Workflow Transition

### Added
- Enforced GitHub branch protection ruleset on `main`:
  - Require pull request before merging
  - Require linear history (no merge commits)
  - Require 1 approving review
  - Require conversation resolution before merge
  - Require CI Checks status to pass before merge
- Restored `.github/workflows/ci.yml` to run:
  - `python manage.py check`
  - `pytest`
- Made repository public
- Verified `.gitignore` excludes private credentials (`private-key.b64`, `.env`)
- Confirmed `private-key.b64` no longer exists in git history
- Confirmed no deploy keys remain active in repository

### Changed
- Development workflow changed:
  - From: direct development and deployment on Hetzner VPS
  - To: commit locally → push to GitHub → auto-deploy to Hetzner via GitHub Actions
- Deployment authentication now uses GitHub App credentials, not user SSH keys
- All changes to `main` must go through pull request + CI + approval

### Outstanding
- [ ] PostgreSQL integration incomplete (Django cannot connect)
- [ ] Add simple rollback command (`rollback.sh`) for production
- [ ] Document `deploy.yml` and GitHub App install/config process
- [ ] Improve `prod.py` and `.env` PostgreSQL configuration
- [ ] Add notification or fallback for failed deployments


## [2025-06-04] GitHub App-Based Auto-Deploy Pipeline Operational

### Added
- Created and installed GitHub App `A3CP Deployer` under `gesturelabs` org.
- Generated and securely stored a `.pem` private key for GitHub App authentication.
- Set appropriate **repository permissions** (`Contents: Read & Write`, `Metadata: Read`) for the app.
- Restricted app installation to `gesturelabs/a3cp` repository.
- Added the following repository secrets for deployment:
  - `GH_APP_ID` — GitHub App ID
  - `GH_APP_PRIVATE_KEY` — Base64-encoded private key for GitHub App
  - `VPS_HOST` — IP/domain of Hetzner server
  - `VPS_USER` — SSH username on VPS
  - `VPS_KEY` — Base64-encoded private SSH key for access

### Changed
- Replaced `deploy_key` SSH workflow with GitHub App token authentication via `tibdex/github-app-token@v2`.
- Updated `deploy.yml` GitHub Actions workflow:
  - Triggers on `push` to `main`
  - Authenticates as GitHub App
  - SSHs into Hetzner VPS and performs:
    - `git pull`
    - `pip install -r requirements.txt`
    - `python manage.py migrate`
    - `python manage.py collectstatic`
    - `sudo systemctl restart a3cp-gunicorn`

### Verified
- ✅ Workflow successfully triggers on push to `main`
- ✅ Authentication via GitHub App works
- ✅ VPS pulls latest code and redeploys cleanly

### Notes
- New workflow: **local → GitHub → Hetzner**
  - No need for developer SSH key management
  - GitHub App manages deployment auth
- GitHub Actions are now decoupled from contributor local machines

### Next Steps
- [ x] Remove unused deploy keys (if any remain)

- [ ] Document `deploy.yml` and app install process for future maintainers







## [2025-06-04] PostgreSQL Prep & Git Deployment Sync

### Changed
- Updated `config/settings/prod.py` to reference PostgreSQL via `.env`.
- Committed local changes made on Hetzner to Git (hotfixes to `prod.py`, `manage.py`, `CHANGELOG.md`).

### Infra
- Installed PostgreSQL 16 on Hetzner VPS.
- Created database `a3cp_pgsql` and user `a3cp_admin` with appropriate privileges.
- Updated `.env` with PostgreSQL credentials and confirmed visibility from `prod.py`.
- `python manage.py check` now passes, but `migrate` still fails due to `DATABASES` misconfiguration.

### Git & CI
- Aligned workflow to follow: local → GitHub → Hetzner.
- Initial GitHub push triggered CI/CD but **deploy job failed**.
- Deployment debugging pending.

### Outstanding
- PostgreSQL integration not yet functional — Django cannot connect.
- Deployment pipeline must be fixed to support automatic syncing from GitHub.


## [2025-06-03] Environment & Import Resolution Fixes

### Fixed
- Resolved `ModuleNotFoundError: No module named 'a3cp'` by ensuring correct working directory (`/opt/a3cp-app`) and `DJANGO_SETTINGS_MODULE` usage.
- Corrected Python path resolution and `sys.path` setup to include Django and local packages.
- Verified `manage.py` works with `config.settings.prod` without crashing.
- Confirmed all required packages are present in `/opt/a3cp-env/lib/python3.12/site-packages`.
- Validated `python manage.py check` and `shell` execute cleanly in production settings.

### Infra
- Ensured active virtual environment is `/opt/a3cp-env/`
- Confirmed Django 5.2.1 is installed and functional under Python 3.12.3

System is now import-clean, Django apps resolve properly, and shell/check commands execute without issue.


## [2025-06-02] - Environment & VS Code Remote Setup

### Added
- Connected to Hetzner VPS via VS Code Remote SSH.
- Verified connection using `~/.ssh/config` and key-based login.
- Opened remote folder and accessed `/opt/a3cp-app/` workspace.
- Activated Python virtual environment `a3cp-env` inside VS Code.

### Fixed
- Clarified SSH config setup and remote folder navigation.
- Ensured remote Python interpreter `/opt/a3cp-env/bin/python` is selected and active in VS Code.

✅ Environment now fully editable and runnable from VS Code over SSH.

## [2025-06-02] - Deployment Documentation Finalized

### Added
- Completed `docs/DEPLOYMENT.md` covering full production setup:
  - System requirements and firewall setup
  - Nginx config for Django and FastAPI endpoints
  - Gunicorn service configuration via systemd
  - HTTPS setup and certbot auto-renewal

✅ Task complete: `Document setup process in docs/DEPLOYMENT.md`

## [2025-06-02] - Routing Setup and Bug Fixes

### Added
- Created `pages` Django app under `apps/pages/`.
- Added basic views: `home`, `ui`, and `docs` returning simple `HttpResponse`s.
- Registered URL routes for `/`, `/ui/`, and `/docs/` in `apps/pages/urls.py`.
- Included `apps.pages.urls` in the root `config/urls.py`.

### Fixed
- Corrected app label in `PagesConfig.name` from `app.pages` to `apps.pages`.
- Resolved `ModuleNotFoundError: No module named 'config_tmp'` by restoring correct `DJANGO_SETTINGS_MODULE` to `'config.settings'`.
- Resolved duplicate app label error (`Application labels aren't unique, duplicates: pages`).

### Deployment
- Restarted services using:
  - `sudo systemctl restart a3cp-gunicorn` — restart the Django app server.
  - `sudo systemctl restart nginx` — restart the Nginx web server.
- Verified:
  - Gunicorn status via `systemctl status a3cp-gunicorn`.
  - Page routing via manual browser testing.

✅ Task complete: `Route all other pages via Django + HTMX (/ /ui /docs)`


## 2025-05-29 — Initial Production Server Setup (Hetzner VPS)

### Infrastructure Setup
- ✅ Created new SSH keypair (`hetzner_key`, `hetzner_key.pub`) and registered for secure access
- ✅ Provisioned new Hetzner VPS with IP `157.180.43.78`
- ✅ Connected to server via SSH using new key
- ✅ Upgraded system and kernel; rebooted into new kernel (6.8.0-60-generic)
- ✅ Enabled UFW firewall: allow only SSH (port 22), deny other incoming traffic

### Domain Configuration
- ✅ Pointed domain `gesturelabs.org` and `www.gesturelabs.org` to server IP
- ✅ Cleaned existing DNS records, replaced with A records
- ✅ Verified DNS propagation with `dig` and fallback nameservers (e.g. `@8.8.8.8`)

### Nginx + HTTPS Setup
- ✅ Installed and started Nginx; verified default Nginx welcome page at:
  - http://gesturelabs.org
- ✅ Installed Certbot and obtained Let’s Encrypt SSL certificates
- ✅ HTTPS successfully enabled for:
  - https://gesturelabs.org
  - https://www.gesturelabs.org
- ✅ Verified `certbot renew --dry-run` passes successfully
- ✅ Verified automatic renewal via `certbot.timer` is active

### Python Web Server (Gunicorn)
- ✅ Installed `python3-venv` and created `/opt/a3cp-env` virtual environment
- ✅ Installed Gunicorn inside venv
- ✅ Verified Gunicorn version: `23.0.0`

---

## Outstanding Tasks

- [ ] Route `/api/infer/` to FastAPI using Nginx reverse proxy
- [ ] Build and deploy initial Django + FastAPI apps

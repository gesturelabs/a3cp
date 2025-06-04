# CHANGELOG.md


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

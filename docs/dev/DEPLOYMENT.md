====================================================================
 DEPLOYMENT.md — A3CP Production Server Setup (Hetzner VPS)
====================================================================

This document describes how to set up and maintain the production server
for A3CP hosted on a Hetzner VPS. It includes system requirements,
firewall settings, Nginx config, Gunicorn setup, and HTTPS certificate
renewal.

--------------------------------------------------------------------
 1. SYSTEM REQUIREMENTS
--------------------------------------------------------------------

 - OS: Ubuntu 24.04 LTS (x86_64)
 - CPU: 2+ cores
 - RAM: 4 GB minimum
 - Disk: 40 GB SSD minimum
 - Access: SSH root login with key
 - Domain: gesturelabs.org

--------------------------------------------------------------------
 2. INITIAL SERVER PREPARATION
--------------------------------------------------------------------

 A. SSH Key Setup (on local machine):

   ssh-keygen -t ed25519 -f ~/.ssh/hetzner_key

   Upload the public key when provisioning your Hetzner VPS.

 B. Basic Updates and Firewall:

   apt update && apt upgrade -y
   apt install ufw -y
   ufw allow OpenSSH
   ufw enable
   ufw status verbose

---------------------------------------------------------------------
 3. NGINX INSTALLATION AND CONFIGURATION
--------------------------------------------------------------------

 A. Install Nginx:

   sudo apt install nginx -y
   sudo systemctl enable nginx
   sudo systemctl start nginx

 B. Nginx Reverse Proxy Configuration:

 Edit the file: /etc/nginx/sites-available/default

   server {
       listen 80;
       server_name gesturelabs.org www.gesturelabs.org;
       return 301 https://$host$request_uri;
   }

   server {
       listen 443 ssl;
       server_name gesturelabs.org www.gesturelabs.org;

       ssl_certificate /etc/letsencrypt/live/gesturelabs.org/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/gesturelabs.org/privkey.pem;

       # Proxy root path (UI) to FastAPI UI service on port 8000
       location / {
           proxy_pass http://127.0.0.1:8000;
           include proxy_params;
           proxy_redirect off;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
       }

       # Proxy API endpoints to FastAPI inference service on port 9000
       location /api/ {
           proxy_pass http://127.0.0.1:9000;
           include proxy_params;
           proxy_redirect off;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
       }
   }

 C. Restart Nginx after changes:

   sudo nginx -t
   sudo systemctl reload nginx

 Notes:
 - Port 8000: FastAPI UI (e.g., `/`, `/about`, `/docs`)
 - Port 9000: FastAPI inference API (e.g., `/api/gesture/infer/`, `/api/sound/infer/`)
 - The upgrade headers ensure compatibility with future WebSocket-based endpoints.
 - Make sure your systemd services bind to 127.0.0.1 on these ports.


--------------------------------------------------------------------
--------------------------------------------------------------------
 4. PYTHON ENVIRONMENT AND FASTAPI DEPLOYMENT
--------------------------------------------------------------------

 A. Install required tools (if not already installed):

   sudo apt update
   sudo apt install python3.11 python3.11-venv -y

 B. Create and activate virtual environment:

   python3.11 -m venv /opt/a3cp-env
   source /opt/a3cp-env/bin/activate

 C. Upgrade pip and install production dependencies:

   pip install --upgrade pip
   pip install -r /opt/a3cp-app/requirements.txt

 D. (Optional) Confirm Gunicorn version:

   /opt/a3cp-env/bin/gunicorn --version

 Notes:
 - This environment is used by systemd to run both the UI and inference FastAPI apps.
 - Ensure Python 3.11+ is available system-wide or specify absolute path to python3.11 in service files.

--------------------------------------------------------------------
 5. SYSTEMD SERVICE: FASTAPI UI APP (via Uvicorn)
--------------------------------------------------------------------

 Create file: /etc/systemd/system/a3cp-fastapi-ui.service

   [Unit]
   Description=FastAPI UI service for A3CP (served via Uvicorn)
   After=network.target

   [Service]
   User=root
   WorkingDirectory=/opt/a3cp-app
   ExecStart=/opt/a3cp-env/bin/uvicorn apps.ui.main:app --host 127.0.0.1 --port 8000
   Restart=always
   Environment="PYTHONUNBUFFERED=1"

   [Install]
   WantedBy=multi-user.target

 Activate and start the service:

   sudo systemctl daemon-reexec
   sudo systemctl enable a3cp-fastapi-ui
   sudo systemctl start a3cp-fastapi-ui

 Notes:
 - Replace `apps.ui.main:app` if your UI app is located elsewhere.
 - Make sure `/opt/a3cp-env/` is your active Python 3.11 environment.


--------------------------------------------------------------------
 6. HTTPS WITH CERTBOT (LET’S ENCRYPT)
--------------------------------------------------------------------

 A. Install Certbot:

   apt install certbot python3-certbot-nginx -y

 B. Obtain Certificates:

   certbot --nginx -d gesturelabs.org -d www.gesturelabs.org

 C. Verify HTTPS:

   curl -I https://gesturelabs.org

--------------------------------------------------------------------
 7. CERTIFICATE RENEWAL
--------------------------------------------------------------------

 A. Test Renewal:

   certbot renew --dry-run

 B. Confirm Auto-Renewal Timer:

   systemctl list-timers | grep certbot


# A3CP Deployment: Essential Service Commands

These are the core commands for managing the A3CP deployment services.

1. Restart FastAPI UI App (Uvicorn via systemd)
--------------------------------------------------
sudo systemctl restart a3cp-fastapi-ui

Use this when:
- You change Python code in the UI app (e.g., route handlers, templates)
- You install or update Python packages used by the UI
- You want to restart the FastAPI UI app without rebooting the server

2. Check UI App Status
--------------------------------------------------
systemctl status a3cp-fastapi-ui

Use this to:
- See if the FastAPI UI app is running
- Check for errors or recent logs
- Confirm that a restart was successful

3. Restart Nginx (Web server / reverse proxy)
--------------------------------------------------
sudo systemctl restart nginx

Use this when:
- You change the Nginx configuration (e.g., `/etc/nginx/sites-available/`)
- You add or remove routes (e.g., `/api/`, `/docs/`)
- You suspect issues with routing, headers, or SSL

Tip: After any command, test the deployment in the browser to confirm it's working:
http://<your-server-ip>/ and http://<your-server-ip>/docs


--------------------------------------------------------------------
 8. DEVELOPMENT NOTES
--------------------------------------------------------------------

 A. No `runserver` — All Development Uses FastAPI + Uvicorn

 The Django development server (`python manage.py runserver`) is NO LONGER
 USED in A3CP. Development has fully transitioned to FastAPI.

 Many A3CP features — including HTMX-based UI, API routing, browser media
 access, and future WebSocket support — behave inconsistently under Django's
 local development server or plain HTTP.

 For consistency, all development is done directly on the production-like
 VPS environment (Ubuntu + Uvicorn + Nginx + HTTPS).

 B. Use `scripts/dev.sh` Instead (if retained)

 If your project still includes Django components (e.g., admin utilities or
 legacy data tooling), you can use the helper script `scripts/dev.sh` to
 activate the correct environment and run safe management commands.

 Example usage:

   ./scripts/dev.sh migrate
   ./scripts/dev.sh createsuperuser
   ./scripts/dev.sh shell

 This avoids hardcoded paths and ensures you are using the correct
 Python 3.11+ environment.

 DO NOT use `python manage.py runserver` unless you are debugging a legacy
 Django component in isolation.

--------------------------------------------------------------------
 9. TO DO (POST-DEPLOYMENT)
--------------------------------------------------------------------

 - Verify all UI routes render correctly over HTTPS
 - Confirm `/docs` now correctly serves FastAPI Swagger UI
 - Finalize systemd services for:
     - `a3cp-fastapi-ui` (serving on port 8000)
     - `a3cp-fastapi-inference` (serving on port 9000)
 - Ensure `/api/` routes proxy to inference service in Nginx config
 - Replace all legacy references to Gunicorn + Django in scripts and docs
 - Add healthcheck endpoints for monitoring integration
 - Implement lightweight smoke tests for CI post-deploy validation


====================================================================
 END OF DEPLOYMENT INSTRUCTIONS
====================================================================

Let me know when you're ready to add deployment notes for the FastAPI
inference app or database configuration.

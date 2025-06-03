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

--------------------------------------------------------------------
 3. NGINX INSTALLATION AND CONFIGURATION
--------------------------------------------------------------------

 A. Install Nginx:

   apt install nginx -y
   systemctl enable nginx
   systemctl start nginx

 B. Basic Nginx Config:

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

       location / {
           proxy_pass http://127.0.0.1:8000;
           include proxy_params;
       }

       location /api/infer/ {
           proxy_pass http://127.0.0.1:9000;
           include proxy_params;
       }
   }

 Restart Nginx:

   systemctl restart nginx

--------------------------------------------------------------------
 4. PYTHON ENVIRONMENT AND GUNICORN
--------------------------------------------------------------------

 A. Install Python venv tools:

   apt install python3-venv -y

 B. Create virtual environment:

   python3 -m venv /opt/a3cp-env
   source /opt/a3cp-env/bin/activate

 C. Install Gunicorn:

   pip install gunicorn
   /opt/a3cp-env/bin/gunicorn --version

--------------------------------------------------------------------
 5. OPTIONAL: GUNICORN SYSTEMD SERVICE
--------------------------------------------------------------------

 Create file: /etc/systemd/system/a3cp-gunicorn.service

   [Unit]
   Description=Gunicorn service for A3CP Django app
   After=network.target

   [Service]
   User=root
   WorkingDirectory=/opt/a3cp-app
   ExecStart=/opt/a3cp-env/bin/gunicorn a3cp.wsgi:application --bind 127.0.0.1:8000
   Restart=always

   [Install]
   WantedBy=multi-user.target

 Activate the service:

   systemctl daemon-reexec
   systemctl enable a3cp-gunicorn
   systemctl start a3cp-gunicorn

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

These are the three main commands for managing the A3CP deployment services:

1. Restart Gunicorn (Django app server)
--------------------------------------------------
sudo systemctl restart a3cp-gunicorn

Use this when:
- You change Python code (e.g., views.py, models.py, settings.py)
- You install new Python packages
- You want to restart the Django app without rebooting the server

2. Check Gunicorn Status
--------------------------------------------------
systemctl status a3cp-gunicorn

Use this to:
- See if the Django app server is running
- Check for errors or recent logs from Gunicorn
- Verify that a restart was successful

3. Restart Nginx (Web server / reverse proxy)
--------------------------------------------------
sudo systemctl restart nginx

Use this when:
- You change the Nginx configuration (e.g., `/etc/nginx/sites-available/`)
- You want to reload static files or domains
- You suspect issues with routing or SSL

Tip: After any command, check the app in the browser to confirm it's working.

--------------------------------------------------------------------
 8. DEVELOPMENT NOTES
--------------------------------------------------------------------

 A. Avoiding `runserver` for Core Development

 The Django development server (`python manage.py runserver`) is NOT used
 in A3CP development. This is intentional.

 Many A3CP features (e.g., HTMX, HTTPS-only APIs, FastAPI endpoints,
 browser media access) behave differently or fail under local HTTP.

 For consistency, all development is done directly on the production-like
 VPS environment (Ubuntu + Gunicorn + Nginx + HTTPS).

 B. Use `scripts/dev.sh` Instead

 A helper script is provided to activate the Python virtual environment
 and safely use Django CLI tools.

 Example usage:

   ./scripts/dev.sh migrate
   ./scripts/dev.sh createsuperuser
   ./scripts/dev.sh test
   ./scripts/dev.sh shell

 This ensures a clean, repeatable setup using production paths and env.

 DO NOT use `python manage.py runserver` unless explicitly debugging.


--------------------------------------------------------------------
 8. TO DO (POST-DEPLOYMENT)
--------------------------------------------------------------------

 - Clone Django + FastAPI codebase from GitHub
 - Set up FastAPI app to run on port 9000
 - Create systemd or supervisor service for FastAPI
 - Connect PostgreSQL or other database if needed

====================================================================
 END OF DEPLOYMENT INSTRUCTIONS
====================================================================

Let me know when you're ready to add deployment notes for the FastAPI
inference app or database configuration.

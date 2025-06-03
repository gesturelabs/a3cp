#!/bin/bash
set -e

# Activate the virtual environment
source /opt/a3cp-env/bin/activate
cd /opt/a3cp-app

echo "[✓] Virtualenv activated. You can now use:"
echo "    - python manage.py shell"
echo "    - python manage.py migrate"
echo "    - python manage.py test"
echo
echo "[⚠️] Warning: Don't use runserver for production testing."
echo "    Use systemctl restart a3cp-gunicorn to restart the real server."

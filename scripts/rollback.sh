#!/bin/bash

# Usage: sudo ./rollback.sh <commit-hash-or-tag>

set -e

if [ -z "$1" ]; then
  echo "❌ Error: You must provide a commit hash or tag to roll back to."
  echo "Usage: sudo ./rollback.sh <commit-hash-or-tag>"
  exit 1
fi

REVISION=$1

echo "🔁 Rolling back to $REVISION..."

cd /opt/a3cp-app

# Stop the app
echo "⛔ Stopping Gunicorn..."
sudo systemctl stop a3cp-gunicorn

# Roll back the code
echo "🔄 Resetting repo..."
git fetch origin
git checkout "$REVISION"
git reset --hard

# Reinstall dependencies (in case they changed)
echo "📦 Installing dependencies..."
source /opt/a3cp-env/bin/activate
pip install -r requirements.txt

# Apply migrations (optional — could skip if dangerous)
echo "⚙️ Running migrations..."
python manage.py migrate --settings=config.settings.prod

# Rebuild static files
echo "🖼️ Collecting static files..."
python manage.py collectstatic --noinput --settings=config.settings.prod

# Restart the app
echo "🚀 Restarting Gunicorn..."
sudo systemctl start a3cp-gunicorn

echo "✅ Rollback to $REVISION complete."

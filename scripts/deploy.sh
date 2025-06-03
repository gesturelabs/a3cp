#!/bin/bash
set -e

echo "🔄 Pulling latest code..."
git pull origin main

echo "🐍 Activating virtualenv..."
source /opt/a3cp-env/bin/activate

echo "📦 Installing requirements..."
pip install -r requirements.txt

echo "🧱 Running migrations..."
python manage.py migrate

echo "🧹 Collecting static files..."
python manage.py collectstatic --noinput

echo "🚀 Restarting Gunicorn..."
sudo systemctl restart a3cp-gunicorn

echo "✅ Deployment complete!"

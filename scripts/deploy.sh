#scripts/deploy.sh

#!/bin/bash
set -e  # Exit immediately if any command fails

# Pull the latest code from the main branch
echo "🔄 Pulling latest code..."
git pull origin main

# Activate the system-wide virtual environment used for production
echo "🐍 Activating virtualenv..."
source /opt/a3cp-env/bin/activate

# Set the Django settings module to use the production configuration
export DJANGO_SETTINGS_MODULE=config.settings.prod
echo "🔧 DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"

# Install any new Python dependencies
echo "📦 Installing requirements..."
pip install -r requirements.txt

# Apply any pending database migrations
echo "🧱 Running migrations..."
python manage.py migrate

# Collect all static files into STATIC_ROOT for serving by the web server
echo "🧹 Collecting static files..."
python manage.py collectstatic --noinput

# Restart the Gunicorn service to apply the updated code and settings
echo "🚀 Restarting Gunicorn..."
sudo systemctl restart a3cp-gunicorn

# Confirm that the deployment script has finished successfully
echo "✅ Deployment complete!"

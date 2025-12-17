#scripts/deploy.sh

#!/bin/bash
set -e  # Exit immediately if any command fails

# Pull the latest code from the main branch
echo "🔄 Pulling latest code..."
git pull origin main

# Activate the system-wide virtual environment used for production
echo "🐍 Activating virtualenv..."
source /opt/a3cp-env/bin/activate

# Install any new Python dependencies
echo "📦 Installing requirements..."
pip install -r requirements.txt

# Restart FastAPI services
echo "🚀 Restarting services..."
sudo systemctl restart a3cp-ui
sudo systemctl restart a3cp-api

# Confirm that the deployment script has finished successfully
echo "✅ Deployment complete!"

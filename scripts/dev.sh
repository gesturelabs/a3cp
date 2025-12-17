#scripts/dev.sh

#!/bin/bash
set -e

# Activate the virtual environment
source /opt/a3cp-env/bin/activate
cd /opt/a3cp-app

echo "[✓] Virtualenv activated. You can now use:"
echo "    - uvicorn apps.ui.main:app --reload --port 8000"
echo "    - uvicorn api.main:app --reload --port 8001"
echo "    - pytest"
echo
echo "[⚠️] Warning: Don't use reload servers for production."
echo "    Use systemctl restart a3cp-ui or a3cp-api instead."

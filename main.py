# main.py
from fastapi import FastAPI

from api.main import app as api_app
from apps.ui.main import app as ui_app

app = FastAPI(
    title="GestureLabs Root",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

# JSON APIs under /api
app.mount("/api", api_app)

# Public website under /
app.mount("/", ui_app)

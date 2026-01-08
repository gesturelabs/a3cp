# tests/conftest.py
import base64
from io import BytesIO

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from PIL import Image

from api.main import app


@pytest.fixture
async def async_client():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client


@pytest.fixture(scope="session")
def tiny_jpeg_base64() -> str:
    """
    Returns a base64-encoded 1x1 black JPEG image as a data URL.
    Guaranteed to decode via Pillow.
    """
    img = Image.new("RGB", (1, 1), color="black")
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


@pytest.fixture(autouse=True)
def _force_log_root_tmp(tmp_path, monkeypatch):
    """
    Prevent tests from writing to repo-local ./logs.
    Forces all LOG_ROOT writes into a per-test temp directory.
    """
    monkeypatch.setenv("LOG_ROOT", str(tmp_path / "logs"))

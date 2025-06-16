#tests/api/test_main_smoke.py

import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from api.main import app


@pytest.mark.anyio
async def test_fastapi_app_smoke():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/openapi.json")
    assert response.status_code == 200
    assert "paths" in response.json()
    assert "/api/sound/infer/" in response.json()["paths"]

@pytest.mark.anyio
async def test_sound_infer_endpoint_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/sound/infer/", json={"user_id": "test", "session_id": "s1"})
    assert response.status_code == 200

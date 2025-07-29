# tests/api/test_session_manager_routes.py
import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from api.main import app
from tests.utils import load_example


@pytest.mark.anyio
async def test_start_session_returns_501():
    input_payload = load_example("session_manager", "input")

    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/session_manager/start", json=input_payload
            )

            assert response.status_code == 501
            assert response.json()["detail"] == "Not implemented yet"


@pytest.mark.anyio
async def test_end_session_returns_501():
    input_payload = load_example("session_manager", "input")

    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/session_manager/end", json=input_payload)

            assert response.status_code == 501
            assert response.json()["detail"] == "Not implemented yet"

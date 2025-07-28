# tests/api/test_input_broker_routes.py

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from api.main import app
from schemas.input_broker.input_broker import AlignedInputBundle


@pytest.mark.anyio
async def test_input_broker_stub_returns_501():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            payload = (
                AlignedInputBundle.example_input()
            )  # Replace with manual dict if not available
            response = await client.post("/api/input_broker/", json=payload)

            assert response.status_code == 501
            assert response.json()["detail"] == "Not implemented yet"

# tests/api/test_gesture_classifier_routes.py

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from api.main import app
from schemas.gesture_classifier.gesture_classifier import GestureClassifierInput


@pytest.mark.anyio
async def test_gesture_classifier_stub_returns_501():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            payload = (
                GestureClassifierInput.example_input()
            )  # use manual dict if not defined
            response = await client.post("/api/gesture_classifier/", json=payload)

            assert response.status_code == 501
            assert response.json()["detail"] == "Not implemented yet"

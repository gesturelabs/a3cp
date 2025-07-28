# tests/api/test_llm_clarifier_routes.py
import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from api.main import app


@pytest.mark.anyio
async def test_llm_clarifier_stub_returns_501():
    input_payload = {
        "flags": ["low_confidence", "ambiguous_gesture"],
        "intent_candidates": [
            {"confidence": 0.42, "label": "eat"},
            {"confidence": 0.40, "label": "help"},
            {"confidence": 0.18, "label": "play"},
        ],
        "session_id": "sess_20250711_e01",
        "timestamp": "2025-07-11T15:45:10.000Z",
        "topic_tag": "meal",
        "user_id": "elias01",
    }

    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/llm_clarifier/", json=input_payload)

            assert response.status_code == 501
            assert response.json()["detail"] == "Not implemented yet"

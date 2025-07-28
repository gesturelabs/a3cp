# tests/api/test_confidence_evaluator_routes.py

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from api.main import app
from schemas.confidence_evaluator.confidence_evaluator import ConfidenceEvaluatorInput


@pytest.mark.anyio
async def test_confidence_evaluator_returns_501():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            payload = (
                ConfidenceEvaluatorInput.example_input()
            )  # replace if no `.example_input()` method
            response = await client.post("/api/confidence_evaluator/", json=payload)

            assert response.status_code == 501
            assert response.json()["detail"] == "Not implemented yet"

# tests/api/test_clarification_planner_routes.py

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from api.main import app
from schemas.clarification_planner.clarification_planner import (
    ClarificationPlannerInput,
)


@pytest.mark.anyio
async def test_clarification_planner_stub_returns_501():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            payload = (
                ClarificationPlannerInput.example_input()
            )  # assumes `.example_input()` method exists
            response = await client.post("/api/clarification_planner/", json=payload)

            assert response.status_code == 501
            assert response.json()["detail"] == "Not implemented yet"

# tests/api/test_clarification_planner_routes.py

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from api.main import app
from tests.utils import load_example

pytestmark = pytest.mark.skip(
    reason="Legacy API test; awaiting rewrite for unified routes"
)


@pytest.mark.anyio
async def test_run_clarification_planner_returns_501():
    input_payload = load_example("clarification_planner", "input")
    # expected_output = load_example("clarification_planner", "output")  # Uncomment when implementing route

    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/clarification_planner/", json=input_payload
            )

            # Current expected behavior: endpoint is not implemented
            assert response.status_code == 501
            assert response.json()["detail"] == "Not implemented yet"

            # Uncomment below when implementation is added
            # assert response.status_code == 200
            # actual = response.json()
            # for key in expected_output:
            #     assert actual[key] == expected_output[key], f"{key} mismatch"

# tests/api/test_landmark_visualizer_routes.py

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from api.main import app
from tests.utils import load_example


@pytest.mark.anyio
async def test_render_landmark_visualization_returns_501():
    input_payload = load_example("landmark_visualizer", "input")
    # expected_output = load_example("landmark_visualizer", "output")  # Uncomment when 200 OK is returned

    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/landmark_visualizer/", json=input_payload
            )

            # Current expected behavior: endpoint is not implemented
            assert response.status_code == 501
            assert response.json()["detail"] == "Not implemented yet"

            # Uncomment below when implementation is added
            # assert response.status_code == 200
            # actual = response.json()
            # for key in expected_output:
            #     assert actual[key] == expected_output[key], f"{key} mismatch"

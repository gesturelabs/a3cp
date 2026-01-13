# tests/api/test_camera_feed_worker_routes.py

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from api.main import app
from tests.test_utils import load_example

pytestmark = pytest.mark.skip(
    reason="Legacy API test; awaiting rewrite for unified routes"
)


@pytest.mark.anyio
async def test_simulate_camera_frame_capture_returns_501():
    input_payload = load_example("camera_feed_worker", "input")
    # expected_output = load_example("camera_feed_worker", "output")

    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/camera_feed_worker/", json=input_payload)

            # Current expected behavior: endpoint is not implemented
            assert response.status_code == 501
            assert response.json()["detail"] == "Not implemented yet"

            # Uncomment below when implementation is added
            # assert response.status_code == 200
            # actual = response.json()
            # assert "timestamp" in actual
            # assert_valid_iso8601(actual["timestamp"])
            # for key in expected_output:
            #     if key != "timestamp":
            #         assert actual[key] == expected_output[key], f"{key} mismatch"

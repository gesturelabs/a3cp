# tests/api/test_landmark_extractor_routes.py

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from api.main import app
from schemas.landmark_extractor.landmark_extractor import LandmarkExtractorInput

pytestmark = pytest.mark.skip(
    reason="Legacy API test; awaiting rewrite for unified routes"
)


@pytest.mark.anyio
async def test_landmark_extractor_stub_returns_example_output(tiny_jpeg_base64):
    example_input = LandmarkExtractorInput.example_input()
    example_input["frame_data"] = tiny_jpeg_base64

    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/landmark_extractor/", json=example_input)

            assert response.status_code == 200
            data = response.json()

            assert data["frame_id"] == example_input["frame_id"]
            assert data["user_id"] == example_input["user_id"]
            assert "landmarks" in data
            assert "pose_landmarks" in data["landmarks"]

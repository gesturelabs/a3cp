# tests/api/test_landmark_visualizer_routes.py
import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from api.main import app
from schemas.landmark_visualizer.landmark_visualizer import LandmarkVisualizerInput


@pytest.mark.anyio
async def test_landmark_visualizer_stub_returns_501():
    example_input = LandmarkVisualizerInput.example_input()

    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/landmark_visualizer/", json=example_input
            )

            assert response.status_code == 501
            assert response.json()["detail"] == "Not implemented yet"

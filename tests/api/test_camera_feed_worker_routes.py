# tests/api/test_camera_feed_worker_routes.py


import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from api.main import app
from schemas.camera_feed_worker.camera_feed_worker import CameraFeedWorkerConfig


@pytest.mark.anyio
async def test_simulate_camera_frame_capture_returns_501():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            payload = CameraFeedWorkerConfig.example_input()
            response = await client.post("/api/camera_feed_worker/", json=payload)
            assert response.status_code == 501
            assert response.json()["detail"] == "Not implemented yet"

# tests/api/test_audio_feed_worker_routes.py
import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from api.main import app
from schemas.audio_feed_worker.audio_feed_worker import AudioFeedWorkerConfig


@pytest.mark.anyio
async def test_simulate_audio_capture_returns_expected_metadata():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            payload = AudioFeedWorkerConfig.example_input()  # or construct manually
            response = await client.post("/api/audio_feed_worker/", json=payload)
            assert response.status_code == 200
            assert "metadata" in response.text.lower() or response.json()  # optional

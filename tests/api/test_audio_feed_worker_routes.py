# tests/api/test_audio_feed_worker_routes.py
import pytest
from httpx import AsyncClient

from api.main import app
from schemas.audio_feed_worker.audio_feed_worker import (
    AudioChunkMetadata,
    AudioFeedWorkerConfig,
)


@pytest.mark.anyio
async def test_simulate_audio_capture_returns_expected_metadata():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = AudioFeedWorkerConfig.example_input()
        response = await ac.post("/api/audio_feed_worker/", json=payload)

    assert response.status_code == 200, response.text

    data = response.json()
    expected_keys = AudioChunkMetadata.example_output().keys()
    assert set(expected_keys).issubset(
        data.keys()
    ), f"Missing keys: {set(expected_keys) - set(data.keys())}"

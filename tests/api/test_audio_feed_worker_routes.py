# tests/api/test_audio_feed_worker_routes.py
import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from api.main import app
from tests.test_utils import assert_valid_iso8601, load_example

pytestmark = pytest.mark.skip(
    reason="Legacy API test; awaiting rewrite for unified routes"
)


@pytest.mark.anyio
async def test_simulate_audio_capture_stub_returns_expected_format():
    input_payload = load_example("audio_feed_worker", "input")
    expected_output = load_example("audio_feed_worker", "output")

    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/audio_feed_worker/", json=input_payload)

            assert response.status_code == 200
            actual = response.json()

            # Validate timestamp format
            assert "timestamp" in actual
            assert_valid_iso8601(actual["timestamp"])

            # Compare remaining fields
            for key in expected_output:
                if key == "timestamp":
                    continue
                assert actual[key] == expected_output[key], f"{key} mismatch"

import pytest
from httpx import ASGITransport, AsyncClient

from api.main import app


@pytest.mark.anyio
async def test_sound_infer_stub():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/sound/infer/")

    assert response.status_code == 200
    data = response.json()
    assert "classifier_output" in data
    assert data["modality"] == "sound"
    assert isinstance(data["classifier_output"], list)
    assert len(data["classifier_output"]) >= 1

    for candidate in data["classifier_output"]:
        assert "label" in candidate
        assert "confidence" in candidate
        assert isinstance(candidate["confidence"], float)

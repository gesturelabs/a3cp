# tests/api/test_gesture_infer.py

import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app


@pytest.mark.anyio
async def test_infer_returns_200():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/gesture/infer/")
    assert response.status_code == 200

@pytest.mark.anyio
async def test_infer_returns_expected_fields():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/gesture/infer/")
    data = response.json()

    expected_keys = {
        "classifier_output",
        "record_id",
        "user_id",
        "session_id",
        "timestamp",
        "modality",
        "source",
        "vector"
    }

    assert expected_keys.issubset(data.keys())


@pytest.mark.anyio
async def test_classifier_output_format():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/gesture/infer/")
    data = response.json()

    assert isinstance(data["classifier_output"], list)
    for candidate in data["classifier_output"]:
        assert "label" in candidate
        assert "confidence" in candidate
        assert isinstance(candidate["label"], str)
        assert isinstance(candidate["confidence"], float)


@pytest.mark.anyio
async def test_confidence_values_in_range():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/gesture/infer/")
    candidates = response.json()["classifier_output"]

    for c in candidates:
        assert 0.0 <= c["confidence"] <= 1.0

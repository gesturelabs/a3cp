# tests/api/test_streamer.py

from fastapi.testclient import TestClient
from api.main import app
import datetime

client = TestClient(app)

def test_streamer_valid_input():
    payload = {
        "user_id": "test_user",
        "session_id": "sess_001",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "modality": "gesture",
        "source": "webcam",
        "intent_label": "hello",
        "consent_given": True,
        "raw_input_video": [0.1, 0.2, 0.3, 0.4]
    }
    response = client.post("/api/streamer/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert data["record_id"].startswith("rec-")
    assert data["modality"] == "gesture"
    assert data["input_size"] == 4

def test_streamer_rejects_without_consent():
    payload = {
        "user_id": "test_user",
        "session_id": "sess_001",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "modality": "sound",
        "source": "mic",
        "intent_label": "help",
        "consent_given": False,
        "raw_input_audio": [0.1, 0.2]
    }
    response = client.post("/api/streamer/", json=payload)
    assert response.status_code == 403
    assert response.json()["detail"] == "Consent is required for input capture."

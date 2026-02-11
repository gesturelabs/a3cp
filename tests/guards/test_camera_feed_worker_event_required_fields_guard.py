import json

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from api.main import app


def _iso_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def test_ws_rejects_capture_open_missing_capture_id() -> None:
    client = TestClient(app)
    with client.websocket_connect("/camera_feed_worker/ws") as ws:
        msg = {
            "schema_version": "1.0.1",
            "record_id": "00000000-0000-0000-0000-000000000001",
            "user_id": "user_1",
            "session_id": "sess_1",
            "timestamp": _iso_now(),
            "modality": "image",
            "source": "browser",
            "event": "capture.open",
            # "capture_id": "cap1",  # missing
            "timestamp_start": _iso_now(),
            "fps_target": 15,
            "width": 640,
            "height": 480,
            "encoding": "jpeg",
        }
        ws.send_text(json.dumps(msg))
        with pytest.raises(WebSocketDisconnect) as e:
            ws.receive_text()
        assert e.value.code == 1008


def test_ws_rejects_capture_open_missing_fps_target() -> None:
    client = TestClient(app)
    with client.websocket_connect("/camera_feed_worker/ws") as ws:
        msg = {
            "schema_version": "1.0.1",
            "record_id": "00000000-0000-0000-0000-000000000002",
            "user_id": "user_1",
            "session_id": "sess_1",
            "timestamp": _iso_now(),
            "modality": "image",
            "source": "browser",
            "event": "capture.open",
            "capture_id": "cap1",
            "timestamp_start": _iso_now(),
            # "fps_target": 15,  # missing
            "width": 640,
            "height": 480,
            "encoding": "jpeg",
        }
        ws.send_text(json.dumps(msg))
        with pytest.raises(WebSocketDisconnect) as e:
            ws.receive_text()
        assert e.value.code == 1008

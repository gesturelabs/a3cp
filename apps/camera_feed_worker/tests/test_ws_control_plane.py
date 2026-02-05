# path: apps/camera_feed_worker/tests/test_ws_control_plane_abort.py

import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from main import app  # adjust if your app import differs


def _isoz(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def test_ws_emits_abort_on_second_open_while_active() -> None:
    client = TestClient(app)

    now = datetime.now(timezone.utc)

    def open_msg(record_id: str) -> dict:
        return {
            "schema_version": "1.0.1",
            "record_id": record_id,
            "user_id": "test_user",
            "session_id": "sess_test",
            "timestamp": _isoz(now),
            "modality": "image",
            "source": "ui",
            "event": "capture.open",
            "capture_id": "cap_test_1",
            "timestamp_start": _isoz(now),
            "fps_target": 15,
            "width": 640,
            "height": 480,
            "encoding": "jpeg",
        }

    with client.websocket_connect("/api/camera_feed_worker/ws") as ws:
        ws.send_json(open_msg(str(uuid.uuid4())))
        ws.send_json(
            open_msg(str(uuid.uuid4()))
        )  # second open while active -> should abort

        out = ws.receive_json()
        assert out["event"] == "capture.abort"
        assert out["capture_id"] == "cap_test_1"
        assert isinstance(out.get("error_code"), str) and out["error_code"].strip()

        with pytest.raises(WebSocketDisconnect):
            ws.receive_text()

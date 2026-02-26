# apps/camera_feed_worker/tests/test_ws_stop_preview_teardown.py

import json
import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from api.main import app
from apps.camera_feed_worker.routes import router as cfw_router_mod


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@pytest.mark.integration
def test_stop_preview_disconnect_tears_down_capture(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Deterministic test for: capturing -> Stop Preview triggers capture teardown.

    We model "Stop Preview" as the client disconnecting the websocket without sending
    capture.close. The server must still stop forwarding and clear repo state.
    """
    # Make session validation succeed
    monkeypatch.setattr(
        cfw_router_mod, "validate_session", lambda user_id, session_id: "active"
    )

    # Fix connection_key by monkeypatching uuid.uuid4 used in _ws_control_plane_loop
    fixed_key = uuid.UUID("00000000-0000-0000-0000-000000000123")
    monkeypatch.setattr(cfw_router_mod.uuid, "uuid4", lambda: fixed_key)

    calls: dict[str, list[str]] = {"stop": [], "clear": []}

    # Spy on teardown calls (preserve real behavior)
    real_stop = cfw_router_mod.repo.stop_forwarding
    real_clear = cfw_router_mod.repo.clear

    def _stop_forwarding_spy(connection_key: str) -> None:
        calls["stop"].append(connection_key)
        return real_stop(connection_key)

    def _clear_spy(connection_key: str) -> None:
        calls["clear"].append(connection_key)
        return real_clear(connection_key)

    monkeypatch.setattr(cfw_router_mod.repo, "stop_forwarding", _stop_forwarding_spy)
    monkeypatch.setattr(cfw_router_mod.repo, "clear", _clear_spy)

    client = TestClient(app)

    with client.websocket_connect("/camera_feed_worker/capture") as ws:
        now = _iso_now()
        capture_id = f"cap-{uuid.uuid4()}"

        open_msg = {
            "schema_version": "1.0.1",
            "record_id": str(uuid.uuid4()),
            "user_id": "u_test",
            "session_id": "sess_test",
            "timestamp": now,
            "modality": "image",
            "source": "ui",
            "event": "capture.open",
            "capture_id": capture_id,
            "timestamp_start": now,
            "fps_target": 15,
            "width": 640,
            "height": 480,
            "encoding": "jpeg",
        }
        ws.send_text(json.dumps(open_msg))

        # Simulate "Stop Preview": client closes the websocket without capture.close.
        ws.close()

    # Server should have executed teardown in finally: stop_forwarding + clear.
    expected_key = str(fixed_key)
    assert expected_key in calls["stop"]
    assert expected_key in calls["clear"]

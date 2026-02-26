# apps/camera_feed_worker/tests/test_ws_capture_close_teardown.py

import json
import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from api.main import app
from apps.camera_feed_worker.routes import router as cfw_router_mod


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@pytest.mark.integration
def test_capture_close_tears_down_forwarding_and_clears_repo(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Explicit stop path: capture.close must:
    - stop forwarding (repo.stop_forwarding)
    - close the websocket cleanly (1000)
    - clear repo state in finally (repo.clear)
    """
    monkeypatch.setattr(
        cfw_router_mod, "validate_session", lambda user_id, session_id: "active"
    )

    # Fix connection_key used by _ws_control_plane_loop so we can assert calls.
    fixed_key = uuid.UUID("00000000-0000-0000-0000-000000000456")
    monkeypatch.setattr(cfw_router_mod.uuid, "uuid4", lambda: fixed_key)
    expected_key = str(fixed_key)

    calls: dict[str, list[str]] = {"stop": [], "clear": []}
    real_stop = cfw_router_mod.repo.stop_forwarding
    real_clear = cfw_router_mod.repo.clear

    def _stop_spy(connection_key: str) -> None:
        calls["stop"].append(connection_key)
        return real_stop(connection_key)

    def _clear_spy(connection_key: str) -> None:
        calls["clear"].append(connection_key)
        return real_clear(connection_key)

    monkeypatch.setattr(cfw_router_mod.repo, "stop_forwarding", _stop_spy)
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

        close_msg = {
            "schema_version": "1.0.1",
            "record_id": str(uuid.uuid4()),
            "user_id": "u_test",
            "session_id": "sess_test",
            "timestamp": _iso_now(),
            "modality": "image",
            "source": "ui",
            "event": "capture.close",
            "capture_id": capture_id,
        }
        ws.send_text(json.dumps(close_msg))

        # Server should close cleanly; next receive should disconnect.
        with pytest.raises(WebSocketDisconnect) as exc:
            ws.receive_text()

        code = getattr(exc.value, "code", None)
        if code is not None:
            assert code == 1000

    assert expected_key in calls["stop"]
    assert expected_key in calls["clear"]

# apps/camera_feed_worker/tests/test_ws_meta_binary_ordering.py

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
def test_ws_rejects_binary_before_first_frame_meta(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Protocol invariant: meta -> binary ordering.
    If the client sends bytes while not expecting binary (no prior capture.frame_meta),
    server must close with 1008 (policy violation).
    """
    monkeypatch.setattr(
        cfw_router_mod, "validate_session", lambda user_id, session_id: "active"
    )

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

        # Send bytes without having armed the binary gate via capture.frame_meta
        ws.send_bytes(b"\x00\x01")

        with pytest.raises(WebSocketDisconnect) as exc:
            ws.receive_text()

        code = getattr(exc.value, "code", None)
        if code is not None:
            assert code == 1008


@pytest.mark.integration
def test_ws_accepts_meta_then_binary_and_enqueues_first_frame(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Protocol invariant: first frame must be meta then bytes of declared length.
    Verify that a correctly ordered first frame results in enqueue_frame() call.
    """
    monkeypatch.setattr(
        cfw_router_mod, "validate_session", lambda user_id, session_id: "active"
    )

    # Spy on enqueue_frame (preserve real behavior)
    calls: dict[str, int] = {"n": 0}
    real_enqueue = cfw_router_mod.repo.enqueue_frame

    def _enqueue_spy(connection_key: str, item) -> None:
        calls["n"] += 1
        return real_enqueue(connection_key, item)

    monkeypatch.setattr(cfw_router_mod.repo, "enqueue_frame", _enqueue_spy)

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

        # Correct ordering: meta then bytes matching byte_length
        payload = b"\x00\x01\x02"
        now2 = _iso_now()
        meta = {
            "schema_version": "1.0.1",
            "record_id": str(uuid.uuid4()),
            "user_id": "u_test",
            "session_id": "sess_test",
            "timestamp": now2,
            "modality": "image",
            "source": "ui",
            "event": "capture.frame_meta",
            "capture_id": capture_id,
            "seq": 1,
            "timestamp_frame": now2,
            "byte_length": len(payload),
        }
        ws.send_text(json.dumps(meta))
        ws.send_bytes(payload)

        # We don't require a server message on success; we only require the frame is enqueued.
        # Close cleanly from client side to end the session.
        ws.close()

    assert calls["n"] >= 1

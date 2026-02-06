# path: apps/camera_feed_worker/tests/test_ws_control_plane_abort.py

import json
import signal
import time
import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from apps.session_manager import service as sm_service
from main import app


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _isoz(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class _Timeout(Exception):
    pass


def _alarm_handler(signum, frame):
    raise _Timeout()


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


def test_ws_rejects_text_when_expecting_binary() -> None:
    """
    Given: capture.frame_meta accepted (binary gate armed)
    When: client sends a TEXT frame instead of BYTES
    Then: server closes with protocol violation (1008)
    """
    client = TestClient(app)

    capture_id = str(uuid.uuid4())
    user_id = "user_1"
    session_id = str(uuid.uuid4())
    sm_service._sessions[str(session_id)] = {
        "user_id": str(user_id),
        "status": "active",
    }

    with client.websocket_connect("/api/camera_feed_worker/ws") as ws:
        # capture.open
        ws.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.open",
                    "capture_id": capture_id,
                    "timestamp_start": _iso_now(),
                    "fps_target": 15,
                    "width": 640,
                    "height": 480,
                    "encoding": "jpeg",
                }
            )
        )

        # capture.frame_meta (arms binary gate)
        ws.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.frame_meta",
                    "capture_id": capture_id,
                    "seq": 1,
                    "timestamp_frame": _iso_now(),
                    "byte_length": 10,
                }
            )
        )

        # WRONG: send text when expecting bytes (server should close)
        ws.send_text(json.dumps({"oops": "text instead of bytes"}))

        # Starlette typically surfaces the close on receive
        with pytest.raises(WebSocketDisconnect) as e:
            ws.receive_text()

        assert e.value.code == 1008


def test_ws_rejects_byte_length_mismatch() -> None:
    """
    Given: capture.frame_meta accepted with byte_length=10
    When: client sends BYTES of different length
    Then: server closes with protocol violation (1008)
    """
    client = TestClient(app)

    capture_id = str(uuid.uuid4())
    user_id = "user_1"
    session_id = str(uuid.uuid4())

    sm_service._sessions[str(session_id)] = {
        "user_id": str(user_id),
        "status": "active",
    }

    with client.websocket_connect("/api/camera_feed_worker/ws") as ws:
        ws.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.open",
                    "capture_id": capture_id,
                    "timestamp_start": _iso_now(),
                    "fps_target": 15,
                    "width": 640,
                    "height": 480,
                    "encoding": "jpeg",
                }
            )
        )

        ws.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.frame_meta",
                    "capture_id": capture_id,
                    "seq": 1,
                    "timestamp_frame": _iso_now(),
                    "byte_length": 10,
                }
            )
        )

        ws.send_bytes(b"12345")

        old = signal.signal(signal.SIGALRM, _alarm_handler)
        signal.alarm(1)
        try:
            msg = ws.receive()
        except WebSocketDisconnect as e:
            assert e.code == 1008
        else:
            assert msg.get("type") == "websocket.close"
            assert msg.get("code") == 1008
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old)


def test_ws_clears_binary_gate_after_successful_bytes() -> None:
    """
    Given: binary gate armed by capture.frame_meta
    When: client sends matching bytes (success)
    Then: gate clears and next TEXT control message is accepted
          (socket remains open; no protocol close 1008).
    """
    client = TestClient(app)

    capture_id = str(uuid.uuid4())
    user_id = "user_1"
    session_id = str(uuid.uuid4())

    sm_service._sessions[str(session_id)] = {
        "user_id": str(user_id),
        "status": "active",
    }

    with client.websocket_connect("/api/camera_feed_worker/ws") as ws:
        ws.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.open",
                    "capture_id": capture_id,
                    "timestamp_start": _iso_now(),
                    "fps_target": 15,
                    "width": 640,
                    "height": 480,
                    "encoding": "jpeg",
                }
            )
        )

        ws.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.frame_meta",
                    "capture_id": capture_id,
                    "seq": 1,
                    "timestamp_frame": _iso_now(),
                    "byte_length": 5,
                }
            )
        )

        ws.send_bytes(b"12345")

        # If gate was NOT cleared, this text would be treated as invalid and close the socket.
        ws.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.close",
                    "capture_id": capture_id,
                    "timestamp_end": _iso_now(),
                }
            )
        )

        # Prove socket is still open by sending another text frame.
        # If the previous text triggered protocol close, this will raise WebSocketDisconnect.
        ws.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.open",
                    "capture_id": str(uuid.uuid4()),
                    "timestamp_start": _iso_now(),
                    "fps_target": 15,
                    "width": 640,
                    "height": 480,
                    "encoding": "jpeg",
                }
            )
        )


def test_ws_protocol_violation_does_not_leak_gate_or_state_to_next_connection() -> None:
    """
    Given: a connection hits protocol violation (text while expecting bytes) and is closed
    Then: a new connection can immediately open + send capture.open without being affected
          by prior connection-local binary gate/state.
    """
    client = TestClient(app)

    user_id = "user_1"
    session_id = str(uuid.uuid4())
    sm_service._sessions[str(session_id)] = {
        "user_id": str(user_id),
        "status": "active",
    }

    # First connection: trigger protocol close (expecting bytes, but send text)
    capture_id1 = str(uuid.uuid4())
    with client.websocket_connect("/api/camera_feed_worker/ws") as ws1:
        ws1.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.open",
                    "capture_id": capture_id1,
                    "timestamp_start": _iso_now(),
                    "fps_target": 15,
                    "width": 640,
                    "height": 480,
                    "encoding": "jpeg",
                }
            )
        )

        ws1.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.frame_meta",
                    "capture_id": capture_id1,
                    "seq": 1,
                    "timestamp_frame": _iso_now(),
                    "byte_length": 10,
                }
            )
        )

        ws1.send_text(json.dumps({"oops": "text instead of bytes"}))
        msg = ws1.receive()
        assert msg.get("type") == "websocket.close"
        assert msg.get("code") == 1008

    # Second connection: should work normally (no leaked gate/state)
    capture_id2 = str(uuid.uuid4())
    with client.websocket_connect("/api/camera_feed_worker/ws") as ws2:
        ws2.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.open",
                    "capture_id": capture_id2,
                    "timestamp_start": _iso_now(),
                    "fps_target": 15,
                    "width": 640,
                    "height": 480,
                    "encoding": "jpeg",
                }
            )
        )

        # If leaked state existed, the server might immediately close; prove it's open by sending a second message.
        ws2.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.close",
                    "capture_id": capture_id2,
                    "timestamp_end": _iso_now(),
                }
            )
        )


def test_ws_does_not_arm_binary_gate_if_frame_meta_rejected_by_domain() -> None:
    """
    Given: active capture
    When: capture.frame_meta is invalid (domain rejects it)
    Then: server emits capture.abort + closes (1000),
          and does NOT behave like it's expecting bytes (no 1008 gate behavior).
    """
    client = TestClient(app)

    capture_id = str(uuid.uuid4())
    user_id = "user_1"
    session_id = str(uuid.uuid4())

    sm_service._sessions[str(session_id)] = {
        "user_id": str(user_id),
        "status": "active",
    }

    with client.websocket_connect("/api/camera_feed_worker/ws") as ws:
        # capture.open
        ws.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.open",
                    "capture_id": capture_id,
                    "timestamp_start": _iso_now(),
                    "fps_target": 15,
                    "width": 640,
                    "height": 480,
                    "encoding": "jpeg",
                }
            )
        )

        # INVALID frame_meta: seq should be 1, send 2 to force domain rejection
        ws.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.frame_meta",
                    "capture_id": capture_id,
                    "seq": 2,  # invalid
                    "timestamp_frame": _iso_now(),
                    "byte_length": 10,
                }
            )
        )

        # Expect domain abort message (text)
        abort_text = ws.receive_text()
        abort_msg = json.loads(abort_text)
        assert abort_msg.get("event") == "capture.abort"
        assert abort_msg.get("capture_id") == capture_id

        # Then close should be normal (1000), not a protocol gate close (1008)
        close_evt = ws.receive()
        assert close_evt.get("type") == "websocket.close"
        assert close_evt.get("code") == 1000


def test_ws_tick_abort_on_meta_to_bytes_timeout() -> None:
    """
    Given: capture.frame_meta accepted (binary gate armed) but bytes never arrive
    When: META_TO_BYTES_TIMEOUT elapses (tick-driven)
    Then: server emits capture.abort and closes (1000).
    """
    client = TestClient(app)

    capture_id = str(uuid.uuid4())
    user_id = "user_1"
    session_id = str(uuid.uuid4())

    sm_service._sessions[str(session_id)] = {
        "user_id": str(user_id),
        "status": "active",
    }

    with client.websocket_connect("/api/camera_feed_worker/ws") as ws:
        # capture.open
        ws.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.open",
                    "capture_id": capture_id,
                    "timestamp_start": _iso_now(),
                    "fps_target": 15,
                    "width": 640,
                    "height": 480,
                    "encoding": "jpeg",
                }
            )
        )

        # capture.frame_meta arms gate, but we will NOT send bytes
        ws.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.frame_meta",
                    "capture_id": capture_id,
                    "seq": 1,
                    "timestamp_frame": _iso_now(),
                    "byte_length": 5,
                }
            )
        )

        # Let real time pass so the domain meta→bytes timeout becomes true.
        # (Domain uses now_ingest=datetime.now(...), so tick requires wall-clock advancement.)
        time.sleep(3.0)

        # Next interaction will advance the server loop and run tick before processing receive.
        abort_evt = ws.receive()
        assert (
            abort_evt.get("type") == "websocket.send"
        ), f"Expected websocket.send, got: {abort_evt}"
        assert abort_evt.get("text"), f"Expected abort text, got: {abort_evt}"

        abort_msg = json.loads(abort_evt["text"])

        abort_msg = json.loads(abort_evt["text"])
        assert abort_msg.get("event") == "capture.abort"
        assert abort_msg.get("capture_id") == capture_id
        assert (
            isinstance(abort_msg.get("error_code"), str)
            and abort_msg["error_code"].strip()
        )

        close_evt = ws.receive()
        assert close_evt.get("type") == "websocket.close"
        assert close_evt.get("code") == 1000


def test_ws_disconnect_does_not_leak_gate_or_state_to_next_connection() -> None:
    """
    Given: binary gate is armed (capture.frame_meta accepted)
    When: client disconnects abruptly (context exit) before sending bytes
    Then: a new connection can open + send capture.open without being affected
          by prior connection-local binary gate/state.
    """
    client = TestClient(app)

    user_id = "user_1"
    session_id = str(uuid.uuid4())
    sm_service._sessions[str(session_id)] = {
        "user_id": str(user_id),
        "status": "active",
    }

    # First connection: arm gate, then disconnect without sending bytes
    capture_id1 = str(uuid.uuid4())
    with client.websocket_connect("/api/camera_feed_worker/ws") as ws1:
        ws1.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.open",
                    "capture_id": capture_id1,
                    "timestamp_start": _iso_now(),
                    "fps_target": 15,
                    "width": 640,
                    "height": 480,
                    "encoding": "jpeg",
                }
            )
        )

        ws1.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.frame_meta",
                    "capture_id": capture_id1,
                    "seq": 1,
                    "timestamp_frame": _iso_now(),
                    "byte_length": 10,
                }
            )
        )
        # Context exit => disconnect without bytes

    # Second connection: should behave normally (no leaked expecting_binary state)
    capture_id2 = str(uuid.uuid4())
    with client.websocket_connect("/api/camera_feed_worker/ws") as ws2:
        ws2.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.open",
                    "capture_id": capture_id2,
                    "timestamp_start": _iso_now(),
                    "fps_target": 15,
                    "width": 640,
                    "height": 480,
                    "encoding": "jpeg",
                }
            )
        )

        # Prove still open by sending a second control message
        ws2.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.close",
                    "capture_id": capture_id2,
                    "timestamp_end": _iso_now(),
                }
            )
        )


def test_ws_unexpected_exception_does_not_leak_gate_or_state_to_next_connection(
    monkeypatch,
) -> None:
    client = TestClient(app)

    user_id = "user_1"
    session_id = str(uuid.uuid4())
    sm_service._sessions[str(session_id)] = {
        "user_id": str(user_id),
        "status": "active",
    }

    from apps.camera_feed_worker.routes import router as cf_router

    original_parse = cf_router._parse_control_message

    def boom(_raw_text: str):
        raise RuntimeError("boom")

    monkeypatch.setattr(cf_router, "_parse_control_message", boom)

    capture_id1 = str(uuid.uuid4())
    with client.websocket_connect("/api/camera_feed_worker/ws") as ws1:
        ws1.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.open",
                    "capture_id": capture_id1,
                    "timestamp_start": _iso_now(),
                    "fps_target": 15,
                    "width": 640,
                    "height": 480,
                    "encoding": "jpeg",
                }
            )
        )

        close_evt = ws1.receive()
        assert close_evt.get("type") == "websocket.close"
        assert close_evt.get("code") == 1011

    # Restore and verify next connection is clean
    monkeypatch.setattr(cf_router, "_parse_control_message", original_parse)

    capture_id2 = str(uuid.uuid4())
    with client.websocket_connect("/api/camera_feed_worker/ws") as ws2:
        ws2.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.open",
                    "capture_id": capture_id2,
                    "timestamp_start": _iso_now(),
                    "fps_target": 15,
                    "width": 640,
                    "height": 480,
                    "encoding": "jpeg",
                }
            )
        )

        # Prove still open by sending close
        ws2.send_text(
            json.dumps(
                {
                    "schema_version": "1.0.1",
                    "record_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": _iso_now(),
                    "modality": "image",
                    "source": "browser",
                    "event": "capture.close",
                    "capture_id": capture_id2,
                    "timestamp_end": _iso_now(),
                }
            )
        )

# apps/camera_feed_worker/tests/test_terminal_delivery.py

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import cast

import pytest
from fastapi import WebSocket
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketState

import apps.camera_feed_worker.routes.router as cfw_router_mod
from apps.camera_feed_worker.state import ActiveState, IdleState
from apps.landmark_extractor import service as le_service
from apps.session_manager import service as sm_service
from main import app
from schemas import CameraFeedWorkerInput, LandmarkExtractorTerminalInput


class _DummyWebSocket:
    def __init__(self) -> None:
        self.sent_texts: list[str] = []
        self.close_codes: list[int] = []
        self.application_state = WebSocketState.CONNECTED

    async def send_text(self, text: str) -> None:
        self.sent_texts.append(text)

    async def close(self, code: int = 1000) -> None:
        self.close_codes.append(code)
        self.application_state = WebSocketState.DISCONNECTED


def _iso_now() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def test_capture_close_delivers_exactly_one_terminal_ingest_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[LandmarkExtractorTerminalInput] = []
    client = TestClient(app)

    capture_id = str(uuid.uuid4())
    user_id = "user_1"
    session_id = str(uuid.uuid4())

    sm_service._sessions[session_id] = {
        "user_id": user_id,
        "status": "active",
    }

    async def _record_handle_message(message: object) -> None:
        assert isinstance(message, LandmarkExtractorTerminalInput)
        captured.append(message)

    monkeypatch.setattr(le_service, "handle_message", _record_handle_message)

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

        msg = ws.receive()
        assert msg.get("type") == "websocket.close"
        assert msg.get("code") == 1000

    terminal_msgs = [
        m
        for m in captured
        if m.event == "capture.close" and str(m.capture_id) == capture_id
    ]

    assert len(terminal_msgs) == 1

    terminal = terminal_msgs[0]
    assert terminal.session_id == session_id
    assert terminal.user_id == user_id


def test_capture_abort_delivers_exactly_one_terminal_ingest_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[LandmarkExtractorTerminalInput] = []
    client = TestClient(app)

    capture_id = str(uuid.uuid4())
    user_id = "user_1"
    session_id = str(uuid.uuid4())

    sm_service._sessions[session_id] = {
        "user_id": user_id,
        "status": "active",
    }

    async def _record_handle_message(message: object) -> None:
        assert isinstance(message, LandmarkExtractorTerminalInput)
        captured.append(message)

    monkeypatch.setattr(le_service, "handle_message", _record_handle_message)

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

        msg = ws.receive()
        assert msg.get("type") == "websocket.send"
        payload = json.loads(msg["text"])
        assert payload["event"] == "capture.abort"
        assert payload["error_code"] == "protocol_violation"

        msg = ws.receive()
        assert msg.get("type") == "websocket.close"
        assert msg.get("code") == 1000

    terminal_msgs = [
        m
        for m in captured
        if m.event == "capture.abort" and str(m.capture_id) == capture_id
    ]

    assert len(terminal_msgs) == 1

    terminal = terminal_msgs[0]
    assert terminal.session_id == session_id
    assert terminal.user_id == user_id
    assert terminal.error_code == "protocol_violation"


def test_duplicate_terminal_attempts_do_not_produce_second_terminal_ingest_message() -> (
    None
):
    captured: list[LandmarkExtractorTerminalInput] = []

    async def _record_ingest(payload: object) -> None:
        assert isinstance(payload, LandmarkExtractorTerminalInput)
        captured.append(payload)

    connection_key = "dup-terminal-test"
    cfw_router_mod.repo.clear(connection_key)

    capture_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    record_id = uuid.uuid4()
    now_ingest = datetime.now(timezone.utc)

    current_state = ActiveState(
        record_id=record_id,
        capture_id=capture_id,
        user_id="user_1",
        session_id=session_id,
        annotation_intent=None,
        timestamp_start=now_ingest,
        last_frame_timestamp=None,
        ingest_timestamp_open=now_ingest,
        fps_target=15,
        width=640,
        height=480,
        encoding="jpeg",
        frame_count=0,
        total_bytes=0,
        expected_next_seq=1,
        pending_meta=None,
        last_meta_ingest_timestamp=now_ingest,
        last_session_check_ingest_timestamp=now_ingest,
    )
    cfw_router_mod.repo.set_state(connection_key, current_state)

    last_msg = CameraFeedWorkerInput(
        schema_version="1.0.1",
        record_id=uuid.uuid4(),
        user_id="user_1",
        session_id=session_id,
        timestamp=now_ingest,
        modality="image",
        source="browser",
        event="capture.open",
        capture_id=capture_id,
        timestamp_start=now_ingest,
        fps_target=15,
        width=640,
        height=480,
        encoding="jpeg",
    )

    ws1 = _DummyWebSocket()
    result1 = asyncio.run(
        cfw_router_mod._emit_abort_and_close(
            cast(WebSocket, ws1),
            connection_key=connection_key,
            now_ingest=now_ingest,
            current_state=current_state,
            capture_id=capture_id,
            error_code="protocol_violation",
            last_msg_for_emit=last_msg,
            ingest_fn=_record_ingest,
        )
    )
    assert result1 is False

    ws2 = _DummyWebSocket()
    result2 = asyncio.run(
        cfw_router_mod._emit_abort_and_close(
            cast(WebSocket, ws2),
            connection_key=connection_key,
            now_ingest=now_ingest,
            current_state=current_state,
            capture_id=capture_id,
            error_code="forward_failed",
            last_msg_for_emit=last_msg,
            ingest_fn=_record_ingest,
        )
    )
    assert result2 is False

    terminal_msgs = [
        m
        for m in captured
        if m.event == "capture.abort" and str(m.capture_id) == capture_id
    ]
    assert len(terminal_msgs) == 1

    terminal = terminal_msgs[0]
    assert terminal.error_code == "protocol_violation"


def test_terminal_emission_is_guarded_by_repo_has_emitted_terminal() -> None:
    captured: list[LandmarkExtractorTerminalInput] = []

    async def _record_ingest(payload: object) -> None:
        assert isinstance(payload, LandmarkExtractorTerminalInput)
        captured.append(payload)

    connection_key = "terminal-guard-test"
    cfw_router_mod.repo.clear(connection_key)

    capture_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    record_id = uuid.uuid4()
    now_ingest = datetime.now(timezone.utc)

    current_state = ActiveState(
        record_id=record_id,
        capture_id=capture_id,
        user_id="user_1",
        session_id=session_id,
        annotation_intent=None,
        timestamp_start=now_ingest,
        last_frame_timestamp=None,
        ingest_timestamp_open=now_ingest,
        fps_target=15,
        width=640,
        height=480,
        encoding="jpeg",
        frame_count=0,
        total_bytes=0,
        expected_next_seq=1,
        pending_meta=None,
        last_meta_ingest_timestamp=now_ingest,
        last_session_check_ingest_timestamp=now_ingest,
    )
    cfw_router_mod.repo.set_state(connection_key, current_state)
    cfw_router_mod.repo.mark_terminal_emitted(connection_key)

    last_msg = CameraFeedWorkerInput(
        schema_version="1.0.1",
        record_id=uuid.uuid4(),
        user_id="user_1",
        session_id=session_id,
        timestamp=now_ingest,
        modality="image",
        source="browser",
        event="capture.open",
        capture_id=capture_id,
        timestamp_start=now_ingest,
        fps_target=15,
        width=640,
        height=480,
        encoding="jpeg",
    )

    ws = _DummyWebSocket()
    result = asyncio.run(
        cfw_router_mod._emit_abort_and_close(
            cast(WebSocket, ws),
            connection_key=connection_key,
            now_ingest=now_ingest,
            current_state=current_state,
            capture_id=capture_id,
            error_code="protocol_violation",
            last_msg_for_emit=last_msg,
            ingest_fn=_record_ingest,
        )
    )

    assert result is False
    assert len(captured) == 0

    abort_payloads = [json.loads(text) for text in ws.sent_texts]
    assert len(abort_payloads) == 1
    assert abort_payloads[0]["event"] == "capture.abort"
    assert abort_payloads[0]["capture_id"] == capture_id

    assert ws.close_codes == [1000]


def test_terminal_ingest_occurs_before_forwarder_shutdown_on_capture_close(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[str] = []

    connection_key = "close-order-test"
    cfw_router_mod.repo.clear(connection_key)

    capture_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    now_ingest = datetime.now(timezone.utc)

    current_state = ActiveState(
        record_id=uuid.uuid4(),
        capture_id=capture_id,
        user_id="user_1",
        session_id=session_id,
        annotation_intent=None,
        timestamp_start=now_ingest,
        last_frame_timestamp=None,
        ingest_timestamp_open=now_ingest,
        fps_target=15,
        width=640,
        height=480,
        encoding="jpeg",
        frame_count=1,
        total_bytes=5,
        expected_next_seq=2,
        pending_meta=None,
        last_meta_ingest_timestamp=now_ingest,
        last_session_check_ingest_timestamp=now_ingest,
    )
    cfw_router_mod.repo.set_state(connection_key, current_state)

    monkeypatch.setattr(
        cfw_router_mod,
        "dispatch",
        lambda **kwargs: (IdleState(), []),
    )

    original_mark_terminal_emitted = cfw_router_mod.repo.mark_terminal_emitted
    original_stop_forwarding = cfw_router_mod.repo.stop_forwarding

    def _mark_terminal_emitted(key: str) -> None:
        events.append("mark_terminal_emitted")
        original_mark_terminal_emitted(key)

    def _stop_forwarding(key: str) -> None:
        events.append("stop_forwarding")
        original_stop_forwarding(key)

    monkeypatch.setattr(
        cfw_router_mod.repo,
        "mark_terminal_emitted",
        _mark_terminal_emitted,
    )
    monkeypatch.setattr(
        cfw_router_mod.repo,
        "stop_forwarding",
        _stop_forwarding,
    )

    async def _record_ingest(payload: object) -> None:
        events.append("terminal_ingest")

    class _OrderingWebSocket:
        async def close(self, code: int = 1000) -> None:
            events.append("websocket_close")

    msg = CameraFeedWorkerInput(
        schema_version="1.0.1",
        record_id=uuid.uuid4(),
        user_id="user_1",
        session_id=session_id,
        timestamp=now_ingest,
        modality="image",
        source="browser",
        event="capture.close",
        capture_id=capture_id,
        timestamp_end=now_ingest,
    )

    result = asyncio.run(
        cfw_router_mod._apply_domain_and_handle_actions(
            cast(WebSocket, _OrderingWebSocket()),
            connection_key=connection_key,
            msg=msg,
            ingest_fn=_record_ingest,
        )
    )

    assert result is False
    assert events == [
        "terminal_ingest",
        "mark_terminal_emitted",
        "stop_forwarding",
        "websocket_close",
    ]


def test_terminal_ingest_not_dropped_when_forward_failure_triggers_shutdown(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Ensures that when a forward failure forces shutdown, the terminal ingest
    message is still delivered before the websocket closes.
    """

    captured: list[LandmarkExtractorTerminalInput] = []

    connection_key = "terminal-cancel-test"
    cfw_router_mod.repo.clear(connection_key)

    capture_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    now_ingest = datetime.now(timezone.utc)

    state = ActiveState(
        record_id=uuid.uuid4(),
        capture_id=capture_id,
        user_id="user_1",
        session_id=session_id,
        annotation_intent=None,
        timestamp_start=now_ingest,
        last_frame_timestamp=None,
        ingest_timestamp_open=now_ingest,
        fps_target=15,
        width=640,
        height=480,
        encoding="jpeg",
        frame_count=1,
        total_bytes=5,
        expected_next_seq=2,
        pending_meta=None,
        last_meta_ingest_timestamp=now_ingest,
        last_session_check_ingest_timestamp=now_ingest,
    )

    cfw_router_mod.repo.set_state(connection_key, state)

    async def _record_ingest(payload: object) -> None:
        assert isinstance(payload, LandmarkExtractorTerminalInput)
        captured.append(payload)

    class _DummyWebSocket:
        def __init__(self) -> None:
            self.closed = False
            self.close_code = None
            self.sent = []

        async def send_text(self, text: str) -> None:
            self.sent.append(text)

        async def close(self, code: int = 1000) -> None:
            self.closed = True
            self.close_code = code

    ws = _DummyWebSocket()

    result = asyncio.run(
        cfw_router_mod._emit_abort_and_close(
            cast(WebSocket, ws),
            connection_key=connection_key,
            now_ingest=now_ingest,
            current_state=state,
            capture_id=capture_id,
            error_code="forward_failed",
            last_msg_for_emit=None,
            ingest_fn=_record_ingest,
        )
    )

    assert result is False
    assert ws.closed is True

    terminal_msgs = [
        m
        for m in captured
        if m.event == "capture.abort" and str(m.capture_id) == capture_id
    ]

    assert len(terminal_msgs) == 1
    terminal = terminal_msgs[0]
    assert terminal.error_code == "forward_failed"


def test_ingest_failure_still_marks_terminal_emitted_to_prevent_retries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    connection_key = "mark-after-ingest-test"
    cfw_router_mod.repo.clear(connection_key)

    capture_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    now_ingest = datetime.now(timezone.utc)

    current_state = ActiveState(
        record_id=uuid.uuid4(),
        capture_id=capture_id,
        user_id="user_1",
        session_id=session_id,
        annotation_intent=None,
        timestamp_start=now_ingest,
        last_frame_timestamp=None,
        ingest_timestamp_open=now_ingest,
        fps_target=15,
        width=640,
        height=480,
        encoding="jpeg",
        frame_count=0,
        total_bytes=0,
        expected_next_seq=1,
        pending_meta=None,
        last_meta_ingest_timestamp=now_ingest,
        last_session_check_ingest_timestamp=now_ingest,
    )
    cfw_router_mod.repo.set_state(connection_key, current_state)

    marked: list[str] = []

    original_mark_terminal_emitted = cfw_router_mod.repo.mark_terminal_emitted

    def _mark_terminal_emitted(key: str) -> None:
        marked.append(key)
        original_mark_terminal_emitted(key)

    monkeypatch.setattr(
        cfw_router_mod.repo,
        "mark_terminal_emitted",
        _mark_terminal_emitted,
    )

    async def _failing_ingest(_: object) -> None:
        raise RuntimeError("forced ingest failure")

    ws = _DummyWebSocket()

    result = asyncio.run(
        cfw_router_mod._emit_abort_and_close(
            cast(WebSocket, ws),
            connection_key=connection_key,
            now_ingest=now_ingest,
            current_state=current_state,
            capture_id=capture_id,
            error_code="protocol_violation",
            last_msg_for_emit=None,
            ingest_fn=_failing_ingest,
        )
    )

    assert result is False
    assert marked == [connection_key]
    assert ws.close_codes == [1000]

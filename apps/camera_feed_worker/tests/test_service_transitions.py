# apps/camera_feed_worker/tests/test_service_transitions.py

from datetime import datetime

import pytest

from apps.camera_feed_worker import service


def _dt(s: str) -> datetime:
    # ISO8601 with Z
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


class OpenEvent:
    def __init__(
        self,
        *,
        capture_id="cap-1",
        record_id="rec-1",
        user_id="user-1",
        session_id="sess-1",
        timestamp_start=None,
        fps_target=15,
        width=640,
        height=480,
        encoding="jpeg",
        annotation=None,
    ):
        self.capture_id = capture_id
        self.record_id = record_id
        self.user_id = user_id
        self.session_id = session_id
        self.timestamp_start = timestamp_start or _dt("2026-02-04T12:00:00Z")
        self.fps_target = fps_target
        self.width = width
        self.height = height
        self.encoding = encoding
        self.annotation = annotation


class CloseEvent:
    def __init__(self, *, timestamp_end=None):
        self.timestamp_end = timestamp_end or _dt("2026-02-04T12:00:01Z")


def test_capture_open_from_idle_to_active(connection_key: str):
    now_ingest = _dt("2026-02-04T12:00:00Z")
    state0 = service.IdleState()

    state1, actions = service.dispatch(
        connection_key,
        state0,
        "capture.open",
        OpenEvent(),
        now_ingest=now_ingest,
    )

    assert isinstance(state1, service.ActiveState)
    assert state1.kind == "active"
    assert any(isinstance(a, service.RequestSessionValidation) for a in actions)


def test_capture_open_from_active_aborts_and_cleans_up(connection_key: str):
    now_ingest = _dt("2026-02-04T12:00:00Z")

    # First open → active
    active_state, _ = service.dispatch(
        connection_key,
        service.IdleState(),
        "capture.open",
        OpenEvent(),
        now_ingest=now_ingest,
    )
    assert isinstance(active_state, service.ActiveState)

    # Second open while active → abort semantics
    state2, actions = service.dispatch(
        connection_key,
        active_state,
        "capture.open",
        OpenEvent(),
        now_ingest=now_ingest,
    )

    assert isinstance(state2, service.IdleState)
    assert any(isinstance(a, service.AbortCapture) for a in actions)
    assert any(isinstance(a, service.CleanupCapture) for a in actions)

    abort = next(a for a in actions if isinstance(a, service.AbortCapture))
    assert abort.capture_id == active_state.capture_id
    assert abort.error_code == "protocol_violation"


def test_capture_close_from_idle_raises_protocol_violation(connection_key: str):
    now_ingest = _dt("2026-02-04T12:00:00Z")
    with pytest.raises(service.ProtocolViolation):
        # In idle state, close is invalid and should raise (no abort wrapper)
        service.dispatch(
            connection_key,
            service.IdleState(),
            "capture.close",
            CloseEvent(),
            now_ingest=now_ingest,
        )


def test_unknown_event_kind_raises_protocol_violation_in_idle(connection_key: str):
    now_ingest = _dt("2026-02-04T12:00:00Z")

    with pytest.raises(service.ProtocolViolation):
        service.dispatch(
            connection_key,
            service.IdleState(),
            "capture.nope",  # type: ignore[arg-type]
            object(),
            now_ingest=now_ingest,
        )


def test_capture_open_sets_annotation_intent(connection_key: str):
    now_ingest = _dt("2026-02-04T12:00:00Z")
    state0 = service.IdleState()

    annotation_obj = type("AnnotationObj", (), {"intent": "wave"})()

    state1, _ = service.dispatch(
        connection_key,
        state0,
        "capture.open",
        OpenEvent(annotation=annotation_obj),
        now_ingest=now_ingest,
    )

    assert isinstance(state1, service.ActiveState)
    assert state1.annotation_intent == "wave"


def test_capture_close_returns_idle_state(connection_key: str):
    now_ingest = _dt("2026-02-04T12:00:00Z")

    annotation_obj = type("AnnotationObj", (), {"intent": "wave"})()

    # Open -> Active
    active_state, _ = service.dispatch(
        connection_key,
        service.IdleState(),
        "capture.open",
        OpenEvent(annotation=annotation_obj),
        now_ingest=now_ingest,
    )
    assert isinstance(active_state, service.ActiveState)
    assert active_state.annotation_intent == "wave"

    # Close -> Idle
    state2, actions = service.dispatch(
        connection_key,
        active_state,
        "capture.close",
        CloseEvent(timestamp_end=_dt("2026-02-04T12:00:01Z")),
        now_ingest=_dt("2026-02-04T12:00:01Z"),
    )

    assert isinstance(state2, service.IdleState)
    assert any(isinstance(a, service.CleanupCapture) for a in actions)


def test_abort_returns_idle_state(connection_key: str):
    now_ingest = _dt("2026-02-04T12:00:00Z")

    annotation_obj = type("AnnotationObj", (), {"intent": "wave"})()

    # Open -> Active (with annotation)
    active_state, _ = service.dispatch(
        connection_key,
        service.IdleState(),
        "capture.open",
        OpenEvent(annotation=annotation_obj),
        now_ingest=now_ingest,
    )
    assert isinstance(active_state, service.ActiveState)
    assert active_state.annotation_intent == "wave"

    # Trigger a domain error while active:
    # frame_bytes without pending_meta => ProtocolViolation => abort wrapper => Idle
    state2, actions = service.dispatch(
        connection_key,
        active_state,
        "capture.frame_bytes",
        10,  # any byte length
        now_ingest=_dt("2026-02-04T12:00:00Z"),
    )

    assert isinstance(state2, service.IdleState)
    assert any(isinstance(a, service.AbortCapture) for a in actions)
    assert any(isinstance(a, service.CleanupCapture) for a in actions)

    abort = next(a for a in actions if isinstance(a, service.AbortCapture))
    assert abort.error_code == "protocol_violation"
    assert abort.capture_id == active_state.capture_id


def test_annotation_isolated_per_connection_key():
    now_ingest = _dt("2026-02-04T12:00:00Z")

    ann_a = type("AnnotationObj", (), {"intent": "wave"})()
    ann_b = type("AnnotationObj", (), {"intent": "point"})()

    # Connection A
    state_a, _ = service.dispatch(
        "conn-a",
        service.IdleState(),
        "capture.open",
        OpenEvent(capture_id="cap-a", annotation=ann_a),
        now_ingest=now_ingest,
    )
    assert isinstance(state_a, service.ActiveState)
    assert state_a.annotation_intent == "wave"

    # Connection B
    state_b, _ = service.dispatch(
        "conn-b",
        service.IdleState(),
        "capture.open",
        OpenEvent(capture_id="cap-b", annotation=ann_b),
        now_ingest=now_ingest,
    )
    assert isinstance(state_b, service.ActiveState)
    assert state_b.annotation_intent == "point"

    # Ensure no cross-contamination
    assert state_a.annotation_intent != state_b.annotation_intent

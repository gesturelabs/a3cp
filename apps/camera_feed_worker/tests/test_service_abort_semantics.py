# apps/camera_feed_worker/tests/test_service_abort_semantics.py

from datetime import datetime

import pytest

from apps.camera_feed_worker import service


def _dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


class OpenEvent:
    def __init__(
        self,
        *,
        capture_id="cap-1",
        user_id="user-1",
        session_id="sess-1",
        timestamp_start=None,
        fps_target=15,
        width=640,
        height=480,
        encoding="jpeg",
    ):
        self.capture_id = capture_id
        self.user_id = user_id
        self.session_id = session_id
        self.timestamp_start = timestamp_start or _dt("2026-02-04T12:00:00Z")
        self.fps_target = fps_target
        self.width = width
        self.height = height
        self.encoding = encoding


class FrameMetaEvent:
    def __init__(self, *, seq: int, timestamp_frame: datetime, byte_length: int):
        self.seq = seq
        self.timestamp_frame = timestamp_frame
        self.byte_length = byte_length


def _open_active(now_ingest: datetime) -> service.ActiveState:
    st, _ = service.dispatch(
        service.IdleState(), "capture.open", OpenEvent(), now_ingest
    )
    assert isinstance(st, service.ActiveState)
    return st


def test_any_domain_error_in_active_state_returns_idle_and_emits_abort_and_cleanup():
    active = _open_active(_dt("2026-02-04T12:00:00Z"))

    # Trigger a CameraFeedWorkerError in ActiveState: wrong seq
    st2, actions = service.dispatch(
        active,
        "capture.frame_meta",
        FrameMetaEvent(
            seq=999, timestamp_frame=_dt("2026-02-04T12:00:00.100Z"), byte_length=10
        ),
        _dt("2026-02-04T12:00:00.010Z"),
    )

    assert isinstance(st2, service.IdleState)

    abort = next(a for a in actions if isinstance(a, service.AbortCapture))
    cleanup = next(a for a in actions if isinstance(a, service.CleanupCapture))

    assert abort.error_code == "protocol_violation"
    assert abort.capture_id == active.capture_id
    assert cleanup.capture_id == active.capture_id


def test_idle_state_errors_are_reraised_no_abort_wrapper():
    now_ingest = _dt("2026-02-04T12:00:00Z")

    # capture.frame_meta is invalid in IdleState, should raise ProtocolViolation (not return Idle+actions)
    with pytest.raises(service.ProtocolViolation):
        service.dispatch(
            service.IdleState(),
            "capture.frame_meta",
            FrameMetaEvent(
                seq=1, timestamp_frame=_dt("2026-02-04T12:00:00.100Z"), byte_length=10
            ),
            now_ingest,
        )

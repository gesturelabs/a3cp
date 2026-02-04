# apps/camera_feed_worker/tests/test_service_happy_path.py

from datetime import datetime

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


class CloseEvent:
    def __init__(self, *, timestamp_end: datetime):
        self.timestamp_end = timestamp_end


def test_full_valid_flow_open_meta_bytes_close():
    # 1) open
    st0, actions0 = service.dispatch(
        service.IdleState(),
        "capture.open",
        OpenEvent(timestamp_start=_dt("2026-02-04T12:00:00Z")),
        _dt("2026-02-04T12:00:00Z"),
    )
    assert isinstance(st0, service.ActiveState)
    assert any(isinstance(a, service.RequestSessionValidation) for a in actions0)

    # 2) meta
    st1, actions1 = service.dispatch(
        st0,
        "capture.frame_meta",
        FrameMetaEvent(
            seq=1, timestamp_frame=_dt("2026-02-04T12:00:00.100Z"), byte_length=123
        ),
        _dt("2026-02-04T12:00:00.010Z"),
    )
    assert isinstance(st1, service.ActiveState)
    assert actions1 == []
    assert st1.pending_meta is not None

    # 3) bytes
    st2, actions2 = service.dispatch(
        st1,
        "capture.frame_bytes",
        123,
        _dt("2026-02-04T12:00:00.020Z"),
    )
    assert isinstance(st2, service.ActiveState)
    assert any(isinstance(a, service.ForwardFrame) for a in actions2)

    fwd = next(a for a in actions2 if isinstance(a, service.ForwardFrame))
    assert fwd.capture_id == st0.capture_id
    assert fwd.seq == 1
    assert fwd.byte_length == 123
    assert fwd.timestamp_event == _dt("2026-02-04T12:00:00.100Z")

    # 4) close
    st3, actions3 = service.dispatch(
        st2,
        "capture.close",
        CloseEvent(timestamp_end=_dt("2026-02-04T12:00:01Z")),
        _dt("2026-02-04T12:00:01Z"),
    )
    assert isinstance(st3, service.IdleState)
    assert any(isinstance(a, service.CleanupCapture) for a in actions3)
    assert not any(isinstance(a, service.AbortCapture) for a in actions3)

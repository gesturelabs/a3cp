# apps/camera_feed_worker/tests/test_service_timeouts.py

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


def _open_active(now_ingest: datetime) -> service.ActiveState:
    st, _ = service.dispatch(
        service.IdleState(), "capture.open", OpenEvent(), now_ingest
    )
    assert isinstance(st, service.ActiveState)
    return st


def test_meta_to_bytes_timeout_aborts():
    # open at ingest 12:00:00
    active = _open_active(_dt("2026-02-04T12:00:00Z"))

    # meta at ingest 12:00:00.010 (sets pending_meta with meta_ingest_timestamp)
    st1, _ = service.dispatch(
        active,
        "capture.frame_meta",
        FrameMetaEvent(
            seq=1, timestamp_frame=_dt("2026-02-04T12:00:00.100Z"), byte_length=10
        ),
        _dt("2026-02-04T12:00:00.010Z"),
    )
    assert isinstance(st1, service.ActiveState)
    assert st1.pending_meta is not None

    # tick at >2s after meta ingest
    st2, actions = service.dispatch(
        st1,
        "tick",
        object(),
        _dt("2026-02-04T12:00:02.011Z"),
    )

    assert isinstance(st2, service.IdleState)
    abort = next(a for a in actions if isinstance(a, service.AbortCapture))
    assert abort.error_code == "protocol_violation"


def test_idle_timeout_no_meta_aborts():
    # open at ingest 12:00:00; last_meta_ingest_timestamp baseline set in handle_open
    active = _open_active(_dt("2026-02-04T12:00:00Z"))

    # tick at >5s with no frame_meta ever received
    st2, actions = service.dispatch(
        active,
        "tick",
        object(),
        _dt("2026-02-04T12:00:05.001Z"),
    )

    assert isinstance(st2, service.IdleState)
    abort = next(a for a in actions if isinstance(a, service.AbortCapture))
    assert abort.error_code == "protocol_violation"


def test_no_timeouts_within_limits_remains_active():
    active = _open_active(_dt("2026-02-04T12:00:00Z"))

    # tick at 1s: within duration, within idle timeout baseline (5s), no pending_meta
    st2, actions = service.dispatch(
        active,
        "tick",
        object(),
        _dt("2026-02-04T12:00:01Z"),
    )

    assert isinstance(st2, service.ActiveState)
    assert actions == []

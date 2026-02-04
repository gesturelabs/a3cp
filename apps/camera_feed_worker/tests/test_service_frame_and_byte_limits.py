# apps/camera_feed_worker/tests/test_service_frame_and_byte_limits.py

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


def _accept_frame(
    active: service.ActiveState,
    *,
    seq: int,
    ts_frame: datetime,
    byte_length: int,
    now_ingest: datetime,
) -> service.ActiveState:
    st1, _ = service.dispatch(
        active,
        "capture.frame_meta",
        FrameMetaEvent(seq=seq, timestamp_frame=ts_frame, byte_length=byte_length),
        now_ingest,
    )
    assert isinstance(st1, service.ActiveState)
    st2, _ = service.dispatch(
        st1,
        "capture.frame_bytes",
        byte_length,
        now_ingest,
    )
    assert isinstance(st2, service.ActiveState)
    return st2


def test_frame_count_exceeds_max_frames_aborts():
    now = _dt("2026-02-04T12:00:00Z")
    active = _open_active(now)

    # Set state right below limit (MAX_FRAMES - 1), with expected seq = 1
    active = service.ActiveState(
        capture_id=active.capture_id,
        user_id=active.user_id,
        session_id=active.session_id,
        timestamp_start=active.timestamp_start,
        ingest_timestamp_open=active.ingest_timestamp_open,
        fps_target=active.fps_target,
        width=active.width,
        height=active.height,
        encoding=active.encoding,
        frame_count=service.MAX_FRAMES,  # already at max; next accepted frame should exceed
        total_bytes=0,
        expected_next_seq=1,
        last_frame_timestamp=None,
        pending_meta=None,
        last_meta_ingest_timestamp=active.last_meta_ingest_timestamp,
        last_session_check_ingest_timestamp=active.last_session_check_ingest_timestamp,
    )

    st2, actions = service.dispatch(
        active,
        "capture.frame_meta",
        FrameMetaEvent(
            seq=1, timestamp_frame=_dt("2026-02-04T12:00:00.100Z"), byte_length=10
        ),
        _dt("2026-02-04T12:00:00.010Z"),
    )
    assert isinstance(st2, service.ActiveState)

    st3, actions = service.dispatch(
        st2,
        "capture.frame_bytes",
        10,
        _dt("2026-02-04T12:00:00.020Z"),
    )

    assert isinstance(st3, service.IdleState)
    abort = next(a for a in actions if isinstance(a, service.AbortCapture))
    assert abort.error_code == "limit_frame_count_exceeded"


def test_single_frame_exceeds_max_frame_bytes_aborts():
    now = _dt("2026-02-04T12:00:00Z")
    active = _open_active(now)

    too_big = service.MAX_FRAME_BYTES + 1

    st2, _ = service.dispatch(
        active,
        "capture.frame_meta",
        FrameMetaEvent(
            seq=1, timestamp_frame=_dt("2026-02-04T12:00:00.100Z"), byte_length=too_big
        ),
        _dt("2026-02-04T12:00:00.010Z"),
    )
    assert isinstance(st2, service.ActiveState)

    st3, actions = service.dispatch(
        st2,
        "capture.frame_bytes",
        too_big,
        _dt("2026-02-04T12:00:00.020Z"),
    )

    assert isinstance(st3, service.IdleState)
    abort = next(a for a in actions if isinstance(a, service.AbortCapture))
    assert abort.error_code == "limit_frame_bytes_exceeded"


def test_total_bytes_exceeds_max_total_bytes_aborts():
    now = _dt("2026-02-04T12:00:00Z")
    active = _open_active(now)

    # Set state near max total bytes
    active = service.ActiveState(
        capture_id=active.capture_id,
        user_id=active.user_id,
        session_id=active.session_id,
        timestamp_start=active.timestamp_start,
        ingest_timestamp_open=active.ingest_timestamp_open,
        fps_target=active.fps_target,
        width=active.width,
        height=active.height,
        encoding=active.encoding,
        frame_count=0,
        total_bytes=service.MAX_TOTAL_BYTES,  # already at max; any new bytes exceed
        expected_next_seq=1,
        last_frame_timestamp=None,
        pending_meta=None,
        last_meta_ingest_timestamp=active.last_meta_ingest_timestamp,
        last_session_check_ingest_timestamp=active.last_session_check_ingest_timestamp,
    )

    st2, _ = service.dispatch(
        active,
        "capture.frame_meta",
        FrameMetaEvent(
            seq=1, timestamp_frame=_dt("2026-02-04T12:00:00.100Z"), byte_length=10
        ),
        _dt("2026-02-04T12:00:00.010Z"),
    )
    assert isinstance(st2, service.ActiveState)

    st3, actions = service.dispatch(
        st2,
        "capture.frame_bytes",
        10,
        _dt("2026-02-04T12:00:00.020Z"),
    )

    assert isinstance(st3, service.IdleState)
    abort = next(a for a in actions if isinstance(a, service.AbortCapture))
    assert abort.error_code == "limit_total_bytes_exceeded"


def test_valid_frame_increments_counters_correctly():
    now = _dt("2026-02-04T12:00:00Z")
    active = _open_active(now)

    st2 = _accept_frame(
        active,
        seq=1,
        ts_frame=_dt("2026-02-04T12:00:00.100Z"),
        byte_length=123,
        now_ingest=_dt("2026-02-04T12:00:00.010Z"),
    )

    assert st2.frame_count == 1
    assert st2.total_bytes == 123
    assert st2.expected_next_seq == 2
    assert st2.pending_meta is None
    assert st2.last_frame_timestamp == _dt("2026-02-04T12:00:00.100Z")

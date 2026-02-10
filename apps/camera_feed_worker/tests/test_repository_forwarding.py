# path: apps/camera_feed_worker/tests/test_repository_forwarding.py

import asyncio
from datetime import datetime, timezone

import pytest

from apps.camera_feed_worker.repository import (
    CameraFeedWorkerRepository,
    ForwardFailed,
    ForwardItem,
    ForwardNotInitialized,
    LimitForwardBufferExceeded,
)


def _mk_item(*, seq: int = 1, payload: bytes = b"abc") -> ForwardItem:
    ts = datetime.now(timezone.utc)
    return ForwardItem(
        capture_id="cap_1",
        seq=seq,
        timestamp_frame=ts,
        payload=payload,
        byte_length=len(payload),
        encoding="jpeg",
        width=640,
        height=480,
        user_id="user_1",
        session_id="sess_1",
    )


def test_init_forwarding_initializes_queue_and_counters() -> None:
    repo = CameraFeedWorkerRepository()
    ck = "conn1"

    repo.init_forwarding(ck, "cap1", max_frames=10, max_bytes=10_000)

    frames, bytes_ = repo.get_forward_stats(ck)
    assert frames == 0
    assert bytes_ == 0


def test_enqueue_frame_increments_counters() -> None:
    repo = CameraFeedWorkerRepository()
    ck = "conn1"
    repo.init_forwarding(ck, "cap1", max_frames=10, max_bytes=10_000)

    repo.enqueue_frame(ck, _mk_item(seq=1, payload=b"x" * 100))

    frames, bytes_ = repo.get_forward_stats(ck)
    assert frames == 1
    assert bytes_ == 100


def test_enqueue_frame_requires_init() -> None:
    repo = CameraFeedWorkerRepository()
    ck = "conn1"

    with pytest.raises(ForwardNotInitialized):
        repo.enqueue_frame(ck, _mk_item(seq=1, payload=b"x" * 10))


def test_max_forward_buffer_frames_enforced() -> None:
    repo = CameraFeedWorkerRepository()
    ck = "conn1"
    repo.init_forwarding(ck, "cap1", max_frames=1, max_bytes=10_000)

    repo.enqueue_frame(ck, _mk_item(seq=1, payload=b"x" * 10))

    with pytest.raises(LimitForwardBufferExceeded):
        repo.enqueue_frame(ck, _mk_item(seq=1, payload=b"x" * 10))


def test_max_forward_buffer_bytes_enforced() -> None:
    repo = CameraFeedWorkerRepository()
    ck = "conn1"
    repo.init_forwarding(ck, "cap1", max_frames=10, max_bytes=15)

    repo.enqueue_frame(ck, _mk_item(seq=1, payload=b"x" * 10))

    with pytest.raises(LimitForwardBufferExceeded):
        repo.enqueue_frame(ck, _mk_item(seq=1, payload=b"x" * 10))


def test_stop_forwarding_resets_counters_and_clears_queue() -> None:
    repo = CameraFeedWorkerRepository()
    ck = "conn1"
    repo.init_forwarding(ck, "cap1", max_frames=10, max_bytes=10_000)

    repo.enqueue_frame(ck, _mk_item(seq=1, payload=b"x" * 10))
    repo.enqueue_frame(ck, _mk_item(seq=2, payload=b"x" * 20))

    frames, bytes_ = repo.get_forward_stats(ck)
    assert frames == 2
    assert bytes_ == 30

    repo.stop_forwarding(ck)

    frames2, bytes2 = repo.get_forward_stats(ck)
    assert frames2 == 0
    assert bytes2 == 0

    with pytest.raises(ForwardNotInitialized):
        repo.enqueue_frame(ck, _mk_item(seq=3, payload=b"x" * 5))

    # Downstream failure state should also be cleared
    repo.raise_if_forward_failed(ck)  # should not raise


def test_forward_buffer_overflow_enforced_by_frames() -> None:
    repo = CameraFeedWorkerRepository()
    ck = "conn1"
    repo.init_forwarding(ck, "cap1", max_frames=1, max_bytes=10_000)

    repo.enqueue_frame(ck, _mk_item(seq=1, payload=b"x" * 10))

    with pytest.raises(LimitForwardBufferExceeded):
        repo.enqueue_frame(ck, _mk_item(seq=2, payload=b"x" * 10))


def test_forward_buffer_overflow_enforced_by_bytes() -> None:
    repo = CameraFeedWorkerRepository()
    ck = "conn1"
    repo.init_forwarding(ck, "cap1", max_frames=10, max_bytes=10)

    with pytest.raises(LimitForwardBufferExceeded):
        repo.enqueue_frame(ck, _mk_item(seq=1, payload=b"x" * 11))


def test_forward_task_failure_is_propagated_via_repo() -> None:
    repo = CameraFeedWorkerRepository()
    ck = "conn1"
    repo.init_forwarding(ck, "cap1", max_frames=10, max_bytes=10_000)

    async def _boom() -> None:
        raise RuntimeError("downstream exploded")

    async def _run() -> None:
        t = asyncio.create_task(_boom())
        repo.start_forwarding_task(ck, t)
        with pytest.raises(RuntimeError):
            await t  # ensure task completes and callback runs

    asyncio.run(_run())

    with pytest.raises(ForwardFailed):
        repo.raise_if_forward_failed(ck)

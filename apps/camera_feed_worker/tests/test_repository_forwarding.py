# path: apps/camera_feed_worker/tests/test_repository_forwarding.py

import pytest

from apps.camera_feed_worker.repository import (
    CameraFeedWorkerRepository,
    ForwardItem,
    ForwardNotInitialized,
    LimitForwardBufferExceeded,
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

    repo.enqueue_frame(ck, ForwardItem(seq=1, byte_length=100, payload=b"x" * 100))

    frames, bytes_ = repo.get_forward_stats(ck)
    assert frames == 1
    assert bytes_ == 100


def test_enqueue_frame_requires_init() -> None:
    repo = CameraFeedWorkerRepository()
    ck = "conn1"

    with pytest.raises(ForwardNotInitialized):
        repo.enqueue_frame(ck, ForwardItem(seq=1, byte_length=10, payload=b"x" * 10))


def test_max_forward_buffer_frames_enforced() -> None:
    repo = CameraFeedWorkerRepository()
    ck = "conn1"
    repo.init_forwarding(ck, "cap1", max_frames=1, max_bytes=10_000)

    repo.enqueue_frame(ck, ForwardItem(seq=1, byte_length=10, payload=b"x" * 10))

    with pytest.raises(LimitForwardBufferExceeded):
        repo.enqueue_frame(ck, ForwardItem(seq=2, byte_length=10, payload=b"x" * 10))


def test_max_forward_buffer_bytes_enforced() -> None:
    repo = CameraFeedWorkerRepository()
    ck = "conn1"
    repo.init_forwarding(ck, "cap1", max_frames=10, max_bytes=15)

    repo.enqueue_frame(ck, ForwardItem(seq=1, byte_length=10, payload=b"x" * 10))

    with pytest.raises(LimitForwardBufferExceeded):
        repo.enqueue_frame(ck, ForwardItem(seq=2, byte_length=10, payload=b"x" * 10))


def test_stop_forwarding_resets_counters_and_clears_queue() -> None:
    repo = CameraFeedWorkerRepository()
    ck = "conn1"
    repo.init_forwarding(ck, "cap1", max_frames=10, max_bytes=10_000)

    repo.enqueue_frame(ck, ForwardItem(seq=1, byte_length=10, payload=b"x" * 10))
    repo.enqueue_frame(ck, ForwardItem(seq=2, byte_length=20, payload=b"x" * 20))

    frames, bytes_ = repo.get_forward_stats(ck)
    assert frames == 2
    assert bytes_ == 30

    repo.stop_forwarding(ck)

    frames2, bytes2 = repo.get_forward_stats(ck)
    assert frames2 == 0
    assert bytes2 == 0

    with pytest.raises(ForwardNotInitialized):
        repo.enqueue_frame(ck, ForwardItem(seq=3, byte_length=5, payload=b"x" * 5))

    # Downstream failure state should also be cleared
    repo.raise_if_forward_failed(ck)  # should not raise

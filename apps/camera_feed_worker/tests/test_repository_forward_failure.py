import asyncio

import pytest

from apps.camera_feed_worker.repository import CameraFeedWorkerRepository, ForwardFailed


async def _failing_coro():
    raise RuntimeError("boom")


def test_forward_failed_is_surfaced() -> None:
    repo = CameraFeedWorkerRepository()
    ck = "conn1"

    repo.init_forwarding(ck, "cap1", max_frames=10, max_bytes=10_000)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    task = loop.create_task(_failing_coro())
    repo.start_forwarding_task(ck, task)

    # Run loop long enough for task to execute and fail
    with pytest.raises(RuntimeError):
        loop.run_until_complete(task)

    with pytest.raises(ForwardFailed):
        repo.raise_if_forward_failed(ck)

    loop.close()

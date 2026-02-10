from __future__ import annotations

from collections.abc import Awaitable, Callable

from apps.camera_feed_worker.forward_adapter import forward_item_to_landmark_input
from apps.camera_feed_worker.repository import repo
from schemas import LandmarkExtractorInput


async def forwarder_loop(
    *,
    connection_key: str,
    ingest_fn: Callable[[LandmarkExtractorInput], Awaitable[None]],
) -> None:
    """
    Async worker:
    - consumes ForwardItem from repo queue
    - adapts to LandmarkExtractorInput (pure)
    - calls ingest entrypoint (injected)

    Must NOT:
    - send WebSocket messages
    - close WebSocket
    - call repo.clear()
    """
    while True:
        item = await repo.dequeue_frame(connection_key)
        le_in = forward_item_to_landmark_input(item)
        await ingest_fn(le_in)

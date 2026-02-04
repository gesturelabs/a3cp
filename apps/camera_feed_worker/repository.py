# apps/camera_feed_worker/repository.py

"""
camera_feed_worker.repository (Sprint 1)

In-memory state holder for camera_feed_worker.

Responsibilities (Sprint 1):
- Own mutable per-connection state (State machine state + any per-connection metadata)
- Provide a minimal API to get/set/clear state
- No IO, no persistence, no logs

This exists to keep service.py pure and to keep router.py thin.
"""

from __future__ import annotations

from typing import Dict

from apps.camera_feed_worker.service import IdleState, State


class CameraFeedWorkerRepository:
    """
    Per-process in-memory repository.

    Keying:
    - Uses an opaque connection_key chosen by the route layer (e.g., id(websocket) or a UUID).
    - Stores exactly one State per connection.

    Concurrency:
    - Sprint 1 assumes a single event loop / single worker process for demo use.
    - If multiple workers are used later, this must be replaced with a shared store.
    """

    def __init__(self) -> None:
        self._states: Dict[str, State] = {}

    def get_state(self, connection_key: str) -> State:
        return self._states.get(connection_key, IdleState())

    def set_state(self, connection_key: str, state: State) -> None:
        self._states[connection_key] = state

    def reset_state(self, connection_key: str) -> None:
        self._states[connection_key] = IdleState()

    def clear(self, connection_key: str) -> None:
        # Remove entirely (vs reset-to-idle). Useful on disconnect.
        if connection_key in self._states:
            del self._states[connection_key]


# Default singleton repository instance (Sprint 1)
repo = CameraFeedWorkerRepository()

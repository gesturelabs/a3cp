# apps/camera_feed_worker/routes/router.py

from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket

router = APIRouter(prefix="/camera_feed_worker", tags=["camera_feed_worker"])


@router.post("/capture.tick", response_model=dict)
def capture_tick() -> dict:
    """
    HTTP hook to drive time-based evaluation in Sprint 1.
    Ingest time is server-authoritative.
    """
    now_ingest = datetime.now(timezone.utc)

    # Sprint 1 A: skeleton only (no domain wiring yet)
    return {
        "status": "not_implemented",
        "source": "camera_feed_worker",
        "now_ingest": now_ingest.isoformat(),
    }


@router.websocket("/ws")
async def ws_camera_feed(websocket: WebSocket) -> None:
    """
    WebSocket entry point for real-time capture.
    Sprint 1 A: accept and immediately close (no streaming logic yet).
    """
    await websocket.accept()
    await websocket.close(code=1000)

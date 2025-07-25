# api/routes/camera_feed_worker_routes.py

from fastapi import APIRouter, HTTPException

from schemas.camera_feed_worker.camera_feed_worker import (
    CameraFeedWorkerConfig,
    CameraFrameMetadata,
)

router = APIRouter()


@router.post("/", response_model=CameraFrameMetadata)
def simulate_camera_frame_capture(
    config: CameraFeedWorkerConfig,
) -> CameraFrameMetadata:
    """
    Simulate a camera frame capture given device config.
    Returns frame metadata with mock values.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")

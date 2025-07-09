# camera_feed_worker Pydantic model
from datetime import datetime
from typing import Literal, Optional, Tuple

from pydantic import BaseModel, Field


class CameraFeedWorkerConfig(BaseModel):
    device_id: Optional[str] = Field(
        None, description="Video device path or index, e.g., '/dev/video0' or '0'"
    )
    resolution: Tuple[int, int] = Field(
        ..., description="Target resolution as (width, height), e.g., (640, 480)"
    )
    fps: int = Field(..., description="Target capture frame rate in frames per second")
    session_id: Optional[str] = Field(
        None, description="Session identifier for downstream tagging"
    )
    user_id: Optional[str] = Field(
        None, description="User identifier for downstream tagging"
    )


class CameraFrameMetadata(BaseModel):
    timestamp: datetime = Field(
        ..., description="UTC ISO 8601 timestamp of video frame capture"
    )
    device_id: Optional[str] = Field(
        None, description="Device ID or index used for capture"
    )
    modality: Literal["image"] = "image"
    source: Literal["communicator"] = "communicator"
    frame_index: Optional[int] = Field(
        None, description="Index of the frame in the current stream or segment"
    )
    stream_segment_id: Optional[str] = Field(
        None, description="Optional window or chunk ID for stream segmentation"
    )
    error: Optional[str] = Field(
        None, description="Optional error message if frame read failed"
    )

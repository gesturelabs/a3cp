# schemas/audio_feed_worker.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AudioFeedWorkerConfig(BaseModel):
    device_index: Optional[int] = Field(None, description="Index of audio input device")
    sample_rate: int = Field(..., description="Target sample rate in Hz, e.g., 16000")
    chunk_size: int = Field(..., description="Internal buffer size (not logged)")


class AudioChunkMetadata(BaseModel):
    timestamp: datetime = Field(
        ..., description="UTC ISO 8601 timestamp of audio capture"
    )
    device_id: Optional[str] = Field(None, description="Driver/device identifier")
    sample_rate: int = Field(..., description="Sampling rate (Hz)")
    num_frames: int = Field(..., description="Frames in this chunk")
    dtype: str = Field(..., description="PCM dtype, e.g., int16")
    channels: int = Field(..., description="Number of channels")


# Single source of truth for examples (module-level)
def example_input() -> dict:
    return {"device_index": 0, "sample_rate": 16000, "chunk_size": 512}


def example_output() -> dict:
    return {
        "timestamp": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
        "device_id": "mic-0",
        "sample_rate": 16000,
        "num_frames": 512,
        "dtype": "int16",
        "channels": 1,
    }

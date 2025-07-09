from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class AudioFeedWorkerConfig(BaseModel):
    device_index: Optional[int] = Field(None, description="Index of audio input device")
    sample_rate: int = Field(..., description="Target sample rate in Hz, e.g., 16000")
    chunk_size: int = Field(
        ..., description="Internal buffer size in samples (not logged)"
    )
    session_id: Optional[str] = Field(None, description="Session identifier")
    user_id: Optional[str] = Field(None, description="User identifier")


class AudioChunkMetadata(BaseModel):
    timestamp: datetime = Field(
        ..., description="UTC ISO 8601 timestamp of audio capture"
    )
    device_id: Optional[str] = Field(
        None, description="Device ID or label for hardware source"
    )
    sample_rate: int = Field(..., description="Sample rate used during capture")
    waveform_format: Literal["bytes", "base64", "ndarray"] = Field(
        ..., description="Encoding format used for audio_payload"
    )
    audio_payload: str = Field(
        ..., description="Waveform data as encoded string or blob reference"
    )
    modality: Literal["audio"] = "audio"
    source: Literal["communicator"] = "communicator"
    error: Optional[str] = Field(
        None, description="Optional error message if capture failed"
    )

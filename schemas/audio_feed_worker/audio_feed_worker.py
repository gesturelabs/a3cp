from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class AudioFeedWorkerConfig(BaseModel):
    device_index: Optional[int] = Field(None, description="Index of audio input device")
    sample_rate: int = Field(..., description="Target sample rate in Hz, e.g., 16000")
    chunk_size: int = Field(..., description="Internal buffer size (not logged)")

    @staticmethod
    def example_input() -> dict:
        return {"device_index": 0, "sample_rate": 16000, "chunk_size": 512}

    @staticmethod
    def example_output() -> dict:
        # Config is not expected to produce output in normal flow
        return AudioFeedWorkerConfig.example_input()


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

    @staticmethod
    def example_input() -> dict:
        return {"device_index": 0, "sample_rate": 16000, "chunk_size": 512}

    @staticmethod
    def example_output() -> dict:
        return {
            "timestamp": "2025-07-09T09:12:34.567Z",
            "device_id": "mic_usb_01",
            "sample_rate": 16000,
            "waveform_format": "base64",
            "audio_payload": "UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YcAAAA==",
            "modality": "audio",
            "source": "communicator",
            "error": None,
        }

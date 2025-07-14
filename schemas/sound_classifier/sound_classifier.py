# sound_classifier Pydantic model
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class IntentPrediction(BaseModel):
    intent: str = Field(..., description="Predicted intent label")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score between 0 and 1"
    )


class SoundClassifierInput(BaseModel):
    timestamp: datetime = Field(
        ..., description="UTC ISO 8601 timestamp of audio capture"
    )
    user_id: str = Field(..., description="Pseudonymous user identifier")
    session_id: str = Field(..., description="Interaction session identifier")
    modality: Literal["audio"] = "audio"
    source: Literal["communicator"] = "communicator"
    sample_rate: int = Field(..., description="Audio sample rate in Hz (e.g., 16000)")
    audio_format: Literal["base64", "bytes", "ndarray"] = Field(
        ..., description="Format of the audio payload encoding"
    )
    audio_payload: str = Field(
        ..., description="Encoded audio waveform (base64 string or similar)"
    )
    device_id: Optional[str] = Field(None, description="Optional source hardware ID")
    error: Optional[str] = Field(None, description="Optional capture or decode error")

    @staticmethod
    def example_input() -> dict:
        return {
            "timestamp": "2025-07-14T17:45:00.000Z",
            "user_id": "elias01",
            "session_id": "sess_20250714_e01",
            "modality": "audio",
            "source": "communicator",
            "sample_rate": 16000,
            "audio_format": "base64",
            "audio_payload": "UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YcAAAA==",
            "device_id": "mic_usb_01",
            "error": None,
        }


class SoundClassifierOutput(BaseModel):
    timestamp: datetime = Field(
        ..., description="UTC ISO 8601 timestamp of inference result"
    )
    user_id: str = Field(..., description="Pseudonymous user ID")
    session_id: str = Field(..., description="Interaction session ID")
    intent_predictions: List[IntentPrediction] = Field(
        ..., description="Ranked list of predicted intents with confidence scores"
    )
    model_version: Optional[str] = Field(
        None, description="Version identifier of the model used for inference"
    )
    inference_time_ms: Optional[int] = Field(
        None, description="Elapsed inference time in milliseconds"
    )

    @staticmethod
    def example_output() -> dict:
        return {
            "timestamp": "2025-07-14T17:45:01.000Z",
            "user_id": "elias01",
            "session_id": "sess_20250714_e01",
            "intent_predictions": [
                {"intent": "play", "confidence": 0.84},
                {"intent": "stop", "confidence": 0.10},
                {"intent": "help", "confidence": 0.06},
            ],
            "model_version": "audio_v1.2_elias01",
            "inference_time_ms": 142,
        }

# visual_environment_classifier Pydantic model
from typing import Dict, Optional

from pydantic import BaseModel, Field


class VisualEnvironmentPrediction(BaseModel):
    environment_label: str = Field(
        ..., description="Predicted environment class (e.g., 'kitchen', 'bedroom')"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model confidence score for the predicted label",
    )
    timestamp: str = Field(
        ..., description="UTC ISO8601 timestamp of frame capture or classification"
    )
    session_id: str = Field(..., description="Interaction session identifier")
    frame_id: Optional[str] = Field(
        None, description="Optional identifier for the video frame"
    )
    device_id: Optional[str] = Field(
        None, description="Optional hardware identifier of the camera"
    )
    context_flags: Optional[Dict[str, bool]] = Field(
        None,
        description="Optional map of derived context flags (e.g., {'is_public': true})",
    )
    model_version: Optional[str] = Field(
        None, description="Version of the environment classification model used"
    )
    input_hash: Optional[str] = Field(
        None, description="SHA-256 hash of the input frame for audit/reproducibility"
    )
    source_module: Optional[str] = Field(
        "visual_environment_classifier",
        description="Module name generating the prediction",
    )

    @staticmethod
    def example_input() -> dict:
        return {
            "environment_label": "kitchen",
            "confidence_score": 0.92,
            "timestamp": "2025-07-14T18:00:00.000Z",
            "session_id": "sess_20250714_e01",
            "frame_id": "frame_000023",
            "device_id": "jetson_cam_01",
            "context_flags": {"is_public": False, "is_cooking_area": True},
            "model_version": "scene_cnn_v2.3",
            "input_hash": "sha256:a1b2c3d4e5f678...",
            "source_module": "visual_environment_classifier",
        }

    @staticmethod
    def example_output() -> dict:
        return VisualEnvironmentPrediction.example_input()

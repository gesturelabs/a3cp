# landmark_visualizer Pydantic model
# schemas/landmark_visualizer.py

"""
Pydantic schema for the landmark visualizer module.

This schema defines structured inputs and outputs for rendering landmark visualizations
from recorded gesture sessions. It supports Parquet-based input data and generates static
images or animations for debugging, feedback, or UI display.
"""

from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field


class LandmarkVisualizerInput(BaseModel):
    session_id: Annotated[
        str, Field(..., description="Unique session ID for the gesture recording")
    ]
    user_id: Annotated[str, Field(..., description="User pseudonym or identifier")]
    modality: Literal["vision"] = Field(
        "vision", description="Modality for recorded data"
    )
    parquet_path: Annotated[
        str, Field(..., description="Path to the recorded landmark .parquet file")
    ]
    frame_skip: int = Field(
        2, description="Skip every Nth frame during rendering (default: 2)"
    )
    render_mode: Literal["animation", "static", "preview"] = Field(
        "animation", description="Type of visualization to render"
    )
    save_format: Literal["gif", "mp4", "png"] = Field(
        "gif", description="File format for exported artifact"
    )


class LandmarkVisualizerOutput(BaseModel):
    success: bool = Field(..., description="True if rendering completed successfully")
    artifact_type: Literal["image", "animation"] = Field(
        ..., description="Type of rendered artifact"
    )
    artifact_path: Optional[str] = Field(
        None, description="Filesystem path to the exported image/video"
    )
    display_inline: Optional[bool] = Field(
        False, description="Whether to display artifact in UI"
    )
    notes: Optional[str] = Field(None, description="Log/debug notes or warnings")

    @staticmethod
    def example_input() -> dict:
        return {
            "session_id": "sess_20250709_e01",
            "user_id": "elias01",
            "modality": "vision",
            "parquet_path": "/data/recordings/elias01_2025-07-09.parquet",
            "frame_skip": 2,
            "render_mode": "animation",
            "save_format": "gif",
        }

    @staticmethod
    def example_output() -> dict:
        return {
            "success": True,
            "artifact_type": "animation",
            "artifact_path": "/tmp/visuals/elias01_2025-07-09.gif",
            "display_inline": True,
            "notes": "Rendered animation with 134 frames (skip=2)",
        }

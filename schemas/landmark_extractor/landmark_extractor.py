# schemas/landmark_extractor.py

"""
Schema for structured output of the landmark extraction stage using MediaPipe Holistic.

This model represents the complete set of spatial landmarks inferred from an RGB frame.
MediaPipe Holistic performs multi-stage inference: pose is detected first, followed by
region-of-interest refinement for face and hand crops. Each region is processed by a
dedicated model, and their outputs are merged into a unified landmark vector.

All coordinates are normalized to image dimensions, and `z`-values indicate approximate
depth (scale varies between body parts). `visibility` is only present for pose and hand
landmarks.
"""

from typing import Annotated, Dict, Literal

from pydantic import BaseModel, Field


class LandmarkPoint(BaseModel):
    x: float = Field(
        ..., description="Normalized x-coordinate (0.0–1.0), relative to image width"
    )
    y: float = Field(
        ..., description="Normalized y-coordinate (0.0–1.0), relative to image height"
    )
    z: float = Field(
        ..., description="Normalized z-depth; scale varies by landmark type"
    )
    visibility: float = Field(
        ..., description="Confidence score (0.0–1.0); only defined for pose and hands"
    )


class LandmarkVector(BaseModel):
    pose_landmarks: Dict[str, LandmarkPoint] = Field(
        default_factory=dict,
        description="Named pose keypoints (e.g., 'left_shoulder', 'right_knee') from the pose model",
    )
    left_hand_landmarks: Dict[str, LandmarkPoint] = Field(
        default_factory=dict,
        description="Named left-hand keypoints (e.g., 'thumb_tip', 'index_finger_mcp') from hand model",
    )
    right_hand_landmarks: Dict[str, LandmarkPoint] = Field(
        default_factory=dict,
        description="Named right-hand keypoints from hand model (e.g., 'thumb_tip')",
    )
    face_landmarks: Dict[str, LandmarkPoint] = Field(
        default_factory=dict,
        description="Named facial keypoints (e.g., 'nose_tip', 'left_eye') from face model",
    )


class LandmarkExtractorOutput(BaseModel):
    schema_version: Literal["1.0.0"] = Field("1.0.0", description="Schema version")
    timestamp: Annotated[str, Field(..., description="UTC timestamp of frame")]
    session_id: Annotated[str, Field(..., description="Session ID")]
    user_id: Annotated[str, Field(..., description="User ID")]
    frame_id: Annotated[str, Field(..., description="Unique ID for the video frame")]
    modality: Literal["vision"] = Field("vision", description="Sensor type")
    source: Literal["camera_feed_worker"] = Field(..., description="Source module")
    vector_version: str = Field(..., description="Feature vector schema version")
    landmarks: LandmarkVector = Field(
        ...,
        description=(
            "All extracted landmark sets for the current RGB frame. "
            "Includes pose, face, left hand, and right hand landmarks. "
            "Each set is inferred from a different model within the MediaPipe Holistic pipeline. "
            "Coordinates are normalized to frame size; z-depth and visibility vary by model."
        ),
    )

    @staticmethod
    def example_input() -> dict:
        return {
            "timestamp": "2025-07-09T13:14:15.123Z",
            "session_id": "sess_20250709_e01",
            "user_id": "elias01",
            "frame_id": "frame_000142",
            "modality": "vision",
            "source": "camera_feed_worker",
            "vector_version": "v1.0.0",
            "landmarks": {
                "pose_landmarks": {
                    "left_shoulder": {
                        "x": 0.42,
                        "y": 0.58,
                        "z": -0.1,
                        "visibility": 0.98,
                    },
                    "right_shoulder": {
                        "x": 0.58,
                        "y": 0.58,
                        "z": -0.1,
                        "visibility": 0.97,
                    },
                    "nose": {"x": 0.50, "y": 0.40, "z": -0.05, "visibility": 0.99},
                },
                "left_hand_landmarks": {
                    "thumb_tip": {"x": 0.48, "y": 0.52, "z": -0.05, "visibility": 0.95},
                    "index_finger_tip": {
                        "x": 0.50,
                        "y": 0.51,
                        "z": -0.04,
                        "visibility": 0.94,
                    },
                },
                "right_hand_landmarks": {
                    "thumb_tip": {"x": 0.62, "y": 0.52, "z": -0.05, "visibility": 0.95},
                    "index_finger_tip": {
                        "x": 0.60,
                        "y": 0.51,
                        "z": -0.04,
                        "visibility": 0.94,
                    },
                },
                "face_landmarks": {
                    "nose_tip": {"x": 0.50, "y": 0.42, "z": -0.02, "visibility": 0.0},
                    "left_eye": {"x": 0.46, "y": 0.40, "z": -0.01, "visibility": 0.0},
                    "right_eye": {"x": 0.54, "y": 0.40, "z": -0.01, "visibility": 0.0},
                },
            },
        }

    @staticmethod
    def example_output() -> dict:
        return LandmarkExtractorOutput.example_input()

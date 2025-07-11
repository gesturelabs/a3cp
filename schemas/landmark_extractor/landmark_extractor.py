# landmark_extractor Pydantic model
# schemas/landmark_extractor.py

from typing import Annotated, Dict, Literal

from pydantic import BaseModel, Field


class LandmarkPoint(BaseModel):
    x: float = Field(..., description="Normalized x-coordinate (0.0–1.0)")
    y: float = Field(..., description="Normalized y-coordinate (0.0–1.0)")
    z: float = Field(..., description="Normalized z-coordinate (depth, -1.0–1.0)")
    visibility: float = Field(..., description="Visibility or confidence (0.0–1.0)")


class LandmarkVector(BaseModel):
    pose_landmarks: Dict[str, LandmarkPoint] = Field(
        default_factory=dict,
        description="Named pose keypoints (e.g., 'left_shoulder', 'right_knee')",
    )
    left_hand_landmarks: Dict[str, LandmarkPoint] = Field(
        default_factory=dict,
        description="Named left-hand keypoints (e.g., 'thumb_tip', 'index_finger_mcp')",
    )
    right_hand_landmarks: Dict[str, LandmarkPoint] = Field(
        default_factory=dict, description="Named right-hand keypoints"
    )
    face_landmarks: Dict[str, LandmarkPoint] = Field(
        default_factory=dict,
        description="Named facial keypoints (e.g., 'nose_tip', 'left_eye')",
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
    landmarks: LandmarkVector = Field(..., description="All extracted landmark sets")

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
                    }
                },
                "left_hand_landmarks": {
                    "thumb_tip": {"x": 0.48, "y": 0.52, "z": -0.05, "visibility": 0.95}
                },
                "right_hand_landmarks": {},
                "face_landmarks": {},
            },
        }

    @staticmethod
    def example_output() -> dict:
        return LandmarkExtractorOutput.example_input()

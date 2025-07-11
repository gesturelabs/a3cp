# input_broker Pydantic model
# schemas/input_broker.py

from typing import Annotated, Dict, List, Literal, Union

from pydantic import BaseModel, Field


class AlignedClassifierMessage(BaseModel):
    """
    Minimal structure expected from any classifier module output (gesture, audio, speech).
    Additional fields are allowed and passed through unchanged.
    """

    modality: Literal["gesture", "audio", "speech"]
    timestamp: Annotated[
        str, Field(..., description="ISO8601 UTC timestamp of the classifier output")
    ]
    session_id: Annotated[
        str, Field(..., description="Session ID shared across modalities")
    ]
    user_id: Annotated[str, Field(..., description="User ID shared across modalities")]
    classifier_output: Annotated[
        Union[Dict[str, float], str],
        Field(
            ...,
            description="Prediction output from the classifier: confidence map or raw text",
        ),
    ]

    class Config:
        extra = "allow"  # allow per-modality extensions


class AlignedInputBundle(BaseModel):
    """
    A single temporally aligned group of classifier messages from multiple modalities.
    """

    schema_version: Literal["1.0.0"] = Field(
        default="1.0.0", description="Schema version"
    )

    stream_segment_id: Annotated[
        str, Field(..., description="Unique identifier for this aligned segment")
    ]
    timestamp: Annotated[
        str,
        Field(
            ..., description="Canonical time for the aligned segment (e.g., midpoint)"
        ),
    ]
    session_id: Annotated[
        str, Field(..., description="Session ID shared by all messages in the bundle")
    ]
    user_id: Annotated[
        str, Field(..., description="User ID shared by all messages in the bundle")
    ]

    aligned_messages: Annotated[
        List[AlignedClassifierMessage],
        Field(..., description="List of aligned outputs from different modalities"),
    ]

    @staticmethod
    def example_input() -> dict:
        return {
            "schema_version": "1.0.0",
            "stream_segment_id": "seg_20250709T120001Z",
            "timestamp": "2025-07-09T12:00:01.110Z",
            "session_id": "sess_20250709_e01",
            "user_id": "elias01",
            "aligned_messages": [
                {
                    "modality": "gesture",
                    "timestamp": "2025-07-09T12:00:01.120Z",
                    "session_id": "sess_20250709_e01",
                    "user_id": "elias01",
                    "classifier_output": {"play": 0.6, "eat": 0.4},
                    "vector_version": "v1.2",
                },
                {
                    "modality": "audio",
                    "timestamp": "2025-07-09T12:00:01.110Z",
                    "session_id": "sess_20250709_e01",
                    "user_id": "elias01",
                    "classifier_output": {"play": 0.7, "sleep": 0.3},
                },
                {
                    "modality": "speech",
                    "timestamp": "2025-07-09T12:00:01.100Z",
                    "session_id": "sess_20250709_e01",
                    "user_id": "elias01",
                    "classifier_output": "I want to play outside",
                },
            ],
        }

    @staticmethod
    def example_output() -> dict:
        return {
            "schema_version": "1.0.0",
            "stream_segment_id": "seg_20250709T120001Z",
            "timestamp": "2025-07-09T12:00:01.110Z",
            "session_id": "sess_20250709_e01",
            "user_id": "elias01",
            "aligned_messages": [
                {
                    "modality": "gesture",
                    "timestamp": "2025-07-09T12:00:01.120Z",
                    "session_id": "sess_20250709_e01",
                    "user_id": "elias01",
                    "classifier_output": {"play": 0.6, "eat": 0.4},
                    "vector_version": "v1.2",
                },
                {
                    "modality": "audio",
                    "timestamp": "2025-07-09T12:00:01.110Z",
                    "session_id": "sess_20250709_e01",
                    "user_id": "elias01",
                    "classifier_output": {"play": 0.7, "sleep": 0.3},
                },
                {
                    "modality": "speech",
                    "timestamp": "2025-07-09T12:00:01.100Z",
                    "session_id": "sess_20250709_e01",
                    "user_id": "elias01",
                    "classifier_output": "I want to play outside",
                },
            ],
        }

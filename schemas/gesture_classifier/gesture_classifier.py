# schemas/gesture_classifier.py

from typing import Annotated, Dict, Literal, Optional

from pydantic import BaseModel, Field


class FileReference(BaseModel):
    uri: Annotated[
        str,
        Field(
            ..., description="Path or URI to model or encoder file (e.g., .h5, .pkl)"
        ),
    ]
    hash: Annotated[str, Field(..., description="SHA-256 hash of the referenced file")]
    version: Annotated[
        str, Field(..., description="Semantic or internal version string")
    ]
    type: Annotated[
        Literal["model", "encoder"],
        Field(..., description="Type of reference (model or encoder)"),
    ]


class RawFeaturesRef(BaseModel):
    uri: Annotated[
        str,
        Field(
            ...,
            description="Path to stored landmark time series (e.g., .parquet or .npy)",
        ),
    ]
    hash: Annotated[
        str, Field(..., description="SHA-256 content hash for file integrity")
    ]
    encoding: Annotated[
        str,
        Field(
            ..., description="Landmark encoding spec used (e.g., mediapipe_pose_v1.2)"
        ),
    ]
    dims: Annotated[
        int, Field(..., description="Total dimensionality of the landmark vector")
    ]
    format: Annotated[
        Literal["parquet", "npy"],
        Field(..., description="Storage format of landmark series"),
    ]


class GestureClassifierInput(BaseModel):
    schema_version: Literal["1.0.0"] = Field(
        default="1.0.0", description="Schema version"
    )

    record_id: Annotated[str, Field(..., description="UUID for this message")]
    user_id: Annotated[str, Field(..., description="Pseudonymous user ID")]
    session_id: Annotated[str, Field(..., description="Session identifier")]
    timestamp: Annotated[str, Field(..., description="UTC ISO8601 timestamp")]

    # modality omitted because always fixed to 'gesture' at API level

    raw_features_ref: Annotated[
        RawFeaturesRef, Field(..., description="Reference to stored gesture landmarks")
    ]
    vector_version: Optional[str] = Field(
        default=None, description="Version of preprocessing pipeline used"
    )

    model_ref: Annotated[
        FileReference, Field(..., description="Reference to model.h5 artifact to use")
    ]
    encoder_ref: Annotated[
        FileReference,
        Field(..., description="Reference to encoder.pkl artifact to use"),
    ]

    @staticmethod
    def example_input() -> dict:
        return {
            "schema_version": "1.0.0",
            "record_id": "5dcac6f8-51f9-4478-b601-dfa57eb9cacf",
            "user_id": "anon_user_17",
            "session_id": "sess_20250709T114300Z",
            "timestamp": "2025-07-09T11:43:00Z",
            "raw_features_ref": {
                "uri": "file://data/landmarks/anon_user_17/20250709_114300_pose.parquet",
                "hash": "ce4f8f85b4dfb630f55e9bb27e3a04db1f9dc3d1947e86a2bc0f0d19074cf1ae",
                "encoding": "mediapipe_pose_v1.2",
                "dims": 225,
                "format": "parquet",
            },
            "vector_version": "landmark_preproc_v1.2.0",
            "model_ref": {
                "uri": "registry://models/anon_user_17/gesture_lstm_v1.4.h5",
                "hash": "44b3942e617eaaf82e39f61e0c2ebac969f71e79b1be74bc51e6b39d607d0b1c",
                "version": "1.4.0",
                "type": "model",
            },
            "encoder_ref": {
                "uri": "registry://encoders/anon_user_17/gesture_encoder_v1.pkl",
                "hash": "9a488d967b47b770a5d4731876c96d5a0c278a776ddfbbaf05cc64d649b93e64",
                "version": "1.0.0",
                "type": "encoder",
            },
        }


class GestureClassifierOutput(BaseModel):
    schema_version: Literal["1.0.0"] = Field(
        default="1.0.0", description="Schema version"
    )

    record_id: Annotated[str, Field(..., description="Copied from input")]
    user_id: Annotated[str, Field(..., description="Copied from input")]
    session_id: Annotated[str, Field(..., description="Copied from input")]
    timestamp: Annotated[
        str, Field(..., description="UTC ISO8601 timestamp of prediction")
    ]

    classifier_output: Annotated[
        Dict[str, Annotated[float, Field(ge=0.0, le=1.0)]],
        Field(..., description="Map of intent label to confidence score (0.0–1.0)"),
    ]

    model_ref: Annotated[
        FileReference, Field(..., description="Reference to model.h5 artifact used")
    ]
    encoder_ref: Annotated[
        FileReference, Field(..., description="Reference to encoder.pkl artifact used")
    ]

    @staticmethod
    def example_output() -> dict:
        return {
            "schema_version": "1.0.0",
            "record_id": "5dcac6f8-51f9-4478-b601-dfa57eb9cacf",
            "user_id": "anon_user_17",
            "session_id": "sess_20250709T114300Z",
            "timestamp": "2025-07-09T11:43:01Z",
            "classifier_output": {"go_outside": 0.84, "hungry": 0.12, "neutral": 0.04},
            "model_ref": {
                "uri": "registry://models/anon_user_17/gesture_lstm_v1.4.h5",
                "hash": "44b3942e617eaaf82e39f61e0c2ebac969f71e79b1be74bc51e6b39d607d0b1c",
                "version": "1.4.0",
                "type": "model",
            },
            "encoder_ref": {
                "uri": "registry://encoders/anon_user_17/gesture_encoder_v1.pkl",
                "hash": "9a488d967b47b770a5d4731876c96d5a0c278a776ddfbbaf05cc64d649b93e64",
                "version": "1.0.0",
                "type": "encoder",
            },
        }

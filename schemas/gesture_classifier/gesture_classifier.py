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

# gesture_classifier Pydantic model

# schemas/gesture_classifier.py

from typing import Annotated, Dict, Literal, Optional

from pydantic import BaseModel, Field

# -------------------------
# FileReference: metadata for any model or encoder file
# -------------------------
# This structure captures essential details for reproducibility and auditing:
# - URI to the file (e.g., .h5 for models, .pkl for encoders)
# - SHA-256 hash for integrity checking
# - Semantic version string (e.g., "1.0.0", "v2.3-r45")
# - Type: must be "model" or "encoder" (case-sensitive)


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


# -------------------------
# RawFeaturesRef: pointer to extracted input features
# -------------------------
# This object links to the external feature vector used as input to the classifier.
# - URI: file path (e.g., a .parquet or .npy file)
# - hash: for audit integrity
# - encoding: e.g., "landmark_v2.1"
# - dims: vector dimensionality
# - format: storage format


class RawFeaturesRef(BaseModel):
    uri: Annotated[
        str,
        Field(..., description="Path to external feature vector file (e.g., .parquet)"),
    ]
    hash: Annotated[
        str, Field(..., description="SHA-256 content hash for file integrity")
    ]
    encoding: Annotated[
        str,
        Field(..., description="Encoder type and version used (e.g., landmark_v2.1)"),
    ]
    dims: Annotated[int, Field(..., description="Dimensionality of the feature vector")]
    format: Annotated[str, Field(..., description="File format: parquet, npy, etc.")]


# -------------------------
# GestureClassifierInput: full input payload to gesture classifier
# -------------------------
# Includes metadata, raw features, and explicit model + encoder references.


class GestureClassifierInput(BaseModel):
    schema_version: Literal["1.0.0"] = Field(default="1.0.0", frozen=True)

    # Core metadata
    record_id: Annotated[str, Field(..., description="UUID for this message")]
    user_id: Annotated[str, Field(..., description="Pseudonymous user ID")]
    session_id: Annotated[str, Field(..., description="Session identifier")]
    timestamp: Annotated[str, Field(..., description="UTC ISO8601 timestamp")]

    # Input metadata
    modality: Literal["gesture"]
    source: Literal["communicator", "caregiver", "system"]

    # Optional context
    context_location: Optional[str] = None
    context_prompt_type: Optional[Literal["prompted", "natural_use", "other"]] = None
    context_partner_speech: Optional[str] = None

    # Gesture input
    raw_features_ref: Annotated[
        RawFeaturesRef, Field(..., description="Pointer to gesture vector")
    ]
    vector_version: Optional[str] = None

    # Model & encoder needed for classification
    model_ref: Annotated[
        FileReference, Field(..., description="Reference to model.h5 artifact to use")
    ]
    encoder_ref: Annotated[
        FileReference,
        Field(..., description="Reference to encoder.pkl artifact to use"),
    ]


# -------------------------
# GestureClassifierOutput: prediction and traceability info
# -------------------------
# Carries model predictions and confirms exactly which artifacts were used.


class GestureClassifierOutput(BaseModel):
    schema_version: Literal["1.0.0"] = Field(default="1.0.0", frozen=True)

    # Core metadata
    record_id: Annotated[str, Field(..., description="Copied from input")]
    user_id: Annotated[str, Field(..., description="Copied from input")]
    session_id: Annotated[str, Field(..., description="Copied from input")]
    timestamp: Annotated[
        str, Field(..., description="UTC ISO8601 timestamp of prediction")
    ]

    # Prediction output
    classifier_output: Annotated[
        Dict[str, float],
        Field(..., description="Map of intent label to confidence score (0.0–1.0)"),
    ]

    # Model artifacts used
    model_ref: Annotated[
        FileReference, Field(..., description="Reference to model.h5 artifact used")
    ]
    encoder_ref: Annotated[
        FileReference, Field(..., description="Reference to encoder.pkl artifact used")
    ]

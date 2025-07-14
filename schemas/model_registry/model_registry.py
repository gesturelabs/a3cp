# model_registry Pydantic model
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ModelRegistryEntry(BaseModel):
    user_id: str = Field(
        ..., description="Pseudonymous user ID for whom the model was trained"
    )
    modality: str = Field(
        ..., description='Modality of model input, e.g., "gesture", "sound", "speech"'
    )
    vector_version: str = Field(
        ..., description="Version of feature encoding (e.g., 'v2.1')"
    )
    timestamp: datetime = Field(
        ..., description="UTC ISO 8601 timestamp of training completion"
    )
    config: Dict[str, Any] = Field(
        ..., description="Training configuration and hyperparameters"
    )
    model_artifact_path: str = Field(
        ..., description="Path or URI to saved model artifact (.pkl, .h5, etc.)"
    )
    schema_version: str = Field(
        ..., description="Schema version used to validate this entry"
    )
    model_version: Optional[str] = Field(
        default=None,
        description="Optional hash, UUID, or label identifying this model version",
    )

    @staticmethod
    def example_input() -> dict:
        return {
            "user_id": "elias01",
            "modality": "gesture",
            "vector_version": "v2.1",
            "timestamp": "2025-07-14T15:45:00.000Z",
            "config": {
                "model_type": "RandomForest",
                "num_trees": 100,
                "input_dim": 128,
                "epochs": 10,
            },
            "model_artifact_path": "/models/elias01_gesture_v2.1.pkl",
            "schema_version": "1.0.0",
            "model_version": "model_20250714_154500_e01",
        }

    @staticmethod
    def example_output() -> dict:
        return ModelRegistryEntry.example_input()

from datetime import datetime
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field


class TrainingRequest(BaseModel):
    user_id: str = Field(..., description="Pseudonymous user ID for training")
    modality: str = Field(
        ..., description='Modality of model (e.g., "gesture", "sound", "speech")'
    )
    training_config: Dict[str, Any] = Field(
        ..., description="Hyperparameters and model configuration"
    )

    @staticmethod
    def example_input() -> dict:
        return {
            "user_id": "elias01",
            "modality": "gesture",
            "training_config": {
                "model_type": "RandomForest",
                "num_trees": 100,
                "input_dim": 128,
                "epochs": 10,
            },
        }


class TrainingLogEntry(BaseModel):
    user_id: str = Field(..., description="User ID for whom the model was trained")
    modality: str = Field(..., description="Modality of trained model")
    timestamp: datetime = Field(
        ..., description="Timestamp of training completion (UTC)"
    )
    sample_count: int = Field(..., description="Number of training samples used")
    training_config: Dict[str, Any] = Field(
        ..., description="Configuration used during training"
    )
    training_metrics: Optional[Dict[str, float]] = Field(
        default=None, description="Training metrics such as accuracy, loss, F1"
    )
    status: Literal["success", "failure", "partial"] = Field(
        ..., description="Outcome of training process"
    )
    error_trace: Optional[str] = Field(
        default=None, description="Error trace if training failed or was incomplete"
    )
    model_artifact_path: str = Field(
        ..., description="Path to saved trained model file"
    )
    label_encoder_path: str = Field(..., description="Path to saved label encoder file")
    model_version: Optional[str] = Field(
        default=None, description="Optional model version string or UUID"
    )
    schema_version: str = Field(
        ..., description="Schema version used for this log entry"
    )

    @staticmethod
    def example_output() -> dict:
        return {
            "user_id": "elias01",
            "modality": "gesture",
            "timestamp": "2025-07-14T16:20:00.000Z",
            "sample_count": 936,
            "training_config": {
                "model_type": "RandomForest",
                "num_trees": 100,
                "input_dim": 128,
                "epochs": 10,
            },
            "training_metrics": {"accuracy": 0.91, "f1_macro": 0.89},
            "status": "success",
            "error_trace": None,
            "model_artifact_path": "/models/elias01_gesture_v2.pkl",
            "label_encoder_path": "/models/elias01_encoder_v2.pkl",
            "model_version": "model_20250714_162000_e01",
            "schema_version": "1.0.0",
        }

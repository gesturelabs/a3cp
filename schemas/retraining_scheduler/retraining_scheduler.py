# retraining_scheduler Pydantic model
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class RetrainingTriggerMetadata(BaseModel):
    trigger_reason: str = Field(
        ...,
        description="Human-readable explanation of why retraining was triggered (e.g., 'New sample threshold exceeded')",
    )
    num_new_samples: Optional[int] = Field(
        None,
        description="Number of new recorded schema entries since the last model version",
    )
    clarification_rate: Optional[float] = Field(
        None,
        description="Observed clarification frequency since last training (e.g., 0.23)",
    )
    correction_rate: Optional[float] = Field(
        None, description="Proportion of corrected labels in feedback log, if available"
    )
    model_version_before: Optional[str] = Field(
        None,
        description="Latest known model version prior to retraining (e.g., 'gesture-elias01-20250701')",
    )
    policy_config_version: str = Field(
        ..., description="Version of the retraining policy configuration applied"
    )


class RetrainingRequest(BaseModel):
    user_id: str = Field(..., description="Pseudonymous user identifier")
    modality: Literal["gesture", "audio", "speech", "image"] = Field(
        ..., description="Modality for which the model should be retrained"
    )
    timestamp: datetime = Field(
        ..., description="Time when the retraining was triggered (UTC ISO 8601)"
    )
    retrain_reason: str = Field(
        ..., description="Short string label for why retraining is triggered"
    )
    latest_model_version: Optional[str] = Field(
        None, description="Model version before retraining, if known"
    )
    policy_config_version: str = Field(
        ..., description="Version of the retraining policy applied"
    )

    @staticmethod
    def example_request() -> dict:
        return {
            "user_id": "elias01",
            "modality": "gesture",
            "timestamp": "2025-07-18T11:30:00.000Z",
            "retrain_reason": "High clarification rate (0.23 > 0.15)",
            "latest_model_version": "gesture-elias01-20250701",
            "policy_config_version": "v1.0.0",
        }


class RetrainingDecisionLog(BaseModel):
    user_id: str = Field(..., description="User for whom retraining was triggered")
    modality: Literal["gesture", "audio", "speech", "image"] = Field(
        ..., description="Modality of the model retrained"
    )
    timestamp: datetime = Field(..., description="When retraining was triggered")
    trigger: RetrainingTriggerMetadata = Field(
        ..., description="Detailed policy metrics and justification"
    )

    @staticmethod
    def example_log() -> dict:
        return {
            "user_id": "elias01",
            "modality": "gesture",
            "timestamp": "2025-07-18T11:30:00.000Z",
            "trigger": {
                "trigger_reason": "High clarification rate (0.23 > 0.15)",
                "num_new_samples": 47,
                "clarification_rate": 0.23,
                "correction_rate": 0.12,
                "model_version_before": "gesture-elias01-20250701",
                "policy_config_version": "v1.0.0",
            },
        }

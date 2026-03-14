# apps/landmark_extractor/artifact_writer.py

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from apps.landmark_extractor.domain import FeatureMatrix


@dataclass(frozen=True)
class ArtifactWriteResult:
    """
    Result returned by write_feature_artifact().
    """

    capture_id: UUID
    artifact_path: str
    artifact_hash: str
    shape: tuple[int, int]
    dtype: str
    format: str


def write_feature_artifact(
    *,
    user_id: str,
    session_id: str,
    capture_id: UUID,
    feature_matrix: FeatureMatrix,
) -> ArtifactWriteResult:
    """
    Write the feature artifact for one completed capture.

    This is a placeholder skeleton. Implementation will be added later.
    """
    raise NotImplementedError("write_feature_artifact is not implemented yet.")


def delete_feature_artifact(*, artifact_path: str) -> None:
    """
    Delete a previously written artifact.

    Used for commit-unit rollback if event append fails.
    """
    raise NotImplementedError("delete_feature_artifact is not implemented yet.")

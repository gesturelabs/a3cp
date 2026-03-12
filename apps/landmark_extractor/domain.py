# apps/landmark_extractor/domain.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeAlias
from uuid import UUID

FeatureRow: TypeAlias = list[float]
FeatureRows: TypeAlias = list[FeatureRow]
FeatureMatrix: TypeAlias = list[FeatureRow]


@dataclass
class CaptureState:
    """
    In-memory buffered state for one active bounded capture.

    Invariants:
    - keyed by capture_id in the service layer
    - stores extracted feature rows only
    - never stores raw frames
    - rows are buffered in frame arrival order
    - seq is not stored or validated here
    """

    capture_id: UUID
    user_id: str
    session_id: str
    feature_rows: FeatureRows = field(default_factory=list)


@dataclass
class FinalizeResult:
    """
    Pure internal finalization structure returned to the service layer, if needed.

    Represents the ordered buffered rows for one completed capture before
    artifact writing and event construction.
    """

    capture_id: UUID
    user_id: str
    session_id: str
    feature_matrix: FeatureMatrix

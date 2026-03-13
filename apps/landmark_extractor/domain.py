# apps/landmark_extractor/domain.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeAlias
from uuid import UUID

FeatureRow: TypeAlias = list[float]
FeatureRows: TypeAlias = list[FeatureRow]
FeatureMatrix: TypeAlias = FeatureRows


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


LandmarkXY: TypeAlias = tuple[float, float]
LandmarkMap: TypeAlias = dict[int, LandmarkXY]


@dataclass(frozen=True)
class NormalizedLandmarks:
    """
    MediaPipe output normalized into module-internal landmark maps.

    Invariants:
    - contains only normalized 2D coordinates (x, y)
    - keys are MediaPipe landmark indices
    - absent keys mean landmark not returned by MediaPipe
    - no missing-landmark fill is applied here
    - no raw MediaPipe objects are retained
    - left_hand and right_hand represent handedness-resolved hand outputs
    """

    pose: LandmarkMap = field(default_factory=dict)
    left_hand: LandmarkMap = field(default_factory=dict)
    right_hand: LandmarkMap = field(default_factory=dict)
    face: LandmarkMap = field(default_factory=dict)

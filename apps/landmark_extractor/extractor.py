# apps/landmark_extractor/extractor.py

from __future__ import annotations

from apps.landmark_extractor.config import (
    FEATURE_DIM,
    MISSING_LANDMARK_PAIR,
    ORDERED_LANDMARKS,
)
from apps.landmark_extractor.domain import FeatureRow, LandmarkMap, NormalizedLandmarks


def build_feature_row(landmarks: NormalizedLandmarks) -> FeatureRow:
    """
    Convert normalized landmark maps into one deterministic fixed-length feature row.

    Contract:
    - input is NormalizedLandmarks
    - output ordering matches ORDERED_LANDMARKS exactly
    - each configured landmark contributes exactly one (x, y) pair
    - missing landmarks are filled with MISSING_LANDMARK_PAIR
    - output length is exactly FEATURE_DIM
    """
    feature_row: FeatureRow = []

    for region, landmark_index in ORDERED_LANDMARKS:
        xy = _resolve_landmark_xy(landmarks, region, landmark_index)
        feature_row.extend(xy)

    if len(feature_row) != FEATURE_DIM:
        raise ValueError(
            f"Feature row length mismatch: expected {FEATURE_DIM}, got {len(feature_row)}"
        )

    return feature_row


def _resolve_landmark_xy(
    landmarks: NormalizedLandmarks,
    region: str,
    landmark_index: int,
) -> tuple[float, float]:
    """
    Resolve one configured landmark from the corresponding landmark map.

    Returns:
    - the normalized (x, y) pair if present
    - MISSING_LANDMARK_PAIR if absent
    """
    landmark_map = _get_landmark_map(landmarks, region)
    return landmark_map.get(landmark_index, _missing_landmark_pair())


def _get_landmark_map(
    landmarks: NormalizedLandmarks,
    region: str,
) -> LandmarkMap:
    """
    Return the normalized landmark map for one configured region.
    """
    if region == "pose":
        return landmarks.pose
    if region == "left_hand":
        return landmarks.left_hand
    if region == "right_hand":
        return landmarks.right_hand
    if region == "face":
        return landmarks.face

    raise ValueError(f"Unsupported landmark region: {region}")


def _missing_landmark_pair() -> tuple[float, float]:
    """
    Return the configured missing-landmark fill pair.
    """
    return MISSING_LANDMARK_PAIR

# apps/landmark_extractor/tests/test_extractor.py

from apps.landmark_extractor.config import (
    FEATURE_DIM,
    MISSING_LANDMARK_PAIR,
    ORDERED_LANDMARKS,
)
from apps.landmark_extractor.domain import NormalizedLandmarks
from apps.landmark_extractor.extractor import build_feature_row


def test_build_feature_row_returns_fixed_length_row():
    landmarks = NormalizedLandmarks()

    feature_row = build_feature_row(landmarks)

    assert isinstance(feature_row, list)
    assert len(feature_row) == FEATURE_DIM


def test_build_feature_row_preserves_configured_order():
    # Create landmarks with distinct values so ordering can be verified
    pose = {0: (0.1, 0.2)}
    left_hand = {0: (1.1, 1.2)}
    right_hand = {0: (2.1, 2.2)}
    face = {ORDERED_LANDMARKS[-1][1]: (3.1, 3.2)}

    landmarks = NormalizedLandmarks(
        pose=pose,
        left_hand=left_hand,
        right_hand=right_hand,
        face=face,
    )

    feature_row = build_feature_row(landmarks)

    # Find the first occurrence of each configured landmark
    # and verify its flattened values appear in the correct order
    expected_sequence = []

    for region, idx in ORDERED_LANDMARKS:
        if region == "pose" and idx in pose:
            expected_sequence.extend(pose[idx])
        elif region == "left_hand" and idx in left_hand:
            expected_sequence.extend(left_hand[idx])
        elif region == "right_hand" and idx in right_hand:
            expected_sequence.extend(right_hand[idx])
        elif region == "face" and idx in face:
            expected_sequence.extend(face[idx])

    # The expected sequence should appear in the feature row in order
    cursor = 0
    for value in expected_sequence:
        cursor = feature_row.index(value, cursor)
        cursor += 1


def test_build_feature_row_fills_missing_landmarks():
    # Only one landmark present; the rest should be filled with missing values
    landmarks = NormalizedLandmarks(pose={0: (0.5, 0.6)})

    feature_row = build_feature_row(landmarks)

    missing_x, missing_y = MISSING_LANDMARK_PAIR

    missing_count = 0
    for i in range(0, FEATURE_DIM, 2):
        x, y = feature_row[i], feature_row[i + 1]
        if (x, y) == (missing_x, missing_y):
            missing_count += 1

    # At least one configured landmark should have been filled as missing
    assert missing_count > 0


def test_build_feature_row_all_missing_returns_only_missing_pairs():
    landmarks = NormalizedLandmarks()

    feature_row = build_feature_row(landmarks)

    missing_x, missing_y = MISSING_LANDMARK_PAIR

    for i in range(0, FEATURE_DIM, 2):
        assert feature_row[i] == missing_x
        assert feature_row[i + 1] == missing_y

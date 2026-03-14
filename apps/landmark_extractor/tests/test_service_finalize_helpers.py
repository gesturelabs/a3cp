# apps/landmark_extractor/tests/test_service_finalize_helpers.py

from datetime import datetime, timezone
from uuid import uuid4

import pytest

import apps.landmark_extractor.service as service
from apps.landmark_extractor.config import FEATURE_DIM


# test_build_finalize_result_returns_finalize_result_for_buffered_rows
def test_build_finalize_result_returns_finalize_result_for_buffered_rows():
    capture_id = uuid4()

    state = service.CaptureState(
        capture_id=capture_id,
        user_id="user-1",
        session_id="session-1",
        feature_rows=[[0.0] * FEATURE_DIM for _ in range(3)],
    )

    result = service._build_finalize_result(state=state)

    assert result.capture_id == capture_id
    assert result.feature_matrix == state.feature_rows


# test_build_finalize_result_raises_for_zero_rows
def test_build_finalize_result_raises_for_zero_rows():
    capture_id = uuid4()

    state = service.CaptureState(
        capture_id=capture_id,
        user_id="user-1",
        session_id="session-1",
        feature_rows=[],
    )

    with pytest.raises(service.LandmarkExtractorFinalizeError):
        service._build_finalize_result(state=state)


# test_build_feature_ref_message_builds_valid_a3cp_message


def test_build_feature_ref_message_builds_valid_a3cp_message():
    capture_id = uuid4()
    now = datetime.now(timezone.utc)

    artifact_result = service.ArtifactWriteResult(
        capture_id=capture_id,
        artifact_path="/tmp/test_artifact.npz",
        artifact_hash="sha256:abc123",
        shape=(3, FEATURE_DIM),
        dtype="float32",
        format="npz",
    )

    message = service._build_feature_ref_message(
        finalize_result=service._build_finalize_result(
            state=service.CaptureState(
                capture_id=capture_id,
                user_id="user-1",
                session_id="session-1",
                feature_rows=[[0.0] * FEATURE_DIM for _ in range(3)],
            )
        ),
        artifact_result=artifact_result,
        timestamp_end=now,
        schema_version="1.0.1",
    )

    assert message.capture_id == capture_id
    assert message.raw_features_ref is not None
    assert message.raw_features_ref.uri.endswith(".npz")
    assert message.raw_features_ref.hash.startswith("sha256:")
    assert message.raw_features_ref.format == "npz"


# test_ensure_feature_matrix_shape_accepts_valid_rows
def test_ensure_feature_matrix_shape_accepts_valid_rows():
    rows = [[0.0] * FEATURE_DIM for _ in range(5)]

    # Should not raise
    service._ensure_feature_matrix_shape(rows)


# test_ensure_feature_matrix_shape_raises_for_empty_matrix
def test_ensure_feature_matrix_shape_raises_for_empty_matrix():
    with pytest.raises(
        service.LandmarkExtractorFinalizeError, match="Feature matrix is empty"
    ):
        service._ensure_feature_matrix_shape([])


# test_ensure_feature_matrix_shape_raises_for_row_dim_mismatch
def test_ensure_feature_matrix_shape_raises_for_row_dim_mismatch():
    rows = [
        [0.0] * FEATURE_DIM,
        [0.0] * (FEATURE_DIM - 1),  # incorrect dimension
    ]

    with pytest.raises(service.LandmarkExtractorFinalizeError):
        service._ensure_feature_matrix_shape(rows)

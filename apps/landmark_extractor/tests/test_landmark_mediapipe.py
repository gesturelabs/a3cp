# apps/landmark_extractor/tests/test_landmark_mediapipe.py

from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pytest

from apps.landmark_extractor.domain import NormalizedLandmarks
from apps.landmark_extractor.landmark_mediapipe import (
    MediaPipeBackendInitError,
    MediaPipeExtractionError,
    MediaPipeLandmarkBackend,
)


def test_mediapipe_backend_runs_one_frame():
    backend = MediaPipeLandmarkBackend(
        pose_model_path="models/mediapipe/pose_landmarker.task",
        hand_model_path="models/mediapipe/hand_landmarker.task",
        face_model_path="models/mediapipe/face_landmarker.task",
    )

    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    timestamp_frame = datetime.now(timezone.utc)

    result = backend.extract_landmarks(frame, timestamp_frame)

    assert isinstance(result, NormalizedLandmarks)
    assert isinstance(result.pose, dict)
    assert isinstance(result.left_hand, dict)
    assert isinstance(result.right_hand, dict)
    assert isinstance(result.face, dict)


def test_mediapipe_backend_rejects_none_frame():
    backend = MediaPipeLandmarkBackend(
        pose_model_path="models/mediapipe/pose_landmarker.task",
        hand_model_path="models/mediapipe/hand_landmarker.task",
        face_model_path="models/mediapipe/face_landmarker.task",
    )

    timestamp_frame = datetime.now(timezone.utc)

    with pytest.raises(MediaPipeExtractionError):
        backend.extract_landmarks(None, timestamp_frame)


def test_mediapipe_backend_raises_init_error_for_missing_model_files():
    missing = Path("models/mediapipe/does_not_exist.task")

    with pytest.raises(MediaPipeBackendInitError):
        MediaPipeLandmarkBackend(
            pose_model_path=missing,
            hand_model_path=missing,
            face_model_path=missing,
        )


def test_mediapipe_backend_returns_xy_pairs_only():
    backend = MediaPipeLandmarkBackend(
        pose_model_path="models/mediapipe/pose_landmarker.task",
        hand_model_path="models/mediapipe/hand_landmarker.task",
        face_model_path="models/mediapipe/face_landmarker.task",
    )

    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    ts = datetime.now(timezone.utc)

    result = backend.extract_landmarks(frame, ts)

    for landmark_map in (
        result.pose,
        result.left_hand,
        result.right_hand,
        result.face,
    ):
        for idx, value in landmark_map.items():
            assert isinstance(idx, int)
            assert isinstance(value, tuple)
            assert len(value) == 2
            assert all(isinstance(v, float) for v in value)

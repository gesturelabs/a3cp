# apps/landmark_extractor/landmark_mediapipe.py

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import cv2
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    FaceLandmarker,
    FaceLandmarkerOptions,
    HandLandmarker,
    HandLandmarkerOptions,
    PoseLandmarker,
    PoseLandmarkerOptions,
    RunningMode,
)

from apps.landmark_extractor.config import (
    FACE_MAX_NUM_FACES,
    HAND_MAX_NUM_HANDS,
    MEDIAPIPE_RUNNING_MODE,
    POSE_MAX_RESULTS,
)
from apps.landmark_extractor.domain import LandmarkMap, NormalizedLandmarks


class MediaPipeBackendError(Exception):
    """Base exception for MediaPipe backend failures."""


class MediaPipeBackendInitError(MediaPipeBackendError):
    """Raised when detector initialization fails."""


class MediaPipeExtractionError(MediaPipeBackendError):
    """Raised when landmark extraction fails."""


class MediaPipeLandmarkBackend:
    """
    Reusable MediaPipe Tasks adapter for landmark extraction.

    Responsibilities:
    - initialize detectors once
    - run detectors in VIDEO mode
    - normalize outputs into module-internal landmark maps
    - expose no raw MediaPipe result objects outside this file
    """

    def __init__(
        self,
        pose_model_path: str | Path,
        hand_model_path: str | Path,
        face_model_path: str | Path,
    ) -> None:
        self._pose_model_path = Path(pose_model_path)
        self._hand_model_path = Path(hand_model_path)
        self._face_model_path = Path(face_model_path)

        try:
            running_mode = getattr(RunningMode, str(MEDIAPIPE_RUNNING_MODE).upper())

            pose_options = PoseLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=str(self._pose_model_path)),
                running_mode=running_mode,
                num_poses=POSE_MAX_RESULTS,
            )

            hand_options = HandLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=str(self._hand_model_path)),
                running_mode=running_mode,
                num_hands=HAND_MAX_NUM_HANDS,
            )

            face_options = FaceLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=str(self._face_model_path)),
                running_mode=running_mode,
                num_faces=FACE_MAX_NUM_FACES,
            )

            self._pose_landmarker = PoseLandmarker.create_from_options(pose_options)
            self._hand_landmarker = HandLandmarker.create_from_options(hand_options)
            self._face_landmarker = FaceLandmarker.create_from_options(face_options)

        except Exception as exc:
            raise MediaPipeBackendInitError(
                "Failed to initialize MediaPipe Tasks landmark detectors."
            ) from exc

    def extract_landmarks(
        self,
        frame: Any,
        timestamp_frame: datetime,
    ) -> NormalizedLandmarks:
        """
        Run MediaPipe Tasks detectors on one decoded frame.

        Args:
            frame:
                Decoded BGR image frame.
            timestamp_frame:
                Frame timestamp used to derive MediaPipe VIDEO-mode timestamp_ms.

        Returns:
            NormalizedLandmarks containing normalized (x, y) only.
        """
        if frame is None:
            raise MediaPipeExtractionError("frame must not be None")

        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            timestamp_ms = self._to_timestamp_ms(timestamp_frame)

            pose_result = self._pose_landmarker.detect_for_video(mp_image, timestamp_ms)
            hand_result = self._hand_landmarker.detect_for_video(mp_image, timestamp_ms)
            face_result = self._face_landmarker.detect_for_video(mp_image, timestamp_ms)

            pose_landmarks = self._extract_pose_landmarks(pose_result)
            left_hand_landmarks, right_hand_landmarks = self._extract_hand_landmarks(
                hand_result
            )
            face_landmarks = self._extract_face_landmarks(face_result)

            return NormalizedLandmarks(
                pose=pose_landmarks,
                left_hand=left_hand_landmarks,
                right_hand=right_hand_landmarks,
                face=face_landmarks,
            )
        except MediaPipeBackendError:
            raise
        except Exception as exc:
            raise MediaPipeExtractionError(
                "Failed to extract landmarks from frame."
            ) from exc

    def _get_running_mode(self) -> Any:
        """
        Resolve configured running mode to MediaPipe enum.
        """
        try:
            return getattr(
                mp.tasks.vision.RunningMode,
                str(MEDIAPIPE_RUNNING_MODE).upper(),
            )
        except AttributeError as exc:
            raise MediaPipeBackendInitError(
                f"Unsupported MediaPipe running mode: {MEDIAPIPE_RUNNING_MODE!r}"
            ) from exc

    def _to_timestamp_ms(self, timestamp_frame: datetime) -> int:
        """
        Convert frame timestamp to integer milliseconds for VIDEO mode.
        """
        if not isinstance(timestamp_frame, datetime):
            raise MediaPipeExtractionError(
                "timestamp_frame must be a datetime instance"
            )

        return int(timestamp_frame.timestamp() * 1000)

    def _extract_pose_landmarks(self, pose_result: Any) -> LandmarkMap:
        """
        Extract first detected pose into a normalized landmark map.
        """
        pose_landmark_sets = getattr(pose_result, "pose_landmarks", None)
        if not pose_landmark_sets:
            return {}

        return self._landmark_list_to_map(pose_landmark_sets[0])

    def _extract_hand_landmarks(
        self, hand_result: Any
    ) -> tuple[LandmarkMap, LandmarkMap]:
        """
        Resolve hand outputs into left/right maps using handedness classification.
        """
        left_hand: LandmarkMap = {}
        right_hand: LandmarkMap = {}

        hand_landmark_sets = getattr(hand_result, "hand_landmarks", None) or []
        handedness_sets = getattr(hand_result, "handedness", None) or []

        for index, landmarks in enumerate(hand_landmark_sets):
            handedness_label = self._resolve_handedness_label(handedness_sets, index)
            landmark_map = self._landmark_list_to_map(landmarks)

            if handedness_label == "left":
                left_hand = landmark_map
            elif handedness_label == "right":
                right_hand = landmark_map

        return left_hand, right_hand

    def _extract_face_landmarks(self, face_result: Any) -> LandmarkMap:
        """
        Extract first detected face into a normalized landmark map.
        """
        face_landmark_sets = getattr(face_result, "face_landmarks", None)
        if not face_landmark_sets:
            return {}

        return self._landmark_list_to_map(face_landmark_sets[0])

    def _resolve_handedness_label(
        self, handedness_sets: list[Any], index: int
    ) -> str | None:
        """
        Resolve hand handedness label for one detected hand.

        Returns:
            "left", "right", or None if unavailable/unrecognized.
        """
        if index >= len(handedness_sets):
            return None

        categories = handedness_sets[index]
        if not categories:
            return None

        best_category = categories[0]
        raw_label = (
            getattr(best_category, "category_name", None)
            or getattr(best_category, "display_name", None)
            or str(best_category)
        )
        label = str(raw_label).strip().lower()

        if label == "left":
            return "left"
        if label == "right":
            return "right"
        return None

    def _landmark_list_to_map(self, landmarks: Any) -> LandmarkMap:
        """
        Convert a MediaPipe landmark list into {index: (x, y)}.
        """
        landmark_map: LandmarkMap = {}

        for index, landmark in enumerate(landmarks):
            landmark_map[index] = (float(landmark.x), float(landmark.y))

        return landmark_map

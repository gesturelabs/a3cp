# apps/landmark_extractor/tests/test_service_state_helpers.py

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from apps.landmark_extractor import service
from apps.landmark_extractor.config import FEATURE_DIM
from apps.landmark_extractor.domain import CaptureState
from schemas import LandmarkExtractorFrameInput

# test_get_or_create_capture_state_creates_new_state


def test_get_or_create_capture_state_creates_new_state():
    service._ACTIVE_CAPTURES.clear()

    capture_id = uuid4()
    now = datetime.now(timezone.utc)

    message = LandmarkExtractorFrameInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="user-1",
        session_id="session-1",
        timestamp=now,
        capture_id=capture_id,
        seq=1,
        timestamp_frame=now,
        frame_data="ZmFrZQ==",
    )

    state = service._get_or_create_capture_state(message)

    assert capture_id in service._ACTIVE_CAPTURES
    assert state.capture_id == capture_id
    assert state.user_id == "user-1"
    assert state.session_id == "session-1"
    assert state.feature_rows == []


# test_get_or_create_capture_state_returns_existing_state


def test_get_or_create_capture_state_returns_existing_state():
    service._ACTIVE_CAPTURES.clear()

    capture_id = uuid4()

    existing_state = CaptureState(
        capture_id=capture_id,
        user_id="user-1",
        session_id="session-1",
        feature_rows=[[0.1] * FEATURE_DIM],
    )

    service._ACTIVE_CAPTURES[capture_id] = existing_state

    now = datetime.now(timezone.utc)

    message = LandmarkExtractorFrameInput(
        schema_version="1.0.1",
        record_id=uuid4(),
        user_id="user-1",
        session_id="session-1",
        timestamp=now,
        capture_id=capture_id,
        seq=1,
        timestamp_frame=now,
        frame_data="ZmFrZQ==",
    )

    state = service._get_or_create_capture_state(message)

    assert state is existing_state


# test_get_active_capture_state_returns_existing_state
def test_get_active_capture_state_returns_existing_state():
    service._ACTIVE_CAPTURES.clear()

    capture_id = uuid4()

    existing_state = CaptureState(
        capture_id=capture_id,
        user_id="user-1",
        session_id="session-1",
        feature_rows=[[0.1] * FEATURE_DIM],
    )

    service._ACTIVE_CAPTURES[capture_id] = existing_state

    state = service._get_active_capture_state(capture_id)

    assert state is existing_state


# test_get_active_capture_state_raises_for_unknown_capture
def test_get_active_capture_state_raises_for_unknown_capture():
    service._ACTIVE_CAPTURES.clear()

    capture_id = uuid4()

    with pytest.raises(service.LandmarkExtractorServiceError):
        service._get_active_capture_state(capture_id)


# test_clear_active_capture_state_removes_capture
def test_clear_active_capture_state_removes_capture():
    service._ACTIVE_CAPTURES.clear()

    capture_id = uuid4()

    service._ACTIVE_CAPTURES[capture_id] = CaptureState(
        capture_id=capture_id,
        user_id="user-1",
        session_id="session-1",
        feature_rows=[[0.1] * FEATURE_DIM],
    )

    service._clear_active_capture_state(capture_id)

    assert capture_id not in service._ACTIVE_CAPTURES


# test_mark_terminal_adds_capture_id
def test_mark_terminal_adds_capture_id():
    service._TERMINAL_CAPTURE_IDS.clear()

    capture_id = uuid4()

    service._mark_terminal(capture_id)

    assert capture_id in service._TERMINAL_CAPTURE_IDS


# test_reject_if_terminal_raises_for_terminal_capture
def test_reject_if_terminal_raises_for_terminal_capture():
    service._TERMINAL_CAPTURE_IDS.clear()

    capture_id = uuid4()
    service._TERMINAL_CAPTURE_IDS.add(capture_id)

    with pytest.raises(service.LandmarkExtractorServiceError):
        service._reject_if_terminal(capture_id)

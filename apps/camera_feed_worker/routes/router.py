# apps/camera_feed_worker/routes/router.py

import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from apps.camera_feed_worker.repository import repo
from apps.camera_feed_worker.service import (
    AbortCapture,
    CleanupCapture,
    ProtocolViolation,
    dispatch,
)
from schemas import CameraFeedWorkerInput, CameraFeedWorkerOutput

router = APIRouter(prefix="/camera_feed_worker", tags=["camera_feed_worker"])


@router.post("/capture.tick", response_model=dict)
def capture_tick() -> dict:
    now_ingest = datetime.now(timezone.utc)
    return {
        "status": "not_implemented",
        "source": "camera_feed_worker",
        "now_ingest": now_ingest.isoformat(),
    }


# ---------------------------------------------------------------------
# Helpers (reduce ws_camera_feed complexity)
# ---------------------------------------------------------------------


def _parse_control_message(raw_text: str) -> CameraFeedWorkerInput:
    payload = json.loads(raw_text)
    return CameraFeedWorkerInput(**payload)


async def _enforce_identity_and_correlation(
    websocket: WebSocket,
    *,
    connection_key: str,
    msg: CameraFeedWorkerInput,
) -> bool:
    record_id = str(msg.record_id)

    if repo.has_seen_record_id(connection_key, record_id):
        await websocket.close(code=1008)
        return False
    repo.mark_record_id_seen(connection_key, record_id)

    if not msg.capture_id.strip():
        await websocket.close(code=1008)
        return False

    if msg.event == "capture.open":
        if not str(msg.user_id).strip() or not str(msg.session_id).strip():
            await websocket.close(code=1008)
            return False

    active_capture_id = repo.get_active_capture_id(connection_key)
    if active_capture_id is None:
        if msg.event == "capture.open":
            repo.set_active_capture_id(connection_key, msg.capture_id)
    else:
        if msg.capture_id != active_capture_id:
            await websocket.close(code=1008)
            return False
        if msg.event == "capture.close":
            repo.set_active_capture_id(connection_key, None)

    return True


async def _apply_domain_and_handle_actions(
    websocket: WebSocket,
    *,
    connection_key: str,
    msg: CameraFeedWorkerInput,
) -> bool:
    now_ingest = datetime.now(timezone.utc)
    current_state = repo.get_state(connection_key)

    try:
        new_state, actions = dispatch(
            current_state=current_state,
            event_kind=msg.event,
            event=msg,
            now_ingest=now_ingest,
        )
    except ProtocolViolation:
        await websocket.close(code=1008)
        return False

    repo.set_state(connection_key, new_state)

    abort_action = next((a for a in actions if isinstance(a, AbortCapture)), None)
    if abort_action is not None:
        out = CameraFeedWorkerOutput(
            schema_version=msg.schema_version,
            record_id=msg.record_id,
            user_id=msg.user_id,
            session_id=msg.session_id,
            timestamp=now_ingest,
            modality=msg.modality,
            source="camera_feed_worker",
            event="capture.abort",
            capture_id=abort_action.capture_id,
            error_code=abort_action.error_code,
        )
        await websocket.send_text(out.model_dump_json())
        repo.set_active_capture_id(connection_key, None)
        await websocket.close(code=1000)
        return False

    if any(isinstance(a, CleanupCapture) for a in actions):
        repo.set_active_capture_id(connection_key, None)

    return True


# ---------------------------------------------------------------------
# WebSocket route
# ---------------------------------------------------------------------


@router.websocket("/ws")
async def ws_camera_feed(websocket: WebSocket) -> None:
    await websocket.accept()
    connection_key = str(uuid.uuid4())

    try:
        while True:
            try:
                raw_text = await websocket.receive_text()
                msg = _parse_control_message(raw_text)
            except json.JSONDecodeError:
                await websocket.close(code=1003)
                return
            except ValidationError:
                await websocket.close(code=1008)
                return

            ok = await _enforce_identity_and_correlation(
                websocket,
                connection_key=connection_key,
                msg=msg,
            )
            if not ok:
                return

            ok = await _apply_domain_and_handle_actions(
                websocket,
                connection_key=connection_key,
                msg=msg,
            )
            if not ok:
                return

    except WebSocketDisconnect:
        pass
    finally:
        repo.clear(connection_key)

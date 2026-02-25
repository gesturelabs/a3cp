# apps/camera_feed_worker/routes/router.py

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Any, MutableMapping

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from apps.camera_feed_worker.forwarder_task import forwarder_loop
from apps.camera_feed_worker.repository import (
    ForwardFailed,
    ForwardItem,
    LimitForwardBufferExceeded,
    repo,
)
from apps.camera_feed_worker.service import (
    AbortCapture,
    ActiveState,
    ForwardFrame,
    IdleState,
    ProtocolViolation,
    RequestSessionRecheck,
    RequestSessionValidation,
    State,
    dispatch,
)
from apps.session_manager.service import validate_session
from schemas import CameraFeedWorkerInput, CameraFeedWorkerOutput

RECEIVE_TIMEOUT_S = (
    1.0  # ticks run even if client is silent; ensures session recheck ≤ 5s
)

router = APIRouter(prefix="/camera_feed_worker", tags=["camera_feed_worker"])


@router.post("/capture.tick", response_model=dict)
def capture_tick() -> dict:
    now_ingest = datetime.now(timezone.utc)
    return {
        "status": "disabled",
        "source": "camera_feed_worker",
        "now_ingest": now_ingest.isoformat(),
        "reason": "Demo invariant: all tick + session enforcement happens inside the WS loop only.",
    }


# ---------------------------------------------------------------------
# Helpers (reduce ws_camera_feed complexity)
# ---------------------------------------------------------------------


async def _noop_landmark_ingest(_: object) -> None:
    return


async def _emit_abort_and_close(
    websocket: WebSocket,
    *,
    connection_key: str,
    now_ingest: datetime,
    current_state: ActiveState,
    capture_id: str,
    error_code: str,
    last_msg_for_emit: CameraFeedWorkerInput | None,
) -> bool:
    record_id = current_state.record_id
    if record_id is None:
        await websocket.close(code=1011)
        return False

    out = CameraFeedWorkerOutput(
        schema_version=(
            last_msg_for_emit.schema_version if last_msg_for_emit else "1.0.1"
        ),
        record_id=record_id,
        user_id=current_state.user_id,
        session_id=current_state.session_id,
        timestamp=now_ingest,
        modality=(last_msg_for_emit.modality if last_msg_for_emit else "image"),
        source="camera_feed_worker",
        event="capture.abort",
        capture_id=capture_id,
        error_code=error_code,
    )
    await websocket.send_text(out.model_dump_json())

    await websocket.close(code=1000)
    return False


async def _tick_and_enforce_session(
    websocket: WebSocket,
    *,
    connection_key: str,
    last_msg_for_emit: CameraFeedWorkerInput | None,
) -> bool:
    """
    Apply domain tick and enforce session re-check actions.
    Returns False if the websocket was closed and the caller should return.
    """
    now_ingest = datetime.now(timezone.utc)
    pre_state = repo.get_state(connection_key)

    new_state, actions = dispatch(
        current_state=pre_state,
        event_kind="tick",
        event=None,
        now_ingest=now_ingest,
    )
    repo.set_state(connection_key, new_state)

    # ------------------------------------------------------------------
    # A) Session re-check has precedence over any other tick abort reasons.
    # ------------------------------------------------------------------
    recheck = next((a for a in actions if isinstance(a, RequestSessionRecheck)), None)
    if recheck is not None:
        status = validate_session(
            user_id=str(recheck.user_id),
            session_id=str(recheck.session_id),
        )
        if status != "active":
            # Prefer capture_id from pre_state if it was active when tick fired.
            active_state = (
                pre_state
                if isinstance(pre_state, ActiveState)
                else (new_state if isinstance(new_state, ActiveState) else None)
            )
            if active_state is None:
                await websocket.close(code=1011)
                return False

            capture_id = str(active_state.capture_id).strip()
            if not capture_id:
                await websocket.close(code=1011)
                return False

            error_code = "session_closed" if status == "closed" else "session_invalid"

            return await _emit_abort_and_close(
                websocket,
                connection_key=connection_key,
                now_ingest=now_ingest,
                current_state=active_state,
                capture_id=capture_id,
                error_code=error_code,
                last_msg_for_emit=last_msg_for_emit,
            )

    # ------------------------------------------------------------------
    # B) Domain-triggered abort (tick), but prefer session status if closed/invalid.
    # ------------------------------------------------------------------
    abort_action = next((a for a in actions if isinstance(a, AbortCapture)), None)
    if abort_action is not None:
        active_state = (
            pre_state
            if isinstance(pre_state, ActiveState)
            else (new_state if isinstance(new_state, ActiveState) else None)
        )
        if active_state is None:
            await websocket.close(code=1011)
            return False

        # If the session is no longer active, override the abort reason.
        status = validate_session(
            user_id=str(active_state.user_id),
            session_id=str(active_state.session_id),
        )
        if status != "active":
            error_code = "session_closed" if status == "closed" else "session_invalid"
            capture_id = str(active_state.capture_id).strip()
            if not capture_id:
                await websocket.close(code=1011)
                return False

            return await _emit_abort_and_close(
                websocket,
                connection_key=connection_key,
                now_ingest=now_ingest,
                current_state=active_state,
                capture_id=capture_id,
                error_code=error_code,
                last_msg_for_emit=last_msg_for_emit,
            )

        capture_id = (
            str(getattr(abort_action, "capture_id", "")).strip()
            or str(active_state.capture_id).strip()
        )
        if not capture_id:
            await websocket.close(code=1011)
            return False

        return await _emit_abort_and_close(
            websocket,
            connection_key=connection_key,
            now_ingest=now_ingest,
            current_state=active_state,
            capture_id=capture_id,
            error_code=abort_action.error_code,
            last_msg_for_emit=last_msg_for_emit,
        )

    return True


def _parse_control_message(raw_text: str) -> CameraFeedWorkerInput:
    payload = json.loads(raw_text)
    return CameraFeedWorkerInput(**payload)


async def _enforce_identity_and_correlation(
    websocket: WebSocket,
    *,
    connection_key: str,
    msg: CameraFeedWorkerInput,
) -> bool:
    # ------------------------------------------------------------------
    # 0) Basic structural ID checks (unchanged)
    # ------------------------------------------------------------------
    record_id = str(msg.record_id).strip()
    if not record_id:
        await websocket.close(code=1008)
        return False

    if repo.has_seen_record_id(connection_key, record_id):
        await websocket.close(code=1008)
        return False
    repo.mark_record_id_seen(connection_key, record_id)

    capture_id = msg.capture_id.strip()
    if not capture_id:
        await websocket.close(code=1008)
        return False

    if msg.event == "capture.open":
        if not str(msg.user_id).strip() or not str(msg.session_id).strip():
            await websocket.close(code=1008)
            return False

    # ------------------------------------------------------------------
    # 1) Domain-state-driven correlation (new)
    # ------------------------------------------------------------------
    state = repo.get_state(connection_key)

    if isinstance(state, IdleState):
        # When idle, only capture.open is permitted.
        if msg.event != "capture.open":
            await websocket.close(code=1008)
            return False
        return True

    if isinstance(state, ActiveState):
        # When active, capture_id must match the active capture.
        if capture_id != str(state.capture_id).strip():
            await websocket.close(code=1008)
            return False

        # If closing, we allow it here; domain dispatch will transition to IdleState.
        return True

    # Defensive: unknown state type
    await websocket.close(code=1011)
    return False


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
        # Only valid here if we were already idle (dispatch re-raises in IdleState).
        if isinstance(current_state, IdleState):
            await websocket.close(code=1008)
            return False
        raise

    repo.set_state(connection_key, new_state)
    # Successful capture.close => stop forwarding and close deterministically.
    if msg.event == "capture.close":
        repo.stop_forwarding(connection_key)
        await websocket.close(code=1000)
        return False

    # Enforce session validation at capture.open
    for a in actions:
        if isinstance(a, RequestSessionValidation):
            status = validate_session(
                user_id=str(a.user_id), session_id=str(a.session_id)
            )
            if status != "active":
                error_code = (
                    "session_closed" if status == "closed" else "session_invalid"
                )
                out = CameraFeedWorkerOutput(
                    schema_version=msg.schema_version,
                    record_id=msg.record_id,
                    user_id=msg.user_id,
                    session_id=msg.session_id,
                    timestamp=now_ingest,
                    modality=msg.modality,
                    source="camera_feed_worker",
                    event="capture.abort",
                    capture_id=str(msg.capture_id),
                    error_code=error_code,
                )
                await websocket.send_text(out.model_dump_json())

                await websocket.close(code=1000)
                return False
            # success: start forwarding only after validation
            if msg.event == "capture.open":
                repo.init_forwarding(
                    connection_key,
                    capture_id=str(msg.capture_id),
                    max_frames=3,
                    max_bytes=1_000_000,
                )
                task = asyncio.create_task(
                    forwarder_loop(
                        connection_key=connection_key,
                        ingest_fn=_noop_landmark_ingest,
                    )
                )
                repo.start_forwarding_task(connection_key, task)
            break

    abort_action = next((a for a in actions if isinstance(a, AbortCapture)), None)
    if abort_action is not None:
        repo.stop_forwarding(connection_key)

        capture_id = str(abort_action.capture_id).strip()
        if not capture_id:
            await websocket.close(code=1011)
            return False

        out = CameraFeedWorkerOutput(
            schema_version=msg.schema_version,
            record_id=msg.record_id,
            user_id=msg.user_id,
            session_id=msg.session_id,
            timestamp=now_ingest,
            modality=msg.modality,
            source="camera_feed_worker",
            event="capture.abort",
            capture_id=capture_id,
            error_code=abort_action.error_code,
        )
        await websocket.send_text(out.model_dump_json())
        await websocket.close(code=1000)
        return False

    # Sprint 1: RequestSessionValidation / RequestSessionRecheck are intentionally ignored here.

    return True


# Helper 1 (add near other helpers)
def _extract_and_validate_expected_bytes(
    event: MutableMapping[str, Any],
    expected_byte_length: int | None,
) -> bytes | None:
    if event.get("text") is not None:
        return None

    data = event.get("bytes")
    if not isinstance(data, (bytes, bytearray, memoryview)):
        return None

    data_bytes = bytes(data)
    if expected_byte_length is None or len(data_bytes) != expected_byte_length:
        return None

    return data_bytes


# Helper 2 (add near other helpers)
def _build_forward_item_or_none(
    *,
    current_state: State,
    actions: list[Any],
    data_bytes: bytes,
) -> ForwardItem | None:
    if not isinstance(current_state, ActiveState):
        return None

    forward_action = next((a for a in actions if isinstance(a, ForwardFrame)), None)
    if forward_action is None:
        return None

    return ForwardItem(
        capture_id=str(forward_action.capture_id),
        seq=int(forward_action.seq),
        timestamp_frame=forward_action.timestamp_event,
        payload=data_bytes,
        byte_length=len(data_bytes),
        encoding=str(current_state.encoding),
        width=int(current_state.width),
        height=int(current_state.height),
        user_id=str(current_state.user_id),
        session_id=str(current_state.session_id),
    )


# NEW (replace the whole function body with this version)
async def _handle_binary_frame_when_expected(
    websocket: WebSocket,
    *,
    connection_key: str,
    event: MutableMapping[str, Any],
    expected_byte_length: int | None,
    last_msg_for_emit: CameraFeedWorkerInput | None,
) -> bool:
    """
    Handle the next frame when the binary gate is armed.

    Returns True to continue the WS loop, False if the socket was closed
    and the caller should return.

    Note: caller is responsible for clearing the binary gate state.
    """
    data_bytes = _extract_and_validate_expected_bytes(event, expected_byte_length)
    if data_bytes is None:
        await websocket.close(code=1008)
        return False

    try:
        repo.raise_if_forward_failed(connection_key)
    except ForwardFailed:
        await websocket.close(code=1011)
        return False

    now_ingest = datetime.now(timezone.utc)
    current_state = repo.get_state(connection_key)

    new_state, actions = dispatch(
        current_state=current_state,
        event_kind="capture.frame_bytes",
        event=len(data_bytes),
        now_ingest=now_ingest,
    )
    repo.set_state(connection_key, new_state)

    abort_action = next((a for a in actions if isinstance(a, AbortCapture)), None)
    if abort_action is not None:
        repo.stop_forwarding(connection_key)

        if last_msg_for_emit is None:
            await websocket.close(code=1011)
            return False

        capture_id = str(getattr(abort_action, "capture_id", "")).strip()
        if not capture_id:
            await websocket.close(code=1011)
            return False

        out = CameraFeedWorkerOutput(
            schema_version=last_msg_for_emit.schema_version,
            record_id=last_msg_for_emit.record_id,
            user_id=(
                current_state.user_id
                if isinstance(current_state, ActiveState)
                else last_msg_for_emit.user_id
            ),
            session_id=(
                current_state.session_id
                if isinstance(current_state, ActiveState)
                else last_msg_for_emit.session_id
            ),
            timestamp=now_ingest,
            modality=last_msg_for_emit.modality,
            source="camera_feed_worker",
            event="capture.abort",
            capture_id=capture_id,
            error_code=abort_action.error_code,
        )
        await websocket.send_text(out.model_dump_json())
        await websocket.close(code=1000)
        return False

    item = _build_forward_item_or_none(
        current_state=current_state,
        actions=actions,
        data_bytes=data_bytes,
    )
    if item is None:
        await websocket.close(code=1011)
        return False

    try:
        repo.enqueue_frame(connection_key, item)
    except LimitForwardBufferExceeded:
        if last_msg_for_emit is None:
            await websocket.close(code=1011)
            return False

        repo.stop_forwarding(connection_key)
        active_state = current_state
        if not isinstance(active_state, ActiveState):
            await websocket.close(code=1011)
            return False

        return await _emit_abort_and_close(
            websocket,
            connection_key=connection_key,
            now_ingest=now_ingest,
            current_state=active_state,
            capture_id=str(active_state.capture_id),
            error_code="limit_forward_buffer_exceeded",
            last_msg_for_emit=last_msg_for_emit,
        )

    return True


async def _handle_text_control_message(
    websocket: WebSocket,
    *,
    connection_key: str,
    event: MutableMapping[str, Any],
) -> tuple[bool, CameraFeedWorkerInput | None]:
    """
    Handle a text control message when not expecting binary.

    Returns (ok, msg). If ok is False, caller should return.
    msg is returned for tracking last_msg_for_emit.
    """
    raw_text = event.get("text")
    if raw_text is None:
        await websocket.close(code=1008)
        return False, None

    msg = _parse_control_message(raw_text)

    ok = await _enforce_identity_and_correlation(
        websocket,
        connection_key=connection_key,
        msg=msg,
    )
    if not ok:
        return False, msg

    ok = await _apply_domain_and_handle_actions(
        websocket,
        connection_key=connection_key,
        msg=msg,
    )
    if not ok:
        return False, msg

    return True, msg


async def _receive_event_or_none(
    websocket: WebSocket,
) -> MutableMapping[str, Any] | None:
    try:
        return await asyncio.wait_for(websocket.receive(), timeout=RECEIVE_TIMEOUT_S)
    except asyncio.TimeoutError:
        return None


async def _ws_step(
    websocket: WebSocket,
    *,
    connection_key: str,
    expecting_binary: bool,
    expected_byte_length: int | None,
    last_msg_for_emit: CameraFeedWorkerInput | None,
) -> tuple[bool, bool, int | None, CameraFeedWorkerInput | None]:
    """
    One iteration of the WS loop.
    Returns: (keep_running, expecting_binary, expected_byte_length, last_msg_for_emit)
    """
    ok = await _tick_and_enforce_session(
        websocket,
        connection_key=connection_key,
        last_msg_for_emit=last_msg_for_emit,
    )
    if not ok:
        return False, expecting_binary, expected_byte_length, last_msg_for_emit

    # 7) Loop-level forward failure detection (once per iteration)
    try:
        repo.raise_if_forward_failed(connection_key)
    except ForwardFailed:
        state = repo.get_state(connection_key)

        # We can only emit capture.abort if we have active state + last_msg_for_emit
        if not isinstance(state, ActiveState) or last_msg_for_emit is None:
            repo.stop_forwarding(connection_key)
            await websocket.close(code=1011)
            return False, expecting_binary, expected_byte_length, last_msg_for_emit

        now_ingest = datetime.now(timezone.utc)
        repo.stop_forwarding(connection_key)

        keep_running = await _emit_abort_and_close(
            websocket,
            connection_key=connection_key,
            now_ingest=now_ingest,
            current_state=state,
            capture_id=str(state.capture_id),
            error_code="forward_failed",
            last_msg_for_emit=last_msg_for_emit,
        )
        return keep_running, expecting_binary, expected_byte_length, last_msg_for_emit

    event = await _receive_event_or_none(websocket)
    if event is None:
        return True, expecting_binary, expected_byte_length, last_msg_for_emit

    if expecting_binary:
        ok = await _handle_binary_frame_when_expected(
            websocket,
            connection_key=connection_key,
            event=event,
            expected_byte_length=expected_byte_length,
            last_msg_for_emit=last_msg_for_emit,
        )
        expecting_binary = False
        expected_byte_length = None
        if not ok:
            return False, expecting_binary, expected_byte_length, last_msg_for_emit
        return True, expecting_binary, expected_byte_length, last_msg_for_emit

    ok, msg = await _handle_text_control_message(
        websocket,
        connection_key=connection_key,
        event=event,
    )
    last_msg_for_emit = msg
    if not ok:
        expecting_binary = False
        expected_byte_length = None
        return False, expecting_binary, expected_byte_length, last_msg_for_emit

    if msg is not None and msg.event == "capture.frame_meta":
        if msg.byte_length is None:
            await websocket.close(code=1008)
            return False, expecting_binary, expected_byte_length, last_msg_for_emit
        expecting_binary = True
        expected_byte_length = int(msg.byte_length)

    return True, expecting_binary, expected_byte_length, last_msg_for_emit


async def _ws_control_plane_loop(websocket: WebSocket) -> None:
    """
    Shared WS loop for control-plane behavior.
    Used by both /ws (legacy) and /capture (new route).
    """
    await websocket.accept()
    connection_key = str(uuid.uuid4())

    expecting_binary = False
    expected_byte_length: int | None = None
    last_msg_for_emit: CameraFeedWorkerInput | None = None

    try:
        while True:
            try:
                (
                    keep_running,
                    expecting_binary,
                    expected_byte_length,
                    last_msg_for_emit,
                ) = await _ws_step(
                    websocket,
                    connection_key=connection_key,
                    expecting_binary=expecting_binary,
                    expected_byte_length=expected_byte_length,
                    last_msg_for_emit=last_msg_for_emit,
                )
                if not keep_running:
                    return

            except json.JSONDecodeError:
                await websocket.close(code=1003)
                return
            except ValidationError:
                await websocket.close(code=1008)
                return
            except Exception:
                await websocket.close(code=1011)
                return

    except WebSocketDisconnect:
        pass
    finally:
        repo.stop_forwarding(connection_key)
        repo.clear(connection_key)


# ---------------------------------------------------------------------
# WebSocket route
# ---------------------------------------------------------------------


@router.websocket("/ws")
async def ws_camera_feed(websocket: WebSocket) -> None:
    await _ws_control_plane_loop(websocket)


@router.websocket("/capture")
async def ws_camera_capture(websocket: WebSocket) -> None:
    await _ws_control_plane_loop(websocket)

# camera_feed_worker — Service Contract (Sprint 1)

Authoritative contract for `apps/camera_feed_worker/service.py`.

Scope:
- Pure domain logic only
- State machine
- Guardrails and limits
- Timeout rules
- Action emission
- No transport, no IO, no persistence

---

## 1. State Model

Per connection: at most one active capture.

States:
- `IdleState`
- `ActiveState`

There are no persistent `closed` or `aborted` states.

All cleanup is expressed via emitted actions.

---

## 2. Valid Transitions

### IdleState

- `capture.open`
  - Preconditions:
    - Valid schema
    - Limits satisfied (fps, resolution, pixels)
  - Transition: → `ActiveState`
  - Actions:
    - `RequestSessionValidation(user_id, session_id)`

- `capture.frame_meta`, `capture.frame_bytes`, `capture.close`
  - → `ProtocolViolation`

- `tick`
  - Remain `IdleState`

---

### ActiveState

- `capture.open`
  - → `ProtocolViolation`

- `capture.frame_meta`
  - Preconditions:
    - `seq == expected_next_seq`
    - `timestamp_frame ≥ last_frame_timestamp` (if exists)
    - No existing `pending_meta`
  - Transition:
    - Set `pending_meta`
    - Remain `ActiveState`

- `capture.frame_bytes`
  - Preconditions:
    - `pending_meta` exists
    - `received_byte_length == pending_meta.byte_length`
    - `byte_length ≤ max_frame_bytes`
    - `total_bytes + byte_length ≤ max_total_bytes`
    - `frame_count + 1 ≤ max_frames`
  - Transition:
    - Increment `frame_count`
    - Increment `total_bytes`
    - Update `last_frame_timestamp`
    - Increment `expected_next_seq`
    - Clear `pending_meta`
  - Actions:
    - `ForwardFrame(capture_id, seq, timestamp_frame, byte_length)`

- `capture.close`
  - Preconditions:
    - `timestamp_end ≥ timestamp_start`
    - `timestamp_end ≥ last_frame_timestamp` (if exists)
    - Duration ≤ `max_duration_s`
    - `pending_meta is None`
  - Transition:
    - → `IdleState`
  - Actions:
    - `CleanupCapture(capture_id)`

- `tick`
  - Checks:
    - Ingest duration > max → `LimitDurationExceeded`
    - Meta→bytes timeout → `ProtocolViolation`
    - Idle timeout → `ProtocolViolation`
    - Session re-check interval reached → emit `RequestSessionRecheck`
  - Transition:
    - Remain `ActiveState` unless abort

---

## 3. Abort Semantics

If any `CameraFeedWorkerError` occurs in `ActiveState`:

- Emit:
  - `AbortCapture(error_code, capture_id)`
  - `CleanupCapture(capture_id)`
- Transition:
  - → `IdleState`

If error occurs in `IdleState`:
- Raise `ProtocolViolation`

Service never maps to WebSocket close codes.

---

## 4. ActiveState Data

When active, maintain:

Identifiers:
- `capture_id`
- `user_id`
- `session_id`

Event-time:
- `timestamp_start`
- `last_frame_timestamp`

Ingest-time:
- `ingest_timestamp_open`
- `last_meta_ingest_timestamp`
- `last_session_check_ingest_timestamp`

Counters:
- `frame_count`
- `total_bytes`
- `expected_next_seq`
- `pending_meta` (seq, timestamp_frame, byte_length, meta_ingest_timestamp)

Counters increment only after successful frame acceptance.

---

## 5. Hard Limits (Sprint 1)

- `max_duration_s = 15`
- `max_fps = 15`
- `max_width = 640`
- `max_height = 480`
- `max_pixels = 307_200`
- `max_frames = 225`
- `max_frame_bytes = 300_000`
- `max_total_bytes = 50_000_000`

---

## 6. Timeouts

Evaluated in `handle_tick`:

- Meta→bytes timeout (>2s) → `ProtocolViolation`
- Idle timeout (>5s without frame_meta) → `ProtocolViolation`
- Session re-check interval (≥5s) → `RequestSessionRecheck`

Two duration guards:
- Ingest-time guard during capture
- Event-time validation on close

---

## 7. Domain Errors

Transport-agnostic.

Protocol:
- `ProtocolViolation`

Limits:
- `LimitDurationExceeded`
- `LimitFrameCountExceeded`
- `LimitResolutionExceeded`
- `LimitFpsExceeded`
- `LimitFrameBytesExceeded`
- `LimitTotalBytesExceeded`
- `LimitForwardBufferExceeded`

Forwarding:
- `ForwardFailed`

Session:
- `SessionInvalid`
- `SessionClosed`

Each maps to a stable `error_code`.

---

## 8. Action Outputs

Service emits actions only:

- `AbortCapture`
- `ForwardFrame`
- `RequestSessionValidation`
- `RequestSessionRecheck`
- `CleanupCapture`

Routes handle:
- WebSocket messages
- Close codes
- Session checks
- Forward queue mechanics

---

## 9. Non-Goals (Sprint 1)

- No persistence
- No disk writes
- No schema recording
- No frame batching
- No resume/retry logic
- No multi-capture per connection

---

This contract defines the authoritative domain behavior for Sprint 1.

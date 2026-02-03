# camera_feed_worker — Sprint 1 Domain Specification (Service Layer Only)

This document defines the pure domain logic for `apps/camera_feed_worker/service.py`.

Scope:
- State machine
- Limit enforcement
- Timestamp rules
- Domain errors
- Action outputs

Out of scope:
- FastAPI / WebSocket handling
- Transport-level close codes
- Persistence
- Forwarding implementation details
- JSON parsing

---

## 1. Capture State Model

Per connection, at most one capture may be active.

Service-level states:
- `idle`
- `active`

There are no persistent `closed` or `aborted` states in the service layer.

Transition rules:
- `capture.open` allowed only in `idle`
- `capture.frame_meta` allowed only in `active`
- `capture.frame_bytes` allowed only in `active` and only if a pending meta exists
- `capture.close` allowed only in `active`
- Any invalid transition → `ProtocolViolation`

Terminal outcomes:
- On successful close:
  - emit `CleanupCapture(capture_id)`
  - return to `idle`
- On abort (error condition):
  - emit `AbortCapture(error_code, capture_id)`
  - emit `CleanupCapture(capture_id)`
  - return to `idle`

All cleanup is expressed via emitted actions, not via intermediate service states.
---
## X. Formal Transition Table (Sprint 1 — Service Layer)

All handlers accept:
- `current_state`
- `event`
- `now_ingest`

They return:
- `(new_state, actions)`
or raise a typed domain error.

---

### IdleState

**capture.open**
Preconditions:
- Valid schema
- Limits satisfied (`fps_target`, `width`, `height`, `pixels`)
Transition:
- → `ActiveState`
Actions:
- `RequestSessionValidation(user_id, session_id)`

**capture.frame_meta / frame_bytes / capture.close**
- → `ProtocolViolation`

**tick**
- Remain `IdleState`

---

### ActiveState

**capture.open**
- → `ProtocolViolation`

**capture.frame_meta**
Preconditions:
- `seq == expected_next_seq`
- `timestamp_frame ≥ last_frame_timestamp` (if exists)
- No existing `pending_meta`
Transition:
- Set `pending_meta`
- Remain `ActiveState`

**frame_bytes**
Preconditions:
- `pending_meta` exists
- `byte_length ≤ max_frame_bytes`
- `total_bytes + byte_length ≤ max_total_bytes`
- `received_byte_length == pending_meta.byte_length`

Transition:
- `frame_count += 1`
- `total_bytes += byte_length`
- `last_frame_timestamp = pending_meta.timestamp_frame`
- `expected_next_seq += 1`
- Clear `pending_meta`
- Remain `ActiveState`
Actions:
- `ForwardFrame(capture_id, seq, timestamp_frame, byte_length)`

**capture.close**
Preconditions:
- `timestamp_end ≥ timestamp_start`
- `timestamp_end ≥ last_frame_timestamp` (if exists)
- `(timestamp_end - timestamp_start) ≤ max_duration_s`
- `pending_meta is None`
Transition:
- → `IdleState`
Actions:
- `CleanupCapture(capture_id)`

**tick**
Checks:
- Ingest duration guard → `LimitDurationExceeded`
- Meta→bytes timeout (>2s) → `ProtocolViolation`
- Idle timeout (>5s no meta) → `ProtocolViolation`
- Session re-check interval (≥5s) → emit `RequestSessionRecheck`
Transition:
- Remain `ActiveState` unless abort

---

### Abort Semantics

On any domain error in `ActiveState`:
- Emit `AbortCapture(error_code, capture_id)`
- Emit `CleanupCapture(capture_id)`
- → `IdleState`




## 2. Capture State Data (In-Memory, Per Capture)

When `active`, maintain:

- `capture_id`
- `user_id`
- `session_id`
- `timestamp_start` (event-time)
- `params` (fps_target, width, height, encoding)

Counters:
- `frame_count`
- `total_bytes`
- `expected_next_seq` (starts at 1)
- `last_frame_timestamp` (event-time)
- `ingest_timestamp_open` (server ingest-time)
- `pending_meta`:
  - `seq`
  - `timestamp_frame`
  - `byte_length`
  - `meta_ingest_timestamp`

No counters increment unless a frame is fully accepted.

---

## 3. Hard Limits (Sprint 1 Locked)

- `max_duration_s = 15`
- `max_fps = 15`
- `max_width = 640`
- `max_height = 480`
- `max_pixels = 307_200`
- `max_frames = 225`
- `max_frame_bytes = 300_000`
- `max_total_bytes = 50_000_000`

---

## 4. Domain Errors (Transport-Agnostic)

Each error maps to exactly one `error_code`.

### Protocol
- `ProtocolViolation` → `"protocol_violation"`

### Limits
- `LimitDurationExceeded`
- `LimitFrameCountExceeded`
- `LimitResolutionExceeded`
- `LimitFpsExceeded`
- `LimitFrameBytesExceeded`
- `LimitTotalBytesExceeded`
- `LimitForwardBufferExceeded`

### Forwarding
- `ForwardFailed`

### Session
- `SessionInvalid`
- `SessionClosed`

Service MUST NOT know WebSocket close codes.

---

## 5. Event Handling Functions (Pure Logic)

All functions accept:
- current state
- event object
- `now_ingest` (server time)

They either:
- return `(new_state, actions)`
- or raise a typed domain error

Required handlers:

- `handle_open(open_event, now_ingest)`
- `handle_frame_meta(meta_event, now_ingest)`
- `handle_frame_bytes(byte_length, now_ingest)`
- `handle_close(close_event, now_ingest)`
- `handle_tick(now_ingest)` (timeouts + duration guard)

---

## 6. Ordering & Timestamp Rules

### Open
- `fps_target ≤ max_fps`
- `width ≤ max_width`
- `height ≤ max_height`
- `width × height ≤ max_pixels`

### Frame Meta
- `seq == expected_next_seq`
- `timestamp_frame ≥ last_frame_timestamp` (if exists)
- No existing `pending_meta`


### Frame Bytes
- Must immediately follow matching meta
- `byte_length ≤ max_frame_bytes`
- After acceptance:
  - increment `frame_count`
  - increment `total_bytes`
  - update `last_frame_timestamp` (from `timestamp_frame`)
  - increment `expected_next_seq`
  - clear `pending_meta`

### Close
- `timestamp_end ≥ timestamp_start`
- `timestamp_end ≥ last_frame_timestamp`
- `(timestamp_end - timestamp_start) ≤ max_duration_s`

Violations → `ProtocolViolation` or appropriate limit error.

---

## 7. Duration Enforcement

Two checks:

1. Ingest-time guard (during capture):
   - `(now_ingest - ingest_timestamp_open) > max_duration_s`
   → `LimitDurationExceeded`

2. Event-time validation on close:
   - `(timestamp_end - timestamp_start) ≤ max_duration_s`

---

## 8. Frame & Byte Limits

- `frame_count > max_frames` → `LimitFrameCountExceeded`
- `byte_length > max_frame_bytes` → `LimitFrameBytesExceeded`
- `total_bytes > max_total_bytes` → `LimitTotalBytesExceeded`

Rejected frames do NOT increment counters.

---

## 9. Timeouts (Evaluated in handle_tick)

- Meta→bytes timeout:
  - `(now_ingest - pending_meta.meta_ingest_timestamp) > 2s`
  → `ProtocolViolation`

- Idle timeout:
  - No `frame_meta` for 5s while active
  → `ProtocolViolation`

- Session re-check trigger:
  - If 5s elapsed since last session check
  → emit action `RequestSessionRecheck`

---

## 10. Action Outputs (Returned to Route Layer)

Service emits actions but performs no IO.

Possible actions:

- `AbortCapture(error_code, capture_id)`
- `ForwardFrame(capture_id, seq, timestamp_event, byte_length)`
- `RequestSessionValidation(user_id, session_id)` (on open)
- `RequestSessionRecheck(user_id, session_id)`
- `CleanupCapture(capture_id)`

Routes decide:
- WebSocket messages
- Close codes
- Queue forwarding
- Session service calls

---

## 11. No-Disk Guarantee

Service layer:
- Performs no persistence
- Writes no files
- Emits no schema events
- Has no knowledge of JSONL logs

---

## 12. Non-Goals (Sprint 1)

- No batching
- No frame reordering
- No resume support
- No multi-capture per connection
- No transport retry logic
- No disk buffering

---

This specification defines the authoritative domain contract for Sprint 1.

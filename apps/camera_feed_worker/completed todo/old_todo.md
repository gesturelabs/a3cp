# apps/camera_feed_worker/TODO.md

16 hours focused work.


## Context Files (authoritative for this slice)
- schemas/base_schema.json  (BaseSchema reference)
- schemas/__init__.py
- schemas/session_manager/session_manager_start/session_manager_start.py
- schemas/session_manager/session_manager_end/session_manager_end.py
- api/routes/camera_feed_worker_routes.py  (legacy shim; required for migration)
- apps/ui/static/js/demo_session.js  (browser capture client reference)

## Module Entry Points (canonical app structure)

- apps/camera_feed_worker/routes/router.py
- apps/camera_feed_worker/service.py
- apps/camera_feed_worker/repository.py

---

## WebSocket Close Codes (Sprint 1 — Locked)

- `1008` — policy/protocol violation
  - `protocol_violation`
  - limit violations (`limit_*`)
  - session invalid/closed (`session_invalid`, `session_closed`)
  - forward buffer overflow (`limit_forward_buffer_exceeded`)
- `1009` — message too big (frame size only)
  - `limit_frame_bytes_exceeded`
- `1011` — internal server error
  - `forward_failed`

## Capture State Model (Sprint 1 — Locked)

Per WebSocket connection, at most one capture may be active.

States:
- `idle` → no active capture
- `active` → after valid `capture.open`
- `closed` → after valid `capture.close`
- `aborted` → after `capture.abort` or protocol/limit/session failure

Rules:
- `capture.open` allowed only in `idle`
- `capture.frame_meta` / `capture.frame_bytes` allowed only in `active`
- `capture.close` allowed only in `active`
- Any invalid transition → `protocol_violation`
- Terminal states (`closed`, `aborted`) return to `idle` only after cleanup completes

## Limit Accounting (Sprint 1 — Locked)

Maintain per-capture counters in connection-local state:

- `frame_count` — increments after each accepted `capture.frame_bytes`
- `total_bytes` — sum of accepted frame byte lengths (increments with `frame_count`)
- `last_frame_timestamp` — event-time timestamp of last accepted frame
- `ingest_timestamp_open` — server ingest-time at accepted `capture.open`

All limit checks are evaluated against these counters; rejected frames do not increment counters.


## Authoritative architecture for this slice: **browser-based capture**

- Browser uses `getUserMedia()` to capture a **bounded capture window**.
- Browser streams a bounded capture window over WebSocket:
  `capture.open` → repeated `capture.frame_meta` + `capture.frame_bytes` → `capture.close`.
- Browser is responsible for device access and frame encoding (e.g., JPEG).
- `camera_feed_worker` is responsible only for ingest validation, guardrail enforcement, and forwarding.
- `camera_feed_worker` does **not** own OS-level camera devices and does **not** rely on `/dev/video*` in containers.
- Transport (Sprint 1 decision): bounded capture windows are ingested via **WebSocket** (not HTTP).

Current repo state note:
- Legacy shim exists at `api/routes/camera_feed_worker_routes.py`
- It currently deep-imports schemas:
  `from schemas.camera_feed_worker.camera_feed_worker import ...`

Target (normative):
- Legacy shim must delegate to `apps/camera_feed_worker/routes/router.py`
- Routes must import schemas only via `from schemas import ...`
- No business logic permitted in `api/routes/*`
- Canonical routes live exclusively under `apps/camera_feed_worker/`

---
## Error Code Taxonomy (Sprint 1 — Locked)

`error_code` values are mutually exclusive and categorized as follows:

**Protocol errors**
- `protocol_violation`
  - invalid message order
  - malformed payload
  - timestamp ordering violations
  - unexpected message type

**Limit violations**
- `limit_duration_exceeded`
- `limit_frame_count_exceeded`
- `limit_resolution_exceeded`
- `limit_fps_exceeded`
- `limit_frame_bytes_exceeded`
- `limit_total_bytes_exceeded`

**Forwarding failures**
- `forward_failed`
- `limit_forward_buffer_exceeded`

**Session validation failures**
- `session_invalid`
- `session_closed`

All aborts must include exactly one `error_code`.



## WebSocket Payload Contract — Sprint 1 (Locked)

**Transport**
- WebSocket
- Control messages: JSON text frames
- Frame payloads: JPEG bytes (binary WS frame)
- Per-frame = 2 messages:
  1) `capture.frame_meta` (JSON)
  2) `capture.frame_bytes` (binary; length must equal `byte_length`)

**Connection / ordering rules (locked)**
- One WebSocket connection may have **at most one active capture** at a time.
- A second `capture.open` while a capture is active is a **protocol violation** → abort.
- Frames for different `capture_id`s must **not** interleave on the same connection.
- No reordering, buffering, or resume support in Sprint 1.

**Protocol error code (locked)**
- `protocol_violation` covers:
  - unexpected message order (e.g., bytes without meta)
  - missing/invalid required fields
  - mismatched `capture_id`
  - duplicate `capture.open` while active
  - unexpected message type

---

### capture.open (JSON)
- `type="capture.open"`
- `schema_version`
- `record_id` (UUIDv4; message instance)
- `user_id`
- `session_id`
- `capture_id` (UUIDv4; browser-generated; authoritative window ID)
- `timestamp_start` (ISO 8601 Z ms; browser event-time)
- `params`: `fps_target`, `width`, `height`, `encoding="jpeg"` (Sprint 1: fixed)

---

### capture.frame_meta (JSON)
- `type="capture.frame_meta"`
- `capture_id`
- `seq` (int; strictly increasing from 1; duplicates/gaps/non-monotonic → `protocol_violation`)
- `timestamp` (ISO 8601 Z ms; event-time; must be ≥ prior frame timestamp)
- `content_type="image/jpeg"` (Sprint 1: fixed)
- `byte_length` (int)

### capture.frame_bytes (binary)
- Raw JPEG bytes
- Must immediately follow matching `frame_meta`
- If bytes do not arrive in time, or length mismatches `byte_length` → `protocol_violation`

---

### capture.close (JSON)
- `type="capture.close"`
- `capture_id`
- `timestamp_end` (ISO 8601 Z ms; event-time; must be ≥ last frame timestamp and ≥ `timestamp_start`)

---

### Timeouts (Locked)
- Meta→bytes timeout: 2s → abort (`protocol_violation`)
  - timer starts after a valid `capture.frame_meta`
- Idle timeout: 5s → abort (`protocol_violation`)
  - timer resets on each valid `capture.frame_meta`
- Disconnects abort capture; resume not supported.

## Pre-Build Decision — Hard Limits (Sprint 1)

### Numeric Caps (Locked)

Authoritative Sprint 1 limits:

- `max_duration_s = 15`  (event-time duration cap)
- `max_fps = 15`
- `max_width = 640`
- `max_height = 480`
- `max_pixels = 307_200`  (width × height upper bound)
- `max_frames = max_duration_s × max_fps`  (= 225)
- `max_frame_bytes = 300_000`
- `max_total_bytes = 50_000_000`

Notes:
- Duration is computed from browser event-time:
  `timestamp_end - timestamp_start`
- Frame count enforcement does **not** rely on client-declared `fps_target`.
- `max_total_bytes` is independent and may be reached before `max_frames`.

---

### Enforcement Rules (Locked)

**Resolution**
- Reject if `width > max_width`
- Reject if `height > max_height`
- Reject if `width × height > max_pixels`

**FPS**
- Reject `capture.open` if `fps_target > max_fps`
- Effective frame rate also bounded by `max_frames` logic

**Duration**
- Ingest-time guard: if `(server_now - ingest_timestamp_open) > max_duration_s` → abort
- Event-time validation: on `capture.close`, ensure
  `(timestamp_end - timestamp_start) ≤ max_duration_s`

**Frames**
- Abort if `frame_count > max_frames`

**Bytes**
- Abort if any `byte_length > max_frame_bytes`
- Abort if cumulative bytes > `max_total_bytes`

---
### Abort Semantics (Limit Violations Only)

On limit breach:

1. Send:

```json
{
  "type": "capture.abort",
  "capture_id": "<uuid>",
  "error_code": "<enum>"
}

2. Close WebSocket:

1008 → policy violation

1009 → message too big (frame size only)

3. Immediately release all in-memory buffers.

Stable Limit Error Codes

limit_duration_exceeded

limit_frame_count_exceeded

limit_resolution_exceeded

limit_fps_exceeded

limit_frame_bytes_exceeded

limit_total_bytes_exceeded


----
## Pre-Build Decision — Timestamp Authority (Sprint 1)

### Event-Time Authority (Locked)

- `timestamp_start`, per-frame `timestamp`, and `timestamp_end` are **browser-supplied event-time** and authoritative.
- `camera_feed_worker` MUST NOT overwrite or normalize these fields.
- These values are propagated unchanged to downstream modules.

### Ingest-Time Diagnostics (Allowed)

- Server may attach separate fields:
  - `ingest_timestamp_open`
  - `ingest_timestamp_frame`
  - `ingest_timestamp_close`
- Ingest-time fields are strictly diagnostic and must never replace event-time.
- Event-time and ingest-time must remain strictly separate (no mixed semantics in a single field).

---

### Ordering & Validity Rules (Locked)

- `timestamp_end` must be ≥ `timestamp_start`.
- Per-frame `timestamp` must be ≥ previous frame timestamp.
- `timestamp_end` must be ≥ last frame timestamp.
- Structurally invalid ISO 8601 timestamps → `protocol_violation`.
- Clearly invalid ordering (e.g., end < start) → `protocol_violation`.

---

### Clock Skew Tolerance (Sprint 1)

- Reasonable client/server clock skew is tolerated (e.g., ±5 minutes relative to ingest-time).
- Implausible timestamps (e.g., >24 hours in the future or past relative to ingest-time) → `protocol_violation`.

---

### Rejection Semantics

Timestamp violations result in:

1. `capture.abort` with `error_code="protocol_violation"`
2. WebSocket close (`1008`)
3. Immediate release of in-memory buffers



## Pre-Build Decision — Forwarding Boundary (Sprint 1)

**Mode (locked)**
- Streaming: each validated frame is forwarded immediately.
- No batching. No frame dropping.

**Queue model (locked)**
- One bounded async in-process queue per active capture.
- Limits:
  - `max_forward_buffer_frames = 30`
  - `max_forward_buffer_bytes = 10_000_000`
- Buffer overflow → `capture.abort`
  - `error_code="limit_forward_buffer_exceeded"`
  - WS close `1008`

**Forward failure (locked)**
- Any downstream exception, queue failure, or forwarding task crash →
  - `capture.abort`
  - `error_code="forward_failed"`
  - WS close `1011`
- No retries in `camera_feed_worker`.

**Cleanup guarantee (locked)**
On close, abort, timeout, or disconnect:
- Cancel forwarding task
- Drain queue
- Release all in-memory buffers
- Remove capture state

Module must remain strictly memory-bounded.



## Pre-Build Decision — Session Validation (Sprint 1)

**Validation point (locked)**
- On `capture.open`, `camera_feed_worker` MUST synchronously verify that:
  - `session_id` exists
  - `session_id` is active
  - `session_id` belongs to `user_id`
- Validation occurs once at `capture.open` (not per-frame).

If validation fails:
- Send `capture.abort`
  - `error_code="session_invalid"`
- Close WebSocket (`1008`)
- Do not create capture state

**Mid-capture closure (locked)**
- Sprint 1 detection mechanism: periodic service re-check during capture:
  - re-check `session_id` active for `user_id` every `5s` while capture is active
- If re-check fails:
  - `capture.abort` with `error_code="session_closed"`
  - close WS (`1008`)
  - release buffers immediately


No session inference. No implicit “current session”.


## Pre-Build Decision — No-Disk Guarantee (Sprint 1)

**Policy (locked)**
- `camera_feed_worker` MUST NOT write raw frames or capture payloads to disk.
- All frame bytes are stored in RAM only (bounded queues/buffers).
- No temp files. No uploads. No caching. No persistence of capture data.

**Architectural boundary (locked)**
- `camera_feed_worker` MUST NOT call:
  - `apps/schema_recorder.service.append_event()`
  - any repository performing session JSONL writes
- Only downstream modules may emit schema-compliant events.

**CI guardrails (locked)**
- Fail build if any file under `apps/camera_feed_worker/**`:
  - writes to filesystem paths
  - imports known file-writing utilities (e.g., `tempfile`, `aiofiles`, `cv2.VideoWriter`)
- Fail build if any file under `apps/camera_feed_worker/**` imports `apps/schema_recorder.repository`.

The module must remain strictly in-memory and side-effect free (except WebSocket I/O).


## Invariant — Recorder Rule (Locked)

- `camera_feed_worker` MUST NOT write or append to any session JSONL files.
- `camera_feed_worker` MUST NOT import or call:
  - `apps/schema_recorder.repository`
  - any file performing JSONL session writes
- If schema-compliant events are required in future slices, they must be emitted via:
  - `apps/schema_recorder.service.append_event()`

CI enforces:
- Writer allowlist: only `apps/schema_recorder/repository.py` may perform session JSONL I/O.
- No direct or indirect imports of the repository layer from `camera_feed_worker`.


## A) Canonical app structure (must be created)

Create the runtime app under `apps/` following the canonical architecture.
`camera_feed_worker` is mounted from `api/main.py`.

- [ ] **Capture correlation rule (locked):** `capture_id: UUID` identifies one bounded capture window end-to-end (browser → camera_feed_worker → landmark_extractor → feature-ref event). `record_id: UUID` remains per A3CPMessage (downstream only).

- [ ] **Authoritative ID generation (locked):**
  - `session_id`: generated only by `session_manager`
  - `record_id`: generated by the emitting module for each `A3CPMessage`
  - `capture_id`: generated by the browser at capture start; `camera_feed_worker` accepts/propagates unchanged (reject if missing)

- [ ] Create app directory:
  - [ ] `apps/camera_feed_worker/`

- [ ] Routes layer (FastAPI/WS adapters only):
  - [ ] `apps/camera_feed_worker/routes/__init__.py`
  - [ ] `apps/camera_feed_worker/routes/router.py`
    - expose WebSocket endpoint (authoritative for Sprint 1):
      - `WS /camera_feed_worker/capture`
    - parse/validate WS messages against transport schemas
    - maintain connection-local ephemeral state (active capture, pending meta, counters)
    - call service functions for policy/guardrail decisions
    - translate domain/protocol errors into `capture.abort` + WS close codes
    - MUST NOT: persistence, cross-app business logic, hidden context/ID generation

- [ ] Service layer (required):
  - [ ] `apps/camera_feed_worker/service.py`
    - implements bounded capture ingest policy (limits, ordering, timestamp rules, session check trigger)
    - pure domain/policy logic; explicit inputs only
    - MUST NOT: depend on FastAPI, raise HTTP exceptions, perform persistence

- [ ] Forwarding boundary (required):
  - [ ] `apps/camera_feed_worker/repository.py`
    - boundary for forwarding validated frames/windows to `landmark_extractor`
    - async bounded in-memory queue per capture (no disk writes)
    - MUST NOT: policy decisions, HTTP/WS exception mapping

- [ ] Tests (required):
  - [ ] `apps/camera_feed_worker/tests/`
    - [ ] protocol sequencing (open/meta/bytes/close; meta→bytes timeout)
    - [ ] guardrails (duration/fps/resolution/frame_bytes/total_bytes)
    - [ ] session validation on open + mid-capture closure behavior
    - [ ] forwarding behavior (buffer overflow, downstream failure)
    - [ ] thin WS route tests (happy path + abort paths)



---

## B) Deep route fix (Route Re-Migration)

Eliminate deep imports and migrate routing to canonical app structure.

### 1) Inventory (read-only)
- [ ] Identify legacy route file(s):
  - `api/routes/camera_feed_worker_routes.py`
- [ ] Identify which schema classes it imports and from where
  - current: `schemas.camera_feed_worker.camera_feed_worker`

### 2) Public schema surface exports (no behavior change)
- [ ] Ensure transport schema names used by camera_feed_worker are exported from `schemas/__init__.py` and included in `__all__`
  (Sprint 1 WS contract):
  - `CaptureOpen`
  - `CaptureFrameMeta`
  - `CaptureClose`
  - `CaptureAbort` (and `CaptureAck` if used)

- [ ] Confirm all camera_feed_worker routes import schemas only via:
  - `from schemas import ...`
  and that referenced names exist in `schemas.__all__`.

### 3) Rewrite legacy shim route (structure-only; no redesign)
- [ ] Update `api/routes/camera_feed_worker_routes.py` to:
  - import schemas only via `from schemas import ...`
  - import the canonical router from `apps.camera_feed_worker.routes.router`
  - register/include that router (no endpoint logic in the shim)
- [ ] Ensure router is mounted once in `api/main.py` (no duplicate registration)

### 4) Scoped guardrails (tests)
- [ ] Test: fail if `api/routes/camera_feed_worker_routes.py` deep-imports `schemas.<submodule>`
- [ ] Test: required schema names exist in `schemas.__all__`
- [ ] Test: shim contains no route logic beyond router inclusion/mounting

### 5) Startup + WS route smoke verification (minimal)
- [ ] App boots without import/validation errors
- [ ] WebSocket path is registered (basic connect attempt acceptable)

---

## C) Browser ingest behavior (Sprint 1)

- [ ] Accept bounded capture windows **streamed over WebSocket** from browser clients.
- [ ] Enforce the locked identity and correlation rules (see “Capture correlation rule” above).
- [ ] Require and validate ingress metadata by message type:
  - `capture.open`: `schema_version`, `record_id`, `user_id`, `session_id`, `capture_id`, `timestamp_start`, `params`
  - `capture.frame_meta`: `capture_id`, `seq`, `timestamp`, `content_type`, `byte_length`
  - `capture.close`: `capture_id`, `timestamp_end`
- [ ] Forward frames to `landmark_extractor` according to the locked forwarding mode (Sprint 1: streaming per frame).
- [ ] Do NOT persist raw video frames/streams (Sprint 1).
- [ ] Explicitly out of scope for Sprint 1:
  - owning OS camera devices
  - `/dev/video*`
  - `cv2.VideoCapture()` direct device capture




---

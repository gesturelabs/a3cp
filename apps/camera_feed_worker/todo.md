# camera_feed_worker — Sprint 1 TODO (Actionable Only)

---

## A0) Schemas

- [x ] Replace/deprecate legacy `camera_feed_worker` schemas
- [x ] Define Sprint 1 control-plane schemas:
  - `CameraFeedWorkerInput` (event-discriminated superset: open / frame_meta / close)
  - `CameraFeedWorkerOutput` (`capture.abort` only)
- [ x] Update domain spec: use `timestamp_frame` (not `timestamp`) for frame event-time



## A) App Skeleton

## A) App Skeleton

- [ ] Create package structure:
  - [ x] `apps/camera_feed_worker/__init__.py`
  - [x ] `apps/camera_feed_worker/routes/__init__.py`
  - [ x] `apps/camera_feed_worker/routes/router.py`
  - [ x] `apps/camera_feed_worker/service.py`
  - [ x] `apps/camera_feed_worker/repository.py`
  - [ x] `apps/camera_feed_worker/tests/__init__.py`

- [ x] Router design:
  - [ x] Prefix: `/camera_feed_worker`
  - [ x] Tags: `["camera_feed_worker"]`
  - [ x] WebSocket endpoint: `/camera_feed_worker/ws`
  - [x ] HTTP endpoint: `POST /camera_feed_worker/capture.tick`

- [x ] Mount router in `api/main.py`
  - [x ] Import `camera_feed_worker_router`
  - [x ] Register with `app.include_router(...)`
  - [x ] Ensure single registration only


## B) Service Layer (Pure Domain Logic)

Implement state machine + limit enforcement per domain spec.

- [x ] Implement state model (`idle`, `active`)
- [ ] Implement handlers:
  - [ x] `handle_open`
  - [x ] `handle_frame_meta`
  - [ x] `handle_frame_bytes`
  - [x ] `handle_close`
  - [ x] `handle_tick`
- [x ] Implement:
  - [ x] ordering validation
  - [ x] timestamp validation
  - [ x] limit accounting (frames, bytes, duration)
  - [ x] timeout detection
  - [ x] session re-check trigger emission
- [ x] Ensure service raises typed domain errors only
- [ x] Ensure service has zero FastAPI imports
- [ x] Ensure service performs no IO


## Service Layer Tests (camera_feed_worker)

### 1. Open / State Transitions
- [ ] `capture.open` from Idle → Active
- [ ] `capture.open` from Active → abort + cleanup
- [ ] `capture.close` from Idle → ProtocolViolation
- [ ] Unknown event_kind → ProtocolViolation

### 2. Protocol Sequencing
- [ ] `frame_meta` with correct `seq` accepted
- [ ] `frame_meta` with wrong `seq` → abort
- [ ] `frame_meta` when `pending_meta` exists → abort
- [ ] `frame_bytes` without `pending_meta` → abort
- [ ] `frame_bytes` with mismatched byte_length → abort
- [ ] `capture.close` with `pending_meta` present → abort

### 3. Timestamp Ordering
- [ ] `timestamp_frame` < `last_frame_timestamp` → abort
- [ ] `timestamp_end` < `timestamp_start` → abort
- [ ] `timestamp_end` < `last_frame_timestamp` → abort

### 4. Duration Enforcement
- [ ] Ingest-time duration exceeded during `tick` → abort
- [ ] Event-time duration exceeded on `capture.close` → abort
- [ ] Valid duration close returns Idle + CleanupCapture

### 5. Frame / Byte Limits
- [ ] Frame count exceeds `MAX_FRAMES` → abort
- [ ] Single frame exceeds `MAX_FRAME_BYTES` → abort
- [ ] Total bytes exceed `MAX_TOTAL_BYTES` → abort
- [ ] Valid frame increments counters correctly

### 6. Timeout Handling (handle_tick)
- [ ] Meta→bytes timeout (>2s) → abort
- [ ] Idle timeout (>5s no meta) → abort
- [ ] No timeout within limits → remain Active

### 7. Session Re-check Emission
- [ ] `tick` before 5s → no recheck
- [ ] `tick` at ≥5s → emit `RequestSessionRecheck`
- [ ] Recheck timestamp updates after emission

### 8. Abort Semantics (dispatch)
- [ ] Any CameraFeedWorkerError in ActiveState → returns IdleState
- [ ] AbortCapture action emitted with correct error_code
- [ ] CleanupCapture action emitted with correct capture_id
- [ ] Error in IdleState is re-raised (no abort wrapper)

### 9. Happy Path Integration
- [ ] Full valid flow:
      open → meta → bytes → close
      → ends in IdleState
      → emits ForwardFrame(s)
      → emits CleanupCapture


---




## C) Identity & Correlation Enforcement

- [ ] Enforce required IDs on `capture.open`
  - `user_id`
  - `session_id`
  - `capture_id`
- [ ] Reject missing `capture_id`
- [ ] Ensure `capture_id` is stable for entire capture
- [ ] Enforce `record_id` uniqueness per control message (message identity only)
- [ ] Do not generate `session_id`, `capture_id`, or `record_id` in this module

---


---

## D) Forwarding Boundary (Repository)

- [ ] Implement bounded async queue per capture
- [ ] Enforce:
  - [ ] `max_forward_buffer_frames`
  - [ ] `max_forward_buffer_bytes`
- [ ] On overflow → surface `LimitForwardBufferExceeded`
- [ ] On downstream failure → surface `ForwardFailed`
- [ ] Ensure:
  - [ ] No disk writes
  - [ ] No schema_recorder imports
  - [ ] No cross-app repository imports
- [ ] Cleanup:
  - [ ] cancel forwarding task
  - [ ] drain queue
  - [ ] release buffers

---


## E) WebSocket Route Layer

- [ ] Implement `WS /camera_feed_worker/capture`
- [ ] Parse and validate JSON control messages against `CameraFeedWorkerInput`
- [ ] Accept WS binary frame bytes (JPEG) immediately after matching `capture.frame_meta`
- [ ] Maintain connection-local ephemeral state
- [ ] Call service handlers
- [ ] Map domain errors to:
  - Emit `CameraFeedWorkerOutput(event="capture.abort", capture_id, error_code)`
  - correct WebSocket close code
- [ ] Integrate session validation:
  - [ ] validate at `capture.open`
  - [ ] re-check every 5s during active capture
- [ ] Ensure:
  - [ ] No persistence
  - [ ] No business logic duplication
  - [ ] No ID generation
---

## F) Route Migration (Deep Import Removal)

- [ ] Rewrite `api/routes/camera_feed_worker_routes.py`
  - import schemas only via `from schemas import ...`
  - delegate to canonical router
  - contain no endpoint logic
- [ ] Ensure router mounted only once

---

## G) Tests



### Repository Tests
- [ ] Buffer overflow
- [ ] Forward failure propagation
- [ ] Cleanup correctness

### WebSocket Route Tests
- [ ] Happy path capture
- [ ] Protocol violation abort
- [ ] Limit violation abort
- [ ] Session invalid on open
- [ ] Session closed mid-capture
- [ ] Correct close codes


### Guardrail Tests
- [ ] No deep schema imports in shim
- [ ] Required schemas exported in `schemas.__all__`
- [ ] Shim contains no route logic
- [ ] No filesystem writes in app
- [ ] No schema_recorder repository imports
- [ ] Control messages validate required fields by `event` (open/meta/close)
- [ ] Ensure no schema includes frame bytes or base64 image fields


---

## H) Smoke Verification

- [ ] App boots cleanly
- [ ] WebSocket route registered
- [ ] Basic connect succeeds

## WebSocket Streaming Integration (Pre-Classifier Gate)

- [ ] Implement internal tick loop per WebSocket connection
  - [ ] Periodic call to `dispatch(..., "tick", ...)`
  - [ ] Ensure single-writer semantics for state mutation
  - [ ] Cancel tick task cleanly on disconnect
  - [ ] Abort + cleanup on timeout-triggered errors
- [ ] Remove reliance on HTTP `capture.tick` for safety enforcement
- [ ] Verify duration guard, idle timeout, and meta→bytes timeout fire autonomously
- [ ] Only after above is complete:
  - [ ] Enable frame forwarding to classifier

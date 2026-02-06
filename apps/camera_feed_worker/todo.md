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
- [ x] `capture.open` from Idle → Active
- [ x] `capture.open` from Active → abort + cleanup
- [ x] `capture.close` from Idle → ProtocolViolation
- [x ] Unknown event_kind → ProtocolViolation

### 2. Protocol Sequencing
- [ x] `frame_meta` with correct `seq` accepted
- [x ] `frame_meta` with wrong `seq` → abort
- [x ] `frame_meta` when `pending_meta` exists → abort
- [x ] `frame_bytes` without `pending_meta` → abort
- [x ] `frame_bytes` with mismatched byte_length → abort
- [x ] `capture.close` with `pending_meta` present → abort

### 3. Timestamp Ordering
- [x ] `timestamp_frame` < `last_frame_timestamp` → abort
- [ x] `timestamp_end` < `timestamp_start` → abort
- [x ] `timestamp_end` < `last_frame_timestamp` → abort

### 4. Duration Enforcement
- [ x] Ingest-time duration exceeded during `tick` → abort
- [ x] Event-time duration exceeded on `capture.close` → abort
- [x ] Valid duration close returns Idle + CleanupCapture

### 5. Frame / Byte Limits
- [ x] Frame count exceeds `MAX_FRAMES` → abort
- [x ] Single frame exceeds `MAX_FRAME_BYTES` → abort
- [ x] Total bytes exceed `MAX_TOTAL_BYTES` → abort
- [ x] Valid frame increments counters correctly

### 6. Timeout Handling (handle_tick)
- [ ] Meta→bytes timeout (>2s) → abort
- [ ] Idle timeout (>5s no meta) → abort
- [ ] No timeout within limits → remain Active

### 7. Session Re-check Emission
- [x ] `tick` before 5s → no recheck
- [xx ] `tick` at ≥5s → emit `RequestSessionRecheck`
- [ ] Recheck timestamp updates after emission

### 8. Abort Semantics (dispatch)
- [ x] Any CameraFeedWorkerError in ActiveState → returns IdleState
- [ x] AbortCapture action emitted with correct error_code
- [x ] CleanupCapture action emitted with correct capture_id
- [x ] Error in IdleState is re-raised (no abort wrapper)

### 9. Happy Path Integration
- [x ] Full valid flow:
      open → meta → bytes → close
      → ends in IdleState
      → emits ForwardFrame(s)
      → emits CleanupCapture


---




## C) Identity & Correlation Enforcement

- [x ] Enforce required IDs on `capture.open`
  - `user_id`
  - `session_id`
  - `capture_id`
- [x ] Reject missing `capture_id`
- [ x] Ensure `capture_id` is stable for entire capture
- [x ] Enforce `record_id` uniqueness per control message (message identity only)
- [ x] Do not generate `session_id`, `capture_id`, or `record_id` in this module

---


---

## D) Forwarding Boundary (Repository)

- [x ] Implement bounded async queue per capture
- [ x] Enforce:
  - [x ] `max_forward_buffer_frames`
  - [x ] `max_forward_buffer_bytes`
- [x ] On overflow → surface `LimitForwardBufferExceeded`
- [ ] On downstream failure → surface `ForwardFailed`
- [ x] Ensure:
  - [x ] No disk writes
  - [x ] No schema_recorder imports
  - [x ] No cross-app repository imports
- [x ] Cleanup:
  - [ x] cancel forwarding task
  - [ x] drain queue
  - [ x] release buffers

---


## E) WebSocket Route Layer — Revised Execution Order

- [ x] Implement `WS /camera_feed_worker/capture`
- [x ] Parse and validate JSON control messages (`CameraFeedWorkerInput`)
- [ x] Maintain connection-local ephemeral state
- [ x] Call service handlers (`dispatch()`) for control-plane events
- [ x] Define and enforce domain error → abort emit + close code mapping
- [x ] Accept WS binary frame bytes immediately after matching `capture.frame_meta`

# camera_feed_worker — Remaining MVP TODO (session recheck + self-ticking + invariants)



## 1) Re-check session every 5s during active capture (demo-correct)

- [x ] Ensure session recheck enforcement happens ONLY in WS loop via `_tick_and_enforce_session()`
- [ x] Remove/disable `/capture.tick` session enforcement:
  - [x ] do not call `validate_session()`
  - [ x] do not mutate `active_capture_id`
  - [x ] do not attempt abort semantics
- [ x] Confirm there is exactly ONE recheck path in the system (WS loop only)

---

## 2) Make WS loop self-ticking (so recheck works when client is silent)

- [ x] Update `_ws_control_plane_loop` to use `receive()` with timeout
- [x ] On timeout:
  - [ x] run `_tick_and_enforce_session(...)`
  - [ x] continue loop (no protocol error)
  - [x ] close only if tick emits abort
- [x ] Ensure timeout does NOT:
  - [x ] reset `expecting_binary`
  - [x ] clear `expected_byte_length`
  - [x ] mutate capture correlation
- [ x] Acceptance:
  - [ x] with a silent client, session recheck occurs ≤ 5s
  - [x ] idle timeout still triggers correctly
  - [ x] meta→bytes timeout still triggers correctly
  - [ x] ingest-time duration limit still triggers correctly

---

## 3) Abort correctness (prevent empty/incorrect capture_id)

- [ x] In `_tick_and_enforce_session()`, derive `capture_id` from domain state (`ActiveState.capture_id`) not `repo.get_active_capture_id()`
- [ x] Ensure no path can emit `capture.abort` with empty `capture_id`
- [x] Ensure abort semantics remain:
  - [x ] emit `capture.abort`
  - [x ] clear correlation
  - [ x] close websocket deterministically

---

## 4) Internal consistency guard (no split-brain state)

- [ x] Ensure no path can yield `ActiveState` while `repo.active_capture_id is None`
  - [x ] remove any “soft abort” patterns that only clear `active_capture_id`
- [ ]x Re-validate that all cleanup paths clear:
  - [x ] binary gate (`expecting_binary`, `expected_byte_length`)
  - [x ] correlation (`active_capture_id`)
  - [ x] connection-local state on disconnect

---

## 5) Binary gating regression check (no expansion, only verification)

- [ x] Confirm `capture.frame_meta` arms binary gate only AFTER domain accepts it
- [x ] Confirm text frame is rejected when `expecting_binary == True`
- [ x] Confirm byte-length mismatch triggers protocol close
- [ ] Confirm gate clears on:
  - [ x] successful byte consumption
  - [ x] abort path
  - [ x] protocol violation
  - [x ] disconnect
  - [x ] unexpected exception

---

## 6) Final invariants pass (for this scope)
# camera_feed_worker — Final Invariants Pass (Sprint 1E)

## 1) No persistence in this module
- [ x] Confirm no file writes (`open`, `Path`, `jsonl`)
- [x ] Confirm no DB usage (sqlite, sqlalchemy, alembic)
- [x ] Confirm no network calls (requests, httpx)
- [ x] Confirm no schema_recorder imports

---

## 2) No business logic duplication
- [x ] Confirm all protocol / limit / timeout rules exist only in `service.py`
- [ x] Confirm `routes/router.py` only:
      - parses transport
      - calls `dispatch`
      - executes returned actions
- [x ] Confirm no MAX_*, limit, duration, or sequencing logic in routes

---
# Camera Feed Worker – Invariants & ID Discipline (Actionable TODO Only)

Scope: ingest boundary + protocol enforcement + per-frame forwarding only.
No inference logic. No UI logic. No persistence.

---

## 3) No ID generation (except `connection_key`)

### A) Hard rule enforcement
- [x ] Remove fallback `uuid.uuid4()` usages for `record_id` in abort emission paths (router)
- [ x] Confirm `record_id` is NEVER generated here (only validated/propagated)
  - `session_id` and `capture_id` already confirmed not generated
- [ x] Verify `connection_key = uuid.uuid4()` is the only allowed ID generation

### B) Abort emission policy (demo-robust)
- [ x] Emit `capture.abort` ONLY if a propagated `record_id` is available
- [ ] If abort required but no valid propagated `record_id` exists:
  - [x ] Close socket deterministically (no abort JSON, no synthetic IDs)
  - [x ] Enforce close code convention:
        - 1008 → protocol/client violation
        - 1011 → invariant/internal breach

### C) State robustness
- [ ] Persist propagated `record_id` in `ActiveState` on `capture.open`
- [ ] Ensure tick/session-triggered aborts use state-held IDs only
      (remove dependence on `last_msg_for_emit` fallbacks)

### D) Verification (regression guard)
- [ ] Search codebase to confirm zero ID fabrication beyond `connection_key`
- [ ] Add/adjust tests:
  - [ ] No synthetic `record_id` appears in abort emissions
  - [ ] Socket closes (no abort emission) when abort occurs without valid propagated IDs
- [ ] Document invariant:
      camera_feed_worker validates & propagates IDs only; never generates them

---

## 4) Domain state is single source of truth

- [ ] Decide and document:
      keep `repo.active_capture_id` as demo guardrail
      OR remove and rely purely on `ActiveState`

---

## 5) Forwarding Boundary (Per-Frame, Locked)

Per-frame forwarding to `landmark_extractor` remains the contract.

- [ ] Confirm forward item includes:
      - `capture_id`
      - `seq`
      - `timestamp_frame` (event-time)
      - JPEG `bytes` (memory-only)
      - declared `encoding`
      - declared dimensions (from open)
- [ ] Ensure queue limits enforce:
      - max forward buffer frames
      - max forward buffer bytes
- [ ] On forward overflow → surface `LimitForwardBufferExceeded`
- [ ] On downstream failure → surface `ForwardFailed`
- [ ] Ensure abort/cleanup:
      - cancels forwarding task
      - drains queue
      - clears correlation
      - releases buffers
- [ ] Add repository-level tests:
      - buffer overflow
      - downstream failure propagation
      - cleanup correctness

---

## F) Route Migration (Deep Import Removal)

- [ ] If legacy `api/routes/camera_feed_worker_routes.py` still exists:
      delete or mark deprecated to prevent regression

- [ ] Add guardrail tests:
      - no deep schema imports
      - required schemas exported in `schemas.__all__`
      - shim contains no route logic
      - no filesystem writes in app
      - no schema_recorder imports
      - control messages validate required fields by `event`
      - no schema includes frame bytes/base64 fields

---

## G) WebSocket Route Tests

- [ ] Happy path capture
- [ ] Protocol violation abort
- [ ] Limit violation abort
- [ ] Session invalid on open
- [ ] Session closed mid-capture
- [ ] Correct close codes

---

## H) Smoke Verification

- [ ] App boots cleanly
- [ ] WebSocket route registered
- [ ] Basic connect succeeds

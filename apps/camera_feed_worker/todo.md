# camera_feed_worker — Sprint 1 TODO (Actionable Only)

---

## A0) Schemas

- [ ] Replace/deprecate legacy `camera_feed_worker` schemas
- [ ] Define Sprint 1 control-plane schemas:
  - `CameraFeedWorkerInput` (event-discriminated superset: open / frame_meta / close)
  - `CameraFeedWorkerOutput` (`capture.abort` only)
- [ ] Update domain spec: use `timestamp_frame` (not `timestamp`) for frame event-time



## A) App Skeleton

- [ ] Create `apps/camera_feed_worker/`
- [ ] Create:
  - [ ] `routes/__init__.py`
  - [ ] `routes/router.py`
  - [ ] `service.py`
  - [ ] `repository.py`
  - [ ] `tests/`

- [ ] Mount router in `api/main.py`
  - Ensure single registration only

---
## B) Service Layer (Pure Domain Logic)

Implement state machine + limit enforcement per domain spec.

- [ ] Implement state model (`idle`, `active`)
- [ ] Implement handlers:
  - [ ] `handle_open`
  - [ ] `handle_frame_meta`
  - [ ] `handle_frame_bytes`
  - [ ] `handle_close`
  - [ ] `handle_tick`
- [ ] Implement:
  - [ ] ordering validation
  - [ ] timestamp validation
  - [ ] limit accounting (frames, bytes, duration)
  - [ ] timeout detection
  - [ ] session re-check trigger emission
- [ ] Ensure service raises typed domain errors only
- [ ] Ensure service has zero FastAPI imports
- [ ] Ensure service performs no IO



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

### Service Tests
- [ ] Protocol sequencing
- [ ] Timestamp ordering
- [ ] Duration enforcement
- [ ] Frame/byte limits
- [ ] Timeout handling
- [ ] Session re-check emission

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

# TODO — camera_feed_worker → landmark_extractor Terminal Integration

## Objective
Enable deterministic bounded-capture finalization in `landmark_extractor`.

Invariant:
One `capture_id` → many frame ingest messages → exactly one terminal ingest message.

---

## 1. Emit Terminal Ingest Message (Required)

### On `capture.close`
- [ ] Build `LandmarkExtractorTerminalInput`
  - event = "capture.close"
  - capture_id
  - user_id
  - session_id
  - timestamp_end
- [ ] Deliver to landmark_extractor ingest boundary
- [ ] Ensure delivery occurs **before** forwarding task is cancelled

### On `capture.abort`
- [ ] Build `LandmarkExtractorTerminalInput`
  - event = "capture.abort"
  - capture_id
  - user_id
  - session_id
  - timestamp_end
  - error_code
- [ ] Deliver to landmark_extractor ingest boundary
- [ ] Ensure delivery occurs **before** forwarding task is cancelled

---

## 2. Forwarder Boundary Adjustments

- [ ] Update forwarder ingest function type to accept:
  - `LandmarkExtractorFrameInput`
  - `LandmarkExtractorTerminalInput`
- [ ] Ensure discriminated union validation works at runtime
- [ ] Confirm terminal message is not dropped during shutdown

---

## 3. Exactly-Once Semantics

- [ ] Guarantee only one terminal ingest per `capture_id`
- [ ] Prevent duplicate terminal emissions on retry paths
- [ ] Add guard test for duplicate terminal message prevention

---

## 4. Tests (Minimum Required)

- [ ] Close path emits terminal ingest exactly once
- [ ] Abort path emits terminal ingest exactly once
- [ ] Terminal ingest delivered before forwarder cancellation
- [ ] No terminal → landmark_extractor does not finalize
- [ ] Duplicate terminal attempt → rejected or ignored deterministically

---

## 5. Not Required (Do Not Change)

- [ ] No change to camera service state machine
- [ ] No change to `ForwardFrame` structure
- [ ] No change to `record_id` semantics
- [ ] No change to schema_recorder
- [ ] No change to per-frame forwarding logic

---

## Acceptance Criteria

landmark_extractor receives:
- N frame ingest messages (same `capture_id`)
- Exactly 1 terminal ingest message (close or abort)

This guarantees:
- Exactly 1 NPZ artifact per capture
- Exactly 1 feature-ref A3CPMessage per capture
- Deterministic replay and integrity enforcement

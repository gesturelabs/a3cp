# TODO — camera_feed_worker → landmark_extractor Terminal Integration (Remaining Work)

## 1) Wire Real Ingest Boundary (stub now, extractor later)
- [x ] Replace `_noop_landmark_ingest` in WS routes with a real **ingest boundary** function (stub implementation acceptable).
- [x ] Ensure ingest boundary performs runtime union validation for:
  - `LandmarkExtractorFrameInput`
  - `LandmarkExtractorTerminalInput`

- [ ] Canonicalize ingest failure handling
  - Ensure `_ingest_or_abort_on_failure` is the single ingest failure path
  - Remove duplicate abort logic triggered by ingest failures
  - Guarantee exactly one terminal emission on ingest failure

---

## 2) Fix `capture.close` State Bug
- [x] Build terminal message from pre-dispatch `ActiveState`, not post-dispatch state.
- [ ] Enforce canonical terminal ordering
  - Ensure terminal ingest occurs before forwarder shutdown
  - Ensure `repo.mark_terminal_emitted` occurs immediately after successful ingest
  - Ensure `repo.stop_forwarding` runs before socket close
  - Remove ordering differences between close and abort paths

---

## 3) Fix Binary-Phase Forward Failure Path
- [ ] Verify binary-phase forward failure uses the real ingest boundary
- [ ] Add one test for binary-phase forward failure exactly-once terminal emission
  - Prove only one terminal ingest message is produced
  - Prove no duplicate terminal is emitted on retry/failure paths

---

## 4) Canonicalize Abort Handling
- [ ] Review remaining abort paths and document exceptions
  - Keep `_emit_abort_and_close` as the preferred path
  - Only refactor additional abort paths if tests or behavior show inconsistency
- [ ] Remove only duplicated terminal emission logic that causes inconsistent behavior

---

## 5) Clarify Multi-Capture Semantics per WS
- [ ] Decide: allow multiple captures per WS or not.
- [ ] If yes: reset `terminal_emitted` on `capture.open`.
- [ ] If no: enforce protocol violation on second open.

---

## 6) Forwarder/Queue Boundary Support (if forwarding is used)
- [ ] Ensure forwarder ingest path accepts both frame + terminal inputs (same union as ingest boundary).
- [ ] Ensure terminal is not dropped during shutdown/cancel.

---

## 7) Tests (Lock Invariants)
- [ ] Close path emits exactly one terminal (before cancellation).
- [ ] Abort path emits exactly one terminal (before cancellation).
- [ ] Binary forward failure emits terminal.
- [ ] Duplicate terminal attempts are rejected/ignored.
- [ ] No terminal → extractor does not finalize (integration test later; for now: boundary sink shows no finalize trigger).







-------

# TODO — camera_feed_worker → landmark_extractor Terminal Integration

## Objective
Enable deterministic bounded-capture finalization in `landmark_extractor`.

Invariant:
One `capture_id` → many frame ingest messages → exactly one terminal ingest message.

---

## 1. Emit Terminal Ingest Message (Required)

### On `capture.close`
- [x ] Build `LandmarkExtractorTerminalInput`
  - event = "capture.close"
  - capture_id
  - user_id
  - session_id
  - timestamp_end
- [ ] Deliver to landmark_extractor ingest boundary
- [x ] Ensure delivery occurs **before** forwarding task is cancelled

### On `capture.abort`
- [x ] Build `LandmarkExtractorTerminalInput`
  - event = "capture.abort"
  - capture_id
  - user_id
  - session_id
  - timestamp_end
  - error_code
- [ ] Deliver to landmark_extractor ingest boundary
- [ x] Ensure delivery occurs **before** forwarding task is cancelled

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


---

## Acceptance Criteria

landmark_extractor receives:
- N frame ingest messages (same `capture_id`)
- Exactly 1 terminal ingest message (close or abort)

This guarantees:
- Exactly 1 NPZ artifact per capture
- Exactly 1 feature-ref A3CPMessage per capture
- Deterministic replay and integrity enforcement




----------

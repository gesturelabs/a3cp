# TODO — camera_feed_worker → landmark_extractor Terminal End-of-Capture (MVP)

## Objective
Guarantee deterministic bounded-capture finalization.

### Core invariant
One `capture_id`:
- `N` frame ingest messages
- exactly `1` terminal ingest message

### Valid terminal events
- `capture.close`
- `capture.abort`

---

## 1) Schema Alignment

- [x] Convert `ForwardItem.capture_id` to UUID in `forward_adapter.py`
  - `capture_id = uuid.UUID(item.capture_id)`

---

## 2) Verify Terminal Delivery (Tests)

- [x ] Test: `capture.close` delivers exactly one terminal ingest message to the `landmark_extractor` ingest boundary
- [ x] Test: `capture.abort` delivers exactly one terminal ingest message to the `landmark_extractor` ingest boundary
- [ x] Test: binary forward failure delivers exactly one terminal ingest message

---

## 3) Exactly-Once Semantics (Tests)

- [x ] Test: duplicate terminal attempts do not produce a second terminal ingest message
- [ x] Test: terminal emission is guarded by `repo.has_emitted_terminal`

---

## 4) Ordering Guarantee (Tests)

Required ordering:

1. terminal ingest
2. `repo.mark_terminal_emitted`
3. `repo.stop_forwarding`
4. `websocket.close`

Tests:

- [ x] Verify terminal ingest occurs before forwarder shutdown
- [ x] Verify terminal ingest is not dropped during cancellation
- [x] Verify terminal emission guard consumes the terminal slot even if ingest fails
  - terminal ingest is attempted once
  - `repo.mark_terminal_emitted` is called even on ingest failure
  - prevents duplicate terminal emission attempts

---

## Acceptance Criteria (MVP)

For each completed capture, `landmark_extractor` receives:

- `N` frame ingest messages with the same `capture_id`
- at most `1` terminal ingest message (`capture.close` or `capture.abort`)

This guarantees:

- no duplicate terminal signals
- deterministic capture shutdown
- bounded-capture finalization when terminal delivery succeeds

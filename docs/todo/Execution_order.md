# Execution Order — Gesture Slice (Recommended)

This list defines the **implementation order** for module TODOs.
The ordering minimizes rework, maximizes observability, and respects slice contracts.

---

## 1) schema_recorder (first)

Goal: establish the authoritative append-only session log spine.


Rationale: all downstream modules depend on a stable, observable session log.

---


session_manager


## 2) ui — Session surface (`/demo/session`)

Goal: exercise session lifecycle end-to-end with minimal UI.

- [ ] Start Session UI
- [ ] End Session UI
- [ ] In-memory session state only
- [ ] Error rendering

Rationale: provides fast feedback that session + recorder wiring works.

---

## 3) camera_feed_worker

Goal: ingest bounded capture windows reliably.

- [ ] Implement bounded capture lifecycle
- [ ] WebSocket (or chosen transport) handling
- [ ] Session + record_id propagation
- [ ] No raw video persistence (Sprint 1 rule)

Rationale: defines the data ingress boundary for gesture input.

---

## 4) landmark_extractor

Goal: produce landmark-derived feature artifacts.

- [ ] Consume bounded capture windows
- [ ] Generate `(T, D)` feature arrays
- [ ] Persist feature artifacts only
- [ ] Emit feature-ref metadata for recorder

Rationale: heavy dependencies; should be built only after ingress is stable.

---

## 5) ui — Gesture surface (`/demo/gesture`)

Goal: complete the demo loop for gesture capture.

- [ ] Start / stop capture controls
- [ ] Display session_id, record_id, status
- [ ] Show latest artifact ref/hash
- [ ] Enforce capture window limits

Rationale: UI is expanded only once backend behavior exists.

---

## Summary

Build order:
1. schema_recorder
2. ui (session)
3. camera_feed_worker
4. landmark_extractor
5. ui (gesture)

This order aligns with slice contracts, exit gates, and audit-first design.

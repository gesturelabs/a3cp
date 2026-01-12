# Gesture Slice — Architectural Contract

This document defines **architectural constraints** for the Gesture Slice.
It is normative for this slice and must be respected by all participating modules.

These rules are **slice-scoped**, not global, and do not apply outside
the Gesture Slice unless explicitly referenced.

---

## Ground rules

- Schemas are treated as **frozen** during this slice.
  - Changes are permitted only to resolve a hard blocker.

- All events are **append-only**.
  - In-place edits or mutations are forbidden.

- Every downstream module interaction must carry explicit identifiers:
  - `user_id`
  - `session_id`
  - `timestamp`
  - `record_id`

- **Log-writing authority**:
  - Only `recorded_schemas` may append to:
    ```
    logs/users/<user_id>/sessions/<session_id>.jsonl
    ```

---

## Relationship to other documents

- Module TODOs must comply with this contract.
- Exit criteria are defined separately (see `EXIT_GATES.md`).
- This document does not define implementation steps.


## Storage policy (Sprint 1 — locked)

- Do **not** persist raw video frames or streams to disk.
- Persist **only** landmark-derived feature artifacts (e.g., `(T, D)` arrays)
  and their `raw_features_ref` metadata recorded in session JSONL:
  - `uri`
  - `sha256`
  - `encoding`
  - `dims`
  - `format`
---

## Status

This contract is authoritative for the Gesture Slice and may be retired
or replaced when the slice is complete.

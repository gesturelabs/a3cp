# apps/schema_recorder/TODO.md

A3CP — schema_recorder TODO (module-scoped)

Purpose: provide the **only allowlisted writer utility** for session JSONL:
- `logs/users/<user_id>/sessions/<session_id>.jsonl`

Invariant (authoritative): **Only `schema_recorder` writes/appends** to
`logs/users/**/sessions/*.jsonl`.
All semantic guarantees about *what* is written are enforced upstream.

## Correctness checks (recorder-scoped; enforce at write time when refs exist)

- [ ] Event replay / duplication protection for recorder writes:
  - [ ] Reject appending the same logical event twice for the same `(user_id, session_id, record_id, source)` tuple (strategy must be explicit)
  - [ ] If an artifact ref includes `sha256`, detect duplicate replays within a session and flag/reject per policy

- [ ] Minimal artifact-ref sanity checks (only on the ref metadata; do not re-derive features):
  - [ ] If `raw_features_ref.dims` is present, validate the metadata is internally consistent (non-empty, positive ints)
  - [ ] If a feature artifact header/manifest is available cheaply, validate that declared dims match the referenced artifact metadata
    - Note: full `(T, D)` validation belongs to the artifact producer; recorder validates only what it can verify at write time

- [ ] “One capture → one feature-ref event” enforcement (session log semantics):
  - [ ] For each `record_id`, enforce exactly one feature-ref append event in the session JSONL (idempotent behavior must be defined)

- [ ] Reproducibility / determinism note (documentation + tests, recorder-facing):
  - [ ] Document that determinism guarantees apply only within the same build/container tag
  - [ ] Add an integration test that asserts stable recorder behavior across repeated runs in the same build (where applicable)

---

## A) Canonical compliance (required)

### 1) Fix deep schema import
- [ ] Update `apps/schema_recorder/session_writer.py` to import schemas only via public surface:
  - from: `schemas.schema_recorder.schema_recorder import RecorderConfig`
  - to: `from schemas import RecorderConfig`
- [ ] Export `RecorderConfig` from `schemas/__init__.py` and include it in `__all__`.

### 2) Import-policy guardrails
- [ ] Module-scoped test: fail if `apps/schema_recorder/**` deep-imports `schemas.<submodule>`.
- [ ] Public-schema presence test: `from schemas import RecorderConfig` succeeds.

## Filesystem & Runtime config (authoritative helpers)

- [ ] Define runtime roots (single source of truth):
  - [ ] `DATA_ROOT = env("DATA_ROOT", default="./data")`
  - [ ] `LOG_ROOT  = env("LOG_ROOT",  default="./logs")`

- [ ] Expose path helpers (helpers may mkdir; callers must not hand-roll paths):
  - [ ] `session_log_path(user_id, session_id)`
        → `<LOG_ROOT>/users/<user_id>/sessions/<session_id>.jsonl`
  - [ ] `session_features_dir(user_id, session_id)`
        → `<DATA_ROOT>/users/<user_id>/sessions/<session_id>/features/`
    - Note: if artifact writing later moves to another module, this helper may be relocated; for MVP it lives here.

- [ ] Runtime config examples:
  - [ ] Local: `DATA_ROOT=./data`, `LOG_ROOT=./logs`
  - [ ] Docker: `DATA_ROOT=/data`, `LOG_ROOT=/logs`

---

## B) Session JSONL writer allowlist (required)

### 1) Single-writer enforcement
- [ ] CI/static-scan test: fail if any code outside the allowlisted writer writes/appends to:
  - `logs/users/**/sessions/*.jsonl`
- [ ] Allowlist exactly:
  - `apps/schema_recorder/session_writer.py`

### 2) Cross-module usage contract
- [ ] Confirm other modules *only* append session events by calling this writer utility:
  - session_manager (session start/end)
  - landmark_extractor (feature-ref event)
  - future modules (same rule)

---

## C) What this module DOES guarantee (documented behavior)

- [x] Append-only writes (no edits, no rewrites).
- [x] Exactly one JSON object per line (JSONL).
- [x] Log path resolved at call time (respects runtime `LOG_ROOT`).
- [x] Writer accepts already-validated, JSON-serializable schema objects.

---

## D) What this module DOES NOT guarantee (explicitly out of scope)

These guarantees must be enforced and tested **upstream** (e.g. in `landmark_extractor`):

- [ ] “Exactly one event per bounded capture (`record_id`)”
- [ ] Enforcement of `source`, `modality`, or required field values
- [ ] Prevention of per-frame / per-chunk event emission
- [ ] Detection of duplicate `record_id` entries
- [ ] Semantic correctness of `raw_features_ref` contents

The writer will append whatever valid schema object it is given.

---

## E) Alignment with slice requirement (reference)

Slice rule (implemented jointly, not solely here):
> For each completed bounded capture (`record_id`), emit **exactly one**
> A3CPMessage and append it via this writer utility.

This module fulfills the **append-only writer** role only; correctness is ensured
by service-level logic and guardrail tests in upstream modules.

---

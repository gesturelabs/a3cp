# apps/landmark_extractor/TODO.md

A3CP — landmark_extractor TODO (module-scoped)

Scope for this slice (authoritative): gesture-only landmark feature extraction from a **bounded capture** (identified by `capture_id`) and emission of **exactly one** feature-ref A3CPMessage per capture via `schema_recorder`.

Legacy spec assessment (non-authoritative; see §H):
- Several parts of the pasted legacy spec conflict with the bounded-capture architecture (per-frame semantics, modality/source values, file format examples, module type, and responsibilities around logging). This TODO follows the slice plan below as authoritative.

---

## Module invariants (locked)

- Input comes from `camera_feed_worker` during an active capture (`capture_id`) plus a terminal signal.
- **One bounded capture** → **one `capture_id`** → **one feature artifact** → **exactly one** session JSONL event (with its own unique `record_id`).
- Persist only landmark-derived features (no raw video persistence).
- Feature artifact is the primary output: dense float32 NPZ `(T, D)` plus `raw_features_ref`.
- **Do NOT classify** (feature extraction only).
- Session JSONL writing rule: only `schema_recorder` appends to:
  - `logs/users/<user_id>/sessions/<session_id>.jsonl`
- Routes import schemas only via: `from schemas import ...` (no deep imports).

---

- [ ] Schema payload policy (base64/bytes) — tracked in `schemas/TODO.md` (post camera_feed_worker consolidation)

---

## A) Canonical app structure (must be created / migrated)

- [ ] Create app directory:
  - [ ] `apps/landmark_extractor/`

- [ ] Routes layer (FastAPI adapters only):
  - [ ] `apps/landmark_extractor/routes/__init__.py`
  - [ ] `apps/landmark_extractor/routes/router.py`
    - validate request/response schemas
    - call service functions
    - translate domain errors to HTTP responses
    - MUST NOT: business logic, IO, state, ID generation, cross-app deps

- [ ] Service layer (required):
  - [ ] `apps/landmark_extractor/service.py`
    - orchestrates extraction for one bounded capture (`capture_id`)
    - enforces “one artifact per capture”
    - finalizes on explicit terminal signal (`capture.close` / `capture.abort`)
    - calls repository for IO (feature file write) and schema_recorder for append

- [ ] Repository layer (expected):
  - [ ] `apps/landmark_extractor/repository.py`
    - MediaPipe Holistic execution boundary (frame→landmarks)
    - feature artifact persistence (NPZ write)
    - sha256 computation over NPZ bytes
    - replay/load helper(s)

- [ ] Optional components:
  - [ ] `config.py`
  - [ ] `models.py`
  - [ ] `domain.py`

- [ ] Tests:
  - [ ] `apps/landmark_extractor/tests/`
    - service-level tests
    - thin route tests

---

## B) Feature extraction + artifact writing

### 1) Input contract

- [ ] Receive per-frame inputs during active capture including:
  - `user_id`
  - `session_id`
  - `capture_id`
  - `seq`
  - `timestamp_frame`
  - `frame_data`
- [ ] Receive terminal control message:
  - `capture.close` or `capture.abort`
  - includes `capture_id`, `timestamp_end`
- [ ] Process frames incrementally but finalize only on terminal signal
- [ ] No per-frame schema events

### 2) Feature artifact

- [ ] Convert frames to Holistic landmark features (gesture only)
- [ ] Produce one feature artifact per bounded capture (`capture_id`)
- [ ] Persist features as float32 NPZ `(T, D)`
- [ ] Write to:
  - `data/users/<user_id>/sessions/<session_id>/features/<capture_id>.npz`
- [ ] Compute sha256 over NPZ bytes
- [ ] Resolve paths via runtime roots (no hardcoded paths)

### 3) raw_features_ref

- [ ] Build `raw_features_ref` with:
  - `uri`
  - `hash`
  - `format="npz"`
  - `dims=D`
  - `encoding="holistic_landmarks_v1;fps=...;max_window_s=...;extractor_tag=..."`

### 4) Determinism

- Same input bytes + same code revision/container tag ⇒ identical feature bytes + sha256
- No cross-version byte identity requirement

---

## C) Schema recording

- [ ] For each completed bounded capture (`capture_id`), emit exactly one A3CPMessage:
  - `source="landmark_extractor"`
  - includes `user_id`, `session_id`, `capture_id`
  - includes a new unique `record_id` (event-scoped)
  - includes `raw_features_ref`
  - `modality="gesture"`
- [ ] Append via `schema_recorder.service.append_event()` only
- [ ] Before append, verify no existing feature-ref event for this `capture_id`
- [ ] No per-frame schema events
- [ ] Session JSONL remains append-only

---

## D) Guardrails & replay proof

- [ ] Verify artifact exists at `raw_features_ref.uri`
- [ ] Recompute sha256 and verify match
- [ ] Load NPZ and confirm `(T, D)` and `D == dims`
- [ ] Verify exactly one feature-ref event per `capture_id`
- [ ] Provide replay helper (load by `capture_id`)
- [ ] Tests for:
  - missing artifact
  - hash mismatch
  - dims mismatch
  - duplicate feature-ref event

---

## E) Route Re-Migration

- [ ] Identify legacy route(s)
- [ ] Ensure schemas exported via `schemas/__init__.py`
- [ ] Update shim route to import only from `schemas`
- [ ] Delegate to `apps/landmark_extractor/routes/router.py`
- [ ] Add deep-import guard test
- [ ] HTTP smoke test (may return 501)

---

## F) CI guardrails

- [ ] Enforce public schema surface usage
- [ ] Fail if module writes directly to `logs/users/**`
- [ ] Static-scan test for JSONL writes outside schema_recorder

---

## G) Exit gate

- [ ] Load artifact by `capture_id`
- [ ] Verify sha256 integrity
- [ ] Confirm `(T, D)` matches metadata
- [ ] After restart (same build), replay produces identical bytes + sha256
- [ ] Session JSONL contains exactly one feature-ref event per `capture_id`

---

## H) Legacy spec assessment

Deprecated:
- Per-frame schema emissions
- Classification logic
- Non-NPZ formats
- Incorrect modality/source fields

Locked:
- `modality="gesture"`
- `source="landmark_extractor"`
- `format="npz"`
- `raw_features_ref.encoding` must include extractor + params + container tag

---

## I) Real-Time Landmark Streaming (Demo Only)

- [ ] Provide per-frame landmark results to UI
- [ ] No session JSONL appends
- [ ] No raw video persistence
- [ ] Stream payload:
  - `capture_id`
  - `seq`
  - `timestamp_frame`
  - `landmarks`
- [ ] WS endpoint: `/landmark_extractor/ws`
- [ ] Bounded backpressure
- [ ] Stop streaming on capture end/abort
- [ ] Tests:
  - WS streaming
  - bounded queue
  - no extra schema events

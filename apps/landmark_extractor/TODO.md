# apps/landmark_extractor/TODO.md



# 1. Lock scope and invariants

- [ ] Confirm module scope: bounded-capture gesture feature extraction
- [ ] Confirm pipeline model: `capture.frame × N → terminal event → artifact + event`
- [ ] Confirm success rule: `capture.close` writes `.npz` and appends one `A3CPMessage`
- [ ] Confirm abort rule: `capture.abort` writes nothing and clears capture state
- [ ] Confirm logging rule: session JSONL writes only through `schema_recorder.append_event`
- [ ] Confirm persistence rule: persist landmark-derived features only (no raw frames)
- [ ] Confirm extraction backend: MediaPipe Holistic
- [ ] Confirm artifact format: `.npz` feature matrix `(T, D)`
- [ ] Confirm schema emission rule: exactly one feature-ref event per successful capture
- [ ] Confirm non-goals for MVP: no classification, no replay helpers, no streaming, no CI guardrails

# Artifact storage rule (MVP)

- [ ] Confirm feature artifacts are stored under:
  - [ ] `data/users/<user_id>/sessions/<session_id>/features/<capture_id>.npz`
- [ ] Confirm artifact paths are resolved via runtime path utilities
- [ ] Confirm `raw_features_ref.uri` points to this stored artifact


# 2. Define internal capture state

- [ ] Define the extractor’s in-memory state model keyed by `capture_id`
- [ ] Define the minimum state fields required for one active bounded capture:
  - [ ] `capture_id`
  - [ ] `user_id`
  - [ ] `session_id`
  - [ ] accumulated feature rows
- [ ] Decide whether frame count is stored explicitly or derived from accumulated rows
- [ ] Define the feature buffer representation for MVP
- [ ] Define what constitutes an “active” capture in extractor state
- [ ] Define the close rule for state:
  - [ ] finalize once
  - [ ] remove state after successful finalize
- [ ] Define the abort rule for state:
  - [ ] discard accumulated rows
  - [ ] remove state without writing artifact
- [ ] Define the minimal invalid-state cases the service must detect

# 3. Define file layout

- [ ] Decide the minimum file set required for MVP
- [ ] Create `apps/landmark_extractor/service.py` for bounded-capture orchestration
- [ ] Create `apps/landmark_extractor/repository.py` for MediaPipe Holistic boundary and artifact IO
- [ ] Create `apps/landmark_extractor/models.py` or `apps/landmark_extractor/domain.py` for internal capture state
- [ ] Create `apps/landmark_extractor/routes/__init__.py`
- [ ] Create `apps/landmark_extractor/routes/router.py` as a thin adapter layer
- [ ] Create `apps/landmark_extractor/tests/` for MVP tests
- [ ] Decide whether `config.py` is needed now or can be deferred
- [ ] Decide whether route files are required in MVP if ingest is initially internal-only


# 4. Define file responsibilities

- [ ] Define `service.py` responsibility:
  - [ ] accept validated `LandmarkExtractorInput`
  - [ ] manage capture lifecycle by `capture_id`
  - [ ] accumulate feature rows across frames
  - [ ] finalize on `capture.close`
  - [ ] discard on `capture.abort`
  - [ ] call repository for extraction and artifact writing
  - [ ] build and append one feature-ref `A3CPMessage`
- [ ] Define `repository.py` responsibility:
  - [ ] decode frame payload
  - [ ] run MediaPipe Holistic
  - [ ] convert landmarks to fixed feature vector
  - [ ] write `.npz` artifact
  - [ ] compute sha256 over written artifact
- [ ] Define `models.py` or `domain.py` responsibility:
  - [ ] represent internal capture state only
- [ ] Define `routes/router.py` responsibility:
  - [ ] thin validation/adapter layer only
  - [ ] no business logic
  - [ ] no direct file writes
  - [ ] no direct JSONL writes
- [ ] Define cross-file rule:
  - [ ] only `schema_recorder.append_event()` may append session JSONL

# 5. Implement ingest orchestration

- [ ] Define the module ingest entrypoint for `LandmarkExtractorInput`
- [ ] Define dispatch behavior by event type:
  - [ ] `capture.frame`
  - [ ] `capture.close`
  - [ ] `capture.abort`
- [ ] Define frame-ingest behavior:
  - [ ] resolve active capture state by `capture_id`
  - [ ] create capture state if this is the first frame for that `capture_id`
  - [ ] call repository to extract one feature row from the frame
  - [ ] append the feature row to the in-memory capture buffer
- [ ] Define close behavior:
  - [ ] require active capture state for `capture_id`
  - [ ] finalize exactly once
  - [ ] trigger artifact write
  - [ ] trigger feature-ref `A3CPMessage` append
  - [ ] clear capture state after successful finalize
- [ ] Define abort behavior:
  - [ ] require active capture state for `capture_id`
  - [ ] discard buffered feature rows
  - [ ] do not write artifact
  - [ ] do not append feature-ref event
  - [ ] clear capture state
- [ ] Define minimal invalid-ingest cases for MVP:
  - [ ] terminal event for unknown `capture_id`
  - [ ] duplicate terminal after cleanup
  - [ ] frame ingest after finalize
  - [ ] frame ingest after abort


  # 6. Implement MediaPipe Holistic extraction boundary

- [ ] Define repository entrypoint for frame → feature extraction
- [ ] Decode `frame_data` from base64 input
- [ ] Convert decoded bytes into an image/frame object suitable for MediaPipe
- [ ] Run MediaPipe Holistic on each ingested frame
- [ ] Decide which landmark groups are included in MVP feature extraction:
  - [ ] pose
  - [ ] left hand
  - [ ] right hand
  - [ ] face
- [ ] Define the MVP feature-row encoding:
  - [ ] fixed-length per frame
  - [ ] stable ordering of landmark values
  - [ ] deterministic handling of missing landmarks
- [ ] Return exactly one feature row per valid frame to the service layer
- [ ] Define minimal extraction failure behavior for MVP

# 7. Implement NPZ artifact writing

- [ ] Define repository entrypoint for writing one finalized feature artifact
- [ ] Convert accumulated feature rows into one feature matrix `(T, D)`
- [ ] Add artifact path helper to `utils/paths.py`:
  - [ ] `feature_artifact_path(data_root, user_id, session_id, capture_id)`
- [ ] Define the canonical artifact write path:
  - [ ] `data/users/<user_id>/sessions/<session_id>/features/<capture_id>.npz`
- [ ] Resolve artifact paths through runtime roots via `utils.paths` (no hardcoded absolute paths)
- [ ] Ensure the path helper is pure:
  - [ ] no IO
  - [ ] no mkdir
  - [ ] treat IDs as opaque path segments
- [ ] Write the feature matrix as `.npz`
- [ ] Read written artifact bytes for hash computation
- [ ] Compute sha256 over the written `.npz` bytes
- [ ] Derive artifact metadata from the written artifact:
  - [ ] `uri`
  - [ ] `hash`
  - [ ] `shape`
  - [ ] `dtype`
  - [ ] `format="npz"`
- [ ] Return artifact metadata needed to build `raw_features_ref`



# 8. Implement feature-ref A3CPMessage append

- [ ] Define the exact `raw_features_ref` payload built from the written artifact:
  - [ ] `uri`
  - [ ] `hash`
  - [ ] `encoding`
  - [ ] `shape`
  - [ ] `dtype`
  - [ ] `format="npz"`
- [ ] Define the exact `A3CPMessage` fields required for MVP emission:
  - [ ] new unique `record_id`
  - [ ] `user_id`
  - [ ] `session_id`
  - [ ] `capture_id`
  - [ ] `modality="gesture"`
  - [ ] `source="landmark_extractor"`
  - [ ] `raw_features_ref`
- [ ] Define when the message is emitted:
  - [ ] only after successful artifact write
  - [ ] only on `capture.close`
  - [ ] never on `capture.abort`
- [ ] Append the message only through `schema_recorder.append_event()`
- [ ] Define failure handling if append fails after artifact write
- [ ] Confirm no per-frame schema events are emitted

# 9. Implement abort and cleanup behavior

- [ ] Define cleanup rules for successful finalize:
  - [ ] remove in-memory capture state after successful artifact write and event append
- [ ] Define cleanup rules for abort:
  - [ ] discard accumulated feature rows
  - [ ] remove in-memory capture state
  - [ ] write no artifact
  - [ ] append no feature-ref event
- [ ] Define duplicate-terminal protection:
  - [ ] prevent double-finalize for the same `capture_id`
  - [ ] prevent artifact double-write
  - [ ] prevent duplicate event append
- [ ] Define post-terminal behavior:
  - [ ] reject or safely ignore frame input for cleaned-up `capture_id`
  - [ ] reject or safely ignore repeated terminal input for cleaned-up `capture_id`
- [ ] Define minimal memory-cleanup guarantee for MVP

# 10. Add MVP tests

- [ ] Add service-level tests for successful bounded capture:
  - [ ] frames + `capture.close` → one `.npz` artifact written
  - [ ] frames + `capture.close` → one feature-ref `A3CPMessage` appended
  - [ ] frames + `capture.close` → capture state removed after finalize
- [ ] Add service-level tests for abort behavior:
  - [ ] frames + `capture.abort` → no artifact written
  - [ ] frames + `capture.abort` → no feature-ref event appended
  - [ ] frames + `capture.abort` → capture state removed
- [ ] Add service-level tests for terminal edge cases:
  - [ ] `capture.close` for unknown `capture_id`
  - [ ] `capture.abort` for unknown `capture_id`
  - [ ] duplicate terminal does not double-write
  - [ ] frame after close is rejected or ignored per MVP rule
  - [ ] frame after abort is rejected or ignored per MVP rule
- [ ] Add repository-level tests for extraction boundary:
  - [ ] base64 frame decode path
  - [ ] MediaPipe Holistic returns a feature row
  - [ ] feature row shape is fixed for MVP
  - [ ] missing landmarks handled deterministically
- [ ] Add repository-level tests for artifact writing:
  - [ ] `.npz` artifact is written at the expected path
  - [ ] artifact metadata reflects written file
  - [ ] sha256 is computed from written bytes

# 11. Define MVP exit criteria

- [ ] Confirm a valid bounded capture path works end-to-end:
  - [ ] `capture.frame × N`
  - [ ] `capture.close`
  - [ ] one `.npz` artifact is written
  - [ ] one feature-ref `A3CPMessage` is appended
- [ ] Confirm artifact correctness:
  - [ ] artifact exists at expected capture-scoped path
  - [ ] stored feature matrix has shape `(T, D)`
  - [ ] `raw_features_ref.shape` matches written artifact
  - [ ] `raw_features_ref.dtype` matches written artifact
  - [ ] `raw_features_ref.format == "npz"`
  - [ ] `raw_features_ref.hash` matches sha256 of written bytes
- [ ] Confirm logging correctness:
  - [ ] session JSONL contains exactly one feature-ref event for the successful capture
  - [ ] no per-frame JSONL events are written
  - [ ] `landmark_extractor` performs no direct JSONL writes
- [ ] Confirm abort correctness:
  - [ ] `capture.abort` produces no artifact
  - [ ] `capture.abort` produces no feature-ref event
  - [ ] capture state is cleaned up
- [ ] Confirm persistence boundaries:
  - [ ] only landmark-derived features are persisted
  - [ ] no raw frame or raw video payload is persisted
- [ ] Confirm MVP boundaries remain intact:
  - [ ] no classification behavior exists in this slice
  - [ ] no replay helper is required for MVP completion
  - [ ] no streaming output is required for MVP completion



# -------------older version--------------

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
- Feature artifact is the primary output: NPZ feature matrix `(T, D)` plus `raw_features_ref`.
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
- [ ] Persist features as NPZ feature matrix `(T, D)`
- [ ] Record the artifact storage type in `raw_features_ref.dtype` based on the actual written NPZ contents
- [ ] Write to:
  - `data/users/<user_id>/sessions/<session_id>/features/<capture_id>.npz`
- [ ] Compute sha256 over NPZ bytes
- [ ] Resolve paths via runtime roots (no hardcoded paths)

### 3) raw_features_ref

- [ ] Build `raw_features_ref` with:
  - `uri`
  - `hash`
  - `format="npz"`
  - `shape=[T, D]`
  - `dtype`
  - `encoding`

- [ ] Populate `shape`, `dtype`, and `hash` from the written NPZ artifact (not from in-memory assumptions)

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
- [ ] Load NPZ and confirm stored shape matches `raw_features_ref.shape`
- [ ] Verify `raw_features_ref.shape` contains exactly two integers `[T, D]`
- [ ] Verify exactly one feature-ref event per `capture_id`
- [ ] Provide replay helper (load by `capture_id`)
- [ ] Tests for:
  - missing artifact
  - hash mismatch
  - shape mismatch
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
- `raw_features_ref.encoding` must be a non-empty descriptive string identifying the extractor or feature encoding

---

Post-MVP / demo functionality.
Not required for bounded-capture MVP pipeline.

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

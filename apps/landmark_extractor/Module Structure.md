# apps/landmark_extractor — Module Structure (MVP)

Purpose: bounded-capture gesture feature extraction producing a feature artifact and a single feature-ref `A3CPMessage`.

Pipeline:
camera_feed_worker → `capture.frame × N` → `capture.close | capture.abort`
→ landmark_extractor → `.npz` artifact → feature-ref event → `schema_recorder.append_event()`


---

## domain.py
**Role:** internal pure data structures

Responsibilities:
- Define capture state keyed by `capture_id`
- Define minimum capture state fields:
  - `capture_id`
  - `user_id`
  - `session_id`
  - `feature_rows`
- Define `FeatureRow` representation as `list[float]` for one `(D,)` frame feature vector
- Define buffered feature row collection as `list[FeatureRow]`
- Define feature matrix representation conceptually as `(T, D)` from ordered buffered rows
- Define finalize result structures returned to the service layer, if needed

Capture-state invariants:
- `feature_rows` stores extracted feature rows only
- raw frames are never stored in domain state
- rows are buffered in frame arrival order
- `landmark_extractor` does not store or validate `seq`
- frame sequencing correctness is enforced upstream by `camera_feed_worker`



`CaptureState` will be implemented as a **Python `dataclass`**.
Rationale:
- `CaptureState` represents a coherent internal domain object (one active buffered capture), not a generic mapping.
- A `dataclass` provides clear structure, explicit fields, and readable attribute access (`state.capture_id`).
- It improves type safety and reasoning in the service layer compared to dictionary-based structures.
- It preserves the design goal that `domain.py` contains **explicit internal state models**, not loosely structured data.


Properties:
- pure Python only
- no filesystem IO
- no schema_recorder usage
- no MediaPipe execution
- no artifact writing
- no landmark-to-feature conversion logic
- no missing-landmark fill logic
---

# File Structure and Responsibilities

## ingest_boundary.py
**Role:** public validated ingest boundary

Responsibilities:
- Expose the single public module ingest entrypoint
- Accept incoming frame and terminal messages for landmark extraction
- Validate input against `LandmarkExtractorInput`
- Enforce the canonical ingest contract:
  - `LandmarkExtractorFrameInput`
  - `LandmarkExtractorTerminalInput`
- Forward validated messages into `service.py` for orchestration
- Keep transport-agnostic module entry semantics consistent across callers

Must NOT:
- buffer capture state
- perform landmark extraction
- write `.npz` artifacts
- append JSONL events
- act as a persistent sink stub in final MVP behavior





## service.py
**Role:** module orchestration

Responsibilities:
- Receive validated messages forwarded from `ingest_boundary.py`
- Dispatch events:
  - `capture.frame` → frame handler
  - `capture.close` → finalize handler
  - `capture.abort` → discard handler
- Manage capture lifecycle keyed by `capture_id`
- Maintain per-capture in-memory buffering of feature rows
- Call extraction boundary for each frame
- Append one fixed-length feature row per successful frame
- On `capture.close`:
  - finalize buffered rows into feature matrix `(T, D)`
  - call `artifact_writer.write_feature_artifact()`
  - build one feature-ref `A3CPMessage`
  - append event via `schema_recorder.append_event()`
- Enforce commit-unit rule:
  - artifact write
  - event append
  - rollback artifact if event append fails
- Define service behavior for:
  - extraction failure on frame ingest
  - unknown capture terminal events
  - duplicate terminal events
  - post-terminal frame ingest

Must NOT:
- validate external input (handled by `ingest_boundary.py`)
- write JSONL directly
- perform low-level filesystem operations
- contain MediaPipe configuration constants


---

## artifact_writer.py
**Role:** feature artifact persistence

Responsibilities:
- Resolve artifact path via `utils.paths.feature_artifact_path(...)`
- Write the finalized feature matrix `(T, D)` to `.npz`
- Read back written artifact bytes for post-write hashing
- Compute `sha256` over the written `.npz` bytes
- Return artifact metadata needed to build `raw_features_ref`:
  - `uri`
  - `hash`
  - `encoding`
  - `shape`
  - `dtype`
  - `format`
- Provide artifact deletion helper for rollback on failed commit

Must NOT:
- append JSONL
- decide when finalize occurs
- maintain capture state
- perform landmark extraction

---



## config.py
**Role:** extractor configuration and constants

Responsibilities:
- Define MediaPipe Holistic configuration used for MVP extraction
- Define the landmark selection set used to build feature rows
- Define deterministic landmark ordering for feature column construction
- Define missing-landmark encoding rule `(0.0, 0.0)`
- Define the feature encoding identifier used in `raw_features_ref.encoding`
- Define artifact format constants (`format="npz"`, dtype, etc.)
- Define feature dimension constant `D` derived from the selected landmarks

Properties:
- no runtime logic
- no filesystem IO
- no schema_recorder usage

---
## routes/router.py
**Role:** transport adapter

Responsibilities:
- Provide HTTP/WebSocket boundary for edge/cloud deployment
- Convert transport requests into `LandmarkExtractorInput`
- Forward validated messages to `ingest_boundary.ingest()`

Must NOT:
- implement extraction logic
- perform artifact IO
- append events
- bypass `ingest_boundary`

## tests/
**Role:** module verification

Responsibilities:
- Frame buffering tests
- Terminal close finalize tests
- Abort behavior tests
- Artifact creation tests
- Commit-unit rollback tests
- Deterministic feature ordering tests
- End-to-end capture → artifact → feature-ref event tests


---

# Supporting External Modules

Used by this module but not defined here:

- `schemas.landmark_extractor`
  - ingest input schemas

- `schemas.a3cp_message`
  - canonical feature-ref event

- `apps.schema_recorder.service`
  - append JSONL events

- `utils.paths`
  - path resolution helpers

- `camera_feed_worker.forward_adapter`
  - upstream message adapter


---

# Key MVP Invariants

- Raw frames are never persisted
- Only `(x, y)` landmark features are stored
- Missing landmarks encoded `(0.0, 0.0)`
- Feature column ordering is deterministic
- Exactly **one event per successful capture**
- `capture.abort` writes **nothing**
- Artifact write + event append form **one commit unit**

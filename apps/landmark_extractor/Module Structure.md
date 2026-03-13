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

# 3a. landmark_mediapipe.py

Purpose: run MediaPipe Tasks landmark detectors on one decoded frame and return normalized landmark data.

## Public module surface
- Expose backend class `MediaPipeLandmarkBackend`
- Expose backend exceptions:
  - `MediaPipeBackendError`
  - `MediaPipeBackendInitError`
  - `MediaPipeExtractionError`
- Keep helper functions private to this file

## Backend construction
- Implement reusable adapter class `MediaPipeLandmarkBackend`
- Expose constructor:
  - `__init__(pose_model_path, hand_model_path, face_model_path)`
- Constructor accepts `str | Path` model paths and normalizes them to `Path`
- Initialize `PoseLandmarker`, `HandLandmarker`, and `FaceLandmarker` once in the constructor
- Reuse initialized detectors across frame calls
- Wrap detector/model initialization failures in `MediaPipeBackendInitError`
- Preserve original exception context via `raise ... from exc`

## Backend execution
- Expose method:
  - `extract_landmarks(frame, timestamp_frame) -> NormalizedLandmarks`
- Accept decoded frame image
- Accept `timestamp_frame` for MediaPipe VIDEO mode
- Assume caller provides a valid decoded frame image
- Do not duplicate upstream transport or schema validation
- Enforce only minimal adapter-local preconditions:
  - reject `frame is None`
  - reject missing `timestamp_frame`
- Convert BGR frame to RGB
- Convert RGB frame into `mp.Image`
- Convert `timestamp_frame` to MediaPipe `timestamp_ms`
- Execute `PoseLandmarker`
- Execute `HandLandmarker`
- Execute `FaceLandmarker`
- Extract pose landmarks into normalized internal mapping
- Extract handedness and map detected hand landmarks into `left_hand` and `right_hand`
- Extract face / iris landmarks into normalized internal mapping
- Return `NormalizedLandmarks` to caller
- Wrap runtime extraction failures in `MediaPipeExtractionError`
- Preserve original exception context via `raise ... from exc`

## Output contract
- Return `NormalizedLandmarks`
- Output contains normalized 2D landmark maps only:
  - `pose`
  - `left_hand`
  - `right_hand`
  - `face`
- Return all detected normalized landmarks produced by the detectors
- Do not apply configured feature selection in this file
- Do not apply deterministic feature ordering in this file
- Do not apply missing-landmark fill in this file
- Absent landmarks remain absent from the returned maps

## Constraints
- No capture state
- No artifact writing
- No JSONL writes
- No feature-row flattening
- No drawing or visualization logic
- No missing-landmark fill beyond what MediaPipe actually returns
- No raw MediaPipe result objects exposed outside this file
- No backend-specific helper functions exposed outside this file



# 3. extractor.py

Purpose: convert normalized landmark maps into one deterministic fixed-length feature row.

## Public module surface
- Expose pure function:
  - `build_feature_row(landmarks: NormalizedLandmarks) -> FeatureRow`
- Keep helper functions private to this file

## Feature-row construction
- Accept `NormalizedLandmarks`
- Accept normalized landmark maps produced by `landmark_mediapipe.py`
- Read configured landmark contract from `config.py`
- Use configured deterministic landmark ordering from `ORDERED_LANDMARKS`
- Resolve each configured `(region, landmark_index)` against the corresponding landmark map:
  - `pose`
  - `left_hand`
  - `right_hand`
  - `face`
- Extract normalized `(x, y)` when the landmark is present
- Apply configured missing-landmark fill when the landmark is absent:
  - `MISSING_LANDMARK_PAIR`
- Flatten ordered landmark pairs into one feature row
- Produce one fixed-length `FeatureRow`

## Output contract
- Return `FeatureRow`
- Output contains only flattened `x, y` values
- Output ordering matches `ORDERED_LANDMARKS` exactly
- Output length is exactly `FEATURE_DIM`
- Output contains one `(x, y)` pair per configured landmark
- Missing configured landmarks are encoded as `MISSING_LANDMARK_PAIR`
- No landmarks outside the configured contract are included in the output

## Helper functions
- Implement private helper to resolve one configured landmark from `NormalizedLandmarks`
- Implement private helper to return configured missing-landmark fill
- Implement private helper to convert ordered landmark pairs into one flat `FeatureRow`

## Constraints
- No MediaPipe calls
- No capture state
- No artifact writing
- No JSONL writes
- No visualization logic
- No schema validation duplication
- No reordering outside the configured `ORDERED_LANDMARKS`
- No exposure of helper functions outside this file




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

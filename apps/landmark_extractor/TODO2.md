# apps/landmark_extractor/TODO.md — MVP Execution Order

Goal: implement bounded-capture landmark feature extraction producing one `.npz` feature artifact and exactly one feature-ref `A3CPMessage` on `capture.close`.

Pipeline:
camera_feed_worker → `capture.frame × N` → `capture.close | capture.abort`
→ landmark_extractor → `.npz` artifact → feature-ref event
→ `schema_recorder.append_event()`

---

# 0. Locked MVP Invariants

- Scope = bounded-capture gesture feature extraction only
- Raw frames must never be persisted
- Only landmark-derived feature matrices are stored
- MediaPipe PoseLandmarker, HandLandmarker, and FaceLandmarker used for landmark detection
- Persist `(x, y)` only (no `z`)
- Missing landmarks encoded as `(0.0, 0.0)`
- Each processed frame produces exactly one feature row
- Feature column ordering must be deterministic
- Artifact format = `.npz` containing `(T, D)` feature matrix
- Artifact path:
  `data/users/<user_id>/sessions/<session_id>/features/<capture_id>.npz`
- Only `capture.close` may produce a persisted artifact
- `capture.abort` writes no artifact and emits no event
- Exactly **one feature-ref event** per successful capture
- JSONL writes occur only via `schema_recorder.append_event()`
- Artifact write + event append form **one commit unit**
- If event append fails → artifact must be deleted
- Frame limits enforced upstream by camera_feed_worker
- landmark_extractor assumes bounded capture input
---

# 1. domain.py

Purpose: internal pure data structures used by `service.py`.



## Capture state (Invariant)

The extractor maintains capture state keyed by `capture_id`.
Minimum state fields:
- `capture_id`
- `user_id`
- `session_id`
- `feature_rows` (ordered list of feature rows for the capture)

Constraints:
- State stores **only extracted feature rows**, never raw frames.
- Feature rows are appended **in frame arrival order**.
- Frame sequencing correctness is enforced upstream by `camera_feed_worker`.
- `landmark_extractor` does **not** store or validate `seq`.

## Feature structures
- [x] Define feature row representation `(D,)` as `list[float]`
- [x] FeatureMatrix = list[list[float]] (until finalize)

## Finalization structures
- [x] Define finalize result structure returned to service layer, if needed



Constraints:
- Pure Python only
- No filesystem IO
- No MediaPipe execution
- No schema_recorder usage
- No artifact writing

---

# 2. config.py Done

Purpose: extractor configuration and deterministic feature layout.
1. MediaPipe MVP settings
   - HOLISTIC_STATIC_IMAGE_MODE
   - HOLISTIC_MODEL_COMPLEXITY
   - HOLISTIC_SMOOTH_LANDMARKS
   - HOLISTIC_ENABLE_SEGMENTATION
   - HOLISTIC_SMOOTH_SEGMENTATION
   - HOLISTIC_REFINE_FACE_LANDMARKS
   - HOLISTIC_MIN_DETECTION_CONFIDENCE
   - HOLISTIC_MIN_TRACKING_CONFIDENCE

2. Landmark-selection contract
   - selected landmark groups for MVP
   - canonical ordered landmark identifiers
   - total ordered landmark count

3. Feature-layout constants
   - FEATURE_COORDS_PER_LANDMARK = 2
   - FEATURE_COORD_NAMES = ("x", "y")
   - FEATURE_INCLUDE_Z = False
   - FEATURE_DIM = ordered_landmark_count * 2

4. Encoding and artifact constants
   - FEATURE_ENCODING_ID
   - FEATURE_ARTIFACT_FORMAT = "npz"
   - FEATURE_DTYPE
   - RAW_FEATURES_REF_ENCODING = FEATURE_ENCODING_ID

5. Missing-value constants
   - MISSING_LANDMARK_X = 0.0
   - MISSING_LANDMARK_Y = 0.0
   - MISSING_LANDMARK_PAIR = (0.0, 0.0)
---

# 3a. landmark_mediapipe.py

Purpose: run MediaPipe Tasks landmark detectors and return normalized landmark data.


## Backend execution
- Implement backend class `MediaPipeLandmarkBackend`
- Implement the MediaPipe backend as a reusable adapter class that initializes detectors once and reuses them across frame calls
- Expose constructor `__init__(pose_model_path, hand_model_path, face_model_path)`
- Constructor accepts `str | Path` model paths and normalizes them to `Path`
- Initialize `PoseLandmarker`, `HandLandmarker`, and `FaceLandmarker` once in the backend constructor
- Expose backend method `extract_landmarks(frame, timestamp_frame)` returning `NormalizedLandmarks`
- Accept decoded frame image
- Accept `timestamp_frame` for MediaPipe VIDEO mode
- Assume caller provides a valid decoded frame image
- Do not duplicate upstream transport or schema validation
- Enforce minimal adapter-local preconditions only:
  - reject `frame is None` with a clear error
  - reject missing `timestamp_frame` with a clear error
- Convert BGR frame to RGB
- Convert RGB frame into `mp.Image`
- Convert `timestamp_frame` into MediaPipe `timestamp_ms`
- Execute `PoseLandmarker` in VIDEO mode
- Execute `HandLandmarker` in VIDEO mode
- Execute `FaceLandmarker` in VIDEO mode
- Extract pose landmarks into normalized internal mapping
- Extract hand landmarks and use handedness classification to map to `left_hand` and `right_hand`
- Extract face / iris landmarks into normalized internal mapping
- Return all detected normalized landmarks produced by the detectors
- Do not apply configured feature selection in this file
- Do not apply missing-landmark fill in this file
- Return `NormalizedLandmarks` to caller
- Wrap detector/model initialization failures in `MediaPipeBackendInitError`
- Wrap runtime extraction failures in `MediaPipeExtractionError`
- Preserve original exception context via `raise ... from exc`

## Public module surface
- Expose backend class `MediaPipeLandmarkBackend`
- Expose backend exceptions:
  - `MediaPipeBackendError`
  - `MediaPipeBackendInitError`
  - `MediaPipeExtractionError`
- Keep helper functions private to this file



-----------
# 3. extractor.py

Purpose: convert `NormalizedLandmarks` into one deterministic fixed-length feature row.

## Public surface
- [ ] Expose pure function:
  - [ ] `build_feature_row(landmarks: NormalizedLandmarks) -> FeatureRow`

## Frame → feature row
- [ ] Accept `NormalizedLandmarks` from `landmark_mediapipe.py`
- [ ] Read configured landmark contract from `config.py`
- [ ] Iterate through `ORDERED_LANDMARKS` in exact configured order
- [ ] For each `(region, landmark_index)`:
  - [ ] resolve the corresponding source map (`pose`, `left_hand`, `right_hand`, `face`)
  - [ ] extract `(x, y)` if present
  - [ ] otherwise emit configured missing pair `(0.0, 0.0)`
- [ ] Flatten ordered landmark pairs into one `FeatureRow`
- [ ] Produce fixed-length row with length `FEATURE_DIM`

## Output invariants
- [ ] Output type is `FeatureRow` (`list[float]`)
- [ ] Output ordering is exactly `ORDERED_LANDMARKS`
- [ ] Output contains only `x, y` values
- [ ] Output length is exactly `FEATURE_DIM`

## Helper functions
- [ ] Implement pure helper to resolve one configured landmark from `NormalizedLandmarks`
- [ ] Implement pure helper to convert ordered landmark selections into one flat feature row
- [ ] Implement pure helper for missing-landmark fill using `MISSING_LANDMARK_PAIR`

## Non-goals
- [ ] No MediaPipe calls in this file
- [ ] No feature artifact writing
- [ ] No JSONL writes
- [ ] No capture state management
- [ ] No visualization logic






# 4. service.py

Purpose: module orchestration and capture lifecycle management.

## Service skeleton
- [ ] Implement internal orchestration entrypoint
- [ ] Accept validated `LandmarkExtractorInput`
- [ ] Dispatch by event type:
  - [ ] `capture.frame`
  - [ ] `capture.close`
  - [ ] `capture.abort`

## Capture lifecycle
- [ ] Maintain capture state keyed by `capture_id`

### `capture.frame`
- [ ] Resolve capture state
- [ ] Create capture state on first frame
- [ ] Read the incoming frame image payload from the validated frame input
- [ ] Call landmark backend to extract normalized landmarks from the incoming frame
- [ ] Pass detected landmarks to `extractor.py`
- [ ] Return one fixed-length feature row `(D,)`
- [ ] Append feature row to buffer
- [ ] Define service behavior if extraction fails on a frame

### `capture.close`
- [ ] Require active capture state
- [ ] Ensure finalize occurs exactly once
- [ ] Convert buffered rows → feature matrix `(T, D)`
- [ ] Call artifact writer
- [ ] Build feature-ref `A3CPMessage`
- [ ] Append event via `schema_recorder.append_event()`
- [ ] Clear capture state only after successful finalize
- [ ] Define service behavior if finalize fails after artifact rollback

### `capture.abort`
- [ ] Require active capture state
- [ ] Discard buffered rows
- [ ] Write no artifact
- [ ] Emit no event
- [ ] Clear capture state

## Terminal edge cases
- [ ] Handle `capture.close` for unknown `capture_id`
- [ ] Handle `capture.abort` for unknown `capture_id`
- [ ] Handle duplicate terminal events
- [ ] Handle frame ingest after finalize
- [ ] Handle frame ingest after abort

## Commit rule
- [ ] Treat artifact write + event append as one commit unit
- [ ] If append fails:
  - [ ] delete artifact
  - [ ] fail finalize
  - [ ] propagate finalize failure to caller
  - [ ] require capture redo

---
# 5. artifact_writer.py

Purpose: feature artifact persistence.

## Artifact path
- [ ] Add helper in `utils.paths`:
  `feature_artifact_path(data_root, user_id, session_id, capture_id)`
- [ ] Ensure helper is pure:
  - [ ] no IO
  - [ ] no mkdir
  - [ ] treat IDs as opaque

## Artifact writing
- [ ] Accept finalized feature matrix `(T, D)`
- [ ] Write feature matrix `(T, D)` as `.npz`
- [ ] Read written artifact bytes
- [ ] Compute sha256 over written artifact bytes

## Metadata return
- [ ] Return artifact metadata:
  - [ ] `uri`
  - [ ] `hash`
  - [ ] `encoding` (from `config.FEATURE_ENCODING_ID`)
  - [ ] `shape`
  - [ ] `dtype`
  - [ ] `format="npz"`

## Rollback support
- [ ] Implement artifact deletion helper
- [ ] Define delete behavior for missing artifact during rollback

---

# 6. ingest_boundary.py

Purpose: public module ingest boundary.

## Ingest interface
- [ ] Expose the single public ingest entrypoint
- [ ] Accept validated `LandmarkExtractorInput`

## Input union
- [ ] Support:
  - [ ] `LandmarkExtractorFrameInput`
  - [ ] `LandmarkExtractorTerminalInput`

## Forwarding behavior
- [ ] Replace sink behavior with forward-to-service behavior
- [ ] Forward validated messages to `service.py`

Constraints:
- No schema validation logic (handled by Pydantic)
- No capture state
- No MediaPipe execution
- No artifact writing
- No JSONL writes
---

# 7. routes/router.py

Purpose: transport adapter for edge/cloud deployment paths.

## Transport boundary
- [ ] Expose HTTP/WebSocket endpoint(s) required for MVP
- [ ] Accept transport requests for landmark extractor ingest
- [ ] Convert transport requests → `LandmarkExtractorInput`
- [ ] Forward validated messages to `ingest_boundary.ingest()`

Constraints:
- No business logic
- No artifact IO
- No event appends
- Do not bypass `ingest_boundary`
---

# 8. tests/

Begin once `domain.py`, `config.py`, and `service.py` interfaces stabilize.

## Service tests
- [ ] frames + `capture.close` → one artifact written
- [ ] frames + `capture.close` → one feature-ref event appended
- [ ] `capture.close` clears capture state
- [ ] frames + `capture.abort` writes no artifact
- [ ] frames + `capture.abort` emits no event
- [ ] abort clears capture state

## Terminal edge cases
- [ ] `capture.close` unknown `capture_id`
- [ ] `capture.abort` unknown `capture_id`
- [ ] duplicate terminal does not double-write artifact
- [ ] duplicate terminal does not double-append event
- [ ] frame after close handled per MVP rule
- [ ] frame after abort handled per MVP rule

## Feature construction tests
- [ ] identical landmark input produces identical feature row output
- [ ] extracted feature row has fixed shape `(D,)`
- [ ] feature column ordering matches canonical landmark order from `config.py`

## Artifact tests
- [ ] `.npz` artifact written at expected path
- [ ] artifact metadata matches written file
- [ ] sha256 computed from written bytes
- [ ] emitted feature-ref event contains encoding matching `config.FEATURE_ENCODING_ID`

- [ ] if `append_event()` fails after artifact write:
  - [ ] artifact is deleted
  - [ ] finalize reports failure
  - [ ] capture state follows defined retry policy
- [ ] stored feature matrix has shape `(T, D)`

## Commit rollback tests
- [ ] if `append_event()` fails after artifact write:
  - [ ] artifact is deleted
  - [ ] finalize reports failure

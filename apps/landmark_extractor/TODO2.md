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
- MediaPipe Holistic used for landmark detection
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

## Capture state
- [ ] Define capture state keyed by `capture_id`
- [ ] Define minimum fields:
  - [ ] `capture_id`
  - [ ] `user_id`
  - [ ] `session_id`
  - [ ] buffered feature rows

## Feature structures
- [ ] Define feature row representation `(D,)`
- [ ] Define feature matrix representation `(T, D)`

## Finalization structures
- [ ] Define finalize result structure returned to service layer, if needed



Constraints:
- Pure Python only
- No filesystem IO
- No MediaPipe execution
- No schema_recorder usage
- No artifact writing

---

# 2. config.py

Purpose: extractor configuration and deterministic feature layout.

## MediaPipe configuration
- [ ] Define MediaPipe Holistic settings used for MVP

## Landmark contract
- [ ] Define selected landmark set used for MVP extraction
- [ ] Define canonical ordered landmark list used for feature-column construction

## Feature layout
- [ ] Lock coordinates persisted per landmark = 2 (`x`, `y`)
- [ ] Exclude `z` from MVP feature layout
- [ ] Derive feature dimension `D` from ordered landmark count × 2

## Encoding configuration
- [ ] Define canonical feature encoding identifier
- [ ] Ensure encoding identifier is emitted in `raw_features_ref.encoding`

## Feature constants
- [ ] Define missing-landmark encoding `(0.0, 0.0)`
- [ ] Define artifact format constant `format="npz"`
- [ ] Define feature dtype constant

---
# 3. extractor.py

Purpose: convert extracted landmarks into deterministic feature rows.


## Frame → feature row
- [ ] Accept normalized landmark data from MediaPipe
- [ ] Select configured landmarks from `config.py`
- [ ] Apply deterministic landmark ordering
- [ ] Convert landmarks → `(x, y)` pairs
- [ ] Apply missing landmark fill `(0.0, 0.0)`
- [ ] Produce fixed-length feature row `(D,)`


## Helper functions
- [ ] Implement deterministic landmark → feature-row conversion helper
- [ ] Implement missing-landmark fill helper `(0.0, 0.0)`


# 3a. landmark_mediapipe.py

Purpose: run MediaPipe Holistic and return normalized landmark data.

## Backend execution
- [ ] Accept incoming frame image payload
- [ ] Execute MediaPipe Holistic
- [ ] Normalize extracted landmarks into module-internal structure
- [ ] Return normalized landmark data for `extractor.py`

Constraints:
- No capture state
- No artifact writing
- No JSONL writes
- No feature-row flattening


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

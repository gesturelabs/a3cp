# apps/landmark_extractor/TODO.md

A3CP — landmark_extractor TODO (module-scoped)

Scope for this slice (authoritative): gesture-only landmark feature extraction from a **bounded capture** (identified by `record_id`) and emission of **exactly one** feature-ref A3CPMessage per capture via `schema_recorder`.

Legacy spec assessment (non-authoritative; see §H):
- Several parts of the pasted legacy spec conflict with the bounded-capture architecture (per-frame semantics, modality/source values, file format examples, module type, and responsibilities around logging). This TODO follows the slice plan below as authoritative.

---

## Module invariants (locked)
- Input comes from `camera_feed_worker` as a **bounded capture window**, not an endless live stream.
- **One bounded capture** → **one `record_id`** → **one feature artifact** → **exactly one** session JSONL event.
- Persist only landmark-derived features (no raw video persistence).
- Feature artifact is the primary output: dense float32 NPZ `(T, D)` plus `raw_features_ref`.
- **Do NOT classify** (feature extraction only).
- Session JSONL writing rule: only `schema_recorder` appends to:
  - `logs/users/<user_id>/sessions/<session_id>.jsonl`
- Routes import schemas only via: `from schemas import ...` (no deep imports).

---

## A) Canonical app structure (must be created / migrated)
Create the runtime app under `apps/` following the canonical architecture.

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
    - orchestrates extraction for one bounded capture (`record_id`)
    - enforces “one artifact per capture”
    - calls repository for IO (feature file write) and for schema append via schema_recorder helper

- [ ] Repository layer (expected):
  - [ ] `apps/landmark_extractor/repository.py`
    - MediaPipe Holistic execution boundary (frame→landmarks)
    - feature artifact persistence (NPZ write)
    - sha256 computation over NPZ bytes
    - replay/load helper(s)

- [ ] Optional app-local components (only if needed):
  - [ ] `apps/landmark_extractor/config.py` (e.g., fps cap, max_window_s, extractor_tag)
  - [ ] `apps/landmark_extractor/models.py` (internal data objects only; no FastAPI/IO)
  - [ ] `apps/landmark_extractor/domain.py` (pure invariants; no FastAPI/IO)

- [ ] Tests (required):
  - [ ] `apps/landmark_extractor/tests/`
    - [ ] service-level tests (no HTTP required)
    - [ ] thin route tests (if routes exist)

---

## B) Feature extraction + artifact writing (slice plan)
### 1) Convert incoming frames to Holistic landmark features (gesture only)
- [ ] Convert incoming frames to **Holistic landmark features** (gesture only).
- [ ] Produce **one feature artifact per bounded capture (`record_id`)**.

- [ ] Define and enforce input contract from `camera_feed_worker`:
  - bounded capture payload (multiple frames) plus required metadata:
    `user_id`, `session_id`, `record_id`, `timestamp_start`, `timestamp_end`
  - landmark_extractor processes the entire bounded capture as a unit
  - no per-frame streaming outputs or incremental schema events


### 2) Persist features as NPZ `(T, D)` float32
- [ ] Persist features as a dense **float32 NPZ** array with shape `(T, D)`:
  - `T` = number of frames in the capture (implicit in file)
  - `D` = flattened per-frame landmark dimensionality
- [ ] Write feature file to:
  - `data/users/<user_id>/sessions/<session_id>/features/<record_id>.npz`
- [ ] Compute **sha256** over the full `.npz` file bytes.

- [ ] Resolve artifact paths via runtime roots (no hardcoded paths):
  - use `DATA_ROOT = env("DATA_ROOT", default="./data")`
- [ ] Use helper-only path resolution (helpers may mkdir; callers may not):
  - `session_features_dir(user_id, session_id)` →
    `<DATA_ROOT>/users/<user_id>/sessions/<session_id>/features/`
- [ ] Write feature file as `<record_id>.npz` into `session_features_dir(...)`



### 3) Build raw_features_ref
- [ ] Build `raw_features_ref` with:
  - `uri` (path to `.npz`)
  - `hash` (sha256)
  - `format = "npz"`
  - `dims = D`
  - `encoding` (string with extractor + window params), e.g.
    `"holistic_landmarks_v1;fps=15;max_window_s=120;extractor_tag=<version>"`
- [ ] Record extractor version/container tag in `raw_features_ref.encoding` (or adjacent metadata).
- [ ] Set `modality = "gesture"` at this stage.

### 4) Determinism scope (locked)
- Same input bytes + same code revision/container tag ⇒ identical feature file bytes and sha256.
- No requirement for byte-identical output across upgrades.

---

## C) Schema recording (append-only, one event per capture)
- [ ] For each completed bounded capture (`record_id`), emit **exactly one** A3CPMessage:
  - `source = "landmark_extractor"`
  - includes `user_id`, `session_id`, `record_id`, `timestamp`
  - includes `raw_features_ref` (uri, sha256, encoding, dims, format="npz")
  - `modality = "gesture"`
- [ ] Append the message via the shared `schema_recorder` writer utility to:
  - `logs/users/<user_id>/sessions/<session_id>.jsonl`
- [ ] Enforce “exactly one event per capture” at service level:
  - before appending, verify session JSONL contains no existing feature-ref event for this `record_id`
  - if a duplicate is detected, fail fast (do not append a second event)

- [ ] **No per-frame / per-chunk messages.** One schema event per bounded capture only.
- [ ] Session JSONL remains strictly append-only (no edits, no rewrites).

---

## D) Guardrails & replay proof (gesture slice)
- [ ] Verify feature artifact exists at `raw_features_ref.uri`.
- [ ] Recompute sha256 over the `.npz` file and confirm it matches `raw_features_ref.hash`.
- [ ] Load the feature array and confirm:
  - shape is `(T, D)`
  - `D == raw_features_ref.dims`
- [ ] Verify session JSONL contains **exactly one** feature-ref event for the given `record_id`.
- [ ] Add a simple replay helper:
  - load features by `record_id`
  - print `(T, D)`, hash, and encoding
- [ ] After service restart (same build/container tag), replay produces identical bytes and hash.
- [ ] Add service-level tests covering replay and integrity:
  - successful replay for a valid `record_id`
  - failure on missing artifact
  - failure on sha256 mismatch
  - failure on shape/dims mismatch
  - failure on duplicate feature-ref event for the same `record_id`


- [ ] Enforce session logging contract
  - [ ] Emit session events only via `schema_recorder.service.append_event()`
  - [ ] Do not write session JSONL directly
  - [ ] Covered by global single-writer guard test
  - [ ] Add module-level test asserting no session JSONL writes in this module

---

## E) Deep route fix (Route Re-Migration)
Eliminate deep imports for landmark_extractor legacy routes and migrate routing to canonical app structure.

### 1) Inventory (read-only)
- [ ] Identify legacy route file(s):
  - `api/routes/landmark_extractor_routes.py` (expected; confirm actual filename)
- [ ] Identify which schema classes it deep-imports (if any) and from where.

### 2) Public schema surface exports (no behavior change)
- [ ] Ensure route-required schema names are exported in `schemas/__init__.py` and included in `__all__`
  - (exact names depend on existing schema set for landmark_extractor)
  - [ ] Confirm landmark_extractor route request/response schemas required by routes
  are exported via the public schema surface (`schemas/__init__.py`) and listed in `__all__`



### 3) Rewrite legacy shim route (structure-only; no redesign)
- [ ] Update `api/routes/landmark_extractor_routes.py` to:
  - import schemas only via `from schemas import ...`
  - delegate to `apps/landmark_extractor/routes/router.py`
- [ ] Ensure router is mounted once in `api/main.py` (no duplicate registration)

### 4) Guardrails (tests)
- [ ] Module-scoped test: fail if `api/routes/landmark_extractor_routes.py` deep-imports `schemas.<submodule>`
- [ ] Public-API presence test: required names exist in `schemas.__all__`

### 5) HTTP smoke verification (minimal)
- [ ] Boot and hit endpoint(s); endpoint may return 501 but must not crash on import/validation.

---

## F) CI guardrails (scoped to this slice; reference)
- [ ] Add module-scoped tests enforcing route imports use only public schema surface:
  - `api/routes/landmark_extractor_routes.py` imports only from `schemas`
- [ ] Ensure required public schema names are exported in `schemas/__init__.py`
- [ ] Keep generator unchanged; only update mapping/config if new module schemas were added
- [ ] CI fails if any module writes directly to `logs/users/**`
  - only the `schema_recorder` writer utility may append session JSONL
- [ ] Add CI static-scan test: fail if any code outside
  `apps/schema_recorder/session_writer.py`
  writes/appends to `logs/users/**/sessions/*.jsonl`
---

## G) Exit gate (“ready to classify” for gesture)
- [ ] For a completed session, the system can reliably:
  - [ ] load the landmark feature artifact by `record_id` via `raw_features_ref.uri`
  - [ ] recompute and verify integrity (`sha256 == raw_features_ref.hash`)
  - [ ] load the feature array and confirm shape `(T, D)` with `D == raw_features_ref.dims`
- [ ] After a service restart **using the same build/container tag**, replaying the same `record_id` produces identical bytes and the same `sha256`
- [ ] Session JSONL contains **exactly one** landmark feature-ref schema event per bounded capture (`record_id`)

---

## H) Legacy spec assessment (explicit)
The pasted legacy spec contains conflicts with the authoritative slice plan above. Treat these statements as deprecated unless re-approved:

Conflicts / mismatches:
- Module Type: legacy says `classifier`; slice scope says **feature extractor only** (no classification).
- Output semantics: legacy describes **per-frame** landmark vectors and forwarding vectors to gesture_classifier and schema_recorder; slice scope requires **one artifact per bounded capture** and **one schema event per capture** (no per-frame/per-chunk messages).
- Schema fields: legacy “SCHEMA COMPLIANCE SUMMARY” and example A3CPMessage use:
  - `modality = "image"` and `source = "communicator"` and `format = "parquet"` and `vector_version` fields.
  Slice plan requires:
  - `modality = "gesture"`, `source = "landmark_extractor"`, `format = "npz"`, and `raw_features_ref.encoding` carrying extrac_

  - [ ] Correct and lock encoding-field wording for this slice:
  - `raw_features_ref.encoding` MUST carry extractor + window params and the extractor/container tag
  - legacy references to `vector_version`, per-frame vectors, or non-NPZ formats remain deprecated

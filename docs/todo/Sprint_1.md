# A3CP — Gesture-First Loop (Start at Session Manager) — REVISED TODO (CLEAN)

## 0) Ground rules for this slice
- Keep schemas unchanged unless a hard blocker is hit.
- Append-only events everywhere (no in-place edits).
- Every downstream module receives: user_id, session_id, timestamp, record_id. **Log writing rule:** Only `recorded_schemas` appends to `logs/users/<user_id>/sessions/<session_id>.jsonl`.

## Sprint 1 storage rule (locked)

- Do **not** persist raw video frames/streams to disk.
- Persist **only** landmark-derived feature artifacts (e.g., `(T, D)` arrays) plus their `raw_features_ref` metadata (uri, sha256, encoding, dims, format) recorded in session JSONL.



---


---

## 1) Session Manager (first module in chain)
- [x ] Confirm public API endpoints exist and are stable:
  - [x ] start session → returns session_id
  - [x] end session → closes session
- [ x] Ensure session_id is unique, stable, and readable.
- [x ] Emit append-only session events as A3CPMessage JSONL:
  - [x ] write via recorded_schemas to `logs/users/<user_id>/sessions/<session_id>.jsonl`
  - [ x] include source="session_manager", performer_id, timestamp, user_id, session_id, record_id
- [ ] Add minimal “get current session” helper (in-memory acceptable for demo).

---

## 2) Contract for downstream modules (session spine)
- [ ] Define minimal session header object:
  - user_id, session_id, timestamp, device_id?, consent_given?, is_demo?
- [ ] Add one guardrail test:
  - start → end produces two ordered events for the same session_id.

---

## 3) Filesystem, helpers, and demo UI (gesture slice)

**Storage roots (single source of truth)**
- DATA_ROOT = env("DATA_ROOT", default="./data")
- LOG_ROOT  = env("LOG_ROOT",  default="./logs")

**User-scoped paths (defined only via helpers; helpers may mkdir, nothing else)**
- session_features_dir(user_id, session_id)
  → `<DATA_ROOT>/users/<user_id>/sessions/<session_id>/features/`
- [ ] session_log_path(user_id, session_id) -> <LOG_ROOT>/users/<user_id>/sessions/<session_id>.jsonl


**Runtime configuration**
- All services (local or Docker) use:
  - DATA_ROOT=/data
  - LOG_ROOT=/logs

## Demo UI (gesture slice)

- [ ] Route served by FastAPI: `/demo/gesture` (same-origin).
- [ ] Controls:
  - **Start Session**
  - **Start Capture** (bounded capture, ≤ 120s)
  - **Stop Capture**
  - **End Session**
- [ ] Uses browser `getUserMedia()` to access camera.
- [ ] Sends bounded capture data to `camera_feed_worker` (transport unspecified at planning level).
- [ ] Displays:
  - `session_id`
  - `record_id`
  - capture status (success / failure)
  - latest feature artifact hash (if available).

**Correctness rules for this slice**
- Integrity: every feature file has a sha256; replay recomputes and matches it.
- Structural validity: feature array loads as `(T, D)` and `D == raw_features_ref.dims`; encoding/format present.
- Logging correctness: one capture record → exactly one feature-ref event in the session JSONL.
- Determinism scope: expected only within the same build/container tag (for debugging), not across upgrades.



---

## Docker structure (monorepo, contributor workflow)
- [ ] Add per-module Dockerfiles:
  - [ ] apps/camera_feed_worker/Dockerfile
  - [ ] apps/landmark_extractor/Dockerfile (Holistic-heavy deps isolated)
- [ ] Add repo-root docker-compose.yml with two services:
  - [ ] camera_feed_worker (uses apps/camera_feed_worker/Dockerfile)
  - [ ] landmark_extractor (uses apps/landmark_extractor/Dockerfile)
- [ ] Standardize container paths + mounts:
  - [ ] /app (code), /data (artifacts), /logs (jsonl)
  - [ ] Mount host ./data → /data and ./logs → /logs
- [ ] Standardize env vars used by both services (minimal):
  - [ ] DATA_ROOT=/data
  - [ ] LOG_ROOT=/logs
  - [ ] APP_ENV, DEVICE_ID (optional)
- [ ] Document “one command to run”:
  - [ ] docker compose up --build


------

## 4) camera_feed_worker (minimal, no learning) (WebSocket)
- [ ] **Window identity rule:** record_id identifies one capture window (many frames), not an individual frame.
- [ ] Accept active session_id from session_manager.
- [ ] Capture a short, bounded camera window.
- [ ] Generate **one record_id per window** (not per frame).
- [ ] Attach metadata: user_id, session_id, record_id, timestamp_start/end.
- [ ] Forward frames (or transient buffer) to landmark_extractor.
- [ ] **Do NOT persist raw video frames** unless explicitly required for a later slice.
- [ ] Apply Route Re-Migration checklist:
  - [ ] routes import only from public schemas
  - [ ] generator unchanged
  - [ ] add module-scoped import guardrail test



  - [ ] Define and lock **HTTP window payload contract** (browser → camera_feed_worker)
  - [ ] Payload format (bounded window representation)
  - [ ] Hard limits: target fps, window_ms, max frames, max request size
  - [ ] Timeout and retry semantics (browser → ingest, ingest → extractor)
  - [ ] Required metadata on ingress: user_id, session_id, record_id, timestamp_start/end

- [ ] Clarify **camera_feed_worker role as browser ingest**
  - [ ] Accept window data uploaded from browser clients
  - [ ] Do **not** rely on OS-level camera access (`/dev/video*`) in containers

- [ ] Enforce capture guardrails (Sprint 1 scope limits):
  - [ ] max capture duration = 120s
  - [ ] max effective FPS = 15
  - [ ] max resolution ≤ 480p
  - [ ] hard server-side cap on total frames (duration × FPS)
  - [ ] hard server-side cap on payload / throughput

## Terminology fix (capture scope)

- Replace all references to “2s window” with **“bounded capture”**.
- Define **window / capture** as:
  - one bounded stream per `record_id`
  - duration between **2s and 120s** (Sprint 1 cap)
- Update UI wording to:
  - **Start Session**
  - **Capture Bounded Gesture (≤ 120s)**
  - **End Session**
- Clarify rule:
  - **One bounded capture (window/stream) → one `record_id` → one feature-ref event**



---

## 5) landmark_extractor (gesture-only, minimal)

- [ ] Convert incoming frames to **Holistic landmark features** (gesture only).
- [ ] Produce **one feature artifact per bounded capture (`record_id`)**.
- [ ] Persist features as a dense **float32 NPZ** array with shape `(T, D)`:
  - `T` = number of frames in the capture (implicit in file)
  - `D` = flattened per-frame landmark dimensionality
- [ ] Write feature file to:
  - `data/users/<user_id>/sessions/<session_id>/features/<record_id>.npz`
- [ ] Compute **sha256** over the full `.npz` file bytes.
- [ ] Build `raw_features_ref` with:
  - `uri` (path to `.npz`)
  - `hash` (sha256)
  - `format = "npz"`
  - `dims = D`
  - `encoding` (string with extractor + window params), e.g.
    `"holistic_landmarks_v1;fps=15;max_window_s=120;extractor_tag=<version>"`
- [ ] Record extractor version/container tag in `raw_features_ref.encoding` (or adjacent metadata).
- [ ] Set `modality = "gesture"` at this stage.
- [ ] **Do NOT classify** (feature extraction only).
- [ ] Emit exactly **one** A3CPMessage referencing `raw_features_ref` via `recorded_schemas`.
- [ ] Apply Route Re-Migration checklist:
  - routes import schemas only from public `schemas` surface.

**Determinism scope**
- Same input bytes + same code revision/container tag ⇒ identical feature file bytes and sha256.
- No requirement for byte-identical output across upgrades.

---

## 6) Schema recording (append-only, one event per capture)

- [ ] For each completed bounded capture (`record_id`), emit **exactly one** A3CPMessage:
  - `source = "landmark_extractor"`
  - includes `user_id`, `session_id`, `record_id`, `timestamp`
  - includes `raw_features_ref` (uri, sha256, encoding, dims, format="npz")
  - `modality = "gesture"`
- [ ] Append the message via the shared `recorded_schemas` writer utility to:
  - `logs/users/<user_id>/sessions/<session_id>.jsonl`
- [ ] **No per-frame / per-chunk messages.** One schema event per bounded capture only.
- [ ] Session JSONL remains strictly append-only (no edits, no rewrites).


---

## 7) Guardrails & replay proof (gesture slice)

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

---

## CI guardrails (scoped to this slice)
- [ ] Add module-scoped tests enforcing route imports use only public schema surface:
  - [ ] api/routes/camera_feed_worker_routes.py imports only from `schemas`
  - [ ] api/routes/landmark_extractor_routes.py imports only from `schemas`
- [ ] Ensure required public schema names are exported in `schemas/__init__.py`
- [ ] Keep generator unchanged; only update mapping/config if new module schemas were added
- [ ] CI fails if any module writes directly to `logs/users/**`; only `recorded_schemas` may write session JSONL.
- [ ] Add CI static-scan test: fail if any code outside `recorded_schemas` writes/appends to `logs/users/**` (allowlist: recorded_schemas writer utility only).



---

## Exit gate (“ready to classify” for gesture)

- [ ] For a completed session, the system can reliably:
  - [ ] load the landmark feature artifact by `record_id` via `raw_features_ref.uri`
  - [ ] recompute and verify integrity (`sha256 == raw_features_ref.hash`)
  - [ ] load the feature array and confirm shape `(T, D)` with `D == raw_features_ref.dims`
- [ ] After a service restart **using the same build/container tag**, replaying the same `record_id` produces identical bytes and the same `sha256`
- [ ] Session JSONL contains **exactly one** landmark feature-ref schema event per bounded capture (`record_id`)

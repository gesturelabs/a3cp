# A3CP — Gesture-First Loop (Start at Session Manager) — REVISED TODO (CLEAN)

## 0) Ground rules for this slice
- [ ] Keep schemas unchanged unless a hard blocker is hit.
- [ ] Append-only events everywhere (no in-place edits).
- [ ] Every downstream module receives: user_id, session_id, timestamp, record_id.
- [ ] **Log writing rule:** Only `recorded_schemas` appends to `logs/sessions/<session_id>.jsonl`.

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

---

## 1) Session Manager (first module in chain)
- [ ] Confirm public API endpoints exist and are stable:
  - [ ] start session → returns session_id
  - [ ] end session → closes session
- [ ] Ensure session_id is unique, stable, and readable.
- [ ] Emit append-only session events as A3CPMessage JSONL:
  - [ ] write via recorded_schemas to `logs/sessions/<session_id>.jsonl`
  - [ ] include source="session_manager", performer_id, timestamp, user_id, session_id, record_id
- [ ] Add minimal “get current session” helper (in-memory acceptable for demo).

---

## 2) Contract for downstream modules (session spine)
- [ ] Define minimal session header object:
  - user_id, session_id, timestamp, device_id?, consent_given?, is_demo?
- [ ] Add one guardrail test:
  - start → end produces two ordered events for the same session_id.

---

## 3) Prepare filesystem & helpers (gesture slice)
- [ ] Define canonical storage roots (single source of truth):
  - [ ] DATA_ROOT = env("DATA_ROOT", default="./data")
  - [ ] LOG_ROOT  = env("LOG_ROOT",  default="./logs")
- [ ] Define per-session paths via helpers (no side effects beyond mkdir):
  - [ ] session_features_dir(user_id, session_id) -> <DATA_ROOT>/users/<user_id>/sessions/<session_id>/features/
  - [ ] session_log_path(session_id) -> <LOG_ROOT>/sessions/<session_id>.jsonl
- [ ] Ensure both Docker services set DATA_ROOT=/data and LOG_ROOT=/logs in docker-compose.yml

- [ ] Add minimal **local browser demo page** (same-origin) to exercise the loop
  - [ ] UI route served by FastAPI (`apps/ui` or `api/main.py`), e.g. `/demo/gesture`
  - [ ] Controls: **Start Session**, **Capture 2s Window**, **End Session**
  - [ ] Uses browser `getUserMedia()` to capture a bounded window
  - [ ] POSTs window payload to `camera_feed_worker`
  - [ ] Displays `session_id`, `record_id`, and success/failure status

---

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

---

## 5) landmark_extractor (gesture-only, minimal)
- [ ] Convert frames to deterministic landmark features (Holistic).
- [ ] Persist features as a **(T, D) array**:
  - T = number of frames in window (implicit in file)
  - D = per-frame flattened dimensionality
- [ ] Set raw_features_ref.dims = D (integer, per SCHEMA_REFERENCE v1.1)
- [ ] Encode windowing params into raw_features_ref.encoding, e.g.:
  - "holistic_landmarks_v1;fps=15;window_ms=2000"
- [ ] Write feature file to:
  - data/users/<user_id>/sessions/<session_id>/features/<record_id>.<npz|parquet>
- [ ] Compute sha256 hash of entire file.
- [ ] Build raw_features_ref:
  - uri
  - hash
  - encoding
  - dims = D
  - format
- [ ] Decide and lock:
  - either set modality="gesture" here, or
  - omit modality until classifier stage.
- [ ] Do NOT classify.
- [ ] Apply Route Re-Migration checklist to routes.

- [ ] Define **determinism scope for hashing**
  - [ ] Same input bytes + same container image/version ⇒ identical feature file bytes and sha256
  - [ ] Record extractor version/container tag in `raw_features_ref.encoding` or adjacent metadata (non-breaking)

---

## 6) Schema recording (append-only)
- [ ] Emit A3CPMessage with:
  - core metadata
  - source="landmark_extractor"
  - raw_features_ref
  - session_id, record_id
- [ ] Append via recorded_schemas to session JSONL.
- [ ] No per-frame messages; one message per window.

---

## 7) Guardrails / proof
- [ ] Verify feature file exists and hash matches raw_features_ref.
- [ ] Verify session JSONL contains valid entry referencing raw_features_ref.
- [ ] Add replay helper:
  - load feature file by record_id
  - confirm deterministic dims (D) and stable hash
- [ ] Guardrail:
  - one camera window → exactly one landmark_extractor A3CPMessage in session JSONL

---

## CI guardrails (scoped to this slice)
- [ ] Add module-scoped tests enforcing route imports use only public schema surface:
  - [ ] api/routes/camera_feed_worker_routes.py imports only from `schemas`
  - [ ] api/routes/landmark_extractor_routes.py imports only from `schemas`
- [ ] Ensure required public schema names are exported in `schemas/__init__.py`
- [ ] Keep generator unchanged; only update mapping/config if new module schemas were added

---

## Exit gate (“ready to classify” for gesture)
- [ ] For a completed session, we can deterministically:
  - [ ] load the feature file by record_id using raw_features_ref.uri
  - [ ] verify integrity by recomputing sha256 == raw_features_ref.hash
  - [ ] confirm the loaded array has shape (T, D) and D == raw_features_ref.dims
- [ ] After service restart, the same record_id replays to identical bytes (same sha256)
- [ ] Session JSONL contains exactly one feature-ref message per window

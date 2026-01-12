# apps/camera_feed_worker/TODO.md

A3CP — camera_feed_worker TODO (module-scoped)

Authoritative architecture for this slice: **browser-based capture**.
- Browser uses `getUserMedia()` to capture a bounded window.
- Browser uploads a bounded capture payload to camera_feed_worker.
- camera_feed_worker acts as ingest + guardrail enforcement + forwarder to landmark_extractor.
- camera_feed_worker does **not** own OS-level camera devices and does **not** rely on `/dev/video*` in containers.
- Transport (Sprint 1 decision): browser uploads bounded capture windows to camera_feed_worker via **WebSocket** (not HTTP).

Current repo state note:
- Legacy shim exists at `api/routes/camera_feed_worker_routes.py`
- It currently deep-imports schemas:
  `from schemas.camera_feed_worker.camera_feed_worker import ...`
Target: routes import schemas only via `from schemas import ...`, and real routes live in `apps/`.

---

## Module invariants (locked)
- **Window identity rule:** `record_id` identifies one capture window (many frames), not an individual frame.
- Accept an explicit, active `session_id` (provided by UI / session_manager); must not infer “current session.”
- Required ingress metadata: `user_id`, `session_id`, `record_id`, `timestamp_start`, `timestamp_end`.
- **Do NOT persist raw video frames/streams to disk** (Sprint 1).
- Forward frames/window payload (or transient buffer) to landmark_extractor.
- Apply Route Re-Migration checklist:
  - routes import schemas only from public `schemas` surface
  - generator unchanged (loads internal schema files)
  - module-scoped import guardrail test
- camera_feed_worker MUST NOT write or append session JSONL directly;
  any schema events (if ever required) must be appended exclusively via
  the `schema_recorder` allowlisted writer utility
---

## A) Canonical app structure (must be created)
Create the runtime app under `apps/` following the canonical architecture.

- [ ] Create app directory:
  - [ ] `apps/camera_feed_worker/`

- [ ] Routes layer (FastAPI adapters only):
  - [ ] `apps/camera_feed_worker/routes/__init__.py`
  - [ ] `apps/camera_feed_worker/routes/router.py`
    - validate request/response schemas
    - call service functions
    - translate domain errors to HTTP responses
    - MUST NOT: business logic, IO, state, ID generation, cross-app deps

- [ ] Service layer (required):
  - [ ] `apps/camera_feed_worker/service.py`
    - implements ingest use-cases for bounded capture windows
    - enforces capture limits and invariants
    - accepts explicit inputs only (no hidden context)
    - MUST NOT: depend on FastAPI, raise HTTP exceptions, perform persistence

- [ ] Repository layer (optional; expected here for forwarding/transport boundary):
  - [ ] `apps/camera_feed_worker/repository.py`
    - IO boundary for forwarding window payload to landmark_extractor
    - transient buffering allowed (memory only; no disk writes)
    - MUST NOT: business decisions, HTTP exceptions

- [ ] Tests (required):
  - [ ] `apps/camera_feed_worker/tests/`
    - [ ] service-level tests (no HTTP required)
    - [ ] thin route tests (if routes exist)

---

## B) Deep route fix (Route Re-Migration)
Eliminate deep imports and migrate routing to canonical app structure.

### 1) Inventory (read-only)
- [ ] Identify legacy route file(s):
  - `api/routes/camera_feed_worker_routes.py`
- [ ] Identify which schema classes it imports and from where
  - current: `schemas.camera_feed_worker.camera_feed_worker`

### 2) Public schema surface exports (no behavior change)
- [ ] Ensure the route-required schema names are exported from `schemas/__init__.py` and included in `__all__`:
  - `CameraFeedWorkerConfig`
  - `CameraFrameMetadata`

- [ ] Confirm that **all** schemas referenced by camera_feed_worker routes
  are imported only via the public surface (`from schemas import ...`)
  and are listed in `schemas.__all__`

### 3) Rewrite legacy shim route (structure-only; no redesign)
- [ ] Update `api/routes/camera_feed_worker_routes.py` to:
  - import schemas only via `from schemas import ...`
  - delegate to canonical router under `apps/camera_feed_worker/routes/router.py`
- [ ] Ensure router is mounted once in `api/main.py` (no duplicate registration)

### 4) Scoped guardrails (tests)
- [ ] Add module-scoped test: fail if `api/routes/camera_feed_worker_routes.py` deep-imports `schemas.<submodule>`
- [ ] Add/extend public-API presence test: required names exist in `schemas.__all__`

### 5) HTTP smoke verification (minimal)
- [ ] Boot and hit endpoint(s); 501 acceptable but must not crash on import/validation

---

## C) Browser ingest behavior (Sprint 1)
- [ ] Accept bounded capture uploaded from browser clients.
- [ ] Generate **one record_id per window** (not per frame) where applicable by contract.
- [ ] Attach/require metadata: `user_id`, `session_id`, `record_id`, `timestamp_start/end`.
- [ ] Forward frames/window payload (or transient buffer) to landmark_extractor.
- [ ] **Do NOT persist raw video frames** unless explicitly required for a later slice.
- [ ] Explicitly out of scope for Sprint 1:
  - owning OS camera devices
  - `/dev/video*`
  - `cv2.VideoCapture()` direct device capture

---

## D) Define and lock HTTP window payload contract (browser → camera_feed_worker)
- [ ] Payload format (bounded window representation)
- [ ] Hard limits: target fps, window_ms, max frames, max request size
- [ ] Timeout and retry semantics (browser → ingest, ingest → extractor)
- [ ] Required metadata on ingress: `user_id`, `session_id`, `record_id`, `timestamp_start/end`

---

## E) Enforce capture guardrails (Sprint 1 scope limits)
- [ ] max capture duration = 120s
- [ ] max effective FPS = 15
- [ ] max resolution ≤ 480p
- [ ] hard server-side cap on total frames (duration × FPS)
- [ ] hard server-side cap on payload / throughput

---

## F) Terminology fix (capture scope)
- [ ] Replace all references to “2s window” with **“bounded capture”**.
- [ ] Define **window / capture** as:
  - one bounded stream per `record_id`
  - duration between **2s and 120s** (Sprint 1 cap)
- [ ] Update UI wording to:
  - **Start Session**
  - **Capture Bounded Gesture (≤ 120s)**
  - **End Session**
- [ ] Clarify rule:
  - **One bounded capture (window/stream) → one `record_id` → one feature-ref event**

---

## G) Cross-cutting CI constraints (reference)
- [ ] Keep generator unchanged; mapping/config updated only if new module schemas were added

- [ ] CI fails if any code outside the `schema_recorder` writer utility writes/appends to `logs/users/**/sessions/*.jsonl`
  - allowlist: `apps/schema_recorder/session_writer.py` only

---

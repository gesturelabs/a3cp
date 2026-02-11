# apps/schema_recorder/TODO.md — REVISED (MVP + Deferred)
---

## Minimal context files required (paste these in the new thread)

To implement `schema_recorder` without hidden assumptions, provide the current contents (or links/paths + relevant excerpts) of:

### potentially useful (ask for when needed)
`schemas/a3cp_message/a3cp_message.py` (canonical A3CPMessage)
`schemas/base/base.py` (Session Spine / BaseSchema)
`utils/paths.py` (must contain `session_log_path(user_id, session_id)` and be pure)
`api/main.py` (router composition / how apps mount routes)

`docs/architecture/app_structure_and_routing.md` (canonical app pattern enforcement)
Session directory creation authority (where session_manager creates the tree):
`apps/session_manager/service.py` (or equivalent)
any helper used to create session log directories
Evidence of current session-log writers (for single-writer CI guardrail):
list/gist/grep results of files that write `logs/users/**/sessions/*.jsonl`, OR
the legacy writer utility file(s)

---


## Purpose (authoritative)

schema_recorder is the only allow-listed writer for session-scoped JSONL logs:

logs/users/<user_id>/sessions/<session_id>.jsonl

It provides a synchronous, ordered, append-only recording service for validated A3CPMessage events.

All semantic guarantees about what is written are enforced upstream.
This module guarantees **how** events are written.

---

## Locked Invariants (MVP)

- Append-only JSONL (no edits, no rewrites)
- Exactly one JSON object per line
- Synchronous write (request returns only after append completes)
- Per-session ordering guaranteed by append order
- OS-level file locking to prevent interleaved writes
- Atomic append discipline (lock → open append → write full line + newline → flush → close)
- No fsync in MVP
- No mkdir in recorder (directories created by session_manager)
- No deduplication or uniqueness enforcement in recorder
- Envelope format: `{ recorded_at, event }`
  - `recorded_at` is UTC ISO 8601 with millisecond precision and `Z` suffix
- `record_id` is authoritative (no extra log_id)
- Missing session path → HTTP 409 Conflict

---


---
## Done
## A) Canonical App Structure

- [x ] Enforce canonical module layout
  - [ x] apps/schema_recorder/routes/router.py exists
  - [ x] apps/schema_recorder/service.py exists
  - [ x] apps/schema_recorder/repository.py exists
  - [ x] apps/schema_recorder/tests/ exists
- [x ] Remove or refactor any legacy/special-case writer files
  - [x ] Ensure all filesystem IO lives exclusively in repository.py



---
## Done
## B) Route Contract (MVP) — schema_recorder (REVISED)

- [x ] Expose HTTP endpoint for session logging
  - [x ] POST `/schema-recorder/append`

- [ x] **LOCK FIRST: error mapping (domain → HTTP)**
  - [x ] `MissingSessionPath` → 409 Conflict
  - [ x] `EventTooLarge` → 413 Payload Too Large
  - [ x] `RecorderIOError` → 500 Internal Server Error



- [ x] Delegate logging to service layer
  - [x ] Route passes only `{ user_id, session_id, message }`
  - [x ] Route does **not** resolve filesystem paths
  - [ x] Route does **not** perform filesystem IO

- [x ] Define success response
  - [x ] Return HTTP 201 Created
  - [ x] Return minimal body `{ record_id, recorded_at }` (from service result)

---
## Done
## C) Service Layer (MVP) — schema_recorder

- [x] Implement public service function `append_event(user_id, session_id, message)`
  - [x] Accept `user_id` + `session_id` (strings/opaque IDs)
  - [x] Accept validated schema payload (`BaseSchema` / A3CPMessage-compatible)
  - [x] Resolve `log_path` internally using `utils/paths.session_log_path(log_root=LOG_ROOT, ...)`
  - [x] Do not read env variables
  - [x] Do not import FastAPI
  - [x] Do not perform filesystem IO (delegates IO to repository)

- [x] Raise domain-level exceptions only (service boundary)
  - [x] MissingSessionPath
  - [x] EventTooLarge
  - [x] RecorderIOError

- [x] No HTTP concerns in service layer


---

## D) Repository Layer (MVP — IO ONLY)

- [x] Repository functions accept concrete `log_path` and serialized bytes

- [x] Implement append-only JSONL writer
  - [x] Acquire OS-level file lock (`flock`)
  - [x] Open file with append semantics
  - [x] Perform atomic single-line `write()`
  - [x] Guarantee newline termination

- [x] Enforce IO-only responsibility
  - [x] Do not mkdir directories
  - [x] Do not enforce uniqueness or deduplication
  - [x] Do not inspect semantic contents

- [x] Fail fast on invalid filesystem state
  - [x] Missing session path raises `MissingSessionPath`
  - [x] OS/FS errors raise `RecorderIOError`


---

## E) Paths & Utilities (MVP)

- [x] Use shared top-level `utils/paths.py`
  - [x] Path helpers are pure (no IO)
  - [x] Path helpers are deterministic
  - [x] Path helpers are parameter-driven (no env reads)

- [x] Ensure recorder resolves paths internally (callers do not)
  - [x] `schema_recorder.service` computes `log_path` via `session_log_path(log_root=LOG_ROOT, user_id, session_id)`
  - [x] Callers pass only `{ user_id, session_id, message }`


---

## F) Single-Writer Enforcement



- [x ] Maintain explicit allowlist (codified, not informal)
  - [ x] Define allowlist in test (single source of truth):
    - [x ] `apps/schema_recorder/repository.py`
  - [ x] Test fails if allowlist is violated

- [x] Enforce cross-module usage contract (implemented)
  - [x] `session_manager` appends session events only via `schema_recorder.service.append_event()`




---

## G) Testing (MVP)
- [x] Service-level tests (covered via session_manager integration tests)
  - [x] Exactly one line appended per call
  - [x] Sequential calls preserve append order

apps/schema_recorder/routes/router.py
apps/schema_recorder/service.py
apps/schema_recorder/repository.py
utils/paths.py
schemas/base/base.py

### A) Repo-wide guardrails (fast static scans) — `tests/guards/`

- [x] Single-writer session JSONL invariant
  - [x] `tests/guards/test_single_writer_session_jsonl.py`
  - [x] Explicit allowlist: `apps/schema_recorder/repository.py`

- [x ] Legacy writer reference guard
  - [x ] Fail if any `apps/**/*.py` contains `append_session_event` or `session_writer` (exclude `*.md`, `*.txt`)

- [ x] Raw session-log path / pattern guard
  - [ x] Fail if any `apps/**/*.py` contains `logs/users/` or `sessions/` + `.jsonl` outside allowlist (exclude docs)

- [ x] IO primitive confinement guard
  - [x ] Fail if any non-allowlisted `apps/**/*.py` uses direct file IO primitives used for recording:
    - [x ] `open(` / `Path.open(` / `os.open(` / `os.write(` / `fcntl.flock(` (tune allowlist as needed)
  - [ x] Explicit allowlist: `apps/schema_recorder/repository.py` (and only that file)

- [x ] Import surface guard (architecture)
  - [x] Assert `apps/schema_recorder/**/*.py` imports schemas only from the public `schemas` surface (no deep/private imports)


### B) Route-level tests — `apps/schema_recorder/tests/test_routes.py`

- [x ] Boundary validation (no service call)
  - [x ] Invalid schema payload rejected (422); `service.append_event` NOT called
  - [x ] (Optional) Unparseable JSON rejected (400); service NOT called

- [x x] Required-field enforcement (422; parameterized; no service call)
  - [ ] Missing `user_id`
  - [ x] Missing `session_id`
  - [ x] Missing `source`

- [x ] Domain → HTTP mapping
  - [ x] `MissingSessionPath` → 409
  - [x ] `EventTooLarge` → 413
  - [x ] `RecorderIOError` → 500

- [ x] Success contract
  - [ x] Returns 201 Created
  - [ x] Response body is exactly `{record_id, recorded_at}` (no extra keys)
  - [ x] `record_id` echoes the request `record_id`
  - [x ] `recorded_at` is ISO-8601 (shape check only; don’t assert exact value)


### C) Repository-level tests — `apps/schema_recorder/tests/test_repository.py`

- [x ] Size limit + atomicity
  - [x ] Near-limit payload writes exactly one JSONL line (newline-terminated)
  - [x ] Over-limit raises `EventTooLarge` AND:
    - [x ] File is not created if absent
    - [x ] File content unchanged if it already exists

- [x ] Filesystem failure modes
  - [x ] Missing parent session directory → `MissingSessionPath` (creates nothing)
  - [x ] Unwritable path → `RecorderIOError` (creates nothing / no change)

- [x ] Concurrency / locking
  - [ x] `flock(LOCK_EX)` prevents interleaved writes under concurrency:
    - [ x] N concurrent appends ⇒ exactly N newlines appended
    - [ x] Each line parses as valid JSON

- [x ] JSONL line invariants
  - [x ] Exactly one newline-terminated JSON object per append
  - [ x] No embedded newlines in the written line (i.e., one event == one line)





- [x ] Validation (non-test, quick manual check)
  - [ x] Confirm repository actually uses `fcntl.flock` + append semantics + single `write()` + no mkdir






---
## I) Post-MVP / Deferred (DO NOT IMPLEMENT NOW)

- [ ] Event replay / duplication protection (service policy)
- [ ] Within-session uniqueness policy (e.g., reject duplicate `(user_id, session_id, record_id, source)`)
- [ ] Artifact hash replay detection within session (service policy)
- [ ] Selective durability (fsync for commit-critical events) (repository)
- [ ] Secondary sink for session-less events (`logs/users/<user_id>/events.jsonl`) (service + paths)
- [ ] Log rotation / archival policy (ops/maintenance)
- [ ] Canonical / stable JSON serialization (service)
- [ ] Explicit per-session sequence numbers (service; requires state)
- [ ] Metrics / instrumentation (service/route)


## Notes / Action Items

- [x ] Double-check source handling in schemas
  - [ x] Keep `source` optional in schema if needed
  - [ x] Enforce `source` as mandatory at recorder route level



## Post-refactor cleanup (session_writer removal → schema_recorder only)

- [x ] Docs/TODO references cleanup (non-code)
  - [x ] Update `apps/camera_feed_worker/todo.md`: replace any allowlist reference to `apps/schema_recorder/session_writer.py` with `apps/schema_recorder/service.py` (+ note: IO in `apps/schema_recorder/repository.py`)
  - [x ] Update `apps/landmark_extractor/TODO.md`: replace `session_writer.py` references with `schema_recorder.service.append_event()`
  - [ x] Update `apps/schema_recorder/TODO.md`: remove the “session_writer is deleted” self-referential checklist lines; replace with a short “completed refactor” note + current public API
  - [x ] Repo-wide grep (docs-only) to ensure references are consistent:
    - [ ] `grep -R --line-number "session_writer.py\|append_session_event" docs apps | cat`

- [ ] API/docstring polish (code comments only; behavior unchanged)
  - [ ] Fix `apps/schema_recorder/service.py` docstring to match current signature (`user_id`, `session_id`, `message`) and remove stale mentions of `log_path`/`event`
  - [ ] Add a one-line comment in `apps/schema_recorder/config.py` stating LOG_ROOT is intentionally patchable for tests



- [ ] Import/legacy shim audit
  - [ ] Verify no imports remain from deleted modules:
    - [ ] `grep -R --line-number --binary-files=without-match "apps\.session_manager\.repository" .`
    - [ ] `grep -R --line-number --binary-files=without-match "apps\.schema_recorder\.session_writer" .`



----------------
# schema_recorder — Remaining MVP Safety Tasks (ONLY)

## 1) Repository correctness fix (prevents subtle line-shape bugs)
- [x ] Fix duplicate newline normalization in `apps/schema_recorder/repository.py`
  - Change second `_ensure_newline(line_bytes)` to `_ensure_newline(data)`.

## 2) Enforce “payload-free JSONL” at the single-writer boundary (prevents raw data persistence)
- [x ] Add content-based payload rejection in `apps/schema_recorder/service.py` (`append_event`, before `json.dumps`)
  - Recursively scan `message.model_dump(mode="json")` for payload-bearing fields.
  - Reject on a narrow denylist (at minimum):
    - `frame_data`
    - the actual audio blob field(s) used by `schemas/sound_classifier/*` when `audio_format` is `base64` or `bytes`
  - Raise a dedicated domain exception (e.g., `PayloadNotAllowed`).

## 3) Route mapping for payload rejection (prevents inconsistent failure modes)
- [ x] Map `PayloadNotAllowed` to a deterministic HTTP status in `apps/schema_recorder/routes/router.py`
  - Recommended: `422 Unprocessable Entity`.

## 4) Tests that lock the payload-free invariant (prevents regressions)
- [x ] Add tests under `apps/schema_recorder/tests/` proving:
  - Tiny payload-bearing message is rejected even when under `MAX_EVENT_BYTES`.
  - Route returns the chosen status code deterministically.
  - `repository.append_bytes()` is not called on payload rejection.

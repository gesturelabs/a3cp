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

## Clarifications to lock before implementation (MVP)

### Locking mechanism (explicit, testable)
- MUST use `flock(LOCK_EX)` via `fcntl.flock()` on the **session JSONL file descriptor**.
- Lock is held across: `open → write → flush → close`.
- MUST NOT use a separate lockfile.
- MUST NOT also use `fcntl.lockf()` / POSIX record locks in addition to `flock`.

### Write atomicity (explicit syscall semantics)
- File MUST be opened with append semantics (`O_APPEND` equivalent).
- Each JSONL record MUST be written as one complete line: `json(envelope) + "\n"`.
- The full line MUST be emitted using a **single `write()` call** (no chunking for one event).
- MUST define + enforce `MAX_EVENT_BYTES` (UTF-8 bytes for one JSONL line incl. newline).
- Oversized events MUST raise domain exception `EventTooLarge`.
- Tests: near-limit payload succeeds; over-limit payload rejects with no partial write.

### Time semantics (avoid ambiguity)
- `event.timestamp` = event-time, owned by upstream.
- `recorded_at` = write-time, owned by recorder.
- Recorder MUST NOT inspect, modify, normalize, or reinterpret `event.timestamp`.
- Recorder MUST preserve the `event` object exactly as received.
- Tests assert `event.timestamp` is byte-for-byte preserved.

### Filesystem integrity assumption (explicit failure model)
- session_manager MUST create the full session directory tree before recording begins.
- Recorder MUST NOT mkdir directories.
- **Log file creation rule:** recorder MAY create `<session_id>.jsonl` if (and only if) the
  parent session directory already exists.
- Missing parent session directory raises domain exception `MissingSessionPath`.
- Route maps `MissingSessionPath` → HTTP 409 Conflict.
- Tests: missing parent directory returns 409 and creates nothing; unwritable path returns 500.

### Single-writer enforcement (REQUIRED CI guardrail)
- Only `apps/schema_recorder/repository.py` may write/append to:
  `logs/users/**/sessions/*.jsonl`
- CI MUST enforce at least one mechanism:
  - static grep / AST check, OR
  - import-guard test, OR
  - centralized writer API + test that no other module writes session logs.
- Guardrail test MUST run in default unit test suite.

---

## A) Canonical App Structure (REQUIRED)

- [x ] Enforce canonical module layout
  - [ x] apps/schema_recorder/routes/router.py exists
  - [ x] apps/schema_recorder/service.py exists
  - [ x] apps/schema_recorder/repository.py exists
  - [ x] apps/schema_recorder/tests/ exists
- [x ] Remove or refactor any legacy/special-case writer files
  - [x ] Ensure all filesystem IO lives exclusively in repository.py

## Post-refactor cleanup (session_writer removal → schema_recorder only)

- [ ] Docs/TODO references cleanup (non-code)
  - [ ] Update `apps/camera_feed_worker/todo.md`: replace any allowlist reference to `apps/schema_recorder/session_writer.py` with `apps/schema_recorder/service.py` (+ note: IO in `apps/schema_recorder/repository.py`)
  - [ ] Update `apps/landmark_extractor/TODO.md`: replace `session_writer.py` references with `schema_recorder.service.append_event()`
  - [ ] Update `apps/schema_recorder/TODO.md`: remove the “session_writer is deleted” self-referential checklist lines; replace with a short “completed refactor” note + current public API
  - [ ] Repo-wide grep (docs-only) to ensure references are consistent:
    - [ ] `grep -R --line-number "session_writer.py\|append_session_event" docs apps | cat`

- [ ] API/docstring polish (code comments only; behavior unchanged)
  - [ ] Fix `apps/schema_recorder/service.py` docstring to match current signature (`user_id`, `session_id`, `message`) and remove stale mentions of `log_path`/`event`
  - [ ] Add a one-line comment in `apps/schema_recorder/config.py` stating LOG_ROOT is intentionally patchable for tests

- [ ] Guardrails (lightweight tests)
  - [ ] Add a repo test that fails if any `apps/**.py` contains `append_session_event` or `session_writer` (excluding markdown)
  - [ ] Add a repo test that asserts only `apps/schema_recorder/repository.py` contains `os.open(` / `fcntl.flock(` / `os.write(` (or equivalent IO primitives), to prevent IO leakage into services/routes

- [ ] Import/legacy shim audit
  - [ ] Verify no imports remain from deleted modules:
    - [ ] `grep -R --line-number --binary-files=without-match "apps\.session_manager\.repository" .`
    - [ ] `grep -R --line-number --binary-files=without-match "apps\.schema_recorder\.session_writer" .`

- [ ] Commit hygiene
  - [ ] Ensure changelog/devlog note exists for: “Removed session_writer; schema_recorder is sole writer; session_manager creates session dir; tests updated to patch schema_recorder.config.LOG_ROOT”


---

## B) Route Contract (MVP) — schema_recorder

- [ ] Expose HTTP endpoint for session logging
  - [ ] POST `/schema-recorder/append`

- [ ] Accept only fully validated schema payloads
  - [ ] Request body must deserialize into `BaseSchema` / `A3CPMessage`
  - [ ] Reject unparseable or invalid payloads at the route boundary

- [ ] Enforce required fields at route level
  - [ ] Reject missing `session_id`
  - [ ] Reject missing `user_id`
  - [ ] Reject missing `source`

- [ ] Delegate logging to service layer
  - [ ] Route passes only `{ user_id, session_id, message }`
  - [ ] Route does **not** resolve filesystem paths
  - [ ] Route does **not** perform filesystem IO

- [ ] Define success response
  - [ ] Return HTTP 201 Created
  - [ ] Return minimal body `{ record_id, recorded_at }` (from service result)

- [ ] Define error mapping (domain → HTTP)
  - [ ] `MissingSessionPath` → 409 Conflict
  - [ ] `EventTooLarge` → 413 Payload Too Large
  - [ ] `RecorderIOError` → 500 Internal Server Error

---

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

## F) Single-Writer Enforcement (REQUIRED)

- [ ] Enforce single-writer invariant via CI / pytest
  - [ ] Add pytest that scans `apps/**/*.py` and fails if session JSONL writes occur outside `apps/schema_recorder/repository.py`
    - [ ] Disallow `open(` / `os.open(` / `pathlib.Path.open(` in non-repository modules
    - [ ] Disallow hardcoded session log patterns (`logs/users/`, `sessions/*.jsonl`) outside repository
    - [ ] Explicitly allow `apps/schema_recorder/repository.py`

- [ ] Maintain explicit allowlist (codified, not informal)
  - [ ] Define allowlist in test (single source of truth):
    - [ ] `apps/schema_recorder/repository.py`
  - [ ] Test fails if allowlist is violated

- [x] Enforce cross-module usage contract (implemented)
  - [x] `session_manager` appends session events only via `schema_recorder.service.append_event()`

- [ ] Verify cross-module usage contract for other producers
  - [ ] Audit `landmark_extractor` to confirm it appends only via `schema_recorder`
  - [ ] Add pytest asserting `landmark_extractor` does not perform filesystem writes
  - [ ] Require future modules to satisfy the same pytest guard

- [ ] Best-practice pytest structure (anti-regression)
  - [ ] Place enforcement tests under `tests/architecture/` or `tests/guards/`
  - [ ] Tests must:
    - [ ] Be fast (string/AST scan only; no filesystem mutation)
    - [ ] Fail loudly with file + line number
    - [ ] Not rely on import-time side effects
  - [ ] Tests should explain *why* the invariant exists (docstring at top of test file)

---

## G) Testing (MVP)

- [x] Service-level tests (covered via session_manager integration tests)
  - [x] Exactly one line appended per call
  - [x] Sequential calls preserve append order

- [ ] Repository-level tests
  - [ ] File locking prevents interleaving under concurrency
  - [ ] Oversized event raises EventTooLarge with no partial write
  - [ ] Missing path raises MissingSessionPath

- [ ] Route-level tests (blocked until Route Contract is implemented)
  - [ ] Reject missing session_id
  - [ ] Reject missing source
  - [ ] Oversized event → 413
  - [ ] Missing session path → 409
  - [ ] IO failure → 500
  - [ ] Success returns 201 with minimal response body

- [ ] Import guardrail tests
  - [ ] schema_recorder imports schemas only from public `schemas` surface


---
## H) Explicit Non-Responsibilities (DOCUMENTED)

- [ ] Recorder does NOT guarantee (documented in schema_recorder docs)
  - [ ] Event replay / duplication protection
  - [ ] Uniqueness of record_id
  - [ ] Semantic correctness of A3CPMessage
  - [ ] One-event-per-capture enforcement
  - [ ] Validation of raw_features_ref contents
  - [ ] Session lifecycle correctness
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

- [ ] Double-check source handling in schemas
  - [ ] Keep `source` optional in schema if needed
  - [ ] Enforce `source` as mandatory at recorder route level

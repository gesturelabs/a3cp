# apps/schema_recorder/TODO.md — REVISED (MVP + Deferred)
---

## Minimal context files required (paste these in the new thread)

To implement `schema_recorder` without hidden assumptions, provide the current contents (or links/paths + relevant excerpts) of:

### Required
- [ ] `schemas/a3cp_message/a3cp_message.py` (canonical A3CPMessage)
- [ ] `schemas/base/base.py` (Session Spine / BaseSchema)
- [ ] `utils/paths.py` (must contain `session_log_path(user_id, session_id)` and be pure)
- [ ] `api/main.py` (router composition / how apps mount routes)

### Strongly recommended
- [ ] `docs/architecture/app_structure_and_routing.md` (canonical app pattern enforcement)
- [ ] Session directory creation authority (where session_manager creates the tree):
  - [ ] `apps/session_manager/service.py` (or equivalent)
  - [ ] any helper used to create session log directories
- [ ] Evidence of current session-log writers (for single-writer CI guardrail):
  - [ ] list/gist/grep results of files that write `logs/users/**/sessions/*.jsonl`, OR
  - [ ] the legacy writer utility file(s)

### Optional
- [ ] Any legacy recorder endpoint or code (if it exists) to remove/replace cleanly

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
- MUST use `flock(LOCK_EX)` on the **session JSONL file descriptor** (no separate lockfile).
- Lock is held across: `open → write → flush → close`.
- MUST NOT mix locking primitives (no `fcntl` in addition to `flock`).
- Concurrency test must show full, non-interleaved JSONL lines.

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
- Recorder MUST NOT mkdir; missing/partial path is a hard conflict.
- Missing session path raises domain exception `MissingSessionPath`.
- Route maps `MissingSessionPath` → HTTP 409 Conflict.
- Tests: missing path returns 409 and creates nothing; unwritable path returns 500.

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

- [ ] Enforce canonical module layout
  - [ ] apps/schema_recorder/routes/router.py exists
  - [ ] apps/schema_recorder/service.py exists
  - [ ] apps/schema_recorder/repository.py exists
  - [ ] apps/schema_recorder/tests/ exists
- [ ] Remove or refactor any legacy/special-case writer files
  - [ ] Ensure all filesystem IO lives exclusively in repository.py

---

## B) Route Contract (MVP)

- [ ] Expose HTTP endpoint for session logging (e.g. POST `/schema-recorder/append`)
- [ ] Accept only fully validated A3CPMessage payloads
- [ ] Enforce required fields at route level
  - [ ] Reject missing session_id
  - [ ] Reject missing source
- [ ] Resolve session log path in route
  - [ ] Use `utils/paths.py` to compute `log_path = session_log_path(user_id, session_id)`
  - [ ] Pass resolved `log_path` + validated event to service
- [ ] Define success response
  - [ ] Return HTTP 201 Created
  - [ ] Return minimal body `{ record_id, recorded_at }`
- [ ] Define error mapping (domain → HTTP)
  - [ ] MissingSessionPath → 409 Conflict
  - [ ] EventTooLarge → 413 Payload Too Large
  - [ ] RecorderIOError → 500 Internal Server Error

---

## C) Service Layer (MVP)

- [ ] Implement public service function (e.g. `append_event(log_path, event)`)
  - [ ] Accept fully resolved `log_path` (Path)
  - [ ] Accept validated A3CPMessage payload
  - [ ] Do not read env variables
  - [ ] Do not import FastAPI
- [ ] Raise domain-level exceptions only
  - [ ] MissingSessionPath
  - [ ] EventTooLarge
  - [ ] RecorderIOError
- [ ] No HTTP concerns in service layer

---

## D) Repository Layer (MVP — IO ONLY)

- [ ] Repository functions accept concrete `log_path` and serialized bytes
- [ ] Implement append-only JSONL writer
  - [ ] Acquire OS-level file lock (`flock`)
  - [ ] Open file with append semantics
  - [ ] Perform atomic single-line `write()`
  - [ ] Guarantee newline termination
  - [ ] Wrap payload as `{ recorded_at, event }`
- [ ] Enforce IO-only responsibility
  - [ ] Do not mkdir directories
  - [ ] Do not enforce uniqueness or deduplication
  - [ ] Do not inspect semantic contents
- [ ] Fail fast on invalid filesystem state
  - [ ] Missing session path raises `MissingSessionPath`
  - [ ] OS/FS errors raise `RecorderIOError`

---

## E) Paths & Utilities (MVP)

- [ ] Use shared top-level `utils/paths.py`
  - [ ] Path helpers are pure (no IO)
  - [ ] Path helpers are deterministic
  - [ ] Path helpers are parameter-driven (no env reads)
- [ ] Ensure recorder receives fully resolved paths from caller

---

## F) Single-Writer Enforcement (REQUIRED)

- [ ] Enforce single-writer invariant via CI/static checks
  - [ ] Fail if any code outside schema_recorder repository writes/appends to session logs
- [ ] Maintain allowlist
  - [ ] Allow filesystem writes only from apps/schema_recorder/repository.py
- [ ] Enforce cross-module usage contract
  - [ ] session_manager appends session events only via schema_recorder
  - [ ] landmark_extractor appends feature-ref events only via schema_recorder
  - [ ] Future modules follow same rule

---

## G) Testing (MVP)

- [ ] Service-level tests
  - [ ] Exactly one line appended per call
  - [ ] Sequential calls preserve append order
- [ ] Repository-level tests
  - [ ] File locking prevents interleaving under concurrency
  - [ ] Oversized event raises EventTooLarge with no partial write
  - [ ] Missing path raises MissingSessionPath
- [ ] Route-level tests
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

- [ ] Recorder does NOT guarantee:
  - [ ] Event replay / duplication protection
  - [ ] Uniqueness of record_id
  - [ ] Semantic correctness of A3CPMessage
  - [ ] One-event-per-capture enforcement
  - [ ] Validation of raw_features_ref contents
  - [ ] Session lifecycle correctness

---

## I) Post-MVP / Deferred (DO NOT IMPLEMENT NOW)

- [ ] Event replay / duplication protection
- [ ] Within-session record_id uniqueness checks
- [ ] Artifact hash replay detection
- [ ] Selective durability (fsync for commit-critical events)
- [ ] Secondary sink for session-less events (`logs/users/<user_id>/events.jsonl`)
- [ ] Log rotation / archival policy
- [ ] Canonical JSON serialization
- [ ] Explicit per-session sequence numbers
- [ ] Metrics / instrumentation

---

## Notes / Action Items

- [ ] Double-check source handling in schemas
  - [ ] Keep `source` optional in schema if needed
  - [ ] Enforce `source` as mandatory at recorder route level

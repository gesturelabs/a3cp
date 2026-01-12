# apps/schema_recorder/TODO.md — REVISED (MVP + Deferred)

Purpose (authoritative)

schema_recorder is the only allow-listed writer for session-scoped JSONL logs:

logs/users/<user_id>/sessions/<session_id>.jsonl

It provides a synchronous, ordered, append-only recording service for validated A3CPMessage events.

All semantic guarantees about what is written are enforced upstream.
This module guarantees how events are written.

---

Locked Invariants (MVP)

- Append-only JSONL (no edits, no rewrites)
- Exactly one JSON object per line
- Synchronous write (request returns only after append completes)
- Per-session ordering guaranteed by append order
- OS-level file locking to prevent interleaved writes
- Atomic append discipline (lock → open append → write full line + newline → flush → close)
- No fsync in MVP
- No mkdir in recorder (directories created by session_manager)
- No deduplication or uniqueness enforcement in recorder
- Envelope format: { recorded_at, event }
- record_id is authoritative (no extra log_id)
- Missing session path → HTTP 409 Conflict

---

A) Canonical App Structure (REQUIRED)

- [ ] Enforce canonical module layout
  - [ ] apps/schema_recorder/routes/router.py exists
  - [ ] apps/schema_recorder/service.py exists
  - [ ] apps/schema_recorder/repository.py exists
  - [ ] apps/schema_recorder/tests/ exists
- [ ] Remove or refactor any legacy/special-case writer files
  - [ ] Ensure all filesystem IO lives exclusively in repository.py

---

B) Route Contract (MVP)

- [ ] Expose HTTP endpoint for session logging (e.g. POST /schema-recorder/append)
- [ ] Accept only fully validated A3CPMessage payloads
- [ ] Enforce required fields at route level
  - [ ] Reject missing session_id
  - [ ] Reject missing source
- [ ] Define success response
  - [ ] Return HTTP 201 Created
  - [ ] Return minimal body { record_id, recorded_at }
- [ ] Define error mapping
  - [ ] Missing session path → 409 Conflict
  - [ ] IO failures → 500 Internal Server Error

---

C) Service Layer (MVP)

- [ ] Implement public service function (e.g. append_event)
  - [ ] Accept fully resolved log path as parameter
  - [ ] Do not read env variables
  - [ ] Do not import FastAPI
- [ ] Raise domain-level exceptions only
  - [ ] No HTTP concerns in service layer

---

D) Repository Layer (MVP — IO ONLY)

- [ ] Implement append-only JSONL writer
  - [ ] Acquire OS-level file lock (Linux)
  - [ ] Perform atomic single-line write
  - [ ] Guarantee newline termination
  - [ ] Wrap payload as { recorded_at, event }
- [ ] Enforce IO-only responsibility
  - [ ] Do not mkdir directories
  - [ ] Do not enforce uniqueness or deduplication
  - [ ] Do not inspect semantic contents
- [ ] Fail fast on invalid filesystem state
  - [ ] Missing session path raises domain exception

---

E) Paths & Utilities (MVP)

- [ ] Use shared top-level utils/paths.py
  - [ ] Path helpers are pure (no IO)
  - [ ] Path helpers are deterministic
  - [ ] Path helpers are parameter-driven (no env reads)
- [ ] Ensure recorder receives fully resolved paths from caller

---

F) Single-Writer Enforcement (REQUIRED)

- [ ] Enforce single-writer invariant via CI/static checks
  - [ ] Fail if any code outside schema_recorder repository writes/appends to logs/users/**/sessions/*.jsonl
- [ ] Maintain allowlist
  - [ ] Allow filesystem writes only from apps/schema_recorder/repository.py
- [ ] Enforce cross-module usage contract
  - [ ] session_manager appends session events only via schema_recorder
  - [ ] landmark_extractor appends feature-ref events only via schema_recorder
  - [ ] Future modules follow same rule

---

G) Testing (MVP)

- [ ] Service-level tests
  - [ ] Exactly one line appended per call
  - [ ] Sequential calls preserve append order
- [ ] Repository-level tests
  - [ ] File locking prevents interleaving under concurrency
  - [ ] Missing path raises expected exception
- [ ] Route-level tests
  - [ ] Reject missing session_id
  - [ ] Reject missing source
  - [ ] Success returns 201 with minimal response body
- [ ] Import guardrail tests
  - [ ] schema_recorder imports schema types only from public schemas surface (no deep imports)

---

H) Explicit Non-Responsibilities (DOCUMENTED)

- [ ] Document that recorder does NOT guarantee:
  - [ ] Event replay / duplication protection
  - [ ] Uniqueness of record_id
  - [ ] Semantic correctness of A3CPMessage
  - [ ] One-event-per-capture enforcement
  - [ ] Validation of raw_features_ref contents
  - [ ] Session lifecycle correctness

---

I) Post-MVP / Deferred (DO NOT IMPLEMENT NOW)

- [ ] Event replay / duplication protection
- [ ] Within-session record_id uniqueness checks
- [ ] Artifact hash replay detection
- [ ] Selective durability (fsync for commit-critical events)
- [ ] Secondary sink for session-less events (logs/users/<user_id>/events.jsonl)
- [ ] Log rotation / archival policy
- [ ] Canonical JSON serialization
- [ ] Explicit per-session sequence numbers
- [ ] Metrics / instrumentation

---

Notes / Action Items

- [ ] Double-check source handling in schemas
  - [ ] Keep source optional in schema if needed
  - [ ] Enforce source as mandatory at recorder route level

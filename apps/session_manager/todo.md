# apps/session_manager/TODO.md

A3CP — session_manager TODO (module-scoped)

Scope: session boundary management and authoritative start/end events.
Status note (authoritative for this file): canonical migration completed (routes/service/repository/idgen/models), schemas fixed, baseline tests passing; behavioral invariants + expanded tests below are pending.

---

## Module invariants (locked)
- Schemas unchanged unless a hard blocker is hit.
- Append-only events everywhere (no in-place edits).
- Downstream request contract (non-session-manager endpoints): every downstream request includes `user_id` and `session_id` (and any module-specific fields).
- Session boundary event contract (session_manager outputs/logs): every emitted start/end event includes `user_id`, `session_id`, server-authoritative `timestamp`, and a new `record_id`.
- Log writing rule: only `schema_recorder` appends to `logs/users/<user_id>/sessions/<session_id>.jsonl` (session_manager may create the session directory but must not write the JSONL file).
- Storage rule (Sprint 1): do not persist raw video; persist only landmark-derived feature artifacts + `raw_features_ref` metadata (recorded later by `landmark_extractor`, not `session_manager`).
- Filesystem authority split (locked): session_manager MAY create session directories (mkdir only); it MUST NOT open, create, or append `*.jsonl` files. All JSONL writes are performed exclusively by `schema_recorder`.

---

## Slice-1 concurrency constraint (locked for Slice 1)
- Run single FastAPI worker / single replica for Slice 1.
- `session_manager` active-session state may be process-local memory.
- Deployment MUST enforce single-worker (no scale-out) until Option B is implemented.
- Option B (multi-worker/replica via shared store) is deferred and requires a dedicated migration.

---

## A) Completed

### Core behavior
- [x] `/sessions.start` returns `session_id`
- [x] `/sessions.end` closes session
- [x] Events appended via `schema_recorder`
- [x] Guardrail test: start → end emits 2 ordered events for the same `session_id`

### Canonical app architecture migration
- [x] Module migrated to canonical structure (routes/service/repository/idgen/models)
- [x] Schemas fixed
- [x] Baseline tests passing

---

## B) Remaining (this slice)

#### 1) Event invariants enforced + tested (session_manager outputs & logs)
- [x] Event invariants enforced + tested


#### 1.1 Authoritative boundary-event contract (emitted / recorded events)
- [ ] Enforce/test invariants on **emitted boundary events** (the `SessionManagerStartOutput` / `SessionManagerEndOutput` recorded to JSONL):
  - `source` is **always** `"session_manager"` (server-fixed)
  - `user_id` present and non-empty
  - `session_id` present and non-empty
  - `timestamp` present and **server-authoritative** (UTC, ISO 8601, millisecond precision, `"Z"` suffix)
  - `record_id` present and **server-generated UUIDv4**
  - `performer_id` policy:
    - required for human-originated boundaries
    - allowed value `"system"` for system-generated boundaries

> NOTE: These invariants apply to **emitted/recorded events only**.
> Input permissiveness (`timestamp`, `source`, `record_id` on input) depends on `BaseSchema.model_config.extra` and MUST NOT affect emitted authority.

## Remaining tests for 1.1 — Authoritative boundary-event contract

### Required (still missing)
- [ x] Recorded JSONL timestamp format invariant
  - Read JSONL line from schema_recorder output
  - Assert `event.timestamp` matches ISO-8601 UTC with millisecond precision and `Z` suffix
  - Regex example: `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$`

### Strongly recommended (authority hardening)
- [x ] Input cannot override server-authoritative `record_id`
  - Provide input `record_id`
  - Assert emitted/recorded event `record_id` is different and UUIDv4

- [x ] Input cannot override server-authoritative `timestamp`
  - Provide stale/fake input timestamp
  - Assert emitted timestamp is near server “now” and not equal to input

- [ x] Input cannot override `source`
  - If input allows `source`, set to something else
  - Assert emitted/recorded event has `source == "session_manager"`

### Optional (policy completeness)
- [x ] `"system"` performer_id accepted for boundaries
  - Start/end with `performer_id="system"`
  - Assert success and recorded value is `"system"`

#### 1.2 Session identity and continuity
- [x] Enforce/test invariant:
  - the `session_id` emitted by `/sessions.end` equals the `session_id` issued by `/sessions.start` for the same session
  - mismatched or unknown `session_id` → rejected (404), user mismatch → rejected (403)

#### 1.3 Record identity authority & uniqueness
- [x ] Enforce/test invariant:
  - `/sessions.start` emits a **new server-generated** `record_id` (UUIDv4) for the start boundary event
  - `/sessions.end` emits a **new server-generated** `record_id` (UUIDv4) for the end boundary event
  - boundary-event `record_id` MUST be unique and MUST NOT be reused across start/end events
  - any client-supplied `record_id` in input is treated as a request/correlation field only and MUST NOT become the emitted boundary-event `record_id`

#### 1.4 Source & timestamp authority (clarified)
- [x ] Enforce/test invariant:
  - emitted boundary-event `source` is `"session_manager"` regardless of any input value
  - emitted boundary-event `timestamp` is generated by `session_manager` regardless of any input value
  - tests must assert emitted authority even when input contains `source` / `timestamp`


#### 1.5 Single active session per user
- [x ] Enforce/test invariant:
  - a user MAY NOT have more than one active session at the same time
  - `/sessions.start` while an active session exists for the same `user_id` → 409 Conflict
  - Slice-1 implementation must be explicit:
    - maintain `active_session_by_user_id`, OR
    - scan `_sessions` for an active session (acceptable for Slice 1; document choice)
  - tests:
    - start session for user → 200
    - start again for same user without ending → 409
    - start for different user → 200

- [ x] Enforce/test invariant (output validation & no-record-on-failure):
  - boundary events MUST be successfully constructed and validated as:
    - `SessionManagerStartOutput` for start
    - `SessionManagerEndOutput` for end
  - if boundary-event construction/validation fails, then:
    - no directory side effects beyond allowed mkdir (if any) for that request path
    - no JSONL append is attempted (or, equivalently, JSONL file remains unchanged)
    - no in-memory state mutation occurs

- [ x]tests (choose at least one deterministic forcing strategy):
    - force an invalid output by injecting a clearly invalid field value (e.g., empty `session_id`, empty `user_id`, or invalid `source`) at construction time in a controlled test seam, and assert:
      - response is 500 (or 400 if you intentionally treat it as client fault)
      - JSONL did not change
      - in-memory state did not change


#### 1.6 Output validation & fail-fast behavior
- [x ] Enforce/test invariant:
  - session boundary outputs are Pydantic-validated (`SessionManagerStartOutput` / `SessionManagerEndOutput`)
  - invalid boundary-event payload MUST NOT be recorded to session JSONL (fail fast)

#### 1.7 Idempotency and terminal state
- [x ] Enforce/test invariant:
  - `/sessions.end`: repeated end for the same `session_id` → 409 Conflict

#### 1.8 System-initiated closure
- [x ] Enforce/test invariant:
  - sessions MAY be closed by the system with `performer_id="system"`
  - system-closed end event MUST:
    - preserve the original `session_id`
    - generate a new unique server `record_id`
    - use server-authoritative `timestamp`

- [ x] Enforce/test fail-fast ordering (no side effects on rejection):
  - `/sessions.start` when an active session exists for `user_id` → 409
    - MUST NOT generate a new `session_id`
    - MUST NOT mkdir a new session directory
    - MUST NOT append any event
    - MUST NOT mutate `_sessions`
  - `/sessions.end` for already-closed session → 409
    - MUST NOT append any event
    - MUST NOT change state
  - `/sessions.end` for not found / user mismatch → 404/403
    - MUST NOT append any event
    - MUST NOT change state
  - tests must assert “no append attempted” and “no mkdir attempted” (where practical) for these rejection paths


#### 1.9 Atomic recording semantics
- [ x] Enforce/test invariant (Slice 1 atomicity):
  - mutate in-memory session state only after a successful `schema_recorder` append
  - START:
    - if append fails, no active session is created (no `_sessions[...]` entry)
  - END:
    - if append fails, session remains active (status not flipped to closed)
  - tests must simulate recorder failure and assert no state change



### 2) performer_id policy enforced at route ingress (session_manager)

performer_id must be provided for all human-originated requests; only "system" is exempt. No inference, substitution, or fallback is permitted.

- [ x] Enforce/test ingress rules (before any state mutation or recording):
  - `/sessions.start`:
    - if `performer_id == "system"` → accept (system-generated boundary)
    - if `performer_id` is missing or empty → reject (400)
  - `/sessions.end`:
    - if `performer_id == "system"` → accept
    - if `performer_id` is missing or empty → reject (400)

- [x ] Explicitly forbid auto-filling:
  - `session_manager` MUST NOT infer or substitute `performer_id` from `user_id`
  - absence is an error unless `"system"`

- [x ] Tests:
  - start/end with missing `performer_id` (human-originated) → 400
  - start/end with `performer_id="system"` → accepted
  - recorded JSONL events reflect the exact `performer_id` value





### 4) Module test coverage (as listed in original plan)
- [x ] `apps/session_manager/tests/test_import_policy.py`
- [x ] `apps/session_manager/tests/test_session_jsonl_append.py`
  - [x ] verifies session_manager delegates event appends to `schema_recorder` (no direct JSONL writes)
  - [x ] allows session directory creation (`mkdir`) but forbids writing `*.jsonl`
- [x ] `apps/session_manager/tests/test_event_invariants.py`
  - invariants: `source/user_id/session_id/timestamp/record_id`
  - `performer_id` per canonical rule
- [x ] `apps/session_manager/tests/test_repository_append_event.py`
  - [x ] verifies session_manager repository does not write session JSONL directly (no `open()` / `Path.open()` on `*.jsonl`)
  - [x ] verifies the only allowed recording path is calling `schema_recorder` (service/repository boundary)
  - [x ] rejects direct file writes outside the allowed writer boundary

### 5) Domain error → HTTP mapping coverage

Slice-1 scope: these errors originate from `session_manager` service logic (not string parsing); HTTP mappings are **locked and testable**.
Rule: SessionUserMismatch is raised only if the session_id exists but belongs to a different user_id; if the session_id does not exist, raise SessionNotFound (do not merge these cases).

- [x ] Introduce and enforce **typed session errors** raised by the service layer (no string-based discrimination):
  - [x ] `SessionNotFound`
        Raised **only** when the `session_id` does not exist → **404 Not Found**
  - [x ] `SessionUserMismatch`
        Raised **only** when the `session_id` exists but belongs to a different `user_id` → **403 Forbidden**
  - [x ] `SessionAlreadyClosed`
        Raised when an end is attempted on an already-closed session → **409 Conflict**
  - [x ] `SessionAlreadyActive` (optional but recommended)
        Raised when `/sessions.start` is called while an active session already exists for the user → **409 Conflict**

Rule: SessionUserMismatch is raised only if the session_id exists but belongs to a different user_id; if the session_id does not exist, raise SessionNotFound (do not merge these cases).

- [ x] Routes map **typed exceptions explicitly** (no substring heuristics, no generic `ValueError` handling):
  - [x ] `/sessions.start`:
    - `SessionAlreadyActive` → 409
  - [x ] `/sessions.end`:
    - `SessionNotFound` → 404
    - `SessionUserMismatch` → 403
    - `SessionAlreadyClosed` → 409




---
## App-local config knobs — triage

### Do now (low effort, prevents drift)
- `config.py`
  - `MODULE_SOURCE = "session_manager"`
  - `SESSION_ID_PREFIX = "sess_"`


## C) Deferred (explicitly later / optional)

### App-local config knobs
### Defer (introduce when behavior exists)
- `DEFAULT_TIMEOUT_SECONDS`
- `get_timeout_seconds()`

### ID validation helper
- [ ] `idgen.py`
  - [x] `generate_session_id() -> str`
  - [ ] `is_valid_session_id(session_id: str) -> bool` (optional)

---------------------
## Domain-only invariants / rules (pure) — revised status

### Deferred

- `domain.py`
  - `assert_can_end_session(session: Session, user_id: str)`
  - `close_session(session: Session, end_time: datetime)`
  - Centralized domain errors

### Reason

- No real `Session` domain object yet (Slice-1 uses in-memory dicts).
- All lifecycle rules are already enforced in `service.py` and fully test-covered.
- Extracting now would add an abstraction that will change once persistence is introduced.

### Revisit when

- `Session` becomes a real domain entity (ORM/dataclass)
- lifecycle logic is reused outside `session_manager`
- persistence or background session handling is added

Deferral is intentional and creates no technical debt.

------------------

## Repository surface — revised status

### Deferred (recommended)

- `repository.py`
  - `create_active_session(session: Session)`
  - `get_active_session(session_id: str) -> Session | None`
  - `mark_session_closed(session_id: str, end_time: datetime)`
  - `append_event(...)`
  - `session_log_path(...)`

### Reason

- Slice-1 uses an **in-memory dict** (`_sessions`) and a **single writer** (`schema_recorder`) by design.
- Introducing a repository abstraction now would:
  - duplicate existing logic,
  - blur the service/recorder boundary you just locked with tests,
  - require refactoring once persistence is added.
- `append_event` and `session_log_path` already exist where they belong: **inside `schema_recorder`**, not session_manager.

### Revisit when

- sessions move to persistent storage (DB, KV store)
- closed sessions must be queryable
- multiple processes/services need shared access
- session lifecycle logic is no longer in-memory

Deferral is intentional; current architecture is correct for Slice-1.

------------------------



### Routes inventory (kept here as reference)
- [ x] `routes/sessions.py` (FastAPI adapter only)
  - [x ] POST `/session_manager/sessions.start` → `SessionManagerStartOutput` (calls `service.start_session`)
  - [x ] POST `/session_manager/sessions.end`   → `SessionManagerEndOutput`   (calls `service.end_session`)
  - [x ] map domain errors to HTTP:
    - [x ] `SessionNotFound` → 404
    - [ x] `SessionUserMismatch` → 403
    - [x ] `SessionAlreadyClosed` → 409

---

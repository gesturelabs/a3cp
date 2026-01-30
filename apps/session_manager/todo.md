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
- [ ] `"system"` performer_id accepted for boundaries
  - Start/end with `performer_id="system"`
  - Assert success and recorded value is `"system"`

#### 1.2 Session identity and continuity
- [ ] Enforce/test invariant:
  - the `session_id` emitted by `/sessions.end` MUST equal the `session_id` issued by `/sessions.start` for the same session
  - mismatched `session_id` → reject (400)

#### 1.3 Record identity authority & uniqueness
- [ ] Enforce/test invariant:
  - `/sessions.start` emits a **new server-generated** `record_id` (UUIDv4) for the start boundary event
  - `/sessions.end` emits a **new server-generated** `record_id` (UUIDv4) for the end boundary event
  - boundary-event `record_id` MUST be unique and MUST NOT be reused across start/end events
  - any client-supplied `record_id` in input is treated as a request/correlation field only and MUST NOT become the emitted boundary-event `record_id`

#### 1.4 Source & timestamp authority (clarified)
- [ ] Enforce/test invariant:
  - emitted boundary-event `source` is `"session_manager"` regardless of any input value
  - emitted boundary-event `timestamp` is generated by `session_manager` regardless of any input value
  - tests must assert emitted authority even when input contains `source` / `timestamp`
  - (optional) if `BaseSchema.extra="forbid"`, add validation tests asserting rejection at ingress

#### 1.5 Single active session per user
- [ ] Enforce/test invariant:
  - a user MAY NOT have more than one active session at the same time
  - `/sessions.start` while an active session exists for the same `user_id` → 409 Conflict
  - Slice-1 implementation must be explicit:
    - maintain `active_session_by_user_id`, OR
    - scan `_sessions` for an active session (acceptable for Slice 1; document choice)
  - tests:
    - start session for user → 200
    - start again for same user without ending → 409
    - start for different user → 200

- [ ] Enforce/test invariant (output validation & no-record-on-failure):
  - boundary events MUST be successfully constructed and validated as:
    - `SessionManagerStartOutput` for start
    - `SessionManagerEndOutput` for end
  - if boundary-event construction/validation fails, then:
    - no directory side effects beyond allowed mkdir (if any) for that request path
    - no JSONL append is attempted (or, equivalently, JSONL file remains unchanged)
    - no in-memory state mutation occurs

  - tests (choose at least one deterministic forcing strategy):
    - force an invalid output by injecting a clearly invalid field value (e.g., empty `session_id`, empty `user_id`, or invalid `source`) at construction time in a controlled test seam, and assert:
      - response is 500 (or 400 if you intentionally treat it as client fault)
      - JSONL did not change
      - in-memory state did not change


#### 1.6 Output validation & fail-fast behavior
- [ ] Enforce/test invariant:
  - session boundary outputs are Pydantic-validated (`SessionManagerStartOutput` / `SessionManagerEndOutput`)
  - invalid boundary-event payload MUST NOT be recorded to session JSONL (fail fast)

#### 1.7 Idempotency and terminal state
- [ ] Enforce/test invariant:
  - `/sessions.end`: repeated end for the same `session_id` → 409 Conflict

#### 1.8 System-initiated closure
- [ ] Enforce/test invariant:
  - sessions MAY be closed by the system with `performer_id="system"`
  - system-closed end event MUST:
    - preserve the original `session_id`
    - generate a new unique server `record_id`
    - use server-authoritative `timestamp`

- [ ] Enforce/test fail-fast ordering (no side effects on rejection):
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
- [ ] Enforce/test invariant (Slice 1 atomicity):
  - mutate in-memory session state only after a successful `schema_recorder` append
  - START:
    - if append fails, no active session is created (no `_sessions[...]` entry)
  - END:
    - if append fails, session remains active (status not flipped to closed)
  - tests must simulate recorder failure and assert no state change



### 2) performer_id policy enforced at route ingress (session_manager)

performer_id must be provided for all human-originated requests; only "system" is exempt. No inference, substitution, or fallback is permitted.

- [ ] Enforce/test ingress rules (before any state mutation or recording):
  - `/sessions.start`:
    - if `performer_id == "system"` → accept (system-generated boundary)
    - if `performer_id` is missing or empty → reject (400)
  - `/sessions.end`:
    - if `performer_id == "system"` → accept
    - if `performer_id` is missing or empty → reject (400)

- [ ] Explicitly forbid auto-filling:
  - `session_manager` MUST NOT infer or substitute `performer_id` from `user_id`
  - absence is an error unless `"system"`

- [ ] Tests:
  - start/end with missing `performer_id` (human-originated) → 400
  - start/end with `performer_id="system"` → accepted
  - recorded JSONL events reflect the exact `performer_id` value


### 3) Guardrail tests for performer_id policy (session_manager)
- [ ] start/end with human-originated payload and missing `performer_id` → 400
- [ ] start/end with `performer_id="system"` → accepted
- [ ] recorded JSONL events reflect correct `performer_id`

### 4) Module test coverage (as listed in original plan)
- [ ] `apps/session_manager/tests/test_import_policy.py`
- [ ] `apps/session_manager/tests/test_session_jsonl_append.py`
  - [ ] verifies session_manager delegates event appends to `schema_recorder` (no direct JSONL writes)
  - [ ] allows session directory creation (`mkdir`) but forbids writing `*.jsonl`
- [ ] `apps/session_manager/tests/test_event_invariants.py`
  - invariants: `source/user_id/session_id/timestamp/record_id`
  - `performer_id` per canonical rule
- [ ] `apps/session_manager/tests/test_repository_append_event.py`
  - [ ] verifies session_manager repository does not write session JSONL directly (no `open()` / `Path.open()` on `*.jsonl`)
  - [ ] verifies the only allowed recording path is calling `schema_recorder` (service/repository boundary)
  - [ ] rejects direct file writes outside the allowed writer boundary

### 5) Domain error → HTTP mapping coverage

Slice-1 scope: these errors originate from `session_manager` service logic (not string parsing); HTTP mappings are **locked and testable**.
Rule: SessionUserMismatch is raised only if the session_id exists but belongs to a different user_id; if the session_id does not exist, raise SessionNotFound (do not merge these cases).

- [ ] Introduce and enforce **typed session errors** raised by the service layer (no string-based discrimination):
  - [ ] `SessionNotFound`
        Raised **only** when the `session_id` does not exist → **404 Not Found**
  - [ ] `SessionUserMismatch`
        Raised **only** when the `session_id` exists but belongs to a different `user_id` → **403 Forbidden**
  - [ ] `SessionAlreadyClosed`
        Raised when an end is attempted on an already-closed session → **409 Conflict**
  - [ ] `SessionAlreadyActive` (optional but recommended)
        Raised when `/sessions.start` is called while an active session already exists for the user → **409 Conflict**

Rule: SessionUserMismatch is raised only if the session_id exists but belongs to a different user_id; if the session_id does not exist, raise SessionNotFound (do not merge these cases).

- [ ] Routes map **typed exceptions explicitly** (no substring heuristics, no generic `ValueError` handling):
  - [ ] `/sessions.start`:
    - `SessionAlreadyActive` → 409
  - [ ] `/sessions.end`:
    - `SessionNotFound` → 404
    - `SessionUserMismatch` → 403
    - `SessionAlreadyClosed` → 409

- [ ] Add route-level tests asserting **exact mappings**:
  - [ ] end non-existent `session_id` → 404
  - [ ] end existing `session_id` with wrong `user_id` → 403
  - [ ] repeated end on same `session_id` → 409
  - [ ] start while active session exists → 409


---

## C) Deferred (explicitly later / optional)

### App-local config knobs
- [ ] `config.py`
  - [ ] `MODULE_SOURCE = "session_manager"`
  - [ ] `SESSION_ID_PREFIX = "sess_"`
  - [ ] `DEFAULT_TIMEOUT_SECONDS` (later)
  - [ ] `get_timeout_seconds()` (later)

### ID validation helper
- [ ] `idgen.py`
  - [x] `generate_session_id() -> str`
  - [ ] `is_valid_session_id(session_id: str) -> bool` (optional)

### Domain-only invariants/rules (pure)
- [ ] `domain.py`
  - [ ] `assert_can_end_session(session: Session, user_id: str) -> None`
  - [ ] `close_session(session: Session, end_time: datetime) -> Session`
  - [ ] Domain errors: `SessionNotFound`, `SessionUserMismatch`, `SessionAlreadyClosed`

### Repository surface (if/where needed beyond current implementation)
- [ ] `repository.py`
  - [ ] `create_active_session(session: Session) -> None`
  - [ ] `get_active_session(session_id: str) -> Session | None`
    - NOTE: returns only active sessions; closed sessions are not retrievable via this helper (demo scope)
  - [ ] `mark_session_closed(session_id: str, end_time: datetime) -> Session`
  - [ ] `append_event(cfg: RecorderConfig, user_id: str, session_id: str, message: BaseSchema) -> None`
  - [ ] `session_log_path(user_id: str, session_id: str) -> Path` (optional)

### Service surface (if/where needed beyond current implementation)
- [ ] `service.py`
  - [ ] `start_session(payload: SessionManagerStartInput) -> SessionManagerStartOutput`
  - [ ] `end_session(payload: SessionManagerEndInput) -> SessionManagerEndOutput`

### Routes inventory (kept here as reference)
- [ ] `routes/sessions.py` (FastAPI adapter only)
  - [ ] POST `/session_manager/sessions.start` → `SessionManagerStartOutput` (calls `service.start_session`)
  - [ ] POST `/session_manager/sessions.end`   → `SessionManagerEndOutput`   (calls `service.end_session`)
  - [ ] map domain errors to HTTP:
    - [ ] `SessionNotFound` → 404
    - [ ] `SessionUserMismatch` → 403
    - [ ] `SessionAlreadyClosed` → 409

---

## D) Domain model (current)
- [x] `models.py` (domain data, no FastAPI/IO)
  - [x] `SessionStatus = {"active", "closed"}`
  - [x] `Session(session_id, user_id, start_time, end_time?, status, is_training_data, session_notes?, training_intent_label?, performer_id?)`

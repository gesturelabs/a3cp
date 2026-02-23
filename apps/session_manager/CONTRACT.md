# Session Manager Contract (A3CP MVP)

This document defines the **behavioral contract** for the Session Manager module, including HTTP route semantics, error mappings, and safety invariants. It is intended to stay aligned with:

- `apps/session_manager/service.py`
- `apps/session_manager/routes/router.py`
- `apps/session_manager/tests/`

---

## Scope

Routes (prefix: `/session_manager`):

- `POST /sessions.start`
- `POST /sessions.end`
- `POST /sessions.validate`

Storage model (current MVP): in-memory `_sessions` store (demo-only), with append-only recording via `schema_recorder.append_event()`.

---

## Core Concepts

### Session identity

- `session_id` is server-issued (via `generate_session_id()`).
- Session state is associated with `user_id`.
- Exactly one session may be **active** per `user_id` at a time (MVP policy).

### Status values

- `"active"`: session exists, belongs to `user_id`, and is active
- `"closed"`: session exists, belongs to `user_id`, but is closed
- `"invalid"`: session missing, malformed, or user mismatch (validate only)

---

## Route Contracts

### POST `/sessions.start`

#### Semantics

- Starts a session for `user_id`, or returns the existing active session for that `user_id` (**idempotent start**).
- Server is authoritative for:
  - `session_id`
  - `record_id`
  - `timestamp` (UTC, ms precision)

#### Required fields (MVP)

- `schema_version`
- `record_id` (client-provided; server outputs its own record_id)
- `user_id`
- `timestamp` (client-provided)
- `performer_id`:
  - Required unless `performer_id == "system"` for system-initiated boundaries.

#### Responses

- `200 OK` or `201 Created` (implementation-dependent) with `SessionManagerStartOutput`.
- **Must not** return 409 for “already active” in normal operation; start is idempotent at the service level.

> Note: The router currently includes an explicit mapping for `SessionAlreadyActive → 409` to satisfy typed-exception mapping policy, even though service behavior is now idempotent.

---

### POST `/sessions.end`

#### Semantics

- Ends the specific session identified by `session_id` for `user_id`.
- On success:
  - Session transitions to `"closed"`.
  - End event is appended via `append_event(...)`.

#### Required fields (MVP)

- `schema_version`
- `record_id`
- `user_id`
- `timestamp`
- `performer_id` (same rule as start)
- `session_id`
- `end_time`

#### Success response

- `200 OK` with `SessionManagerEndOutput`.

#### Error mapping (router contract)

- `404 Not Found` — `SessionNotFound`
- `403 Forbidden` — `SessionUserMismatch`
- `409 Conflict` — `SessionAlreadyClosed`
- `400 Bad Request` — `SessionError` (generic validation)

#### Wrong session_id safety invariant (critical)

If `sessions.end` is called with a `session_id` that:

- does not exist → **404**
- exists but belongs to a different `user_id` → **403**

Then:

- No session state is mutated.
- No other active session is closed.
- No side effects occur (beyond returning the error response).

This is enforced in `service.end_session()` by looking up only `_sessions[payload.session_id]` and mutating only that entry on success.

---

### POST `/sessions.validate`

#### Semantics

- Reconciliation-only status check used by other modules and the UI.
- Does not mutate session state.

#### Input

- `user_id`
- `session_id`

#### Output

- `{ "status": "active" | "closed" | "invalid" }`

#### Behavior

- Missing/blank `session_id` → `"invalid"`
- Unknown `session_id` → `"invalid"`
- `session_id` exists but `user_id` mismatch → `"invalid"`
- Existing session with status `"active"` → `"active"`
- Existing session with status `"closed"` → `"closed"`

---

## Recording & Preflight Invariants

### Append-only recording

- `sessions.start` and `sessions.end` append schema events via `append_event(...)`.
- `sessions.end` requires the parent session directory to exist; otherwise it raises `MissingSessionPath` and must not mutate state.

### No partial state commits on recorder failure

- If recorder append/preflight fails, the service must not commit session state mutations (e.g., must not leave a session active/closed incorrectly).

---

## Test Coverage Expectations

Minimum tests expected to exist and remain passing:

- Router maps typed exceptions explicitly (no heuristic mapping).
- Start: recorder failure → no active session committed.
- End: missing session dir → no state change (session remains active).
- End: wrong-session mismatch → raises `SessionUserMismatch` and does not close any active session.
- Validate: closed session returns `"closed"`; unknown returns `"invalid"`.

---

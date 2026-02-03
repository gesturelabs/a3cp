# App Structure and Routing Architecture (Canonical)

## Purpose
Define a single, enforceable app pattern for A3CP runtime modules that:
- keeps routes thin and replaceable,
- centralizes behavior,
- supports many contributors,
- enables future Dockerization and service extraction.

These rules are normative.

---

## Scope
Applies to:
- all runtime apps under `apps/`
- all FastAPI routing and router composition

Does not define:
- module behavior (`docs/modules/`)
- schemas/contracts (`schemas/`)
- execution order (`docs/todo/`)

---

## Canonical App Pattern

Every runtime app MUST follow:

apps/<app_name>/
- routes/
  - __init__.py
  - router.py
- service.py
- tests/

Optional (only when needed):
- repository.py   # IO / persistence
- idgen.py        # ID generation
- domain.py       # pure invariants
- models.py       # internal data objects
- config.py       # app-local config

---

## Layer Responsibilities

### Routes (apps/<app>/routes/router.py)
Transport adapters only (HTTP or WebSocket).

MUST:
- validate request/response schemas
- call service functions
- translate domain errors into transport responses:
  - HTTP status codes (for HTTP routes), or
  - control messages + close codes (for WebSocket routes)

Error boundary rules:
- Services raise domain/protocol errors only (transport-agnostic).
- Routes are the only layer allowed to map domain errors to:
  - HTTPException
  - WebSocket close codes
  - control message payloads

MUST NOT:
- contain business logic
- manage cross-request or persistent state
- perform IO (DB, files, logs)
- generate IDs
- depend on other apps

---

### Services (apps/<app>/service.py)
Own application behavior and protocol/domain logic.

MUST:
- implement use-cases and orchestration
- enforce app-level rules and invariants
- implement protocol/domain state machines where applicable
- accept explicit inputs (no hidden context)
- call repositories for IO

MUST NOT:
- raise HTTP/WS transport exceptions
- depend on FastAPI or transport layer details
- perform direct persistence


---

### Repositories (apps/<app>/repository.py, optional)
IO boundary only.

MUST:
- handle persistence and in-memory storage
- expose stable functions to services
- follow IO allowlists and writer boundaries

MUST NOT:
- contain business decisions
- raise HTTP/WS exceptions
- write session JSONL logs unless explicitly allowlisted
  (session JSONL writer is `apps/schema_recorder/repository.py` only)

---

### Domain / Models (domain.py, models.py, optional)
Pure logic and data.

MUST:
- have no FastAPI or IO dependencies

---

## Schemas
- All public schemas live in `schemas/`.
- Apps MUST import schemas only via: from schemas import ...
- Deep imports from schemas.* are forbidden.
- Schemas must not depend on apps.

---

## Routing Architecture
- All real routes (HTTP and WebSocket) live in apps: apps/<app>/routes/.
- `api/main.py` is the single composition point for:
  - HTTP routers
  - WebSocket routes
- `api/routes/` is legacy/transitional only.

Rules:
- New routes (HTTP or WebSocket) MUST NOT be added to `api/routes/`.
- Apps MUST NOT self-register or mutate global routing.
- Route composition is centralized and declarative in `api/main.py`.

---

## State Rules
- No implicit “current” state.
- Session, user, and context must always be explicit inputs.

In-memory state rules:
- Connection-local ephemeral state is allowed where required by transport
  (e.g., WebSocket protocol sequencing, counters, pending frame_meta).
- Such state MUST be bounded, per-connection, and fully cleaned up on close/abort.
- Cross-connection or long-lived “global” in-memory state is allowed only for demo paths
  and must be explicitly documented.


---

## Dockerization & Scaling
- Apps should be liftable into standalone services with minimal change.
- Apps SHOULD NOT import other apps directly.

Cross-app interaction rules:
- Cross-app calls must go through explicit service boundaries.
- Prefer dependency injection (ports/adapters pattern) over direct imports.
- If a direct import is required, it must target the public service surface
  and be documented in an explicit allowlist.
- Repositories must never be imported across apps.
---

## Testing
Each app MUST have apps/<app>/tests/ with:
- service-level tests (no transport required)
- thin route tests for the supported transport:
  - HTTP route tests (if HTTP endpoints exist)
  - WebSocket route tests (if WS endpoints exist)
- protocol/transition tests where the transport defines sequencing rules

---

## Migration Policy
- api/routes/ may exist temporarily but must not grow.
- New code MUST follow this architecture.
- Exceptions must be explicit and justified.

---

## Status
This document defines the target architecture and is intended to remain stable.

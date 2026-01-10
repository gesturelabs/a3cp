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
FastAPI adapters only.

MUST:
- validate request/response schemas
- call service functions
- translate domain errors to HTTP responses

MUST NOT:
- contain business logic
- manage state or context
- perform IO (DB, files, logs)
- generate IDs
- depend on other apps

---

### Services (apps/<app>/service.py)
Own application behavior.

MUST:
- implement use-cases and orchestration
- enforce app-level rules
- accept explicit inputs (no hidden context)
- call repositories for IO

MUST NOT:
- raise HTTP exceptions
- depend on FastAPI
- perform direct persistence

---

### Repositories (apps/<app>/repository.py, optional)
IO boundary only.

MUST:
- handle persistence, files, logs, in-memory storage
- expose stable functions to services

MUST NOT:
- contain business decisions
- raise HTTP exceptions

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
- All real routes live in apps: apps/<app>/routes/.
- api/main.py is the single router composition point.
- api/routes/ is legacy/transitional only.

Rules:
- New routes MUST NOT be added to api/routes/.
- Apps MUST NOT self-register or mutate global routing.

---

## State Rules
- No implicit “current” state.
- Session, user, and context must always be explicit inputs.
- In-memory state is allowed only for demo paths and must be documented.

---

## Dockerization & Scaling
- Apps should be liftable into standalone services with minimal change.
- Apps SHOULD NOT import other apps directly.
- Cross-app interaction must be explicit and documented.

---

## Testing
Each app MUST have apps/<app>/tests/ with:
- service-level tests (no HTTP required)
- thin route tests if routes exist

---

## Migration Policy
- api/routes/ may exist temporarily but must not grow.
- New code MUST follow this architecture.
- Exceptions must be explicit and justified.

---

## Status
This document defines the target architecture and is intended to remain stable.

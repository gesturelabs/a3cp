# A3CP App Pattern (Target)

Each runtime app lives under `apps/<app_name>/` and follows this structure:

apps/<app_name>/
- routes/
  - __init__.py
  - router.py              # canonical router entry (may import other route modules)
  - Purpose: FastAPI adapters only (request/response + error mapping)
- service.py               # REQUIRED
  - Purpose: application use-cases and orchestration (behavior lives here)
- repository.py            # OPTIONAL (only if app performs IO / persistence)
  - Purpose: persistence + IO boundary (DB, files, logs, in-memory state)
- idgen.py                 # OPTIONAL (only if app generates stable IDs/keys)
- models.py                # OPTIONAL (internal domain data structures; no FastAPI, no IO)
- domain.py                # OPTIONAL (domain rules and invariants; pure)
- config.py                # OPTIONAL (app-local configuration/constants)
- tests/                   # REQUIRED (at least app-level guardrails)

Rules:
- api/main.py registers app routers from apps/<app_name>/routes/router.py
- api/routes/ contains legacy shims only (no business logic); may be removed over time
- Routes contain no business logic or state
- Services implement behavior; repositories implement IO
- Schemas (schemas/) are the public contract and are never imported deeply
- Apps never expose or rely on a “current” global state

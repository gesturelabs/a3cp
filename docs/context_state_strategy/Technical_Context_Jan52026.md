# GestureLabs / A3CP — Technical Context State (Baseline)

## Repository & Structure
- Monorepo with stable layout: `api/`, `apps/`, `schemas/`, `docs/`, `scripts/`, `tests/`
- ~90 directories / ~350 files
- File tree documented (`FILE_TREE.txt`)

## Module Definition (design-complete)
- Full initial module set enumerated (~25+ modules)
- For each module:
  - Dedicated README (`docs/modules/<module>/README.md`)
  - Purpose, responsibilities, inputs, outputs defined
  - Invariants documented where applicable
- No module business logic implemented yet (intentional)

## Schema System (v1)
- Schema-first architecture established
- For each module:
  - Python schema definition
  - Generated JSON Schema
  - Input example JSON
  - Output example JSON
- Canonical `A3CPMessage` schema defined and versioned
- Shared base schema in place
- Schema generation + mapping scripts implemented
- Schema architecture, reference, and refactor docs present

## FastAPI Infrastructure
- Working FastAPI app (`api/main.py`)
- Route stubs registered for all modules
- Routes wired to schema validation
- Consistent API surface across modules

## Testing
- Pytest configured and passing for current stub state
- Shared test utilities and fixtures in place

## Implemented Domain Logic (exception)
- `session_manager` implemented beyond stub level:
  - Domain model, repository, service, routes
  - Session start/end schemas
  - ID generation
  - Unit and route tests

## UI / Website
- FastAPI-powered website (`apps/ui`)
- Jinja templates + component system
- Static assets integrated (CSS, images, diagrams)
- Public pages implemented (home, tech, docs, etc.)
- Deployed and live on Hetzner

## CI / CD
- GitHub Actions:
  - CI (tests)
  - Lint
  - Deploy
- Local → GitHub → Hetzner pipeline operational
- Deployment and management scripts present

## Deployment & Runtime
- Hetzner VPS provisioned
- HTTPS enabled
- FastAPI service running
- Dependency sets frozen and recorded

## Documentation
- Architecture diagrams and MVP doc
- Development, testing, deployment docs
- Module docs, schema docs, governance docs
- Changelog maintained

## Summary
- Infrastructure, schemas, routes, tests, CI/CD, deployment, and documentation complete
- One reference domain (`session_manager`) implemented
- All other modules fully specified, wired, and tested at interface level only
- No classifier, fusion, learning, or CARE logic implemented yet

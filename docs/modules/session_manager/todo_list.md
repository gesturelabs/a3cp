PHASE 0 — Bootstrap & Scaffolding
[ ] SM-APP-00: Create module scaffold
      apps/session_manager/__init__.py
      apps/session_manager/config.py
      apps/session_manager/idgen.py
      apps/session_manager/domain.py
      apps/session_manager/repository.py
      apps/session_manager/service.py
      apps/session_manager/routes/__init__.py
      apps/session_manager/routes/sessions.py
      apps/session_manager/tests/__init__.py
      apps/session_manager/tests/test_service.py
      apps/session_manager/tests/test_repository.py
      apps/session_manager/tests/test_routes.py
[ ] SM-API-00: Central wiring files (thin integration)
      api/routes/session_manager_routes.py
      ensure api/main.py includes the router

PHASE 1 — Schemas (single source of truth, central repo)
[ ] SM-SCH-01: Implement/confirm central schemas:
      schemas/session_manager_start/session_manager_start.py (StartRequest/Response)
      schemas/session_manager_end/session_manager_end.py (EndEvent with record_id)
      (optional MVP) schemas/session_manager_heartbeat.py (simple heartbeat)
[ ] SM-SCH-02: Regenerate JSON Schemas; update SCHEMA_CHANGELOG.md
[ ] SM-SCH-03: Ensure module routes import these central schemas only (no local copies)

PHASE 2 — Database Infrastructure
[ ] SM-DB-00: Shared infra
      db/__init__.py
      db/engine.py (async SQLAlchemy engine/sessionmaker wired to settings)
[ ] SM-DB-01: Alembic migration (name explicitly)
      alembic/versions/20250811_0001_sessions_core.py
      creates:
        a3cp.sessions (id, user_id, status, start_time, end_time, last_activity_time, policy_json, is_training_data)
        a3cp.session_events (id, session_id, record_id, event_type, timestamp, payload_jsonb, received_at)
        indexes: sessions(user_id, start_time DESC), session_events(session_id, timestamp, id)
[ ] SM-DB-02: Apply migration locally and in CI

PHASE 3 — Repository Layer (DB I/O only)
[ ] SM-APP-03: Define repository interfaces (async):
      create_session(), end_session(), get_active_by_user(), insert_event(), get_session()
[ ] SM-TST-03: Write repository tests against test Postgres (record_id uniqueness, ordering)
[ ] SM-APP-03i: Implement repository methods to satisfy tests

PHASE 4 — Service Layer (business rules)
[ ] SM-APP-04: Implement service logic:
      start (one ACTIVE per user, idempotency via record_id)
      end (idempotent)
      idle-timeout handling (simple T_idle; no pause/resume)
[ ] SM-CFG-01: config.py reads env with defaults (SESSION_T_IDLE_MS); expose Settings
[ ] SM-CFG-02: enforce one ACTIVE session per user in service (soft, no DB constraint)
[ ] SM-TST-01: Service tests — start/end idempotency; one-active-per-user; basic timeout
[ ] SM-APP-02: idgen.new_session_id() → "sess_<ulid|uuidv7>"

PHASE 5 — Routes (API surface)
[ ] SM-API-01: POST /session_manager/sessions.start → SessionStartResponse
[ ] SM-API-02: POST /session_manager/sessions.end → SessionEndEvent
[ ] SM-API-03: (optional MVP) POST /session_manager/sessions.heartbeat
[ ] SM-API-URL: Keep dot-style endpoints for continuity
[ ] SM-TST-04: API tests — happy path start/end; error on duplicate active session; schema conformance

PHASE 6 — Observability & Security (MVP-minimal)
[ ] SM-OBS-01: Log start/end with session_id and record_id (avoid PII)
[ ] SM-SEC-01: (optional) simple internal API key check for mutating endpoints

PHASE 7 — CI/CD
[ ] SM-CI-01: CI spins up Postgres, runs Alembic upgrade, then pytest for repo/service/routes
[ ] SM-CI-02: Include schema generation + fail on drift (optional for MVP)

PHASE 8 — Documentation
[ ] SM-DOC-01: apps/session_manager/README.md — purpose, lifecycle, endpoints, minimal examples

PHASE 9 — Migration/Cleanup
[ ] SM-MIG-01: Port any logic from apps/session_manager_start and _end into service/repository
[ ] SM-MIG-02: Deprecate/remove old start/end route files after parity tests pass
[ ] SM-MIG-03: Ensure api/routes only mounts the unified module router

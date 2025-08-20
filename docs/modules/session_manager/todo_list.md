PHASE 0 — Bootstrap & Scaffolding
[ ] SM-APP-00  apps/session_manager scaffold
[x] SM-API-00  central wiring files in api/

PHASE 1 — Schemas
[x] SM-SCH-01  central schemas: start + end
[ ] SM-SCH-Heartbeat (optional)
[ ] SM-SCH-02 regenerate JSON schemas + changelog
[x] SM-SCH-03 routes import only from schemas/

PHASE 2 — Database Infrastructure
[x] SM-DB-00  db/engine.py + init
[ ] SM-DB-01  Alembic migration (sessions, session_events)
[ ] SM-DB-02  apply migration locally + CI

PHASE 3 — Repository Layer
[ ] SM-APP-03  define repo interfaces (create, end, get_active, insert_event, get_session)
[ ] SM-TST-03  repo tests (idempotency, ordering)
[ ] SM-APP-03i implement repo methods

PHASE 4 — Service Layer
[ ] SM-APP-04  service logic (one active per user, idempotency, idle-timeout)
[ ] SM-CFG-01  config.py reads env (SESSION_T_IDLE_MS)
[ ] SM-CFG-02  enforce one-active rule in service
[ ] SM-TST-01  service tests
[ ] SM-APP-02  idgen.new_session_id()

PHASE 5 — Routes
[x] SM-API-01  POST sessions.start
[x] SM-API-02  POST sessions.end
[ ] SM-API-03  sessions.heartbeat (optional)
[~] SM-API-URL dot-style endpoints kept
[~] SM-TST-04  API tests partial; need error + schema asserts

PHASE 6 — Observability & Security
[ ] SM-OBS-01  log start/end (session_id, record_id, no PII)
[ ] SM-SEC-01  (optional) internal API key

PHASE 7 — CI/CD
[ ] SM-CI-01  CI: Postgres + Alembic + pytest
[ ] SM-CI-02  CI: schema drift check (optional)

PHASE 8 — Documentation
[ ] SM-DOC-01  apps/session_manager/README.md

PHASE 9 — Migration/Cleanup
[ ] SM-MIG-01  port old logic into service/repo
[ ] SM-MIG-02  remove legacy start/end route files
[ ] SM-MIG-03  ensure unified router only

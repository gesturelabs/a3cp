

## 4. Plan Postgres Schema & Migration Strategy (No Code Yet)
- Decide on database approach:
  - SQLAlchemy + Alembic
  - SQLModel + Alembic
  - Raw SQL migrations
- Clarify:
  - What data must persist for the A3CP demo vs. production
  - Whether migrations are needed immediately or can be deferred
- Define when and how schema creation will happen in deploy/CI.

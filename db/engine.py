# db/engine.py
from __future__ import annotations

import os
from typing import Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

_ENGINE: Optional[AsyncEngine] = None
_SESSIONMAKER: Optional[async_sessionmaker[AsyncSession]] = None


def make_engine(dsn: str, *, echo: bool = False) -> AsyncEngine:
    """Factory: create a new AsyncEngine."""
    return create_async_engine(dsn, echo=echo, pool_pre_ping=True)


def make_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Factory: create a new async sessionmaker bound to engine."""
    return async_sessionmaker(engine, expire_on_commit=False)


def get_engine() -> AsyncEngine:
    """
    Lazy singleton. Reads DSN from env:
      SESSION_DB_DSN = postgresql+asyncpg://user:pass@localhost:5432/a3cp
    Optional:
      SESSION_DB_ECHO = 1|true|yes|on  (default: off)
    """
    global _ENGINE, _SESSIONMAKER
    if _ENGINE is None:
        dsn = os.getenv("SESSION_DB_DSN")
        if not dsn:
            raise RuntimeError("SESSION_DB_DSN is not set")
        echo = os.getenv("SESSION_DB_ECHO", "0").lower() in {"1", "true", "yes", "on"}
        _ENGINE = make_engine(dsn, echo=echo)
        _SESSIONMAKER = make_sessionmaker(_ENGINE)
    return _ENGINE


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """Lazy singleton sessionmaker bound to the global engine."""
    if _SESSIONMAKER is None:
        # ensures engine + sessionmaker are initialized
        get_engine()
    assert _SESSIONMAKER is not None
    return _SESSIONMAKER

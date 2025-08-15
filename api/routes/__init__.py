# api/routes/__init__.py

import importlib
from typing import Iterable, List, Optional, Tuple

from fastapi import APIRouter

# Each entry: (primary_module, optional_fallback_pair)
# Start with session_manager only; extend this list module-by-module.
ROUTE_MODULES: List[Tuple[str, Optional[Tuple[str, str]]]] = [
    (
        "session_manager_routes",
        ("session_manager_start_routes", "session_manager_end_routes"),
    ),
    # ("audio_feed_worker_routes", None),
    # ("camera_feed_worker_routes", None),
    # ...add more as they are ready...
]


def _load_router(modname: str) -> APIRouter:
    mod = importlib.import_module(f".{modname}", package=__name__)
    r = getattr(mod, "router", None)
    if not isinstance(r, APIRouter):
        raise AttributeError(
            f"Module {modname} has no fastapi.APIRouter named 'router'"
        )
    return r


def _compose_fallback_router(
    a: str, b: str, prefix: str, tags: Iterable[str]
) -> APIRouter:
    ra = _load_router(a)
    rb = _load_router(b)
    r = APIRouter(prefix=prefix, tags=list(tags))
    r.include_router(ra)
    r.include_router(rb)
    return r


routers: List[APIRouter] = []

for primary, fallback in ROUTE_MODULES:
    try:
        # Prefer unified router module if present
        routers.append(_load_router(primary))
    except Exception:
        if fallback is None:
            raise
        # Compose unified router from legacy pair (keeps app booting during migration)
        prefix = "/session_manager" if primary.startswith("session_manager") else ""
        tags = ["session_manager"] if prefix else [primary.replace("_routes", "")]
        routers.append(_compose_fallback_router(fallback[0], fallback[1], prefix, tags))

__all__ = ["routers"]

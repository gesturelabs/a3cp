# apps/schema_recorder/__init__.py
# Public surface: callers should use schema_recorder.service.append_event()

from .service import append_event

__all__ = ["append_event"]

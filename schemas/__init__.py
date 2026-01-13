# schemas/__init__.py
"""
Public schema API surface.

Routes must import ONLY from this module, e.g.:
    from schemas import SessionManagerStartInput, SessionManagerStartOutput

The generator continues to import from internal module files
(e.g., schemas/session_manager_start/session_manager_start.py),
not from this public package.
"""
# Canonical runtime message used across modules (and by schema_recorder)
from .a3cp_message.a3cp_message import A3CPMessage

# Re-export BaseSchema first to avoid circular import issues
from .base.base import BaseSchema
from .session_manager_end.session_manager_end import (
    SessionEndInput as SessionManagerEndInput,
)
from .session_manager_end.session_manager_end import (
    SessionEndOutput as SessionManagerEndOutput,
)
from .session_manager_start.session_manager_start import (
    SessionStartInput as SessionManagerStartInput,
)
from .session_manager_start.session_manager_start import (
    SessionStartOutput as SessionManagerStartOutput,
)

__all__ = [
    "BaseSchema",
    # session_manager
    "SessionManagerStartInput",
    "SessionManagerStartOutput",
    "SessionManagerEndInput",
    "SessionManagerEndOutput",
    # canonical message
    "A3CPMessage",
]

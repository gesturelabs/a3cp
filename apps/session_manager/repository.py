# apps/session_manager/repository.py


from apps.schema_recorder import service as schema_recorder_service
from apps.session_manager.config import LOG_ROOT
from utils.paths import session_log_path


def append_session_event(*, user_id: str, session_id: str, message) -> None:
    """
    Session manager delegates event recording to schema_recorder.

    Responsibilities here:
    - resolve session log path
    - ensure session directory exists (session_manager authority)
    - call schema_recorder service
    """

    # Session manager is the directory-creation authority
    log_path = session_log_path(
        log_root=LOG_ROOT,
        user_id=user_id,
        session_id=session_id,
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Delegate append (no config objects, no env, no IO duplication)
    schema_recorder_service.append_event(
        log_path=log_path,
        event=message,
    )

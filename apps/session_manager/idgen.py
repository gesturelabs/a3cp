# apps/session_manager/idgen.py

import uuid


def generate_session_id() -> str:
    # Stable, explicit policy for session IDs
    return f"sess_{uuid.uuid4().hex[:16]}"

# apps/session_manager/models.py


from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional

SessionStatus = Literal["active", "closed"]


@dataclass
class SessionState:
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime]
    status: SessionStatus

    is_training_data: bool
    session_notes: Optional[str]
    performer_id: Optional[str]
    training_intent_label: Optional[str]

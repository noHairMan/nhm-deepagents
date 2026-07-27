"""Models used by Fragile sessions."""

from uuid import UUID

from pydantic import BaseModel


class SessionState(BaseModel):
    """Mutable state shared by interactive command handlers."""

    thread_id: UUID
    prompt_session: object

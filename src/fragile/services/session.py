"""Completed session output application service."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from fragile.models.history import SessionOutput
from fragile.repositories.session_output import SessionOutputRepository


class SessionService:
    """Coordinate persistence and replay of completed turns."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.repository = SessionOutputRepository(session_factory)

    async def save(
        self,
        thread_id: UUID,
        user_input: str,
        assistant_output: str,
        style_payload: str = "",
        thinking_output: str | None = None,
        trace_payload: str | None = None,
    ) -> None:
        await self.repository.save(
            thread_id, user_input, assistant_output, style_payload, thinking_output, trace_payload
        )

    async def list_for_thread(self, thread_id: UUID) -> list[SessionOutput]:
        return await self.repository.list_for_thread(thread_id)

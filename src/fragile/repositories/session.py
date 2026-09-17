"""Persistence operations spanning conversation session tables."""

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from fragile.models.history import ConversationHistory, SessionOutput


class SessionRepository:
    """Delete persisted conversation data in one short transaction."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def purge(self) -> int:
        """Delete all conversation titles and outputs, returning title count."""
        async with self.session_factory() as session:
            result = await session.execute(delete(ConversationHistory))
            await session.execute(delete(SessionOutput))
            await session.commit()
            return result.rowcount or 0

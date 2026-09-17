"""Conversation history application service."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from fragile.models.history import ConversationHistory
from fragile.repositories.conversation import ConversationRepository


class ConversationService:
    """Coordinate conversation title persistence and queries."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.repository = ConversationRepository(session_factory)

    async def register(self, thread_id: UUID, title: str) -> None:
        await self.repository.register(thread_id, title)

    async def list(self) -> list[ConversationHistory]:
        return await self.repository.list()

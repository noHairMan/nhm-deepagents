import uuid

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from fragile.services.conversation import ConversationService


class TestConversationService:
    @pytest.mark.asyncio
    async def test_register_and_list(self, session_factory: async_sessionmaker) -> None:
        service = ConversationService(session_factory)
        thread_id = uuid.uuid4()

        await service.register(thread_id, "Test Conversation")

        conversations = await service.list()
        assert len(conversations) == 1
        assert conversations[0].title == "Test Convers..."

        await service.register(thread_id, "Updated Title")
        conversations = await service.list()
        assert len(conversations) == 1
        assert conversations[0].title == "Test Convers..."

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from fragile.services.conversation import ConversationService


class TestConversationService:
    @pytest.mark.asyncio
    async def test_generate_title_returns_title(self, session_factory: async_sessionmaker) -> None:
        service = ConversationService(session_factory)
        mock_response = MagicMock()
        mock_response.content = "  Generated Title  "
        mock_model = AsyncMock()
        mock_model.ainvoke.return_value = mock_response

        with patch("tomorrow.core.model.get_model", return_value=mock_model):
            title = await service.generate_title("some user input")

        assert title == "Generated Title"
        mock_model.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_title_empty_response_returns_none(self, session_factory: async_sessionmaker) -> None:
        service = ConversationService(session_factory)
        mock_response = MagicMock()
        mock_response.content = "   "
        mock_model = AsyncMock()
        mock_model.ainvoke.return_value = mock_response

        with patch("tomorrow.core.model.get_model", return_value=mock_model):
            title = await service.generate_title("some user input")

        assert title is None

    @pytest.mark.asyncio
    async def test_generate_title_exception_returns_none(self, session_factory: async_sessionmaker) -> None:
        service = ConversationService(session_factory)

        with patch("tomorrow.core.model.get_model", side_effect=RuntimeError("model error")):
            title = await service.generate_title("some user input")

        assert title is None

    @pytest.mark.asyncio
    async def test_register_and_list(self, session_factory: async_sessionmaker) -> None:
        service = ConversationService(session_factory)
        thread_id = uuid.uuid4()

        await service.register(thread_id, "Test Conversation")

        conversations = await service.list()
        assert len(conversations) == 1
        assert conversations[0].title == "Test Conversation"

        await service.register(thread_id, "Updated Title")
        conversations = await service.list()
        assert len(conversations) == 1
        assert conversations[0].title == "Test Conversation"

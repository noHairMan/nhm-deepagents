"""Conversation history application service."""

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from fragile.models.history import ConversationHistory
from fragile.repositories.conversation import ConversationRepository

logger = logging.getLogger(__name__)


class ConversationService:
    """Coordinate conversation title persistence and queries."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.repository = ConversationRepository(session_factory)

    async def generate_title(self, user_input: str) -> str | None:
        """Use the LLM to generate a short title (≤20 characters) for a conversation.

        Returns the generated title on success, or ``None`` if the model call fails.
        """
        try:
            from langchain_core.messages import HumanMessage

            from tomorrow.core.model import get_model

            model = get_model()
            response = await model.ainvoke(
                [
                    HumanMessage(
                        content=(
                            "请将以下用户输入总结为一个简短的对话标题。"
                            "要求：20字以内，不要包含引号或句号，直接返回标题文本。"
                            f"\n\n用户输入：{user_input}"
                        )
                    )
                ]
            )
            title = response.content.strip()
            if title:
                return title
            return None
        except Exception as exc:
            logger.warning("标题生成失败，将回退到用户输入: %s", exc)
            return None

    async def register(self, thread_id: UUID, title: str) -> None:
        await self.repository.register(thread_id, title)

    async def list(self) -> list[ConversationHistory]:
        return await self.repository.list()

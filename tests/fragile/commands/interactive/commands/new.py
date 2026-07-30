from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest

from fragile.commands.interactive.commands.new import NewCommand
from fragile.models import SessionState
from fragile.models.constants import CommandResult


class TestNewCommand:
    @pytest.mark.asyncio
    async def test_new_command_registers_history(self) -> None:
        state = SessionState(thread_id=UUID(int=1), prompt_session=object())
        with patch(
            "fragile.commands.interactive.commands.new.ConversationHistory.register_conversation_async",
            new_callable=AsyncMock,
        ) as register:
            result = await NewCommand().handle("新对话", state)

        assert result is CommandResult.CONTINUE
        register.assert_awaited_once_with(state.thread_id, "新对话")

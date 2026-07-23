from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest

from fragile.commands.interactive.agent import chat


class TestAgent:
    @pytest.mark.asyncio
    async def test_chat_uses_checkpoint_and_outputs_stream(self) -> None:
        context = MagicMock()
        context.__aenter__ = AsyncMock(return_value="checkpoint")
        context.__aexit__ = AsyncMock(return_value=None)
        output = MagicMock()

        async def values(*args: object, **kwargs: object):
            yield "answer"

        with (
            patch("fragile.commands.interactive.agent.get_checkpointer_context", return_value=context),
            patch("fragile.commands.interactive.agent.AgentManager.create_agent", return_value=MagicMock()),
            patch("fragile.commands.interactive.agent.stream_events", return_value=values()),
        ):
            await chat("prompt", UUID(int=1), output)

        output.assert_any_call("answer")
        output.assert_called_with("\n")

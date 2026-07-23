from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest

from fragile.commands.interactive.agent import content_text, stream_events


class TestAgent:
    @staticmethod
    async def _async_values(value: str):
        yield value

    @pytest.mark.asyncio
    async def test_events_filters_and_yields_text_filters_and_yields_text(self) -> None:
        agent = MagicMock()

        async def stream(*args, **kwargs):
            yield "ignored"
            yield {"event": "other", "data": {}}
            yield {"event": "on_chat_model_stream", "data": {"chunk": MagicMock(content="")}}
            yield {"event": "on_chat_model_stream", "data": {"chunk": MagicMock(content="ok")}}
            yield {
                "event": "on_chat_model_stream",
                "data": {
                    "chunk": MagicMock(content=[{"type": "text", "text": "你好"}, {"type": "text", "text": "呀"}])
                },
            }

        agent.astream_events = stream

        assert [value async for value in stream_events(agent, "prompt", UUID(int=1))] == ["ok", "你好呀"]

    def testcontent_text_handles_supported_content(self) -> None:

        assert content_text("text") == "text"
        assert content_text(["a", {"type": "text", "text": "b"}, {"type": "image"}]) == "ab"
        assert content_text(None) == ""

    @pytest.mark.asyncio
    async def test_chat_uses_checkpoint_and_prints(self, capsys) -> None:
        context = MagicMock()
        context.__aenter__ = AsyncMock(return_value="checkpoint")
        context.__aexit__ = AsyncMock(return_value=None)
        output = MagicMock()
        with (
            patch("fragile.commands.interactive.agent.get_checkpointer_context", return_value=context),
            patch("fragile.commands.interactive.agent.AgentManager.create_agent", return_value=MagicMock()),
            patch("fragile.commands.interactive.agent.stream_events", return_value=self._async_values("answer")),
        ):
            from fragile.commands.interactive.agent import chat

            await chat("prompt", UUID(int=1), output)
        assert output.call_args_list == [(("answer",), {}), (("\n",), {})]

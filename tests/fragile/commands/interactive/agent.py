from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
from langgraph.graph.state import CompiledStateGraph

from fragile.commands.interactive.agent import (
    agent_runtime,
    chat,
    content_text,
    create_agent,
    load_agent_factory,
    stream_events,
)
from fragile.exceptions import AgentFactoryImportError, AgentFactoryTypeError, AgentGraphTypeError


class TestAgent:
    @staticmethod
    async def async_values(value: str):
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

    def test_create_agent_uses_configured_factory(self, monkeypatch):
        graph = MagicMock(spec=CompiledStateGraph)
        factory = MagicMock(return_value=graph)
        monkeypatch.setattr("fragile.commands.interactive.agent.fragile_settings.AGENT", "tests.factory")
        with patch("fragile.commands.interactive.agent.load_agent_factory", return_value=factory):
            assert create_agent("checkpoint") is graph
        factory.assert_called_once_with("checkpoint")

    def test_load_agent_factory_imports_callable(self):
        factory = load_agent_factory("tomorrow.core.agent.AgentManager.create_agent")

        assert callable(factory)

    def test_load_agent_factory_rejects_non_callable(self):
        with (
            patch("fragile.commands.interactive.agent.import_module", return_value=SimpleNamespace(value=object())),
            pytest.raises(AgentFactoryTypeError, match="is not callable"),
        ):
            load_agent_factory("module.value")

    def test_create_agent_rejects_invalid_factory(self):
        with (
            patch("fragile.commands.interactive.agent.fragile_settings.AGENT", "invalid"),
            pytest.raises(AgentFactoryImportError, match="Unable to load configured agent factory"),
        ):
            create_agent()

    def test_create_agent_rejects_non_callable_factory(self):
        with (
            patch(
                "fragile.commands.interactive.agent.load_agent_factory",
                side_effect=AgentFactoryTypeError("not callable"),
            ),
            pytest.raises(AgentFactoryTypeError, match="not callable"),
        ):
            create_agent()

    def test_create_agent_rejects_invalid_graph(self):
        with (
            patch("fragile.commands.interactive.agent.load_agent_factory", return_value=lambda _: object()),
            pytest.raises(AgentGraphTypeError, match="did not return a CompiledStateGraph"),
        ):
            create_agent()

    @pytest.mark.asyncio
    async def test_chat_uses_provided_agent_and_prints(self) -> None:
        agent = MagicMock(spec=CompiledStateGraph)
        with (
            patch("fragile.commands.interactive.agent.stream_events", return_value=self.async_values("answer")),
            patch("fragile.commands.interactive.agent.print_stream") as output,
            patch("fragile.commands.interactive.agent.SessionOutput.save_output", new_callable=AsyncMock),
        ):
            await chat(agent, "prompt", UUID(int=1))
        assert output.call_args_list == [(("answer",), {}), (("\n",), {})]

    @pytest.mark.asyncio
    async def test_agent_runtime_initializes_and_releases_once(self) -> None:
        context = MagicMock()
        context.__aenter__ = AsyncMock(return_value="checkpoint")
        context.__aexit__ = AsyncMock(return_value=None)
        agent = MagicMock(spec=CompiledStateGraph)
        with (
            patch("fragile.commands.interactive.agent.get_checkpointer_context", return_value=context) as get_context,
            patch(
                "fragile.commands.interactive.agent.restore_account_configuration", new_callable=AsyncMock
            ) as restore,
            patch("fragile.commands.interactive.agent.create_agent", return_value=agent) as create,
        ):
            async with agent_runtime() as actual:
                assert actual == (agent, "checkpoint")
        get_context.assert_called_once_with()
        restore.assert_awaited_once_with()
        create.assert_called_once_with("checkpoint")
        context.__aenter__.assert_awaited_once_with()
        context.__aexit__.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_agent_runtime_releases_context_when_creation_fails(self) -> None:
        context = MagicMock()
        context.__aenter__ = AsyncMock(return_value="checkpoint")
        context.__aexit__ = AsyncMock(return_value=None)
        with (
            patch("fragile.commands.interactive.agent.get_checkpointer_context", return_value=context),
            patch("fragile.commands.interactive.agent.restore_account_configuration", new_callable=AsyncMock),
            patch(
                "fragile.commands.interactive.agent.create_agent",
                side_effect=RuntimeError("creation failed"),
            ),
            pytest.raises(RuntimeError, match="creation failed"),
        ):
            async with agent_runtime():
                pass
        context.__aexit__.assert_awaited_once()

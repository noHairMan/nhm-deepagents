from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
from langgraph.graph.state import CompiledStateGraph

from fragile.commands.interactive.agent import (
    StreamSegment,
    agent_runtime,
    chat,
    content_segments,
    content_text,
    create_agent,
    load_agent_factory,
    stream_events,
)
from fragile.commands.interactive.trace import TraceEvent, trace_from_json
from fragile.exceptions import AgentFactoryImportError, AgentFactoryTypeError, AgentGraphTypeError, AgentResponseError


class TestAgent:
    @staticmethod
    async def async_values(value: StreamSegment):
        yield value

    @pytest.mark.asyncio
    async def test_events_filters_and_yields_typed_segments(self) -> None:
        agent = MagicMock()

        async def stream(*args, **kwargs):
            yield "ignored"
            yield {"event": "other", "data": {}}
            yield {"event": "on_chat_model_stream", "data": None}
            yield {"event": "on_chat_model_stream", "data": {"chunk": MagicMock(content="")}}
            yield {"event": "on_chat_model_stream", "data": {"chunk": MagicMock(content="ok")}}
            yield {
                "event": "on_chat_model_stream",
                "data": {
                    "chunk": MagicMock(
                        content=[
                            {"type": "reasoning", "reasoning": "先想"},
                            {"type": "text", "text": "你好"},
                            {"type": "thinking", "thinking": "再想"},
                            {"type": "text", "text": "呀"},
                            {"type": "image", "data": "ignored"},
                        ]
                    )
                },
            }

        agent.astream_events = stream

        assert [value async for value in stream_events(agent, "prompt", UUID(int=1))] == [
            TraceEvent(0, "text", content="ok"),
            TraceEvent(1, "thinking", content="先想"),
            TraceEvent(2, "text", content="你好"),
            TraceEvent(3, "thinking", content="再想"),
            TraceEvent(4, "text", content="呀"),
        ]

    @pytest.mark.asyncio
    async def test_events_normalize_tool_and_stage_lifecycle(self) -> None:
        agent = MagicMock()

        async def stream(*args, **kwargs):
            yield {"event": "on_chain_start", "name": "agent", "data": {"input": {}}}
            yield {"event": "on_tool_start", "name": "read_file", "data": {"input": {"path": "README.md"}}}
            yield {"event": "on_tool_end", "name": "read_file", "data": {"output": "contents"}}
            yield {"event": "on_chain_end", "name": "agent", "data": {"output": {}}}

        agent.astream_events = stream

        actual = [
            (event.sequence, event.kind, event.status) async for event in stream_events(agent, "prompt", UUID(int=1))
        ]

        assert actual == [
            (0, "stage", "running"),
            (1, "tool_start", "running"),
            (2, "tool_end", "completed"),
            (3, "stage", "completed"),
        ]

    @pytest.mark.asyncio
    async def test_stream_events_wraps_invalid_stream_response(self) -> None:
        agent = MagicMock()

        async def stream(*args, **kwargs):
            raise ValueError("No generations found in stream.")
            yield

        agent.astream_events = stream

        with pytest.raises(AgentResponseError, match="No generations found in stream."):
            _ = [value async for value in stream_events(agent, "prompt", UUID(int=1))]

    def testcontent_text_handles_supported_content(self) -> None:

        assert content_text("text") == "text"
        assert content_text(["a", {"type": "text", "text": "b"}, {"text": "c"}, {"type": "image"}]) == "abc"
        assert content_text(None) == ""

    def test_content_segments_ignores_empty_and_malformed_blocks(self) -> None:
        assert content_segments(
            [
                "",
                {"type": "reasoning", "reasoning": ""},
                {"type": "thinking", "thinking": 1},
                {"type": "reasoning", "reasoning": "思考"},
                {"reasoning": "兼容"},
                {"thinking": "形态"},
                {"type": "text", "text": "正文"},
                {"type": "text", "text": None},
                1,
            ]
        ) == [
            StreamSegment("thinking", "思考"),
            StreamSegment("thinking", "兼容"),
            StreamSegment("thinking", "形态"),
            StreamSegment("text", "正文"),
        ]

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
            patch(
                "fragile.commands.interactive.agent.stream_events",
                return_value=self.async_values(TraceEvent(0, "text", content="answer")),
            ),
            patch("fragile.commands.interactive.display.print_stream") as output,
            patch("fragile.commands.interactive.agent.SessionOutput.save_output", new_callable=AsyncMock),
        ):
            await chat(agent, "prompt", UUID(int=1))
        assert output.call_args_list == [(("answer",), {}), (("\n",), {})]

    @pytest.mark.asyncio
    async def test_chat_prints_thinking_separately_and_accumulates_it(self) -> None:
        agent = MagicMock(spec=CompiledStateGraph)

        async def segments():
            yield TraceEvent(0, "thinking", content="先想")
            yield TraceEvent(1, "text", content="答案")

        save_output = AsyncMock()
        with (
            patch("fragile.commands.interactive.agent.stream_events", return_value=segments()),
            patch("fragile.commands.interactive.display.print_thinking") as thinking,
            patch("fragile.commands.interactive.display.print_stream"),
            patch("fragile.commands.interactive.agent.SessionOutput.save_output", save_output),
        ):
            await chat(agent, "prompt", UUID(int=1))
        thinking.assert_called_once_with("先想")
        save_output.assert_awaited_once()
        saved_args = save_output.await_args.args
        saved_kwargs = save_output.await_args.kwargs
        assert saved_args == (UUID(int=1), "prompt", "答案", "答案")
        assert saved_kwargs["thinking_output"] == "先想"
        assert trace_from_json(saved_kwargs["trace_payload"]) == [
            TraceEvent(0, "thinking", content="先想"),
            TraceEvent(1, "text", content="答案"),
        ]

    @pytest.mark.asyncio
    async def test_chat_renders_non_text_events_without_adding_them_to_answer(self) -> None:
        agent = MagicMock(spec=CompiledStateGraph)

        async def events():
            yield TraceEvent(0, "tool_start", name="read_file", input={"path": "README.md"}, status="running")
            yield TraceEvent(1, "text", content="answer")

        save_output = AsyncMock()
        with (
            patch("fragile.commands.interactive.agent.stream_events", return_value=events()),
            patch("fragile.commands.interactive.agent.SessionOutput.save_output", save_output),
        ):
            await chat(agent, "prompt", UUID(int=1))

        assert save_output.await_args.args[2] == "answer"
        assert trace_from_json(save_output.await_args.kwargs["trace_payload"]) == [
            TraceEvent(0, "tool_start", name="read_file", input={"path": "README.md"}, status="running"),
            TraceEvent(1, "text", content="answer"),
        ]

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

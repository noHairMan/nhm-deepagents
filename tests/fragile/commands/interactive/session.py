from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import asyncclick as click
import httpx
import pytest
from langchain_anthropic.chat_models import AnthropicInvalidRequestError
from sqlalchemy import create_engine

from fragile.commands.interactive.commands import CommandRegistry, command_registry
from fragile.commands.interactive.commands.base import extract_prompt
from fragile.commands.interactive.commands.quit import QuitCommand
from fragile.commands.interactive.session import InteractiveSession, interactive
from fragile.exceptions import AgentResponseError, FragileError, InvalidThreadIdError
from fragile.models import Base, SessionState
from fragile.models.constants import CommandResult
from fragile.utils.uid import resolve_thread_id


class TestSession:
    @pytest.fixture(autouse=True)
    def database(self, tmp_path, monkeypatch) -> None:
        engine = create_engine(f"sqlite:///{tmp_path / 'history.db'}")
        Base.metadata.create_all(engine)
        monkeypatch.setattr("fragile.commands.interactive.commands.history.engine", engine)
        runtime = MagicMock()
        runtime.__aenter__ = AsyncMock(return_value=(MagicMock(), MagicMock()))
        runtime.__aexit__ = AsyncMock(return_value=None)
        monkeypatch.setattr("fragile.commands.interactive.session.agent_runtime", MagicMock(return_value=runtime))

    def test_command_registry_rejects_non_command_registration(self) -> None:
        with pytest.raises(TypeError, match="command must be a Command instance"):
            CommandRegistry().register(object())

    def test_interactive_session_initializes_thread_state(self) -> None:
        thread_id = UUID(int=1)
        with patch("fragile.commands.interactive.session.create_prompt_session") as create_session:
            session = InteractiveSession(str(thread_id))

        assert session.thread_id == thread_id
        assert session.state.thread_id == thread_id
        assert session.is_running
        create_session.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_interactive_session_stops_on_exit_result(self) -> None:
        with patch("fragile.commands.interactive.session.create_prompt_session"):
            session = InteractiveSession(None)

        await session.handle_result(MagicMock(), MagicMock(), CommandResult.EXIT, "/quit")

        assert not session.is_running

    @pytest.mark.asyncio
    async def test_model_change_restores_selection_before_recreating_agent(self) -> None:
        replacement_agent = MagicMock()
        events: list[str] = []
        with (
            patch("fragile.commands.interactive.session.create_prompt_session"),
            patch(
                "fragile.commands.interactive.session.restore_account_configuration",
                new_callable=AsyncMock,
                side_effect=lambda: events.append("restore"),
            ),
            patch(
                "fragile.commands.interactive.session.create_agent",
                side_effect=lambda _checkpointer: events.append("create") or replacement_agent,
            ),
        ):
            session = InteractiveSession(None)
            agent = await session.handle_result(MagicMock(), MagicMock(), CommandResult.MODEL_CHANGED, "/model")

        assert agent is replacement_agent
        assert events == ["restore", "create"]

    @pytest.mark.asyncio
    async def test_chat_connection_error_is_logged_and_shown_without_stopping_session(self, capsys) -> None:
        with (
            patch("fragile.commands.interactive.session.create_prompt_session"),
            patch(
                "fragile.commands.interactive.session.ConversationHistory.register_conversation",
                new_callable=AsyncMock,
            ),
            patch(
                "fragile.commands.interactive.session.chat",
                new_callable=AsyncMock,
                side_effect=httpx.ConnectError("connection failed"),
            ),
            patch("fragile.commands.interactive.session.logger.exception") as log_exception,
            patch(
                "fragile.commands.interactive.session.tomorrow_settings.MODEL",
                {
                    "type": "ollama",
                    "ollama": {"model": "qwen3.5:9b", "base_url": "http://localhost:11434"},
                },
            ),
        ):
            session = InteractiveSession(None)
            await session.handle_result(MagicMock(), MagicMock(), CommandResult.NOT_HANDLED, "hello")

        log_exception.assert_called_once_with(
            "模型服务连接失败 provider=%s model=%s base_url=%s",
            "ollama",
            "qwen3.5:9b",
            "http://localhost:11434",
        )
        assert "模型服务连接失败" in capsys.readouterr().out
        assert session.is_running

    @pytest.mark.asyncio
    async def test_chat_connection_error_handles_missing_model_configuration(self, capsys) -> None:
        with (
            patch("fragile.commands.interactive.session.create_prompt_session"),
            patch(
                "fragile.commands.interactive.session.ConversationHistory.register_conversation",
                new_callable=AsyncMock,
            ),
            patch(
                "fragile.commands.interactive.session.chat",
                new_callable=AsyncMock,
                side_effect=httpx.ConnectError("connection failed"),
            ),
            patch("fragile.commands.interactive.session.logger.exception") as log_exception,
            patch("fragile.commands.interactive.session.tomorrow_settings.MODEL", {"type": "ollama", "ollama": None}),
        ):
            session = InteractiveSession(None)
            await session.handle_result(MagicMock(), MagicMock(), CommandResult.NOT_HANDLED, "hello")

        assert "模型服务连接失败" in capsys.readouterr().out
        log_exception.assert_called_once_with(
            "模型服务连接失败 provider=%s model=%s base_url=%s",
            "ollama",
            "unknown",
            "未配置",
        )
        assert session.is_running

    @pytest.mark.asyncio
    async def test_anthropic_invalid_request_is_logged_and_shown_without_stopping_session(self, capsys) -> None:
        error = AnthropicInvalidRequestError(
            "tools[0].type is invalid",
            response=httpx.Response(400, request=httpx.Request("POST", "https://proxy.example")),
            body={"error": {"type": "invalid_request_error"}},
        )
        with (
            patch("fragile.commands.interactive.session.create_prompt_session"),
            patch(
                "fragile.commands.interactive.session.ConversationHistory.register_conversation",
                new_callable=AsyncMock,
            ),
            patch(
                "fragile.commands.interactive.session.chat",
                new_callable=AsyncMock,
                side_effect=error,
            ),
            patch("fragile.commands.interactive.session.logger.exception") as log_exception,
            patch(
                "fragile.commands.interactive.session.tomorrow_settings.MODEL",
                {
                    "type": "anthropic",
                    "anthropic": {"model": "claude-sonnet-5", "base_url": "https://proxy.example"},
                },
            ),
        ):
            session = InteractiveSession(None)
            await session.handle_result(MagicMock(), MagicMock(), CommandResult.NOT_HANDLED, "hello")

        log_exception.assert_called_once_with(
            "模型请求失败 provider=%s model=%s base_url=%s error=%s",
            "anthropic",
            "claude-sonnet-5",
            "https://proxy.example",
            error,
        )
        output = capsys.readouterr().out
        assert "模型请求失败" in output
        assert "tools[0].type is invalid" in output
        assert session.is_running

    @pytest.mark.asyncio
    async def test_anthropic_invalid_request_handles_missing_model_configuration(self, capsys) -> None:
        error = AnthropicInvalidRequestError(
            "tools[0].type is invalid",
            response=httpx.Response(400, request=httpx.Request("POST", "https://proxy.example")),
            body={"error": {"type": "invalid_request_error"}},
        )
        with (
            patch("fragile.commands.interactive.session.create_prompt_session"),
            patch(
                "fragile.commands.interactive.session.ConversationHistory.register_conversation",
                new_callable=AsyncMock,
            ),
            patch(
                "fragile.commands.interactive.session.chat",
                new_callable=AsyncMock,
                side_effect=error,
            ),
            patch("fragile.commands.interactive.session.logger.exception") as log_exception,
            patch("fragile.commands.interactive.session.tomorrow_settings.MODEL", {"type": "anthropic"}),
        ):
            session = InteractiveSession(None)
            await session.handle_result(MagicMock(), MagicMock(), CommandResult.NOT_HANDLED, "hello")

        output = capsys.readouterr().out
        assert "模型请求失败" in output
        assert "tools[0].type is invalid" in output
        log_exception.assert_called_once_with(
            "模型请求失败 provider=%s model=%s base_url=%s error=%s",
            "anthropic",
            "unknown",
            "未配置",
            error,
        )
        assert session.is_running

    @pytest.mark.asyncio
    async def test_chat_empty_generation_stream_is_logged_and_shown_without_stopping_session(self, capsys) -> None:
        error = AgentResponseError("No generations found in stream.")
        with (
            patch("fragile.commands.interactive.session.create_prompt_session"),
            patch(
                "fragile.commands.interactive.session.ConversationHistory.register_conversation",
                new_callable=AsyncMock,
            ),
            patch(
                "fragile.commands.interactive.session.chat",
                new_callable=AsyncMock,
                side_effect=error,
            ),
            patch("fragile.commands.interactive.session.logger.exception") as log_exception,
            patch(
                "fragile.commands.interactive.session.tomorrow_settings.MODEL",
                {
                    "type": "anthropic",
                    "anthropic": {"model": "claude-sonnet-5", "base_url": "https://proxy.example"},
                },
            ),
        ):
            session = InteractiveSession(None)
            await session.handle_result(MagicMock(), MagicMock(), CommandResult.NOT_HANDLED, "hello")

        log_exception.assert_called_once_with(
            "模型请求失败 provider=%s model=%s base_url=%s error=%s",
            "anthropic",
            "claude-sonnet-5",
            "https://proxy.example",
            error,
        )
        output = capsys.readouterr().out
        assert "模型请求失败" in output
        assert "No generations found in stream." in output
        assert session.is_running

    @pytest.mark.asyncio
    async def test_command_registry_handles_registered_commands(self) -> None:
        state = SessionState(thread_id=UUID(int=1))

        assert await command_registry.handle("/quit", state) is CommandResult.EXIT
        assert await command_registry.handle("/new", state) is CommandResult.CONTINUE
        assert await command_registry.handle("ordinary prompt", state) is CommandResult.NOT_HANDLED

    @pytest.mark.asyncio
    async def test_new_command_does_not_create_history_before_chat(self) -> None:
        with patch("fragile.commands.interactive.commands.new.show_startup"):
            state = SessionState(thread_id=UUID(int=1))
            assert await command_registry.handle("/new", state) is CommandResult.CONTINUE

    @pytest.mark.asyncio
    async def test_command_registry_handles_only_the_indexed_handler(self) -> None:
        state = SessionState(thread_id=UUID(int=1))
        with patch.dict(command_registry._handlers, {"quit": QuitCommand()}, clear=True):
            assert await command_registry.handle("  /QUIT  ", state) is CommandResult.EXIT

    @pytest.mark.asyncio
    async def test_command_registry_does_not_call_handlers_for_unknown_command(self) -> None:
        state = SessionState(thread_id=UUID(int=1))
        handler = patch("fragile.commands.interactive.commands.quit.QuitCommand.handle")
        with handler as mocked_handler:
            assert await command_registry.handle("/unknown", state) is CommandResult.NOT_HANDLED
        mocked_handler.assert_not_called()

    def test_extract_command_ignores_case_and_whitespace(self) -> None:
        assert extract_prompt("  /QUIT  ").model_dump() == {"command": "quit", "prompt": None}
        assert extract_prompt("  /NEW  你好呀").model_dump() == {"command": "new", "prompt": "你好呀"}
        assert extract_prompt("  /HISTORY  ").model_dump() == {"command": "history", "prompt": None}
        assert extract_prompt("你好呀").model_dump() == {"command": None, "prompt": "你好呀"}

    @pytest.mark.asyncio
    async def test_interactive_handles_commands_and_chat(self) -> None:
        prompt_session = MagicMock()
        prompt_session.prompt_async = AsyncMock(side_effect=["  hello  ", "   ", "/new", "/quit"])
        state = MagicMock()
        with (
            patch("fragile.commands.interactive.session.enter_fullscreen"),
            patch("fragile.commands.interactive.session.leave_fullscreen") as leave_fullscreen,
            patch("fragile.commands.interactive.session.show_startup"),
            patch("fragile.commands.interactive.session.create_prompt_session", return_value=prompt_session),
            patch("fragile.commands.interactive.session.SessionState", return_value=state),
            patch.object(
                command_registry,
                "handle",
                new_callable=AsyncMock,
                side_effect=[
                    CommandResult.NOT_HANDLED,
                    CommandResult.NOT_HANDLED,
                    CommandResult.CONTINUE,
                    CommandResult.EXIT,
                ],
            ),
            patch(
                "fragile.commands.interactive.session.ConversationHistory.register_conversation",
                new_callable=AsyncMock,
            ) as register,
            patch("fragile.commands.interactive.session.chat", new_callable=AsyncMock) as chat,
            patch(
                "fragile.commands.interactive.session.agent_runtime",
                return_value=MagicMock(
                    __aenter__=AsyncMock(return_value=(MagicMock(), MagicMock())), __aexit__=AsyncMock()
                ),
            ),
        ):
            await interactive(None)

        register.assert_awaited_once_with(state.thread_id, "hello")
        chat.assert_awaited_once_with(chat.call_args.args[0], "hello", state.thread_id)
        leave_fullscreen.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_interactive_reuses_agent_and_switches_thread_on_new(self) -> None:
        prompt_session = MagicMock()
        prompt_session.prompt_async = AsyncMock(side_effect=["hello", "/new", "world", "/quit"])
        agent = MagicMock()
        runtime = MagicMock()
        runtime.__aenter__ = AsyncMock(return_value=(agent, MagicMock()))
        runtime.__aexit__ = AsyncMock(return_value=None)
        with (
            patch("fragile.commands.interactive.session.enter_fullscreen"),
            patch("fragile.commands.interactive.session.leave_fullscreen"),
            patch("fragile.commands.interactive.session.show_startup"),
            patch("fragile.commands.interactive.session.create_prompt_session", return_value=prompt_session),
            patch("fragile.commands.interactive.session.agent_runtime", return_value=runtime),
            patch(
                "fragile.commands.interactive.session.ConversationHistory.register_conversation",
                new_callable=AsyncMock,
            ),
            patch("fragile.commands.interactive.session.chat", new_callable=AsyncMock) as chat,
            patch("fragile.commands.interactive.commands.new.show_startup"),
        ):
            await InteractiveSession(str(UUID(int=1))).run()

        assert chat.await_count == 2
        assert chat.call_args_list[0].args[0] is agent
        assert chat.call_args_list[1].args[0] is agent
        assert chat.call_args_list[0].args[2] != chat.call_args_list[1].args[2]
        runtime.__aenter__.assert_awaited_once_with()
        runtime.__aexit__.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_interactive_recreates_agent_only_after_model_change(self) -> None:
        prompt_session = MagicMock()
        prompt_session.prompt_async = AsyncMock(side_effect=["hello", "/model", "world", "/quit"])
        initial_agent = MagicMock()
        replacement_agent = MagicMock()
        checkpointer = MagicMock()
        runtime = MagicMock()
        runtime.__aenter__ = AsyncMock(return_value=(initial_agent, checkpointer))
        runtime.__aexit__ = AsyncMock(return_value=None)
        with (
            patch("fragile.commands.interactive.session.enter_fullscreen"),
            patch("fragile.commands.interactive.session.leave_fullscreen"),
            patch("fragile.commands.interactive.session.show_startup"),
            patch("fragile.commands.interactive.session.create_prompt_session", return_value=prompt_session),
            patch("fragile.commands.interactive.session.agent_runtime", return_value=runtime),
            patch(
                "fragile.commands.interactive.session.restore_account_configuration",
                new_callable=AsyncMock,
            ),
            patch.object(
                command_registry,
                "handle",
                new_callable=AsyncMock,
                side_effect=[
                    CommandResult.NOT_HANDLED,
                    CommandResult.MODEL_CHANGED,
                    CommandResult.NOT_HANDLED,
                    CommandResult.EXIT,
                ],
            ),
            patch(
                "fragile.commands.interactive.session.ConversationHistory.register_conversation",
                new_callable=AsyncMock,
            ),
            patch("fragile.commands.interactive.session.chat", new_callable=AsyncMock) as chat,
            patch("fragile.commands.interactive.session.create_agent", return_value=replacement_agent) as create,
        ):
            await InteractiveSession(str(UUID(int=1))).run()

        create.assert_called_once_with(checkpointer)
        assert chat.call_args_list[0].args[0] is initial_agent
        assert chat.call_args_list[1].args[0] is replacement_agent
        assert chat.call_args_list[0].args[2] == chat.call_args_list[1].args[2] == UUID(int=1)

    @pytest.mark.asyncio
    async def test_interactive_retries_after_keyboard_interrupt_and_eof(self) -> None:
        prompt_session = MagicMock()
        prompt_session.prompt_async = AsyncMock(side_effect=[KeyboardInterrupt, EOFError, "/quit"])
        with (
            patch("fragile.commands.interactive.session.enter_fullscreen"),
            patch("fragile.commands.interactive.session.leave_fullscreen"),
            patch("fragile.commands.interactive.session.show_startup"),
            patch("fragile.commands.interactive.session.create_prompt_session", return_value=prompt_session),
        ):
            await interactive(None)

    @pytest.mark.asyncio
    async def test_interactive_exits_after_two_keyboard_interrupts(self) -> None:
        prompt_session = MagicMock()
        prompt_session.prompt_async = AsyncMock(side_effect=[KeyboardInterrupt, KeyboardInterrupt])
        with (
            patch("fragile.commands.interactive.session.enter_fullscreen"),
            patch("fragile.commands.interactive.session.leave_fullscreen"),
            patch("fragile.commands.interactive.session.show_startup"),
            patch("fragile.commands.interactive.session.create_prompt_session", return_value=prompt_session),
            patch("fragile.commands.interactive.session.time.monotonic", side_effect=[1.0, 1.1]),
        ):
            await interactive(None)

    def test_resolve_thread_id_rejects_invalid_value(self) -> None:

        with pytest.raises(InvalidThreadIdError, match="Must be a valid UUID"):
            resolve_thread_id("bad")

    def test_invalid_resolve_thread_id_is_fragile_error(self) -> None:
        assert issubclass(InvalidThreadIdError, FragileError)
        assert issubclass(InvalidThreadIdError, click.BadParameter)

    def test_resolve_thread_id(self) -> None:

        value = UUID("12345678-1234-5678-1234-567812345678")
        assert resolve_thread_id(str(value)) == value

from unittest.mock import ANY, AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
import typer
from sqlalchemy import create_engine
from typer.testing import CliRunner

from fragile.commands.interactive.commands import COMMAND_REGISTRY, CommandRegistry
from fragile.commands.interactive.commands.base import extract_prompt
from fragile.commands.interactive.commands.quit import QuitCommand
from fragile.commands.interactive.session import interactive, parse_thread_id
from fragile.exceptions import FragileError, InvalidThreadIdError
from fragile.models import Base, SessionState
from fragile.models.constants import CommandResult

runner = CliRunner()


class TestSession:
    @pytest.fixture(autouse=True)
    def database(self, tmp_path, monkeypatch) -> None:
        engine = create_engine(f"sqlite:///{tmp_path / 'history.db'}")
        Base.metadata.create_all(engine)
        monkeypatch.setattr("fragile.commands.interactive.commands.history.engine", engine)

    def test_command_registry_rejects_non_command_registration(self) -> None:
        with pytest.raises(TypeError, match="command must be a Command instance"):
            CommandRegistry().register(object())

    @pytest.mark.asyncio
    async def test_command_registry_handles_registered_commands(self) -> None:
        state = SessionState(thread_id=UUID(int=1), prompt_session=object())

        assert await COMMAND_REGISTRY.handle("/quit", state) is CommandResult.EXIT
        assert await COMMAND_REGISTRY.handle("/new", state) is CommandResult.CONTINUE
        assert await COMMAND_REGISTRY.handle("ordinary prompt", state) is CommandResult.NOT_HANDLED

    @pytest.mark.asyncio
    async def test_new_command_does_not_create_history_before_chat(self) -> None:
        with patch("fragile.commands.interactive.commands.new.show_startup"):
            state = SessionState(thread_id=UUID(int=1), prompt_session=object())
            assert await COMMAND_REGISTRY.handle("/new", state) is CommandResult.CONTINUE

    @pytest.mark.asyncio
    async def test_command_registry_handles_only_the_indexed_handler(self) -> None:
        state = SessionState(thread_id=UUID(int=1), prompt_session=object())
        with patch.dict(COMMAND_REGISTRY._handlers, {"quit": QuitCommand()}, clear=True):
            assert await COMMAND_REGISTRY.handle("  /QUIT  ", state) is CommandResult.EXIT

    @pytest.mark.asyncio
    async def test_command_registry_does_not_call_handlers_for_unknown_command(self) -> None:
        state = SessionState(thread_id=UUID(int=1), prompt_session=object())
        handler = patch("fragile.commands.interactive.commands.quit.QuitCommand.handle")
        with handler as mocked_handler:
            assert await COMMAND_REGISTRY.handle("/unknown", state) is CommandResult.NOT_HANDLED
        mocked_handler.assert_not_called()

    def test_extract_command_ignores_case_and_whitespace(self) -> None:
        assert extract_prompt("  /QUIT  ").model_dump() == {"command": "quit", "prompt": None}
        assert extract_prompt("  /NEW  你好呀").model_dump() == {"command": "new", "prompt": "你好呀"}
        assert extract_prompt("  /HISTORY  ").model_dump() == {"command": "history", "prompt": None}
        assert extract_prompt("你好呀").model_dump() == {"command": None, "prompt": "你好呀"}

    @pytest.mark.asyncio
    async def testinteractive_history_command_reads_prompt(self) -> None:
        first = UUID(int=1)
        with (
            patch(
                "fragile.commands.interactive.commands.history.list_history",
                new_callable=AsyncMock,
                return_value=[(first, "第一次对话")],
            ),
            patch("fragile.commands.interactive.commands.history.select_history", return_value=first),
            patch(
                "fragile.commands.interactive.session.prompt",
                new_callable=AsyncMock,
                side_effect=["/history", "/quit"],
            ),
            patch("fragile.commands.interactive.commands.history.show_startup") as show_startup,
        ):
            await interactive(None)

        show_startup.assert_any_call(first, True)

    @pytest.mark.asyncio
    async def testinteractive_history_command_uses_keyboard_selector(self) -> None:
        first = UUID(int=1)
        with (
            patch(
                "fragile.commands.interactive.commands.history.list_history",
                new_callable=AsyncMock,
                return_value=[(first, "第一次对话")],
            ),
            patch(
                "fragile.commands.interactive.commands.history.select_history",
                new_callable=AsyncMock,
                return_value=first,
            ) as selector,
            patch(
                "fragile.commands.interactive.session.prompt",
                new_callable=AsyncMock,
                side_effect=["/history", "/quit"],
            ),
        ):
            await interactive(None)

        selector.assert_awaited_once()

    def testparse_thread_id_rejects_invalid_value(self) -> None:

        with pytest.raises(InvalidThreadIdError, match="Must be a valid UUID"):
            parse_thread_id("bad")

    def test_invalidparse_thread_id_is_fragile_error_and_typer_parameter(self) -> None:
        assert issubclass(InvalidThreadIdError, FragileError)
        assert issubclass(InvalidThreadIdError, typer.BadParameter)

    @pytest.mark.asyncio
    async def test_interactive_restores_terminal_on_exit(self) -> None:
        with (
            patch("fragile.commands.interactive.session.enter_fullscreen"),
            patch("fragile.commands.interactive.session.leave_fullscreen") as leave_fullscreen,
            patch("fragile.commands.interactive.session.prompt", new_callable=AsyncMock, return_value="/quit"),
        ):
            await interactive(None)
        leave_fullscreen.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_interactive_retries_after_keyboard_interrupt_and_eof(self) -> None:
        with (
            patch("fragile.commands.interactive.session.enter_fullscreen"),
            patch("fragile.commands.interactive.session.leave_fullscreen"),
            patch(
                "fragile.commands.interactive.session.prompt",
                new_callable=AsyncMock,
                side_effect=[KeyboardInterrupt, EOFError, "/quit"],
            ),
        ):
            await interactive(None)

    @pytest.mark.asyncio
    async def test_interactive_exits_after_two_keyboard_interrupts(self) -> None:
        with (
            patch("fragile.commands.interactive.session.enter_fullscreen"),
            patch("fragile.commands.interactive.session.leave_fullscreen"),
            patch(
                "fragile.commands.interactive.session.prompt",
                new_callable=AsyncMock,
                side_effect=[KeyboardInterrupt, KeyboardInterrupt],
            ),
        ):
            await interactive(None)

    @pytest.mark.asyncio
    async def test_interactive_chats_for_unhandled_nonempty_prompt(self) -> None:
        state = MagicMock()
        with (
            patch("fragile.commands.interactive.session.enter_fullscreen"),
            patch("fragile.commands.interactive.session.leave_fullscreen"),
            patch("fragile.commands.interactive.session.SessionState", return_value=state),
            patch(
                "fragile.commands.interactive.session.prompt",
                new_callable=AsyncMock,
                side_effect=["  hello  ", "/quit"],
            ),
            patch.object(
                COMMAND_REGISTRY,
                "handle",
                new_callable=AsyncMock,
                side_effect=[CommandResult.NOT_HANDLED, CommandResult.EXIT],
            ),
            patch(
                "fragile.commands.interactive.session.ConversationHistory.register_conversation",
                new_callable=AsyncMock,
            ) as register,
            patch("fragile.commands.interactive.session.chat", new_callable=AsyncMock) as chat,
        ):
            await interactive(None)

        register.assert_awaited_once_with(state.thread_id, "hello")
        chat.assert_awaited_once_with("hello", state.thread_id, ANY)

    @pytest.mark.asyncio
    async def test_interactive_ignores_empty_prompt(self) -> None:
        with (
            patch("fragile.commands.interactive.session.enter_fullscreen"),
            patch("fragile.commands.interactive.session.leave_fullscreen"),
            patch(
                "fragile.commands.interactive.session.prompt",
                new_callable=AsyncMock,
                side_effect=["   ", "/quit"],
            ),
        ):
            await interactive(None)

    def testparse_thread_id(self) -> None:

        value = UUID("12345678-1234-5678-1234-567812345678")
        assert parse_thread_id(str(value)) == value

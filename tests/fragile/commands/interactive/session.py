from unittest.mock import ANY, AsyncMock, MagicMock, patch
from uuid import UUID

import asyncclick as click
import pytest
from sqlalchemy import create_engine

from fragile.commands.interactive.commands import CommandRegistry, command_registry
from fragile.commands.interactive.commands.base import extract_prompt
from fragile.commands.interactive.commands.quit import QuitCommand
from fragile.commands.interactive.session import interactive, parse_thread_id
from fragile.exceptions import FragileError, InvalidThreadIdError
from fragile.models import Base, SessionState
from fragile.models.constants import CommandResult


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
        ):
            await interactive(None)

        register.assert_awaited_once_with(state.thread_id, "hello")
        chat.assert_awaited_once_with("hello", state.thread_id, ANY)
        leave_fullscreen.assert_called_once_with()

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

    def testparse_thread_id_rejects_invalid_value(self) -> None:

        with pytest.raises(InvalidThreadIdError, match="Must be a valid UUID"):
            parse_thread_id("bad")

    def test_invalidparse_thread_id_is_fragile_error_and_typer_parameter(self) -> None:
        assert issubclass(InvalidThreadIdError, FragileError)
        assert issubclass(InvalidThreadIdError, click.BadParameter)

    def testparse_thread_id(self) -> None:

        value = UUID("12345678-1234-5678-1234-567812345678")
        assert parse_thread_id(str(value)) == value

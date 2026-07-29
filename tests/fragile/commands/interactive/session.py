from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
import typer
from sqlalchemy import create_engine
from typer.testing import CliRunner

from fragile.app import app
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
        monkeypatch.setattr("fragile.models.history.engine", engine)
        monkeypatch.setattr("fragile.commands.interactive.commands.history.engine", engine)

    def test_command_registry_rejects_non_command_registration(self) -> None:
        with pytest.raises(TypeError, match="command must be a Command instance"):
            CommandRegistry().register(object())

    def test_command_registry_handles_registered_commands(self) -> None:
        state = SessionState(thread_id=UUID(int=1), prompt_session=object())

        assert COMMAND_REGISTRY.handle("/quit", state) is CommandResult.EXIT
        assert COMMAND_REGISTRY.handle("/new", state) is CommandResult.CONTINUE
        assert COMMAND_REGISTRY.handle("ordinary prompt", state) is CommandResult.NOT_HANDLED

    def test_command_registry_handles_only_the_indexed_handler(self) -> None:
        state = SessionState(thread_id=UUID(int=1), prompt_session=object())
        with patch.dict(COMMAND_REGISTRY._handlers, {"quit": QuitCommand()}, clear=True):
            assert COMMAND_REGISTRY.handle("  /QUIT  ", state) is CommandResult.EXIT

    def test_command_registry_does_not_call_handlers_for_unknown_command(self) -> None:
        state = SessionState(thread_id=UUID(int=1), prompt_session=object())
        handler = patch("fragile.commands.interactive.commands.quit.QuitCommand.handle")
        with handler as mocked_handler:
            assert COMMAND_REGISTRY.handle("/unknown", state) is CommandResult.NOT_HANDLED
        mocked_handler.assert_not_called()

    def test_extract_command_ignores_case_and_whitespace(self) -> None:
        assert extract_prompt("  /QUIT  ").model_dump() == {"command": "quit", "prompt": None}
        assert extract_prompt("  /NEW  你好呀").model_dump() == {"command": "new", "prompt": "你好呀"}
        assert extract_prompt("  /HISTORY  ").model_dump() == {"command": "history", "prompt": None}
        assert extract_prompt("你好呀").model_dump() == {"command": None, "prompt": "你好呀"}

    def testinteractive_history_command_reads_prompt_outside_async_context(self) -> None:
        first = UUID(int=1)
        with (
            patch(
                "fragile.commands.interactive.commands.history.list_history",
                new_callable=AsyncMock,
                return_value=[(first, "第一次对话")],
            ),
            patch("fragile.commands.interactive.commands.history.choice", return_value=first),
            patch("fragile.commands.interactive.session.prompt", side_effect=["/history", "/quit"]),
            patch("fragile.commands.interactive.commands.history.show_startup") as show_startup,
        ):
            interactive(None)

        show_startup.assert_any_call(first, True)

    def testinteractive_history_command_uses_keyboard_selector(self) -> None:
        first = UUID(int=1)
        with (
            patch(
                "fragile.commands.interactive.commands.history.list_history",
                new_callable=AsyncMock,
                return_value=[(first, "第一次对话")],
            ),
            patch("fragile.commands.interactive.commands.history.choice", return_value=first) as selector,
            patch("fragile.commands.interactive.session.prompt", side_effect=["/history", "/quit"]),
        ):
            interactive(None)

        selector.assert_called_once()

    def testparse_thread_id_rejects_invalid_value(self) -> None:

        with pytest.raises(InvalidThreadIdError, match="Must be a valid UUID"):
            parse_thread_id("bad")

    def test_invalidparse_thread_id_is_fragile_error_and_typer_parameter(self) -> None:
        assert issubclass(InvalidThreadIdError, FragileError)
        assert issubclass(InvalidThreadIdError, typer.BadParameter)

    def test_main_without_arguments_entersinteractive_mode(self) -> None:
        with (
            patch("fragile.commands.interactive.session.prompt", return_value="/quit"),
            patch("fragile.commands.interactive.session.chat", new_callable=AsyncMock) as chat,
        ):
            result = runner.invoke(app, [])
        assert result.exit_code == 0
        chat.assert_not_awaited()

    def testinteractive_requires_two_consecutive_keyboard_interrupts(self) -> None:
        with (
            patch(
                "fragile.commands.interactive.session.prompt",
                side_effect=[KeyboardInterrupt, "hello", KeyboardInterrupt, KeyboardInterrupt],
            ),
            patch("fragile.commands.interactive.session.chat", new_callable=AsyncMock) as chat,
        ):
            interactive(None)

        assert chat.await_args.args[0] == "hello"

    def testinteractive_requires_two_consecutive_abort_exceptions(self) -> None:
        with (
            patch(
                "fragile.commands.interactive.session.prompt",
                side_effect=[typer.Abort, "hello", typer.Abort, typer.Abort],
            ),
            patch("fragile.commands.interactive.session.chat", new_callable=AsyncMock) as chat,
        ):
            interactive(None)

        assert chat.await_args.args[0] == "hello"

    def testinteractive_requires_interrupts_within_one_second(self) -> None:
        with (
            patch(
                "fragile.commands.interactive.session.prompt",
                side_effect=[KeyboardInterrupt, KeyboardInterrupt, "/quit"],
            ),
            patch("fragile.commands.interactive.session.time.monotonic", side_effect=[0, 0.6]),
            patch("fragile.commands.interactive.session.settings.INTERRUPT_EXIT_THRESHOLD", 0.5),
        ):
            interactive(None)

    def testinteractive_exits_after_two_interrupts_within_one_second(self) -> None:
        with (
            patch(
                "fragile.commands.interactive.session.prompt",
                side_effect=[KeyboardInterrupt, KeyboardInterrupt],
            ),
            patch("fragile.commands.interactive.session.time.monotonic", side_effect=[0, 0.5]),
            patch("fragile.commands.interactive.session.settings.INTERRUPT_EXIT_THRESHOLD", 0.5),
        ):
            interactive(None)

    def testinteractive_ignores_eof(self) -> None:
        with patch(
            "fragile.commands.interactive.session.prompt",
            side_effect=[EOFError, "/quit"],
        ):
            interactive(None)

    def testinteractive_restores_terminal_on_exit(self) -> None:
        with (
            patch("fragile.commands.interactive.session.enter_fullscreen") as enter_fullscreen,
            patch("fragile.commands.interactive.session.leave_fullscreen") as leave_fullscreen,
            patch("fragile.commands.interactive.session.prompt", return_value="/quit"),
        ):
            interactive(None)

        enter_fullscreen.assert_called_once_with()
        leave_fullscreen.assert_called_once_with()

    def testinteractive_sends_nonemptyprompt(self) -> None:
        with (
            patch("fragile.commands.interactive.session.prompt", side_effect=["hello", "/quit"]),
            patch("fragile.commands.interactive.session.chat", new_callable=AsyncMock) as chat,
        ):
            interactive(None)
        chat.assert_awaited_once()

    def testinteractive_emptyprompt(self) -> None:
        with (
            patch("fragile.commands.interactive.session.prompt", side_effect=["", "/quit"]),
            patch("fragile.commands.interactive.session.chat", new_callable=AsyncMock),
        ):
            result = runner.invoke(app, [])
        assert result.exit_code == 0

    def testinteractive_new_command_preserves_screen_and_starts_new_thread(self) -> None:
        with (
            patch("fragile.commands.interactive.session.uuid4", side_effect=[UUID(int=1)]),
            patch("fragile.commands.interactive.commands.new.uuid4", side_effect=[UUID(int=2)]),
            patch("fragile.commands.interactive.session.show_startup") as show_startup,
            patch("fragile.commands.interactive.commands.new.show_startup") as new_show_startup,
            patch("fragile.commands.interactive.session.chat", new_callable=AsyncMock) as chat,
        ):
            with patch("fragile.commands.interactive.session.prompt", side_effect=["/new", "hello", "/quit"]):
                interactive(None)

        assert show_startup.call_args_list[0].args == (UUID(int=1), False)
        assert new_show_startup.call_args.args == (UUID(int=2), False)
        assert chat.await_args.args[:2] == ("hello", UUID(int=2))

    def testparse_thread_id(self) -> None:

        value = UUID("12345678-1234-5678-1234-567812345678")
        assert parse_thread_id(str(value)) == value

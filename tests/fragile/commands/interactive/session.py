from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
import typer
from typer.testing import CliRunner

from fragile.cli import app
from fragile.commands.interactive import commands
from fragile.commands.interactive.commands import CommandRegistry, handle_command
from fragile.commands.interactive.commands.history import is_history_command
from fragile.commands.interactive.commands.new import is_new_command
from fragile.commands.interactive.commands.quit import is_exit_command
from fragile.commands.interactive.session import interactive, parse_thread_id
from fragile.exceptions import FragileError, InvalidThreadIdError
from fragile.models import SessionState
from fragile.models.constants import CommandResult

runner = CliRunner()


class TestSession:
    def test_command_registry_registers_and_filters_commands(self) -> None:
        registry = CommandRegistry()
        handler = lambda prompt, state: CommandResult.EXIT
        registry.register(" /CUSTOM ", handler)

        assert registry.build(("custom",)) == {"/custom": handler}
        assert registry.build(("other",)) == {}

    def testhandle_command_dispatches_registered_commands(self) -> None:
        state = SessionState(thread_id=UUID(int=1), prompt_session=object())

        assert handle_command("/quit", state) is CommandResult.EXIT
        assert handle_command("/new", state) is CommandResult.CONTINUE
        assert handle_command("ordinary prompt", state) is CommandResult.NOT_HANDLED

    def testhandle_command_uses_only_the_indexed_handler(self) -> None:
        state = SessionState(thread_id=UUID(int=1), prompt_session=object())
        custom_handler = lambda prompt, state: CommandResult.EXIT
        with patch.dict(commands.COMMAND_HANDLER_MAP, {"/custom": custom_handler}, clear=True):
            assert handle_command("  /CUSTOM  ", state) is CommandResult.EXIT

    def testhandle_command_does_not_call_handlers_for_unknown_command(self) -> None:
        state = SessionState(thread_id=UUID(int=1), prompt_session=object())
        handler = patch("fragile.commands.interactive.commands.handle_exit")
        with handler as mocked_handler:
            assert handle_command("/unknown", state) is CommandResult.NOT_HANDLED
        mocked_handler.assert_not_called()

    def testis_exit_command_ignores_case_and_whitespace(self) -> None:

        assert is_exit_command("  EXIT  ") is False
        assert is_exit_command("  quit  ") is False
        assert is_exit_command("  /QUIT  ") is True
        assert is_exit_command("continue") is False

    def testis_new_command_ignores_case_and_whitespace(self) -> None:

        assert is_new_command("  /NEW  ") is True
        assert is_new_command("new") is False

    def testis_history_command_ignores_case_and_whitespace(self) -> None:

        assert is_history_command("  /HISTORY  ") is True
        assert is_history_command("history") is False

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

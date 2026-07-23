from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
import typer
from typer.testing import CliRunner

from fragile.cli import app
from fragile.commands.interactive.session import interactive, is_exit_command, is_new_command, parse_thread_id
from fragile.exceptions import FragileError, InvalidThreadIdError

runner = CliRunner()


class TestSession:
    def testis_exit_command_ignores_case_and_whitespace(self) -> None:

        assert is_exit_command("  EXIT  ") is False
        assert is_exit_command("  quit  ") is False
        assert is_exit_command("  /QUIT  ") is True
        assert is_exit_command("continue") is False

    def testis_new_command_ignores_case_and_whitespace(self) -> None:

        assert is_new_command("  /NEW  ") is True
        assert is_new_command("new") is False

    def testparse_thread_id_rejects_invalid_value(self) -> None:

        with pytest.raises(InvalidThreadIdError, match="必须是有效的 UUID"):
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
            patch("fragile.commands.interactive.session.time.monotonic", side_effect=[0, 1.1]),
        ):
            interactive(None)

    def testinteractive_exits_after_two_interrupts_within_one_second(self) -> None:
        with (
            patch(
                "fragile.commands.interactive.session.prompt",
                side_effect=[KeyboardInterrupt, KeyboardInterrupt],
            ),
            patch("fragile.commands.interactive.session.time.monotonic", side_effect=[0, 1]),
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

    def testinteractive_new_command_clears_screen_and_starts_new_thread(self) -> None:
        with (
            patch("fragile.commands.interactive.session.clear_screen") as clear_screen,
            patch("fragile.commands.interactive.session.uuid4", side_effect=[UUID(int=1), UUID(int=2)]),
            patch("fragile.commands.interactive.session.show_startup") as show_startup,
            patch("fragile.commands.interactive.session.chat", new_callable=AsyncMock) as chat,
        ):
            with patch("fragile.commands.interactive.session.prompt", side_effect=["/new", "hello", "/quit"]):
                interactive(None)

        clear_screen.assert_called_once_with()
        assert show_startup.call_args_list[0].args == (UUID(int=1), False)
        assert show_startup.call_args_list[1].args == (UUID(int=2), False)
        assert chat.await_args.args[:2] == ("hello", UUID(int=2))

    def testparse_thread_id(self) -> None:

        value = UUID("12345678-1234-5678-1234-567812345678")
        assert parse_thread_id(str(value)) == value

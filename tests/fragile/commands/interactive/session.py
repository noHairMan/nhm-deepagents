from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
import typer
from typer.testing import CliRunner

from fragile.cli import app
from fragile.commands.interactive.session import (
    choose_history,
    interactive,
    is_exit_command,
    is_history_command,
    is_new_command,
    list_thread_ids,
    parse_thread_id,
)
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

    def testis_history_command_ignores_case_and_whitespace(self) -> None:

        assert is_history_command("  /HISTORY  ") is True
        assert is_history_command("history") is False

    @pytest.mark.asyncio
    async def testlist_thread_ids_returns_distinct_ids(self) -> None:
        first = UUID(int=1)
        second = UUID(int=2)
        checkpoints = [
            type("Checkpoint", (), {"config": {"configurable": {"thread_id": str(second)}}})(),
            type("Checkpoint", (), {"config": {"configurable": {"thread_id": str(first)}}})(),
            type("Checkpoint", (), {"config": {"configurable": {"thread_id": str(second)}}})(),
        ]

        async def alist(self: object, config: object) -> object:
            for checkpoint in checkpoints:
                yield checkpoint

        checkpointer = type("Checkpointer", (), {"alist": alist})()
        with patch("fragile.commands.interactive.session.get_checkpointer_context") as context:
            context.return_value.__aenter__ = AsyncMock(return_value=checkpointer)
            context.return_value.__aexit__ = AsyncMock(return_value=None)
            assert await list_thread_ids() == [first, second]

    @pytest.mark.asyncio
    async def testlist_thread_ids_ignores_checkpoints_without_thread_id(self) -> None:
        checkpoint = type("Checkpoint", (), {"config": {"configurable": {}}})()

        async def alist(self: object, config: object) -> object:
            yield checkpoint

        checkpointer = type("Checkpointer", (), {"alist": alist})()
        with patch("fragile.commands.interactive.session.get_checkpointer_context") as context:
            context.return_value.__aenter__ = AsyncMock(return_value=checkpointer)
            context.return_value.__aexit__ = AsyncMock(return_value=None)
            assert await list_thread_ids() == []

    def testchoose_history_accepts_number_and_rejects_unknown(self) -> None:
        first = UUID(int=1)
        session = object()
        with patch("fragile.commands.interactive.session.prompt", return_value="1"):
            assert choose_history(session, [first]) == first
        with patch("fragile.commands.interactive.session.prompt", return_value="bad"):
            assert choose_history(session, [first]) is None
        with patch("fragile.commands.interactive.session.prompt", return_value="2"):
            assert choose_history(session, [first]) is None

    def testchoose_history_accepts_uuid_and_handles_empty_or_unknown_history(self) -> None:
        first = UUID(int=1)
        session = object()
        with patch("fragile.commands.interactive.session.prompt", return_value=str(first)):
            assert choose_history(session, [first]) == first
        with patch("fragile.commands.interactive.session.prompt", return_value=str(UUID(int=2))):
            assert choose_history(session, [first]) is None
        assert choose_history(session, []) is None

    @pytest.mark.asyncio
    async def testlist_thread_ids_returns_empty_without_checkpointer(self) -> None:
        context = MagicMock()
        context.return_value.__aenter__ = AsyncMock(return_value=None)
        context.return_value.__aexit__ = AsyncMock(return_value=None)
        with patch("fragile.commands.interactive.session.get_checkpointer_context", context):
            assert await list_thread_ids() == []

    def testinteractive_history_command_reads_prompt_outside_async_context(self) -> None:
        first = UUID(int=1)
        with (
            patch("fragile.commands.interactive.session.list_thread_ids", new_callable=AsyncMock, return_value=[first]),
            patch("fragile.commands.interactive.session.prompt", side_effect=["/history", "1", "/quit"]),
            patch("fragile.commands.interactive.session.show_startup") as show_startup,
        ):
            interactive(None)

        show_startup.assert_any_call(first, True)

    def testinteractive_history_command_keeps_current_thread_on_invalid_selection(self) -> None:
        with (
            patch(
                "fragile.commands.interactive.session.list_thread_ids",
                new_callable=AsyncMock,
                return_value=[UUID(int=1)],
            ),
            patch("fragile.commands.interactive.session.prompt", side_effect=["/history", "bad", "/quit"]),
        ):
            interactive(None)

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

    def testinteractive_new_command_preserves_screen_and_starts_new_thread(self) -> None:
        with (
            patch("fragile.commands.interactive.session.uuid4", side_effect=[UUID(int=1), UUID(int=2)]),
            patch("fragile.commands.interactive.session.show_startup") as show_startup,
            patch("fragile.commands.interactive.session.chat", new_callable=AsyncMock) as chat,
        ):
            with patch("fragile.commands.interactive.session.prompt", side_effect=["/new", "hello", "/quit"]):
                interactive(None)

        assert show_startup.call_args_list[0].args == (UUID(int=1), False)
        assert show_startup.call_args_list[1].args == (UUID(int=2), False)
        assert chat.await_args.args[:2] == ("hello", UUID(int=2))

    def testparse_thread_id(self) -> None:

        value = UUID("12345678-1234-5678-1234-567812345678")
        assert parse_thread_id(str(value)) == value

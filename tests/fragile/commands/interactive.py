from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
import typer
from prompt_toolkit.document import Document
from prompt_toolkit.keys import Keys
from typer.testing import CliRunner

from fragile.cli import app
from fragile.exceptions import FragileError, InvalidThreadIdError

runner = CliRunner()


class TestApp:
    @pytest.mark.asyncio
    async def test_events_filters_and_yields_text(self) -> None:
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
        from fragile.commands.interactive import _events

        assert [value async for value in _events(agent, "prompt", UUID(int=1))] == ["ok", "你好呀"]

    def test_content_text_handles_supported_content(self) -> None:
        from fragile.commands.interactive import _content_text

        assert _content_text("text") == "text"
        assert _content_text(["a", {"type": "text", "text": "b"}, {"type": "image"}]) == "ab"
        assert _content_text(None) == ""

    def test_prompt_session_configures_interactive_features(self) -> None:
        from fragile.commands.interactive import _CommandCompleter, _create_prompt_session, _prompt

        session = _create_prompt_session()
        assert session.multiline is True
        assert isinstance(session.completer, _CommandCompleter)
        assert {binding.keys for binding in session.key_bindings.bindings} == {
            (Keys.ControlM,),
            (Keys.Escape, Keys.ControlM),
        }
        with patch.object(session, "prompt", return_value="answer") as prompt:
            assert _prompt(session) == "answer"
        prompt.assert_called_once_with("你> ")

    def test_prompt_session_key_bindings_submit_and_insert_newline(self) -> None:
        from fragile.commands.interactive import _create_prompt_session

        session = _create_prompt_session()
        event = MagicMock()
        handlers = {binding.keys: binding.handler for binding in session.key_bindings.bindings}

        handlers[(Keys.ControlM,)](event)
        handlers[(Keys.Escape, Keys.ControlM)](event)

        event.current_buffer.validate_and_handle.assert_called_once_with()
        event.current_buffer.insert_text.assert_called_once_with("\n")

    def test_command_completer_completes_commands_only(self) -> None:
        from fragile.commands.interactive import _CommandCompleter

        completer = _CommandCompleter()
        completions = list(completer.get_completions(Document("/q"), None))
        assert [completion.text for completion in completions] == ["/quit"]
        assert list(completer.get_completions(Document("hello"), None)) == []
        assert list(completer.get_completions(Document("/new arg"), None)) == []

    def test_is_exit_command_ignores_case_and_whitespace(self) -> None:
        from fragile.commands.interactive import _is_exit_command

        assert _is_exit_command("  EXIT  ") is False
        assert _is_exit_command("  quit  ") is False
        assert _is_exit_command("  /QUIT  ") is True
        assert _is_exit_command("continue") is False

    def test_is_new_command_ignores_case_and_whitespace(self) -> None:
        from fragile.commands.interactive import _is_new_command

        assert _is_new_command("  /NEW  ") is True
        assert _is_new_command("new") is False

    def test_clear_screen(self, capsys) -> None:
        from fragile.commands.interactive import _clear_screen

        _clear_screen()

        assert capsys.readouterr().out == "\033[2J\033[3J\033[H"

    def test_fullscreen_terminal_sequences(self, capsys) -> None:
        from fragile.commands.interactive import _enter_fullscreen, _leave_fullscreen

        _enter_fullscreen()
        _leave_fullscreen()

        assert capsys.readouterr().out == "\033[2J\033[3J\033[H\033[?25l\033[?25h"

    def test_startup_display_for_new_session(self, capsys) -> None:
        from fragile.commands.interactive import _show_startup

        _show_startup(UUID(int=1), False)

        output = capsys.readouterr().out
        assert "Fresh start" in output
        assert "All previous messages and task state have been cleared" in output
        assert "Connected to Tomorrow agent" in output
        assert "Fragile is ready" in output

    def test_startup_display_for_resumed_session(self, capsys) -> None:
        from fragile.commands.interactive import _show_startup

        _show_startup(UUID(int=1), True)

        output = capsys.readouterr().out
        assert "已恢复会话" in output
        assert "Fresh start" not in output

    @pytest.mark.asyncio
    async def test_chat_uses_checkpoint_and_prints(self, capsys) -> None:
        context = MagicMock()
        context.__aenter__ = AsyncMock(return_value="checkpoint")
        context.__aexit__ = AsyncMock(return_value=None)
        with (
            patch("fragile.commands.interactive.get_checkpointer_context", return_value=context),
            patch("fragile.commands.interactive.AgentManager.create_agent", return_value=MagicMock()),
            patch("fragile.commands.interactive._events", return_value=self._async_values("answer")),
        ):
            from fragile.commands.interactive import _chat

            await _chat("prompt", UUID(int=1))
        assert capsys.readouterr().out == "answer\n"

    @staticmethod
    async def _async_values(*values: str):
        for value in values:
            yield value

    def test_help(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "interactive" not in result.stdout

    def test_module_entrypoint(self) -> None:
        import runpy

        with patch("fragile.cli.app") as app_mock:
            runpy.run_path("src/fragile/__main__.py", run_name="__main__")

        app_mock.assert_called_once_with()

    def test_prompt_argument_is_rejected(self) -> None:
        result = runner.invoke(app, ["你好"])
        assert result.exit_code != 0

    def test_invalid_thread(self) -> None:
        result = runner.invoke(app, ["--thread", "bad"])
        assert result.exit_code != 0

    def test_thread_id_rejects_invalid_value(self) -> None:
        from fragile.commands.interactive import _thread_id

        with pytest.raises(InvalidThreadIdError, match="必须是有效的 UUID"):
            _thread_id("bad")

    def test_invalid_thread_id_is_fragile_error_and_typer_parameter(self) -> None:
        assert issubclass(InvalidThreadIdError, FragileError)
        assert issubclass(InvalidThreadIdError, typer.BadParameter)

    def test_main_without_prompt(self) -> None:
        from fragile.cli import main

        with patch("fragile.cli.interactive") as interactive:
            main(None)
        interactive.assert_called_once_with(None)

    def test_main_without_arguments_enters_interactive_mode(self) -> None:
        with (
            patch("fragile.commands.interactive._prompt", return_value="/quit"),
            patch("fragile.commands.interactive._chat", new_callable=AsyncMock) as chat,
        ):
            result = runner.invoke(app, [])
        assert result.exit_code == 0
        chat.assert_not_awaited()

    def test_interactive_requires_two_consecutive_keyboard_interrupts(self) -> None:
        from fragile.commands.interactive import interactive

        with (
            patch(
                "fragile.commands.interactive._prompt",
                side_effect=[KeyboardInterrupt, "hello", KeyboardInterrupt, KeyboardInterrupt],
            ),
            patch("fragile.commands.interactive._chat", new_callable=AsyncMock) as chat,
        ):
            interactive(None)

        assert chat.await_args.args[0] == "hello"

    def test_interactive_requires_two_consecutive_abort_exceptions(self) -> None:
        from fragile.commands.interactive import interactive

        with (
            patch(
                "fragile.commands.interactive._prompt",
                side_effect=[typer.Abort, "hello", typer.Abort, typer.Abort],
            ),
            patch("fragile.commands.interactive._chat", new_callable=AsyncMock) as chat,
        ):
            interactive(None)

        assert chat.await_args.args[0] == "hello"

    def test_interactive_requires_interrupts_within_one_second(self) -> None:
        from fragile.commands.interactive import interactive

        with (
            patch(
                "fragile.commands.interactive._prompt",
                side_effect=[KeyboardInterrupt, KeyboardInterrupt, "/quit"],
            ),
            patch("fragile.commands.interactive.time.monotonic", side_effect=[0, 1.1]),
        ):
            interactive(None)

    def test_interactive_exits_after_two_interrupts_within_one_second(self) -> None:
        from fragile.commands.interactive import interactive

        with (
            patch(
                "fragile.commands.interactive._prompt",
                side_effect=[KeyboardInterrupt, KeyboardInterrupt],
            ),
            patch("fragile.commands.interactive.time.monotonic", side_effect=[0, 1]),
        ):
            interactive(None)

    def test_interactive_ignores_eof(self) -> None:
        from fragile.commands.interactive import interactive

        with patch(
            "fragile.commands.interactive._prompt",
            side_effect=[EOFError, "/quit"],
        ):
            interactive(None)

    def test_interactive_restores_terminal_on_exit(self) -> None:
        from fragile.commands.interactive import interactive

        with (
            patch("fragile.commands.interactive._enter_fullscreen") as enter_fullscreen,
            patch("fragile.commands.interactive._leave_fullscreen") as leave_fullscreen,
            patch("fragile.commands.interactive._prompt", return_value="/quit"),
        ):
            interactive(None)

        enter_fullscreen.assert_called_once_with()
        leave_fullscreen.assert_called_once_with()

    def test_interactive_sends_nonempty_prompt(self) -> None:
        from fragile.commands.interactive import interactive

        with (
            patch("fragile.commands.interactive._prompt", side_effect=["hello", "/quit"]),
            patch("fragile.commands.interactive._chat", new_callable=AsyncMock) as chat,
        ):
            interactive(None)
        chat.assert_awaited_once()

    def test_interactive_empty_prompt(self) -> None:
        with (
            patch("fragile.commands.interactive._prompt", side_effect=["", "/quit"]),
            patch("fragile.commands.interactive._chat", new_callable=AsyncMock),
        ):
            result = runner.invoke(app, [])
        assert result.exit_code == 0

    def test_interactive_new_command_clears_screen_and_starts_new_thread(self) -> None:
        with (
            patch("fragile.commands.interactive._clear_screen") as clear_screen,
            patch("fragile.commands.interactive.uuid4", side_effect=[UUID(int=1), UUID(int=2)]),
            patch("fragile.commands.interactive._show_startup") as show_startup,
            patch("fragile.commands.interactive._chat", new_callable=AsyncMock) as chat,
        ):
            from fragile.commands.interactive import interactive

            with patch("fragile.commands.interactive._prompt", side_effect=["/new", "hello", "/quit"]):
                interactive(None)

        clear_screen.assert_called_once_with()
        assert show_startup.call_args_list[0].args == (UUID(int=1), False)
        assert show_startup.call_args_list[1].args == (UUID(int=2), False)
        chat.assert_awaited_once_with("hello", UUID(int=2))

    def test_thread_id(self) -> None:
        from fragile.commands.interactive import _thread_id

        value = UUID("12345678-1234-5678-1234-567812345678")
        assert _thread_id(str(value)) == value

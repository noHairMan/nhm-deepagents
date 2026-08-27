from unittest.mock import patch
from uuid import UUID

from fragile.commands.interactive.display import (
    enter_fullscreen,
    leave_fullscreen,
    print_stream,
    replay_outputs,
    show_connection_error,
    show_startup,
)


class TestDisplay:
    def test_show_connection_error_uses_red_style(self, capsys) -> None:
        show_connection_error("ollama", "qwen3.5:9b", "http://user:secret@localhost:11434/api")

        output = capsys.readouterr().out
        assert "模型服务连接失败" in output
        assert "provider: ollama" in output
        assert "qwen3.5:9b" in output
        assert "http://localhost:11434/api" in output
        assert "secret" not in output

    def test_show_connection_error_does_not_use_red_background(self) -> None:
        with patch("fragile.commands.interactive.display.console.print") as print_console:
            show_connection_error()

        error_text = print_console.call_args.args[0]
        assert error_text.style == "bold red"

    def test_print_stream(self, capsys) -> None:
        print_stream("answer")

        assert capsys.readouterr().out == "answer"

    def test_replay_outputs_preserves_markup(self, capsys) -> None:
        record = type("Record", (), {"user_input": "question", "assistant_output": "[bold]answer[/bold]"})()

        replay_outputs([record])

        output = capsys.readouterr().out
        assert "> question" in output
        assert "answer" in output

    def test_replay_outputs_handles_empty_assistant_content(self, capsys) -> None:
        record = type("Record", (), {"user_input": "question", "assistant_output": ""})()

        replay_outputs([record])

        assert "> question" in capsys.readouterr().out

    def test_fullscreen_uses_isolated_terminal_screen(self, capsys) -> None:

        enter_fullscreen()
        leave_fullscreen()

        assert capsys.readouterr().out == "\033[?1049h\033[?1049l"

    def test_startup_display_for_new_session(self, capsys) -> None:

        show_startup(UUID(int=1), False)

        output = capsys.readouterr().out
        assert "Fresh start" in output
        assert "All previous messages and task state have been cleared" in output
        assert "Tomorrow agent client is ready" in output
        assert "Fragile is ready" in output

    def test_startup_display_for_resumed_session(self, capsys) -> None:

        show_startup(UUID(int=1), True)

        output = capsys.readouterr().out
        assert "Resumed conversation" in output
        assert "Fresh start" not in output

from uuid import UUID

from fragile.commands.interactive.display import (
    clear_screen,
    enter_fullscreen,
    leave_fullscreen,
    print_stream,
    show_startup,
)


class TestDisplay:
    def test_print_stream(self, capsys) -> None:
        print_stream("answer")

        assert capsys.readouterr().out == "answer"

    def testclear_screen(self, capsys) -> None:

        clear_screen()

        assert capsys.readouterr().out == "\033[2J\033[3J\033[H"

    def test_fullscreen_terminal_sequences(self, capsys) -> None:

        enter_fullscreen()
        leave_fullscreen()

        assert capsys.readouterr().out == "\033[2J\033[3J\033[H\033[?25l\033[?25h"

    def test_startup_display_for_new_session(self, capsys) -> None:

        show_startup(UUID(int=1), False)

        output = capsys.readouterr().out
        assert "Fresh start" in output
        assert "All previous messages and task state have been cleared" in output
        assert "Connected to Tomorrow agent" in output
        assert "Fragile is ready" in output

    def test_startup_display_for_resumed_session(self, capsys) -> None:

        show_startup(UUID(int=1), True)

        output = capsys.readouterr().out
        assert "已恢复会话" in output
        assert "Fresh start" not in output

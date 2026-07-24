from fragile.commands.interactive.commands.quit import is_exit_command


class TestQuitCommand:
    def test_is_exit_command_ignores_case_and_whitespace(self) -> None:
        assert is_exit_command("  EXIT  ") is False
        assert is_exit_command("  quit  ") is False
        assert is_exit_command("  /QUIT  ") is True
        assert is_exit_command("continue") is False

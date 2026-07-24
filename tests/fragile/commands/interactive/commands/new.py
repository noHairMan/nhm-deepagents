from fragile.commands.interactive.commands.new import is_new_command


class TestNewCommand:
    def test_is_new_command_ignores_case_and_whitespace(self) -> None:
        assert is_new_command("  /NEW  ") is True
        assert is_new_command("new") is False

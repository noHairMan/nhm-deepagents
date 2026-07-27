from fragile.models.constants import Command, CommandResult


class TestCommand:
    def test_commands(self) -> None:
        assert Command.NEW.value == "new"
        assert Command.HISTORY.value == "history"
        assert Command.QUIT.value == "quit"
        assert Command.NEW.label == "New"
        assert Command.QUIT.label == "Quit"
        assert str(Command.NEW) == "Command.NEW"

    def test_command_results(self) -> None:
        assert CommandResult.NOT_HANDLED.value == 1
        assert CommandResult.CONTINUE.value == 2
        assert CommandResult.EXIT.value == 3
        assert CommandResult.CONTINUE.label == "Continue"

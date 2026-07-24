from fragile.enums import Command


class TestCommand:
    def test_commands(self) -> None:

        assert Command.NEW.value == "new"
        assert Command.HISTORY.value == "history"
        assert Command.QUIT.value == "quit"
        assert Command.NEW.label == "New"
        assert Command.QUIT.label == "Quit"
        assert str(Command.NEW) == "Command.NEW"

from fragile.models.constants import CommandResult


class TestCommand:
    def test_command_results(self) -> None:
        assert CommandResult.NOT_HANDLED.value == 1
        assert CommandResult.CONTINUE.value == 2
        assert CommandResult.EXIT.value == 3
        assert CommandResult.CONTINUE.label == "Continue"

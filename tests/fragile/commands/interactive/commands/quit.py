from uuid import UUID

from fragile.commands.interactive.commands.quit import QuitCommand
from fragile.models import SessionState
from fragile.models.constants import CommandResult


class TestQuitCommand:
    def test_quit_command_handles_prompt_directly(self) -> None:
        state = SessionState(thread_id=UUID(int=1), prompt_session=object())
        assert QuitCommand().handle("ordinary prompt", state) is CommandResult.EXIT

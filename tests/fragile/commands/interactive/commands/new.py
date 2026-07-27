from uuid import UUID

from fragile.commands.interactive.commands.new import NewCommand
from fragile.models import SessionState
from fragile.models.constants import CommandResult


class TestNewCommand:
    def test_new_command_starts_new_conversation(self) -> None:
        state = SessionState(thread_id=UUID(int=1), prompt_session=object())
        assert NewCommand().handle("ordinary prompt", state) is CommandResult.CONTINUE
        assert state.thread_id != UUID(int=1)

from uuid import UUID

import pytest

from fragile.commands.interactive.commands.quit import QuitCommand
from fragile.models import SessionState
from fragile.models.constants import CommandResult


class TestQuitCommand:
    @pytest.mark.asyncio
    async def test_quit_command_handles_prompt(self) -> None:
        state = SessionState(thread_id=UUID(int=1), prompt_session=object())
        assert await QuitCommand().handle("ordinary prompt", state) is CommandResult.EXIT

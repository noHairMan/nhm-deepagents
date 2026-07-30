from unittest.mock import patch
from uuid import UUID

import pytest

from fragile.commands.interactive.commands.new import NewCommand
from fragile.models import SessionState
from fragile.models.constants import CommandResult


class TestNewCommand:
    @pytest.mark.asyncio
    async def test_new_command_does_not_register_history(self) -> None:
        state = SessionState(thread_id=UUID(int=1), prompt_session=object())
        with patch("fragile.commands.interactive.commands.new.show_startup"):
            result = await NewCommand().handle("新对话", state)

        assert result is CommandResult.CONTINUE

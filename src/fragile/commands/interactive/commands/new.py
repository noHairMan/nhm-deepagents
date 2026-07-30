"""New conversation command handling."""

from typing import Optional
from uuid import uuid4

from fragile.commands.interactive.commands.base import Command as BaseCommand
from fragile.commands.interactive.display import show_startup
from fragile.models import SessionState
from fragile.models.constants import CommandResult


class NewCommand(BaseCommand):
    """Start a new conversation."""

    name = "new"

    async def handle(self, prompt: Optional[str], state: SessionState) -> CommandResult:
        """Handle a new conversation without blocking the event loop."""
        state.thread_id = uuid4()
        show_startup(state.thread_id, False)
        return CommandResult.CONTINUE

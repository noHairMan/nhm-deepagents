"""Exit command handling."""

from typing import Optional

from fragile.commands.interactive.commands.base import Command as BaseCommand
from fragile.models import SessionState
from fragile.models.constants import CommandResult


class QuitCommand(BaseCommand):
    """Exit the interactive session."""

    name = "quit"

    def handle(self, prompt: Optional[str], state: SessionState) -> CommandResult:
        """Handle the exit command."""
        return CommandResult.EXIT

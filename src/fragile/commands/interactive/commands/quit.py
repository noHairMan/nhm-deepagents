"""Exit command handling."""

from fragile.commands.interactive.commands.base import Command as BaseCommand
from fragile.models import SessionState
from fragile.models.constants import Command, CommandResult


class QuitCommand(BaseCommand):
    """Exit the interactive session."""

    name = Command.QUIT.value

    def handle(self, prompt: str, state: SessionState) -> CommandResult:
        """Handle the exit command."""
        del state
        return CommandResult.EXIT if is_exit_command(prompt) else CommandResult.NOT_HANDLED


def is_exit_command(prompt: str) -> bool:
    """Return whether the prompt requests leaving the session."""
    return prompt.strip().casefold() == f"/{Command.QUIT.value}"

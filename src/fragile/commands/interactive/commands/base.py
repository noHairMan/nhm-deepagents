"""Base abstractions for interactive commands."""

from abc import ABC, abstractmethod

from fragile.models import SessionState
from fragile.models.constants import CommandResult


class Command(ABC):
    """Base class for an interactive command."""

    name: str

    @abstractmethod
    def handle(self, prompt: str, state: SessionState) -> CommandResult:
        """Handle a prompt and return the resulting session action."""

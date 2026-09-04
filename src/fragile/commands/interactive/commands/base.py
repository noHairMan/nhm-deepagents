"""Base abstractions for interactive commands."""

from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel

from fragile.models import SessionState
from fragile.models.constants import CommandResult


class CommandPrompt(BaseModel):
    """The command and prompt extracted from interactive input."""

    command: str | None
    prompt: str | None


def extract_prompt(prompt: str) -> CommandPrompt:
    """Extract a normalized command name and the remaining prompt."""
    value = prompt.strip()
    if not value.startswith("/"):
        return CommandPrompt(command=None, prompt=value)
    parts = value.split(maxsplit=1)
    return CommandPrompt(
        command=parts[0].lstrip("/").casefold(),
        prompt=parts[1] if len(parts) == 2 else None,
    )


class Command(ABC):
    """Base class for an interactive command."""

    name: str
    clears_output_after_handling: bool = False

    @abstractmethod
    async def handle(self, prompt: Optional[str], state: SessionState) -> CommandResult:
        """Handle a prompt and return the resulting session action."""

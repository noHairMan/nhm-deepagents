"""Shared types for interactive command processing."""

from dataclasses import dataclass
from enum import Enum, auto
from uuid import UUID


class CommandResult(Enum):
    """Result of processing one interactive command."""

    NOT_HANDLED = auto()
    CONTINUE = auto()
    EXIT = auto()


@dataclass
class SessionState:
    """Mutable state shared by interactive command handlers."""

    thread_id: UUID
    prompt_session: object

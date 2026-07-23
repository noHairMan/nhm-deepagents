"""Exceptions raised by the Fragile command-line application."""

from __future__ import annotations

import typer


class FragileError(Exception):
    """Base class for all Fragile-specific exceptions."""


class InvalidThreadIdError(FragileError, typer.BadParameter):
    """Raised when a thread identifier is not a valid UUID."""

"""Exceptions raised by the Fragile command-line application."""

import asyncclick as click


class FragileError(Exception):
    """Base class for all Fragile-specific exceptions."""


class InvalidThreadIdError(FragileError, click.BadParameter):
    """Raised when a thread identifier is not a valid UUID."""

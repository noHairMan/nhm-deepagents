"""Exceptions raised by the Fragile command-line application."""

import asyncclick as click


class FragileError(Exception):
    """Base class for all Fragile-specific exceptions."""


class AgentConfigurationError(FragileError):
    """Base class for invalid configured agent definitions."""


class AgentFactoryImportError(AgentConfigurationError, ImportError):
    """Raised when a configured agent factory cannot be imported."""


class AgentFactoryTypeError(AgentConfigurationError, TypeError):
    """Raised when a configured agent factory is not callable."""


class AgentGraphTypeError(AgentConfigurationError, TypeError):
    """Raised when an agent factory does not return a compiled graph."""


class InvalidCommandError(FragileError, TypeError):
    """Raised when a non-command object is registered."""


class InvalidThreadIdError(FragileError, click.BadParameter):
    """Raised when a thread identifier is not a valid UUID."""

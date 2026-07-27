from tomorrow.core.enums import IntChoices


class CommandResult(IntChoices):
    """Result of processing one interactive command."""

    NOT_HANDLED = 1, "Not handled"
    CONTINUE = 2, "Continue"
    EXIT = 3, "Exit"

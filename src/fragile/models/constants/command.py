from tomorrow.core.enums import IntChoices, TextChoices


class Command(TextChoices):
    """Built-in commands supported by the Fragile interactive session."""

    NEW = "new", "New"
    HISTORY = "history", "History"
    QUIT = "quit", "Quit"


class CommandResult(IntChoices):
    """Result of processing one interactive command."""

    NOT_HANDLED = 1, "Not handled"
    CONTINUE = 2, "Continue"
    EXIT = 3, "Exit"

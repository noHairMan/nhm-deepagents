from tomorrow.core.enums import TextChoices


class Command(TextChoices):
    """Built-in commands supported by the Fragile interactive session."""

    NEW = "new", "New"
    HISTORY = "history", "History"
    QUIT = "quit", "Quit"

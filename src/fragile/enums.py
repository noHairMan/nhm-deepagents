from tomorrow.core.enums import TextChoices


class Command(TextChoices):
    """Fragile 交互式会话支持的内置命令。"""

    NEW = "new", "New"
    HISTORY = "history", "History"
    QUIT = "quit", "Quit"

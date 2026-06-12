from tomorrow.core.enums import TextChoices


class StoreType(TextChoices):
    SQLITE = "sqlite", "SQLite"
    MEMORY = "memory", "Memory"

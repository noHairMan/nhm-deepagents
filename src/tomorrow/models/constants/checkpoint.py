from tomorrow.core.enums import TextChoices


class CheckpointType(TextChoices):
    MEMORY = "memory", "Memory"
    SQLITE = "sqlite", "SQLite"
    POSTGRES = "postgres", "PostgreSQL"
    REDIS = "redis", "Redis"
    MONGODB = "mongodb", "MongoDB"

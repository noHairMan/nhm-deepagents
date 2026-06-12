from tomorrow.core.enums import TextChoices


class BackendType(TextChoices):
    FILESYSTEM = "filesystem", "Filesystem"
    DAYTONA = "daytona", "Daytona"

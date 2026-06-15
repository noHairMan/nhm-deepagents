from tomorrow.core.enums import TextChoices


class BackendType(TextChoices):
    FILESYSTEM = "filesystem", "Filesystem"
    LOCAL_SHELL = "local_shell", "LocalShell"

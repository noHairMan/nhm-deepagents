from pathlib import Path

from fragile.app import app
from tomorrow.conf import settings
from tomorrow.models.constants import CheckpointType


def configure_checkpoint() -> None:
    settings.CHECKPOINT.type = CheckpointType.SQLITE
    settings.CHECKPOINT.sqlite.path = Path.cwd() / "fragile.db"


def main() -> None:
    configure_checkpoint()
    app()


if __name__ == "__main__":
    main()

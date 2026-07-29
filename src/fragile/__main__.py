from pathlib import Path

from fragile.app import app  # pragma: no cover
from tomorrow.conf import settings  # pragma: no cover
from tomorrow.models.constants import CheckpointType  # pragma: no cover


def configure_checkpoint() -> None:  # pragma: no cover
    settings.CHECKPOINT.type = CheckpointType.SQLITE
    settings.CHECKPOINT.sqlite.path = Path.cwd() / "fragile.db"


def main() -> None:  # pragma: no cover
    configure_checkpoint()
    app()


if __name__ == "__main__":  # pragma: no cover
    main()

from logging.config import dictConfig
from pathlib import Path

from fragile.app import app
from fragile.conf import settings


def configure_checkpoint() -> None:
    from tomorrow.conf import settings
    from tomorrow.models.constants import CheckpointType

    settings.CHECKPOINT.type = CheckpointType.SQLITE
    settings.CHECKPOINT.sqlite.path = Path.cwd() / "fragile.db"


def configure_logging() -> None:
    dictConfig(settings.LOGGING)


def main() -> None:
    configure_logging()
    configure_checkpoint()
    app()


if __name__ == "__main__":
    main()

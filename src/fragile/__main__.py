from pathlib import Path

from fragile.app import app


def configure_checkpoint() -> None:
    from tomorrow.conf import settings
    from tomorrow.models.constants import CheckpointType

    settings.CHECKPOINT.type = CheckpointType.SQLITE
    settings.CHECKPOINT.sqlite.path = Path.cwd() / "fragile.db"


def main() -> None:
    configure_checkpoint()
    app()


if __name__ == "__main__":
    main()

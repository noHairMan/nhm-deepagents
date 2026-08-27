import logging
from logging.config import dictConfig
from pathlib import Path

from fragile.conf import settings


def configure_checkpoint() -> None:
    import fragile.commands.purge as purge_module
    import fragile.models.base as base_module
    from tomorrow.conf import settings
    from tomorrow.models.constants import CheckpointType

    settings.CHECKPOINT.type = CheckpointType.SQLITE
    settings.CHECKPOINT.sqlite.path = Path.cwd() / "fragile.db"
    base_module.engine = base_module.get_engine()
    purge_module.engine = base_module.engine


def configure_logging() -> None:
    dictConfig(settings.LOGGING)
    logging.captureWarnings(True)
    manager = logging.root.manager
    for logger in manager.loggerDict.values():
        if isinstance(logger, logging.Logger):
            logger.handlers.clear()
            logger.disabled = False
            logger.propagate = True


def main() -> None:
    configure_logging()
    configure_checkpoint()
    from fragile.app import app

    app()


if __name__ == "__main__":
    main()

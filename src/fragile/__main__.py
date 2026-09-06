import logging
from logging.config import dictConfig

from fragile.conf import settings


def configure_checkpoint() -> None:
    import fragile.commands.purge as purge_module
    import fragile.models.base as base_module
    import tomorrow.conf
    from tomorrow.models.constants import CheckpointType

    tomorrow.conf.settings.CHECKPOINT.type = CheckpointType.SQLITE
    tomorrow.conf.settings.CHECKPOINT.sqlite.path = settings.DATABASE_FILE
    base_module.engine = base_module.get_engine()
    purge_module.engine = base_module.engine


def configure_logging() -> None:
    dictConfig(settings.LOGGING)
    logging.captureWarnings(True)
    manager = logging.root.manager
    for logger_name, logger in manager.loggerDict.items():
        if isinstance(logger, logging.Logger):
            if logger_name == "tomorrow.llm":
                continue
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

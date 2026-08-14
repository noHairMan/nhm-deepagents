import logging
import os
from pathlib import Path
from typing import ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class FragileSettings(BaseSettings):
    APP: str = "fragile"
    AGENT: str = "tomorrow.core.agent.AgentManager.create_agent"
    BASE_DIR: ClassVar[Path] = Path(__file__).resolve().parent.parent
    INTERRUPT_EXIT_THRESHOLD: float = Field(default=0.5, gt=0)
    LOG_LEVEL: int = logging.INFO
    LOG_ROOT: ClassVar[Path] = Path(__file__).resolve().parent.parent.parent / "logs"
    LOGGING: ClassVar[dict] = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "verbose": {
                "format": "[%(levelname)s] %(asctime)s.%(msecs).3d %(filename)s(%(lineno)s) > "
                "%(funcName)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "fragile": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(LOG_ROOT, "fragile.log"),
                "formatter": "verbose",
                "maxBytes": 100 * 1024 * 1024,
                "backupCount": 5,
            },
        },
        "root": {
            "handlers": ["fragile"],
            "level": logging.INFO,
        },
        "loggers": {
            "fragile": {"handlers": [], "level": logging.INFO, "propagate": True},
        },
    }
    ENABLED_COMMANDS: tuple[str, ...] = (
        "fragile.commands.interactive.commands.quit.QuitCommand",
        "fragile.commands.interactive.commands.new.NewCommand",
        "fragile.commands.interactive.commands.history.HistoryCommand",
        "fragile.commands.interactive.commands.account.AccountCommand",
    )

    model_config = SettingsConfigDict(
        env_prefix="FRAGILE_",
        env_nested_delimiter="__",
        extra="ignore",
        env_file=os.environ.get("FRAGILE_ENV_FILE", ".env"),
    )

    def __init__(self, **values):
        super().__init__(**values)
        os.makedirs(self.LOG_ROOT, exist_ok=True)

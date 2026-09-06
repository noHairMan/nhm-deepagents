import copy
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
    DATA_ROOT: Path = Field(default_factory=lambda: Path.home() / ".fragile")
    DATABASE_FILE: Path = Path("fragile.db")
    INPUT_HISTORY_FILE: Path = Path(".fragile_history")
    INPUT_HISTORY_LIMIT: int = Field(default=100, gt=0)
    INTERRUPT_EXIT_THRESHOLD: float = Field(default=0.5, gt=0)
    LOG_LEVEL: int = logging.INFO
    LOG_ROOT: Path = Path("logs")
    _LOGGING: ClassVar[dict] = {
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
                "formatter": "verbose",
                "encoding": "utf-8",
                "maxBytes": 100 * 1024 * 1024,
                "backupCount": 5,
            },
            "llm": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "verbose",
                "encoding": "utf-8",
                "maxBytes": 100 * 1024 * 1024,
                "backupCount": 5,
                "level": logging.DEBUG,
            },
        },
        "root": {
            "handlers": ["fragile"],
            "level": logging.INFO,
        },
        "loggers": {
            "fragile": {"handlers": [], "level": logging.INFO, "propagate": True},
            "py.warnings": {"handlers": [], "level": logging.INFO, "propagate": True},
            "tomorrow.llm": {"handlers": ["llm"], "level": logging.DEBUG, "propagate": False},
        },
    }
    ENABLED_COMMANDS: tuple[str, ...] = (
        "fragile.commands.interactive.commands.quit.QuitCommand",
        "fragile.commands.interactive.commands.new.NewCommand",
        "fragile.commands.interactive.commands.history.HistoryCommand",
        "fragile.commands.interactive.commands.account.AccountCommand",
        "fragile.commands.interactive.commands.model.ModelCommand",
    )

    model_config = SettingsConfigDict(
        env_prefix="FRAGILE_",
        env_nested_delimiter="__",
        extra="ignore",
        env_file=os.environ.get("FRAGILE_ENV_FILE", ".env"),
    )

    @property
    def LOGGING(self) -> dict:
        """Return logging configuration using the configured log level."""
        logging_config = copy.deepcopy(self._LOGGING)
        logging_config["handlers"]["fragile"]["filename"] = str(self.LOG_ROOT / "fragile.log")
        logging_config["handlers"]["llm"]["filename"] = str(self.LOG_ROOT / "llm.log")
        logging_config["handlers"]["fragile"]["level"] = self.LOG_LEVEL
        logging_config["root"]["level"] = self.LOG_LEVEL
        for logger_config in logging_config["loggers"].values():
            logger_config["level"] = self.LOG_LEVEL
        logging_config["handlers"]["llm"]["level"] = logging.DEBUG
        logging_config["loggers"]["tomorrow.llm"]["level"] = logging.DEBUG
        return logging_config

    def model_post_init(self, __context: object) -> None:
        if "DATABASE_FILE" not in self.model_fields_set:
            self.DATABASE_FILE = self.DATA_ROOT / "fragile.db"
        if "INPUT_HISTORY_FILE" not in self.model_fields_set:
            self.INPUT_HISTORY_FILE = self.DATA_ROOT / ".fragile_history"
        if "LOG_ROOT" not in self.model_fields_set:
            self.LOG_ROOT = self.DATA_ROOT / "logs"

        self.DATA_ROOT.mkdir(parents=True, exist_ok=True)
        self.DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.INPUT_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.LOG_ROOT.mkdir(parents=True, exist_ok=True)

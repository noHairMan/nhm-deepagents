import logging
import os
from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfigModel(BaseModel):
    def get(self, key, default=None):
        return self.model_dump(by_alias=True).get(key, default)

    def __getitem__(self, key):
        return self.model_dump(by_alias=True)[key]


class RainySettings(BaseSettings):
    APP: str = "rainy"
    BASE_DIR: ClassVar[Path] = Path(__file__).resolve().parent.parent

    HOST: str = "localhost"
    PORT: int = 8000

    MIDDLEWARE: list[str] = Field(
        default_factory=lambda: [
            "rainy.middleware.unify_response_format",
            "rainy.middleware.add_process_time_header",
        ]
    )

    UNIFY_RESPONSE_FORMAT_EXCLUDE: list[str] = Field(default_factory=lambda: ["/docs", "/redoc", "/openapi.json"])

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
            "simple": {
                "format": "[%(levelname)s] %(asctime)s.%(msecs).3d: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "console": {
                "format": "[%(levelname)s] %(asctime)s.%(msecs).3d %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console",
                "filters": [],
            },
            "root": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(LOG_ROOT, "root.log"),
                "formatter": "verbose",
                "maxBytes": 100 * 1024 * 1024,
                "backupCount": 5,
            },
        },
        "root": {
            "handlers": ["console", "root"],
            "level": logging.INFO,
        },
        "loggers": {
            "rainy": {"handlers": [], "level": logging.INFO, "propagate": True},
            "uvicorn": {"handlers": [], "level": logging.INFO, "propagate": True},
            "starlette": {"handlers": [], "level": logging.INFO, "propagate": True},
        },
    }

    model_config = SettingsConfigDict(
        env_prefix="RAINY_",
        env_nested_delimiter="__",
        extra="ignore",
        env_file=os.environ.get("RAINY_ENV_FILE", ".env"),
    )

    def __init__(self, **values):
        super().__init__(**values)
        os.makedirs(self.LOG_ROOT, exist_ok=True)

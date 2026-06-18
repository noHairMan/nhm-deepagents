import logging
import os
from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfigModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    def get(self, key, default=None):
        return self.model_dump(by_alias=True).get(key, default)

    def __getitem__(self, key):
        return self.model_dump(by_alias=True)[key]


class FormatterConfig(BaseConfigModel):
    format: str = "[%(levelname)s] %(asctime)s.%(msecs).3d %(name)s: %(message)s"
    datefmt: str = "%Y-%m-%d %H:%M:%S"


class HandlerConfig(BaseConfigModel):
    class_: str = Field(..., alias="class")
    formatter: str
    filters: list = Field(default_factory=list)
    filename: str | None = None
    maxBytes: int | None = None
    backupCount: int | None = None


class RootLoggerConfig(BaseConfigModel):
    handlers: list[str]
    level: int = logging.INFO


class LoggerConfig(BaseConfigModel):
    handlers: list[str] = Field(default_factory=list)
    level: int = logging.INFO
    propagate: bool = True


class LoggingConfig(BaseConfigModel):
    version: int = 1
    disable_existing_loggers: bool = True
    formatters: dict[str, FormatterConfig] = Field(
        default_factory=lambda: {
            "verbose": FormatterConfig(
                format="[%(levelname)s] %(asctime)s.%(msecs).3d %(filename)s(%(lineno)s) > %(funcName)s: %(message)s",
            ),
            "simple": FormatterConfig(format="[%(levelname)s] %(asctime)s.%(msecs).3d: %(message)s"),
            "console": FormatterConfig(),
        }
    )
    handlers: dict[str, HandlerConfig] = Field(
        default_factory=lambda: {
            "console": HandlerConfig(
                class_="logging.StreamHandler",
                formatter="console",
            ),
            "root": HandlerConfig(
                class_="logging.handlers.RotatingFileHandler",
                filename=os.path.join(LoggingConfig.LOG_ROOT, "root.log"),
                formatter="verbose",
                maxBytes=100 * 1024 * 1024,
                backupCount=5,
            ),
        }
    )
    root: RootLoggerConfig = Field(default_factory=lambda: RootLoggerConfig(handlers=["console", "root"]))
    loggers: dict[str, LoggerConfig] = Field(
        default_factory=lambda: {
            "rainy": LoggerConfig(),
            "uvicorn": LoggerConfig(),
            "starlette": LoggerConfig(),
        }
    )
    LOG_ROOT: ClassVar[Path] = Path(__file__).resolve().parent.parent.parent / "logs"


class RainySettings(BaseSettings):
    APP: str = "rainy"
    BASE_DIR: Path = Path(__file__).resolve().parent.parent

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

    LOGGING: LoggingConfig = Field(default_factory=LoggingConfig)

    model_config = SettingsConfigDict(
        env_prefix="RAINY_",
        env_nested_delimiter="__",
        extra="ignore",
        env_file=os.environ.get("RAINY_ENV_FILE", ".env"),
    )

    def __init__(self, **values):
        super().__init__(**values)
        os.makedirs(self.LOGGING.LOG_ROOT, exist_ok=True)

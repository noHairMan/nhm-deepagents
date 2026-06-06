import logging
import os
from pathlib import Path
from typing import Final

APP: Final = "rainy"
BASE_DIR: Final = Path(__file__).resolve().parent.parent

HOST: str = "localhost"
PORT: int = 8000

MIDDLEWARE = [
    "rainy.middleware.unify_response_format",
    "rainy.middleware.add_process_time_header",
]


UNIFY_RESPONSE_FORMAT_EXCLUDE = ["/docs", "/redoc", "/openapi.json"]


LOG_LEVEL = logging.getLevelName(logging.INFO)
LOG_ROOT = BASE_DIR.parent / "logs"
os.makedirs(LOG_ROOT, exist_ok=True)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "format": "[%(levelname)s] %(asctime)s.%(msecs).3d %(filename)s(%(lineno)s) > %(funcName)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {"format": "[%(levelname)s] %(asctime)s.%(msecs).3d: %(message)s", "datefmt": "%Y-%m-%d %H:%M:%S"},
        "console": {
            "format": "[%(levelname)s] %(asctime)s.%(msecs).3d %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
        "root": {
            "class": "logging.handlers.RotatingFileHandler",
            "filters": [],
            "filename": os.path.join(LOG_ROOT, "root.log"),
            "formatter": "verbose",
            "maxBytes": 100 * 1024 * 1024,
            "backupCount": 5,
        },
    },
    "root": {
        "handlers": ["console", "root"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        APP.lower(): {
            "handlers": [],
            "level": LOG_LEVEL,
            "propagate": True,
        },
        "uvicorn": {
            "handlers": [],
            "level": LOG_LEVEL,
            "propagate": True,
        },
        "starlette": {
            "handlers": [],
            "level": LOG_LEVEL,
            "propagate": True,
        },
    },
}

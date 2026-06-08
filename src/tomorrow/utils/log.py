from logging import Logger, getLogger
from typing import Optional

from tomorrow.conf import settings


def get_logger(name: Optional[str] = None) -> Logger:
    return getLogger(name or __name__)


logger = get_logger(settings.APP.lower())

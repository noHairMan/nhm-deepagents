from logging import Logger, getLogger
from typing import Optional

from fragile.conf import settings


def get_logger(name: Optional[str] = None) -> Logger:
    return getLogger(name or settings.APP.lower())


logger = get_logger()

import logging

from tomorrow.conf import settings
from tomorrow.utils.log import get_logger
from tomorrow.utils.log import logger as default_logger


class TestLog:
    def test_get_logger_named(self):
        logger = get_logger("test_name")
        assert logger.name == "test_name"
        assert isinstance(logger, logging.Logger)

    def test_get_logger_default(self):
        logger = get_logger()
        assert logger.name == "tomorrow.utils.log"

    def test_default_logger(self):
        assert default_logger.name == settings.APP.lower()

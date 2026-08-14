from fragile.utils.log import get_logger, logger


class TestLog:
    def test_default_logger_name(self) -> None:
        assert logger.name == "fragile"
        assert get_logger().name == "fragile"

    def test_custom_logger_name(self) -> None:
        assert get_logger("custom").name == "custom"

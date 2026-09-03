import logging
from pathlib import Path

from rainy.settings import RainySettings


class TestRainySettings:
    def test_rainy_settings(self):
        import os
        from unittest.mock import patch

        with patch.dict(os.environ, {"RAINY_HOST": "0.0.0.0"}):
            settings = RainySettings(_env_file="/non/existent/path")
        assert settings.APP == "rainy"
        assert settings.HOST == "0.0.0.0"
        assert settings.PORT == 8000
        assert "rainy.middleware.unify_response_format" in settings.MIDDLEWARE
        assert "/docs" in settings.UNIFY_RESPONSE_FORMAT_EXCLUDE

    def test_logging_config(self):
        logging_config = RainySettings.LOGGING
        assert "console" in logging_config["handlers"]
        assert "root" in logging_config["handlers"]
        assert "llm" in logging_config["handlers"]
        assert logging_config["handlers"]["root"]["encoding"] == "utf-8"
        assert Path(logging_config["handlers"]["llm"]["filename"]).name == "llm.log"
        assert logging_config["handlers"]["llm"]["class"] == "logging.handlers.RotatingFileHandler"
        assert logging_config["handlers"]["llm"]["encoding"] == "utf-8"
        assert logging_config["handlers"]["llm"]["level"] == logging.DEBUG
        assert "rainy" in logging_config["loggers"]
        assert logging_config["loggers"]["tomorrow.llm"] == {
            "handlers": ["llm"],
            "level": logging.DEBUG,
            "propagate": False,
        }

    def test_base_config_model(self):
        from rainy.settings import BaseConfigModel

        class TestConfig(BaseConfigModel):
            key: str = "value"

        config = TestConfig()
        assert config.get("key") == "value"
        assert config.get("missing", "default") == "default"
        assert config["key"] == "value"

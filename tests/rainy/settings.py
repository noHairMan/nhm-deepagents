from rainy.settings import RainySettings


class TestRainySettings:
    def test_rainy_settings(self):
        settings = RainySettings()
        assert settings.APP == "rainy"
        assert settings.HOST == "0.0.0.0"
        assert settings.PORT == 8000
        assert "rainy.middleware.unify_response_format" in settings.MIDDLEWARE
        assert "/docs" in settings.UNIFY_RESPONSE_FORMAT_EXCLUDE

    def test_logging_config(self):
        logging_config = RainySettings.LOGGING
        assert "console" in logging_config["handlers"]
        assert "root" in logging_config["handlers"]
        assert "rainy" in logging_config["loggers"]

    def test_base_config_model(self):
        from rainy.settings import BaseConfigModel

        class TestConfig(BaseConfigModel):
            key: str = "value"

        config = TestConfig()
        assert config.get("key") == "value"
        assert config.get("missing", "default") == "default"
        assert config["key"] == "value"

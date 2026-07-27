from fragile.settings import FragileSettings


class TestFragileSettings:
    def test_fragile_settings(self, monkeypatch):
        monkeypatch.setenv("FRAGILE_APP", "custom-fragile")

        settings = FragileSettings(_env_file="/non/existent/path")

        assert settings.APP == "custom-fragile"
        assert settings.BASE_DIR.name == "src"

    def test_default_settings(self):
        settings = FragileSettings(_env_file="/non/existent/path")

        assert settings.APP == "fragile"
        assert settings.ENABLED_COMMANDS == (
            "fragile.commands.interactive.commands.quit.QuitCommand",
            "fragile.commands.interactive.commands.new.NewCommand",
            "fragile.commands.interactive.commands.history.HistoryCommand",
        )

    def test_base_config_model(self):
        from fragile.settings import BaseConfigModel

        class TestConfig(BaseConfigModel):
            key: str = "value"

        config = TestConfig()
        assert config.get("key") == "value"
        assert config.get("missing", "default") == "default"
        assert config["key"] == "value"

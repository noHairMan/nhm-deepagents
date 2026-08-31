from pathlib import Path

from fragile.settings import FragileSettings
from tomorrow.models.constants import ModelType


class TestFragileSettings:
    def test_fragile_settings(self, monkeypatch):
        monkeypatch.setenv("FRAGILE_APP", "custom-fragile")

        settings = FragileSettings(_env_file="/non/existent/path")

        assert settings.APP == "custom-fragile"
        assert settings.BASE_DIR.name == "src"

    def test_default_settings(self):
        settings = FragileSettings(_env_file="/non/existent/path")

        assert settings.APP == "fragile"
        assert settings.AGENT == "tomorrow.core.agent.AgentManager.create_agent"
        assert settings.LOG_LEVEL == 20
        assert settings.LOG_ROOT.name == "logs"
        log_filename = Path(settings.LOGGING["handlers"]["fragile"]["filename"])
        assert log_filename.name == "fragile.log"
        assert log_filename.parent.name == "logs"
        assert settings.LOGGING["handlers"]["fragile"]["class"] == "logging.handlers.RotatingFileHandler"
        assert settings.LOGGING["handlers"]["fragile"]["level"] == settings.LOG_LEVEL
        assert "console" not in settings.LOGGING["handlers"]
        assert settings.LOGGING["root"]["handlers"] == ["fragile"]
        assert settings.LOGGING["root"]["level"] == settings.LOG_LEVEL
        assert settings.LOGGING["loggers"]["py.warnings"]["propagate"]
        assert settings.ENABLED_COMMANDS == (
            "fragile.commands.interactive.commands.quit.QuitCommand",
            "fragile.commands.interactive.commands.new.NewCommand",
            "fragile.commands.interactive.commands.history.HistoryCommand",
            "fragile.commands.interactive.commands.account.AccountCommand",
            "fragile.commands.interactive.commands.model.ModelCommand",
        )
        assert settings.MODEL_CATALOG[ModelType.ANTHROPIC] == (
            "claude-sonnet-5",
            "claude-haiku-4-5",
            "glm-5.3-flash",
        )

    def test_agent_setting(self, monkeypatch):
        monkeypatch.setenv("FRAGILE_AGENT", "custom.module.create_agent")

        settings = FragileSettings(_env_file="/non/existent/path")

        assert settings.AGENT == "custom.module.create_agent"

    def test_log_level_setting(self, monkeypatch):
        monkeypatch.setenv("FRAGILE_LOG_LEVEL", "10")

        settings = FragileSettings(_env_file="/non/existent/path")

        assert settings.LOG_LEVEL == 10
        assert settings.LOGGING["root"]["level"] == 10
        assert settings.LOGGING["handlers"]["fragile"]["level"] == 10

import logging
from pathlib import Path

from fragile.settings import FragileSettings


class TestFragileSettings:
    def test_fragile_settings(self, monkeypatch):
        monkeypatch.setenv("FRAGILE_APP", "custom-fragile")

        settings = FragileSettings(_env_file="/non/existent/path")

        assert settings.APP == "custom-fragile"
        assert settings.BASE_DIR.name == "src"

    def test_default_settings(self, monkeypatch, tmp_path):
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        settings = FragileSettings(_env_file="/non/existent/path")

        assert settings.APP == "fragile"
        assert settings.AGENT == "tomorrow.core.agent.AgentManager.create_agent"
        assert tmp_path / ".fragile" == settings.DATA_ROOT
        assert settings.DATABASE_FILE == settings.DATA_ROOT / "fragile.db"
        assert settings.INPUT_HISTORY_FILE == settings.DATA_ROOT / ".fragile_history"
        assert settings.INPUT_HISTORY_LIMIT == 100
        assert settings.LOG_LEVEL == 20
        assert settings.LOG_ROOT == settings.DATA_ROOT / "logs"
        assert settings.DATA_ROOT.is_dir()
        assert settings.LOG_ROOT.is_dir()
        log_filename = Path(settings.LOGGING["handlers"]["fragile"]["filename"])
        assert log_filename == settings.LOG_ROOT / "fragile.log"
        assert settings.LOGGING["handlers"]["fragile"]["class"] == "logging.handlers.RotatingFileHandler"
        assert settings.LOGGING["handlers"]["fragile"]["encoding"] == "utf-8"
        assert settings.LOGGING["handlers"]["fragile"]["level"] == settings.LOG_LEVEL
        llm_logging = settings.LOGGING["handlers"]["llm"]
        assert Path(llm_logging["filename"]) == settings.LOG_ROOT / "llm.log"
        assert llm_logging["class"] == "logging.handlers.RotatingFileHandler"
        assert llm_logging["encoding"] == "utf-8"
        assert llm_logging["level"] == logging.DEBUG
        assert settings.LOGGING["loggers"]["tomorrow.llm"] == {
            "handlers": ["llm"],
            "level": logging.DEBUG,
            "propagate": False,
        }
        assert "console" not in settings.LOGGING["handlers"]
        assert settings.LOGGING["root"]["handlers"] == ["fragile"]
        assert settings.LOGGING["root"]["level"] == settings.LOG_LEVEL
        assert settings.LOGGING["loggers"]["py.warnings"]["propagate"]
        assert not hasattr(settings, "MODEL_CATALOG")
        assert settings.ENABLED_COMMANDS == (
            "fragile.commands.interactive.commands.quit.QuitCommand",
            "fragile.commands.interactive.commands.new.NewCommand",
            "fragile.commands.interactive.commands.history.HistoryCommand",
            "fragile.commands.interactive.commands.account.AccountCommand",
            "fragile.commands.interactive.commands.model.ModelCommand",
        )

    def test_data_root_setting_derives_runtime_paths(self, monkeypatch, tmp_path):
        data_root = tmp_path / "nested" / "fragile-data"
        monkeypatch.setenv("FRAGILE_DATA_ROOT", str(data_root))

        settings = FragileSettings(_env_file="/non/existent/path")

        assert data_root == settings.DATA_ROOT
        assert data_root / "fragile.db" == settings.DATABASE_FILE
        assert data_root / ".fragile_history" == settings.INPUT_HISTORY_FILE
        assert data_root / "logs" == settings.LOG_ROOT
        assert data_root.is_dir()
        assert settings.LOG_ROOT.is_dir()

    def test_derived_paths_can_be_overridden(self, monkeypatch, tmp_path):
        database_file = tmp_path / "database" / "custom.db"
        history_file = tmp_path / "history" / "custom-history"
        log_root = tmp_path / "custom-logs"
        monkeypatch.setenv("FRAGILE_DATABASE_FILE", str(database_file))
        monkeypatch.setenv("FRAGILE_INPUT_HISTORY_FILE", str(history_file))
        monkeypatch.setenv("FRAGILE_LOG_ROOT", str(log_root))

        settings = FragileSettings(_env_file="/non/existent/path")

        assert database_file == settings.DATABASE_FILE
        assert history_file == settings.INPUT_HISTORY_FILE
        assert log_root == settings.LOG_ROOT
        assert database_file.parent.is_dir()
        assert history_file.parent.is_dir()
        assert log_root.is_dir()
        assert Path(settings.LOGGING["handlers"]["fragile"]["filename"]) == log_root / "fragile.log"

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
        assert settings.LOGGING["handlers"]["llm"]["level"] == logging.DEBUG
        assert settings.LOGGING["loggers"]["tomorrow.llm"]["level"] == logging.DEBUG

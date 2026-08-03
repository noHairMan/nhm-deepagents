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
        assert settings.AGENT == "tomorrow.core.agent.AgentManager.create_agent"
        assert settings.ENABLED_COMMANDS == (
            "fragile.commands.interactive.commands.quit.QuitCommand",
            "fragile.commands.interactive.commands.new.NewCommand",
            "fragile.commands.interactive.commands.history.HistoryCommand",
            "fragile.commands.interactive.commands.account.AccountCommand",
        )

    def test_agent_setting(self, monkeypatch):
        monkeypatch.setenv("FRAGILE_AGENT", "custom.module.create_agent")

        settings = FragileSettings(_env_file="/non/existent/path")

        assert settings.AGENT == "custom.module.create_agent"

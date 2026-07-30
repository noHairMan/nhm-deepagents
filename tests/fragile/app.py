from unittest.mock import AsyncMock, patch

from typer.testing import CliRunner

from fragile.app import app

runner = CliRunner()


class TestCli:
    def test_help(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "interactive" not in result.stdout

    def testprompt_argument_is_rejected(self) -> None:
        result = runner.invoke(app, ["你好"])
        assert result.exit_code != 0

    def test_invalid_thread(self) -> None:
        result = runner.invoke(app, ["--thread", "bad"])
        assert result.exit_code != 0

    def test_main_without_prompt(self) -> None:
        from fragile.app import main

        with patch("fragile.app.interactive", return_value=object()) as interactive:
            main(None, None)
        interactive.assert_called_once_with(None)

    def test_main_runs_async_interactive_session(self) -> None:
        from fragile.app import main

        with patch("fragile.app.interactive", new_callable=AsyncMock) as interactive:
            main(None, None)
        interactive.assert_called_once_with(None)

    def test_main_skips_interactive_when_subcommand_is_invoked(self) -> None:
        from fragile.app import main

        context = type("Context", (), {"invoked_subcommand": "purge"})()
        with patch("fragile.app.interactive") as interactive:
            main(context, None)
        interactive.assert_not_called()

    def test_main_starts_interactive_without_subcommand(self) -> None:
        from fragile.app import main

        context = type("Context", (), {"invoked_subcommand": None})()
        with (
            patch("fragile.app.interactive", return_value=object()) as interactive,
            patch("fragile.app.inspect.isawaitable", return_value=False),
        ):
            main(context, "thread-id")
        interactive.assert_called_once_with("thread-id")

    def test_purge_command(self) -> None:
        with patch("fragile.app.purge_sessions", return_value=3) as purge_sessions:
            result = runner.invoke(app, ["purge"])
        assert result.exit_code == 0
        assert result.stdout == "Cleared 3 session records.\n"
        purge_sessions.assert_called_once_with()

from unittest.mock import patch

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

        with patch("fragile.app.interactive") as interactive:
            main(None)
        interactive.assert_called_once_with(None)

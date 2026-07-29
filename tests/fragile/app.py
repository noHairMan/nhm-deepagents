from unittest.mock import patch

from typer.testing import CliRunner

from fragile.app import app
from tomorrow.conf import settings
from tomorrow.models.constants import CheckpointType

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

    def test_main_withoutprompt(self) -> None:
        from fragile.app import main

        with patch("fragile.app.interactive") as interactive:
            main(None)
        interactive.assert_called_once_with(None)
        assert settings.CHECKPOINT.type == CheckpointType.SQLITE

    def test_sqlite_checkpoint_path_is_current_directory(self, tmp_path, monkeypatch) -> None:
        from fragile.app import configure_checkpoint

        monkeypatch.chdir(tmp_path)
        configure_checkpoint()
        assert settings.CHECKPOINT.type == CheckpointType.SQLITE
        assert settings.CHECKPOINT.sqlite.path == tmp_path / "fragile.db"

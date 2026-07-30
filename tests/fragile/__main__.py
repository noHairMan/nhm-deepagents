import runpy
from pathlib import Path
from unittest.mock import patch

from fragile.__main__ import configure_checkpoint, main
from tomorrow.conf import settings
from tomorrow.models.constants import CheckpointType


class TestMain:
    def test_module_entrypoint_calls_main(self) -> None:
        with patch("fragile.app.app"):
            runpy.run_path(str(Path(__file__).parents[2] / "src/fragile/__main__.py"), run_name="__main__")

    def test_sqlite_checkpoint_path_is_current_directory(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        configure_checkpoint()
        assert settings.CHECKPOINT.type == CheckpointType.SQLITE
        assert settings.CHECKPOINT.sqlite.path == tmp_path / "fragile.db"

    def test_main_configures_checkpoint_before_starting_app(self) -> None:
        with patch("fragile.__main__.configure_checkpoint") as configure, patch("fragile.__main__.app") as run_app:
            main()

        configure.assert_called_once_with()
        run_app.assert_called_once_with()

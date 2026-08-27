import logging
import runpy
from pathlib import Path
from unittest.mock import patch

from fragile.__main__ import configure_checkpoint, configure_logging, main
from fragile.conf import settings as fragile_settings
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

    def test_configure_checkpoint_rebinds_fragile_database_engine(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        with patch("fragile.models.base.get_engine") as get_engine:
            configure_checkpoint()

        get_engine.assert_called_once_with()

    def test_configure_logging_uses_fragile_settings(self) -> None:
        with (
            patch("fragile.__main__.dictConfig") as configure,
            patch("fragile.__main__.logging.captureWarnings") as capture_warnings,
        ):
            configure_logging()

        configure.assert_called_once_with(fragile_settings.LOGGING)
        capture_warnings.assert_called_once_with(True)

    def test_configure_logging_removes_existing_logger_handlers(self) -> None:
        third_party_logger = logging.getLogger("third_party.test")
        handler = logging.StreamHandler()
        third_party_logger.addHandler(handler)
        try:
            with patch("fragile.__main__.dictConfig"):
                configure_logging()
            assert third_party_logger.handlers == []
            assert third_party_logger.propagate
            assert not third_party_logger.disabled
        finally:
            third_party_logger.handlers.clear()

    def test_main_configures_checkpoint_before_starting_app(self) -> None:
        with (
            patch("fragile.__main__.configure_logging") as configure_logging,
            patch("fragile.__main__.configure_checkpoint") as configure,
            patch("fragile.app.app") as run_app,
        ):
            main()

        configure_logging.assert_called_once_with()
        configure.assert_called_once_with()
        run_app.assert_called_once_with()

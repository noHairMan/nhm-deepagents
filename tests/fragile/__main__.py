import logging
import runpy
from pathlib import Path
from unittest.mock import Mock, patch

import fragile.commands.purge as purge_module
import fragile.models.base as base_module
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
        database_file = tmp_path / "fragile-data" / "fragile.db"
        monkeypatch.setattr(fragile_settings, "DATABASE_FILE", database_file)
        store_path = settings.STORE.sqlite.path
        filesystem_root = settings.BACKEND.filesystem.root_dir
        local_shell_root = settings.BACKEND.local_shell.root_dir

        configure_checkpoint()

        assert settings.CHECKPOINT.type == CheckpointType.SQLITE
        assert settings.CHECKPOINT.sqlite.path == database_file
        assert settings.STORE.sqlite.path == store_path
        assert settings.BACKEND.filesystem.root_dir == filesystem_root
        assert settings.BACKEND.local_shell.root_dir == local_shell_root

    def test_configure_checkpoint_rebinds_fragile_database_engine(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(base_module, "engine", base_module.engine)
        monkeypatch.setattr(purge_module, "engine", purge_module.engine)
        engine = Mock()
        with patch("fragile.models.base.get_engine") as get_engine:
            get_engine.return_value = engine
            configure_checkpoint()

        get_engine.assert_called_once_with()
        assert base_module.engine is engine
        assert purge_module.engine is engine

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

    def test_configure_logging_preserves_llm_logger(self) -> None:
        llm_logger = logging.getLogger("tomorrow.llm")
        handler = logging.StreamHandler()
        llm_logger.addHandler(handler)
        llm_logger.propagate = False
        try:
            with patch("fragile.__main__.dictConfig"):
                configure_logging()
            assert handler in llm_logger.handlers
            assert not llm_logger.propagate
        finally:
            llm_logger.removeHandler(handler)

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

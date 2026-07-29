from fragile.__main__ import configure_checkpoint
from tomorrow.conf import settings
from tomorrow.models.constants import CheckpointType


class TestMain:
    def test_sqlite_checkpoint_path_is_current_directory(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        configure_checkpoint()
        assert settings.CHECKPOINT.type == CheckpointType.SQLITE
        assert settings.CHECKPOINT.sqlite.path == tmp_path / "fragile.db"

from tomorrow.models.constants.backend import BackendType
from tomorrow.models.constants.checkpoint import CheckpointType


class TestConstants:
    def test_checkpoint_type(self):
        assert CheckpointType.MEMORY == "memory"
        assert CheckpointType.MEMORY.label == "Memory"
        assert CheckpointType.SQLITE == "sqlite"
        assert CheckpointType.SQLITE.label == "SQLite"
        assert CheckpointType.POSTGRES == "postgres"
        assert CheckpointType.POSTGRES.label == "PostgreSQL"
        assert CheckpointType.REDIS == "redis"
        assert CheckpointType.REDIS.label == "Redis"
        assert CheckpointType.MONGODB == "mongodb"
        assert CheckpointType.MONGODB.label == "MongoDB"
        assert "memory" in CheckpointType
        assert "sqlite" in CheckpointType
        assert "postgres" in CheckpointType
        assert "redis" in CheckpointType
        assert "mongodb" in CheckpointType

    def test_backend_type(self):
        assert BackendType.FILESYSTEM == "filesystem"
        assert BackendType.FILESYSTEM.label == "Filesystem"
        assert BackendType.DAYTONA == "daytona"
        assert BackendType.DAYTONA.label == "Daytona"
        assert "filesystem" in BackendType
        assert "daytona" in BackendType

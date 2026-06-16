from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from tomorrow.conf import settings
from tomorrow.models.constants import CheckpointType


async def get_checkpoint_saver() -> AsyncSqliteSaver:
    checkpoint_config = settings.CHECKPOINT.get(CheckpointType.SQLITE, {})
    path = checkpoint_config.get("path")
    if not path:
        raise ValueError("path is required for SQLite checkpoint")
    return AsyncSqliteSaver.from_conn_string(path)

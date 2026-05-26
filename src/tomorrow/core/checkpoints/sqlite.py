from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from tomorrow.conf import settings


async def get_checkpoint_saver():
    path = settings.CHECKPOINT["options"]["path"]
    return AsyncSqliteSaver.from_conn_string(path)

import contextlib

from tomorrow.conf import settings
from tomorrow.models.constants import CheckpointType


@contextlib.asynccontextmanager
async def get_checkpointer_context():
    checkpoint_type = settings.CHECKPOINT["type"]
    if checkpoint_type == CheckpointType.SQLITE:
        from .sqlite import get_checkpoint_saver as get_sqlite_saver

        async with await get_sqlite_saver() as saver:
            yield saver
    elif checkpoint_type == CheckpointType.MEMORY:
        from .memory import get_checkpoint_saver as get_memory_saver

        yield get_memory_saver()
    else:
        # 不使用检查点。不保存任何对话session
        yield None

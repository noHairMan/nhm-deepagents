import contextlib
from typing import AsyncGenerator, Optional

from langgraph.checkpoint.base import BaseCheckpointSaver

from tomorrow.conf import settings
from tomorrow.models.constants import CheckpointType


@contextlib.asynccontextmanager
async def get_checkpointer_context() -> AsyncGenerator[Optional[BaseCheckpointSaver], None]:
    checkpoint_type = settings.CHECKPOINT["type"]
    match checkpoint_type:
        case CheckpointType.SQLITE:
            from .sqlite import get_checkpoint_saver as get_sqlite_saver

            async with await get_sqlite_saver() as saver:
                yield saver
        case CheckpointType.MEMORY:
            from .memory import get_checkpoint_saver as get_memory_saver

            yield get_memory_saver()
        case _:
            # 不使用检查点。不保存任何对话session
            yield None

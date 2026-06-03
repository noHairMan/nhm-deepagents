from unittest.mock import AsyncMock, patch

import pytest

from tomorrow.core.checkpoints import get_checkpointer_context
from tomorrow.models.constants import CheckpointType


class TestCheckpoints:
    @pytest.mark.asyncio
    async def test_get_checkpointer_context_memory(self):
        with patch("tomorrow.conf.settings.CHECKPOINT", {"type": CheckpointType.MEMORY}):
            async with get_checkpointer_context() as saver:
                from langgraph.checkpoint.memory import InMemorySaver

                assert isinstance(saver, InMemorySaver)

    @pytest.mark.asyncio
    async def test_get_checkpointer_context_sqlite(self):
        mock_saver = AsyncMock()
        # 使用 AsyncMock 模拟上下文管理器
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_saver

        with patch(
            "tomorrow.conf.settings.CHECKPOINT",
            {"type": CheckpointType.SQLITE, "options": {"path": ":memory:"}},
        ):
            with patch("tomorrow.core.checkpoints.sqlite.get_checkpoint_saver", return_value=mock_context):
                async with get_checkpointer_context() as saver:
                    assert saver == mock_saver

    @pytest.mark.asyncio
    async def test_get_checkpointer_context_none(self):
        with patch("tomorrow.conf.settings.CHECKPOINT", {"type": "UNKNOWN"}):
            async with get_checkpointer_context() as saver:
                assert saver is None


class TestSqliteCheckpoint:
    @pytest.mark.asyncio
    async def test_get_checkpoint_saver_sqlite(self):
        with patch("tomorrow.conf.settings.CHECKPOINT", {"options": {"path": "test.db"}}):
            with patch("langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver.from_conn_string") as mock_from_conn:
                from tomorrow.core.checkpoints.sqlite import get_checkpoint_saver

                await get_checkpoint_saver()
                mock_from_conn.assert_called_once_with("test.db")

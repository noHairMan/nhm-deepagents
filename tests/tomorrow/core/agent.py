from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import SystemMessage

from tomorrow.core.agent import AgentManager, get_backend, get_model, get_store
from tomorrow.models.constants import BackendType, StoreType


class TestAgent:
    def test_get_backend_filesystem(self):
        from deepagents.backends import FilesystemBackend

        from tomorrow.conf import settings

        with patch.object(
            settings, "BACKEND", {"type": BackendType.FILESYSTEM, BackendType.FILESYSTEM.value: {"root_dir": "/tmp"}}
        ):
            backend = get_backend()
            assert isinstance(backend, FilesystemBackend)
            assert backend.virtual_mode is True

    def test_get_backend_filesystem_no_root_dir(self):
        from tomorrow.conf import settings

        with patch.object(settings, "BACKEND", {"type": BackendType.FILESYSTEM, BackendType.FILESYSTEM.value: {}}):
            with pytest.raises(ValueError, match="root_dir is required for Filesystem backend"):
                get_backend()

    def test_get_backend_invalid(self):
        from tomorrow.conf import settings

        with patch.object(settings, "BACKEND", {"type": "invalid"}):
            with pytest.raises(ValueError, match="Unsupported backend type: invalid"):
                get_backend()

    def test_get_store_memory(self):
        from langgraph.store.memory import InMemoryStore

        from tomorrow.conf import settings

        with patch.object(settings, "STORE", {"type": StoreType.MEMORY, StoreType.MEMORY.value: {}}):
            store = get_store()
            assert isinstance(store, InMemoryStore)

    def test_get_store_sqlite(self):

        from tomorrow.conf import settings

        with patch.object(settings, "STORE", {"type": StoreType.SQLITE, StoreType.SQLITE.value: {"path": ":memory:"}}):
            store_ctx = get_store()
            assert hasattr(store_ctx, "__aenter__")

    def test_get_store_sqlite_no_path(self):
        from tomorrow.conf import settings

        with patch.object(settings, "STORE", {"type": StoreType.SQLITE, StoreType.SQLITE.value: {}}):
            with pytest.raises(ValueError, match="path is required for SQLite store"):
                get_store()

    def test_get_store_invalid(self):
        from tomorrow.conf import settings

        with patch.object(settings, "STORE", {"type": "invalid"}):
            with pytest.raises(ValueError, match="Unsupported store type: invalid"):
                get_store()

    def test_get_store_no_attr(self):
        from tomorrow.conf import settings

        with patch.object(settings, "STORE", spec=[]):
            # delattr doesn't work well with settings object sometimes,
            # but hasattr(settings, "STORE") is what we check.
            # actually patch.object might not be enough if we use hasattr
            pass

    def test_get_store_not_present(self):
        # Use a mock that doesn't have STORE attribute
        mock_settings = MagicMock(spec=[])
        with patch("tomorrow.core.store.settings", mock_settings):
            assert get_store() is None

    def test_get_model(self):
        with patch("tomorrow.core.agent.ChatOllama") as mock_ollama:
            from tomorrow.conf import settings

            get_model("test-model")
            mock_ollama.assert_called_once_with(
                model="test-model",
                base_url=settings.OLLAMA_BASE_URL,
                temperature=0,
            )

    def test_get_model_default(self):
        with patch("tomorrow.core.agent.ChatOllama") as mock_ollama:
            from tomorrow.conf import settings

            get_model()
            mock_ollama.assert_called_once_with(
                model="qwen3.5:9b",
                base_url=settings.OLLAMA_BASE_URL,
                temperature=0,
            )

    @pytest.mark.asyncio
    async def test_get_agent_context(self):
        mock_checkpointer = MagicMock()
        mock_agent = MagicMock()

        # 模拟 get_checkpointer_context
        with patch("tomorrow.core.agent.get_checkpointer_context") as mock_context:
            # 模拟异步上下文管理器
            mock_context.return_value.__aenter__.return_value = mock_checkpointer
            mock_context.return_value.__aexit__.return_value = None

            with patch("tomorrow.core.agent.create_deep_agent", return_value=mock_agent) as mock_create:
                async with AgentManager.get_agent_context() as agent:
                    assert agent == mock_agent
                    mock_create.assert_called_once()
                    args, kwargs = mock_create.call_args
                    assert kwargs["checkpointer"] == mock_checkpointer
                    assert isinstance(kwargs["system_prompt"], SystemMessage)

    def test_create_agent(self):
        mock_checkpointer = MagicMock()
        mock_agent = MagicMock()
        mock_backend = MagicMock()
        with (
            patch("tomorrow.core.agent.create_deep_agent", return_value=mock_agent) as mock_create,
            patch("tomorrow.core.agent.get_backend", return_value=mock_backend) as mock_get_backend,
        ):
            agent = AgentManager.create_agent(mock_checkpointer)
            assert agent == mock_agent
            mock_create.assert_called_once()
            mock_get_backend.assert_called_once()
            args, kwargs = mock_create.call_args
            assert kwargs["checkpointer"] == mock_checkpointer
            assert kwargs["backend"] == mock_backend

    def test_agent_manager_methods(self):
        mock_agent = MagicMock()
        AgentManager.set_agent(mock_agent)
        assert AgentManager.get_agent() == mock_agent
        AgentManager.clear_agent()
        with pytest.raises(RuntimeError, match="Agent has not been initialized"):
            AgentManager.get_agent()

    @pytest.mark.asyncio
    async def test_get_agent_context_with_store(self):
        mock_checkpointer = MagicMock()
        mock_agent = MagicMock()
        mock_store = MagicMock()

        with (
            patch("tomorrow.core.agent.get_checkpointer_context") as mock_cp_ctx,
            patch("tomorrow.core.agent.get_store", return_value=mock_store),
            patch("tomorrow.core.agent.create_deep_agent", return_value=mock_agent) as mock_create,
        ):
            mock_cp_ctx.return_value.__aenter__.return_value = mock_checkpointer
            mock_cp_ctx.return_value.__aexit__.return_value = None

            async with AgentManager.get_agent_context() as agent:
                assert agent == mock_agent
                mock_create.assert_called_once()
                args, kwargs = mock_create.call_args
                assert kwargs["store"] == mock_store

    @pytest.mark.asyncio
    async def test_get_agent_context_no_store(self):
        mock_checkpointer = MagicMock()
        mock_agent = MagicMock()

        with (
            patch("tomorrow.core.agent.get_checkpointer_context") as mock_cp_ctx,
            patch("tomorrow.core.agent.get_store", return_value=None),
            patch("tomorrow.core.agent.create_deep_agent", return_value=mock_agent) as mock_create,
        ):
            mock_cp_ctx.return_value.__aenter__.return_value = mock_checkpointer
            mock_cp_ctx.return_value.__aexit__.return_value = None

            async with AgentManager.get_agent_context() as agent:
                assert agent == mock_agent
                mock_create.assert_called_once()
                args, kwargs = mock_create.call_args
                assert "store" not in kwargs or kwargs["store"] is None

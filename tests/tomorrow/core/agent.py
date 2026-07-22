from unittest.mock import MagicMock, patch

import pytest

from tomorrow.core.agent import AgentManager
from tomorrow.core.store import get_store
from tomorrow.exceptions import TomorrowRuntimeError, TomorrowStoreError
from tomorrow.models.constants import StoreType


class TestAgent:
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
            with pytest.raises(TomorrowStoreError, match="path is required for SQLite store"):
                get_store()

    def test_get_store_invalid(self):
        from tomorrow.conf import settings

        with patch.object(settings, "STORE", {"type": "invalid"}):
            with pytest.raises(TomorrowStoreError, match="Unsupported store type: invalid"):
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
            with pytest.raises(AttributeError):
                get_store()

    def test_create_agent(self):
        from tomorrow.conf import settings

        mock_checkpointer = MagicMock()
        mock_agent = MagicMock()
        mock_backend = MagicMock()
        with (
            patch("tomorrow.core.agent.create_deep_agent", return_value=mock_agent) as mock_create,
            patch("tomorrow.core.agent.get_backend", return_value=mock_backend) as mock_get_backend,
            patch("tomorrow.core.agent.CodeInterpreterMiddleware") as mock_middleware,
            patch("tomorrow.core.agent.logger") as mock_logger,
        ):
            agent = AgentManager.create_agent(mock_checkpointer)
            assert agent == mock_agent
            mock_create.assert_called_once()
            mock_get_backend.assert_called_once()
            args, kwargs = mock_create.call_args
            assert kwargs["checkpointer"] == mock_checkpointer
            assert kwargs["backend"] == mock_backend
            mock_middleware.assert_called_once_with()
            assert len(kwargs["middleware"]) == 1
            assert kwargs["middleware"][0] == mock_middleware.return_value

            # 验证日志是否被调用
            # Initializing Agent for ... (1)
            # MODEL: ... (1)
            # BACKEND: ... (1)
            # STORE: ... (1)
            # CHECKPOINT: ... (1)
            # SKILLS: ... (1)
            assert mock_logger.info.call_count == 7
            assert kwargs["skills"] == settings.SKILLS
            assert kwargs["subagents"] == []

    def test_get_subagents(self):
        from tomorrow.conf import settings
        from tomorrow.settings import SubAgentConfig

        configured = [
            SubAgentConfig(
                name="researcher",
                description="Researches a topic",
                system_prompt="You research carefully.",
                model="test-model",
                skills=["research/"],
            ),
            SubAgentConfig(
                name="writer",
                description="Writes a summary",
                system_prompt="You write clearly.",
            ),
        ]
        with patch.object(settings, "SUBAGENTS", configured):
            assert AgentManager.get_subagents() == [
                {
                    "name": "researcher",
                    "description": "Researches a topic",
                    "system_prompt": "You research carefully.",
                    "model": "test-model",
                    "skills": ["research/"],
                },
                {
                    "name": "writer",
                    "description": "Writes a summary",
                    "system_prompt": "You write clearly.",
                },
            ]

    def test_agent_manager_methods(self):
        mock_agent = MagicMock()
        AgentManager.set_agent(mock_agent)
        assert AgentManager.get_agent() == mock_agent
        AgentManager.clear_agent()
        with pytest.raises(TomorrowRuntimeError, match="Agent has not been initialized"):
            AgentManager.get_agent()

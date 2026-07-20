from unittest.mock import MagicMock, patch


class TestGraph:
    def test_graph_is_created_from_agent_manager(self) -> None:
        mock_graph = MagicMock()
        with patch("tomorrow.core.agent.AgentManager.create_agent", return_value=mock_graph):
            import importlib

            module = importlib.import_module("tomorrow.graph")
            assert module.graph is mock_graph
            AgentManager = module.AgentManager
            AgentManager.create_agent.assert_called_once_with(use_store=False)

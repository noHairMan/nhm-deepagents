from langgraph.graph.state import CompiledStateGraph

from tomorrow.core.agent import AgentManager


def get_agent() -> CompiledStateGraph:
    """从 AgentManager 中获取 Agent 的依赖项。"""
    return AgentManager.get_agent()

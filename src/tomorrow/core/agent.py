import contextlib
from typing import Optional

from deepagents import create_deep_agent
from langchain_core.messages import SystemMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph

from tomorrow.core.backend import get_backend
from tomorrow.core.checkpoint import get_checkpointer_context
from tomorrow.core.model import get_model
from tomorrow.core.store import get_store


class AgentManager:
    """Agent 管理器，用于在生命周期内持有 Agent 实例并提供创建方法。"""

    _agent: Optional[CompiledStateGraph] = None

    @classmethod
    def set_agent(cls, agent: CompiledStateGraph) -> None:
        cls._agent = agent

    @classmethod
    def get_agent(cls) -> CompiledStateGraph:
        if cls._agent is None:
            raise RuntimeError("Agent has not been initialized. Ensure lifespan is running.")
        return cls._agent

    @classmethod
    def clear_agent(cls) -> None:
        cls._agent = None

    @staticmethod
    def create_agent(checkpointer: Optional[BaseCheckpointSaver] = None) -> CompiledStateGraph:
        return create_deep_agent(
            model=get_model(),
            memory=[],
            tools=[],
            skills=[],
            system_prompt=SystemMessage(content="""你是一名智能助理，运用你的知识尽可能的回答用户问题。"""),
            checkpointer=checkpointer,
            backend=get_backend(),
            store=get_store(),
        )

    @staticmethod
    @contextlib.asynccontextmanager
    async def get_agent_context():
        async with get_checkpointer_context() as checkpointer:
            yield AgentManager.create_agent(checkpointer)

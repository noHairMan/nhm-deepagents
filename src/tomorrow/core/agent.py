import contextlib
from typing import Any, Optional

from deepagents import create_deep_agent
from langchain_core.messages import SystemMessage

from tomorrow.core.backends import get_backend
from tomorrow.core.checkpoints import get_checkpointer_context
from tomorrow.core.models import get_model
from tomorrow.core.store import get_store


class AgentManager:
    """Agent 管理器，用于在生命周期内持有 Agent 实例并提供创建方法。"""

    _agent: Optional[Any] = None

    @classmethod
    def set_agent(cls, agent: Any) -> None:
        cls._agent = agent

    @classmethod
    def get_agent(cls) -> Any:
        if cls._agent is None:
            raise RuntimeError("Agent has not been initialized. Ensure lifespan is running.")
        return cls._agent

    @classmethod
    def clear_agent(cls) -> None:
        cls._agent = None

    @staticmethod
    def create_agent(checkpointer: Optional[Any] = None):
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

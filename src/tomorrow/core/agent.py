import contextlib
from typing import Any, Optional

from daytona import Daytona
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage
from langchain_daytona import DaytonaSandbox
from langchain_ollama import ChatOllama

from tomorrow.conf import settings
from tomorrow.core.checkpoints import get_checkpointer_context
from tomorrow.models.constants.backend import BackendType


def get_backend() -> Any:
    backend_type = settings.BACKEND.get("type")
    backend_config = settings.BACKEND.get(backend_type, {})
    if backend_type == BackendType.FILESYSTEM:
        root_dir = backend_config.get("root_dir")
        if not root_dir:
            raise ValueError("root_dir is required for Filesystem backend")
        return FilesystemBackend(root_dir=root_dir, virtual_mode=True)
    elif backend_type == BackendType.DAYTONA:
        daytona_client = Daytona()
        sandbox = daytona_client.create()
        return DaytonaSandbox(sandbox=sandbox)
    else:
        raise ValueError(f"Unsupported backend type: {backend_type}")


def get_model(model: Optional[str] = None) -> BaseChatModel:
    model = model or settings.DEFAULT_MODEL
    return ChatOllama(
        model=model,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0,
    )


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
        )

    @staticmethod
    @contextlib.asynccontextmanager
    async def get_agent_context():
        async with get_checkpointer_context() as checkpointer:
            yield AgentManager.create_agent(checkpointer)

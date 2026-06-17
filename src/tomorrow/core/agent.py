from typing import Optional

from deepagents import create_deep_agent
from langchain_core.messages import SystemMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph

from tomorrow.conf import settings
from tomorrow.core.backend import get_backend
from tomorrow.core.model import get_model
from tomorrow.core.store import get_store
from tomorrow.exceptions import TomorrowRuntimeError
from tomorrow.utils.log import logger


class AgentManager:
    """Agent 管理器，用于在生命周期内持有 Agent 实例并提供创建方法。"""

    _agent: Optional[CompiledStateGraph] = None

    @classmethod
    def set_agent(cls, agent: CompiledStateGraph) -> None:
        cls._agent = agent

    @classmethod
    def get_agent(cls) -> CompiledStateGraph:
        if cls._agent is None:
            raise TomorrowRuntimeError("Agent has not been initialized. Ensure lifespan is running.")
        return cls._agent

    @classmethod
    def clear_agent(cls) -> None:
        cls._agent = None

    @staticmethod
    def create_agent(checkpointer: Optional[BaseCheckpointSaver] = None) -> CompiledStateGraph:
        logger.info(f"Initializing Agent for {settings.APP}...")

        # 打印当前使用的配置
        model_type = settings.MODEL.get("type")
        logger.info(f"MODEL: {model_type} -> {settings.MODEL.get(model_type)}")

        backend_type = settings.BACKEND.get("type")
        logger.info(f"BACKEND: {backend_type} -> {settings.BACKEND.get(backend_type)}")

        store_type = settings.STORE.get("type")
        logger.info(f"STORE: {store_type} -> {settings.STORE.get(store_type)}")

        checkpoint_type = settings.CHECKPOINT.get("type")
        logger.info(f"CHECKPOINT: {checkpoint_type} -> {settings.CHECKPOINT.get(checkpoint_type)}")

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

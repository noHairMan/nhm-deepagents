from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from tomorrow.core.agent import AgentManager
from tomorrow.core.checkpoints import get_checkpointer_context


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    async with get_checkpointer_context() as checkpointer:
        AgentManager.set_agent(AgentManager.create_agent(checkpointer))
        try:
            yield
        finally:
            AgentManager.clear_agent()

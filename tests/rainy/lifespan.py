import os

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# 设置环境变量
os.environ["TOMORROW_APP"] = "tomorrow"
os.environ["TOMORROW_SETTINGS_MODULE"] = "tomorrow.settings"
os.environ["RAINY_APP"] = "rainy"
os.environ["RAINY_SETTINGS_MODULE"] = "rainy.settings"

from rainy.lifespan import lifespan
from tomorrow.core.agent import AgentManager


class TestLifespan:
    @pytest.mark.asyncio
    async def test_lifespan_execution(self):
        """测试 lifespan 函数能正确在 AgentManager 中设置 agent"""
        app = FastAPI(lifespan=lifespan)

        # 使用 TestClient 触发 lifespan
        with TestClient(app):
            assert AgentManager.get_agent() is not None

        # lifespan 结束后应该被清理
        with pytest.raises(RuntimeError):
            AgentManager.get_agent()

import os

from fastapi.testclient import TestClient

# 设置环境变量
os.environ["TOMORROW_APP"] = "tomorrow"
os.environ["TOMORROW_SETTINGS_MODULE"] = "tomorrow.settings"
os.environ["RAINY_APP"] = "rainy"
os.environ["RAINY_SETTINGS_MODULE"] = "rainy.settings"

from rainy.app import app
from tomorrow.core.agent import AgentManager


class TestApp:
    def test_lifespan(self):
        """测试 lifespan 事件能够正确执行"""
        # TestClient 使用 with 语句时会触发 lifespan 事件
        with TestClient(app):
            assert AgentManager.get_agent() is not None

            # 验证请求可以正常工作（可选）
            # response = client.get("/api/health")
            # assert response.status_code == 200

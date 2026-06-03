import os

from fastapi.testclient import TestClient

# 设置环境变量以确保配置正确加载
os.environ["TOMORROW_APP"] = "tomorrow"
os.environ["TOMORROW_SETTINGS_MODULE"] = "tomorrow.settings"
os.environ["RAINY_APP"] = "rainy"
os.environ["RAINY_SETTINGS_MODULE"] = "rainy.settings"

from rainy.app import app


class TestResponseMiddleware:
    client = TestClient(app)

    def test_health_check_wrapped(self):
        """验证健康检查路径现在也被包装"""
        # 注意：urls.py 中有 prefix="/api" ，所以路径是 /api/health
        response = self.client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        # 现在 /api/health 不在排除列表中，所以应该被包装
        assert "code" in data
        assert data["code"] == 0
        assert "data" in data
        assert data["data"] == {"status": "ok"}
        assert data["message"] == "成功"

    def test_chat_response_wrapped(self):
        """验证聊天接口返回被包装"""
        response = self.client.post("/api/chat", json={"message": "hello"})
        assert response.status_code == 200
        data = response.json()
        assert "code" in data
        assert data["code"] == 0
        assert "data" in data
        assert data["data"] is None  # chat 接口目前返回 None
        assert data["message"] == "成功"

    def test_docs_not_wrapped(self):
        """验证文档路径不被包装"""
        response = self.client.get("/docs")
        # 如果 /docs 存在，它应该返回 200 或重定向，且不应该被包装成 BaseResponse 格式
        # 这里主要验证中间件的排除逻辑
        assert response.status_code in [200, 307]
        if response.status_code == 200 and "application/json" in response.headers.get("Content-Type", ""):
            assert "code" not in response.json()

    def test_non_json_response_not_wrapped(self):
        """验证非 JSON 响应不被包装"""
        # 我们需要一个返回非 JSON 的接口，或者模拟一个
        # 由于我们目前只有 chat 和 health，且都是 JSON。
        # 这里暂时用一个不存在的路径测试 404，它应该不被包装（因为 status_code != 200）
        response = self.client.get("/non-existent")
        assert response.status_code == 404
        # FastAPI 的默认 404 是 JSON，但 status_code 是 404，所以中间件应该直接返回
        data = response.json()
        assert "detail" in data
        assert "code" not in data

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

    def test_chat_response_not_wrapped(self):
        """验证聊天接口为 SSE 流式响应，不被统一格式中间件包装"""

        from langchain_core.messages import AIMessageChunk

        class FakeAgent:
            async def astream(self, *args, **kwargs):
                yield "test answer"

            async def astream_events(self, *args, **kwargs):
                yield {
                    "event": "on_chat_model_stream",
                    "data": {"chunk": AIMessageChunk(content="test answer")},
                }

        from tomorrow.core.agent import AgentManager

        AgentManager.set_agent(FakeAgent())
        try:
            response = self.client.post("/api/chat/stream", json={"message": "hello"})
            assert response.status_code == 200
            content_type = response.headers.get("Content-Type", "")
            assert "text/event-stream" in content_type or "application/jsonl" in content_type
            assert "test answer" in response.text
            # 流式响应不应被包装成统一 JSON 格式
            assert "code" not in response.text
        finally:
            AgentManager.clear_agent()

    def test_docs_not_wrapped(self):
        """验证文档路径不被包装"""
        response = self.client.get("/docs")
        # 如果 /docs 存在，它应该返回 200 或重定向，且不应该被包装成 BaseResponse 格式
        # 这里主要验证中间件的排除逻辑
        assert response.status_code in [200, 307]
        if response.status_code == 200 and "application/json" in response.headers.get("Content-Type", ""):
            assert "code" not in response.json()

    def test_unify_response_format_error(self):
        """验证统一响应格式中间件在解析错误时的处理（不再捕获 JSON 解析错误）"""
        import json

        import pytest
        from fastapi import Request
        from fastapi.responses import StreamingResponse

        from rainy.middleware.response import unify_response_format

        async def call_next(request):
            async def content_gen():
                yield b"invalid json"

            return StreamingResponse(content_gen(), status_code=200, media_type="application/json")

        scope = {"type": "http", "path": "/api/test", "method": "GET", "headers": [(b"host", b"localhost")]}
        request = Request(scope=scope)

        import asyncio

        with pytest.raises(json.JSONDecodeError):
            asyncio.run(unify_response_format(request, call_next))

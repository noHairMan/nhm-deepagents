import json
import os
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage, AIMessageChunk

# 设置环境变量以确保配置正确加载
os.environ["TOMORROW_APP"] = "tomorrow"
os.environ["TOMORROW_SETTINGS_MODULE"] = "tomorrow.settings"
os.environ["RAINY_APP"] = "rainy"
os.environ["RAINY_SETTINGS_MODULE"] = "rainy.settings"

from rainy.app import app


def _make_event(content):
    return {
        "event": "on_chat_model_stream",
        "data": {"chunk": AIMessageChunk(content=content)},
    }


class FakeAgent:
    def __init__(self, events=None, answer=""):
        self._events = events or []
        self._answer = answer

    async def astream_events(self, *args, **kwargs):
        for event in self._events:
            yield event

    async def ainvoke(self, *args, **kwargs):
        return {"messages": [AIMessage(content=self._answer)]}


class TestChat:
    client = TestClient(app)

    def _patch_agent(self, **kwargs):
        mock_create_agent = MagicMock()
        mock_create_agent.return_value.__aenter__.return_value = FakeAgent(**kwargs)
        mock_create_agent.return_value.__aexit__.return_value = None
        return patch("rainy.api.endpoints.chat.create_agent", mock_create_agent)

    def test_chat_sync(self):
        """验证同步聊天接口一次性返回完整回答。"""
        with self._patch_agent(answer="你好，世界"):
            response = self.client.post("/api/chat", json={"message": "hi"})
        assert response.status_code == 200
        data = response.json()
        # 经统一响应中间件包装
        assert data["data"]["answer"] == "你好，世界"

    def test_chat_stream(self):
        """验证流式聊天接口以 SSE 流式输出内容。"""
        events = [
            _make_event("你好"),
            _make_event(""),  # 空内容应被跳过
            {"event": "on_chain_start", "data": {}},  # 非目标事件应被忽略
            _make_event("，世界"),
        ]
        with self._patch_agent(events=events):
            with self.client.stream("POST", "/api/chat/stream", json={"message": "hi"}) as response:
                assert response.status_code == 200
                assert "text/event-stream" in response.headers["content-type"]
                body = "".join(response.iter_text())

        # 内容以合法 JSON 形式拼接
        assert f"data: {json.dumps({'answer': '你好'}, ensure_ascii=False)}\n\n" in body
        assert f"data: {json.dumps({'answer': '，世界'}, ensure_ascii=False)}\n\n" in body
        assert "data: [DONE]" in body
        # 空内容不应产生数据行（你好、，世界、[DONE] 共 3 行 data:）
        assert body.count("data: ") == 3

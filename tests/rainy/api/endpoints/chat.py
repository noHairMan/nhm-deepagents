import os

from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage, AIMessageChunk

# 设置环境变量以确保配置正确加载
os.environ["TOMORROW_APP"] = "tomorrow"
os.environ["TOMORROW_SETTINGS_MODULE"] = "tomorrow.settings"
os.environ["RAINY_APP"] = "rainy"
os.environ["RAINY_SETTINGS_MODULE"] = "rainy.settings"

from rainy.app import app
from tomorrow.core.agent import AgentManager


def _make_event(content):
    return {
        "event": "on_chat_model_stream",
        "data": {"chunk": AIMessageChunk(content=content)},
    }


class FakeAgent:
    def __init__(self, events=None, answer=""):
        self._events = events or []
        self._answer = answer
        self.invoked_config = None

    async def astream_events(self, *args, **kwargs):
        self.invoked_config = kwargs.get("config")
        for event in self._events:
            yield event

    async def ainvoke(self, *args, **kwargs):
        self.invoked_config = kwargs.get("config")
        return {"messages": [AIMessage(content=self._answer)]}


class TestChat:
    client = TestClient(app)

    def test_chat_sync(self):
        """验证同步聊天接口一次性返回完整回答。"""
        fake_agent = FakeAgent(answer="你好，世界")
        AgentManager.set_agent(fake_agent)
        try:
            response = self.client.post(
                "/api/chat", json={"message": "hi", "thread_id": "00000000-0000-0000-0000-000000000001"}
            )
            assert response.status_code == 200
            data = response.json()
            # 经统一响应中间件包装
            assert data["data"]["answer"] == "你好，世界"
            assert str(fake_agent.invoked_config["configurable"]["thread_id"]) == "00000000-0000-0000-0000-000000000001"
        finally:
            AgentManager.clear_agent()

    def test_chat_sync_no_thread_id(self):
        """验证未传递 thread_id 时自动生成。"""
        fake_agent = FakeAgent(answer="你好，世界")
        AgentManager.set_agent(fake_agent)
        try:
            response = self.client.post("/api/chat", json={"message": "hi"})
            assert response.status_code == 200
            assert fake_agent.invoked_config["configurable"]["thread_id"] is not None
        finally:
            AgentManager.clear_agent()

    def test_chat_stream(self):
        """验证流式聊天接口以 SSE 流式输出内容。"""
        events = [
            _make_event("你好"),
            _make_event(""),  # 空内容应被跳过
            {"event": "on_chain_start", "data": {}},  # 非目标事件应被忽略
            _make_event("，世界"),
        ]
        fake_agent = FakeAgent(events=events)
        AgentManager.set_agent(fake_agent)
        try:
            with self.client.stream(
                "POST", "/api/chat/stream", json={"message": "hi", "thread_id": "00000000-0000-0000-0000-000000000002"}
            ) as response:
                assert response.status_code == 200
                assert "text/event-stream" in response.headers["content-type"]
                body = "".join(response.iter_text())

            # 内容以合法 JSON 形式拼接
            assert "data: " in body
            assert "answer" in body
            decoded_body = body.encode().decode("unicode_escape")
            assert "你好" in decoded_body
            assert "，世界" in decoded_body
            # 空内容不应产生数据行（你好、，世界 共 2 行 data:）
            assert body.count("data: ") == 3
            assert str(fake_agent.invoked_config["configurable"]["thread_id"]) == "00000000-0000-0000-0000-000000000002"
        finally:
            AgentManager.clear_agent()

    def test_chat_stream_no_thread_id(self):
        """验证流式接口未传递 thread_id 时自动生成。"""
        events = [_make_event("test")]
        fake_agent = FakeAgent(events=events)
        AgentManager.set_agent(fake_agent)
        try:
            with self.client.stream("POST", "/api/chat/stream", json={"message": "hi"}) as response:
                assert response.status_code == 200
                "".join(response.iter_text())
            assert fake_agent.invoked_config["configurable"]["thread_id"] is not None
        finally:
            AgentManager.clear_agent()

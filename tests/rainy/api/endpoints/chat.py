import os

from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage

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
        if self._events == "FAIL":
            raise Exception("Model error")
        for event in self._events:
            yield event

    async def ainvoke(self, *args, **kwargs):
        self.invoked_config = kwargs.get("config")
        if self._answer == "FAIL":
            raise Exception("Model error")
        return {
            "messages": [
                HumanMessage(content="User message"),
                AIMessage(content=self._answer),
            ]
        }


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
            assert data["data"]["choices"][0]["message"]["content"] == "你好，世界"
            assert data["data"]["choices"][0]["message"]["role"] == "assistant"
            assert data["data"]["object"] == "chat.completion"
            assert data["data"]["id"] == "chatcmpl-00000000-0000-0000-0000-000000000001"
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
            {"event": "on_chat_model_start", "data": {}},
            _make_event("你好"),
            _make_event(""),  # 空内容应被跳过
            {"event": "on_chain_start", "data": {}},  # 非目标事件应被忽略
            _make_event("，世界"),
            {"event": "on_chat_model_end", "data": {}},
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
            assert "choices" in body
            assert "delta" in body
            assert "你好" in body
            assert "，世界" in body
            assert "chat.completion.chunk" in body
            assert "chatcmpl-00000000-0000-0000-0000-000000000002" in body
            assert "stop" in body
            # 只有有内容的 chunk 和 end 事件会产生 data 行
            # 你好, ，世界, end 共 3 行
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

    def test_chat_sync_error(self):
        """验证同步接口发生错误时的处理。"""
        fake_agent = FakeAgent(answer="FAIL")
        AgentManager.set_agent(fake_agent)
        try:
            import pytest

            # 由于 TestClient 会捕获异常并返回 500，我们如果要在单元测试层面验证
            # 最好直接调用路由函数，或者依赖 TestClient 的 raise_server_exceptions=True
            client = TestClient(app, raise_server_exceptions=True)
            with pytest.raises(Exception) as excinfo:
                client.post("/api/chat", json={"message": "hi"})
            assert "Model error" in str(excinfo.value)
        finally:
            AgentManager.clear_agent()

    def test_chat_stream_error(self):
        """验证流式接口发生错误时的处理。"""
        fake_agent = FakeAgent(events="FAIL")
        AgentManager.set_agent(fake_agent)
        try:
            import pytest

            client = TestClient(app, raise_server_exceptions=True)
            with pytest.raises(Exception) as excinfo:
                with client.stream("POST", "/api/chat/stream", json={"message": "hi"}) as response:
                    "".join(response.iter_text())
            assert "Model error" in str(excinfo.value)
        finally:
            AgentManager.clear_agent()

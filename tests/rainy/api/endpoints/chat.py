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

    async def astream(self, *args, **kwargs):
        self.invoked_config = kwargs.get("config")
        if self._events == "FAIL":
            raise Exception("Model error")
        for event in self._events:
            yield event

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
        from unittest.mock import MagicMock

        mock_response = MagicMock()
        mock_response.value = {
            "messages": [
                HumanMessage(content="User message"),
                AIMessage(content=self._answer),
            ]
        }
        return mock_response


class TestChat:
    client = TestClient(app)

    def test_chat(self):
        """验证聊天接口正常返回最后一条消息。"""
        fake_agent = FakeAgent(answer="Hello, I am an AI.")
        AgentManager.set_agent(fake_agent)
        try:
            response = self.client.post(
                "/api/chat", json={"message": "hi", "thread_id": "00000000-0000-0000-0000-000000000001"}
            )
            assert response.status_code == 200
            assert response.json()["data"] == "Hello, I am an AI."
            assert response.json()["code"] == 0
            assert str(fake_agent.invoked_config["configurable"]["thread_id"]) == "00000000-0000-0000-0000-000000000001"
        finally:
            AgentManager.clear_agent()

    def test_chat_error(self):
        """验证聊天接口发生错误时的处理。"""
        fake_agent = FakeAgent(answer="FAIL")
        AgentManager.set_agent(fake_agent)
        try:
            import pytest

            client = TestClient(app, raise_server_exceptions=True)
            with pytest.raises(Exception) as excinfo:
                client.post("/api/chat", json={"message": "hi"})
            assert "Model error" in str(excinfo.value)
        finally:
            AgentManager.clear_agent()

    def test_chat_stream(self):
        """验证流式聊天接口输出文本增量。"""
        events = [
            {"event": "on_chat_model_start", "data": {}},
            {"event": "on_chat_model_stream", "data": {"chunk": AIMessageChunk(content="你好")}},
            {"event": "on_chat_model_stream", "data": {"chunk": AIMessageChunk(content="世界")}},
            {"event": "on_chat_model_end", "data": {}},
        ]
        fake_agent = FakeAgent(events=events)
        AgentManager.set_agent(fake_agent)
        try:
            with self.client.stream(
                "POST", "/api/chat/stream", json={"message": "hi", "thread_id": "00000000-0000-0000-0000-000000000002"}
            ) as response:
                assert response.status_code == 200
                body = "".join(response.iter_text())

            assert 'data: {"content": "你好"}' in body
            assert 'data: {"content": "世界"}' in body
            assert body.count("data: ") == 2
            assert str(fake_agent.invoked_config["configurable"]["thread_id"]) == "00000000-0000-0000-0000-000000000002"
        finally:
            AgentManager.clear_agent()

    def test_chat_stream_event(self):
        """验证 chat_stream_event 接口。"""
        # 使用简单的字典以确保可以被 json.dumps 成功序列化
        events = [{"event": "on_chat_model_stream", "data": {"content": "test"}}]
        fake_agent = FakeAgent(events=events)
        AgentManager.set_agent(fake_agent)
        try:
            with self.client.stream("POST", "/api/chat/stream/event", json={"message": "hi"}) as response:
                assert response.status_code == 200
                body = "".join(response.iter_text())
                assert 'data: {"event": "on_chat_model_stream"' in body
        finally:
            AgentManager.clear_agent()

    def test_chat_stream_event_serialization_error(self):
        """验证 chat_stream_event 接口序列化失败时的处理。"""

        # 无法序列化的对象
        class Unserializable:
            def __repr__(self):
                return "<unserializable>"

        events = [{"event": "error", "data": Unserializable()}]
        fake_agent = FakeAgent(events=events)
        AgentManager.set_agent(fake_agent)
        try:
            with self.client.stream("POST", "/api/chat/stream/event", json={"message": "hi"}) as response:
                assert response.status_code == 200
                body = "".join(response.iter_text())
                # 当 json.dumps 失败时，会回退到 json.dumps(str(event))
                assert "unserializable" in body
                assert body.startswith('data: "')  # 应该是 JSON 字符串
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

    def test_chat_stream_event_json_serialization(self):
        """测试 chat_stream_event 接口中 json.dumps 是否按预期工作。"""
        # 测试正常可序列化对象
        events = [{"event": "on_chat_model_stream", "data": {"chunk": {"content": "hello"}}}]
        fake_agent = FakeAgent(events=events)
        AgentManager.set_agent(fake_agent)
        try:
            with self.client.stream("POST", "/api/chat/stream/event", json={"message": "hi"}) as response:
                assert response.status_code == 200
                body = "".join(response.iter_text())
                assert 'data: {"event": "on_chat_model_stream"' in body
                assert '"content": "hello"' in body
        finally:
            AgentManager.clear_agent()

    def test_chat_stream_non_dict_event(self):
        """测试 astream 返回非字典事件。"""
        events = ["some string event"]
        fake_agent = FakeAgent(events=events)
        AgentManager.set_agent(fake_agent)
        try:
            with self.client.stream("POST", "/api/chat/stream", json={"message": "hi"}) as response:
                assert response.status_code == 200
                body = "".join(response.iter_text())
                assert body == ""
        finally:
            AgentManager.clear_agent()

    def test_chat_stream_empty_content(self):
        """测试 astream_events 返回 content 为空的事件。"""
        events = [
            {"event": "on_chat_model_stream", "data": {"chunk": AIMessageChunk(content="你好")}},
            {"event": "on_chat_model_stream", "data": {"chunk": AIMessageChunk(content=" ")}},  # 只有空格
            {"event": "on_chat_model_stream", "data": {"chunk": AIMessageChunk(content="")}},  # 为空
        ]
        fake_agent = FakeAgent(events=events)
        AgentManager.set_agent(fake_agent)
        try:
            with self.client.stream("POST", "/api/chat/stream", json={"message": "hi"}) as response:
                assert response.status_code == 200
                body = "".join(response.iter_text())
                assert 'data: {"content": "你好"}' in body
                assert 'data: {"content": " "}' in body
                assert body.count("data: ") == 2
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

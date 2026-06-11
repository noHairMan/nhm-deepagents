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

    def test_chat_stream(self):
        """验证流式聊天接口直接输出原始事件流。"""
        # 模拟各种类型的对象以测试序列化器
        from pydantic import BaseModel

        class MockPydantic(BaseModel):
            content: str = "你好"

        class MockOldDict(BaseModel):
            key: str = "value"

        events = [
            {"event": "on_chain_start", "name": "thought_node", "data": {}},
            {"event": "on_chat_model_start", "data": {"p": MockPydantic()}},
            {"event": "on_chat_model_stream", "data": {"d": MockOldDict()}},
            {"event": "on_tool_start", "name": "search_tool", "data": {"other": "unknown"}},
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
                # Starlette's EventSourceResponse might set different content-types depending on version/config
                # In this environment it seems to be application/jsonl
                assert (
                    "text/event-stream" in response.headers["content-type"]
                    or "application/jsonl" in response.headers["content-type"]
                )
                body = "".join(response.iter_text())

            # 验证返回的内容中包含原始事件的关键信息
            assert "on_chain_start" in body
            assert "thought_node" in body
            assert "on_chat_model_stream" in body
            # 处理中文编码：可能是原始字符或 \u 序列
            assert "你好" in body or "\\u4f60\\u597d" in body
            assert "on_tool_start" in body
            assert "search_tool" in body
            assert "，世界" in body or "\\uff0c\\u4e16\\u754c" in body
            assert "on_chat_model_end" in body

            # 每个 event 都会产生一行数据
            assert body.count("data: {") == 6
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

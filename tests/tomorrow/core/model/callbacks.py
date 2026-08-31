import json
from unittest.mock import patch
from uuid import UUID

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, Generation, LLMResult

from tomorrow.core.model.callbacks import LLMLoggingCallbackHandler


class TestLLMLoggingCallbackHandler:
    def test_on_chat_model_start_logs_model_run_id_and_messages(self):
        callback = LLMLoggingCallbackHandler()
        run_id = UUID(int=1)
        messages = [[SystemMessage(content="system"), HumanMessage(content="hello")]]

        with patch("tomorrow.core.model.callbacks.logger") as mock_logger:
            callback.on_chat_model_start(
                {"name": "test-model", "kwargs": {"api_key": "secret"}},
                messages,
                run_id=run_id,
            )

        call_args = mock_logger.debug.call_args.args
        payload = json.loads(call_args[2])
        assert call_args[0] == "llm_event=%s payload=%s"
        assert call_args[1] == "input"
        assert payload == {
            "event": "input",
            "run_id": str(run_id),
            "model": "test-model",
            "messages": [
                [
                    {"role": "system", "content": "system"},
                    {"role": "human", "content": "hello"},
                ]
            ],
        }
        assert "secret" not in call_args[2]

    def test_on_chat_model_start_uses_id_and_safe_structured_content(self):
        callback = LLMLoggingCallbackHandler()

        class UnsupportedContent:
            pass

        with patch("tomorrow.core.model.callbacks.logger") as mock_logger:
            callback.on_chat_model_start(
                {"id": ["provider", "model"]},
                [[HumanMessage(content=[{"type": "text", "value": UnsupportedContent()}])]],
                run_id=UUID(int=2),
            )

        payload = json.loads(mock_logger.debug.call_args.args[2])
        assert payload["model"] == ["provider", "model"]
        assert payload["messages"][0][0]["content"][0]["value"] == "<unserializable:UnsupportedContent>"

    def test_on_chat_model_start_logs_flat_messages(self):
        callback = LLMLoggingCallbackHandler()

        with patch("tomorrow.core.model.callbacks.logger") as mock_logger:
            callback.on_chat_model_start(
                {"name": "test-model"},
                [HumanMessage(content="hello")],
                run_id=UUID(int=7),
            )

        payload = json.loads(mock_logger.debug.call_args.args[2])
        assert payload["messages"] == [[{"role": "human", "content": "hello"}]]

    def test_safe_value_normalizes_message(self):
        normalized = LLMLoggingCallbackHandler._safe_value(AIMessage(content="answer"))

        assert normalized == {"role": "ai", "content": "answer"}

    def test_on_llm_end_logs_text_and_structured_message_generations(self):
        callback = LLMLoggingCallbackHandler()
        response = LLMResult(
            generations=[
                [Generation(text="first"), Generation(text="second")],
                [ChatGeneration(message=AIMessage(content=[{"type": "text", "text": "answer"}]))],
            ]
        )

        with patch("tomorrow.core.model.callbacks.logger") as mock_logger:
            callback.on_llm_end(response, run_id=UUID(int=3))

        payload = json.loads(mock_logger.debug.call_args.args[2])
        assert payload == {
            "event": "output",
            "run_id": "00000000-0000-0000-0000-000000000003",
            "generations": [
                [{"content": "first"}, {"content": "second"}],
                [
                    {
                        "role": "ai",
                        "content": [{"type": "text", "text": "answer"}],
                    }
                ],
            ],
        }

    def test_on_llm_end_logs_empty_generations(self):
        callback = LLMLoggingCallbackHandler()

        with patch("tomorrow.core.model.callbacks.logger") as mock_logger:
            callback.on_llm_end(LLMResult(generations=[]), run_id=UUID(int=4))

        payload = json.loads(mock_logger.debug.call_args.args[2])
        assert payload["event"] == "output"
        assert payload["generations"] == []

    def test_on_llm_end_logs_flat_generation(self):
        callback = LLMLoggingCallbackHandler()

        with patch("tomorrow.core.model.callbacks.logger") as mock_logger:
            callback.on_llm_end(
                type("Response", (), {"generations": [Generation(text="answer")]})(),
                run_id=UUID(int=8),
            )

        payload = json.loads(mock_logger.debug.call_args.args[2])
        assert payload["generations"] == [[{"content": "answer"}]]

    def test_logging_failure_does_not_escape_callback(self):
        callback = LLMLoggingCallbackHandler()

        with patch("tomorrow.core.model.callbacks.logger") as mock_logger:
            mock_logger.debug.side_effect = RuntimeError("logging unavailable")
            callback.on_chat_model_start({}, [], run_id=UUID(int=5))
            callback.on_llm_end(LLMResult(generations=[]), run_id=UUID(int=6))

        assert mock_logger.debug.call_count == 2

    def test_serialize_uses_fallback_when_normalization_fails(self):
        with patch.object(LLMLoggingCallbackHandler, "_safe_value", side_effect=RuntimeError("cannot normalize")):
            serialized = LLMLoggingCallbackHandler._serialize({"event": "output"})

        assert serialized == '{"event":"logging-failed"}'

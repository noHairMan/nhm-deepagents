import contextlib
import json
import logging
from collections.abc import Mapping
from typing import Any
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage
from langchain_core.outputs import LLMResult

logger = logging.getLogger("tomorrow.llm")


class LLMLoggingCallbackHandler(BaseCallbackHandler):
    """Record chat model inputs and final outputs without affecting model calls."""

    def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[BaseMessage]],
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> Any:
        del kwargs
        self._log_event(
            "input",
            {
                "event": "input",
                "run_id": str(run_id),
                "model": self._model_identifier(serialized),
                "messages": [
                    [self._message_payload(message) for message in batch] for batch in self._message_batches(messages)
                ],
            },
        )

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> Any:
        del kwargs
        generations = self._generation_batches(getattr(response, "generations", None))
        self._log_event(
            "output",
            {
                "event": "output",
                "run_id": str(run_id),
                "generations": [
                    [self._generation_payload(generation) for generation in batch] for batch in generations
                ],
            },
        )

    @classmethod
    def _model_identifier(cls, serialized: Mapping[str, Any]) -> Any:
        for key in ("name", "id"):
            value = serialized.get(key)
            if value:
                return cls._safe_value(value)
        return "unknown"

    @classmethod
    def _message_batches(cls, messages: Any) -> list[list[Any]]:
        batches: list[list[Any]] = []
        for batch in messages or []:
            if isinstance(batch, BaseMessage):
                batches.append([batch])
            elif isinstance(batch, (list, tuple)):
                batches.append(list(batch))
            else:
                batches.append([batch])
        return batches

    @classmethod
    def _generation_batches(cls, generations: Any) -> list[list[Any]]:
        batches: list[list[Any]] = []
        for batch in generations or []:
            if isinstance(batch, (list, tuple)):
                batches.append(list(batch))
            else:
                batches.append([batch])
        return batches

    @classmethod
    def _message_payload(cls, message: Any) -> dict[str, Any]:
        return {
            "role": getattr(message, "type", "message"),
            "content": cls._safe_value(getattr(message, "content", message)),
        }

    @classmethod
    def _generation_payload(cls, generation: Any) -> Any:
        message = getattr(generation, "message", None)
        if isinstance(message, BaseMessage):
            return cls._message_payload(message)
        return {"content": cls._safe_value(getattr(generation, "text", ""))}

    @classmethod
    def _safe_value(cls, value: Any) -> Any:
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, BaseMessage):
            return cls._message_payload(value)
        if isinstance(value, Mapping):
            return {str(key): cls._safe_value(item) for key, item in value.items()}
        if isinstance(value, (list, tuple, set, frozenset)):
            return [cls._safe_value(item) for item in value]
        return f"<unserializable:{type(value).__name__}>"

    @classmethod
    def _serialize(cls, payload: Mapping[str, Any]) -> str:
        try:
            return json.dumps(cls._safe_value(payload), ensure_ascii=False)
        except Exception:
            return '{"event":"logging-failed"}'

    @classmethod
    def _log_event(cls, event: str, payload: Mapping[str, Any]) -> None:
        with contextlib.suppress(Exception):
            logger.debug("llm_event=%s payload=%s", event, cls._serialize(payload))


llm_callback = LLMLoggingCallbackHandler()  # noqa: W292

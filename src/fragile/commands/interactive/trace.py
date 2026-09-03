"""Stable, safe representations of interactive agent stream events."""

import json
import re
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any, Literal
from urllib.parse import urlsplit, urlunsplit

TraceKind = Literal["stage", "thinking", "text", "tool_start", "tool_end", "tool_error"]
TraceStatus = Literal["running", "completed", "failed"]

_REDACTED = "[REDACTED]"
_SENSITIVE_KEY = re.compile(
    r"(?:api[_-]?key|authorization|password|passwd|secret|token|credential|cookie)", re.IGNORECASE
)
_EVENT_TO_KIND: dict[str, TraceKind] = {
    "on_tool_start": "tool_start",
    "on_tool_end": "tool_end",
    "on_tool_error": "tool_error",
}
_IGNORED_STAGE_NAMES = {
    "__start__",
    "__end__",
    "langgraph",
    "runnablesequence",
    "channelwrite",
}


@dataclass(frozen=True)
class StreamSegment:
    """A model content fragment before it is assigned to a trace sequence."""

    kind: Literal["thinking", "text"]
    content: str


@dataclass(frozen=True)
class TraceEvent:
    """A serializable event in the interactive execution timeline."""

    sequence: int
    kind: TraceKind
    name: str | None = None
    content: str | None = None
    input: Any = None
    output: Any = None
    status: TraceStatus | None = None
    run_id: str | None = None
    parent_run_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


def content_segments(content: Any) -> list[StreamSegment]:
    """Extract supported text, thinking, and reasoning blocks from model content."""
    if isinstance(content, str):
        return [StreamSegment("text", content)] if content else []
    if not isinstance(content, list):
        return []

    segments: list[StreamSegment] = []
    for block in content:
        if isinstance(block, str):
            if block:
                segments.append(StreamSegment("text", block))
            continue
        if not isinstance(block, dict):
            continue

        block_type = block.get("type")
        if block_type == "reasoning" or "reasoning" in block:
            reasoning = block.get("reasoning")
            if isinstance(reasoning, str) and reasoning:
                segments.append(StreamSegment("thinking", reasoning))
        elif block_type == "thinking" or "thinking" in block:
            thinking = block.get("thinking")
            if isinstance(thinking, str) and thinking:
                segments.append(StreamSegment("thinking", thinking))
        elif block_type == "text" or block_type is None:
            text = block.get("text")
            if isinstance(text, str) and text:
                segments.append(StreamSegment("text", text))
    return segments


def content_text(content: Any) -> str:
    """Return only ordinary text from supported model content blocks."""
    return "".join(segment.content for segment in content_segments(content) if segment.kind == "text")


def _redact_text(value: str) -> str:
    """Redact inline credentials and URL user information from text values."""
    redacted = re.sub(
        r"((?:api[_-]?key|authorization|password|passwd|secret|token|credential|cookie)\s*[:=]\s*)[^\s,;]+",
        rf"\1{_REDACTED}",
        value,
        flags=re.IGNORECASE,
    )
    return _redact_url(redacted)


def safe_value(value: Any, key: str | None = None) -> Any:
    """Convert a value into JSON-compatible data while redacting sensitive values."""
    if key is not None and _SENSITIVE_KEY.search(key):
        return _REDACTED
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return _redact_text(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(item_key): safe_value(item_value, str(item_key)) for item_key, item_value in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [safe_value(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return [safe_value(item) for item in value]
    return f"<{type(value).__name__}>"


def _redact_url(value: str) -> str:
    """Remove credentials from URL-looking strings without changing ordinary text."""
    try:
        parsed = urlsplit(value)
    except ValueError:
        return value
    if not parsed.scheme or parsed.hostname is None or parsed.username is None:
        return value
    hostname = parsed.hostname
    if ":" in hostname and not hostname.startswith("["):
        hostname = f"[{hostname}]"
    try:
        port = f":{parsed.port}" if parsed.port is not None else ""
    except ValueError:
        port = ""
    return urlunsplit((parsed.scheme, f"{hostname}{port}", parsed.path, parsed.query, parsed.fragment))


def _event_metadata(event: Mapping[str, Any]) -> dict[str, Any]:
    """Keep useful stream metadata while ensuring it is safe to persist."""
    metadata: dict[str, Any] = {}
    for key in ("tags", "metadata", "parent_ids", "run_type"):
        if key in event:
            metadata[key] = safe_value(event[key], key)
    return metadata


def _run_ids(event: Mapping[str, Any]) -> tuple[str | None, str | None]:
    run_id = event.get("run_id")
    parent_ids = event.get("parent_ids")
    parent_run_id = (
        parent_ids[-1]
        if isinstance(parent_ids, Sequence) and not isinstance(parent_ids, (str, bytes, bytearray)) and parent_ids
        else None
    )
    return (str(run_id) if run_id is not None else None, str(parent_run_id) if parent_run_id is not None else None)


def _tool_input(data: Mapping[str, Any]) -> Any:
    return data.get("input")


def _command_text(name: str | None, value: Any) -> str | None:
    if name is None or name.lower() != "execute" or not isinstance(value, Mapping):
        return None
    command = value.get("command")
    return command if isinstance(command, str) and command else None


def _safe_text(value: Any) -> str:
    """Render event error text without allowing sensitive URL or field values through."""
    if isinstance(value, str):
        return _redact_text(value)
    normalized = safe_value(value)
    return normalized if isinstance(normalized, str) else str(normalized)


def _stage_event_kind(event_name: str, name: str | None) -> tuple[TraceKind, TraceStatus] | None:
    if event_name not in {"on_chain_start", "on_chain_end", "on_chain_error"} or not name:
        return None
    normalized_name = name.lower()
    if normalized_name in _IGNORED_STAGE_NAMES or normalized_name.startswith("__"):
        return None
    if (
        "agent" not in normalized_name
        and "subagent" not in normalized_name
        and normalized_name not in {"tools", "model"}
    ):
        return None
    status: TraceStatus = {
        "on_chain_start": "running",
        "on_chain_end": "completed",
        "on_chain_error": "failed",
    }[event_name]
    return "stage", status


def normalize_event(event: Any, sequence: int) -> Iterator[TraceEvent]:
    """Convert one LangGraph v2 event into zero or more stable trace events."""
    if not isinstance(event, Mapping):
        return []
    event_name = event.get("event")
    if not isinstance(event_name, str):
        return []
    data = event.get("data")
    if not isinstance(data, Mapping):
        return []
    name = event.get("name")
    name = str(name) if name is not None else None
    run_id, parent_run_id = _run_ids(event)
    metadata = _event_metadata(event)

    if event_name == "on_chat_model_stream":
        chunk = data.get("chunk")
        for offset, segment in enumerate(content_segments(getattr(chunk, "content", ""))):
            yield_event = TraceEvent(
                sequence=sequence + offset,
                kind=segment.kind,
                content=segment.content,
                status=None,
                run_id=run_id,
                parent_run_id=parent_run_id,
                metadata=metadata,
            )
            yield yield_event
        return

    tool_kind = _EVENT_TO_KIND.get(event_name)
    if tool_kind is not None:
        tool_input = _tool_input(data)
        output = data.get("output") if tool_kind == "tool_end" else None
        error = data.get("error") if tool_kind == "tool_error" else None
        content = _command_text(name, tool_input)
        if content is not None:
            content = _redact_text(content)
        if tool_kind == "tool_error":
            content = _safe_text(error) if error is not None else "Tool failed"
        yield TraceEvent(
            sequence=sequence,
            kind=tool_kind,
            name=name,
            content=content,
            input=safe_value(tool_input),
            output=safe_value(output if tool_kind == "tool_end" else error),
            status={"tool_start": "running", "tool_end": "completed", "tool_error": "failed"}[tool_kind],
            run_id=run_id,
            parent_run_id=parent_run_id,
            metadata=metadata,
        )
        return

    stage = _stage_event_kind(event_name, name)
    if stage is not None:
        kind, status = stage
        input_value = data.get("input")
        output_value = data.get("output")
        error_value = data.get("error")
        content_value = _safe_text(error_value) if status == "failed" else None
        yield TraceEvent(
            sequence=sequence,
            kind=kind,
            name=name,
            content=content_value,
            input=safe_value(input_value),
            output=safe_value(output_value if status != "failed" else error_value),
            status=status,
            run_id=run_id,
            parent_run_id=parent_run_id,
            metadata=metadata,
        )


def trace_to_dict(event: TraceEvent) -> dict[str, Any]:
    """Return a safe JSON-compatible dictionary for a trace event."""
    return safe_value(asdict(event))


def trace_to_json(events: Sequence[TraceEvent]) -> str:
    """Serialize trace events in their stable sequence order."""
    ordered = sorted(events, key=lambda event: event.sequence)
    return json.dumps([trace_to_dict(event) for event in ordered], ensure_ascii=False)


def trace_from_json(payload: str | None) -> list[TraceEvent]:
    """Deserialize a trace payload, returning an empty list for unusable data."""
    if not payload:
        return []
    try:
        raw_events = json.loads(payload)
    except TypeError, ValueError:
        return []
    if not isinstance(raw_events, list):
        return []
    events: list[TraceEvent] = []
    for raw_event in raw_events:
        if not isinstance(raw_event, dict) or not isinstance(raw_event.get("sequence"), int):
            continue
        kind = raw_event.get("kind")
        if kind not in {"stage", "thinking", "text", "tool_start", "tool_end", "tool_error"}:
            continue
        events.append(
            TraceEvent(
                sequence=raw_event["sequence"],
                kind=kind,
                name=raw_event.get("name"),
                content=raw_event.get("content"),
                input=raw_event.get("input"),
                output=raw_event.get("output"),
                status=raw_event.get("status"),
                run_id=raw_event.get("run_id"),
                parent_run_id=raw_event.get("parent_run_id"),
                metadata=raw_event.get("metadata") if isinstance(raw_event.get("metadata"), dict) else {},
            )
        )
    return sorted(events, key=lambda event: event.sequence)

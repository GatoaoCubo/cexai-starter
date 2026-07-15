"""Cross-provider stream normalization helpers.

Providers PRODUCE a normalized ``Iterator[LlmStreamChunk]`` (each adapter maps
its SDK's native stream events to chunks). This module is the CONSUMER side:
shared helpers to reassemble streamed tool calls and to fold a chunk stream back
into a single ``LlmResponse`` -- the same shape ``call()`` returns -- so callers
get identical semantics whether they stream or not (spec P1 streaming edge case).

absorbs: 08_goose/provider-abstraction
"""

from __future__ import annotations

import json
from collections.abc import Iterable

from cexai.foundation._shared.errors import NormalizationError
from cexai.foundation._shared.types import (
    LlmResponse,
    LlmStreamChunk,
    ToolCall,
    ToolCallDelta,
    Usage,
)

__all__ = [
    "text_of",
    "finish_reason_of",
    "merge_tool_call_deltas",
    "aggregate_stream",
]


def text_of(chunks: Iterable[LlmStreamChunk]) -> str:
    """Concatenate the text deltas of ``chunks`` in arrival order."""
    return "".join(chunk.delta_text for chunk in chunks)


def finish_reason_of(chunks: Iterable[LlmStreamChunk]) -> str | None:
    """Return the last non-null ``finish_reason`` seen across ``chunks``."""
    reason: str | None = None
    for chunk in chunks:
        if chunk.finish_reason is not None:
            reason = chunk.finish_reason
    return reason


def merge_tool_call_deltas(
    deltas: Iterable[ToolCallDelta],
    *,
    indices: Iterable[int | None] | None = None,
) -> tuple[ToolCall, ...]:
    """Reassemble complete ``ToolCall``s from an ordered stream of partial deltas.

    Grouping rule (provider-agnostic): a delta carrying a non-null ``id`` that
    differs from the current call's id opens a new call; a delta with ``id``
    null normally extends the call in progress (continuation fragment, per the
    OpenAI/Anthropic contract where only the first fragment of a call carries
    an id). ``arguments_delta`` fragments are concatenated in order, then
    JSON-decoded once the stream is exhausted.

    ``indices`` (optional, aligned 1:1 with ``deltas`` by position -- e.g. the
    enclosing ``LlmStreamChunk.index``) disambiguates providers that emit
    MULTIPLE parallel tool calls with ``id=None`` (Ollama has no per-call
    ids at all). When supplied, an ``id=None`` delta whose index differs from
    the call in progress's index opens a NEW call instead of being folded into
    it -- this is what stops two distinct parallel Ollama tool calls from
    concatenating their argument JSON into one corrupt call. When ``indices``
    is omitted, grouping falls back to id-only (previous behavior), so this is
    purely additive: existing callers that pass no ``indices`` are unaffected.
    """
    idx_iter = iter(indices) if indices is not None else None
    accumulators: list[dict] = []
    current: dict | None = None
    for delta in deltas:
        idx = next(idx_iter, None) if idx_iter is not None else None
        starts_new = (delta.id is not None and (current is None or delta.id != current["id"])) or (
            delta.id is None
            and (
                current is None
                or (idx is not None and current["index"] is not None and idx != current["index"])
            )
        )
        if starts_new:
            current = {"id": delta.id or "", "name": delta.name or "", "args": "", "index": idx}
            accumulators.append(current)
        else:
            if delta.name:
                current["name"] = delta.name
            if current["index"] is None:
                current["index"] = idx
        if delta.arguments_delta:
            current["args"] += delta.arguments_delta

    calls: list[ToolCall] = []
    for acc in accumulators:
        raw_args = acc["args"]
        if raw_args.strip():
            try:
                arguments = json.loads(raw_args)
            except json.JSONDecodeError as exc:
                raise NormalizationError(f"streamed tool-call arguments are not valid JSON: {exc}") from exc
        else:
            arguments = {}
        calls.append(ToolCall(id=acc["id"], name=acc["name"], arguments=arguments))
    return tuple(calls)


def aggregate_stream(
    chunks: Iterable[LlmStreamChunk],
    *,
    model: str,
    provider: str,
    usage: Usage | None = None,
) -> LlmResponse:
    """Fold a chunk stream into one ``LlmResponse`` (text + reassembled tools +
    terminal finish_reason). ``model``/``provider`` are supplied by the caller
    because chunks do not carry them; ``usage`` defaults to a zero counter when
    the provider does not emit token accounting mid-stream."""
    text_parts: list[str] = []
    deltas: list[ToolCallDelta] = []
    delta_indices: list[int | None] = []
    finish_reason: str | None = None
    for chunk in chunks:
        if chunk.delta_text:
            text_parts.append(chunk.delta_text)
        if chunk.tool_call_delta is not None:
            deltas.append(chunk.tool_call_delta)
            delta_indices.append(chunk.index)
        if chunk.finish_reason is not None:
            finish_reason = chunk.finish_reason
    return LlmResponse(
        text="".join(text_parts),
        finish_reason=finish_reason,
        usage=usage if usage is not None else Usage(0, 0, 0),
        model=model,
        provider=provider,
        tool_calls=merge_tool_call_deltas(deltas, indices=delta_indices),
    )

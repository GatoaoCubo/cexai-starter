"""Tool-call schema normalizer -- the hub-and-spoke translator (FR-003, SC-004).

The canonical ``ToolCallSchema`` is the HUB; each provider's native
tool/function-declaration format is a SPOKE. ``to_provider_tools`` converts
canonical tool definitions into a provider's native tool list;
``from_provider_tool_calls`` converts a provider's native tool material back to
canonical ``ToolCall`` values. It accepts either the tool DEFINITIONS echoed by
``to_provider_tools`` (the SC-004 round-trip case) or the tool-USE/call objects a
live response carries -- both expose name + parameters/arguments, and both are
recovered losslessly.

The SC-004 invariant the contract test asserts:
    for every supported provider p,
    from_provider_tool_calls(p, to_provider_tools(p, schemas))
    preserves each schema's ``name`` and ``parameters`` with zero loss.

absorbs: 08_goose/tool-call-normalizer
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from cexai.foundation._shared.errors import NormalizationError
from cexai.foundation._shared.types import ToolCall, ToolCallSchema

__all__ = ["to_provider_tools", "from_provider_tool_calls", "supported_providers"]

# v1 provider set per spec FR-002. Kept sorted for stable enumeration.
_SUPPORTED: tuple[str, ...] = ("anthropic", "google", "ollama", "openai")


def supported_providers() -> tuple[str, ...]:
    """Return the providers the normalizer can translate (v1 set, sorted)."""
    return _SUPPORTED


# --------------------------------------------------------------------------- #
# Public API                                                                    #
# --------------------------------------------------------------------------- #
def to_provider_tools(provider: str, tools: tuple[ToolCallSchema, ...]) -> list[dict]:
    """Translate canonical tool definitions to ``provider``'s native tool list."""
    encoder = _TO.get(provider)
    if encoder is None:
        raise NormalizationError(f"cannot translate tools for unknown provider {provider!r}")
    return [encoder(tool) for tool in tools]


def from_provider_tool_calls(provider: str, native: object) -> tuple[ToolCall, ...]:
    """Translate a provider's native tool material to canonical ``ToolCall``s.

    ``native`` may be a list/tuple of native items, a single item, or ``None``.
    Each item may be a tool DEFINITION (round-trip) or a tool-USE object (live
    response); the per-provider decoder recovers name + arguments from either.
    """
    decoder = _FROM.get(provider)
    if decoder is None:
        raise NormalizationError(f"cannot parse tool calls for unknown provider {provider!r}")
    return tuple(decoder(item) for item in _as_items(native))


# --------------------------------------------------------------------------- #
# Encoders: canonical ToolCallSchema -> native tool definition                  #
# --------------------------------------------------------------------------- #
def _to_anthropic(tool: ToolCallSchema) -> dict:
    return {"name": tool.name, "description": tool.description, "input_schema": _plain(tool.parameters)}


def _to_openai(tool: ToolCallSchema) -> dict:
    return {
        "type": "function",
        "function": {"name": tool.name, "description": tool.description, "parameters": _plain(tool.parameters)},
    }


def _to_google(tool: ToolCallSchema) -> dict:
    return {"name": tool.name, "description": tool.description, "parameters": _plain(tool.parameters)}


def _to_ollama(tool: ToolCallSchema) -> dict:
    # Ollama mirrors the OpenAI function-tool shape.
    return {
        "type": "function",
        "function": {"name": tool.name, "description": tool.description, "parameters": _plain(tool.parameters)},
    }


# --------------------------------------------------------------------------- #
# Decoders: native item -> canonical ToolCall (name + arguments)                #
# Each decoder reads the definition shape (``*_schema``/``parameters``) when     #
# present, otherwise the call shape (``input``/``arguments``/``args``).          #
# --------------------------------------------------------------------------- #
def _from_anthropic(item: object) -> ToolCall:
    data = _as_mapping(item)
    params = data.get("input_schema")
    if params is None:
        params = data.get("input", {})
    return ToolCall(id=_str_id(data.get("id")), name=str(data.get("name", "")), arguments=_plain(params or {}))


def _from_openai(item: object) -> ToolCall:
    data = _as_mapping(item)
    function = _as_mapping(data.get("function", {}))
    params = function.get("parameters")
    if params is None:
        params = _decode_arguments(function.get("arguments", {}))
    return ToolCall(id=_str_id(data.get("id")), name=str(function.get("name", "")), arguments=_plain(params or {}))


def _from_google(item: object) -> ToolCall:
    data = _as_mapping(item)
    params = data.get("parameters")
    if params is None:
        params = data.get("args", {})
    return ToolCall(id=_str_id(data.get("id")), name=str(data.get("name", "")), arguments=_plain(params or {}))


def _from_ollama(item: object) -> ToolCall:
    data = _as_mapping(item)
    function = _as_mapping(data.get("function", {}))
    params = function.get("parameters")
    if params is None:
        params = _decode_arguments(function.get("arguments", {}))
    return ToolCall(id=_str_id(data.get("id")), name=str(function.get("name", "")), arguments=_plain(params or {}))


_TO = {"anthropic": _to_anthropic, "openai": _to_openai, "google": _to_google, "ollama": _to_ollama}
_FROM = {"anthropic": _from_anthropic, "openai": _from_openai, "google": _from_google, "ollama": _from_ollama}


# --------------------------------------------------------------------------- #
# Internal helpers                                                              #
# --------------------------------------------------------------------------- #
def _as_items(native: object) -> list:
    if native is None:
        return []
    if isinstance(native, Mapping):
        return [native]
    if isinstance(native, (list, tuple)):
        return list(native)
    try:
        return list(native)  # type: ignore[arg-type]
    except TypeError:
        return [native]


def _as_mapping(obj: object) -> Mapping[str, Any]:
    if isinstance(obj, Mapping):
        return obj
    # Best-effort read of a native SDK object via its known attributes. Providers
    # in this package pre-convert SDK objects to dicts, so this is purely defensive.
    keys = ("id", "name", "input", "input_schema", "parameters", "args", "arguments", "function", "type")
    return {key: getattr(obj, key) for key in keys if hasattr(obj, key)}


def _decode_arguments(value: object) -> Mapping[str, Any] | dict:
    """OpenAI/Ollama call arguments arrive as a JSON string or a mapping."""
    if isinstance(value, str):
        if not value.strip():
            return {}
        try:
            return json.loads(value)
        except json.JSONDecodeError as exc:
            raise NormalizationError(f"invalid tool-call arguments JSON: {exc}") from exc
    if isinstance(value, Mapping):
        return dict(value)
    return value or {}  # type: ignore[return-value]


def _plain(value: Any) -> Any:
    """Deep-copy mappings/sequences to plain JSON-shaped containers so native
    payloads are serializable and round-trip equality is structural, not by
    identity (the frozen contract hands us read-only MappingProxyType values)."""
    if isinstance(value, Mapping):
        return {key: _plain(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(val) for val in value]
    return value


def _str_id(value: object) -> str:
    return str(value) if value else ""

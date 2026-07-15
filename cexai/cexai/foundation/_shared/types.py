"""Frozen type contracts for the CEXAI foundation -- the linchpin module.

These names and shapes are FROZEN for the whole CEXAI_ASSIMILATION mission.
Every later wave (W1 provider implementations, W2 mcp/tracing, W3 invocation)
imports these symbols and MUST NOT change their names or fields. If a shape
must evolve, that is a versioned, peer-reviewed change -- not an in-flight edit.

Design constraints (Article VIII -- Anti-Abstraction):
  * stdlib typing only -- NO pydantic in this hot path.
  * every value type is an immutable ``@dataclass(frozen=True, slots=True)``.
  * collection fields are tuples / read-only mappings so instances are safely
    shareable across threads and providers without defensive copying.

Spec provenance: cexai-specs/08_goose/spec.md (User Story P1, FR-001..003,
SC-001/SC-004) and v01_sprint_plan.md task T010.

absorbs: 08_goose/provider-abstraction
absorbs: 08_goose/tool-call-normalizer
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Literal, Protocol, runtime_checkable

__all__ = [
    "Role",
    "Message",
    "ToolCallSchema",
    "ToolCall",
    "ToolCallDelta",
    "Usage",
    "LlmRequest",
    "LlmResponse",
    "LlmStreamChunk",
    "LlmProvider",
]

# Immutable empty mapping -- safe shared default for provider_options. A frozen
# dataclass cannot take a dict default (mutable); MappingProxyType is read-only.
_EMPTY_OPTIONS: Mapping[str, Any] = MappingProxyType({})

# Canonical chat role. Providers normalize their own role vocabularies to this.
Role = Literal["system", "user", "assistant", "tool"]


@dataclass(frozen=True, slots=True)
class Message:
    """One chat message. ``content`` is either plain text OR an ordered tuple of
    multimodal blocks (each block a provider-agnostic mapping, e.g. an image or
    document part). ``role`` is a ``Role`` value, kept as ``str`` so providers
    may carry extensions without breaking the contract."""

    role: str
    content: str | tuple[Mapping[str, Any], ...]


@dataclass(frozen=True, slots=True)
class ToolCallSchema:
    """Canonical JSON-Schema tool DEFINITION -- the normalizer target. Each
    provider's native tool/function-declaration format is translated to and
    from this single shape (SC-004: zero translation errors)."""

    name: str
    description: str
    parameters: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class ToolCall:
    """A tool use REQUESTED by the model in a response. ``arguments`` is the
    parsed argument object (already JSON-decoded)."""

    id: str
    name: str
    arguments: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class ToolCallDelta:
    """A streaming partial of a tool call. Any field may be ``None`` while the
    provider has not yet emitted that fragment; ``arguments_delta`` is the raw
    argument-JSON fragment to be concatenated by the stream consumer."""

    id: str | None
    name: str | None
    arguments_delta: str | None


@dataclass(frozen=True, slots=True)
class Usage:
    """Token accounting for a single call. Providers map their own usage fields
    onto these three counters."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass(frozen=True, slots=True)
class LlmRequest:
    """A provider-agnostic request. ``tools`` are offered tool definitions;
    ``provider_options`` is an escape hatch for provider-specific knobs that do
    not belong in the portable contract (kept read-only)."""

    model: str
    messages: tuple[Message, ...]
    tools: tuple[ToolCallSchema, ...] = ()
    temperature: float | None = None
    max_tokens: int | None = None
    stream: bool = False
    provider_options: Mapping[str, Any] = _EMPTY_OPTIONS


@dataclass(frozen=True, slots=True)
class LlmResponse:
    """A normalized non-streaming response. ``raw`` carries the provider-native
    response object, opaque to the contract, for observability and escape
    hatches; consumers MUST NOT rely on its shape."""

    text: str
    finish_reason: str | None
    usage: Usage
    model: str
    provider: str
    tool_calls: tuple[ToolCall, ...] = ()
    raw: Any = None


@dataclass(frozen=True, slots=True)
class LlmStreamChunk:
    """One chunk of a normalized stream. ``index`` orders chunks within a single
    streamed response; ``finish_reason`` is set only on the terminal chunk."""

    delta_text: str = ""
    tool_call_delta: ToolCallDelta | None = None
    finish_reason: str | None = None
    index: int = 0


@runtime_checkable
class LlmProvider(Protocol):
    """The single interface every provider adapter implements (W1). It is a
    structural ``Protocol`` -- adapters need only match the shape, no base class
    required. ``runtime_checkable`` allows ``isinstance`` smoke checks.

    Note (founder taxonomy rule): the CEX *artifact kind* for a provider remains
    the canonical ``model_provider`` (P02). ``LlmProvider`` is a CODE construct
    (sanctioned by T010), NOT a new CEX kind. The kind<->code mapping is
    registered in W4, not here.
    """

    name: str

    def call(self, request: LlmRequest) -> LlmResponse:
        """Execute ``request`` and return a normalized response."""
        ...

    def call_stream(self, request: LlmRequest) -> Iterator[LlmStreamChunk]:
        """Execute ``request`` in streaming mode, yielding normalized chunks."""
        ...

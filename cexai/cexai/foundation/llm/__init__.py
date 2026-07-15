"""Unified multi-provider LLM abstraction -- the public facade (W1).

``cexai.foundation.llm.call(request)`` transparently dispatches to the configured
provider (Anthropic / OpenAI / Google / Ollama), returning a normalized
``LlmResponse``; ``call_stream`` yields normalized ``LlmStreamChunk``s. This is
FR-001/002/003 + SC-001/SC-004. The frozen contracts it builds on live in
``cexai.foundation._shared.types``; the tool-call ``normalizer`` unifies tool
schemas across providers.

Provider selection (v0.1, deliberately simple -- Article VIII):
    explicit ``provider=`` argument
    -> env ``CEXAI_PROVIDER``
    -> ``.cexai/providers.yaml`` key ``default:``
    -> ``"anthropic"``
An unknown provider name raises ``ProviderConfigError(name, "unknown provider")``.
The 4 built-ins self-register LAZILY by name on first ``get_provider`` -- importing
this package builds no SDK client and needs no credentials.

``register_provider`` is the test/extension seam: inject a fake or a v1.5 adapter
(Azure / Bedrock / OpenRouter) under any name without touching this module.

absorbs: 08_goose/provider-abstraction
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

from cexai.foundation._shared.errors import ProviderConfigError
from cexai.foundation._shared.types import (
    LlmProvider,
    LlmRequest,
    LlmResponse,
    LlmStreamChunk,
)

__all__ = [
    "call",
    "call_stream",
    "register_provider",
    "get_provider",
    "available_providers",
]

# The 4 built-in adapters, by canonical name. Sorted for stable enumeration.
_BUILTIN_NAMES: tuple[str, ...] = ("anthropic", "google", "ollama", "openai")

# Live registry of instantiated/registered providers. Empty until first use or
# an explicit register_provider call; built-ins fill in lazily by name.
_REGISTRY: dict[str, LlmProvider] = {}


# --------------------------------------------------------------------------- #
# Public API                                                                    #
# --------------------------------------------------------------------------- #
def call(request: LlmRequest, *, provider: str | None = None) -> LlmResponse:
    """Dispatch ``request`` to the resolved provider, returning a normalized
    ``LlmResponse``. ``provider`` overrides the configured default for this call."""
    return get_provider(_resolve_name(provider)).call(request)


def call_stream(request: LlmRequest, *, provider: str | None = None) -> Iterator[LlmStreamChunk]:
    """Dispatch ``request`` in streaming mode, yielding normalized chunks."""
    return get_provider(_resolve_name(provider)).call_stream(request)


def register_provider(name: str, provider: LlmProvider) -> None:
    """Register (or override) the provider served under ``name``. The test/
    extension seam -- inject fakes or new adapters without editing this module."""
    _REGISTRY[name] = provider


def get_provider(name: str) -> LlmProvider:
    """Return the provider for ``name``, instantiating a built-in lazily on first
    request. Raises ``ProviderConfigError(name, "unknown provider")`` if unknown."""
    existing = _REGISTRY.get(name)
    if existing is not None:
        return existing
    provider = _instantiate_builtin(name)
    if provider is None:
        raise ProviderConfigError(name, "unknown provider")
    _REGISTRY[name] = provider
    return provider


def available_providers() -> tuple[str, ...]:
    """Return all provider names callable right now: the 4 built-ins plus any
    explicitly registered, sorted and de-duplicated."""
    return tuple(sorted(set(_BUILTIN_NAMES) | set(_REGISTRY)))


# --------------------------------------------------------------------------- #
# Provider selection + lazy built-in instantiation                              #
# --------------------------------------------------------------------------- #
def _resolve_name(explicit: str | None) -> str:
    if explicit:
        return explicit
    env = os.environ.get("CEXAI_PROVIDER")
    if env:
        return env
    configured = _default_from_config()
    if configured:
        return configured
    return "anthropic"


def _default_from_config() -> str | None:
    """Read the top-level ``default:`` key from ``.cexai/providers.yaml`` without
    a hard YAML dependency (the config is a flat key list in v0.1).

    Indentation-guarded (R-226): a line is only a candidate if it starts in
    column 0. Without this guard, a *nested* ``default:`` key (e.g. under a
    per-provider block) silently wins over -- or in the absence of a real
    top-level key, fabricates -- the provider selection, contradicting the
    "top-level default:" contract documented above.
    """
    path = Path(".cexai") / "providers.yaml"
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, ValueError):
        return None
    for line in text.splitlines():
        if line[:1].isspace():
            continue  # indented -- a nested key, not the top-level default:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("default:"):
            value = stripped.split(":", 1)[1].strip().strip("\"'")
            return value or None
    return None


def _instantiate_builtin(name: str) -> LlmProvider | None:
    """Import and construct a built-in adapter by name. The per-name import keeps
    the facade import cheap and credential-free: only the requested adapter's
    module loads, and even then no SDK client is built until its first call."""
    if name == "anthropic":
        from cexai.foundation.llm.providers.anthropic_provider import AnthropicProvider

        return AnthropicProvider()
    if name == "openai":
        from cexai.foundation.llm.providers.openai_provider import OpenAIProvider

        return OpenAIProvider()
    if name == "google":
        from cexai.foundation.llm.providers.google_provider import GoogleProvider

        return GoogleProvider()
    if name == "ollama":
        from cexai.foundation.llm.providers.ollama_provider import OllamaProvider

        return OllamaProvider()
    return None

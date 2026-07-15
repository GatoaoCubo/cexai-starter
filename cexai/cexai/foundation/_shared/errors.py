"""CEXAI exception hierarchy (foundation root + llm subtree).

Rooted at ``CexaiError`` so callers can catch the whole package with one except.
The llm subtree (``CexaiLlmError`` and descendants) covers provider config,
call, and normalization failures per spec User Story P1 acceptance scenario #3.

MCP errors (McpExtensionLoadError, IncompatibleExtensionVersionError) belong to
the mcp module and land in W2 -- they are intentionally NOT defined here.

Spec provenance: cexai-specs/08_goose/spec.md (P1 acceptance #3).

absorbs: 08_goose/provider-abstraction
"""

from __future__ import annotations

__all__ = [
    "CexaiError",
    "CexaiLlmError",
    "ProviderConfigError",
    "ProviderCallError",
    "NormalizationError",
]


class CexaiError(Exception):
    """Root of every CEXAI exception. Catch this to handle any package error."""


class CexaiLlmError(CexaiError):
    """Root of the llm subtree -- provider configuration, call, or normalization."""


class ProviderConfigError(CexaiLlmError):
    """A provider is misconfigured (e.g. missing or invalid API key).

    Raised per spec P1 acceptance #3. Carries the offending provider name and a
    human-readable reason as structured attributes so callers can branch on them
    without parsing the message.
    """

    def __init__(self, provider_name: str, reason: str) -> None:
        self.provider_name = provider_name
        self.reason = reason
        super().__init__(f"provider {provider_name!r} misconfigured: {reason}")


class ProviderCallError(CexaiLlmError):
    """A provider call failed at runtime (transport, API error, timeout)."""


class NormalizationError(CexaiLlmError):
    """A request or response could not be normalized to the canonical contract
    (e.g. an untranslatable tool-call schema)."""

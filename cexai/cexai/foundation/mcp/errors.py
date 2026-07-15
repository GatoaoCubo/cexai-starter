"""MCP subsystem exception hierarchy (W2).

Rooted at the package-wide ``CexaiError`` (defined in ``_shared.errors``) so a
caller can still catch the whole package with one except, while ``McpError``
lets a feature catch only extension-loading failures. These errors are
deliberately defined HERE, not in ``_shared.errors`` -- the shared module owns
only the llm subtree (W1); MCP errors land with the MCP code (W2).

Spec provenance: cexai-specs/08_goose/spec.md (User Story P2 acceptance #3 and
the version-mismatch edge case).

absorbs: 08_goose/mcp-extension-loader
"""

from __future__ import annotations

from cexai.foundation._shared.errors import CexaiError

__all__ = [
    "McpError",
    "McpExtensionLoadError",
    "IncompatibleExtensionVersionError",
]


class McpError(CexaiError):
    """Root of the MCP subtree -- extension discovery, loading, or versioning."""


class McpExtensionLoadError(McpError):
    """An MCP extension could not be discovered or started (bad config, bad
    binary, transport failure). Raised per spec P2 acceptance #3; the feature
    aborts. Carries the offending ``extension`` name and a human-readable
    ``reason`` as structured attributes so callers branch without parsing text.
    """

    def __init__(self, extension: str, reason: str) -> None:
        self.extension = extension
        self.reason = reason
        super().__init__(f"mcp extension {extension!r} failed to load: {reason}")


class IncompatibleExtensionVersionError(McpError):
    """A connected extension reports a server version outside the feature's
    declared semver range. Raised per the spec P2 version-mismatch edge case;
    the loader refuses the extension rather than registering possibly-wrong
    tools. Carries ``declared`` (the requested range) and ``found`` (the actual
    server version) for diagnostics.
    """

    def __init__(self, extension: str, declared: str, found: str) -> None:
        self.extension = extension
        self.declared = declared
        self.found = found
        super().__init__(
            f"mcp extension {extension!r} version {found!r} does not satisfy "
            f"declared range {declared!r}"
        )

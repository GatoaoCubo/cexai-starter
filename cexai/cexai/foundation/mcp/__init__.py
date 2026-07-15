"""MCP extension discovery, loading, and tool registry (W2).

Implements spec User Story P2: a feature declares its required extensions and the
runtime discovers, validates (semver), connects, and namespaces their tools as
``<extension>.<tool>``. ``mcp_extension`` EXTENDS the existing CEX ``mcp_server``
kind (name, version_range, transport) -- it is not a new kind; kind registration
is W4.

Public surface:
    discover_extensions(declared)            -> tuple[ExtensionSpec, ...]
    load_extension(spec, *, registry, ...)   -> None   (connect + register tools)
    McpRegistry                              -- namespaced tool registry
    detect_collisions(registry)              -> tuple[str, ...]  (colliding bare names)
    version_satisfies(range, version)        -> bool   (semver gate, also used internally)
    ExtensionSpec / McpToolDef               -- the data records
    McpConnector / McpConnection             -- the synchronous transport seam
    McpError / McpExtensionLoadError / IncompatibleExtensionVersionError

MCP-specific errors are defined in this package (``mcp.errors``), NOT in
``_shared.errors`` -- they land with the MCP code in W2.

absorbs: 08_goose/mcp-extension-loader
"""

from __future__ import annotations

from cexai.foundation.mcp.collision import detect_collisions
from cexai.foundation.mcp.discovery import (
    ExtensionSpec,
    VALID_TRANSPORTS,
    discover_extensions,
    version_satisfies,
)
from cexai.foundation.mcp.errors import (
    IncompatibleExtensionVersionError,
    McpError,
    McpExtensionLoadError,
)
from cexai.foundation.mcp.loader import (
    McpConnection,
    McpConnector,
    McpToolDef,
    load_extension,
)
from cexai.foundation.mcp.registry import McpRegistry

__all__ = [
    "discover_extensions",
    "load_extension",
    "McpRegistry",
    "detect_collisions",
    "version_satisfies",
    "ExtensionSpec",
    "McpToolDef",
    "McpConnection",
    "McpConnector",
    "VALID_TRANSPORTS",
    "McpError",
    "McpExtensionLoadError",
    "IncompatibleExtensionVersionError",
]

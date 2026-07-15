"""MCP extension loader: connect, version-check, register tools (W2).

``load_extension`` is the synchronous entry point. It does NOT talk to the
async ``mcp`` SDK directly; it talks to an ``McpConnector`` -- a thin
synchronous seam (Article VIII: one thin wrapper, no wrapper-on-wrapper). In
production W4 injects an SDK-backed connector carrying each extension's launch
coordinates; in tests an in-process FAKE connector returns a canned tool list,
so the suite needs no network and no subprocess (spec SC-002 is a structural
gate, not a live benchmark).

Flow per extension (spec User Story P2):
  1. ``connector.connect(spec)``  -> an open ``McpConnection`` (or it raises).
  2. semver gate: if the server reports a version outside ``spec.version_range``
     -> ``IncompatibleExtensionVersionError`` (refuse; register nothing).
  3. register every advertised tool under ``<extension>.<tool>``.
Any non-CEXAI exception from ``connect`` is wrapped as ``McpExtensionLoadError``
so a feature catches one typed error and aborts (acceptance #3).

absorbs: 08_goose/mcp-extension-loader
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol

from cexai.foundation.mcp.discovery import ExtensionSpec, version_satisfies
from cexai.foundation.mcp.errors import (
    IncompatibleExtensionVersionError,
    McpError,
    McpExtensionLoadError,
)
from cexai.foundation.mcp.registry import McpRegistry

__all__ = [
    "McpToolDef",
    "McpConnection",
    "McpConnector",
    "load_extension",
]


@dataclass(frozen=True, slots=True)
class McpToolDef:
    """One tool advertised by a connected extension: its bare ``name`` and its
    JSON-Schema input shape (the MCP ``inputSchema``). Immutable so a connection
    snapshot is safely shareable."""

    name: str
    schema: Mapping[str, Any]


class McpConnection(Protocol):
    """An already-open connection to one extension. ``server_version`` is the
    server's reported semver (or ``None`` if it advertises none)."""

    server_version: str | None

    def list_tools(self) -> tuple[McpToolDef, ...]:
        """Return the tools this extension advertises."""
        ...


class McpConnector(Protocol):
    """The synchronous seam. Real impl (W4) drives the async ``mcp`` SDK; the
    test fake returns a canned ``McpConnection``."""

    def connect(self, spec: ExtensionSpec) -> McpConnection:
        """Open a connection for ``spec`` (may raise on a start failure)."""
        ...


def load_extension(
    spec: ExtensionSpec,
    *,
    registry: McpRegistry,
    connector: McpConnector | None = None,
    allow_override: bool = False,
) -> None:
    """Discover, version-check, and register one extension's tools into
    ``registry``. ``connector`` overrides the default (always supply one in v0.1
    -- see ``_DefaultConnector``). ``allow_override=True`` lets a tool replace an
    already-registered qualified name (the registry logs a WARN)."""
    active = connector if connector is not None else _default_connector()

    try:
        connection = active.connect(spec)
    except McpError:
        raise  # already a typed MCP error (incl. the default-connector guard)
    except Exception as exc:  # bad config / bad binary / transport failure
        raise McpExtensionLoadError(spec.name, str(exc)) from exc

    found = getattr(connection, "server_version", None)
    if found is not None and not version_satisfies(spec.version_range, found):
        raise IncompatibleExtensionVersionError(spec.name, spec.version_range, found)

    for tool in connection.list_tools():
        registry.register_tool(spec.name, tool.name, dict(tool.schema), override=allow_override)


# --------------------------------------------------------------------------- #
# Default connector -- the W4 seam                                              #
# --------------------------------------------------------------------------- #
class _DefaultConnector:
    """Placeholder for the SDK-backed connector wired in W4.

    The frozen v0.1 ``ExtensionSpec`` carries only {name, version_range,
    transport} -- it has no launch coordinates (command/args/env for stdio, URL
    for http), so a live ``mcp`` ClientSession cannot be opened from a spec
    alone. W4 integration extends the wiring with those coordinates and a real
    connector. Until then, v0.1 callers MUST inject a ``connector=`` (the fake in
    tests; an application-provided one in features). This raises a clear, typed
    error rather than pretending to connect.
    """

    def connect(self, spec: ExtensionSpec) -> McpConnection:  # pragma: no cover - W4 seam
        raise McpExtensionLoadError(
            spec.name,
            "no live MCP transport configured in v0.1; inject a connector= "
            "(W4 wires the mcp-SDK-backed connector with launch coordinates)",
        )


_DEFAULT_CONNECTOR = _DefaultConnector()


def _default_connector() -> McpConnector:  # pragma: no cover - W4 seam
    return _DEFAULT_CONNECTOR

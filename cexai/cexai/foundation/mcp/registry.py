"""In-memory MCP tool registry with ``<extension>.<tool>`` namespacing (W2).

A feature's loaded extensions register their tools here. Namespacing is the
collision-avoidance default (spec FR-005): two extensions may each declare a
``search`` tool and both survive as ``ext_a.search`` / ``ext_b.search``. An
EXPLICIT override of an already-registered qualified name is the only case that
mutates an existing entry, and it is always logged at WARN (Article V:
observable, no silent state change).

absorbs: 08_goose/mcp-extension-loader
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

__all__ = ["McpRegistry"]

_logger = logging.getLogger("cexai.foundation.mcp.registry")


class McpRegistry:
    """Maps fully-qualified ``<extension>.<tool>`` names to tool schemas.

    Also keeps a bare-name index (tool_name -> the extensions that declared it)
    so ``detect_collisions`` can report cross-extension name clashes without
    re-deriving them from the qualified keys."""

    def __init__(self) -> None:
        self._tools: dict[str, dict] = {}
        self._bare: dict[str, list[str]] = {}

    def register_tool(
        self,
        extension: str,
        tool_name: str,
        schema: Mapping[str, Any],
        *,
        override: bool = False,
    ) -> None:
        """Register ``tool_name`` from ``extension`` under ``<extension>.<tool>``.

        First registration of a qualified name wins. A repeat registration of the
        SAME qualified name is either an explicit ``override`` (replace + WARN) or
        an accidental duplicate (keep first + WARN) -- never a silent clobber."""
        qualified = f"{extension}.{tool_name}"
        if qualified in self._tools:
            if override:
                _logger.warning("explicit override of already-registered tool %r", qualified)
                self._tools[qualified] = dict(schema)
            else:
                _logger.warning("duplicate registration of tool %r ignored (first wins)", qualified)
            return
        self._tools[qualified] = dict(schema)
        self._bare.setdefault(tool_name, [])
        if extension not in self._bare[tool_name]:
            self._bare[tool_name].append(extension)

    def tools(self) -> tuple[str, ...]:
        """All fully-qualified tool names, sorted for stable enumeration."""
        return tuple(sorted(self._tools))

    def get(self, qualified_name: str) -> dict:
        """Return the schema registered under ``qualified_name``.

        Raises ``KeyError`` if no such tool is registered (callers that prefer a
        typed miss can catch it -- v0.1 keeps the stdlib contract)."""
        return self._tools[qualified_name]

    def bare_name_index(self) -> Mapping[str, tuple[str, ...]]:
        """Map each bare tool name to the tuple of extensions that declared it.
        The collision detector reads this; a name with >= 2 owners collides."""
        return {name: tuple(exts) for name, exts in self._bare.items()}

"""Tool-name collision detection across loaded MCP extensions (W2).

Namespacing (registry) already PREVENTS direct collisions -- two extensions that
each declare ``search`` coexist as ``ext_a.search`` / ``ext_b.search``. This
module REPORTS the bare names that more than one extension declared, so a feature
(or a governance gate) can surface the ambiguity to the operator. Reporting is
pure + side-effect-free; the WARN on an explicit override lives in the registry.

Spec provenance: cexai-specs/08_goose/spec.md (FR-005, P2 collision edge case).

absorbs: 08_goose/mcp-extension-loader
"""

from __future__ import annotations

from cexai.foundation.mcp.registry import McpRegistry

__all__ = ["detect_collisions"]


def detect_collisions(registry: McpRegistry) -> tuple[str, ...]:
    """Return the bare tool names declared by two or more extensions, sorted.

    An empty tuple means every tool name is owned by exactly one extension."""
    index = registry.bare_name_index()
    return tuple(sorted(name for name, owners in index.items() if len(owners) >= 2))

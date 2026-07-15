"""Structural query over a built knowledge graph (06 US P1/P2, FR-004).

The query surface is a small, deterministic PATTERN dialect (a Cypher front-end
is the documented v0.2-W3 successor -- the spec marks Cypher 'provisional'):

  ``"<relation> of <seed>"``
      Traverse ``<relation>`` edges OUT of the resolved seed node(s); the matched
      targets sit one hop away. Special cases:
        * ``imports of X``      -- X a file: its imports; X a module: its importers.
        * ``definitions of Y``  -- every ``function``/``class`` named Y across all
                                   files (polymorphism, US P1 #2), plus a file
                                   seed's own definitions.
        * ``neighborhood of X`` -- the N-hop out-neighborhood of X (default 2,
                                   ``hops=`` configurable) -- US P2 #2.
  ``"<bare token>"``
      Resolve to node(s) by id / file path / symbol name (a hop-0 lookup).

Seeds resolve flexibly: an exact node id, a file by ``path`` (full, suffix, or
basename), or any node by its ``name`` attr -- so a caller can write
``imports of pkg/core.py`` without knowing the ``file:`` id prefix.

Hits are ranked ``score = 1 / (hops + 1)`` (direct matches first), ties broken by
node id for run-to-run determinism. Staleness is the caller's concern: this
module exposes ``STALE_MARKER`` to prefix results with, while
``KnowledgeGraph.query(..., require_fresh=True)`` raises ``GraphStaleError``.

absorbs: 06_graphify/code-graph
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from cexai.memory._shared.types import GraphHit

if TYPE_CHECKING:
    from cexai.memory.graph.store import KnowledgeGraph

__all__ = ["run_query", "STALE_MARKER"]

# Per 06 FR-005 / US P1 #3: results computed against a changed source are flagged
# with this marker so a consumer can surface "[STALE] ..." and suggest a reindex.
STALE_MARKER = "[STALE]"

_DEFINITION_RELS = frozenset({"definition", "definitions", "def", "defs"})
_NEIGHBORHOOD_RELS = frozenset({"neighborhood", "neighbourhood", "neighbors", "neighbours", "context"})


def run_query(graph: KnowledgeGraph, pattern: str, *, hops: int = 2) -> tuple[GraphHit, ...]:
    """Execute a pattern query; return ranked ``GraphHit``s (best first)."""
    text = pattern.strip()
    marker = " of "
    lowered = text.lower()
    if marker in lowered:
        split_at = lowered.index(marker)
        relation = text[:split_at].strip().lower()
        seed = text[split_at + len(marker):].strip()
        return _relational(graph, relation, seed, hops)
    return _hits({node_id: 0 for node_id in _resolve(graph, text)})


# --------------------------------------------------------------------------- #
# Relation handlers                                                            #
# --------------------------------------------------------------------------- #
def _relational(graph: KnowledgeGraph, relation: str, seed: str, hops: int) -> tuple[GraphHit, ...]:
    seed_ids = _resolve(graph, seed)
    if relation in _NEIGHBORHOOD_RELS:
        return _neighborhood(graph, seed_ids, hops)
    if relation in _DEFINITION_RELS:
        return _definitions(graph, seed, seed_ids)
    if relation == "imports":
        return _imports(graph, seed, seed_ids)
    # Generic: outgoing edges of this exact type, one hop from each seed.
    found: dict[str, int] = {}
    for seed_id in seed_ids:
        for dst in graph.neighbors(seed_id, relation, "out"):
            found.setdefault(dst, 1)
    return _hits(found)


def _definitions(graph: KnowledgeGraph, seed: str, seed_ids: list[str]) -> tuple[GraphHit, ...]:
    found: dict[str, int] = {}
    # Symbol lookup: every function/class with this name, anywhere (polymorphism).
    for node in graph.nodes():
        if node.type in {"function", "class"} and node.attrs.get("name") == seed:
            found[node.id] = 0
    # File seed: that file's own definitions, one hop out.
    for seed_id in seed_ids:
        node = graph.get_node(seed_id)
        if node is not None and node.type == "file":
            for dst in graph.neighbors(seed_id, "defines", "out"):
                found.setdefault(dst, 1)
    return _hits(found)


def _imports(graph: KnowledgeGraph, seed: str, seed_ids: list[str]) -> tuple[GraphHit, ...]:
    found: dict[str, int] = {}
    resolved = list(seed_ids)
    # Allow a bare module name (e.g. "imports of os") even when no file seed hit.
    module_id = f"module:{seed}"
    if graph.get_node(module_id) is not None and module_id not in resolved:
        resolved.append(module_id)
    for seed_id in resolved:
        node = graph.get_node(seed_id)
        if node is None:
            continue
        if node.type == "module":
            for src in graph.neighbors(seed_id, "imports", "in"):  # files importing it
                found.setdefault(src, 1)
        else:  # treat as a file/importer: what it imports
            for dst in graph.neighbors(seed_id, "imports", "out"):
                found.setdefault(dst, 1)
    return _hits(found)


def _neighborhood(graph: KnowledgeGraph, seed_ids: list[str], hops: int) -> tuple[GraphHit, ...]:
    """Breadth-first OUT-neighborhood, recording each node's hop distance."""
    distance: dict[str, int] = {}
    frontier: list[str] = []
    for seed_id in seed_ids:
        if graph.get_node(seed_id) is not None and seed_id not in distance:
            distance[seed_id] = 0
            frontier.append(seed_id)
    depth = 0
    while frontier and depth < hops:
        depth += 1
        nxt: list[str] = []
        for node_id in frontier:
            for dst in graph.neighbors(node_id, None, "out"):
                if dst not in distance:
                    distance[dst] = depth
                    nxt.append(dst)
        frontier = nxt
    return _hits(distance)


# --------------------------------------------------------------------------- #
# Seed resolution + ranking                                                    #
# --------------------------------------------------------------------------- #
def _resolve(graph: KnowledgeGraph, seed: str) -> list[str]:
    """Map a seed token to node id(s): exact id, file by path/basename, or any
    node by ``name`` attr."""
    if graph.get_node(seed) is not None:
        return [seed]
    matches: list[str] = []
    for node in graph.nodes():
        path = node.attrs.get("path")
        if node.type == "file" and path and (path == seed or path.endswith("/" + seed) or path.split("/")[-1] == seed):
            matches.append(node.id)
        elif node.attrs.get("name") == seed:
            matches.append(node.id)
    return matches


def _hits(distance: dict[str, int]) -> tuple[GraphHit, ...]:
    hits = [GraphHit(node_id=node_id, score=1.0 / (hop + 1), hops=hop) for node_id, hop in distance.items()]
    hits.sort(key=lambda hit: (-hit.score, hit.node_id))
    return tuple(hits)

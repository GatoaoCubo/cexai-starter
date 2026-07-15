"""Knowledge graph store -- a pure-Python typed property graph (06 FR-001..005).

``KnowledgeGraph`` satisfies the FROZEN ``GraphStore`` protocol
(``cexai.memory._shared.types``): typed ``add_node`` / ``add_edge``, a string
``query`` returning ranked ``GraphHit``s, and ``is_stale`` source-change
detection. It also exposes the small accessor surface (``get_node``,
``out_edges``, ``neighbors``, removal + orphan GC) that ``build`` and ``query``
compose over.

BACKEND CHOICE (Article VIII -- Anti-Abstraction; FR-006 -- runs locally).
The in-memory backend is plain ``dict`` adjacency: zero dependencies, always
works, fully testable offline. ``networkx`` and ``DuckDB`` are listed as the
optional ``cexai[memory]`` extras; rather than ship a second, dependency-gated
code path that the offline suite cannot exercise, this store keeps ONE correct
path and treats those libraries as deferred scale upgrades (the SC-001..005
benchmark corpus that would justify them lands in v0.2-W3). ``persist`` / ``load``
give durable JSON round-trips today; a DuckDB property-table backend is the
documented lazy successor.

Node id convention (stable, prefix-typed so ``query`` can parse a seed):
  ``file:<relposix>``  ``module:<dotted>``  ``function:<relposix>:<name>``
  ``class:<relposix>:<name>``  ``doc:<wikilink>``  ``key:<relposix>:<name>``

absorbs: 06_graphify/code-graph
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from cexai.memory._shared.errors import GraphStaleError
from cexai.memory._shared.types import GraphEdge, GraphHit, GraphNode

__all__ = ["KnowledgeGraph"]


class KnowledgeGraph:
    """A typed, in-memory property graph implementing ``GraphStore``.

    Provenance (``_root`` + ``_manifest`` of ``relposix -> (size, sha1)``) is
    recorded by ``build`` so ``is_stale`` can re-scan the tree and incremental
    reindex can diff it. Construct empty, then populate via ``add_node`` /
    ``add_edge`` (the contract path) or via ``build_graph`` (the source-tree
    path)."""

    def __init__(self) -> None:
        self._nodes: dict[str, GraphNode] = {}
        self._out: dict[str, list[GraphEdge]] = {}
        self._in: dict[str, list[GraphEdge]] = {}
        self._root: str | None = None
        self._manifest: dict[str, tuple[int, str]] = {}

    # ----------------------------------------------------------------- #
    # GraphStore protocol                                                #
    # ----------------------------------------------------------------- #
    def add_node(self, n: GraphNode) -> None:
        """Add or replace a typed node (id is the identity key)."""
        self._nodes[n.id] = n
        self._out.setdefault(n.id, [])
        self._in.setdefault(n.id, [])

    def add_edge(self, e: GraphEdge) -> None:
        """Add a typed directed edge. Missing endpoints get a minimal stub node
        so a partial extraction never raises (defensive -- ``build`` adds real
        endpoint nodes first)."""
        for endpoint in (e.src, e.dst):
            if endpoint not in self._nodes:
                self.add_node(GraphNode(id=endpoint, type="unknown", attrs={}))
        self._out[e.src].append(e)
        self._in[e.dst].append(e)

    def query(
        self, cypher_or_pattern: str, *, hops: int = 2, require_fresh: bool = False
    ) -> tuple[GraphHit, ...]:
        """Run a pattern/Cypher-ish query (see ``query.run_query``). With
        ``require_fresh=True`` a stale index raises ``GraphStaleError`` (FR-005)
        instead of returning possibly-outdated hits."""
        if require_fresh and self.is_stale():
            raise GraphStaleError(
                "graph index is stale relative to its source tree; reindex before "
                "demanding fresh results"
            )
        from cexai.memory.graph.query import run_query  # lazy: avoid import cycle

        return run_query(self, cypher_or_pattern, hops=hops)

    def is_stale(self) -> bool:
        """True if any indexed file changed/was removed, or a new indexable file
        appeared, since the last build/reindex. False when no source is tracked
        (a hand-built contract graph)."""
        if self._root is None:
            return False
        from cexai.memory.graph.build import scan_manifest  # lazy: avoid cycle

        return scan_manifest(self._root) != self._manifest

    # ----------------------------------------------------------------- #
    # Accessors composed by build/query                                  #
    # ----------------------------------------------------------------- #
    def get_node(self, node_id: str) -> GraphNode | None:
        return self._nodes.get(node_id)

    def nodes(self) -> tuple[GraphNode, ...]:
        return tuple(self._nodes.values())

    def edges(self) -> tuple[GraphEdge, ...]:
        return tuple(edge for edges in self._out.values() for edge in edges)

    def out_edges(self, node_id: str, edge_type: str | None = None) -> tuple[GraphEdge, ...]:
        edges = self._out.get(node_id, ())
        if edge_type is None:
            return tuple(edges)
        return tuple(edge for edge in edges if edge.type == edge_type)

    def in_edges(self, node_id: str, edge_type: str | None = None) -> tuple[GraphEdge, ...]:
        edges = self._in.get(node_id, ())
        if edge_type is None:
            return tuple(edges)
        return tuple(edge for edge in edges if edge.type == edge_type)

    def neighbors(
        self, node_id: str, edge_type: str | None = None, direction: str = "out"
    ) -> tuple[str, ...]:
        """Adjacent node ids via ``direction`` ('out' | 'in') edges, optionally
        filtered by ``edge_type``."""
        edges = self.out_edges(node_id, edge_type) if direction == "out" else self.in_edges(node_id, edge_type)
        return tuple(edge.dst if direction == "out" else edge.src for edge in edges)

    def degree(self, node_id: str) -> int:
        return len(self._out.get(node_id, ())) + len(self._in.get(node_id, ()))

    def nodes_from_source(self, relposix: str) -> tuple[str, ...]:
        """Ids of every node extracted from one source file (file + its defs +
        its keys). Shared targets (module/doc) carry ``source=None`` and are
        intentionally excluded -- they are GC'd separately when orphaned."""
        return tuple(nid for nid, node in self._nodes.items() if node.source == relposix)

    # ----------------------------------------------------------------- #
    # Mutation used by incremental reindex                               #
    # ----------------------------------------------------------------- #
    def remove_node(self, node_id: str) -> None:
        """Remove a node and every edge incident to it (both directions)."""
        self._nodes.pop(node_id, None)
        for edge in self._out.pop(node_id, []):
            kept = [e for e in self._in.get(edge.dst, []) if e.src != node_id]
            self._in[edge.dst] = kept
        for edge in self._in.pop(node_id, []):
            kept = [e for e in self._out.get(edge.src, []) if e.dst != node_id]
            self._out[edge.src] = kept

    def remove_source(self, relposix: str) -> None:
        """Remove every node (and its edges) that originated from ``relposix``."""
        for node_id in self.nodes_from_source(relposix):
            self.remove_node(node_id)

    def gc_orphans(self) -> tuple[str, ...]:
        """Drop non-file nodes left with zero edges (e.g. a ``module`` whose only
        importer was just removed). File nodes are kept even when isolated."""
        removed: list[str] = []
        for node_id in list(self._nodes):
            if self._nodes[node_id].type == "file":
                continue
            if not self._out.get(node_id) and not self._in.get(node_id):
                self.remove_node(node_id)
                removed.append(node_id)
        return tuple(removed)

    # ----------------------------------------------------------------- #
    # Provenance (set by build) + durable persistence                    #
    # ----------------------------------------------------------------- #
    @property
    def root(self) -> str | None:
        return self._root

    @property
    def manifest(self) -> Mapping[str, tuple[int, str]]:
        return dict(self._manifest)

    def record_build(self, root: str | Path, manifest: Mapping[str, tuple[int, str]]) -> None:
        """Stamp the source root + per-file signatures captured at build time."""
        self._root = str(root)
        self._manifest = dict(manifest)

    def persist(self, path: str | Path) -> None:
        """Write a durable JSON snapshot (zero-dep). A DuckDB property-table
        backend is the documented lazy successor for large graphs (v0.2-W3)."""
        payload = {
            "root": self._root,
            "manifest": {rel: list(sig) for rel, sig in self._manifest.items()},
            "nodes": [
                {
                    "id": n.id,
                    "type": n.type,
                    "attrs": dict(n.attrs),
                    "source": n.source,
                    "parse_error": n.parse_error,
                }
                for n in self._nodes.values()
            ],
            "edges": [
                {"src": e.src, "dst": e.dst, "type": e.type, "attrs": dict(e.attrs)}
                for e in self.edges()
            ],
        }
        Path(path).write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> KnowledgeGraph:
        """Reconstruct a graph from a ``persist`` JSON snapshot."""
        payload: dict[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))
        graph = cls()
        for raw in payload["nodes"]:
            graph.add_node(
                GraphNode(
                    id=raw["id"],
                    type=raw["type"],
                    attrs=raw["attrs"],
                    source=raw["source"],
                    parse_error=raw["parse_error"],
                )
            )
        for raw in payload["edges"]:
            graph.add_edge(GraphEdge(src=raw["src"], dst=raw["dst"], type=raw["type"], attrs=raw["attrs"]))
        root = payload.get("root")
        manifest = {rel: tuple(sig) for rel, sig in payload.get("manifest", {}).items()}
        if root is not None:
            graph.record_build(root, manifest)
        return graph

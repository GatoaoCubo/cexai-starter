"""Graph subsystem -- structural query over a typed knowledge graph (v0.2-W1).

Implements the ``GraphStore`` protocol from ``cexai.memory._shared.types`` over
a pure-Python in-memory property graph, satisfying cexai-specs/06_graphify/spec.md
US P1 (FR-001..007). Nodes and edges are typed; queries accept a pattern dialect
(``"<relation> of <seed>"`` / N-hop ``neighborhood``); stale state is detectable
(FR-005 -- ``is_stale`` / ``GraphStaleError`` / ``STALE_MARKER``). Runs entirely
locally (FR-006); incremental re-index via ``build.reindex_graph`` (FR-007).

Heavy deps (duckdb, networkx, tree-sitter) are OPTIONAL
(``pip install cexai[memory]``) and treated as deferred scale upgrades: the
zero-dependency path here is the always-available, fully-tested default. The
SC-001..005 benchmark corpus + Cypher front-end land in v0.2-W3.

Public surface:
  * ``KnowledgeGraph`` -- the ``GraphStore`` implementation.
  * ``build_graph(root)`` -- index a source tree into a graph.
  * ``query(graph, pattern, *, hops=2)`` -- structural retrieval.

absorbs: 06_graphify/code-graph
"""

from __future__ import annotations

from cexai.memory.graph.build import build_graph
from cexai.memory.graph.query import run_query as query
from cexai.memory.graph.store import KnowledgeGraph

__all__ = ["KnowledgeGraph", "build_graph", "query"]

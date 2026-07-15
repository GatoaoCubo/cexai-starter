"""Structural validation for typed topologies (03 US1 + FR-006, SC-005 < 50ms).

Three cheap, dependency-free checks, in order:
  1. unknown variant           -> UnknownVariantError(variant, known_variants)  (FR-006)
  2. zero nodes                -> EmptyTopologyError                            (US1 edge)
  3. topological-policy cycle  -> CyclicTopologyError(cycle_path)               (US1 #3)

Check 3 runs for EVERY variant whose registry descriptor uses the
``topological`` order policy (``sequential``, ``hierarchical``, ``graph`` today
-- see ``registry.py``), not just the literal ``"graph"`` variant (R-222). The
interpreter's ``_execution_order`` uses the SAME Kahn-sort builder for all three;
a cyclic sequential/hierarchical topology would otherwise pass validation and
have its stuck nodes silently stranded into declared-order fallback with no
error. ``declared``-policy variants (``concurrent``, ``group_chat``) legitimately
allow cycles (e.g. a round-robin chat's wrap-around edge) and skip the check;
``synthesis`` (``mixture_of_agents``) is not a node-walk at all.

The cycle check is iterative (explicit-stack DFS with white/grey/black colouring)
so it cannot hit Python's recursion limit on a pathological graph, and it
reconstructs the offending node sequence for the error. Validation is the hot
path on every topology load, so it allocates only small dicts/lists and returns
as early as possible (SC-005).

absorbs: 03_swarms/topology
"""

from __future__ import annotations

from cexai.orchestration._shared.errors import (
    CyclicTopologyError,
    EmptyTopologyError,
    UnknownVariantError,
)
from cexai.orchestration._shared.types import Topology
from cexai.orchestration.topology.registry import KNOWN_VARIANTS, lookup

__all__ = ["validate_topology"]

_WHITE, _GREY, _BLACK = 0, 1, 2
_TOPOLOGICAL = "topological"


def validate_topology(topology: Topology) -> None:
    """Validate ``topology`` structurally. Returns ``None`` when valid; otherwise
    raises the frozen orchestration error for the first violation found."""
    if topology.variant not in KNOWN_VARIANTS:
        raise UnknownVariantError(topology.variant, KNOWN_VARIANTS)
    if not topology.nodes:
        raise EmptyTopologyError()
    if lookup(topology.variant).order_policy == _TOPOLOGICAL:
        cycle = _find_cycle(topology)
        if cycle is not None:
            raise CyclicTopologyError(cycle)
    return None


def _find_cycle(topology: Topology) -> tuple[str, ...] | None:
    """Return the first directed cycle as a node sequence (closing node repeated,
    e.g. ``("x", "y", "z", "x")``), or ``None`` if the graph is acyclic. Edges that
    reference an unknown node id are ignored (they are not part of any cycle)."""
    node_ids = [node.id for node in topology.nodes]
    adjacency: dict[str, list[str]] = {node_id: [] for node_id in node_ids}
    for edge in topology.edges:
        if edge.src in adjacency and edge.dst in adjacency:
            adjacency[edge.src].append(edge.dst)

    color = {node_id: _WHITE for node_id in node_ids}

    for root in node_ids:
        if color[root] != _WHITE:
            continue
        # Explicit-stack DFS. Each frame is [node, next-neighbour-index]; ``path``
        # is the current grey chain used to slice out a cycle when one is found.
        stack: list[list] = [[root, 0]]
        path: list[str] = [root]
        color[root] = _GREY
        while stack:
            node, index = stack[-1]
            neighbours = adjacency[node]
            if index < len(neighbours):
                stack[-1][1] = index + 1
                nxt = neighbours[index]
                state = color[nxt]
                if state == _GREY:
                    start = path.index(nxt)
                    return tuple(path[start:]) + (nxt,)
                if state == _WHITE:
                    color[nxt] = _GREY
                    stack.append([nxt, 0])
                    path.append(nxt)
            else:
                color[node] = _BLACK
                stack.pop()
                path.pop()
    return None

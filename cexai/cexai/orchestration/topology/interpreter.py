"""Generic topology interpreter (03 FR-003 / FR-004 / SC-004).

One executor walks ANY typed ``Topology``, regardless of variant. The variant
only selects an execution-order policy (from the registry); the traversal,
node-execution, and audit-trail emission are shared. This is the "generic
interpreter" of FR-003 -- adding a variant is a registry entry, not a new code
path.

Node execution is abstracted behind an injected ``NodeRunner`` callable so the
interpreter stays generic AND offline-testable (Article XIV): the default
``FakeNodeRunner`` returns a deterministic ``payload_ref`` with no live nucleus or
provider. Wiring real nucleus/provider dispatch behind this seam is a later
wave's concern.

Execution model (the audit trail, 03 US3 / SC-004):
  * Nodes execute in the variant's order policy -- ``topological`` (edge order) for
    sequential/hierarchical/graph, ``declared`` (node order) for concurrent/
    group_chat. Each node's runner receives the payload_refs of its already-run
    predecessors, so output of N feeds N+1.
  * The trail is ONE initial ``CoordinationEvent`` (``from_node=None``) for the
    entry node, then one event per declared edge. So ``len(events) == 1 + edges``
    and exactly one event has ``from_node=None`` (no phantom inputs). Catalog
    topologies are single-entry by construction.
  * ``mixture_of_agents`` is NOT a node-walk -- it fans the prompt to N distinct-
    provider workers and synthesizes. The interpreter detects its ``synthesis``
    order policy and routes it to the dedicated ``mixture_of_agents`` executor
    (v0.3-W2); the injected ``node_runner`` does not apply on that path (MoA
    dispatches to providers via ``cexai.foundation.llm``, not to nuclei).

Governance integration (v0.3-W3c, 05_agno US P1/P2/P3): governance enters through
OPTIONAL constructor params with safe defaults that reproduce today's behavior
EXACTLY -- the frozen ``run(topology) -> TopologyRun`` signature is unchanged.
  * RBAC (US P3 / SC-004/005): with BOTH an ``auth_guard`` and an ``auth_token``,
    ``run`` authorizes the ``dispatch`` operation at entry and raises
    ``RbacForbiddenError`` [403] on a denied role. No token == dev mode: the guard
    is never consulted -- zero overhead (FR-008).
  * HITL (US P2 / SC-003): with an ``approval_gate`` and a non-empty
    ``hitl_operations`` set, a node whose operation is tagged pauses for a verdict
    before it runs; ``denied`` -> ``ApprovalDeniedError``, ``timeout`` ->
    ``ApprovalTimeoutError``, ``approved`` proceeds. No gate / untagged node == no
    pause, behavior unchanged.
  * TRACING (US P1 / SC-001): with a ``tracer``, the walk opens a ``mission`` span
    and one child dispatch span per node (100% of dispatch ops get a span), and the
    completed ``TopologyRun`` (+ its span tree) is persisted to
    ``{root}/.cexai/topology/runs/{run_id}.json`` so ``topology audit <run_id>`` can
    reconstruct it. No tracer == no spans, no persistence, no I/O.

The tracer is used through the frozen ``Tracer`` Protocol only (``start_span`` +
``emit``); the guard / gate likewise through their frozen Protocols, so any
conforming implementation works and none is imported on the default path.

absorbs: 03_swarms/topology + 05_agno/governance-integration
"""

from __future__ import annotations

import json
import time
import uuid
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

from cexai.governance._shared.errors import (
    ApprovalDeniedError,
    ApprovalTimeoutError,
    RbacForbiddenError,
)
from cexai.governance._shared.types import (
    ApprovalGate,
    AuthGuard,
    AuthToken,
    Span,
    Tracer,
)
from cexai.orchestration._shared.types import (
    CoordinationEvent,
    Topology,
    TopologyNode,
    TopologyRun,
)
from cexai.orchestration.topology.mixture_of_agents import run_mixture_of_agents
from cexai.orchestration.topology.registry import TopologyRegistry
from cexai.orchestration.topology.validate import validate_topology

__all__ = ["NodeRunner", "FakeNodeRunner", "GenericTopologyInterpreter"]

# The dispatch span the tracer opens per node. ``dispatch`` is the default; a node
# may override via ``config['span_operation']`` to ``tool_call`` / ``llm_call`` when
# that better describes its work (05 US P1 / FR-001). Anything else -> ``dispatch``.
_DEFAULT_SPAN_OPERATION = "dispatch"
_SPAN_OPERATIONS = frozenset({"dispatch", "tool_call", "llm_call"})
# The single privileged operation the RBAC entry gate authorizes (05 US P3 / FR-007).
_DISPATCH = "dispatch"

# A node runner turns one node + its inbound predecessor payload_refs into this
# node's own payload_ref. Real runners dispatch to a nucleus/provider; the
# default is offline and deterministic.
NodeRunner = Callable[[TopologyNode, tuple[str, ...]], str]


class FakeNodeRunner:
    """Deterministic, offline default node runner. Returns a stable payload_ref
    derived only from the node id, so a topology run is fully reproducible without
    a live nucleus pool or provider (Article XIV)."""

    def __call__(self, node: TopologyNode, inbound: tuple[str, ...]) -> str:
        return f"payload:{node.id}"


def _now_iso() -> str:
    """Current UTC time as an ISO-8601 string (the CoordinationEvent timestamp)."""
    return datetime.now(timezone.utc).isoformat()


class GenericTopologyInterpreter:
    """Executes any typed ``Topology`` and returns its completed ``TopologyRun``.
    Satisfies the frozen ``TopologyInterpreter`` protocol. Construct with a custom
    ``node_runner`` to dispatch real work, or a custom ``registry`` to recognise
    extension variants; both default to the canonical, offline implementations."""

    def __init__(
        self,
        node_runner: NodeRunner | None = None,
        registry: TopologyRegistry | None = None,
        *,
        tracer: Tracer | None = None,
        auth_guard: AuthGuard | None = None,
        auth_token: AuthToken | None = None,
        approval_gate: ApprovalGate | None = None,
        hitl_operations: frozenset[str] = frozenset(),
        root_dir: str | Path | None = None,
    ) -> None:
        self._node_runner: NodeRunner = (
            node_runner if node_runner is not None else FakeNodeRunner()
        )
        self._registry = registry if registry is not None else TopologyRegistry()
        # Governance seams -- ALL optional, ALL off by default (dev-mode parity).
        self._tracer = tracer
        self._auth_guard = auth_guard
        self._auth_token = auth_token
        self._approval_gate = approval_gate
        self._hitl_operations = frozenset(hitl_operations)
        # Where a traced run persists its TopologyRun + span tree (tracing only).
        self._root = Path(root_dir) if root_dir is not None else Path(".")

    def run(self, topology: Topology) -> TopologyRun:
        # Validate FIRST -- a malformed topology never reaches execution.
        validate_topology(topology)
        # RBAC entry gate (05 US P3 / FR-007/008, SC-004/005). Dev mode -- no token
        # -- never consults the guard (zero overhead); a denied role raises 403.
        self._authorize_dispatch()
        descriptor = self._registry.lookup(topology.variant)
        # Synthesis-policy variants (mixture_of_agents) are not a node-walk; route
        # them to the dedicated MoA executor (distinct-provider fan-out + synth).
        if descriptor.order_policy == "synthesis":
            run = run_mixture_of_agents(topology)
            self._observe_moa(topology, run)
            return run
        if not descriptor.executable:
            raise NotImplementedError(
                f"variant {topology.variant!r} is registered but not executable"
            )

        run_id = "run-" + uuid.uuid4().hex[:12]
        started_at = _now_iso()

        # TRACING (05 US P1 / SC-001): open the root mission span for the whole walk.
        mission_span = self._open_mission(topology, run_id)
        traced: list[tuple[str | None, Span]] = []
        if mission_span is not None:
            traced.append((None, mission_span))

        order = _execution_order(topology, descriptor.order_policy)
        node_by_id = {node.id: node for node in topology.nodes}
        predecessors = _predecessor_map(topology)

        # Execute each node once, feeding it the outputs of its run predecessors.
        outputs: dict[str, str] = {}
        for node_id in order:
            node = node_by_id[node_id]
            # HITL (05 US P2 / SC-003): a tagged node pauses for a verdict first.
            self._gate_node(node)
            inbound = tuple(
                outputs[src] for src in predecessors[node_id] if src in outputs
            )
            outputs[node_id] = self._node_runner(node, inbound)
            # One dispatch span per node -> 100% dispatch-op span coverage (SC-001).
            node_span = self._trace_node(node, mission_span)
            if node_span is not None:
                traced.append((node_id, node_span))

        events = self._emit_events(topology, order, outputs, run_id)
        completed_at = _now_iso()
        run = TopologyRun(
            run_id=run_id,
            topology_id=topology.id,
            started_at=started_at,
            completed_at=completed_at,
            status="completed",
            events=events,
        )
        # Close the mission span (whole-walk wrap) and persist the audit record.
        self._emit_mission(mission_span)
        self._persist_run(run, traced)
        return run

    # -- governance seams (all no-ops unless a seam was injected) ------------- #
    def _authorize_dispatch(self) -> None:
        """RBAC entry gate. Consults the guard ONLY when both a guard and a token
        are present (dev mode = no token = zero overhead, FR-008/SC-005); a role
        the guard refuses raises ``RbacForbiddenError`` [403] (US P3 / SC-004)."""
        if self._auth_guard is None or self._auth_token is None:
            return
        if not self._auth_guard.authorize(self._auth_token, _DISPATCH):
            raise RbacForbiddenError(
                self._auth_token.subject, self._auth_token.role, _DISPATCH
            )

    def _gate_node(self, node: TopologyNode) -> None:
        """HITL per-node gate. A node whose operation is in ``hitl_operations``
        emits a pending approval request and blocks for a terminal verdict; a
        ``denied`` / ``timeout`` aborts the run with the spec-named error, an
        ``approved`` proceeds. No gate or an untagged node -> instant return."""
        if self._approval_gate is None or not self._hitl_operations:
            return
        operation = _node_operation(node)
        if operation not in self._hitl_operations:
            return
        request = self._approval_gate.request(operation, node.agent)
        started = time.monotonic()
        decision = self._approval_gate.await_decision(request.request_id)
        if decision == "denied":
            raise ApprovalDeniedError(request.request_id)
        if decision == "timeout":
            raise ApprovalTimeoutError(
                request.request_id, round(time.monotonic() - started, 3)
            )

    def _open_mission(self, topology: Topology, run_id: str) -> Span | None:
        """Open the root ``mission`` span (no parent) for the run, or ``None`` when
        no tracer is wired."""
        if self._tracer is None:
            return None
        return self._tracer.start_span("mission", parent_id=None)

    def _trace_node(self, node: TopologyNode, mission_span: Span | None) -> Span | None:
        """Open + emit one dispatch span for ``node`` as a child of the mission
        span, or ``None`` when no tracer is wired."""
        if self._tracer is None or mission_span is None:
            return None
        span = self._tracer.start_span(
            _span_operation(node), parent_id=mission_span.span_id
        )
        self._tracer.emit(span)
        return span

    def _emit_mission(self, mission_span: Span | None) -> None:
        """Emit the root mission span once the walk has completed."""
        if self._tracer is not None and mission_span is not None:
            self._tracer.emit(mission_span)

    def _observe_moa(self, topology: Topology, run: TopologyRun) -> None:
        """Trace + persist an MoA run (the MoA executor builds its own event trail;
        here we add a mission span + one dispatch span per node so the audit CLI can
        read MoA runs too, then persist the record). No-op without a tracer."""
        if self._tracer is None:
            return
        mission_span = self._tracer.start_span("mission", parent_id=None)
        traced: list[tuple[str | None, Span]] = [(None, mission_span)]
        for node in topology.nodes:
            span = self._tracer.start_span(
                _span_operation(node), parent_id=mission_span.span_id
            )
            self._tracer.emit(span)
            traced.append((node.id, span))
        self._tracer.emit(mission_span)
        self._persist_run(run, traced)

    def _persist_run(
        self, run: TopologyRun, traced: list[tuple[str | None, Span]]
    ) -> None:
        """Persist the completed run + its span tree to
        ``{root}/.cexai/topology/runs/{run_id}.json`` so ``topology audit`` can
        reconstruct it by ``run_id``. Tracing-only -- the default (no-tracer) path
        writes nothing."""
        if self._tracer is None:
            return
        runs_dir = self._root / ".cexai" / "topology" / "runs"
        runs_dir.mkdir(parents=True, exist_ok=True)
        record = {
            "run_id": run.run_id,
            "topology_id": run.topology_id,
            "started_at": run.started_at,
            "completed_at": run.completed_at,
            "status": run.status,
            "events": [_event_to_dict(event) for event in run.events],
            "spans": [_span_to_dict(node_id, span) for node_id, span in traced],
        }
        (runs_dir / f"{run.run_id}.json").write_text(
            json.dumps(record, indent=2, default=str) + "\n", encoding="utf-8"
        )

    @staticmethod
    def _emit_events(
        topology: Topology,
        order: list[str],
        outputs: dict[str, str],
        run_id: str,
    ) -> tuple[CoordinationEvent, ...]:
        """One initial event for the entry node (from_node=None), then one event
        per declared edge -- the SC-004 audit trail with zero phantom inputs."""
        events: list[CoordinationEvent] = []
        root = order[0]
        events.append(
            CoordinationEvent(
                event_id=f"{run_id}-e000",
                from_node=None,
                to_node=root,
                payload_ref=outputs.get(root, ""),
                timestamp=_now_iso(),
                event_type="initial",
            )
        )
        for position, edge in enumerate(topology.edges, start=1):
            events.append(
                CoordinationEvent(
                    event_id=f"{run_id}-e{position:03d}",
                    from_node=edge.src,
                    to_node=edge.dst,
                    payload_ref=outputs.get(edge.dst, ""),
                    timestamp=_now_iso(),
                    event_type=edge.event_type,
                )
            )
        return tuple(events)


def _node_operation(node: TopologyNode) -> str:
    """The operation a node performs for HITL tagging -- ``config['operation']`` if
    set (e.g. ``publish_to_social_media``), else the node id."""
    raw = node.config.get("operation")
    return str(raw) if raw else node.id


def _span_operation(node: TopologyNode) -> str:
    """The span operation for a node's dispatch span. ``config['span_operation']``
    when it names a known SpanOperation (``dispatch`` / ``tool_call`` / ``llm_call``),
    else the default ``dispatch``."""
    raw = node.config.get("span_operation")
    if isinstance(raw, str) and raw in _SPAN_OPERATIONS:
        return raw
    return _DEFAULT_SPAN_OPERATION


def _event_to_dict(event: CoordinationEvent) -> dict[str, object]:
    """JSON-safe projection of a ``CoordinationEvent`` (one audit-trail row)."""
    return {
        "event_id": event.event_id,
        "from_node": event.from_node,
        "to_node": event.to_node,
        "payload_ref": event.payload_ref,
        "timestamp": event.timestamp,
        "event_type": event.event_type,
    }


def _span_to_dict(node_id: str | None, span: Span) -> dict[str, object]:
    """JSON-safe projection of a ``Span`` plus the ``node_id`` it traces (``None``
    for the root mission span). The audit CLI joins these by ``span_id``."""
    return {
        "span_id": span.span_id,
        "parent_id": span.parent_id,
        "operation": span.operation,
        "start": span.start,
        "end": span.end,
        "node_id": node_id,
        "attrs": dict(span.attrs),
        "events": [
            {"name": event.name, "timestamp": event.timestamp, "attrs": dict(event.attrs)}
            for event in span.events
        ],
    }


def _predecessor_map(topology: Topology) -> dict[str, list[str]]:
    """For each node id, the source ids of edges pointing at it (declared order)."""
    predecessors: dict[str, list[str]] = {node.id: [] for node in topology.nodes}
    for edge in topology.edges:
        if edge.dst in predecessors:
            predecessors[edge.dst].append(edge.src)
    return predecessors


def _execution_order(topology: Topology, order_policy: str) -> list[str]:
    """Resolve the node execution order for a variant's policy. ``declared`` keeps
    declared node order (parallel / round-robin shapes); ``topological`` (and the
    not-executed ``synthesis``) sequence by edge dependency via a deterministic
    Kahn sort, tie-broken by declared order. Any node a cycle would strand is
    appended in declared order so every node still executes."""
    node_ids = [node.id for node in topology.nodes]
    if order_policy == "declared":
        return node_ids

    position = {node_id: index for index, node_id in enumerate(node_ids)}
    indegree = {node_id: 0 for node_id in node_ids}
    adjacency: dict[str, list[str]] = {node_id: [] for node_id in node_ids}
    for edge in topology.edges:
        if edge.src in adjacency and edge.dst in indegree:
            adjacency[edge.src].append(edge.dst)
            indegree[edge.dst] += 1

    ready = sorted(
        (node_id for node_id in node_ids if indegree[node_id] == 0),
        key=lambda node_id: position[node_id],
    )
    order: list[str] = []
    while ready:
        node_id = ready.pop(0)
        order.append(node_id)
        freed = []
        for target in adjacency[node_id]:
            indegree[target] -= 1
            if indegree[target] == 0:
                freed.append(target)
        if freed:
            ready.extend(freed)
            ready.sort(key=lambda node_id: position[node_id])

    if len(order) < len(node_ids):
        seen = set(order)
        order.extend(node_id for node_id in node_ids if node_id not in seen)
    return order

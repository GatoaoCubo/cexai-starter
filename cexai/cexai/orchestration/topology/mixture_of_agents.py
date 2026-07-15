"""Mixture-of-Agents executor (03 US2 / FR-005, SC-004).

The MoA execution path the generic interpreter routes ``mixture_of_agents`` into.
Unlike the generic node-walk, MoA does NOT sequence nodes along edges: it fans
the SAME prompt to N >= 2 workers, each pinned to a DISTINCT LLM provider (genuine
diversity, V03-F1 -- not same-model-different-seed), gathers their outputs with
per-worker crash tolerance, enforces a quorum, then hands the survivors to a
single synthesizer that decides the swarm's one answer.

Flow:
  1. Partition nodes by ``config['role']`` into workers + the one synthesizer and
     enforce FR-005 structurally (>= 2 workers, all distinct providers, exactly 1
     synthesizer) BEFORE any provider call.
  2. Fan out: dispatch each worker via ``cexai.foundation.llm.call`` on its own
     provider. A worker that raises OR returns empty text is a failure -- caught,
     recorded, and tolerated (one crash must not abort the swarm).
  3. Quorum: default M = ceil(N/2)+1 (overridable via the synthesizer node's
     ``config['quorum']``). Fewer than M survivors -> ``QuorumFailureError``.
  4. Synthesize: the survivors (in declared order) go to the ``Synthesizer``,
     which converges / merges / flags / picks per its policy.
  5. Audit trail (SC-004, zero phantom inputs): one fan-out ``CoordinationEvent``
     per worker (``from_node=None`` -- fed by the initial prompt), one ``data``
     gather event per survivor into the synthesizer, and one ``synthesis`` event
     carrying the synthesizer's verdict ref. Every input is traceable.

Offline by construction (Article XIV): the only LLM seam is
``foundation.llm.call``; tests register deterministic fake providers under the
worker provider names via ``foundation.llm.register_provider``. The live
multi-provider path is opt-in (the W3 benchmark), never the unit suite.

MoA is an existing ``topology`` variant and provider diversity rides the existing
``model_provider`` abstraction -- this registers NO new CEX kind (founder rule).

absorbs: 03_swarms/moa
"""

from __future__ import annotations

import math
import uuid
from collections.abc import Callable
from datetime import datetime, timezone

from cexai.foundation import llm
from cexai.foundation._shared.types import LlmRequest, LlmResponse, Message
from cexai.orchestration._shared.errors import MoaStructuralError, QuorumFailureError
from cexai.orchestration._shared.types import (
    CoordinationEvent,
    Topology,
    TopologyNode,
    TopologyRun,
)
from cexai.orchestration.topology.synthesizer import Synthesizer

__all__ = ["run_mixture_of_agents"]

# A worker dispatch turns one worker node + a prompt into its output text. The
# default dispatches through the multi-provider facade; injectable for isolation.
WorkerDispatch = Callable[[TopologyNode, str], LlmResponse]

_WORKER_ROLE = "worker"
_SYNTHESIZER_ROLE = "synthesizer"


def run_mixture_of_agents(
    topology: Topology,
    *,
    prompt: str | None = None,
    dispatch: WorkerDispatch | None = None,
    synthesizer: Synthesizer | None = None,
) -> TopologyRun:
    """Execute an MoA ``topology`` and return its completed ``TopologyRun``.

    ``prompt`` is the shared task handed to every worker (a deterministic default
    is derived from the topology id, since the frozen ``Topology`` carries no
    runtime input). ``dispatch`` overrides the provider-call seam (defaults to the
    multi-provider facade); ``synthesizer`` overrides the merge policy (defaults to
    one built from the synthesizer node's config). Raises ``MoaStructuralError``
    for a structurally invalid MoA and ``QuorumFailureError`` when too few
    workers survive."""
    workers, synth_node = _partition(topology)
    worker_dispatch = dispatch if dispatch is not None else _facade_dispatch
    task = prompt if prompt is not None else f"[MoA:{topology.id}] Produce your best independent response."

    run_id = "run-" + uuid.uuid4().hex[:12]
    started_at = _now_iso()

    # Fan-out: dispatch each worker on its own provider; tolerate per-worker
    # crashes so the swarm degrades gracefully (03 US2 edge case).
    outputs: dict[str, str] = {}
    for worker in workers:
        text = _dispatch_one(worker, task, worker_dispatch)
        if text:
            outputs[worker.id] = text

    required = _quorum(len(workers), synth_node)
    if len(outputs) < required:
        raise QuorumFailureError(required=required, succeeded=len(outputs))

    active_synth = synthesizer if synthesizer is not None else _synthesizer_from(synth_node)
    outcome = active_synth.synthesize(outputs)

    events = _build_events(run_id, workers, synth_node, outputs, outcome.summary_ref)
    return TopologyRun(
        run_id=run_id,
        topology_id=topology.id,
        started_at=started_at,
        completed_at=_now_iso(),
        status="completed",
        events=events,
    )


# --------------------------------------------------------------------------- #
# Structural partition + FR-005 enforcement                                     #
# --------------------------------------------------------------------------- #
def _partition(topology: Topology) -> tuple[tuple[TopologyNode, ...], TopologyNode]:
    """Split nodes into ordered workers + the single synthesizer, enforcing FR-005
    BEFORE any provider call. Raises ``MoaStructuralError`` for any structural
    violation (R-236: previously a bare ``ValueError``, invisible to the
    package's ``except CexaiError`` contract)."""
    workers: list[TopologyNode] = []
    synthesizers: list[TopologyNode] = []
    for node in topology.nodes:
        role = node.config.get("role")
        if role == _WORKER_ROLE:
            workers.append(node)
        elif role == _SYNTHESIZER_ROLE:
            synthesizers.append(node)
        else:
            raise MoaStructuralError(
                node.id,
                f"must have role {_WORKER_ROLE!r} or {_SYNTHESIZER_ROLE!r}, got {role!r}",
            )

    if len(synthesizers) != 1:
        raise MoaStructuralError(
            "", f"MoA requires exactly 1 synthesizer node, found {len(synthesizers)}"
        )
    if len(workers) < 2:
        raise MoaStructuralError("", f"MoA requires >= 2 workers, found {len(workers)}")

    providers = [worker.agent for worker in workers]
    if len(set(providers)) != len(providers):
        raise MoaStructuralError(
            "",
            "MoA workers must use distinct providers (V03-F1 genuine diversity, "
            f"not same-model-different-seed); got {providers}",
        )

    return tuple(workers), synthesizers[0]


def _quorum(num_workers: int, synth_node: TopologyNode) -> int:
    """Quorum threshold M. Default ``ceil(N/2)+1`` (a strict majority plus one);
    a positive integer ``config['quorum']`` on the synthesizer node overrides it."""
    override = synth_node.config.get("quorum")
    # bool is an int subclass in Python; a stray ``quorum: true`` must NOT read as 1.
    if isinstance(override, int) and not isinstance(override, bool) and override > 0:
        return override
    return math.ceil(num_workers / 2) + 1


def _synthesizer_from(synth_node: TopologyNode) -> Synthesizer:
    """Build the merge policy from the synthesizer node config. Only the
    ``divergence_action`` is read here (the spec's one knob); thresholds keep
    their defaults unless a caller injects a custom ``Synthesizer``."""
    action = synth_node.config.get("divergence_action")
    if isinstance(action, str) and action:
        return Synthesizer(divergence_action=action)
    return Synthesizer()


# --------------------------------------------------------------------------- #
# Worker dispatch (the only LLM seam)                                           #
# --------------------------------------------------------------------------- #
def _facade_dispatch(worker: TopologyNode, prompt: str) -> LlmResponse:
    """Dispatch one worker through the multi-provider facade, pinned to the
    worker's OWN provider (``worker.agent``). The model is the worker config's
    ``model`` or, absent that, the provider name."""
    model = str(worker.config.get("model") or worker.agent)
    request = LlmRequest(model=model, messages=(Message(role="user", content=prompt),))
    return llm.call(request, provider=worker.agent)


def _dispatch_one(worker: TopologyNode, prompt: str, dispatch: WorkerDispatch) -> str:
    """Run one worker and return its non-empty output text, or ``""`` on failure.
    A broad ``except`` is intentional here: this is the swarm's resilience
    boundary -- any single provider crash (network, auth, runtime) must be
    contained so quorum logic can decide, never propagate and abort the run."""
    try:
        response = dispatch(worker, prompt)
    except Exception:  # noqa: BLE001 -- resilience boundary; see docstring.
        return ""
    text = response.text or ""
    return text if text.strip() else ""


# --------------------------------------------------------------------------- #
# Audit trail (SC-004)                                                          #
# --------------------------------------------------------------------------- #
def _build_events(
    run_id: str,
    workers: tuple[TopologyNode, ...],
    synth_node: TopologyNode,
    outputs: dict[str, str],
    synthesis_ref: str,
) -> tuple[CoordinationEvent, ...]:
    """The MoA coordination trail: a fan-out event per worker (``from_node=None``,
    fed by the initial prompt -- so failures are still traceable, zero phantom
    inputs), a ``data`` gather event per survivor into the synthesizer, then one
    terminal ``synthesis`` self-event carrying the synthesizer's verdict ref (the
    merged artifact rests at the synthesizer; MoA has no downstream consumer)."""
    events: list[CoordinationEvent] = []
    index = 0

    for worker in workers:
        succeeded = worker.id in outputs
        events.append(
            CoordinationEvent(
                event_id=f"{run_id}-e{index:03d}",
                from_node=None,
                to_node=worker.id,
                payload_ref=f"payload:{worker.id}" if succeeded else "",
                timestamp=_now_iso(),
                event_type="worker" if succeeded else "worker_error",
            )
        )
        index += 1

    for worker in workers:
        if worker.id not in outputs:
            continue
        events.append(
            CoordinationEvent(
                event_id=f"{run_id}-e{index:03d}",
                from_node=worker.id,
                to_node=synth_node.id,
                payload_ref=f"payload:{worker.id}",
                timestamp=_now_iso(),
                event_type="data",
            )
        )
        index += 1

    events.append(
        CoordinationEvent(
            event_id=f"{run_id}-e{index:03d}",
            from_node=synth_node.id,
            to_node=synth_node.id,
            payload_ref=synthesis_ref,
            timestamp=_now_iso(),
            event_type="synthesis",
        )
    )
    return tuple(events)


def _now_iso() -> str:
    """Current UTC time as an ISO-8601 string (the CoordinationEvent timestamp)."""
    return datetime.now(timezone.utc).isoformat()

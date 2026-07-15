"""Topology subsystem -- typed agent-coordination catalog + generic interpreter.

The six absorbed variants (sequential, concurrent, hierarchical, graph,
group_chat, mixture_of_agents) and the generic interpreter that executes any
typed ``Topology`` (cexai-specs/03_swarms FR-001..004). The frozen ``Topology`` /
``TopologyInterpreter`` contracts live in ``cexai.orchestration._shared.types``;
this package is their v0.3-W1 implementation.

Public surface:
  * ``TopologyRegistry`` / ``lookup`` / ``known_variants`` / ``TopologyDescriptor``
        -- the 6-variant catalog (03 FR-001 / FR-006).
  * ``validate_topology``
        -- structural validation: empty / cyclic-graph / unknown variant (US1).
  * ``GenericTopologyInterpreter`` / ``FakeNodeRunner`` / ``NodeRunner``
        -- the generic executor + its injectable, offline node-runner seam.
  * ``run_mixture_of_agents`` / ``Synthesizer`` / ``SynthesisOutcome`` /
    ``cosine_similarity``
        -- the MoA execution path: distinct-provider worker fan-out + quorum +
           the merge/converge/diverge synthesizer (03 US2 / FR-005).

``mixture_of_agents`` is REGISTERED with a ``synthesis`` order policy; the
interpreter detects that policy and routes it to ``run_mixture_of_agents``
(v0.3-W2). Its registry descriptor stays ``executable=False`` -- that flag means
"not runnable by the generic node-walk", which remains true: MoA needs its own
multi-provider executor over ``cexai.foundation.llm``.

``DefaultTopologyInterpreter`` is an alias of ``GenericTopologyInterpreter`` kept
so the frozen contract seam (``tests/orchestration/contract/
test_orchestration_contracts.test_topology_interpreter_runs``) imports that exact
name. This mirrors the ``memory.vector.InMemoryVectorStore`` alias pattern: a
later wave can un-skip the frozen sig without editing that file.

absorbs: 03_swarms/topology
"""

from cexai.orchestration.topology.interpreter import (
    FakeNodeRunner,
    GenericTopologyInterpreter,
    NodeRunner,
)
from cexai.orchestration.topology.mixture_of_agents import run_mixture_of_agents
from cexai.orchestration.topology.registry import (
    KNOWN_VARIANTS,
    TopologyDescriptor,
    TopologyRegistry,
    known_variants,
    lookup,
)
from cexai.orchestration.topology.synthesizer import (
    SynthesisOutcome,
    Synthesizer,
    cosine_similarity,
)
from cexai.orchestration.topology.validate import validate_topology

# Alias for the frozen contract seam (see module docstring).
DefaultTopologyInterpreter = GenericTopologyInterpreter

__all__ = [
    "KNOWN_VARIANTS",
    "TopologyDescriptor",
    "TopologyRegistry",
    "known_variants",
    "lookup",
    "validate_topology",
    "GenericTopologyInterpreter",
    "DefaultTopologyInterpreter",
    "FakeNodeRunner",
    "NodeRunner",
    "run_mixture_of_agents",
    "Synthesizer",
    "SynthesisOutcome",
    "cosine_similarity",
]

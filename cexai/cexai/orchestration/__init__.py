"""CEXAI orchestration layer -- the v0.3 coordination plane over foundation + memory.

Four coordination subsystems share one frozen vocabulary
(``cexai.orchestration._shared.types``):

  topology   typed agent-coordination catalog + interpreter  (W1) -- cexai-specs/03_swarms
  planning   GOAP state-space planner (pre/effect operators)  (W1) -- cexai-specs/02_ruflo US P2
  streaming  stream-json agent-to-agent chaining              (W2) -- cexai-specs/02_ruflo US P3
  sparc      opt-in 5-phase methodology templates             (W3) -- cexai-specs/04_claude-flow

Import is intentionally light (Article VIII): this module exposes nothing at the
top level for W0. The subsystems stay addressable at ``cexai.orchestration.
{topology,planning,streaming,sparc}`` once their W1+ implementations land.

TAXONOMY NOTE (taxonomy-neutral wave): the types frozen here are Python CODE.
Whether ``topology`` / ``sparc_phase`` become NEW CEX kinds or EXTENSIONS of
existing kinds (``collaboration_pattern``, ``pipeline_template``,
``planning_strategy``, ``event_schema``) is DEFERRED to W1 (it needs an ADR).
This wave registers ZERO kinds and does NOT touch ``.cex/kinds_meta.json``.

absorbs: 03_swarms/topology + 02_ruflo/goap+stream + 04_claude-flow/sparc
"""

__all__: list = []

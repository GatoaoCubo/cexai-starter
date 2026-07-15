"""CEXAI governance layer -- the v0.3-W3 quality + safety plane over orchestration.

Four governance subsystems share one frozen vocabulary
(``cexai.governance._shared.types``):

  tracing  OTel mission/wave/nucleus/dispatch/tool/LLM span tree   (W3b) -- 05_agno US P1
  hitl     human-in-the-loop approval gates (pause/approve/reject) (W3b) -- 05_agno US P2
  rbac     opt-in JWT viewer/dev authorization (dev = no-auth)      (W3b) -- 05_agno US P3
  audit    audit_event record export                               (W3b) -- 05_agno FR-001/007

Import is intentionally light (Article VIII): this module exposes nothing at the
top level for W3a. The subsystems stay addressable at ``cexai.governance.
{tracing,hitl,rbac,audit}`` once their W3b implementations land. The tracing
subsystem EXTENDS the existing ``cexai.foundation.tracing`` substrate (OTLP +
local-file fallback) into a mission-scoped span tree; it does not replace it.

TAXONOMY NOTE (founder rule, taxonomy-neutral wave): the types frozen here are
Python CODE. Per N07's locked W3 decision this wave REUSES existing kinds --
``hitl_config`` (HITL policy), ``rbac_policy`` + ``role_assignment`` (RBAC roles),
``trace_config`` (tracing config). OTel spans and JWT auth tokens are RUNTIME
DATACLASSES, NOT kinds (precedent: orchestration's CoordinationEvent / TopologyRun
were spans-not-kinds). The NEW kinds (``approval_request``; a lean ``audit_event``)
are registered LATER by a dedicated W3b ADR cell -- NOT here. ``AuthToken`` as a
kind is DEFERRED to v1.0 (RBAC is opt-in / dormant). This wave registers ZERO
kinds and does NOT touch ``.cex/kinds_meta.json``.

Spec provenance: cexai-specs/05_agno/spec.md (US P1/P2/P3, FR-001..011,
SC-001..005, Key Entities).

absorbs: 05_agno/governance
"""

__all__: list = []

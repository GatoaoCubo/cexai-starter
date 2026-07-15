"""Tracing subsystem -- OTel mission span tree (impl: v0.3-W3b).

EXTENDS the existing ``cexai.foundation.tracing`` substrate (OTLP exporter +
``.cexai/traces`` local-file fallback) into a mission-scoped span tree: mission
-> wave -> nucleus -> dispatch -> tool/LLM-call spans with parent-child links
(05_agno US P1 / FR-001/002), graceful degrade to ``.cexai/traces/buffer/
{mission_id}.jsonl`` when the collector is unreachable (FR-003), and attribute
redaction (FR-009). The frozen ``Span`` / ``SpanEvent`` / ``RedactionConfig`` /
``Tracer`` contracts live in ``cexai.governance._shared.types``; W3b ships the
concrete ``MissionTracer`` behind that seam here.

absorbs: 05_agno/governance
"""

from __future__ import annotations

from cexai.governance.tracing.mission_tracer import MissionTracer
from cexai.governance.tracing.redaction import (
    default_redaction_config,
    load_redaction_config,
    redact,
)

__all__ = [
    "MissionTracer",
    "redact",
    "default_redaction_config",
    "load_redaction_config",
]

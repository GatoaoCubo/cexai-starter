"""OpenTelemetry tracing substrate (impl: W2).

Emits structured spans for missions and LLM calls (Article V -- Observable by
Default) with an OTLP exporter and a local file-buffer fallback. Wired into
provider calls via decorators so every call is observable. Partial absorption
from vertical 05 (agno) tracing skeleton.

Public surface (W4 wires llm calls through these -- keep stable)::

    configure_tracing(*, otlp_endpoint=None, local_dir=None) -> None
    get_tracer(name) -> Tracer
    traced(name=None)                      # decorator

Plus the seams ``install_exporter`` / ``active_exporter`` / ``reset_tracing``
and the re-exported OTel ``SpanKind`` / ``Status`` / ``StatusCode`` helpers.

absorbs: 05_agno/observability-otel
"""

from __future__ import annotations

from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode

from cexai.foundation.tracing.decorators import traced
from cexai.foundation.tracing.spans import (
    active_exporter,
    configure_tracing,
    get_tracer,
    install_exporter,
    reset_tracing,
)

__all__ = [
    "configure_tracing",
    "get_tracer",
    "traced",
    "install_exporter",
    "active_exporter",
    "reset_tracing",
    "SpanKind",
    "Status",
    "StatusCode",
]

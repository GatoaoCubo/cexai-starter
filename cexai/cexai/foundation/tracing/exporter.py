"""OTLP span exporter factory.

Thin over ``opentelemetry-exporter-otlp`` (HTTP/protobuf transport -- one fewer
runtime dependency than gRPC and friendlier to proxies). The import is lazy and
local to the factory so importing the tracing package never requires the OTLP
wheel: the fallback path stays usable with zero external services, and an OTLP
import problem surfaces only when an endpoint is actually configured.

absorbs: 05_agno/observability-otel
"""

from __future__ import annotations

from opentelemetry.sdk.trace.export import SpanExporter

__all__ = ["build_otlp_exporter"]


def build_otlp_exporter(endpoint: str) -> SpanExporter:
    """Return an OTLP/HTTP span exporter targeting ``endpoint`` (e.g.
    ``http://localhost:4318/v1/traces``). Construction is connection-free; the
    first network call happens when a span is exported."""
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

    return OTLPSpanExporter(endpoint=endpoint)

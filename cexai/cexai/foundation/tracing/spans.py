"""Tracer provider lifecycle -- a thin wrapper over opentelemetry-sdk.

Owns a single module-global provider that ``get_tracer`` and the ``@traced``
decorator read. Exporter selection is deliberately simple (Article VIII): an
OTLP endpoint (argument or env ``CEXAI_OTLP_ENDPOINT``) routes spans to the
OTLP exporter; otherwise spans land in the local-file fallback. The OTel
process-global provider is set ONCE (its first install) so re-configuration in
the same process -- and back-to-back tests -- never trips the SDK's
"Overriding of current TracerProvider is not allowed" guard; our own
``_PROVIDER`` is what ``get_tracer`` resolves against, so it always reflects the
latest ``configure_tracing`` / ``install_exporter`` call.

W4 wires llm provider calls through ``get_tracer`` / ``@traced``; this module
only builds the standalone primitives.

absorbs: 05_agno/observability-otel
"""

from __future__ import annotations

import os

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SimpleSpanProcessor,
    SpanExporter,
)
from opentelemetry.trace import Tracer

__all__ = [
    "configure_tracing",
    "get_tracer",
    "install_exporter",
    "active_exporter",
    "reset_tracing",
]

# Env var that, when set, routes spans to the OTLP exporter instead of the
# local-file fallback. Mirrors the llm facade's .cexai/ env conventions.
_OTLP_ENDPOINT_ENV = "CEXAI_OTLP_ENDPOINT"
_SERVICE_NAME = "cexai"

# Module-global state. _PROVIDER is what get_tracer resolves against;
# _ACTIVE_EXPORTER backs active_exporter(); _GLOBAL_SET guards the one-time
# propagation to the OTel process-global provider.
_PROVIDER: TracerProvider | None = None
_ACTIVE_EXPORTER: SpanExporter | None = None
_GLOBAL_SET = False


def configure_tracing(*, otlp_endpoint: str | None = None, local_dir: str | None = None) -> None:
    """Select and install an exporter. If ``otlp_endpoint`` (or env
    ``CEXAI_OTLP_ENDPOINT``) is set, route spans through the OTLP exporter
    (batched); otherwise append them to the local-file fallback (synchronous).
    ``local_dir`` overrides the fallback directory (default ``.cexai/traces``)."""
    endpoint = otlp_endpoint or os.environ.get(_OTLP_ENDPOINT_ENV)
    if endpoint:
        from cexai.foundation.tracing.exporter import build_otlp_exporter

        install_exporter(build_otlp_exporter(endpoint), batch=True)
    else:
        from cexai.foundation.tracing.fallback import build_fallback_exporter

        install_exporter(build_fallback_exporter(local_dir), batch=False)


def get_tracer(name: str) -> Tracer:
    """Return a tracer from the active provider, lazily configuring the
    local-file fallback first so tracing is never silently a no-op."""
    if _PROVIDER is None:
        configure_tracing()
    return _PROVIDER.get_tracer(name)


def install_exporter(exporter: SpanExporter, *, batch: bool = False) -> None:
    """Build a provider around ``exporter`` and make it active. ``batch`` picks
    a ``BatchSpanProcessor`` (off the hot path -- for OTLP); otherwise a
    ``SimpleSpanProcessor`` exports synchronously on span end (local file /
    in-memory tests). The test/extension seam -- inject any ``SpanExporter``."""
    global _PROVIDER, _ACTIVE_EXPORTER
    _PROVIDER = _build_tracer_provider(exporter, batch=batch)
    _ACTIVE_EXPORTER = exporter
    _set_global_once(_PROVIDER)


def active_exporter() -> SpanExporter | None:
    """The exporter backing the active provider, or ``None`` before configure.
    Introspection seam: assert which exporter was selected without emitting."""
    return _ACTIVE_EXPORTER


def reset_tracing() -> None:
    """Drop the active provider + exporter (next ``get_tracer`` re-configures).
    Used between tests for isolation. The OTel process-global stays put -- the
    SDK forbids un-setting it -- but our resolution path is fully reset."""
    global _PROVIDER, _ACTIVE_EXPORTER
    _PROVIDER = None
    _ACTIVE_EXPORTER = None


def _build_tracer_provider(exporter: SpanExporter, *, batch: bool) -> TracerProvider:
    provider = TracerProvider(resource=Resource.create({"service.name": _SERVICE_NAME}))
    processor = BatchSpanProcessor(exporter) if batch else SimpleSpanProcessor(exporter)
    provider.add_span_processor(processor)
    return provider


def _set_global_once(provider: TracerProvider) -> None:
    global _GLOBAL_SET
    if _GLOBAL_SET:
        return
    trace.set_tracer_provider(provider)
    _GLOBAL_SET = True

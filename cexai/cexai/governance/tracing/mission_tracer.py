"""MissionTracer -- the concrete mission span-tree tracer (05_agno US P1).

Implements the FROZEN ``cexai.governance._shared.types.Tracer`` Protocol over the
existing ``cexai.foundation.tracing`` substrate. It builds the mission span tree
(mission / wave / nucleus / dispatch / tool_call / llm_call) as the typed
``Span`` projection with explicit parent-child links and ZERO phantom parents
(FR-001/002), masks sensitive attributes before export (FR-009, see
``redaction``), and gracefully degrades to a local JSONL buffer when the active
exporter fails -- the mission proceeds and spans flush on reconnect (FR-003).

Design (Article VIII Anti-Abstraction, Article XIV offline):
  * ``start_span`` is a pure projection: it opens a ``Span`` (16-hex span_id,
    ISO-8601 start, ``end=None``) and links ``parent_id`` exactly as passed --
    no global state, no I/O, no network, so the hot open-path is hermetic.
  * ``emit`` redacts, then hands the COMPLETED span to the active exporter. The
    default exporter WRAPS ``foundation.tracing.get_tracer`` -- it mints and ends
    a real OTel span carrying the projected operation + attributes, so the
    foundation's OTLP exporter / local-file fallback records it (the v0.1
    substrate, unchanged). The exporter is an injectable callable seam: a
    deployment routes spans to a live collector; a test injects a stub.
  * On exporter failure ``emit`` does NOT raise -- it marks the failure with
    ``TraceExportError`` and buffers the span to
    ``.cexai/traces/buffer/{mission_id}.jsonl`` (one JSON span per line).

absorbs: 05_agno/observability-otel
"""

from __future__ import annotations

import json
import logging
import os
import secrets
from collections.abc import Callable, Mapping
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Any

from cexai.governance._shared.errors import TraceExportError
from cexai.governance._shared.types import RedactionConfig, Span, SpanEvent
from cexai.governance.tracing.redaction import default_redaction_config, redact

__all__ = ["MissionTracer"]

# Logical tracer name handed to foundation.tracing.get_tracer for the real OTel
# span emitted per projected span.
_TRACER_NAME = "cexai.governance.mission"

# R-214: an audit/trace export failure must be OBSERVABLE -- emit()/_buffer()
# log at warning level instead of silently discarding the failure (the
# file-buffer degrade itself is unchanged; only its visibility is fixed).
_LOG = logging.getLogger("cexai.governance.tracing.mission_tracer")

# Env var foundation.tracing reads to select OTLP vs local-file. Re-read here
# only to label the graceful-degrade marker (TraceExportError.endpoint).
_OTLP_ENDPOINT_ENV = "CEXAI_OTLP_ENDPOINT"

# Span attribute value types OTel accepts natively; anything else is stringified
# before it crosses into the foundation span.
_OTEL_SCALARS = (str, bool, int, float)


def _now_iso() -> str:
    """Current UTC instant as an ISO-8601 string ending in ``Z``."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class MissionTracer:
    """Build and emit a mission's OTel span tree as typed ``Span`` projections.

    ``exporter`` is the active-exporter seam: a ``Callable[[Span], None]`` invoked
    by ``emit`` with the redacted, completed span. When omitted, the default
    exporter forwards to ``foundation.tracing`` (real OTel emission). When the
    exporter raises (e.g. collector unreachable), the span is buffered locally and
    the mission continues (FR-003)."""

    def __init__(
        self,
        mission_id: str | None = None,
        *,
        redaction: RedactionConfig | None = None,
        root_dir: str | Path | None = None,
        exporter: Callable[[Span], None] | None = None,
    ) -> None:
        self._mission_id = mission_id or f"mission-{secrets.token_hex(6)}"
        self._redaction = redaction if redaction is not None else default_redaction_config()
        self._root = Path(root_dir) if root_dir is not None else Path(".")
        self._exporter = exporter
        self._endpoint = os.environ.get(_OTLP_ENDPOINT_ENV)

    @property
    def mission_id(self) -> str:
        """The mission this tracer scopes its buffer / spans under."""
        return self._mission_id

    # -- Tracer Protocol ---------------------------------------------------- #
    def start_span(
        self,
        operation: str,
        parent_id: str | None = None,
        *,
        attrs: Mapping[str, Any] | None = None,
        events: tuple[SpanEvent, ...] | None = None,
    ) -> Span:
        """Open a span for ``operation`` under ``parent_id`` (``None`` = root
        mission span) and return it. ``span_id`` is a fresh 16-hex id (OTel
        span-id shaped); ``start`` is ISO-8601 and ``end`` is ``None`` while
        open. Pure projection -- no I/O, no network, no global state."""
        return Span(
            span_id=secrets.token_hex(8),
            parent_id=parent_id,
            operation=operation,
            start=_now_iso(),
            end=None,
            attrs=MappingProxyType(dict(attrs)) if attrs else MappingProxyType({}),
            events=tuple(events) if events else (),
        )

    def emit(self, span: Span) -> None:
        """Record a completed ``span`` to the active exporter, masking sensitive
        attributes first (FR-009). On exporter failure the span is buffered to
        ``.cexai/traces/buffer/{mission_id}.jsonl`` and the mission proceeds
        (FR-003) -- this method never raises for an export problem, but the
        failure is logged (R-214) so a silent exporter fault is observable."""
        masked = redact(span, self._redaction)
        try:
            self._export(masked)
        except Exception as exc:  # collector unreachable / exporter fault -> degrade
            _LOG.warning(
                "[TRACE-DEGRADE] exporter failed for span %s (operation=%s): %s -- buffering locally",
                masked.span_id,
                masked.operation,
                exc,
            )
            self._buffer(masked)

    # -- helpers (not part of the Protocol) --------------------------------- #
    def end_span(self, span: Span) -> Span:
        """Return a completed copy of ``span`` with ``end`` stamped now. The open
        span is left untouched (frozen dataclasses are never edited in place)."""
        return replace(span, end=_now_iso())

    def flush_buffer(self, exporter: Callable[[Span], None] | None = None) -> int:
        """Replay buffered spans through a now-healthy exporter (FR-003 flush on
        reconnect). Returns the number flushed. Spans that still fail to export
        are kept in the buffer (in order); on a fully successful drain the buffer
        file is removed. ``exporter`` defaults to this tracer's active exporter."""
        buffer_path = self._buffer_path()
        if not buffer_path.exists():
            return 0
        lines = [line for line in buffer_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if not lines:
            return 0

        sink = exporter if exporter is not None else self._export
        flushed = 0
        remaining: list[str] = []
        for index, line in enumerate(lines):
            span = _dict_to_span(json.loads(line))
            try:
                sink(span)
            except Exception:
                remaining = lines[index:]
                break
            flushed += 1

        if remaining:
            buffer_path.write_text("\n".join(remaining) + "\n", encoding="utf-8")
        else:
            buffer_path.unlink(missing_ok=True)
        return flushed

    def _export(self, span: Span) -> None:
        """Dispatch to the injected exporter, or the foundation default."""
        if self._exporter is not None:
            self._exporter(span)
        else:
            self._foundation_export(span)

    def _foundation_export(self, span: Span) -> None:
        """Default exporter: mint + end a real OTel span via the foundation
        substrate so its active exporter (OTLP, or the local-file fallback)
        records this projected span. Imported lazily so module import stays
        light and the hot path only touches foundation when actually emitting."""
        from cexai.foundation.tracing import get_tracer

        otel_span = get_tracer(_TRACER_NAME).start_span(span.operation)
        try:
            for key, value in span.attrs.items():
                otel_span.set_attribute(key, value if isinstance(value, _OTEL_SCALARS) else str(value))
            for event in span.events:
                otel_span.add_event(
                    event.name,
                    attributes={
                        k: (v if isinstance(v, _OTEL_SCALARS) else str(v)) for k, v in event.attrs.items()
                    },
                )
        finally:
            otel_span.end()

    def _buffer(self, span: Span) -> None:
        """Append the span as one JSON line to the mission buffer (graceful
        degrade). ``TraceExportError`` is constructed as the FR-003 marker (it
        carries the endpoint + buffer path); it is logged (R-214), not just
        constructed and discarded, so the degrade reason is observable, then
        recorded rather than raised, so the mission proceeds."""
        buffer_path = self._buffer_path()
        marker = TraceExportError(self._endpoint or "<no-otlp-endpoint>", str(buffer_path))
        _LOG.warning("%s", marker)
        buffer_path.parent.mkdir(parents=True, exist_ok=True)
        with buffer_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(_span_to_dict(span), default=str))
            handle.write("\n")

    def _buffer_path(self) -> Path:
        return self._root / ".cexai" / "traces" / "buffer" / f"{self._mission_id}.jsonl"


def _span_to_dict(span: Span) -> dict[str, Any]:
    """JSON-safe projection of a ``Span`` (one buffer line)."""
    return {
        "span_id": span.span_id,
        "parent_id": span.parent_id,
        "operation": span.operation,
        "start": span.start,
        "end": span.end,
        "attrs": dict(span.attrs),
        "events": [
            {"name": event.name, "timestamp": event.timestamp, "attrs": dict(event.attrs)}
            for event in span.events
        ],
    }


def _dict_to_span(data: Mapping[str, Any]) -> Span:
    """Reconstruct a ``Span`` from a buffer line (inverse of ``_span_to_dict``)."""
    events = tuple(
        SpanEvent(
            name=event["name"],
            timestamp=event["timestamp"],
            attrs=MappingProxyType(dict(event.get("attrs", {}))),
        )
        for event in data.get("events", ())
    )
    return Span(
        span_id=data["span_id"],
        parent_id=data.get("parent_id"),
        operation=data["operation"],
        start=data["start"],
        end=data.get("end"),
        attrs=MappingProxyType(dict(data.get("attrs", {}))),
        events=events,
    )

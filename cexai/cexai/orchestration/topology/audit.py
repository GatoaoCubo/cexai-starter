"""Topology audit-trace reconstruction (03_swarms US P3 / SC-004 + 05_agno US P1).

``reconstruct(run_id)`` rebuilds the complete audit trace for one topology run by
joining two persisted sources written during a traced run (see
``GenericTopologyInterpreter`` with a ``tracer``):

  * the TopologyRun record at ``{root}/.cexai/topology/runs/{run_id}.json`` -- the
    ordered ``CoordinationEvent`` trail (one initial event + one per edge, or the
    MoA fan-out/gather/synthesis trail) plus the run's span tree.
  * any graceful-degrade spans buffered under ``{root}/.cexai/traces/buffer/*.jsonl``
    (FR-003: spans the OTel collector could not take are written here; the mission
    proceeds). These are merged in, deduped by ``span_id``, so a trace stays whole
    even when export degraded mid-run.

The reconstruction ENFORCES the SC-004 / US P3 invariant -- ZERO phantom inputs:
every ``CoordinationEvent.from_node`` either is ``None`` (an initial event, fed by
the run's external/initial input) or names a node that was itself reached in the
run (it appears as some event's ``to_node``). A violation raises
``PhantomInputError`` -- the audit refuses to certify a trace whose coordination
references a source that never ran (Gating-Wrath: a broken audit trail is a hard
failure, never a silent pass).

Offline by construction (Article XIV): pure filesystem reads of JSON the
interpreter already wrote; no collector, no network. ``root_dir`` is injectable so
tests / the CLI point at a ``tmp_path`` instead of the process CWD.

This reads only RUNTIME artifacts (TopologyRun + spans are dataclasses-as-spans,
not kinds) and registers NO new CEX kind.

absorbs: 05_agno/governance-integration + 03_swarms/audit
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from cexai.orchestration._shared.errors import OrchestrationError

__all__ = [
    "reconstruct",
    "verify_phantom_free",
    "AuditTraceNotFoundError",
    "PhantomInputError",
]

# Span operations that represent a dispatch (the SC-001 coverage denominator).
_DISPATCH_OPERATIONS: frozenset[str] = frozenset({"dispatch", "tool_call", "llm_call"})


class AuditTraceNotFoundError(OrchestrationError):
    """No persisted TopologyRun exists for ``run_id`` (it was never traced, or the
    ``root_dir`` is wrong). Carries the ``run_id`` and the ``path`` looked up."""

    def __init__(self, run_id: str, path: str) -> None:
        self.run_id = run_id
        self.path = path
        super().__init__(f"no audit trace for run {run_id!r} (looked in {path!r})")


class PhantomInputError(OrchestrationError):
    """A coordination event references a ``from_node`` that was never reached in the
    run (SC-004 / 03 US P3 violation -- a phantom input). Carries the offending
    ``event_id`` and the dangling ``from_node``."""

    def __init__(self, event_id: str, from_node: str) -> None:
        self.event_id = event_id
        self.from_node = from_node
        super().__init__(
            f"phantom input in event {event_id!r}: from_node {from_node!r} "
            "was never reached in the run"
        )


def reconstruct(run_id: str, *, root_dir: str | Path | None = None) -> dict[str, Any]:
    """Rebuild and certify the audit trace for ``run_id``.

    Reads the persisted TopologyRun, merges any buffered (graceful-degrade) spans,
    verifies the zero-phantom-input invariant, and returns the joined trace as a
    JSON-safe dict: ``run_id`` / ``topology_id`` / ``status`` / timings, the ordered
    ``events``, the ``spans`` tree, plus ``phantom_free`` and the
    ``event_count`` / ``span_count`` / ``dispatch_span_count`` tallies (the SC-001
    span-coverage denominator). Raises ``AuditTraceNotFoundError`` when no run was
    persisted and ``PhantomInputError`` when the trail fails the invariant.
    """
    root = Path(root_dir) if root_dir is not None else Path(".")
    run_path = root / ".cexai" / "topology" / "runs" / f"{run_id}.json"
    try:
        raw_record = run_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise AuditTraceNotFoundError(run_id, str(run_path)) from None

    record = json.loads(raw_record)
    events: list[dict[str, Any]] = list(record.get("events", []))
    spans: list[dict[str, Any]] = _merge_spans(
        list(record.get("spans", [])), _read_buffered_spans(root)
    )

    # SC-004 / 03 US P3: refuse to certify a trace with a phantom input.
    verify_phantom_free(events)

    dispatch_spans = [s for s in spans if s.get("operation") in _DISPATCH_OPERATIONS]
    return {
        "run_id": record.get("run_id", run_id),
        "topology_id": record.get("topology_id"),
        "status": record.get("status"),
        "started_at": record.get("started_at"),
        "completed_at": record.get("completed_at"),
        "events": events,
        "spans": spans,
        "phantom_free": True,
        "event_count": len(events),
        "span_count": len(spans),
        "dispatch_span_count": len(dispatch_spans),
    }


def verify_phantom_free(events: list[dict[str, Any]]) -> None:
    """Assert the zero-phantom-input invariant over an event trail (SC-004 / US P3):
    every ``from_node`` is ``None`` (an initial event) or names a node reached in the
    run (some event's ``to_node``). Raises ``PhantomInputError`` on the first
    violation; returns ``None`` when the trail is clean."""
    produced = {event.get("to_node") for event in events}
    for event in events:
        source = event.get("from_node")
        if source is not None and source not in produced:
            raise PhantomInputError(str(event.get("event_id", "?")), str(source))


def _read_buffered_spans(root: Path) -> list[dict[str, Any]]:
    """Read graceful-degrade spans from ``{root}/.cexai/traces/buffer/*.jsonl`` (one
    JSON span per line, FR-003). A partial/corrupt line is skipped, never fatal -- an
    audit must still reconstruct what IS readable."""
    buffer_dir = root / ".cexai" / "traces" / "buffer"
    if not buffer_dir.exists():
        return []
    spans: list[dict[str, Any]] = []
    for path in sorted(buffer_dir.glob("*.jsonl")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            try:
                spans.append(json.loads(stripped))
            except json.JSONDecodeError:
                continue
    return spans


def _merge_spans(
    primary: list[dict[str, Any]], buffered: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Append buffered spans not already present in ``primary`` (dedupe by
    ``span_id``), preserving primary order then buffer order."""
    seen = {span.get("span_id") for span in primary}
    merged = list(primary)
    for span in buffered:
        span_id = span.get("span_id")
        if span_id not in seen:
            merged.append(span)
            seen.add(span_id)
    return merged

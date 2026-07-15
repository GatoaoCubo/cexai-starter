"""Runtime audit-record export (05_agno US P3 acceptance #1 -- the audit trail).

A durable, append-only JSONL trail of governance-relevant decisions: RBAC
denials ("rejected with ... audit log entry"), HITL verdicts, role-escalation
attempts. ``AuditRecord`` is a RUNTIME DATACLASS, NOT a registered kind -- N04
owns taxonomy; this lane registers NOTHING and does not touch
``.cex/kinds_meta.json``. (The lean ``audit_event`` kind, if any, is a later ADR
cell's call.) The record composes with tracing via an optional ``span_id`` so an
audit entry can point at the exact span where a decision was taken.

Offline (Article XIV): a local file sink only -- no live collector. ``export_audit``
appends one JSON object per record to ``.cexai/audit/{mission_id}.jsonl``.

absorbs: 05_agno/audit
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

__all__ = ["AuditRecord", "audit_path", "export_audit"]

# Shared read-only empty mapping -- a frozen dataclass cannot take a mutable dict
# default; one shared MappingProxyType is the safe immutable default for detail.
_EMPTY_DETAIL: Mapping[str, Any] = MappingProxyType({})


@dataclass(frozen=True, slots=True)
class AuditRecord:
    """One immutable entry in a mission's audit trail. ``timestamp`` is ISO-8601;
    ``actor`` is the principal/subject that attempted the action; ``operation`` is
    the action (e.g. ``dispatch``); ``outcome`` is the decision/result (e.g.
    ``allowed`` / ``denied`` / ``approved`` / ``timeout``); ``mission_id`` scopes
    the entry. ``span_id`` optionally references the tracing span where the
    decision occurred (audit <-> tracing composition); ``detail`` is a read-only
    bag for extra context (e.g. ``{role, http_status}`` on an RBAC denial)."""

    timestamp: str
    actor: str
    operation: str
    outcome: str
    mission_id: str
    span_id: str | None = None
    detail: Mapping[str, Any] = _EMPTY_DETAIL


def audit_path(mission_id: str, root_dir: str | Path | None = None) -> Path:
    """The conventional audit sink for a mission:
    ``{root_dir}/.cexai/audit/{mission_id}.jsonl`` (root_dir defaults to cwd)."""
    root = Path(root_dir) if root_dir is not None else Path(".")
    return root / ".cexai" / "audit" / f"{mission_id}.jsonl"


def export_audit(records: Iterable[AuditRecord], path: str | Path) -> Path:
    """Append ``records`` to ``path`` as JSON Lines (one object per record),
    creating parent directories as needed. Append (not truncate) so a trail
    accumulates across calls within a mission. Returns the written path."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(_record_to_dict(record), default=str))
            handle.write("\n")
    return target


def _record_to_dict(record: AuditRecord) -> dict[str, Any]:
    """JSON-safe projection of an ``AuditRecord`` (one trail line)."""
    return {
        "timestamp": record.timestamp,
        "actor": record.actor,
        "operation": record.operation,
        "outcome": record.outcome,
        "mission_id": record.mission_id,
        "span_id": record.span_id,
        "detail": dict(record.detail),
    }

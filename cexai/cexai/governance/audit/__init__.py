"""Audit subsystem -- audit_event record export (impl: v0.3-W3b).

Durable audit trail for governance-relevant events: RBAC denials (05_agno US P3
acceptance #1 -- "rejected with ... audit log entry"), role-escalation attempts
(US P3 edge case), and HITL verdicts. The NEW lean ``audit_event`` kind is
registered LATER by a dedicated W3b ADR cell -- NOT this wave (taxonomy-neutral).
No frozen contract types live here in W3a; W3b ships the record schema + exporter
behind this seam.

absorbs: 05_agno/audit
"""

from __future__ import annotations

from cexai.governance.audit.record import AuditRecord, audit_path, export_audit

__all__ = [
    "AuditRecord",
    "audit_path",
    "export_audit",
]

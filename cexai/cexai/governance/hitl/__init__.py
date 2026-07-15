"""HITL subsystem -- human-in-the-loop approval gates (impl: v0.3-W3b).

Pauses a HITL-tagged operation until a human approves, rejects, or the request
times out (05_agno US P2 / FR-004/005), with M-of-N approval policy (FR-010) and
a pluggable approval transport (v1 = file-based; email / Slack / webhook in v1.5,
FR-006). HITL policy reuses the existing ``hitl_config`` kind. The frozen
``ApprovalRequest`` / ``ApprovalStatus`` / ``ApprovalPolicy`` / ``ApprovalGate``
contracts live in ``cexai.governance._shared.types``; W3b ships the concrete
``FileApprovalGate`` behind that seam here.

Public surface:
  * ``FileApprovalGate`` -- the v1 file-based ``ApprovalGate`` (request / await /
    M-of-N resolution + the ``await_or_raise`` caller-side error seam).
  * ``record_verdict`` -- the offline approver helper that records a verdict in a
    request's watch file (the in-process stand-in for a human / v1.5 push channel).

The frozen contract sig ``tests/governance/contract`` imports ``FileApprovalGate``
by this exact name (mirrors the orchestration ``DefaultTopologyInterpreter`` seam),
so W3c can un-skip ``test_approval_gate_pauses_until_decision`` without editing it.

absorbs: 05_agno/hitl
"""

from cexai.governance.hitl.approver import record_verdict
from cexai.governance.hitl.file_gate import FileApprovalGate

__all__ = ["FileApprovalGate", "record_verdict"]

"""record_verdict -- the in-process approver helper for the file-based gate (05_agno US P2).

Stands in for the human (or automation) that records a verdict in a request's
watch file, so ``FileApprovalGate.await_decision`` can resolve WITHOUT a live human
or any infrastructure (Article XIV). This is the symmetric write side of the gate's
poll-and-resolve read side: the gate writes the pending record and reads verdicts;
this appends one ``{"approver", "verdict"}`` entry to that same file's ``verdicts``
list.

It is the offline-test counterpart of the v1.5 push transports (email / Slack /
webhook, FR-006) -- in production a human approves through one of those channels;
here a test calls ``record_verdict`` directly. ``verdict`` MUST be ``approve`` or
``deny`` (anything else is rejected loudly so a typo cannot leave a request pending
until it times out). M-of-N tallying (DISTINCT approvers, deny-vetoes) is the gate's
concern (``file_gate._resolve``); this helper just records one verdict faithfully.

``token`` (R-202 crypto-binding, optional): when the gate is configured with a
``verifier`` (see ``FileApprovalGate``), an ``approve`` only counts toward M if this
entry carries a ``token`` -- a signed JWS minted for the approving principal via
``cexai.governance.rbac.principal_signing.mint_principal_token``. Passing ``token``
here just persists it alongside ``approver``/``verdict``; this helper does not mint,
validate, or interpret it -- ``resolve_verdicts`` does that at resolution time. Left
``None`` (the default), the entry has no ``token`` key at all, so the on-disk record
for every pre-existing caller is unchanged (backward-compat).

absorbs: 05_agno/hitl
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

__all__ = ["record_verdict"]

_APPROVE = "approve"
_DENY = "deny"
_VALID_VERDICTS = (_APPROVE, _DENY)


def record_verdict(
    approvals_dir: Path | str,
    request_id: str,
    *,
    approver: str,
    verdict: str,
    token: str | None = None,
) -> None:
    """Append ``approver``'s ``verdict`` to the request's watch file under
    ``approvals_dir``. ``verdict`` must be ``'approve'`` or ``'deny'`` (rejected with
    ``ValueError`` otherwise). Raises ``FileNotFoundError`` if no pending request was
    emitted for ``request_id`` (the gate writes the file in ``request``).

    ``token`` (R-202, optional): a signed principal JWS to carry alongside this
    verdict, for gates configured with a crypto ``verifier``. Omitted (``None``, the
    default), the persisted entry has no ``token`` key -- byte-identical to every
    call site that predates this parameter."""
    if verdict not in _VALID_VERDICTS:
        raise ValueError(
            f"verdict must be one of {_VALID_VERDICTS!r}, got {verdict!r}"
        )
    path = Path(approvals_dir) / f"{request_id}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    entry: dict[str, Any] = {"approver": approver, "verdict": verdict}
    if token is not None:
        entry["token"] = token
    data.setdefault("verdicts", []).append(entry)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

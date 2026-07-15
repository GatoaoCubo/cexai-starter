"""CEXAI governance exception hierarchy (tracing + hitl + rbac).

Rooted at the foundation's ``CexaiError`` so a caller can still catch the whole
package with one ``except CexaiError``. ``GovernanceError`` is the v0.3-W3
subtree root; the leaves below map to the specific failure modes the 05_agno spec
names, with the spec-named signatures encoded as structured attributes so callers
and contract tests branch on fields (``.request_id``, ``.waited_seconds``, ...)
rather than parsing messages -- mirroring ``ProviderConfigError`` in the
foundation and ``PlanInvalidError`` in orchestration.

W3b MAY add more leaves under ``GovernanceError`` in their own lanes (e.g. a
``AuthTokenExpiredError`` carrying the 401 + ``WWW-Authenticate`` challenge of
FR-011, or an ``approval_request`` validation error); the names defined here are
FROZEN for v0.3-W3.

Spec provenance (cexai-specs/05_agno/spec.md):
  * ApprovalDeniedError  -> US P2 acceptance #3 -- human rejects; step marked
                            ``denied_by_human``. ApprovalDeniedError(request_id).
  * ApprovalTimeoutError -> US P2 acceptance #4 -- approval times out (default
                            24h); step marked ``approval_timeout``.
                            ApprovalTimeoutError(request_id, waited_seconds).
  * RbacForbiddenError   -> US P3 acceptance #1 / FR-007 -- viewer-role dispatch
                            rejected 403. RbacForbiddenError(subject, role, operation).
  * TraceExportError     -> US P1 acceptance #3 / FR-003 -- OTel collector
                            unreachable; spans buffer to
                            ``.cexai/traces/buffer/{mission_id}.jsonl`` and flush
                            on reconnect. TraceExportError(endpoint, buffer_path).

absorbs: 05_agno/governance
"""

from __future__ import annotations

from cexai.foundation._shared.errors import CexaiError

__all__ = [
    "GovernanceError",
    "GovernanceDenied",
    "ApprovalDeniedError",
    "ApprovalTimeoutError",
    "RbacForbiddenError",
    "TraceExportError",
]


class GovernanceError(CexaiError):
    """Root of the governance subtree -- a tracing, HITL, or RBAC failure.
    Subclasses ``CexaiError`` so a single ``except CexaiError`` covers it."""


class GovernanceDenied(Exception):
    """Dedicated base for SECURITY-DENY exceptions across the governance crypto
    (CONVERGENCE T7/T8) -- audit R5.

    THE PROBLEM IT FIXES: the security-deny exceptions (``PrincipalTokenError``,
    ``CrossTenantInferenceDenied``, ``ModelLoadDenied``, ``KnowledgeBomError``,
    ``CycloneDxBomError``, ``EnvelopeKeyError``, ``TransparencyLogError``,
    ``StatusListError``) historically subclassed ``ValueError``. A generic, idiomatic
    ``except ValueError`` somewhere upstream (input parsing, coercion) would then
    SWALLOW a security deny -- a fail-OPEN under a common caller mistake. Re-basing
    those classes to ``GovernanceDenied`` (which does NOT inherit ``ValueError``)
    means a deny can only be caught by ``except GovernanceDenied`` (or the specific
    type), never by an accidental ``except ValueError``.

    DELIBERATELY NOT a ``ValueError`` and NOT a ``CexaiError`` subtree member: a
    security deny is its own category. Catch it explicitly. The leaf classes keep
    their own ``.reason`` field + constructor identical; only the base changed, so
    ``pytest.raises(ModelLoadDenied)`` and friends are unaffected."""


# --------------------------------------------------------------------------- #
# HITL / approval gates (cexai-specs/05_agno US P2)                            #
# --------------------------------------------------------------------------- #
class ApprovalDeniedError(GovernanceError):
    """A human rejected a HITL-gated operation (05 US P2 acceptance #3). The
    action aborts and the mission marks the step ``denied_by_human``;
    ``request_id`` identifies the rejected ``ApprovalRequest``."""

    def __init__(self, request_id: str) -> None:
        self.request_id = request_id
        super().__init__(f"approval request {request_id!r} denied by human")


class ApprovalTimeoutError(GovernanceError):
    """A HITL approval was not granted before the deadline (05 US P2 acceptance
    #4, default 24h). The action aborts and the mission marks the step
    ``approval_timeout``; ``request_id`` identifies the request and
    ``waited_seconds`` is how long the gate waited before timing out."""

    def __init__(self, request_id: str, waited_seconds: float) -> None:
        self.request_id = request_id
        self.waited_seconds = waited_seconds
        super().__init__(
            f"approval request {request_id!r} timed out after {waited_seconds}s"
        )


# --------------------------------------------------------------------------- #
# RBAC / authorization (cexai-specs/05_agno US P3)                             #
# --------------------------------------------------------------------------- #
class RbacForbiddenError(GovernanceError):
    """A token's role is not permitted to perform an operation (05 US P3
    acceptance #1 / FR-007) -- e.g. a ``viewer`` attempting dispatch. Maps to
    HTTP 403; ``http_status`` carries it for transport layers. ``subject``,
    ``role``, and ``operation`` are surfaced for the audit-log entry."""

    http_status: int = 403

    def __init__(self, subject: str, role: str, operation: str) -> None:
        self.subject = subject
        self.role = role
        self.operation = operation
        super().__init__(
            f"role {role!r} (subject {subject!r}) forbidden from {operation!r} [403]"
        )


# --------------------------------------------------------------------------- #
# Tracing / OTel export (cexai-specs/05_agno US P1)                            #
# --------------------------------------------------------------------------- #
class TraceExportError(GovernanceError):
    """The OTel collector at ``endpoint`` was unreachable (05 US P1 acceptance #3
    / FR-003). This is the graceful-degradation MARKER: the mission proceeds and
    spans are buffered to ``buffer_path`` (``.cexai/traces/buffer/{mission_id}.
    jsonl``), flushed on the next successful collector connection. Carried, not
    necessarily raised to the caller -- W3b may catch it internally to switch to
    the local buffer rather than abort the mission."""

    def __init__(self, endpoint: str, buffer_path: str) -> None:
        self.endpoint = endpoint
        self.buffer_path = buffer_path
        super().__init__(
            f"OTel collector {endpoint!r} unreachable; buffering spans to {buffer_path!r}"
        )

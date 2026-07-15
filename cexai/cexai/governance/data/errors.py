"""Data-plane deny leaf -- the tenant-boundary 403 of the Supabase adapter
(mission MULTITENANT_DATA_PLANE, task T1).

``TenantDataDenied`` is the data lane's sibling of the inference lane's
``CrossTenantInferenceDenied`` (``governance.rbac.inference_gate``). It subclasses
the frozen ``cexai.governance._shared.errors.GovernanceDenied`` -- NOT
``ValueError`` -- the SAME security-deny posture as ``PrincipalTokenError`` /
``CrossTenantInferenceDenied`` / ``EnvelopeKeyError``. A security deny must NOT be
swallowed by a generic, idiomatic ``except ValueError`` somewhere upstream (input
parsing, coercion); rebasing on ``GovernanceDenied`` (which does NOT inherit
``ValueError``) means a deny can only be caught by ``except GovernanceDenied`` (or
this specific type). That is a fail-CLOSED choice: under a common caller mistake
the deny still propagates.

The leaf carries a ``reason`` token in {``missing_tenant``, ``cross_tenant``,
``claim_bind_failed``} plus the ``bound`` / ``target`` tenants (when known) and the
``op``, so an audit log records the denied pair WITHOUT re-parsing the message
(field-branching, mirroring ``CrossTenantInferenceDenied``). NEVER raised on an
allowed call.

ASCII-only per .claude/rules/ascii-code-rule.md.

absorbs: convergence/multitenant-data-plane (T1 -- data-plane deny surface)
"""

from __future__ import annotations

from cexai.governance._shared.errors import GovernanceDenied

__all__ = [
    "TenantDataDenied",
]


class TenantDataDenied(GovernanceDenied):
    """A data-plane call was denied because it could not be bound to a tenant or
    crossed a tenant boundary (mission MULTITENANT_DATA_PLANE, the data deny
    surface).

    Subclasses ``GovernanceDenied`` (audit R5) -- NOT ``ValueError`` -- so an
    accidental ``except ValueError`` upstream cannot swallow the deny; a caller
    catches it via ``except GovernanceDenied`` (or this specific type). Mirrors
    ``CrossTenantInferenceDenied`` field-for-field so the file / inference / data
    deny surfaces report identically.

    Carries:
      * ``reason`` -- one of ``missing_tenant`` (no usable tenant supplied,
        fail-closed deny-by-default -- the data path has no global single-tenant
        mode), ``cross_tenant`` (the bound tenant and the target tenant differ),
        ``claim_bind_failed`` (the session claim could not be set on the
        connection, so RLS cannot be relied on -- refuse rather than run unscoped).
      * ``bound`` / ``target`` -- the tenant pair (when known) for the audit log.
      * ``op`` -- the operation tag (default ``data``)."""

    def __init__(
        self,
        reason: str,
        *,
        bound: str | None = None,
        target: str | None = None,
        op: str = "data",
    ) -> None:
        self.reason = reason
        self.bound = bound
        self.target = target
        self.op = op
        if reason == "cross_tenant":
            message = (
                f"cross-tenant {op} DENIED -- principal bound to {bound!r} may not "
                f"touch tenant {target!r} (fail-closed)"
            )
        elif reason == "missing_tenant":
            message = (
                f"{op} DENIED -- no usable tenant supplied; cannot bind the data "
                f"call (fail-closed)"
            )
        elif reason == "claim_bind_failed":
            message = (
                f"{op} DENIED -- could not bind the session claim for tenant "
                f"{bound!r}; RLS cannot be relied on (fail-closed)"
            )
        else:
            message = f"{op} DENIED -- {reason} (fail-closed)"
        super().__init__(message)

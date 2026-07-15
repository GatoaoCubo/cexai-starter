"""Framework-side inference deny-surface -- bind an inference call to the VERIFIED
principal's tenant (CONVERGENCE T8, Component 2 + the inference gate).

This is the second half of the C2 brick (the first is ``envelope_keys.py``). It
closes the ADR's SIXTH deny surface: the inference call itself. Components 1-5 of
the trust model gate identity, transport, routing, residency, and federation;
this gate adds the rule that a principal bound to tenant A may NEVER run inference
against tenant B -- enforced at the moment of the inference request, on the
framework side, using the ``tenant`` claim that Component 1's verifier already
validated.

The contract chain (C1 -> C2):
    1. ``mint_principal_token`` issues a signed JWS carrying ``{..., tenant}``.
    2. ``make_principal_verifier`` (C1) verifies alg/sig/exp/aud/iss/replay and
       returns the VALIDATED claims dict (it raises on any failure; a dict in
       hand means the principal is authentic).
    3. ``authorize_inference`` (here) reads ``claims["tenant"]`` -- the bound
       tenant -- and refuses any inference whose target tenant differs. The
       binding is to the VERIFIED claim, never to a caller-supplied tenant, so an
       attacker cannot assert "I am tenant B" without a B-signed token.

Why a LOCAL equality check instead of importing ``_tools.cex_tenant_paths.
deny_cross_tenant``:
    ``deny_cross_tenant`` is the canonical fail-closed cross-tenant primitive and
    this gate enforces the SAME invariant (string equality, deny-by-default,
    fail-closed on mismatch). Reuse was attempted and REJECTED for a concrete
    reason: ``cex_tenant_paths`` lives in the repo-root ``_tools/`` tree and does
    ``from cex_bootstrap import _safe_tenant_id, ROOT, TENANTS_DIR`` at import
    time. The ``cexai`` package is a self-contained subtree (see cexai/
    pyproject.toml: "designed for eventual extraction into its own repository ...
    does NOT discover this tree") -- importing ``_tools`` would (a) fail outright
    from the package context (``ModuleNotFoundError: cex_tenant_paths``, verified)
    and (b) even if force-pathed, drag monorepo filesystem state (ROOT/TENANTS_DIR
    + a .cex/tenants/ layout) into the governance lane, breaking extractability.
    So this module MIRRORS the invariant rather than importing it. The mirrored
    contract, kept deliberately identical to ``deny_cross_tenant``:
      * compare a requested TARGET tenant against the BOUND tenant;
      * fail-closed: on any mismatch DENY (raise), never widen scope;
      * deny-by-default: a missing/empty bound tenant is treated as UNSAFE here
        (raise) -- this DIFFERS from ``deny_cross_tenant``'s single-tenant
        convenience (it returns the target when no tenant is bound, because in
        that tool an unset ``CEX_TENANT_ID`` means "global single-tenant mode").
        On the inference path there is no global mode: a verified principal that
        carries no tenant claim cannot be safely bound, so we REFUSE. Fail-closed
        on the inference call is the stricter, correct posture.
    If a future refactor makes ``deny_cross_tenant`` cleanly importable from the
    package (e.g. it is moved into ``cexai``), this local check SHOULD be swapped
    for it so there is one equality primitive. The ``_deny_cross_tenant_equality``
    helper isolates the mirrored logic to make that swap a one-function change.

HONEST CAVEAT (ADR honest-floor / council finding -- framework vs fabric):
    This is the FRAMEWORK gate. It stops the framework from DISPATCHING an
    inference request that crosses tenants. It CANNOT enforce what the inference
    FABRIC does: the fabric must ALSO refuse to serve tenant-B model weights on a
    tenant-A-keyed session (the matching custody rule to ``envelope_keys`` --
    DEKs ephemeral / non-co-resident). That fabric behavior is a Phase-2 contract
    obligation. The framework gate alone narrows, but does not close, the
    cross-tenant inference surface; the proof requires the fabric to honor its
    half.

ASCII-only per .claude/rules/ascii-code-rule.md.

absorbs: convergence/t8-trust-model (Component 2 -- inference deny-surface)
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from cexai.governance._shared.errors import GovernanceDenied

__all__ = [
    "CrossTenantInferenceDenied",
    "authorize_inference",
]


class CrossTenantInferenceDenied(GovernanceDenied):
    """An inference call was denied because it crossed a tenant boundary or could
    not be bound to a verified tenant (CONVERGENCE T8, Component 2 -- the sixth
    deny surface).

    Subclasses ``GovernanceDenied`` (audit R5) -- NOT ``ValueError`` -- the same
    security-deny posture as ``PrincipalTokenError`` / ``EnvelopeKeyError``. A
    security deny must NOT be swallowed by a generic ``except ValueError`` upstream;
    a caller catches it via ``except GovernanceDenied`` (or this specific type).
    RAISED fail-closed by
    ``authorize_inference`` whenever the target tenant differs from the bound
    tenant, or the verified claims carry no usable tenant. Carries a ``reason``
    token (``cross_tenant`` | ``missing_bound_tenant`` | ``missing_target``) plus
    the ``bound`` / ``target`` tenants (when known) so the audit log records the
    denied pair without re-parsing the message. NEVER raised on an allowed call."""

    def __init__(
        self,
        reason: str,
        *,
        bound: str | None = None,
        target: str | None = None,
        op: str = "infer",
    ) -> None:
        self.reason = reason
        self.bound = bound
        self.target = target
        self.op = op
        if reason == "cross_tenant":
            message = (
                f"cross-tenant {op} DENIED -- principal bound to {bound!r} may not "
                f"run inference against {target!r} (fail-closed)"
            )
        elif reason == "missing_bound_tenant":
            message = (
                f"{op} DENIED -- verified principal carries no tenant claim; cannot "
                f"bind inference (fail-closed)"
            )
        elif reason == "missing_target":
            message = f"{op} DENIED -- no target tenant supplied (fail-closed)"
        else:
            message = f"{op} DENIED -- {reason} (fail-closed)"
        super().__init__(message)


def _deny_cross_tenant_equality(target: str, bound: str, op: str) -> str:
    """The mirrored cross-tenant equality invariant (see module docstring).

    Deliberately identical in semantics to ``_tools.cex_tenant_paths.
    deny_cross_tenant``'s core check: fail-closed STRING EQUALITY -- a principal
    bound to ``bound`` may touch ``target`` ONLY when ``target == bound``. Returns
    the validated target on allow; raises ``CrossTenantInferenceDenied`` on
    mismatch. Isolated as its own function so that if ``deny_cross_tenant`` ever
    becomes cleanly importable from this package, the swap is a one-line change
    here and nowhere else.

    NOTE on the comparison: like ``deny_cross_tenant`` this is exact byte/string
    equality with no normalization. The tenant value compared is the one the C1
    verifier already validated as part of an authentic signed token, so it is
    trusted input; we do not re-sanitize it (re-running a ``_safe_tenant_id``
    style guard here would duplicate the bootstrap guard and is out of this
    module's scope -- the token signature is the integrity guarantee)."""
    if target != bound:
        raise CrossTenantInferenceDenied(
            "cross_tenant", bound=bound, target=target, op=op
        )
    return target


def authorize_inference(
    verified_claims: Mapping[str, Any],
    target_tenant_id: str,
    op: str = "infer",
) -> str:
    """Authorize an inference call against ``target_tenant_id`` for the principal
    described by ``verified_claims`` (CONVERGENCE T8, Component 2 inference gate).

    INFERENCE-GATE CONTRACT (so N07 can re-run + adversarially review):
      * Input ``verified_claims``: the dict returned by C1's
        ``make_principal_verifier`` callable -- i.e. claims that have ALREADY
        passed alg-pin + signature + exp + aud + iss + replay. This gate does NOT
        re-verify the token; presenting unverified/attacker-controlled claims here
        is a caller bug (the whole point of C1 is that you call the verifier
        first, then pass its output here). The binding tenant is taken from
        ``verified_claims["tenant"]`` -- the VERIFIED claim, never a
        caller-asserted value.
      * Input ``target_tenant_id``: the tenant whose data/model the inference
        would touch.
      * On ALLOW (target tenant == bound tenant): returns the validated
        ``target_tenant_id`` (string), so a caller can use the return value as the
        confirmed tenant.
      * On DENY: RAISES ``CrossTenantInferenceDenied`` (a ``ValueError`` subclass)
        with a ``.reason`` field. The function NEVER returns on deny and NEVER
        silently downgrades to a permissive path.

    Deny conditions, fail-closed, in order:
      1. ``missing_bound_tenant`` -- ``verified_claims`` has no ``tenant`` key, or
         it is empty/blank. A verified principal with no tenant cannot be bound to
         a tenant scope, so inference is REFUSED (deny-by-default). This is the
         intentional divergence from ``deny_cross_tenant`` (which permits an
         unbound principal under "global single-tenant mode") -- on the inference
         path there is no global mode; an unbindable principal is denied.
      2. ``missing_target`` -- ``target_tenant_id`` is empty/blank. Without a
         target there is nothing to authorize; REFUSED.
      3. ``cross_tenant`` -- the bound tenant and the target tenant differ
         (string inequality). This is the core ADR invariant: a principal bound to
         tenant A may NEVER run inference against tenant B. REFUSED.

    HONEST CAVEAT (framework vs fabric): an ALLOW here means the FRAMEWORK will not
    dispatch a cross-tenant inference. It does NOT guarantee the inference FABRIC
    refuses to serve another tenant's weights on this session -- that is the
    Phase-2 fabric contract (see module docstring + ``envelope_keys``)."""
    bound_raw = verified_claims.get("tenant")
    bound = "" if bound_raw is None else str(bound_raw).strip()
    if not bound:
        raise CrossTenantInferenceDenied("missing_bound_tenant", op=op)

    target = "" if target_tenant_id is None else str(target_tenant_id).strip()
    if not target:
        raise CrossTenantInferenceDenied("missing_target", bound=bound, op=op)

    return _deny_cross_tenant_equality(target, bound, op)

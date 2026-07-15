# -*- coding: ascii -*-
"""Supabase JWT verification + tenant extraction (mission CEXAI_PRODUCT_RUNTIME, T3).

THE #1 SECURITY RULE (spec_cexai_product_build_v1 B.3 INVARIANTS):
    tenant_id is resolved ONLY from a VERIFIED Supabase JWT claim. A client may not
    pass tenant_id; if it does, it is IGNORED. This module is the single chokepoint
    that turns a bearer token into a trusted tenant_id -- nothing downstream reads a
    client-supplied tenant.

The Supabase Auth JWT carries the tenant under ``app_metadata.tenant_id`` (the
end-user plane, coalesce branch 2 in spec_multitenant_data_plane_v1 B.2). Some
service / agent tokens instead carry a TOP-LEVEL ``tenant_id`` (coalesce branch 1).
``extract_tenant_id`` COALESCES the two: app_metadata first (the documented end-user
shape), then top-level, exactly mirroring the DB-side ``coalesce(branch1, branch2)``.

VERIFICATION (fail-closed):
    * HS256 with the project's ``SUPABASE_JWT_SECRET`` (the default Supabase Auth
      signing scheme) -- the symmetric secret is held SERVER-SIDE only.
    * ``aud`` defaults to "authenticated" (the Supabase Auth audience). Set
      ``SUPABASE_JWT_AUD=""`` to disable the audience check (NOT recommended).
    * expiry (``exp``) is always enforced by PyJWT.
    * ANY failure -- bad signature, expired, missing/empty secret, malformed token,
      missing tenant claim -- raises AuthError (-> HTTP 401). Never returns a partial
      identity. There is no "anonymous tenant" and no env fallback for the tenant.

ASCII-only per .claude/rules/ascii-code-rule.md. No network at import; the secret is
read lazily (per request) so the app starts even before the env is fully configured
(a missing secret then fails CLOSED at verify time with 401, never open).
"""

from __future__ import annotations

import os
from typing import Any, Dict, Mapping, Optional

import jwt  # PyJWT
from jwt import InvalidTokenError, PyJWKClient

__all__ = [
    "AuthError",
    "verify_supabase_jwt",
    "extract_tenant_id",
    "bearer_token_from_header",
]

# Env var names (server-side only; never sent to the browser).
ENV_JWT_SECRET = "SUPABASE_JWT_SECRET"       # HS256 symmetric secret (Supabase default)
ENV_JWT_AUD = "SUPABASE_JWT_AUD"             # expected audience; "" disables the check
ENV_JWKS_URL = "SUPABASE_JWKS_URL"           # optional: RS256/ES256 asymmetric verify
ENV_JWT_ALGS = "SUPABASE_JWT_ALGORITHMS"     # optional CSV override of allowed algs

# Supabase Auth defaults.
_DEFAULT_AUD = "authenticated"
_DEFAULT_HS_ALG = "HS256"
_DEFAULT_JWKS_ALGS = ("RS256", "ES256")

# Claim fields carrying the tenant. app_metadata is the END-USER plane (branch 2);
# top-level is the AGENT/service plane (branch 1). We coalesce app_metadata FIRST.
_APP_METADATA_FIELD = "app_metadata"
_TENANT_FIELD = "tenant_id"


class AuthError(Exception):
    """Raised on ANY auth failure: missing/bad/expired token, missing secret, or a
    token with no usable tenant claim. The API layer maps this to HTTP 401.

    Carries ``.reason`` (a short machine code) and ``.detail`` (a safe human string).
    NEVER carries the token, the secret, or any key material.
    """

    def __init__(self, reason: str, *, detail: str = "") -> None:
        self.reason = reason
        self.detail = detail
        msg = "auth failed: %s" % reason
        if detail:
            msg += " -- %s" % detail
        super().__init__(msg)


def bearer_token_from_header(authorization: Optional[str]) -> str:
    """Extract the raw token from an ``Authorization: Bearer <jwt>`` header value.

    Fail-closed: a missing header, a non-Bearer scheme, or an empty token raises
    AuthError('missing_token'). The scheme match is case-insensitive ("bearer" ok).
    """
    if not authorization:
        raise AuthError("missing_token", detail="no Authorization header")
    parts = authorization.split(None, 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthError("missing_token", detail="expected 'Bearer <token>'")
    token = parts[1].strip()
    if not token:
        raise AuthError("missing_token", detail="empty bearer token")
    return token


def _allowed_algorithms(asymmetric: bool) -> list[str]:
    """Resolve the allowed signing algorithms (env override -> sane defaults).

    Pinned to a closed allowlist so an attacker cannot down-grade to ``none`` or swap
    HS256<->RS256. ``SUPABASE_JWT_ALGORITHMS`` (CSV) overrides; otherwise HS256 for the
    secret path and RS256/ES256 for the JWKS path.
    """
    override = os.environ.get(ENV_JWT_ALGS, "").strip()
    if override:
        algs = [a.strip() for a in override.split(",") if a.strip()]
        if algs:
            return algs
    return list(_DEFAULT_JWKS_ALGS) if asymmetric else [_DEFAULT_HS_ALG]


def _audience_kwargs() -> Dict[str, Any]:
    """Build the audience-related kwargs for ``jwt.decode``.

    Default audience is "authenticated" (Supabase Auth). If ``SUPABASE_JWT_AUD`` is set
    to the empty string, audience verification is disabled (operator opt-out, logged by
    the caller's config -- not recommended). If set to a value, that value is required.
    """
    raw = os.environ.get(ENV_JWT_AUD)
    if raw is None:
        return {"audience": _DEFAULT_AUD}
    raw = raw.strip()
    if raw == "":
        # Explicit opt-out: disable the audience check.
        return {"options": {"verify_aud": False}}
    return {"audience": raw}


def _decode_with_secret(token: str) -> Dict[str, Any]:
    """HS256 path: verify with the symmetric ``SUPABASE_JWT_SECRET`` (Supabase default).

    Fail-closed: an unset/empty secret raises AuthError('no_secret') -- we never fall
    back to an unverified decode. Signature/expiry/audience failures raise
    AuthError('invalid_token').
    """
    secret = os.environ.get(ENV_JWT_SECRET, "")
    if not secret:
        raise AuthError(
            "no_secret",
            detail="%s is not set; cannot verify JWT" % ENV_JWT_SECRET,
        )
    aud_kwargs = _audience_kwargs()
    options = aud_kwargs.pop("options", {})
    try:
        claims = jwt.decode(
            token,
            secret,
            algorithms=_allowed_algorithms(asymmetric=False),
            options=options,
            **aud_kwargs,
        )
    except InvalidTokenError as exc:
        raise AuthError("invalid_token", detail=str(exc)) from exc
    return dict(claims)


def _decode_with_jwks(token: str, jwks_url: str) -> Dict[str, Any]:
    """JWKS path: verify with the project's published public keys (RS256/ES256).

    Used when the operator configures ``SUPABASE_JWKS_URL`` (asymmetric signing). The
    signing key is selected from the token's ``kid`` against the JWKS. Any failure
    raises AuthError('invalid_token').
    """
    aud_kwargs = _audience_kwargs()
    options = aud_kwargs.pop("options", {})
    try:
        jwk_client = PyJWKClient(jwks_url)
        signing_key = jwk_client.get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=_allowed_algorithms(asymmetric=True),
            options=options,
            **aud_kwargs,
        )
    except AuthError:
        raise
    except InvalidTokenError as exc:
        raise AuthError("invalid_token", detail=str(exc)) from exc
    except Exception as exc:  # JWKS fetch / key-selection failure -> fail closed
        raise AuthError("jwks_error", detail=str(exc)) from exc
    return dict(claims)


def verify_supabase_jwt(token: str) -> Dict[str, Any]:
    """Verify a Supabase Auth JWT and return its claims (the ONLY trusted identity).

    Picks the verification path from the environment:
      * ``SUPABASE_JWKS_URL`` set  -> asymmetric (RS256/ES256) via the project JWKS.
      * otherwise                  -> symmetric HS256 via ``SUPABASE_JWT_SECRET``.

    Fail-closed: every failure raises AuthError. The returned claims are a plain dict;
    callers must still pull the tenant via ``extract_tenant_id`` (never trust a raw
    field without going through that coalesce + non-empty check).
    """
    if not token or not token.strip():
        raise AuthError("missing_token", detail="empty token")
    jwks_url = os.environ.get(ENV_JWKS_URL, "").strip()
    if jwks_url:
        return _decode_with_jwks(token, jwks_url)
    return _decode_with_secret(token)


def _coerce_tenant(value: Any) -> str:
    """Project a raw claim value to a stripped string ('' if absent/None).

    Mirrors the adapter's ``_coerce_tenant`` so the API edge and the data plane agree
    on what 'no usable tenant' means (empty -> fail-closed deny).
    """
    if value is None:
        return ""
    return str(value).strip()


def extract_tenant_id(claims: Mapping[str, Any]) -> str:
    """Extract the tenant_id from VERIFIED claims (coalesce: app_metadata, then top-level).

    THE SECURITY-CRITICAL FUNCTION. The tenant is read ONLY from these two verified-claim
    locations -- never from a request body, query string, or header other than the signed
    JWT itself:
      1. ``claims['app_metadata']['tenant_id']``  -- the documented Supabase end-user shape
         (spec_multitenant_data_plane_v1 B.2 coalesce branch 2). Checked FIRST.
      2. ``claims['tenant_id']``                  -- a top-level claim (agent/service plane,
         coalesce branch 1). Fallback.

    Fail-closed: if neither yields a non-empty value, raises AuthError('missing_tenant')
    (-> HTTP 401). A token without a tenant is not a usable identity for a tenant-scoped
    API; we refuse rather than guess.

    R-010 AMBIGUOUS-CLAIMS GUARD (2-plane identity precedence fix): the DB-side RLS
    ``tenant_boundary`` policy (every ``supabase/migrations/2026061*_*.sql`` -- see
    e.g. ``20260616000001_tenant_memory.sql`` lines ~99-102) coalesces the SAME two
    claim locations in the OPPOSITE order -- top-level FIRST, app_metadata second:
        coalesce(claims->>'tenant_id', claims->'app_metadata'->>'tenant_id')
    Historically, this function silently picked app_metadata whenever BOTH claims were
    present and DIFFERENT, while a raw-JWT-consuming DB-side path (any direct-to-
    Postgres/PostgREST access bypassing this API's own claim-rebuild in
    ``cexai...adapter.bind_session_tenant``, which re-injects ONLY the value THIS
    function already resolved) would pick top-level -- a SILENT, opposite-precedence
    divergence for the exact JWT shape this ADR exists to prevent (docs/
    AUDIT_CLAIMS_VS_REALITY_2026_07_02.md D2.5 / register row R-010). Today this is
    LATENT (no token-minting path in this repo ever sets both claims on one token --
    end-user tokens carry ONLY app_metadata, agent/service tokens carry ONLY
    top-level), but nothing in the code enforced that mutual exclusivity.

    Rather than flip this function's precedence (a change to a DIFFERENT, equally
    security-critical, already-tested contract -- see test_extract_tenant_ambiguous_
    claims_disagree_raises for the full architectural-tradeoff note), a JWT that
    carries BOTH claims with DIFFERING values now FAILS CLOSED (AuthError
    'ambiguous_tenant_claims' -> 401) instead of silently resolving to whichever
    layer's precedence the caller happens to hit -- the two layers can no longer
    silently disagree on which tenant a request is for. Equal-valued duplicate claims
    (both present, same value) are unaffected -- there is no ambiguity to refuse.
    """
    app_meta = claims.get(_APP_METADATA_FIELD)
    app_meta_tenant = ""
    if isinstance(app_meta, Mapping):
        app_meta_tenant = _coerce_tenant(app_meta.get(_TENANT_FIELD))
    top_level_tenant = _coerce_tenant(claims.get(_TENANT_FIELD))

    if app_meta_tenant and top_level_tenant and app_meta_tenant != top_level_tenant:
        raise AuthError(
            "ambiguous_tenant_claims",
            detail="app_metadata and top-level tenant_id claims disagree",
        )
    if app_meta_tenant:
        return app_meta_tenant
    if top_level_tenant:
        return top_level_tenant
    raise AuthError(
        "missing_tenant",
        detail="no tenant_id in app_metadata or top-level claims",
    )

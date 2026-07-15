"""Per-tenant envelope-key hierarchy -- KEK -> DEK derivation via HKDF-SHA256
(CONVERGENCE T8, Component 2 -- the per-tenant scoped key custody half).

This is the SECOND brick of the T8 signing/identity foundation
(N05_operations/P08_architecture/p08_adr_convergence_trust_model.md, Component 2).
Component 1 (``principal_signing.py``) stood up signed-principal identity; this
module stands up the KEY hierarchy that makes the ADR's blast-radius claim true:
a leaked Data Encryption Key (DEK) burns ONE tenant/session, not the whole
fabric. The hierarchy is three deterministic HKDF hops:

    root KEK  (32 random bytes, the in-process root)
        |  HKDF-SHA256, info = b"cex-tenant:" + tenant_id
        v
    tenant KEK  (per-tenant Key Encryption Key)
        |  HKDF-SHA256, info = b"cex-session:" + session_id
        v
    session DEK  (per-session Data Encryption Key)

Key properties (the security argument, ADR Component 2):
  * DISTINCT tenants -> DISTINCT tenant KEKs (different ``info`` label).
  * DISTINCT sessions -> DISTINCT session DEKs (different ``info`` label).
  * SAME inputs -> IDENTICAL bytes (HKDF is a deterministic PRF -- no random
    salt; the caller can re-derive a DEK from (root, tenant, session) rather
    than store it). This determinism is what lets the fabric re-derive a DEK on
    demand instead of holding a key vault of them.
  * A leaked DEK reveals nothing about the tenant KEK or root KEK (HKDF is
    one-way), and a leaked tenant KEK reveals nothing about a SIBLING tenant's
    KEK -- so the blast radius of any single key compromise is bounded to the
    sub-tree below it.

HONEST CAVEATS (stated, not hidden -- ADR honest-floor / council finding):
  * The root KEK is generated and held IN PROCESS for v1. Custody of the root in
    an HSM / KMS (so the root never lives in fabric memory) is a v2 SPEC
    obligation (ADR Component 2 / Component 6). ``generate_root_kek`` says so.
  * This module is the FRAMEWORK half of Component 2. The blast-radius reduction
    is only *proven* once the FABRIC honors the matching custody contract:
    DEKs must be ephemeral, zeroized after use, and NON-CO-RESIDENT in fabric
    memory (no two tenants' DEKs live in the same address space at once). That
    fabric-side behavior is a Phase-2 vendor_fabric contract obligation; deriving a
    distinct key here does NOT by itself stop a fabric that keeps every DEK warm
    in one heap. The framework derives correctly; the fabric must hold correctly.

Dependency: ``cryptography`` (HKDF-SHA256 + os.urandom-backed key gen), verified
present (cryptography 46.0.7). Like ``principal_signing`` this is the T8 crypto
brick, so it imports the primitive at module load (not the lazy-import discipline
of the dormant RBAC dev path).

ASCII-only per .claude/rules/ascii-code-rule.md.

absorbs: convergence/t8-trust-model (Component 2 -- per-tenant envelope keys)
"""

from __future__ import annotations

import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from cexai.governance._shared.errors import GovernanceDenied

__all__ = [
    "ROOT_KEK_BYTES",
    "DERIVED_KEY_BYTES",
    "EnvelopeKeyError",
    "generate_root_kek",
    "derive_tenant_kek",
    "derive_session_dek",
]

# Root KEK size: 256-bit. 32 bytes of CSPRNG output is the standard root-secret
# width and matches the HKDF-SHA256 output width below (the root is itself a
# uniformly-random key, so it needs no extraction step before use as IKM).
ROOT_KEK_BYTES = 32

# Width of every derived key (tenant KEK + session DEK). SHA-256 -> 32 bytes.
# A single width keeps the hierarchy uniform: a tenant KEK is itself valid IKM
# for the next HKDF hop, so KEK and DEK share the 32-byte shape.
DERIVED_KEY_BYTES = 32

# HKDF ``info`` label prefixes. The label DOMAIN-SEPARATES the two derivation
# levels: even if a tenant_id and a session_id were byte-identical, the tenant
# KEK and the session DEK derived from them would differ, because the info
# strings ("cex-tenant:" vs "cex-session:") differ. This is the mechanism behind
# "distinct level -> distinct key" and is a deliberate anti-collision measure.
_TENANT_INFO_PREFIX = b"cex-tenant:"
_SESSION_INFO_PREFIX = b"cex-session:"

# No HKDF salt (salt=None). HKDF without a salt is still a sound PRF when the
# input keying material is already a uniformly-random key (our root KEK and
# tenant KEK both are). Omitting the salt is what makes derivation DETERMINISTIC:
# the same (IKM, info) pair always yields the same key, so the fabric can
# re-derive a DEK on demand instead of persisting a key vault. The domain
# separation that a salt would otherwise provide is supplied by the ``info``
# label instead.
_NO_SALT = None


class EnvelopeKeyError(GovernanceDenied):
    """An envelope-key derivation input was invalid (CONVERGENCE T8, Component 2).

    Subclasses ``GovernanceDenied`` (audit R5) -- NOT ``ValueError`` -- the same
    security-deny posture as ``PrincipalTokenError``. A security deny must NOT be
    swallowed by a generic ``except ValueError`` upstream; catch it via
    ``except GovernanceDenied`` (or this specific type). RAISED fail-closed when key
    material or a derivation label is missing/ill-typed -- a derivation MUST NOT
    silently fall
    back to a weaker or shared key. Carries a ``reason`` token (e.g.
    ``bad_root_kek``, ``empty_tenant_id``, ``empty_session_id``) so callers and
    the audit log branch on a field, not a parsed message."""

    def __init__(self, reason: str, detail: str = "") -> None:
        self.reason = reason
        message = f"envelope key rejected: {reason}"
        if detail:
            message = f"{message} -- {detail}"
        super().__init__(message)


def _as_label_bytes(value: object) -> bytes:
    """Coerce a tenant_id / session_id to bytes for use in an HKDF ``info`` label.

    Accepts ``str`` (UTF-8 encoded) or ``bytes`` as-is. This keeps the API
    ergonomic for the common string-id case while still allowing raw-bytes ids.
    The caller-facing emptiness check happens in the derive functions (so the
    raised ``reason`` is specific to which level was empty)."""
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return value.encode("utf-8")
    raise EnvelopeKeyError("bad_label_type", f"type={type(value).__name__}")


def _hkdf(ikm: bytes, info: bytes, length: int = DERIVED_KEY_BYTES) -> bytes:
    """One HKDF-SHA256 expansion of ``ikm`` under ``info`` to ``length`` bytes.

    The single derivation primitive shared by both hops. ``salt`` is None (see
    ``_NO_SALT`` rationale): derivation is deterministic so a DEK can be
    re-derived rather than stored. A fresh ``HKDF`` instance per call is required
    -- the cryptography ``HKDF`` object is single-use (``derive`` may be called
    once), which is also why this is not a module-level singleton."""
    kdf = HKDF(
        algorithm=hashes.SHA256(),
        length=length,
        salt=_NO_SALT,
        info=info,
    )
    return kdf.derive(ikm)


def generate_root_kek() -> bytes:
    """Generate the root Key Encryption Key: ``ROOT_KEK_BYTES`` (32) of CSPRNG
    output -- the single in-process root of the v1 envelope hierarchy.

    Uses ``os.urandom`` (the OS CSPRNG) so the root is uniformly random and thus
    valid HKDF input keying material without a separate extraction step.

    HONEST CAVEAT (ADR Component 2 / Component 6): for v1 the root is generated
    and held IN PROCESS. Production custody of the root in an HSM / KMS -- so the
    root secret NEVER materializes in fabric memory and a process compromise
    cannot exfiltrate it -- is a v2 SPEC obligation. This function is the v1
    in-process stand-in; the derivation hierarchy below it is custody-agnostic
    (it works identically whether the root comes from here or from a KMS unwrap),
    so swapping in HSM custody later does not change the derive API."""
    return os.urandom(ROOT_KEK_BYTES)


def derive_tenant_kek(root_kek: bytes, tenant_id: object) -> bytes:
    """Derive a tenant's Key Encryption Key from the root KEK (HKDF-SHA256).

    ``tenant_kek = HKDF(root_kek, info = b"cex-tenant:" + tenant_id)``.

    DISTINCT ``tenant_id`` values yield DISTINCT KEKs (the id is part of the info
    label); the SAME (root, tenant_id) always yields the SAME 32 bytes
    (deterministic PRF). One-way: a leaked tenant KEK does not reveal the root or
    any sibling tenant's KEK -- this is the per-tenant blast-radius boundary
    (ADR Component 2). Fail-closed: a non-bytes root or an empty tenant_id
    raises ``EnvelopeKeyError`` rather than deriving a degenerate key."""
    if not isinstance(root_kek, bytes) or not root_kek:
        raise EnvelopeKeyError("bad_root_kek", "root_kek must be non-empty bytes")
    tid = _as_label_bytes(tenant_id)
    if not tid:
        raise EnvelopeKeyError("empty_tenant_id")
    return _hkdf(root_kek, _TENANT_INFO_PREFIX + tid)


def derive_session_dek(tenant_kek: bytes, session_id: object) -> bytes:
    """Derive a session's Data Encryption Key from a tenant KEK (HKDF-SHA256).

    ``session_dek = HKDF(tenant_kek, info = b"cex-session:" + session_id)``.

    DISTINCT ``session_id`` values (under one tenant KEK) yield DISTINCT DEKs;
    the SAME (tenant_kek, session_id) always yields the SAME 32 bytes. Because
    the tenant KEK is itself tenant-scoped, two tenants with an identically-named
    session still get different DEKs (the tenant KEKs differ upstream). One-way:
    a leaked DEK does not reveal the tenant KEK -- so a single DEK compromise is
    bounded to ONE session of ONE tenant (the ADR's blast-radius claim).

    HONEST CAVEAT (ADR Component 2, council finding): this returns a correctly
    SCOPED DEK, but the blast-radius reduction is only realized once the FABRIC
    treats the DEK as ephemeral / zeroized / non-co-resident in its memory
    (Phase-2 vendor_fabric contract). The framework derives a distinct key; the
    fabric must refuse to keep every tenant's DEK warm in one address space.

    Fail-closed: a non-bytes tenant KEK or an empty session_id raises
    ``EnvelopeKeyError``."""
    if not isinstance(tenant_kek, bytes) or not tenant_kek:
        raise EnvelopeKeyError("bad_tenant_kek", "tenant_kek must be non-empty bytes")
    sid = _as_label_bytes(session_id)
    if not sid:
        raise EnvelopeKeyError("empty_session_id")
    return _hkdf(tenant_kek, _SESSION_INFO_PREFIX + sid)

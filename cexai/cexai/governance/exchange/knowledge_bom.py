"""knowledge_bom -- the signed, license-bearing exchange unit (the "X" in CEX).
CONVERGENCE T7, checkpoint C5: the FUNCTIONAL DSSE-style envelope that wraps an
exchangeable asset's Bill of Materials so a RECEIVING sovereign instance can verify
its provenance WITHOUT trusting the sender.

Design source: N04_knowledge/P08_architecture/p08_adr_knowledge_bom_exchange_unit.md
(T7 design -- the 4 mandatory envelope fields, the sovereignty paradox, the
access modifiers) + N07_admin/P08_architecture/p08_adr_convergence_master.md
(Section 6 council corrections + Section 9.2 open questions). The council found T7
was design-only BECAUSE the signing infra did not exist; it now does (C1
principal_signing + C4 transparency_log/status_list), and this module COMPOSES them.

----------------------------------------------------------------------------------
THE 4 MANDATORY ENVELOPE FIELDS (T7 ADR "4 mandatory envelope fields"):
  1. provenance / lineage  -- a list of derivation steps / sources (the build graph).
  2. license               -- a single SPDX expression string (e.g. "Apache-2.0").
  3. source_manifest       -- a list of components, EACH carrying {id, sha256,
                              optional name}. The source/training-data inventory.
  4. signer identity       -- the did:key of the signer (C1's self-rooted DID).
Plus: ``access_modifier`` (public/protected/private) + the asset's own ``sha256``
(what the BOM vouches for).

----------------------------------------------------------------------------------
COUNCIL CORRECTIONS HONORED (master ADR Section 6 + T7 ADR contested claims):

  * DSSE-style envelope, NOT W3C Data Integrity. The signature is Ed25519 over a
    DSSE Pre-Authentication Encoding (PAE):
        PAE = b"DSSEv1" + SP + len(payloadType) + SP + payloadType
                        + SP + len(payload)     + SP + payload
    (ASCII space-separated; lengths as DECIMAL ASCII; payload = the RAW BOM bytes,
    NOT the base64). The SHARED thing is the KEY + DID (C1), not a JWS/JSON-LD proof.
    See ``_pae`` and ``DSSE_PAYLOAD_TYPE``.

  * HASH-BINDING (master ADR open Q2). Every source-manifest component MUST carry a
    non-empty sha256. A component that names a source but cannot bind it to bytes is
    unverifiable lineage -- it is REJECTED at BUILD and again at VERIFY
    (KnowledgeBomError 'missing_source_hash'). Naming a source without a hash is the
    exact thing the council refused to allow.

  * ACCESS MODIFIER fails-closed (T7 ADR access-modifier table + master ADR open Q).
    The enum is public | protected | private. ``protected`` requires a trust-group
    that does NOT exist in v1, so ``protected`` is normalized to ``private``
    (fail-closed) and documented. The default is ``private``. Absent/unknown ->
    treated as private.

  * OPAQUE source ids for non-private (master ADR open Q3 / council LoRA-Leak
    finding). A ``public`` BOM may NOT carry real internal dataset NAMES in its
    source manifest -- only opaque ids + hashes. A BOM that names internal datasets
    must be at least ``protected`` (== private in v1). Enforced at BUILD
    (KnowledgeBomError 'name_leak'). Because ``protected`` collapses to ``private``,
    the rule reduces to: a PUBLIC BOM with any named component is rejected.

  * VERIFY-WITHOUT-TRUST is TOFU in v1 (self-rooted). The verifier checks the
    signature against a RECEIVER-SUPPLIED ``trust_set`` (a mapping did -> public
    key the receiver chose to trust), NOT a DID the envelope itself asserts
    unverified. v1 is self-rooted / Trust-On-First-Use: C1's ``did:key`` is derived
    from the key bytes, so the envelope's claimed signer is only as trustworthy as
    the receiver's decision to put it in ``trust_set``. The independent root + a
    witnessed transparency log is a LATER brick (C4's log is framework-self-signed).
    See ``verify_knowledge_bom``.

----------------------------------------------------------------------------------
THE EXCHANGE CONTRACT (so N07 can re-run + adversarially review):

  build_knowledge_bom(privkey, signer_did, asset_sha256, license_spdx,
                      source_components, lineage, access_modifier="private")
      -> a signed DSSE-style envelope dict:
         {payloadType, payload(b64url), signatures: [{keyid, sig(b64url)}]}
      The ``keyid`` is ``signer_did``; the ``sig`` is Ed25519 over the PAE of the
      RAW payload bytes. Build-time enforcement: hash-binding, name-leak,
      modifier normalization (protected->private).

  verify_knowledge_bom(envelope, trust_set, *, revocation=None)
      -> the validated BOM payload dict. Fail-closed steps: parse envelope ->
         resolve signer did in trust_set (unknown -> 'untrusted_signer') -> verify
         the Ed25519 sig over the PAE (bad -> 'bad_signature') -> re-check every
         source component has a sha256 ('missing_source_hash') -> if ``revocation``
         (a C4 StatusList) and the signer carries a status index, reject if revoked
         ('revoked'). Returns the payload on allow.

  authorize_bom_flow(payload, requesting_tenant, owner_tenant)
      -> a fail-closed cross-tenant flow gate keyed on the access_modifier:
         public -> allow; private/protected -> allow only if requesting == owner
         (the C2 inference-gate equality posture; protected == private in v1).
         Raises KnowledgeBomError('cross_tenant') on deny.

  log_bom_issuance(merkle_log, envelope)
      -> append the canonical envelope bytes to a C4 MerkleLog (tamper-evident
         issuance) and return (index, leaf_hash). OPTIONAL composition with C4.

KnowledgeBomError(ValueError) carries ``.reason`` in {missing_source_hash,
name_leak, malformed, untrusted_signer, bad_signature, revoked, cross_tenant} so a
caller / audit log branches on a field, not a parsed message.

----------------------------------------------------------------------------------
HONEST CAVEATS (stated, not hidden):
  * SELF-ROOTED TOFU (v1). The signer DID is C1's self-rooted did:key; the verifier
    trusts only what the RECEIVER put in ``trust_set``. There is no independent root
    yet -- a witnessed transparency log + a receiver-chosen federation bundle is the
    later T8/Component-5 brick.
  * ``protected`` == ``private`` until a trust-domain (SPIFFE-style trust group, T7
    open question) is defined. v1 fails closed: a protected BOM never crosses a
    tenant boundary.
  * This is the FRAMEWORK exchange unit. A RECEIVING instance must USE this verifier
    (offline, against its own trust_set); the BOM is only sovereign-on-both-ends if
    the receiver actually verifies rather than trusting the channel.

Dependencies: ``cryptography`` (Ed25519 verify) via the C1 key type + the C1/C4
governance primitives. Imports them at module load -- it is a T7 composition brick,
not the dormant RBAC dev path.

ASCII-only per .claude/rules/ascii-code-rule.md.

absorbs: convergence/t7-knowledge-bom (checkpoint C5 -- the signed exchange unit)
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from cexai.governance._shared.errors import GovernanceDenied
from cexai.governance.rbac._b64 import b64url_decode, b64url_encode
from cexai.governance.rbac.principal_signing import did_key as _did_key

__all__ = [
    "KnowledgeBomError",
    "DSSE_PAYLOAD_TYPE",
    "ACCESS_MODIFIERS",
    "build_knowledge_bom",
    "verify_knowledge_bom",
    "authorize_bom_flow",
    "log_bom_issuance",
]

# The DSSE payloadType for a knowledge_bom payload. DSSE carries an opaque
# payloadType string that is BOUND INTO the PAE (so a verifier cannot be tricked
# into interpreting the bytes under a different type). v1 uses a CEX-scoped media
# type; the T7 ADR's wire format (CycloneDX ML-BOM) is the v2 payload encoding --
# the envelope mechanics (PAE + Ed25519 + did:key) are identical regardless.
DSSE_PAYLOAD_TYPE = "application/vnd.cex.knowledge-bom+json; version=1"

# The expected ``schema`` field of a CEX knowledge_bom payload (set by
# ``build_knowledge_bom``). The verifier asserts BOTH the DSSE payloadType and this
# schema (audit R7) so a foreign-typed / foreign-schema envelope (e.g. a CycloneDX
# payload) cannot be accepted by the CEX verifier and silently return a payload with
# a missing ``source_manifest``.
_EXPECTED_SCHEMA = "cex.knowledge_bom/v1"

# The three dbt-Mesh-style access modifiers (T7 ADR). ``protected`` requires a
# trust-group that does NOT exist in v1 and is therefore NORMALIZED to ``private``
# (fail-closed) at build. ``private`` is the default and the fail-closed fallback
# for an absent/unknown modifier.
ACCESS_MODIFIERS = ("public", "protected", "private")
_DEFAULT_MODIFIER = "private"

# DSSE PAE constants (in-toto / DSSE v1). The version tag and the single ASCII
# space separator, kept as the single source of truth for signer + verifier.
_PAE_TYPE = b"DSSEv1"
_PAE_SP = b" "


class KnowledgeBomError(GovernanceDenied):
    """A knowledge_bom build / verify / authorize / issuance operation failed
    (CONVERGENCE T7, checkpoint C5).

    Subclasses ``GovernanceDenied`` (audit R5) -- NOT ``ValueError`` -- the same
    security-deny posture as ``PrincipalTokenError`` (C1),
    ``CrossTenantInferenceDenied`` (C2), ``ModelLoadDenied`` (C3),
    ``TransparencyLogError`` / ``StatusListError`` (C4). A security deny must NOT be
    swallowed by a generic ``except ValueError`` upstream; catch it via
    ``except GovernanceDenied`` (or this specific type). Carries a ``reason`` token so
    callers and the audit log branch on a field, not a parsed message. ``reason`` is
    one of:

      * ``missing_source_hash`` -- a source-manifest component has no (or an empty)
        ``sha256``. Lineage that names a source but cannot bind it to bytes is
        unverifiable -- REJECTED at build AND at verify (hash-binding, master ADR
        open Q2).
      * ``name_leak``           -- a non-private BOM carries a real internal dataset
        NAME in its source manifest. A public BOM may only carry opaque ids + hashes
        (master ADR open Q3 / council LoRA-Leak). REJECTED at build.
      * ``malformed``           -- a structurally broken envelope / payload / input
        (missing field, wrong type, non-decodable base64, bad JSON). A clean denial,
        never a raw crash on hostile input.
      * ``untrusted_signer``    -- the envelope's signer did is NOT in the receiver's
        ``trust_set`` (the TOFU / receiver-root point). REJECTED at verify.
      * ``bad_signature``       -- the Ed25519 signature does not authenticate the
        PAE of the payload under the trusted signer's key (tampered payload, wrong
        key). REJECTED at verify.
      * ``revoked``             -- the signer is marked revoked in the receiver's C4
        StatusList. REJECTED at verify.
      * ``revocation_unresolved`` -- a revocation check was requested but no
        RECEIVER-supplied index resolves the signer (a bare status_list with no
        index_map, or a signer absent from the index_map). FAIL-CLOSED at verify:
        the signer-controlled payload index is NOT trusted (audit R1), so an
        unresolvable check is a denial, never a silent skip.
      * ``cross_tenant``        -- ``authorize_bom_flow`` denied a flow because a
        private/protected BOM's owner tenant differs from the requesting tenant
        (fail-closed; protected == private in v1).

    RAISED on a failed operation; NEVER on a successful build / verify / authorize.
    """

    _REASONS = frozenset(
        {
            "missing_source_hash",
            "name_leak",
            "malformed",
            "untrusted_signer",
            "did_key_mismatch",
            "bad_signature",
            "revoked",
            "revocation_unresolved",
            "cross_tenant",
        }
    )

    def __init__(self, reason: str, detail: str = "") -> None:
        self.reason = reason
        message = f"knowledge_bom error: {reason}"
        if detail:
            message = f"{message} -- {detail}"
        super().__init__(message)


# --------------------------------------------------------------------------- #
# DSSE Pre-Authentication Encoding (the council's "DSSE-style, not Data Integrity") #
# --------------------------------------------------------------------------- #
def _pae(payload_type: str, payload: bytes) -> bytes:
    """The DSSE v1 Pre-Authentication Encoding of ``(payload_type, payload)``.

        PAE = "DSSEv1" SP len(type) SP type SP len(payload) SP payload

    All separators are a single ASCII space; the two lengths are DECIMAL ASCII
    (the byte length of the UTF-8 ``payload_type`` and of the raw ``payload``
    bytes respectively). Binding BOTH the type and the length-prefixed payload into
    the signed bytes is what stops a payload from being reinterpreted under a
    different type or having bytes shifted between fields -- the DSSE answer to the
    canonicalization ambiguities that plague JSON-LD signing. The signer and the
    verifier MUST build these bytes identically; this one helper is the single
    source of truth for both ``build`` and ``verify``."""
    type_bytes = payload_type.encode("utf-8")
    return b"".join(
        (
            _PAE_TYPE,
            _PAE_SP,
            str(len(type_bytes)).encode("ascii"),
            _PAE_SP,
            type_bytes,
            _PAE_SP,
            str(len(payload)).encode("ascii"),
            _PAE_SP,
            payload,
        )
    )


# --------------------------------------------------------------------------- #
# Build-time normalization + validation helpers                                 #
# --------------------------------------------------------------------------- #
def _normalize_modifier(access_modifier: str | None) -> str:
    """Resolve the requested access modifier to its FAIL-CLOSED effective value.

    Mapping (T7 ADR + council): ``public`` -> public; ``private`` -> private;
    ``protected`` -> ``private`` (the trust-group needed for protected does not
    exist in v1, so protected collapses to private -- fail-closed); anything else,
    including ``None`` / empty / unknown -> ``private`` (deny-by-default). The
    returned value is always one of {public, private}."""
    if access_modifier is None:
        return _DEFAULT_MODIFIER
    value = str(access_modifier).strip().lower()
    if value == "public":
        return "public"
    if value == "private":
        return "private"
    if value == "protected":
        # protected == private in v1 (no trust-group defined yet). Fail-closed.
        return "private"
    # Unknown / malformed modifier -> private (deny-by-default).
    return _DEFAULT_MODIFIER


def _validate_source_components(
    source_components: Sequence[Mapping[str, Any]],
    *,
    effective_modifier: str,
    at: str,
) -> list[dict[str, Any]]:
    """Validate + normalize the source manifest. Shared by build (full check incl.
    name-leak) and verify (hash-binding re-check only -- ``effective_modifier`` is
    passed as 'private' there so the name-leak rule is a no-op on a received BOM).

    Enforces, per component:
      * the component is a mapping with a non-empty ``id`` (else 'malformed');
      * a non-empty ``sha256`` -- HASH-BINDING (else 'missing_source_hash'); a
        component that names a source but cannot bind it to bytes is unverifiable;
      * NAME-LEAK: if ``effective_modifier`` is not 'private' (i.e. 'public') the
        component MUST NOT carry a non-empty ``name`` -- a public BOM exposes only
        opaque ids + hashes (master ADR open Q3 / council LoRA-Leak). Because
        protected collapses to private, in practice this fires only for public BOMs.

    Returns the normalized component list ({id, sha256, optional name}). ``at`` is
    'build' or 'verify' for error context."""
    if not isinstance(source_components, (list, tuple)):
        raise KnowledgeBomError("malformed", f"{at}: source_manifest must be a list")
    normalized: list[dict[str, Any]] = []
    for i, comp in enumerate(source_components):
        if not isinstance(comp, Mapping):
            raise KnowledgeBomError(
                "malformed", f"{at}: source component {i} is not a mapping"
            )
        cid_raw = comp.get("id")
        cid = "" if cid_raw is None else str(cid_raw).strip()
        if not cid:
            raise KnowledgeBomError(
                "malformed", f"{at}: source component {i} has no id"
            )
        digest_raw = comp.get("sha256")
        digest = "" if digest_raw is None else str(digest_raw).strip()
        if not digest:
            # HASH-BINDING: reject a source that cannot be bound to bytes.
            raise KnowledgeBomError(
                "missing_source_hash",
                f"{at}: source component {cid!r} has no sha256",
            )
        name_raw = comp.get("name")
        name = None if name_raw is None else str(name_raw).strip() or None
        if effective_modifier != "private" and name:
            # NAME-LEAK: a non-private (public) BOM must not name internal datasets.
            raise KnowledgeBomError(
                "name_leak",
                f"{at}: {effective_modifier} BOM names internal dataset "
                f"{name!r} (use an opaque id; name a dataset only in a "
                f"protected/private BOM)",
            )
        out: dict[str, Any] = {"id": cid, "sha256": digest}
        if name:
            out["name"] = name
        normalized.append(out)
    return normalized


def _normalize_lineage(lineage: Sequence[Any]) -> list[Any]:
    """Validate the provenance/lineage block: a non-None ordered list of steps /
    sources. Each step is opaque (a string or a mapping describing a derivation
    activity); the BOM transports it verbatim into the signed payload so a receiver
    can read the derivation offline. A non-list lineage is 'malformed'."""
    if not isinstance(lineage, (list, tuple)):
        raise KnowledgeBomError("malformed", "build: lineage must be a list of steps")
    return list(lineage)


def _canonical_payload_bytes(payload: Mapping[str, Any]) -> bytes:
    """Serialize a BOM payload mapping to canonical, deterministic bytes for
    signing: UTF-8 JSON with sorted keys and compact separators. Determinism
    matters because the signature covers the PAE of THESE bytes -- the same payload
    must serialize identically on the signer and (re-serialization is NOT needed on
    the verifier; it signs/checks the transported bytes) for diffing + logging. The
    verifier checks the signature over the bytes it RECEIVED (decoded from the
    envelope ``payload``), not a re-serialization, so a canonicalization mismatch
    cannot silently pass."""
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


# --------------------------------------------------------------------------- #
# BUILD -- a signed DSSE-style envelope FROM the 4 mandatory fields              #
# --------------------------------------------------------------------------- #
def build_knowledge_bom(
    privkey: Ed25519PrivateKey,
    signer_did: str,
    asset_sha256: str,
    license_spdx: str,
    source_components: Sequence[Mapping[str, Any]],
    lineage: Sequence[Any],
    access_modifier: str = _DEFAULT_MODIFIER,
) -> dict[str, Any]:
    """Build a SIGNED DSSE-style knowledge_bom envelope (CONVERGENCE T7, C5).

    Inputs (the 4 mandatory fields + the asset hash + the modifier):
      * ``privkey``           -- C1's Ed25519 signing private key
        (``ps.generate_signing_key``). Signs the PAE of the payload.
      * ``signer_did``        -- the SIGNER IDENTITY (field 4): C1's ``did:key`` for
        the public half of ``privkey`` (``ps.did_key(ps.public_key_of(privkey))``).
        Recorded both in the payload and as the signature ``keyid``.
      * ``asset_sha256``      -- the sha256 of the asset the BOM vouches for (the
        adapter / overlay / knowledge pack bytes). Non-empty (else 'malformed').
      * ``license_spdx``      -- the LICENSE (field 2): a single SPDX expression
        string (e.g. "Apache-2.0", "CC-BY-4.0 AND MIT"). Non-empty (else
        'malformed'); not validated against the SPDX list in v1 (a later seam).
      * ``source_components`` -- the SOURCE MANIFEST (field 3): a list of components,
        each ``{id, sha256, optional name}``. HASH-BINDING enforced (each needs a
        sha256). For a ``public`` BOM, NAME-LEAK enforced (no internal names).
      * ``lineage``           -- the PROVENANCE (field 1): an ordered list of
        derivation steps / sources, transported verbatim.
      * ``access_modifier``   -- public | protected | private (default private).
        ``protected`` is normalized to ``private`` (fail-closed); unknown ->
        private. The EFFECTIVE modifier is what is signed into the payload.

    Returns the envelope dict:
        {
          "payloadType": DSSE_PAYLOAD_TYPE,
          "payload":     "<base64url of the canonical BOM JSON>",
          "signatures":  [{"keyid": signer_did, "sig": "<base64url Ed25519 sig>"}],
        }

    Build-time enforcement (fail-closed, before any signing):
      * 'malformed' for an empty signer_did / asset_sha256 / license_spdx, a
        non-mapping component, or a component with no id.
      * 'missing_source_hash' for any component lacking a sha256.
      * 'name_leak' for a public BOM whose manifest names an internal dataset.

    The signature is Ed25519 over ``_pae(DSSE_PAYLOAD_TYPE, payload_bytes)`` -- the
    council's DSSE-style PAE, NOT a W3C Data Integrity proof. The KEY + DID are the
    shared trust root (C1); the cryptosuite is a detached signature over the PAE."""
    sd = "" if signer_did is None else str(signer_did).strip()
    if not sd:
        raise KnowledgeBomError("malformed", "build: signer_did is required")
    asset = "" if asset_sha256 is None else str(asset_sha256).strip()
    if not asset:
        raise KnowledgeBomError("malformed", "build: asset_sha256 is required")
    lic = "" if license_spdx is None else str(license_spdx).strip()
    if not lic:
        raise KnowledgeBomError("malformed", "build: license_spdx is required")

    effective_modifier = _normalize_modifier(access_modifier)
    components = _validate_source_components(
        source_components, effective_modifier=effective_modifier, at="build"
    )
    steps = _normalize_lineage(lineage)

    # The BOM payload carries fields 1-4 + the asset hash + the EFFECTIVE modifier.
    payload: dict[str, Any] = {
        "schema": "cex.knowledge_bom/v1",
        "asset_sha256": asset,
        "license": lic,
        "access_modifier": effective_modifier,
        "signer": sd,
        "provenance": steps,
        "source_manifest": components,
    }
    payload_bytes = _canonical_payload_bytes(payload)

    # DSSE: sign the PAE of the RAW payload bytes (not the base64).
    signature = privkey.sign(_pae(DSSE_PAYLOAD_TYPE, payload_bytes))

    return {
        "payloadType": DSSE_PAYLOAD_TYPE,
        "payload": b64url_encode(payload_bytes),
        "signatures": [{"keyid": sd, "sig": b64url_encode(signature)}],
    }


# --------------------------------------------------------------------------- #
# VERIFY -- receiver-side, against a RECEIVER-SUPPLIED trust set (TOFU v1)        #
# --------------------------------------------------------------------------- #
def _parse_envelope(envelope: Mapping[str, Any]) -> tuple[str, bytes, str, bytes]:
    """Parse + structurally validate a DSSE-style envelope. Returns
    ``(payload_type, payload_bytes, signer_did, signature_bytes)``. Fail-closed:
    any missing field, wrong type, non-decodable base64, or empty signatures list
    is a clean ``KnowledgeBomError('malformed')`` -- never a raw KeyError / binascii
    error leaking through. v1 reads the FIRST signature (single-signer BOM)."""
    if not isinstance(envelope, Mapping):
        raise KnowledgeBomError("malformed", "verify: envelope must be a mapping")
    payload_type = envelope.get("payloadType")
    if not isinstance(payload_type, str) or not payload_type:
        raise KnowledgeBomError("malformed", "verify: missing payloadType")
    payload_b64 = envelope.get("payload")
    if not isinstance(payload_b64, str) or not payload_b64:
        raise KnowledgeBomError("malformed", "verify: missing payload")
    sigs = envelope.get("signatures")
    if not isinstance(sigs, (list, tuple)) or not sigs:
        raise KnowledgeBomError("malformed", "verify: missing signatures")
    first = sigs[0]
    if not isinstance(first, Mapping):
        raise KnowledgeBomError("malformed", "verify: signature entry is not a mapping")
    keyid = first.get("keyid")
    sig_b64 = first.get("sig")
    if not isinstance(keyid, str) or not keyid:
        raise KnowledgeBomError("malformed", "verify: signature has no keyid")
    if not isinstance(sig_b64, str) or not sig_b64:
        raise KnowledgeBomError("malformed", "verify: signature has no sig")
    try:
        payload_bytes = b64url_decode(payload_b64)
    except (ValueError, TypeError) as exc:
        raise KnowledgeBomError("malformed", f"verify: payload not base64url: {exc}") from exc
    try:
        signature_bytes = b64url_decode(sig_b64)
    except (ValueError, TypeError) as exc:
        raise KnowledgeBomError("malformed", f"verify: sig not base64url: {exc}") from exc
    return payload_type, payload_bytes, keyid, signature_bytes


def _decode_payload(payload_bytes: bytes) -> dict[str, Any]:
    """Decode the BOM payload JSON. Fail-closed: non-JSON or a non-object payload is
    'malformed', never a raw JSONDecodeError."""
    try:
        payload = json.loads(payload_bytes.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise KnowledgeBomError("malformed", f"verify: payload not JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise KnowledgeBomError("malformed", "verify: payload is not a JSON object")
    return payload


def _assert_did_key_binding(signer_did: str, pubkey: Ed25519PublicKey) -> None:
    """Assert a ``did:key:z...`` signer id re-derives from the trusted ``pubkey``
    (audit R2). A ``did:key`` is self-rooted -- it is a deterministic function of the
    public-key bytes -- so a verifier MUST re-derive it and compare, otherwise the
    ``signer`` field is an unbound claim: an attacker could name a trusted did whose
    ``trust_set`` entry is a DIFFERENT key the signature actually validates under.

    Only ``did:key:z`` ids are checked (their identifier IS the key). A non-did:key
    signer id is intentionally skipped -- such an id is bound by the receiver's
    enrollment decision (``trust_set``), not by key derivation, and v1 keeps those
    forms working. On mismatch -> ``KnowledgeBomError('did_key_mismatch')``."""
    if not signer_did.startswith("did:key:z"):
        return
    try:
        derived = _did_key(pubkey)
    except Exception as exc:  # noqa: BLE001 -- a key that cannot derive a did is malformed
        raise KnowledgeBomError(
            "malformed", f"verify: cannot derive did:key from trusted key: {exc}"
        ) from exc
    if derived != signer_did:
        raise KnowledgeBomError(
            "did_key_mismatch",
            f"signer {signer_did!r} does not derive from its trusted key "
            f"(re-derived {derived!r}); the signer field is not bound to the key",
        )


def verify_knowledge_bom(
    envelope: Mapping[str, Any],
    trust_set: Mapping[str, Ed25519PublicKey],
    *,
    revocation: Any | None = None,
) -> dict[str, Any]:
    """Verify a knowledge_bom envelope against a RECEIVER-SUPPLIED ``trust_set`` and
    return the validated payload (CONVERGENCE T7, C5).

    VERIFY CONTRACT (so N07 can re-run + adversarially review):
      * ``envelope``   -- the dict produced by ``build_knowledge_bom``.
      * ``trust_set``  -- a mapping ``did -> Ed25519PublicKey`` the RECEIVER chose to
        trust. THIS is the TOFU / receiver-root point: the signature is checked
        against a key the RECEIVER supplied, NOT a key the envelope asserts. v1 is
        self-rooted -- the signer's did:key is derived from its own key bytes, so
        trust is the receiver's decision to enroll that did, not an independent
        anchor. (The independent root + witnessed log is a later brick.)
      * ``revocation`` -- OPTIONAL. To perform a REAL revocation check, pass the
        2-tuple ``(status_list, {signer_did: index})`` where the index map is
        RECEIVER/ISSUER-supplied. The signer's revocation index is read ONLY from
        that receiver map -- NEVER from the signed payload (the signer controls the
        payload, so a payload index is untrusted; audit R1). Passing a bare
        ``StatusList`` (no index map), or a map that has no entry for the signer,
        raises 'revocation_unresolved' (fail-closed) rather than skipping the check
        or trusting a self-asserted index. ``None`` (the default) opts out of the
        check entirely.

    Steps, FAIL-CLOSED, in order (each raises ``KnowledgeBomError`` on failure):
      1. parse + structurally validate the envelope ('malformed' on any defect).
      2. resolve the signer ``keyid`` (a did) in ``trust_set``. An unknown signer ->
         'untrusted_signer' (the receiver never enrolled this did). For a
         ``did:key`` signer, the did MUST re-derive from the trusted key bytes
         ('did_key_mismatch' otherwise; audit R2).
      3. verify the Ed25519 signature over ``_pae(payloadType, payload_bytes)`` with
         the trusted key. A tampered payload or wrong key -> 'bad_signature'.
      4. decode the payload; assert the DSSE payloadType + the CEX schema (audit
         R7), then re-check HASH-BINDING -- every source component must carry a
         sha256 ('missing_source_hash'). A BOM whose manifest lost a hash in transit
         is unverifiable lineage and is refused even with a valid signature.
      5. if ``revocation`` is supplied, resolve the signer's index from the RECEIVER
         map and reject a revoked signer -> 'revoked' (unresolvable ->
         'revocation_unresolved', fail-closed).

    Returns the validated payload dict on ALLOW (it NEVER returns on a failed step).
    The returned payload preserves ``asset_sha256``, ``license``,
    ``source_manifest``, ``provenance``, ``signer``, and ``access_modifier`` exactly
    as signed."""
    # Step 1 -- parse the envelope (fail-closed on any structural defect).
    payload_type, payload_bytes, signer_did, signature_bytes = _parse_envelope(envelope)

    # Step 2 -- resolve the signer in the RECEIVER's trust set (TOFU / receiver-root).
    if not isinstance(trust_set, Mapping):
        raise KnowledgeBomError("malformed", "verify: trust_set must be a mapping")
    pubkey = trust_set.get(signer_did)
    if pubkey is None:
        raise KnowledgeBomError(
            "untrusted_signer",
            f"signer {signer_did!r} is not in the receiver's trust set",
        )
    if not isinstance(pubkey, Ed25519PublicKey):
        raise KnowledgeBomError(
            "malformed", f"verify: trust_set[{signer_did!r}] is not an Ed25519 public key"
        )

    # Step 2b -- did:key BINDING (audit R2). A self-rooted ``did:key`` is derived
    # purely from the key bytes, so it MUST re-derive from the trusted key. Without
    # this, an attacker could set ``signer`` to a trusted did while the signature
    # validates under a DIFFERENT trusted key mapped to that did. Re-derive and
    # assert equality. Non-did:key signer ids are skipped (their binding is the
    # receiver's enrollment decision, not a key-derived identifier).
    _assert_did_key_binding(signer_did, pubkey)

    # Step 3 -- verify the Ed25519 signature over the PAE (DSSE-style). A tampered
    # payload, a wrong key, or a swapped payloadType all break this.
    try:
        pubkey.verify(signature_bytes, _pae(payload_type, payload_bytes))
    except InvalidSignature as exc:
        raise KnowledgeBomError("bad_signature", "signature does not authenticate the payload") from exc

    # Step 4 -- decode + assert type/schema (audit R7) + re-check hash-binding.
    payload = _decode_payload(payload_bytes)
    # TYPE/SCHEMA BINDING: a CEX verifier accepts ONLY a CEX-typed, CEX-schema
    # envelope. A CycloneDX-typed or foreign-schema envelope is 'malformed' here
    # rather than returning a payload with a missing source_manifest.
    if payload_type != DSSE_PAYLOAD_TYPE:
        raise KnowledgeBomError(
            "malformed",
            f"verify: payloadType {payload_type!r} is not the CEX knowledge_bom type",
        )
    if payload.get("schema") != _EXPECTED_SCHEMA:
        raise KnowledgeBomError(
            "malformed",
            f"verify: payload schema {payload.get('schema')!r} is not {_EXPECTED_SCHEMA!r}",
        )
    source_components = payload.get("source_manifest", [])
    # at='verify' passes effective_modifier='private' so the name-leak rule is inert
    # on a received BOM (the producer already enforced it at build); only the
    # hash-binding re-check runs here.
    _validate_source_components(
        source_components, effective_modifier="private", at="verify"
    )

    # Step 5 -- offline revocation check (C4 StatusList), if supplied.
    _check_revocation(revocation, signer_did, payload)

    return payload


def _check_revocation(
    revocation: Any | None, signer_did: str, payload: Mapping[str, Any]
) -> None:
    """Reject a revoked signer using a C4 ``StatusList`` (offline-checkable).

    Accepted ``revocation`` shapes (v1, FAIL-CLOSED):
      * ``None``                       -- no revocation check (caller opted out).
      * ``(status_list, index_map)``   -- a 2-tuple of a StatusList and a mapping
        ``{did: index}``; the signer's index is looked up there. THIS IS THE ONLY
        SHAPE THAT PERFORMS A REAL CHECK. The index map is RECEIVER/ISSUER-supplied
        (the receiver holds the issuer's index assignment), so a revoked signer
        cannot influence which bit is read.

    REVOCATION-BYPASS HARDENING (audit R1): the revocation index MUST come from the
    RECEIVER, NEVER from the signed payload. A previous version fell back to a
    payload ``status_index`` on the bare-``status_list`` path -- but the signer
    controls the payload, so a revoked signer could self-assert an unrevoked index
    and be accepted. That trust is REMOVED:
      * a bare ``status_list`` (no index_map) -> ``KnowledgeBomError(
        'revocation_unresolved')`` -- there is no receiver-supplied index to read,
        so the check cannot be performed and we FAIL CLOSED rather than trust the
        payload.
      * a ``(status_list, index_map)`` where the signer is NOT in the index_map ->
        ``KnowledgeBomError('revocation_unresolved')`` -- the receiver enabled a
        revocation check but has no index for this signer; fail closed (do NOT
        silently skip, and do NOT read the payload).

    A ``True`` from ``status_list.is_revoked(index)`` -> ``KnowledgeBomError(
    'revoked')``. Any structural problem reading the index (out-of-range, bad type,
    a non-int receiver index -- audit R10) is surfaced as 'malformed' rather than
    silently passing -- fail-closed. The payload's ``status_index`` is NEVER read."""
    if revocation is None:
        return
    status_list: Any
    index_map: Mapping[str, int] | None
    if isinstance(revocation, tuple) and len(revocation) == 2:
        status_list, index_map = revocation
    else:
        status_list, index_map = revocation, None

    # Resolve the signer's status index from the RECEIVER-supplied index map ONLY.
    # The index is NEVER read from the signed payload (the signer controls it). A
    # bare status_list with no index map, or a signer absent from the map, is an
    # UNRESOLVED check -> fail closed (a revoked signer must not pass by absence).
    if index_map is None:
        raise KnowledgeBomError(
            "revocation_unresolved",
            "verify: a real revocation check requires (status_list, index_map); "
            "a bare status_list has no receiver-supplied index (the payload index "
            "is signer-controlled and is not trusted)",
        )
    if not isinstance(index_map, Mapping):
        raise KnowledgeBomError("malformed", "verify: revocation index map must be a mapping")
    if signer_did not in index_map:
        raise KnowledgeBomError(
            "revocation_unresolved",
            f"verify: signer {signer_did!r} has no entry in the receiver's "
            f"revocation index map; fail-closed (the payload index is not trusted)",
        )
    # int() coercion of a RECEIVER-supplied index is wrapped (audit R10): a
    # non-int receiver index is 'malformed', never a raw ValueError/TypeError.
    try:
        index = int(index_map[signer_did])
    except (ValueError, TypeError) as exc:
        raise KnowledgeBomError("malformed", f"verify: bad revocation index: {exc}") from exc

    is_revoked = getattr(status_list, "is_revoked", None)
    if not callable(is_revoked):
        raise KnowledgeBomError("malformed", "verify: revocation object has no is_revoked")
    try:
        revoked = bool(is_revoked(index))
    except Exception as exc:  # noqa: BLE001 -- StatusListError or any read failure
        # A bad index (out of range) or any read failure is fail-closed 'malformed',
        # never a silent allow.
        raise KnowledgeBomError("malformed", f"verify: revocation check failed: {exc}") from exc
    if revoked:
        raise KnowledgeBomError("revoked", f"signer {signer_did!r} is revoked")


# --------------------------------------------------------------------------- #
# AUTHORIZE FLOW -- fail-closed cross-tenant gate keyed on the access modifier   #
# --------------------------------------------------------------------------- #
def authorize_bom_flow(
    payload: Mapping[str, Any],
    requesting_tenant: str,
    owner_tenant: str,
) -> str:
    """Authorize a knowledge_bom FLOW across a tenant boundary, keyed on the BOM's
    access modifier (CONVERGENCE T7, C5 -- the dbt-Mesh access-modifier gate).

    This is the SECOND, independent gate of the convergence move: the modifier
    governs WHETHER the BOM may flow; the signature (``verify_knowledge_bom``)
    governs whether the receiver can TRUST it. Both are required.

    AUTHORIZE CONTRACT (mirrors C2's ``authorize_inference`` fail-closed equality):
      * ``payload``           -- the validated payload from ``verify_knowledge_bom``
        (it carries the EFFECTIVE ``access_modifier``). A payload with no / unknown
        modifier is treated as ``private`` (deny-by-default).
      * ``requesting_tenant`` -- the tenant that wants to RECEIVE the BOM.
      * ``owner_tenant``      -- the tenant that PRODUCED / owns the BOM.

    Decision (fail-closed):
      * ``public``                -> ALLOW for any tenant (returns requesting_tenant).
      * ``private`` / ``protected`` -> ALLOW only if ``requesting_tenant ==
        owner_tenant`` (exact string equality, the C2 posture); otherwise DENY ->
        ``KnowledgeBomError('cross_tenant')``. ``protected`` is identical to
        ``private`` in v1 (no trust-group defined), so a protected BOM never crosses
        a tenant boundary.

    A missing/blank ``owner_tenant`` (for a non-public BOM) or a missing/blank
    ``requesting_tenant`` is 'cross_tenant' (deny-by-default -- an unbindable flow is
    refused, matching C2's stricter inference posture). Returns the validated
    ``requesting_tenant`` on ALLOW; NEVER returns on deny."""
    if not isinstance(payload, Mapping):
        raise KnowledgeBomError("malformed", "authorize: payload must be a mapping")
    modifier = _normalize_modifier(payload.get("access_modifier"))
    requesting = "" if requesting_tenant is None else str(requesting_tenant).strip()
    owner = "" if owner_tenant is None else str(owner_tenant).strip()

    if modifier == "public":
        # A public BOM flows to any tenant. (The receiver still verifies the
        # signature; trust is established by the BOM, not by the channel.)
        if not requesting:
            # Even public flow needs a named receiver to return; deny-by-default.
            raise KnowledgeBomError(
                "cross_tenant", "authorize: no requesting tenant for public flow"
            )
        return requesting

    # private / protected (protected == private in v1) -> same-tenant only.
    if not requesting or not owner:
        raise KnowledgeBomError(
            "cross_tenant",
            f"authorize: {modifier} BOM flow needs both tenants "
            f"(requesting={requesting!r}, owner={owner!r}); fail-closed",
        )
    if requesting != owner:
        raise KnowledgeBomError(
            "cross_tenant",
            f"{modifier} BOM owned by {owner!r} may not flow to {requesting!r} "
            f"(fail-closed; protected == private in v1)",
        )
    return requesting


# --------------------------------------------------------------------------- #
# LOG ISSUANCE -- compose with C4's tamper-evident Merkle log (OPTIONAL)         #
# --------------------------------------------------------------------------- #
def envelope_canonical_bytes(envelope: Mapping[str, Any]) -> bytes:
    """The canonical bytes of an ENVELOPE for logging / hashing: UTF-8 JSON with
    sorted keys + compact separators. Deterministic so the SAME envelope logs to the
    SAME leaf (stable inclusion proofs + diffing). Distinct from the payload
    canonicalizer -- this covers the whole envelope (payloadType + payload + the
    signature), which is what a transparency log should commit to (the signed unit
    AS ISSUED)."""
    if not isinstance(envelope, Mapping):
        raise KnowledgeBomError("malformed", "log: envelope must be a mapping")
    try:
        return json.dumps(
            envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise KnowledgeBomError("malformed", f"log: envelope not serializable: {exc}") from exc


def log_bom_issuance(merkle_log: Any, envelope: Mapping[str, Any]) -> tuple[int, bytes]:
    """Append the canonical envelope bytes to a C4 ``MerkleLog`` and return
    ``(index, leaf_hash)`` -- a tamper-evident record that this exact BOM was issued
    (CONVERGENCE T7 + T8/C4 composition).

    ``merkle_log`` is a ``cexai.governance.rbac.transparency_log.MerkleLog``. This
    function does not import it (to keep the exchange lane decoupled) -- it
    duck-types ``append(bytes) -> (index, leaf_hash)``. The receiver can later call
    ``transparency_log.verify_inclusion(leaf_hash, index, log.inclusion_proof(index),
    log.root(), log.size)`` to prove the BOM is committed under the log's
    (signed) tree head.

    HONEST CAVEAT (C4): the v1 transparency log is framework-SELF-rooted -- it is
    tamper-evident to the operator (and to a holder of an older signed tree head),
    but it is NOT an independent witness. Real cross-instance non-repudiation needs
    a receiver-chosen / witnessed log (the same Component 5 brick that the BOM's
    self-rooted did:key awaits)."""
    data = envelope_canonical_bytes(envelope)
    append = getattr(merkle_log, "append", None)
    if not callable(append):
        raise KnowledgeBomError("malformed", "log: merkle_log has no append(bytes) method")
    index, leaf = append(data)
    return index, leaf

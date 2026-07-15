"""trust -- the SAFE-BY-DEFAULT public facade over the CONVERGENCE governance bricks
(C1-C10). One coherent API for an OSS consumer, so the SAFE path is the SHORT path.

----------------------------------------------------------------------------------
WHY THIS MODULE EXISTS

The governance crypto is going public. The underlying bricks
(``cexai.governance.rbac.*`` C1-C4 + ``cexai.governance.exchange.*`` C5/C7) are
correct and audit-hardened, but a consumer who wires them by hand must compose 8+
modules in the RIGHT order with the RIGHT safe defaults -- and one wrong default is
a fail-OPEN security hole the four-lens audit already closed once (trust_set
required, ``aud``/``iss`` required, revocation issuer-attested, ``did:key`` bound).

This facade PRESERVES + EXPOSES those safe defaults. It is ADDITIVE: it COMPOSES the
bricks (it imports and calls their public functions), it does NOT reimplement crypto
and it does NOT modify a single brick. Two cohesive classes split the world the way
the trust model does:

  * ``Issuer``   -- the PRODUCING / signing side. Holds ONE Ed25519 trust-root key.
  * ``Verifier`` -- the CONSUMING / receiving side. SAFE BY DEFAULT: it cannot even
    be CONSTRUCTED in a fail-open configuration.

----------------------------------------------------------------------------------
THE END-TO-END SAFE FLOW (the whole point, in ~10 lines)

    from cexai.governance.trust import Issuer, Verifier, GovernanceDenied

    issuer = Issuer.from_new()                      # one trust-root Ed25519 key
    token  = issuer.mint_principal("alice", tenant="acme",
                                   aud="spiffe://fabric", iss="did:web:acme")
    bom    = issuer.build_bom(asset_sha256=sha, license_spdx="Apache-2.0",
                              source_components=[{"id": "src-1", "sha256": h}],
                              lineage=[{"activity": "finetune"}],
                              access_modifier="public")

    # RECEIVER side -- trust is the receiver's enrollment decision, NEVER the envelope's:
    v = Verifier(trust_set={issuer.did: issuer.public_key},   # did -> pubkey, receiver-chosen
                 expected_aud="spiffe://fabric", expected_iss="did:web:acme")
    claims  = v.verify_principal(token)             # raises GovernanceDenied on tamper
    payload = v.verify_bom(bom)                     # raises GovernanceDenied on any failure

----------------------------------------------------------------------------------
SAFE-BY-DEFAULT CONTRACT (each item embodies a specific audit fix)

  * A ``Verifier`` with an empty / None ``trust_set`` RAISES at construction. Trust
    is the RECEIVER's enrollment decision -- a verifier with nothing enrolled trusts
    nothing, and silently trusting "whatever signed it" is the TOFU-collapse the
    audit (F4) forbids. NEVER build ``trust_set`` from the envelope's own ``keyid``.
  * A ``Verifier`` with a falsy ``expected_aud`` / ``expected_iss`` RAISES at
    construction (audit R4). A falsy ``expected_aud`` (notably ``None``) makes the
    underlying PyJWT decode SKIP the audience check -- a fail-OPEN trap. Refused.
  * Every denial surfaces as ``GovernanceDenied`` (the post-audit base, R5), so a
    consumer catches ONE base for ALL denies and an accidental ``except ValueError``
    upstream can NEVER swallow a security deny.
  * There is NO parameter whose UNSAFE value is the default. There is no
    "verification optional" switch. ``require_revocation=True`` is the only knob and
    it makes the path STRICTER, never weaker.

----------------------------------------------------------------------------------
WHAT THIS FACADE COMPOSES (no new crypto)

  C1 rbac.principal_signing   -- Ed25519 key, did:key, JWKS, mint + verify principal.
  C3 rbac.model_allowlist     -- signed allow-list entry (Issuer.sign_model).
  C4 rbac.transparency_log    -- MerkleLog issuance logging (Issuer.log_to).
  C4 rbac.status_list         -- StatusList2021 revocation (Issuer.issue_status_list /
                                 .revoke ; Verifier.verify_bom require_revocation).
  C5 exchange.knowledge_bom   -- the DSSE-CEX signed exchange unit (default payload).
  C7 exchange.cyclonedx_bom   -- the CycloneDX 1.6 ML-BOM payload (cyclonedx=True).

ASCII-only per .claude/rules/ascii-code-rule.md.

absorbs: convergence/c11-trust-facade (the SAFE-BY-DEFAULT public composition)
"""

from __future__ import annotations

from collections.abc import Mapping, MutableSet, Sequence
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

# The single security-deny base every brick now subclasses (audit R5). Re-exported so
# a consumer of the facade catches ONE thing for ALL denies.
from cexai.governance._shared.errors import GovernanceDenied

# C1 -- identity: key, did, JWKS, mint, verify.
from cexai.governance.rbac import principal_signing as _ps

# C2 -- the inference deny-surface (verified-identity-driven).
from cexai.governance.rbac.inference_gate import authorize_inference as _authorize_inference

# C3 -- the signed-model allow-list entry.
from cexai.governance.rbac.model_allowlist import (
    AllowlistEntry,
    make_allowlist_entry as _make_allowlist_entry,
)

# C4 -- transparency log + StatusList2021 revocation.
from cexai.governance.rbac.status_list import (
    StatusList,
    sign_status_list as _sign_status_list,
)

# C5 -- the DSSE-CEX signed knowledge_bom (default exchange payload).
from cexai.governance.exchange.knowledge_bom import (
    authorize_bom_flow as _authorize_bom_flow,
    build_knowledge_bom as _build_knowledge_bom,
    log_bom_issuance as _log_bom_issuance,
    verify_knowledge_bom as _verify_knowledge_bom,
)

# C7 -- the CycloneDX 1.6 ML-BOM payload (cyclonedx=True path).
from cexai.governance.exchange.cyclonedx_bom import (
    build_signed_cyclonedx_bom as _build_signed_cyclonedx_bom,
    verify_signed_cyclonedx_bom as _verify_signed_cyclonedx_bom,
)

__all__ = [
    "GovernanceDenied",
    "Issuer",
    "Verifier",
    "DEFAULT_PRINCIPAL_TTL_SECONDS",
]

# Default principal-token lifetime exposed at the facade so a consumer sees the value
# without reaching into C1. Mirrors C1's ADR-pinned default (exp <= 90s).
DEFAULT_PRINCIPAL_TTL_SECONDS = 90


# =========================================================================== #
# Issuer -- the producing / signing side (ONE Ed25519 trust-root key)          #
# =========================================================================== #
class Issuer:
    """The PRODUCING / signing side of the trust model -- a single sovereign instance
    holding ONE Ed25519 trust-root key (the convergence "share the key, not the
    cryptosuite" thesis: this one key signs principal tokens, model-allow-list
    entries, status lists, transparency-log tree heads, AND knowledge BOMs).

    Construct with ``Issuer.from_new()`` (fresh key) or ``Issuer(privkey)`` (an
    existing C1 ``Ed25519PrivateKey`` from ``principal_signing.generate_signing_key``).

    IDENTITY: the issuer's ``did`` is C1's self-rooted ``did:key`` for its public
    half. Every artifact this issuer signs carries that did, and a RECEIVER enrolls
    exactly that did into its ``Verifier`` trust_set. The same did is used as the
    principal-token ``kid`` so a receiver resolves ONE trust anchor (the did) for
    both principals and BOMs.

    HONEST CAVEAT (inherited from C1): ``did:key`` is self-rooted / Trust-On-First-Use
    -- it is derived from the key bytes, so it asserts the issuer's OWN identity, not
    an independent anchor. Trust is the receiver's decision to enroll it. The
    independent root (witnessed transparency log + receiver-chosen federation bundle)
    is a later brick."""

    def __init__(self, privkey: Ed25519PrivateKey) -> None:
        """Wrap an existing C1 Ed25519 signing private key. Use ``Issuer.from_new()``
        to generate a fresh one. Raises ``TypeError`` if ``privkey`` is not an
        ``Ed25519PrivateKey`` (a wrong-typed key is a programming error, not a
        security deny)."""
        if not isinstance(privkey, Ed25519PrivateKey):
            raise TypeError(
                f"Issuer requires an Ed25519PrivateKey, got {type(privkey).__name__}; "
                "use Issuer.from_new() or principal_signing.generate_signing_key()"
            )
        self._privkey = privkey
        self._pubkey = _ps.public_key_of(privkey)
        self._did = _ps.did_key(self._pubkey)

    @classmethod
    def from_new(cls) -> "Issuer":
        """Generate a fresh Ed25519 trust-root key and return a new ``Issuer`` over it
        (C1 ``generate_signing_key``)."""
        return cls(_ps.generate_signing_key())

    # -- identity ----------------------------------------------------------- #
    @property
    def did(self) -> str:
        """The issuer's ``did:key:z...`` -- its self-rooted identity (C1 ``did_key``).
        A receiver enrolls this exact did into its ``Verifier`` trust_set; it is also
        the principal-token ``kid`` and every BOM's signature ``keyid``."""
        return self._did

    @property
    def public_key(self) -> Ed25519PublicKey:
        """The public half of the trust-root key -- the value a receiver pairs with
        ``did`` in its trust_set (``{issuer.did: issuer.public_key}``)."""
        return self._pubkey

    def jwks(self) -> dict[str, list[dict[str, str]]]:
        """The issuer's JWKS document ``{"keys": [<jwk>]}`` (C1 ``jwks_set`` /
        ``jwk_of``). The single JWK's ``kid`` is the issuer ``did`` -- the same anchor
        a receiver enrolls. Exposed for a consumer that wants to publish a JWKS
        endpoint; the ``Verifier`` does NOT consume this (it builds its own JWKS from
        the receiver-chosen trust_set, never from issuer-published material)."""
        return _ps.jwks_set(_ps.jwk_of(self._pubkey, self._did))

    # -- C1: principal tokens ----------------------------------------------- #
    def mint_principal(
        self,
        sub: str,
        *,
        tenant: str,
        aud: str,
        iss: str,
        role: str | None = None,
        ttl_seconds: int = DEFAULT_PRINCIPAL_TTL_SECONDS,
        extra_claims: Mapping[str, Any] | None = None,
    ) -> str:
        """Mint a signed principal JWS (``alg=EdDSA``) for subject ``sub`` bound to
        ``tenant`` (C1 ``mint_principal_token``).

        ``aud`` and ``iss`` are REQUIRED keyword arguments (a token a receiver pins
        must carry the audience + issuer it pins). ``tenant`` is what the C2 inference
        gate binds to. The token header ``kid`` is the issuer ``did`` so a receiver
        resolves it against the same trust anchor it enrolled. C1 fills ``iat`` /
        ``exp`` (now + ttl, default 90s) / ``jti`` (the one-time replay key). Returns
        the compact JWS string."""
        claims: dict[str, Any] = {
            "sub": sub,
            "tenant": tenant,
            "aud": aud,
            "iss": iss,
        }
        if role is not None:
            claims["role"] = role
        if extra_claims:
            # Caller-supplied claims are layered first; the core identity fields above
            # are authoritative and overwrite any collision.
            merged = dict(extra_claims)
            merged.update(claims)
            claims = merged
        return _ps.mint_principal_token(
            self._privkey, self._did, claims, ttl_seconds=ttl_seconds
        )

    # -- C3: signed-model allow-list entry ---------------------------------- #
    def sign_model(
        self, model_id: str, sha256: str, fmt: str = "safetensors"
    ) -> AllowlistEntry:
        """Sign a model into a C3 ``AllowlistEntry`` (detached Ed25519 over
        ``model_id || sha256 || format``). The receiver builds a model gate with
        ``make_model_gate(issuer.public_key, [entry])`` to refuse any non-safetensors
        / unsigned / hash-mismatched load. Wraps C3 ``make_allowlist_entry``."""
        return _make_allowlist_entry(self._privkey, model_id, sha256, fmt)

    # -- C5 / C7: the signed exchange unit ---------------------------------- #
    def build_bom(
        self,
        asset_sha256: str,
        license_spdx: str,
        source_components: Sequence[Mapping[str, Any]],
        lineage: Sequence[Any],
        access_modifier: str = "private",
        *,
        cyclonedx: bool = False,
    ) -> dict[str, Any]:
        """Build a SIGNED knowledge_bom envelope (DSSE) signed by this issuer's key
        and identified by this issuer's ``did`` (C5 ``build_knowledge_bom`` by default;
        C7 ``build_signed_cyclonedx_bom`` when ``cyclonedx=True``).

        Both paths enforce, at BUILD, before any signing (fail-closed):
          * HASH-BINDING -- every source component MUST carry a non-empty sha256.
          * NAME-LEAK    -- a ``public`` BOM may not name an internal dataset.
          * modifier normalization -- ``protected`` collapses to ``private`` (v1).

        ``access_modifier`` defaults to ``private`` (the fail-closed default -- a
        BOM does not cross a tenant boundary unless explicitly made ``public``).
        ``cyclonedx=False`` (the default) emits the CEX-scoped DSSE payload; the SAME
        envelope mechanics (PAE + Ed25519 + did:key) apply to the CycloneDX payload --
        only the encoding + bound ``payloadType`` differ. The ``Verifier`` auto-detects
        which payload type it received. Returns the envelope dict
        ``{payloadType, payload, signatures:[{keyid, sig}]}``."""
        if cyclonedx:
            return _build_signed_cyclonedx_bom(
                self._privkey,
                self._did,
                asset_sha256,
                license_spdx,
                source_components,
                lineage,
                access_modifier=access_modifier,
            )
        return _build_knowledge_bom(
            self._privkey,
            self._did,
            asset_sha256,
            license_spdx,
            source_components,
            lineage,
            access_modifier=access_modifier,
        )

    # -- C4: StatusList2021 revocation -------------------------------------- #
    def issue_status_list(
        self, revoked_indices: Sequence[int] | None = None, *, size_bits: int | None = None
    ) -> tuple[StatusList, str, bytes]:
        """Issue a C4 ``StatusList`` (revocation bitstring) and SIGN its published
        form. Returns ``(status_list, encoded, signature)`` where ``encoded`` is the
        spec ``encodedList`` (GZIP + base64url) and ``signature`` is a detached Ed25519
        signature over those exact bytes (C4 ``sign_status_list``).

        Optionally pre-revoke ``revoked_indices``. ``size_bits`` defaults to the C4
        spec minimum (131072) for the herd-privacy property. A receiver checks a
        signer's index OFFLINE against this list; pass it to
        ``Verifier.verify_bom(..., require_revocation=True)`` via the verifier's
        ``revocation`` config (see ``Verifier``)."""
        status = StatusList() if size_bits is None else StatusList(size_bits)
        for idx in revoked_indices or ():
            status.set_revoked(idx)
        encoded = status.encode()
        signature = _sign_status_list(self._privkey, encoded)
        return status, encoded, signature

    def revoke(self, status_list: StatusList, index: int) -> tuple[str, bytes]:
        """Flip a signer's revocation bit in ``status_list`` and RE-SIGN the updated
        published form. Returns the new ``(encoded, signature)`` pair the receiver
        should re-fetch. Wraps C4 ``StatusList.set_revoked`` + ``sign_status_list``.

        HONEST CAVEAT (C4): revocation is only as fresh as a verifier's last re-fetch
        -- the issuer cannot force a stale verifier to refresh. Publish on a short
        interval."""
        status_list.set_revoked(index)
        encoded = status_list.encode()
        signature = _sign_status_list(self._privkey, encoded)
        return encoded, signature

    # -- C4: transparency log ----------------------------------------------- #
    def log_to(self, merkle_log: Any, envelope: Mapping[str, Any]) -> tuple[int, bytes]:
        """Append the canonical bytes of a BOM ``envelope`` to a C4 ``MerkleLog`` for
        tamper-evident issuance, returning ``(index, leaf_hash)`` (C4
        ``log_bom_issuance``). The receiver can later prove inclusion under a signed
        tree head (``merkle_log.signed_tree_head(...)`` +
        ``transparency_log.verify_inclusion(...)``)."""
        return _log_bom_issuance(merkle_log, envelope)


# =========================================================================== #
# Verifier -- the consuming / receiving side (SAFE BY DEFAULT)                  #
# =========================================================================== #
# The two CycloneDX-vs-CEX payload type markers, used to auto-route verify_bom to the
# right brick verifier WITHOUT trusting any consumer-supplied flag.
_CYCLONEDX_TYPE_MARKER = "cyclonedx"


class Verifier:
    """The CONSUMING / receiving side of the trust model -- SAFE BY DEFAULT. A
    ``Verifier`` cannot be constructed in a fail-open configuration.

    A RECEIVER builds a verifier with the dids it CHOSE to trust and the audience +
    issuer it pins, then verifies principals + BOMs offline. Trust is the receiver's
    enrollment decision; nothing is trusted because the envelope says so.

    Construction (ALL safety-critical, each enforced):
      * ``trust_set``    -- a mapping ``did -> Ed25519PublicKey`` the receiver CHOSE.
        REQUIRED and NON-EMPTY -- a None / empty trust_set RAISES ``GovernanceDenied``.
        NEVER build this from an envelope's own ``keyid`` (that is the TOFU collapse
        the audit F4 forbids: an attacker would simply name themselves trusted).
      * ``expected_aud`` -- the audience this receiver pins. REQUIRED and NON-EMPTY --
        a falsy value RAISES (audit R4: a falsy aud silently disables the audience
        check downstream -> fail-open).
      * ``expected_iss`` -- the issuer this receiver pins. REQUIRED and NON-EMPTY --
        a falsy value RAISES (same R4 fail-open trap).
      * ``revocation``   -- OPTIONAL ``(status_list, {did: index})``. When supplied,
        ``verify_bom`` checks the signer's index against it. The index is read ONLY
        from this RECEIVER map, NEVER from the signer-controlled payload (audit R1).
      * ``replay_store`` -- OPTIONAL shared ``MutableSet`` for the principal ``jti``
        replay defense (C1). Defaults to a per-Verifier in-memory set; pass a durable
        set to span processes.

    EVERY failure -- tamper, untrusted signer, wrong audience, replay, revoked,
    cross-tenant -- raises ``GovernanceDenied`` (or a brick subclass of it), so a
    consumer catches ONE base. The verifier NEVER returns on a failed check."""

    def __init__(
        self,
        trust_set: Mapping[str, Ed25519PublicKey],
        *,
        expected_aud: str,
        expected_iss: str,
        revocation: tuple[Any, Mapping[str, int]] | None = None,
        replay_store: MutableSet[str] | None = None,
    ) -> None:
        # SAFE-BY-DEFAULT GUARD 1 (audit F4 / TOFU-collapse): trust is the receiver's
        # enrollment decision. A None / empty trust_set means "trust nothing"; allowing
        # it would invite a consumer to backfill it from the envelope's own keyid,
        # which is exactly the fail-open we refuse. Raise BEFORE anything else.
        if not trust_set:
            raise GovernanceDenied(
                "Verifier requires a non-empty trust_set (a did -> public key mapping "
                "the RECEIVER chose to trust). NEVER build it from the envelope's own "
                "keyid -- that is a TOFU collapse (an attacker would name themselves "
                "trusted). Enroll the issuer's did explicitly: "
                "{issuer.did: issuer.public_key}."
            )
        if not isinstance(trust_set, Mapping):
            raise GovernanceDenied(
                f"trust_set must be a mapping did -> Ed25519PublicKey, got "
                f"{type(trust_set).__name__}"
            )
        for did, key in trust_set.items():
            if not isinstance(key, Ed25519PublicKey):
                raise GovernanceDenied(
                    f"trust_set[{did!r}] must be an Ed25519PublicKey, got "
                    f"{type(key).__name__}"
                )

        # SAFE-BY-DEFAULT GUARD 2 (audit R4): a falsy expected_aud / expected_iss
        # silently disables the audience/issuer binding in the underlying PyJWT decode
        # (fail-open). Refuse to build such a verifier. (C1 ALSO enforces this, but the
        # facade fails earlier + with a facade-level message so the consumer never even
        # reaches a half-built verifier.)
        if not expected_aud or not expected_iss:
            raise GovernanceDenied(
                "Verifier requires non-empty expected_aud AND expected_iss (a falsy "
                "value silently disables the audience/issuer check downstream -- "
                "fail-open). Pass the audience + issuer this receiver pins."
            )

        self._trust_set: dict[str, Ed25519PublicKey] = dict(trust_set)
        self._expected_aud = expected_aud
        self._expected_iss = expected_iss
        self._revocation = revocation
        self._replay_store: MutableSet[str] = (
            set() if replay_store is None else replay_store
        )

        # Build the C1 principal verifier over a JWKS reconstructed from the
        # RECEIVER-chosen trust_set -- each enrolled did becomes a kid. The principal
        # token's header kid is the issuer did (set by Issuer.mint_principal), so it
        # resolves against the receiver's enrolled key, NOT a key the token asserts.
        # NOTE: this raises C1 PrincipalTokenError('config') -- a GovernanceDenied --
        # if aud/iss are falsy; we already guarded that above (defense in depth).
        jwks_doc = _ps.jwks_set(
            *[_ps.jwk_of(pub, did) for did, pub in self._trust_set.items()]
        )
        self._principal_verify = _ps.make_principal_verifier(
            jwks_doc,
            expected_aud=expected_aud,
            expected_iss=expected_iss,
            replay_store=self._replay_store,
        )

    @property
    def trusted_dids(self) -> tuple[str, ...]:
        """The dids this verifier enrolled (read-only view of the trust_set keys)."""
        return tuple(self._trust_set)

    # -- C1: principal verification ----------------------------------------- #
    def verify_principal(self, token: str) -> dict[str, Any]:
        """Verify a principal JWS and return the VALIDATED claims dict (C1
        ``make_principal_verifier`` callable). Pins ``alg=EdDSA`` (rejects ``none`` +
        every downgrade), resolves the ``kid`` against the RECEIVER's trust_set,
        verifies signature + ``exp`` + ``aud`` + ``iss``, and enforces one-time
        ``jti`` replay defense.

        RAISES ``GovernanceDenied`` (the C1 ``PrincipalTokenError`` subclass) on ANY
        failure -- tampered signature, unknown kid, wrong audience/issuer, expired,
        or a replayed jti. Returns the claims on success; the returned dict is what
        feeds ``authorize_inference``."""
        return self._principal_verify(token)

    # -- C5 / C7: BOM verification ------------------------------------------ #
    def verify_bom(
        self,
        envelope: Mapping[str, Any],
        *,
        require_revocation: bool = False,
    ) -> dict[str, Any]:
        """Verify a signed BOM ``envelope`` against the RECEIVER's trust_set and return
        the validated payload (C5 ``verify_knowledge_bom`` or, for a CycloneDX-typed
        envelope, C7 ``verify_signed_cyclonedx_bom`` -- auto-detected from the
        envelope's own ``payloadType``, never from a consumer flag).

        Fail-closed steps (each raises ``GovernanceDenied``): resolve the signer did
        in trust_set ('untrusted_signer'); for a ``did:key`` signer, the did must
        re-derive from the trusted key ('did_key_mismatch', audit R2); verify the
        Ed25519 signature over the DSSE PAE ('bad_signature'); re-check hash-binding
        on every source/data component ('missing_source_hash' / 'missing_hash').

        REVOCATION (the strict path):
          * ``require_revocation=False`` (default): a revocation check runs ONLY if a
            ``revocation`` config was supplied at construction; otherwise it is skipped
            (the caller opted out). This is NOT a fail-open default -- it simply means
            "no revocation list configured, so no revocation claim is made".
          * ``require_revocation=True``: a revocation check is MANDATORY. If no
            ``revocation`` config was supplied at construction, OR the configured map
            has no index for this signer, this RAISES ``GovernanceDenied`` rather than
            returning a payload whose revocation status is unknown. The signer's index
            is read ONLY from the RECEIVER's map, NEVER from the signer-controlled
            payload (audit R1). A revoked signer raises 'revoked'.

        Returns the validated payload on ALLOW; NEVER returns on a failed step."""
        revocation_arg = self._resolve_revocation_arg(envelope, require_revocation)
        if self._is_cyclonedx(envelope):
            return _verify_signed_cyclonedx_bom(
                envelope, self._trust_set, revocation=revocation_arg
            )
        return _verify_knowledge_bom(
            envelope, self._trust_set, revocation=revocation_arg
        )

    def _resolve_revocation_arg(
        self, envelope: Mapping[str, Any], require_revocation: bool
    ) -> Any | None:
        """Decide what ``revocation`` value to hand the brick verifier, fail-closed.

        If ``require_revocation`` is True but no revocation config exists, we MUST NOT
        let the brick silently skip the check. We surface a ``GovernanceDenied`` here,
        BUT only after the signature itself has been validated (so an unverified,
        attacker-controlled envelope cannot probe this path). To preserve that order,
        when a strict check is requested with no config we still pass the brick a
        *bare* sentinel that the brick treats as 'revocation_unresolved' AFTER it has
        verified the signature -- i.e. the strict failure is itself fail-closed and
        post-signature. If a real config IS present, pass it through unchanged."""
        if self._revocation is not None:
            return self._revocation
        if require_revocation:
            # A strict check with NO receiver-supplied index map. The brick verifiers
            # treat a bare (non-tuple) status_list as 'revocation_unresolved' AFTER the
            # signature check -- fail-closed, post-signature. We hand them a minimal
            # StatusList so the strict deny is raised by the brick's own audited path
            # rather than a facade-side shortcut that would bypass the signature gate.
            return StatusList()
        return None

    @staticmethod
    def _is_cyclonedx(envelope: Mapping[str, Any]) -> bool:
        """Route to the CycloneDX verifier iff the envelope's OWN ``payloadType`` names
        a CycloneDX media type. Auto-detection from the envelope (not a consumer flag)
        keeps the call site small AND honest: a mis-typed envelope is rejected by the
        chosen brick verifier's payloadType binding, not silently coerced."""
        if not isinstance(envelope, Mapping):
            return False
        payload_type = envelope.get("payloadType")
        return isinstance(payload_type, str) and _CYCLONEDX_TYPE_MARKER in payload_type

    # -- C2 / C5: authorization gates --------------------------------------- #
    def authorize_inference(
        self, claims: Mapping[str, Any], target_tenant: str, op: str = "infer"
    ) -> str:
        """Authorize an inference call for a VERIFIED principal against
        ``target_tenant`` (C2 ``authorize_inference``). ``claims`` MUST be the dict
        returned by ``verify_principal`` (its ``tenant`` claim is the bound tenant).

        Same-tenant -> returns the validated ``target_tenant``. Cross-tenant, a
        principal with no bound tenant, or an empty target -> RAISES
        ``GovernanceDenied`` (the C2 ``CrossTenantInferenceDenied`` subclass),
        fail-closed."""
        return _authorize_inference(claims, target_tenant, op)

    def authorize_bom_flow(
        self, payload: Mapping[str, Any], requesting_tenant: str, owner_tenant: str
    ) -> str:
        """Authorize a BOM FLOW across a tenant boundary, keyed on the validated
        payload's ``access_modifier`` (C5 ``authorize_bom_flow``). ``payload`` MUST be
        the dict returned by ``verify_bom``.

        ``public`` -> allow any tenant. ``private`` / ``protected`` (protected ==
        private in v1) -> allow ONLY if ``requesting_tenant == owner_tenant``;
        otherwise RAISES ``GovernanceDenied`` ('cross_tenant'), fail-closed. Returns
        the validated ``requesting_tenant`` on allow."""
        return _authorize_bom_flow(payload, requesting_tenant, owner_tenant)

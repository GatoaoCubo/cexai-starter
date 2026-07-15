"""Signed-principal identity + the alg-pinned verifier that fills the jwt_guard
seam (CONVERGENCE T8, Component 1 -- principal identity).

This is the FIRST brick of the T8 signing/identity foundation
(N05_operations/P08_architecture/p08_adr_convergence_trust_model.md, Component 1).
Today ``jwt_guard.py`` ships ``options={"verify_signature": False}`` on its
no-verifier fallback path -- it will accept any token, including ``alg=none``.
The blueprint's design is that the fabric injects a REAL verifier callable via
the ``_decode`` precedence path the guard already exposes
(``JwtAuthGuard(verifier=...)``). This module is that callable, plus the signing
root it verifies against.

What lives here (the v1-ENFORCES set; v2 attestation is deferred per the ADR):

  * ``generate_signing_key`` -- a fresh Ed25519 private key (the per-tenant scoped
    signing key of Component 2; HSM custody is v2 SPEC).
  * ``did_key`` -- a ``did:key:z...`` string for an Ed25519 public key
    (multicodec 0xed01 -> base58btc). SELF-ROOTED: a ``did:key`` is derived
    entirely from the key bytes, so it is the cex-lab instance asserting its own
    identity, NOT an independent root. The ADR's INDEPENDENT root of trust
    (transparency log + receiver-chosen federation bundle, Component 5) is a
    later brick; ``did:key`` alone is Trust-On-First-Use, and the docstring on
    ``did_key`` says so plainly.
  * ``jwks`` / ``jwks_set`` -- the public half as a JWK (``kty=OKP, crv=Ed25519``)
    and a JWKS document. The fabric resolves ``kid -> public key`` from this
    (ADR hop 4, "NOT from the token, NOT from the caller").
  * ``mint_principal_token`` -- mints a signed JWS (``alg=EdDSA``) FROM the bound
    Principal, with the claim set ``{iss, sub, aud, tenant, iat, exp, jti}``
    (Component 1 / the propagation diagram). ``jti`` is THE replay key; no unchecked
    ``nonce`` is minted (audit R8 -- the code matches the enforced control).
  * ``make_principal_verifier`` -- the injectable verifier. It pins ``alg=EdDSA``
    (rejects ``none`` and every downgrade -- "the single most important hardening
    over today's verify_signature: False", ADR Component 1), resolves the ``kid``
    against the JWKS, verifies signature + ``exp`` + ``aud`` + ``iss`` via PyJWT,
    and enforces a one-time ``jti`` replay defense. It returns the validated
    claims dict; it RAISES ``PrincipalTokenError`` on ANY failure.

Honest caveats (stated, not hidden):
  * The replay store is an in-memory ``set`` for v1. The ADR is explicit that the
    fabric MUST persist the jti seen-set as a contract obligation (Component 1,
    replay-defense row); see ``make_principal_verifier``. The replay key is ``jti``
    ONLY -- no ``nonce`` is minted or checked (audit R8).
  * ``did:key`` is self-rooted (TOFU), not the independent root of trust.

Dependencies (both verified present): ``cryptography`` (Ed25519 key ops + raw key
bytes) and ``PyJWT`` (``alg=EdDSA`` sign/verify). This module imports them at
module load -- it is the T8 crypto brick, NOT the dormant RBAC dev path, so the
import-light discipline of ``jwt_guard`` (lazy pyjwt) does not apply here. The
injected-verifier contract this satisfies is documented on
``make_principal_verifier``.

ASCII-only per .claude/rules/ascii-code-rule.md.

absorbs: convergence/t8-trust-model (Component 1 -- principal identity)
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable, Iterable, Mapping, MutableSet
from typing import Any

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from cexai.governance._shared.errors import GovernanceDenied
from cexai.governance.rbac._b58 import b58encode
from cexai.governance.rbac._b64 import b64url_encode

__all__ = [
    "PrincipalTokenError",
    "generate_signing_key",
    "public_key_of",
    "did_key",
    "jwk_of",
    "jwks",
    "jwks_set",
    "mint_principal_token",
    "make_principal_verifier",
]

# The ONE pinned signing algorithm (ADR Component 1: alg MUST be EdDSA; "none" and
# RS256-downgrade are rejected). Kept as a 1-tuple so the pin is a single source of
# truth shared by the minter and the verifier.
_PINNED_ALGS: tuple[str, ...] = ("EdDSA",)

# Multicodec prefix for an Ed25519 public key, varint-encoded: 0xed 0x01 (ADR
# Component 1 / W3C did:key method). Prepended to the 32 raw key bytes before
# base58btc to form the did:key method-specific id.
_ED25519_MULTICODEC_PREFIX = b"\xed\x01"

# Default principal-token lifetime. The ADR pins exp <= 90s (Component 1, replay
# defense: "short exp (<= 90s)"). A caller may override per-mint.
_DEFAULT_TTL_SECONDS = 90


class PrincipalTokenError(GovernanceDenied):
    """A presented principal token failed verification (CONVERGENCE T8,
    Component 1). Subclasses ``GovernanceDenied`` (audit R5) -- NOT ``ValueError`` --
    so an idiomatic ``except ValueError`` upstream cannot silently swallow a security
    deny; a caller wrapping the injected verifier in ``JwtAuthGuard`` catches it via
    ``except GovernanceDenied`` (or this specific type) instead of letting a
    PyJWT-internal type leak through. Carries a ``reason`` token (e.g.
    ``alg_not_pinned``, ``unknown_kid``, ``replay``, ``bad_signature``,
    ``expired``, ``bad_audience``, ``bad_issuer``, ``malformed``, ``config``) so
    callers and the audit log branch on a field, not a parsed message. RAISED by the
    ``make_principal_verifier`` callable on ANY failure; never on success. ``config``
    is raised at CONSTRUCTION (not per-token) when ``expected_aud``/``expected_iss``
    are missing -- a misconfigured, fail-open verifier must not be buildable
    (audit R4)."""

    def __init__(self, reason: str, detail: str = "") -> None:
        self.reason = reason
        message = f"principal token rejected: {reason}"
        if detail:
            message = f"{message} -- {detail}"
        super().__init__(message)


# --------------------------------------------------------------------------- #
# Key material (Component 2 -- the per-tenant scoped signing key)               #
# --------------------------------------------------------------------------- #
def generate_signing_key() -> Ed25519PrivateKey:
    """Generate a fresh Ed25519 signing private key. In the T8 design this is a
    per-tenant SCOPED key (Component 2): it both signs the principal JWS and is
    the tenant's network identity, so a key leak burns one tenant, not the whole
    fabric. v1 keeps the key in process; HSM/KMS custody of the root KEK is v2
    SPEC (ADR Component 2 / Component 6)."""
    return Ed25519PrivateKey.generate()


def public_key_of(privkey: Ed25519PrivateKey) -> Ed25519PublicKey:
    """The public half of ``privkey`` -- the bytes published in the JWKS and
    embedded in the ``did:key``."""
    return privkey.public_key()


def _raw_public_bytes(pubkey: Ed25519PublicKey) -> bytes:
    """The 32 raw Ed25519 public-key bytes (no PEM/DER wrapper). This is the
    canonical form for both the multicodec did:key id and the JWK ``x`` value."""
    return pubkey.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


# --------------------------------------------------------------------------- #
# did:key (SELF-ROOTED identity -- TOFU, not the independent root of trust)     #
# --------------------------------------------------------------------------- #
def did_key(pubkey: Ed25519PublicKey) -> str:
    """Return the ``did:key:z...`` DID for an Ed25519 public key (W3C did:key).

    Construction: ``base58btc( 0xed01 || raw_pubkey )`` with the multibase ``z``
    prefix, yielding ``did:key:z<base58>``. Self-contained -- no network resolver,
    no registry: the DID IS the key.

    HONESTY (ADR Component 5, load-bearing): because the DID is derived purely
    from the key bytes, it is SELF-ROOTED. The cex-lab instance is asserting its
    own identity; anyone can mint a ``did:key`` for any key they hold. This is
    Trust-On-First-Use (TOFU), NOT the zero-trust independent root of trust the
    blueprint requires (a transparency log + a RECEIVER-chosen federation bundle,
    Component 5). This function stands up the identity SEED only; binding it to an
    independent anchor is a later T8 brick."""
    multicodec = _ED25519_MULTICODEC_PREFIX + _raw_public_bytes(pubkey)
    return f"did:key:z{b58encode(multicodec)}"


# --------------------------------------------------------------------------- #
# JWKS (Component 1 hop 4 -- fabric resolves kid -> public key from HERE)        #
# --------------------------------------------------------------------------- #
def jwk_of(pubkey: Ed25519PublicKey, kid: str) -> dict[str, str]:
    """Return the public key as a single JWK (RFC 8037 OKP/Ed25519). ``x`` is the
    base64url (unpadded) raw public key; ``kid`` is the key id the token header
    carries so the verifier can resolve this exact key. ``use`` / ``alg`` are set
    so a strict consumer knows this is an EdDSA verification key."""
    return {
        "kty": "OKP",
        "crv": "Ed25519",
        "x": b64url_encode(_raw_public_bytes(pubkey)),
        "kid": kid,
        "use": "sig",
        "alg": "EdDSA",
    }


# Back-compat / spec alias: the blueprint names this ``jwks(pubkey, kid)``.
jwks = jwk_of


def jwks_set(*jwk_entries: Mapping[str, str]) -> dict[str, list[dict[str, str]]]:
    """Wrap one or more JWKs into a JWKS document ``{"keys": [...]}`` (RFC 7517).
    This is what a JWKS endpoint serves and what ``make_principal_verifier``
    consumes; supporting multiple keys is what enables the ADR's overlapping-``kid``
    rotation (Component 1, rotation row)."""
    return {"keys": [dict(entry) for entry in jwk_entries]}


# --------------------------------------------------------------------------- #
# Mint (framework side -- a signed JWS FROM the bound Principal)                 #
# --------------------------------------------------------------------------- #
def mint_principal_token(
    privkey: Ed25519PrivateKey,
    kid: str,
    claims: Mapping[str, Any],
    *,
    ttl_seconds: int = _DEFAULT_TTL_SECONDS,
) -> str:
    """Mint a signed JWS (``alg=EdDSA``) carrying the principal claims (ADR
    Component 1 / the propagation diagram, hop 3 "mint").

    ``claims`` supplies the identity fields; this function fills the standard
    time/uniqueness claims so callers cannot forget them:
      * ``iat`` -- issued-at (now, epoch seconds).
      * ``exp`` -- now + ``ttl_seconds`` (default 90s per the ADR replay-defense row).
      * ``jti`` -- a fresh uuid4 if the caller did not supply one. This is THE
        one-time replay key: the verifier's replay store rejects a second
        presentation of the same jti.
    Caller-supplied values (including ``iss``/``sub``/``aud``/``tenant``) are kept
    as-is. The header pins ``alg=EdDSA`` and carries the ``kid`` the verifier uses
    to resolve the public key. Returns the compact JWS string.

    REPLAY CONTROL HONESTY (audit R8): this minter does NOT add a ``nonce`` claim.
    An earlier version minted+advertised a ``nonce`` that NO verifier ever checked
    (a dead control -- the code claimed a defense it did not enforce). The single,
    REAL replay key is ``jti``; the verifier records and rejects a repeated ``jti``.
    The code now matches the claim. (A caller MAY still pass its own ``nonce`` in
    ``claims`` for an out-of-band protocol; this function neither adds nor checks one.)

    The token carries ``{iss, sub, aud, tenant, residency_tag (if supplied), iat,
    exp, jti}``; this function does not REQUIRE iss/sub/aud/tenant (the verifier
    enforces aud/iss at decode time) but does guarantee iat/exp/jti are present and
    well-formed."""
    now = int(time.time())
    payload: dict[str, Any] = dict(claims)
    payload.setdefault("iat", now)
    payload["exp"] = now + int(ttl_seconds)
    payload.setdefault("jti", uuid.uuid4().hex)
    return jwt.encode(
        payload,
        privkey,
        algorithm=_PINNED_ALGS[0],
        headers={"kid": kid},
    )


# --------------------------------------------------------------------------- #
# Verify (the injectable callable -- fills the jwt_guard seam)                  #
# --------------------------------------------------------------------------- #
def _index_jwks_by_kid(jwks_doc: Mapping[str, Any]) -> dict[str, Any]:
    """Build a ``kid -> PyJWK`` index from a JWKS document. Each key is parsed once
    at verifier-construction time (not per token) so verification is a dict lookup.
    A JWK missing a ``kid`` is skipped (it cannot be resolved by a token header)."""
    index: dict[str, Any] = {}
    for entry in jwks_doc.get("keys", ()):  # type: ignore[union-attr]
        kid = entry.get("kid")
        if not kid:
            continue
        index[kid] = jwt.PyJWK.from_dict(dict(entry))
    return index


def make_principal_verifier(
    jwks_doc: Mapping[str, Any],
    expected_aud: str,
    expected_iss: str,
    replay_store: MutableSet[str] | None = None,
    *,
    leeway_seconds: int = 0,
) -> Callable[[str], dict[str, Any]]:
    """Build the injectable verifier callable that fills the ``jwt_guard`` seam
    (CONVERGENCE T8, Component 1 / ADR propagation hop 4 "verify").

    INJECTED-VERIFIER CONTRACT (so N07 can re-run + review):
      * Build:   ``verify = make_principal_verifier(jwks_set(jwk_of(pub, kid)),
                 expected_aud, expected_iss[, replay_store])``.
      * Inject:  ``JwtAuthGuard(verifier=verify)`` -- this matches the guard's
                 declared ``verifier: Callable[[str], Mapping[str, Any]]`` and the
                 ``_decode`` precedence path (``self._verifier(token_str)`` first).
      * Call:    ``verify(token_str: str) -> dict[str, Any]``.
      * On success: returns the VALIDATED claims dict (``sub``, ``role``, ``exp``,
                 ``tenant``, ``aud``, ``iss``, ``jti``, ...). The guard then projects
                 ``sub``/``role``/``exp`` into its frozen ``AuthToken`` exactly as it
                 does for any verifier.
      * On ANY failure: RAISES ``PrincipalTokenError`` (a ``ValueError`` subclass)
                 with a ``.reason`` field. The callable NEVER returns on failure
                 and NEVER silently downgrades.

    Verification steps, in order (ADR hop 4 steps 1-4):
      1. Read the JWS header WITHOUT trusting it; ASSERT ``alg == 'EdDSA'``. This
         rejects ``alg=none`` and every downgrade BEFORE any signature math -- the
         single most important hardening over today's ``verify_signature: False``.
      2. Resolve ``kid`` -> public key from ``jwks_doc`` (NOT from the token body,
         NOT from the caller). An unknown/absent ``kid`` is rejected.
      3. Verify the signature + ``exp`` + ``aud`` + ``iss`` via PyJWT
         ``decode(verify_signature=True, algorithms=['EdDSA'], audience=..., issuer=...)``.
         A tampered payload, wrong key, expired token, or audience/issuer mismatch
         each raise.
      4. Enforce replay defense: the ``jti`` must be unseen. A second presentation
         of the same ``jti`` raises ``PrincipalTokenError('replay')``. A token with
         no ``jti`` is rejected (a principal token MUST carry one).

    CONFIG GUARD (audit R4): ``expected_aud`` and ``expected_iss`` are REQUIRED and
    must be non-empty. A falsy ``expected_aud`` (notably ``None``) makes PyJWT SKIP
    the audience check entirely -- a fail-OPEN trap where a token for any audience is
    accepted. (An empty string already fails closed in PyJWT, but ``None`` is the
    silent-disable trap.) Both are therefore validated AT CONSTRUCTION and a falsy
    value raises ``PrincipalTokenError('config')`` immediately, so a misconfigured
    verifier can never be built -- the audience/issuer binding is never silently off.

    HONEST CAVEAT (replay store): ``replay_store`` defaults to an in-memory
    ``set`` -- correct and sufficient for a single process / v1. The ADR is
    explicit that PRODUCTION persistence of the jti seen-set is a FABRIC-SIDE
    contract obligation (Component 1, replay-defense row: "the fabric MUST persist
    the jti seen-set"). Pass a shared, durable ``MutableSet`` to span processes.
    ``leeway_seconds`` allows a small clock-skew tolerance on ``exp`` (default 0 --
    strict).

    EVICTION (R-215): entries this verifier instance adds to ``seen_jti`` are
    pruned once past their own ``exp`` (+ ``leeway_seconds``), so the store does
    not grow without bound over the life of a long-running verifier. This is
    SAFE: a jti past its exp holds zero replay-defense value already, because
    step 3 above re-checks ``exp`` on every call via PyJWT independent of the
    replay store -- an expired token is rejected as ``expired`` whether or not
    its jti is still on file. Eviction therefore narrows nothing a still-valid
    (unexpired, within ``leeway_seconds``) token relies on for replay-rejection;
    it only reclaims memory for jtis that could never be replayed again anyway."""
    # CONFIG GUARD (audit R4): a falsy expected_aud/expected_iss would silently
    # disable the audience/issuer check (fail-open). Refuse to build such a verifier.
    if not expected_aud or not expected_iss:
        raise PrincipalTokenError(
            "config", "expected_aud and expected_iss are required (non-empty)"
        )
    key_index = _index_jwks_by_kid(jwks_doc)
    seen_jti: MutableSet[str] = set() if replay_store is None else replay_store
    # R-215: jti -> exp (+leeway) for entries THIS verifier added, so they can be
    # pruned once expired. Local bookkeeping only -- does not change what
    # `replay_store` itself is (still a MutableSet[str]); a jti this instance
    # never inserted (e.g. pre-seeded, or added by another verifier sharing the
    # same store) is simply not tracked here and is left alone, same as today.
    _jti_exp: dict[str, float] = {}

    def _evict_expired(now: float) -> None:
        stale = [j for j, exp_at in _jti_exp.items() if exp_at <= now]
        for j in stale:
            seen_jti.discard(j)
            del _jti_exp[j]

    def verify(token_str: str) -> dict[str, Any]:
        # Step 1 -- ALG PINNING (before any signature work). Reading the header is
        # unverified by definition; we use it ONLY to reject a bad alg and to find
        # the kid. A malformed token (not three base64url segments) raises here.
        try:
            header = jwt.get_unverified_header(token_str)
        except jwt.PyJWTError as exc:
            raise PrincipalTokenError("malformed", str(exc)) from exc
        alg = header.get("alg")
        if alg not in _PINNED_ALGS:
            # Covers "none", RS256/HS256 downgrade, and any unexpected alg.
            raise PrincipalTokenError("alg_not_pinned", f"alg={alg!r}")

        # Step 2 -- resolve kid -> public key from the JWKS (independent of token body).
        kid = header.get("kid")
        if not kid or kid not in key_index:
            raise PrincipalTokenError("unknown_kid", f"kid={kid!r}")
        signing_jwk = key_index[kid]

        # Step 3 -- verify signature + exp + aud + iss. algorithms is pinned AGAIN
        # here (defense in depth): even if step 1 were bypassed, PyJWT will not
        # accept a non-EdDSA signature.
        try:
            claims: dict[str, Any] = jwt.decode(
                token_str,
                signing_jwk.key,
                algorithms=list(_PINNED_ALGS),
                audience=expected_aud,
                issuer=expected_iss,
                leeway=leeway_seconds,
                options={"require": ["exp"]},
            )
        except jwt.ExpiredSignatureError as exc:
            raise PrincipalTokenError("expired", str(exc)) from exc
        except jwt.InvalidAudienceError as exc:
            raise PrincipalTokenError("bad_audience", str(exc)) from exc
        except jwt.InvalidIssuerError as exc:
            raise PrincipalTokenError("bad_issuer", str(exc)) from exc
        except jwt.InvalidSignatureError as exc:
            raise PrincipalTokenError("bad_signature", str(exc)) from exc
        except jwt.PyJWTError as exc:
            # Any other PyJWT failure (missing required exp, decode error, ...).
            raise PrincipalTokenError("invalid", str(exc)) from exc

        # Step 4 -- REPLAY defense. The jti must exist and be unseen. Recording it
        # AFTER successful signature/exp checks means a forged/expired token never
        # pollutes the seen-set (so it cannot be used to DoS a legitimate jti).
        # R-215: prune anything past its own exp+leeway BEFORE the membership
        # check -- bounds seen_jti to the currently-live TTL window instead of
        # growing forever (see EVICTION note on this function's docstring).
        _evict_expired(time.time())
        jti = claims.get("jti")
        if not jti:
            raise PrincipalTokenError("missing_jti")
        if jti in seen_jti:
            raise PrincipalTokenError("replay", f"jti={jti}")
        seen_jti.add(str(jti))
        _jti_exp[str(jti)] = float(claims["exp"]) + leeway_seconds

        return claims

    return verify


def _coerce_kids(entries: Iterable[Mapping[str, str]]) -> tuple[str, ...]:
    """Helper for callers/tests: the ordered kids present in a JWKS key list."""
    return tuple(str(e["kid"]) for e in entries if e.get("kid"))

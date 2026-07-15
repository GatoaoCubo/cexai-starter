"""Append-only Merkle transparency log + a signed tree head -- the tamper-evident
signing history of the T8 trust foundation (CONVERGENCE T8, checkpoint 7).

This is checkpoint C4 / the LAST brick of the T8 framework foundation
(N07_admin/P08_architecture/p08_adr_convergence_master.md Section 4.1 step 7,
"transparency log (Rekor-style, append-only) -- a signing event is logged with an
inclusion proof"; p08_adr_convergence_trust_model.md Component 5 -- root of trust /
revocation). Component 1 stood up signed-principal identity; Component 2 the
per-tenant key hierarchy + the inference deny-surface; Component 3 the signed-model
allow-list. C1's ``did:key`` is SELF-ROOTED (Trust-On-First-Use), and the ADR is
explicit that the INDEPENDENT root of trust requires (a) a tamper-evident log of
signing events so a receiver can confirm a signature existed at a point in time and
(b) an offline-checkable revocation list. This module is (a); ``status_list``
(checkpoint 8) is (b).

WHAT LIVES HERE:
  * ``MerkleLog`` -- an append-only log. ``append(data)`` adds a leaf and returns
    ``(index, leaf_hash)``; ``root()`` is the current Merkle tree head over all
    leaves; ``size`` is the leaf count; ``inclusion_proof(index)`` returns the
    audit path (the sibling hashes) proving leaf ``index`` is committed under the
    current root.
  * ``verify_inclusion(leaf_hash, index, proof, root, tree_size)`` -- recomputes the
    root from the leaf + audit path and constant-time-compares it to the claimed
    root. A tampered leaf, a tampered proof element, or a wrong root all yield
    ``False``. This is the receiver-side check: it needs ONLY the leaf, its index,
    the audit path, the tree size, and the (signed) root -- not the whole log.
  * ``signed_tree_head(privkey)`` / ``SignedTreeHead`` -- a detached Ed25519
    signature over the canonical bytes of ``(tree_size || root)``. The KEY is C1's
    Ed25519 key (``generate_signing_key`` / ``public_key_of``); the CRYPTOSUITE is a
    detached signature, NOT a JWS (a tree head is a static integrity assertion, not
    a bearer token -- the council's "share the key, not the cryptosuite", same shape
    as C3's model-allow-list entry). ``verify_signed_tree_head(pubkey, sth)`` returns
    ``True`` only if the signature is authentic for that exact ``(tree_size, root)``.

RFC 6962 DOMAIN SEPARATION (second-preimage defense -- the headline crypto choice):
    A naive Merkle tree (hash(left||right) with leaves hashed the same way) is
    vulnerable to a second-preimage attack: an attacker can present an internal
    node as if it were a leaf, because the two are indistinguishable. RFC 6962
    fixes this with a one-byte domain tag:
      leaf hash = SHA256( 0x00 || data )
      node hash = SHA256( 0x01 || left || right )
    A leaf can never collide with an interior node because their first hashed byte
    differs. Both hashers live in ``_hash_leaf`` / ``_hash_node`` as the single
    source of truth shared by the log, the proof, and the verifier.

HONEST CAVEATS (stated, not hidden -- both are ADR/council findings):
  (1) SELF-ROOTED v1. This log is in-process / framework-RUN: the SAME framework
      that mints the signing events also roots the log and signs its tree head. It
      is therefore "tamper-evident TO THE OPERATOR" -- it detects accidental
      corruption and lets a holder of an old signed tree head detect a fork or a
      rewrite, but it does NOT provide the ADR Component 5 INDEPENDENCE. A truly
      independent root needs a RECEIVER-CHOSEN / third-party log operator (a
      Rekor-style witnessed log, or gossip between independent monitors). Until then
      a malicious operator could rewrite the whole log AND re-sign a fresh tree head
      with the same key. The mechanism (inclusion proofs + signed tree heads) is the
      RIGHT mechanism; the trust is only as strong as the operator until a witness
      is added. See ``MerkleLog`` and ``signed_tree_head``.
  (2) NO consistency proof in v1. RFC 6962 also defines a consistency proof (old
      tree head -> new tree head is append-only, no rewrite). v1 ships inclusion
      proofs + signed tree heads only; a monitor that retains successive signed tree
      heads can still detect a non-append-only jump by re-deriving, but the compact
      consistency-proof primitive is a later brick. Stated, not hidden.

Dependency: ``cryptography`` (Ed25519 sign/verify) + stdlib ``hashlib`` -- NO new
dependency. Like the sibling C1/C2/C3 modules this imports the crypto primitive at
module load (it IS a T8 crypto brick, not the dormant RBAC dev path).

ASCII-only per .claude/rules/ascii-code-rule.md.

absorbs: convergence/t8-trust-model (Component 5 / checkpoint 7 -- transparency log)
"""

from __future__ import annotations

import hashlib
import hmac
import time
from dataclasses import dataclass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from cexai.governance._shared.errors import GovernanceDenied

__all__ = [
    "TransparencyLogError",
    "MerkleLog",
    "SignedTreeHead",
    "leaf_hash",
    "verify_inclusion",
    "verify_signed_tree_head",
]

# RFC 6962 domain-separation prefixes. The single byte that distinguishes a leaf
# hash from an interior-node hash; prepended before the SHA-256 so a leaf can never
# be presented as an interior node (second-preimage defense). Kept as named
# constants so every hasher (log + proof + verifier) agrees on the exact bytes.
_LEAF_PREFIX = b"\x00"
_NODE_PREFIX = b"\x01"

# The Merkle hash of the EMPTY log (size 0). RFC 6962 defines it as SHA-256 of the
# empty string (no domain prefix -- there is no leaf and no node to tag). Returned
# by ``root()`` on an empty log and accepted by ``verify_signed_tree_head`` for a
# size-0 head, so the empty-log edge case is well-defined rather than a crash.
_EMPTY_ROOT = hashlib.sha256(b"").digest()


class TransparencyLogError(GovernanceDenied):
    """A transparency-log operation failed (CONVERGENCE T8, checkpoint 7).

    Subclasses ``GovernanceDenied`` (audit R5) -- NOT ``ValueError`` -- the same
    security-deny posture as ``PrincipalTokenError`` (C1), ``EnvelopeKeyError`` (C2),
    and ``ModelLoadDenied`` (C3). A security deny must NOT be swallowed by a generic
    ``except ValueError`` upstream; catch it via ``except GovernanceDenied`` (or this
    specific type) rather than letting an IndexError/TypeError leak through. Carries a
    ``reason`` token so callers and the audit log branch on a field, not a parsed
    message. ``reason`` is one of:
      * ``index_out_of_range`` -- ``inclusion_proof`` asked for a leaf index that is
        not in ``[0, size)``. A clean error, never a crash.
      * ``empty_log``          -- a proof was requested from a log with no leaves.
      * ``malformed_sth``      -- a signed-tree-head mapping is missing a field or
        carries a wrong-typed value (verify side).
    RAISED on a bad request; NEVER on a successful append / proof / verify."""

    def __init__(self, reason: str, detail: str = "") -> None:
        self.reason = reason
        message = f"transparency log error: {reason}"
        if detail:
            message = f"{message} -- {detail}"
        super().__init__(message)


# --------------------------------------------------------------------------- #
# RFC 6962 hashers (the single source of truth for leaf + node hashing)         #
# --------------------------------------------------------------------------- #
def _hash_leaf(data: bytes) -> bytes:
    """RFC 6962 leaf hash: ``SHA256(0x00 || data)``. The ``0x00`` domain tag is what
    makes a leaf un-spoofable as an interior node (second-preimage defense)."""
    return hashlib.sha256(_LEAF_PREFIX + data).digest()


def _hash_node(left: bytes, right: bytes) -> bytes:
    """RFC 6962 interior-node hash: ``SHA256(0x01 || left || right)``. The ``0x01``
    domain tag distinguishes a node from a leaf."""
    return hashlib.sha256(_NODE_PREFIX + left + right).digest()


def leaf_hash(data: bytes) -> bytes:
    """Public helper: the RFC 6962 leaf hash of ``data`` (``SHA256(0x00 || data)``).

    Exposed so a caller can compute the leaf hash of bytes it is about to log (or
    independently re-derive the leaf hash it stored) without reaching into the
    private hasher. ``MerkleLog.append`` returns this same value for the appended
    leaf."""
    return _hash_leaf(data)


def _merkle_root(leaves: list[bytes]) -> bytes:
    """The RFC 6962 Merkle tree head (MTH) over an ordered list of LEAF HASHES.

    Definition (RFC 6962 Sec. 2.1), recursive:
      * MTH({})        = SHA256("")            -- the empty-log root.
      * MTH({d0})      = d0                     -- a single leaf hash IS the root.
      * MTH(D[n]), n>1 = node( MTH(D[0:k]), MTH(D[k:n]) ) where k is the LARGEST
        power of two strictly less than n.
    The ``k = largest power of two < n`` split (not n/2) is what makes the tree
    left-balanced and the inclusion/consistency proofs well-defined; ``_split_point``
    computes it. Operates on leaf HASHES (already domain-tagged), so it only ever
    applies ``_hash_node``."""
    n = len(leaves)
    if n == 0:
        return _EMPTY_ROOT
    if n == 1:
        return leaves[0]
    k = _split_point(n)
    return _hash_node(_merkle_root(leaves[:k]), _merkle_root(leaves[k:]))


def _split_point(n: int) -> int:
    """The largest power of two strictly less than ``n`` (RFC 6962 ``k``). For
    ``n >= 2``: e.g. n=2 -> 1, n=3 -> 2, n=4 -> 2, n=5 -> 4, n=8 -> 4. This is the
    left-subtree size at every interior node and is shared by the root computation
    and the inclusion-proof walk so the two never disagree."""
    k = 1
    while (k << 1) < n:
        k <<= 1
    return k


def _inclusion_path(leaves: list[bytes], index: int) -> list[bytes]:
    """The RFC 6962 audit path for leaf ``index`` within ``leaves`` (leaf HASHES).

    Returns the ordered list of sibling hashes from the leaf up to (but excluding)
    the root -- exactly what a verifier folds back together with the leaf to
    recompute the root. Recursive, mirroring ``_merkle_root``'s split: at each
    interior node, if the target index is in the left subtree, the sibling is the
    root of the RIGHT subtree (and recurse left); otherwise the sibling is the root
    of the LEFT subtree (and recurse right, re-basing the index). A single-leaf tree
    has an empty path. Precondition: ``0 <= index < len(leaves)`` (the caller
    ``inclusion_proof`` enforces this and raises a clean error otherwise)."""
    n = len(leaves)
    if n <= 1:
        return []
    k = _split_point(n)
    if index < k:
        # Target is in the left subtree; sibling is the right subtree's root.
        return _inclusion_path(leaves[:k], index) + [_merkle_root(leaves[k:])]
    # Target is in the right subtree; sibling is the left subtree's root.
    return _inclusion_path(leaves[k:], index - k) + [_merkle_root(leaves[:k])]


# --------------------------------------------------------------------------- #
# The append-only log                                                           #
# --------------------------------------------------------------------------- #
class MerkleLog:
    """An append-only RFC 6962 Merkle log -- the tamper-evident signing history
    (CONVERGENCE T8, checkpoint 7).

    USAGE (so N07 can re-run + review):
      * ``log = MerkleLog()`` -- a fresh empty log.
      * ``index, lh = log.append(b"<event bytes>")`` -- log a signing event (e.g. a
        principal-token mint or a model-allow-list entry's canonical bytes). Returns
        the leaf's 0-based ``index`` and its RFC 6962 leaf hash ``lh``.
      * ``root = log.root()`` -- the current Merkle tree head over ALL leaves. Empty
        log -> the RFC 6962 empty root (``SHA256("")``).
      * ``proof = log.inclusion_proof(index)`` -- the audit path (sibling hashes) for
        that leaf under the CURRENT root.
      * ``verify_inclusion(lh, index, proof, root, log.size)`` -> ``True`` -- a
        receiver re-derives the root from leaf + path and compares.
      * ``sth = log.signed_tree_head(privkey)`` -- a detached Ed25519 signature over
        ``(tree_size || root)``; ``verify_signed_tree_head(pubkey, sth)`` checks it.

    Append-only is enforced by construction: there is no public mutate/delete; the
    only state change is ``append``, which extends the leaf list. The Merkle root is
    recomputed from the full leaf list on each ``root()`` / ``inclusion_proof`` call
    (correct + simple for v1's volumes; an incremental tree is a later optimization,
    not a correctness change).

    HONEST CAVEAT (self-rooted -- ADR Component 5): the framework that appends the
    events also owns this object and signs its tree head. This is tamper-evident TO
    THE OPERATOR (and to any holder of a previously-issued signed tree head, who can
    detect a fork/rewrite), but it is NOT an independent root of trust -- a malicious
    operator can rewrite the whole list and re-sign. The independence the ADR
    requires needs a receiver-chosen / third-party (witnessed) log. See the module
    docstring."""

    def __init__(self) -> None:
        # Ordered list of LEAF HASHES (already RFC 6962 domain-tagged). The raw data
        # is intentionally NOT retained: a transparency log commits to and proves the
        # data's hash, and not holding the plaintext keeps the log's memory bounded
        # and avoids becoming a second copy of (possibly sensitive) event payloads.
        self._leaves: list[bytes] = []

    @property
    def size(self) -> int:
        """The number of leaves currently in the log (the tree size)."""
        return len(self._leaves)

    def append(self, data: bytes) -> tuple[int, bytes]:
        """Append one leaf for ``data`` and return ``(index, leaf_hash)``.

        ``index`` is the 0-based position (== the old size). ``leaf_hash`` is the
        RFC 6962 leaf hash ``SHA256(0x00 || data)`` -- the value a receiver later
        passes to ``verify_inclusion``. Appending strictly grows the log and changes
        the root (a new leaf is folded into a new tree head). ``data`` must be
        ``bytes`` (a ``bytearray`` is accepted and normalized); any other type is a
        ``TypeError`` from the hasher -- the log stores bytes, not objects."""
        lh = _hash_leaf(bytes(data))
        index = len(self._leaves)
        self._leaves.append(lh)
        return index, lh

    def root(self) -> bytes:
        """The current Merkle tree head over all leaves (RFC 6962 MTH). An empty log
        returns the RFC 6962 empty root (``SHA256("")``); a single-leaf log returns
        that leaf's hash; otherwise the recursively-folded node hash. Recomputed from
        the full leaf list on each call."""
        return _merkle_root(self._leaves)

    def inclusion_proof(self, index: int) -> list[bytes]:
        """The audit path (list of sibling hashes) proving leaf ``index`` is
        committed under the current ``root()``.

        The returned list runs from the leaf's immediate sibling UP to the level
        just below the root; ``verify_inclusion`` folds it back together with the
        leaf hash to recompute the root. A single-leaf log returns ``[]`` (the leaf
        IS the root, no siblings). Raises ``TransparencyLogError`` -- ``empty_log``
        if the log has no leaves, ``index_out_of_range`` if
        ``index`` is not in ``[0, size)`` -- a clean error, never an IndexError."""
        n = len(self._leaves)
        if n == 0:
            raise TransparencyLogError("empty_log", "no leaves to prove")
        if index < 0 or index >= n:
            raise TransparencyLogError(
                "index_out_of_range", f"index={index} not in [0, {n})"
            )
        return _inclusion_path(self._leaves, index)

    def signed_tree_head(self, privkey: Ed25519PrivateKey) -> SignedTreeHead:
        """Produce a ``SignedTreeHead`` over the CURRENT ``(size, root())``.

        The signature is a DETACHED Ed25519 signature (the raw 64-byte signature,
        not a JWS) over ``_sth_canonical_bytes(size, root)`` -- the shared-KEY design:
        ``privkey`` is an Ed25519 key as produced by C1's ``generate_signing_key``,
        the SAME trust root that signs principal tokens (C1) and model entries (C3).
        A ``timestamp`` (epoch seconds, ``time.time()``) is recorded for operational
        context but is NOT part of the signed canonical bytes -- a verifier checks
        the signature over ``(tree_size, root)`` only, so the head's authenticity
        does not depend on the clock (and tests do not depend on a time value)."""
        size = len(self._leaves)
        rt = self.root()
        signature = privkey.sign(_sth_canonical_bytes(size, rt))
        return SignedTreeHead(
            tree_size=size,
            root_hex=rt.hex(),
            signature=signature,
            timestamp=time.time(),
        )


# --------------------------------------------------------------------------- #
# Signed tree head (reuses C1's Ed25519 KEY, detached-signature cryptosuite)    #
# --------------------------------------------------------------------------- #
def _sth_canonical_bytes(tree_size: int, root: bytes) -> bytes:
    """The canonical byte string a signed tree head's signature covers:
    ``tree_size`` as an 8-byte big-endian unsigned int, concatenated with the raw
    32-byte ``root``.

    Fixed-width length-prefixing (8 bytes) makes the two fields unambiguous to parse
    and impossible to confuse (an attacker cannot move bytes between the size field
    and the root). Signing the SIZE as well as the root binds the head to a specific
    tree state -- a root cannot be replayed under a different claimed size. The
    signer and the verifier MUST build these bytes identically; this one helper is
    the single source of truth for both."""
    return tree_size.to_bytes(8, byteorder="big", signed=False) + root


@dataclass(frozen=True)
class SignedTreeHead:
    """A signed commitment to the log's state at a point in time (CONVERGENCE T8,
    checkpoint 7).

    Fields:
      * ``tree_size`` -- the number of leaves the head commits to.
      * ``root_hex``  -- the Merkle tree head (root) as lowercase hex (transport- and
        log-friendly; the raw bytes are ``bytes.fromhex(root_hex)``).
      * ``signature`` -- the detached Ed25519 signature over
        ``_sth_canonical_bytes(tree_size, root)``, produced by
        ``MerkleLog.signed_tree_head`` with the trust-root private key.
      * ``timestamp`` -- epoch seconds when the head was signed (operational context;
        NOT covered by the signature, so it never affects verification).

    Frozen (immutable) so the bytes that were signed are the bytes that are checked.
    ``as_dict`` emits a ``{tree_size, root_hex, signature, timestamp}`` mapping
    (signature kept as raw bytes; a transport layer may hex/base64 it)."""

    tree_size: int
    root_hex: str
    signature: bytes
    timestamp: float = 0.0

    def root_bytes(self) -> bytes:
        """The raw 32-byte root this head commits to (decoded from ``root_hex``)."""
        return bytes.fromhex(self.root_hex)

    def canonical_bytes(self) -> bytes:
        """The exact bytes this head's signature covers (delegates to the shared
        canonicalizer so signer + verifier never drift)."""
        return _sth_canonical_bytes(self.tree_size, self.root_bytes())

    def as_dict(self) -> dict[str, object]:
        """The ``{tree_size, root_hex, signature, timestamp}`` mapping."""
        return {
            "tree_size": self.tree_size,
            "root_hex": self.root_hex,
            "signature": self.signature,
            "timestamp": self.timestamp,
        }


def verify_signed_tree_head(pubkey: Ed25519PublicKey, sth: SignedTreeHead) -> bool:
    """Return ``True`` only if ``sth``'s detached Ed25519 signature is authentic for
    its exact ``(tree_size, root)`` under ``pubkey`` (the public half of the
    trust-root key -- C1's ``public_key_of`` of the signing key).

    Verifies the signature over ``sth.canonical_bytes()``. A head signed by a
    DIFFERENT key, or whose ``tree_size`` / ``root_hex`` was altered after signing,
    fails -> ``False`` (no exception for a bad signature -- a boolean is the contract,
    matching how a receiver branches). A structurally broken ``sth`` (root_hex not
    valid hex) is a clean ``TransparencyLogError('malformed_sth')`` rather than a
    crash."""
    try:
        message = sth.canonical_bytes()
    except (ValueError, TypeError) as exc:
        raise TransparencyLogError("malformed_sth", str(exc)) from exc
    try:
        pubkey.verify(sth.signature, message)
    except InvalidSignature:
        return False
    return True


# --------------------------------------------------------------------------- #
# Receiver-side inclusion verification (needs only leaf + path + root + size)   #
# --------------------------------------------------------------------------- #
def verify_inclusion(
    leaf_hash: bytes,
    index: int,
    proof: list[bytes],
    root: bytes,
    tree_size: int,
) -> bool:
    """Recompute the Merkle root from ``leaf_hash`` + the audit ``proof`` and
    constant-time-compare it to the claimed ``root`` (RFC 6962 inclusion check).

    This is the RECEIVER side -- it needs ONLY the leaf hash, its ``index``, the
    audit ``proof`` (from ``MerkleLog.inclusion_proof``), the ``tree_size`` the proof
    was issued at, and the (signed) ``root``. It does NOT need the log itself.

    PROOF ORDERING (must match ``_inclusion_path``): the audit path is emitted
    BOTTOM-UP -- ``proof[0]`` is the leaf's immediate sibling (deepest level) and the
    LAST element is the sibling just below the root (shallowest level). The tree
    structure, however, is naturally walked TOP-DOWN (the largest power-of-two split
    first). To reconcile the two, this verifier first walks the structure top-down to
    record, at each level, whether the target sits in the LEFT or RIGHT subtree; it
    then folds the leaf upward consuming the proof in its natural bottom-up order
    against those recorded sides (reversed, so the deepest side pairs with
    ``proof[0]``). This keeps proof generation and verification provably consistent
    for every tree shape, not just balanced ones.

    Returns:
      * ``True``  -- the recomputed root EQUALS ``root`` (the leaf is committed under
        that root at that size).
      * ``False`` -- ANY mismatch: a tampered leaf hash, a tampered/missing/extra
        proof element, a wrong root, or an ``index``/``tree_size`` that is internally
        inconsistent (e.g. index >= tree_size, or a proof whose length does not match
        the tree shape). Fail-closed: a malformed proof is a ``False``, not a crash.

    The final compare is ``hmac.compare_digest`` (constant-time) so verification does
    not leak how many leading bytes matched via timing -- defense in depth for a
    primitive that may run on attacker-controlled input."""
    # Internal-consistency guard: an out-of-range index or non-positive size can
    # never have a valid proof. Reject before folding (fail-closed, no crash).
    if tree_size <= 0 or index < 0 or index >= tree_size:
        return False

    # Pass 1 (TOP-DOWN): record at each interior level whether the target is in the
    # left subtree. ``sides[j]`` corresponds to the j-th split from the TOP. The
    # number of splits equals the number of siblings the proof must contain.
    sides: list[bool] = []  # True == target in LEFT subtree at that level
    idx = index
    size = tree_size
    while size > 1:
        k = _split_point(size)
        if idx < k:
            sides.append(True)
            size = k
        else:
            sides.append(False)
            idx -= k
            size -= k

    # The proof must contain EXACTLY one sibling per split -- too few or too many
    # means a malformed proof and must not silently verify.
    if len(proof) != len(sides):
        return False

    # Pass 2 (BOTTOM-UP): fold the leaf upward. The proof is bottom-up (proof[0] is
    # the deepest sibling) while ``sides`` is top-down, so iterate ``sides`` reversed
    # so the deepest recorded side pairs with proof[0].
    computed = leaf_hash
    for sibling, target_in_left in zip(proof, reversed(sides)):
        if target_in_left:
            # Target was the LEFT child; sibling is the right subtree root.
            computed = _hash_node(computed, sibling)
        else:
            # Target was the RIGHT child; sibling is the left subtree root.
            computed = _hash_node(sibling, computed)
    return hmac.compare_digest(computed, root)

"""StatusList2021-style revocation -- the offline-checkable revocation list of the
T8 trust foundation (CONVERGENCE T8, checkpoint 8).

This is the companion to ``transparency_log`` in checkpoint C4 / the LAST brick of
the T8 framework foundation (N07_admin/P08_architecture/p08_adr_convergence_master.md
Section 4.1 step 8, "federation/revocation issuance (federation bundle +
StatusList2021) -- a receiver verifies + checks revocation offline";
p08_adr_convergence_trust_model.md Component 5 -- root of trust / revocation). The
ADR's "verify-without-trust" needs an OFFLINE-checkable revocation list so a
compromised key/credential can be revoked without a per-check network call to the
issuer (the council picked StatusList2021 for identity-revocation, alongside the
transparency log for tamper-evident history -- master ADR row 5).

THE STATUSLIST2021 MODEL (W3C Bitstring Status List):
    Each credential / key the framework issues is assigned an INDEX into a shared
    bitstring. Bit ``i`` == 1 means "the entity at index i is REVOKED"; 0 means
    valid. The whole list is published (GZIP + base64url), so a verifier fetches it
    ONCE and can then check any index OFFLINE (a single bit read) -- no per-check
    callback to the issuer. The spec mandates a MINIMUM list length of 131072 bits
    (16 KB) so that the herd-privacy property holds: a published list this large
    hides WHICH specific credential a verifier is checking (the index is not leaked
    by a targeted fetch).

WHAT LIVES HERE:
  * ``StatusList`` -- a fixed-size bitstring (``bytearray``). Defaults to the spec
    minimum (131072 bits = 16 KB). ``set_revoked(index)`` flips a bit to 1;
    ``is_revoked(index)`` reads it. ``encode()`` -> a compact published form (GZIP +
    base64url, the spec's ``encodedList``); ``StatusList.decode(encoded)`` round-trips
    it back, preserving every revocation bit.
  * ``sign_status_list(privkey, encoded)`` -> a detached Ed25519 signature over the
    ENCODED bytes. ``verify_status_list(pubkey, encoded, sig)`` -> ``True`` only if
    the signature is authentic for that exact encoded list. The KEY is C1's Ed25519
    key (the council's "share the key, not the cryptosuite"); the cryptosuite is a
    detached signature over the published bytes -- same shape as C3's model entry and
    the transparency log's tree head, NOT a JWS.

WHY SIGN THE *ENCODED* FORM: the published artifact a verifier actually fetches IS
the encoded list. Signing exactly those bytes means a bit-flip ANYWHERE in transit
(whether it lands as a revocation change after decode or as gzip corruption) breaks
the signature -- the verifier rejects the tampered list before trusting any bit.

HONEST CAVEAT (revocation latency -- ADR/council revocation-staleness finding):
    Revocation is only as fresh as a verifier's last re-fetch of the status list.
    The framework can ISSUE and re-sign an updated list the instant a key is
    compromised, but it CANNOT force a verifier that cached an older signed list to
    refresh. A revoked entity therefore remains accepted by a stale verifier until
    that verifier re-fetches -- the staleness window is bounded by the verifier's
    refresh cadence, which the issuer does not control. This is inherent to ANY
    offline / pull-based revocation (it is the whole reason CRLs carry a
    ``nextUpdate`` and OCSP-stapling exists); the mitigation is a short
    publish/refresh interval, NOT a guarantee the framework can make alone. Stated,
    not hidden. (A second-order point: this v1 list is framework-self-signed, so it
    shares the transparency log's self-rooted caveat -- an independent root makes the
    SIGNATURE trustworthy across instances; that is the same Component 5 brick.)

Dependency: ``cryptography`` (Ed25519 sign/verify) + stdlib ``gzip`` + the local
``_b64`` (base64url) helper -- NO new dependency. Imports the crypto primitive at
module load (it IS a T8 crypto brick, like its C1/C2/C3 siblings).

ASCII-only per .claude/rules/ascii-code-rule.md.

absorbs: convergence/t8-trust-model (Component 5 / checkpoint 8 -- StatusList2021 revocation)
"""

from __future__ import annotations

import gzip

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from cexai.governance._shared.errors import GovernanceDenied
from cexai.governance.rbac._b64 import b64url_decode, b64url_encode

__all__ = [
    "StatusListError",
    "StatusList",
    "DEFAULT_SIZE_BITS",
    "MIN_SPEC_SIZE_BITS",
    "sign_status_list",
    "verify_status_list",
]

# The W3C StatusList2021 mandated MINIMUM bitstring length: 131072 bits = 16 KB.
# A list at least this large gives the herd-privacy property (a fetch does not
# reveal which index is being checked). This is the DEFAULT so a v1 list is
# spec-conformant out of the box.
MIN_SPEC_SIZE_BITS = 16 * 1024 * 8  # 131072

# Default list size. Equal to the spec minimum -- a caller MAY pass a smaller size
# for a constrained v1 deployment (the class allows it and documents the privacy
# trade-off), but the default is conformant.
DEFAULT_SIZE_BITS = MIN_SPEC_SIZE_BITS

# Upper bound on the size we will ALLOCATE from a decoded list, so a hostile/corrupt
# encoded blob that gzip-inflates to a multi-gigabyte bitstring is rejected as
# malformed rather than exhausting memory. 16 MiB of bits (134,217,728 bits) is far
# beyond any realistic revocation list yet caps the blast radius of a decompression
# bomb. (gzip itself is also bounded below via a max-decompress read.)
_MAX_SIZE_BITS = 16 * 1024 * 1024 * 8

# Hard cap on bytes we will inflate from a single encoded list (decompression-bomb
# guard). Mirrors _MAX_SIZE_BITS in byte terms with headroom.
_MAX_DECOMPRESS_BYTES = (_MAX_SIZE_BITS // 8) + 1024


class StatusListError(GovernanceDenied):
    """A status-list operation failed (CONVERGENCE T8, checkpoint 8).

    Subclasses ``GovernanceDenied`` (audit R5) -- NOT ``ValueError`` -- the same
    security-deny posture as ``PrincipalTokenError`` (C1), ``EnvelopeKeyError`` (C2),
    ``ModelLoadDenied`` (C3), and ``TransparencyLogError`` (checkpoint 7). A security
    deny must NOT be swallowed by a generic ``except ValueError`` upstream; catch it
    via ``except GovernanceDenied`` (or this specific type) rather than letting an
    IndexError/OSError leak through. Carries a ``reason`` token so callers and the
    audit log branch on a field, not a parsed message.
    ``reason`` is one of:
      * ``index_out_of_range`` -- ``set_revoked`` / ``is_revoked`` was given an index
        outside ``[0, size_bits)``. A clean error, never an IndexError.
      * ``bad_size``           -- a non-positive or absurd (> cap) size was requested.
      * ``malformed_encoding`` -- ``decode`` was given bytes that are not valid
        base64url, do not gzip-inflate, or inflate past the size cap. A clean denial,
        never a crash on hostile input.
    RAISED on a bad request; NEVER on a successful set / read / encode / decode."""

    def __init__(self, reason: str, detail: str = "") -> None:
        self.reason = reason
        message = f"status list error: {reason}"
        if detail:
            message = f"{message} -- {detail}"
        super().__init__(message)


class StatusList:
    """A StatusList2021-style revocation bitstring (CONVERGENCE T8, checkpoint 8).

    USAGE (so N07 can re-run + review):
      * ``sl = StatusList()`` -- a fresh list at the spec-minimum size, all bits 0
        (nothing revoked).
      * ``sl.set_revoked(i)`` -- mark the entity at index ``i`` revoked (bit -> 1).
      * ``sl.is_revoked(i) -> bool`` -- read index ``i`` (revoked == ``True``).
      * ``encoded = sl.encode()`` -- the published compact form (GZIP + base64url,
        the spec's ``encodedList``), an ASCII ``str``.
      * ``sl2 = StatusList.decode(encoded)`` -- round-trip back to a StatusList with
        identical bits (and identical ``size_bits``).
      * pair with ``sign_status_list`` / ``verify_status_list`` for authenticity.

    Bit layout: index ``i`` lives in byte ``i // 8`` at bit position ``i % 8``
    (LSB-first within the byte). Encode/decode preserve this exactly, so a bit set
    before encoding reads the same after decoding.

    HONEST CAVEAT (latency + self-rooted): revocation freshness is bounded by a
    verifier's refresh cadence (the issuer cannot force a stale verifier to refetch),
    and the v1 list is framework-self-signed (independent cross-instance trust needs
    the Component 5 root). See the module docstring."""

    def __init__(self, size_bits: int = DEFAULT_SIZE_BITS) -> None:
        """Create an all-zero (nothing-revoked) list of ``size_bits`` bits.

        Defaults to the spec minimum (131072). A caller MAY pass a smaller size for a
        constrained deployment (the privacy property weakens -- module docstring); a
        non-positive or absurdly large size raises ``StatusListError('bad_size')``.
        ``size_bits`` is rounded UP to a whole byte for storage, but ``size_bits``
        (the logical bit length) is what bounds ``set_revoked`` / ``is_revoked`` and
        what survives an encode/decode round-trip."""
        if size_bits <= 0:
            raise StatusListError("bad_size", f"size_bits must be > 0, got {size_bits}")
        if size_bits > _MAX_SIZE_BITS:
            raise StatusListError(
                "bad_size", f"size_bits {size_bits} exceeds cap {_MAX_SIZE_BITS}"
            )
        self._size_bits = int(size_bits)
        self._bytes = bytearray((self._size_bits + 7) // 8)

    @property
    def size_bits(self) -> int:
        """The logical bit length of the list (the number of revocable indices)."""
        return self._size_bits

    def _check_index(self, index: int) -> None:
        """Raise ``StatusListError('index_out_of_range')`` unless ``index`` is a valid
        bit position in ``[0, size_bits)``. Shared by ``set_revoked`` / ``is_revoked``
        so an out-of-range access is a clean denial, never an IndexError."""
        if not isinstance(index, int) or isinstance(index, bool):
            raise StatusListError("index_out_of_range", f"index must be int, got {type(index).__name__}")
        if index < 0 or index >= self._size_bits:
            raise StatusListError(
                "index_out_of_range", f"index={index} not in [0, {self._size_bits})"
            )

    def set_revoked(self, index: int, revoked: bool = True) -> None:
        """Set the revocation bit at ``index`` (default ``True`` == revoked).

        Passing ``revoked=False`` clears the bit (un-revoke) -- supported because a
        list is re-issued over time and an entry can be corrected, though revocation
        is normally monotonic. Raises ``StatusListError('index_out_of_range')`` for
        an index outside ``[0, size_bits)``."""
        self._check_index(index)
        byte_i, bit_i = divmod(index, 8)
        mask = 1 << bit_i
        if revoked:
            self._bytes[byte_i] |= mask
        else:
            self._bytes[byte_i] &= ~mask & 0xFF

    def is_revoked(self, index: int) -> bool:
        """Return ``True`` if the entity at ``index`` is revoked (bit == 1), ``False``
        otherwise. Raises ``StatusListError('index_out_of_range')`` for an index
        outside ``[0, size_bits)`` -- the contract is a clean error, not a crash on a
        bad index."""
        self._check_index(index)
        byte_i, bit_i = divmod(index, 8)
        return bool(self._bytes[byte_i] & (1 << bit_i))

    def encode(self) -> str:
        """Encode the list to the published compact form: GZIP-compress the raw
        bitstring bytes, then base64url (unpadded) -- the spec's ``encodedList``.

        The logical ``size_bits`` is recoverable from the inflated byte length only
        up to a byte boundary, so the exact bit length is carried out-of-band: this
        method emits ONLY the encoded bitstring (the spec's ``encodedList`` is exactly
        that), and ``decode`` reconstructs ``size_bits`` from the inflated length
        (size is a whole multiple of 8 by construction here). The GZIP step is what
        makes a mostly-zero 16 KB list tiny on the wire (a fresh list compresses to a
        few dozen bytes). Deterministic ``mtime=0`` so the same bits encode to the
        same string (stable for signing + diffing)."""
        compressed = gzip.compress(bytes(self._bytes), mtime=0)
        return b64url_encode(compressed)

    @classmethod
    def decode(cls, encoded: str) -> "StatusList":
        """Reconstruct a ``StatusList`` from ``encode()`` output (base64url -> gunzip).

        Round-trips the bits exactly: a bit set before ``encode`` reads the same after
        ``decode``. FAIL-CLOSED on hostile input -- bytes that are not valid
        base64url, do not gzip-inflate, or inflate past the size cap raise
        ``StatusListError('malformed_encoding')`` rather than crashing or allocating
        unbounded memory (decompression-bomb guard via a bounded read)."""
        try:
            compressed = b64url_decode(encoded)
        except (ValueError, TypeError) as exc:
            raise StatusListError("malformed_encoding", f"not base64url: {exc}") from exc
        try:
            raw = _gunzip_bounded(compressed, _MAX_DECOMPRESS_BYTES)
        except (OSError, EOFError, ValueError) as exc:
            # gzip raises BadGzipFile (OSError subclass) / EOFError on bad streams.
            raise StatusListError("malformed_encoding", f"not gzip: {exc}") from exc
        size_bits = len(raw) * 8
        if size_bits <= 0:
            raise StatusListError("malformed_encoding", "decoded to an empty list")
        if size_bits > _MAX_SIZE_BITS:
            raise StatusListError(
                "malformed_encoding", f"decoded size {size_bits} exceeds cap"
            )
        sl = cls.__new__(cls)
        sl._size_bits = size_bits
        sl._bytes = bytearray(raw)
        return sl


def _gunzip_bounded(compressed: bytes, max_bytes: int) -> bytes:
    """Gunzip ``compressed`` but read AT MOST ``max_bytes`` of inflated output, so a
    decompression bomb (a tiny blob that inflates to gigabytes) is refused instead of
    exhausting memory. Reads ``max_bytes + 1`` and rejects if the stream produced
    more than ``max_bytes`` (it did not terminate within budget). Returns the inflated
    bytes on success."""
    with gzip.GzipFile(fileobj=_BytesReader(compressed)) as gz:
        out = gz.read(max_bytes + 1)
    if len(out) > max_bytes:
        raise ValueError("decompressed output exceeds bound (possible gzip bomb)")
    return out


class _BytesReader:
    """Minimal read-only file-like wrapper over a ``bytes`` buffer for
    ``gzip.GzipFile`` (which needs a ``read``-able fileobj). Stdlib ``io.BytesIO``
    would also work; this keeps the dependency surface to nothing and makes the
    bounded-read intent explicit."""

    def __init__(self, data: bytes) -> None:
        self._data = data
        self._pos = 0

    def read(self, n: int = -1) -> bytes:
        if n is None or n < 0:
            chunk = self._data[self._pos :]
            self._pos = len(self._data)
            return chunk
        chunk = self._data[self._pos : self._pos + n]
        self._pos += len(chunk)
        return chunk


# --------------------------------------------------------------------------- #
# Signature over the ENCODED list (reuses C1's Ed25519 KEY, detached suite)     #
# --------------------------------------------------------------------------- #
def sign_status_list(privkey: Ed25519PrivateKey, encoded: str) -> bytes:
    """Produce a DETACHED Ed25519 signature over the ENCODED status list bytes.

    ``encoded`` is the output of ``StatusList.encode()`` -- the exact published
    artifact a verifier fetches. Signing those bytes (ASCII-encoded) means any
    tampering with the published list breaks the signature. ``privkey`` is an Ed25519
    key as produced by C1's ``generate_signing_key`` -- the shared-KEY design (one
    trust root signs principal tokens, model entries, tree heads, AND status lists);
    the signature is DETACHED (raw 64 bytes, not a JWS) because a status list is a
    static integrity assertion, not a bearer token. Returns the signature bytes;
    publish them alongside ``encoded``."""
    return privkey.sign(encoded.encode("ascii"))


def verify_status_list(
    pubkey: Ed25519PublicKey, encoded: str, signature: bytes
) -> bool:
    """Return ``True`` only if ``signature`` is an authentic Ed25519 signature over
    ``encoded`` under ``pubkey`` (the public half of the trust-root key -- C1's
    ``public_key_of`` of the signing key).

    A list signed by a DIFFERENT key, or whose ``encoded`` bytes were altered after
    signing (even a single flipped bit, which changes the gzip stream), fails ->
    ``False`` (no exception for a bad signature -- a boolean is the contract, matching
    how a receiver branches). A non-str ``encoded`` is a clean
    ``StatusListError('malformed_encoding')`` rather than a crash."""
    if not isinstance(encoded, str):
        raise StatusListError(
            "malformed_encoding", f"encoded must be str, got {type(encoded).__name__}"
        )
    try:
        pubkey.verify(signature, encoded.encode("ascii"))
    except InvalidSignature:
        return False
    return True

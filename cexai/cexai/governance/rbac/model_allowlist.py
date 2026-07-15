"""Signed-model allow-list + the safetensors-vs-pickle format gate that refuses to
DISPATCH an unsafe model load (CONVERGENCE T8, Component 3 -- model integrity).

This is the THIRD brick of the T8 trust foundation
(N07_admin/P08_architecture/p08_adr_convergence_master.md Section 4.1 step 4,
honest-floor row "signed-model allow-list + safetensors safe-load";
p08_adr_convergence_trust_model.md Component 3). Component 1 stood up
signed-principal identity; Component 2 stood up the per-tenant key hierarchy +
the inference deny-surface. This module closes a DIFFERENT live hole: today model
bytes flow over TCP behind a shared key with NO integrity check. A pickle-format
model file deserializes ARBITRARY Python on load -- a remote-code-execution
primitive handed straight to the fabric. C3 builds the framework-side gate that
refuses to dispatch a model load unless BOTH:

  (a) the file is safetensors (a pure-data tensor container -- NOT pickle, so a
      load cannot execute code), AND
  (b) its SHA-256 is present in a signed allow-list (so an attacker who swaps the
      bytes for a different-but-still-safetensors file is also refused).

The two checks are independent and BOTH fail-closed: format is checked BEFORE any
hash work (a pickle file is rejected without ever being read as a model), and the
allow-list entry's own Ed25519 signature is verified before its hash is trusted (a
forged entry cannot whitelist a malicious hash).

KEY-SHARING DESIGN (council finding "share the key, not the cryptosuite"):
    The allow-list signature REUSES Component 1's Ed25519 key approach -- the same
    ``cryptography`` Ed25519 primitive C1's ``generate_signing_key`` produces. It
    does NOT reuse C1's JWT/JWS machinery: a model-allow-list entry is not a
    bearer token with aud/iss/exp/replay semantics, it is a static integrity
    assertion. The right shape is a DETACHED Ed25519 signature over the canonical
    entry bytes (model_id || sha256 || format), verified with the SAME public-key
    type the fabric already resolves for principals. So the shared, reusable thing
    is the KEY (one Ed25519 trust root signs both principal tokens and model
    entries); the cryptosuite around it is per-use.

HONEST CAVEAT (ADR honest-floor / council finding -- framework vs fabric):
    This is the FRAMEWORK gate. ``authorize_model_load`` refuses to DISPATCH a
    load it judges unsafe. It CANNOT stop a FABRIC that ignores the gate and
    pickle-loads anyway: the Phase-2 vendor_fabric (the fabric) MUST ALSO enforce
    safetensors-only + the allow-list AT ITS ACTUAL DESERIALIZATION POINT. The
    framework deciding "this file is safe to send" does not make the receiver
    deserialize it safely -- if the fabric calls ``torch.load`` (pickle) on
    whatever bytes arrive, this gate is bypassed. The gate NARROWS the surface
    (nothing unsafe is dispatched THROUGH the framework) but the proof requires
    the fabric to honor the matching safe-load contract. Stated, not hidden.

ADDITIONAL CAVEATS:
  * The format gate is a STRUCTURAL parser, not a deep validator. ``is_safetensors``
    positively validates the 8-byte length prefix + that the header parses as a
    JSON object; it does NOT validate every tensor dtype/offset (the fabric's
    safetensors loader does that). Its JOB is to (1) POSITIVELY confirm the
    safetensors container shape and (2) REJECT anything pickle-ish. A file that is
    neither valid-safetensors nor pickle is still rejected (not_safetensors) --
    deny-by-default.
  * ``is_pickle`` is deliberately CONSERVATIVE (over-rejects rather than under-
    rejects): protocol-2..5 framing (b"\\x80" + 0x01..0x05) AND the classic
    protocol-0/1 opcodes that can appear at offset 0 are all treated as pickle.
    A non-pickle file that happens to start with one of those opcode bytes would
    be rejected -- acceptable, because the safetensors path is the positive
    allow-path and a real safetensors file never starts with those bytes (it
    starts with a little-endian uint64 length).
  * ``authorize_model_load`` (the closure ``make_model_gate`` returns) reads a
    path input ONCE via ``_read_all_bytes`` and threads that single ``bytes``
    snapshot through the format gate AND the hash check (TOCTOU close -- a
    prior version opened the path independently up to four times across those
    two checks, leaving a window where the on-disk file could be swapped
    between opens). The trade-off, stated: this holds the full file in memory
    for the duration of one gate call, rather than streaming the hash off a
    fresh path read as the module's ``_sha256_hex`` docstring originally
    intended for path inputs -- correctness (validated bytes == hashed bytes
    == dispatched bytes) is prioritized over that streaming optimization. The
    standalone ``is_pickle`` / ``is_safetensors`` / ``assert_safe_format`` /
    ``_sha256_hex`` functions are UNCHANGED and still stream a path in bounded
    reads when called directly (e.g. by tests probing a path in isolation);
    only the gate's own multi-check sequence was TOCTOU-exposed.

Dependency: ``cryptography`` (Ed25519 sign/verify) + stdlib ``hashlib`` / ``json``
-- NO new dependency (the ``safetensors`` pip package is intentionally NOT
required; the format is parsed from raw bytes). Like the sibling C1/C2 modules
this imports the crypto primitive at module load (it IS a T8 crypto brick).

ASCII-only per .claude/rules/ascii-code-rule.md.

absorbs: convergence/t8-trust-model (Component 3 -- signed-model allow-list + safe-load)
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from typing import Any, Union

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from cexai.governance._shared.errors import GovernanceDenied

__all__ = [
    "ModelLoadDenied",
    "AllowlistEntry",
    "DEFAULT_FORMAT",
    "is_pickle",
    "is_safetensors",
    "assert_safe_format",
    "sign_allowlist_entry",
    "make_allowlist_entry",
    "make_model_gate",
]

# The one format this gate POSITIVELY allows. safetensors is a pure-data container
# (a JSON header + raw tensor bytes), so loading it cannot execute code -- unlike
# pickle. Kept as a named constant so the minter and the gate agree on the label
# that goes into the signed canonical bytes.
DEFAULT_FORMAT = "safetensors"

# safetensors layout: the first 8 bytes are a little-endian uint64 giving the
# length of the JSON header that immediately follows. We read exactly this many
# bytes to parse + bound-check the header.
_HEADER_LEN_FIELD = 8

# Upper bound on the JSON header length we will accept (sanity guard against a
# corrupt/forged 8-byte prefix claiming a multi-exabyte header). 100 MiB is far
# larger than any real safetensors metadata header yet stops an absurd allocation
# request from a hostile length prefix. A header this large is rejected as
# malformed rather than trusted.
_MAX_HEADER_LEN = 100 * 1024 * 1024

# Pickle protocol-2..5 files begin with the PROTO opcode b"\\x80" followed by a
# single protocol-version byte in 0x01..0x05. This is the dominant modern pickle
# framing (and exactly what ``torch.save`` emits), so it is the primary RCE
# signature we reject.
_PICKLE_PROTO_OPCODE = 0x80
_PICKLE_MAX_PROTO = 0x05

# Classic protocol-0/1 pickles are not framed with b"\\x80"; they begin directly
# with a pickle opcode. These are the opcodes that legitimately appear at offset 0
# of a real pickle stream (push-mark, build-list/dict, and the GLOBAL opcode 'c'
# that imports an arbitrary callable -- the literal RCE lever). Treating them as
# pickle-ish is conservative by design (see module docstring).
_PICKLE_LEADING_OPCODES = frozenset(b"(]}c")

# Read budget for format sniffing when a path is given: enough to cover the 8-byte
# length prefix plus a generous header, without slurping a multi-GB weights file
# into memory just to classify it. The header for any real model fits well under
# this; if the declared header_len exceeds what we read, we re-open and read the
# exact slice (see ``_read_safetensors_header``).
_SNIFF_BYTES = 1 << 16  # 64 KiB

# A path-or-bytes input. ``str`` / ``os.PathLike`` are treated as a filesystem
# path to read; ``bytes`` / ``bytearray`` are treated as the file content itself
# (so callers can probe in-memory buffers without a temp file).
PathOrBytes = Union[str, "os.PathLike[str]", bytes, bytearray]


class ModelLoadDenied(GovernanceDenied):
    """A model load was REFUSED by the C3 framework gate (CONVERGENCE T8,
    Component 3).

    Subclasses ``GovernanceDenied`` (audit R5) -- NOT ``ValueError`` -- the same
    security-deny posture as ``PrincipalTokenError`` (C1) and ``EnvelopeKeyError``
    (C2). A security deny must NOT be swallowed by a generic ``except ValueError``
    upstream; catch it via ``except GovernanceDenied`` (or this specific type).
    RAISED fail-closed on ANY failure of the format gate or the signed allow-list;
    NEVER raised on success (the gate returns the validated entry instead). Carries
    a ``reason`` token so callers and the audit log branch on a field, not a parsed
    message. ``reason`` is one of:
      * ``pickle_rejected`` -- the file is (or looks like) a pickle. THE RCE GATE.
      * ``not_safetensors`` -- the file is not pickle but does not positively
        validate as a safetensors container.
      * ``unknown_model``   -- no allow-list entry exists for the given model_id,
        or the computed file hash is not allow-listed.
      * ``bad_signature``   -- an allow-list entry's Ed25519 signature does not
        verify against the gate's trusted public key (forged/absent signature).
      * ``hash_mismatch``   -- the file's SHA-256 differs from the signed entry's
        hash (the model bytes were tampered after signing).
      * ``malformed``       -- the file/entry is structurally unreadable (empty
        file, truncated header, bad length prefix, non-JSON header, missing entry
        fields). Never a crash -- a malformed input is a clean denial.
    """

    def __init__(self, reason: str, detail: str = "") -> None:
        self.reason = reason
        message = f"model load denied: {reason}"
        if detail:
            message = f"{message} -- {detail}"
        super().__init__(message)


# --------------------------------------------------------------------------- #
# byte access (path or in-memory buffer)                                        #
# --------------------------------------------------------------------------- #
def _read_prefix(data_or_path: PathOrBytes, n: int) -> bytes:
    """Return up to the first ``n`` bytes of the input.

    For a ``bytes``/``bytearray`` input, slices in memory. For a path, opens the
    file and reads ``n`` bytes. A path that does not exist / cannot be read raises
    ``ModelLoadDenied('malformed')`` rather than leaking an ``OSError`` -- the gate
    NEVER crashes on a bad input, it denies."""
    if isinstance(data_or_path, (bytes, bytearray)):
        return bytes(data_or_path[:n])
    try:
        with open(data_or_path, "rb") as handle:
            return handle.read(n)
    except OSError as exc:
        raise ModelLoadDenied("malformed", f"cannot read {data_or_path!r}: {exc}") from exc


def _file_size(data_or_path: PathOrBytes) -> int:
    """Total byte length of the input (len() for a buffer, stat size for a path).
    A path that cannot be stat'd raises ``ModelLoadDenied('malformed')``."""
    if isinstance(data_or_path, (bytes, bytearray)):
        return len(data_or_path)
    try:
        return os.path.getsize(data_or_path)
    except OSError as exc:
        raise ModelLoadDenied("malformed", f"cannot stat {data_or_path!r}: {exc}") from exc


def _read_all_bytes(data_or_path: PathOrBytes) -> bytes:
    """Return the FULL contents of the input as a single ``bytes`` object,
    obtained via exactly ONE open-and-read of a path (or a plain copy of an
    in-memory buffer).

    Used by ``authorize_model_load`` to close a TOCTOU window: the format gate
    (``assert_safe_format`` -> ``is_safetensors`` / ``is_pickle``) and the hash
    check (``_sha256_hex``) previously each independently re-opened the PATH by
    name (up to four separate ``open()`` calls across the four gate steps). A
    caller who can swap the file on disk between those opens could get one
    file's bytes format-validated and a DIFFERENT (swapped) file's bytes
    hashed/dispatched -- defeating the gate's own invariant that the validated
    bytes are the bytes that get loaded. Reading once here and threading the
    resulting ``bytes`` through every subsequent check (they already have an
    in-memory-buffer code path, exercised directly by
    ``test_pickle_detected_from_in_memory_bytes``) means every check sees the
    SAME snapshot, taken at a single point in time.

    A path that cannot be read raises ``ModelLoadDenied('malformed')`` --
    consistent with ``_read_prefix`` / ``_file_size`` / ``_sha256_hex``, the
    gate never crashes on a bad input, it denies."""
    if isinstance(data_or_path, (bytes, bytearray)):
        return bytes(data_or_path)
    try:
        with open(data_or_path, "rb") as handle:
            return handle.read()
    except OSError as exc:
        raise ModelLoadDenied("malformed", f"cannot read {data_or_path!r}: {exc}") from exc


def _read_safetensors_header(data_or_path: PathOrBytes, header_len: int) -> bytes:
    """Read exactly the ``header_len`` JSON-header bytes that follow the 8-byte
    length prefix. Uses the in-memory slice for a buffer; for a path, reads the
    exact slice (re-opening if the header is larger than the initial probe)."""
    if isinstance(data_or_path, (bytes, bytearray)):
        return bytes(data_or_path[_HEADER_LEN_FIELD : _HEADER_LEN_FIELD + header_len])
    try:
        with open(data_or_path, "rb") as handle:
            handle.seek(_HEADER_LEN_FIELD)
            return handle.read(header_len)
    except OSError as exc:
        raise ModelLoadDenied("malformed", f"cannot read header {data_or_path!r}: {exc}") from exc


# --------------------------------------------------------------------------- #
# format gate -- pickle detection (the RCE gate) + safetensors validation       #
# --------------------------------------------------------------------------- #
def is_pickle(data_or_path: PathOrBytes) -> bool:
    """Return ``True`` if the input is (or looks like) a Python pickle.

    Pickle is the RCE format: deserializing one can import and call arbitrary code
    (the GLOBAL/REDUCE opcodes). This detector is deliberately CONSERVATIVE -- it
    over-rejects rather than under-rejects (module docstring), because a false
    "this is pickle" only costs a legitimate non-pickle, non-safetensors file (the
    safetensors positive-allow path is unaffected), whereas a false "this is not
    pickle" would be an RCE bypass.

    Detected shapes:
      * protocol 2..5 framing: first byte ``0x80`` (PROTO opcode) followed by a
        protocol-version byte in ``0x01..0x05`` -- the modern framing emitted by
        ``pickle.dumps(..., protocol>=2)`` and ``torch.save``.
      * protocol 0/1: the stream starts directly with a pickle opcode that can
        legitimately lead a pickle -- one of ``(`` ``]`` ``}`` ``c`` (mark,
        empty-list, empty-dict, GLOBAL). The GLOBAL opcode ``c`` is the literal
        arbitrary-import lever.
    An empty input is not pickle (it is simply malformed -- handled elsewhere)."""
    head = _read_prefix(data_or_path, 2)
    if not head:
        return False
    first = head[0]
    # Protocol 2..5: PROTO opcode + a sane protocol byte.
    if first == _PICKLE_PROTO_OPCODE:
        if len(head) >= 2 and 0x01 <= head[1] <= _PICKLE_MAX_PROTO:
            return True
        # A lone 0x80 with no/garbage protocol byte is still pickle-ish framing.
        return True
    # Protocol 0/1: a classic leading opcode at offset 0.
    if first in _PICKLE_LEADING_OPCODES:
        return True
    return False


def is_safetensors(data_or_path: PathOrBytes) -> bool:
    """Return ``True`` only if the input POSITIVELY validates as a safetensors
    container AND is not pickle.

    safetensors structure (validated here):
      1. at least 8 bytes exist;
      2. the first 8 bytes, read as a little-endian uint64, give ``header_len``;
      3. ``header_len`` is sane: ``> 0``, ``<= _MAX_HEADER_LEN``, and
         ``8 + header_len <= file_size`` (the declared header must fit inside the
         file -- a prefix claiming more header than exists is a forgery/corruption
         and fails);
      4. ``bytes[8 : 8 + header_len]`` parses as JSON AND that JSON is an OBJECT
         (a dict) -- the safetensors header is always a JSON object mapping tensor
         names to dtype/shape/offset metadata.
    Anything that fails any step returns ``False`` (deny-by-default). This is a
    structural validation, not a per-tensor one (module docstring). This function
    is the POSITIVE allow-path and is AUTHORITATIVE: a file that validates here is
    safetensors regardless of which byte its little-endian length prefix starts
    with. It deliberately does NOT short-circuit on ``is_pickle`` -- an earlier
    version did and false-rejected valid safetensors files whose ``header_len`` low
    byte collided with a pickle opcode (e.g. header_len 128 -> 0x80, 384 -> 0x80
    0x01). Pickle detection is applied separately in ``assert_safe_format`` for the
    NEGATIVE case (a file that is NOT valid safetensors). A crafted file that
    validates as safetensors here is safe to treat as safetensors: a safetensors
    loader reads it as pure data and never executes opcodes."""
    size = _file_size(data_or_path)
    if size < _HEADER_LEN_FIELD:
        return False
    prefix = _read_prefix(data_or_path, _HEADER_LEN_FIELD)
    if len(prefix) < _HEADER_LEN_FIELD:
        return False
    header_len = int.from_bytes(prefix, byteorder="little", signed=False)
    if header_len <= 0 or header_len > _MAX_HEADER_LEN:
        return False
    if _HEADER_LEN_FIELD + header_len > size:
        return False
    header_bytes = _read_safetensors_header(data_or_path, header_len)
    if len(header_bytes) < header_len:
        return False
    try:
        parsed = json.loads(header_bytes.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return False
    return isinstance(parsed, dict)


def assert_safe_format(path: PathOrBytes) -> None:
    """Raise ``ModelLoadDenied`` unless ``path`` is a valid safetensors file;
    return ``None`` on success. FAIL-CLOSED and pickle-FIRST.

    Order matters and is part of the contract (safetensors-positive FIRST, so a
    valid safetensors file is never misjudged by the conservative pickle sniffer):
      1. if the input POSITIVELY validates as safetensors -> return ``None`` (safe
         to DISPATCH, subject to the allow-list check). A valid safetensors
         container cannot execute code on a safetensors load, so it is the
         authoritative allow-path -- regardless of its length-prefix low byte.
      2. else if the input looks like pickle -> ``ModelLoadDenied('pickle_rejected')``
         (THE RCE gate; a non-safetensors file beginning with pickle framing/opcodes).
      3. else -> ``ModelLoadDenied('not_safetensors')`` (empty/garbage/truncated --
         deny-by-default)."""
    if is_safetensors(path):
        return
    if is_pickle(path):
        raise ModelLoadDenied("pickle_rejected", "input matches a pickle signature")
    raise ModelLoadDenied("not_safetensors", "input is not a valid safetensors container")


# --------------------------------------------------------------------------- #
# signed allow-list (reuses C1's Ed25519 KEY, not its JWS machinery)            #
# --------------------------------------------------------------------------- #
def _canonical_entry_bytes(model_id: str, sha256_hex: str, fmt: str) -> bytes:
    """The canonical byte string an allow-list signature covers:
    ``model_id\\nsha256_hex\\nformat`` (UTF-8).

    Newline-joining three fields is unambiguous here because none of the fields
    contains a newline (a model id, a 64-char lowercase hex digest, and a short
    format token). Signing the format too means an attacker cannot keep a valid
    signature while flipping the declared format from safetensors to pickle. The
    minter and the verifier MUST build these bytes identically -- this one helper
    is the single source of truth for both."""
    return "\n".join([model_id, sha256_hex, fmt]).encode("utf-8")


def sign_allowlist_entry(
    privkey: Ed25519PrivateKey,
    model_id: str,
    sha256_hex: str,
    fmt: str = DEFAULT_FORMAT,
) -> bytes:
    """Produce a DETACHED Ed25519 signature over the canonical entry bytes
    (``model_id || sha256 || format``).

    ``privkey`` is an Ed25519 private key as produced by C1's
    ``generate_signing_key`` -- the shared-KEY design: one trust root signs both
    principal tokens (C1) and model entries (here). The signature is DETACHED (the
    raw 64-byte Ed25519 signature, not a JWS) because a model-allow-list entry is a
    static integrity assertion, not a bearer token. Returns the signature bytes;
    pair them with ``model_id`` / ``sha256_hex`` / ``fmt`` to form an
    ``AllowlistEntry``."""
    return privkey.sign(_canonical_entry_bytes(model_id, sha256_hex, fmt))


@dataclass(frozen=True)
class AllowlistEntry:
    """One signed allow-list record binding a model id to an approved file hash +
    format (CONVERGENCE T8, Component 3).

    Fields:
      * ``model_id``  -- the logical model identifier the fabric asks to load.
      * ``sha256``    -- the lowercase hex SHA-256 of the APPROVED file bytes.
      * ``format``    -- the approved container format (only ``safetensors`` is
        allow-listed by this gate; the field is signed so it cannot be downgraded).
      * ``signature`` -- the detached Ed25519 signature over
        ``_canonical_entry_bytes(model_id, sha256, format)``, produced by
        ``sign_allowlist_entry`` with the trust-root private key.

    Frozen (immutable) so an entry cannot be mutated after construction -- the
    bytes that were signed are the bytes that are checked. ``as_dict`` emits the
    spec's ``{model_id, sha256, format, signature}`` mapping (signature kept as raw
    bytes; a transport layer may hex/base64 it)."""

    model_id: str
    sha256: str
    format: str
    signature: bytes

    def canonical_bytes(self) -> bytes:
        """The exact bytes this entry's signature covers (delegates to the shared
        canonicalizer so entry + minter never drift)."""
        return _canonical_entry_bytes(self.model_id, self.sha256, self.format)

    def as_dict(self) -> dict[str, Any]:
        """The ``{model_id, sha256, format, signature}`` mapping (spec shape)."""
        return {
            "model_id": self.model_id,
            "sha256": self.sha256,
            "format": self.format,
            "signature": self.signature,
        }


def make_allowlist_entry(
    privkey: Ed25519PrivateKey,
    model_id: str,
    sha256_hex: str,
    fmt: str = DEFAULT_FORMAT,
) -> AllowlistEntry:
    """Convenience: sign + box a model into an ``AllowlistEntry`` in one call.
    Equivalent to constructing ``AllowlistEntry`` with the signature from
    ``sign_allowlist_entry``."""
    sig = sign_allowlist_entry(privkey, model_id, sha256_hex, fmt)
    return AllowlistEntry(model_id=model_id, sha256=sha256_hex, format=fmt, signature=sig)


def _coerce_entry(entry: Union[AllowlistEntry, Mapping[str, Any]]) -> AllowlistEntry:
    """Accept either an ``AllowlistEntry`` or a plain ``{model_id, sha256, format,
    signature}`` mapping and normalize to an ``AllowlistEntry``.

    A mapping missing any required field, or carrying a non-bytes signature, raises
    ``ModelLoadDenied('malformed')`` -- a structurally broken entry is a clean
    denial, never a crash."""
    if isinstance(entry, AllowlistEntry):
        return entry
    if not isinstance(entry, Mapping):
        raise ModelLoadDenied("malformed", f"entry is not a mapping: {type(entry).__name__}")
    try:
        model_id = entry["model_id"]
        sha256 = entry["sha256"]
        fmt = entry["format"]
        signature = entry["signature"]
    except KeyError as exc:
        raise ModelLoadDenied("malformed", f"entry missing field {exc}") from exc
    if not isinstance(signature, (bytes, bytearray)):
        raise ModelLoadDenied(
            "malformed", f"entry signature must be bytes, got {type(signature).__name__}"
        )
    return AllowlistEntry(
        model_id=str(model_id),
        sha256=str(sha256),
        format=str(fmt),
        signature=bytes(signature),
    )


def _sha256_hex(data_or_path: PathOrBytes) -> str:
    """Lowercase hex SHA-256 of the FULL input. Streams a path in chunks (so a
    multi-GB weights file is not held in memory); hashes a buffer directly. A
    path that cannot be read raises ``ModelLoadDenied('malformed')``."""
    digest = hashlib.sha256()
    if isinstance(data_or_path, (bytes, bytearray)):
        digest.update(data_or_path)
        return digest.hexdigest()
    try:
        with open(data_or_path, "rb") as handle:
            for chunk in iter(lambda: handle.read(1 << 20), b""):
                digest.update(chunk)
    except OSError as exc:
        raise ModelLoadDenied("malformed", f"cannot hash {data_or_path!r}: {exc}") from exc
    return digest.hexdigest()


def make_model_gate(
    pubkey: Ed25519PublicKey,
    entries: Iterable[Union[AllowlistEntry, Mapping[str, Any]]],
) -> Callable[[PathOrBytes, str], AllowlistEntry]:
    """Build the framework-side model-load gate (CONVERGENCE T8, Component 3).

    GATE CONTRACT (so N07 can re-run + review):
      * Build:  ``gate = make_model_gate(pubkey, [entry, ...])`` where ``pubkey``
        is the trust-root Ed25519 public key (the public half of the key that
        signed the entries -- C1's ``public_key_of`` of the signing key) and
        ``entries`` is any iterable of ``AllowlistEntry`` (or
        ``{model_id, sha256, format, signature}`` mappings).
      * Call:   ``gate(path, model_id) -> AllowlistEntry``.
      * On ALLOW: returns the VALIDATED ``AllowlistEntry`` (the caller may proceed
        to dispatch the load).
      * On ANY failure: RAISES ``ModelLoadDenied`` with a ``.reason``. The gate
        NEVER returns on failure and NEVER silently downgrades. FAIL-CLOSED.

    Checks, IN ORDER (each fail-closed; later checks never run if an earlier one
    fails):
      1. ``assert_safe_format(path)`` -- reject pickle (``pickle_rejected``, THE
         RCE gate) or a non-safetensors file (``not_safetensors``) BEFORE any hash
         or signature work. Nothing about the allow-list is consulted for an unsafe
         FORMAT: an attacker cannot get a pickle dispatched by also forging an
         entry, because the format gate fires first.
      2. resolve the entry for ``model_id``. No entry -> ``unknown_model``.
      3. verify the entry's detached Ed25519 signature over its canonical bytes
         with ``pubkey``. A forged/absent/wrong-key signature ->
         ``bad_signature``. The hash in the entry is NOT trusted until this passes.
      4. compute the file's SHA-256 and compare to the entry's signed hash. A
         tampered model (bytes changed after signing) -> ``hash_mismatch``. An
         entry whose model_id matches but whose signed hash matches no on-disk
         bytes is caught here.
    Returns the entry only if all four pass.

    Design notes:
      * The entry is indexed by ``model_id`` at build time, so the gate is a dict
        lookup plus one signature verify + one hash per call. Each entry's
        signature is verified at CALL time (not build time) so the trust decision
        is made against the file actually presented, and so a build-time list can
        carry not-yet-presented models cheaply. (Verifying at call time also means
        a malformed entry only fails the model_id that references it.)
      * Signature verify is step 3 and the hash compare is step 4 ON PURPOSE: the
        signed hash must not be trusted (step 4) until the signature that vouches
        for it is proven authentic (step 3). Reversing them would let a forged
        entry's hash drive the comparison.

    HONEST CAVEAT (framework vs fabric): see the module docstring. This gate
    decides "safe to DISPATCH"; the fabric MUST independently enforce
    safetensors-only + the allow-list at its deserialization point. A fabric that
    pickle-loads arriving bytes bypasses this gate entirely."""
    index: dict[str, AllowlistEntry] = {}
    for raw in entries:
        coerced = _coerce_entry(raw)
        index[coerced.model_id] = coerced

    def authorize_model_load(path: PathOrBytes, model_id: str) -> AllowlistEntry:
        # Step 0 -- read the input ONCE. Every check below validates this SAME
        # snapshot (TOCTOU close -- see _read_all_bytes docstring): previously
        # the format gate and the hash check each independently re-opened
        # ``path`` by name, leaving a window where the on-disk file could be
        # swapped between opens so that format-validation and hashing ran
        # against different bytes. Passing the resulting ``bytes`` into
        # ``assert_safe_format`` / ``_sha256_hex`` below routes them through
        # their existing in-memory-buffer path (no new re-open of ``path``).
        data = _read_all_bytes(path)

        # Step 1 -- FORMAT GATE (pickle-first, before any hash/signature work).
        assert_safe_format(data)

        # Step 2 -- resolve the allow-list entry for this model_id.
        entry = index.get(model_id)
        if entry is None:
            raise ModelLoadDenied("unknown_model", f"model_id={model_id!r} not in allow-list")

        # Step 3 -- verify the entry's signature BEFORE trusting its hash. A forged
        # or wrong-key signature is rejected here; only a proven-authentic entry
        # advances to the hash compare.
        try:
            pubkey.verify(entry.signature, entry.canonical_bytes())
        except InvalidSignature as exc:
            raise ModelLoadDenied(
                "bad_signature", f"allow-list entry for {model_id!r} failed Ed25519 verify"
            ) from exc

        # Step 4 -- the SAME bytes' hash must equal the SIGNED hash. This catches
        # a model whose bytes were swapped after the entry was signed (still a
        # valid safetensors file, still a signed entry, but the WRONG bytes) --
        # and, per Step 0, is computed from the identical snapshot the format
        # gate already validated, not from a fresh re-open of ``path``.
        actual = _sha256_hex(data)
        if actual != entry.sha256:
            raise ModelLoadDenied(
                "hash_mismatch",
                f"model_id={model_id!r} file sha256={actual} != signed {entry.sha256}",
            )

        return entry

    return authorize_model_load

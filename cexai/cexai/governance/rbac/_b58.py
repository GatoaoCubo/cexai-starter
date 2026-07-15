"""base58btc (Bitcoin alphabet) encode/decode -- the did:key multibase ``z`` body.

Tiny, dependency-free, ASCII-only. A ``did:key`` is ``did:key:z<base58btc(
multicodec || raw_key)>``; the ``z`` multibase prefix denotes base58btc (the
Bitcoin alphabet, NOT base58check -- there is no checksum). Neither the stdlib nor
``cryptography``/PyJWT ships a base58 codec, so this is a self-contained, tested
implementation. Split out of ``principal_signing`` so it is unit-testable on its
own and so its provenance (Bitcoin/IPFS alphabet) is explicit.

Reference: the Bitcoin base58 alphabet (omits 0, O, I, l to avoid visual
ambiguity); leading zero BYTES map to leading ``1`` characters.

absorbs: convergence/t8-trust-model (Component 1 -- principal identity)
"""

from __future__ import annotations

__all__ = ["b58encode", "b58decode", "BASE58_ALPHABET"]

# The Bitcoin / IPFS base58 alphabet (RFC draft-msporny-base58, multibase 'z').
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_BASE = len(BASE58_ALPHABET)
_INDEX = {ch: i for i, ch in enumerate(BASE58_ALPHABET)}


def b58encode(data: bytes) -> str:
    """Encode ``data`` (bytes) as a base58btc string (Bitcoin alphabet).

    Leading zero bytes become leading ``1`` characters (so the multicodec prefix
    is preserved on decode). An empty input encodes to an empty string."""
    # Count leading zero bytes -> they each become a leading '1'.
    n_zeros = 0
    for byte in data:
        if byte == 0:
            n_zeros += 1
        else:
            break

    # Big-endian integer -> base58 digits.
    num = int.from_bytes(data, byteorder="big")
    digits: list[str] = []
    while num > 0:
        num, rem = divmod(num, _BASE)
        digits.append(BASE58_ALPHABET[rem])
    # The leading zero bytes (stripped by int conversion) are restored as '1's.
    digits.append("1" * n_zeros)
    return "".join(reversed(digits))


def b58decode(text: str) -> bytes:
    """Decode a base58btc string back to bytes. Raises ``ValueError`` on a char
    outside the alphabet. Leading ``1`` characters restore leading zero bytes."""
    num = 0
    for ch in text:
        try:
            num = num * _BASE + _INDEX[ch]
        except KeyError as exc:
            raise ValueError(f"invalid base58 character: {ch!r}") from exc

    # Leading '1's are leading zero bytes.
    n_zeros = 0
    for ch in text:
        if ch == "1":
            n_zeros += 1
        else:
            break

    body = num.to_bytes((num.bit_length() + 7) // 8, byteorder="big") if num else b""
    return b"\x00" * n_zeros + body

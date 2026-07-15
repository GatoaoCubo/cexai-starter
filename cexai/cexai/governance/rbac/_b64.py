"""base64url (unpadded) helpers -- the JWK ``x`` encoding (RFC 7515 Sec. 2).

Tiny, dependency-free, ASCII-only. JOSE uses base64url WITHOUT ``=`` padding for
the JWK ``x`` member and for JWS segments; the stdlib ``base64.urlsafe_b64encode``
keeps the padding, so these wrappers strip/restore it. Split out of
``principal_signing`` so the encoding is unit-testable in isolation.

STRICT DECODE (audit R9): ``b64url_decode`` is a SECURITY boundary -- it decodes the
signature + payload segments of a DSSE envelope (knowledge_bom / cyclonedx_bom) and
the C4 status_list. A malleable decoder (one that silently accepts standard-base64
``+``/``/``, ignores junk, or tolerates an impossible ``len % 4 == 1``) lets two
distinct input strings map to the same bytes -- a signature-malleability / canonical-
form hazard. This decoder therefore REJECTS any non-urlsafe-alphabet character,
rejects ``len % 4 == 1``, validates strictly, and asserts a CANONICAL round-trip
(decode -> re-encode equals the input minus padding) so only the one canonical
encoding of a given byte string is accepted.

absorbs: convergence/t8-trust-model (Component 1 -- principal identity)
"""

from __future__ import annotations

import base64
import binascii

__all__ = ["b64url_encode", "b64url_decode"]

# The base64url alphabet (RFC 4648 Sec. 5): A-Z a-z 0-9 plus '-' and '_'. NO '+'
# or '/' (those are STANDARD base64) and NO whitespace. A strict decoder accepts
# ONLY these characters (padding '=' is added by us, never present in the input).
_B64URL_ALPHABET = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
)


def b64url_encode(data: bytes) -> str:
    """Encode ``data`` as unpadded base64url (the JOSE / JWK ``x`` form)."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64url_decode(text: str) -> bytes:
    """Decode unpadded base64url back to bytes -- STRICT (audit R9).

    Rejects (raising ``ValueError``) any input that is not the ONE canonical unpadded
    base64url encoding of some byte string:
      * a non-``str`` input;
      * any character outside the base64url alphabet -- in particular standard-base64
        ``+`` / ``/`` (malleability vector), whitespace, or stray ``=`` padding;
      * a length ``% 4 == 1`` (no valid base64 group has this remainder);
      * bytes that fail strict base64 validation after re-padding;
      * a non-canonical encoding -- one whose trailing bits are non-zero, detected by
        re-encoding the decoded bytes and requiring equality with the input. This
        closes the classic "two strings decode to the same bytes" malleability."""
    if not isinstance(text, str):
        raise ValueError("b64url_decode: input must be a str")
    # Reject any character not in the urlsafe alphabet (catches +,/, whitespace, =).
    illegal = set(text) - _B64URL_ALPHABET
    if illegal:
        raise ValueError(
            "b64url_decode: non-urlsafe-base64 character(s): "
            + repr("".join(sorted(illegal)))
        )
    # len % 4 == 1 can never be a valid base64 group remainder.
    if len(text) % 4 == 1:
        raise ValueError("b64url_decode: invalid length (len % 4 == 1)")
    padding = "=" * (-len(text) % 4)
    try:
        decoded = base64.urlsafe_b64decode(text + padding)
    except (binascii.Error, ValueError) as exc:
        raise ValueError(f"b64url_decode: invalid base64url: {exc}") from exc
    # CANONICAL round-trip: only the unique canonical encoding is accepted. A string
    # with non-zero trailing (unused) bits decodes but re-encodes to a DIFFERENT
    # string -- reject it as non-canonical (malleable).
    if b64url_encode(decoded) != text:
        raise ValueError("b64url_decode: non-canonical base64url encoding")
    return decoded

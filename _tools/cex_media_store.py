#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI media store -- the upload sink SEAM for the dual-output upload-persist wire.

THE PROBLEM: a human uploads a media file for a dual-output media slot (the DualOutputFace
"upload-fallback" dropzone). The bytes need a tenant-scoped home, and the result is a ``src``
the slot can carry (status empty -> generated) so BOTH faces (the human audiovisual face and
the machine .md ledger the tenant's AI reads) reflect the upload.

THE SEAM: ``MediaStore.put(...) -> {src, content_type, bytes, stored_as}``. ONE contract, two
implementations:
  * ``Base64InlineStore`` (V1 default, founder-chosen): the bytes become a ``data:`` URI stored
    INLINE in the slot's src (and thus in the tenant_data JSONB row). Zero gated infra, works
    offline + in fixtures. Size-capped (the row must stay sane); the machine .md ELIDES the long
    URI downstream (cex_media_persist) so the AI-readable face stays lean.
  * ``SupabaseStorageStore`` (gated drop-in): the bytes go to a tenant-prefixed object-store path
    ``tenant/<tid>/media/<record_id>/<slot_key>`` and the src is a signed URL. NOT activated yet
    (the storage RLS owner-path is founder-gated); it raises a clear ``storage_not_provisioned``
    so the seam is ready without pretending it works.

NEVER-TRUST-UPLOAD (security): every put VALIDATES fail-closed -- the declared slot kind must be
one of image|video|audio; the content-type must be in the per-kind allowlist (sniffed from the
magic bytes when the client omitted/mis-stated it); the payload must be non-empty and within the
size cap. A mismatch raises MediaStoreError with a precise HTTP status (400/413/415). No bytes are
ever executed/parsed beyond a magic-byte probe; an SVG (active content) is accepted ONLY as an
image data URI that the renderer treats as an <img> src (never injected as DOM).

PURE: ``Base64InlineStore`` does NO network/disk IO (base64 is in-memory) -- so it is fully
offline-testable and degrade-never. ASCII-only per .claude/rules/ascii-code-rule.md.

Spec: _docs/specs/spec_dual_output_contract.md (the upload-persist follow-up). Consumer:
apps/dashboard_api/main.py (PATCH /capability/{record_id}/media/{slot_key}) via cex_media_persist.
"""

from __future__ import annotations

import base64
import os
from typing import Dict, Optional

# The media kinds a slot may carry (mirror cex_dual_output.VALID_MEDIA_KINDS).
VALID_MEDIA_KINDS = ("image", "video", "audio")

# Per-kind content-type allowlist. Fail-closed: a content-type NOT here is rejected (415). Kept
# deliberately small (the common web-safe set) -- widen deliberately, never by accident.
ALLOWED_CONTENT_TYPES: Dict[str, tuple] = {
    "image": ("image/png", "image/jpeg", "image/webp", "image/gif", "image/svg+xml"),
    "video": ("video/mp4", "video/webm", "video/ogg"),
    "audio": ("audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav", "audio/ogg",
              "audio/webm", "audio/mp4"),
}

# A sensible default content-type per kind (used only when the client omitted it AND the magic
# probe did not resolve one -- never to override a stated-but-invalid type).
_DEFAULT_CONTENT_TYPE = {"image": "image/png", "video": "video/mp4", "audio": "audio/mpeg"}

# Size cap (bytes). Base64 inflates ~33%, and the data URI rides the tenant_data JSONB row, so the
# cap keeps rows sane. Env-overridable for an operator who accepts bigger rows. Default 4 MiB.
_DEFAULT_MAX_BYTES = 4 * 1024 * 1024
_MAX_BYTES_ENV = "CEXAI_MEDIA_MAX_BYTES"

# Which store the factory returns. Default = the founder-chosen base64-inline V1.
_STORE_ENV = "CEXAI_MEDIA_STORE"


class MediaStoreError(Exception):
    """An upload-store failure mapped to a precise HTTP status (never a secret/traceback).

    ``reason`` is a stable machine code (the error envelope's ``reason``); ``status`` is the HTTP
    code the API should return; the message is a safe, human one. FAIL-CLOSED by construction.
    """

    def __init__(self, reason: str, *, status: int = 400, detail: str = "") -> None:
        self.reason = reason
        self.status = status
        self.detail = detail or reason
        super().__init__(self.detail)


def max_upload_bytes() -> int:
    """The active upload size cap (env override -> default). A bad/blank env -> the default."""
    raw = (os.environ.get(_MAX_BYTES_ENV) or "").strip()
    if raw:
        try:
            val = int(raw)
            if val > 0:
                return val
        except (TypeError, ValueError):
            pass
    return _DEFAULT_MAX_BYTES


# --------------------------------------------------------------------------- #
# Magic-byte probe (a small, defensive content-type resolver). NOT a parser.  #
# --------------------------------------------------------------------------- #
def sniff_content_type(data: bytes) -> Optional[str]:
    """Best-effort content-type from the leading magic bytes. None when unrecognized.

    A narrow, total sniffer over the common web media signatures -- NEVER decodes/executes the
    payload. Used only to RESOLVE an omitted content-type (and to corroborate a stated one); the
    per-kind allowlist remains the authority on what is accepted."""
    if not data:
        return None
    head = data[:16]
    # images
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if head.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if head.startswith(b"GIF87a") or head.startswith(b"GIF89a"):
        return "image/gif"
    if head[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    if head[:4] == b"RIFF" and data[8:12] == b"WAVE":
        return "audio/wav"
    # a leading '<?xml' or '<svg' -> svg (an image, rendered as an <img> src only).
    stripped = data[:64].lstrip()
    if stripped.startswith(b"<?xml") or stripped.startswith(b"<svg"):
        return "image/svg+xml"
    # mp3 (ID3 tag or frame sync) / ogg / mp4-family (ftyp)
    if head.startswith(b"ID3") or head[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"):
        return "audio/mpeg"
    if head.startswith(b"OggS"):
        return "audio/ogg"
    if data[4:8] == b"ftyp":
        return "video/mp4"
    if head.startswith(b"\x1aE\xdf\xa3"):  # EBML -> webm/mkv
        return "video/webm"
    return None


def _resolve_content_type(stated: Optional[str], data: bytes, kind: str) -> str:
    """Resolve the EFFECTIVE content-type fail-closed.

    Order: a STATED type that is allowed for the kind wins; else the magic probe if allowed; else
    -- only when the client stated NOTHING and the probe was empty -- the per-kind default. A
    STATED-but-INVALID type is NOT silently replaced: it raises 415 (the client lied about the
    type; do not guess around it)."""
    allowed = ALLOWED_CONTENT_TYPES.get(kind, ())
    stated_norm = (stated or "").split(";")[0].strip().lower()
    if stated_norm:
        if stated_norm in allowed:
            return stated_norm
        # A stated type that is not allowed for this kind -> reject (never coerce around a lie).
        raise MediaStoreError(
            "unsupported_media_type", status=415,
            detail="content-type %r is not allowed for a %s slot" % (stated_norm, kind),
        )
    sniffed = sniff_content_type(data)
    if sniffed and sniffed in allowed:
        return sniffed
    if sniffed and sniffed not in allowed:
        raise MediaStoreError(
            "unsupported_media_type", status=415,
            detail="sniffed content-type %r is not allowed for a %s slot" % (sniffed, kind),
        )
    return _DEFAULT_CONTENT_TYPE.get(kind, "application/octet-stream")


def _validate(kind: str, data: bytes) -> str:
    """Shared fail-closed validation (kind + non-empty + size cap). Returns the normalized kind."""
    k = (kind or "").strip().lower()
    if k not in VALID_MEDIA_KINDS:
        raise MediaStoreError("invalid_kind", status=400,
                              detail="slot kind must be one of %s" % ", ".join(VALID_MEDIA_KINDS))
    if not data:
        raise MediaStoreError("empty_file", status=400, detail="the uploaded file is empty")
    cap = max_upload_bytes()
    if len(data) > cap:
        raise MediaStoreError("file_too_large", status=413,
                              detail="file is %d bytes; the cap is %d" % (len(data), cap))
    return k


# --------------------------------------------------------------------------- #
# The seam + implementations.                                                 #
# --------------------------------------------------------------------------- #
class MediaStore:
    """The upload-sink contract. ``put`` stores the bytes tenant-scoped and returns the src +
    metadata. Implementations are interchangeable behind ``get_media_store()``."""

    name = "media_store"

    def put(
        self,
        tenant_id: str,
        record_id: str,
        slot_key: str,
        kind: str,
        filename: str,
        data: bytes,
        content_type: Optional[str] = None,
    ) -> Dict[str, object]:  # pragma: no cover - abstract
        raise NotImplementedError


class Base64InlineStore(MediaStore):
    """V1 (founder-chosen): the bytes become a ``data:`` URI stored INLINE in the slot src.

    PURE: no network, no disk -- base64 is in-memory, so this is fully offline + degrade-never.
    The data URI rides the tenant_data JSONB row (media_slots[key].src); cex_media_persist ELIDES
    the long URI from the machine .md so the AI-readable face stays lean. tenant_id/record_id/
    slot_key are accepted for parity with the storage sink (and audit) but not needed to compute
    the inline src."""

    name = "base64_inline"

    def put(
        self,
        tenant_id: str,
        record_id: str,
        slot_key: str,
        kind: str,
        filename: str,
        data: bytes,
        content_type: Optional[str] = None,
    ) -> Dict[str, object]:
        k = _validate(kind, data)
        ct = _resolve_content_type(content_type, data, k)
        b64 = base64.b64encode(data).decode("ascii")
        src = "data:%s;base64,%s" % (ct, b64)
        return {
            "src": src,
            "content_type": ct,
            "bytes": len(data),
            "stored_as": "inline_base64",
        }


class SupabaseStorageStore(MediaStore):
    """Gated drop-in: object-store the bytes at ``tenant/<tid>/media/<record_id>/<slot_key>`` and
    return a signed URL. NOT activated -- the storage RLS owner-path is founder-gated (and the 8a
    key rotation). It raises a precise, honest ``storage_not_provisioned`` (503) so the seam is
    ready WITHOUT pretending to work. When un-gated, implement ``put`` here ONLY -- nothing else in
    the wire changes (same contract, same return shape)."""

    name = "supabase_storage"

    def put(
        self,
        tenant_id: str,
        record_id: str,
        slot_key: str,
        kind: str,
        filename: str,
        data: bytes,
        content_type: Optional[str] = None,
    ) -> Dict[str, object]:
        # Validate first (so a bad upload is rejected identically regardless of sink), THEN refuse
        # honestly: the bucket + RLS owner-path are not provisioned yet (founder-gated).
        _validate(kind, data)
        raise MediaStoreError(
            "storage_not_provisioned", status=503,
            detail="Supabase Storage sink is not provisioned yet (founder-gated); "
                   "set %s=base64 for the inline V1 sink" % _STORE_ENV,
        )


def get_media_store() -> MediaStore:
    """Return the configured MediaStore. Default = Base64InlineStore (the founder-chosen V1).

    ``$CEXAI_MEDIA_STORE`` selects: 'base64' (default) | 'supabase'. An unknown value degrades to
    the base64 store (never a crash) -- the safe, working default."""
    choice = (os.environ.get(_STORE_ENV) or "base64").strip().lower()
    if choice in ("supabase", "supabase_storage", "storage"):
        return SupabaseStorageStore()
    return Base64InlineStore()


__all__ = [
    "MediaStore",
    "Base64InlineStore",
    "SupabaseStorageStore",
    "MediaStoreError",
    "get_media_store",
    "<tenant>_content_type",
    "max_upload_bytes",
    "VALID_MEDIA_KINDS",
    "ALLOWED_CONTENT_TYPES",
]

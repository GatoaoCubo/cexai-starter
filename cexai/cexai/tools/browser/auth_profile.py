"""AuthProfileStore -- encrypted-at-rest browser auth-profile persistence (15 US P1 / FR-002 / SC-005).

Persists and reloads a browser ``AuthProfile``'s auth-state (cookies / tokens) so a
session resumes authenticated without re-login (US P1). The auth-state is ENCRYPTED
at rest via an injected ``Cipher`` + key: a leaked ``auth_state/`` directory without
the key cannot be replayed against the target site (SC-005). Two files per profile
under ``{root}/auth_state/``:

  * ``{name}.enc``  -- the ciphertext of ``MAGIC + json(auth_state)``. The integrity
                       marker lets ``load`` reject a wrong-key / tampered blob
                       deterministically (a wrong key -> marker mismatch -> refuse,
                       rather than handing back a corrupt-but-accepted session).
  * ``{name}.json`` -- non-secret profile metadata (name, encrypted_at_rest marker,
                       max_age_days freshness bound, created_at), so the profile can
                       be reconstructed without decrypting the secret.

Gating-Wrath strictness: ``persist`` REFUSES a profile explicitly marked
``encrypted_at_rest=False`` -- the encrypted store never writes a replayable
plaintext secret. The ``Cipher`` is injected so tests run offline with a fake
key-dependent cipher; production wires a real authenticated cipher (e.g. Fernet),
lazily, with NO new package dependency added by this freeze-respecting lane.

absorbs: 15_auto-browser
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from cexai.tools._shared.types import AuthProfile

__all__ = ["Cipher", "AuthProfileStore"]

# Integrity marker prepended to the plaintext before encryption. On load, the
# decrypted bytes MUST start with this; a wrong key (or tampering) breaks the
# prefix, so a leaked blob cannot be silently replayed (SC-005).
_MAGIC = b"CEXAI-AUTHSTATE-V1\n"


def _now_iso() -> str:
    """Current UTC instant (tz-aware) as ISO-8601 -- the profile creation stamp."""
    return datetime.now(timezone.utc).isoformat()


@runtime_checkable
class Cipher(Protocol):
    """The symmetric-cipher seam (FR-002). ``encrypt`` / ``decrypt`` are inverse
    over ``(data, key)``. Injected so tests use a fake key-dependent cipher offline;
    production wires a real authenticated cipher. This lane never imports a crypto
    package at module load -- the concrete cipher rides behind this seam."""

    def encrypt(self, data: bytes, key: bytes) -> bytes:
        """Return the ciphertext of ``data`` under ``key``."""
        ...

    def decrypt(self, token: bytes, key: bytes) -> bytes:
        """Return the plaintext of ``token`` under ``key`` (inverse of ``encrypt``)."""
        ...


class AuthProfileStore:
    """Encrypted-at-rest auth-profile store rooted at ``root``. Inject the
    ``cipher`` + ``key`` used to encrypt the auth-state; the key must be non-empty
    (Gating-Wrath: an empty key is not encryption)."""

    def __init__(self, *, root: Path | str, cipher: Cipher, key: bytes) -> None:
        self._root = Path(root)
        self._cipher = cipher
        self._key = bytes(key)
        if not self._key:
            raise ValueError("auth profile encryption key must be non-empty")

    def persist(self, profile: AuthProfile, auth_state: Mapping[str, Any]) -> Path:
        """Encrypt ``auth_state`` under the store key and write it (+ profile
        metadata) under ``{root}/auth_state/``. Refuses a profile marked
        ``encrypted_at_rest=False`` (SC-005). Returns the ciphertext path."""
        if not profile.encrypted_at_rest:
            raise ValueError(
                f"refusing to persist auth profile {profile.name!r} marked "
                "encrypted_at_rest=False: the encrypted store never writes a "
                "replayable plaintext secret (SC-005)"
            )
        auth_state_dir = self._root / "auth_state"
        auth_state_dir.mkdir(parents=True, exist_ok=True)
        plaintext = _MAGIC + json.dumps(dict(auth_state), sort_keys=True).encode("utf-8")
        token = self._cipher.encrypt(plaintext, self._key)
        enc_path = auth_state_dir / f"{profile.name}.enc"
        enc_path.write_bytes(token)
        meta = {
            "name": profile.name,
            "encrypted_at_rest": True,
            "max_age_days": profile.max_age_days,
            "created_at": profile.created_at if profile.created_at is not None else _now_iso(),
        }
        (auth_state_dir / f"{profile.name}.json").write_text(
            json.dumps(meta, indent=2) + "\n", encoding="utf-8"
        )
        return enc_path

    def load(self, name: str, *, key: bytes | None = None) -> dict[str, Any]:
        """Decrypt and return the auth-state for ``name`` (using ``key`` or the store
        key). Raises ``ValueError`` if the integrity marker is absent -- i.e. a wrong
        key or tampered blob, so a leaked ``auth_state/`` cannot be replayed (SC-005)."""
        token = (self._root / "auth_state" / f"{name}.enc").read_bytes()
        plaintext = self._cipher.decrypt(token, bytes(key) if key is not None else self._key)
        if not plaintext.startswith(_MAGIC):
            raise ValueError(
                f"auth state for {name!r} failed its integrity check -- wrong "
                "decryption key or tampered ciphertext; cannot replay"
            )
        payload = plaintext[len(_MAGIC):]
        try:
            return json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"auth state for {name!r} could not be decoded: {exc}") from exc

    def read_profile(self, name: str) -> AuthProfile:
        """Reconstruct the ``AuthProfile`` from its (non-secret) metadata file -- no
        decryption of the auth-state required."""
        meta = json.loads(
            (self._root / "auth_state" / f"{name}.json").read_text(encoding="utf-8")
        )
        return AuthProfile(
            name=meta["name"],
            encrypted_at_rest=meta.get("encrypted_at_rest", True),
            max_age_days=meta.get("max_age_days", 7),
            created_at=meta.get("created_at"),
        )

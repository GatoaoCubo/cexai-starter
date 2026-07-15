# -*- coding: ascii -*-
"""cex_sdk.credentials.tenant_store -- the BYOK TenantCredentialStore contract
(mission BYOK_0713, lane vault-backend; decision D5 in
.cex/runtime/decisions/decision_manifest_wave2_0713.yaml).

WHY THIS LOCATION (canonical-home justification, per the task contract):
  * ``cexai/`` is explicitly extraction-bound (cexai/pyproject.toml) and its own
    adapter module (cexai/cexai/governance/data/adapter.py) documents in its own
    docstring that it "MUST NOT import repo-root _tools" -- EnvRefStore below reads
    the tenant secrets vault via ``_tools.cex_tenant_paths``, so it cannot live in
    ``cexai`` without breaking that boundary.
  * ``cex_sdk`` already reaches into ``_tools`` this exact way, guarded, at need
    (precedent: ``cex_sdk/models/chat.py`` inserts ``_tools`` onto ``sys.path`` and
    lazily imports ``cex_model_resolver``; ``cex_sdk/pipeline.py`` does the same for
    the run_capability executor). ``cex_sdk.credentials`` sits next to
    ``cex_sdk.models`` (the provider dispatch this store's resolved key feeds) and
    ``cex_sdk.agent`` (the Credential consumer) -- the natural SDK-layer home for a
    reusable, independently-testable contract, as opposed to ``apps/dashboard_api``
    (an app-layer glue module that CONSUMES this contract, not the right place to
    OWN it) or ``_tools`` itself (a flat scripts dir, not a package other code
    imports as a library).

CONTRACT (the task brief, verbatim): a ``TenantCredentialStore`` with
``get(tenant_id, provider) -> Optional[str]`` and ``set(tenant_id, provider,
key_ref)``. ``key_ref`` is a REFERENCE, never a raw secret value -- for
``EnvRefStore`` it is the NAME of an env var to resolve inside the tenant's local
vault; a future concrete store may treat it as an encrypted-blob pointer or a row
id. ``get`` returns the RESOLVED secret VALUE (or None); callers must still never
log/print it (secret discipline: name + presence + len only, NEVER the value).

TWO implementations ship today:
  * EnvRefStore   -- dev/default. Per (tenant, provider), resolves an env-ref name
                     (an explicit ``set()`` override, else a built-in per-provider
                     convention) against the tenant's LOCAL secrets vault via
                     ``cex_tenant_paths.load_tenant_secrets`` -- the SAME loader
                     ``apps.dashboard_api.deps._try_tenant_secret_key`` already
                     uses (re-verified against disk 2026-07-13: that loader reads
                     ``.cex/tenants/<tid>/secrets/.env``; every tenant on this repo
                     today has only a ``.env.example`` template -- zero real
                     secrets are read by this module in this state). NEVER caches
                     a resolved value across calls; NEVER logs; degrades to None
                     on ANY read failure (missing file, broken loader, bad tenant
                     id) rather than raising.
  * SupabaseStore -- PRODUCTION STUB. Every method raises NotImplementedError
                     immediately. # FOUNDER-GATED: RLS table + encryption-at-rest.
                     Not wired, not faked, not partially implemented.

ASCII-only per .claude/rules/ascii-code-rule.md. No network, no real secret value
is ever hardcoded in this file.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, Optional, Protocol, Tuple, runtime_checkable

__all__ = [
    "TenantCredentialStore",
    "EnvRefStore",
    "SupabaseStore",
    "default_tenant_credential_store",
]


# --------------------------------------------------------------------------- #
# TenantCredentialStore (the contract) -- mirrors the house Protocol style
# already used by _tools/cex_run_capability.py's DbWriter/DbReader seams.
# --------------------------------------------------------------------------- #
@runtime_checkable
class TenantCredentialStore(Protocol):
    """The BYOK backend-seam contract: resolve/register a tenant's OWN
    per-provider credential, independent of HOW it is actually stored.

    ``get`` returns the RESOLVED secret VALUE (or None -- 'no key registered for
    this tenant+provider', which is a normal, expected outcome, NOT an error).
    ``set`` registers a ``key_ref`` (a REFERENCE, never a raw value) for a
    (tenant_id, provider) pair, overriding the store's default resolution for
    that pair only.
    """

    def get(self, tenant_id: str, provider: str) -> Optional[str]:
        """Resolve the tenant's OWN key for ``provider``, or None if absent.

        Degrade-never for the "no key" case: returns None, never raises. Only a
        genuinely UNIMPLEMENTED store (SupabaseStore) raises, and only because
        the operation itself is not built -- never because a key was missing."""
        ...

    def set(self, tenant_id: str, provider: str, key_ref: str) -> None:
        """Register ``key_ref`` (a REFERENCE, not a raw secret value) for
        (tenant_id, provider). Overrides the store's default naming convention
        for THIS tenant+provider pair only; does not affect any other pair."""
        ...


# --------------------------------------------------------------------------- #
# EnvRefStore (dev/default implementation).
# --------------------------------------------------------------------------- #

# The built-in per-provider env-ref convention -- INTENTIONALLY duplicated (not
# imported) from _tools/cex_run_capability.py's _provider_key_env table. This
# module must not hard-import _tools at module load (only lazily, guarded,
# inside a method body -- see _load_vault below), so the tiny 3-entry table is
# copied rather than coupled. Keep in sync by hand if a new provider is added
# to _provider_key_env; a provider missing here still works via an explicit
# EnvRefStore.set(tenant_id, provider, key_ref) override.
_DEFAULT_PROVIDER_ENV_NAMES: Dict[str, str] = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "openwebui": "OPENWEBUI_API_KEY",
    # "ollama" deliberately absent: the local daemon takes no API key (matches
    # _provider_key_env's own ollama/unknown -> None branch).
}


def _ensure_tools_on_path() -> None:
    """Put the repo-root ``_tools`` dir on sys.path (idempotent), mirroring the
    exact pattern ``cex_sdk/models/chat.py`` already uses for this same reach."""
    tools_dir = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_tools")
    )
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)


class EnvRefStore:
    """Dev/default TenantCredentialStore: resolves an env-ref name per
    (tenant, provider) against the tenant's LOCAL secrets vault.

    The ``_refs`` registry (populated by ``set``) is PROCESS-LOCAL, in-memory
    only -- it is NOT persisted to disk (persisting an override mapping is a
    production-wiring concern, out of this backend-seam lane's scope). A fresh
    process starts with only the built-in ``_DEFAULT_PROVIDER_ENV_NAMES``
    convention; callers that need a custom ref name re-register it via
    ``set()`` at process start (e.g. app startup), or construct their own
    instance for test isolation instead of touching the module-default
    singleton (see ``default_tenant_credential_store``)."""

    def __init__(self) -> None:
        self._refs: Dict[Tuple[str, str], str] = {}

    def set(self, tenant_id: str, provider: str, key_ref: str) -> None:
        """Register an env-var NAME override for (tenant_id, provider).

        Malformed input (empty tenant_id / provider / key_ref) is a silent
        no-op -- degrade-never, never raises."""
        tid = (tenant_id or "").strip()
        prov = (provider or "").strip().lower()
        ref = (key_ref or "").strip()
        if not tid or not prov or not ref:
            return
        self._refs[(tid, prov)] = ref

    def get(self, tenant_id: str, provider: str) -> Optional[str]:
        """Resolve the tenant's OWN key for ``provider`` from the local vault.

        Resolution order for the env-ref NAME: an explicit ``set()`` override
        for THIS (tenant_id, provider) pair, else the built-in per-provider
        convention. An unknown provider with no override yields None (fail
        closed to 'no key' rather than guessing an env-var name). The vault
        read + every step is wrapped so ANY failure (bad tenant id, missing
        file, broken loader) degrades to None, never raises, never logs the
        value."""
        tid = (tenant_id or "").strip()
        prov = (provider or "").strip().lower()
        if not tid or not prov:
            return None
        ref_name = self._refs.get((tid, prov)) or _DEFAULT_PROVIDER_ENV_NAMES.get(prov)
        if not ref_name:
            return None
        secrets = self._load_vault(tid)
        if not secrets:
            return None
        val = secrets.get(ref_name)
        if val and str(val).strip():
            return str(val).strip()
        return None

    def _load_vault(self, tenant_id: str) -> Dict[str, str]:
        """Best-effort read of the tenant's local secrets vault via
        ``cex_tenant_paths.load_tenant_secrets`` (the SAME loader
        apps.dashboard_api.deps already uses). {} on ANY failure -- an absent
        module, an absent vault file, or a loader surprise all degrade to 'no
        secrets', never a raised exception, never a logged value."""
        _ensure_tools_on_path()
        try:
            import cex_tenant_paths  # type: ignore[import]
        except Exception:
            return {}
        try:
            secrets = cex_tenant_paths.load_tenant_secrets(tenant_id)
        except Exception:
            return {}
        return secrets if isinstance(secrets, dict) else {}


# --------------------------------------------------------------------------- #
# SupabaseStore (production STUB -- FOUNDER-GATED, not implemented).
# --------------------------------------------------------------------------- #
class SupabaseStore:
    """PRODUCTION TenantCredentialStore -- NOT IMPLEMENTED.

    # FOUNDER-GATED: RLS table + encryption-at-rest.

    The intended prod shape (documented, NOT built): a dedicated
    tenant_credentials table behind Supabase RLS (tenant_id-scoped, the same
    isolation seam every other tenant_data table uses --
    cexai.governance.data.adapter.SupabaseDataAdapter), with the key VALUE
    encrypted-at-rest and decrypted only at read time inside the audited
    adapter path. None of that plumbing exists here.

    This class exists ONLY so the TenantCredentialStore contract has a second,
    HONESTLY stubbed implementation -- a future founder-gated lane fills it in
    without changing the contract callers (apps.dashboard_api.deps.
    resolve_credential) already code against. Every method raises
    NotImplementedError immediately: no partial behavior, no silent no-op, no
    fabricated success."""

    def __init__(self, *_args: Any, **_kwargs: Any) -> None:
        # Accepts arbitrary args so a future concrete wiring (a Supabase client,
        # a table name, ...) can be added without breaking this constructor's
        # shape. Stores nothing today -- there is nothing real to store yet.
        pass

    def get(self, tenant_id: str, provider: str) -> Optional[str]:
        raise NotImplementedError(
            "SupabaseStore.get is FOUNDER-GATED (RLS table + encryption-at-rest "
            "are not built yet) -- production BYOK read is not wired. Use "
            "EnvRefStore for dev/local, or wait for the founder-gated production "
            "lane."
        )

    def set(self, tenant_id: str, provider: str, key_ref: str) -> None:
        raise NotImplementedError(
            "SupabaseStore.set is FOUNDER-GATED (RLS table + encryption-at-rest "
            "are not built yet) -- production BYOK write is not wired. Use "
            "EnvRefStore for dev/local, or wait for the founder-gated production "
            "lane."
        )


# --------------------------------------------------------------------------- #
# Module-default store (a lazily-constructed EnvRefStore singleton).
# --------------------------------------------------------------------------- #
_DEFAULT_STORE: Optional[EnvRefStore] = None


def default_tenant_credential_store() -> EnvRefStore:
    """The process-wide default TenantCredentialStore (an EnvRefStore).

    Tests / callers that need isolation from the shared singleton (e.g. to
    register a custom ``set()`` override without affecting other callers in
    the same process) should construct their own ``EnvRefStore()`` instance
    and pass it explicitly wherever a store is accepted, rather than mutating
    this one."""
    global _DEFAULT_STORE
    if _DEFAULT_STORE is None:
        _DEFAULT_STORE = EnvRefStore()
    return _DEFAULT_STORE

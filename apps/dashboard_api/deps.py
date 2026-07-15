# -*- coding: ascii -*-
"""Dependency seams for the dashboard API (mission CEXAI_PRODUCT_RUNTIME, T3).

This module LAZILY binds the dashboard backend to the two PARALLEL-BUILT modules it
orchestrates -- without importing them at module load:

  * ``_tools/cex_run_capability.py``    -- the headless runtime (run_capability + the
    Credential / CapabilityResult / CapabilityRefused contract).
  * ``_tools/cex_capability_registry.py`` -- the per-tenant capability catalog
    (``list_capabilities(tenant_id)``).

WHY LAZY (the task contract): these files are built in PARALLEL with this one. The
dashboard app MUST start even if either is mid-build or absent. So every import is
deferred to first use and guarded -- a missing runtime surfaces as a clean 503-style
RuntimeUnavailable at request time, never an ImportError at app boot. The app also
codes strictly against the build-spec CONTRACT (signatures), never against internals.

It also owns:
  * the Credential BUILDER (server-side ONLY) -- mode=byo_api_key from the tenant's
    stored key or a DEV env. The browser NEVER sends a credential (spec B.3 INVARIANT).
  * the ENABLED-capability resolution from the tenant overlay (spec D.3), passed to
    run_capability via ``options['enabled_capabilities']`` so the runtime's own deny
    seam (capability_disabled) is authoritative.

ASCII-only per .claude/rules/ascii-code-rule.md. Fully type-hinted. No network/secret
read at import.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

__all__ = [
    "RuntimeUnavailable",
    "ComposeError",
    "repo_root",
    "load_runtime",
    "load_agent_runtime",
    "load_agent_loop_runtime",
    "load_registry",
    "load_media_modules",
    "build_credential",
    "resolve_credential",
    "resolve_enabled_capabilities",
    "resolve_enabled_agents",
    "list_capability_cards",
    "get_capabilities_config",
    "mutate_capability",
    "make_run_writer",
    "make_run_reader",
    "make_public_reader",
    "resolve_public_brand",
    "register_public_session_factory_from_env",
    "secret_is_configured",
    "count_managed_entities",
    "overlay_integrations",
    "register_session_factory_from_env",
    "DEV_API_KEY_ENV",
    "DEV_PROVIDER_ENV",
    "DEV_MODEL_ENV",
    "SESSION_FACTORY_ENV",
    "PUBLIC_SESSION_FACTORY_ENV",
]

# Dev-mode credential env (used ONLY when a tenant has no stored key; server-side).
DEV_API_KEY_ENV = "CEXAI_DASHBOARD_DEV_API_KEY"     # a BYO key for local dev runs
DEV_PROVIDER_ENV = "CEXAI_DASHBOARD_DEV_PROVIDER"   # default provider for dev (anthropic;
                                                     # also accepts openai/ollama/openwebui --
                                                     # opaque string, resolved by cex_sdk.models.chat)
DEV_MODEL_ENV = "CEXAI_DASHBOARD_DEV_MODEL"         # default model ("" -> SDK resolves)

# The live-go DbSession factory registration seam (T5 / debt D5). An environment
# names a factory "module.path:callable" here; register_session_factory_from_env()
# imports it at app startup and binds it to ``deps.tenant_session_factory`` (the
# attribute every session-factory path resolves via getattr). UNSET (default) ->
# no factory -> live reads/writes degrade to empty/local-only. See the runbook
# (_docs/compiled/runbook_dashboard_deploy.md) for the Protocol the callable must satisfy.
SESSION_FACTORY_ENV = "CEXAI_DASHBOARD_SESSION_FACTORY"

# The PUBLIC (anon-role) DbSession factory registration seam (spec 10 W1-backend). A
# SEPARATE env from SESSION_FACTORY_ENV so the unauthenticated public path NEVER borrows
# the authenticated/service tenant factory: the public factory mints anon-role sessions
# (SET LOCAL ROLE anon) so RLS public_catalog_read constrains them to published-only.
# UNSET (default) -> no public factory -> the public reader degrades to local-only
# (resolve -> None / catalog -> empty), NEVER disclosing a tenant. Same dotted
# "module.path:callable" contract as SESSION_FACTORY_ENV.
PUBLIC_SESSION_FACTORY_ENV = "CEXAI_DASHBOARD_PUBLIC_SESSION_FACTORY"

# The tenant-id env the runtime/overlay machinery reads (set transiently by the runtime
# itself; we use it here only to scope the overlay/registry read on the edge).
_ENV_TENANT_ID = "CEX_TENANT_ID"

_BYO_API_KEY_MODE = "byo_api_key"


class RuntimeUnavailable(RuntimeError):
    """Raised when a parallel-built dependency (runtime or registry) cannot be loaded.

    The API maps this to HTTP 503 (Service Unavailable) -- the dashboard is up but the
    runtime it fronts is not ready. Carries ``.component`` ('runtime' | 'registry') and
    a safe ``.detail`` (never a secret).
    """

    def __init__(self, component: str, *, detail: str = "") -> None:
        self.component = component
        self.detail = detail
        msg = "%s unavailable" % component
        if detail:
            msg += ": %s" % detail
        super().__init__(msg)


class ComposeError(Exception):
    """A composition-control-plane mutation error (mission DASHBOARD_COMPOSITION W2).

    Raised by ``mutate_capability`` and mapped by the API to a precise status:
      * ``unknown_action`` -> 400 (the PATCH body action was not 'attach'|'detach');
      * ``not_declared``   -> 409 (FAIL-CLOSED: a capability must be DECLARED to be toggled);
      * ``write_failed``   -> 500 (the guarded overlay write could not complete).
    Carries ``.reason``, ``.slug`` and a safe ``.detail`` (never a secret/traceback)."""

    def __init__(self, reason: str, *, slug: str = "", detail: str = "") -> None:
        self.reason = reason
        self.slug = slug
        self.detail = detail
        msg = reason
        if slug:
            msg += " (%s)" % slug
        if detail:
            msg += ": %s" % detail
        super().__init__(msg)


def repo_root() -> Path:
    """Resolve the repo root (apps/dashboard_api/ -> ../../). Used to put ``_tools`` on
    sys.path for the lazy imports without hardcoding an absolute path."""
    return Path(__file__).resolve().parents[2]


def _ensure_tools_on_path() -> None:
    """Put the repo-root ``_tools`` dir on sys.path (idempotent) so the runtime + registry
    modules import by their flat module names, exactly as they do for each other."""
    tools_dir = str(repo_root() / "_tools")
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)


def load_runtime() -> Any:
    """Lazily import + return the ``cex_run_capability`` module (the runtime).

    Deferred to first use so the app boots even while the runtime is mid-build. A failed
    import raises RuntimeUnavailable('runtime', ...) -> HTTP 503, never an ImportError at
    app startup.
    """
    _ensure_tools_on_path()
    try:
        import cex_run_capability  # type: ignore[import]
    except Exception as exc:  # ImportError or any load-time failure -> fail soft to 503
        raise RuntimeUnavailable("runtime", detail=str(exc)) from exc
    return cex_run_capability


def load_agent_runtime() -> Any:
    """Lazily import + return the ``cex_run_agent`` module (the agent runtime, ADR Phase B).

    The SIBLING of the capability runtime: it REUSES cex_run_capability's spine (Credential /
    CapabilityRefused / DbWriter / the credential+enabled+frozen helpers) and adds the
    ASSEMBLE loader + run_agent. Deferred to first use so the app boots even while it is
    mid-build; a failed import raises RuntimeUnavailable('agent_runtime', ...) -> HTTP 503,
    never an ImportError at app startup. The api maps the SAME CapabilityRefused taxonomy this
    module already maps for /capability/run (cex_run_agent re-exports run_capability's
    CapabilityRefused, so one handler covers both siblings).
    """
    _ensure_tools_on_path()
    try:
        import cex_run_agent  # type: ignore[import]
    except Exception as exc:  # ImportError or any load-time failure -> fail soft to 503
        raise RuntimeUnavailable("agent_runtime", detail=str(exc)) from exc
    return cex_run_agent


def load_agent_loop_runtime() -> Any:
    """Lazily import + return the ``cex_agent_loop`` module (the MULTI-STEP runtime, ADR Phase C).

    The SIBLING of the single-step agent runtime, one layer up: it REUSES cex_run_agent's spine
    (which itself reuses cex_run_capability's) and adds the plan/act/observe LOOP composing the
    dormant cex_sdk primitives (Toolkit/Workflow/Session) + the OQ4 budget + the OQ8 HITL gate +
    the agent_runs/agent_steps persistence. Deferred to first use so the app boots even while it
    is mid-build; a failed import raises RuntimeUnavailable('agent_loop_runtime', ...) -> HTTP
    503. It re-exports run_capability's CapabilityRefused (via the sibling chain), so the SAME
    exception handler covers it.
    """
    _ensure_tools_on_path()
    try:
        import cex_agent_loop  # type: ignore[import]
    except Exception as exc:  # ImportError or any load-time failure -> fail soft to 503
        raise RuntimeUnavailable("agent_loop_runtime", detail=str(exc)) from exc
    return cex_agent_loop


def load_media_modules() -> Any:
    """Lazily import + return ``(cex_media_store, cex_media_persist)`` for the upload-persist
    endpoint (PATCH /capability/{record_id}/media/{slot_key}).

    Ensures ``_tools`` is on sys.path (same posture as load_runtime), then imports the two PURE
    modules: the upload sink seam (base64-inline V1) + the apply-upload-to-dual-output projector.
    Deferred to first use; a failed import raises RuntimeUnavailable('media', ...) -> HTTP 503,
    never an ImportError at app startup.
    """
    _ensure_tools_on_path()
    try:
        import cex_media_store  # type: ignore[import]
        import cex_media_persist  # type: ignore[import]
    except Exception as exc:  # ImportError or any load-time failure -> fail soft to 503
        raise RuntimeUnavailable("media", detail=str(exc)) from exc
    return cex_media_store, cex_media_persist


def load_registry() -> Any:
    """Lazily import + return the ``cex_capability_registry`` module (the catalog).

    Built in PARALLEL and may not exist yet. A failed import raises
    RuntimeUnavailable('registry', ...). Callers that can degrade (e.g. /capabilities)
    may catch this and fall back to the runtime's base capability set.
    """
    _ensure_tools_on_path()
    try:
        import cex_capability_registry  # type: ignore[import]
    except Exception as exc:
        raise RuntimeUnavailable("registry", detail=str(exc)) from exc
    return cex_capability_registry


def build_credential(tenant_id: str, *, runtime: Optional[Any] = None) -> Any:
    """Build a server-side ``Credential`` (mode=byo_api_key) for a tenant run.

    KEY CUSTODY (spec B.3 / OQ5): the credential is assembled SERVER-SIDE. The browser
    never sends it. The api_key resolves from, in order:
      1. the tenant's stored key on the secret surface (production path); resolved via the
         runtime's own helper if present, otherwise the tenant-scoped env.
      2. a single DEV env (``CEXAI_DASHBOARD_DEV_API_KEY``) for local development.

    The key is placed ONLY inside the Credential dataclass (which the runtime guarantees
    never to echo/log/persist). This function returns the runtime's ``Credential`` type so
    the object is exactly what ``run_capability`` expects.

    NOTE: ``native_local`` (the company native Claude sub) is OQ2-unresolved and is NOT
    built here -- Phase 1 proves the byo_api_key path (spec E.5).
    """
    rt = runtime if runtime is not None else load_runtime()
    api_key = _resolve_tenant_api_key(tenant_id)
    if not api_key:
        # Fail-closed at construction would hide the cause; let the runtime's
        # Credential.validate() raise CapabilityRefused('missing_credential') so the
        # API maps it to a precise 4xx. We still construct with an empty key.
        api_key = None
    provider = os.environ.get(DEV_PROVIDER_ENV, "anthropic").strip() or "anthropic"
    model = os.environ.get(DEV_MODEL_ENV, "").strip()
    return rt.Credential(
        mode=_BYO_API_KEY_MODE,
        provider=provider,
        model=model,
        api_key=api_key,
    )


def _resolve_tenant_api_key(tenant_id: str) -> Optional[str]:
    """Resolve the tenant's stored BYO key (server-side), with a DEV fallback.

    Production: the tenant secret surface (``.cex/tenants/<tid>/secrets/.env``, gitignored,
    loaded by the runtime's tenant-paths helper if available). We attempt that helper
    lazily; ANY failure degrades silently to the DEV env (never raises -- the absence of a
    key is handled as missing_credential downstream, fail-closed).

    The key is never logged here.
    """
    # 1. Try the tenant secret surface via the runtime's tenant-paths helper (best-effort).
    key = _try_tenant_secret_key(tenant_id)
    if key:
        return key
    # 2. DEV fallback: a single server-side env for local development.
    dev = os.environ.get(DEV_API_KEY_ENV, "").strip()
    return dev or None


def _try_tenant_secret_key(tenant_id: str) -> Optional[str]:
    """Best-effort read of the tenant's stored provider key from the secret surface.

    Uses ``cex_tenant_paths.load_tenant_secrets`` if importable; scoped to this tenant via
    CEX_TENANT_ID, restored in finally. Returns the first plausible provider key found, or
    None. NEVER raises (a degraded env just means 'no stored key' -> DEV fallback).
    """
    _ensure_tools_on_path()
    prev = os.environ.get(_ENV_TENANT_ID)
    try:
        os.environ[_ENV_TENANT_ID] = tenant_id
        try:
            import cex_tenant_paths  # type: ignore[import]
        except Exception:
            return None
        loader = getattr(cex_tenant_paths, "load_tenant_secrets", None)
        if loader is None:
            return None
        try:
            secrets = loader(tenant_id)
        except TypeError:
            # Signature variance: some impls take no arg (read CEX_TENANT_ID).
            try:
                secrets = loader()
            except Exception:
                return None
        except Exception:
            return None
        if not isinstance(secrets, dict):
            return None
        for name in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "CEXAI_API_KEY", "OPENWEBUI_API_KEY"):
            val = secrets.get(name)
            if val and str(val).strip():
                return str(val).strip()
        return None
    finally:
        if prev is None:
            os.environ.pop(_ENV_TENANT_ID, None)
        else:
            os.environ[_ENV_TENANT_ID] = prev


# --------------------------------------------------------------------------- #
# BYOK precedence resolver (mission BYOK_0713, lane vault-backend; decision D5
# in .cex/runtime/decisions/decision_manifest_wave2_0713.yaml).
# --------------------------------------------------------------------------- #
def _default_credential_store() -> Optional[Any]:
    """Lazily import + return the module-default TenantCredentialStore
    (cex_sdk.credentials.tenant_store.default_tenant_credential_store()).

    Guarded exactly like every other cross-module reference in this file: an
    import failure degrades to None (tier 1 unavailable -> resolve_credential
    falls through to the served-Central tier), never raising, never blocking
    app boot."""
    try:
        from cex_sdk.credentials.tenant_store import default_tenant_credential_store
    except Exception:
        return None
    try:
        return default_tenant_credential_store()
    except Exception:
        return None


def resolve_credential(
    tenant_id: str, provider: str, *, store: Optional[Any] = None
) -> Optional[str]:
    """BYOK precedence resolver (mission BYOK_0713 D5 -- "tese hibrida": tenant
    plugs their OWN API key, else the SERVED key (least-privilege) is used).

    PRECEDENCE (documented, load-bearing -- proved by test_byok_vault_r354.py):
      1. TENANT-OWNED key -- ``store.get(tenant_id, provider)`` via the
         TenantCredentialStore contract (cex_sdk.credentials.tenant_store).
         Default store is EnvRefStore (dev/local vault); WINS when present.
      2. SERVED-CENTRAL key -- "a atual": the SAME single global fallback
         ``build_credential`` / ``_resolve_tenant_api_key`` already use today
         (``DEV_API_KEY_ENV``). This function does NOT alter that path.
      3. None (degrade-never). The caller's EXISTING missing_credential
         handling applies unchanged (``Credential.validate()`` raises
         ``CapabilityRefused`` downstream, the capability's deterministic
         refusal path) -- this resolver itself NEVER raises.

    ADDITIVE, NOT a replacement: ``build_credential`` / ``_resolve_tenant_api_key``
    are UNTOUCHED by this function (zero regression -- see the module's A/B
    test proving build_credential never calls this). This is a NEW,
    provider-aware entry point a future production-wiring lane can adopt for
    the live dashboard route; wiring it into that route is OUT OF SCOPE for
    this backend-seam lane.

    SECRET DISCIPLINE: returns the resolved key VALUE (or None) and NOTHING
    else. Never logs, never prints. A broken/misbehaving store's exception is
    swallowed (degrade-never) -- it can never propagate a secret-adjacent
    traceback upward.
    """
    active_store = store if store is not None else _default_credential_store()
    tenant_key: Optional[str] = None
    if active_store is not None:
        try:
            tenant_key = active_store.get(tenant_id, provider)
        except Exception:
            # degrade-never: a broken/stubbed store (e.g. SupabaseStore today)
            # must not block the served-Central fallback, and must never leak
            # whatever the exception text contains.
            tenant_key = None
    if tenant_key:
        return tenant_key
    served = os.environ.get(DEV_API_KEY_ENV, "").strip()
    return served or None


def resolve_enabled_capabilities(tenant_id: str) -> Optional[List[str]]:
    """Resolve the tenant's RUN-enabled capability allowlist for the run-options seam.

    Two gates are layered, both overlay-derived (mission DASHBOARD_COMPOSITION W1):
      1. the kinds_overlay ``enabled_capabilities`` VISIBILITY gate (spec D.3) --
         ``_kinds_overlay_enabled_capabilities`` below (a list, or None for 'no gate');
      2. the capability_map.yaml ``capabilities:{enabled,disabled}`` ATTACH gate (D2) --
         ``registry.resolve_enabled`` over the declared universe.

    Returns the resolved enabled set as a list -- the run endpoint injects it as
    ``options['enabled_capabilities']`` so the runtime's deny seam (capability_disabled) is
    authoritative AND consistent with the attached set. Returns None ONLY when NEITHER gate
    is active (None => 'all base capabilities', the pre-W1 semantics: ZERO REGRESSION).

    DEGRADE-NEVER: any error in the compose layer falls back to the kinds_overlay result
    (gate 1) unchanged; an absent ``capabilities:`` block leaves gate 1 untouched. NEVER
    raises -- the AUTHORITATIVE per-run deny is the runtime's own check; this is the edge hint.
    """
    base = _kinds_overlay_enabled_capabilities(tenant_id)
    # Layer the capability_map ATTACH gate ON TOP of the kinds_overlay visibility gate.
    try:
        registry = load_registry()
    except RuntimeUnavailable:
        return base
    gate_active = getattr(registry, "compose_gate_active", None)
    resolve_enabled = getattr(registry, "resolve_enabled", None)
    declared_fn = getattr(registry, "declared_capabilities", None)
    if gate_active is None or resolve_enabled is None or declared_fn is None:
        return base  # older registry without the compose gate -> unchanged (zero regression)
    try:
        if not gate_active(tenant_id):
            return base  # no compose gate declared -> unchanged (zero regression)
        declared = set(declared_fn(tenant_id))
        composed = set(resolve_enabled(tenant_id, declared))
    except Exception:
        return base  # degrade-never: any failure -> the kinds_overlay result unchanged
    if base is None:
        return sorted(composed)
    return sorted(set(base) & composed)


def _kinds_overlay_enabled_capabilities(tenant_id: str) -> Optional[List[str]]:
    """Resolve the tenant's enabled-capability allowlist (spec D.3) from the kinds overlay.

    Returns a list of capability strings the operator enabled, or None when the overlay
    declares no gate (None => 'all base capabilities', matching the runtime's
    ``_capability_enabled`` semantics, which DENIES only when the key is present).

    Best-effort + fail-OPEN-to-None on read errors (a missing overlay is not a security
    hole here: the AUTHORITATIVE deny is the runtime's per-call check, and the registry/
    card list is also overlay-derived). NEVER raises.
    """
    _ensure_tools_on_path()
    prev = os.environ.get(_ENV_TENANT_ID)
    try:
        os.environ[_ENV_TENANT_ID] = tenant_id
        try:
            import cex_tenant_paths  # type: ignore[import]
        except Exception:
            return None
        getter = getattr(cex_tenant_paths, "load_overlay", None) or getattr(
            cex_tenant_paths, "load_tenant_overlay", None
        )
        if getter is None:
            return None
        try:
            overlay = getter(tenant_id)
        except TypeError:
            try:
                overlay = getter()
            except Exception:
                return None
        except Exception:
            return None
        if not isinstance(overlay, dict):
            return None
        enabled = overlay.get("enabled_capabilities")
        if enabled is None:
            return None
        if isinstance(enabled, (list, tuple)):
            return [str(c) for c in enabled]
        return None
    finally:
        if prev is None:
            os.environ.pop(_ENV_TENANT_ID, None)
        else:
            os.environ[_ENV_TENANT_ID] = prev


def resolve_enabled_agents(tenant_id: str) -> Optional[List[str]]:
    """Resolve the tenant's enabled-AGENT allowlist (ADR Phase B) from the visible set.

    The agent analogue of ``resolve_enabled_capabilities``: it returns the ids of the agents
    the tenant may RUN, which is exactly the ENABLED subset of the overlay-gated VISIBLE set
    that GET /agents returns. REUSES ``agents_config.list_agents`` (the SAME overlay-gated,
    tenant-scoped, degrade-never reader the catalog uses) so the run gate and the catalog can
    NEVER disagree -- an agent the tenant cannot see or that the overlay disabled is not
    runnable, BY CONSTRUCTION.

    Returns the enabled-id list (passed to run_agent as ``options['enabled_capabilities']`` so
    the runtime's authoritative ``_capability_enabled`` deny seam fires for a non-enabled /
    gated-out agent). Returns ``[]`` (an explicit empty gate -> deny all) when the tenant has
    NO visible-and-enabled agents. NEVER returns None for the agent path: agents are
    deny-by-default (unlike base capabilities, there is no implicit "all" set), so an
    unresolvable overlay yields the (possibly empty) visible-enabled set, never an open gate.

    Best-effort + fail-CLOSED-to-empty on read errors (a degraded reader -> [] -> deny all,
    which is safe: a run the tenant cannot prove it may make is refused). NEVER raises.
    """
    try:
        from . import agents_config as _ac  # deferred (house style); acyclic
    except Exception:
        return []  # cannot resolve the visible set -> deny all (fail-closed for runs)
    try:
        agents = _ac.list_agents(tenant_id)
    except Exception:
        return []
    if not isinstance(agents, list):
        return []
    enabled: List[str] = []
    for agent in agents:
        if not isinstance(agent, dict):
            continue
        if not agent.get("enabled"):
            continue  # a disabled (muted) agent is visible but NOT runnable
        aid = str(agent.get("id") or "").strip()
        if aid:
            enabled.append(aid)
    return enabled


def list_capability_cards(tenant_id: str) -> List[Dict[str, Any]]:
    """Return the tenant's ENABLED capability cards (spec B.3 GET /capabilities).

    Primary path: the parallel-built registry's ``list_capabilities(tenant_id)`` -- the
    organic, overlay-derived card list. The registry is the source of truth (spec OQ6:
    one shared registry + per-tenant overlay).

    Degraded path: if the registry module is not yet built (RuntimeUnavailable), fall back
    to the runtime's in-module base capability set (``_BASE_CAPABILITIES``) intersected
    with the tenant's enabled list, so the dashboard still renders cards during the
    parallel build. Each card is a plain JSON-able dict.

    COMPOSE GATE (mission DASHBOARD_COMPOSITION W1): the returned cards are filtered
    to the tenant's ATTACHED (enabled) set per the capability_map.yaml
    ``capabilities:{enabled,disabled}`` block -- a declared-but-disabled capability card
    does NOT appear. DEGRADE-NEVER + ZERO-REGRESSION: an absent block (or any error) leaves
    the cards unchanged (allow-all).
    """
    try:
        registry = load_registry()
    except RuntimeUnavailable:
        cards = _fallback_cards_from_runtime(tenant_id)
    else:
        lister = getattr(registry, "list_capabilities", None)
        if lister is None:
            cards = _fallback_cards_from_runtime(tenant_id)
        else:
            cards = _normalize_cards(lister(tenant_id))
    return _filter_cards_by_compose_gate(tenant_id, cards)


def _filter_cards_by_compose_gate(
    tenant_id: str, cards: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Filter ``cards`` to the tenant's ATTACHED (enabled) set (mission
    DASHBOARD_COMPOSITION W1, spec SS3.3 / deliverable 3).

    The declared universe is the slugs of the cards themselves; the enabled subset is
    ``registry.resolve_enabled(tenant_id, declared)`` (reads the capability_map.yaml
    ``capabilities:`` block). A card whose slug is not enabled is dropped.

    DEGRADE-NEVER + ZERO-REGRESSION: a registry without resolve_enabled, an absent
    ``capabilities:`` block (resolve_enabled returns the declared set), or ANY error ->
    the cards are returned unchanged (allow-all). NEVER raises."""
    if not cards:
        return cards
    try:
        registry = load_registry()
    except RuntimeUnavailable:
        return cards
    resolve_enabled = getattr(registry, "resolve_enabled", None)
    if resolve_enabled is None:
        return cards  # older registry without the gate -> allow-all
    try:
        declared = {
            str(c.get("capability", "")).strip()
            for c in cards
            if str(c.get("capability", "")).strip()
        }
        enabled = set(resolve_enabled(tenant_id, declared))
    except Exception:
        return cards  # degrade-never: any failure -> allow-all
    return [c for c in cards if str(c.get("capability", "")).strip() in enabled]


# --------------------------------------------------------------------------- #
# Composition control-plane bridge (mission DASHBOARD_COMPOSITION W2).    #
# Thin lazy-load wrappers over the registry's attach_state / attach_capability  #
# / detach_capability, used by GET /capabilities-config + PATCH /capabilities.  #
# --------------------------------------------------------------------------- #

# The GENERIC, path-free client detail for a 500 write_failed. The real exception (which can carry
# the ABSOLUTE overlay path) is logged server-side only -- never returned to the browser.
_COMPOSE_WRITE_FAILED_DETAIL = "the overlay write could not be completed"


def _log_compose_write_failure(slug: str, exc: Any) -> None:
    """Log a compose-overlay WRITE failure SERVER-SIDE only (stderr) -- never to the client.

    The real exception text can embed the ABSOLUTE overlay path (OS username + dir layout) and
    other server internals; it must stay server-side so the 500 envelope can return a generic
    detail. NEVER raises (logging must not be the thing that breaks the request)."""
    try:
        sys.stderr.write("[ERROR] compose overlay write failed (slug=%s): %s\n" % (slug, exc))
    except Exception:
        pass


def get_capabilities_config(tenant_id: str) -> Dict[str, Any]:
    """The tenant's full ATTACH state (GET /capabilities-config): ``{declared, enabled,
    disabled}`` via the registry's ``attach_state``.

    DEGRADE-NEVER (this is a READ): a registry that is not importable, lacks the function, or
    errors -> an empty state (the compose UI then shows nothing to toggle, never a 500). NEVER
    raises. The api wraps the result with the verified tenant_id (never a body value).
    """
    empty: Dict[str, Any] = {"declared": [], "enabled": [], "disabled": []}
    try:
        registry = load_registry()
    except RuntimeUnavailable:
        return empty
    fn = getattr(registry, "attach_state", None)
    if fn is None:
        return empty  # older registry without the W2 surface -> empty (degrade-never)
    try:
        state = fn(tenant_id)
    except Exception:
        return empty
    return state if isinstance(state, dict) else empty


def mutate_capability(tenant_id: str, slug: str, action: str) -> Dict[str, Any]:
    """Attach/detach ``slug`` for ``tenant_id`` (PATCH /capabilities/{slug}); return the NEW state.

    FAIL-CLOSED (this is a WRITE):
      * an action other than 'attach'|'detach' -> ComposeError('unknown_action')  (-> 400);
      * an undeclared slug                     -> ComposeError('not_declared')    (-> 409);
      * a registry that cannot be loaded       -> RuntimeUnavailable               (-> 503);
      * any guarded-write failure (IO/yaml/path-guard SystemExit) -> ComposeError('write_failed')
        (-> 500).
    The actor recorded in the overlay log is 'operator' (this is the dashboard PATCH path); N07's
    own intent-driven attach calls ``registry.attach_capability(by='n07')`` directly. tenant_id is
    the verified JWT claim (resolved upstream), NEVER a body value.
    """
    action_norm = (action or "").strip().lower()
    if action_norm not in ("attach", "detach"):
        raise ComposeError("unknown_action", detail="action must be 'attach' or 'detach'")
    # A WRITE needs the registry -- do NOT wrap this: an unavailable registry must surface as a
    # 503 (RuntimeUnavailable), never a silent success.
    registry = load_registry()
    writer = getattr(
        registry,
        "attach_capability" if action_norm == "attach" else "detach_capability",
        None,
    )
    if writer is None:
        raise RuntimeUnavailable("registry", detail="compose writers unavailable")
    not_declared = getattr(registry, "CapabilityNotDeclared", None)
    try:
        state = writer(tenant_id, slug, by="operator")
    except (Exception, SystemExit) as exc:
        # The declared-check fail-closed maps to 409; everything else (IO/yaml/hostile-id
        # SystemExit from the path guard) is a server-side write failure -> 500. Secret-free.
        if not_declared is not None and isinstance(exc, not_declared):
            raise ComposeError("not_declared", slug=slug, detail=str(exc))
        # write_failed: str(exc) can embed the ABSOLUTE overlay path (OS username + dir layout)
        # -> info disclosure. Log the real text SERVER-SIDE only; the client gets a GENERIC,
        # path-free detail. (not_declared / unknown_action details are safe and stay verbatim.)
        _log_compose_write_failure(slug, exc)
        raise ComposeError("write_failed", slug=slug, detail=_COMPOSE_WRITE_FAILED_DETAIL)
    return state if isinstance(state, dict) else {"declared": [], "enabled": [], "disabled": []}


def _normalize_cards(cards: Any) -> List[Dict[str, Any]]:
    """Coerce a registry return into a list of plain dicts (defensive, JSON-safe).

    Accepts a list of dicts or a list of dataclass-like objects (``__dict__``). Anything
    else is skipped. This keeps the API contract stable regardless of how the registry
    represents a card internally.
    """
    out: List[Dict[str, Any]] = []
    if not isinstance(cards, (list, tuple)):
        return out
    for card in cards:
        if isinstance(card, dict):
            out.append({str(k): v for k, v in card.items()})
        elif hasattr(card, "__dict__"):
            out.append({str(k): v for k, v in vars(card).items()})
    return out


def _fallback_cards_from_runtime(tenant_id: str) -> List[Dict[str, Any]]:
    """Build cards from the runtime's base capability map when the registry is absent.

    Mirrors the spec B.5 base table the runtime already holds. Intersected with the
    tenant's enabled set (None => all base). Marked ``source='runtime_base'`` so a caller
    can tell this is the degraded path.
    """
    try:
        runtime = load_runtime()
    except RuntimeUnavailable:
        return []
    base = getattr(runtime, "_BASE_CAPABILITIES", {})
    if not isinstance(base, dict):
        return []
    enabled = resolve_enabled_capabilities(tenant_id)
    enabled_set = set(enabled) if enabled is not None else None
    cards: List[Dict[str, Any]] = []
    for capability, tup in base.items():
        if enabled_set is not None and capability not in enabled_set:
            continue
        nucleus = tup[0] if len(tup) > 0 else ""
        kind = tup[1] if len(tup) > 1 else ""
        pillar = tup[2] if len(tup) > 2 else ""
        cards.append(
            {
                "capability": capability,
                "label": capability.replace("_", " ").title(),
                "nucleus": nucleus,
                "kind": kind,
                "pillar": pillar,
                "enabled": True,
                "source": "runtime_base",
            }
        )
    return cards


# --------------------------------------------------------------------------- #
# Runtime->central WRITE seam (roadmap C5 / debt D5 -- the /run db wiring).    #
# --------------------------------------------------------------------------- #
def make_run_writer(tenant_id: str, user_jwt: str) -> Any:
    """Build the run_capability DB writer (the persistence seam for POST /capability/run).

    REUSES the just-built ``cex_runtime_sync.make_runtime_sync_writer`` over the SAME
    tenant-session-factory seam the /results read path already uses (``deps.
    tenant_session_factory``, registered per-environment). This connects run_capability's
    ``db=None`` to the audited SupabaseDataAdapter so a run persists into the tenant's own
    tenant_data (tenant_id EXPLICIT, RLS-enforced).

    DEGRADE-NEVER: no factory configured (no central creds) OR the runtime-sync module not
    importable -> ``make_runtime_sync_writer(None)`` returns a LocalOnlyWriter -> the run
    still completes (persisted=False). NEVER raises -- a missing data plane must never
    block a run.
    """
    factory = _resolve_session_factory(tenant_id, user_jwt)
    _ensure_tools_on_path()
    try:
        import cex_runtime_sync  # type: ignore[import]
    except Exception:
        # Runtime-sync glue not importable here -> fall back to local-only via the same
        # contract (a tiny inline no-op writer) so the run is never blocked.
        return _LocalOnlyRunWriter()
    return cex_runtime_sync.make_runtime_sync_writer(factory)


# --------------------------------------------------------------------------- #
# EDIT->REFLECT READ seam (arch-council B2 -- the /run db_reader wiring).      #
# --------------------------------------------------------------------------- #
def make_run_reader(tenant_id: str, user_jwt: str) -> Any:
    """Build the run_capability product reader (the EDIT->REFLECT seam for POST /capability
    /run). REUSES cex_tenant_knowledge.make_tenant_knowledge_reader over the SAME tenant-
    session-factory seam make_run_writer + the /results read path use (``deps.
    tenant_session_factory``). This lets an ad/catalog run hydrate inputs['product_record']
    from the tenant's CURRENT product data (tenant_data kind='products') through the AUDITED
    SupabaseDataAdapter (tenant_id EXPLICIT, RLS-enforced) -- the SAME isolation seam the
    writer uses, in reverse.

    DEGRADE-NEVER: no factory configured (no central creds) OR cex_tenant_knowledge not
    importable -> a LocalOnly reader (find_product returns None) -> the run proceeds with no
    hydration (byte-identical to today). NEVER raises -- a missing data plane / a read miss
    must never block or alter a run."""
    factory = _resolve_session_factory(tenant_id, user_jwt)
    _ensure_tools_on_path()
    try:
        import cex_tenant_knowledge  # type: ignore[import]
    except Exception:
        # Reader glue not importable here -> a tiny inline no-op reader so the run still runs.
        return _LocalOnlyRunReader()
    return cex_tenant_knowledge.make_tenant_knowledge_reader(factory)


# --------------------------------------------------------------------------- #
# PUBLIC (unauthenticated, anon-role) read seam (spec 10 W1-backend).          #
# The L2 public site has NO JWT. This builds the anon-role public reader over a #
# SEPARATE public session factory so the public path NEVER borrows the          #
# authenticated/service tenant factory. Plus a brand serializer for             #
# /public/tenant-info. Both degrade-never + never disclose a tenant.            #
# --------------------------------------------------------------------------- #
def make_public_reader() -> Any:
    """Build the unauthenticated PUBLIC reader (spec 10 W1-backend).

    REUSES ``public_reader.make_public_reader`` over the SEPARATE public session factory
    (``deps.public_session_factory`` if registered) -- NEVER the tenant_session_factory the
    authenticated path uses. The public factory mints anon-role sessions (SET LOCAL ROLE
    anon) so RLS public_catalog_read constrains every read to published-only rows.

    DEGRADE-NEVER: no public factory configured (no central creds) -> a LocalOnlyPublicReader
    (resolve -> None / catalog -> empty), so the public site renders an empty/branded shell
    rather than 500-ing, and NEVER discloses a tenant. NEVER raises."""
    from . import public_reader as _pr  # deferred (house style); acyclic
    factory = _resolve_public_session_factory()
    return _pr.make_public_reader(factory)


def _resolve_public_session_factory() -> Optional[Any]:
    """Resolve the per-environment PUBLIC (anon-role) zero-arg DbSession factory, or None.

    The public analogue of ``_resolve_session_factory`` but bound to the SEPARATE
    ``deps.public_session_factory`` attribute (registered from PUBLIC_SESSION_FACTORY_ENV)
    so the unauthenticated path can NEVER pick up the authenticated/service factory. The
    public factory takes NO tenant/jwt (there is no claim on the public path); it mints a
    fresh anon-role session per call. None when unconfigured (-> local-only). NEVER raises.
    """
    provider = globals().get("public_session_factory")
    if provider is None:
        return None
    try:
        return provider()
    except Exception:
        return None


def resolve_public_brand(tenant_id: str) -> Dict[str, Any]:
    """Serialize a tenant's PUBLIC brand for /public/tenant-info (spec 10 W1-backend).

    REUSES ``cex_brand_context.resolve_brand_context`` (the ONE brand seam: identity +
    24 design tokens + voice, degrade-never) and projects a value-free, JSON-safe public
    subset: ``{name, tagline, logo, tokens}``. The 24 tokens are the public design system
    the public site themes from (the SAME contract dual_output/brandTheme use). The brand
    is NEVER fabricated -- a tenant with no brand sources yields empty strings + neutral
    tokens (the resolver's degrade-never contract).

    SECURE: this carries NO secret (a brand has none -- name/tagline/logo/colors are public
    by nature). DEGRADE-NEVER: cex_brand_context not importable / any failure -> a neutral
    public brand (empty name/tagline/logo, empty tokens). NEVER raises, NEVER another
    tenant's brand (the tenant_id is the slug-resolved one the caller passes in)."""
    neutral: Dict[str, Any] = {"name": "", "tagline": "", "logo": "", "tokens": {}}
    _ensure_tools_on_path()
    try:
        import cex_brand_context  # type: ignore[import]
    except Exception:
        return neutral
    try:
        ctx = cex_brand_context.resolve_brand_context(tenant_id)
    except Exception:
        return neutral
    if not isinstance(ctx, dict):
        return neutral
    tokens = ctx.get("brand_tokens")
    return {
        "name": str(ctx.get("brand_name") or ""),
        "tagline": str(ctx.get("brand_tagline") or ""),
        "logo": str(ctx.get("brand_logo") or ""),
        "tokens": {str(k): str(v) for k, v in tokens.items()} if isinstance(tokens, Mapping) else {},
    }


def register_public_session_factory_from_env(*, env: Optional[Dict[str, str]] = None) -> bool:
    """Register the PUBLIC (anon-role) DbSession factory named by
    ``$CEXAI_DASHBOARD_PUBLIC_SESSION_FACTORY`` onto ``deps.public_session_factory``.

    The public analogue of ``register_session_factory_from_env`` but for the SEPARATE
    public attribute the unauthenticated path resolves. The contract differs: the public
    callable takes NO args (there is no tenant/jwt on the public path) and returns a
    zero-arg factory minting an anon-role DbSession::

        public_factory() -> Callable[[], DbSession]   # anon-role session per call

    Returns True if a factory was registered, False if the env var is unset/blank (the
    default -> the public reader degrades to local-only). FAIL-SOFT: a bad target is
    logged-as-warning to stderr and returns False -- the app still boots. NEVER raises."""
    src = env if env is not None else dict(os.environ)
    target = (src.get(PUBLIC_SESSION_FACTORY_ENV) or "").strip()
    if not target:
        return False  # default: no public factory -> local-only (degrade-never)
    if ":" not in target:
        _warn_factory(
            "invalid %s=%r (expected 'module.path:callable')"
            % (PUBLIC_SESSION_FACTORY_ENV, target)
        )
        return False
    module_path, _, attr = target.partition(":")
    module_path = module_path.strip()
    attr = attr.strip()
    if not module_path or not attr:
        _warn_factory(
            "invalid %s=%r (expected 'module.path:callable')"
            % (PUBLIC_SESSION_FACTORY_ENV, target)
        )
        return False
    _ensure_tools_on_path()
    import importlib

    try:
        module = importlib.import_module(module_path)
    except Exception as exc:
        _warn_factory("could not import %r: %s" % (module_path, exc))
        return False
    provider = getattr(module, attr, None)
    if provider is None:
        _warn_factory("module %r has no attribute %r" % (module_path, attr))
        return False
    if not callable(provider):
        _warn_factory("%s:%s is not callable" % (module_path, attr))
        return False
    globals()["public_session_factory"] = provider
    return True


class _LocalOnlyRunReader:
    """Inline degrade-never reader used only when cex_tenant_knowledge is not importable.

    Mirrors cex_tenant_knowledge.LocalOnlyKnowledgeReader's find_product + list_entity shape
    so run_capability's hydration (product_record) and leads-injection (inputs['leads']) are
    safe no-ops (None / () -> no injection). Never raises, never touches a session."""

    def find_product(self, tenant_id: str, ref: str) -> Optional[Dict[str, Any]]:
        return None

    def list_entity(self, tenant_id: str, kind: str) -> Tuple[Dict[str, Any], ...]:
        return ()


class _LocalOnlyRunWriter:
    """Inline degrade-never writer used only when cex_runtime_sync is not importable.

    Mirrors cex_runtime_sync.LocalOnlyWriter's persist_artifact shape so run_capability's
    ``db.persist_artifact(...)`` is a safe no-op (returns None -> persisted=False). Never
    raises, never touches a session."""

    def persist_artifact(
        self,
        tenant_id: str,
        capability: str,
        kind: str,
        artifact: str,
        meta: Any,
    ) -> Optional[str]:
        return None

    def read_artifact(self, tenant_id: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Degrade-never no-op (upload-persist read seam): no data plane -> None."""
        return None

    def update_artifact_payload(
        self, tenant_id: str, record_id: str, payload: Mapping[str, Any]
    ) -> bool:
        """Degrade-never no-op (upload-persist write seam): no data plane -> False."""
        return False


def _resolve_session_factory(tenant_id: str, user_jwt: str) -> Optional[Any]:
    """Resolve the per-environment DbSession factory (or None). Mirrors main.
    _build_session_factory: an environment registers ``deps.tenant_session_factory`` to
    inject a pooled tenant connection; absent that, returns None (-> local-only).

    NEVER raises (a degraded provider just means 'no factory' -> local-only)."""
    provider = globals().get("tenant_session_factory")
    if provider is None:
        return None
    try:
        return provider(tenant_id, user_jwt)
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# DbSession factory REGISTRATION seam (T5 / debt D5 -- the live-go injection).  #
# This is the ONE place a deployment plugs a real (pooled) tenant DB connection #
# into the dashboard WITHOUT editing app code: name the factory in an env var.  #
# --------------------------------------------------------------------------- #
def register_session_factory_from_env(*, env: Optional[Dict[str, str]] = None) -> bool:
    """Register the DbSession factory named by ``$CEXAI_DASHBOARD_SESSION_FACTORY``.

    THE LIVE-GO SEAM. The env value is a dotted target ``"module.path:callable"``.
    This imports the module, looks up the callable, and binds it onto
    ``deps.tenant_session_factory`` -- the SAME attribute that every session-factory
    path already resolves via ``getattr(deps, "tenant_session_factory", None)``
    (main._build_session_factory + deps._resolve_session_factory). So once
    registered, /results, /summary, /entity CRUD, and the /run write-through all
    flow to the live tenant DB through the AUDITED SupabaseDataAdapter -- no other
    code changes.

    THE CALLABLE CONTRACT (documented in full in the runbook):
        factory(tenant_id: str, user_jwt: str) -> Callable[[], DbSession]
    i.e. it returns a ZERO-ARG factory minting ONE fresh DbSession per call, where
    the DbSession satisfies cexai.governance.data.adapter.DbSession:
        execute(sql, params) -> driver-native result
        set_config(key, value, is_local) -> None   # is_local=True is MANDATORY
    The factory MUST honor set_config(is_local=True) so the verified-claim tenant
    bind is transaction-scoped (pooled-connection safety; spec A.5). The adapter
    issues the bind for you (bind_session_tenant); the driver just executes it.

    Returns True if a factory was registered, False if the env var is unset/blank
    (the default -> degrade to empty/local-only, NEVER blocking). FAIL-SOFT: a bad
    target (unimportable module, missing attr, non-callable, malformed value) is
    logged-as-warning to stderr and returns False -- the app still boots and runs
    local-only rather than crashing at startup. NEVER raises.

    Idempotent enough for a startup call: re-registering simply rebinds the
    attribute to the freshly-imported callable.
    """
    src = env if env is not None else dict(os.environ)
    target = (src.get(SESSION_FACTORY_ENV) or "").strip()
    if not target:
        return False  # default: no factory -> local-only / empty (degrade-never)

    if ":" not in target:
        _warn_factory(
            "invalid %s=%r (expected 'module.path:callable')" % (SESSION_FACTORY_ENV, target)
        )
        return False
    module_path, _, attr = target.partition(":")
    module_path = module_path.strip()
    attr = attr.strip()
    if not module_path or not attr:
        _warn_factory(
            "invalid %s=%r (expected 'module.path:callable')" % (SESSION_FACTORY_ENV, target)
        )
        return False

    # Make the repo + _tools importable so a factory living anywhere in the tree
    # (or shipped as an installed package) resolves the same way the runtime does.
    _ensure_tools_on_path()
    import importlib

    try:
        module = importlib.import_module(module_path)
    except Exception as exc:  # unimportable target -> warn + degrade (do not crash)
        _warn_factory("could not import %r: %s" % (module_path, exc))
        return False
    provider = getattr(module, attr, None)
    if provider is None:
        _warn_factory("module %r has no attribute %r" % (module_path, attr))
        return False
    if not callable(provider):
        _warn_factory("%s:%s is not callable" % (module_path, attr))
        return False

    # Bind onto the deps module attribute the resolvers read. This is the whole
    # registration -- nothing else in the app changes.
    globals()["tenant_session_factory"] = provider
    return True


def _warn_factory(message: str) -> None:
    """Emit a one-line startup warning to stderr (ASCII tag, never a secret).

    Used only for a MISCONFIGURED factory target so the operator sees the cause;
    a missing/blank var is the silent, intended default (no warning)."""
    try:
        sys.stderr.write("[WARN] dashboard session factory: %s\n" % message)
    except Exception:
        # Logging must never be the thing that breaks startup.
        pass


# --------------------------------------------------------------------------- #
# Secret STATUS probe (status-only -- NEVER reads or returns a value).        #
# --------------------------------------------------------------------------- #
def secret_is_configured(tenant_id: str, name: str) -> bool:
    """Report whether a NAMED secret is configured for the tenant -- STATUS ONLY.

    SECURE-BY-DEFAULT (the #1 settings rule): this returns a BOOL and NEVER reads, returns,
    or logs the secret VALUE. It checks PRESENCE on the tenant secret surface (the same
    best-effort loader deps already uses for the BYO key) plus a server-side env presence
    check for the dev/data-plane names. A name whose presence cannot be determined returns
    False (fail-closed to 'not configured' -- never guess true).

    NEVER raises. The returned bool is the only thing the /settings surface ever learns
    about a secret."""
    # 1. Tenant secret surface (best-effort; returns the dict of NAMES present). We read
    #    only membership/non-emptiness -- never surface the value upstream.
    present = _tenant_secret_names(tenant_id)
    if name in present:
        return True
    # 2. Server-side env presence for the dev/data-plane wiring names (presence only).
    env_aliases = _SECRET_ENV_ALIASES.get(name, ())
    for env_name in env_aliases:
        if os.environ.get(env_name, "").strip():
            return True
    return False


# Map a public secret NAME -> the server-side env var(s) whose PRESENCE indicates it is
# configured in this environment. Presence only -- the value is never read here.
_SECRET_ENV_ALIASES: Dict[str, tuple] = {
    "API_PROVIDER_KEY": (DEV_API_KEY_ENV, "ANTHROPIC_API_KEY", "OPENAI_API_KEY"),
    "DATA_PLANE_URL": ("CEXAI_TENANT_DB_URL", "SUPABASE_URL"),
    "DATA_PLANE_SERVICE_KEY": ("CEXAI_TENANT_DB_KEY", "SUPABASE_SERVICE_ROLE_KEY"),
}


def _tenant_secret_names(tenant_id: str) -> frozenset:
    """Best-effort SET of secret NAMES present on the tenant secret surface (no values).

    Reuses the tenant-paths loader if importable; scoped to this tenant via CEX_TENANT_ID,
    restored in finally. Returns ONLY the keys (names) -- the values are discarded, never
    surfaced. NEVER raises (a degraded env -> empty set -> names resolve via env presence
    or report not-configured)."""
    _ensure_tools_on_path()
    prev = os.environ.get(_ENV_TENANT_ID)
    try:
        os.environ[_ENV_TENANT_ID] = tenant_id
        try:
            import cex_tenant_paths  # type: ignore[import]
        except Exception:
            return frozenset()
        loader = getattr(cex_tenant_paths, "load_tenant_secrets", None)
        if loader is None:
            return frozenset()
        try:
            secrets = loader(tenant_id)
        except TypeError:
            try:
                secrets = loader()
            except Exception:
                return frozenset()
        except Exception:
            return frozenset()
        if not isinstance(secrets, dict):
            return frozenset()
        # NAMES of the non-empty entries ONLY (values discarded immediately).
        return frozenset(
            str(k) for k, v in secrets.items() if v and str(v).strip()
        )
    finally:
        if prev is None:
            os.environ.pop(_ENV_TENANT_ID, None)
        else:
            os.environ[_ENV_TENANT_ID] = prev


# --------------------------------------------------------------------------- #
# Shell-widget projections (roadmap C5 / debt D5 -- the home + settings shells).#
# REUSES: the AUDITED SupabaseDataAdapter for the per-entity counts (NEVER a    #
# re-implemented read) + entities_config's overlay reader for the entity list   #
# and the integrations list (NEVER a duplicated overlay parse).                 #
# --------------------------------------------------------------------------- #
def count_managed_entities(
    tenant_id: str, user_jwt: str = ""
) -> List[Dict[str, Any]]:
    """Per managed-entity row COUNT for the tenant (the home shell's count rollup).

    SHAPE the reference commerce AdminDashboard.useAdminStats count-with-fallback: read
    the tenant's ``managed_entities`` from the overlay (REUSE entities_config -- the SAME
    overlay the /entities-config cards path reads, never a duplicate parse), then COUNT
    tenant_data rows per ``kind == slug`` THROUGH the audited SupabaseDataAdapter
    (tenant-scoped: the session is bound to the verified-claim tenant; the framework
    cross-tenant mirror is defence-in-depth on top of RLS). Each count is wrapped in its
    OWN try/except -> FALLBACK to 0, so one bad table can never 500 the whole shell (the
    same posture as the React ``.catch(() => ({ count: 0 }))`` per query).

    tenant_id MUST be the VERIFIED JWT claim (the caller resolves it upstream). Read-only.

    Returns ``[{slug, label, count}]`` (overlay order). DEGRADE-NEVER: no session factory
    configured (no central creds), no overlay, or the adapter not importable -> ``[]`` (the
    home shell then shows no per-entity rollup, the documented empty-but-200 fallback).
    NEVER raises -- a missing data plane must never block the home shell."""
    entities = _managed_entity_list(tenant_id)
    if not entities:
        return []
    factory = _resolve_session_factory(tenant_id, user_jwt)
    if factory is None:
        return []  # no creds -> empty-but-200 (LIVE needs the factory, like the rest)
    adapter = _make_data_adapter(factory)
    if adapter is None:
        return []
    out: List[Dict[str, Any]] = []
    for slug, label in entities:
        # PER-TABLE FALLBACK to 0: one bad count never breaks the rollup (mirrors the
        # React per-query .catch). A cross-tenant deny cannot occur here (the bind tenant
        # == the count tenant == the verified claim), but if it ever did it degrades to 0.
        out.append(
            {"slug": slug, "label": label, "count": _count_one_kind(adapter, factory, tenant_id, slug)}
        )
    return out


def _count_one_kind(adapter: Any, factory: Any, tenant_id: str, slug: str) -> int:
    """COUNT tenant_data rows for ONE (tenant, kind=slug) via the audited adapter, or 0.

    Binds a FRESH session to the verified-claim tenant (set_config is_local=True ->
    pooled-conn safe), then ``adapter.query`` a ``SELECT count(*)`` under the SAME explicit
    tenant_id inside that one session. FALLBACK to 0 on ANY failure (no rows, a driver
    surprise, a deny) so the rollup never raises."""
    try:
        session = factory()
        adapter.bind_session_tenant(session, {"tenant": tenant_id})
        sql = "SELECT count(*) FROM tenant_data WHERE tenant_id = %s AND kind = %s"
        raw = adapter.query(session, tenant_id, sql, [tenant_id, slug])
        return _scalar_count(raw)
    except Exception:
        return 0


def _scalar_count(raw: Any) -> int:
    """Coerce a COUNT(*) driver result into an int (0 on anything unrecognized).

    Accepts a cursor with fetchone(), a list/tuple of rows ([(n,)] / [{'count': n}]), a
    single row, or a bare number. Defensive: a shape surprise yields 0 (the rollup degrades
    a single entity to 0, never raises)."""
    fetchone = getattr(raw, "fetchone", None)
    if callable(fetchone):
        try:
            raw = fetchone()
        except Exception:
            return 0
    if isinstance(raw, (list, tuple)):
        if not raw:
            return 0
        first = raw[0]
        return _scalar_count(first) if not isinstance(first, (int, float)) else int(first)
    if isinstance(raw, Mapping):
        for key in ("count", "n", "c"):
            if key in raw:
                return _as_int(raw[key])
        for value in raw.values():
            return _as_int(value)
        return 0
    return _as_int(raw)


def _as_int(value: Any) -> int:
    """Best-effort int coercion (a non-numeric / None -> 0)."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _managed_entity_list(tenant_id: str) -> List[tuple]:
    """The tenant's managed entities as ``[(slug, label)]`` from the overlay, DEGRADE-NEVER.

    REUSES ``entities_config.list_entity_schemas`` (the SAME overlay reader + slug
    allowlist + drop rules the /entities-config route uses) so the home counts and the
    management nav can NEVER disagree on the entity set. Returns ``[]`` on any failure or
    an empty overlay. NEVER raises, NEVER another tenant's data."""
    try:
        from . import entities_config as _ec  # deferred (house style); acyclic
    except Exception:
        return []
    try:
        schemas = _ec.list_entity_schemas(tenant_id)
    except Exception:
        return []
    out: List[tuple] = []
    for schema in schemas or []:
        if not isinstance(schema, dict):
            continue
        slug = str(schema.get("entity", "")).strip()
        if not slug:
            continue
        label = str(schema.get("plural") or schema.get("singular") or slug)
        out.append((slug, label))
    return out


def _make_data_adapter(factory: Any) -> Optional[Any]:
    """Construct the audited ``SupabaseDataAdapter`` over ``factory``, or None.

    Deferred + guarded import (same posture as the /results read path): the cexai package
    may be mid-build. None -> the caller degrades to an empty rollup, never an ImportError
    at request time."""
    try:
        from cexai.governance.data.adapter import SupabaseDataAdapter  # type: ignore
    except Exception:
        return None
    try:
        return SupabaseDataAdapter(factory)
    except Exception:
        return None


def overlay_integrations(tenant_id: str) -> List[Dict[str, Any]]:
    """The tenant's overlay-declared integrations as STATUS-ONLY rows (the settings shell).

    STATUS CONCEPT the reference commerce Integracoes page: each integration reports a
    connection STATE (connected | available | error) -- NEVER a credential value. REUSES
    entities_config's overlay reader (``_read_overlay_raw`` -- the SAME parse the cards +
    managed_entities use) and projects an optional top-level overlay ``integrations:`` list
    to ``{key, label, state, detail?}``. The STATE is a value-FREE presence check: an entry
    that names a ``requires`` secret resolves ``connected`` iff that secret is configured
    (``secret_is_configured`` -- presence only, the value is NEVER read), else ``available``.

    tenant_id MUST be the VERIFIED JWT claim. Returns ``[]`` when the overlay declares no
    integrations (the settings shell then shows only the base integrations). DEGRADE-NEVER:
    no overlay / malformed file / absent PyYAML -> ``[]``. NEVER raises, NEVER a secret
    value, NEVER another tenant's config."""
    raw = _read_overlay_for_integrations(tenant_id)
    entries = raw.get("integrations") if isinstance(raw, dict) else None
    if not isinstance(entries, (list, tuple)):
        return []
    out: List[Dict[str, Any]] = []
    seen: set = set()
    for entry in entries:
        if not isinstance(entry, Mapping):
            continue
        key = str(entry.get("key", "")).strip()
        if not key or key in seen:
            continue
        seen.add(key)
        label = str(entry.get("label") or key.replace("_", " ").title())
        row: Dict[str, Any] = {"key": key, "label": label, "state": _integration_state(tenant_id, entry)}
        detail = entry.get("detail")
        if detail:
            row["detail"] = str(detail)
        out.append(row)
    return out


# The integration connection states the frontend IntegrationStatus understands
# (lib/types.ts). An overlay-declared state outside this set is normalized to 'available'.
_INTEGRATION_STATES = frozenset({"connected", "available", "error"})


def _integration_state(tenant_id: str, entry: Mapping[str, Any]) -> str:
    """Resolve ONE overlay integration's STATE (value-free), defaulting to 'available'.

    Precedence: an explicit, KNOWN ``state`` in the overlay wins (an operator can pin
    'error'); otherwise, if the entry names a ``requires`` secret, the state is a PRESENCE
    check -- ``connected`` iff ``secret_is_configured(tenant, name)`` (a bool; the value is
    NEVER read), else ``available``. No ``requires`` and no ``state`` -> ``available``
    (offered, not wired). NEVER reads or returns a secret value."""
    declared = str(entry.get("state", "")).strip().lower()
    if declared in _INTEGRATION_STATES:
        return declared
    requires = entry.get("requires")
    names: List[str] = []
    if isinstance(requires, str) and requires.strip():
        names = [requires.strip()]
    elif isinstance(requires, (list, tuple)):
        names = [str(n).strip() for n in requires if str(n).strip()]
    if names:
        # value-FREE: connected only when EVERY required secret is present (presence bool).
        try:
            present = all(secret_is_configured(tenant_id, name) for name in names)
        except Exception:
            present = False
        return "connected" if present else "available"
    return "available"


def _read_overlay_for_integrations(tenant_id: str) -> Dict[str, Any]:
    """Read the tenant overlay as a raw dict via entities_config's reader, DEGRADE-NEVER.

    REUSES ``entities_config._read_overlay_raw`` -- the SAME fail-closed, tenant-scoped
    path guard the cards + managed_entities reads use (never a duplicated parse). ``{}`` on
    any failure. NEVER raises, NEVER another tenant's overlay."""
    try:
        from . import entities_config as _ec  # deferred (house style); acyclic
    except Exception:
        return {}
    try:
        raw = _ec._read_overlay_raw(tenant_id)
    except Exception:
        return {}
    return raw if isinstance(raw, dict) else {}

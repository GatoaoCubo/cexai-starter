# -*- coding: ascii -*-
"""Home + settings projections for the dashboard-v2 shells (mission CEXAI_DASHBOARD_V2,
roadmap C5 / debt D5).

THE GAP THIS CLOSES: the dashboard-v2 frontend calls GET /summary (home/analytics) and
GET /settings (tenant + integrations + secret STATUS) -- shapes SummaryResponse /
TenantSettings in apps/dashboard_web/lib/types.ts. No backend served them -> live-mode
404. This module PROJECTS those shapes from the tenant's OWN data (the capability cards,
the recent tenant_data rows, integration health) so fixtures-mode and live-mode AGREE.

READ-ONLY + DERIVED (no invented numbers): every stat is a projection of the tenant's
own catalog/results. ``summary`` reuses ``deps.list_capability_cards`` (the organic,
overlay-derived cards) and the SAME tenant_data read the /results endpoint already uses
(passed IN as a callable so this module touches no DB itself).

LIVE COUNT ROLLUP (roadmap C5 / debt D5): ``build_summary`` ALSO projects a per
managed-entity row COUNT (the SHAPE of the reference commerce AdminDashboard.useAdminStats,
count-with-fallback) -- the tenant's ``managed_entities`` from the overlay (REUSED via
``deps.count_managed_entities``, which reads the SAME overlay the cards path reads and
COUNTs tenant_data per kind THROUGH the AUDITED SupabaseDataAdapter, each with a
per-table fallback to 0). The counts are an INJECTED ``entity_counts`` argument when the
caller supplies one (the pure-projection seam -- this module still touches no DB); when
omitted they are self-resolved via ``deps`` from the verified tenant_id. DEGRADE-NEVER:
no session factory -> an empty rollup -> the home shell keeps its current (cards-only)
projection. tenant_id is ALWAYS the verified JWT claim (the caller resolves it upstream).

INTEGRATIONS FROM THE OVERLAY (the settings shell): ``build_settings`` populates
TenantSettings.integrations from the tenant overlay (REUSED via
``deps.overlay_integrations`` -> entities_config's overlay reader) on top of the base
integrations -- the STATUS CONCEPT of the reference commerce Integracoes (connected /
available / error), value-FREE (a secret value is NEVER part of an integration row).

SECURE-BY-DEFAULT SECRETS (the #1 settings rule): the secrets surface reports CONFIGURED
STATUS ONLY -- ``{name, label?, configured: bool, last_rotated?}``. A secret VALUE is
NEVER part of the shape and is NEVER read here (the module does not even open the Vault).
The SecretStatus type in lib/types.ts has no value field; this module mirrors that. The
status is derived from the tenant secret surface's PRESENCE (a name -> bool), never its
contents.

ASCII-only per .claude/rules/ascii-code-rule.md. Fully type-hinted. No secret/value read.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

__all__ = [
    "build_summary",
    "build_settings",
    "SECRET_SURFACE",
]

# The named secrets the dashboard reports STATUS for (NAMES ONLY -- never values). This
# is the catalog of what a tenant CAN configure; ``configured`` is resolved per-name from
# a presence probe (a name -> bool the caller supplies), never by reading the value.
# Ordered for a stable settings render. Mirrors the fixtures surface (lib/fixtures.ts
# fxGetSettings) so live-mode and fixtures-mode agree on the rows shown.
SECRET_SURFACE: Tuple[Tuple[str, str], ...] = (
    ("API_PROVIDER_KEY", "Model provider key (BYO)"),
    ("DATA_PLANE_URL", "Tenant Supabase URL"),
    ("DATA_PLANE_SERVICE_KEY", "Tenant Supabase service key"),
    ("SOCIAL_PUBLISH_KEY", "Social publishing key"),
    ("OBJECT_STORE_KEY", "Object storage key"),
)


# --------------------------------------------------------------------------- #
# GET /summary -- the home shell payload.                                     #
# --------------------------------------------------------------------------- #
def build_summary(
    tenant_id: str,
    cards: Sequence[Mapping[str, Any]],
    recent_rows: Sequence[Mapping[str, Any]],
    *,
    data_plane_ok: bool,
    entity_counts: Optional[Sequence[Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    """Project a SummaryResponse from the tenant's own catalog + recent rows + live counts.

    ``cards``       -- the tenant's capability cards (deps.list_capability_cards) -- the
                       SAME source the /capabilities endpoint returns. Stat cards count
                       enabled/overlay/nuclei from these (no invention).
    ``recent_rows`` -- recent tenant_data rows (the /results read shape: {id, capability,
                       kind, created_at}). Drives the 'artifacts produced' stat + the
                       recent strip.
    ``data_plane_ok`` -- whether a live tenant data plane is wired (drives the health
                       state). False => the read degraded (no central creds) and the
                       health strip says so rather than claiming green.
    ``entity_counts`` -- OPTIONAL injected per managed-entity row counts (the pure-projection
                       seam: ``[{slug, label, count}]``). When None, self-resolved via
                       ``deps.count_managed_entities(tenant_id)`` (reads the overlay's
                       managed_entities + COUNTs tenant_data per kind through the AUDITED
                       adapter, each with a per-table fallback to 0). DEGRADE-NEVER: no
                       session factory / no overlay -> an empty rollup -> no per-entity
                       stats (the home shell keeps its cards-only projection).

    Every number is a derivation of the inputs; nothing is fabricated client-side."""
    card_list = [dict(c) for c in cards]
    total = len(card_list)
    enabled = sum(1 for c in card_list if _truthy(c.get("enabled")))
    overlay = sum(1 for c in card_list if str(c.get("source", "")) == "overlay")
    nuclei = len({str(c.get("nucleus", "")) for c in card_list if c.get("nucleus")})

    rows = [dict(r) for r in recent_rows]
    scores = [
        float(r["score"])
        for r in rows
        if isinstance(r.get("score"), (int, float))
    ]
    avg = round(sum(scores) / len(scores), 1) if scores else 0.0

    # Per managed-entity row COUNT (count-with-fallback, reference commerce AdminDashboard shape):
    # injected when supplied, else self-resolved from the verified tenant_id (read-only,
    # degrade-never to []). Each entry is {slug, label, count}.
    entity_rollup = _resolve_entity_counts(tenant_id, entity_counts)
    managed_total = sum(_as_int(e.get("count")) for e in entity_rollup)

    stats: List[Dict[str, Any]] = [
        {
            "key": "capabilities_enabled",
            "label": "capabilities enabled",
            "value": enabled,
            "hint": "of %d in catalog" % total,
            "tone": "synapse",
        },
        {
            "key": "runs_total",
            "label": "artifacts produced",
            "value": len(rows),
            "hint": "in your data plane",
        },
        {
            "key": "avg_score",
            "label": "avg quality",
            "value": ("%.1f" % avg) if avg else "--",
            "hint": "F7 structural score",
            "tone": "synapse" if avg >= 8 else "signal",
        },
        {
            "key": "custom_overlay",
            "label": "custom (overlay)",
            "value": overlay,
            "hint": "%d nuclei wired" % nuclei,
        },
    ]

    # Append one stat per managed entity (the live count rollup) + a managed-records total.
    # ADDITIVE: when the rollup is empty (no data plane / no overlay) NOTHING is appended,
    # so the home shell degrades to exactly its prior cards-only projection.
    if entity_rollup:
        stats.append(
            {
                "key": "managed_records",
                "label": "managed records",
                "value": managed_total,
                "hint": "across %d entit%s" % (len(entity_rollup), "y" if len(entity_rollup) == 1 else "ies"),
                "tone": "synapse" if managed_total else "muted",
            }
        )
        for entry in entity_rollup:
            slug = str(entry.get("slug", "")).strip()
            if not slug:
                continue
            stats.append(
                {
                    "key": "entity_%s" % slug,
                    "label": str(entry.get("label") or slug),
                    "value": _as_int(entry.get("count")),
                    "hint": "rows in %s" % slug,
                }
            )

    health: List[Dict[str, Any]] = [
        {
            "key": "runtime",
            "label": "8F runtime",
            "state": "ok",
            "detail": "F1..F8 ready",
        },
        {
            "key": "data_plane",
            "label": "Data plane",
            "state": "ok" if data_plane_ok else "degraded",
            "detail": "RLS on . tenant_id" if data_plane_ok else "not wired (degraded)",
        },
        {
            "key": "auth",
            "label": "Identity",
            "state": "ok",
            "detail": "tenant from JWT",
        },
        {
            "key": "backend",
            "label": "Backend",
            "state": "ok",
            "detail": "live API",
        },
    ]

    # ``recent`` uses the SAME ResultRow shape the Results ledger uses (capped to 5).
    recent = [_recent_row(r) for r in rows[:5]]

    return {
        "tenant_id": tenant_id,
        "stats": stats,
        "recent": recent,
        "health": health,
    }


def _recent_row(row: Mapping[str, Any]) -> Dict[str, Any]:
    """Project a tenant_data row to the ResultRow shape the home strip renders.

    {id, capability, kind?, created_at, score?} -- the optional label/nucleus the UI fills
    in from the card catalog; the backend row does not carry them (mirrors the /results
    _normalize_rows shape)."""
    out: Dict[str, Any] = {
        "id": str(row.get("id", "")),
        "capability": str(row.get("capability", "")),
        "created_at": str(row.get("created_at", "")),
    }
    if row.get("kind") is not None:
        out["kind"] = str(row["kind"])
    if isinstance(row.get("score"), (int, float)):
        out["score"] = row["score"]
    return out


# --------------------------------------------------------------------------- #
# GET /settings -- the tenant shell payload (STATUS-ONLY secrets).            #
# --------------------------------------------------------------------------- #
def build_settings(
    tenant_id: str,
    *,
    operator_email: str = "",
    tenant_label: str = "",
    data_plane_ok: bool,
    secret_is_configured: Optional[Callable[[str], bool]] = None,
    overlay_integrations: Optional[Sequence[Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    """Project a TenantSettings from the verified principal + the integration/secret status.

    ``operator_email`` / ``tenant_label`` -- provenance copy from the verified claim /
                        overlay (the client never picks a tenant).
    ``data_plane_ok``  -- whether the tenant data plane is wired (integration state).
    ``secret_is_configured`` -- a presence probe ``name -> bool``. SECURE-BY-DEFAULT: it
                        returns ONLY whether the named secret EXISTS; this module never
                        reads or returns the value. If None (no probe wired), every secret
                        reports ``configured=False`` (status unknown -> shown as not set,
                        never guessed-true). The probe MUST NOT return a value.
    ``overlay_integrations`` -- OPTIONAL injected tenant-overlay integration rows (status
                        only: ``[{key, label, state, detail?}]``). When None, self-resolved
                        via ``deps.overlay_integrations(tenant_id)`` (entities_config's
                        overlay reader + a value-FREE presence check). APPENDED after the
                        base integrations; a base key is never overridden. DEGRADE-NEVER:
                        no overlay -> base integrations only.

    The returned ``secrets`` list carries ``{name, label, configured}`` (+ no value field
    by construction -- the dict is built explicitly, not from any value source). The
    ``integrations`` list is status-only too (no integration row ever carries a value)."""
    probe = secret_is_configured or (lambda _name: False)

    integrations: List[Dict[str, Any]] = [
        {
            "key": "supabase_auth",
            "label": "Supabase Auth",
            "state": "connected",
            "detail": "identity . tenant_id from JWT",
        },
        {
            "key": "data_plane",
            "label": "Tenant data plane",
            "state": "connected" if data_plane_ok else "available",
            "detail": "RLS by tenant_id" if data_plane_ok else "offered . not wired",
        },
        {
            "key": "object_store",
            "label": "Object storage",
            "state": "available",
            "detail": "offered . tenant supplies key",
        },
        {
            "key": "social_publish",
            "label": "Social publishing",
            "state": "available",
            "detail": "offered . tenant supplies key",
        },
    ]

    # Append the tenant overlay's OWN integrations (status-only) after the base set. A base
    # key is authoritative (never overridden by an overlay entry of the same key). Each row
    # is sanitized to the value-FREE IntegrationStatus shape (no value can ride along).
    base_keys = {row["key"] for row in integrations}
    overlay_rows = _resolve_overlay_integrations(tenant_id, overlay_integrations)
    for row in overlay_rows:
        key = str(row.get("key", "")).strip()
        if not key or key in base_keys:
            continue
        base_keys.add(key)
        integrations.append(_clean_integration_row(row))

    secrets: List[Dict[str, Any]] = []
    for name, label in SECRET_SURFACE:
        # PRESENCE ONLY -- a bool. The value is NEVER read, NEVER placed on the dict.
        configured = bool(_safe_probe(probe, name))
        secrets.append(
            {
                "name": name,
                "label": label,
                "configured": configured,
            }
        )

    payload: Dict[str, Any] = {
        "tenant_id": tenant_id,
        "integrations": integrations,
        "secrets": secrets,
        "identity_note": (
            "Identity and tenant binding come from your account "
            "(JWT app_metadata.tenant_id). You never pick a tenant; the client never "
            "sends one. RLS on tenant_id is the boundary."
        ),
    }
    if tenant_label:
        payload["tenant_label"] = tenant_label
    if operator_email:
        payload["operator_email"] = operator_email
    return payload


def _safe_probe(probe: Callable[[str], bool], name: str) -> bool:
    """Call the presence probe defensively. A probe that raises -> 'not configured'
    (fail-closed to the SAFER state: we never claim a secret is present on an error, and
    we never surface the error -- which could leak a path)."""
    try:
        return bool(probe(name))
    except Exception:
        return False


# --------------------------------------------------------------------------- #
# Self-resolution seams (REUSE deps; this module stays DB-free and degrade-never).
# When the caller injects the data, these are pure pass-throughs; when omitted the
# data is resolved from the verified tenant_id via the AUDITED-adapter helpers in
# deps. The deps import is DEFERRED (house style) + guarded so this module imports
# and the pure-projection unit tests run with NO deps side effects.               #
# --------------------------------------------------------------------------- #
def _resolve_entity_counts(
    tenant_id: str, injected: Optional[Sequence[Mapping[str, Any]]]
) -> List[Dict[str, Any]]:
    """Per managed-entity counts: the injected list verbatim, else self-resolved via deps.

    INJECTED path (the pure-projection seam): the caller's ``[{slug,label,count}]`` is used
    as-is (this module touches no DB). SELF-RESOLVE path: ``deps.count_managed_entities``
    reads the overlay's managed_entities + COUNTs tenant_data per kind through the AUDITED
    adapter (per-table fallback to 0). DEGRADE-NEVER: deps absent / no factory / no overlay
    -> ``[]``. NEVER raises."""
    if injected is not None:
        return [dict(e) for e in injected if isinstance(e, Mapping)]
    deps = _load_deps()
    if deps is None:
        return []
    getter = getattr(deps, "count_managed_entities", None)
    if getter is None:
        return []
    try:
        rollup = getter(tenant_id)
    except Exception:
        return []
    if not isinstance(rollup, (list, tuple)):
        return []
    return [dict(e) for e in rollup if isinstance(e, Mapping)]


def _resolve_overlay_integrations(
    tenant_id: str, injected: Optional[Sequence[Mapping[str, Any]]]
) -> List[Dict[str, Any]]:
    """Overlay integrations: the injected list verbatim, else self-resolved via deps.

    SELF-RESOLVE path: ``deps.overlay_integrations`` reads the tenant overlay (entities_config
    reader) + a value-FREE presence check. DEGRADE-NEVER: deps absent / no overlay -> ``[]``.
    NEVER raises, NEVER a secret value."""
    if injected is not None:
        return [dict(r) for r in injected if isinstance(r, Mapping)]
    deps = _load_deps()
    if deps is None:
        return []
    getter = getattr(deps, "overlay_integrations", None)
    if getter is None:
        return []
    try:
        rows = getter(tenant_id)
    except Exception:
        return []
    if not isinstance(rows, (list, tuple)):
        return []
    return [dict(r) for r in rows if isinstance(r, Mapping)]


def _clean_integration_row(row: Mapping[str, Any]) -> Dict[str, Any]:
    """Sanitize an integration entry to the value-FREE IntegrationStatus shape.

    Emits ONLY ``{key, label, state[, detail]}`` -- an explicit allowlist so NO value-shaped
    field (a credential a future overlay author slips in) can ever ride along. ``state`` is
    normalized to a known set (unknown -> 'available')."""
    key = str(row.get("key", "")).strip()
    label = str(row.get("label") or (key.replace("_", " ").title() if key else "Integration"))
    state = str(row.get("state", "")).strip().lower()
    if state not in ("connected", "available", "error"):
        state = "available"
    out: Dict[str, Any] = {"key": key, "label": label, "state": state}
    detail = row.get("detail")
    if detail:
        out["detail"] = str(detail)
    return out


def _load_deps() -> Optional[Any]:
    """Return the ``deps`` module if importable, else None (deferred + guarded).

    Deferred so this module imports in isolation (the pure-projection unit tests do
    ``import summary`` without wanting deps' side effects) and so the app boots even while a
    sibling is mid-build. None -> the caller degrades to an empty rollup/integration list."""
    try:
        from . import deps as _deps  # acyclic: deps does not import summary
    except Exception:
        return None
    return _deps


def _as_int(value: Any) -> int:
    """Best-effort int coercion for a count value (None / non-numeric -> 0)."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _truthy(value: Any) -> bool:
    """Coerce a card's ``enabled`` (bool | 'true'/'false' | None) to a bool."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes")
    return bool(value)

# -*- coding: ascii -*-
"""Overlay-driven managed-entity SCHEMAS for the dashboard management half (mission
CEXAI_DASHBOARD_V2, the mold's tenant-generic promise).

THE GAP THIS CLOSES: the dashboard-v2 management half (apps/dashboard_web) renders a
generic <DataManager/> per managed entity, but the LIST of entities a tenant manages
used to come from a STATIC map baked into the frontend (lib/entities.ts -- one demo
entity). The mold's core promise is that the manageable entities come from the TENANT'S
OVERLAY, so each tenant declares its own (products, contacts, leads, ...) WITHOUT a code
change. This module is the server-side half: it reads the verified tenant's overlay
``managed_entities:`` and projects it to the EntitySchema[] shape the frontend already
consumes (apps/dashboard_web/lib/types.ts EntitySchema). GET /entities-config serves it.

MIRRORS THE CARDS PATH EXACTLY: capability cards already flow overlay -> registry ->
GET /capabilities -> frontend (deps.list_capability_cards). Entity schemas flow the same
way: overlay ``managed_entities`` -> THIS module -> GET /entities-config -> frontend
loader. One overlay file (.cex/tenants/<tid>/overlay/capability_map.yaml) drives both
surfaces; this module reads the SAME file the registry's enabled_capabilities read uses.

TENANT-SCOPED + SECURE-BY-DEFAULT:
  * The tenant_id is ALWAYS the VERIFIED JWT claim (resolved upstream in main.py via
    auth.extract_tenant_id) -- NEVER from the client. The overlay read is scoped to that
    tenant via the fail-closed ``cex_tenant_paths`` guard (surface="overlay"), so a tenant
    can NEVER see another tenant's config.
  * Each entry's ``slug`` is re-validated against the SAME strict allowlist the /entity
    CRUD uses (entities._SLUG_RE / ^[a-z0-9][a-z0-9_-]{0,63}$). A malformed slug entry is
    DROPPED (a bad overlay row never reaches the frontend as a broken route); it cannot
    smuggle SQL or reach a different tenant_data ``kind``.

DEGRADE-NEVER (mirrors the registry's overlay read + the /results read path): NO tenant
overlay, a missing/malformed ``capability_map.yaml``, an absent PyYAML, or a hostile
CEX_TENANT_ID that makes the path guard raise SystemExit -> an EMPTY schema list (the
management nav then simply hides itself). NEVER raises, NEVER 500s, NEVER another tenant's
data.

ALLOWED IMPORT DIRECTION + LAZY IMPORT: ``apps`` may use ``_tools`` (cex_tenant_paths is
the canonical, audited path resolver -- REUSED, never re-implemented). The import is
deferred to call time + guarded so the app boots even while the tree is mid-build (same
posture as deps.load_runtime / entities._load_adapter_cls).

ASCII-only per .claude/rules/ascii-code-rule.md. Fully type-hinted. No DB, no network,
no secret read -- a pure overlay-file read + projection.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

__all__ = [
    "list_entity_schemas",
    "OVERLAY_FILENAME",
    "MANAGED_ENTITIES_KEY",
]

# The overlay file the managed_entities section lives in. SAME file the capability cards
# overlay uses (capability_map.yaml), under the per-tenant overlay surface. Read via the
# fail-closed cex_tenant_paths guard so the path can never escape the tenant root.
OVERLAY_FILENAME = "capability_map.yaml"

# The top-level overlay key holding the managed-entity schemas (a list of EntitySchema).
MANAGED_ENTITIES_KEY = "managed_entities"

# The tenant-id env the overlay/path machinery reads (mirrors deps + the registry).
_ENV_TENANT_ID = "CEX_TENANT_ID"

# Slug allowlist -- IDENTICAL to apps/dashboard_api/entities._SLUG_RE. The slug is BOTH
# the api path segment AND the tenant_data ``kind``; pinning it means a path can never
# smuggle SQL or reach a different table/kind. Kept in lockstep with the CRUD layer so a
# slug that lists here is a slug the CRUD endpoints will accept.
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")

# Column render hints the frontend understands (lib/types.ts EntityColumn.type). An
# unknown type is dropped to plain text (presentation only -- never logic).
_COLUMN_TYPES = frozenset(
    {"text", "number", "badge", "boolean", "date", "currency"}
)

# Field input kinds the frontend understands (lib/types.ts EntityField.type).
_FIELD_TYPES = frozenset(
    {"text", "number", "textarea", "select", "boolean", "date"}
)

# Column alignment values the frontend understands (lib/types.ts EntityColumn.align).
_ALIGN_VALUES = frozenset({"left", "right"})


# --------------------------------------------------------------------------- #
# Public entry point.                                                          #
# --------------------------------------------------------------------------- #
def list_entity_schemas(tenant_id: str) -> List[Dict[str, Any]]:
    """Return the tenant's managed-entity schemas (EntitySchema[]) from its overlay.

    ``tenant_id`` MUST be the VERIFIED JWT claim (the caller resolves it; this function
    never reads a client-supplied tenant). The overlay read is scoped to that tenant.

    Returns a list of plain JSON-able dicts shaped like the frontend EntitySchema
    (apps/dashboard_web/lib/types.ts): ``{entity, singular, plural, columns, fields,
    description?, nucleus?, icon?, writable?}``. Order is preserved from the overlay.

    DEGRADE-NEVER: no overlay / no managed_entities / malformed file / no PyYAML ->
    ``[]`` (the management surface then hides). A malformed individual entry is dropped
    (not a 500). NEVER raises, NEVER another tenant's data."""
    raw = _read_overlay_raw(tenant_id)
    entries = raw.get(MANAGED_ENTITIES_KEY)
    if not isinstance(entries, (list, tuple)):
        return []
    schemas: List[Dict[str, Any]] = []
    seen: set = set()
    for entry in entries:
        schema = _schema_from_raw(entry)
        if schema is None:
            continue
        # Drop a duplicate slug (keep the first) so the frontend never renders two
        # routes for the same entity.
        if schema["entity"] in seen:
            continue
        seen.add(schema["entity"])
        schemas.append(schema)
    return schemas


# --------------------------------------------------------------------------- #
# Overlay read (MIRRORS cex_capability_registry._read_overlay_raw posture).    #
# --------------------------------------------------------------------------- #
def _read_overlay_raw(tenant_id: str) -> Dict[str, Any]:
    """Read the tenant overlay ``capability_map.yaml`` as a raw dict, DEGRADE-NEVER.

    Mirrors cex_capability_registry._read_overlay_raw's IO posture EXACTLY: resolves the
    path via the fail-closed ``cex_tenant_paths`` guard (surface="overlay", the verified
    tenant) and returns ``{}`` on ANY failure -- no tenant, no file, malformed YAML,
    unreadable, absent PyYAML, or a hostile CEX_TENANT_ID that makes the guard raise
    SystemExit. NEVER raises.

    The verified tenant_id is bound onto CEX_TENANT_ID for the resolve (restored in
    ``finally``) AND passed explicitly to the resolver, so the read is scoped to exactly
    that tenant's overlay surface -- never another tenant's."""
    tid = (tenant_id or "").strip()
    if not tid:
        return {}
    prev = os.environ.get(_ENV_TENANT_ID)
    try:
        os.environ[_ENV_TENANT_ID] = tid
        _ensure_tools_on_path()
        try:
            import cex_tenant_paths as _tp  # type: ignore[import]
        except Exception:
            return {}
        path = _tp.resolve_tenant_path(
            OVERLAY_FILENAME, surface="overlay", tenant_id=tid
        )
        if not path.exists():
            return {}
        data = _parse_yaml_text(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (Exception, SystemExit):
        # SystemExit included deliberately (mirrors the registry, audit R3): the
        # tenant-path guard raises SystemExit on a malformed CEX_TENANT_ID; the
        # dashboard must DEGRADE to an empty list, never crash a dashboard call.
        return {}
    finally:
        if prev is None:
            os.environ.pop(_ENV_TENANT_ID, None)
        else:
            os.environ[_ENV_TENANT_ID] = prev


def _ensure_tools_on_path() -> None:
    """Put the repo-root ``_tools`` dir on sys.path (idempotent) so cex_tenant_paths
    imports by its flat module name -- the same way deps._ensure_tools_on_path does."""
    tools_dir = str(Path(__file__).resolve().parents[2] / "_tools")
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)


def _parse_yaml_text(text: str) -> Dict[str, Any]:
    """Parse overlay YAML into a dict, DEGRADE-NEVER. PyYAML preferred; on any failure
    (absent dep, parse error) return ``{}`` so the caller degrades to an empty list."""
    try:
        import yaml  # optional dep; absence must not break the dashboard
    except Exception:
        return {}
    try:
        data = yaml.safe_load(text)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


# --------------------------------------------------------------------------- #
# Projection: a raw overlay entry -> a frontend EntitySchema dict (pure).      #
# --------------------------------------------------------------------------- #
def _schema_from_raw(entry: Any) -> Optional[Dict[str, Any]]:
    """Project ONE overlay ``managed_entities`` entry to a frontend EntitySchema dict.

    Returns None (the entry is DROPPED) when the entry is structurally invalid: not a
    mapping, a missing/blank/malformed ``slug`` (must match the strict allowlist), or no
    valid columns. A dropped entry never reaches the frontend as a broken route. Pure +
    total: never raises.

    The output key is ``entity`` (the frontend EntitySchema field name) sourced from the
    overlay ``slug`` -- the overlay author writes ``slug`` (it IS the tenant_data kind),
    the wire calls it ``entity``. singular/plural default off the slug when omitted."""
    if not isinstance(entry, Mapping):
        return None

    slug = _clean_str(entry.get("slug"))
    if not slug or not _SLUG_RE.match(slug):
        return None

    columns = _columns_from_raw(entry.get("columns"))
    if not columns:
        # An entity with no renderable column is a broken table -> drop it.
        return None
    fields = _fields_from_raw(entry.get("fields"))

    label = _clean_str(entry.get("label")) or _titleize(slug)
    singular = _clean_str(entry.get("singular")) or label
    plural = _clean_str(entry.get("plural")) or label

    schema: Dict[str, Any] = {
        "entity": slug,
        "singular": singular,
        "plural": plural,
        "columns": columns,
        "fields": fields,
    }

    description = _clean_str(entry.get("description"))
    if description:
        schema["description"] = description
    nucleus = _clean_str(entry.get("nucleus"))
    if nucleus:
        schema["nucleus"] = nucleus
    icon = _clean_str(entry.get("icon"))
    if icon:
        schema["icon"] = icon
    # ``writable`` defaults to True (a managed entity is editable unless the overlay
    # explicitly disables writes). Only emit it when explicitly false so the wire shape
    # matches the static map (which omitted it when true).
    if "writable" in entry and not _truthy(entry.get("writable")):
        schema["writable"] = False

    return schema


def _columns_from_raw(raw: Any) -> List[Dict[str, Any]]:
    """Project the overlay ``columns`` list to EntityColumn dicts (dropping bad rows).

    Each column needs a non-blank ``key`` + ``label``; ``type``/``align`` are validated
    against the frontend's known sets (an unknown type is omitted -> plain text; an
    unknown align is omitted -> default left). ``primary`` is coerced to a bool."""
    out: List[Dict[str, Any]] = []
    if not isinstance(raw, (list, tuple)):
        return out
    for col in raw:
        if not isinstance(col, Mapping):
            continue
        key = _clean_str(col.get("key"))
        label = _clean_str(col.get("label"))
        if not key or not label:
            continue
        column: Dict[str, Any] = {"key": key, "label": label}
        ctype = _clean_str(col.get("type"))
        if ctype in _COLUMN_TYPES:
            column["type"] = ctype
        if _truthy(col.get("primary")):
            column["primary"] = True
        align = _clean_str(col.get("align"))
        if align in _ALIGN_VALUES:
            column["align"] = align
        # SECURE-BY-DEFAULT margin guard: a column flagged ``admin_only`` (or its
        # synonym ``sensitive``) is SENSITIVE -- cost, B2B price, margin. The flag
        # passes through here and the frontend DataManager EXCLUDES it from the
        # default table view for every tenant entity (the leak is prevented BY
        # CONSTRUCTION). Emitted only when truthy so a non-sensitive column's wire
        # shape is unchanged.
        if _truthy(col.get("admin_only")) or _truthy(col.get("sensitive")):
            column["admin_only"] = True
        out.append(column)
    return out


def _fields_from_raw(raw: Any) -> List[Dict[str, Any]]:
    """Project the overlay ``fields`` list to EntityField dicts (dropping bad rows).

    Each field needs a non-blank ``key`` + ``label`` + a known ``type`` (default text for
    an unknown type). ``required`` is coerced to a bool; ``placeholder``/``help`` pass
    through as strings; ``options`` (for type=select) project to ``{value,label}`` dicts.
    An empty/absent ``fields`` yields ``[]`` (a read-only-ish entity with no editor)."""
    out: List[Dict[str, Any]] = []
    if not isinstance(raw, (list, tuple)):
        return out
    for fld in raw:
        if not isinstance(fld, Mapping):
            continue
        key = _clean_str(fld.get("key"))
        label = _clean_str(fld.get("label"))
        if not key or not label:
            continue
        ftype = _clean_str(fld.get("type"))
        if ftype not in _FIELD_TYPES:
            ftype = "text"
        field_out: Dict[str, Any] = {"key": key, "label": label, "type": ftype}
        if _truthy(fld.get("required")):
            field_out["required"] = True
        placeholder = _clean_str(fld.get("placeholder"))
        if placeholder:
            field_out["placeholder"] = placeholder
        help_text = _clean_str(fld.get("help"))
        if help_text:
            field_out["help"] = help_text
        if ftype == "select":
            options = _options_from_raw(fld.get("options"))
            if options:
                field_out["options"] = options
        # SECURE-BY-DEFAULT margin guard (mirror of the column flag): an
        # ``admin_only`` / ``sensitive`` field is EXCLUDED from the default edit
        # form by the frontend, so the sensitive value is neither shown nor
        # editable in the default surface. Emitted only when truthy.
        if _truthy(fld.get("admin_only")) or _truthy(fld.get("sensitive")):
            field_out["admin_only"] = True
        out.append(field_out)
    return out


def _options_from_raw(raw: Any) -> List[Dict[str, str]]:
    """Project a select field's ``options`` to ``{value, label}`` string dicts.

    Each option needs a non-blank ``value``; ``label`` defaults to the value when
    omitted. A malformed option row is dropped."""
    out: List[Dict[str, str]] = []
    if not isinstance(raw, (list, tuple)):
        return out
    for opt in raw:
        if not isinstance(opt, Mapping):
            continue
        value = _clean_str(opt.get("value"))
        if not value:
            continue
        label = _clean_str(opt.get("label")) or value
        out.append({"value": value, "label": label})
    return out


# --------------------------------------------------------------------------- #
# Small pure helpers.                                                         #
# --------------------------------------------------------------------------- #
def _clean_str(value: Any) -> str:
    """Coerce a scalar overlay value to a whitespace-normalized string ('' if None).

    YAML folded scalars may carry trailing newlines; we collapse internal whitespace the
    same way the registry's presentation-field normaliser does. A non-scalar (list/dict)
    yields '' (it is never a valid string field)."""
    if value is None:
        return ""
    if isinstance(value, bool):
        # A bool is not a string field; treat as absent for string slots.
        return ""
    if isinstance(value, (str, int, float)):
        return " ".join(str(value).split())
    return ""


def _truthy(value: Any) -> bool:
    """Coerce an overlay bool-ish value (bool | 'true'/'false'/'yes' | None) to a bool."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes", "on")
    return bool(value)


def _titleize(slug: str) -> str:
    """Fallback human label from a slug ('client_leads' -> 'Client Leads')."""
    return " ".join(part.capitalize() for part in re.split(r"[_-]+", slug) if part)

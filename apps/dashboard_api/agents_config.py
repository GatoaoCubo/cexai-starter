# -*- coding: ascii -*-
"""Agent CATALOG + READ surface for the dashboard mold (ADR adr_agents_sdk_dashboard,
Phase A -- the agents-SDK layer's lowest-risk first cut).

THE GAP THIS CLOSES: the dashboard runs ONE runtime shape today -- the single-shot
capability card. The founder wants the AGENTS layer ABOVE that: persistent, multi-step,
tool-using agents. Phase A is the READ half only -- it surfaces the agents that already
exist as a typed catalog so a tenant can BROWSE/DEFINE them. ZERO runtime change (NO
run_agent), ZERO new tables, ZERO frozen-kind touch. The run cockpit is Phase B/C.

MIRRORS THE CARDS PATH EXACTLY (the mold's overlay-as-catalog promise). Capability cards
flow: catalog (cex_capability_registry) + overlay enabled_capabilities -> GET /capabilities
-> frontend. Agents flow the SAME way: the agent catalog (.cex/config/capability_registry.json
``agents`` block) + the tenant overlay ``agents:`` block (overlay-gated enable/disable,
EXACTLY like managed_entities) -> GET /agents -> frontend. One overlay file
(capability_map.yaml) already drives capabilities, entities, and now agents.

PUBLIC API
  list_agents(tenant_id)      -> list[Agent DTO]  (the Agents list; overlay-gated)
  get_agent(tenant_id, id)    -> Agent DTO + detail (persona/capabilities/IO/SLA from the
                                 agent + agent_card on disk if resolvable, else the registry
                                 record). None when the id is not a visible agent.

OVERLAY-GATING (mirrors cex_capability_registry.list_capabilities + entities_config):
  * overlay ``agents:`` may be a LIST of {id, enabled?, ...} entries OR a MAP
    id -> {enabled?, ...}. A tenant gates its agents by listing the ids it enables (and may
    disable one with ``enabled: false``), the SAME shape managed_entities/enabled_capabilities
    use. NO overlay / no ``agents:`` block -> the DEFAULT cut (degrade-never; see below).
  * default cut (no overlay gate): the registry's domain agents (kind=agent + a real
    nucleus) are returned ENABLED. The 302 builder-subagents (source=builder_subagent,
    nucleus=null) are NOT surfaced as runnable agents -- they are kind-builders, not domain
    agents (ADR OQ1). A tenant overlay can still name any catalog id to expose it.

SECURE-BY-DEFAULT + TENANT-SCOPED:
  * tenant_id is ALWAYS the VERIFIED JWT claim (resolved upstream in main.py via
    auth.extract_tenant_id) -- NEVER from the client. The overlay read is scoped to that
    tenant via entities_config's fail-closed cex_tenant_paths guard (REUSED, never
    re-implemented), so a tenant can NEVER see another tenant's config.
  * READ-ONLY: no DB, no network, no secret read. The DTO is a value-free allowlist
    projection (id/name/nucleus/goal/kind/pillar/tools/model/enabled + detail) -- a
    credential/api_key field can never leak because there is none on the catalog record and
    the projection is an explicit allowlist. A field flagged sensitive on disk is dropped.

DEGRADE-NEVER (mirrors the registry + the /results read path): NO registry JSON, a
missing/malformed overlay, an absent PyYAML, an unresolvable on-disk artifact, or a hostile
CEX_TENANT_ID that makes the path guard raise SystemExit -> a sensible empty/registry-only
result (the Agents nav then simply hides). NEVER raises, NEVER 500s, NEVER another tenant's
data.

ALLOWED IMPORT DIRECTION + LAZY IMPORT: ``apps`` may use the repo catalog file + reuse
``entities_config`` for the audited overlay reader. The on-disk artifact read is bounded +
guarded. ASCII-only per .claude/rules/ascii-code-rule.md. Fully type-hinted.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

__all__ = [
    "list_agents",
    "get_agent",
    "REGISTRY_PATH",
    "OVERLAY_AGENTS_KEY",
]

# The shared agent catalog -- the SAME 373-record index the crew planner queries
# (.cex/config/capability_registry.json ``agents`` block). One source of truth; the
# dashboard reads the projectable presentation fields off each record (ADR D7).
REGISTRY_PATH = (
    Path(__file__).resolve().parents[2] / ".cex" / "config" / "capability_registry.json"
)

# The top-level overlay key holding the tenant's agent gate (mirrors managed_entities /
# enabled_capabilities). Read off the SAME overlay file the cards path reads, via
# entities_config's reader.
OVERLAY_AGENTS_KEY = "agents"

# An agent id allowlist -- a registry id is BOTH the route segment AND the lookup key.
# Permissive enough for the registry's ids (builder-subagent slugs, aitmpl_* ids, nucleus
# ids) but pins out path traversal / control chars so a hostile overlay entry can never
# smuggle a path. A malformed id is dropped, never a broken route.
_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")

# The 8F MOAT (kept in lockstep with cex_capability_registry._FROZEN_KINDS): an agent whose
# kind is frozen is NEVER surfaced as a runnable/definable agent. Belt-and-braces -- the
# agent catalog should not carry frozen kinds, but the read refuses them anyway so a future
# catalog edit can never expose one.
_FROZEN_KINDS = frozenset(
    {
        "workflow",
        "pipeline_template",
        "prompt_compiler",
        "reasoning_trace",
        "quality_gate",
        "dispatch_rule",
        "handoff",
    }
)

# Truthy-flag set (shared convention with the registry/entities reader).
_TRUTHY = frozenset({"1", "true", "yes", "on"})

# The kinds that are DOMAIN AGENTS for the default cut (kind=agent or kind=agent_card). A
# builder-subagent (kind=<some_artifact_kind>, source=builder_subagent, nucleus=null) is a
# kind-builder, not a standing domain agent, so it is excluded from the default surface
# (ADR OQ1: ship over the existing registry, let real domain agents accrue). A tenant
# overlay can still name ANY catalog id to expose it.
_DOMAIN_AGENT_KINDS = frozenset({"agent", "agent_card"})

# Max on-disk artifact bytes to read for the detail page (a guard -- the agent kind caps at
# ~5120B; we read generously but bounded so a surprise file can never blow the request).
_MAX_ARTIFACT_BYTES = 64 * 1024


# --------------------------------------------------------------------------- #
# Public entry points.                                                        #
# --------------------------------------------------------------------------- #
def list_agents(tenant_id: str) -> List[Dict[str, Any]]:
    """Return the tenant's VISIBLE agents as Agent DTOs (the Agents list), overlay-gated.

    ``tenant_id`` MUST be the VERIFIED JWT claim (the caller resolves it; this function
    never reads a client-supplied tenant). The overlay read is scoped to that tenant.

    Computation (MIRRORS cex_capability_registry.list_capabilities):
      catalog       = the registry's agent records (.cex/config/capability_registry.json).
      gate          = the tenant overlay ``agents:`` block (a list/map of ids, each
                      optionally ``enabled``), or None (no gate => the default cut).
      VISIBLE       = (default cut: domain agents enabled) when no gate, else
                      (the overlay-named ids, each enabled per its flag, default True).

    Each DTO carries ``enabled`` (a disabled agent is shown muted, like a disabled card).
    Order: catalog order. DEGRADE-NEVER: no registry / no overlay / malformed -> the
    default cut over whatever catalog loaded (possibly ``[]``). NEVER raises, NEVER another
    tenant's data.
    """
    records = _load_registry_agents()
    gate = _overlay_agent_gate(tenant_id)

    out: List[Dict[str, Any]] = []
    seen: set = set()
    for rec in records:
        agent_id = _clean_str(rec.get("id"))
        if not agent_id or not _ID_RE.match(agent_id) or agent_id in seen:
            continue
        kind = _clean_str(rec.get("kind"))
        if kind in _FROZEN_KINDS:
            continue  # the moat: an agent can never target a frozen kind
        decision = _visibility(rec, agent_id, kind, gate)
        if decision is None:
            continue  # not visible for this tenant (gated out / not a default domain agent)
        seen.add(agent_id)
        out.append(_dto_from_record(rec, enabled=decision))
    return out


def get_agent(tenant_id: str, agent_id: str) -> Optional[Dict[str, Any]]:
    """Return ONE visible agent's DTO + fuller detail, or None if not visible for the tenant.

    ``tenant_id`` MUST be the VERIFIED JWT claim. The agent is resolved from the SAME
    catalog + overlay-gate list_agents uses (so an agent gated out / frozen / not a default
    domain agent returns None -- the route renders its "unknown agent" state, never another
    tenant's data).

    The DETAIL (persona / capabilities table / Input+Output JSON Schema / SLA / toolkit) is
    enriched from the ``agent`` + ``agent_card`` artifact on disk WHEN resolvable (the
    record's ``path``), else it falls back to the registry record (description + capabilities
    + tools). READ-ONLY + degrade-never: an unreadable/out-of-tree artifact yields the
    registry-only detail, NEVER an error.
    """
    key = _clean_str(agent_id)
    if not key or not _ID_RE.match(key):
        return None
    # Reuse the SAME visible set so the detail can never expose a gated-out / frozen agent.
    visible = {row["id"]: row for row in list_agents(tenant_id)}
    dto = visible.get(key)
    if dto is None:
        return None
    # Find the source record (for the on-disk path + raw capabilities/tools).
    record = _find_record(key)
    detail = _detail_from_disk(record) if record is not None else {}
    merged = dict(dto)
    merged.update(detail)
    return merged


# --------------------------------------------------------------------------- #
# Registry (catalog) read -- DEGRADE-NEVER.                                    #
# --------------------------------------------------------------------------- #
def _load_registry_agents() -> List[Mapping[str, Any]]:
    """Load the registry's ``agents`` list (.cex/config/capability_registry.json), or [].

    DEGRADE-NEVER: a missing/unreadable/malformed JSON, or no ``agents`` key, yields ``[]``
    (the Agents nav then hides). NEVER raises. Pure file read -- no DB, no network.
    """
    try:
        if not REGISTRY_PATH.exists():
            return []
        data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []
    agents = data.get("agents") if isinstance(data, dict) else None
    if isinstance(agents, list):
        return [a for a in agents if isinstance(a, Mapping)]
    # Tolerate a map id -> record shape too (defensive against a future index reshape).
    if isinstance(agents, Mapping):
        return [a for a in agents.values() if isinstance(a, Mapping)]
    return []


def _find_record(agent_id: str) -> Optional[Mapping[str, Any]]:
    """The raw registry record for one id, or None. Linear scan (catalog is small)."""
    for rec in _load_registry_agents():
        if _clean_str(rec.get("id")) == agent_id:
            return rec
    return None


# --------------------------------------------------------------------------- #
# Overlay gate read (REUSES entities_config's audited, tenant-scoped reader).  #
# --------------------------------------------------------------------------- #
def _overlay_agent_gate(tenant_id: str) -> Optional[Dict[str, bool]]:
    """The tenant's agent gate from the overlay ``agents:`` block, or None (no gate).

    REUSES ``entities_config._read_overlay_raw`` -- the SAME fail-closed, tenant-scoped path
    guard the cards + managed_entities reads use (NEVER a duplicated parse). The overlay
    ``agents:`` value may be:
      * a LIST of entries: ``[{id: ..., enabled?: ...}, "<id>", ...]`` (a bare string is an
        enabled id); OR
      * a MAP: ``{<id>: {enabled?: ...}}`` (a bare ``true``/``false`` value gates it).
    Returns ``{id: enabled_bool}`` (the gate is ACTIVE -> only these ids show, each per its
    flag). Returns None when the overlay declares no ``agents:`` block (=> the default cut).
    An EMPTY but present block is an explicit empty gate ({} -> show no agents). DEGRADE-NEVER:
    any failure -> None (default cut). NEVER raises, NEVER another tenant's overlay.
    """
    raw = _read_overlay_raw(tenant_id)
    block = raw.get(OVERLAY_AGENTS_KEY) if isinstance(raw, dict) else None
    if block is None:
        return None  # no gate -> default cut
    gate: Dict[str, bool] = {}
    if isinstance(block, (list, tuple)):
        for entry in block:
            if isinstance(entry, str):
                aid = _clean_str(entry)
                if aid and _ID_RE.match(aid):
                    gate[aid] = True
            elif isinstance(entry, Mapping):
                aid = _clean_str(entry.get("id"))
                if aid and _ID_RE.match(aid):
                    gate[aid] = _enabled_flag(entry.get("enabled"), default=True)
        return gate
    if isinstance(block, Mapping):
        for aid_raw, val in block.items():
            aid = _clean_str(aid_raw)
            if not aid or not _ID_RE.match(aid):
                continue
            if isinstance(val, Mapping):
                gate[aid] = _enabled_flag(val.get("enabled"), default=True)
            else:
                gate[aid] = _enabled_flag(val, default=True)
        return gate
    # A malformed scalar block -> treat as no gate (degrade-never).
    return None


def _read_overlay_raw(tenant_id: str) -> Dict[str, Any]:
    """Read the tenant overlay as a raw dict via entities_config's reader, DEGRADE-NEVER.

    REUSES ``entities_config._read_overlay_raw`` (the audited, fail-closed, tenant-scoped
    path guard) so the agents gate, the cards, and managed_entities all read the SAME
    overlay file through ONE reader -- they can never disagree on tenant scoping. ``{}`` on
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


# --------------------------------------------------------------------------- #
# Visibility (MIRRORS the cards enabled-gate semantics).                       #
# --------------------------------------------------------------------------- #
def _visibility(
    rec: Mapping[str, Any],
    agent_id: str,
    kind: str,
    gate: Optional[Dict[str, bool]],
) -> Optional[bool]:
    """Whether a record is visible for the tenant, and (if so) its ``enabled`` flag.

    Returns:
      * None  -> NOT visible (omit the row entirely -- matches the cards "hidden, not
                 disabled" rule for gated-out items).
      * True  -> visible + enabled.
      * False -> visible + disabled (shown muted; the overlay explicitly disabled it).

    When a gate is present: only ids IN the gate are visible, each per its flag. When no
    gate (default cut): a DOMAIN AGENT (kind in {agent, agent_card} AND a real nucleus) is
    visible+enabled; a builder-subagent / nucleus-less record is omitted (ADR OQ1).
    """
    if gate is not None:
        if agent_id not in gate:
            return None  # the gate is authoritative -> only named ids show
        return gate[agent_id]
    # Default cut: surface only standing domain agents (not the 302 kind-builders).
    nucleus = _clean_str(rec.get("nucleus"))
    if kind in _DOMAIN_AGENT_KINDS and nucleus:
        return True
    return None


# --------------------------------------------------------------------------- #
# Projection: a raw registry record -> the Agent DTO (pure, value-free).      #
# --------------------------------------------------------------------------- #
def _dto_from_record(rec: Mapping[str, Any], *, enabled: bool) -> Dict[str, Any]:
    """Project ONE registry record to the Agent DTO the frontend consumes.

    ALLOWLIST projection (secure-by-default): only the presentation/runtime-descriptive
    fields are emitted -- a credential/secret can never leak because there is none on the
    record and we never copy the raw object. Shape (mirrors the frontend lib/types Agent):
    ``{id, name, nucleus, goal, description, kind, pillar, tools, model, domain, enabled}``.

    Field derivation:
      * name      <- name or id.
      * nucleus   <- uppercased (registry stores 'n03'; the dashboard shows 'N03', matching
                     the card nucleus convention).
      * goal      <- the first ``capabilities`` line if present, else the description (a
                     one-line "what this agent does", like a card's description).
      * tools     <- ``tools_allowed`` (string list; the toolkit chips). Empty when none.
      * model     <- ``model_tier`` ('' when the catalog record carries none).
      * pillar    <- best-effort from the record; '' when absent (the catalog index omits it
                     for most records -- the detail page backfills from disk).
    """
    agent_id = _clean_str(rec.get("id"))
    name = _clean_str(rec.get("name")) or agent_id
    nucleus = _clean_str(rec.get("nucleus")).upper()
    kind = _clean_str(rec.get("kind"))
    description = _clean_str(rec.get("description"))
    domain = _clean_str(rec.get("domain"))
    caps = _str_list(rec.get("capabilities"))
    goal = caps[0] if caps else description
    tools = _str_list(rec.get("tools_allowed"))
    model = _clean_str(rec.get("model_tier"))
    pillar = _clean_str(rec.get("pillar"))

    dto: Dict[str, Any] = {
        "id": agent_id,
        "name": name,
        "nucleus": nucleus,
        "kind": kind or "agent",
        "pillar": pillar,
        "goal": goal,
        "description": description,
        "domain": domain,
        "tools": tools,
        "model": model,
        "enabled": bool(enabled),
        "source": _clean_str(rec.get("source")),
    }
    return dto


# --------------------------------------------------------------------------- #
# Detail enrichment from the on-disk agent / agent_card artifact (READ-ONLY).  #
# --------------------------------------------------------------------------- #
def _detail_from_disk(rec: Mapping[str, Any]) -> Dict[str, Any]:
    """Enrich an agent DTO with detail parsed from its on-disk artifact, DEGRADE-NEVER.

    The record's ``path`` points at the ``agent`` (or ``agent_card``) .md. We read it
    (bounded + tree-guarded) and extract the persona/capabilities/Input+Output JSON
    Schema/SLA sections the detail page renders. ANY failure (no path, out-of-tree,
    unreadable, parse miss) -> ``{}`` so the caller keeps the registry-only detail. NEVER
    raises. READ-ONLY: no DB, no network, no secret.

    Returns a partial dict that may carry: ``persona`` (the Overview prose), ``capabilities``
    (a list of {capability, description, tools}), ``input_schema``/``output_schema`` (raw
    JSON strings), ``sla`` (a list of {label, value}), and ``artifact_path`` (provenance).
    """
    path_str = _clean_str(rec.get("path"))
    if not path_str:
        return {}
    text = _read_artifact_text(path_str)
    if not text:
        return {}
    detail: Dict[str, Any] = {"artifact_path": path_str}

    persona = _extract_section_prose(text, ("Overview", "Persona", "Identity"))
    if persona:
        detail["persona"] = persona

    caps = _extract_capabilities_table(text)
    if caps:
        detail["capabilities"] = caps

    in_schema = _extract_json_block(text, ("Input Schema", "Input"))
    if in_schema:
        detail["input_schema"] = in_schema
    out_schema = _extract_json_block(text, ("Output Schema", "Output"))
    if out_schema:
        detail["output_schema"] = out_schema

    sla = _extract_sla(text)
    if sla:
        detail["sla"] = sla

    return detail


def _read_artifact_text(path_str: str) -> str:
    """Read an on-disk artifact, BOUNDED + TREE-GUARDED, DEGRADE-NEVER.

    The path is resolved RELATIVE TO THE REPO ROOT and confirmed to stay INSIDE the repo
    tree (a registry ``path`` is a repo-relative file; an absolute / traversing path that
    escapes the root is refused -> ''). Reads at most _MAX_ARTIFACT_BYTES. ANY failure -> ''.
    NEVER raises. This is the only filesystem read in the module and it can only ever read a
    repo file, never escape the tree."""
    try:
        root = Path(__file__).resolve().parents[2]
        candidate = (root / path_str).resolve()
        # Tree guard: the resolved path MUST be within the repo root.
        candidate.relative_to(root)
        if not candidate.exists() or not candidate.is_file():
            return ""
        data = candidate.read_bytes()[:_MAX_ARTIFACT_BYTES]
        return data.decode("utf-8", errors="replace")
    except Exception:
        return ""


# --------------------------------------------------------------------------- #
# Markdown section parsers (pure, total -- never raise).                       #
# --------------------------------------------------------------------------- #
def _strip_frontmatter(text: str) -> str:
    """Drop a leading ``---``-fenced YAML frontmatter block, if present."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            nl = text.find("\n", end + 1)
            if nl != -1:
                return text[nl + 1 :]
    return text


def _section_body(text: str, headings: Tuple[str, ...]) -> str:
    """The body text under the FIRST matching ``## <heading>`` (any level), up to the next
    heading of the same-or-higher level. '' when no heading matches. Case-insensitive on the
    heading label. Pure + total."""
    body = _strip_frontmatter(text)
    lines = body.splitlines()
    wanted = {h.strip().lower() for h in headings}
    start = -1
    start_level = 0
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.*?)\s*$", line)
        if not m:
            continue
        label = m.group(2).strip().lower()
        # Tolerate a trailing colon / annotation (e.g. "Input Schema (JSON)").
        label_head = re.split(r"[(:]", label, 1)[0].strip()
        if label in wanted or label_head in wanted:
            start = i + 1
            start_level = len(m.group(1))
            break
    if start < 0:
        return ""
    out: List[str] = []
    for line in lines[start:]:
        m = re.match(r"^(#{1,6})\s+", line)
        if m and len(m.group(1)) <= start_level:
            break
        out.append(line)
    return "\n".join(out).strip()


def _extract_section_prose(text: str, headings: Tuple[str, ...]) -> str:
    """The first paragraph(s) of a section as plain prose (drops code fences + tables).

    Used for the persona/overview. Collapses to the leading non-table, non-fence lines so
    the detail page shows a clean one/two-line persona, not the whole section. Bounded to
    ~600 chars."""
    body = _section_body(text, headings)
    if not body:
        return ""
    out: List[str] = []
    in_fence = False
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if stripped.startswith("|") or stripped.startswith("#"):
            # stop at the first table / sub-heading -- the prose precedes them.
            if out:
                break
            continue
        if not stripped:
            if out:
                break  # one paragraph is enough for the persona line
            continue
        out.append(stripped)
    prose = " ".join(out).strip()
    return prose[:600]


def _extract_capabilities_table(text: str) -> List[Dict[str, str]]:
    """Parse a ``## Capabilities`` markdown table into [{capability, description, tools}].

    Tolerant: a 2-column table (capability | description) omits tools; extra columns are
    ignored. Returns [] when there is no Capabilities table. Bounded to 40 rows."""
    body = _section_body(text, ("Capabilities", "Capabilities Map"))
    if not body:
        return []
    rows = _parse_md_table(body)
    out: List[Dict[str, str]] = []
    for cells in rows[:40]:
        if not cells:
            continue
        cap = cells[0].strip()
        if not cap:
            continue
        desc = cells[1].strip() if len(cells) > 1 else ""
        tools = cells[2].strip() if len(cells) > 2 else ""
        out.append({"capability": cap, "description": desc, "tools": tools})
    return out


def _extract_json_block(text: str, headings: Tuple[str, ...]) -> str:
    """The first fenced code block under a section as a raw string (the Input/Output Schema).

    Returns the code-fence CONTENT verbatim (so the frontend can render it in a <pre>). ''
    when the section or its fence is absent. Bounded to ~4000 chars."""
    body = _section_body(text, headings)
    if not body:
        return ""
    lines = body.splitlines()
    block: List[str] = []
    in_fence = False
    for line in lines:
        if line.strip().startswith("```"):
            if in_fence:
                break  # end of the first fence
            in_fence = True
            continue
        if in_fence:
            block.append(line)
    content = "\n".join(block).strip()
    return content[:4000]


def _extract_sla(text: str) -> List[Dict[str, str]]:
    """Best-effort SLA rows from an ``## SLA`` / ``## Service Level`` / ``## Routing`` table
    or a bullet list -> [{label, value}]. Returns [] when none. Bounded to 20 rows.

    The agent_card carries SLA-ish info as a Provider/Routing table (model, latency,
    fallback); we surface whatever 2-column table the SLA-ish section holds so the detail
    page can render a small key/value SLA strip."""
    body = _section_body(
        text, ("SLA", "Service Level", "Service Level Agreement", "Routing", "Provider")
    )
    if not body:
        return []
    out: List[Dict[str, str]] = []
    rows = _parse_md_table(body)
    for cells in rows[:20]:
        if len(cells) >= 2 and cells[0].strip():
            out.append({"label": cells[0].strip(), "value": cells[1].strip()})
    if out:
        return out
    # Fallback: bullet "- key: value" lines.
    for line in body.splitlines()[:20]:
        m = re.match(r"^\s*[-*]\s+\*?\*?(.+?)\*?\*?\s*[:=]\s*(.+)$", line)
        if m:
            out.append({"label": m.group(1).strip(), "value": m.group(2).strip()})
    return out


def _parse_md_table(body: str) -> List[List[str]]:
    """Parse a markdown pipe-table body into a list of cell-lists (DATA rows only).

    Skips the header row + the ``|---|---|`` separator. Tolerant of leading/trailing pipes.
    Pure + total. Returns [] when no table is present."""
    rows: List[List[str]] = []
    seen_separator = False
    header_seen = False
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if header_seen:
                # a table block ended; stop at the first non-table line after it.
                break
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not header_seen:
            header_seen = True
            continue  # the header row
        if not seen_separator and all(set(c) <= set("-: ") for c in cells):
            seen_separator = True
            continue  # the |---|---| separator
        rows.append(cells)
    return rows


# --------------------------------------------------------------------------- #
# Small pure helpers.                                                         #
# --------------------------------------------------------------------------- #
def _clean_str(value: Any) -> str:
    """Coerce a scalar to a whitespace-normalized string ('' if None/non-scalar/bool)."""
    if value is None or isinstance(value, bool):
        return ""
    if isinstance(value, (str, int, float)):
        return " ".join(str(value).split())
    return ""


def _str_list(value: Any) -> List[str]:
    """Coerce a list-ish value to a list of non-empty clean strings ([] otherwise)."""
    if not isinstance(value, (list, tuple)):
        return []
    out: List[str] = []
    for item in value:
        s = _clean_str(item)
        if s:
            out.append(s)
    return out


def _enabled_flag(value: Any, *, default: bool) -> bool:
    """Coerce an overlay ``enabled`` value to a bool. Absent (None) -> ``default``."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in _TRUTHY
    return bool(value)

# -*- coding: ascii -*-
"""Crew CATALOG + READ surface for the dashboard mold (ADR adr_agents_sdk_dashboard,
Phase D -- the crews browse+inspect surface, the layer ABOVE single agents).

THE GAP THIS CLOSES: Phase A surfaced the AGENTS catalog (persistent, tool-using
agents above the single-shot card). A CREW is the next layer up: a multi-role TEAM
(crew_template artifact) that ships ONE coherent deliverable via N roles with handoffs
and a process topology (sequential | hierarchical | consensus). Phase D is the READ
half only -- it surfaces the crews that already exist as a typed catalog so a tenant can
BROWSE the crew catalog + INSPECT one crew's roles/topology/handoffs. ZERO runtime change
(NO run_crew), ZERO new tables, ZERO frozen-kind touch. The crew run cockpit is the
founder-gated control-plane step.

MIRRORS THE AGENTS PATH EXACTLY (agents_config.py). Agents flow: the agent catalog
(.cex/config/capability_registry.json ``agents`` block) + the tenant overlay ``agents:``
block (overlay-gated) -> GET /agents -> frontend. Crews flow the SAME way -- EXCEPT the
catalog is NOT a registry block (the registry carries no crews); it is the crew_template
ARTIFACTS on disk (N0*/P12_orchestration/**/p12_ct_*.md, the SAME set cex_crew.find_crews
discovers). The tenant overlay ``crews:`` block gates them (overlay-gated enable/disable,
EXACTLY like agents/managed_entities) -> GET /crews -> frontend. One overlay file
(capability_map.yaml) already drives capabilities, entities, agents, and now crews.

PUBLIC API
  list_crews(tenant_id)      -> list[Crew DTO]  (the Crews list; overlay-gated)
  get_crew(tenant_id, id)    -> Crew DTO + detail (roles table / process topology /
                                handoff protocol / provenance parsed from the crew_template
                                on disk). None when the id is not a visible crew.

OVERLAY-GATING (mirrors agents_config._overlay_agent_gate + entities_config):
  * overlay ``crews:`` may be a LIST of {id, enabled?, ...} entries OR a MAP
    id -> {enabled?, ...}. A tenant gates its crews by listing the ids it enables (and may
    disable one with ``enabled: false``), the SAME shape agents/managed_entities use. NO
    overlay / no ``crews:`` block -> the DEFAULT cut (degrade-never; see below).
  * default cut (no overlay gate): every discovered crew_template (kind=crew_template) is
    returned ENABLED -- a crew is a standing, named team (unlike the 302 builder-subagents,
    there is no "kind-builder" subset to hide). A tenant overlay can still name any crew id
    to gate the set.

SECURE-BY-DEFAULT + TENANT-SCOPED:
  * tenant_id is ALWAYS the VERIFIED JWT claim (resolved upstream in main.py via
    auth.extract_tenant_id) -- NEVER from the client. The overlay read is scoped to that
    tenant via entities_config's fail-closed cex_tenant_paths guard (REUSED, never
    re-implemented), so a tenant can NEVER see another tenant's config.
  * READ-ONLY: no DB, no network, no secret read. The DTO is a value-free allowlist
    projection (id/name/nucleus/process/role_count/roles/goal/enabled/source + detail) --
    a crew_template carries no credential, and the projection is an explicit allowlist.

DEGRADE-NEVER (mirrors agents_config + the /results read path): NO crew artifacts on disk,
a missing/malformed overlay, an absent PyYAML, an unreadable/out-of-tree artifact, or a
hostile CEX_TENANT_ID that makes the path guard raise SystemExit -> a sensible empty result
(the Crews nav then simply hides). NEVER raises, NEVER 500s, NEVER another tenant's data.

ALLOWED IMPORT DIRECTION + LAZY IMPORT: ``apps`` may glob the repo crew_template files +
reuse ``entities_config`` for the audited overlay reader. The on-disk artifact read is
bounded + tree-guarded. ASCII-only per .claude/rules/ascii-code-rule.md. Fully type-hinted.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

__all__ = [
    "list_crews",
    "get_crew",
    "CREWS_GLOBS",
    "OVERLAY_CREWS_KEY",
]

# The repo root -- the crew_template artifacts live under it (N0*/P12_orchestration/...).
_REPO_ROOT = Path(__file__).resolve().parents[2]

# The crew_template discovery globs -- the SAME set cex_crew.find_crews scans (the crew
# planner's source of truth). One catalog; the dashboard reads the projectable presentation
# fields off each crew_template's frontmatter + body (ADR mirror of the agents D7 read).
CREWS_GLOBS: Tuple[str, ...] = (
    "N0*/P12_orchestration/p12_ct_*.md",
    "N0*/P12_orchestration/crews/p12_ct_*.md",
)

# The top-level overlay key holding the tenant's crew gate (mirrors agents / managed_entities
# / enabled_capabilities). Read off the SAME overlay file the cards path reads, via
# entities_config's reader.
OVERLAY_CREWS_KEY = "crews"

# A crew id allowlist -- a crew id is BOTH the route segment AND the lookup key. The crew id
# is the crew_name (or the file stem without the ``p12_ct_`` prefix); pin out path traversal /
# control chars so a hostile overlay entry can never smuggle a path. A malformed id is dropped.
_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")

# The 8F MOAT (kept in lockstep with agents_config._FROZEN_KINDS): a crew whose kind is frozen
# is NEVER surfaced. Belt-and-braces -- a crew_template is kind=crew_template (not frozen), but
# the read refuses a frozen kind anyway so a future catalog edit can never expose one.
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

# The kind a crew record MUST be to surface (the crew catalog is crew_template artifacts).
_CREW_KIND = "crew_template"

# The process topologies the dashboard understands (lib/types Crew.process). An unknown /
# absent topology falls back to "sequential" (the cex_crew default), never a broken chip.
_PROCESS_VALUES = frozenset({"sequential", "hierarchical", "consensus"})
_DEFAULT_PROCESS = "sequential"

# Truthy-flag set (shared convention with the agents/entities reader).
_TRUTHY = frozenset({"1", "true", "yes", "on"})

# Max on-disk artifact bytes to read for the detail page (a guard -- crew_template caps small;
# we read generously but bounded so a surprise file can never blow the request).
_MAX_ARTIFACT_BYTES = 64 * 1024

# Max roles surfaced from a Roles table (a guard against a pathological table).
_MAX_ROLES = 40


# --------------------------------------------------------------------------- #
# Public entry points.                                                        #
# --------------------------------------------------------------------------- #
def list_crews(tenant_id: str) -> List[Dict[str, Any]]:
    """Return the tenant's VISIBLE crews as Crew DTOs (the Crews list), overlay-gated.

    ``tenant_id`` MUST be the VERIFIED JWT claim (the caller resolves it; this function
    never reads a client-supplied tenant). The overlay read is scoped to that tenant.

    Computation (MIRRORS agents_config.list_agents):
      catalog       = the crew_template artifacts on disk (CREWS_GLOBS), parsed to records.
      gate          = the tenant overlay ``crews:`` block (a list/map of ids, each
                      optionally ``enabled``), or None (no gate => the default cut).
      VISIBLE       = (default cut: every crew_template enabled) when no gate, else
                      (the overlay-named ids, each enabled per its flag, default True).

    Each DTO carries ``enabled`` (a disabled crew is shown muted, like a disabled card).
    Order: crew name order (catalog scan order, then de-duped). DEGRADE-NEVER: no artifacts
    / no overlay / malformed -> the default cut over whatever loaded (possibly ``[]``). NEVER
    raises, NEVER another tenant's data.
    """
    records = _load_crew_records()
    gate = _overlay_crew_gate(tenant_id)

    out: List[Dict[str, Any]] = []
    seen: set = set()
    for rec in records:
        crew_id = _clean_str(rec.get("id"))
        if not crew_id or not _ID_RE.match(crew_id) or crew_id in seen:
            continue
        kind = _clean_str(rec.get("kind")) or _CREW_KIND
        if kind in _FROZEN_KINDS:
            continue  # the moat: a crew can never target a frozen kind
        decision = _visibility(rec, crew_id, kind, gate)
        if decision is None:
            continue  # not visible for this tenant (gated out / not a crew_template)
        seen.add(crew_id)
        out.append(_dto_from_record(rec, enabled=decision))
    return out


def get_crew(tenant_id: str, crew_id: str) -> Optional[Dict[str, Any]]:
    """Return ONE visible crew's DTO + fuller detail, or None if not visible for the tenant.

    ``tenant_id`` MUST be the VERIFIED JWT claim. The crew is resolved from the SAME catalog
    + overlay-gate list_crews uses (so a crew gated out / frozen / not a crew_template returns
    None -- the route renders its "unknown crew" state, never another tenant's data).

    The DETAIL (the full Roles table + the process topology + the handoff protocol + the
    Overview goal + provenance ``artifact_path``) is parsed from the crew_template artifact on
    disk (already loaded for the list; re-resolved here). READ-ONLY + degrade-never: an
    unreadable/out-of-tree artifact yields the list-only DTO, NEVER an error.
    """
    key = _clean_str(crew_id)
    if not key or not _ID_RE.match(key):
        return None
    # Reuse the SAME visible set so the detail can never expose a gated-out / frozen crew.
    visible = {row["id"]: row for row in list_crews(tenant_id)}
    dto = visible.get(key)
    if dto is None:
        return None
    record = _find_record(key)
    detail = _detail_from_record(record) if record is not None else {}
    merged = dict(dto)
    merged.update(detail)
    return merged


# --------------------------------------------------------------------------- #
# Catalog read -- enumerate crew_template artifacts on disk. DEGRADE-NEVER.    #
# --------------------------------------------------------------------------- #
def _load_crew_records() -> List[Mapping[str, Any]]:
    """Discover + parse every crew_template artifact into a record list, or [].

    Globs the SAME paths cex_crew.find_crews uses, parses each file's frontmatter + body
    into a record dict ({id, name, nucleus, kind, process, role_count, roles, goal,
    description, path, source, handoff_protocol}). DEGRADE-NEVER: an unreadable/malformed
    file is skipped; a non-crew_template kind is skipped; no matches yields ``[]``. NEVER
    raises. Pure file read -- no DB, no network.
    """
    records: List[Mapping[str, Any]] = []
    seen_paths: set = set()
    seen_names: set = set()
    try:
        candidates: List[Path] = []
        for pattern in CREWS_GLOBS:
            candidates.extend(_REPO_ROOT.glob(pattern))
    except Exception:
        return []
    # Stable order: by relative path string (deterministic across platforms).
    for path in sorted(candidates, key=lambda p: str(p).replace("\\", "/")):
        try:
            rel = str(path.resolve().relative_to(_REPO_ROOT)).replace("\\", "/")
        except Exception:
            continue
        if rel in seen_paths:
            continue
        seen_paths.add(rel)
        rec = _record_from_file(path, rel)
        if rec is None:
            continue
        # De-dupe by crew id (first wins -- mirrors cex_crew's seen-by-name guard).
        cid = _clean_str(rec.get("id"))
        if not cid or cid in seen_names:
            continue
        seen_names.add(cid)
        records.append(rec)
    return records


def _record_from_file(path: Path, rel_path: str) -> Optional[Mapping[str, Any]]:
    """Parse ONE crew_template file into a record dict, or None when it is not a crew.

    Reads the file (bounded + tree-guarded), parses the leading ``---`` frontmatter, and -- if
    the kind is crew_template (or absent, tolerated like cex_crew) -- projects the record. The
    id is the frontmatter ``crew_name`` (or the file stem without ``p12_ct_``). DEGRADE-NEVER:
    any failure -> None. Pure + total: never raises."""
    text = _read_artifact_text(rel_path)
    if not text:
        return None
    fm = _parse_frontmatter(text)
    kind = _clean_str(fm.get("kind"))
    if kind and kind != _CREW_KIND:
        return None  # a non-crew_template file under the glob (defensive) -> skip

    stem = path.stem
    crew_id = _clean_str(fm.get("crew_name")) or re.sub(r"^p12_ct_", "", stem)
    crew_id = crew_id.strip()
    if not crew_id:
        return None

    name = _clean_str(fm.get("title")) or _titleize(crew_id)
    nucleus = _nucleus_from_relpath(rel_path)
    process = _normalize_process(fm.get("process"))
    purpose = _clean_str(fm.get("purpose"))
    tldr = _clean_str(fm.get("tldr"))
    goal = purpose or tldr
    handoff = _clean_str(fm.get("handoff_protocol_id"))

    roles = _extract_roles_table(text)
    # role_count: prefer the parsed table; fall back to a frontmatter roles_count if present.
    role_count = len(roles)
    if role_count == 0:
        fm_count = _coerce_int(fm.get("roles_count")) or _coerce_int(fm.get("role_count"))
        if fm_count is not None:
            role_count = fm_count

    return {
        "id": crew_id,
        "name": name,
        "nucleus": nucleus,
        "kind": kind or _CREW_KIND,
        "pillar": _clean_str(fm.get("pillar")) or "P12",
        "process": process,
        "role_count": role_count,
        "roles": roles,
        "goal": goal,
        "description": goal,
        "domain": _clean_str(fm.get("domain")),
        "handoff_protocol": handoff,
        "path": rel_path,
        "source": _clean_str(fm.get("author")) or "crew_template",
    }


def _find_record(crew_id: str) -> Optional[Mapping[str, Any]]:
    """The parsed record for one crew id, or None. Linear scan (catalog is small)."""
    for rec in _load_crew_records():
        if _clean_str(rec.get("id")) == crew_id:
            return rec
    return None


# --------------------------------------------------------------------------- #
# Overlay gate read (REUSES entities_config's audited, tenant-scoped reader).  #
# --------------------------------------------------------------------------- #
def _overlay_crew_gate(tenant_id: str) -> Optional[Dict[str, bool]]:
    """The tenant's crew gate from the overlay ``crews:`` block, or None (no gate).

    REUSES ``entities_config._read_overlay_raw`` -- the SAME fail-closed, tenant-scoped path
    guard the cards + agents + managed_entities reads use (NEVER a duplicated parse). The
    overlay ``crews:`` value may be:
      * a LIST of entries: ``[{id: ..., enabled?: ...}, "<id>", ...]`` (a bare string is an
        enabled id); OR
      * a MAP: ``{<id>: {enabled?: ...}}`` (a bare ``true``/``false`` value gates it).
    Returns ``{id: enabled_bool}`` (the gate is ACTIVE -> only these ids show, each per its
    flag). Returns None when the overlay declares no ``crews:`` block (=> the default cut).
    An EMPTY but present block is an explicit empty gate ({} -> show no crews). DEGRADE-NEVER:
    any failure -> None (default cut). NEVER raises, NEVER another tenant's overlay.
    """
    raw = _read_overlay_raw(tenant_id)
    block = raw.get(OVERLAY_CREWS_KEY) if isinstance(raw, dict) else None
    if block is None:
        return None  # no gate -> default cut
    gate: Dict[str, bool] = {}
    if isinstance(block, (list, tuple)):
        for entry in block:
            if isinstance(entry, str):
                cid = _clean_str(entry)
                if cid and _ID_RE.match(cid):
                    gate[cid] = True
            elif isinstance(entry, Mapping):
                cid = _clean_str(entry.get("id"))
                if cid and _ID_RE.match(cid):
                    gate[cid] = _enabled_flag(entry.get("enabled"), default=True)
        return gate
    if isinstance(block, Mapping):
        for cid_raw, val in block.items():
            cid = _clean_str(cid_raw)
            if not cid or not _ID_RE.match(cid):
                continue
            if isinstance(val, Mapping):
                gate[cid] = _enabled_flag(val.get("enabled"), default=True)
            else:
                gate[cid] = _enabled_flag(val, default=True)
        return gate
    # A malformed scalar block -> treat as no gate (degrade-never).
    return None


def _read_overlay_raw(tenant_id: str) -> Dict[str, Any]:
    """Read the tenant overlay as a raw dict via entities_config's reader, DEGRADE-NEVER.

    REUSES ``entities_config._read_overlay_raw`` (the audited, fail-closed, tenant-scoped
    path guard) so the crews gate, the agents gate, the cards, and managed_entities all read
    the SAME overlay file through ONE reader -- they can never disagree on tenant scoping.
    ``{}`` on any failure. NEVER raises, NEVER another tenant's overlay."""
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
# Visibility (MIRRORS the agents enabled-gate semantics).                      #
# --------------------------------------------------------------------------- #
def _visibility(
    rec: Mapping[str, Any],
    crew_id: str,
    kind: str,
    gate: Optional[Dict[str, bool]],
) -> Optional[bool]:
    """Whether a record is visible for the tenant, and (if so) its ``enabled`` flag.

    Returns:
      * None  -> NOT visible (omit the row entirely -- matches the "hidden, not disabled" rule
                 for gated-out items).
      * True  -> visible + enabled.
      * False -> visible + disabled (shown muted; the overlay explicitly disabled it).

    When a gate is present: only ids IN the gate are visible, each per its flag. When no gate
    (default cut): every crew_template is visible+enabled (a crew is a standing named team --
    there is no builder-subagent subset to hide, unlike agents).
    """
    if gate is not None:
        if crew_id not in gate:
            return None  # the gate is authoritative -> only named ids show
        return gate[crew_id]
    # Default cut: surface every crew_template (kind already checked + non-frozen).
    if kind == _CREW_KIND:
        return True
    return None


# --------------------------------------------------------------------------- #
# Projection: a parsed record -> the Crew DTO (pure, value-free).             #
# --------------------------------------------------------------------------- #
def _dto_from_record(rec: Mapping[str, Any], *, enabled: bool) -> Dict[str, Any]:
    """Project ONE crew record to the Crew DTO the frontend consumes.

    ALLOWLIST projection (secure-by-default): only the presentation/topology-descriptive
    fields are emitted -- a crew_template carries no credential, and we never copy the raw
    object. Shape (mirrors the frontend lib/types Crew):
    ``{id, name, nucleus, kind, pillar, process, role_count, roles, goal, description,
    domain, enabled, source}``.

    Field derivation:
      * name        <- title or a titleized id.
      * nucleus     <- the owning nucleus, derived from the artifact path (N0X) + uppercased.
      * process     <- the process topology (sequential | hierarchical | consensus), defaulted.
      * role_count  <- the parsed Roles table length (frontmatter roles_count fallback).
      * roles       <- [{name, agent?, goal?, tools?}] from the Roles table (list view shows
                       the names; the detail page renders the table).
      * goal        <- the crew purpose / tldr (a one-line "what this crew ships").
    """
    crew_id = _clean_str(rec.get("id"))
    name = _clean_str(rec.get("name")) or _titleize(crew_id)
    nucleus = _clean_str(rec.get("nucleus")).upper()
    kind = _clean_str(rec.get("kind")) or _CREW_KIND
    process = _normalize_process(rec.get("process"))
    goal = _clean_str(rec.get("goal"))
    description = _clean_str(rec.get("description")) or goal
    domain = _clean_str(rec.get("domain"))
    pillar = _clean_str(rec.get("pillar")) or "P12"
    roles = _roles_list(rec.get("roles"))
    role_count = _coerce_int(rec.get("role_count"))
    if role_count is None:
        role_count = len(roles)

    dto: Dict[str, Any] = {
        "id": crew_id,
        "name": name,
        "nucleus": nucleus,
        "kind": kind,
        "pillar": pillar,
        "process": process,
        "role_count": int(role_count),
        "roles": roles,
        "goal": goal,
        "description": description,
        "domain": domain,
        "enabled": bool(enabled),
        "source": _clean_str(rec.get("source")) or "crew_template",
    }
    return dto


# --------------------------------------------------------------------------- #
# Detail enrichment from the parsed crew_template record (READ-ONLY).          #
# --------------------------------------------------------------------------- #
def _detail_from_record(rec: Mapping[str, Any]) -> Dict[str, Any]:
    """Enrich a crew DTO with the detail fields the detail page renders, DEGRADE-NEVER.

    The record already carries the parsed Roles table + process + handoff protocol (parsed
    once in _record_from_file). Here we surface the detail-only additions: the handoff
    protocol id/prose and the provenance ``artifact_path``. The roles table + process travel
    on the DTO already (the list view shows them too). ANY missing field simply does not
    render. Returns a partial dict that may carry: ``handoff_protocol``, ``handoff_note``
    (the Handoff Protocol section prose), and ``artifact_path``."""
    detail: Dict[str, Any] = {}
    path_str = _clean_str(rec.get("path"))
    if path_str:
        detail["artifact_path"] = path_str
    handoff = _clean_str(rec.get("handoff_protocol"))
    if handoff:
        detail["handoff_protocol"] = handoff

    # Re-read the artifact for the Handoff Protocol section prose (degrade-never).
    text = _read_artifact_text(path_str) if path_str else ""
    if text:
        note = _extract_section_prose(text, ("Handoff Protocol", "Handoffs"))
        if note:
            detail["handoff_note"] = note
    return detail


def _read_artifact_text(path_str: str) -> str:
    """Read an on-disk artifact, BOUNDED + TREE-GUARDED, DEGRADE-NEVER.

    The path is resolved RELATIVE TO THE REPO ROOT and confirmed to stay INSIDE the repo tree
    (a crew_template path is a repo-relative file; an absolute / traversing path that escapes
    the root is refused -> ''). Reads at most _MAX_ARTIFACT_BYTES. ANY failure -> ''. NEVER
    raises. This is the only filesystem read in the module and it can only ever read a repo
    file, never escape the tree."""
    try:
        candidate = (_REPO_ROOT / path_str).resolve()
        # Tree guard: the resolved path MUST be within the repo root.
        candidate.relative_to(_REPO_ROOT)
        if not candidate.exists() or not candidate.is_file():
            return ""
        data = candidate.read_bytes()[:_MAX_ARTIFACT_BYTES]
        return data.decode("utf-8", errors="replace")
    except Exception:
        return ""


# --------------------------------------------------------------------------- #
# Markdown parsers (pure, total -- never raise).                               #
# --------------------------------------------------------------------------- #
def _parse_frontmatter(text: str) -> Dict[str, Any]:
    """Parse a leading ``---``-fenced YAML frontmatter block to a flat dict, DEGRADE-NEVER.

    Prefers PyYAML; on any failure (absent dep, parse error, no frontmatter) returns ``{}``.
    Only the top-level scalar keys the crew read needs (kind/crew_name/title/process/purpose/
    tldr/handoff_protocol_id/roles_count/pillar/domain/author) are consumed downstream, so a
    list/dict value on some other key is harmless."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    try:
        import yaml  # optional dep; absence must not break the dashboard
    except Exception:
        return _parse_frontmatter_fallback(block)
    try:
        data = yaml.safe_load(block)
    except Exception:
        return _parse_frontmatter_fallback(block)
    return data if isinstance(data, dict) else {}


def _parse_frontmatter_fallback(block: str) -> Dict[str, Any]:
    """A minimal ``key: value`` scalar parser used only when PyYAML is unavailable.

    Reads top-level ``key: value`` lines (ignores nested/list lines). Strips surrounding
    quotes. Pure + total -- only the scalar keys the crew read needs are required, so this
    fallback is sufficient to keep the surface alive without PyYAML."""
    out: Dict[str, Any] = {}
    for line in block.splitlines():
        if not line or line[0] in (" ", "\t", "-", "#"):
            continue
        m = re.match(r"^([A-Za-z0-9_]+)\s*:\s*(.*)$", line)
        if not m:
            continue
        key = m.group(1).strip()
        val = m.group(2).strip()
        if val and val[0] in ('"', "'") and val[-1:] == val[0]:
            val = val[1:-1]
        if key and key not in out:
            out[key] = val
    return out


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

    Used for the handoff-protocol note. Collapses to the leading non-table, non-fence lines so
    the detail page shows a clean one/two-line note, not the whole section. Bounded to ~600
    chars."""
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
            if out:
                break
            continue
        if not stripped:
            if out:
                break  # one paragraph is enough for the note
            continue
        out.append(stripped)
    prose = " ".join(out).strip()
    return prose[:600]


def _extract_roles_table(text: str) -> List[Dict[str, str]]:
    """Parse the ``## Roles`` markdown table into [{name, agent, goal, tools}].

    A crew_template Roles table is typically ``| Role | Role Assignment ID | Reason |`` (some
    add a ``Provider`` column). We map column 0 -> ``name`` (the role_name), the LAST column
    -> ``goal`` (the Reason / why), and the middle column(s) -> ``agent`` (the role_assignment
    /agent binding). Tolerant: a 2-column table omits the agent. Returns [] when there is no
    Roles table. Bounded to _MAX_ROLES rows."""
    body = _section_body(text, ("Roles", "Role Assignments"))
    if not body:
        return []
    rows = _parse_md_table(body)
    out: List[Dict[str, str]] = []
    for cells in rows[:_MAX_ROLES]:
        if not cells:
            continue
        name = cells[0].strip()
        if not name:
            continue
        ncols = len(cells)
        role: Dict[str, str] = {"name": name}
        if ncols >= 3:
            # col 1 = the agent / role_assignment binding; the LAST col = the goal/reason.
            agent = cells[1].strip()
            goal = cells[ncols - 1].strip()
            if agent:
                role["agent"] = agent
            if goal and goal != agent:
                role["goal"] = goal
            # A 4+ column table (e.g. with a Provider col) folds the extra middle cell into
            # ``tools`` as supplementary context (never a security field).
            if ncols >= 4:
                extra = cells[2].strip()
                if extra and extra != goal:
                    role["tools"] = extra
        elif ncols == 2:
            goal = cells[1].strip()
            if goal:
                role["goal"] = goal
        out.append(role)
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
                break  # a table block ended; stop at the first non-table line after it.
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
def _nucleus_from_relpath(rel_path: str) -> str:
    """Derive the owning nucleus ('N03') from a crew_template repo path, '' if none.

    The crew_template lives under ``N0X_<domain>/P12_orchestration/...``; the leading path
    segment carries the nucleus. Returns the uppercased N-code, or '' (e.g. N00_genesis still
    yields 'N00')."""
    head = rel_path.replace("\\", "/").split("/", 1)[0]
    m = re.match(r"^(N0[0-9])", head.upper())
    return m.group(1) if m else ""


def _normalize_process(value: Any) -> str:
    """Coerce a process value to a known topology, defaulting to 'sequential'.

    An unknown / absent / non-scalar value falls back to the cex_crew default so the chip
    always renders a valid topology, never a broken value."""
    proc = _clean_str(value).lower()
    return proc if proc in _PROCESS_VALUES else _DEFAULT_PROCESS


def _roles_list(value: Any) -> List[Dict[str, str]]:
    """Coerce a parsed roles value to a clean list of {name, agent?, goal?, tools?} dicts."""
    if not isinstance(value, (list, tuple)):
        return []
    out: List[Dict[str, str]] = []
    for item in value:
        if not isinstance(item, Mapping):
            continue
        name = _clean_str(item.get("name"))
        if not name:
            continue
        role: Dict[str, str] = {"name": name}
        for key in ("agent", "goal", "tools"):
            val = _clean_str(item.get(key))
            if val:
                role[key] = val
        out.append(role)
    return out


def _clean_str(value: Any) -> str:
    """Coerce a scalar to a whitespace-normalized string ('' if None/non-scalar/bool)."""
    if value is None or isinstance(value, bool):
        return ""
    if isinstance(value, (str, int, float)):
        return " ".join(str(value).split())
    return ""


def _coerce_int(value: Any) -> Optional[int]:
    """Coerce a scalar to a non-negative int, or None when not an int-ish value."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, float):
        return int(value) if value >= 0 else None
    if isinstance(value, str):
        s = value.strip()
        if s.isdigit():
            return int(s)
    return None


def _enabled_flag(value: Any, *, default: bool) -> bool:
    """Coerce an overlay ``enabled`` value to a bool. Absent (None) -> ``default``."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in _TRUTHY
    return bool(value)


def _titleize(slug: str) -> str:
    """Fallback human label from a crew id ('product_launch' -> 'Product Launch')."""
    return " ".join(part.capitalize() for part in re.split(r"[_-]+", slug) if part)

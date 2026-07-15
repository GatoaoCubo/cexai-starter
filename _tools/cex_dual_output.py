#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI dual-output emitter -- cex_dual_output (mission DUALMINT, Wave 1).

THE universal DUAL-SURFACE output contract (founder directive 2026-06-21). EVERY dashboard
capability emits ONE asset with TWO coupled faces from its STRUCTURED output:

  * MACHINE face -- ``.md`` + YAML frontmatter. The typed/governed asset persisted
    tenant-scoped to the tenant's OWN Supabase (the multitenant data plane) and readable by
    THAT tenant's AI. Canonical source of truth. Frontmatter carries id/capability/tenant/
    created/real/score/passed/mold_id + a ``media:`` ledger; the body carries the structured
    sections (the same output_sections the generator produced).
  * HUMAN face  -- a self-contained HTML AUDIOVISUAL report. The structured sections rendered
    as readable tables/chips/lists PLUS a MEDIA layer: each editable media slot is either a
    real <img>/<video>/<audio> (when the media pipeline already produced it) OR an empty
    UPLOAD-FALLBACK dropzone (when it did not). NEVER a broken/fabricated media ref.

The two faces share ONE ``id`` (the coupling): the human edits the visual/media side, the
tenant's AI reads + operates the structured ``.md``+YAML side; they CO-OWN the asset. A media
slot is referenced by the SAME ``key`` in both faces (HTML ``data-slot-key`` <-> frontmatter
``media[].key``), so a human upload on the visual side updates the machine ledger entry the AI
reads (status empty -> generated, src filled). That key-equality IS the sync rule.

INPUT (the generator's STRUCTURED output -- the capability_generators.StructuredOutput shape):
    {"mold_id": str, "output_sections": [MoldSection...], "real": bool, "passed": bool,
     "score": float, "artifact": str, "notes": [str...]}
  where each MoldSection is one of (the FROZEN renderer shapes, lib/molds.MoldSection):
    {"title", "layout": "fields", "rows": [{"label","value"}...]}
    {"title", "layout": "table",  "columns": [...], "table": [[...]...]}
    {"title", "layout": "list",   "items": [...]}

RELATION TO cex_output_contract (the sibling dual emitter): cex_output_contract.render() is the
dual MD+HTML emitter for the FLAT 30-field pesquisa_produto contract (a field-schema walk, no
media). cex_dual_output is the UNIVERSAL emitter for the ``output_sections`` shape the 13 typed
generators emit, and it ADDS the media-slot layer the founder directive requires. They are
complementary (different input shape; only this one carries media), not duplicative.

PURE: NO LLM, NO network, NO DB, NO file IO. ``to_dual_output(...)`` is a deterministic
projection -- given the same inputs it always yields the same faces. The MEDIA pipeline
(_tools/cex_media_produce.py -- img/TTS/video) and the founder-voice TTS are the layer that
FILLS a slot's src; the EDGE runs them and passes the produced srcs in via ``produced_media``.
This module never calls them (so it stays pure + offline-testable + degrade-never). Persisting
the machine ``.md`` tenant-scoped = the multitenant data plane (cexai.governance.data
.SupabaseDataAdapter, via run_capability.db.persist_artifact); this module never wires the DB.

NEVER-FABRICATE (the load-bearing invariant): an un-produced media field becomes an EMPTY
upload-fallback slot (status="empty", no ``src``, an HTML dropzone) -- never a fake URL, never a
broken <img>. DEGRADE-NEVER: a malformed struct/section degrades to a valid-but-thin pair, never
raises. ASCII-only per .claude/rules/ascii-code-rule.md (runtime VALUES may carry accents; the
module's own constants stay diacritic-free).

Spec: _docs/specs/spec_dual_output_contract.md. Sibling: _tools/cex_output_contract.py. Input
shape: _tools/capability_generators/_base.StructuredOutput. TS mirror:
apps/dashboard_web/lib/dual_output_contract.ts.
"""

from __future__ import annotations

from html import escape as _html_escape
from typing import Any, Dict, List, Mapping, Optional, Sequence

# --------------------------------------------------------------------------- #
# Module constants -- no side effects.
# --------------------------------------------------------------------------- #
SCHEMA_VERSION = "1.0"

# The media kinds a slot may carry (mirror dual_output_contract.ts MediaKind).
VALID_MEDIA_KINDS = ("image", "video", "audio")

# The slot statuses (mirror dual_output_contract.ts MediaSlotStatus).
STATUS_GENERATED = "generated"
STATUS_EMPTY = "empty"

# When a capability declares NO media requests, the directive still wants the human to have an
# editable media affordance: ONE empty, upload-fallback hero image slot. This is the affordance
# ("editable media slots + an open-field upload/edit fallback wherever the generator did not
# auto-produce the media"), NOT a fabricated asset -- it is empty until a human/pipeline fills it.
_DEFAULT_MEDIA_REQUESTS: tuple = (
    {"key": "hero", "kind": "image", "section": None, "label": "Imagem principal"},
)


# --------------------------------------------------------------------------- #
# THE entry.
# --------------------------------------------------------------------------- #
def to_dual_output(
    capability: str,
    struct: Mapping[str, Any],
    *,
    tenant: Optional[str] = None,
    created: Optional[str] = None,
    asset_id: Optional[str] = None,
    media_requests: Optional[Sequence[Mapping[str, Any]]] = None,
    produced_media: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Project ONE capability STRUCTURED output into the dual-surface asset (the founder contract).

    Args:
      capability       -- the capability slug (e.g. "research", "marketplace_listing").
      struct           -- the generator's StructuredOutput dict (output_sections + real/score/...).
      tenant           -- the tenant id this asset belongs to (the edge passes it; "" when absent.
                          NEVER fabricated -- the persist seam binds the real tenant via RLS).
      created          -- the creation timestamp (ISO-8601 the edge supplies; "" when absent.
                          NEVER fabricated -- this module is time-pure for deterministic tests).
      asset_id         -- the shared id coupling the two faces (the edge passes the persisted
                          record id; defaults to a deterministic slug of mold_id/capability).
      media_requests   -- the media slots the capability declares it wants: a list of
                          {key, kind, section?, label?}. None -> ONE empty hero image slot.
      produced_media   -- slot_key -> produced media the pipeline ALREADY made: either a src
                          string OR {"src", "alt"?}. A key absent / empty src -> the slot stays
                          EMPTY (upload-fallback), never fabricated.

    Returns a dict with the THREE contract faces plus coupling metadata:
      {"machine_md": str,            # the .md + YAML frontmatter (canonical, AI-readable)
       "human_html": str,            # the HTML audiovisual report (human, with media slots)
       "media_slots": [slot...],     # the resolved media slots (the ledger, both faces share it)
       "id": str, "capability": str, # the shared coupling id
       "frontmatter": dict,          # the assembled machine frontmatter (structured)
       "real": bool}

    PURE + TOTAL: a missing/malformed struct degrades to a valid-but-thin pair; never raises.
    """
    if not isinstance(struct, Mapping):
        struct = {}

    cap = str(capability or struct.get("mold_id") or "capability").strip() or "capability"
    sections = _sections(struct)
    real = bool(struct.get("real", False))

    aid = _resolve_asset_id(asset_id, struct, cap)
    slots = _resolve_media_slots(media_requests, produced_media)

    frontmatter = _build_frontmatter(
        cap, struct, slots, tenant=tenant, created=created, asset_id=aid, real=real,
    )
    machine_md = _render_machine_md(cap, struct, sections, slots, frontmatter)
    human_html = _render_human_html(cap, struct, sections, slots)

    return {
        "id": aid,
        "capability": cap,
        "machine_md": machine_md,
        "human_html": human_html,
        "media_slots": slots,
        "frontmatter": frontmatter,
        "real": real,
    }


# --------------------------------------------------------------------------- #
# Media slot resolution (NEVER-FABRICATE -- the heart of the directive).
# --------------------------------------------------------------------------- #
def _resolve_media_slots(
    media_requests: Optional[Sequence[Mapping[str, Any]]],
    produced_media: Optional[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    """Resolve the declared media requests into slots, filling src ONLY where the pipeline
    actually produced it. PURE + TOTAL.

    A request {key, kind, section?, label?} becomes a slot:
      * produced_media[key] has a non-empty src -> status="generated", src=<that src> (+alt).
      * otherwise                               -> status="empty", NO src (upload-fallback).
    Both states are editable + upload-fallback (a human may swap a generated asset too). An
    invalid/blank request (no key, or a kind not in VALID_MEDIA_KINDS) is DROPPED honestly
    (never coerced into a fabricated kind). None requests -> the default hero slot.
    """
    requests = media_requests if media_requests is not None else _DEFAULT_MEDIA_REQUESTS
    produced = produced_media if isinstance(produced_media, Mapping) else {}

    slots: List[Dict[str, Any]] = []
    seen_keys: set = set()
    for req in requests or []:
        if not isinstance(req, Mapping):
            continue
        key = str(req.get("key") or "").strip()
        kind = str(req.get("kind") or "").strip().lower()
        if not key or kind not in VALID_MEDIA_KINDS:
            continue  # honest drop -- never fabricate a key/kind
        if key in seen_keys:
            continue  # de-dup by key (the coupling key must be unique)
        seen_keys.add(key)

        label = str(req.get("label") or "").strip()
        section = req.get("section")
        section = str(section).strip() if isinstance(section, str) and section.strip() else None

        src, alt = _produced_src(produced.get(key))
        slot: Dict[str, Any] = {
            "key": key,
            "kind": kind,
            "status": STATUS_GENERATED if src else STATUS_EMPTY,
            "editable": True,
            "uploadFallback": True,
        }
        if section:
            slot["section"] = section
        if label:
            slot["label"] = label
        if src:
            slot["src"] = src
            if alt:
                slot["alt"] = alt
        # status="empty" -> NO src key at all (never a fabricated/blank URL).
        slots.append(slot)
    return slots


def _produced_src(produced: Any) -> "tuple[Optional[str], Optional[str]]":
    """Extract (src, alt) from a produced_media entry. Accepts a bare src string OR a
    {"src","alt"?} mapping. Returns (None, None) when no usable src -> the slot stays EMPTY.
    PURE + TOTAL: a blank/whitespace src is treated as ABSENT (never a fabricated ref)."""
    if isinstance(produced, str):
        s = produced.strip()
        return (s, None) if s else (None, None)
    if isinstance(produced, Mapping):
        s = str(produced.get("src") or "").strip()
        a = str(produced.get("alt") or "").strip() or None
        return (s, a) if s else (None, None)
    return (None, None)


# --------------------------------------------------------------------------- #
# MACHINE face -- .md + YAML frontmatter (canonical, AI-readable).
# --------------------------------------------------------------------------- #
def _build_frontmatter(
    capability: str,
    struct: Mapping[str, Any],
    slots: Sequence[Mapping[str, Any]],
    *,
    tenant: Optional[str],
    created: Optional[str],
    asset_id: str,
    real: bool,
) -> Dict[str, Any]:
    """Assemble the machine frontmatter mapping: the coupling identity + the media ledger.

    Fields (per spec): id, capability, tenant, created, kind (mold_id), real, score, passed,
    schema_version, media[] (the slot ledger -- key/kind/status/src). The structured BODY (the
    output_sections) follows in the .md body, not the frontmatter. tenant/created default to ""
    (honest empty -- NEVER fabricated). yaml.safe_dump renders this ASCII-safe downstream.
    """
    score = struct.get("score")
    try:
        score_val = float(score) if score is not None else 0.0
    except (TypeError, ValueError):
        score_val = 0.0

    fm: Dict[str, Any] = {
        "id": asset_id,
        "capability": capability,
        "tenant": str(tenant or "").strip(),
        "created": str(created or "").strip(),
        "kind": str(struct.get("mold_id") or capability),
        "schema_version": SCHEMA_VERSION,
        "real": bool(real),
        "passed": bool(struct.get("passed", False)),
        "score": score_val,
        "media": [_media_ledger_entry(s) for s in slots],
    }
    notes = struct.get("notes")
    if isinstance(notes, (list, tuple)) and notes:
        fm["notes"] = [str(n) for n in notes]
    return fm


def _media_ledger_entry(slot: Mapping[str, Any]) -> Dict[str, Any]:
    """The machine-face view of a slot (the ledger entry the AI reads). Mirrors the slot but
    keeps only the AI-relevant keys; an EMPTY slot carries NO src (the sync target a human
    upload later fills)."""
    entry: Dict[str, Any] = {
        "key": str(slot.get("key") or ""),
        "kind": str(slot.get("kind") or ""),
        "status": str(slot.get("status") or STATUS_EMPTY),
    }
    if slot.get("section"):
        entry["section"] = str(slot.get("section"))
    if slot.get("status") == STATUS_GENERATED and slot.get("src"):
        entry["src"] = str(slot.get("src"))
    return entry


def _render_machine_md(
    capability: str,
    struct: Mapping[str, Any],
    sections: Sequence[Mapping[str, Any]],
    slots: Sequence[Mapping[str, Any]],
    frontmatter: Mapping[str, Any],
) -> str:
    """The MACHINE .md: YAML frontmatter + a body of the structured sections + a media ledger.

    The body code-fences each section so values render verbatim (machine-parseable, no markdown
    surprises) -- the SAME discipline cex_output_contract uses. The Media block restates the
    slot ledger in the body so the AI reading the .md sees the pending-upload state inline."""
    fm_text = _safe_yaml_dump(dict(frontmatter)).rstrip("\n")
    parts: List[str] = ["---", fm_text, "---", ""]
    parts.append("# %s" % (str(frontmatter.get("id") or capability)))
    parts.append("")

    for section in sections:
        title = str(section.get("title") or "").strip()
        if not title:
            continue
        parts.append("## %s" % title)
        note = section.get("note")
        if isinstance(note, str) and note.strip():
            parts.append("")
            parts.append("> %s" % " ".join(note.split()))
        parts.append("")
        parts.append("```")
        parts.extend(_section_fence_lines(section))
        parts.append("```")
        parts.append("")

    # The media ledger in the body (key/kind/status) -- AI-readable pending-upload state.
    parts.append("## Media")
    parts.append("")
    parts.append("```")
    if slots:
        for s in slots:
            line = "%s (%s): %s" % (s.get("key"), s.get("kind"), s.get("status"))
            if s.get("status") == STATUS_GENERATED and s.get("src"):
                line += " -> %s" % s.get("src")
            elif s.get("status") == STATUS_EMPTY:
                line += " -> upload-fallback (vazio; aguarda upload/edicao do humano)"
            parts.append(line)
    else:
        parts.append("(nenhum slot de midia declarado)")
    parts.append("```")
    parts.append("")
    return "\n".join(parts).rstrip("\n") + "\n"


def _section_fence_lines(section: Mapping[str, Any]) -> List[str]:
    """Render one output_section into code-fence body lines (compact, machine-parseable)."""
    layout = str(section.get("layout") or "").strip()
    out: List[str] = []
    if layout == "fields":
        for row in _rows(section):
            out.append("%s: %s" % (row.get("label"), _scalar_for_fence(row.get("value"))))
    elif layout == "table":
        cols = [str(c) for c in (section.get("columns") or [])]
        if cols:
            out.append(" | ".join(cols))
        for r in section.get("table") or []:
            if isinstance(r, (list, tuple)):
                out.append(" | ".join(_scalar_for_fence(c) for c in r))
    elif layout == "list":
        for item in section.get("items") or []:
            if item is not None and str(item).strip():
                out.append("- %s" % _scalar_for_fence(item))
    if not out:
        out.append("(sem dados)")
    return out


# --------------------------------------------------------------------------- #
# HUMAN face -- HTML audiovisual report (sections + media slots).
# --------------------------------------------------------------------------- #
def _render_human_html(
    capability: str,
    struct: Mapping[str, Any],
    sections: Sequence[Mapping[str, Any]],
    slots: Sequence[Mapping[str, Any]],
) -> str:
    """The HUMAN HTML audiovisual face: the structured sections as readable widgets + a media
    layer (real <img>/<video>/<audio> when produced, an upload-fallback dropzone when empty).

    Section-bound slots (slot.section == section.title) render inside that section; unbound slots
    render in a trailing 'Midia' gallery. NEVER emits a broken/fabricated media tag for an empty
    slot -- it emits an editable upload dropzone."""
    real = bool(struct.get("real", False))
    out: List[str] = []
    out.append("<section class=\"cex-dual\" style=\"font-family:system-ui,Arial,sans-serif;"
               "max-width:880px;margin:0 auto;color:#1a1a1a;\">")
    out.append("<header style=\"border-bottom:2px solid #eee;padding-bottom:8px;\">")
    out.append("<h1 style=\"margin:0;font-size:1.4rem;\">%s</h1>" % _html_escape(capability))
    out.append(_real_badge_html(real))
    out.append("</header>")

    bound_by_section = _slots_by_section(slots)
    for section in sections:
        title = str(section.get("title") or "").strip()
        block = _render_html_section(section)
        if block:
            out.append(block)
        # slots bound to this section title render directly under it.
        for slot in bound_by_section.get(title, []):
            out.append(_render_media_slot_html(slot))

    # Unbound slots (no section, or a section that did not match a rendered title) -> a gallery.
    unbound = bound_by_section.get(None, [])
    rendered_titles = {str(s.get("title") or "").strip() for s in sections}
    for title, group in bound_by_section.items():
        if title is not None and title not in rendered_titles:
            unbound = unbound + group
    if unbound:
        out.append("<div class=\"cex-media-gallery\" style=\"margin-top:16px;\">")
        out.append("<h2 style=\"font-size:1.05rem;border-bottom:1px solid #f0f0f0;\">Midia</h2>")
        for slot in unbound:
            out.append(_render_media_slot_html(slot))
        out.append("</div>")

    out.append("<footer style=\"margin-top:16px;border-top:1px solid #eee;padding-top:8px;"
               "font-size:.8rem;color:#888;\">Face humana (audiovisual) -- co-editavel; a face "
               "maquina (.md+YAML) e a fonte canonica que a IA do tenant opera. Mesmo id, dois "
               "lados.</footer>")
    out.append("</section>")
    return "\n".join(out)


def _render_html_section(section: Mapping[str, Any]) -> str:
    """Render one output_section as an HTML block by its layout (fields|table|list). TOTAL."""
    title = str(section.get("title") or "").strip()
    layout = str(section.get("layout") or "").strip()
    if not title and not layout:
        return ""

    out: List[str] = ["<div class=\"cex-section\" style=\"margin-top:14px;\">"]
    if title:
        out.append("<h2 style=\"font-size:1.05rem;border-bottom:1px solid #f0f0f0;\">%s</h2>"
                   % _html_escape(title))
    note = section.get("note")
    if isinstance(note, str) and note.strip():
        out.append("<p style=\"font-size:.85rem;color:#777;margin:2px 0 8px;\">%s</p>"
                   % _html_escape(" ".join(note.split())))

    if layout == "fields":
        rows = _rows(section)
        if rows:
            out.append("<table style=\"border-collapse:collapse;width:100%;font-size:.92rem;\">")
            for row in rows:
                label = _html_escape(str(row.get("label") or ""))
                value = _html_escape(_scalar_for_html(row.get("value")))
                out.append("<tr><td style=\"padding:4px 8px;border:1px solid #eee;"
                           "font-weight:600;width:40%%;\">%s</td>"
                           "<td style=\"padding:4px 8px;border:1px solid #eee;\">%s</td></tr>"
                           % (label, value))
            out.append("</table>")
    elif layout == "table":
        out.append(_table_html(section))
    elif layout == "list":
        items = [str(i) for i in (section.get("items") or []) if i is not None and str(i).strip()]
        if items:
            out.append("<ul style=\"margin:6px 0;padding-left:18px;\">")
            for it in items:
                out.append("<li style=\"margin:2px 0;\">%s</li>" % _html_escape(it))
            out.append("</ul>")

    out.append("</div>")
    return "\n".join(out)


def _table_html(section: Mapping[str, Any]) -> str:
    """Render a layout=table section as an HTML grid (header + rows). TOTAL."""
    cols = [str(c) for c in (section.get("columns") or [])]
    grid = section.get("table") or []
    out: List[str] = ["<table style=\"border-collapse:collapse;width:100%;font-size:.9rem;\">"]
    if cols:
        out.append("<thead><tr>")
        for c in cols:
            out.append("<th style=\"padding:4px 8px;border:1px solid #eee;background:#fafafa;"
                       "text-align:left;\">%s</th>" % _html_escape(c))
        out.append("</tr></thead>")
    out.append("<tbody>")
    for r in grid:
        if not isinstance(r, (list, tuple)):
            continue
        out.append("<tr>")
        for cell in r:
            out.append("<td style=\"padding:4px 8px;border:1px solid #eee;\">%s</td>"
                       % _html_escape(_scalar_for_html(cell)))
        out.append("</tr>")
    out.append("</tbody></table>")
    return "\n".join(out)


def _render_media_slot_html(slot: Mapping[str, Any]) -> str:
    """Render ONE media slot. A generated slot -> the real media element (editable/swappable);
    an empty slot -> an UPLOAD-FALLBACK dropzone. NEVER a fabricated/broken media ref.

    Both carry data-* hooks the dashboard wires to its upload/edit handlers:
      data-slot-key (the coupling key) / data-kind / data-editable / data-upload-fallback.
    """
    key = str(slot.get("key") or "")
    kind = str(slot.get("kind") or "image")
    label = str(slot.get("label") or key)
    status = str(slot.get("status") or STATUS_EMPTY)
    data_attrs = ("data-slot-key=\"%s\" data-kind=\"%s\" data-editable=\"true\" "
                  "data-upload-fallback=\"true\"" % (_html_escape(key), _html_escape(kind)))

    if status == STATUS_GENERATED and slot.get("src"):
        src = _html_escape(str(slot.get("src")))
        alt = _html_escape(str(slot.get("alt") or label))
        media = _media_element_html(kind, src, alt)
        return ("<figure class=\"cex-media-slot cex-media-generated\" %s "
                "style=\"margin:10px 0;\">%s<figcaption style=\"font-size:.8rem;color:#777;\">"
                "%s</figcaption></figure>" % (data_attrs, media, alt))

    # EMPTY -> editable upload-fallback dropzone (no src, no broken media tag).
    prompt = {"image": "Enviar imagem", "video": "Enviar video", "audio": "Enviar audio"}.get(
        kind, "Enviar midia")
    return ("<div class=\"cex-media-slot cex-media-empty\" %s "
            "style=\"margin:10px 0;padding:18px;border:2px dashed #bbb;border-radius:8px;"
            "text-align:center;color:#888;background:#fafafa;\">"
            "<strong>[ + ] %s</strong><br><span style=\"font-size:.82rem;\">slot vazio (%s) -- "
            "faca upload ou edite</span></div>"
            % (data_attrs, _html_escape(prompt), _html_escape(label)))


def _media_element_html(kind: str, src: str, alt: str) -> str:
    """The real media element for a generated slot (src already html-escaped). TOTAL."""
    if kind == "video":
        return ("<video controls style=\"max-width:100%%;border-radius:8px;\">"
                "<source src=\"%s\"></video>" % src)
    if kind == "audio":
        return "<audio controls src=\"%s\" style=\"width:100%%;\"></audio>" % src
    # image (default)
    return ("<img src=\"%s\" alt=\"%s\" style=\"max-width:100%%;border-radius:8px;\"/>"
            % (src, alt))


def _real_badge_html(real: bool) -> str:
    """A small badge: real run vs molded/simulated (honest by construction)."""
    if real:
        return ("<span style=\"display:inline-block;background:#2e7d32;color:#fff;"
                "border-radius:6px;padding:2px 10px;margin-left:8px;font-size:.82rem;\">"
                "resultado real</span>")
    return ("<span style=\"display:inline-block;background:#b8860b;color:#fff;"
            "border-radius:6px;padding:2px 10px;margin-left:8px;font-size:.82rem;\">"
            "dados simulados</span>")


# --------------------------------------------------------------------------- #
# Accessors + coercion (PURE + TOTAL).
# --------------------------------------------------------------------------- #
def _sections(struct: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    raw = struct.get("output_sections")
    if isinstance(raw, (list, tuple)):
        return [s for s in raw if isinstance(s, Mapping)]
    return []


def _rows(section: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    raw = section.get("rows")
    if isinstance(raw, (list, tuple)):
        return [r for r in raw if isinstance(r, Mapping) and r.get("label") is not None]
    return []


def _slots_by_section(
    slots: Sequence[Mapping[str, Any]],
) -> Dict[Optional[str], List[Mapping[str, Any]]]:
    """Group slots by their bound section title (None for unbound). Order-preserving."""
    grouped: Dict[Optional[str], List[Mapping[str, Any]]] = {}
    for slot in slots:
        sec = slot.get("section")
        key = str(sec).strip() if isinstance(sec, str) and sec.strip() else None
        grouped.setdefault(key, []).append(slot)
    return grouped


def _resolve_asset_id(asset_id: Optional[str], struct: Mapping[str, Any], capability: str) -> str:
    """The shared coupling id: a caller value wins; else a deterministic slug of mold_id/
    capability (NO time/random -- so two runs of the same input couple identically in tests)."""
    if isinstance(asset_id, str) and asset_id.strip():
        return asset_id.strip()
    base = str(struct.get("mold_id") or capability or "asset")
    slug = _slug(base)
    return "dualout_%s" % (slug or "asset")


def _slug(text: Any) -> str:
    """ASCII-only lowercase hyphen/underscore slug. TOTAL: non-ascii folded out."""
    import re

    s = str(text or "").encode("ascii", "ignore").decode("ascii").lower().strip()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s


def _scalar_for_fence(value: Any) -> str:
    """A value for a code-fenced MD body line (compact, single line)."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, (list, tuple)):
        return ", ".join(str(v) for v in value)
    if isinstance(value, Mapping):
        return ", ".join("%s=%s" % (k, v) for k, v in value.items())
    return " ".join(str(value).split())


def _scalar_for_html(value: Any) -> str:
    """A value for an HTML cell (the caller escapes the result)."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Sim" if value else "Nao"
    if isinstance(value, (int, float)):
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)
    if isinstance(value, (list, tuple)):
        return ", ".join(str(v) for v in value)
    if isinstance(value, Mapping):
        return ", ".join("%s=%s" % (k, v) for k, v in value.items())
    return " ".join(str(value).split())


def _safe_yaml_dump(data: Mapping[str, Any]) -> str:
    """yaml.safe_dump with allow_unicode=False (ASCII-safe) + block style.

    DEGRADE-NEVER: if PyYAML is unavailable, fall back to a minimal hand-rolled emitter so the
    machine face is still valid-ish frontmatter rather than a crash. The production runtime
    always has PyYAML; the fallback only guards this PURE module."""
    safe = {str(k): _yaml_safe_value(v) for k, v in data.items()}
    try:
        import yaml

        return yaml.safe_dump(
            safe, default_flow_style=False, allow_unicode=False, sort_keys=True, width=4096,
        )
    except Exception:
        return _fallback_yaml(safe)


def _yaml_safe_value(value: Any) -> Any:
    """Project a value into a yaml.safe_dump-able primitive tree. PURE + TOTAL (never raises)."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple)):
        return [_yaml_safe_value(v) for v in value]
    if isinstance(value, Mapping):
        return {str(k): _yaml_safe_value(v) for k, v in value.items()}
    return str(value)


def _fallback_yaml(data: Mapping[str, Any]) -> str:
    """Minimal safe YAML emitter (only if PyYAML is absent). One level of list/dict; quotes
    strings. A degrade-never floor, not a full serializer."""
    lines: List[str] = []
    for key in sorted(str(k) for k in data.keys()):
        lines.append("%s: %s" % (key, _fallback_scalar(data[key])))
    return "\n".join(lines) + "\n"


def _fallback_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_fallback_scalar(v) for v in value) + "]"
    if isinstance(value, Mapping):
        return "{" + ", ".join("%s: %s" % (k, _fallback_scalar(v)) for k, v in value.items()) + "}"
    s = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return '"%s"' % s


__all__ = [
    "to_dual_output",
    "VALID_MEDIA_KINDS",
    "STATUS_GENERATED",
    "STATUS_EMPTY",
    "SCHEMA_VERSION",
]

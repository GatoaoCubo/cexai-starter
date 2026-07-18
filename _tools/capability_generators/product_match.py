#!/usr/bin/env python3
# -*- coding: ascii -*-
"""product_match -- N03 W3 SOURCING: the visual product-matcher / catalog-auditor.

KIND = "product_match" (capability #16, owned by N03). 6 inputs -> 4 output sections
(frozen shape from apps/dashboard_web/lib/molds.ts MOLD_PRODUCT_MATCH). It is
record-linkage (supplier item x marketplace listing) by a NON-key composite join --
photo + dimension + supplier_code -- with EAN/GTIN/barcode EXCLUDED on purpose (every
reseller recodes them). It doubles as a catalog auditor: even offline it flags
text-vs-photo cadastral divergence + low-res / missing photos on the LOCAL item data.

SHARED with the marketplace_listing / TUDAO mold: the two core helpers
``_normalize_join_key`` + ``_audit_text_vs_photo`` are PURE + importable so another
generator reuses the exact same join-key + audit logic (no drift between the two molds).

Sourcing rigor: provenance-as-section + honest-null offline (S1-S5 from
_docs/specs/contract/n01_sourcing_rigor.md). Offline-safe: degrade-never -- a match is
NEVER fabricated. match_engine=none (or no credential) -> match rows return "nao
executado" / NAO, confidence 0.0, endpoint_status "blocked: offline (sem motor
reverse-image)".

N07 WIRE REQUIRED: add to _BASE_CAPABILITIES in _tools/cex_run_capability.py:
    "product_match": ("N03", "product_match", "P04", "analyze"),
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Mapping, Optional

from ._base import (
    effective_kind,
    fields_section,
    list_section,
    make_provenance,
    register,
    structured_output,
    table_section,
)

KIND = "product_match"
CONTRACT_VERSION = "1.0.0"
RUN_MODE = "offline-deterministic"

# Input-contract defaults (capability_contracts_v1.0.md section 16 + MOLD_PRODUCT_MATCH).
_MATCH_ENGINE_ENUM = ("reverse_image", "embedding", "manual", "none")
_DEFAULT_MATCH_ENGINE = "none"
_DEFAULT_JOIN_KEYS = ("photo", "dimension", "supplier_code")
_DEFAULT_EXCLUDE_KEYS = ("ean", "gtin", "barcode")
_DEFAULT_CONFIDENCE_FLOOR = 0.7
_DEFAULT_MIN_PHOTO_PX = 200

# join_key name -> the item field(s) it reads, first non-empty wins (the join-key -> item-
# field resolution rule _normalize_join_key applies below). Module-level (Missao A /
# MOLDED_REAL_SEAM export-deepening) so domain_contract() further down can reference the
# SAME dict _normalize_join_key reads at runtime -- never a re-typed literal.
_JOIN_KEY_FIELD_ALIASES: dict = {
    "photo": ("photo_uri", "photo", "image", "image_uri"),
    "dimension": ("dimension", "dim", "size"),
    "supplier_code": ("code", "supplier_code", "sku"),
    "code": ("code", "supplier_code", "sku"),
}

# The GENERIC (run-independent) phrasing of the join-key-exclusion rule, for
# domain_contract() further down -- domain_contract() has no specific per-run
# effective_join list (it describes the LAW, not one run's output), so it restates the
# rule already in the module docstring + the "Chave de casamento" field in build() (s_prov)
# without the run-specific interpolation. Mirrors ads.py's _COMPLIANCE_CHARS_GENERIC.
_JOIN_KEY_EXCLUSION_RULE_GENERIC = (
    "EAN/GTIN/barcode excluidos de proposito -- todo revendedor recodifica esses campos,"
    " entao eles NUNCA entram no join (non-key composite linkage only)"
)

# Piece-count recognition tokens -- the ONLY tokens _piece_count treats as a piece-count
# marker (e.g. "12 pecas"). Module-level so domain_contract() can reference the SAME tuple
# _piece_count reads at runtime (never re-typed).
_PIECE_COUNT_TOKENS = (" pecas", " peca", " pcs", " pc", "c", " unidades", " unid")

# The frozen per-source endpoint_status palette (n01_sourcing_rigor S2) -- every
# capability's per-source status is one of these 4; _OFFLINE_ENDPOINT_STATUS below is
# THIS generator's own value from it ("blocked: ...").
_ENDPOINT_STATUS_ENUM = ("ok", "blocked", "skipped", "failed")
# The honest-null offline endpoint status (frozen palette above: ok|blocked|skipped|failed).
_OFFLINE_ENDPOINT_STATUS = "blocked: offline (sem motor reverse-image)"

# The two honest match-row reasons emitted in the "Fonte casada" column (S1-S5 honest-null:
# a match is NEVER fabricated, live or offline -- see build()'s own comment on the live
# branch below). _NO_ENGINE has no interpolation (hoisted verbatim); _ENGINE_PENDING_TEMPLATE
# is %-formatted with the resolved engine name at runtime, so domain_contract() uses the
# GENERIC (non-interpolated) phrasing instead (same split as _JOIN_KEY_EXCLUSION_RULE_GENERIC
# above / ads.py's _COMPLIANCE_CHARS_GENERIC).
_MATCH_ROW_REASON_NO_ENGINE = "nao executado -- sem motor de match"
_MATCH_ROW_REASON_ENGINE_PENDING_TEMPLATE = "pendente -- run live com motor '%s'"
_MATCH_ROW_REASON_ENGINE_PENDING_GENERIC = (
    "pendente -- run live com o motor configurado (ver enums.match_engine)"
)

# Scoring weights -- the F7 GOVERN penalties build() actually subtracts from the 0..1
# score. Module-level so domain_contract() references the SAME numbers, never re-typed
# magic numbers.
_SCORE_PENALTY_OFFLINE = 0.35
_SCORE_PENALTY_ZERO_ITEMS = 0.25
_SCORE_PENALTY_PER_NO_PHOTO = 0.05
_SCORE_PENALTY_NO_PHOTO_CAP = 0.15

# Per-section rule notes -- hoisted so build() (each section's note=) and domain_contract()
# share ONE source of truth (same pattern as ads.py's _COMPLIANCE_STATIC). Text unchanged
# from the original inline notes.
_NOTE_MATCH = (
    "Uma linha por item -- casou? contra qual fonte e com que confianca"
    " (>= match_confidence_floor para contar como match). Offline retorna NAO"
    " honesto, nunca um match inventado."
)
_NOTE_AUDIT = (
    "Flags de cadastro divergente, foto divergente ou baixa-res"
    " (< audit_min_photo_px) detectadas durante o match (rodam offline sobre o"
    " dado local do item)."
)
_NOTE_PROVENANCE = (
    "Motor usado + fontes consultadas + status por fonte; offline retorna"
    " honest-null (nunca um match fabricado). Status: %s."
) % " | ".join(_ENDPOINT_STATUS_ENUM)
_NOTE_VEREDITO = (
    "Gate nomeado (match_confiavel) -- cobertura do match e os bloqueadores que"
    " impedem um match confiavel."
)


# --------------------------------------------------------------------------- #
# PURE + IMPORTABLE HELPERS (shared with the marketplace_listing / TUDAO mold).
# EXACT signatures -- another generator imports these by name. TOTAL: never raise.
# --------------------------------------------------------------------------- #

def _normalize_join_key(item: Any, join_keys: Any, exclude_keys: Any) -> str:
    """Build a composite match key from the join_keys present on ``item``.

    The join is a NON-key linkage: it composes photo + dimension + supplier_code (+ code)
    -- whatever of ``join_keys`` the item actually carries -- and EXPLICITLY skips anything
    in ``exclude_keys`` (ean / gtin / barcode), because every reseller recodes those so
    they are useless as a cross-marketplace identity. Each part is lowercased + stripped;
    parts are joined with "|". A join_key name maps to the item field by a small alias map
    (e.g. "photo" -> photo_uri, "supplier_code" -> code).

    TOTAL: never raises; returns "" on bad input (non-mapping item, no usable keys).

    >>> _normalize_join_key({"code": "A1", "photo_uri": "u", "dimension": "10X10"},
    ...                     ["photo", "dimension", "supplier_code"], ["ean"])
    'photo=u|dimension=10x10|supplier_code=a1'
    """
    try:
        if not isinstance(item, Mapping):
            return ""

        # Normalize the exclude set (lowercased) -- these are NEVER part of the key.
        excl = set()
        for e in (exclude_keys or ()):
            try:
                es = str(e).strip().lower()
                if es:
                    excl.add(es)
            except Exception:
                continue

        keys = list(join_keys or _DEFAULT_JOIN_KEYS)
        parts: List[str] = []
        seen: set = set()
        for raw_key in keys:
            try:
                jk = str(raw_key).strip().lower()
            except Exception:
                continue
            if not jk or jk in excl or jk in seen:
                continue  # never join on an excluded key (ean/gtin/barcode), no dups
            seen.add(jk)
            fields = _JOIN_KEY_FIELD_ALIASES.get(jk, (jk,))
            val = ""
            for f in fields:
                try:
                    v = item.get(f)
                except Exception:
                    v = None
                if v is not None and str(v).strip() != "":
                    val = str(v).strip().lower()
                    break
            if val:
                parts.append("%s=%s" % (jk, val))
        return "|".join(parts)
    except Exception:
        return ""


def _audit_text_vs_photo(item: Any, min_photo_px: int = _DEFAULT_MIN_PHOTO_PX) -> "Optional[str]":
    """Return ONE audit-flag string when the item's registered text/dimension disagrees
    with its photo signal OR the photo is missing / low-res (< ``min_photo_px``), else None.

    Runs on LOCAL item data only -- no network -- so it is valid even offline. Signals:
      * no photo_uri                       -> "sem foto no cadastro ..."
      * photo dimensions parseable + small -> "foto baixa-res (<min>px) ..."
      * the desc names a piece-count / dimension token that contradicts the `dimension`
        field (e.g. desc "12 pecas" vs a dimension declaring "14")     -> divergence flag
    The piece-count check is a deterministic, conservative heuristic (only fires on a clear
    numeric contradiction); it never guesses.

    TOTAL: never raises; returns None on bad input.
    """
    try:
        if not isinstance(item, Mapping):
            return None

        code = ""
        try:
            code = str(item.get("code") or "").strip()
        except Exception:
            code = ""
        label = ("Codigo %s: " % code) if code else ""

        try:
            mn = int(min_photo_px)
        except (TypeError, ValueError):
            mn = _DEFAULT_MIN_PHOTO_PX

        photo = ""
        try:
            photo = str(item.get("photo_uri") or "").strip()
        except Exception:
            photo = ""

        # 1. No photo -> cannot match by image (auditable offline).
        if not photo:
            return label + "sem foto no cadastro -- impossivel casar por imagem (so codigo)"

        # 2. Low-res photo: prefer an explicit photo_px field, else parse a WxH from the uri.
        px = _photo_min_px(item, photo)
        if px is not None and px < mn:
            return label + "foto baixa-res (%dpx < %dpx minimo) -- match rebaixado para PARCIAL" % (px, mn)

        # 3. Text vs dimension contradiction (piece-count tokens only -- conservative).
        flag = _piece_count_conflict(item)
        if flag:
            return label + flag

        return None
    except Exception:
        return None


def _photo_min_px(item: Mapping[str, Any], photo: str) -> "Optional[int]":
    """Best-effort smallest photo dimension in px, or None when unknown. TOTAL.

    Reads an explicit numeric ``photo_px`` first (honest, no guessing); else parses a
    "WxH" token from the photo uri/filename (e.g. ``img_160x160.jpg`` -> 160)."""
    try:
        raw_px = item.get("photo_px")
        if raw_px is not None and str(raw_px).strip() != "":
            try:
                return int(float(str(raw_px).strip()))
            except (TypeError, ValueError):
                pass
        # Parse a WxH token from the uri without regex (ASCII, dependency-free).
        low = photo.lower()
        for sep in ("x", "X"):
            cand = _scan_wxh(low, sep.lower())
            if cand is not None:
                return cand
        return None
    except Exception:
        return None


def _scan_wxh(text: str, sep: str) -> "Optional[int]":
    """Scan ``text`` for a ``<digits>sep<digits>`` token; return the smaller side. TOTAL."""
    try:
        n = len(text)
        i = 0
        while i < n:
            if text[i].isdigit():
                j = i
                while j < n and text[j].isdigit():
                    j += 1
                if j < n and text[j] == sep:
                    k = j + 1
                    m = k
                    while m < n and text[m].isdigit():
                        m += 1
                    if m > k:
                        a = int(text[i:j])
                        b = int(text[k:m])
                        return min(a, b)
                i = j
            else:
                i += 1
        return None
    except Exception:
        return None


def _piece_count_conflict(item: Mapping[str, Any]) -> "Optional[str]":
    """Flag a clear piece-count contradiction between ``desc`` and ``dimension``. TOTAL.

    Fires ONLY when both the desc and the dimension contain an explicit piece-count token
    ("<n> pecas" / "<n>c" / "<n> pcs") and the two numbers differ. Conservative: any
    ambiguity -> None (never a fabricated divergence)."""
    try:
        desc = str(item.get("desc") or "").lower()
        dim = str(item.get("dimension") or "").lower()
        d_desc = _piece_count(desc)
        d_dim = _piece_count(dim)
        if d_desc is not None and d_dim is not None and d_desc != d_dim:
            return ("dimensao divergente -- texto diz %d pecas, dimensao registra %d pecas"
                    % (d_desc, d_dim))
        return None
    except Exception:
        return None


def _piece_count(text: str) -> "Optional[int]":
    """Extract an integer piece-count from ``<n> pecas|pcs|pc|c`` in ``text``, else None. TOTAL."""
    try:
        low = text.lower()
        n = len(low)
        for tok in _PIECE_COUNT_TOKENS:
            idx = low.find(tok)
            while idx > 0:
                # walk back over the digits immediately preceding the token
                j = idx
                while j > 0 and low[j - 1].isdigit():
                    j -= 1
                if j < idx:
                    try:
                        return int(low[j:idx])
                    except (TypeError, ValueError):
                        pass
                idx = low.find(tok, idx + 1)
        return None
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# Internal parse helpers.
# --------------------------------------------------------------------------- #

def _item_list(raw: Any) -> List[Dict[str, Any]]:
    """Coerce the ``items`` input into a list of dicts. TOTAL: [] on bad input."""
    out: List[Dict[str, Any]] = []
    if isinstance(raw, Mapping):
        raw = [raw]
    if isinstance(raw, (list, tuple)):
        for it in raw:
            if isinstance(it, Mapping):
                out.append(dict(it))
    return out


def _str_list(raw: Any, default: Any) -> List[str]:
    if isinstance(raw, (list, tuple)):
        vals = [str(x).strip() for x in raw if str(x).strip()]
        return vals or [str(x) for x in default]
    if isinstance(raw, str) and raw.strip():
        return [p.strip() for p in raw.replace("\n", ",").split(",") if p.strip()]
    return [str(x) for x in default]


def _code_of(item: Mapping[str, Any], idx: int) -> str:
    try:
        c = str(item.get("code") or "").strip()
    except Exception:
        c = ""
    return c or ("item-%d" % (idx + 1))


def _artifact_json(items: List[Dict[str, Any]], engine: str, floor: float,
                   gate: bool, matched: int, kind: str = KIND) -> str:
    try:
        return json.dumps({
            "kind": kind,
            "match_engine": engine,
            "match_confidence_floor": floor,
            "items_total": len(items),
            "items_matched": matched,
            "match_confiavel": bool(gate),
        }, ensure_ascii=True, sort_keys=True)
    except Exception:
        return "{}"


@register(KIND)
def build(
    inputs: Mapping[str, Any], *, credential: "Optional[Any]" = None,
    resolved_kind: Optional[str] = None,
) -> dict:
    """REAL product_match generator (N03 -- visual record-linkage + catalog audit).

    Offline path (match_engine=none OR credential is None): match rows are honest-null
    (NAO / "nao executado", confidence 0.0); the audit STILL runs on local item data.
    Shape frozen to MOLD_PRODUCT_MATCH. Never raises (degrade-never).

    ``resolved_kind`` (mission R-333): the PER-TENANT RESOLVED kind the caller
    (cex_run_capability) already holds, embedded verbatim into the artifact JSON
    self-description instead of the module KIND constant. None/blank falls back to KIND."""
    notes: List[str] = []
    _kind = effective_kind(resolved_kind, KIND)

    # F1: parse inputs (default every optional from the contract) ----------------
    items = _item_list(inputs.get("items"))
    if not items:
        notes.append("items vazio ou invalido -- nenhum item para casar/auditar")

    join_keys = _str_list(inputs.get("match_join_keys"), _DEFAULT_JOIN_KEYS)
    exclude_keys = _str_list(inputs.get("match_exclude_keys"), _DEFAULT_EXCLUDE_KEYS)

    engine = str(inputs.get("match_engine") or "").strip()
    if engine not in _MATCH_ENGINE_ENUM:
        if engine:
            notes.append("match_engine '%s' invalido; usando '%s'" % (engine, _DEFAULT_MATCH_ENGINE))
        engine = _DEFAULT_MATCH_ENGINE

    try:
        floor = float(inputs.get("match_confidence_floor"))
    except (TypeError, ValueError):
        floor = _DEFAULT_CONFIDENCE_FLOOR
        if inputs.get("match_confidence_floor") is not None:
            notes.append("match_confidence_floor invalido; default %.2f" % _DEFAULT_CONFIDENCE_FLOOR)
    floor = max(0.0, min(1.0, floor))

    audit_enabled = inputs.get("audit_enabled", True)
    audit_enabled = bool(audit_enabled) if audit_enabled is not None else True

    try:
        min_px = int(inputs.get("audit_min_photo_px") or _DEFAULT_MIN_PHOTO_PX)
    except (TypeError, ValueError):
        min_px = _DEFAULT_MIN_PHOTO_PX
        notes.append("audit_min_photo_px invalido; default %d" % _DEFAULT_MIN_PHOTO_PX)

    # Honest-offline detection: no engine OR no credential => never a real match.
    offline = (engine == "none") or (credential is None)
    if offline:
        if engine == "none":
            notes.append("match_engine=none -- sem motor de match (offline honest-null)")
        elif credential is None:
            notes.append("offline: sem credencial -- motor de reverse-image requer fetch live")

    # Guard against an excluded key sneaking into the join (defensive transparency).
    excl_lc = {e.lower() for e in exclude_keys}
    leaked = [k for k in join_keys if k.lower() in excl_lc]
    if leaked:
        notes.append("chaves excluidas ignoradas no join: %s (EAN/GTIN nunca casam)"
                     % ", ".join(sorted(set(leaked))))
    effective_join = [k for k in join_keys if k.lower() not in excl_lc]

    # F6: SECTION 1 -- Resultado do match (table; columns BYTE-IDENTICAL to mold) -
    mat_cols = ["Codigo", "Match?", "Fonte casada", "Confianca"]
    mat_rows: List[List[Any]] = []
    prov_list: List[Dict[str, Any]] = []
    matched_count = 0
    for idx, item in enumerate(items):
        code = _code_of(item, idx)
        # Offline => never fabricate: every row is an honest NAO at 0.0 confidence.
        if offline:
            mat_rows.append([
                code,
                "NAO",
                _MATCH_ROW_REASON_NO_ENGINE,
                0.0,
            ])
            method = "offline"
            conf = 0.0
        else:
            # A live engine would populate these; this generator runs offline-only today,
            # so even on the live branch we emit an honest "pendente" rather than invent.
            mat_rows.append([
                code,
                "NAO",
                _MATCH_ROW_REASON_ENGINE_PENDING_TEMPLATE % engine,
                0.0,
            ])
            method = engine
            conf = 0.0
        prov_list.append(make_provenance(
            finding="Match::%s" % code,
            source_url=None,
            fetched_at=None,
            method=method,
            confidence=conf,
        ))

    s_match = table_section(
        "Resultado do match",
        mat_cols,
        mat_rows,
        note=_NOTE_MATCH,
    )

    # F6: SECTION 2 -- Auditoria de catalogo (list; runs offline on local data) ---
    audit_flags: List[str] = []
    if audit_enabled:
        for idx, item in enumerate(items):
            flag = _audit_text_vs_photo(item, min_photo_px=min_px)
            if flag:
                audit_flags.append(flag)
        if not audit_flags and items:
            audit_flags.append("Nenhuma divergencia de cadastro/foto detectada nos %d itens"
                               " (text-vs-photo + baixa-res OK)." % len(items))
    else:
        notes.append("audit_enabled=false -- auditoria de catalogo pulada")
        audit_flags.append("Auditoria desligada (audit_enabled=false) -- nenhuma flag emitida.")

    s_audit = list_section(
        "Auditoria de catalogo",
        audit_flags,
        note=_NOTE_AUDIT,
    )

    # F6: SECTION 3 -- Proveniencia (fields; S2 always a section) -----------------
    engine_str = (
        "%s (modo declarado) -- nenhum motor de reverse-image/embedding executado neste run" % engine
        if offline else "%s -- run live" % engine
    )
    status_str = (
        "todas: %s" % _OFFLINE_ENDPOINT_STATUS if offline
        else "ok (run live)"
    )
    honest_str = (
        "match_engine=%s + sem URL publica da foto -> itens sem candidato retornam NAO,"
        " nunca um match inventado" % engine if offline
        else "live -- cada match carrega URL + confianca verificavel"
    )
    s_prov = fields_section(
        "Proveniencia",
        [
            ("Motor de match", engine_str),
            ("Chave de casamento", "%s -- EAN/GTIN/barcode excluidos de proposito (todo"
                                   " revendedor recodifica; nunca entram no join)"
                                   % ("+".join(effective_join) or "(nenhuma)")),
            ("Fontes consultadas", "0 -- %s" % _OFFLINE_ENDPOINT_STATUS if offline
             else "live"),
            ("Status por fonte", status_str),
            ("Honest-null offline", honest_str),
        ],
        note=_NOTE_PROVENANCE,
    )

    # F6: SECTION 4 -- Veredito (fields; S4 named gate match_confiavel) -----------
    # matched_count is 0 offline by construction (never a fabricated match).
    total = len(items)
    gate_pass = (not offline) and (total > 0) and (matched_count >= total)
    cobertura = (
        "%d/%d acima do piso (%.2f)" % (matched_count, total, floor) if total
        else "sem itens"
    )
    blockers: List[str] = []
    if offline:
        blockers.append("precisa de URL publica da foto + motor de reverse-image (Serper/Lens)")
        if engine == "none":
            blockers.append("match_engine ainda em none")
    if total == 0:
        blockers.append("nenhum item fornecido em items")
    # surface low-res / no-photo items as blockers too (auditable offline)
    for idx, item in enumerate(items):
        f = _audit_text_vs_photo(item, min_photo_px=min_px)
        if f and ("sem foto" in f or "baixa-res" in f):
            blockers.append(f)

    s_veredito = fields_section(
        "Veredito",
        [
            ("match_confiavel", "true" if gate_pass else "false -- cobertura %s" % cobertura),
            ("Cobertura", cobertura),
            ("Bloqueadores", "; ".join(blockers) if blockers else "nenhum (gate APROVADO)"),
        ],
        note=_NOTE_VEREDITO,
    )

    sections = [s_match, s_audit, s_prov, s_veredito]

    # F7: govern (S1-S5 from n01_sourcing_rigor) --------------------------------
    score = 1.0
    if offline:
        score -= _SCORE_PENALTY_OFFLINE
        notes.append("offline scaffold -- score reduzido (sem motor de match real)")
    if total == 0:
        score -= _SCORE_PENALTY_ZERO_ITEMS
    # audit findings are valuable signal, not a penalty; only no-photo coverage hurts trust
    no_photo = sum(1 for it in items if not str(it.get("photo_uri") or "").strip())
    if total and no_photo:
        score -= min(_SCORE_PENALTY_NO_PHOTO_CAP, _SCORE_PENALTY_PER_NO_PHOTO * no_photo)
        notes.append("%d/%d itens sem foto -- cobertura de match por imagem limitada"
                     % (no_photo, total))

    passed = gate_pass

    # confidence_breakdown: honest -- 0 sources offline, recency/agreement null.
    confidence_breakdown = {
        "overall": max(0.0, min(1.0, score)),
        "source_count": 0 if offline else None,
        "recency": None,
        "agreement": None,
    }

    return structured_output(
        KIND,
        sections,
        passed=passed,
        score=max(0.0, min(1.0, score)),
        artifact=_artifact_json(items, engine, floor, gate_pass, matched_count, kind=_kind),
        real=True,
        notes=notes,
        provenance=prov_list,
        confidence_breakdown=confidence_breakdown,
    )


# --------------------------------------------------------------------------- #
# Domain contract (Missao A / MOLDED_REAL_SEAM export-deepening) -- the REAL domain law
# this generator enforces, exposed for cex_export_agent.py to bake into an exported agent
# package (system_instruction GROUNDING + a new knowledge/domain_contract.md bundle file)
# instead of a generic ISO-scaffold. Discovered via capability_generators._base.
# get_domain_contract (module-level convention -- see that function's docstring).
#
# SINGLE SOURCE OF TRUTH: every value below is a REFERENCE to a module constant build() (or
# one of its PURE helpers -- _normalize_join_key / _piece_count) reads above -- never a
# re-typed literal -- so an exported bundle can never drift from what this generator
# actually enforces at runtime. Two entries are GENERIC (non-interpolated) siblings of a
# %-templated runtime string (_JOIN_KEY_EXCLUSION_RULE_GENERIC,
# _MATCH_ROW_REASON_ENGINE_PENDING_GENERIC): domain_contract() has no specific per-run value
# to interpolate, so it uses the rule's generic phrasing instead (same split as ads.py's
# _COMPLIANCE_CHARS_TEMPLATE / _COMPLIANCE_CHARS_GENERIC).
#
# HONEST FRAMING: product_match.py is NOT an LLM-creative / wave-1-scaffold generator like
# ads.py/docs.py -- it is RUN_MODE="offline-deterministic" BY DESIGN (the live branch above
# still emits an honest "pendente" rather than invent a match). So there is no fake/
# placeholder creative scaffold to expose here the way ads.py's _scaffold_row or docs.py's
# step-by-step content are -- every value below is real, permanent domain law, not
# provisional filler standing in for a future LLM pass. 'offline_fallback_messages' are the
# literal, honest-null text this generator always emits when no live reverse-image engine
# ran -- included for transparency, not because they are placeholders awaiting replacement.
#
# ALSO HONEST: 'defaults.confidence_floor' is a DECLARED, threaded-through contract value
# (parsed, clamped, surfaced in the artifact JSON + the Cobertura text) -- but no live
# reverse-image/embedding engine is implemented yet, so no code path in build() today ever
# computes a confidence > 0.0 and compares it against this floor to promote a row to
# SIM/PARCIAL. It is forward-declared law for the engine this generator will call once one
# is wired in, not (yet) an actively-exercised gate (see the "matched_count is 0 offline by
# construction" comment above).
# --------------------------------------------------------------------------- #
def domain_contract() -> dict:
    """The REAL domain law product_match.py enforces on every match/audit run (Missao A).
    Returns a structured, JSON-serialisable dict -- never {} for THIS generator (product_match
    DOES declare domain law: the match_engine/endpoint_status enums, the input-contract
    defaults, the EAN/GTIN/barcode join-exclusion rule + the join-key -> item-field alias
    map _normalize_join_key uses, the piece-count divergence tokens _piece_count recognizes,
    the F7 scoring penalties, and the per-section rule notes baked into every run; {} is
    only the _base.py no-op default for a generator with none)."""
    return {
        "contract_version": CONTRACT_VERSION,
        "run_mode": RUN_MODE,
        "enums": {
            "match_engine": list(_MATCH_ENGINE_ENUM),
            "endpoint_status": list(_ENDPOINT_STATUS_ENUM),
        },
        "defaults": {
            "match_engine": _DEFAULT_MATCH_ENGINE,
            "join_keys": list(_DEFAULT_JOIN_KEYS),
            "confidence_floor": _DEFAULT_CONFIDENCE_FLOOR,
            "min_photo_px": _DEFAULT_MIN_PHOTO_PX,
        },
        "excluded_join_keys": list(_DEFAULT_EXCLUDE_KEYS),
        "join_key_exclusion_reason": _JOIN_KEY_EXCLUSION_RULE_GENERIC,
        "join_key_field_aliases": {
            k: list(v) for k, v in _JOIN_KEY_FIELD_ALIASES.items()
        },
        "piece_count_conflict_tokens": list(_PIECE_COUNT_TOKENS),
        "score_penalties": {
            "offline": _SCORE_PENALTY_OFFLINE,
            "zero_items": _SCORE_PENALTY_ZERO_ITEMS,
            "per_missing_photo": _SCORE_PENALTY_PER_NO_PHOTO,
            "missing_photo_cap": _SCORE_PENALTY_NO_PHOTO_CAP,
        },
        "offline_endpoint_status": _OFFLINE_ENDPOINT_STATUS,
        "offline_fallback_messages": {
            "match_row_no_engine": _MATCH_ROW_REASON_NO_ENGINE,
            "match_row_engine_pending": _MATCH_ROW_REASON_ENGINE_PENDING_GENERIC,
        },
        "section_rule_notes": {
            "resultado_do_match": _NOTE_MATCH,
            "auditoria_de_catalogo": _NOTE_AUDIT,
            "proveniencia": _NOTE_PROVENANCE,
            "veredito": _NOTE_VEREDITO,
        },
    }


# --------------------------------------------------------------------------- #
# Media hooks (public -- canonical unprefixed pair; resolve_media discovers these).
# --------------------------------------------------------------------------- #

def product_match_media_requests(inputs: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Declare ONE image slot: match_grid (the side-by-side supplier-vs-listing photos).

    ALWAYS declared; starts as upload-fallback until a live reverse-image run renders the
    grid. NEVER-FABRICATE: no src emitted here. PURE + TOTAL: never raises."""
    return [
        {
            "key": "match_grid",
            "kind": "image",
            "section": "Resultado do match",
            "label": "Grade de comparacao (foto fornecedor x anuncio casado)",
        }
    ]


def product_match_produced_media(inputs: Mapping[str, Any]) -> Dict[str, Any]:
    """Map match_grid to a real image src ONLY when inputs['match_grid_url'] is non-empty
    (a live run injects a rendered comparison-grid URL). Blank -> empty dict -> the slot
    stays upload-fallback. NEVER-FABRICATE. PURE + TOTAL: never raises."""
    produced: Dict[str, Any] = {}
    grid_url = str(inputs.get("match_grid_url") or "").strip()
    if grid_url:
        produced["match_grid"] = {"src": grid_url, "alt": "Grade de comparacao de produtos"}
    return produced


__all__ = [
    "KIND",
    "build",
    "_normalize_join_key",
    "_audit_text_vs_photo",
    "product_match_media_requests",
    "product_match_produced_media",
    # Missao A / MOLDED_REAL_SEAM: the real domain-law contract (cex_export_agent.py).
    "domain_contract",
]

#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI research-universe CONTRACT -- cex_research_universe_contract (the GROWTH-FIRST schema).

THE formal input/output contract for the research-universe orchestrator (cex_research_universe).
Modelled on the marketplace contract (cex_output_contract.PESQUISA_PRODUTO_CONTRACT) -- an ordered,
VERSIONED, APPEND-ONLY field schema + a PURE dual MD/HTML renderer that walks the contract EXACTLY
ONCE -- but generalised so the universe report (firmographics, market, reputation, social, keywords,
questions, sentiment, + the marketplace PRODUCT section) is ONE typed object.

  +------------------------------------------------------------------------------------------------+
  |  DESIGNED FOR GROWTH (the founder's explicit ask): a NEW lane / source plugs in as DATA,        |
  |  not code. Adding a lane = adding ONE ``LANE_REGISTRY`` entry (its seed_types, the section it    |
  |  fills, and that section's fields). Routing (``select_lanes``), assembly, schema-validation,     |
  |  and BOTH render projections are DRIVEN BY the registry -- none of them has a per-lane branch.   |
  |  The ``test_research_universe_contract.py`` GROWTH PROOF registers a fake ``demo_lane`` and       |
  |  shows it flows end-to-end (routing -> section -> MD+HTML) with ZERO code change beyond the entry.|
  +------------------------------------------------------------------------------------------------+

THE THREE DECLARED OBJECTS
  1. ``LANE_REGISTRY`` -- the GROWTH mechanism. ``lane_name -> {seed_types_served, section, label,
     fields, ...}``. ``seed_types_served`` is an ORDERED map ``{seed_type: order_index}`` so the
     registry reproduces the orchestrator's per-seed-type lane ORDER exactly (brand and keyword
     order reddit/youtube/seo differently -- a per-type index captures that without a code branch).
  2. ``RESEARCH_UNIVERSE_CONTRACT`` -- the output schema, DERIVED from the registry (so a new lane's
     section/fields appear automatically) + the two non-lane sections (identity reuses the cnpj lane;
     ``product`` is COMPOSED from the marketplace contract, never duplicated). Carries ``schema_version``
     and an ordered ``sections`` list + a flat ordered ``fields`` list (name/label/type/section/source_lane).
  3. ``RESEARCH_UNIVERSE_INPUT_SCHEMA`` -- the declared INPUT contract: ``{seed, seed_type?, kinds?,
     per_lane_params?, budget?}``. ``validate_input`` returns a normalised request + honest ``dropped``
     notes (an unknown ``kinds`` lane is dropped, never fabricated into a lane).

RECONCILIATION WITH THE MARKETPLACE CONTRACT (the founder's point 5)
  A marketplace / product seed's report carries a ``product`` SECTION whose fields ARE the marketplace
  ``PESQUISA_PRODUTO_CONTRACT`` fields -- COMPOSED by reference (``_product_section_fields`` re-tags the
  marketplace field descriptors with ``section='product'`` + ``source_lane='product'``), NEVER copied.
  The marketplace contract stays the single source of truth for those fields; if it grows, this section
  grows with it on next import. ``render_universe`` delegates the product sub-report to the marketplace
  ``render`` so the product projection is byte-identical to a standalone marketplace render.

THE RENDERER (the founder's point 4) -- ``render_universe(report) -> {"md", "html"}``
  PURE dual projection (no LLM / network / IO). Walks ``RESEARCH_UNIVERSE_CONTRACT`` ONCE:
    * MD  (canonical AI view): YAML frontmatter (schema_version + provenance + per-section status) +
      one code-fenced block PER section in contract order. A NEW section auto-renders (zero new code).
    * HTML (human view): a self-contained report -- one card per section, an endpoint-status table, a
      provenance roll-up, the sentiment badge. Always derivative of the MD.
  Both reuse the marketplace module's value-coercion + safe-YAML helpers (one house style, no
  duplicated serialiser). The product section, when present, is rendered by the marketplace renderer
  and EMBEDDED (md fenced verbatim; html inlined) so there is ONE product projection in the codebase.

INVARIANTS (mirrors the orchestrator + marketplace contract):
  never-fabricate (a blocked/absent lane renders blank/honest-status, never invented data);
  degrade-never (every function is TOTAL -- a malformed report/contract degrades to a valid-but-empty
  projection, never raises); ASCII-only (.claude/rules/ascii-code-rule.md; PT labels use \\uXXXX
  escapes); append-only (existing sections/fields are never reordered/removed -- new ones APPEND);
  backward-compatible (the orchestrator's existing report dict is a VALID contract instance -- the
  contract formalises + validates the shape already on disk; the 19 test_research_universe.py tests
  stay green).

Spec lineage: reference_research_universe_taxonomy_2026_06_19 (the 12 research-types) +
cex_output_contract (the append-only dual-render pattern this generalises) + cex_research_universe
(the orchestrator whose report shape this types). Consumed by: cex_research_universe.research_universe
(validates input + exposes render_universe) + any dashboard ?render_format=md|html projection.

ASCII-only. Fully type-hinted. PURE -- declares + projects; performs no network/IO.
"""

from __future__ import annotations

import sys
from html import escape as _html_escape
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

# Make the _tools dir importable so the marketplace contract resolves whether this file is imported
# from the repo root or run as a script (mirrors the orchestrator's seam-import posture).
_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

# The marketplace contract is COMPOSED (its fields become the universe ``product`` section) + its PURE
# helpers are REUSED (one house serialiser). Imported lazily-safe: if it is ever absent the universe
# contract still works (the product section degrades to empty) -- degrade-never.
try:  # pragma: no cover - import shape is environment-trivial; both branches are exercised by tests.
    import cex_output_contract as _mkt  # the marketplace dual-render module.
    _MKT_AVAILABLE = True
except Exception:  # pragma: no cover
    _mkt = None  # type: ignore[assignment]
    _MKT_AVAILABLE = False


# --------------------------------------------------------------------------- #
# Module constants.
# --------------------------------------------------------------------------- #
# The contract's own schema version (independent of the marketplace SCHEMA_VERSION). Bump the MINOR
# when sections/fields are APPENDED (append-only growth); bump the MAJOR only for a breaking reshape
# (which the append-only invariant is designed to avoid).
SCHEMA_VERSION = "1.0"

# The canonical lane names (kept in lock-step with cex_research_universe.LANES -- this module declares
# the SCHEMA for those lanes; the orchestrator owns the network). Re-declared here as literals (not
# imported) so the contract module never pulls the orchestrator at import time (no import cycle).
LANE_CNPJ = "cnpj"
LANE_IBGE = "ibge"
LANE_APPSTORE = "appstore"
LANE_REDDIT = "reddit"
LANE_YOUTUBE = "youtube"
LANE_RECLAME_AQUI = "reclame_aqui"
LANE_SEO = "seo"
LANE_QUESTIONS = "questions"

# The non-lane / composed sections (declared so the contract carries them even though no routable lane
# "fills" them through the registry's seed-type routing):
#   * ``identity``  -- the cnpj lane ALSO writes sections['identity'] (firmographics is its reserved
#                      alias slot); declared as a section but its fields come from the cnpj registry
#                      entry (section_alias), so we do not double-route.
#   * ``sentiment_summary`` -- an ENRICHMENT the orchestrator computes over collected text (not a lane).
#   * ``product``   -- COMPOSED from the marketplace PESQUISA_PRODUTO_CONTRACT (point 5).
SECTION_PRODUCT = "product"
SECTION_SENTIMENT = "sentiment_summary"
SECTION_FIRMOGRAPHICS = "firmographics"


def _f(
    name: str, label: str, ftype: str, section: str, source_lane: str,
) -> Dict[str, str]:
    """Build one ordered contract field descriptor (terse helper, PURE). A universe field adds
    ``source_lane`` (which lane/section produced it) to the marketplace field shape so provenance is
    declared in the schema itself."""
    return {
        "name": name,
        "label": label,
        "type": ftype,
        "section": section,
        "source_lane": source_lane,
    }


# The NON-LANE section fields -- the composed/enrichment sections that no routable lane "fills" through
# the registry's seed-type routing, but which the contract still TYPES so they render. ``product`` is
# composed from the marketplace contract (handled separately); ``sentiment_summary`` is the
# orchestrator's enrichment aggregate. APPEND-ONLY (extend at the tail). source_lane names the producer.
_NON_LANE_SECTION_FIELDS: Dict[str, List[Dict[str, str]]] = {
    SECTION_SENTIMENT: [
        _f("label", "Polaridade", "string", SECTION_SENTIMENT, "sentiment"),
        _f("pos", "Positivos", "number", SECTION_SENTIMENT, "sentiment"),
        _f("neu", "Neutros", "number", SECTION_SENTIMENT, "sentiment"),
        _f("neg", "Negativos", "number", SECTION_SENTIMENT, "sentiment"),
        _f("analyzed", "Itens Analisados", "number", SECTION_SENTIMENT, "sentiment"),
        _f("method", "Metodo", "string", SECTION_SENTIMENT, "sentiment"),
    ],
}


# --------------------------------------------------------------------------- #
# THE LANE REGISTRY -- the growth mechanism. Adding a lane == adding an entry here.
#
# Each entry:
#   seed_types_served: an ORDERED map {seed_type: order_index}. A lane is selected for a seed_type iff
#                      it appears here; the index gives its POSITION in that type's lane list (so the
#                      registry reproduces the orchestrator's per-type ordering EXACTLY without a code
#                      branch -- brand orders reddit<youtube<seo, keyword orders seo<youtube<reddit).
#   section:           the report ``sections[...]`` key this lane writes.
#   section_label:     the human label for that section (used by the schema + both renderers).
#   section_alias:     OPTIONAL -- a second declared section name that maps to the SAME data (the cnpj
#                      lane declares section='identity' with alias='firmographics' so both appear in the
#                      contract section list while only one lane routes). PURE-metadata, no routing.
#   fields:            the ordered field descriptors this section contributes to the schema.
#   render_hint:       OPTIONAL projection hint for a whole section ('product' -> delegate to the
#                      marketplace renderer). Absent -> the generic section renderer is used.
#
# APPEND-ONLY: a new lane APPENDS a new key; an existing entry's fields are extended at the TAIL only.
# The orchestrator's routing/assembly read THIS registry (see cex_research_universe), so a registry
# edit is the ONLY change needed to grow a lane.
# --------------------------------------------------------------------------- #
LANE_REGISTRY: Dict[str, Dict[str, Any]] = {
    # --- Firmographics (B2B) -- the cnpj lane. Writes sections['identity']; 'firmographics' is its
    # reserved alias slot (declared so both names appear in the contract; only 'identity' is routed).
    LANE_CNPJ: {
        "seed_types_served": {"cnpj": 0},
        "section": "identity",
        "section_label": "Identidade e Firmografia (B2B)",
        "section_alias": SECTION_FIRMOGRAPHICS,
        "fields": [
            _f("cnpj", "CNPJ", "string", "identity", LANE_CNPJ),
            _f("razao_social", "Razao Social", "string", "identity", LANE_CNPJ),
            _f("nome_fantasia", "Nome Fantasia", "string", "identity", LANE_CNPJ),
            _f("uf", "UF", "string", "identity", LANE_CNPJ),
            _f("municipio", "Municipio", "string", "identity", LANE_CNPJ),
            _f("situacao", "Situacao Cadastral", "string", "identity", LANE_CNPJ),
            _f("cnae_principal", "CNAE Principal", "string", "identity", LANE_CNPJ),
            _f("porte", "Porte", "string", "identity", LANE_CNPJ),
        ],
    },
    # --- Market-sizing -- the ibge lane. Writes sections['market'].
    LANE_IBGE: {
        "seed_types_served": {"cnpj": 1},
        "section": "market",
        "section_label": "Tamanho de Mercado (IBGE/SIDRA)",
        "fields": [
            _f("preset", "Preset SIDRA", "string", "market", LANE_IBGE),
            _f("summary", "Resumo (TAM)", "object", "market", LANE_IBGE),
            _f("row_count", "Linhas", "number", "market", LANE_IBGE),
            _f("rows", "Series", "list", "market", LANE_IBGE),
        ],
    },
    # --- Reputation (mobile app) -- the appstore lane. Writes sections['social']['appstore'].
    LANE_APPSTORE: {
        "seed_types_served": {"app": 0, "brand": 0, "company": 0},
        "section": "social",
        "section_label": "Sinal Social e Reputacao",
        "subkey": "appstore",  # this lane writes a SUB-record under sections['social'][subkey].
        "fields": [
            _f("app_id", "ID do App", "string", "social", LANE_APPSTORE),
            _f("store", "Loja", "string", "social", LANE_APPSTORE),
            _f("rating_avg", "Nota Media", "number", "social", LANE_APPSTORE),
            _f("ratings_count", "Qtd de Notas", "number", "social", LANE_APPSTORE),
            _f("reviews_count", "Reviews Coletados", "number", "social", LANE_APPSTORE),
        ],
    },
    # --- Social-inbound (Reddit) -- writes sections['social']['reddit'].
    LANE_REDDIT: {
        "seed_types_served": {"keyword": 2, "brand": 1, "company": 1},
        "section": "social",
        "section_label": "Sinal Social e Reputacao",
        "subkey": "reddit",
        "fields": [
            _f("reddit_query", "Termo (Reddit)", "string", "social", LANE_REDDIT),
            _f("reddit_result_count", "Posts Coletados", "number", "social", LANE_REDDIT),
        ],
    },
    # --- Social-inbound (YouTube) -- writes sections['social']['youtube'].
    LANE_YOUTUBE: {
        "seed_types_served": {"keyword": 1, "brand": 2, "company": 2},
        "section": "social",
        "section_label": "Sinal Social e Reputacao",
        "subkey": "youtube",
        "fields": [
            _f("youtube_query", "Termo (YouTube)", "string", "social", LANE_YOUTUBE),
            _f("youtube_videos_count", "Videos", "number", "social", LANE_YOUTUBE),
            _f("youtube_comments_count", "Comentarios", "number", "social", LANE_YOUTUBE),
        ],
    },
    # --- Reputation (company) -- the reclame_aqui lane. Writes sections['reputation'].
    LANE_RECLAME_AQUI: {
        "seed_types_served": {"brand": 3, "company": 3},
        "section": "reputation",
        "section_label": "Reputacao (Reclame Aqui)",
        "fields": [
            _f("company", "Empresa", "object", "reputation", LANE_RECLAME_AQUI),
            _f("complaints_count", "Reclamacoes Coletadas", "number", "reputation", LANE_RECLAME_AQUI),
        ],
    },
    # --- Keyword discovery (SEO) -- writes sections['keywords'].
    LANE_SEO: {
        "seed_types_served": {"keyword": 0, "brand": 4, "company": 4},
        "section": "keywords",
        "section_label": "Palavras-Chave (SEO)",
        "fields": [
            _f("seed", "Semente", "string", "keywords", LANE_SEO),
            _f("suggestions", "Sugestoes", "list", "keywords", LANE_SEO),
            _f("related", "Relacionados", "list", "keywords", LANE_SEO),
            _f("volume", "Volume", "number", "keywords", LANE_SEO),
            _f("volume_note", "Nota de Volume", "string", "keywords", LANE_SEO),
        ],
    },
    # --- Multi-perspective question planning -- writes sections['questions'].
    LANE_QUESTIONS: {
        "seed_types_served": {"brand": 5, "company": 5},
        "section": "questions",
        "section_label": "Perguntas Multi-Perspectiva",
        "fields": [
            _f("count", "Qtd de Perguntas", "number", "questions", LANE_QUESTIONS),
            _f("method", "Metodo", "string", "questions", LANE_QUESTIONS),
            _f("questions", "Perguntas", "list", "questions", LANE_QUESTIONS),
        ],
    },
}


# --------------------------------------------------------------------------- #
# Registry-driven routing (the orchestrator delegates select_lanes to THIS). PURE + TOTAL.
# --------------------------------------------------------------------------- #
def registry_lanes() -> List[str]:
    """The full set of routable lane names declared in the registry (the override vocabulary). PURE.
    Order is the registry declaration order (stable)."""
    return list(LANE_REGISTRY.keys())


def lanes_for_seed_type(seed_type: str) -> List[str]:
    """The ordered lane list a ``seed_type`` selects, DERIVED FROM the registry (the growth mechanism:
    a new lane that serves this type appears here automatically). A lane is included iff its
    ``seed_types_served`` map contains ``seed_type``; the per-type ``order_index`` gives its position
    (so a new lane chooses where it sits by its index). TOTAL: an unknown seed_type -> the 'brand'
    fan-out (the safe broad default, matching the orchestrator). NEVER fabricates a lane.

    Ties on the same index are broken by the registry declaration order (deterministic)."""
    if not isinstance(seed_type, str):
        seed_type = "brand"
    selected: List[Tuple[int, int, str]] = []
    for decl_order, (lane, entry) in enumerate(LANE_REGISTRY.items()):
        served = entry.get("seed_types_served")
        if isinstance(served, Mapping) and seed_type in served:
            idx = served.get(seed_type)
            idx = int(idx) if isinstance(idx, (int, float)) else decl_order
            selected.append((idx, decl_order, lane))
    if selected:
        selected.sort(key=lambda t: (t[0], t[1]))
        return [lane for _idx, _decl, lane in selected]
    # Unknown seed_type -> the 'brand' fan-out (safe broad default; matches the orchestrator's table).
    if seed_type != "brand":
        return lanes_for_seed_type("brand")
    return []


def lane_section(lane: str) -> Optional[str]:
    """The report section a lane writes (``sections[...]`` key), or None. PURE + TOTAL."""
    entry = LANE_REGISTRY.get(lane)
    if isinstance(entry, Mapping):
        sect = entry.get("section")
        return sect if isinstance(sect, str) else None
    return None


def lane_subkey(lane: str) -> Optional[str]:
    """For a lane that writes a SUB-record under ``sections['social'][subkey]`` (appstore/reddit/
    youtube), its subkey; else None (the lane writes the whole section). PURE + TOTAL."""
    entry = LANE_REGISTRY.get(lane)
    if isinstance(entry, Mapping):
        sub = entry.get("subkey")
        return sub if isinstance(sub, str) else None
    return None


# --------------------------------------------------------------------------- #
# THE OUTPUT CONTRACT -- DERIVED from the registry (so a new lane's section/fields appear here for
# free) + the composed/enrichment sections. APPEND-ONLY + VERSIONED.
# --------------------------------------------------------------------------- #
def _ordered_section_ids() -> List[str]:
    """The CANONICAL ordered section id list (the founder's required order + growth room). The order
    is STABLE and APPEND-ONLY: identity, firmographics, market, reputation, social, keywords,
    questions, sentiment_summary, product, then ANY new registry section (a brand-new lane writing a
    brand-new section appends here automatically -- the GROWTH path). PURE."""
    # The required spine, in the founder's order (firmographics sits next to identity as its alias).
    spine = [
        "identity",
        SECTION_FIRMOGRAPHICS,
        "market",
        "reputation",
        "social",
        "keywords",
        "questions",
        SECTION_SENTIMENT,
        SECTION_PRODUCT,
    ]
    seen = set(spine)
    # Append any registry section NOT already in the spine (the growth slot -- a new lane's new section).
    for entry in LANE_REGISTRY.values():
        sect = entry.get("section")
        if isinstance(sect, str) and sect not in seen:
            seen.add(sect)
            spine.append(sect)
        alias = entry.get("section_alias")
        if isinstance(alias, str) and alias not in seen:
            seen.add(alias)
            spine.append(alias)
    return spine


def _section_label(section_id: str) -> str:
    """The human label for a section id (from the first registry entry that declares it, else a sane
    default for the composed/enrichment sections). PURE + TOTAL."""
    for entry in LANE_REGISTRY.values():
        if entry.get("section") == section_id or entry.get("section_alias") == section_id:
            lab = entry.get("section_label")
            if isinstance(lab, str) and lab:
                return lab
    defaults = {
        SECTION_SENTIMENT: "Sentimento (Agregado)",
        SECTION_PRODUCT: "Produto (Marketplace)",
        SECTION_FIRMOGRAPHICS: "Firmografia",
        "identity": "Identidade",
    }
    return defaults.get(section_id, section_id.replace("_", " ").title())


def _product_section_fields() -> List[Dict[str, str]]:
    """The ``product`` section fields -- COMPOSED from the marketplace PESQUISA_PRODUTO_CONTRACT, NEVER
    duplicated. Each marketplace field descriptor is RE-TAGGED with section='product' +
    source_lane='product' so it slots into the universe schema while the marketplace contract stays the
    single source of truth (if it grows, this section grows on next import). TOTAL: if the marketplace
    contract is absent the product section is simply empty (degrade-never)."""
    if not _MKT_AVAILABLE or _mkt is None:
        return []
    contract = getattr(_mkt, "PESQUISA_PRODUTO_CONTRACT", None)
    if not isinstance(contract, Mapping):
        return []
    out: List[Dict[str, str]] = []
    for field in contract.get("fields", []) or []:
        if not isinstance(field, Mapping):
            continue
        name = field.get("name")
        if not name:
            continue
        out.append(_f(
            str(name),
            str(field.get("label") or name),
            str(field.get("type") or "string"),
            SECTION_PRODUCT,
            SECTION_PRODUCT,
        ))
    return out


def _build_sections() -> List[Dict[str, str]]:
    """The ordered ``sections`` list of the contract (id + label), in the canonical/growth order. PURE."""
    return [{"id": sid, "label": _section_label(sid)} for sid in _ordered_section_ids()]


def _build_fields() -> List[Dict[str, str]]:
    """The flat ordered ``fields`` list of the contract -- the union of every registry section's fields
    (in section order) PLUS the composed ``product`` fields. A new lane's fields appear here for free
    (the GROWTH path: routing + schema both read the registry). APPEND-ONLY + PURE.

    Order: walk the canonical section order; for each section emit the fields the registry declares for
    it, then the product fields when the product section is reached. Dedup is PER-SECTION (a field name
    is unique WITHIN a section, but the SAME name may recur across sections -- e.g. 'method' lives in
    both questions and sentiment_summary, 'label' in sentiment_summary; a global dedup would wrongly drop
    the later one). The identity/firmographics alias shares the cnpj fields (declared once, under
    'identity'; the alias section is NOT re-emitted to avoid duplicating the same fields)."""
    fields: List[Dict[str, str]] = []

    # Index registry fields by their declared section.
    by_section: Dict[str, List[Dict[str, str]]] = {}
    for entry in LANE_REGISTRY.values():
        sect = entry.get("section")
        for field in entry.get("fields", []) or []:
            if not isinstance(field, Mapping):
                continue
            target = field.get("section") or sect
            if isinstance(target, str):
                by_section.setdefault(target, []).append(dict(field))

    # The alias sections (e.g. 'firmographics' aliasing 'identity') share their canonical section's
    # fields -- do NOT re-emit them under the alias id (the alias appears in the sections list only).
    alias_ids = {
        entry.get("section_alias")
        for entry in LANE_REGISTRY.values()
        if isinstance(entry.get("section_alias"), str)
    }

    for sid in _ordered_section_ids():
        if sid in alias_ids:
            continue  # alias section: its fields live under the canonical section id.
        if sid == SECTION_PRODUCT:
            fields.extend(_product_section_fields())
            continue
        seen_in_section: set = set()
        # Lane-fed fields for this section, then non-lane/enrichment fields (e.g. sentiment_summary).
        for field in by_section.get(sid, []) + _NON_LANE_SECTION_FIELDS.get(sid, []):
            nm = field.get("name")
            if nm and nm not in seen_in_section:
                seen_in_section.add(nm)
                fields.append(dict(field))
    return fields


# The DECLARED, VERSIONED contract -- built ONCE at import from the registry (so it always reflects the
# current registry, including any newly-registered growth lane). A consumer reads RESEARCH_UNIVERSE_CONTRACT
# exactly like the marketplace PESQUISA_PRODUTO_CONTRACT.
def build_contract() -> Dict[str, Any]:
    """Assemble the full RESEARCH_UNIVERSE_CONTRACT dict from the current registry. PURE + idempotent.
    Exposed as a function (not just the module constant) so a test that registers a growth lane can
    REBUILD the contract and see the new section/fields without re-importing the module."""
    return {
        "schema_id": "research_universe",
        "schema_version": SCHEMA_VERSION,
        "title_field": "seed",
        "summary_field": "seed_type",
        "sections": _build_sections(),
        "fields": _build_fields(),
    }


RESEARCH_UNIVERSE_CONTRACT: Dict[str, Any] = build_contract()


# --------------------------------------------------------------------------- #
# THE INPUT SCHEMA -- declared + validated. {seed, seed_type?, kinds?, per_lane_params?, budget?}.
# --------------------------------------------------------------------------- #
RESEARCH_UNIVERSE_INPUT_SCHEMA: Dict[str, Any] = {
    "schema_id": "research_universe_input",
    "schema_version": SCHEMA_VERSION,
    "fields": [
        {"name": "seed", "type": "string", "required": True,
         "desc": "The research subject (brand/product/CNPJ/company/keyword/store:id)."},
        {"name": "seed_type", "type": "string", "required": False,
         "desc": "Explicit routing override (cnpj|app|keyword|company|brand); else inferred."},
        {"name": "kinds", "type": "list", "required": False,
         "desc": "Force EXACTLY these lanes (subset of the registry lanes); unknown names dropped."},
        {"name": "per_lane_params", "type": "object", "required": False,
         "desc": "Optional per-lane parameter overrides: {lane_name: {param: value}}."},
        {"name": "budget", "type": "object", "required": False,
         "desc": "Optional budget hints (e.g. {max_items, max_text_chars}); advisory."},
    ],
}


def validate_input(request: Any) -> Dict[str, Any]:
    """Validate + normalise a research-universe INPUT request against RESEARCH_UNIVERSE_INPUT_SCHEMA.

    Returns a dict:
      {
        "valid": bool,                     # False only when ``seed`` is missing/empty (the one required)
        "seed": str,                       # normalised (stripped) seed
        "seed_type": Optional[str],        # an explicit override iff it is a KNOWN type, else None
        "kinds": Optional[List[str]],      # the VALID subset of registry lanes, or None (no override)
        "per_lane_params": Dict[str, Any], # per-lane params for KNOWN lanes only
        "budget": Dict[str, Any],          # the budget mapping (passed through; advisory)
        "dropped": {                       # HONEST record of what was dropped + why (never fabricated)
            "kinds": [...],                # unknown lane names in ``kinds`` that were dropped
            "seed_type": Optional[str],    # an unknown seed_type override that was dropped
            "per_lane_params": [...],      # per-lane param keys for unknown lanes that were dropped
        },
        "errors": [...],                   # human-readable validation errors (e.g. missing seed)
      }

    PURE + TOTAL: never raises. A non-mapping request is treated as ``{"seed": <str(request)>}`` when it
    is a bare string (the common CLI case), else an invalid empty request. NEVER fabricates a lane /
    type -- an unknown kind/type is DROPPED and recorded honestly."""
    known_lanes = set(registry_lanes())
    known_types = {"cnpj", "app", "keyword", "company", "brand"}

    out: Dict[str, Any] = {
        "valid": False,
        "seed": "",
        "seed_type": None,
        "kinds": None,
        "per_lane_params": {},
        "budget": {},
        "dropped": {"kinds": [], "seed_type": None, "per_lane_params": []},
        "errors": [],
    }

    # Accept a bare string request as {"seed": ...} (the CLI passes a string).
    if isinstance(request, str):
        request = {"seed": request}
    if not isinstance(request, Mapping):
        out["errors"].append("request must be a mapping or a seed string")
        return out

    # seed (required).
    seed = request.get("seed")
    seed_str = seed.strip() if isinstance(seed, str) else ""
    out["seed"] = seed_str
    if not seed_str:
        out["errors"].append("seed is required and must be a non-empty string")
    else:
        out["valid"] = True

    # seed_type (optional override; honored only if KNOWN).
    st = request.get("seed_type")
    if isinstance(st, str) and st.strip():
        st_norm = st.strip().lower()
        if st_norm in known_types:
            out["seed_type"] = st_norm
        else:
            out["dropped"]["seed_type"] = st_norm  # honest: unknown override dropped, inference applies.

    # kinds (optional; the valid subset of registry lanes; unknowns dropped honestly).
    kinds = request.get("kinds")
    if kinds is not None:
        if isinstance(kinds, str):
            items: Sequence[Any] = [p for p in kinds.replace(",", " ").split()]
        elif isinstance(kinds, (list, tuple)):
            items = kinds
        else:
            items = []
        valid_kinds: List[str] = []
        seen: set = set()
        for item in items:
            name = item.strip().lower() if isinstance(item, str) else ""
            if name in known_lanes and name not in seen:
                seen.add(name)
                valid_kinds.append(name)
            elif name:
                out["dropped"]["kinds"].append(name)  # honest: unknown lane dropped, never fabricated.
        out["kinds"] = valid_kinds or None

    # per_lane_params (optional; keep only KNOWN lanes).
    plp = request.get("per_lane_params")
    if isinstance(plp, Mapping):
        for lane, params in plp.items():
            lane_name = str(lane).strip().lower()
            if lane_name in known_lanes:
                out["per_lane_params"][lane_name] = params
            else:
                out["dropped"]["per_lane_params"].append(lane_name)

    # budget (optional; passed through as a mapping; advisory).
    budget = request.get("budget")
    if isinstance(budget, Mapping):
        out["budget"] = {str(k): v for k, v in budget.items()}

    return out


# --------------------------------------------------------------------------- #
# THE DUAL RENDERER -- render_universe(report) -> {"md", "html"}. PURE; walks the contract ONCE.
# --------------------------------------------------------------------------- #
def render_universe(
    report: Mapping[str, Any],
    contract: Optional[Mapping[str, Any]] = None,
) -> Dict[str, str]:
    """Render ONE research_universe_report into {"md": <str>, "html": <str>} (the dual emitter).

    PURE: no LLM, no network, no IO. Walks ``contract['sections']`` EXACTLY ONCE (no per-lane
    branching) -- a NEW section auto-renders. The ``product`` section, when the report carries one, is
    delegated to the marketplace renderer + embedded (so the product projection is byte-identical to a
    standalone marketplace render -- ONE product renderer in the codebase).

    Args:
      report: the orchestrator's research_universe_report dict (or any compatible mapping).
      contract: the schema to walk; defaults to RESEARCH_UNIVERSE_CONTRACT. Passing a freshly-built
        contract (after registering a growth lane) makes the new section render.

    TOTAL: a missing section/field renders blank; a malformed report/contract degrades to a valid-but-
    empty pair (never raises)."""
    if not isinstance(report, Mapping):
        report = {}
    if not isinstance(contract, Mapping):
        contract = RESEARCH_UNIVERSE_CONTRACT

    md = _render_md(report, contract)
    html = _render_html(report, contract)
    return {"md": md, "html": html}


# --------------------------------------------------------------------------- #
# Section-value extraction -- map a report + a section id to the {field_name: value} this section
# renders. The universe report nests data per lane, so a section's values come from its lane record(s).
# PURE + TOTAL.
# --------------------------------------------------------------------------- #
def _section_values(report: Mapping[str, Any], section_id: str) -> Dict[str, Any]:
    """Extract the flat {field_name: value} mapping a section renders, from the nested report. PURE.

    The mapping mirrors the orchestrator's assembly:
      identity/firmographics <- sections['identity'] (the cnpj record) -- alias shares the same data.
      market                 <- sections['market'] (the ibge record).
      reputation             <- sections['reputation'] (the reclame_aqui record) + a complaints_count.
      keywords               <- sections['keywords'] (the seo record).
      questions              <- sections['questions'] (the question pool).
      social                 <- sections['social'] sub-records, FLATTENED to the declared prefixed
                                field names (reddit_*/youtube_*) + the appstore fields.
      sentiment_summary      <- sections['sentiment_summary'] (the aggregate).
      product                <- handled separately (delegated to the marketplace renderer).
    A section the report does not carry -> {} (renders blank; never fabricated)."""
    sections = report.get("sections")
    sections = sections if isinstance(sections, Mapping) else {}

    if section_id in ("identity", SECTION_FIRMOGRAPHICS):
        rec = sections.get("identity")
        if isinstance(rec, Mapping):
            return _flatten_identity(rec)
        return {}

    if section_id == "market":
        rec = sections.get("market")
        return dict(rec) if isinstance(rec, Mapping) else {}

    if section_id == "reputation":
        rec = sections.get("reputation")
        if isinstance(rec, Mapping):
            out = dict(rec)
            out.setdefault("complaints_count", _safe_len(rec.get("complaints")))
            return out
        return {}

    if section_id == "keywords":
        rec = sections.get("keywords")
        return dict(rec) if isinstance(rec, Mapping) else {}

    if section_id == "questions":
        rec = sections.get("questions")
        return dict(rec) if isinstance(rec, Mapping) else {}

    if section_id == SECTION_SENTIMENT:
        rec = sections.get(SECTION_SENTIMENT)
        return dict(rec) if isinstance(rec, Mapping) else {}

    if section_id == "social":
        return _flatten_social(sections.get("social"))

    # An unknown / growth section: read sections[section_id] verbatim if it is a mapping (so a brand-new
    # lane writing a brand-new section renders with zero special-casing -- the GROWTH path).
    rec = sections.get(section_id)
    return dict(rec) if isinstance(rec, Mapping) else {}


def _flatten_identity(rec: Mapping[str, Any]) -> Dict[str, Any]:
    """Flatten the cnpj record to the declared identity field names (some come from a nested
    ``endereco``). PURE + TOTAL."""
    out = dict(rec)
    endereco = rec.get("endereco")
    if isinstance(endereco, Mapping):
        out.setdefault("uf", endereco.get("uf"))
        out.setdefault("municipio", endereco.get("municipio"))
    return out


def _flatten_social(social: Any) -> Dict[str, Any]:
    """Flatten the per-lane social sub-records to the declared prefixed field names. PURE + TOTAL.
    Reddit/YouTube fields are prefixed (reddit_*/youtube_*) so they coexist in one section; appstore
    fields keep their names (the appstore lane owns the un-prefixed app_id/store/rating_avg/...)."""
    out: Dict[str, Any] = {}
    social = social if isinstance(social, Mapping) else {}

    appstore = social.get("appstore")
    if isinstance(appstore, Mapping):
        for key in ("app_id", "store", "rating_avg", "ratings_count", "reviews_count"):
            if key in appstore:
                out[key] = appstore.get(key)

    reddit = social.get("reddit")
    if isinstance(reddit, Mapping):
        out["reddit_query"] = reddit.get("query")
        out["reddit_result_count"] = reddit.get("result_count", _safe_len(reddit.get("results")))

    youtube = social.get("youtube")
    if isinstance(youtube, Mapping):
        out["youtube_query"] = youtube.get("query")
        out["youtube_videos_count"] = youtube.get("videos_count", _safe_len(youtube.get("videos")))
        out["youtube_comments_count"] = youtube.get(
            "comments_count", _safe_len(youtube.get("comments")))
    return out


def _product_subreport(report: Mapping[str, Any]) -> Optional[Mapping[str, Any]]:
    """The marketplace product structured-result carried by the report, if any. Looked up under
    sections['product'] OR a top-level 'product' key (both accepted). PURE + TOTAL -> None when absent."""
    sections = report.get("sections")
    if isinstance(sections, Mapping):
        prod = sections.get(SECTION_PRODUCT)
        if isinstance(prod, Mapping) and prod:
            return prod
    prod = report.get(SECTION_PRODUCT)
    if isinstance(prod, Mapping) and prod:
        return prod
    return None


# --------------------------------------------------------------------------- #
# MD projection (canonical: safe-YAML frontmatter + code-fenced body, ONE walk).
# --------------------------------------------------------------------------- #
def _render_md(report: Mapping[str, Any], contract: Mapping[str, Any]) -> str:
    """The MD projection: yaml.safe_dump frontmatter + a body of code-fenced sections (contract order).
    Reuses the marketplace module's safe-YAML + value coercion (one house serialiser)."""
    frontmatter = _build_frontmatter(report, contract)
    fm_text = _safe_yaml_dump(frontmatter)

    parts: List[str] = ["---", fm_text.rstrip("\n"), "---", ""]
    title = _resolve_title(report, contract)
    parts.append("# %s" % (title or "Research Universe"))
    parts.append("")

    fields_by_section = _group_fields_by_section(contract)
    product_rendered = False
    for section in _sections(contract):
        sid = section.get("id")
        slabel = section.get("label") or sid

        # The product section: embed the marketplace MD verbatim (fenced) -- ONE product projection.
        if sid == SECTION_PRODUCT:
            prod = _product_subreport(report)
            if prod is not None and _MKT_AVAILABLE and _mkt is not None and not product_rendered:
                product_rendered = True
                prod_md = _safe_mkt_render(prod).get("md", "")
                if prod_md.strip():
                    parts.append("## %s" % slabel)
                    parts.append("")
                    parts.append("```markdown")
                    parts.append(prod_md.rstrip("\n"))
                    parts.append("```")
                    parts.append("")
            continue

        section_fields = fields_by_section.get(sid, [])
        if not section_fields:
            continue
        values = _section_values(report, sid)
        # Skip a section that contributed NO value (honest: an un-run lane renders nothing, not a wall
        # of blank keys) -- but ALWAYS render the sentiment summary (it is always computed).
        if not _any_value(values, section_fields) and sid != SECTION_SENTIMENT:
            continue
        parts.append("## %s" % slabel)
        parts.append("")
        parts.append("```")
        for field in section_fields:
            name = field.get("name")
            parts.append("%s: %s" % (name, _scalar_for_fence(values.get(name))))
        parts.append("```")
        parts.append("")
    return "\n".join(parts).rstrip("\n") + "\n"


def _build_frontmatter(report: Mapping[str, Any], contract: Mapping[str, Any]) -> Dict[str, Any]:
    """Assemble the MD frontmatter: schema id/version + the report's provenance (seed, seed_type,
    lanes_run, endpoint_status, data_sources, fetched_at, mock) + the H01/H03 identity guarantee.
    PURE + TOTAL. Never fabricates -- a value the report lacks is omitted/defaulted honestly."""
    fm: Dict[str, Any] = {}
    fm["schema_id"] = str(contract.get("schema_id") or "research_universe")
    fm["schema_version"] = str(contract.get("schema_version") or SCHEMA_VERSION)

    fm["seed"] = _yaml_safe_value(report.get("seed"))
    fm["seed_type"] = _yaml_safe_value(report.get("seed_type"))
    fm["lanes_run"] = _yaml_safe_value(report.get("lanes_run") or [])
    fm["selected_lanes"] = _yaml_safe_value(report.get("selected_lanes") or [])
    fm["endpoint_status"] = _yaml_safe_value(report.get("endpoint_status") or {})
    fm["data_sources"] = _yaml_safe_value(report.get("data_sources") or {})
    fm["fetched_at"] = _yaml_safe_value(report.get("fetched_at"))
    mock = report.get("mock")
    fm["mock"] = bool(mock) if isinstance(mock, bool) else False

    _ensure_artifact_identity(fm, report, contract)
    return fm


def _ensure_artifact_identity(
    fm: Dict[str, Any], report: Mapping[str, Any], contract: Mapping[str, Any],
) -> None:
    """Guarantee the H01/H03 frontmatter identity (id, kind, title, description) IN PLACE -- so the
    rendered universe artifact passes the same universal gates the marketplace render does. PURE +
    TOTAL + idempotent (a producer-supplied value always wins). The fallbacks are honest METADATA
    derived from the seed/schema_id -- never a fabricated research finding."""
    seed = _as_opt_str(report.get("seed")) or ""
    schema_id = str(contract.get("schema_id") or "research_universe")

    if not _is_nonempty_str(fm.get("id")):
        slug = _identity_slug(seed) or _identity_slug(schema_id) or "research-universe"
        fm["id"] = slug

    if not _is_nonempty_str(fm.get("kind")):
        fm["kind"] = "research_universe"

    if not _is_nonempty_str(fm.get("title")):
        fm["title"] = ("Research Universe: %s" % seed) if seed else "Research Universe"

    if len(_as_opt_str(fm.get("description")) or "") < 10:
        what = seed or schema_id.replace("_", " ")
        fm["description"] = "Relatorio de pesquisa-universo CEXAI sobre: %s." % what


# --------------------------------------------------------------------------- #
# HTML projection (derivative: self-contained human report).
# --------------------------------------------------------------------------- #
def _render_html(report: Mapping[str, Any], contract: Mapping[str, Any]) -> str:
    """The HTML projection: a self-contained report (one card per section + a status/provenance table).
    Always derivative of the MD. PURE + TOTAL."""
    title = _resolve_title(report, contract)
    seed_type = _as_opt_str(report.get("seed_type")) or ""

    out: List[str] = []
    out.append("<section class=\"cex-universe\" style=\"font-family:system-ui,Arial,sans-serif;"
               "max-width:920px;margin:0 auto;color:#1a1a1a;\">")
    out.append("<header style=\"border-bottom:2px solid #eee;padding-bottom:8px;\">")
    out.append("<h1 style=\"margin:0;font-size:1.4rem;\">%s</h1>"
               % _html_escape(title or "Research Universe"))
    if seed_type:
        out.append("<span style=\"display:inline-block;background:#334;color:#fff;border-radius:6px;"
                   "padding:2px 10px;margin-left:8px;font-size:.82rem;\">tipo: %s</span>"
                   % _html_escape(seed_type))
    out.append(_sentiment_badge_html(report))
    out.append("</header>")

    fields_by_section = _group_fields_by_section(contract)
    product_rendered = False
    for section in _sections(contract):
        sid = section.get("id")

        if sid == SECTION_PRODUCT:
            prod = _product_subreport(report)
            if prod is not None and _MKT_AVAILABLE and _mkt is not None and not product_rendered:
                product_rendered = True
                prod_html = _safe_mkt_render(prod).get("html", "")
                if prod_html.strip():
                    out.append("<div class=\"cex-section cex-product\" style=\"margin-top:14px;\">")
                    out.append("<h2 style=\"font-size:1.05rem;border-bottom:1px solid #f0f0f0;\">"
                               "%s</h2>" % _html_escape(str(section.get("label") or "Produto")))
                    out.append(prod_html)
                    out.append("</div>")
            continue

        section_fields = fields_by_section.get(sid, [])
        if not section_fields:
            continue
        values = _section_values(report, sid)
        if not _any_value(values, section_fields) and sid != SECTION_SENTIMENT:
            continue
        out.append(_render_html_section(section, section_fields, values))

    out.append(_status_table_html(report))
    out.append("<footer style=\"margin-top:16px;border-top:1px solid #eee;padding-top:8px;"
               "font-size:.8rem;color:#888;\">Gerado por CEXAI -- relatorio-universo derivado do "
               "artefato canonico (MD). %s</footer>" % _mock_note_html(report))
    out.append("</section>")
    return "\n".join(out)


def _render_html_section(
    section: Mapping[str, Any], fields: Sequence[Mapping[str, Any]], values: Mapping[str, Any],
) -> str:
    """Render one HTML section card as a label/value table over its fields. PURE + TOTAL (blank cells on
    missing values; list/object values are compacted to a readable string)."""
    out: List[str] = []
    out.append("<div class=\"cex-section\" style=\"margin-top:14px;\">")
    out.append("<h2 style=\"font-size:1.05rem;border-bottom:1px solid #f0f0f0;\">%s</h2>"
               % _html_escape(str(section.get("label") or section.get("id") or "")))
    out.append("<table style=\"border-collapse:collapse;width:100%;font-size:.92rem;\">")
    for field in fields:
        name = field.get("name")
        value = values.get(name)
        if value in (None, "", [], {}):
            continue  # honest: omit a blank cell rather than show an empty row.
        label = _html_escape(str(field.get("label") or name or ""))
        cell = _html_escape(_scalar_for_html(value))
        out.append("<tr><td style=\"padding:4px 8px;border:1px solid #eee;font-weight:600;"
                   "width:42%%;\">%s</td><td style=\"padding:4px 8px;border:1px solid #eee;\">"
                   "%s</td></tr>" % (label, cell))
    out.append("</table>")
    out.append("</div>")
    return "\n".join(out)


def _status_table_html(report: Mapping[str, Any]) -> str:
    """The per-lane endpoint-status table (honest provenance: ok|blocked|skipped|failed). PURE + TOTAL."""
    status = report.get("endpoint_status")
    if not isinstance(status, Mapping) or not status:
        return ""
    out: List[str] = []
    out.append("<div class=\"cex-status\" style=\"margin-top:14px;\">")
    out.append("<h2 style=\"font-size:1.05rem;border-bottom:1px solid #f0f0f0;\">Status das Fontes</h2>")
    out.append("<table style=\"border-collapse:collapse;width:100%;font-size:.88rem;\">")
    for lane in sorted(str(k) for k in status.keys()):
        token = str(status.get(lane))
        color = _status_color(token)
        out.append("<tr><td style=\"padding:3px 8px;border:1px solid #eee;font-weight:600;\">%s</td>"
                   "<td style=\"padding:3px 8px;border:1px solid #eee;color:%s;\">%s</td></tr>"
                   % (_html_escape(lane), color, _html_escape(token)))
    out.append("</table>")
    out.append("</div>")
    return "\n".join(out)


def _status_color(token: str) -> str:
    """A color for an endpoint-status token (green ok, amber blocked/skipped, red failed). PURE."""
    t = token.strip().lower()
    if t.startswith("ok"):
        return "#2e7d32"
    if t.startswith("blocked") or t.startswith("skipped"):
        return "#b8860b"
    if t.startswith("failed") or t.startswith("rejected") or t.startswith("invalid"):
        return "#c62828"
    return "#555"


def _sentiment_badge_html(report: Mapping[str, Any]) -> str:
    """A sentiment badge from sections['sentiment_summary'] (green POS, grey NEU, red NEG). PURE + TOTAL."""
    sections = report.get("sections")
    summary = sections.get(SECTION_SENTIMENT) if isinstance(sections, Mapping) else None
    if not isinstance(summary, Mapping):
        return ""
    label = str(summary.get("label") or "NEU").upper()
    analyzed = summary.get("analyzed")
    n = int(analyzed) if isinstance(analyzed, (int, float)) else 0
    if n <= 0:
        return ""  # no text analyzed -> no badge (honest; never a fabricated polarity).
    color = {"POS": "#2e7d32", "NEG": "#c62828"}.get(label, "#666")
    return ("<span style=\"display:inline-block;background:%s;color:#fff;border-radius:6px;"
            "padding:2px 10px;margin-left:8px;font-size:.82rem;\">sentimento: %s (%d)</span>"
            % (color, _html_escape(label), n))


def _mock_note_html(report: Mapping[str, Any]) -> str:
    """Surface the mock flag honestly (the orchestrator is always mock=False). PURE + TOTAL."""
    mock = report.get("mock")
    if isinstance(mock, bool) and mock:
        return "<strong style=\"color:#c62828;\">DADOS SIMULADOS (mock=true).</strong>"
    return "Dados reais (mock=false)."


# --------------------------------------------------------------------------- #
# Marketplace-renderer bridge (delegate the product sub-report; degrade-never). PURE.
# --------------------------------------------------------------------------- #
def _safe_mkt_render(prod: Mapping[str, Any]) -> Dict[str, str]:
    """Render a product structured-result via the marketplace renderer (its own contract). TOTAL: if the
    marketplace module is absent or raises, return an empty pair (the universe still renders). PURE."""
    if not _MKT_AVAILABLE or _mkt is None:
        return {"md": "", "html": ""}
    try:
        contract = getattr(_mkt, "PESQUISA_PRODUTO_CONTRACT", {})
        result = _mkt.render(prod, contract)
        if isinstance(result, Mapping):
            return {"md": str(result.get("md") or ""), "html": str(result.get("html") or "")}
    except Exception:
        return {"md": "", "html": ""}
    return {"md": "", "html": ""}


# --------------------------------------------------------------------------- #
# Contract accessors (TOTAL -- always return a usable shape). Mirror the marketplace module.
# --------------------------------------------------------------------------- #
def _fields(contract: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    fields = contract.get("fields")
    if isinstance(fields, (list, tuple)):
        return [f for f in fields if isinstance(f, Mapping) and f.get("name")]
    return []


def _sections(contract: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    sections = contract.get("sections")
    if isinstance(sections, (list, tuple)) and sections:
        return [s for s in sections if isinstance(s, Mapping) and s.get("id")]
    return [{"id": None, "label": "Fields"}]


def _group_fields_by_section(contract: Mapping[str, Any]) -> Dict[Any, List[Mapping[str, Any]]]:
    grouped: Dict[Any, List[Mapping[str, Any]]] = {}
    for field in _fields(contract):
        grouped.setdefault(field.get("section"), []).append(field)
    return grouped


def _resolve_title(report: Mapping[str, Any], contract: Mapping[str, Any]) -> str:
    name = contract.get("title_field")
    if isinstance(name, str):
        v = report.get(name)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def _any_value(values: Mapping[str, Any], fields: Sequence[Mapping[str, Any]]) -> bool:
    """True iff at least one declared field of the section has a non-empty value (used to skip an
    un-run section in the projections). PURE + TOTAL."""
    for field in fields:
        v = values.get(field.get("name"))
        if v not in (None, "", [], {}):
            return True
    return False


def _safe_len(value: Any) -> int:
    """len() of a list/tuple, else 0. PURE + TOTAL."""
    if isinstance(value, (list, tuple)):
        return len(value)
    return 0


# --------------------------------------------------------------------------- #
# Value coercion + serialiser helpers -- DELEGATE to the marketplace module when present (one house
# style), with local TOTAL fallbacks so this module is self-contained + degrade-never.
# --------------------------------------------------------------------------- #
def _as_opt_str(value: Any) -> Optional[str]:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _is_nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _identity_slug(text: Any) -> str:
    """ASCII-only lowercase hyphenated slug (for the artifact id). Delegates to the marketplace helper
    when available; else a local equivalent. PURE + TOTAL."""
    if _MKT_AVAILABLE and _mkt is not None and hasattr(_mkt, "_identity_slug"):
        try:
            return _mkt._identity_slug(text)  # type: ignore[attr-defined]
        except Exception:
            pass
    import re as _re

    s = str(text or "").encode("ascii", "ignore").decode("ascii").lower().strip()
    return _re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def _yaml_safe_value(value: Any) -> Any:
    if _MKT_AVAILABLE and _mkt is not None and hasattr(_mkt, "_yaml_safe_value"):
        try:
            return _mkt._yaml_safe_value(value)  # type: ignore[attr-defined]
        except Exception:
            pass
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple)):
        return [_yaml_safe_value(v) for v in value]
    if isinstance(value, Mapping):
        return {str(k): _yaml_safe_value(v) for k, v in value.items()}
    return str(value)


def _safe_yaml_dump(data: Mapping[str, Any]) -> str:
    if _MKT_AVAILABLE and _mkt is not None and hasattr(_mkt, "_safe_yaml_dump"):
        try:
            return _mkt._safe_yaml_dump(data)  # type: ignore[attr-defined]
        except Exception:
            pass
    try:
        import yaml
        return yaml.safe_dump(
            dict(data), default_flow_style=False, allow_unicode=False, sort_keys=True, width=4096)
    except Exception:
        lines = ["%s: %s" % (k, data[k]) for k in sorted(str(x) for x in data.keys())]
        return "\n".join(lines) + "\n"


def _scalar_for_fence(value: Any) -> str:
    if _MKT_AVAILABLE and _mkt is not None and hasattr(_mkt, "_scalar_for_fence"):
        try:
            return _mkt._scalar_for_fence(value)  # type: ignore[attr-defined]
        except Exception:
            pass
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
    if _MKT_AVAILABLE and _mkt is not None and hasattr(_mkt, "_scalar_for_html"):
        try:
            return _mkt._scalar_for_html(value)  # type: ignore[attr-defined]
        except Exception:
            pass
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


__all__ = [
    "RESEARCH_UNIVERSE_CONTRACT",
    "RESEARCH_UNIVERSE_INPUT_SCHEMA",
    "LANE_REGISTRY",
    "SCHEMA_VERSION",
    "build_contract",
    "validate_input",
    "render_universe",
    "registry_lanes",
    "lanes_for_seed_type",
    "lane_section",
    "lane_subkey",
]

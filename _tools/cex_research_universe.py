#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI research-universe ORCHESTRATOR -- cex_research_universe (one call -> the full report).

THE stitcher. CEXAI ships 10 standalone research lanes (B2B firmographics, market-sizing,
app-store reputation, Reddit listening, YouTube, Reclame Aqui reputation, PT sentiment, SEO
keywords, influencer ranking, multi-perspective question planning). Each is already a TOTAL,
degrade-never function on disk. This module is the PURE COMPOSITION over them: from ONE ``seed``
it infers a seed TYPE, selects the relevant lanes, fans out (each call wrapped so one lane
failing/blocked degrades ONLY its own section), enriches the collected social/review text with
PT sentiment, and assembles ONE unified ``research_universe_report`` dict.

NO new network code, NO new secret, NO new key. The lanes OWN the network/credentials/redaction;
this orchestrator only routes + assembles. It NEVER raises (a lane raising -> that section is
honest-null/blocked, the others proceed) and it NEVER fabricates (a blocked lane shows up honestly
as ``blocked`` in ``endpoint_status``, never invented).

SEED ROUTING (inferred from the seed shape; a ``kinds=[...]`` override forces specific lanes):

  | seed shape                         | seed_type   | lanes selected                                       |
  |------------------------------------|-------------|------------------------------------------------------|
  | 14 digits (after stripping punct)  | cnpj        | cnpj + ibge                                          |
  | ``store:id`` (apple|googleplay:..) | app         | appstore (+ sentiment over review text)              |
  | a short keyword (1-2 tokens)       | keyword     | seo + youtube + reddit (+ sentiment over text)       |
  | free-text brand/product (default)  | brand       | appstore? + reddit + youtube + reclame_aqui + seo    |
  |                                    |             |   + questions (+ sentiment over collected text)      |
  | a company NAME (multi-word, looks  | company     | cnpj? (only if a CNPJ is ALSO present) -> else uses  |
  |   like an org, no product cues)    |             |   the brand routing + reclame_aqui search-first      |

  Notes on the routing decisions:
    * ``app`` requires the explicit ``store:id`` form -- an app-id is never GUESSED from free text.
    * ``cnpj`` is the only purely-numeric seed; it routes to the two GREEN gov sources (firmographics
      + market-sizing) and does NOT trigger the social lanes (a bare CNPJ has no product query).
    * ``keyword`` is the lighter sibling of ``brand``: a 1-2 token seed is treated as a search keyword
      (seo + youtube + reddit) WITHOUT the reputation lane (a keyword is not a company).
    * ``brand`` (the default for a free-text multi-word product/brand) runs the full social+reputation
      fan-out; ``reclame_aqui`` is fed the seed as a company id/slug (it self-validates + honest-blocks).
    * ``company`` (a multi-word seed that reads like an organisation, not a product) is routed exactly
      like ``brand`` for the social lanes BUT additionally resolves the name via Reclame Aqui's
      ``search_company`` first. A 14-digit CNPJ embedded anywhere ALWAYS wins -> ``cnpj`` routing.

  The ``kinds`` override: pass any subset of LANE NAMES (see ``LANES``) to force EXACTLY those lanes
  regardless of the inferred type (e.g. ``kinds=['seo','reddit']``). Unknown names are ignored
  (honest -- never fabricated into a lane); an empty/garbage override falls back to inference.

FAN-OUT + DEGRADE-NEVER: each selected lane is invoked inside ``_run_lane`` which catches ANY
exception the lane (or its import) raises and records that section as honest-null with
``endpoint_status[lane]='failed: <type>'`` -- the other lanes proceed. A lane that itself returns a
``blocked`` posture (the keyless/Cloudflare lanes) is surfaced VERBATIM as ``blocked``. Lanes are
imported LAZILY (inside ``_run_lane``) so a broken/absent lane module degrades that one section only
and never breaks orchestrator import.

SENTIMENT ENRICHMENT: after the social/reputation lanes run, the orchestrator collects their text
(reddit selftext + appstore review text + youtube comment text + reclame_aqui complaint titles),
runs ``cex_sentiment_pt`` over it (the LOCAL, zero-network, always-available lexicon tier at worst),
fills each collected item's ``sentiment`` hook, and rolls a top-level ``sentiment_summary`` aggregate.
This is a TRANSFORM over already-collected text -- it makes no network call and fabricates nothing.

THE unified report shape (``research_universe_report``):
  seed, seed_type, lanes_run (list), sections {identity, firmographics, market, reputation, social,
  keywords, questions, sentiment_summary}, endpoint_status {lane: ok|blocked|skipped|failed:..},
  data_sources (roll-up of every lane's data_sources), fetched_at (the optional ``now`` echo),
  mock (ALWAYS False -- a blocked lane is honest-blocked, never a simulated value).

INVARIANTS: degrade-never (the orchestrator NEVER raises); never-fabricate (a blocked lane is
honest-blocked, never invented); secrets-never-logged (the lanes already redact; this orchestrator
adds no secret + logs none); ASCII-only (.claude/rules/ascii-code-rule.md); bounded (the collected
text + per-section item lists are capped); PURE composition (NO new network/key code).

INTERFACE:
  CLI:        python _tools/cex_research_universe.py "<seed>" [--kinds a,b,c]  -> unified JSON, exit 0
  importable: research_universe(seed, kinds=None, now=None) -> dict

ASCII-only. Fully type-hinted. Composes; modifies nothing.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

# Make the _tools dir importable so the lanes resolve when this file is run as a script OR imported
# from the repo root (mirrors the house seam-import posture used by the marketplace/social lanes).
_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)


# --------------------------------------------------------------------------- #
# The canonical lane names (the ``kinds`` override vocabulary + the section keys).
# --------------------------------------------------------------------------- #
LANE_CNPJ = "cnpj"
LANE_IBGE = "ibge"
LANE_APPSTORE = "appstore"
LANE_REDDIT = "reddit"
LANE_YOUTUBE = "youtube"
LANE_RECLAME_AQUI = "reclame_aqui"
LANE_SEO = "seo"
LANE_QUESTIONS = "questions"

# The full set of routable lanes (the override vocabulary). ``sentiment`` is NOT a routable lane --
# it is an automatic ENRICHMENT over whatever social/reputation text the routed lanes collected.
LANES: Tuple[str, ...] = (
    LANE_CNPJ, LANE_IBGE, LANE_APPSTORE, LANE_REDDIT, LANE_YOUTUBE,
    LANE_RECLAME_AQUI, LANE_SEO, LANE_QUESTIONS,
)

# The formal contract module (cex_research_universe_contract) DECLARES the output schema, the input
# schema, the LANE_REGISTRY (the growth mechanism), and the dual MD/HTML renderer. Routing (select_lanes)
# and the entry's input-validation + render exposure are DRIVEN BY it so adding a lane is a registry
# edit (DATA), not a code branch here. Imported lazily-safe: if the contract module is ever absent the
# orchestrator falls back to its own hardcoded routing table (degrade-never -- a missing contract never
# breaks orchestration, it only forgoes the schema/render layer).
try:
    import cex_research_universe_contract as _contract  # the formal schema + registry + renderer.
    _CONTRACT_AVAILABLE = True
except Exception:  # pragma: no cover - import shape is environment-trivial.
    _contract = None  # type: ignore[assignment]
    _CONTRACT_AVAILABLE = False

# Bounds (the "bounded" invariant): cap the text we hand the sentiment engine + per-item lists so a
# pathological lane payload can never balloon the report. The sentiment engine is itself bounded too.
_MAX_SENTIMENT_ITEMS = 300       # cap on the social/review items we attach a sentiment hook to.
_MAX_TEXT_CHARS = 4000           # per-item text cap before sentiment (the engine also truncates).

# A short, deterministic multi-perspective question count (the question planner is deterministic).
_QUESTIONS_PER_PERSPECTIVE = 3


# --------------------------------------------------------------------------- #
# Seed-type inference (PURE + TOTAL -- never raises, never fabricates a type).
# --------------------------------------------------------------------------- #
def _digits_only(value: str) -> str:
    """The digit characters of ``value`` (PURE). Used to detect a CNPJ regardless of punctuation."""
    return "".join(ch for ch in value if ch.isdigit())


def _looks_like_cnpj(seed: str) -> bool:
    """True iff ``seed`` is EXACTLY a 14-digit CNPJ once punctuation (. / -) and spaces are stripped
    AND the seed contains no letters (a 14-digit run inside a product name is NOT a CNPJ seed). The
    authoritative validation still lives in cex_cnpj_enrich.normalize_cnpj -- this is only the router
    heuristic. PURE + TOTAL."""
    if any(ch.isalpha() for ch in seed):
        return False
    return len(_digits_only(seed)) == 14


def _parse_store_id(seed: str) -> Optional[Tuple[str, str]]:
    """If ``seed`` is the ``store:id`` form (e.g. ``apple:6447526069`` / ``googleplay:com.x.y``),
    return ``(store, app_id)``; else None. The store half must be a known app-store token (so a bare
    ``foo:bar`` is NOT mistaken for an app); the id half is passed THROUGH to the appstore lane which
    does the authoritative anti-injection validation. PURE + TOTAL."""
    if ":" not in seed:
        return None
    head, _, tail = seed.partition(":")
    store = head.strip().lower()
    app_id = tail.strip()
    if not app_id:
        return None
    # Known app-store tokens (mirrors cex_appstore_reviews._STORE_ALIASES, kept local to avoid an
    # import at routing time). A non-store prefix -> not an app seed (falls through to other types).
    store_tokens = {
        "apple", "ios", "appstore", "app_store", "itunes",
        "googleplay", "google", "play", "android", "google_play",
    }
    if store not in store_tokens:
        return None
    return (store, app_id)


def _word_count(seed: str) -> int:
    """The whitespace-delimited token count of ``seed`` (PURE)."""
    return len([t for t in seed.strip().split() if t])


# Company-ish tokens: when a multi-word seed carries one of these it reads like an ORGANISATION (a
# legal/brand entity) rather than a product, so it routes as ``company`` (adds the RA name-search).
# Lower-cased, accent-free matched. A conservative list -- the default for ambiguous multi-word
# seeds is ``brand`` (which already runs the reputation lane), so a miss here is harmless.
_COMPANY_HINTS = frozenset({
    "ltda", "sa", "s.a", "me", "epp", "eireli", "inc", "corp", "llc", "gmbh",
    "company", "companhia", "empresa", "industria", "comercio", "loja", "lojas",
    "magazine", "banco", "seguros", "telecom", "operadora",
})


def infer_seed_type(seed: Any) -> str:
    """Infer the seed TYPE -> one of {cnpj, app, keyword, company, brand}. PURE + TOTAL: a non-string
    / empty seed -> 'brand' (the safe default that runs the broad social fan-out on the raw text).
    NEVER raises; NEVER fabricates -- the type only SELECTS lanes, it never invents data.

    Priority (most specific first):
      1. a 14-digit CNPJ (no letters)            -> 'cnpj'
      2. the explicit ``store:id`` app form       -> 'app'
      3. a multi-word seed with a company hint     -> 'company'
      4. a 1-2 token seed (a search keyword)       -> 'keyword'
      5. anything else (a multi-word product/brand)-> 'brand'
    """
    if not isinstance(seed, str):
        return "brand"
    s = seed.strip()
    if not s:
        return "brand"
    if _looks_like_cnpj(s):
        return "cnpj"
    if _parse_store_id(s) is not None:
        return "app"
    words = [w for w in s.split() if w]
    lowered = {_fold_ascii(w) for w in words}
    if len(words) >= 2 and (lowered & _COMPANY_HINTS):
        return "company"
    if _word_count(s) <= 2:
        return "keyword"
    return "brand"


def _fold_ascii(token: str) -> str:
    """Lower-case + drop the common PT-BR accents off a single token (ASCII-only matching for the
    company-hint test). Uses \\uXXXX escapes so the SOURCE stays ASCII per the ascii-code rule. A
    non-string -> ''. PURE + TOTAL."""
    if not isinstance(token, str):
        return ""
    s = token.strip().lower().strip(".,;:!?")
    # The accent keys are \uXXXX escapes so the SOURCE stays ASCII (.claude/rules/ascii-code-rule.md
    # -- functional i18n strings use escapes, NOT literal chars); Python decodes them at runtime.
    accents = {
        "\u00e1": "a", "\u00e0": "a", "\u00e2": "a", "\u00e3": "a", "\u00e4": "a",
        "\u00e9": "e", "\u00e8": "e", "\u00ea": "e", "\u00eb": "e",
        "\u00ed": "i", "\u00ec": "i", "\u00ee": "i", "\u00ef": "i",
        "\u00f3": "o", "\u00f2": "o", "\u00f4": "o", "\u00f5": "o", "\u00f6": "o",
        "\u00fa": "u", "\u00f9": "u", "\u00fb": "u", "\u00fc": "u",
        "\u00e7": "c",
    }
    return "".join(accents.get(ch, ch) for ch in s)


# --------------------------------------------------------------------------- #
# Lane selection (which lanes a seed_type triggers). PURE + TOTAL.
# --------------------------------------------------------------------------- #
def select_lanes(seed_type: str) -> List[str]:
    """Map a seed_type to its ordered lane list. PURE + TOTAL: an unknown type -> the 'brand' fan-out
    (the safe broad default). NEVER fabricates a lane outside ``LANES``.

    GROWTH: the routing is DRIVEN BY the contract's LANE_REGISTRY (cex_research_universe_contract) --
    a new lane plugs in by adding a registry entry (DATA), NOT a branch here. The registry reproduces
    this table EXACTLY (verified per seed_type); ``_select_lanes_fallback`` below is the byte-identical
    hardcoded table kept ONLY as the degrade-never floor for when the contract module is unavailable."""
    if _CONTRACT_AVAILABLE and _contract is not None:
        try:
            return _contract.lanes_for_seed_type(seed_type)
        except Exception:
            pass  # degrade-never: fall through to the local hardcoded table below.
    return _select_lanes_fallback(seed_type)


def _select_lanes_fallback(seed_type: str) -> List[str]:
    """The hardcoded routing table -- the degrade-never floor used ONLY when the contract registry is
    unavailable. Kept byte-identical to the historical routing so behavior is preserved. PURE + TOTAL."""
    if seed_type == "cnpj":
        return [LANE_CNPJ, LANE_IBGE]
    if seed_type == "app":
        return [LANE_APPSTORE]
    if seed_type == "keyword":
        return [LANE_SEO, LANE_YOUTUBE, LANE_REDDIT]
    # 'brand' and 'company' both run the broad social + reputation fan-out. 'company' additionally
    # resolves the name via Reclame Aqui's search-first inside the reclame_aqui lane runner.
    if seed_type in ("brand", "company"):
        return [
            LANE_APPSTORE, LANE_REDDIT, LANE_YOUTUBE, LANE_RECLAME_AQUI,
            LANE_SEO, LANE_QUESTIONS,
        ]
    return [LANE_APPSTORE, LANE_REDDIT, LANE_YOUTUBE, LANE_RECLAME_AQUI, LANE_SEO, LANE_QUESTIONS]


def _resolve_kinds_override(kinds: Any) -> Optional[List[str]]:
    """If ``kinds`` names a non-empty subset of ``LANES``, return that ordered, de-duplicated subset
    (forcing EXACTLY those lanes). Unknown names are dropped (honest -- never fabricated into a lane).
    A None / empty / all-garbage override -> None (the caller then uses inference). PURE + TOTAL."""
    if kinds is None:
        return None
    if isinstance(kinds, str):
        items: Sequence[Any] = [p for p in kinds.replace(",", " ").split()]
    elif isinstance(kinds, (list, tuple)):
        items = kinds
    else:
        return None
    seen: set = set()
    out: List[str] = []
    for item in items:
        name = item.strip().lower() if isinstance(item, str) else ""
        if name in LANES and name not in seen:
            seen.add(name)
            out.append(name)
    return out or None


# --------------------------------------------------------------------------- #
# The per-lane safe runner -- the degrade-never wrapper around EVERY lane call.
# --------------------------------------------------------------------------- #
def _run_lane(
    report: Dict[str, Any], lane: str, call: Callable[[], Any],
) -> Optional[Any]:
    """Invoke ONE lane (a zero-arg thunk) and record its status. DEGRADE-NEVER: ANY exception the
    lane (or its lazy import) raises is caught -> ``endpoint_status[lane]='failed: <type>'`` and None
    is returned; the OTHER lanes proceed. A lane that returns normally has its own ``endpoint_status``
    / ``data_sources`` rolled up by the caller. NEVER fabricates; NEVER re-raises.

    The lane's OWN posture is preserved: a lane that returns a dict whose internal status is 'blocked'
    is surfaced as 'blocked' by the section assembler -- this wrapper only catches HARD failures
    (an import error / an unexpected raise), which the lanes are built never to produce, so this is
    the belt-and-suspenders floor that makes the ORCHESTRATOR total even if a lane regresses."""
    if lane not in report["lanes_run"]:
        report["lanes_run"].append(lane)
    try:
        return call()
    except Exception as exc:  # belt-and-suspenders: a lane/import surprise degrades ONLY this section.
        report["endpoint_status"][lane] = "failed: %s" % type(exc).__name__
        return None


def _rollup_status(report: Dict[str, Any], lane: str, lane_result: Any) -> None:
    """Roll a lane result's internal ``endpoint_status`` + ``data_sources`` up to the report level.

    A lane returns its own per-endpoint status map; we COLLAPSE it to one honest top-level token for
    the lane: 'ok' if any endpoint is ok, else 'blocked' if any is blocked, else 'failed'/'skipped'.
    The lane's data_sources (a dict OR a list, depending on the lane) are merged into the report's
    data_sources roll-up. PURE-ish (mutates the report) + TOTAL -- a non-mapping result is left as a
    pre-recorded failure (set by _run_lane) and not overwritten with a false success."""
    if not isinstance(lane_result, Mapping):
        # _run_lane already recorded 'failed: ...' for a hard failure; for a None-by-design lane we
        # leave whatever status exists (don't fabricate an 'ok').
        report["endpoint_status"].setdefault(lane, "failed: no_result")
        return

    statuses = lane_result.get("endpoint_status")
    report["endpoint_status"][lane] = _collapse_status(statuses)

    # Merge the lane's data_sources (dict OR list) into the report roll-up under the lane key.
    sources = lane_result.get("data_sources")
    merged = _normalize_sources(sources)
    if merged:
        report["data_sources"][lane] = merged


def _collapse_status(statuses: Any) -> str:
    """Collapse a lane's per-endpoint status map (or string) into ONE honest top-level token. PURE.

    Precedence: any 'ok' -> 'ok'; else any 'blocked' -> 'blocked'; else any 'rejected'/'invalid' ->
    that; else any 'failed' -> 'failed'; else 'skipped'. A bare string status (some lanes use one) is
    classified directly. An empty/absent map -> 'unknown' (honest, never a false 'ok')."""
    tokens: List[str] = []
    if isinstance(statuses, Mapping):
        tokens = [str(v).strip().lower() for v in statuses.values() if v is not None]
    elif isinstance(statuses, str):
        tokens = [statuses.strip().lower()]
    if not tokens:
        return "unknown"
    if any(t == "ok" or t.startswith("ok") or t.startswith("ok:") or t.startswith("ok ") for t in tokens):
        return "ok"
    if any(t.startswith("blocked") for t in tokens):
        return "blocked"
    for marker in ("rejected", "invalid"):
        if any(t.startswith(marker) for t in tokens):
            return marker
    if any(t.startswith("failed") for t in tokens):
        return "failed"
    if any(t.startswith("skipped") for t in tokens):
        return "skipped"
    return "unknown"


def _normalize_sources(sources: Any) -> Any:
    """Normalize a lane's data_sources into a JSON-safe value for the roll-up. A dict stays a dict; a
    list stays a list; anything else -> None (dropped). PURE + TOTAL."""
    if isinstance(sources, Mapping) and sources:
        return {str(k): v for k, v in sources.items()}
    if isinstance(sources, (list, tuple)) and sources:
        return [s for s in sources]
    return None


# --------------------------------------------------------------------------- #
# THE entry -- one seed -> the unified research_universe_report. TOTAL; NEVER fabricates.
# --------------------------------------------------------------------------- #
def research_universe(
    seed: Any,
    kinds: Optional[Sequence[str]] = None,
    now: Optional[str] = None,
) -> Dict[str, Any]:
    """Run the research-universe orchestrator for ONE ``seed`` -> a unified report dict. TOTAL:
    NEVER raises (a lane failing/blocked degrades ONLY its section); NEVER fabricates (a blocked lane
    is honest-blocked, never invented). PURE composition -- no new network/secret code (the lanes own
    the network + the credentials + the redaction).

    Args:
      seed: the research subject. Inferred to a seed_type (cnpj | app | keyword | company | brand)
        which SELECTS the lanes (see the module docstring routing table). A non-string / empty seed
        is treated as the 'brand' default on its string form (honest -- no fabricated subject).
      kinds: an OPTIONAL override -- a list (or comma string) of LANE NAMES (see ``LANES``) to force
        EXACTLY those lanes regardless of the inferred type. Unknown names are ignored; an
        empty/garbage override falls back to inference.
      now: an OPTIONAL ISO-8601 timestamp echoed verbatim into ``fetched_at`` (and threaded to every
        lane that accepts a ``now`` so the whole report shares one provenance stamp). NEVER invented.

    Returns the ``research_universe_report`` dict:
      seed, seed_type, lanes_run (list of the lanes that ran),
      sections {identity, firmographics, market, reputation, social, keywords, questions,
                sentiment_summary},
      endpoint_status {lane: ok|blocked|skipped|failed:..|rejected|invalid|unknown},
      data_sources (roll-up of each lane's data_sources), fetched_at (the ``now`` echo or None),
      mock (ALWAYS False -- a blocked lane is honest-blocked, NEVER a simulated value).
    """
    # INPUT VALIDATION (the formal input schema -- cex_research_universe_contract). ADDITIVE +
    # BACKWARD-COMPATIBLE: the validator NORMALISES the request (strips the seed, keeps only the VALID
    # subset of ``kinds``, honors an explicit ``seed_type`` override only if it is a KNOWN type) and
    # records honest ``dropped`` notes -- it NEVER fabricates a lane/type and NEVER changes the result
    # for the existing call shapes (a bare seed + a valid kinds list flow through unchanged). When the
    # contract module is unavailable the orchestrator degrades to its own inference + LANES-based
    # override (the historical path), so this layer is purely additive.
    seed_str = seed.strip() if isinstance(seed, str) else ("" if seed is None else str(seed).strip())

    seed_type_override: Optional[str] = None
    validated_kinds: Any = kinds
    validation: Optional[Dict[str, Any]] = None
    if _CONTRACT_AVAILABLE and _contract is not None:
        try:
            validation = _contract.validate_input(
                {"seed": seed_str, "kinds": kinds} if kinds is not None else {"seed": seed_str})
            # The validator only narrows ``kinds`` to the registry-known subset (unknowns dropped
            # honestly); an empty result -> None (inference applies), preserving the historical fallback.
            validated_kinds = validation.get("kinds")
            seed_type_override = validation.get("seed_type")  # None unless a KNOWN explicit override.
        except Exception:
            validation = None
            validated_kinds = kinds  # degrade-never: fall back to the raw kinds + inference.

    seed_type = seed_type_override or infer_seed_type(seed_str)

    report: Dict[str, Any] = _empty_report(seed_str, seed_type, now)
    # Honest input-validation provenance (the dropped notes) when the contract validated the request --
    # additive, never alters routing beyond the registry-known-subset narrowing already applied above.
    if isinstance(validation, Mapping):
        report["validation"] = {
            "schema": "research_universe_input",
            "valid": validation.get("valid"),
            "dropped": validation.get("dropped"),
        }

    override = _resolve_kinds_override(validated_kinds)
    selected = override if override is not None else select_lanes(seed_type)
    report["selected_lanes"] = list(selected)

    # Fan-out: run each selected lane through the degrade-never wrapper, assemble its section, and
    # roll its status/sources up. The order is the selection order (deterministic).
    for lane in selected:
        _dispatch_lane(report, lane, seed_str, seed_type, now)

    # Sentiment enrichment: a TRANSFORM over the social/review text the lanes already collected (no
    # network). Fills each item's sentiment hook + the top-level sentiment_summary aggregate.
    _enrich_sentiment(report, now)

    return report


def _dispatch_lane(
    report: Dict[str, Any], lane: str, seed: str, seed_type: str, now: Optional[str],
) -> None:
    """Dispatch ONE lane: build its zero-arg thunk, run it (degrade-never), write its section, and
    roll up its status/sources. PURE-ish (mutates the report). NEVER raises (the thunk runs inside
    _run_lane). A lane with no usable input self-records a 'skipped' status, never a fabricated call."""
    sections = report["sections"]

    if lane == LANE_CNPJ:
        result = _run_lane(report, lane, lambda: _call_cnpj(seed, now))
        sections["identity"] = result
        report["_cnpj_result"] = result  # stashed so the ibge lane can read the company UF (best-effort).
        _rollup_status(report, lane, result)
        return

    if lane == LANE_IBGE:
        result = _run_lane(report, lane, lambda: _call_ibge(report))
        sections["market"] = result
        _rollup_status(report, lane, result)
        return

    if lane == LANE_APPSTORE:
        store_id = _parse_store_id(seed)
        if store_id is None:
            # No explicit store:id -> the appstore lane is honestly SKIPPED (an app id is never
            # guessed from a free-text brand). The brand fan-out still runs every other lane.
            if lane not in report["lanes_run"]:
                report["lanes_run"].append(lane)
            report["endpoint_status"][lane] = "skipped: no store:id in seed (app id never guessed)"
            return
        store, app_id = store_id
        result = _run_lane(report, lane, lambda: _call_appstore(store, app_id, now))
        _store_social(sections, "appstore", result)
        _rollup_status(report, lane, result)
        return

    if lane == LANE_REDDIT:
        result = _run_lane(report, lane, lambda: _call_reddit(seed, now))
        _store_social(sections, "reddit", result)
        _rollup_status(report, lane, result)
        return

    if lane == LANE_YOUTUBE:
        result = _run_lane(report, lane, lambda: _call_youtube(seed, now))
        _store_social(sections, "youtube", result)
        _rollup_status(report, lane, result)
        return

    if lane == LANE_RECLAME_AQUI:
        result = _run_lane(report, lane, lambda: _call_reclame_aqui(seed, seed_type, now))
        sections["reputation"] = result
        _rollup_status(report, lane, result)
        return

    if lane == LANE_SEO:
        result = _run_lane(report, lane, lambda: _call_seo(seed, now))
        sections["keywords"] = result
        _rollup_status(report, lane, result)
        return

    if lane == LANE_QUESTIONS:
        result = _run_lane(report, lane, lambda: _call_questions(seed))
        sections["questions"] = result
        # The question planner is deterministic/local -> mark it ok when it produced a pool.
        report["endpoint_status"][lane] = (
            "ok" if isinstance(result, Mapping) and result.get("count") else "ok (0)"
        )
        srcs = result.get("method") if isinstance(result, Mapping) else None
        if srcs:
            report["data_sources"][lane] = ["multiperspective:%s" % srcs]
        return

    # An unknown lane name should never reach here (the override + selection only emit known lanes),
    # but stay total: record it honestly rather than raise.
    report["endpoint_status"][lane] = "skipped: unknown lane"


def _store_social(sections: Dict[str, Any], key: str, result: Any) -> None:
    """Store ONE social sub-record (reddit/youtube/appstore) under sections['social'][key], but ONLY
    when the lane returned a real Mapping record. A hard-failed lane (result None -- _run_lane caught
    a raise) is NOT written as a None placeholder: its honest 'failed:' status already lives in
    endpoint_status, and the absent sub-key is the honest shape (no fabricated/empty record). PURE-ish
    + TOTAL."""
    if isinstance(result, Mapping):
        sections["social"].setdefault(key, result)


# --------------------------------------------------------------------------- #
# Lane adapters -- each LAZILY imports its lane module + calls the documented entry. NO new network.
# Each is wrapped by _run_lane, so a raise here degrades ONLY that section.
# --------------------------------------------------------------------------- #
def _call_cnpj(seed: str, now: Optional[str]) -> Any:
    """B2B firmographics -- cex_cnpj_enrich.enrich_cnpj. The lane self-validates the CNPJ format."""
    import cex_cnpj_enrich as _cnpj  # lazy import (offline-friendly; failure degrades this section).

    return _cnpj.enrich_cnpj(seed, now=now)


def _call_ibge(report: Dict[str, Any]) -> Any:
    """Market-sizing -- cex_ibge_sidra.query_sidra. Uses the national population preset (the top-line
    TAM denominator); a CNPJ seed has no category, so the country-level denominator is the honest,
    universally-useful market signal. The lane is preset-driven + total."""
    import cex_ibge_sidra as _ibge  # lazy import.

    # The national population estimate is the safe, always-meaningful denominator for a B2B/company
    # seed (we do NOT guess a per-product category). A future caller can override via kinds + a custom
    # driver, but the orchestrator never fabricates a category.
    return _ibge.query_sidra(preset="populacao_brasil")


def _call_appstore(store: str, app_id: str, now: Optional[str]) -> Any:
    """Reputation (mobile app) -- cex_appstore_reviews.fetch_reviews. ``now`` may be a datetime in the
    lane; we pass the string through (the lane accepts a datetime OR falls back to real now on a bad
    value -- it is total), so we pass None when ``now`` is not a datetime to keep the lane's stamp
    honest rather than feed it a string it would ignore."""
    import cex_appstore_reviews as _app  # lazy import.

    return _app.fetch_reviews(store, app_id)


def _call_reddit(seed: str, now: Optional[str]) -> Any:
    """Social-inbound -- cex_reddit_listen.listen_reddit (keyless-first; honest-blocked on throttle)."""
    import cex_reddit_listen as _reddit  # lazy import.

    return _reddit.listen_reddit(seed, now=now)


def _call_youtube(seed: str, now: Optional[str]) -> Any:
    """Social-inbound (video) -- cex_youtube_data.youtube_research (needs a key; honest-blocked sans
    key). ``now`` is echoed into provenance by the lane."""
    import cex_youtube_data as _yt  # lazy import.

    return _yt.youtube_research(query=seed, now=now)


def _call_reclame_aqui(seed: str, seed_type: str, now: Optional[str]) -> Any:
    """Reputation (company) -- cex_reclame_aqui. For a 'company' seed we resolve the NAME via
    ``search_company`` first; for a 'brand'/other seed we treat the seed as a company id/slug and call
    ``fetch_reputation`` (the lane self-validates the id + honest-blocks under Cloudflare). The
    Cloudflare-gated lane is total either way -- it never fabricates a score."""
    import cex_reclame_aqui as _ra  # lazy import.

    # A 'company' seed: resolve the name -> a candidate id/slug, then fetch that candidate's
    # reputation. The search self-blocks under Cloudflare (honest) -> we still return a usable record.
    if seed_type == "company":
        search = _ra.search_company(seed, now=now)
        companies = search.get("companies") if isinstance(search, Mapping) else None
        candidate_id = None
        if isinstance(companies, list) and companies:
            first = companies[0]
            if isinstance(first, Mapping):
                candidate_id = first.get("slug") or first.get("id")
        if isinstance(candidate_id, str) and candidate_id.strip():
            rep = _ra.fetch_reputation(candidate_id, now=now)
            # Thread the search provenance into the reputation record so the report shows BOTH steps.
            if isinstance(rep, Mapping):
                rep = dict(rep)
                rep["search"] = search
            return rep
        # No candidate resolved (blocked / no match) -> return the search record honestly (it carries
        # the blocked/empty status). We do NOT fabricate a reputation.
        return search

    # A 'brand'/other seed: treat the raw seed as a company id/slug; the lane validates + honest-blocks
    # an unusable id (e.g. a multi-word brand fails the ^[A-Za-z0-9_-]{1,80}$ gate -> honest record).
    return _ra.fetch_reputation(seed, now=now)


def _call_seo(seed: str, now: Optional[str]) -> Any:
    """Keyword discovery -- cex_seo_keyword.autocomplete (keyless, YELLOW-tolerant; honest-blocked on
    a Google throttle). Volume stays an honest null in the lane (a paid BUY)."""
    import cex_seo_keyword as _seo  # lazy import.

    return _seo.autocomplete(seed, now=now)


def _call_questions(seed: str) -> Any:
    """Question planning -- cex_storm_upgrades.generate_multiperspective_questions (deterministic,
    PURE, no network). Composes research SUB-QUESTIONS from the diverse default perspective set."""
    import cex_storm_upgrades as _storm  # lazy import.

    return _storm.generate_multiperspective_questions(seed, n_per=_QUESTIONS_PER_PERSPECTIVE)


# --------------------------------------------------------------------------- #
# SENTIMENT ENRICHMENT -- a TRANSFORM over the collected social/review text (NO network).
# --------------------------------------------------------------------------- #
def _enrich_sentiment(report: Dict[str, Any], now: Optional[str]) -> None:
    """Run cex_sentiment_pt over the social/reputation text collected by the lanes -> fill each item's
    ``sentiment`` hook + the top-level ``sentiment_summary``. PURE-ish (mutates the report). TOTAL:
    the sentiment engine is local + degrade-never (lexicon tier at worst), and a missing engine import
    is caught -> the sentiment_summary is an honest empty aggregate, never fabricated.

    Item collection (bounded by _MAX_SENTIMENT_ITEMS): reddit selftext/title, appstore review text,
    youtube comment text, reclame_aqui complaint titles. Each collected item is paired with the LIVING
    dict it came from so its ``sentiment`` field can be filled IN PLACE (the lanes seed it as None)."""
    items = _collect_sentiment_items(report)
    if not items:
        report["sections"]["sentiment_summary"] = _empty_sentiment_summary()
        return

    try:
        import cex_sentiment_pt as _sent  # lazy import (local engine; no network).
    except Exception as exc:
        # Degrade-never: no sentiment engine -> an honest empty aggregate (never a fabricated label).
        summary = _empty_sentiment_summary()
        summary["note"] = "sentiment engine unavailable: %s" % type(exc).__name__
        report["sections"]["sentiment_summary"] = summary
        return

    texts = [it[1] for it in items]
    # use_model=False forces the always-available, zero-dep LEXICON tier -> deterministic + offline
    # (the orchestrator must not pull a heavy ML model implicitly; the model tier stays opt-in to the
    # standalone lane). The engine is total + never-fabricates.
    batch = _sent.analyze_batch(texts, use_model=False, now=now)
    results = batch.get("results") if isinstance(batch, Mapping) else None
    results = results if isinstance(results, list) else []

    # Fill each source item's sentiment hook IN PLACE with its per-text result (label + score + method).
    for (carrier, _text), result in zip(items, results):
        if isinstance(carrier, dict) and isinstance(result, Mapping):
            carrier["sentiment"] = {
                "label": result.get("label"),
                "score": result.get("score"),
                "method": result.get("method"),
            }

    aggregate = batch.get("aggregate") if isinstance(batch, Mapping) else None
    summary = _empty_sentiment_summary()
    if isinstance(aggregate, Mapping):
        summary.update({
            "label": aggregate.get("label"),
            "pos": aggregate.get("pos"),
            "neu": aggregate.get("neu"),
            "neg": aggregate.get("neg"),
        })
    summary["analyzed"] = len(results)
    summary["method"] = _sentiment_method(batch)
    summary["data_sources"] = batch.get("data_sources") if isinstance(batch, Mapping) else None
    summary["mock"] = False
    report["sections"]["sentiment_summary"] = summary
    if LANE_REDDIT in report["lanes_run"] or LANE_APPSTORE in report["lanes_run"]:
        report["data_sources"]["sentiment"] = summary.get("data_sources")


def _collect_sentiment_items(report: Dict[str, Any]) -> List[Tuple[dict, str]]:
    """Collect (carrier_dict, text) pairs from the social/reputation sections, bounded. Each carrier
    is the LIVING dict whose ``sentiment`` hook will be filled in place. PURE-ish (reads the report).
    NEVER fabricates -- only text the lanes actually returned is collected."""
    out: List[Tuple[dict, str]] = []
    social = report["sections"].get("social")
    social = social if isinstance(social, Mapping) else {}

    # Reddit: each result's title + selftext (the carrier is the result dict).
    reddit = social.get("reddit")
    if isinstance(reddit, Mapping):
        for item in (reddit.get("results") or []):
            if not isinstance(item, dict):
                continue
            text = _join_text(item.get("title"), item.get("selftext"))
            if text:
                out.append((item, text))
            if len(out) >= _MAX_SENTIMENT_ITEMS:
                return out

    # Appstore: each review's title + text (the carrier is the review dict).
    appstore = social.get("appstore")
    if isinstance(appstore, Mapping):
        for review in (appstore.get("reviews") or []):
            if not isinstance(review, dict):
                continue
            text = _join_text(review.get("title"), review.get("text"))
            if text:
                out.append((review, text))
            if len(out) >= _MAX_SENTIMENT_ITEMS:
                return out

    # YouTube: each comment's text (the carrier is the comment dict).
    youtube = social.get("youtube")
    if isinstance(youtube, Mapping):
        for comment in (youtube.get("comments") or []):
            if not isinstance(comment, dict):
                continue
            text = _join_text(comment.get("text"))
            if text:
                out.append((comment, text))
            if len(out) >= _MAX_SENTIMENT_ITEMS:
                return out

    # Reclame Aqui: each complaint's title (the carrier is the complaint dict).
    reputation = report["sections"].get("reputation")
    if isinstance(reputation, Mapping):
        for complaint in (reputation.get("complaints") or []):
            if not isinstance(complaint, dict):
                continue
            text = _join_text(complaint.get("title"))
            if text:
                out.append((complaint, text))
            if len(out) >= _MAX_SENTIMENT_ITEMS:
                return out

    return out


def _join_text(*parts: Any) -> str:
    """Join the non-empty string parts into one bounded text (PURE + TOTAL). Used to assemble an
    item's title+body before sentiment. Truncated to _MAX_TEXT_CHARS."""
    chunks = [p.strip() for p in parts if isinstance(p, str) and p.strip()]
    if not chunks:
        return ""
    return " ".join(chunks)[:_MAX_TEXT_CHARS]


def _sentiment_method(batch: Mapping[str, Any]) -> Optional[str]:
    """The sentiment method used (from the first result), for the summary provenance. PURE + TOTAL."""
    results = batch.get("results") if isinstance(batch, Mapping) else None
    if isinstance(results, list) and results and isinstance(results[0], Mapping):
        return results[0].get("method")
    return None


# --------------------------------------------------------------------------- #
# Skeletons (the honest-null report shape). mock is ALWAYS False.
# --------------------------------------------------------------------------- #
def _empty_report(seed: str, seed_type: str, now: Optional[str]) -> Dict[str, Any]:
    """The all-null unified report skeleton (every section present, honest null). mock is ALWAYS
    False -- a blocked lane is honest-blocked, never simulated. ``sections`` carries the 8 declared
    section keys so the shape is STABLE regardless of which lanes ran (an un-run section stays None /
    its empty default)."""
    return {
        "seed": seed,
        "seed_type": seed_type,
        "lanes_run": [],
        "selected_lanes": [],
        "sections": {
            "identity": None,            # cnpj firmographics
            "firmographics": None,       # alias slot (reserved; identity carries the cnpj record)
            "market": None,              # ibge market-sizing
            "reputation": None,          # reclame_aqui
            "social": {},                # appstore / reddit / youtube sub-records
            "keywords": None,            # seo autocomplete
            "questions": None,           # multi-perspective question pool
            "sentiment_summary": None,   # sentiment aggregate (filled by _enrich_sentiment)
        },
        "endpoint_status": {},
        "data_sources": {},
        "fetched_at": now if isinstance(now, str) and now.strip() else None,
        "mock": False,
    }


def _empty_sentiment_summary() -> Dict[str, Any]:
    """The honest empty sentiment aggregate (no text analyzed). mock is ALWAYS False; the label is
    NEU (the honest non-committal call), counts are 0 -- never a fabricated polarity."""
    return {
        "label": "NEU",
        "pos": 0,
        "neu": 0,
        "neg": 0,
        "analyzed": 0,
        "method": None,
        "data_sources": None,
        "mock": False,
    }


def render_universe(
    report: Mapping[str, Any], contract: Optional[Mapping[str, Any]] = None,
) -> Dict[str, str]:
    """Project a research_universe_report into {"md", "html"} via the formal contract renderer
    (cex_research_universe_contract.render_universe). PURE -- no network/IO. Re-exported here so a caller
    can do ``research_universe(seed)`` then ``render_universe(report)`` from ONE module. TOTAL: when the
    contract module is unavailable, returns an honest empty pair (degrade-never)."""
    if _CONTRACT_AVAILABLE and _contract is not None:
        try:
            return _contract.render_universe(report, contract)
        except Exception:
            return {"md": "", "html": ""}
    return {"md": "", "html": ""}


def research_universe_contract() -> Optional[Dict[str, Any]]:
    """The formal output contract dict (RESEARCH_UNIVERSE_CONTRACT) when available, else None. Exposed
    so a caller can introspect the schema (sections + fields) without importing the contract module."""
    if _CONTRACT_AVAILABLE and _contract is not None:
        try:
            return _contract.RESEARCH_UNIVERSE_CONTRACT
        except Exception:
            return None
    return None


__all__ = [
    "research_universe",
    "infer_seed_type",
    "select_lanes",
    "render_universe",
    "research_universe_contract",
    "LANES",
]


# --------------------------------------------------------------------------- #
# CLI -- one seed -> the unified JSON report + exit 0 (degrade-never). The lanes hit the real network
# (each honest-blocks without its credential); the orchestrator adds no secret and prints none.
# --------------------------------------------------------------------------- #
def _stamp_now() -> str:
    """An ISO-8601 UTC provenance stamp for the CLI (the library stays clock-free; only the executable
    touches wall-time). ASCII 'Z' suffix."""
    import datetime as _dt

    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z")


def _parse_kinds_arg(argv: List[str]) -> Optional[str]:
    """Pull a ``--kinds a,b,c`` value out of argv (PURE). Returns the raw comma string or None."""
    for i, tok in enumerate(argv):
        if tok == "--kinds" and i + 1 < len(argv):
            return argv[i + 1]
        if tok.startswith("--kinds="):
            return tok.split("=", 1)[1]
    return None


def _main(argv: List[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print("CEXAI research-universe orchestrator (one call -> the full report). Usage:")
        print('  python _tools/cex_research_universe.py "<seed>" [--kinds a,b,c]')
        print("")
        print("  <seed>   a brand/product, a 14-digit CNPJ, a company name, a keyword, or store:id")
        print("           (e.g. apple:6447526069 / googleplay:com.whatsapp)")
        print("  --kinds  OPTIONAL comma list forcing specific lanes (override the inferred routing).")
        print("           lanes: %s" % ", ".join(LANES))
        print("")
        print("Each lane is degrade-never + honest-blocked without its credential; the orchestrator")
        print("NEVER raises, NEVER fabricates (a blocked lane shows up as 'blocked'), and adds NO")
        print("secret (the lanes own the network/keys/redaction). Prints the unified JSON; exit 0.")
        return 0

    # The seed is every non-flag token before --kinds (so an unquoted multi-word seed still works).
    kinds_raw = _parse_kinds_arg(argv)
    seed_tokens: List[str] = []
    skip_next = False
    for tok in argv:
        if skip_next:
            skip_next = False
            continue
        if tok == "--kinds":
            skip_next = True
            continue
        if tok.startswith("--kinds="):
            continue
        seed_tokens.append(tok)
    seed = " ".join(seed_tokens).strip()

    now = _stamp_now()
    report = research_universe(seed, kinds=kinds_raw, now=now)

    import json
    print(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True))
    # Exit 0 even when every lane honest-blocks -- a blocked lane is a VALID, recorded result, not a
    # tool crash. The per-lane status lives in the report's endpoint_status for the caller to read.
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))

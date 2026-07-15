#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI lead-gen REAL orchestrator -- cex_leadgen_run (spec 05_leadgen_suite, Phase 1b).

THE real path behind the ``leadgen`` capability. Phase 1a shipped the PURE generator
(capability_generators/leadgen.py) as the offline/fixtures scaffold; THIS module wires the
REAL network lanes for a non-fixtures run, mirroring cex_research_universe.py exactly: from
the 7 typed inputs it maps the requested CHANNELS to existing lanes, fans out (each call
wrapped so one lane failing/blocked degrades ONLY its own channel), maps the REAL lane
results to typed LEAD RECORDS (spec sec 5), and returns the SAME StructuredOutput contract as
leadgen.build (mold_id="leadgen", the 5 frozen sections, the 7-col Leads table) so dual-output
+ persist + UI rendering are byte-identical in SHAPE to 1a.

NO new network code, NO new secret, NO new key. The lanes + the marketplace tier-router OWN
the network/credentials/redaction; this orchestrator only routes channels -> lanes, calls
them, and assembles. It reuses leadgen.parse_inputs + leadgen.assemble_output so the frozen
SHAPE is built in ONE place and can never drift between the offline scaffold and the real path.

CHANNEL -> LANE MAPPING (spec D2, verified against the live lane signatures):
  | channel          | lanes                                                              |
  |------------------|--------------------------------------------------------------------|
  | b2c_marketplace  | meli + shopee DETAIL/SEARCH via cex_marketplace_tier_router.resolve |
  |                  |   (the credit-aware tier router -- Firecrawl 402 -> honest-blocked) |
  | b2b_cnpj         | research_universe cnpj (cex_cnpj_enrich) + ibge (cex_ibge_sidra)    |
  | ugc_social       | research_universe reddit (cex_reddit_listen) + youtube             |
  |                  |   (cex_youtube_data); instagram -> SKIPPED (no credential)         |

INVARIANTS (the whole point of 1b -- non-negotiable):
  1. NEVER FABRICATE. A lead/name/contact/CNPJ/source appears ONLY if a lane ACTUALLY
     returned it. A lane that returns a lead with no contact -> Contato is the absent marker
     ('--'), never an invented email/phone/url. No mock/placeholder leads on the real path.
  2. DEGRADE-NEVER. A lane that errors / is blocked / hits no-credit (Firecrawl HTTP 402) /
     has no credential -> that channel is honest blocked|skipped|failed; the OTHER channels
     proceed. ALL channels yielding nothing -> honest-EMPTY (0 leads, gate REVISAR) -- never a
     crash, never fabricated filler. (Firecrawl is likely out of credits -> mostly honest-
     blocked is the CORRECT real-run result today, not a failure.)
  3. HONEST STATUS. Per-source ok|blocked|skipped|failed is truthful (mirrors research_universe
     endpoint_status). Confidence is COMPUTED from real signals, never guessed.
  4. FROZEN SHAPE. The 5 sections in order, the 7 Leads columns, mold_id="leadgen" -- via the
     SHARED leadgen.assemble_output.

ASCII-only (.claude/rules/ascii-code-rule.md). Runtime lead VALUES may carry PT-BR accents
(they are real source data); the module's own constants/keys stay diacritic-free.

INTERFACE:
  importable: leadgen_run(inputs, *, credential=None, now=None) -> StructuredOutput (dict)
  CLI:        python _tools/cex_leadgen_run.py "<objetivo>" --seed "<seed>" [--canais a,b]
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

# Make the _tools dir importable so the lanes + the 1a generator resolve when this file is run
# as a script OR imported from the repo root (the house seam-import posture).
_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

# The 1a generator is the SHAPE source of truth: we reuse its input parser + output assembler +
# the frozen section/column constants + the absent-contact marker + the per-lead row projector,
# so the real path's StructuredOutput is byte-identical IN SHAPE to the offline scaffold.
from capability_generators import leadgen as _gen  # type: ignore[import]

CAPABILITY = "leadgen"
RUN_MODE = "real-lanes"  # the metadata-envelope run_mode for a real (non-fixtures) run.

# The v1 channels (spec D2). Re-exported from the generator so the two never drift.
CHANNEL_B2C = "b2c_marketplace"
CHANNEL_B2B = "b2b_cnpj"
CHANNEL_UGC = "ugc_social"

# Human label per channel (display only -- never a fabricated datum). Mirrors the generator's.
_CHANNEL_LABEL: Dict[str, str] = {
    CHANNEL_B2C: "B2C marketplace",
    CHANNEL_B2B: "B2B CNPJ",
    CHANNEL_UGC: "UGC social",
}

# Bounds (the "bounded" invariant): cap how many candidates per lane become leads so a
# pathological lane payload can never balloon the report. A real run is best-effort, never padded.
_MAX_LEADS_PER_LANE = 25
_MARKETPLACE_LIMIT = 20  # listings the tier-router search pass returns.

# The marketplaces a b2c_marketplace channel resolves (the tier-router keys).
_MARKETPLACES = ("mercadolivre", "shopee")


# --------------------------------------------------------------------------- #
# Lane seams -- each is a module-level injectable so the offline UNIT tests fake them (no real
# network), exactly like cex_run_capability's monkeypatchable globals + research_universe's
# lazy _call_* adapters. When a global is None (default), the real lane is imported lazily.
# --------------------------------------------------------------------------- #
# Tests set cex_leadgen_run.<name> = fake to run offline + deterministic.
marketplace_resolve: Any = None      # cex_marketplace_tier_router.resolve(marketplace, query, ...)
enrich_cnpj: Any = None              # cex_cnpj_enrich.enrich_cnpj(cnpj, now=)
query_sidra: Any = None              # cex_ibge_sidra.query_sidra(preset=, now=)
listen_reddit: Any = None            # cex_reddit_listen.listen_reddit(query, now=)
youtube_research: Any = None         # cex_youtube_data.youtube_research(query=, now=)


def _lane_marketplace_resolve(marketplace: str, query: str) -> Any:
    """The B2C marketplace lane (cex_marketplace_tier_router.resolve -- credit-aware: official
    API -> real browser -> Firecrawl /v1/extract -> manual-paste floor). Lazy import; the
    tier-router is itself TOTAL (never raises, never fabricates; a Firecrawl 402 is an honest
    tier failure)."""
    fn = marketplace_resolve
    if fn is None:
        import cex_marketplace_tier_router as _r  # type: ignore[import]
        fn = _r.resolve
    return fn(marketplace, query, limit=_MARKETPLACE_LIMIT)


def _lane_cnpj(seed: str, now: Optional[str]) -> Any:
    """The B2B firmographics lane (cex_cnpj_enrich.enrich_cnpj). Self-validates the CNPJ format
    (a non-CNPJ seed -> honest invalid record). Lazy import; TOTAL."""
    fn = enrich_cnpj
    if fn is None:
        import cex_cnpj_enrich as _c  # type: ignore[import]
        fn = _c.enrich_cnpj
    return fn(seed, now=now)


def _lane_ibge(now: Optional[str]) -> Any:
    """The market-sizing lane (cex_ibge_sidra.query_sidra, national-population preset). It is
    firmographic CONTEXT for the b2b channel (NOT a lead source -- it never yields a lead). Lazy
    import; TOTAL."""
    fn = query_sidra
    if fn is None:
        import cex_ibge_sidra as _i  # type: ignore[import]
        fn = _i.query_sidra
    return fn(preset="populacao_brasil", now=now)


def _lane_reddit(seed: str, now: Optional[str]) -> Any:
    """The UGC-social lane (cex_reddit_listen.listen_reddit -- keyless-first; honest-blocked on
    throttle). Lazy import; TOTAL."""
    fn = listen_reddit
    if fn is None:
        import cex_reddit_listen as _r  # type: ignore[import]
        fn = _r.listen_reddit
    return fn(seed, now=now)


def _lane_youtube(seed: str, now: Optional[str]) -> Any:
    """The UGC-social (video) lane (cex_youtube_data.youtube_research -- needs a key; honest-
    blocked sans key). Lazy import; TOTAL."""
    fn = youtube_research
    if fn is None:
        import cex_youtube_data as _y  # type: ignore[import]
        fn = _y.youtube_research
    return fn(query=seed, now=now)


# --------------------------------------------------------------------------- #
# Per-lane safe runner -- the degrade-never wrapper around EVERY lane call (mirrors
# research_universe._run_lane). ANY exception the lane (or its lazy import) raises is caught and
# recorded as a HARD failure for that lane; the OTHER lanes proceed. NEVER re-raises.
# --------------------------------------------------------------------------- #
def _run_lane(status: Dict[str, str], lane: str, call: Callable[[], Any]) -> Optional[Any]:
    """Invoke ONE lane (a zero-arg thunk); on a hard exception record status[lane]='failed: T'
    and return None. The lane's OWN honest posture (a returned dict with status 'blocked'/'ok')
    is interpreted by the channel handler. TOTAL."""
    try:
        return call()
    except Exception as exc:  # belt-and-suspenders: a lane/import surprise degrades ONLY this lane.
        status[lane] = "failed: %s" % type(exc).__name__
        return None


# --------------------------------------------------------------------------- #
# Status helpers (honest per-source token). Mirror research_universe._collapse_status.
# --------------------------------------------------------------------------- #
def _collapse_endpoint_status(rec: Any) -> str:
    """Collapse a lane record's per-endpoint ``endpoint_status`` map (or bare string) into ONE
    honest token: any 'ok' -> 'ok'; else any 'blocked' -> 'blocked'; else any 'invalid'/
    'rejected' -> that; else any 'failed' -> 'failed'; else 'skipped'; empty -> 'unknown'. PURE."""
    statuses = rec.get("endpoint_status") if isinstance(rec, Mapping) else None
    tokens: List[str] = []
    if isinstance(statuses, Mapping):
        tokens = [str(v).strip().lower() for v in statuses.values() if v is not None]
    elif isinstance(statuses, str):
        tokens = [statuses.strip().lower()]
    if not tokens:
        # Some lanes carry a top-level 'status' instead of an endpoint_status map.
        top = rec.get("status") if isinstance(rec, Mapping) else None
        if isinstance(top, str) and top.strip():
            tokens = [top.strip().lower()]
    if not tokens:
        return "unknown"
    if any(t == "ok" or t.startswith("ok") for t in tokens):
        return "ok"
    if any(t.startswith("blocked") for t in tokens):
        return "blocked"
    for marker in ("rejected", "invalid", "unavailable"):
        if any(t.startswith(marker) for t in tokens):
            return "blocked" if marker == "unavailable" else marker
    if any(t.startswith("failed") for t in tokens):
        return "failed"
    if any(t.startswith("skipped") for t in tokens):
        return "skipped"
    return "unknown"


def _s(value: Any) -> str:
    """A clean stripped string, or '' (TOTAL)."""
    return value.strip() if isinstance(value, str) and value.strip() else ""


def _truncate(text: str, n: int) -> str:
    """Truncate to n chars (the bounded invariant). PURE."""
    return text[:n] if len(text) > n else text


# --------------------------------------------------------------------------- #
# Confidence (spec sec 5 -- S3 formula: source count + agreement + freshness). COMPUTED from
# REAL signals on a lead, never guessed. PURE + TOTAL. Bounded to [0, 1].
# --------------------------------------------------------------------------- #
def _lead_confidence(n_signals: int, has_contact: bool, has_identifier: bool) -> float:
    """A conservative, honest confidence for ONE lead from the REAL evidence it carries:
      * a base from how many corroborating signals/fields the lane returned (source_count);
      * a small bump when a usable contact/identifier was ACTUALLY found (agreement that the
        lead is reachable/real).
    NEVER inflated -- a lead with one signal + no contact stays low. Bounded [0, 1]."""
    base = 0.45 + 0.12 * max(0, min(3, n_signals))   # 1 signal -> 0.57; 3+ -> 0.81
    if has_identifier:
        base += 0.05
    if has_contact:
        base += 0.08
    return round(max(0.0, min(1.0, base)), 2)


# --------------------------------------------------------------------------- #
# B2C marketplace channel -- meli + shopee via the credit-aware tier router. A marketplace
# SELLER (the listing's seller) is a B2C lead (tipo=empresa); the listing is the intent signal
# (a competitor anchored to the seed). NEVER fabricates: a lead exists only if the tier router
# actually returned a listing with a seller; the contact is the listing/seller URL a real lane
# returned, never an invented email.
# --------------------------------------------------------------------------- #
def _channel_b2c(
    seed: str, region: str, status: Dict[str, str], leads: List[Dict[str, Any]],
    sources: List[str], prov: List[Dict[str, Any]],
) -> None:
    """Resolve the B2C marketplace channel. Mutates status/leads/sources/prov in place. TOTAL."""
    any_ok = False
    any_blocked = False
    for mp in _MARKETPLACES:
        lane = "marketplace_%s" % mp
        result = _run_lane(status, lane, lambda mp=mp: _lane_marketplace_resolve(mp, seed))
        if lane in status and status[lane].startswith("failed"):
            continue  # hard failure already recorded by _run_lane.
        if not isinstance(result, Mapping):
            status[lane] = "failed: no_result"
            continue
        winning_tier = _s(result.get("winning_tier"))
        listings = _marketplace_listings(result)
        # A manual-paste / no-listing win is NOT lead data -> honest blocked (NEVER fabricated).
        if winning_tier in ("", "manual_paste") or not listings:
            any_blocked = True
            status[lane] = _marketplace_blocked_status(result, winning_tier)
            continue
        any_ok = True
        status[lane] = "ok (tier=%s, %d listings)" % (winning_tier, len(listings))
        src_label = "%s.com.br [%s]" % (mp, winning_tier)
        if src_label not in sources:
            sources.append(src_label)
        n_added = 0
        for listing in listings:
            if n_added >= _MAX_LEADS_PER_LANE:
                break
            lead = _listing_to_lead(listing, mp, region, seed)
            if lead is not None:
                leads.append(lead)
                prov.append(_gen.make_provenance(
                    finding="Leads::%s" % _truncate(str(lead.get("nome") or ""), 50),
                    source_url=lead.get("_source_url"),
                    fetched_at=None,
                    method="scrape",
                    confidence=float(lead.get("score") or 0.0),
                ))
                n_added += 1
    # If neither marketplace produced data, record an honest blocked channel-roll for prov.
    if not any_ok and (any_blocked or all(k.startswith("marketplace_") for k in status)):
        pass  # the per-lane statuses already carry the honest blocked/failed truth.


def _marketplace_listings(result: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    """Pull the listings list from a tier-router result (result.result.listings). A detail-only
    payload (no listings) -> []. PURE + TOTAL (never fabricates)."""
    inner = result.get("result")
    if not isinstance(inner, Mapping):
        return []
    items = inner.get("listings")
    if isinstance(items, list):
        return [it for it in items if isinstance(it, Mapping)]
    return []


def _marketplace_blocked_status(result: Mapping[str, Any], winning_tier: str) -> str:
    """An honest blocked status for a marketplace lane that produced no lead data, surfacing the
    tier failure reasons (e.g. Firecrawl 402). PURE + TOTAL."""
    failures = result.get("tier_failures")
    reasons: List[str] = []
    if isinstance(failures, list):
        for f in failures:
            if isinstance(f, Mapping):
                reasons.append("%s: %s" % (_s(f.get("tier")), _truncate(_s(f.get("reason")), 80)))
    detail = "; ".join(reasons[:4]) if reasons else "no listings"
    if winning_tier == "manual_paste":
        return "blocked (needs_paste -- all automated tiers degraded; %s)" % detail
    return "blocked (%s)" % detail


def _listing_to_lead(
    listing: Mapping[str, Any], marketplace: str, region: str, seed: str,
) -> Optional[Dict[str, Any]]:
    """Map ONE marketplace listing -> a lead record (spec sec 5). NEVER-FABRICATE: a lead needs
    a seller OR a title (otherwise it is dropped, never invented); the contact is the listing/
    seller URL the lane ACTUALLY returned (a public profile -- NOT an email/phone, which the
    marketplace does not expose). PURE + TOTAL."""
    seller = _s(listing.get("seller"))
    title = _s(listing.get("title"))
    url = _s(listing.get("url")) or _s(listing.get("permalink"))
    if not seller and not title:
        return None  # nothing real to anchor a lead on -> drop (never fabricate a name).

    nome = seller or ("Vendedor (%s)" % title[:40] if title else "")
    if not nome:
        return None

    # The intent signal: the competing listing anchored to the seed (a REAL quote of the title).
    sinal_parts: List[str] = []
    if title:
        sinal_parts.append("anuncio: '%s'" % _truncate(title, 80))
    sold = listing.get("sold_quantity")
    if isinstance(sold, int) and sold > 0:
        sinal_parts.append("%d vendidos" % sold)
    sinal = " -- ".join(sinal_parts) if sinal_parts else "anuncio concorrente para '%s'" % _truncate(seed, 40)

    # The contact: ONLY a real public URL the lane returned (NEVER an invented email/phone). When
    # the lane returned no URL, the contact display is None -> the row renders '--' (absent).
    contato_display: Optional[str] = None
    identificadores: Dict[str, Any] = {"loja": seller} if seller else {}
    contato: Dict[str, Any] = {}
    if url:
        contato_display = "via %s (perfil/anuncio publico) -- e-mail nao exposto" % marketplace
        contato["url"] = url
        identificadores["url_perfil"] = url

    n_signals = len(sinal_parts) if sinal_parts else 1
    score = _lead_confidence(n_signals, has_contact=bool(url), has_identifier=bool(seller))
    qualificado = bool(seller) and bool(url)  # a reachable seller with a real listing is qualified.

    return {
        "nome": nome,
        "tipo": "empresa",
        "canal": CHANNEL_B2C,
        "fonte": "ml" if marketplace in ("mercadolivre", "meli", "ml") else marketplace,
        "identificadores": identificadores,
        "contato": contato,
        "contato_display": contato_display,
        "sinal": sinal,
        "score": score,
        "status": "qualificado" if qualificado else "novo",
        "provenancia": {"fonte": marketplace, "metodo": "scrape", "status": "ok"},
        "_qualificado": qualificado,
        "_source_url": url or None,
    }


# --------------------------------------------------------------------------- #
# B2B CNPJ channel -- cex_cnpj_enrich (firmographics) + cex_ibge_sidra (market context). A
# CNPJ seed that resolves to a real company IS a lead (tipo=empresa); its contact is the email/
# phone the Receita/BrasilAPI ACTUALLY returned (NEVER fabricated). ibge is context only.
# --------------------------------------------------------------------------- #
def _channel_b2b(
    seed: str, region: str, now: Optional[str], status: Dict[str, str],
    leads: List[Dict[str, Any]], sources: List[str], prov: List[Dict[str, Any]],
) -> None:
    """Resolve the B2B CNPJ channel. Mutates state in place. TOTAL."""
    rec = _run_lane(status, "cnpj", lambda: _lane_cnpj(seed, now))
    cnpj_token = _collapse_endpoint_status(rec) if rec is not None else status.get("cnpj", "failed")
    if rec is not None and "cnpj" not in (k for k in status if status[k].startswith("failed")):
        status["cnpj"] = cnpj_token
    if isinstance(rec, Mapping) and cnpj_token == "ok":
        if "cnpj.gov (BrasilAPI)" not in sources:
            sources.append("cnpj.gov (BrasilAPI)")
        lead = _cnpj_to_lead(rec, region, seed)
        if lead is not None:
            leads.append(lead)
            prov.append(_gen.make_provenance(
                finding="Leads::%s" % _truncate(str(lead.get("nome") or ""), 50),
                source_url=None,  # BrasilAPI has no per-company public URL the lane returns.
                fetched_at=_s(rec.get("fetched_at")) or None,
                method="fetch",
                confidence=float(lead.get("score") or 0.0),
            ))

    # ibge: market-sizing CONTEXT only (firmographic backdrop) -- NEVER a lead source.
    ibge = _run_lane(status, "ibge", lambda: _lane_ibge(now))
    ibge_token = _collapse_endpoint_status(ibge) if ibge is not None else status.get("ibge", "failed")
    if ibge is not None and not status.get("ibge", "").startswith("failed"):
        status["ibge"] = "%s (contexto de mercado, nao gera lead)" % ibge_token
    if isinstance(ibge, Mapping) and ibge_token == "ok" and "ibge (SIDRA)" not in sources:
        sources.append("ibge (SIDRA)")


def _cnpj_to_lead(rec: Mapping[str, Any], region: str, seed: str) -> Optional[Dict[str, Any]]:
    """Map a CNPJ firmographics record -> a lead record (spec sec 5). NEVER-FABRICATE: needs a
    real razao_social/nome_fantasia (else dropped); the contact is ONLY the email/phone the API
    returned. PURE + TOTAL."""
    nome = _s(rec.get("razao_social")) or _s(rec.get("nome_fantasia"))
    if not nome:
        return None  # the API returned no company name -> not a real lead (never fabricated).

    cnpj = _s(rec.get("cnpj"))
    cnae = _s(rec.get("cnae_principal_descricao")) or _s(rec.get("cnae_principal"))
    uf = ""
    endereco = rec.get("endereco")
    if isinstance(endereco, Mapping):
        uf = _s(endereco.get("uf"))
    sinal_parts: List[str] = []
    if cnae:
        sinal_parts.append("CNAE %s" % _truncate(cnae, 60))
    if uf:
        sinal_parts.append("atua em %s" % uf)
    sinal = " -- ".join(sinal_parts) if sinal_parts else "firmografia (CNPJ ativo)"

    # The contact: ONLY a REAL email/phone the API returned (NEVER fabricated).
    email = _s(rec.get("email"))
    telefones = rec.get("telefones")
    telefone = ""
    if isinstance(telefones, list):
        for t in telefones:
            ts = _s(t) if isinstance(t, str) else _s(str(t))
            if ts:
                telefone = ts
                break
    contato: Dict[str, Any] = {}
    contato_bits: List[str] = []
    if email:
        contato["email"] = email
        contato_bits.append("e-mail: %s" % email)
    if telefone:
        contato["telefone"] = telefone
        contato_bits.append("tel: %s" % telefone)
    contato_display = "; ".join(contato_bits) if contato_bits else None

    identificadores: Dict[str, Any] = {}
    if cnpj:
        identificadores["cnpj"] = cnpj

    n_signals = len(sinal_parts) if sinal_parts else 1
    has_contact = bool(email or telefone)
    score = _lead_confidence(n_signals, has_contact=has_contact, has_identifier=bool(cnpj))
    qualificado = bool(cnpj) and has_contact

    return {
        "nome": nome,
        "tipo": "empresa",
        "canal": CHANNEL_B2B,
        "fonte": "cnpj_gov",
        "identificadores": identificadores,
        "contato": contato,
        "contato_display": contato_display,
        "sinal": sinal,
        "score": score,
        "status": "qualificado" if qualificado else "novo",
        "provenancia": {"fonte": "cnpj_gov", "metodo": "fetch", "status": "ok"},
        "_qualificado": qualificado,
        "_source_url": None,
    }


# --------------------------------------------------------------------------- #
# UGC social channel -- reddit + youtube (instagram skipped, no credential). A reddit author /
# youtube comment author voicing a pain/intent around the seed IS a lead (tipo=pessoa); the
# contact is the public post/profile URL the lane returned (NEVER an invented DM/email).
# --------------------------------------------------------------------------- #
def _channel_ugc(
    seed: str, region: str, now: Optional[str], status: Dict[str, str],
    leads: List[Dict[str, Any]], sources: List[str], prov: List[Dict[str, Any]],
) -> None:
    """Resolve the UGC social channel. Mutates state in place. TOTAL."""
    # Reddit.
    reddit = _run_lane(status, "reddit", lambda: _lane_reddit(seed, now))
    reddit_token = _collapse_endpoint_status(reddit) if reddit is not None else status.get("reddit", "failed")
    if reddit is not None and not status.get("reddit", "").startswith("failed"):
        status["reddit"] = reddit_token
    if isinstance(reddit, Mapping) and reddit_token == "ok":
        results = reddit.get("results")
        if isinstance(results, list) and results:
            if "reddit.com" not in sources:
                sources.append("reddit.com")
            n_added = 0
            for post in results:
                if n_added >= _MAX_LEADS_PER_LANE:
                    break
                lead = _reddit_to_lead(post, seed)
                if lead is not None:
                    leads.append(lead)
                    prov.append(_gen.make_provenance(
                        finding="Leads::%s" % _truncate(str(lead.get("nome") or ""), 50),
                        source_url=lead.get("_source_url"),
                        fetched_at=_s(reddit.get("fetched_at")) or None,
                        method="fetch",
                        confidence=float(lead.get("score") or 0.0),
                    ))
                    n_added += 1

    # YouTube.
    yt = _run_lane(status, "youtube", lambda: _lane_youtube(seed, now))
    yt_token = _collapse_endpoint_status(yt) if yt is not None else status.get("youtube", "failed")
    if yt is not None and not status.get("youtube", "").startswith("failed"):
        status["youtube"] = yt_token
    if isinstance(yt, Mapping) and yt_token == "ok":
        comments = yt.get("comments")
        if isinstance(comments, list) and comments:
            if "youtube.com" not in sources:
                sources.append("youtube.com")
            n_added = 0
            for comment in comments:
                if n_added >= _MAX_LEADS_PER_LANE:
                    break
                lead = _youtube_to_lead(comment, seed)
                if lead is not None:
                    leads.append(lead)
                    prov.append(_gen.make_provenance(
                        finding="Leads::%s" % _truncate(str(lead.get("nome") or ""), 50),
                        source_url=lead.get("_source_url"),
                        fetched_at=_s(yt.get("fetched_at")) or None,
                        method="fetch",
                        confidence=float(lead.get("score") or 0.0),
                    ))
                    n_added += 1

    # Instagram: explicitly SKIPPED (no credential / no keyless lane). Honest, never fabricated.
    status["instagram"] = "skipped (sem credencial / sem lane keyless)"


def _reddit_to_lead(post: Mapping[str, Any], seed: str) -> Optional[Dict[str, Any]]:
    """Map ONE reddit result -> a lead record (spec sec 5). NEVER-FABRICATE: needs a real author
    (else dropped); the contact is the public permalink/url the lane returned (NOT a DM/email).
    PURE + TOTAL."""
    if not isinstance(post, Mapping):
        return None
    author = _s(post.get("author"))
    if not author or author.lower() in ("[deleted]", "automoderator"):
        return None  # no real handle -> not a lead (never fabricated).
    title = _s(post.get("title"))
    selftext = _s(post.get("selftext"))
    url = _s(post.get("permalink")) or _s(post.get("url"))
    subreddit = _s(post.get("subreddit"))

    sinal_src = title or selftext
    sinal = ("post: '%s'" % _truncate(sinal_src, 100)) if sinal_src else "atividade em r/%s sobre '%s'" % (
        subreddit or "?", _truncate(seed, 40))

    contato_display: Optional[str] = None
    contato: Dict[str, Any] = {}
    identificadores: Dict[str, Any] = {"handle": "u/%s" % author}
    if url:
        contato_display = "perfil/post publico no Reddit -- sem e-mail/telefone"
        contato["url"] = url
        identificadores["url_perfil"] = url

    n_signals = 1 + (1 if title and selftext else 0)
    score = _lead_confidence(n_signals, has_contact=bool(url), has_identifier=True)
    qualificado = bool(sinal_src) and bool(url)

    return {
        "nome": "u/%s" % author,
        "tipo": "pessoa",
        "canal": CHANNEL_UGC,
        "fonte": "reddit",
        "identificadores": identificadores,
        "contato": contato,
        "contato_display": contato_display,
        "sinal": sinal,
        "score": score,
        "status": "qualificado" if qualificado else "novo",
        "provenancia": {"fonte": "reddit", "metodo": "fetch", "status": "ok"},
        "_qualificado": qualificado,
        "_source_url": url or None,
    }


def _youtube_to_lead(comment: Mapping[str, Any], seed: str) -> Optional[Dict[str, Any]]:
    """Map ONE youtube comment -> a lead record (spec sec 5). NEVER-FABRICATE: needs a real
    author + text; the contact is the comment/channel URL the lane returned (never an email).
    PURE + TOTAL."""
    if not isinstance(comment, Mapping):
        return None
    author = _s(comment.get("author")) or _s(comment.get("author_name"))
    text = _s(comment.get("text"))
    if not author or not text:
        return None  # no real handle/text -> not a lead.
    url = _s(comment.get("url")) or _s(comment.get("comment_url")) or _s(comment.get("author_channel_url"))

    sinal = "comentario: '%s'" % _truncate(text, 100)
    contato_display: Optional[str] = None
    contato: Dict[str, Any] = {}
    identificadores: Dict[str, Any] = {"handle": author}
    if url:
        contato_display = "perfil/comentario publico no YouTube -- sem e-mail/telefone"
        contato["url"] = url
        identificadores["url_perfil"] = url

    score = _lead_confidence(1, has_contact=bool(url), has_identifier=True)
    qualificado = bool(url)

    return {
        "nome": author,
        "tipo": "pessoa",
        "canal": CHANNEL_UGC,
        "fonte": "youtube",
        "identificadores": identificadores,
        "contato": contato,
        "contato_display": contato_display,
        "sinal": sinal,
        "score": score,
        "status": "qualificado" if qualificado else "novo",
        "provenancia": {"fonte": "youtube", "metodo": "fetch", "status": "ok"},
        "_qualificado": qualificado,
        "_source_url": url or None,
    }


# --------------------------------------------------------------------------- #
# THE entry -- the 7 inputs + credential -> the SAME StructuredOutput as leadgen.build. TOTAL;
# NEVER fabricates; NEVER raises (a hard surprise degrades to the offline scaffold).
# --------------------------------------------------------------------------- #
_CHANNEL_HANDLERS = {CHANNEL_B2C, CHANNEL_B2B, CHANNEL_UGC}


def leadgen_run(
    inputs: Mapping[str, Any],
    *,
    credential: "Optional[Any]" = None,
    now: Optional[str] = None,
) -> dict:
    """Run the REAL lead-gen orchestrator -> a StructuredOutput dict (spec 05_leadgen_suite 1b).

    Maps the requested channels (objetivo/seed/canais/regiao/qtd_alvo/qualificacao/min_sinais) to
    the existing lanes, fans out (degrade-never per lane), maps REAL results -> lead records, and
    assembles via the SHARED leadgen.assemble_output so the SHAPE (mold_id="leadgen", 5 sections,
    7-col Leads) is byte-identical to the offline scaffold.

    DEGRADE-NEVER: ALL channels blocked/empty -> honest-EMPTY (0 leads, gate REVISAR), NEVER a
    crash, NEVER a fabricated lead. A HARD orchestrator surprise falls back to leadgen.build (the
    offline scaffold) so the run NEVER 500s. ``credential`` is accepted for interface parity (the
    lanes own their own keys via the env; it is NOT logged/echoed). ``now`` is an OPTIONAL ISO-8601
    stamp threaded to the lanes for deterministic provenance."""
    try:
        return _leadgen_run_inner(inputs, credential=credential, now=now)
    except Exception:
        # Belt-and-suspenders: the inner path is built never to raise (each lane is wrapped), but
        # if anything surprises, fall back to the offline scaffold -- an honest-empty, never a 500,
        # never a fabricated lead. The shape is identical (it is the SAME generator).
        try:
            return _gen.build(inputs, credential=None)
        except Exception:
            # The absolute floor: a minimal honest-empty via the assembler on default inputs.
            notes = ["leadgen_run hard fallback -- honest-empty (nenhum lead fabricado)"]
            parsed = _gen.parse_inputs(inputs if isinstance(inputs, Mapping) else {}, notes)
            return _empty_assemble(parsed, notes, inputs if isinstance(inputs, Mapping) else {})


def _leadgen_run_inner(
    inputs: Mapping[str, Any],
    *,
    credential: "Optional[Any]" = None,
    now: Optional[str] = None,
) -> dict:
    """The real orchestration body. Each lane is wrapped (degrade-never), so this is TOTAL."""
    notes: List[str] = []

    # BRAND_MUSTACHE: brand-frame the brief (additive; un-branded -> no note). Mirrors the gen.
    _bnote = _gen.brand_frame_note(inputs) if hasattr(_gen, "brand_frame_note") else None
    if _bnote:
        notes.append(_bnote)

    parsed = _gen.parse_inputs(inputs, notes)
    seed = parsed["seed"]
    region = parsed["region"]
    channels = list(parsed["channels"])
    min_sinais = int(parsed["min_sinais"])

    notes.append("lanes reais (fase 1b) -- credencial das lanes via ambiente; nenhum lead fabricado")

    # Fan-out: each channel handler runs its lanes (each lane degrade-never wrapped) and appends
    # any REAL leads + honest per-source statuses + the specific sources consulted.
    status: Dict[str, str] = {}
    leads: List[Dict[str, Any]] = []
    sources: List[str] = []
    prov: List[Dict[str, Any]] = []

    for ch in channels:
        if ch == CHANNEL_B2C:
            _channel_b2c(seed, region, status, leads, sources, prov)
        elif ch == CHANNEL_B2B:
            _channel_b2b(seed, region, now, status, leads, sources, prov)
        elif ch == CHANNEL_UGC:
            _channel_ugc(seed, region, now, status, leads, sources, prov)
        # An unknown channel never reaches here (parse_inputs filters to the valid subset).

    # Assemble the honest outcome from the REAL leads (NEVER padded; honest count).
    leads_encontrados = len(leads)
    leads_qualificados = sum(1 for ld in leads if ld.get("_qualificado"))
    # Coverage (condition c): a LEAD-BEARING lane returned data OR a lead was actually found.
    # ibge is firmographic CONTEXT, NOT a lead source, so an ibge-only 'ok' does NOT count as
    # coverage (that would be a misleading PROSSEGUIR-leaning signal). Honest by construction.
    cobertura_ok = leads_encontrados > 0 or any(
        v.startswith("ok") for lane, v in status.items() if lane != "ibge"
    )

    # Confidence aggregate: the mean of the per-lead scores (REAL), or 0 when no leads. NEVER guessed.
    if leads:
        confianca_agregada = round(sum(float(ld.get("score") or 0.0) for ld in leads) / len(leads), 2)
    else:
        confianca_agregada = 0.0

    # The Leads rows -- one per REAL lead via the SHARED projector (contato '--' when lane-less).
    canais_label = ", ".join(_CHANNEL_LABEL.get(ch, ch) for ch in channels)
    if leads:
        lead_rows = [_gen._lead_row(ld, canais_label) for ld in leads]
    else:
        # Honest empty-state row (the never-fabricate stance: shows WHY it is empty, not a fake lead).
        lead_rows = [[
            "(nenhum lead encontrado)", "--", canais_label, _gen.CONTACT_ABSENT,
            "lanes consultadas, nenhum lead retornado (ver Proveniencia)", 0.0, "vazio",
        ]]

    # Per-channel status string (honest, rolled from the lane statuses for each channel).
    status_por_canal = _status_por_canal(channels, status)

    # Provenance counts: ok lanes vs blocked/failed/skipped lanes.
    n_fontes_ok = sum(1 for v in status.values() if v.startswith("ok"))
    n_fontes_sem_dado = sum(1 for v in status.values() if not v.startswith("ok"))

    # Fontes (the specific sources actually consulted, each with its recorte). When none produced
    # data, list the lanes that were consulted with their honest status (never a fabricated source).
    fontes_items = _fontes_items(seed, region, sources, status)

    fontes_consultadas_label = "; ".join(sources) if sources else "nenhuma com dado"
    # Per-lane blocked reason is kept generously (so a Firecrawl 402 / anti-bot reason stays
    # VISIBLE -- honest provenance), but still bounded (the "bounded" invariant): a pathological
    # lane status can never balloon the report.
    sem_dado = ["%s: %s" % (lane, _truncate(st, 220)) for lane, st in status.items() if not st.startswith("ok")]
    fontes_sem_dado_label = "; ".join(sem_dado) if sem_dado else "nenhuma"

    frescor = _s(now) and ("dado coletado em %s" % _s(now)) or "lanes consultadas (sem stamp)"
    if not leads:
        frescor = "nenhum dado coletado (lanes bloqueadas/vazias)"

    total_brutos_label = "%d leads de %d lane(s) ok" % (leads_encontrados, n_fontes_ok)
    captura_ts_label = _s(now) or "executado (sem stamp)"

    if leads_encontrados == 0:
        notes.append("honest-empty: nenhuma lane retornou lead (Firecrawl 402 / sem credencial / "
                     "bloqueio anti-bot -- resultado correto, nada fabricado)")

    return _gen.assemble_output(
        parsed,
        offline=False,
        lead_rows=lead_rows,
        leads_encontrados=leads_encontrados,
        leads_qualificados=leads_qualificados,
        confianca_agregada=confianca_agregada,
        frescor=frescor,
        n_fontes_ok=n_fontes_ok,
        n_fontes_sem_dado=n_fontes_sem_dado,
        status_por_canal=status_por_canal,
        fontes_consultadas_label=fontes_consultadas_label,
        fontes_sem_dado_label=fontes_sem_dado_label,
        total_brutos_label=total_brutos_label,
        captura_ts_label=captura_ts_label,
        cobertura_ok=cobertura_ok,
        fontes_items=fontes_items,
        notes=notes,
        inputs=inputs,
        provenance=prov,
        run_mode=RUN_MODE,
    )


def _status_por_canal(channels: List[str], status: Dict[str, str]) -> str:
    """Roll the per-lane statuses up to one honest per-CHANNEL string. PURE + TOTAL."""
    chan_lanes = {
        CHANNEL_B2C: ("marketplace_mercadolivre", "marketplace_shopee"),
        CHANNEL_B2B: ("cnpj", "ibge"),
        CHANNEL_UGC: ("reddit", "youtube", "instagram"),
    }
    parts: List[str] = []
    for ch in channels:
        lane_bits = []
        for lane in chan_lanes.get(ch, ()):
            if lane in status:
                # Bounded but generous so a blocked reason (e.g. Firecrawl 402) stays visible.
                lane_bits.append("%s=%s" % (lane, _truncate(status[lane], 180)))
        label = _CHANNEL_LABEL.get(ch, ch)
        parts.append("%s: %s" % (label, ", ".join(lane_bits) if lane_bits else "nenhuma lane"))
    return "; ".join(parts)


def _fontes_items(
    seed: str, region: str, sources: List[str], status: Dict[str, str],
) -> List[str]:
    """The specific sources hit, each with its recorte (query). When a lane produced data it is
    listed as consulted; a blocked/failed lane is listed honestly (NEVER fabricated as 'ok')."""
    items: List[str] = []
    for lane, st in status.items():
        verb = "consultada" if st.startswith("ok") else "bloqueada/sem dado"
        items.append("%s [%s] -- recorte: '%s' em %s (%s)"
                     % (lane, verb, _truncate(seed, 40), region, _truncate(st, 80)))
    if not items:
        items = ["nenhuma fonte consultada"]
    return items


def _empty_assemble(parsed: Mapping[str, Any], notes: List[str], inputs: Mapping[str, Any]) -> dict:
    """The absolute hard-fallback honest-empty output (used only if even _gen.build raised). Same
    frozen shape, 0 leads, gate REVISAR. NEVER fabricates."""
    channels = list(parsed["channels"])
    canais_label = ", ".join(_CHANNEL_LABEL.get(ch, ch) for ch in channels)
    lead_rows = [[
        "(nenhum lead encontrado)", "--", canais_label, _gen.CONTACT_ABSENT,
        "fallback honesto -- nenhuma lane executada", 0.0, "vazio",
    ]]
    return _gen.assemble_output(
        parsed,
        offline=True,
        lead_rows=lead_rows,
        leads_encontrados=0,
        leads_qualificados=0,
        confianca_agregada=0.0,
        frescor="indisponivel (fallback)",
        n_fontes_ok=0,
        n_fontes_sem_dado=0,
        status_por_canal="; ".join("%s: nao executado (fallback)" % _CHANNEL_LABEL.get(ch, ch)
                                   for ch in channels),
        fontes_consultadas_label="nenhuma (fallback)",
        fontes_sem_dado_label="nenhuma",
        total_brutos_label="0 (fallback)",
        captura_ts_label="nao executado (fallback)",
        cobertura_ok=False,
        fontes_items=["nenhuma fonte consultada (fallback)"],
        notes=notes,
        inputs=inputs,
    )


__all__ = [
    "leadgen_run",
    "CAPABILITY",
    "RUN_MODE",
    "CHANNEL_B2C",
    "CHANNEL_B2B",
    "CHANNEL_UGC",
]


# --------------------------------------------------------------------------- #
# CLI -- a credential-free dry run (the lanes honest-block without their credentials; the
# orchestrator NEVER raises, NEVER fabricates). Prints the StructuredOutput JSON; exit 0.
# --------------------------------------------------------------------------- #
def _parse_opt(argv: List[str], flag: str) -> Optional[str]:
    """Pull a ``--flag value`` (or ``--flag=value``) out of argv (PURE)."""
    for i, tok in enumerate(argv):
        if tok == flag and i + 1 < len(argv):
            return argv[i + 1]
        if tok.startswith(flag + "="):
            return tok.split("=", 1)[1]
    return None


def _main(argv: List[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print("CEXAI lead-gen REAL orchestrator (spec 05_leadgen_suite Phase 1b). Usage:")
        print('  python _tools/cex_leadgen_run.py "<objetivo>" --seed "<seed>" '
              "[--canais b2c_marketplace,b2b_cnpj,ugc_social] [--regiao <r>]")
        print("")
        print("  Each lane is degrade-never + honest-blocked without its credential; the")
        print("  orchestrator NEVER raises, NEVER fabricates a lead/contact. Prints the")
        print("  StructuredOutput JSON (mold_id=leadgen, the 5 frozen sections); exit 0.")
        return 0

    objetivo_tokens: List[str] = []
    skip = 0
    for i, tok in enumerate(argv):
        if skip:
            skip = 0
            continue
        if tok.startswith("--"):
            if "=" not in tok:
                skip = 1  # the value follows as the next token.
            continue
        objetivo_tokens.append(tok)
    objetivo = " ".join(objetivo_tokens).strip()

    seed = _parse_opt(argv, "--seed") or ""
    canais = _parse_opt(argv, "--canais")
    regiao = _parse_opt(argv, "--regiao")

    inputs: Dict[str, Any] = {"objetivo": objetivo, "seed": seed}
    if canais:
        inputs["canais"] = canais
    if regiao:
        inputs["regiao"] = regiao

    import datetime as _dt
    now = _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    out = leadgen_run(inputs, credential=None, now=now)

    import json
    print(json.dumps(out, ensure_ascii=True, indent=2, sort_keys=True))
    # Exit 0 even when every lane honest-blocks -- a blocked lane is a VALID, recorded result.
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))

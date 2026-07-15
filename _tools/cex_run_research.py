#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI STORM research engine -- cex_run_research (mission CAPABILITY_LAYER, Wave 2).

THE multi-source research engine: the depth upgrade over Wave 1's single-step research
(plan S1.2 / S7.2 W2). It swaps run_capability's ONE build for a real STORM loop
(Shao et al. 2024, n01 S2): PLAN the query space, FAN OUT over N source lanes in parallel,
MERGE the branches (dedup + CRAG-lite score + partition), then CRITIC the merge against the
output contract. It COMPOSES the shipped spine + cex_sdk.workflow.Parallel -- it does NOT
fork either (the #1 rule).

THE FLOW (n01 S2 STORM method + n03 S1 engineering seam):
  0  SCOPE/BUDGET  reuse the spine's deny-by-default tenant gate + the OQ4 budget guard
                   (cex_agent_loop._Budget / _resolve_budget) -- the budget step ceiling is
                   the FAN-OUT CAP (n03 S1.6 "budget carving"). A non-positive budget refuses
                   BEFORE any LLM call. tenant_id EXPLICIT, fail-closed.
  1  PLAN        ONE CEXAgent.build -> a query plan: head_terms / longtails + N angle
                 sub-questions (STORM 5-perspective, n01 S2.1). The producer's frontmatter
                 carries the plan; we parse it (safe-YAML, degrade-never -> a derived plan).
  2  FAN OUT     cex_sdk.workflow.Parallel(*[Step(lane_i) ...]): N source lanes, each calling
                 the tool_resolver SEAM (the SAME module-level slot in cex_agent_loop, faked
                 in tests). Default unbound -> a deterministic stub PageResult per lane. The
                 ThreadPoolExecutor returns as_completed order -> NON-deterministic, so MERGE
                 sorts by lane index first (n03 S1.6 risk #1).
  3  MERGE       PURE python (NO LLM): collect every lane's pages, dedup by title_hash
                 (n01 S2.3), CRAG-lite score each (n01 S2 / n05 S3.3: relevance + freshness +
                 extractability, mean 0-10), partition accept (>=7.5) / downweight (5.0-7.4) /
                 reject (<5.0). The downweight confidence_modifier = (crag-5.0)/2.5 is a NAMED
                 constant (plan C5 -- make the choice visible). Offline-testable end to end.
  4  CRITIC      ONE CEXAgent.build -> verify the merged evidence vs the 30-field contract
                 (n01 S2.3 / n05 S3.4): set confidence_score (= validation_score), flag gaps,
                 NEVER fabricate. The producer's frontmatter is the corrected structured view.
  5  ASSEMBLE    a structured result matching cex_output_contract.PESQUISA_PRODUTO_CONTRACT
                 (~30 fields): identity/provenance + gate + pricing + competitive + keywords +
                 filing. EVERY datum carries provenance (data_sources per-field origin) and
                 mock:false (n05 S6.3 -- checked at 3 redundant layers). ready_for_ads is the
                 canonical gate (cex_output_contract.compute_ready_for_ads).

DEGRADE-NEVER (n05 S2 -- the cascade ALWAYS bottoms out at the paste floor):
  * NO tool_resolver bound -> each lane returns the unbound stub note; MERGE yields zero
    accepted pages; the run still PLANs + CRITICs over the plan and returns a VALID PARTIAL
    (marketplaces_failed populated, data_sources=paste-floor, mock:false). The run NEVER
    returns empty and NEVER fabricates a number (n05 SLO: non-empty >=99.5%, fabrication 0%).
  * a single lane failing (raises / returns FAILED) does NOT block the others -- Parallel
    catches it into a FAILED StepOutput; MERGE skips it and records the failure.
  * no DbWriter / a LocalOnlyWriter -> the run still completes; step persistence is skipped.
  * no cex_sdk -> a procedural fan-out fallback (ThreadPool directly) runs the SAME lanes.

run_agent_multistep-COMPATIBLE signature (so the async plane can adopt it verbatim):
  run_research(tenant_id, agent_id, inputs, credential, *, db=None, options=None,
               run_key=None) -> ResearchRunResult  (mirrors MultiStepResult's public shape +
  adds the structured 30-field result). The async dashboard plane (POST /agent/runs) can call
  THIS exactly like run_agent_multistep (n03 S1.4).

THE tool_resolver SEAM (the founder-gated live web arsenal -- left as an injectable stub):
  the live firecrawl / brave / tavily lanes are the FOUNDER-GATED seam (n05 S1.5). This module
  binds NO live credentials. Each lane dispatches through cex_agent_loop.tool_resolver
  (default None -> the unbound stub). Tests set cex_agent_loop.tool_resolver = fn to fake the
  lanes; live wiring injects the real MCP-backed resolver. Signature (matches cex_agent_loop):
    tool_resolver(tool_name, args, *, tenant_id, agent_id) -> (result_str, meta_dict).
  A lane interprets result_str as a JSON pages list when possible (the real firecrawl/tavily
  shape), else as one opaque page body. NEVER trusts ambient state (tenant_id is explicit).

HARD RULES (task contract + .claude/rules/ascii-code-rule.md):
  * ASCII-only; fully type-hinted; FAIL-CLOSED (a deny from the spine propagates).
  * 0 NEW KINDS. Compose the spine + cex_sdk.workflow; do NOT fork. Does NOT modify
    cex_agent_loop / agent_runs / the crews surface / the frontend.
  * NO concrete DB driver / NO LLM key imported at MODULE IMPORT (the spine is import-light;
    cex_sdk is imported lazily inside the fan-out). The DbWriter + Credential are INJECTED.

Spec: plan_capability_layer_FINAL_2026-06-18.md (S1.2 STORM module, S2 verticals, S6 robust)
+ n01_brief.md (STORM method + 30-field contract) + n03_brief.md (S1 STORM seam) + n05_brief.md
(S2 degrade-never + S3 quality gates). Composes: _tools/cex_run_capability.py (the spine,
verbatim) + cex_sdk/workflow/Parallel + _tools/cex_output_contract.py (the contract) +
cex_agent_loop._Budget + the cex_agent_loop.tool_resolver seam (READ, not modified).
"""

from __future__ import annotations

import hashlib
import os
import re
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

# --------------------------------------------------------------------------- #
# REUSE the spine VERBATIM (the #1 rule). cex_run_capability is import-light (no
# driver/key at load); cex_agent_loop is import-light too (cex_sdk is lazy). We pull
# the SAME Credential / CapabilityRefused / DbWriter + the run_capability deny/credential
# seam, and the _Budget / _resolve_budget OQ4 ceiling (the fan-out cap).
# --------------------------------------------------------------------------- #
_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

import cex_agent_loop as _al  # type: ignore[import]  # the multi-step plane (tool_resolver + _Budget)
import cex_output_contract as _oc  # type: ignore[import]  # the contract (pure)
import cex_run_capability as _rc  # type: ignore[import]  # the spine

Credential = _rc.Credential
CapabilityResult = _rc.CapabilityResult
CapabilityRefused = _rc.CapabilityRefused
DbWriter = _rc.DbWriter
MODE_BYO_API_KEY = _rc.MODE_BYO_API_KEY
MODE_NATIVE_LOCAL = _rc.MODE_NATIVE_LOCAL
MODE_PLATFORM = _rc.MODE_PLATFORM
_TENANT_DATA_TABLE = _rc._TENANT_DATA_TABLE

# The Wave-2 vertical (plan V1) -- the tenant_data discriminator + the persisted kind.
DEFAULT_RESEARCH_CAPABILITY = "pesquisa_produto"
RESEARCH_KIND = "pesquisa_produto"

# The STORM source lanes (n01 S2.2 / n05 S1.1). Each is a tool_resolver dispatch target. The
# DEFAULT lane set models the live arsenal's tiers; the real impls are the founder-gated seam.
#
# 'playwright_scrape' is the REAL-BROWSER lane (the PROVEN anti-bot marketplace lane): it drives a
# real Chrome to the ML search-results URL and reads the live DOM into STRUCTURED listings
# (title/price/seller). It is the PROVEN competitor/price source -- verified LIVE that a real
# browser defeats the ML anti-bot that blocks the API/firecrawl/firecrawl-screenshot (180 cards
# from the real grid, zero block, zero hallucination -- it is the REAL DOM). It LEADS the default
# set so a browser-ready run reads marketplace prices/competitors DIRECTLY from the live page; with
# no browser available it self-reports 'unavailable' (zero pages -> a recorded lane failure) and
# the merge falls back to the other lanes -- it NEVER fabricates marketplace data (memory:
# reference_ml_scraping_antibot_hallucination).
#
# 'vision_scrape' is the VISION lane (the screenshot+transcribe anti-bot lane): it screenshots a
# marketplace search-results page and transcribes it with a vision model into STRUCTURED listings
# (title/price/sold_quantity/seller). A robust fallback when a real browser is not available.
#
# 'mercadolivre' is the Mercado Livre OFFICIAL-API lane (kept for the seller's OWN catalog; the
# ML /search API is restricted for COMPETITOR search, so this lane mostly future-proofs the
# seller-catalog path). It self-reports 'unavailable' without a token and the merge falls back.
DEFAULT_SOURCE_LANES: Tuple[str, ...] = (
    "playwright_scrape", "vision_scrape", "mercadolivre", "firecrawl", "tavily",
)

# The marketplace lanes (structured-truth: the real-browser DOM read + the VISION transcription +
# the official API). Used to TARGET the query gen toward a CLEAN product query (no 'site:'
# operator -- these lanes hit a marketplace page/API directly, so the operator would only pollute
# the search box / slug).
MARKETPLACE_LANES: Tuple[str, ...] = (
    "mercadolivre", "mercado_livre", "ml_search", "meli",
    "vision_scrape", "vision", "screenshot", "vision_marketplace",
    "playwright_scrape", "browser_scrape", "ml_browser", "playwright",
)

# OPT-IN tier-router routing (W2.5, mirrors how options['use_storm'] was added opt-in in
# cex_run_pipeline). When options['use_tier_router'] is True (or env CEX_USE_TIER_ROUTER=1), a
# MARKETPLACE lane resolves through cex_marketplace_tier_router.resolve(...) -- the degrade-never
# TIER1 OFFICIAL_API -> TIER2 REAL_BROWSER -> TIER3 FIRECRAWL_EXTRACT -> TIER4 MANUAL_PASTE
# escalation -- instead of a single hard-coded tool_resolver fetch. The lane records which tier WON
# (winning_tier) + each prior tier's failure (tier_failures) into provenance/meta. With the flag OFF
# (default) the lane behaves EXACTLY as before (the proven playwright_scrape flagship path stays
# byte-preserving). The tier-router is a READ-ONLY stable dependency (composed, never modified).
USE_TIER_ROUTER_ENV = "CEX_USE_TIER_ROUTER"

# Maps a marketplace LANE name -> the canonical marketplace key the tier-router understands (its
# search-URL builder + the official-API restricted set key off this). A lane NOT in this map is NOT
# routed through the tier-router even when the flag is on (e.g. the VISION lane has no tier mapping
# -> it keeps the direct tool_resolver path). Only the canonical mercadolivre / shopee / amazon_br
# targets route (the task contract: marketplace-lane resolution for those three).
TIER_ROUTER_LANE_MARKETPLACE: Dict[str, str] = {
    "mercadolivre": "mercadolivre",
    "mercado_livre": "mercadolivre",
    "ml_search": "mercadolivre",
    "meli": "mercadolivre",
    "playwright_scrape": "mercadolivre",
    "browser_scrape": "mercadolivre",
    "ml_browser": "mercadolivre",
    "playwright": "mercadolivre",
    "shopee": "shopee",
    "shopee_scrape": "shopee",
    "amazon_br": "amazon_br",
    "amazon": "amazon_br",
    "amazon_scrape": "amazon_br",
}

# CRAG-lite bands (n01 S2.3 / n05 S3.3). accept >= 7.5 | downweight 5.0-7.4 | reject < 5.0.
CRAG_ACCEPT_THRESHOLD = 7.5
CRAG_DOWNWEIGHT_FLOOR = 5.0
# The downweight confidence_modifier coefficient (plan C5 -- adopted DELIBERATELY + NAMED, not
# implicit). Maps a crag score in [5.0, 7.5] -> [0.0, 1.0].
CRAG_CONFIDENCE_DIVISOR = 2.5

# The default fan-out cap when no budget is declared (n03 S1.6 -- the safety backstop). The
# OQ4 budget (options['max_steps'] / options['budget']) tightens this; this is the ceiling.
_DEFAULT_FANOUT_CAP = 5

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


# --------------------------------------------------------------------------- #
# PageResult -- one retrieved source (the unit MERGE dedups + scores). Mirrors n01 S2.4.
# --------------------------------------------------------------------------- #
@dataclass
class PageResult:
    """One retrieved source from a STORM lane. NEVER carries a secret. The CRAG-lite score is
    set by MERGE (relevance + freshness + extractability mean); origin is the lane provenance."""

    title: str = ""
    url: str = ""
    origin: str = ""                       # the lane / provider (brave|firecrawl|tavily|paste)
    price: Optional[float] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None
    seller: str = ""
    marketplace: str = ""
    snippet: str = ""
    crag_score: float = 0.0                # set by MERGE (0-10)
    confidence: float = 0.0               # set by MERGE for downweighted pages [0,1]
    mock: bool = False                     # NEVER true for a delivered datum (n05 S6.3)

    def title_hash(self) -> str:
        """Normalized title hash for dedup (n01 S2.3)."""
        t = (self.title or self.url or "").lower().strip()
        t = re.sub(r"[^\w\s]", "", t)
        t = re.sub(r"\s+", " ", t)
        return hashlib.md5(t.encode("ascii", "ignore")).hexdigest()[:12]


# --------------------------------------------------------------------------- #
# StormMerge -- the MERGE output (accepted / downweight / reject partitions + the failures).
# --------------------------------------------------------------------------- #
@dataclass
class StormMerge:
    """The deterministic MERGE result (n01 S2.3). accepted + downweight feed synthesis;
    rejected + lane_failures drive the degrade-never provenance (marketplaces_failed)."""

    accepted: List[PageResult] = field(default_factory=list)
    downweight: List[PageResult] = field(default_factory=list)
    rejected: List[PageResult] = field(default_factory=list)
    lane_failures: List[str] = field(default_factory=list)   # lane names that failed/empty

    def usable(self) -> List[PageResult]:
        """accepted + downweight, sorted by crag_score desc (n01 S2.4 return order)."""
        return sorted(self.accepted + self.downweight, key=lambda p: p.crag_score, reverse=True)


# --------------------------------------------------------------------------- #
# ResearchRunResult -- the public result (run_agent_multistep-shaped + the structured fields).
# --------------------------------------------------------------------------- #
@dataclass
class ResearchRunResult:
    """Outcome of one STORM research run. The api_key is NEVER present on this object.

    Mirrors MultiStepResult's public shape (so the dashboard _result_to_view projects the
    SAME credential-free fields) and ADDS ``structured`` -- the ~30-field result matching
    cex_output_contract.PESQUISA_PRODUTO_CONTRACT (every datum provenance-tagged, mock:false).
    """

    tenant_id: str
    agent_id: str
    capability: str
    kind: str = RESEARCH_KIND
    pillar: str = "P01"
    nucleus: str = "N01"
    run_id: str = ""
    artifact: str = ""                     # the canonical MD (frontmatter + body)
    score: float = 0.0                     # the CRITIC validation_score (== confidence_score)
    passed: bool = False                   # the F7 gate (the structured result is well-formed)
    status: str = "error"                  # completed | degraded | refused | budget_exceeded | error
    model_used: str = ""
    record_id: Optional[str] = None
    persisted: bool = False
    steps: int = 0
    ready_for_ads: bool = False
    structured: Dict[str, Any] = field(default_factory=dict)   # the 30-field contract result
    open_vars: Dict[str, Any] = field(default_factory=dict)    # the C3 ads-input adapter
    trace: str = ""
    errors: List[str] = field(default_factory=list)
    steps_log: List[Dict[str, Any]] = field(default_factory=list)
    cost: Dict[str, Any] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# THE entry (run_agent_multistep-shaped).
# --------------------------------------------------------------------------- #
def run_research(
    tenant_id: str,
    agent_id: str,
    inputs: Mapping[str, Any],
    credential: Credential,
    *,
    db: Optional[DbWriter] = None,
    options: Optional[Mapping[str, Any]] = None,
    run_key: Optional[str] = None,
) -> ResearchRunResult:
    """THE STORM research run (PLAN -> Parallel fan-out -> MERGE -> CRITIC -> 30-field result).

    See module docstring. run_agent_multistep-compatible signature so the async plane adopts it.

    FAIL-CLOSED: a deny from the spine (missing tenant / disabled capability / native_local /
    missing credential) PROPAGATES as CapabilityRefused. DEGRADE-NEVER: no tools / a lane
    failing / no DB -> a VALID PARTIAL is still returned (status='degraded'), never empty,
    never fabricated. The api_key is never echoed / logged / persisted.
    """
    tid = (tenant_id or "").strip()
    if not tid:
        raise CapabilityRefused("missing_tenant", capability=agent_id)
    capability = (agent_id or DEFAULT_RESEARCH_CAPABILITY).strip() or DEFAULT_RESEARCH_CAPABILITY

    run_inputs: Mapping[str, Any] = inputs if isinstance(inputs, Mapping) else {}
    opts: Mapping[str, Any] = options if isinstance(options, Mapping) else {}
    intent = _derive_intent(run_inputs)

    # -- STEP 0a SCOPE: deny-by-default on the tenant's enabled set (BEFORE any build). ----
    if not _rc._capability_enabled(tid, capability, opts):
        raise CapabilityRefused("capability_disabled", tenant_id=tid, capability=capability)

    # -- STEP 0b RESOLVE: capability -> (nucleus, kind, pillar, verb), OVERLAY-FIRST. ------
    nucleus, kind, pillar, _verb = _rc._resolve_capability(tid, capability)

    # -- STEP 0c CREDENTIAL: select the F5 model/provider (native_local -> raise, OQ2). ----
    model, provider = _rc._select_credential(credential, tid, capability, default_model="")

    # -- STEP 0d BUDGET: the fan-out cap (OQ4). A non-positive budget refuses here. --------
    budget = _al._resolve_budget(opts)
    _guard_budget(tid, capability, opts)
    fanout_cap = _fanout_cap(budget)

    rkey = (run_key or uuid.uuid4().hex)
    run_id = _agent_run_id(tid, rkey)
    result = ResearchRunResult(
        tenant_id=tid, agent_id=capability, capability=capability,
        kind=kind, pillar=pillar, nucleus=nucleus.upper(), run_id=run_id,
    )
    steps_log: List[Dict[str, Any]] = []

    # -- STEP 1 PLAN: ONE CEXAgent.build -> the query plan. --------------------------------
    plan, plan_meta = _plan_step(
        tid, capability, nucleus, kind, model, provider, credential, intent, run_inputs, opts,
    )
    # OPT-IN Co-STORM multi-perspective enrichment (W3, mirrors the use_tier_router opt-in). When
    # env CEX_STORM_MULTIPERSPECTIVE=1 OR options['use_multiperspective'] is True, the PLAN's angles
    # are EXTENDED (additive -- no existing angle removed) with multi-perspective sub-questions. With
    # the flag OFF (default) this is a complete no-op -> the plan + the whole run stay byte-identical
    # (the helper module is imported LAZILY inside the branch, so the default import surface is
    # unchanged). Degrade-never: a missing helper module / any error -> the original plan is kept.
    plan = _maybe_enrich_multiperspective(plan, opts)
    budget.steps_used += 1
    result.model_used = str(plan_meta.get("model_used") or model)
    steps_log.append({"index": 0, "kind": "plan", "content": {
        "head_terms": plan.get("head_terms", []),
        "angles": plan.get("angles", []),
        "passed": bool(plan_meta.get("passed")),
    }})
    # H01/H03 are stamped ONLY on the FINAL assembled artifact (_stamp_artifact_identity below);
    # the intermediate PLAN frontmatter legitimately lacks id/title/description, so its build emits
    # spurious H01/H03 identity-gate errors -- filter them out (they do NOT apply to a plan step).
    result.errors.extend(_strip_intermediate_identity_gates(plan_meta.get("errors")))

    # -- STEP 2 FAN OUT: N source lanes in parallel via the tool_resolver seam. ------------
    lanes = _resolve_lanes(opts, fanout_cap)
    lane_pages, lane_steps, tier_meta = _fanout(
        tid, capability, lanes, plan, run_inputs, opts, budget,
    )
    steps_log.extend(lane_steps)

    # -- STEP 3 MERGE: PURE python dedup + CRAG-lite + partition. --------------------------
    merged = merge_storm_branches(lane_pages)
    budget.steps_used += 1
    steps_log.append({"index": len(steps_log), "kind": "merge", "content": {
        "accepted": len(merged.accepted),
        "downweight": len(merged.downweight),
        "rejected": len(merged.rejected),
        "lane_failures": merged.lane_failures,
    }})

    # -- STEP 4 CRITIC: ONE CEXAgent.build -> verify vs the contract, flag gaps. -----------
    critic, critic_meta = _critic_step(
        tid, capability, nucleus, kind, model, provider, credential,
        intent, plan, merged, run_inputs, opts,
    )
    budget.steps_used += 1
    if critic_meta.get("model_used"):
        result.model_used = str(critic_meta.get("model_used"))
    steps_log.append({"index": len(steps_log), "kind": "critic", "content": {
        "validation_score": critic.get("confidence_score"),
        "passed": bool(critic_meta.get("passed")),
    }})
    # Same as the PLAN step: the intermediate CRITIC frontmatter has no id/title/description, so its
    # build emits spurious H01/H03 identity-gate errors -- filter them (only the final artifact gates).
    result.errors.extend(_strip_intermediate_identity_gates(critic_meta.get("errors")))

    # -- STEP 5 ASSEMBLE: the 30-field structured result (provenance-tagged, mock:false). --
    structured = _assemble_structured(
        tid, run_id, plan, merged, critic, run_inputs, tier_meta,
    )
    # H01/H03 frontmatter identity (the F7 universal gates: H01 needs id+kind+title in the
    # frontmatter; H03 needs a description >=10 chars). The dual renderer emits any extra
    # producer key into the frontmatter, so stamping them on the structured result is enough --
    # the contract stays generic (no per-vertical hardcoding). kind/pillar are the RESOLVED
    # tuple (internally consistent with what the runtime persisted).
    _stamp_artifact_identity(structured, run_id, kind, pillar, plan)
    result.structured = structured
    result.score = _oc._as_number(structured.get("confidence_score")) or 0.0
    result.ready_for_ads = _oc.compute_ready_for_ads(structured)
    result.open_vars = _oc.build_anuncio_open_vars(structured)

    # The run "passed" iff the structured result is well-formed (the gate fields exist). A
    # degrade-never partial (no usable sources) still returns -- status 'degraded', passed
    # reflects whether the contract's required fields are present (n05 honest-partial posture).
    result.passed = _structured_well_formed(structured)
    # status: completed when we got usable evidence AND passed; degraded when the floor fired.
    if merged.usable():
        result.status = "completed" if result.passed else "degraded"
    else:
        result.status = "degraded"

    rendered = _oc.render(structured, _oc.PESQUISA_PRODUTO_CONTRACT)
    result.artifact = rendered.get("md", "")
    result.steps = len(steps_log)
    result.steps_log = steps_log
    result.cost = budget.as_dict()
    result.trace = _trace(plan_meta, merged, critic_meta)

    # -- PERSIST (best-effort-after-pass; tenant_id EXPLICIT; degrade-never). --------------
    _persist(db, result, merged, rendered, tier_meta)
    return result


# --------------------------------------------------------------------------- #
# PLAN -- one CEXAgent.build -> a query plan (head_terms / longtails + N angles).
# --------------------------------------------------------------------------- #
def _plan_step(
    tenant_id: str,
    capability: str,
    nucleus: str,
    kind: str,
    model: str,
    provider: str,
    credential: Credential,
    intent: str,
    inputs: Mapping[str, Any],
    options: Mapping[str, Any],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Run the PLAN build (STORM 5-perspective query gen, n01 S2.1). Returns (plan, meta).

    DEGRADE-NEVER: a build failure / no frontmatter -> a DERIVED plan from the raw intent (so
    the fan-out still has lanes to run). The plan carries head_terms / longtails / angles +
    the product_name (the one hard input, n05 S2.2)."""
    system = _plan_system(inputs)
    build_meta = _build_once(
        tenant_id, capability, nucleus, kind, model, provider, credential, intent, system,
    )
    fm = _extract_frontmatter(build_meta.get("artifact", ""))
    plan = _coerce_plan(fm, intent, inputs)
    return plan, build_meta


def _plan_system(inputs: Mapping[str, Any]) -> str:
    """The PLAN system prompt: ask for the query plan as YAML frontmatter (no accents in
    query strings -- the marketplace anti-bot standard, n01 S2.1)."""
    product = _product_name(inputs)
    return (
        "You are the STORM query planner (5-perspective). Given the product, emit a research "
        "query plan as YAML frontmatter with keys: product_name, head_terms (10-15), longtails "
        "(30-50), synonyms (15-25), angles (5 expert sub-questions: buyer_intent, competitor, "
        "price, spec, trend). Include MARKETPLACE-TARGETED terms in longtails (e.g. "
        "'<produto> mercadolivre', '<produto> preco mercado livre') so the fan-out reaches the "
        "Mercado Livre catalog where the price/competitor evidence lives. Query strings: PT-BR, "
        "lowercase, NO accents. product_name=%r. Never fabricate; if unknown leave a field "
        "empty." % product
    )


def _coerce_plan(fm: Mapping[str, Any], intent: str, inputs: Mapping[str, Any]) -> Dict[str, Any]:
    """Coerce the PLAN frontmatter into a usable plan dict (DEGRADE-NEVER -> derive from intent)."""
    product = _product_name(inputs) or _str_or_empty(fm.get("product_name")) or _first_line(intent)
    head = _oc._as_str_list(fm.get("head_terms")) or _derive_head_terms(product)
    longtails = _oc._as_str_list(fm.get("longtails"))
    synonyms = _oc._as_str_list(fm.get("synonyms"))
    angles = _oc._as_str_list(fm.get("angles")) or list(_DEFAULT_ANGLES)
    marketplaces = _oc._as_str_list(inputs.get("mercados")) or list(_DEFAULT_MARKETPLACES)
    return {
        "product_name": product,
        "head_terms": head,
        "longtails": longtails,
        "synonyms": synonyms,
        "angles": angles,
        "marketplaces": marketplaces,
    }


_DEFAULT_ANGLES = ("buyer_intent", "competitor", "price", "spec", "trend")
_DEFAULT_MARKETPLACES = ("mercado_livre", "shopee", "amazon_br")


def _derive_head_terms(product: str) -> List[str]:
    """A minimal head-term derivation (degrade-never, when PLAN emitted none). Lowercase, no
    accents; the product name + a couple of buying-intent variants (n01 S2.1)."""
    base = _ascii_lower(product)
    if not base:
        return []
    return _dedup([base, ("%s preco" % base).strip(), ("comprar %s" % base).strip()])


# --------------------------------------------------------------------------- #
# FAN OUT -- N source lanes in parallel (cex_sdk.workflow.Parallel), each via tool_resolver.
# --------------------------------------------------------------------------- #
def _fanout(
    tenant_id: str,
    agent_id: str,
    lanes: List[str],
    plan: Mapping[str, Any],
    inputs: Mapping[str, Any],
    options: Mapping[str, Any],
    budget: "_al._Budget",
) -> Tuple[Dict[str, List[PageResult]], List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """Run the N source lanes CONCURRENTLY. Each lane dispatches the tool_resolver seam (the
    SAME slot in cex_agent_loop; default unbound -> stub). Returns ({lane:[pages]}, step_log,
    tier_meta) where tier_meta maps a tier-routed marketplace lane -> {winning_tier, tier_failures}
    (EMPTY unless the OPT-IN tier-router flag is on -> default fan-out is byte-preserving).

    Uses cex_sdk.workflow.Parallel when importable (the composed SDK path); falls back to a
    direct ThreadPoolExecutor with the SAME lane logic (degrade-never). The fan-out cap (the
    budget ceiling) bounds how many lanes fire (n03 S1.6 budget carving)."""
    capped = lanes[: max(1, budget.step_ceiling())]
    query = _primary_query(plan)
    # The OPT-IN tier-router flag + the shared per-lane tier-meta SINK (each lane writes its OWN key
    # -> GIL-safe across the ThreadPool / Parallel workers, the SAME pattern lane_pages uses). With
    # the flag OFF the sink stays empty and every lane takes the unchanged tool_resolver path.
    use_tier_router = _use_tier_router(options)
    tier_meta: Dict[str, Dict[str, Any]] = {}
    lane_args: Dict[str, Any] = {
        "query": query, "plan": dict(plan), "marketplaces": list(plan.get("marketplaces", [])),
        "use_tier_router": use_tier_router, "tier_meta": tier_meta,
    }

    sdk = _import_parallel()
    if sdk is not None:
        lane_pages, step_log = _fanout_via_sdk(sdk, tenant_id, agent_id, capped, lane_args, budget)
    else:
        lane_pages, step_log = _fanout_procedural(tenant_id, agent_id, capped, lane_args, budget)
    return lane_pages, step_log, tier_meta


def _fanout_via_sdk(
    sdk: Dict[str, Any],
    tenant_id: str,
    agent_id: str,
    lanes: List[str],
    lane_args: Mapping[str, Any],
    budget: "_al._Budget",
) -> Tuple[Dict[str, List[PageResult]], List[Dict[str, Any]]]:
    """Fan out through cex_sdk.workflow.Parallel (the composed SDK path, n03 S1.3)."""
    Parallel = sdk["Parallel"]
    Step = sdk["Step"]
    StepInput = sdk["StepInput"]
    StepOutput = sdk["StepOutput"]

    # Each lane is a cex_sdk Step whose executor calls the tool_resolver seam and returns the
    # parsed pages in the StepOutput content (carried back through Parallel's {name: output}).
    steps = []
    for lane in lanes:
        steps.append(Step(name=lane, executor=_make_lane_executor(
            lane, tenant_id, agent_id, lane_args, StepOutput,
        ), max_retries=1))
    parallel = Parallel(*steps, name="storm_fanout", max_workers=max(1, min(3, len(steps))))
    outputs = parallel.run(StepInput(content=lane_args.get("query", "")))

    lane_pages: Dict[str, List[PageResult]] = {}
    step_log: List[Dict[str, Any]] = []
    # SORT by lane index (Parallel returns as_completed order -> non-deterministic; n03 S1.6).
    for idx, lane in enumerate(lanes):
        out = outputs.get(lane)
        pages = list(getattr(out, "content", None) or []) if out is not None else []
        if not isinstance(pages, list):
            pages = []
        lane_pages[lane] = [p for p in pages if isinstance(p, PageResult)]
        budget.steps_used += 1
        budget.tokens_used += sum(len(p.snippet) for p in lane_pages[lane])
        step_log.append({"index": idx + 1, "kind": "tool", "tool": lane, "content": {
            "pages": len(lane_pages[lane]),
            "status": str(getattr(out, "status", "")) if out is not None else "missing",
        }})
    return lane_pages, step_log


def _fanout_procedural(
    tenant_id: str,
    agent_id: str,
    lanes: List[str],
    lane_args: Mapping[str, Any],
    budget: "_al._Budget",
) -> Tuple[Dict[str, List[PageResult]], List[Dict[str, Any]]]:
    """The SAME fan-out WITHOUT cex_sdk -- a direct ThreadPoolExecutor (degrade-never). Mirrors
    _fanout_via_sdk so the lanes behave identically whether or not cex_sdk imports."""
    lane_pages: Dict[str, List[PageResult]] = {lane: [] for lane in lanes}
    failures: Dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=max(1, min(3, len(lanes)))) as pool:
        futures = {pool.submit(_run_lane, lane, tenant_id, agent_id, lane_args): lane for lane in lanes}
        for fut in as_completed(futures):
            lane = futures[fut]
            try:
                lane_pages[lane] = fut.result()
            except Exception as exc:  # a lane failing must NOT block the others (n05 S2.1).
                failures[lane] = "%s: %s" % (type(exc).__name__, exc)
                lane_pages[lane] = []

    step_log: List[Dict[str, Any]] = []
    for idx, lane in enumerate(lanes):  # deterministic order (sort by lane index)
        budget.steps_used += 1
        budget.tokens_used += sum(len(p.snippet) for p in lane_pages[lane])
        step_log.append({"index": idx + 1, "kind": "tool", "tool": lane, "content": {
            "pages": len(lane_pages[lane]),
            "status": "failed" if lane in failures else "ok",
        }})
    return lane_pages, step_log


def _make_lane_executor(
    lane: str,
    tenant_id: str,
    agent_id: str,
    lane_args: Mapping[str, Any],
    step_output_cls: Any,
) -> Callable[[Any], Any]:
    """Build a cex_sdk Step executor for one lane. It runs the lane and wraps the pages in a
    StepOutput. NEVER raises (a lane error becomes an empty-pages StepOutput -> MERGE records
    it as a failure)."""

    def _exec(_inp: Any) -> Any:
        try:
            pages = _run_lane(lane, tenant_id, agent_id, lane_args)
            return step_output_cls(content=pages)
        except Exception as exc:
            return step_output_cls(content=[], error="%s: %s" % (type(exc).__name__, exc))

    return _exec


def _run_lane(
    lane: str,
    tenant_id: str,
    agent_id: str,
    lane_args: Mapping[str, Any],
) -> List[PageResult]:
    """Run ONE source lane: dispatch the tool_resolver seam, parse the result into PageResults.

    The resolver is cex_agent_loop.tool_resolver (default None -> the unbound stub). Signature
    (matches cex_agent_loop): tool_resolver(tool_name, args, *, tenant_id, agent_id) ->
    (result_str, meta_dict). We read the resolver THROUGH the module so a test that sets
    cex_agent_loop.tool_resolver is honored (it is the SAME slot the multi-step loop uses).

    DEGRADE-NEVER: resolver None / a resolver error -> [] (the paste-floor provenance is
    applied in MERGE/ASSEMBLE). NEVER fabricates a page.

    OPT-IN: when lane_args['use_tier_router'] is True AND the lane maps to a tier-router
    marketplace (TIER_ROUTER_LANE_MARKETPLACE), the lane resolves through the tier-router's
    TIER1->TIER4 escalation instead of the single resolver dispatch, recording winning_tier +
    tier_failures into lane_args['tier_meta'][lane]. The flag-OFF default path below is unchanged."""
    plan = lane_args.get("plan") if isinstance(lane_args.get("plan"), Mapping) else {}
    if lane_args.get("use_tier_router") and (lane or "").strip().lower() in TIER_ROUTER_LANE_MARKETPLACE:
        return _run_lane_via_tier_router(lane, tenant_id, agent_id, lane_args, plan)

    resolver = getattr(_al, "tool_resolver", None)
    if resolver is None:
        # Unbound: record the honest note (no live impl); zero pages -> degrade to floor.
        return []
    query = _lane_query(lane, str(lane_args.get("query", "")), plan)
    args = {"query": query, "marketplaces": list(lane_args.get("marketplaces", []))}
    try:
        result_str, meta = resolver(lane, args, tenant_id=tenant_id, agent_id=agent_id)
    except Exception:
        return []
    return _parse_lane_result(lane, result_str, meta)


def _run_lane_via_tier_router(
    lane: str,
    tenant_id: str,
    agent_id: str,
    lane_args: Mapping[str, Any],
    plan: Mapping[str, Any],
) -> List[PageResult]:
    """Resolve ONE marketplace lane through cex_marketplace_tier_router.resolve(...) -- the
    degrade-never TIER1 OFFICIAL_API -> TIER2 REAL_BROWSER -> TIER3 FIRECRAWL_EXTRACT -> TIER4
    MANUAL_PASTE escalation. Records {winning_tier, tier_failures, mock} into the shared
    tier_meta sink under the lane key, and returns the winning tier's listings as PageResults.

    DEGRADE-NEVER + TOTAL: a missing tier-router module, a resolve error, or a non-listing
    winning tier (e.g. the TIER4 manual_paste sentinel) -> [] (the paste floor in MERGE/ASSEMBLE).
    NEVER fabricates a page. The bound cex_agent_loop.tool_resolver (if any) is adapted into the
    router's browser_scraper seam so the SAME test/live seam still drives the lane."""
    router = _import_tier_router()
    sink = lane_args.get("tier_meta")
    marketplace = TIER_ROUTER_LANE_MARKETPLACE.get((lane or "").strip().lower(), "mercadolivre")
    query = _lane_query(lane, str(lane_args.get("query", "")), plan)
    if router is None:
        if isinstance(sink, dict):
            sink[lane] = {"winning_tier": None, "tier_failures": [], "marketplace": marketplace,
                          "note": "tier_router_unavailable"}
        return []
    scraper = _tier_router_browser_seam(tenant_id, agent_id, lane_args)
    try:
        resolved = router.resolve(marketplace, query, browser_scraper=scraper)
    except Exception as exc:  # the router is TOTAL, but stay belt-and-suspenders (never raises up).
        if isinstance(sink, dict):
            sink[lane] = {"winning_tier": None, "tier_failures": [
                {"tier": "resolve", "reason": "%s: %s" % (type(exc).__name__, exc)}],
                "marketplace": marketplace}
        return []

    if isinstance(sink, dict):
        sink[lane] = {
            "winning_tier": resolved.get("winning_tier"),
            "tier_failures": list(resolved.get("tier_failures") or []),
            "marketplace": marketplace,
            "mock": bool(resolved.get("mock")),
        }
    return _pages_from_tier_result(lane, resolved)


def _tier_router_browser_seam(
    tenant_id: str, agent_id: str, lane_args: Mapping[str, Any],
) -> Optional[Callable[..., Any]]:
    """Adapt the bound cex_agent_loop.tool_resolver into the tier-router's browser_scraper seam
    (query, *, marketplace, limit) -> {"status", "listings"}. Returns None when no resolver is
    bound (the router then uses its OWN default browser lane / degrades). DEGRADE-NEVER: a resolver
    error -> an 'unavailable' status (the router records it as the tier's failure)."""
    resolver = getattr(_al, "tool_resolver", None)
    if resolver is None:
        return None

    def _seam(query: str, *, marketplace: str, limit: int = 20) -> Dict[str, Any]:
        args = {"query": query, "marketplaces": list(lane_args.get("marketplaces", []))}
        try:
            result_str, meta = resolver(marketplace, args, tenant_id=tenant_id, agent_id=agent_id)
        except Exception as exc:
            return {"status": "unavailable", "listings": [], "error": type(exc).__name__}
        pages = _parse_lane_result(marketplace, result_str, meta)
        listings = [_page_to_listing(p) for p in pages][: max(1, limit)]
        return {"status": "ok" if listings else "empty", "listings": listings}

    return _seam


def _page_to_listing(page: PageResult) -> Dict[str, Any]:
    """A PageResult -> the marketplace listing dict shape the tier-router emits (so the round-trip
    back through _page_from_obj preserves the structured fields). NEVER fabricates."""
    return {
        "title": page.title, "url": page.url, "origin": page.origin, "price": page.price,
        "rating": page.rating, "reviews": page.reviews, "seller": page.seller,
        "marketplace": page.marketplace, "snippet": page.snippet, "mock": False,
    }


def _pages_from_tier_result(lane: str, resolved: Mapping[str, Any]) -> List[PageResult]:
    """Extract the winning tier's listings from a tier-router result -> PageResults. The TIER4
    manual_paste sentinel carries NO listing (only a URL) -> [] (the paste floor). TOTAL."""
    result = resolved.get("result") if isinstance(resolved, Mapping) else None
    if not isinstance(result, Mapping):
        return []
    listings = result.get("listings")
    if not isinstance(listings, list):
        return []
    pages: List[PageResult] = []
    for item in listings:
        page = _page_from_obj(lane, item)
        if page is not None:
            pages.append(page)
    return pages


def _lane_query(lane: str, base_query: str, plan: Mapping[str, Any]) -> str:
    """The MARKETPLACE-TARGETED query for ONE lane (query rewriting, n07 F3 INJECT). The official
    Mercado Livre lane gets the CLEAN product query (its API already scopes to MLB -- a 'site:'
    operator would only pollute it). A web lane (serper/firecrawl/brave/tavily) gets a
    'site:mercadolivre.com.br <product>' rewrite so the SERP surfaces marketplace listings (the
    richest price/competitor evidence) rather than generic blog pages. The neutral 'exa' neural
    lane keeps the clean query (it ranks by semantics, not operators). DEGRADE-NEVER: an empty
    base_query falls back to the plan's product_name."""
    q = (base_query or "").strip() or _ascii_lower(_str_or_empty(plan.get("product_name")))
    name = (lane or "").strip().lower()
    if name in MARKETPLACE_LANES:
        return q  # official API lane -> clean product query (no operator).
    if name in ("serper", "firecrawl", "brave", "web_search", "search"):
        # Web SERP lanes: target the Brazilian marketplace explicitly to surface listings.
        return ("site:mercadolivre.com.br %s" % q).strip() if q else q
    return q  # exa / research / reviews / unknown -> clean query.


def _parse_lane_result(lane: str, result_str: Any, meta: Any) -> List[PageResult]:
    """Parse a resolver result into PageResults. The real firecrawl/tavily shape is a JSON list
    of page dicts; a degraded resolver may return one opaque body. DEGRADE-NEVER + TOTAL."""
    pages: List[PageResult] = []
    raw_pages = None
    if isinstance(meta, Mapping) and isinstance(meta.get("pages"), list):
        raw_pages = meta.get("pages")
    elif isinstance(result_str, list):
        raw_pages = result_str
    else:
        parsed = _try_json(result_str)
        if isinstance(parsed, list):
            raw_pages = parsed
        elif isinstance(parsed, Mapping) and isinstance(parsed.get("pages"), list):
            raw_pages = parsed.get("pages")

    if isinstance(raw_pages, list):
        for item in raw_pages:
            page = _page_from_obj(lane, item)
            if page is not None:
                pages.append(page)
        return pages

    # Opaque single-body result: one page carrying the snippet (real source, origin=lane).
    body = str(result_str or "").strip()
    if body:
        pages.append(PageResult(title=body[:80], origin=lane, snippet=body[:2000], mock=False))
    return pages


def _page_from_obj(lane: str, item: Any) -> Optional[PageResult]:
    """Build a PageResult from a resolver page dict (TOTAL -- skips a non-mapping)."""
    if isinstance(item, PageResult):
        return item
    if not isinstance(item, Mapping):
        return None
    return PageResult(
        title=_str_or_empty(item.get("title")),
        url=_str_or_empty(item.get("url")),
        origin=_str_or_empty(item.get("origin")) or lane,
        price=_oc._as_number(item.get("price")),
        rating=_oc._as_number(item.get("rating")),
        reviews=_as_int(item.get("reviews")),
        seller=_str_or_empty(item.get("seller")),
        marketplace=_str_or_empty(item.get("marketplace")),
        snippet=_str_or_empty(item.get("snippet")),
        mock=bool(item.get("mock")) if isinstance(item.get("mock"), bool) else False,
    )


# --------------------------------------------------------------------------- #
# MERGE -- PURE python: dedup by title_hash, CRAG-lite score, partition (n01 S2.3). Offline.
# --------------------------------------------------------------------------- #
def merge_storm_branches(lane_pages: Mapping[str, List[PageResult]]) -> StormMerge:
    """The deterministic MERGE (n01 S2.3 / n05 S3.3). PURE -- NO LLM, fully offline-testable.

    1. SORT lanes by name (Parallel/ThreadPool order is non-deterministic -> stabilize first).
    2. Flatten + dedup by title_hash (collision: keep higher crag_score; |delta|<0.5 merge
       fields, prefer structured firecrawl for price/rating).
    3. CRAG-lite score each (relevance + freshness + extractability mean, 0-10).
    4. Partition accept (>=7.5) / downweight (5.0-7.4, with confidence_modifier) / reject (<5.0).
    A lane with zero pages is recorded in lane_failures (the degrade-never provenance)."""
    merge = StormMerge()
    by_hash: Dict[str, PageResult] = {}

    for lane in sorted(lane_pages.keys()):
        pages = lane_pages[lane]
        if not pages:
            merge.lane_failures.append(lane)
            continue
        for page in pages:
            _crag_lite_score(page)  # set page.crag_score in place
            h = page.title_hash()
            existing = by_hash.get(h)
            if existing is None:
                by_hash[h] = page
            else:
                by_hash[h] = _merge_collision(existing, page)

    for page in by_hash.values():
        if page.crag_score >= CRAG_ACCEPT_THRESHOLD:
            page.confidence = 1.0
            merge.accepted.append(page)
        elif page.crag_score >= CRAG_DOWNWEIGHT_FLOOR:
            # The NAMED downweight coefficient (plan C5): map [5.0,7.5] -> [0,1].
            page.confidence = round((page.crag_score - CRAG_DOWNWEIGHT_FLOOR) / CRAG_CONFIDENCE_DIVISOR, 4)
            merge.downweight.append(page)
        else:
            page.confidence = 0.0
            merge.rejected.append(page)
    return merge


def _crag_lite_score(page: PageResult) -> None:
    """CRAG-lite: mean of relevance + freshness + extractability (0-10), set in place (n05 S3.3).

    Offline-deterministic: relevance from snippet/title presence; freshness defaults mid (no
    lastModified offline); extractability from how many structured fields (price/rating/reviews)
    are present. The artifact gives the BANDS only; this is the documented heuristic (n05 caveat)."""
    relevance = 8.0 if (page.title or page.snippet) else 2.0
    if page.url:
        relevance = min(10.0, relevance + 1.0)
    freshness = 6.0  # no lastModified offline -> mid-band (n05 S3.3 freshness default)
    present = sum(1 for v in (page.price, page.rating, page.reviews) if v is not None)
    extractability = 3.0 + present * 2.0  # 3 (none) .. 9 (all three structured fields)
    if page.snippet:
        extractability = min(10.0, extractability + 1.0)
    page.crag_score = round((relevance + freshness + min(10.0, extractability)) / 3.0, 2)


def _merge_collision(a: PageResult, b: PageResult) -> PageResult:
    """Resolve a title_hash collision (n01 S2.3): keep the higher crag_score; if |delta|<0.5,
    merge fields (prefer firecrawl-structured price/rating; fill empties)."""
    hi, lo = (a, b) if a.crag_score >= b.crag_score else (b, a)
    if abs(a.crag_score - b.crag_score) < 0.5:
        # Field merge: fill hi's empties from lo; prefer a 'firecrawl' origin for structured.
        if hi.price is None and lo.price is not None:
            hi.price = lo.price
        if hi.rating is None and lo.rating is not None:
            hi.rating = lo.rating
        if hi.reviews is None and lo.reviews is not None:
            hi.reviews = lo.reviews
        if not hi.snippet and lo.snippet:
            hi.snippet = lo.snippet
        if not hi.marketplace and lo.marketplace:
            hi.marketplace = lo.marketplace
    return hi


# --------------------------------------------------------------------------- #
# CRITIC -- one CEXAgent.build -> verify vs the contract, flag gaps (n01 S2.3 / n05 S3.4).
# --------------------------------------------------------------------------- #
def _critic_step(
    tenant_id: str,
    capability: str,
    nucleus: str,
    kind: str,
    model: str,
    provider: str,
    credential: Credential,
    intent: str,
    plan: Mapping[str, Any],
    merged: StormMerge,
    inputs: Mapping[str, Any],
    options: Mapping[str, Any],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Run the CRITIC build: verify the merged evidence vs the 30-field contract, set the
    validation_score, flag gaps. Returns (critic_fields, meta).

    The CRITIC's frontmatter is the corrected structured view (the producer's self-correction,
    n01 S2.3). DEGRADE-NEVER: a build failure / no frontmatter -> a DERIVED critic from the
    merge alone (confidence_score computed from the usable-source count + structured coverage)."""
    system = _critic_system(plan, merged)
    build_meta = _build_once(
        tenant_id, capability, nucleus, kind, model, provider, credential, intent, system,
    )
    fm = _extract_frontmatter(build_meta.get("artifact", ""))
    critic = _coerce_critic(fm, merged)
    return critic, build_meta


def _critic_system(plan: Mapping[str, Any], merged: StormMerge) -> str:
    """The CRITIC system prompt: verify vs the contract, NEVER fabricate (n05 S3.5)."""
    usable = merged.usable()
    lines = [
        "You are the STORM CRITIC. Verify the research against the product-research contract "
        "(30 fields). Set confidence_score (0-10 = validation_score), price_band_min/max, "
        "price_avg, sweet_spot_price, competitors_count, top_competitor_name, gaps, "
        "opportunities, differentiation_angle, head_terms. EVERY number MUST come from the "
        "evidence below -- if a field has no source, leave it empty and add it to gaps. "
        "mock:false ALWAYS. Do NOT fabricate.",
        "## Evidence (%d usable sources)" % len(usable),
    ]
    for page in usable[:10]:
        lines.append("- %s | price=%s rating=%s reviews=%s origin=%s crag=%.1f" % (
            page.title[:60], page.price, page.rating, page.reviews, page.origin, page.crag_score,
        ))
    return "\n".join(lines)


def _coerce_critic(fm: Mapping[str, Any], merged: StormMerge) -> Dict[str, Any]:
    """Coerce the CRITIC frontmatter into the corrected fields. DEGRADE-NEVER: derive the
    pricing/competitive aggregates from the MERGE when the CRITIC emitted none (so a no-LLM /
    degraded run still computes honest numbers from real evidence -- NEVER fabricated)."""
    derived = _derive_aggregates(merged)
    out: Dict[str, Any] = dict(derived)

    # The CRITIC's frontmatter OVERRIDES the derived aggregates where present (it is the
    # producer's verified view); a missing CRITIC field falls back to the derived aggregate.
    for key in (
        "confidence_score", "price_band_min", "price_band_max", "price_avg", "sweet_spot_price",
        "competitors_count", "top_competitor_name", "top_competitor_rating", "top_competitor_reviews",
    ):
        if key in fm and fm.get(key) is not None:
            out[key] = fm.get(key)
    for key in ("head_terms", "longtails", "synonyms", "gaps", "opportunities",
                "seo_inbound", "seo_outbound", "negative_keywords"):
        vals = _oc._as_str_list(fm.get(key))
        if vals:
            out[key] = vals
    for key in ("differentiation_angle", "recommended_positioning"):
        v = _str_or_empty(fm.get(key))
        if v:
            out[key] = v

    # confidence_score: the CRITIC's value wins; else a derived honest score (n05 S3.4 ->
    # escalate-vs-publish). With zero usable sources the floor is low (degrade-never partial).
    if _oc._as_number(out.get("confidence_score")) is None:
        out["confidence_score"] = _derive_confidence(merged)
    return out


def _derive_aggregates(merged: StormMerge) -> Dict[str, Any]:
    """Compute pricing + competitive aggregates from the MERGE (PURE, from REAL evidence only).
    Returns only fields with actual data (NEVER fabricates a number; an absent metric stays
    absent so the renderer omits it -- n05 S6.3)."""
    usable = merged.usable()
    prices = [p.price for p in usable if isinstance(p.price, (int, float)) and p.price > 0]
    out: Dict[str, Any] = {}
    if prices:
        prices_sorted = sorted(prices)
        out["price_band_min"] = round(min(prices_sorted), 2)
        out["price_band_max"] = round(max(prices_sorted), 2)
        out["price_avg"] = round(sum(prices_sorted) / len(prices_sorted), 2)
        # sweet_spot: the median (a defensible distribution point; CRITIC may override).
        mid = prices_sorted[len(prices_sorted) // 2]
        out["sweet_spot_price"] = round(mid, 2)
    competitors = [p for p in usable if p.reviews is not None or p.rating is not None or p.seller]
    if competitors:
        out["competitors_count"] = len(competitors)
        top = max(competitors, key=lambda p: (p.reviews or 0))
        if top.title or top.seller:
            out["top_competitor_name"] = top.seller or top.title[:60]
        if top.rating is not None:
            out["top_competitor_rating"] = top.rating
        if top.reviews is not None:
            out["top_competitor_reviews"] = top.reviews
    return out


def _derive_confidence(merged: StormMerge) -> float:
    """An honest derived confidence_score when the CRITIC emitted none (degrade-never).

    Scales with the usable-evidence count: 0 sources -> 2.0 (a partial; below the 7.5 gate so
    ready_for_ads is False); grows to ~9.0 with several accepted sources. NEVER a fabricated
    high score on no data (n05 S3.4: honest partial > false completion)."""
    accepted = len(merged.accepted)
    downweight = len(merged.downweight)
    if accepted == 0 and downweight == 0:
        return 2.0
    score = 5.0 + min(4.5, accepted * 1.2 + downweight * 0.4)
    return round(min(9.5, score), 2)


# --------------------------------------------------------------------------- #
# ASSEMBLE -- the 30-field structured result (provenance-tagged, mock:false). n01 S3.1.
# --------------------------------------------------------------------------- #
def _assemble_structured(
    tenant_id: str,
    run_id: str,
    plan: Mapping[str, Any],
    merged: StormMerge,
    critic: Mapping[str, Any],
    inputs: Mapping[str, Any],
    tier_meta: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Assemble the structured result matching PESQUISA_PRODUTO_CONTRACT (n01 S3.1). EVERY datum
    carries provenance (data_sources per-field origin) + mock:false. The CRITIC fields win;
    pricing/competitive fall back to MERGE aggregates; keywords come from the plan/critic.

    tier_meta (OPT-IN tier-router only; EMPTY by default) records per-lane winning_tier +
    tier_failures into the provenance so a tier-routed run is auditable."""
    usable = merged.usable()
    origins = _dedup([p.origin for p in usable if p.origin]) or ["paste"]
    marketplaces = list(plan.get("marketplaces", []))
    failed = list(merged.lane_failures)

    structured: Dict[str, Any] = {
        # Identity / provenance (9).
        "tenant_id": tenant_id,
        "run_id": run_id,
        "product_id": _slug(plan.get("product_name", "")),
        "product_name": _str_or_empty(plan.get("product_name")),
        "run_timestamp": "",            # the persist/edge stamps the real ISO time
        "data_freshness": "",
        "marketplaces_queried": marketplaces,
        "marketplaces_failed": failed,
        "data_sources": _data_sources(critic, merged, origins, tier_meta),
        # Gate (2).
        "confidence_score": _oc._as_number(critic.get("confidence_score")) or 0.0,
        # ready_for_ads is computed by the renderer (compute_ready_for_ads) from the gate fields.
        # Pricing (4).
        "price_band_min": _num_or_absent(critic.get("price_band_min")),
        "price_band_max": _num_or_absent(critic.get("price_band_max")),
        "price_avg": _num_or_absent(critic.get("price_avg")),
        "sweet_spot_price": _num_or_absent(critic.get("sweet_spot_price")),
        # Competitive (8).
        "top_competitor_name": _str_or_empty(critic.get("top_competitor_name")),
        "top_competitor_rating": _num_or_absent(critic.get("top_competitor_rating")),
        "top_competitor_reviews": _num_or_absent(critic.get("top_competitor_reviews")),
        "competitors_count": _num_or_absent(critic.get("competitors_count")) or 0,
        "gaps": _oc._as_str_list(critic.get("gaps")),
        "opportunities": _oc._as_str_list(critic.get("opportunities")),
        "differentiation_angle": _str_or_empty(critic.get("differentiation_angle")),
        "recommended_positioning": _str_or_empty(critic.get("recommended_positioning")),
        # Keywords (6).
        "head_terms": _oc._as_str_list(critic.get("head_terms")) or _oc._as_str_list(plan.get("head_terms")),
        "longtails": _oc._as_str_list(critic.get("longtails")) or _oc._as_str_list(plan.get("longtails")),
        "synonyms": _oc._as_str_list(critic.get("synonyms")) or _oc._as_str_list(plan.get("synonyms")),
        "seo_inbound": _oc._as_str_list(critic.get("seo_inbound")),
        "seo_outbound": _oc._as_str_list(critic.get("seo_outbound")),
        "negative_keywords": _oc._as_str_list(critic.get("negative_keywords")),
        # Filing (1).
        "category_paths": _category_paths(critic, marketplaces),
        # Mandatory anti-hallucination flag (n05 S6.3) -- the engine NEVER ships mock data.
        "mock": False,
        "schema_version": _oc.SCHEMA_VERSION,
    }
    # Drop the absent (None) pricing/competitive fields so the renderer omits them cleanly (a
    # missing metric must NOT render as a fabricated 0; n05 S6.3).
    return {k: v for k, v in structured.items() if v is not None}


def _stamp_artifact_identity(
    structured: Dict[str, Any],
    run_id: str,
    kind: str,
    pillar: str,
    plan: Mapping[str, Any],
) -> None:
    """Stamp the H01/H03 frontmatter identity onto the structured result IN PLACE (the universal
    F7 gates: H01 requires id+kind+title; H03 requires a description >=10 chars).

    These are METADATA about the artifact, not marketplace claims -- so deriving them from the
    product name + run_id is honest (no data is fabricated). All values are ASCII-safe (the
    product name is ascii-folded for the id; the title/description keep the raw product label
    which the safe-YAML dump renders ASCII-only anyway). Idempotent: never overwrites a value the
    CRITIC already set."""
    product = _str_or_empty(structured.get("product_name")) or _str_or_empty(plan.get("product_name"))
    slug = _slug(product) or "produto"
    short_run = (run_id or "").replace("-", "")[:8]

    if not _str_or_empty(structured.get("id")):
        structured["id"] = ("pp_%s_%s" % (slug, short_run)).strip("_") if short_run else "pp_%s" % slug
    if not _str_or_empty(structured.get("kind")):
        structured["kind"] = str(kind or RESEARCH_KIND)
    if not _str_or_empty(structured.get("pillar")):
        structured["pillar"] = str(pillar or "P01")
    if not _str_or_empty(structured.get("title")):
        label = product or "Produto"
        structured["title"] = "Pesquisa de Produto: %s" % label
    if len(_str_or_empty(structured.get("description"))) < 10:
        label = product or "produto"
        # A descriptive sentence about WHAT this artifact is (>=10 chars guaranteed by the
        # fixed prefix); never asserts a price/competitor number.
        structured["description"] = (
            "Pesquisa de mercado para %s: faixa de preco, concorrentes e palavras-chave "
            "para anuncio." % label
        )


def _data_sources(
    critic: Mapping[str, Any], merged: StormMerge, origins: List[str],
    tier_meta: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """The per-field provenance log (n01 S3.1 data_sources / n05 S2.4). Records which lane each
    metric came from -- or 'paste' (the floor) when no usable source produced it. mock:false.

    When the OPT-IN tier-router routed any marketplace lane, the per-lane {winning_tier,
    tier_failures} is recorded under '_tier_router' (absent/empty by default -> byte-preserving)."""
    usable = merged.usable()
    price_origin = next((p.origin for p in usable if p.price is not None), None)
    comp_origin = next((p.origin for p in usable if p.reviews is not None or p.rating is not None), None)
    floor = "paste"
    out: Dict[str, Any] = {
        "price": price_origin or floor,
        "competitors": comp_origin or floor,
        "keywords": "llm_plan",                 # head/longtails are LLM-derived (n01 S3.1)
        "confidence_score": "critic",
        "_origins": origins,
        "_lane_failures": list(merged.lane_failures),
        "mock": False,
    }
    if isinstance(tier_meta, Mapping) and tier_meta:
        out["_tier_router"] = {str(k): v for k, v in tier_meta.items()}
    return out


def _category_paths(critic: Mapping[str, Any], marketplaces: List[str]) -> Dict[str, Any]:
    """The per-marketplace category map (n01 S3.1 category_paths). From the CRITIC if present,
    else an empty per-marketplace skeleton (never fabricated)."""
    cp = critic.get("category_paths")
    if isinstance(cp, Mapping) and cp:
        return {str(k): v for k, v in cp.items()}
    return {m: "" for m in marketplaces}


# --------------------------------------------------------------------------- #
# The ONE LLM-build seam (PLAN + CRITIC each call this) -- REUSE the spine's credential scope.
# --------------------------------------------------------------------------- #
def _build_once(
    tenant_id: str,
    capability: str,
    nucleus: str,
    kind: str,
    model: str,
    provider: str,
    credential: Credential,
    intent: str,
    system: str,
) -> Dict[str, Any]:
    """Run ONE CEXAgent.build under the spine's _ProviderKeyScope (REUSE verbatim). Returns a
    meta dict (artifact / passed / score / model_used / errors). NEVER raises on a build error
    (it is recorded -> the caller degrades). The CEXAgent seam is the SAME module-level name
    the spine + the W1 tests fake (cex_run_capability.CEXAgent)."""
    agent_cls = _rc.CEXAgent if _rc.CEXAgent is not None else _rc._import_cex_agent()
    meta: Dict[str, Any] = {"artifact": "", "passed": False, "score": 0.0, "model_used": model, "errors": []}
    try:
        with _rc._ProviderKeyScope(credential, provider):
            agent = agent_cls(nucleus=nucleus.lower(), kind=kind, model=model)
            build = _call_build(agent, intent, system)
        meta["artifact"] = str(getattr(build, "artifact", "") or "")
        meta["passed"] = bool(getattr(build, "passed", False))
        meta["score"] = float(getattr(build, "score", 0.0) or 0.0)
        meta["model_used"] = str(getattr(agent, "model", model) or model)
        meta["errors"] = list(getattr(build, "errors", []) or [])
    except CapabilityRefused:
        raise  # a credential/deny refusal must propagate (fail-closed).
    except Exception as exc:  # a build error degrades (we still PLAN/CRITIC-derive offline).
        meta["errors"].append("build_error: %s: %s" % (type(exc).__name__, exc))
    return meta


def _call_build(agent: Any, intent: str, system: str) -> Any:
    """Call agent.build, passing system= when the seam accepts it (the multi-step loop passes
    system=; the W1 FakeAgent.build accepts **kwargs). Falls back to build(intent) for a seam
    that does not take system (the single-step capability FakeAgent)."""
    try:
        return agent.build(intent, system=system)
    except TypeError:
        return agent.build(intent)


# --------------------------------------------------------------------------- #
# PERSIST -- best-effort-after-pass; tenant_id EXPLICIT; degrade-never.
# --------------------------------------------------------------------------- #
def _persist(
    db: Optional[DbWriter],
    result: ResearchRunResult,
    merged: StormMerge,
    rendered: Mapping[str, str],
    tier_meta: Optional[Mapping[str, Any]] = None,
) -> None:
    """Persist the canonical research MD via the injected DbWriter (tenant_id EXPLICIT). The
    HTML + structured fields ride in meta. DEGRADE-NEVER: db=None -> persisted=False; a DB
    failure is surfaced (an error appended) but never discards the artifact (n03 S5.6 / the
    spine's best-effort-after-pass rule). Only persist a well-formed (passed) result."""
    if db is None or not result.passed:
        return
    meta: Dict[str, Any] = {
        "table": _TENANT_DATA_TABLE,
        "capability": result.capability,
        "pillar": result.pillar,
        "nucleus": result.nucleus,
        "score": result.score,
        "model_used": result.model_used,
        "html": rendered.get("html", ""),
        "structured": _oc._yaml_safe_value(dict(result.structured)),
        "ready_for_ads": result.ready_for_ads,
        "sources_accepted": len(merged.accepted),
        "sources_downweight": len(merged.downweight),
        "lane_failures": list(merged.lane_failures),
    }
    # OPT-IN tier-router audit (absent by default -> byte-preserving meta for existing callers).
    if isinstance(tier_meta, Mapping) and tier_meta:
        meta["tier_router"] = _oc._yaml_safe_value({str(k): v for k, v in tier_meta.items()})
    try:
        rid = db.persist_artifact(result.tenant_id, result.capability, result.kind, result.artifact, meta)
        result.record_id = str(rid) if rid is not None else None
        result.persisted = result.record_id is not None
    except Exception as exc:  # surface, never discard.
        result.persisted = False
        result.errors.append("persist_failed: %s: %s" % (type(exc).__name__, exc))


# --------------------------------------------------------------------------- #
# Budget / fan-out cap (REUSE cex_agent_loop's _Budget / _resolve_budget).
# --------------------------------------------------------------------------- #
def _guard_budget(tenant_id: str, capability: str, options: Mapping[str, Any]) -> None:
    """Refuse a non-positive declared budget BEFORE any LLM call (OQ4). A bare options[
    'max_steps']<=0 or a budget mapping whose max_steps/steps is <=0 -> budget_exceeded.
    Mirrors cex_agent_loop / Phase B's guard intent without importing the private helper name
    (which expects an agent_id resolution path); this is the research-engine analog."""
    declared: Any = None
    budget = options.get("budget")
    if isinstance(budget, Mapping):
        declared = budget.get("max_steps", budget.get("steps"))
    elif "max_steps" in options:
        declared = options.get("max_steps")
    if declared is None:
        return
    if isinstance(declared, bool) or not isinstance(declared, (int, float)) or declared <= 0:
        raise CapabilityRefused(
            "budget_exceeded", tenant_id=tenant_id, capability=capability,
            detail="declared budget max_steps=%r is non-positive (refused before any build)" % declared,
        )


def _fanout_cap(budget: "_al._Budget") -> int:
    """The fan-out cap = the budget step ceiling (n03 S1.6). The OQ4 budget tightens the default
    backstop; the cap is at least 1 (a single lane always runs)."""
    ceiling = budget.step_ceiling()
    return max(1, min(ceiling, _DEFAULT_FANOUT_CAP) if budget.max_steps is None else ceiling)


def _resolve_lanes(options: Mapping[str, Any], cap: int) -> List[str]:
    """The source lanes to fan out over (operator override via options['source_lanes']; default
    DEFAULT_SOURCE_LANES). Capped at the fan-out cap (n03 S1.6)."""
    declared = options.get("source_lanes") if isinstance(options, Mapping) else None
    lanes = [str(x).strip() for x in declared if str(x).strip()] if isinstance(declared, (list, tuple)) else list(DEFAULT_SOURCE_LANES)
    return (lanes or list(DEFAULT_SOURCE_LANES))[: max(1, cap)]


# --------------------------------------------------------------------------- #
# Small helpers (PURE + TOTAL).
# --------------------------------------------------------------------------- #
def _import_parallel() -> Optional[Dict[str, Any]]:
    """Import cex_sdk.workflow.Parallel + Step + StepInput/StepOutput, or None (degrade-never)."""
    try:
        from cex_sdk.workflow import Parallel, Step, StepInput, StepOutput  # type: ignore[import]

        return {"Parallel": Parallel, "Step": Step, "StepInput": StepInput, "StepOutput": StepOutput}
    except Exception:
        return None


def _use_tier_router(options: Mapping[str, Any]) -> bool:
    """OPT-IN: the tier-router marketplace-lane path is active iff options['use_tier_router'] is
    True OR env CEX_USE_TIER_ROUTER=1 (mirrors the use_storm opt-in). Default/absent -> False ->
    the existing single tool_resolver fetch per lane (byte-preserving)."""
    if isinstance(options, Mapping) and options.get("use_tier_router") is True:
        return True
    return os.environ.get(USE_TIER_ROUTER_ENV, "").strip() in ("1", "true", "True", "yes")


def _import_tier_router() -> Optional[Any]:
    """Import cex_marketplace_tier_router (a READ-ONLY stable dep), or None (degrade-never -> the
    lane returns [] and the merge degrades to the floor). No browser/network/key touched at import."""
    try:
        import cex_marketplace_tier_router  # type: ignore[import]

        return cex_marketplace_tier_router
    except Exception:
        return None


def _maybe_enrich_multiperspective(
    plan: Dict[str, Any], options: Mapping[str, Any],
) -> Dict[str, Any]:
    """OPT-IN Co-STORM enrichment of the PLAN angles (W3). DEFAULT OFF -> returns `plan` unchanged
    (byte-identical). When env CEX_STORM_MULTIPERSPECTIVE=1 OR options['use_multiperspective'] is
    True, extends plan['angles'] (additively) with multi-perspective sub-questions via the SEPARATE
    cex_storm_upgrades module.

    The module is imported LAZILY here so the default path's import surface is unchanged. TOTAL +
    DEGRADE-NEVER: a missing/erroring helper module -> the original plan is returned (the run never
    breaks because an opt-in enrichment failed). NEVER fabricates marketplace data (it only adds
    research QUESTIONS to the angles)."""
    try:
        import cex_storm_upgrades as _su  # type: ignore[import]
    except Exception:
        return plan
    try:
        if not _su.multiperspective_enabled(options):
            return plan
        return _su.enrich_plan_with_multiperspective(plan, options)
    except Exception:
        return plan


def _strip_intermediate_identity_gates(errors: Any) -> List[str]:
    """Drop H01/H03 identity-gate errors from an INTERMEDIATE plan/critic build (n07 F7).

    H01 (id+kind+title present) + H03 (description >=10) are stamped ONLY on the FINAL assembled
    artifact (_stamp_artifact_identity). The PLAN/CRITIC frontmatters legitimately carry no
    id/title/description (they hold plan/critic keys), so their CEXAgent.build emits SPURIOUS
    H01/H03 errors. Filter them so only the final artifact surfaces those gates. TOTAL: a
    non-list / None -> []. Any non-H01/H03 build error is PRESERVED (still honestly surfaced)."""
    if not isinstance(errors, (list, tuple)):
        return []
    out: List[str] = []
    for e in errors:
        s = str(e)
        if s.startswith("H01") or s.startswith("H03"):
            continue
        out.append(s)
    return out


def _agent_run_id(tenant_id: str, run_key: str) -> str:
    """The deterministic run_id (matches cex_runtime_sync.agent_run_id when present)."""
    try:
        import cex_runtime_sync  # type: ignore[import]

        return cex_runtime_sync.agent_run_id(tenant_id, run_key)
    except Exception:
        ns = uuid.UUID("a4f3c2d1-0000-5000-8000-6167656e7472")
        return str(uuid.uuid5(ns, "%s|%s" % (tenant_id, run_key)))


def _derive_intent(inputs: Mapping[str, Any]) -> str:
    """The research intent: the explicit 'intent', else the product name / a joined inputs view."""
    intent = inputs.get("intent")
    if isinstance(intent, str) and intent.strip():
        return intent.strip()
    product = _product_name(inputs)
    if product:
        return "Pesquisa de produto: %s" % product
    return " ".join("%s=%s" % (k, v) for k, v in inputs.items() if str(k).lower() != "intent")


def _product_name(inputs: Mapping[str, Any]) -> str:
    for key in ("product_name", "nome_produto", "produto", "produto_ou_categoria"):
        v = inputs.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def _primary_query(plan: Mapping[str, Any]) -> str:
    head = _oc._as_str_list(plan.get("head_terms"))
    if head:
        return head[0]
    return _ascii_lower(_str_or_empty(plan.get("product_name")))


def _trace(plan_meta: Mapping[str, Any], merged: StormMerge, critic_meta: Mapping[str, Any]) -> str:
    return "PLAN:passed=%s || FANOUT:accepted=%d,downweight=%d,failed=%d || CRITIC:passed=%s" % (
        bool(plan_meta.get("passed")), len(merged.accepted), len(merged.downweight),
        len(merged.lane_failures), bool(critic_meta.get("passed")),
    )


def _structured_well_formed(structured: Mapping[str, Any]) -> bool:
    """The F7 gate analog: the structured result carries the contract's identity + a numeric
    confidence_score + a keyword seed. A degrade-never partial with no sources still passes IF
    it is well-formed (the honest-partial posture); ready_for_ads is the separate downstream gate."""
    if not _str_or_empty(structured.get("product_name")):
        return False
    if _oc._as_number(structured.get("confidence_score")) is None:
        return False
    return bool(_oc._as_str_list(structured.get("head_terms")))


def _extract_frontmatter(artifact: str) -> Dict[str, Any]:
    """Extract YAML frontmatter from an artifact (DEGRADE-NEVER -> {})."""
    if not isinstance(artifact, str) or not artifact:
        return {}
    m = _FRONTMATTER_RE.match(artifact)
    if not m:
        return {}
    try:
        import yaml
        data = yaml.safe_load(m.group(1))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _try_json(value: Any) -> Any:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        import json
        return json.loads(value)
    except Exception:
        return None


def _str_or_empty(value: Any) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else ""


def _as_int(value: Any) -> Optional[int]:
    n = _oc._as_number(value)
    return int(n) if n is not None else None


def _num_or_absent(value: Any) -> Optional[float]:
    """A number, or None (so ASSEMBLE drops it -> the renderer omits a missing metric)."""
    return _oc._as_number(value)


def _first_line(text: str) -> str:
    return (text or "").strip().splitlines()[0].strip() if (text or "").strip() else ""


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", _ascii_lower(text)).strip("-")
    return s


def _ascii_lower(text: str) -> str:
    return str(text or "").encode("ascii", "ignore").decode("ascii").lower().strip()


def _dedup(items: List[str]) -> List[str]:
    seen: set = set()
    out: List[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


__all__ = [
    "run_research",
    "merge_storm_branches",
    "ResearchRunResult",
    "PageResult",
    "StormMerge",
    "Credential",
    "CapabilityResult",
    "CapabilityRefused",
    "DbWriter",
    "DEFAULT_RESEARCH_CAPABILITY",
    "DEFAULT_SOURCE_LANES",
    "MARKETPLACE_LANES",
    "TIER_ROUTER_LANE_MARKETPLACE",
    "USE_TIER_ROUTER_ENV",
    "RESEARCH_KIND",
    "CRAG_ACCEPT_THRESHOLD",
    "CRAG_DOWNWEIGHT_FLOOR",
    "CRAG_CONFIDENCE_DIVISOR",
    "MODE_BYO_API_KEY",
    "MODE_NATIVE_LOCAL",
    "MODE_PLATFORM",
]

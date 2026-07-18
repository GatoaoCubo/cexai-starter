#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI capability pipeline -- cex_run_pipeline (mission CAPABILITY_LAYER, Wave 1).

THE sequential research -> ads driver: the flagship "Cole um produto -> anuncio" chain,
single-step (NO STORM fan-out yet -- that is Wave 2). It COMPOSES the shipped spine
(cex_run_capability.run_capability -> CEXAgent.build -> the persist seam); it does NOT fork
it (the #1 rule). The chain is what sells (plan S7.1); single-step research is enough to
prove the wow moment end to end (plan C1: W1 merges N06's "Research+Ads chained" with N01's
engine on a single-step research run).

THE FLOW (plan S9 + n02 S3 chaining map):
  1. RUN RESEARCH   run_capability(tenant, capability=research_capability, intent, cred,
                    db=None) -- the spine builds + scores the research artifact through the
                    EXISTING F1..F8 path. db=None so the SPINE does not persist (this driver
                    owns the richer dual-output persist below); the deny/credential/budget
                    seam is REUSED verbatim (a refusal propagates).
  2. STRUCTURE      extract the structured result from the research artifact frontmatter
                    (yaml.safe_load) -- the producer's frontmatter IS the 30-field contract
                    (n01 S3). A research gate FAIL (passed=False) short-circuits: no ads.
  3. RENDER         cex_output_contract.render(structured, contract) -> {"md", "html"} (the
                    dual emitter; MD canonical, HTML derivative).
  4. PERSIST RESEARCH  the injected DbWriter.persist_artifact(tenant, capability, kind=
                    pesquisa_produto, artifact=md, meta={html, structured, capability set}).
                    tenant_id EXPLICIT; best-effort-after-pass; degrade-never (no DB ->
                    LocalOnly -> persisted=False, NEVER blocks the chain).
  5. GATE           if NOT ready_for_ads (plan S3.1 gate) -> STOP after research (the
                    dashboard shows "Pesquisa incompleta"; ads is blocked). No fabrication.
  6. ADAPT          build_anuncio_open_vars(structured) -> the STABLE ads-input shape (plan
                    C3: usps := merge(opportunities, differentiation_angle); competitor_gaps
                    := gaps; social_insights := {} when no lead_b2c). The ads capability
                    reads THIS, never the raw vertical fields.
  7. FEED ADS       run_capability(tenant, capability=ads_capability, intent=<ads intent
                    carrying the open_vars>, cred, db=None) -- single-step ads build.
  8. PERSIST ADS    persist the ads result (kind from the build, capability=ads) the SAME
                    way. The handoff rides an IN-MEMORY dict (the session_state bus analog);
                    NO file IO, NO new tables -- ads lands in tenant_data exactly like
                    research, discriminated by ``capability``/``kind`` (n03 S5.4).

REUSE (do NOT fork the rails): this module imports run_capability's spine VERBATIM and
reuses Credential / CapabilityRefused / DbWriter and the run_capability entry (which itself
owns _select_credential / _ProviderKeyScope / the enabled+frozen guards). The ONLY new logic
here is the CHAINING (research -> adapter -> ads) + the dual-output persist; everything
tenant/credential/deny-shaped is the shipped seam.

HARD RULES (task contract + .claude/rules/ascii-code-rule.md):
  * ASCII-only; fully type-hinted; FAIL-CLOSED (a deny from the spine propagates).
  * tenant_id is ALWAYS an explicit argument; never inferred from ambient global state.
  * NO concrete DB driver / NO LLM key imported at MODULE IMPORT (run_capability is
    import-light; cex_output_contract is pure). The DbWriter + Credential are INJECTED.
  * DEGRADE-NEVER: no DbWriter -> the chain still runs + returns, just persisted=False.

Spec: plan_capability_layer_FINAL_2026-06-18.md (S9 Wave-1 concrete spec, S3 contract, S4
chaining, C3 adapter). Composes: _tools/cex_run_capability.py (the spine, verbatim) +
_tools/cex_output_contract.py (the dual renderer). Persist seam: cex_runtime_sync
.RuntimeSyncWriter.persist_artifact (or any DbWriter), via tenant_data (NO new tables).
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

# --------------------------------------------------------------------------- #
# REUSE the run_capability spine VERBATIM (the #1 rule: do NOT fork the rails).
# cex_run_capability is import-light (no driver/key at load). We pull the SAME
# Credential / CapabilityResult / CapabilityRefused / DbWriter + the run_capability
# entry, so the tenant/credential/persist rails are SHARED, never re-implemented.
# --------------------------------------------------------------------------- #
_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

import cex_run_capability as _rc  # type: ignore[import]
import cex_output_contract as _oc  # type: ignore[import]
from cex_shared import parse_frontmatter as _parse_frontmatter  # type: ignore[import]

# Wave 2: the STORM research engine. Imported LAZILY at call time (kept import-light here so a
# degraded env that lacks it still runs the W1 single-step path). See _run_research_stage.

# Re-export the SAME contract types so callers construct ONE set of objects regardless of
# which entry (run_capability / run_agent / run_pipeline) they call. NOT new types.
Credential = _rc.Credential
CapabilityResult = _rc.CapabilityResult
CapabilityRefused = _rc.CapabilityRefused
DbWriter = _rc.DbWriter
MODE_BYO_API_KEY = _rc.MODE_BYO_API_KEY
MODE_NATIVE_LOCAL = _rc.MODE_NATIVE_LOCAL
MODE_PLATFORM = _rc.MODE_PLATFORM
_TENANT_DATA_TABLE = _rc._TENANT_DATA_TABLE

# The Wave-1 vertical + its downstream ads capability (plan S9). The research kind is the
# tenant_data discriminator (n01 S1 "Tenant DB Wiring"); ads resolves through the registry.
DEFAULT_RESEARCH_CAPABILITY = "pesquisa_produto"
DEFAULT_ADS_CAPABILITY = "ads"
# The persisted kind for the research artifact (plan S9: payload.kind = pesquisa_produto).
RESEARCH_KIND = "pesquisa_produto"

# Wave 2 toggles (plan S7.2): the STORM engine is used for the research stage when available
# AND opted-in; the W1 single-step path stays the default + the degrade fallback. The image
# stage runs ONLY when a generator is bound (founder-gated; otherwise skipped cleanly).
#   options['use_storm']      -- opt-in (True): use cex_run_research.run_research for research
#                                (the W2 fan-out depth). Default/absent -> W1 single-step (the
#                                proven path; W1 behavior byte-preserved). Falls back to single-
#                                step when the STORM engine is not importable (degrade-never).
#   options['image_generator']-- a bound generator callable -> run the 2x2 image stage after ads.
#   options['image_prompt']   -- the product/scene prompt for the image stage (else derived).

# --------------------------------------------------------------------------- #
# Typed handoff dataclasses (plan S4.1; modeled on entity_memory_pesquisa_handoff).
# In Wave 1 the handoff rides an in-memory dict; these dataclasses give it a typed shape
# so the chain is self-documenting + the ads stage reads a stable contract.
# --------------------------------------------------------------------------- #
@dataclass
class ResearchHandoff:
    """research -> ads handoff (plan S4.1; the open_vars adapter shape, plan C3)."""

    head_terms: List[str] = field(default_factory=list)
    longtails: List[str] = field(default_factory=list)
    sweet_spot_price: Optional[float] = None
    differentiation_angle: Optional[str] = None
    gaps: List[str] = field(default_factory=list)
    usps: List[str] = field(default_factory=list)
    competitor_gaps: List[str] = field(default_factory=list)
    social_insights: Dict[str, Any] = field(default_factory=dict)
    ready_for_ads: bool = False

    @classmethod
    def from_structured(cls, structured: Mapping[str, Any]) -> "ResearchHandoff":
        """Build the handoff from the research structured result via the C3 adapter."""
        ov = _oc.build_anuncio_open_vars(structured)
        return cls(
            head_terms=list(ov.get("head_terms") or []),
            longtails=list(ov.get("longtails") or []),
            sweet_spot_price=ov.get("sweet_spot_price"),
            differentiation_angle=_str_or_none(structured.get("differentiation_angle")),
            gaps=_str_list(structured.get("gaps")),
            usps=list(ov.get("usps") or []),
            competitor_gaps=list(ov.get("competitor_gaps") or []),
            social_insights=dict(ov.get("social_insights") or {}),
            ready_for_ads=_oc.compute_ready_for_ads(structured),
        )

    def to_open_vars(self) -> Dict[str, Any]:
        """The stable ads-input block (anuncio_open_vars) the ads capability reads."""
        return {
            "usps": list(self.usps),
            "competitor_gaps": list(self.competitor_gaps),
            "social_insights": dict(self.social_insights),
            "head_terms": list(self.head_terms),
            "longtails": list(self.longtails),
            "sweet_spot_price": self.sweet_spot_price,
            "differentiation_angle": self.differentiation_angle,
        }


@dataclass
class PipelineResult:
    """Outcome of one research -> ads pipeline run. NO api_key is ever present here.

    Carries the two stage results (research + optional ads) + the chain-level status so the
    dashboard can render a single coherent "Lanca Produto" view. ``ads`` is None when the
    research gate (ready_for_ads) blocked the ads stage (plan S3.1).
    """

    tenant_id: str
    research_capability: str
    ads_capability: str
    status: str = "error"                  # research_only | completed | error
    ready_for_ads: bool = False
    research: Optional[CapabilityResult] = None
    ads: Optional[CapabilityResult] = None
    research_record_id: Optional[str] = None
    ads_record_id: Optional[str] = None
    research_md: str = ""                   # the canonical research MD (frontmatter+body)
    research_html: str = ""                 # the derivative research HTML report
    open_vars: Dict[str, Any] = field(default_factory=dict)  # the C3 ads-input adapter
    research_engine: str = "single_step"    # single_step (W1 spine) | storm (W2 fan-out engine)
    image_tiles: List[str] = field(default_factory=list)     # the 4 2x2 image tile paths (W2)
    errors: List[str] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# THE entry.
# --------------------------------------------------------------------------- #
def run_pipeline(
    tenant_id: str,
    intent: str,
    credential: Credential,
    *,
    db: Optional[DbWriter] = None,
    research_capability: str = DEFAULT_RESEARCH_CAPABILITY,
    ads_capability: str = DEFAULT_ADS_CAPABILITY,
    contract: Optional[Mapping[str, Any]] = None,
    options: Optional[Mapping[str, Any]] = None,
) -> PipelineResult:
    """Run the research -> ads chain for ONE tenant (the flagship pipeline). See module docstring.

    FAIL-CLOSED: a deny from the spine (missing tenant / disabled capability / native_local /
    missing credential) PROPAGATES as CapabilityRefused -- the chain never silently produces
    an empty result. PERSIST is best-effort-after-pass; a DB failure is surfaced (persisted=
    False + an error) but never discards a produced artifact. DEGRADE-NEVER: db=None (no data
    plane) -> the chain still runs, persisted=False. The api_key is never echoed/logged/persisted.
    """
    tid = (tenant_id or "").strip()
    if not tid:
        # Mirror the spine deny seam exactly (fail-closed before any build).
        raise CapabilityRefused("missing_tenant", capability=research_capability)

    used_contract: Mapping[str, Any] = contract if isinstance(contract, Mapping) else _oc.PESQUISA_PRODUTO_CONTRACT
    result = PipelineResult(
        tenant_id=tid,
        research_capability=research_capability,
        ads_capability=ads_capability,
    )

    # -- STAGE 1+2: RUN RESEARCH + STRUCTURE ------------------------------------------- #
    # W2: route through the STORM engine when available + enabled; else the W1 single-step
    # spine (the degrade fallback). BOTH return a CapabilityResult-shaped research_res + the
    # structured 30-field result; the rest of the chain is identical. Reuse db=None so THIS
    # driver owns the dual-output persist.
    research_res, storm_structured, engine = _run_research_stage(
        tid, research_capability, intent, credential, options=options,
    )
    result.research = research_res
    result.research_engine = engine

    if not research_res.passed:
        # The research gate failed; surface, do not proceed to ads (no fabrication downstream).
        result.status = "research_only"
        result.ready_for_ads = False
        result.errors.append("research_gate_failed: score=%.2f" % research_res.score)
        # Still render + persist the (failed) research so the employee sees WHY it failed.
        structured = storm_structured if storm_structured else _extract_structured(research_res.artifact)
        _render_and_persist_research(result, structured, used_contract, db, research_res)
        return result

    # The STORM engine already returns the structured 30-field result; the single-step path
    # extracts it from the producer's frontmatter (n01 S3 -- the frontmatter IS the contract).
    structured = storm_structured if storm_structured else _extract_structured(research_res.artifact)

    # -- STAGE 3+4: RENDER + PERSIST RESEARCH (dual output, capability set) ------------- #
    handoff = ResearchHandoff.from_structured(structured)
    result.ready_for_ads = handoff.ready_for_ads
    result.open_vars = handoff.to_open_vars()
    _render_and_persist_research(result, structured, used_contract, db, research_res)

    # -- STAGE 5: GATE ----------------------------------------------------------------- #
    if not handoff.ready_for_ads:
        # Pesquisa incompleta -> block ads (plan S3.1). Research persisted; chain stops here.
        result.status = "research_only"
        return result

    # -- STAGE 6+7: ADAPT (open_vars) + FEED ADS (single-step) -------------------------- #
    ads_intent = _compose_ads_intent(intent, handoff)
    # Stamp the INNER flag (entry-point-agnostic, mirroring research_opts) so the ads sub-call
    # uses the spine's GENERIC ads build, NOT the standalone ``ads`` structured generator -- the
    # pipeline owns its ads output + persist. Internal-only (stripped before generator inputs).
    ads_opts: Dict[str, Any] = dict(options) if isinstance(options, Mapping) else {}
    ads_opts[_rc._PESQUISA_PRODUTO_INNER_FLAG] = True
    try:
        ads_res = _rc.run_capability(
            tid, ads_capability, ads_intent, credential, db=None, options=ads_opts,
        )
    except CapabilityRefused as exc:
        # The ads capability may be disabled / unresolved for this tenant; surface but keep
        # the (successful, persisted) research. The chain degrades to research_only.
        result.status = "research_only"
        result.errors.append("ads_refused: %s" % exc.reason)
        return result
    result.ads = ads_res

    # -- STAGE 8: PERSIST ADS ---------------------------------------------------------- #
    if ads_res.passed:
        ads_meta: Dict[str, Any] = {
            "table": _TENANT_DATA_TABLE,
            "capability": ads_capability,
            "pillar": ads_res.pillar,
            "nucleus": ads_res.nucleus,
            "score": ads_res.score,
            "model_used": ads_res.model_used,
            "from_research_run": research_res.record_id,
            "open_vars": handoff.to_open_vars(),
        }
        rid = _persist(db, tid, ads_capability, ads_res.kind, ads_res.artifact, ads_meta, result)
        result.ads_record_id = rid

    # -- STAGE 9 (W2, OPTIONAL): the 2x2 image stage -- ONLY if a generator is bound. -- #
    # Founder-gated: runs the 2x2 generate-then-crop ONLY when options['image_generator'] is a
    # bound callable; otherwise SKIPPED cleanly (no crash, no fabricated image). A failure in
    # the image stage is surfaced but never fails the (completed) research+ads chain.
    _run_image_stage(result, options, handoff)

    result.status = "completed"
    return result


# --------------------------------------------------------------------------- #
# STAGE 1+2 research router: STORM engine when available + enabled, else single-step (W1).
# --------------------------------------------------------------------------- #
def _run_research_stage(
    tenant_id: str,
    research_capability: str,
    intent: str,
    credential: Credential,
    *,
    options: Optional[Mapping[str, Any]],
) -> "tuple[CapabilityResult, Dict[str, Any], str]":
    """Run the research stage and return (research_res, structured, engine).

    USES the STORM engine (cex_run_research.run_research) when it is importable AND ENABLED
    (options['use_storm'] is True) -- the W2 fan-out/merge/critic depth. FALLS BACK to the W1
    single-step spine (run_capability) when STORM is unavailable OR not enabled (the degrade
    fallback + the default). BOTH paths:
      * run with db=None (THIS driver owns the dual-output persist);
      * REUSE the spine's deny/credential/budget seam verbatim (a refusal propagates);
      * return a CapabilityResult-shaped result so the chain is engine-agnostic downstream.

    The STORM path additionally returns its 30-field structured result directly (no re-parse);
    the single-step path returns {} so the caller parses the producer's frontmatter (n01 S3).

    WHY opt-in (not default-on): STORM runs a real multi-turn loop (PLAN + N parallel lanes +
    MERGE + CRITIC), so it issues TWO builds (PLAN + CRITIC) and derives the gate from REAL
    merged evidence -- a deliberately DIFFERENT behavior + cost profile from the W1 single-step
    path (ONE build, the producer's own gate). The dashboard wiring opts in with
    options['use_storm']=True for the depth; the default stays single-step so the proven W1
    behavior (and its tests) is byte-preserved (n03 S6.3 W2 "upgrade research to fan-out").
    """
    use_storm = bool(isinstance(options, Mapping) and options.get("use_storm") is True)

    # Re-entrancy guard (dashboard roadmap W2): when the research capability resolves to kind
    # pesquisa_produto (the flagship), run_capability ROUTES it back into THIS pipeline. The
    # research-stage builds (the single-step spine call here AND the STORM PLAN/CRITIC builds inside
    # run_research) all go through run_capability with that SAME capability, so without a guard they
    # would re-fire the route -> infinite recursion. Stamp the spine's inner-flag into the options
    # both paths receive so any run_capability(kind=pesquisa_produto) reached during the research
    # stage does a PLAIN build instead of re-entering run_pipeline. Idempotent + additive (the flag
    # is internal-only; it never reaches the enabled-capability deny gate). This makes the guard
    # entry-point-agnostic -- a DIRECT run_pipeline(...) call is protected exactly like a routed one.
    research_opts: Dict[str, Any] = dict(options) if isinstance(options, Mapping) else {}
    research_opts[_rc._PESQUISA_PRODUTO_INNER_FLAG] = True

    storm = _import_storm() if use_storm else None
    if storm is not None:
        # The STORM engine: run_research is run_agent_multistep-shaped (tenant, agent_id,
        # inputs, credential, ...). Feed the product via inputs['intent']; reuse options (the
        # enabled-gate + the budget + the source_lanes pass straight through). The guarded options
        # ensure the PLAN/CRITIC builds inside run_research never re-fire the flagship route.
        run = storm.run_research(
            tenant_id, research_capability, {"intent": intent}, credential,
            db=None, options=research_opts,
        )
        # LIFT the ResearchRunResult into a CapabilityResult so the chain is engine-agnostic.
        research_res = CapabilityResult(
            tenant_id=run.tenant_id, capability=run.capability, kind=run.kind,
            pillar=run.pillar, nucleus=run.nucleus, artifact=run.artifact, score=run.score,
            passed=run.passed, status="produced" if run.passed else "produced_unpersisted",
            model_used=run.model_used, trace=run.trace, errors=list(run.errors),
        )
        return research_res, dict(run.structured), "storm"

    # DEGRADE FALLBACK: the W1 single-step spine (verbatim, with the re-entrancy guard).
    research_res = _rc.run_capability(
        tenant_id, research_capability, intent, credential, db=None, options=research_opts,
    )
    return research_res, {}, "single_step"


def _import_storm() -> Any:
    """Import the STORM engine (cex_run_research), or None (degrade-never -> single-step)."""
    try:
        import cex_run_research  # type: ignore[import]

        return cex_run_research
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# STAGE 9 image router (W2, OPTIONAL): the 2x2 generate-then-crop, founder-gated.
# --------------------------------------------------------------------------- #
def _run_image_stage(
    result: PipelineResult,
    options: Optional[Mapping[str, Any]],
    handoff: "ResearchHandoff",
) -> None:
    """Run the 2x2 image stage ONLY if a generator is bound (options['image_generator']).

    GUARDED + DEGRADE-NEVER: no generator bound -> skip cleanly (the common case -- no image MCP
    is wired today, n05 S5.1). A generator bound -> generate ONE 2x2 + crop into 4 tiles
    (cex_image_grid.generate_and_crop); the 4 tile paths land on result.image_tiles. An image
    failure is surfaced (an error appended) but NEVER fails the completed research+ads chain
    (the image stage is Phase-2 / cost-lever, not the flagship -- plan S7.1)."""
    if not isinstance(options, Mapping):
        return
    generator = options.get("image_generator")
    if generator is None:
        return  # founder-gated seam not bound -> skip cleanly (no crash, no fabricated image).

    grid = _import_image_grid()
    if grid is None:
        result.errors.append("image_stage_skipped: cex_image_grid not importable")
        return

    out_dir = options.get("image_out_dir") or str(
        Path(_TOOLS_DIR).parents[0] / ".cexai" / "images" / _safe_seg(result.tenant_id)
    )
    base_name = options.get("image_base_name") or _slug_for_image(handoff.head_terms)
    prompt = options.get("image_prompt") or _derive_image_prompt(handoff)
    try:
        tiles = grid.generate_and_crop(
            prompt, generator=generator, out_dir=str(out_dir),
            base_name=base_name, tenant_id=result.tenant_id,
        )
        result.image_tiles = list(tiles)
    except Exception as exc:  # surface, never fail the chain.
        result.errors.append("image_stage_failed: %s: %s" % (type(exc).__name__, exc))


def _import_image_grid() -> Any:
    """Import the 2x2 image pipeline (cex_image_grid), or None (degrade-never)."""
    try:
        import cex_image_grid  # type: ignore[import]

        return cex_image_grid
    except Exception:
        return None


def _derive_image_prompt(handoff: "ResearchHandoff") -> str:
    """A minimal image prompt from the research handoff (head_terms + differentiation_angle).
    NEVER fabricates a product; an empty handoff -> a generic-but-honest prompt."""
    parts: List[str] = []
    if handoff.head_terms:
        parts.append(handoff.head_terms[0])
    if handoff.differentiation_angle:
        parts.append(handoff.differentiation_angle)
    return ", ".join(parts) if parts else "product hero shot"


def _slug_for_image(head_terms: List[str]) -> str:
    base = head_terms[0] if head_terms else "product"
    s = re.sub(r"[^a-z0-9]+", "_", base.encode("ascii", "ignore").decode("ascii").lower()).strip("_")
    return s or "product"


def _safe_seg(text: str) -> str:
    return "".join(c for c in str(text or "") if c.isalnum() or c in "-_") or "unknown"


# --------------------------------------------------------------------------- #
# Render + persist the research stage (dual output, capability set).
# --------------------------------------------------------------------------- #
def _render_and_persist_research(
    result: PipelineResult,
    structured: Mapping[str, Any],
    contract: Mapping[str, Any],
    db: Optional[DbWriter],
    research_res: CapabilityResult,
) -> None:
    """Render the research result to MD+HTML and persist BOTH (capability set). Mutates
    ``result`` (research_md / research_html / research_record_id). Best-effort persist."""
    rendered = _oc.render(structured, contract)
    result.research_md = rendered.get("md", "")
    result.research_html = rendered.get("html", "")

    if not research_res.passed:
        # A failed-gate research is rendered (so the employee sees it) but NOT persisted
        # (persist-after-pass; mirrors run_capability's rule).
        return

    meta: Dict[str, Any] = {
        "table": _TENANT_DATA_TABLE,
        "capability": result.research_capability,
        "pillar": research_res.pillar,
        "nucleus": research_res.nucleus,
        "score": research_res.score,
        "model_used": research_res.model_used,
        "html": result.research_html,          # the derivative HTML, alongside the canonical MD
        "structured": _oc._yaml_safe_value(dict(structured)),  # the structured fields (jsonb-safe)
        "ready_for_ads": result.ready_for_ads,
    }
    # The persisted artifact is the CANONICAL MD (not the monolithic build string) so the
    # tenant_data row holds the safe-YAML frontmatter the next capability reads.
    rid = _persist(db, result.tenant_id, result.research_capability, RESEARCH_KIND,
                   result.research_md, meta, result)
    result.research_record_id = rid


def _persist(
    db: Optional[DbWriter],
    tenant_id: str,
    capability: str,
    kind: str,
    artifact: str,
    meta: Mapping[str, Any],
    result: PipelineResult,
) -> Optional[str]:
    """Persist ONE artifact via the injected DbWriter, best-effort-after-pass.

    DEGRADE-NEVER: db=None -> returns None (persisted=False), the chain proceeds. A DB
    failure is surfaced (an error appended to ``result``) but never discards the artifact.
    The DbWriter.persist_artifact seam is the SHIPPED contract (tenant_id EXPLICIT); the
    ``capability`` is carried so the writer can stamp the new ``capability`` column."""
    if db is None:
        return None
    try:
        record_id = db.persist_artifact(tenant_id, capability, kind, artifact, dict(meta))
        return str(record_id) if record_id is not None else None
    except Exception as exc:  # surface, never discard
        result.errors.append(
            "persist_failed[%s]: %s: %s" % (capability, type(exc).__name__, exc)
        )
        return None


# --------------------------------------------------------------------------- #
# Helpers (PURE).
# --------------------------------------------------------------------------- #
def _extract_structured(artifact: str) -> Dict[str, Any]:
    """Extract the structured result from an artifact's YAML frontmatter (the producer's
    frontmatter IS the 30-field contract -- n01 S3). DEGRADE-NEVER: no frontmatter / no
    PyYAML / a parse error -> {} (the renderer then emits a minimal-but-valid card).

    R-190: mirrors cex_run_capability._extract_research_structured's fix -- delegates to
    cex_shared.parse_frontmatter (line-anchored close-fence scan) instead of the local
    `_FRONTMATTER_RE` (`re.match(r"^---\\s*\\n(.*?)\\n---")`), which closed on the FIRST
    '---' SUBSTRING anywhere -- including one embedded inside a quoted frontmatter value
    or a markdown table divider -- silently truncating or corrupting the 30-field contract."""
    if not isinstance(artifact, str) or not artifact:
        return {}
    try:
        return _parse_frontmatter(artifact) or {}
    except Exception:
        return {}


def _compose_ads_intent(base_intent: str, handoff: ResearchHandoff) -> str:
    """Compose the ads-stage intent from the user's base intent + the C3 open_vars adapter.

    The ads capability reads a STABLE shape (plan C3): the open_vars block is embedded as a
    compact, machine-readable hint appended to the user's intent. The product always wins
    (plan S4.1 "PRODUTO sempre vence"): the base_intent (the user's product description)
    leads; research is ADDITIVE context. NEVER fabricates a field (empty -> omitted)."""
    lines: List[str] = [base_intent.strip()]
    lines.append("")
    lines.append("## Pesquisa (contexto -- produto sempre vence; nao inventar dados)")
    if handoff.head_terms:
        lines.append("head_terms: %s" % ", ".join(handoff.head_terms[:15]))
    if handoff.usps:
        lines.append("usps: %s" % ", ".join(handoff.usps[:7]))
    if handoff.competitor_gaps:
        lines.append("competitor_gaps: %s" % ", ".join(handoff.competitor_gaps[:5]))
    complaints = handoff.social_insights.get("top_complaints") if handoff.social_insights else None
    if isinstance(complaints, (list, tuple)) and complaints:
        lines.append("pain_points: %s" % ", ".join(str(c) for c in complaints[:5]))
    if handoff.differentiation_angle:
        lines.append("differentiation_angle: %s" % handoff.differentiation_angle)
    if handoff.sweet_spot_price is not None:
        lines.append("sweet_spot_price (validacao apenas, nunca emitir R$): %s"
                     % handoff.sweet_spot_price)
    return "\n".join(lines).strip()


def _str_list(value: Any) -> List[str]:
    if isinstance(value, (list, tuple)):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _str_or_none(value: Any) -> Optional[str]:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


__all__ = [
    "run_pipeline",
    "PipelineResult",
    "ResearchHandoff",
    "Credential",
    "CapabilityResult",
    "CapabilityRefused",
    "DbWriter",
    "DEFAULT_RESEARCH_CAPABILITY",
    "DEFAULT_ADS_CAPABILITY",
    "RESEARCH_KIND",
    "MODE_BYO_API_KEY",
    "MODE_NATIVE_LOCAL",
    "MODE_PLATFORM",
]

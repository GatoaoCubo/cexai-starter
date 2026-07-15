#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI headless product runtime -- run_capability (mission CEXAI_PRODUCT_RUNTIME).

THE headless product entry (ADR D1 "Agent-SDK runtime"). A thin, tenant-scoping +
persistence WRAPPER over the EXISTING cex_sdk.agent.CEXAgent 8F pipeline. Implements
section A of spec_cexai_product_build_v1 (the frozen 0b "Canonical Contract").

WHAT THIS ADDS (the gap section A closes): CEXAgent is tenant-UNAWARE -- it takes no
tenant_id and persists nothing to a tenant DB; it only emits a signal and returns the
artifact string. run_capability is the layer that:
  1. RESOLVE   capability -> (nucleus, kind, pillar, verb) OVERLAY-FIRST by DELEGATING to
               cex_capability_registry.resolve_capability(capability, tenant_id) -- the
               tested, overlay-first SINGLE SOURCE (the tenant's kinds_overlay.yaml is
               consulted before the global base catalog). tenant_id is passed EXPLICITLY
               (no ambient CEX_TENANT_ID juggling). DEGRADE-NEVER: if the registry import
               fails, fall back to the in-module _BASE_CAPABILITIES table.
  2. SCOPE     deny-by-default: empty/missing tenant_id -> CapabilityRefused
               ('missing_tenant'); a capability not in the tenant's enabled set ->
               CapabilityRefused('capability_disabled'); a frozen-kind override ->
               CapabilityRefused('frozen_kind'). Mirrors the adapter's tenant rule.
  3. CREDENTIAL select the F5 model/provider/key from the Credential (ADR D5). The
               native_local headless path is NOT solved (OQ2) and RAISES a clear
               deferral; byo_api_key is the WIRED path (chat() exists); platform is a
               placeholder (DEFERRED).
  4. BUILD     CEXAgent(nucleus, kind, model).build(intent) -> the EXISTING F1->F8 path.
  5. PERSIST   if a DbWriter is injected and the build passed: db.persist_artifact(...)
               writes the artifact INTO the tenant's OWN Supabase via SupabaseDataAdapter
               (tenant_id EXPLICIT). Best-effort-after-pass: a DB failure is surfaced
               (persisted=False + error) but never discards the produced artifact.
  6. RETURN    a CapabilityResult (artifact + score + record_id + model_used + trace).
               The api_key is never echoed back, never logged, never persisted.

HARD RULES (per the task contract + .claude/rules/ascii-code-rule.md):
  * ASCII-only; fully type-hinted; FAIL-CLOSED (every deny raises, never a silent empty).
  * NO concrete DB driver and NO LLM key are imported/read at MODULE IMPORT. The DbWriter
    (the persistence seam) and the Credential (the auth seam) are INJECTED. The api_key
    lives only inside the passed Credential; the module never reads ANTHROPIC_API_KEY etc.
    at import time -- it only sets the env var transiently around the build IF the caller
    supplied a byo_api_key, restoring it in a finally.
  * tenant_id is ALWAYS an explicit argument; the runtime NEVER infers it from ambient
    global state inside a request. CEX_TENANT_ID is set ONLY for the duration of
    overlay/credential resolution and restored in finally (spec A.4 deny seam).

DbWriter CONTRACT RECONCILIATION: the frozen 0b/A.2 Protocol method is
``persist_artifact(tenant_id, capability, kind, artifact, meta) -> str`` -- that is the
canonical seam the runtime calls and the tests assert against (it carries the full
capability/kind/meta context the persistence layer needs). The task brief's shorthand
"write(tenant_id, table, row)" is the lower-level adapter call that a CONCRETE DbWriter
makes INTERNALLY (it owns one SupabaseDataAdapter and turns persist_artifact into an
adapter.write under the tenant_id). The Protocol exposes persist_artifact; the
``table``/``row`` shaping is an implementation detail of the concrete writer (C.2).

HONEST -- WHAT IS NOT EXERCISED HERE: a LIVE LLM run (a real research via the SDK) needs
an API key (anthropic/openai) or a local Ollama server, plus a real Supabase for persist.
NEITHER is run in this module's unit tests. The tests prove the STRUCTURE only -- wiring,
overlay-first scoping, the deny seam, credential selection, and that persistence is
invoked via db.persist_artifact with the EXPLICIT tenant_id -- using a fake CEXAgent and
a fake DbWriter (offline, zero network). The native_local credential path (ADR D2 lead
tier) is OQ2 and deliberately UNWIRED: it raises, it is not faked.

Spec: _docs/compiled/spec_cexai_product_build_v1.md (section A; canonical contract 0b).
Wraps: cex_sdk/agent/cex_agent.py (CEXAgent.build). Persist seam: cexai.governance.data
.SupabaseDataAdapter. Resolution: _tools/cex_capability_registry.py (overlay-first single
source; itself mirrors cex_intent_resolver's kinds_overlay load + frozen guard).
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Mapping, Optional, Protocol, Tuple, runtime_checkable

# --------------------------------------------------------------------------- #
# Module constants -- no side effects, no driver/key reads at import.
# --------------------------------------------------------------------------- #

# Credential modes (ADR D5). Exactly one per run.
MODE_BYO_API_KEY = "byo_api_key"     # hosted/employee path -- WIRED (chat() exists)
MODE_NATIVE_LOCAL = "native_local"   # company native Claude sub -- UNRESOLVED (OQ2)
MODE_PLATFORM = "platform"           # platform-pays-API -- placeholder (DEFERRED)
_VALID_MODES = frozenset({MODE_BYO_API_KEY, MODE_NATIVE_LOCAL, MODE_PLATFORM})

# The 8F MOAT (spec 0b): kinds an overlay can NEVER re-point. Belt-and-braces guard
# on the runtime side -- the overlay loader already rejects these at load time, but
# run_capability refuses again so a frozen target can never reach the builder. Kept in
# sync with cex_intent_resolver._FROZEN_KINDS.
_FROZEN_KINDS = frozenset({
    "workflow",
    "pipeline_template",
    "prompt_compiler",
    "reasoning_trace",
    "quality_gate",
    "dispatch_rule",
    "handoff",
})

# The base card -> nucleus map (spec B.5). The MVP standard capabilities the runtime
# resolves against AFTER the tenant overlay. Each value is (nucleus, kind, pillar, verb).
# A tenant overlay EXTENDS/overrides this per-tenant (overlay wins); frozen kinds are
# protected above. OQ6 proposes promoting this to a versioned capability_registry kind;
# until then it is the in-module base set, intentionally small + explicit.
_BASE_CAPABILITIES: dict[str, Tuple[str, str, str, str]] = {
    # capability : (nucleus, kind,                 pillar, verb)
    # SYNCED with the shipped catalog (cexai_capability_catalog.yaml) -- council MEDIUM: the
    # fallback used to carry only 9 of the catalog's 17 cards, so on a registry import failure
    # 8 capabilities silently vanished. Every catalog card now has a fallback tuple here; the
    # parity is asserted by test_base_capabilities_match_catalog. Keep this in lockstep with the
    # YAML (the YAML is the source of truth; this is the degrade-never safety net).
    "research":    ("N01", "knowledge_card",       "P01", "analyze"),
    "ads":         ("N02", "prompt_template",      "P03", "create"),
    "pricing":     ("N06", "content_monetization", "P11", "create"),
    "roi_calc":    ("N06", "roi_calculator",       "P11", "create"),
    "funnel_diag": ("N06", "tool_card",            "P11", "analyze"),
    "media_photo": ("N02", "multimodal_prompt",    "P03", "create"),
    "content":     ("N04", "knowledge_card",       "P01", "document"),
    "docs":        ("N04", "knowledge_card",       "P01", "document"),
    "landing":     ("N03", "landing_page",         "P05", "create"),
    "tier_designer":   ("N06", "subscription_tier", "P11", "create"),
    "product_docs":    ("N04", "knowledge_card",   "P01", "document"),
    "email_builder":   ("N02", "prompt_template",  "P03", "create"),
    "oauth_connect":   ("N03", "oauth_app_config", "P04", "create"),
    "competitor_benchmark": ("N01", "competitive_matrix", "P01", "analyze"),
    # SPEC 05 lead-gen suite Phase 1a: the scraping/lead-gen vertical (D1 reuses the
    # research_pipeline kind -- 0 kinds_meta/doctor churn; NOT a frozen kind). N01 research
    # pipeline; its run emits a typed lead LIST (the leads managed_entity seeds the CRM). The
    # structured-generator seam (@register("leadgen")) owns the output; CEXAgent.build is NOT used.
    "leadgen": ("N01", "research_pipeline", "P04", "analyze"),
    # CAPABILITY_LAYER W1: the pesquisa_produto research vertical (plan V1). Resolves to
    # knowledge_card (0 new kinds); the tenant_data discriminator is the capability column.
    "pesquisa_produto": ("N01", "knowledge_card",  "P01", "analyze"),
    # DASHBOARD ROADMAP W1: the Research Universe capability (spec_dashboard_roadmap Sec 4
    # W1). Resolves to the synthetic kind ``research_universe`` -- NOT a frozen kind, NOT an
    # LLM build. The runtime routes it to cex_research_universe.research_universe(seed) (the
    # 10-lane orchestrator), NOT CEXAgent.build (see _ROUTE_RESEARCH_UNIVERSE_KIND below).
    "research_universe": ("N01", "research_universe", "P01", "analyze"),
    # N06 BRANDBOOK Cell B (commit 86e6e0ef8d): complete brand book from brand materials
    # (name / essence / palette / text). Routes through the structured-generator seam
    # (MOLDED_REAL_SEAM @register("brandbook")); CEXAgent.build is NOT used. kind=brandbook
    # is NOT a frozen kind. 8 output sections: identity, palette, typography, persona, logo
    # use, imagery, messaging, and do/don't guardrails. Slug and kind are identical so
    # both the cap-slug and the kind lookup in _get_structured_generator hit the same fn.
    "brandbook":  ("N06", "brandbook",           "P05", "create"),
    # W3 SOURCING (contract foundation): the buy-side opportunity matrix + the shared
    # visual product-match/catalog-audit. Both molded in apps/dashboard_web/lib/molds.ts
    # (I/O contract sections 15-16). Kinds opportunity_matrix / product_match are NOT
    # frozen kinds. inject_sources (n01_sourcing_rigor + n06_unit_econ) live in the
    # catalog YAML record, not here -- this table is just the runtime tuple.
    "sourcing_opportunity": ("N06", "opportunity_matrix", "P11", "analyze"),
    "product_match":        ("N03", "product_match",      "P04", "analyze"),
    # S5 completeness fix: marketplace_listing (channel-projection of a canonical_product,
    # e.g. a Mercado Livre Items API payload + readiness report) was in the catalog YAML but
    # missing from this fallback table -- kept in lockstep per this table's own stated
    # invariant ("every catalog card now has a fallback tuple here").
    "marketplace_listing":  ("N06", "marketplace_listing", "P05", "create"),
}

# The resolved kind that flags the Research Universe route (spec_dashboard_roadmap W1). A
# capability (base table OR overlay card) whose resolved kind == this value is run through
# the research-universe orchestrator instead of the generic 8F CEXAgent.build. Keyed on the
# KIND (not the capability slug) so a tenant overlay can expose the universe under any slug.
_ROUTE_RESEARCH_UNIVERSE_KIND = "research_universe"

# The resolved kind that flags the marketplace flagship route (dashboard roadmap W2). A
# capability (base table OR overlay card) whose resolved kind == this value is run through the
# REAL research -> ads pipeline (cex_run_pipeline.run_pipeline) instead of the generic 8F
# CEXAgent.build: the research stage produces the 30-field contract, it is rendered + persisted
# via the dual emitter, and a ready_for_ads PASS chains into the ads build. Keyed on the KIND
# (not the slug) so a tenant overlay can expose the flagship under any slug. Mirrors the
# research_universe route precedent exactly (a resolved-kind pre-build branch). See
# _run_pesquisa_produto below. The marketplace catalog/buy-box/demand lanes are reachable
# through this route's STORM fan-out (see _PESQUISA_PRODUTO_DEFAULT_OPTIONS).
_ROUTE_PESQUISA_PRODUTO_KIND = "pesquisa_produto"

# Default run options for the pesquisa_produto route (dashboard roadmap W2). The marketplace
# catalog / buy-box / demand lanes live in the STORM fan-out (cex_run_research -> the tier-router
# cex_marketplace_tier_router), NOT in the W1 single-step path. So this route OPTS INTO STORM by
# default so one pesquisa_produto run reaches those lanes; degrade-never, the pipeline falls back
# to single-step research when the STORM engine is not importable. ``use_tier_router`` routes the
# marketplace lanes through the degrade-never tier-router (a gated lane, e.g. Firecrawl out of
# credits, is honest-blocked/skipped there -- never fabricated). A CALLER-supplied value ALWAYS
# wins (the dashboard / a test may force single-step by passing use_storm=False).
_PESQUISA_PRODUTO_DEFAULT_OPTIONS: dict[str, Any] = {
    "use_storm": True,
    "use_tier_router": True,
}

# Re-entrancy guard sentinel (dashboard roadmap W2). The pesquisa_produto route delegates to
# cex_run_pipeline.run_pipeline, whose single-step research fallback calls back INTO this
# run_capability with capability=pesquisa_produto (which resolves to kind pesquisa_produto again
# -> the route would re-fire -> infinite recursion). The route stamps this sentinel into the
# options it hands the pipeline; the nested run_capability sees it and SKIPS the route, doing the
# plain CEXAgent.build the pipeline expects for the single-step research stage. The STORM path is
# unaffected (it calls run_research, not run_capability, for research). The flag is internal-only
# and NEVER reaches the deny-gate logic (which keys on enabled_capabilities, not this key).
_PESQUISA_PRODUTO_INNER_FLAG = "_cex_pesquisa_produto_inner"

# The tenant Supabase table capability results land in (spec B.2 / C.2). A concrete
# DbWriter targets this via the adapter; surfaced here as the default meta hint.
_TENANT_DATA_TABLE = "tenant_data"

# --------------------------------------------------------------------------- #
# Shared boolean env-switch convention (R-192 consolidation).
#
# Every CEX_* rollback lever in this module is an OPT-OUT switch: ON by default;
# setting it to a FALSY value turns it OFF. Before this consolidation, 7 functions
# re-derived this same check independently -- 4 shared this `_FALSY_FLAGS` constant
# inline, 3 duplicated the identical 4-value tuple literal instead of referencing
# it (a "half-shared" convention, register R-192). `_env_switch` is now the ONE
# place that check lives; every switch below is a single call into it. Verified
# behavior-preserving: an A/B probe of all 7 switches across
# {1,0,true,false,yes,no,"",unset} (plus True/FALSE/"  0  "/Off/OFF/TrUe/junk)
# produced byte-identical before/after result matrices (see docs/KILL_SWITCHES_
# 2026_06_23.md for the audit this consolidation follows up on).
#
# NOTE this is the same falsy set as `_FALSY` in cex_brand_context.py and
# `_OFF_VALUES` in cex_cli_resolver.py -- both independently duplicate the exact
# same 4-tuple in OTHER files. That cross-file duplication is a separate,
# reported-not-fixed follow-up (this row is scoped to cex_run_capability.py only).
# --------------------------------------------------------------------------- #
_FALSY_FLAGS = frozenset({"0", "false", "no", "off"})


def _env_switch(name: str, default: bool = True) -> bool:
    """The one house check for every CEX_* boolean rollback lever in this module:
    enabled unless env var ``name`` is set to a falsy flag (0/false/no/off,
    case/whitespace-insensitive). Unset -> ``default``. Any other value --
    including an explicitly-set empty string, or an unrecognized word -- reads
    as enabled (fails SAFE to the default-on posture). PURE: no side effects."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() not in _FALSY_FLAGS


# Composition attach-gate kill-switch (mission DASHBOARD_COMPOSITION W1). The gate
# is ON by default; CEX_COMPOSE_GATE in {0,false,no,off} bypasses it entirely (allow-all).
_ENV_COMPOSE_GATE = "CEX_COMPOSE_GATE"

# --------------------------------------------------------------------------- #
# EDIT->REFLECT product hydration (arch-council wave 0.5, Group B / B2).
#
# THE GAP: the headline "edit a product -> the ad/catalog reflects it" was UNWIRED. The ad
# mold (cex_ad_mold_bind) already CONSUMES inputs['product_record'] (ADMAX W2b), but no
# caller ever HYDRATED it from the tenant's current product data. This block hydrates it,
# BEFORE dispatch, from the SAME source the admin product-editor writes (tenant_data
# kind='products', read through the audited cex_tenant_knowledge reader -> the SAME
# isolation seam). So once wired, the next ad/catalog run reflects the just-edited product.
#
# The hydration fires ONLY when (a) the run resolves to an ad/catalog capability AND (b) the
# inputs carry a product ref (sku/slug/record_id) AND (c) inputs does NOT already carry an
# explicit product_record (an explicit one always wins -- the edge may pass it inline).
# --------------------------------------------------------------------------- #
# Gate: hydration is ON by default; CEX_PRODUCT_HYDRATE in {0,false,no,off} disables it ->
# byte-identical to the pre-B2 behaviour (degrade-never rollback lever).
_ENV_PRODUCT_HYDRATE = "CEX_PRODUCT_HYDRATE"

# The CAPABILITY SLUGS whose runs are ad/catalog runs that benefit from a product_record.
# Keyed on the SLUG (not the resolved kind) per the council A4 lesson: ``ads`` resolves to
# kind ``prompt_template`` which collides with ``email_builder`` -- so a kind trigger would
# wrongly hydrate an email run. The slug is unambiguous. ``marketplace_listing`` registers by
# its own kind=slug; a tenant overlay may expose a catalog generator under any slug, so the
# KIND set below catches overlay-introduced catalog kinds too.
_PRODUCT_HYDRATE_SLUGS = frozenset({"ads", "marketplace_listing"})

# Catalog/ad KINDS that also trigger hydration (an overlay may expose them under a custom
# slug). ``marketplace_listing`` (the G2 catalog kind) + ``product_ad`` (the ad mold kind).
# ``prompt_template`` is DELIBERATELY EXCLUDED (it is shared by ads + email_builder -- the
# slug, not the kind, disambiguates the ads case).
_PRODUCT_HYDRATE_KINDS = frozenset({"marketplace_listing", "product_ad"})

# The inputs keys carrying a product ref, in priority order: an explicit record_id (the row
# id) wins, then sku, then slug. Matched case-insensitively by the reader.
_PRODUCT_REF_KEYS = ("record_id", "product_record_id", "sku", "slug", "product_slug", "handle")

# The inputs key the hydrated record lands under (the SAME key cex_ad_mold_bind reads).
_PRODUCT_RECORD_KEY = "product_record"

# --------------------------------------------------------------------------- #
# LEADS injection (the CRM / Sales-Assistant run-path seam). MIRRORS the product
# hydration above: an additive, opt-in, degrade-never read that folds the tenant's CURRENT
# managed leads into inputs BEFORE dispatch, so the CRM funnel + the Sales Assistant operate
# on LIVE tenant_data rows (the SAME rows the leadgen capability writes + the Data-tab CRUD
# manages) instead of an empty honest-fallback. SLUG-keyed (the council A4 disambiguation):
# both capabilities resolve to SHARED kinds (demo_acme_crm / demo_acme_sales_assistant), so
# the SLUG -- never the kind -- is the unambiguous trigger.
# --------------------------------------------------------------------------- #
# The capability SLUGS whose runs consume a leads list (crm.build reads inputs['leads'];
# sales_assistant._select_lead reads inputs['lead'] OR inputs['leads'] + lead_id). Keyed on
# the SLUG so a future kind collision can never mis-route an unrelated run.
_LEADS_CONSUMING_SLUGS = frozenset({"crm", "sales_assistant"})

# The managed-entity ``kind`` (= tenant_data.kind slug) the leads live under. Founder-
# confirmed 2026-06-24: a real tenant's leads are stored under tenant_data kind="contacts" (the
# ``contacts`` managed entity in the tenant overlay capability_map.yaml -- "B2B leads e
# contatos"). The entity row payload carries nome/status (+ overlay fields cidade/segmento/
# telefone/next_followup/notes); the generators read nome/status directly and degrade-never
# on the leadgen-shape keys (tipo/canal/fonte/contato/sinal/score) the contacts payload may
# not carry -- so the mapping is pass-the-payload-through (never fabricate a missing field).
_LEADS_ENTITY_KIND = "contacts"

# The inputs key the hydrated leads list lands under (the key BOTH generators consume).
_LEADS_INPUTS_KEY = "leads"


# --------------------------------------------------------------------------- #
# Fail-closed deny error (spec A.2 CapabilityRefused).
# --------------------------------------------------------------------------- #
class CapabilityRefused(RuntimeError):
    """Raised when a capability run is DENIED. Fail-closed: a deny is always an
    exception, never a silent empty CapabilityResult.

    Carries ``.reason`` -- one of:
      * ``missing_tenant``                    -- empty/missing tenant_id.
      * ``capability_disabled``               -- capability not in the tenant enabled set.
      * ``frozen_kind``                       -- overlay tried to re-point an 8F-moat kind.
      * ``missing_credential``                -- no usable credential for the F5 call.
      * ``native_local_headless_unresolved``  -- the native-sub headless path (OQ2) is
                                                 not wired; use mode=byo_api_key instead.
      * ``unresolved_capability``             -- capability maps to no kind (resolver miss).
      * ``sdk_unavailable``                   -- the generic F1->F8 build needs
                                                 cex_sdk (CEXAgent), which is not
                                                 importable in this deployment (a
                                                 distilled tenant does not carry
                                                 cex_sdk/ under the locked
                                                 sdk_choice=cexai_packaged default;
                                                 re-distill with --sdk cex_sdk_legacy
                                                 or --sdk both to vendor it in);
                                                 structured-generator capabilities
                                                 are unaffected.

    plus ``.tenant_id`` and ``.capability`` for diagnostics (never includes any key).
    """

    def __init__(
        self,
        reason: str,
        *,
        tenant_id: str = "",
        capability: str = "",
        detail: str = "",
    ) -> None:
        self.reason = reason
        self.tenant_id = tenant_id
        self.capability = capability
        self.detail = detail
        msg = "capability refused: %s" % reason
        if capability:
            msg += " (capability=%s)" % capability
        if tenant_id:
            msg += " (tenant=%s)" % tenant_id
        if detail:
            msg += " -- %s" % detail
        super().__init__(msg)


# --------------------------------------------------------------------------- #
# Credential (spec A.2 / A.5) -- the F5 auth seam. INJECTED, never read at import.
# --------------------------------------------------------------------------- #
@dataclass
class Credential:
    """How the F5 LLM call is authenticated for THIS run (ADR D5). Exactly one mode.

    mode='byo_api_key'  -> hosted/employee path; ``api_key`` is the tenant's own key
        (resolved from the tenant secret surface by the EDGE, passed IN here -- this
        module never reads another tenant's secrets and never logs the key). WIRED:
        cex_sdk.models.chat() authenticates with this key via the provider env var.
    mode='native_local' -> operator-run, the company's NATIVE Claude sub. SEE OQ2: the
        SDK chat() path is API-key based; native single-seat OAuth headless invocation
        is an UNRESOLVED open question. This mode is a CONTRACT PLACEHOLDER -- selecting
        it raises CapabilityRefused('native_local_headless_unresolved'). It is NOT faked.
    mode='platform'     -> platform-pays-API (hosted-SaaS tier 3, DEFERRED). Treated like
        byo_api_key for plumbing (a platform key in ``api_key``); flagged in model_used.

    ``api_key`` is NEVER persisted, NEVER returned in CapabilityResult, NEVER logged.
    """

    mode: str
    provider: str = "anthropic"          # anthropic | openai | ollama
    model: str = ""                      # "" -> resolve via nucleus_models.yaml at build
    api_key: Optional[str] = None        # set ONLY for byo_api_key (or platform)

    def validate(self) -> None:
        """Fail-closed shape check. Raises CapabilityRefused on an unusable credential.

        Does NOT resolve native_local here (that is the runtime's job, so the refusal
        carries tenant/capability context); only validates the mode is known and that a
        key-bearing mode actually carries a key.
        """
        if self.mode not in _VALID_MODES:
            raise CapabilityRefused(
                "missing_credential",
                detail="unknown credential mode %r (expected one of %s)"
                % (self.mode, sorted(_VALID_MODES)),
            )
        if self.mode in (MODE_BYO_API_KEY, MODE_PLATFORM) and not self.api_key:
            raise CapabilityRefused(
                "missing_credential",
                detail="mode=%s requires a non-empty api_key" % self.mode,
            )


# --------------------------------------------------------------------------- #
# CapabilityResult (spec A.2) -- mirrors BuildResult + tenant/persistence fields.
# --------------------------------------------------------------------------- #
@dataclass
class CapabilityResult:
    """Outcome of one capability run. The api_key is NEVER present on this object."""

    tenant_id: str
    capability: str
    kind: str
    pillar: str
    nucleus: str
    artifact: str = ""                         # produced artifact (frontmatter+body)
    score: float = 0.0                          # F7 structural score
    passed: bool = False                        # gate result (score floor AND frontmatter)
    status: str = "error"                       # produced | persisted | produced_unpersisted | not_attached | error
    model_used: str = ""                        # the F5 model string actually used
    record_id: Optional[str] = None             # row id in the tenant Supabase
    persisted: bool = False                     # True iff artifact landed in tenant DB
    trace: str = ""                             # the F1..F8 trace string from BuildResult
    errors: List[str] = field(default_factory=list)
    # The STRUCTURED result payload (dashboard roadmap W1). Default None for the 8F-build
    # capabilities (their deliverable is the ``artifact`` string). The research_universe route
    # sets it to the orchestrator's research_universe_report dict so the dashboard can render
    # per-section cards (default) or project it via render_universe (?render_format=md|html).
    # JSON-safe by construction (the orchestrator emits a pure dict). NEVER carries a secret.
    structured: Optional[dict] = None
    # The DUAL-OUTPUT asset (mission DUAL2, founder directive 2026-06-21). Set by the
    # structured-generator route to the to_dual_output projection of ``structured`` + the
    # generator's discovered media: {machine_md, human_html, media_slots, id, capability,
    # frontmatter, real}. The HUMAN html face renders in the dashboard; the MACHINE .md face
    # is the canonical, tenant-AI-readable surface (persisted in meta). None on 8F-build /
    # universe / pesquisa routes (they carry ``artifact`` / ``structured`` instead). JSON-safe
    # by construction (a pure projection of structured data + public media srcs); NEVER a secret.
    dual_output: Optional[dict] = None
    # The ACTION QUEUE (mission COMPLETE2 W2b, completeness gap #4). Derived AFTER the run from
    # this result's own gate/score/run_mode/confidence_breakdown/endpoint_status by
    # cex_action_queue.derive_action_queue -- {open_items, next_actions, blocking, idle}: the
    # "what's missing / what to do next" the static APROVADO/BLOQUEADO verdict never gave. ADDITIVE
    # + degrade-never: None when derivation is unavailable/failed (the run is never affected). The
    # queue is DERIVED, never fabricated, and never carries a secret (it reads only public result
    # state -- the api_key is not on this object). Default None so every existing caller is unaffected.
    action_queue: Optional[dict] = None


# --------------------------------------------------------------------------- #
# DbWriter (spec A.2 / C.2) -- the persistence seam. INJECTED so the runtime is
# test-fakeable offline and never imports a concrete DB driver itself.
# --------------------------------------------------------------------------- #
@runtime_checkable
class DbWriter(Protocol):
    """The seam to the tenant's OWN Supabase. A thin wrapper over SupabaseDataAdapter
    bound to ONE DbSession + the verified principal (spec C.2). A concrete impl owns the
    adapter and turns ``persist_artifact`` into an ``adapter.write(session, tenant_id,
    sql, params)`` under the tenant_id (the task brief's ``write(tenant_id, table, row)``
    is that internal adapter call). The runtime only ever calls ``persist_artifact``.

    Injected (never constructed here) so run_capability imports no driver at module load
    (Article VIII import-light) and offline tests pass a fake.
    """

    def persist_artifact(
        self,
        tenant_id: str,
        capability: str,
        kind: str,
        artifact: str,
        meta: Mapping[str, Any],
    ) -> str:
        """Write ``artifact`` INTO the tenant's OWN Supabase (tenant_id EXPLICIT,
        RLS-enforced) and return the new row id. MUST fail-closed on a cross-tenant
        write (the underlying adapter raises TenantDataDenied)."""
        ...


# --------------------------------------------------------------------------- #
# DbReader (arch-council B2) -- the EDIT->REFLECT read seam. INJECTED so the runtime is
# test-fakeable offline and never imports a concrete DB driver itself. A concrete impl is
# cex_tenant_knowledge.TenantKnowledgeReader over the SAME audited adapter + verified-claim
# bind the DbWriter uses (the SAME isolation seam, in reverse). The run path calls ONLY
# find_product (the product-ref -> current-product-record lookup that hydrates an ad/catalog
# run's inputs['product_record'] from the SAME tenant_data the admin product-editor writes).
# --------------------------------------------------------------------------- #
@runtime_checkable
class DbReader(Protocol):
    """The brain-side read seam to the tenant's OWN Supabase (council B1/B2). A concrete
    impl owns the audited SupabaseDataAdapter and turns ``find_product`` into a tenant-scoped
    ``adapter.query`` under the verified-claim bind (RLS + the cross-tenant mirror). The run
    path uses it ONLY to hydrate a product record before an ad/catalog dispatch.

    Injected (never constructed here) so run_capability imports no driver at module load
    (Article VIII import-light) and offline tests pass a fake. degrade-never: a concrete
    reader returns None on no-match / no-data-plane; the run path treats None as 'no
    hydration' and proceeds byte-identically to today."""

    def find_product(
        self, tenant_id: str, ref: str
    ) -> Optional[Mapping[str, Any]]:
        """Return the tenant's CURRENT product record for ``ref`` (a sku/slug/record_id)
        from the SAME source the admin product-editor writes, tenant-scoped + RLS-enforced,
        or None when there is no match / no data plane. MUST fail-closed on a cross-tenant
        read (the underlying adapter raises / yields nothing -- NEVER another tenant's row)."""
        ...

    def list_entity(
        self, tenant_id: str, kind: str
    ) -> Tuple[Mapping[str, Any], ...]:
        """Return the tenant's managed-entity rows for ``kind`` (the tenant_data.kind slug,
        e.g. 'contacts' for leads) as a tuple of row payload mappings (each carries the saved
        entity fields + the row id), tenant-scoped + RLS-enforced. Powers the LEADS injection
        seam (CRM / Sales Assistant): a run that consumes a leads list has inputs['leads']
        folded from the tenant's CURRENT rows BEFORE dispatch -- the SAME rows leadgen writes.

        ADDITIVE (does NOT change find_product). DEGRADE-NEVER: no match / no data plane /
        a denied (cross-tenant) read -> () (an empty tuple -- NEVER another tenant's rows,
        NEVER a crash, NEVER a fabricated row). MUST fail-closed exactly like find_product."""
        ...


# --------------------------------------------------------------------------- #
# Capability resolution (spec A.3 -- overlay-first via the registry).
# --------------------------------------------------------------------------- #
def _import_registry() -> Any:
    """Import cex_capability_registry from the _tools dir (lazy, sys.path-guarded).

    Lazy so a degraded environment that lacks the registry still imports THIS module
    (the failure surfaces only when a run is attempted, and even then it degrades to the
    in-module _BASE_CAPABILITIES table). Returns the module.
    """
    tools_dir = str(Path(__file__).resolve().parent)
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    import cex_capability_registry  # type: ignore[import]

    return cex_capability_registry


def _resolve_capability(
    tenant_id: str,
    capability: str,
) -> Tuple[str, str, str, str]:
    """Resolve ``capability`` -> (nucleus, kind, pillar, verb), OVERLAY-FIRST.

    DELEGATES to cex_capability_registry.resolve_capability(capability, tenant_id) -- the
    tested, overlay-first SINGLE SOURCE (its own logic consults the tenant overlay
    `kinds:` map before the base catalog and already enforces the frozen-kind moat). The
    registry takes tenant_id EXPLICITLY, so no ambient CEX_TENANT_ID juggling is needed.

    Mapping of registry outcomes -> the runtime's fail-closed contract:
      * a record -> (nucleus, kind, pillar, verb) via record.runtime_tuple();
      * CapabilityUnknown -> CapabilityRefused('unresolved_capability');
      * CapabilityFrozen  -> CapabilityRefused('frozen_kind').

    DEGRADE-NEVER: if the registry module cannot be imported at all, fall back to the
    in-module _BASE_CAPABILITIES table (spec B.5) so a degraded environment still runs the
    standard capabilities. The frozen guard (_guard_frozen) runs belt-and-braces on the
    resolved tuple in EITHER path.
    """
    try:
        registry = _import_registry()
    except Exception:
        registry = None

    if registry is not None:
        try:
            record = registry.resolve_capability(capability, tenant_id=tenant_id)
        except getattr(registry, "CapabilityFrozen", ()) as exc:  # frozen-kind moat
            raise CapabilityRefused(
                "frozen_kind",
                tenant_id=tenant_id,
                capability=capability,
                detail=str(exc),
            )
        except getattr(registry, "CapabilityUnknown", ()):  # no overlay/base card
            raise CapabilityRefused(
                "unresolved_capability",
                tenant_id=tenant_id,
                capability=capability,
                detail="capability maps to no kind (no overlay entry, not in base catalog)",
            )
        nucleus, kind, pillar, verb = record.runtime_tuple()
        _guard_frozen(kind, tenant_id, capability)
        return str(nucleus), str(kind), str(pillar), str(verb or "create")

    # DEGRADE-NEVER fallback: the registry is unavailable -> the in-module base table.
    base = _BASE_CAPABILITIES.get(capability)
    if base is not None:
        nucleus, kind, pillar, verb = base
        _guard_frozen(kind, tenant_id, capability)
        return nucleus, kind, pillar, verb

    raise CapabilityRefused(
        "unresolved_capability",
        tenant_id=tenant_id,
        capability=capability,
        detail="capability maps to no kind (registry unavailable, not in base registry)",
    )


def _guard_frozen(kind: str, tenant_id: str, capability: str) -> None:
    """Refuse a resolved kind that is in the 8F MOAT (spec A.3 frozen guard)."""
    if kind in _FROZEN_KINDS:
        raise CapabilityRefused(
            "frozen_kind",
            tenant_id=tenant_id,
            capability=capability,
            detail="kind %r is an 8F-moat frozen kind; an overlay can never re-point it"
            % kind,
        )


# --------------------------------------------------------------------------- #
# Enabled-capability gate (spec B.4 / D.3 -- deny-by-default per tenant).
# --------------------------------------------------------------------------- #
def _capability_enabled(
    tenant_id: str,
    capability: str,
    options: Optional[Mapping[str, Any]],
) -> bool:
    """Decide whether ``capability`` is ENABLED for this tenant.

    The enabled set is the operator-controlled allowlist (spec D.3 ``enabled_capabilities``
    in the overlay, OQ4). For the headless entry the EDGE (dashboard backend / operator)
    resolves the enabled set and passes it via ``options['enabled_capabilities']`` (a list)
    so this pure function never reads a file. Contract:
      * options carries an ``enabled_capabilities`` list -> membership test (deny if absent
        from the list). This is the deny-by-default posture (B.5/D).
      * options omits it (None / key missing) -> ALL capabilities allowed (the spec D.3
        default: "omit => all base"). The operator opted not to gate.
    A tenant-overlay card not in the base set is still subject to this same gate.
    """
    if not options:
        return True
    if "enabled_capabilities" not in options:
        return True
    enabled = options.get("enabled_capabilities")
    if enabled is None:
        return True
    try:
        return capability in set(enabled)
    except TypeError:
        # Malformed enabled set -> fail-closed (deny). The operator declared a gate but
        # in an unusable shape; refusing is safer than silently allowing everything.
        return False


# --------------------------------------------------------------------------- #
# Composition ATTACH gate (mission DASHBOARD_COMPOSITION W1, spec SS3.2).
#
# DISTINCT from _capability_enabled above: that is the EDGE-passed allowlist
# (options['enabled_capabilities']) whose miss RAISES capability_disabled. THIS gate
# reads the per-tenant capability_map.yaml ``capabilities:{enabled,disabled}`` block
# from disk (the D2 git source of truth) and, when a RESOLVED capability is declared-
# but-not-attached, the caller returns a CLEAN ``not_attached`` result -- NEVER a raise,
# NEVER a generator/build dispatch. Kill-switch CEX_COMPOSE_GATE=0 -> bypass (allow-all).
# DEGRADE-NEVER: absent block / read error / older registry -> attached (run).
# --------------------------------------------------------------------------- #
def _compose_gate_on() -> bool:
    """The compose attach gate is ON unless CEX_COMPOSE_GATE is a falsy flag (default ON)."""
    return _env_switch(_ENV_COMPOSE_GATE)


def _capability_attached(tenant_id: str, capability: str) -> bool:
    """Decide whether a RESOLVED ``capability`` is ATTACHED (enabled) for the tenant.

    Reads the tenant capability_map.yaml ``capabilities:{enabled,disabled}`` block via the
    registry's resolve_enabled. The capability has already RESOLVED (it is declared), so it
    is added to the declared universe handed to resolve_enabled -- it can only be filtered
    out by an EXPLICIT enabled-allowlist miss or a disabled entry, never by the
    declared-intersection on its own account.

    TOTAL / DEGRADE-NEVER: the kill-switch, an older registry without resolve_enabled, OR
    ANY read/import error -> True (attached). The attach gate must NEVER block a tenant's
    dashboard on an error -- absent block -> allow-all is the zero-regression contract.

    FAIL-CLOSED EXCEPTION (arch-council C1): a SENSITIVE/PAID capability whose per-tenant
    capability_map.yaml is PRESENT-but-unparseable is REFUSED (returns False -> not_attached).
    A corrupt gate file must never silently RE-ENABLE a paid cap (which is what the plain
    degrade-to-allow would do, since resolve_enabled reads a corrupt file as {} == allow-all).
    This is SURGICAL: it only fires for a sensitive cap AND a present-but-unparseable file; a
    transient read error, an ABSENT file, and every non-sensitive cap keep degrading to allow."""
    if not _compose_gate_on():
        return True
    try:
        registry = _import_registry()
    except Exception:
        return True  # registry unavailable -> allow-all (degrade-never, mirrors resolve)

    # -- C1 fail-closed: a PRESENT-but-unparseable gate file denies the SENSITIVE set. ------
    # Guarded + total: any surprise in the C1 primitives degrades to the historical allow path
    # (we never let the fail-closed check itself become a new way to crash the dashboard).
    try:
        is_sensitive = getattr(registry, "is_sensitive_capability", None)
        map_unparseable = getattr(registry, "capability_map_unparseable", None)
        if (
            is_sensitive is not None
            and map_unparseable is not None
            and is_sensitive(capability)
            and map_unparseable(tenant_id)
        ):
            return False  # corrupt gate + paid cap -> REFUSE (fail-closed), never re-enable
    except Exception:
        pass  # C1 primitives unavailable/older registry -> fall through to the allow path

    resolve_enabled = getattr(registry, "resolve_enabled", None)
    if resolve_enabled is None:
        return True  # older registry without the gate -> allow-all
    declared: "set[str]" = set()
    declared_fn = getattr(registry, "declared_capabilities", None)
    if declared_fn is not None:
        try:
            declared = set(declared_fn(tenant_id))
        except Exception:
            declared = set()
    declared.add(capability)
    try:
        enabled = resolve_enabled(tenant_id, declared)
        return capability in set(enabled)
    except Exception:
        return True  # degrade-never: any gate failure -> attached (run)


def _not_attached_result(
    tid: str, cap: str, nucleus: str, kind: str, pillar: str
) -> "CapabilityResult":
    """Build the CLEAN 'capability not attached' result (spec SS3.2). NEVER raises; the
    generator / build is NOT run (no LLM, no DB). status='not_attached', passed=False, no
    artifact. The dashboard / N07 reads this to PROPOSE attaching the module (the
    compose-by-talking-to-N07 loop, spec SS3.4)."""
    return CapabilityResult(
        tenant_id=tid,
        capability=cap,
        kind=kind,
        pillar=pillar,
        nucleus=nucleus,
        artifact="",
        score=0.0,
        passed=False,
        status="not_attached",
        model_used="",
        trace="",
        errors=[
            "capability_not_attached: %r is declared but not attached (enabled) for this "
            "tenant; attach the module to run it" % cap
        ],
    )


# --------------------------------------------------------------------------- #
# Credential selection (spec A.5 -- the honest flag). Returns (model, provider) and
# yields a context that transiently sets the provider key env var, restored after.
# --------------------------------------------------------------------------- #
def _select_credential(
    credential: Credential,
    tenant_id: str,
    capability: str,
    default_model: str,
) -> Tuple[str, str]:
    """Resolve the F5 (model, provider) from the Credential, FAIL-CLOSED.

    native_local -> raise CapabilityRefused('native_local_headless_unresolved') with a
    message pointing at byo_api_key (OQ2 -- NOT faked). byo_api_key / platform -> return
    the resolved model + provider; the api_key itself is applied transiently around the
    build by ``_apply_provider_key`` (never here, never logged).
    """
    credential.validate()

    if credential.mode == MODE_NATIVE_LOCAL:
        raise CapabilityRefused(
            "native_local_headless_unresolved",
            tenant_id=tenant_id,
            capability=capability,
            detail=(
                "native_local (company native Claude sub) headless invocation via the "
                "Agent SDK is UNRESOLVED (OQ2): the SDK chat() path is API-key based and "
                "a single-seat OAuth sub is non-injectable. Use mode=byo_api_key for "
                "dashboard/headless runs until OQ2 is resolved."
            ),
        )

    # byo_api_key / platform: model is the credential's model or the nucleus default.
    model = credential.model or default_model
    provider = credential.provider or "anthropic"
    return model, provider


def _provider_key_env(provider: str) -> Optional[str]:
    """The env var cex_sdk.models.chat() reads for ``provider``'s API key. Ollama is
    local (no key) -> None."""
    p = (provider or "").lower()
    if p == "anthropic":
        return "ANTHROPIC_API_KEY"
    if p == "openai":
        return "OPENAI_API_KEY"
    if p == "openwebui":
        return "OPENWEBUI_API_KEY"
    return None  # ollama / unknown -> no key env


class _ProviderKeyScope:
    """Context manager that sets the provider API-key env var from the Credential for
    the duration of the build ONLY, then restores the prior value. The key never persists
    in the environment beyond the build and is never logged.

    For mode=native_local this is never reached (selection raises first); for ollama the
    key env is None and this is a no-op.

    BYOK EXTENSION (mission BYOK_0713 D5, backend seam): the optional keyword-only
    ``resolved_key`` overrides ``credential.api_key`` for the duration of the scope --
    the seam a tenant-aware caller uses to inject a BYOK-resolved per-tenant key (e.g.
    from ``apps.dashboard_api.deps.resolve_credential``) into the SAME least-privilege
    injection mechanism, without needing to stuff it into a Credential object first.
    ADDITIVE ONLY: every existing call site (``_ProviderKeyScope(credential, provider)``,
    unchanged) keeps using ``credential.api_key`` exactly as before -- ``resolved_key``
    defaults to None and changes nothing when omitted.
    """

    def __init__(
        self,
        credential: Credential,
        provider: str,
        *,
        resolved_key: Optional[str] = None,
    ) -> None:
        self._var = _provider_key_env(provider)
        self._key = resolved_key if resolved_key else credential.api_key
        self._prev: Optional[str] = None
        self._active = False

    def __enter__(self) -> "_ProviderKeyScope":
        if self._var and self._key:
            self._prev = os.environ.get(self._var)
            os.environ[self._var] = self._key
            self._active = True
        return self

    def __exit__(self, *exc: Any) -> None:
        if not self._active:
            return
        if self._prev is None:
            os.environ.pop(self._var, None)  # type: ignore[arg-type]
        else:
            os.environ[self._var] = self._prev  # type: ignore[index]
        self._active = False


# --------------------------------------------------------------------------- #
# CEXAgent seam -- module-level name so tests can monkeypatch it without a live LLM.
# Imported lazily inside run_capability; bound here as Optional for fakeability.
# --------------------------------------------------------------------------- #
def _import_cex_agent() -> Any:
    """Import cex_sdk.agent.CEXAgent lazily (no LLM client touched at import)."""
    from cex_sdk.agent.cex_agent import CEXAgent  # type: ignore[import]

    return CEXAgent


# Tests set cex_run_capability.CEXAgent = FakeAgent to run offline. When None (default),
# run_capability imports the real CEXAgent lazily.
CEXAgent: Any = None


# --------------------------------------------------------------------------- #
# Research Universe seam (dashboard roadmap W1) -- module-level name so tests can
# monkeypatch it without touching the network. Imported lazily inside the route.
# --------------------------------------------------------------------------- #
def _import_research_universe() -> Any:
    """Import the cex_research_universe orchestrator module lazily (no network at import).

    The orchestrator is itself degrade-never + offline-safe (every lane honest-blocks
    without its credential and is lazily imported), so importing it here touches no key.
    """
    tools_dir = str(Path(__file__).resolve().parent)
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    import cex_research_universe  # type: ignore[import]

    return cex_research_universe


# Tests set cex_run_capability.research_universe = fake to run offline + deterministic.
# When None (default), the route imports the real orchestrator lazily.
research_universe: Any = None


# --------------------------------------------------------------------------- #
# Lead-gen REAL orchestrator seam (spec 05_leadgen_suite Phase 1b) -- module-level name so
# tests can monkeypatch it without touching the network. Imported lazily inside the route.
# The orchestrator (cex_leadgen_run.leadgen_run) is itself degrade-never + offline-safe (each
# lane honest-blocks without its credential, lazily imported), so importing it touches no key.
# --------------------------------------------------------------------------- #
def _import_leadgen_run() -> Any:
    """Import the cex_leadgen_run orchestrator module lazily (no network at import)."""
    tools_dir = str(Path(__file__).resolve().parent)
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    import cex_leadgen_run  # type: ignore[import]

    return cex_leadgen_run


# Tests set cex_run_capability.leadgen_run = fake to run offline + deterministic. When None
# (default), the route imports the real orchestrator lazily (see _import_leadgen_run).
leadgen_run: Any = None

# The capability SLUG that flags the lead-gen real route (spec 05_leadgen_suite Phase 1b). Keyed
# on the SLUG (not the resolved kind): leadgen resolves to the SHARED, FROZEN kind
# research_pipeline (council A4 -- a kind trigger would collide / be a frozen-kind no-op), so the
# slug is the unambiguous, authoritative route key (the same lesson as the ads/product hydration).
_ROUTE_LEADGEN_SLUG = "leadgen"


# --------------------------------------------------------------------------- #
# Marketplace flagship seam (dashboard roadmap W2) -- the research -> ads pipeline.
# cex_run_pipeline imports THIS module at its top level, so it MUST be imported LAZILY
# here (inside the route, never at module load) to avoid an import cycle -- the SAME lazy
# discipline the research_universe seam uses. Bound as a module-level name so tests can
# monkeypatch ``run_pipeline`` with an offline fake (no LLM/DB/network).
# --------------------------------------------------------------------------- #
def _import_run_pipeline() -> Any:
    """Import the cex_run_pipeline module lazily (BREAKS the import cycle).

    cex_run_pipeline does ``import cex_run_capability`` at its top level (it reuses this
    spine verbatim), so importing it at THIS module's top level would be circular. Deferring
    the import to call time means cex_run_capability finishes importing first; by the time a
    pesquisa_produto run is attempted, the pipeline module imports cleanly. The pipeline is
    itself import-light (no driver/key at load), so this touches no secret.
    """
    tools_dir = str(Path(__file__).resolve().parent)
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    import cex_run_pipeline  # type: ignore[import]

    return cex_run_pipeline


# Tests set cex_run_capability.run_pipeline = fake to run the route offline + deterministic.
# When None (default), the route imports the real pipeline lazily (see _import_run_pipeline).
run_pipeline: Any = None


def _is_pesquisa_inner(options: Optional[Mapping[str, Any]]) -> bool:
    """True iff this run_capability call is the pipeline's INNER single-step research call (the
    re-entrancy guard). When set, the pesquisa_produto route is skipped so a plain build runs."""
    return bool(options and options.get(_PESQUISA_PRODUTO_INNER_FLAG) is True)


def _run_pesquisa_produto(
    tid: str,
    cap: str,
    nucleus: str,
    kind: str,
    pillar: str,
    intent: str,
    credential: Credential,
    *,
    db: Optional[DbWriter] = None,
    options: Optional[Mapping[str, Any]] = None,
) -> CapabilityResult:
    """Run the marketplace flagship via the REAL pipeline (dashboard roadmap W2). See run_capability.

    Routes ``pesquisa_produto`` through cex_run_pipeline.run_pipeline -- the research -> render(30-
    field contract) -> ads chain -- instead of the generic 8F CEXAgent.build (which produced a flat
    knowledge_card). The pipeline:
      * STAGE 1 RESEARCH  -- the STORM fan-out (default-on here so the marketplace catalog/buy-box/
        demand lanes are reachable; degrade-never falls back to single-step research);
      * STAGE 3+4 RENDER+PERSIST -- the 30-field result -> canonical MD + derivative HTML, persisted
        via the SAME audited db.persist_artifact seam (tenant_id EXPLICIT -> tenant-scoped + RLS);
      * STAGE 5 GATE + 6/7/8 ADS -- a ready_for_ads PASS chains into the ads build + persist.

    CREDENTIAL: the pipeline reuses this spine's _select_credential / _ProviderKeyScope (native_local
    -> raises, byo_api_key -> the key is applied transiently around each build and restored). So the
    api_key is NEVER logged / persisted / echoed -- the pipeline's CapabilityResult-shaped stage
    results carry no key, and this route's CapabilityResult carries none either.

    DEGRADE-NEVER: the pipeline never crashes on a blocked/failing lane (it returns an honest partial
    -- status research_only / completed); a HARD pipeline surprise here is caught and surfaced as an
    error on the result, never a 500. A CapabilityRefused from the spine (missing_credential /
    native_local / capability_disabled) PROPAGATES (fail-closed), exactly as the build path.

    PERSIST: the pipeline owns its dual-output persist (research MD + ads), so we pass ``db`` straight
    through and DO NOT double-persist here. persisted reflects whether the research row landed (no
    data plane -> persisted=False, the safe default).

    Returns a CapabilityResult whose ``structured`` carries the chain-level report (status, the 30-
    field research structured fields, open_vars, ads summary, record ids, errors) so the dashboard
    renders the marketplace result view, and whose ``artifact`` is the CANONICAL research MD (so the
    existing results-row / render machinery has a stable text payload).
    """
    # The pipeline needs the credential (it runs real builds). It also reuses the SAME deny seam,
    # so a refusal (native_local / missing_credential / a disabled ads capability) propagates.
    pipe = run_pipeline if run_pipeline is not None else _import_run_pipeline().run_pipeline

    # Caller options win; default-on STORM + tier-router so the marketplace lanes are reachable.
    run_opts: dict[str, Any] = dict(_PESQUISA_PRODUTO_DEFAULT_OPTIONS)
    if options:
        run_opts.update(dict(options))
    # Stamp the re-entrancy guard so the pipeline's single-step research fallback (which calls back
    # into run_capability with capability=pesquisa_produto) does a plain build instead of re-firing
    # this route. The STORM research path is unaffected (it uses run_research, not run_capability).
    run_opts[_PESQUISA_PRODUTO_INNER_FLAG] = True

    errors: List[str] = []
    pr: Any = None
    try:
        pr = pipe(
            tid,
            intent,
            credential,
            db=db,
            research_capability=cap,
            ads_capability=run_opts.get("ads_capability", "ads"),
            options=run_opts,
        )
    except CapabilityRefused:
        # Fail-closed: a deny from the spine (native_local / missing_credential / disabled) is an
        # authorization/config error the caller must see -- propagate, never swallow into a partial.
        raise
    except Exception as exc:  # DEGRADE-NEVER: a hard pipeline surprise must not 500 the run.
        errors.append("pesquisa_produto_failed: %s: %s" % (type(exc).__name__, exc))

    if pr is None:
        # The pipeline raised a non-refusal surprise (caught above). Return an honest error result
        # rather than a crash -- no fabricated data, no secret.
        return CapabilityResult(
            tenant_id=tid, capability=cap, kind=kind, pillar=pillar, nucleus=nucleus,
            artifact="", score=0.0, passed=False, status="error",
            model_used="", trace="", errors=errors, structured=None,
        )

    # Map the PipelineResult -> a CapabilityResult the dashboard already renders. The research stage
    # result carries the score/model/trace; the chain-level status reflects research_only/completed.
    research = getattr(pr, "research", None)
    score = float(getattr(research, "score", 0.0) or 0.0) if research is not None else 0.0
    model_used = str(getattr(research, "model_used", "") or "") if research is not None else ""
    trace = str(getattr(research, "trace", "") or "") if research is not None else ""
    # ``passed`` for the capability = the research stage produced a usable artifact (the chain may
    # still degrade to research_only if ready_for_ads was false -- that is honest, not a failure).
    passed = bool(getattr(research, "passed", False)) if research is not None else False

    pr_status = str(getattr(pr, "status", "error") or "error")
    research_record_id = getattr(pr, "research_record_id", None)
    persisted = research_record_id is not None
    # The capability-level status mirrors the build path vocabulary: persisted when the research row
    # landed; produced_unpersisted when it passed but no row id (no data plane / a persist failure);
    # error when the chain itself errored.
    if pr_status == "error":
        status = "error"
    elif persisted:
        status = "persisted"
    elif passed:
        status = "produced_unpersisted"
    else:
        status = "error"

    structured = _pipeline_structured(pr)

    # Surface the pipeline's own errors (e.g. ads_refused, persist_failed) without leaking a secret
    # (the pipeline never puts a key in an error string -- proven by its own tests).
    errors.extend(list(getattr(pr, "errors", []) or []))

    return CapabilityResult(
        tenant_id=tid,
        capability=cap,
        kind=kind,
        pillar=pillar,
        nucleus=nucleus,
        artifact=str(getattr(pr, "research_md", "") or ""),
        score=score,
        passed=passed,
        status=status,
        model_used=model_used,
        record_id=str(research_record_id) if research_record_id is not None else None,
        persisted=persisted,
        trace=trace,
        errors=errors,
        structured=structured,
    )


def _pipeline_structured(pr: Any) -> Optional[dict]:
    """Project a PipelineResult into the JSON-safe ``structured`` dict the dashboard renders.

    PURE + TOTAL: carries the chain-level shape (status, ready_for_ads, the 30-field research
    structured fields parsed from the canonical MD, the C3 open_vars, an ads summary, record ids,
    the research engine + image tiles). NEVER carries a secret (every field is data the pipeline
    already exposed without a key). A shape surprise degrades to a minimal dict, never raises.
    """
    out: dict[str, Any] = {
        "status": str(getattr(pr, "status", "") or ""),
        "ready_for_ads": bool(getattr(pr, "ready_for_ads", False)),
        "research_engine": str(getattr(pr, "research_engine", "") or ""),
        "open_vars": dict(getattr(pr, "open_vars", {}) or {}),
        "research_record_id": getattr(pr, "research_record_id", None),
        "ads_record_id": getattr(pr, "ads_record_id", None),
        "image_tiles": list(getattr(pr, "image_tiles", []) or []),
        "errors": list(getattr(pr, "errors", []) or []),
    }
    # The 30-field research structured fields (the producer's frontmatter contract). Parse from the
    # canonical MD so the dashboard's marketplace view has the per-section fields, the SAME way
    # cex_run_pipeline._extract_structured does (degrade-never -> {} on any parse issue).
    out["research"] = _extract_research_structured(getattr(pr, "research_md", ""))
    # A compact ads summary (kind/score/passed) -- NOT the full ads artifact (that lives in its own
    # persisted row). None when the gate blocked ads (honest -- ready_for_ads false).
    ads = getattr(pr, "ads", None)
    if ads is not None:
        out["ads"] = {
            "kind": str(getattr(ads, "kind", "") or ""),
            "pillar": str(getattr(ads, "pillar", "") or ""),
            "nucleus": str(getattr(ads, "nucleus", "") or ""),
            "score": float(getattr(ads, "score", 0.0) or 0.0),
            "passed": bool(getattr(ads, "passed", False)),
            "artifact": str(getattr(ads, "artifact", "") or ""),
        }
    else:
        out["ads"] = None
    return out


def _extract_research_structured(research_md: Any) -> dict:
    """Parse the 30-field structured fields from the canonical research MD frontmatter (PURE + TOTAL).

    Mirrors cex_run_pipeline._extract_structured: the producer's YAML frontmatter IS the 30-field
    contract. DEGRADE-NEVER: no MD / no frontmatter / no PyYAML / a parse error -> {} (the dashboard
    then renders the chain-level fields only, never a crash).

    R-190: delegates to cex_shared.parse_frontmatter (line-anchored close-fence scan) instead of
    the local `re.match(r"^---\\s*\\n(.*?)\\n---")`, which closed on the FIRST '---' SUBSTRING
    anywhere -- including one embedded inside a quoted frontmatter value or a markdown table
    divider -- silently truncating or corrupting the parsed 30-field contract."""
    if not isinstance(research_md, str) or not research_md:
        return {}
    try:
        tools_dir = str(Path(__file__).resolve().parent)
        if tools_dir not in sys.path:
            sys.path.insert(0, tools_dir)
        from cex_shared import parse_frontmatter

        return parse_frontmatter(research_md) or {}
    except Exception:
        return {}


def _run_research_universe(
    tid: str,
    cap: str,
    nucleus: str,
    kind: str,
    pillar: str,
    intent: str,
    *,
    db: Optional[DbWriter] = None,
    options: Optional[Mapping[str, Any]] = None,
) -> CapabilityResult:
    """Run the Research Universe capability (spec_dashboard_roadmap W1). See run_capability.

    NOT an LLM build: the seed is the ``intent`` (the user's product/brand/CNPJ/keyword);
    the 10-lane orchestrator fans out + assembles ONE structured report. DEGRADE-NEVER --
    the orchestrator NEVER raises (a blocked/failing lane is an honest section in
    endpoint_status), and even a HARD orchestrator/import failure here is caught and
    surfaced as an error on the result, never a crash. NEVER fabricates (a blocked lane is
    honest-blocked, never invented). PERSIST is best-effort: the structured report is
    serialised + written via the SAME audited db.persist_artifact seam the build path uses
    (tenant_id EXPLICIT -> tenant-scoped + RLS); no data plane -> persisted=False (safe
    default). The api_key is never touched here (no credential is used).

    Returns a CapabilityResult whose ``structured`` carries the research_universe_report
    dict (so the dashboard renders section cards / projects it via render_universe) and
    whose ``artifact`` carries a JSON serialisation of that report (so the existing persist
    + results-row machinery has a stable text payload).
    """
    # The seed is the user's intent (the product/brand/CNPJ/keyword/store:id). An optional
    # ``kinds`` override may be passed through ``options['kinds']`` (the orchestrator narrows
    # it to the valid lane subset itself; unknown lanes are dropped honestly, never run).
    seed = (intent or "").strip()
    kinds = None
    if options and isinstance(options.get("kinds"), (list, tuple, str)):
        kinds = options.get("kinds")

    errors: List[str] = []
    report: dict = {}
    try:
        orchestrator = (
            research_universe
            if research_universe is not None
            else _import_research_universe().research_universe
        )
        produced = orchestrator(seed, kinds=kinds) if kinds is not None else orchestrator(seed)
        report = produced if isinstance(produced, dict) else {}
        if not isinstance(produced, dict):
            errors.append(
                "research_universe returned a non-dict (%s); degraded to empty report"
                % type(produced).__name__
            )
    except Exception as exc:  # DEGRADE-NEVER: even a hard orchestrator/import surprise.
        # The orchestrator is built never to raise; this is the belt-and-suspenders floor so
        # the RUN still returns 200 with an honest error rather than a 500. No secret here.
        report = {}
        errors.append("research_universe_failed: %s: %s" % (type(exc).__name__, exc))

    # A research-universe run "passed" iff the orchestrator produced a report dict. There is
    # no 8F score floor here (it is not an LLM artifact); the per-lane endpoint_status carries
    # the honest provenance. ``mock`` is always False in the orchestrator's contract.
    passed = bool(report)
    artifact = _serialize_report(report)

    result = CapabilityResult(
        tenant_id=tid,
        capability=cap,
        kind=kind,
        pillar=pillar,
        nucleus=nucleus,
        artifact=artifact,
        score=0.0,
        passed=passed,
        status="produced" if passed else "error",
        model_used="",                 # no LLM model is used for the universe route
        trace="",
        errors=errors,
        structured=report or None,
    )

    # PERSIST: best-effort-after-pass via the SAME audited seam the build path uses. The
    # structured report rides in meta['structured'] so a row can be re-projected to MD/HTML
    # (the /results render path) the same way a marketplace row is. DEGRADE-NEVER: no data
    # plane -> persisted=False; a DB failure is surfaced, never discards the produced report.
    if db is not None and passed:
        meta: dict[str, Any] = {
            "table": _TENANT_DATA_TABLE,
            "pillar": pillar,
            "nucleus": nucleus,
            "seed": report.get("seed"),
            "seed_type": report.get("seed_type"),
            "structured": report,
        }
        if options and "meta" in options and isinstance(options["meta"], Mapping):
            meta.update(dict(options["meta"]))
        try:
            record_id = db.persist_artifact(tid, cap, kind, artifact, meta)
            result.record_id = str(record_id) if record_id is not None else None
            result.persisted = result.record_id is not None
            result.status = "persisted" if result.persisted else "produced_unpersisted"
        except Exception as exc:  # DB failure: surface, never discard the produced report.
            result.persisted = False
            result.status = "produced_unpersisted"
            result.errors.append("persist_failed: %s: %s" % (type(exc).__name__, exc))

    return result


def _serialize_report(report: Mapping[str, Any]) -> str:
    """JSON-serialise a research_universe_report into an ASCII-safe string (PURE + TOTAL).

    Used as the ``artifact`` text payload for persistence/results. ensure_ascii=True keeps
    the output ASCII (PT-BR labels are escaped) per the ascii-code rule. A non-serialisable
    surprise degrades to '{}' rather than raising (degrade-never)."""
    try:
        import json

        return json.dumps(dict(report), ensure_ascii=True, sort_keys=True)
    except Exception:
        return "{}"


def _run_leadgen(
    tid: str,
    cap: str,
    nucleus: str,
    kind: str,
    pillar: str,
    intent: str,
    credential: Credential,
    *,
    db: Optional[DbWriter] = None,
    options: Optional[Mapping[str, Any]] = None,
    form_inputs: Optional[Mapping[str, Any]] = None,
    brand_context: Optional[Mapping[str, Any]] = None,
) -> CapabilityResult:
    """Run the lead-gen capability through the REAL lane orchestrator (spec 05_leadgen_suite
    Phase 1b). See run_capability.

    The REAL path: cex_leadgen_run.leadgen_run maps the 7 typed inputs -> the existing lanes
    (marketplace tier-router + research_universe cnpj/ibge/reddit/youtube), fans out degrade-
    never, maps REAL results -> lead records, and returns the SAME StructuredOutput contract as
    the 1a generator (mold_id="leadgen", the 5 frozen sections, the 7-col Leads table). So this
    route builds its CapabilityResult EXACTLY like the structured-generator route (dual_output +
    persist), keeping the shape byte-identical to 1a.

    DEGRADE-NEVER: the orchestrator NEVER raises (each lane is wrapped; ALL channels blocked ->
    honest-empty, gate REVISAR) and even a HARD import/orchestrator surprise here falls back to
    the OFFLINE generator scaffold (leadgen.build) -- the PURE 1a fallback -- so the run NEVER
    500s and NEVER fabricates a lead. The deny-by-default tenant + enabled gates above ALREADY
    ran (this branch inherits the same scoping). The credential is passed through for interface
    parity (the lanes own their keys via the env; it is never logged/echoed).

    NEVER-FABRICATE: the orchestrator surfaces a lead/contact ONLY when a lane actually returned
    it; a lane-less contact stays the absent marker ('--'). No mock leads on this real path.
    """
    # Build the typed form payload (the SAME seam the structured route uses), so an uploaded
    # doc/url is resolved + the brand context is stamped. intent stays the free-text fallback.
    inputs = _structured_inputs(intent, options, form_inputs, brand_context)

    runner = leadgen_run if leadgen_run is not None else None
    payload: Optional[dict] = None
    try:
        if runner is None:
            runner = _import_leadgen_run().leadgen_run
        payload = runner(inputs, credential=credential)
    except Exception:
        # DEGRADE-NEVER: a hard orchestrator/import surprise -> fall back to the OFFLINE 1a
        # scaffold (honest-empty, never fabricated). No secret is ever in scope here.
        payload = None

    if not isinstance(payload, dict) or not payload.get("output_sections"):
        # Fall back to the PURE offline generator scaffold (the degrade-never 1a fallback).
        gen = _resolve_structured_generator(tid, cap, kind)
        if gen is not None:
            routed = _run_structured_generator(
                tid, cap, nucleus, kind, pillar, intent, credential, gen,
                db=db, options=options, form_inputs=form_inputs, brand_context=brand_context,
            )
            if routed is not None:
                return routed
        # The absolute floor: an honest error result (no generator, no orchestrator). Never a crash.
        return CapabilityResult(
            tenant_id=tid, capability=cap, kind=kind, pillar=pillar, nucleus=nucleus,
            artifact="", score=0.0, passed=False, status="error", model_used="", trace="",
            errors=["leadgen_unavailable: orchestrator + offline scaffold both unavailable"],
        )

    # The orchestrator returns the SAME StructuredOutput shape as a generator, so reuse the
    # structured-route result assembly (dual_output projection + best-effort persist) verbatim
    # via the shared builder -- the shape is byte-identical to 1a.
    return _build_structured_result(
        tid, cap, nucleus, kind, pillar, payload, inputs,
        generator=_resolve_structured_generator(tid, cap, kind),
        db=db, options=options,
    )


# --------------------------------------------------------------------------- #
# Structured-generator route (mission MOLDED_REAL_SEAM, Wave 0). A capability whose
# RESOLVED kind has a registered generator in capability_generators emits a REAL
# ``structured`` payload (the molded-real shape: mold_id + output_sections + real=True)
# instead of falling to the generic CEXAgent.build mock. Keyed on the KIND (not the slug)
# so a tenant overlay can expose a generator under any slug. ADDITIVE + degrade-never:
# no generator for a kind -> byte-identical fall-through (structured stays None).
# --------------------------------------------------------------------------- #

# Option keys that are PLUMBING (deny gate / persist meta / route flags), NOT form inputs.
# Stripped before the typed form payload is handed to a generator.
_GENERATOR_RESERVED_OPTION_KEYS = frozenset({
    "enabled_capabilities",
    "meta",
    "kinds",
    "tenant_id",
    _PESQUISA_PRODUTO_INNER_FLAG,
    # BRAND_MUSTACHE: the resolved brand context is INJECTED into a generator's typed inputs
    # under this key (the universal brand seam). It is PLUMBING, not a user form field, so it
    # is stripped from the options-derived + form_inputs payloads the same way the other
    # reserved keys are -- only the run path itself sets it (see _dispatch_capability).
    "brand_context",
})


def _get_structured_generator(kind: str) -> Optional[Any]:
    """Look up a registered structured generator for ``kind``, or None (degrade-never).

    Lazy + sys.path-guarded so THIS module imports no generator package at load time and a
    degraded environment that lacks the package still runs every other capability. ANY
    failure (missing package, broken discovery) returns None -> the generic build path runs
    byte-identically (the zero-regression invariant)."""
    try:
        tools_dir = str(Path(__file__).resolve().parent)
        if tools_dir not in sys.path:
            sys.path.insert(0, tools_dir)
        import capability_generators  # type: ignore[import]

        return capability_generators.get_generator(kind)
    except Exception:
        return None


def _base_catalog_kinds() -> "frozenset[str]":
    """The set of kinds the SHIPPED base capability catalog uses (council A4).

    Source of truth: the registry catalog (cex_capability_registry.base_capabilities) UNION the
    in-module _BASE_CAPABILITIES fallback table -- so a kind is "base" iff some shipped base card
    resolves to it. DEGRADE-NEVER: a missing registry falls back to the in-module table alone.

    Used to GATE the kind fallback at the structured-generator resolution site: a base kind never
    gets a kind lookup (its capabilities collide on the kind), but a tenant's OVERLAY-INTRODUCED
    novel kind -- one NOT in this set -- still may, so an overlay can register a generator by its
    own kind. Computed fresh (not cached) -- it is tiny and a test may swap the catalog."""
    kinds = {v[1] for v in _BASE_CAPABILITIES.values()}
    try:
        registry = _import_registry()
        for rec in registry.base_capabilities():
            k = getattr(rec, "kind", None)
            if isinstance(k, str) and k:
                kinds.add(k)
    except Exception:
        pass  # degrade-never: the in-module table alone is a safe subset
    return frozenset(kinds)


def _resolve_structured_generator(tid: str, cap: str, kind: str) -> Optional[Any]:
    """Resolve the structured generator for a run (council A4): SLUG is the SOLE key.

    Lookup order:
      1. by the capability SLUG (``cap``) -- the unique, authoritative generator key.
      2. by the resolved ``kind`` ONLY when ``kind`` is an OVERLAY-INTRODUCED custom kind (a kind
         NOT in the shipped base catalog). A tenant overlay may register a generator under its own
         novel kind; that path is preserved + GUARDED. A BASE kind gets NO kind fallback -- several
         base capabilities share one kind, so a kind lookup over the last-write-wins registry would
         silently route the wrong generator (e.g. a `content` run emitting a `research` brief).

    DEGRADE-NEVER: any failure -> the slug result (or None) -> the generic build fall-through."""
    by_slug = _get_structured_generator(cap)
    if by_slug is not None:
        return by_slug
    # Slug missed. Only fall back to the KIND lookup for an overlay-custom (non-base) kind.
    try:
        if kind and kind not in _base_catalog_kinds():
            return _get_structured_generator(kind)
    except Exception:
        return None
    return None


def _structured_inputs(
    intent: str,
    options: Optional[Mapping[str, Any]],
    form_inputs: Optional[Mapping[str, Any]] = None,
    brand_context: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    """Build the typed form payload handed to a generator (the INPUT seam, mission BRANDBOOK
    Cell A). Three layers, last-wins:
      1. the dashboard ``options`` form hints (minus plumbing keys) -- the LEGACY path
         (a caller that stuffed fields into options still works, byte-identical);
      2. the EXPLICIT typed ``form_inputs`` payload, RESOLVED for rich any-media ingest
         (an uploaded image -> ``<key>_palette``; an uploaded doc / a URL -> ``<key>_text``;
         text/string/number/enum pass through as-is) -- the NEW, preferred path;
      3. the free-text ``intent`` fallback (only when nothing else set it).
    PURE-ish + TOTAL: resolution is degrade-never (see _resolve_inputs); no form_inputs ->
    byte-identical to the pre-BRANDBOOK behaviour (only the options-derived fields + intent).

    BRAND_MUSTACHE: ``brand_context`` (the unified per-tenant brand dict from
    cex_brand_context.resolve_brand_context) is stamped onto the inputs under the reserved
    ``brand_context`` key AFTER the form-field strip -- so EVERY generator can brand-frame its
    output ({{brand_name}}-aware titles/notes etc.) without it ever being treated as a user
    form field. None (diffusion off / resolve failed) -> no key -> byte-identical to before."""
    inputs: dict[str, Any] = {}
    if options:
        for k, v in options.items():
            if k in _GENERATOR_RESERVED_OPTION_KEYS:
                continue
            inputs[k] = v
    if form_inputs:
        for k, v in _resolve_inputs(form_inputs).items():
            if k in _GENERATOR_RESERVED_OPTION_KEYS:
                continue
            inputs[k] = v
    inputs.setdefault("intent", intent)
    # The brand context is the LAST, authoritative stamp (a caller can never spoof it via a
    # form field -- it was stripped above; only the run path sets it here).
    if isinstance(brand_context, Mapping) and brand_context:
        inputs["brand_context"] = dict(brand_context)
    return inputs


# --------------------------------------------------------------------------- #
# INPUT INGEST RESOLVER (mission BRANDBOOK, Cell A -- the any-media input seam).
#
# The typed ``inputs`` payload a capability run carries (per a capability's input_contract,
# see _docs/specs/spec_input_contract.md) may hold RICH tenant materials, not just scalars:
#   * an UPLOAD (any media) arrives as a ``data:<ct>;base64,<...>`` URI (the frontend's
#     FileReader shape). An IMAGE -> a dominant-color palette at ``inputs[<key>_palette]``;
#     a DOC/text -> extracted text at ``inputs[<key>_text]``.
#   * a URL (a brand site, a spec sheet) -> fetched + reduced to text at ``inputs[<key>_text]``.
#   * text / string / number / enum -> passed through verbatim.
# The RAW value is ALWAYS kept at ``inputs[<key>]``; the resolved facts are ADDITIVE derived
# keys. So a generator that wants the raw upload/URL still has it, and one that wants the
# palette/text reads the derived key (the seam Cell B's brandbook builds to).
#
# DEGRADE-NEVER + TOTAL: no Pillow -> empty palette (+ an honest note key); no markitdown ->
# doc text honestly skipped; a fetch failure -> no _text; the resolver NEVER raises and a
# non-string value passes straight through. Two kill-switches (env): CEX_INPUT_RESOLVE=0
# disables the whole resolver (raw pass-through); CEX_INPUT_FETCH_URLS=0 disables ONLY the
# network URL fetch (the local palette/doc paths still run).
# --------------------------------------------------------------------------- #

# Bounds (defensive): a URL fetch is timed + size-capped; extracted text is char-capped.
_URL_FETCH_TIMEOUT_S = 8
_URL_FETCH_MAX_BYTES = 512 * 1024
_INGEST_MAX_TEXT = 20000


def _input_resolve_enabled() -> bool:
    """True unless CEX_INPUT_RESOLVE is a falsy flag (default ON). The master rollback lever."""
    return _env_switch("CEX_INPUT_RESOLVE")


def _url_fetch_enabled() -> bool:
    """True unless CEX_INPUT_FETCH_URLS is a falsy flag (default ON). Gates the NETWORK side
    effect only -- the local palette/doc-text paths are unaffected when this is off."""
    return _env_switch("CEX_INPUT_FETCH_URLS")


def _parse_data_uri(value: str) -> Optional[Tuple[str, bytes]]:
    """Parse a ``data:[<ct>][;base64],<payload>`` URI -> (content_type, raw_bytes), or None.

    TOTAL: a non-data value, a malformed URI, or a decode failure -> None (never raises)."""
    if not value.startswith("data:") or "," not in value:
        return None
    try:
        header, _, payload = value.partition(",")
        if not payload:
            return None
        meta = header[len("data:"):]
        is_b64 = ";base64" in meta.lower()
        content_type = meta.split(";")[0].strip().lower() or "application/octet-stream"
        if is_b64:
            import base64

            data = base64.b64decode(payload, validate=False)
        else:
            from urllib.parse import unquote_to_bytes

            data = unquote_to_bytes(payload)
        return content_type, data
    except Exception:
        return None


def _image_palette(data: bytes) -> Tuple[list, Optional[str]]:
    """Dominant-color palette of image bytes + an honest note when empty. Delegates to
    cex_color_extract (lazy, sys.path-guarded). DEGRADE-NEVER: tool absent -> ([], note)."""
    try:
        tools_dir = str(Path(__file__).resolve().parent)
        if tools_dir not in sys.path:
            sys.path.insert(0, tools_dir)
        import cex_color_extract  # type: ignore[import]
    except Exception:
        return [], "no palette: cex_color_extract unavailable"
    try:
        palette = cex_color_extract.extract_palette(data)
        note = cex_color_extract.palette_note(data) if not palette else None
        return list(palette), note
    except Exception:
        return [], "no palette: extraction error"


def _strip_html(text: str) -> str:
    """Naive HTML -> plain text (drop script/style + tags, unescape the common entities)."""
    import re

    clean = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", text)
    clean = re.sub(r"(?s)<[^>]+>", " ", clean)
    for a, b in (
        ("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
        ("&quot;", '"'), ("&#39;", "'"), ("&nbsp;", " "),
    ):
        clean = clean.replace(a, b)
    return re.sub(r"\s+", " ", clean).strip()


def _markitdown_text(data: bytes) -> Optional[str]:
    """Extract text from a rich doc (pdf/docx/...) via markitdown if installed, else None.
    DEGRADE-NEVER: markitdown absent / a convert failure -> None (the caller skips honestly)."""
    try:
        from io import BytesIO

        from markitdown import MarkItDown  # type: ignore[import]

        md = MarkItDown()
        result = md.convert_stream(BytesIO(data))
        return getattr(result, "text_content", None) or getattr(result, "markdown", None)
    except Exception:
        return None


def _extract_doc_text(data: bytes, content_type: str) -> Optional[str]:
    """Best-effort text from an uploaded document's bytes. text/* + json/xml decode directly
    (html is tag-stripped); richer formats go through markitdown when present; anything else
    is honestly skipped (None). TOTAL -- never raises. Char-capped at _INGEST_MAX_TEXT."""
    if not data:
        return None
    ct = (content_type or "").lower()
    text: Optional[str] = None
    if (
        ct.startswith("text/")
        or ct in ("application/json", "application/xml")
        or ct.endswith("+json")
        or ct.endswith("+xml")
    ):
        try:
            text = data.decode("utf-8", errors="replace")
        except Exception:
            return None
        if ct in ("text/html", "application/xhtml+xml"):
            text = _strip_html(text)
    else:
        text = _markitdown_text(data)
    if not text:
        return None
    text = text.strip()
    return text[:_INGEST_MAX_TEXT] or None


def _looks_fetchable_url(value: str) -> bool:
    """True for an http(s) URL safe to fetch. SSRF hygiene: refuse loopback / link-local /
    private-range / *.local hosts and absurd lengths. TOTAL -- never raises."""
    v = value.strip()
    if not (v.startswith("http://") or v.startswith("https://")):
        return False
    if len(v) > 2048 or any(c in v for c in (" ", "\n", "\r", "\t")):
        return False
    try:
        from urllib.parse import urlparse

        host = (urlparse(v).hostname or "").lower()
    except Exception:
        return False
    if not host or "." not in host:
        return False
    if host in ("localhost", "0.0.0.0", "::1") or host.endswith((".local", ".internal")):
        return False
    if host.startswith(("127.", "10.", "169.254.", "192.168.")):
        return False
    if host.startswith("172."):
        parts = host.split(".")
        if len(parts) >= 2 and parts[1].isdigit() and 16 <= int(parts[1]) <= 31:
            return False
    return True


def _fetch_url_text(url: str) -> Optional[str]:
    """Fetch an http(s) URL (timed + size-capped) and reduce it to plain text. Returns None
    on any failure or for non-text content (an image URL is NOT fabricated into text).
    DEGRADE-NEVER + TOTAL: never raises; bounded by _URL_FETCH_TIMEOUT_S/_MAX_BYTES."""
    try:
        import urllib.request

        req = urllib.request.Request(
            url, headers={"User-Agent": "cexai-input-ingest/1.0"}
        )
        with urllib.request.urlopen(req, timeout=_URL_FETCH_TIMEOUT_S) as resp:  # noqa: S310
            ctype = (resp.headers.get("Content-Type") or "").lower()
            raw = resp.read(_URL_FETCH_MAX_BYTES + 1)
    except Exception:
        return None
    if not raw:
        return None
    raw = raw[:_URL_FETCH_MAX_BYTES]
    if ctype.startswith("image/"):
        return None  # an image URL has no text; palette-from-url is out of this seam's scope
    try:
        text = raw.decode("utf-8", errors="replace")
    except Exception:
        return None
    if "html" in ctype or "<html" in text[:512].lower() or "<body" in text[:2000].lower():
        text = _strip_html(text)
    else:
        text = " ".join(text.split())
    return text[:_INGEST_MAX_TEXT].strip() or None


def _resolve_inputs(form_inputs: Mapping[str, Any]) -> dict[str, Any]:
    """Resolve a typed ``inputs`` payload for rich any-media ingest (the BRANDBOOK Cell A
    seam). For each entry the RAW value is kept at ``[<key>]``; ADDITIVE derived facts are
    added: an uploaded image -> ``[<key>_palette]`` (+ ``[<key>_palette_note]`` when empty);
    an uploaded doc or a fetchable URL -> ``[<key>_text]``. Non-string values + plain text
    pass through untouched. TOTAL + DEGRADE-NEVER (kill-switch CEX_INPUT_RESOLVE=0 -> raw
    pass-through; CEX_INPUT_FETCH_URLS=0 -> skip only the network fetch)."""
    out: dict[str, Any] = {}
    if not form_inputs:
        return out
    # Master kill-switch: copy through raw (no palette/text/fetch), preserving order.
    if not _input_resolve_enabled():
        for key, value in form_inputs.items():
            out[str(key)] = value
        return out
    fetch_on = _url_fetch_enabled()
    for key, value in form_inputs.items():
        k = str(key)
        out[k] = value  # always keep the raw value
        if not isinstance(value, str) or not value:
            continue
        parsed = _parse_data_uri(value)
        if parsed is not None:
            content_type, data = parsed
            if content_type.startswith("image/"):
                palette, note = _image_palette(data)
                out[k + "_palette"] = palette
                if note:
                    out[k + "_palette_note"] = note
            else:
                doc_text = _extract_doc_text(data, content_type)
                if doc_text:
                    out[k + "_text"] = doc_text
            continue
        if fetch_on and _looks_fetchable_url(value):
            url_text = _fetch_url_text(value)
            if url_text:
                out[k + "_text"] = url_text
    return out


# DUAL2 kill-switch: the dual-output projection is ON by default -- the founder directive
# (2026-06-21) makes it the UNIVERSAL capability output contract (every capability emits one
# asset with two coupled faces). Set CEX_DUAL_OUTPUT=0 to disable it: the run path becomes
# byte-identical to the pre-DUAL2 behaviour (a no-code rollback lever for N07 / operators).
def _dual_output_enabled() -> bool:
    """True unless CEX_DUAL_OUTPUT is set to a falsey value (0/false/no/off). TOTAL."""
    return _env_switch("CEX_DUAL_OUTPUT")


# ADWIRE W3 kill-switch: the `ads` capability's SPECIALIZED conversion human face (the
# product_ad mold) is ON by default. Set CEX_AD_MOLD=0 to disable it: the ads run then
# uses the GENERIC dual human_html like every other capability (a no-code rollback lever).
def _ad_mold_enabled() -> bool:
    """True unless CEX_AD_MOLD is set to a falsey value (0/false/no/off). TOTAL."""
    return _env_switch("CEX_AD_MOLD")


def _render_ad_mold_html(
    cap: str,
    payload: Mapping[str, Any],
    inputs: Mapping[str, Any],
    dual: Mapping[str, Any],
    tenant: str,
) -> Optional[str]:
    """Render the SPECIALIZED product-ad mold human_html for the `ads` capability (ADWIRE
    W3). The mold is the conversion-grade HUMAN face the founder's brand-voice copy fills;
    it REPLACES only ``dual['human_html']`` (machine_md / media_slots / frontmatter / id
    stay coupled + unchanged -- the mold is the human face only).

    GENERIC routing, ads-specific binding: cex_ad_mold_bind maps the ads output_sections +
    the run inputs + the dual's resolved media_slots + the tenant brand tokens into the
    emit_product_ad ``data`` shape and emits the HTML.

    FAIL-SAFE + TOTAL: kill-switch off, import failure, no usable copy, or any bind/emit
    surprise ALL return None -> the caller keeps the generic dual human_html (degrade-never;
    the ads run is NEVER broken). NEVER leaks a secret (a pure projection of public copy +
    brand tokens + media srcs -- no api_key is ever in scope)."""
    if not _ad_mold_enabled():
        return None
    try:
        tools_dir = str(Path(__file__).resolve().parent)
        if tools_dir not in sys.path:
            sys.path.insert(0, tools_dir)
        import cex_ad_mold_bind  # type: ignore[import]
    except Exception:
        return None
    try:
        html = cex_ad_mold_bind.build_ad_human_html(
            payload,
            inputs,
            media_slots=dual.get("media_slots"),
            tenant_id=tenant,
        )
    except Exception:
        return None
    return html if isinstance(html, str) and html.strip() else None


def _render_dual_output(
    cap: str,
    payload: Mapping[str, Any],
    generator: Any,
    inputs: Mapping[str, Any],
    *,
    tenant: Optional[str] = None,
) -> Optional[dict]:
    """Project a structured payload + the generator's DISCOVERED media into the dual-surface
    asset (mission DUAL2; founder directive 2026-06-21): {machine_md, human_html,
    media_slots, id, capability, frontmatter, real}.

    GENERIC -- no per-generator code here. capability_generators.resolve_media discovers the
    generator module's OPTIONAL media hooks (the canonical ``media_requests``/``produced_media``
    pair, OR a prefixed ``<prefix>_media_requests``/``<prefix>_produced_media`` pair such as
    marketplace_listing's ``listing_*`` / research's ``research_*``) and feeds them to
    cex_dual_output.to_dual_output. A produced media src -> a real <img>/<video>/<audio>; an
    un-produced one -> an editable upload-fallback slot (NEVER fabricated). A generator with
    no media hooks -> to_dual_output's default single empty hero slot (the founder's
    "editable media affordance everywhere").

    FAIL-SAFE + TOTAL: the kill-switch off, an import failure, a discovery failure, OR a
    render failure ALL return None -> the capability run still succeeds with no dual face
    (degrade-never; the structured artifact is untouched). NEVER leaks a secret: a pure
    projection of the structured data + public media srcs -- no api_key is ever in scope."""
    if not _dual_output_enabled():
        return None
    try:
        tools_dir = str(Path(__file__).resolve().parent)
        if tools_dir not in sys.path:
            sys.path.insert(0, tools_dir)
        import capability_generators  # type: ignore[import]
        from cex_dual_output import to_dual_output  # type: ignore[import]
    except Exception:
        return None
    try:
        media_requests, produced_media = capability_generators.resolve_media(generator, inputs)
    except Exception:
        media_requests, produced_media = None, None
    try:
        dual = to_dual_output(
            cap,
            payload,
            tenant=tenant,
            media_requests=media_requests,
            produced_media=produced_media,
        )
    except Exception:
        return None
    return dual if isinstance(dual, dict) else None


# SPEC 10 W4 kill-switch: the GENERIC-fallback dual face (the plain CEXAgent.build text run
# that has NO structured generator) is ON by default -- it completes the founder's UNIVERSAL
# dual_output contract (EVERY capability now emits both faces, not just the 16 structured
# ones). Set CEX_GENERIC_DUAL=0 to disable ONLY the generic-fallback face: the structured
# routes (governed by CEX_DUAL_OUTPUT) are untouched, and the generic build becomes
# byte-identical to its pre-W4 behaviour (a no-code rollback lever, mirroring CEX_AD_MOLD).
def _generic_dual_output_enabled() -> bool:
    """True unless CEX_GENERIC_DUAL is set to a falsey value (0/false/no/off). TOTAL.

    Independent of the structured CEX_DUAL_OUTPUT switch: a deployment may keep structured
    dual faces ON while rolling back only the generic-fallback face (or vice-versa)."""
    return _env_switch("CEX_GENERIC_DUAL")


def _generic_struct_from_artifact(
    cap: str, artifact: str, *, passed: bool, score: float,
) -> dict:
    """Project a GENERIC CEXAgent.build text ``artifact`` (frontmatter+markdown body) into the
    minimal StructuredOutput shape to_dual_output consumes -- WITHOUT fabricating structure.

    The generic build's deliverable is a single markdown document, not the typed
    ``output_sections`` the 16 generators emit. Rather than invent fake section tables, this
    projects the WHOLE artifact verbatim into ONE list section ("Conteudo") -- an honest,
    lossless carry of exactly what the model produced. An EMPTY/whitespace artifact yields a
    single honest-empty list item ("(sem conteudo)"), NEVER fabricated prose. The score is the
    0..10 display score (the dual face's badge reads ``real``/passed off this).

    PURE + TOTAL: never raises; an unusable artifact still yields a valid-but-thin struct."""
    body = artifact if isinstance(artifact, str) else ""
    # Carry the markdown VERBATIM as list lines (line-split) so the human face renders the
    # produced text faithfully and the machine .md re-states it -- never re-interpreted.
    lines = [ln for ln in body.splitlines() if ln.strip()]
    items = lines if lines else ["(sem conteudo)"]  # honest-empty, never fabricated
    return {
        "mold_id": cap,
        "output_sections": [
            {"title": "Conteudo", "layout": "list", "items": items},
        ],
        "real": bool(body.strip()),  # an empty build is honestly NOT a real produced asset
        "passed": bool(passed),
        "score": float(score) if isinstance(score, (int, float)) else 0.0,
        "artifact": body,
        "notes": [],
    }


def _render_generic_dual_output(
    cap: str,
    artifact: str,
    *,
    passed: bool,
    score: float,
    tenant: Optional[str] = None,
) -> Optional[dict]:
    """Project a GENERIC CEXAgent.build text artifact into the dual-surface asset (SPEC 10 W4).

    This is the analogue of _render_dual_output for the NON-structured route: the generic
    fallback (STEP 4) produces a plain markdown ``artifact`` and previously carried NO dual
    face, so those capabilities were the LAST gap in the founder's universal dual_output
    contract. It REUSES the SAME emitter (cex_dual_output.to_dual_output) + the SAME envelope
    the 16 structured generators inherit -- it does NOT hand-roll a second dual-output shape.

    There is no generator here, so there are NO media hooks -> to_dual_output falls back to its
    default single EMPTY hero slot (the founder's "editable media affordance everywhere"),
    NEVER a fabricated asset. An empty/short artifact -> an honest empty face (a single
    "(sem conteudo)" item + the empty hero dropzone), never invented media or prose.

    FAIL-SAFE + TOTAL: the W4 kill-switch off (CEX_GENERIC_DUAL=0), the master kill-switch off
    (CEX_DUAL_OUTPUT=0), an import failure, or any render surprise ALL return None -> the
    generic run still succeeds with no dual face (degrade-never; the ``artifact`` is untouched,
    byte-identical to pre-W4). NEVER leaks a secret: a pure projection of the produced public
    text -- no api_key is ever in scope. The score is the 0..10 display score."""
    if not _generic_dual_output_enabled() or not _dual_output_enabled():
        return None
    try:
        tools_dir = str(Path(__file__).resolve().parent)
        if tools_dir not in sys.path:
            sys.path.insert(0, tools_dir)
        from cex_dual_output import to_dual_output  # type: ignore[import]
    except Exception:
        return None
    struct = _generic_struct_from_artifact(cap, artifact, passed=passed, score=score)
    try:
        # media_requests=None -> the default empty hero slot (no media hooks on a text build).
        dual = to_dual_output(cap, struct, tenant=tenant)
    except Exception:
        return None
    return dual if isinstance(dual, dict) else None


# --------------------------------------------------------------------------- #
# B2 brand-setup seam -- write a passing brandbook run's output back to the tenant
# moldgen overlay (the brand source cex_brand_context.resolve_brand_context reads). Imported
# LAZILY + sys.path-guarded (the same import-light discipline the registry/brand-context/
# action-queue seams use) so THIS module loads even if cex_brand_writeback is absent. TOTAL +
# FAIL-SAFE: any surprise leaves the produced brandbook untouched (degrade-never).
# --------------------------------------------------------------------------- #
# Tests may set cex_run_capability.write_brand_overlay = fake. When None (default), the
# write-back helper imports the real cex_brand_writeback.write_brand_overlay lazily.
write_brand_overlay: Any = None


def _writeback_brand_overlay(
    tid: str,
    payload: Mapping[str, Any],
    inputs: Mapping[str, Any],
    result: "CapabilityResult",
) -> None:
    """Write the brandbook ``payload`` back to the tenant moldgen overlay (in place on result).

    The founder's brand-setup write: a PASSING brandbook run's structured output IS the brand
    config, so persist it where resolve_brand_context reads -> every other capability re-brands.
    A logo image data-uri carried in the run inputs (the dashboard file control) becomes the
    overlay logo. ADDITIVE: on success a short note records the path + token count; on a refusal
    / failure a short honest note is appended -- the produced brandbook is NEVER discarded.
    DEGRADE-NEVER + TOTAL: a missing module is swallowed silently (truly optional dependency).
    R-187 fix: a REAL write failure (the resolved `writer` call raising) is now RECORDED into
    `result.errors` instead of being swallowed by the same bare except as the optional-import
    guard -- the caller (and the founder) can see that the brand overlay was NOT written and why.
    The produced brandbook is still NEVER discarded either way (this function only appends a
    note; it never mutates or drops `payload`/`result.artifact`). No api_key is ever in scope
    here (pure brand data)."""
    try:
        writer = write_brand_overlay
        if writer is None:
            tools_dir = str(Path(__file__).resolve().parent)
            if tools_dir not in sys.path:
                sys.path.insert(0, tools_dir)
            import cex_brand_writeback  # type: ignore[import]

            writer = cex_brand_writeback.write_brand_overlay
    except Exception:
        # Belt-and-braces: cex_brand_writeback is a genuinely optional module -- its absence
        # never breaks a brandbook run that already succeeded, and there is nothing actionable
        # to record (the write-back seam simply isn't available in this environment).
        return

    try:
        # The logo data-uri: the run's typed inputs carry it under the brandbook contract key
        # (the file control sends the picked image as a data: uri). Absent -> no logo override.
        logo_uri = None
        if isinstance(inputs, Mapping):
            cand = inputs.get("brand_materials_data_uri") or inputs.get("brand_logo")
            if isinstance(cand, str) and cand.strip().startswith("data:image"):
                logo_uri = cand.strip()
        res = writer(tid, payload, logo_data_uri=logo_uri)
        ok = bool(getattr(res, "ok", False))
        if ok:
            result.errors.append(
                "brand_overlay_written: %s tokens from palette (brand=%s) -- every capability "
                "now re-brands from this overlay"
                % (int(getattr(res, "tokens_written", 0) or 0), getattr(res, "brand_name", ""))
            )
        else:
            result.errors.append(
                "brand_overlay_not_written: %s (the brandbook is intact; no brand source changed)"
                % str(getattr(res, "reason", "unknown"))
            )
    except Exception as exc:
        # A REAL failure calling the resolved writer -- record it honestly (this is the bug
        # R-187 fixes: this used to be swallowed by the same except as the optional-import
        # guard above). The brandbook run itself still stands; only the write-back note changes.
        result.errors.append("brand_overlay_not_written: writer raised %s: %s"
                             % (type(exc).__name__, str(exc)))


def _generator_accepts_resolved_kind(generator: Any) -> bool:
    """True iff ``generator`` (a structured generator's ``build`` callable) accepts a
    ``resolved_kind`` keyword -- either an explicit parameter or a ``**kwargs`` catch-all
    (mission R-333). TOTAL + degrade-never: any introspection surprise (a non-function
    object, a builtin with no inspectable signature) -> False, the safe default that
    reproduces the pre-R-333 2-argument call exactly -- the R-333 kind-threading is simply
    skipped for that generator, never a crash. This lets the ONE call site below thread the
    resolved kind into every generator that has adopted the new kwarg (all 21 shipped
    generators) while staying byte-identical for any direct/legacy/test fake that has not."""
    try:
        import inspect

        sig = inspect.signature(generator)
    except (TypeError, ValueError):
        return False
    for p in sig.parameters.values():
        if p.kind == inspect.Parameter.VAR_KEYWORD or p.name == "resolved_kind":
            return True
    return False


def _run_structured_generator(
    tid: str,
    cap: str,
    nucleus: str,
    kind: str,
    pillar: str,
    intent: str,
    credential: Credential,
    generator: Any,
    *,
    db: Optional[DbWriter] = None,
    options: Optional[Mapping[str, Any]] = None,
    form_inputs: Optional[Mapping[str, Any]] = None,
    brand_context: Optional[Mapping[str, Any]] = None,
) -> Optional[CapabilityResult]:
    """Run a registered structured generator and build its CapabilityResult.

    The deny-by-default tenant + enabled gates ALREADY ran in run_capability before this
    branch (it inherits the same scoping). The credential is passed THROUGH to the
    generator (deterministic generators ignore it; an LLM generator validates/uses it
    itself). Returns:
      * a CapabilityResult with ``structured`` = the generator payload on success;
      * None when the generator RAISES or returns a non-dict -> the caller FALLS BACK to
        the generic CEXAgent.build (degrade-never; the endpoint never crashes).
    PERSIST is best-effort-after-pass and rides the structured payload in meta (the SAME
    seam the research_universe route uses) so /results can re-render it.

    BRAND_MUSTACHE: ``brand_context`` (resolved once per run) is stamped onto the generator's
    inputs (under the reserved ``brand_context`` key) so the generator can brand-frame its
    output. None -> byte-identical to before (degrade-never).

    R-333: ``kind`` (the RESOLVED per-tenant kind this run already carries -- e.g. a real
    <tenant> tenant's overlay resolves ``crm`` to ``<tenant>_crm``) is threaded to the generator as
    ``resolved_kind`` so its artifact-JSON self-description matches ``res.kind`` instead of
    silently reverting to the generator's own module KIND constant. Gated by
    ``_generator_accepts_resolved_kind`` so a generator/fake that predates the new kwarg is
    called exactly as before (degrade-never; no TypeError, no behavior change)."""
    inputs = _structured_inputs(intent, options, form_inputs, brand_context)
    try:
        if _generator_accepts_resolved_kind(generator):
            payload = generator(inputs, credential=credential, resolved_kind=kind)
        else:
            payload = generator(inputs, credential=credential)
    except Exception:
        # DEGRADE-NEVER: a regressed generator must not crash the endpoint. Signal the
        # caller to fall back to the generic build. No secret is ever in scope here.
        return None
    if not isinstance(payload, dict) or not payload.get("output_sections"):
        # A generator that produced nothing usable -> fall back (never a half-built result).
        return None

    return _build_structured_result(
        tid, cap, nucleus, kind, pillar, payload, inputs,
        generator=generator, db=db, options=options,
    )


def _build_structured_result(
    tid: str,
    cap: str,
    nucleus: str,
    kind: str,
    pillar: str,
    payload: Mapping[str, Any],
    inputs: Mapping[str, Any],
    *,
    generator: Any = None,
    db: Optional[DbWriter] = None,
    options: Optional[Mapping[str, Any]] = None,
) -> CapabilityResult:
    """Assemble a CapabilityResult from a StructuredOutput ``payload`` (the shared result builder).

    Extracted from _run_structured_generator so BOTH the structured-generator route AND the
    lead-gen real-orchestrator route (spec 05_leadgen_suite Phase 1b -- whose orchestrator returns
    the SAME StructuredOutput shape) build their result IDENTICALLY: score scaling, the DUAL2
    dual-output projection (+ the ads-mold / brandbook special cases), and best-effort-after-pass
    persist via the audited db.persist_artifact seam. ``generator`` is used ONLY for media-hook
    discovery (None -> the to_dual_output default empty hero slot). PURE-ish + degrade-never."""
    artifact = str(payload.get("artifact", "") or "")
    passed = bool(payload.get("passed", False))
    # StructuredOutput.score is 0..1 (the generator contract). The outcome-strip ScoreMeter
    # expects 0..10, so a 0..1 score is scaled up; a generator already on 0..10 (>1.0) is
    # passed through unscaled. The raw 0..1 score stays inside ``structured`` untouched.
    raw_score = 0.0
    try:
        raw_score = float(payload.get("score", 0.0) or 0.0)
    except (TypeError, ValueError):
        raw_score = 0.0
    display_score = raw_score * 10.0 if 0.0 <= raw_score <= 1.0 else raw_score

    result = CapabilityResult(
        tenant_id=tid,
        capability=cap,
        kind=kind,
        pillar=pillar,
        nucleus=nucleus,
        artifact=artifact,
        score=display_score,
        passed=passed,
        status="produced",
        model_used="",                 # deterministic/typed generators use no LLM model
        trace="",
        errors=[],
        structured=dict(payload),
    )

    # DUAL2: project the structured output + the generator's DISCOVERED media into the
    # dual-surface asset (human HTML audiovisual face + machine .md face). FAIL-SAFE: a None
    # result (kill-switch off / no media hooks / any failure) simply leaves dual_output unset
    # -- the structured run itself is never affected (degrade-never).
    dual = _render_dual_output(cap, payload, generator, inputs, tenant=tid)
    if dual is not None:
        # ADWIRE W3: the `ads` capability gets a SPECIALIZED conversion human face -- the
        # product_ad mold the brand-voice copy fills -- replacing ONLY the generic
        # human_html. machine_md / media_slots / frontmatter / id stay coupled + unchanged
        # (the mold is the HUMAN face only; the AI still reads the full structured .md).
        # FAIL-SAFE: a None render (kill-switch off / no copy / any surprise) leaves the
        # generic human_html in place -- the ads run is never broken (degrade-never). Other
        # capabilities never reach this branch (cap == "ads" only).
        if cap == "ads":
            _ad_html = _render_ad_mold_html(cap, payload, inputs, dual, tid)
            if _ad_html:
                dual["human_html"] = _ad_html
        result.dual_output = dual

    # B2 BRAND-SETUP: a PASSING `brandbook` run is the founder's brand-setup path -- its output
    # IS the brand config (the {{brand_*}} VALUES). Write it back to the tenant moldgen overlay
    # (the source cex_brand_context.resolve_brand_context reads) so AFTER this run every OTHER
    # capability re-personalizes from the NEW brand (the open-mustache invariant). The brand is
    # never hardcoded -- this run SETS it. FAIL-SAFE + TOTAL: a non-ok / failed write is a no-op
    # (an honest note is appended); the produced brandbook is NEVER discarded. Other capabilities
    # never reach this branch (cap == "brandbook" only). Gated on ``passed`` so a half-built /
    # nameless brandbook never overwrites a tenant's brand.
    if cap == "brandbook" and passed:
        _writeback_brand_overlay(tid, payload, inputs, result)

    # PERSIST: best-effort-after-pass via the SAME audited seam the build path uses; the
    # structured payload rides in meta['structured'] so a row re-projects on /results. For the
    # lead-gen route this is the CRM seed (spec 4.5): a passed run persists the leads as a
    # tenant_data row (kind=research_pipeline), payload = the structured leads -- RLS-scoped.
    if db is not None and passed:
        meta: dict[str, Any] = {
            "table": _TENANT_DATA_TABLE,
            "pillar": pillar,
            "nucleus": nucleus,
            "mold_id": payload.get("mold_id"),
            "structured": dict(payload),
        }
        if options and "meta" in options and isinstance(options["meta"], Mapping):
            meta.update(dict(options["meta"]))
        # DUAL2: persist the MACHINE face (.md + media ledger) tenant-scoped -- the canonical,
        # tenant-AI-readable surface (founder directive). The HUMAN html face is derivative
        # (re-renderable from the structured payload), so it is NOT stored -- keeps the row lean.
        if dual is not None:
            meta["dual_output"] = {
                "id": dual.get("id"),
                "machine_md": dual.get("machine_md"),
                "media_slots": dual.get("media_slots"),
            }
        try:
            record_id = db.persist_artifact(tid, cap, kind, artifact, meta)
            result.record_id = str(record_id) if record_id is not None else None
            result.persisted = result.record_id is not None
            result.status = "persisted" if result.persisted else "produced_unpersisted"
        except Exception as exc:  # DB failure: surface, never discard the produced output.
            result.persisted = False
            result.status = "produced_unpersisted"
            result.errors.append("persist_failed: %s: %s" % (type(exc).__name__, exc))

    return result


# --------------------------------------------------------------------------- #
# Action-queue seam (mission COMPLETE2 W2b) -- the post-run open-items/next-actions
# deriver. Imported LAZILY + sys.path-guarded (the same import-light discipline the
# registry/generator seams use) so THIS module loads even if cex_action_queue is absent,
# and a degraded environment still runs every capability. Bound as a module-level name so
# a test can monkeypatch it. When None (default), the attach helper imports it lazily.
# --------------------------------------------------------------------------- #
def _import_action_queue() -> Any:
    """Import cex_action_queue from the _tools dir (lazy, sys.path-guarded). Returns the module."""
    tools_dir = str(Path(__file__).resolve().parent)
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    import cex_action_queue  # type: ignore[import]

    return cex_action_queue


# Tests may set cex_run_capability.derive_action_queue = fake. When None (default), the attach
# helper imports the real deriver lazily.
derive_action_queue: Any = None


# --------------------------------------------------------------------------- #
# Brand-context seam (mission BRAND_MUSTACHE) -- the UNIVERSAL brand diffusion point. Resolved
# ONCE per run in _dispatch_capability and threaded into every structured generator's inputs so
# EVERY capability output can be brand-personalized ({{brand_*}} mustache, filled per-tenant).
# Imported LAZILY + sys.path-guarded (the same import-light discipline the registry/generator/
# action-queue seams use) so THIS module loads even if cex_brand_context is absent, and a
# degraded environment still runs every capability. Bound as a module-level name so a test can
# monkeypatch it. When None (default), the resolver imports it lazily.
# --------------------------------------------------------------------------- #
def _import_brand_context() -> Any:
    """Import cex_brand_context from the _tools dir (lazy, sys.path-guarded). Returns the module."""
    tools_dir = str(Path(__file__).resolve().parent)
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    import cex_brand_context  # type: ignore[import]

    return cex_brand_context


# Tests may set cex_run_capability.resolve_brand_context = fake. When None (default), the run
# resolver imports the real cex_brand_context.resolve_brand_context lazily.
resolve_brand_context: Any = None


def _resolve_brand_context_for_run(tid: str) -> Optional[dict]:
    """Resolve the unified per-tenant brand context for THIS run, or None (degrade-never).

    Returns None when the diffusion kill-switch (CEX_BRAND_DIFFUSE=0) is off, when
    cex_brand_context is unavailable, or on ANY resolve surprise -> the run path then injects
    no brand_context and behaves byte-identically to the pre-mustache contract (zero-regression).
    NEVER raises, NEVER fabricates, NEVER hardcodes any ONE tenant's brand (the resolver enforces
    all three). The
    api_key is never in scope here (the context is pure brand data: name/tokens/voice/palette)."""
    try:
        mod = _import_brand_context()
    except Exception:
        return None
    # Honour the kill-switch (default ON). Off -> no diffusion (byte-identical pre-mustache).
    try:
        if not mod.brand_diffuse_enabled():
            return None
    except Exception:
        pass  # a malformed switch -> default-on posture (resolve below)
    try:
        resolver = resolve_brand_context if resolve_brand_context is not None else mod.resolve_brand_context
        ctx = resolver(tid)
        return ctx if isinstance(ctx, dict) and ctx else None
    except Exception:
        return None


def _attach_action_queue(result: "CapabilityResult") -> None:
    """Attach result.action_queue = derive_action_queue(result), in place. DEGRADE-NEVER +
    TOTAL: a missing module, a monkeypatched fake that misbehaves, or ANY derivation surprise
    leaves action_queue at its default None -- the produced result is NEVER altered or
    discarded. The queue is purely additive metadata; the run's contract is untouched."""
    try:
        deriver = derive_action_queue if derive_action_queue is not None else _import_action_queue().derive_action_queue
        queue = deriver(result)
        if isinstance(queue, dict):
            result.action_queue = queue
    except Exception:
        # The deriver is self-guarding too; this is belt-and-braces so the wrapper can never
        # break a run that already succeeded. No secret is ever in scope here.
        return


# --------------------------------------------------------------------------- #
# EDIT->REFLECT product hydration (arch-council wave 0.5, Group B / B2). Hydrates
# inputs['product_record'] from the tenant's CURRENT product data (tenant_data
# kind='products', via the audited cex_tenant_knowledge reader -> the SAME isolation seam)
# BEFORE an ad/catalog dispatch, so the run reflects the just-edited product. Gated behind
# CEX_PRODUCT_HYDRATE (default ON); degrade-never to today's behaviour on any miss/failure.
# --------------------------------------------------------------------------- #
def _product_hydrate_enabled() -> bool:
    """True unless CEX_PRODUCT_HYDRATE is a falsy flag (default ON). The rollback lever: off
    -> no hydration -> byte-identical to the pre-B2 contract (zero-regression)."""
    return _env_switch(_ENV_PRODUCT_HYDRATE)


def _is_product_capability(cap: str, kind: str) -> bool:
    """True iff a run resolving to (slug=cap, kind=kind) is an ad/catalog run that benefits
    from a product_record. SLUG-FIRST (the council A4 disambiguation: ``ads`` resolves to the
    shared ``prompt_template`` kind, so only the slug -- never the kind -- triggers the ads
    case); a catalog KIND (marketplace_listing / product_ad) triggers an overlay-custom slug.
    PURE + TOTAL."""
    if (cap or "").strip() in _PRODUCT_HYDRATE_SLUGS:
        return True
    if (kind or "").strip() in _PRODUCT_HYDRATE_KINDS:
        return True
    return False


def _extract_product_ref(inputs: Optional[Mapping[str, Any]]) -> str:
    """The product ref (sku / slug / record_id) carried in the run inputs, or '' (PURE +
    TOTAL). Checks _PRODUCT_REF_KEYS in priority order; the first non-empty scalar wins. A
    non-string scalar (e.g. a numeric sku) is stringified; a dict/list value is ignored (a
    ref is a scalar). degrade-never: no inputs / no ref key -> ''."""
    if not isinstance(inputs, Mapping):
        return ""
    for k in _PRODUCT_REF_KEYS:
        v = inputs.get(k)
        if v is None or isinstance(v, (Mapping, list, tuple)):
            continue
        s = str(v).strip()
        if s:
            return s
    return ""


def _hydrate_product_record(
    tid: str,
    cap: str,
    kind: str,
    db_reader: Optional["DbReader"],
    inputs: Optional[Mapping[str, Any]],
) -> Optional[dict]:
    """Resolve inputs to a NEW dict with inputs['product_record'] hydrated from the tenant's
    CURRENT product data, or None when nothing should change (so the caller keeps the
    original inputs object byte-for-byte -- the zero-regression contract).

    Fires ONLY when: the hydration gate is ON, a DbReader is injected, the run is an
    ad/catalog capability (_is_product_capability), the inputs carry a product ref, and the
    inputs do NOT already carry an explicit product_record (an explicit one always wins --
    the edge may pass it inline). The reader (cex_tenant_knowledge.TenantKnowledgeReader)
    reads tenant_data kind='products' THROUGH the SAME audited adapter + verified-claim bind
    the writer uses, so the lookup is tenant-scoped + RLS-enforced -- NOT a raw cross-tenant
    query. The matched record IS the product the admin last edited (the EDIT->REFLECT loop).

    DEGRADE-NEVER + TOTAL: gate off / no reader / not a product cap / no ref / an explicit
    record already present / no match / ANY reader surprise -> None (the run proceeds with
    the inputs unchanged). NEVER raises. NEVER fabricates a record. No secret is in scope."""
    if db_reader is None or not _product_hydrate_enabled():
        return None
    if not _is_product_capability(cap, kind):
        return None
    # An explicit product_record (passed inline by the edge / a test) always wins -- never
    # overwrite it with a catalog read.
    if isinstance(inputs, Mapping) and isinstance(inputs.get(_PRODUCT_RECORD_KEY), Mapping):
        if inputs.get(_PRODUCT_RECORD_KEY):
            return None
    ref = _extract_product_ref(inputs)
    if not ref:
        return None
    try:
        record = db_reader.find_product(tid, ref)
    except Exception:
        # DEGRADE-NEVER: a reader surprise must never break a run -> proceed unchanged.
        return None
    if not isinstance(record, Mapping) or not record:
        return None  # no current product for this ref -> proceed unchanged (never fabricate).
    merged: dict = dict(inputs) if isinstance(inputs, Mapping) else {}
    merged[_PRODUCT_RECORD_KEY] = dict(record)
    return merged


# --------------------------------------------------------------------------- #
# LEADS injection (the CRM / Sales-Assistant LIVE-leads seam). MIRRORS
# _hydrate_product_record exactly: an additive, opt-in, degrade-never read that folds the
# tenant's CURRENT managed leads (tenant_data kind='contacts') into inputs['leads'] BEFORE
# dispatch, so the CRM funnel + the Sales Assistant operate on REAL rows instead of the
# honest-empty fallback. The generators consume inputs['leads'] (crm.build directly;
# sales_assistant._select_lead via inputs['leads'] + lead_id). NEVER fabricates a row.
# --------------------------------------------------------------------------- #
def _is_leads_consuming_capability(cap: str) -> bool:
    """True iff a run resolving to (slug=cap) is one that consumes a leads list (crm /
    sales_assistant). SLUG-ONLY (the council A4 disambiguation: both resolve to shared kinds,
    so the kind is NOT a safe trigger -- only the unambiguous slug). PURE + TOTAL."""
    return (cap or "").strip() in _LEADS_CONSUMING_SLUGS


def _has_explicit_leads(inputs: Optional[Mapping[str, Any]]) -> bool:
    """True iff ``inputs`` already carries a NON-EMPTY ``leads`` list (an explicit payload the
    edge / a test passed). An explicit leads list always wins -- never overwrite it with a
    catalog read (mirrors the explicit-product_record-wins rule). PURE + TOTAL."""
    if not isinstance(inputs, Mapping):
        return False
    existing = inputs.get(_LEADS_INPUTS_KEY)
    return isinstance(existing, (list, tuple)) and len(existing) > 0


def _lead_row_to_dict(row: Any) -> Optional[dict]:
    """Project ONE managed-entity row payload into a plain lead dict, or None for a non-mapping
    row (skipped, never fabricated). PASS-THROUGH: the saved entity fields are kept verbatim so
    the generators read whatever real keys the row carries (nome/status + any leadgen-shape
    keys) and degrade-never on the rest. NEVER invents a field. PURE + TOTAL."""
    if not isinstance(row, Mapping):
        return None
    return dict(row)


def _inject_leads_entity(
    tid: str,
    cap: str,
    db_reader: Optional["DbReader"],
    inputs: Optional[Mapping[str, Any]],
) -> Optional[Mapping[str, Any]]:
    """Resolve inputs to a NEW mapping with inputs['leads'] folded from the tenant's CURRENT
    managed-leads rows (tenant_data kind='contacts'), or None when nothing should change (so
    the caller keeps the original inputs object byte-for-byte -- the zero-regression contract).

    Fires ONLY when: a DbReader is injected, the run is a leads-consuming capability
    (crm / sales_assistant, by SLUG), and the inputs do NOT already carry a non-empty
    ``leads`` list (an explicit payload always wins). The reader reads tenant_data
    kind='contacts' THROUGH the SAME audited adapter + verified-claim bind the writer uses, so
    the read is tenant-scoped + RLS-enforced -- NOT a raw cross-tenant query. The rows ARE the
    leads leadgen wrote + the Data-tab CRUD manages (LIVE leads, the same isolation seam).

    DEGRADE-NEVER + TOTAL: no reader / not a leads cap / explicit leads already present / no
    rows / a reader with no list_entity / ANY reader surprise -> None (the run proceeds with
    the inputs UNCHANGED -- honest-empty stays honest-empty). NEVER raises. NEVER fabricates a
    lead row. No secret is ever in scope (the reader reads only managed-entity data)."""
    if db_reader is None:
        return None
    if not _is_leads_consuming_capability(cap):
        return None
    # An explicit leads list (passed inline by the edge / a test) always wins.
    if _has_explicit_leads(inputs):
        return None
    # The reader is duck-typed (Protocol); a concrete reader that predates list_entity simply
    # lacks the method -> getattr is None -> no injection (degrade-never, no AttributeError).
    reader_call = getattr(db_reader, "list_entity", None)
    if not callable(reader_call):
        return None
    try:
        rows = reader_call(tid, _LEADS_ENTITY_KIND)
    except Exception:
        # DEGRADE-NEVER: a reader surprise must never break a run -> proceed unchanged.
        return None
    if not isinstance(rows, (list, tuple)) or not rows:
        return None  # no current leads -> proceed unchanged (honest-empty, never fabricate).
    leads: list = []
    for row in rows:
        lead = _lead_row_to_dict(row)
        if lead is not None:
            leads.append(lead)
    if not leads:
        return None  # rows present but none usable -> unchanged (never inject an empty list).
    merged: dict = dict(inputs) if isinstance(inputs, Mapping) else {}
    merged[_LEADS_INPUTS_KEY] = leads
    return merged


# --------------------------------------------------------------------------- #
# THE entry (spec A.2). Thin PUBLIC wrapper: dispatch the run, then attach the action
# queue (mission COMPLETE2 W2b) on the way out -- ONE attach point covers ALL dispatch
# routes (not_attached / universe / pesquisa / structured-generator / generic build). A
# fail-closed CapabilityRefused raised by the dispatch PROPAGATES unchanged (a deny gets no
# queue -- it is an exception, not a result). The dispatch body is unchanged in
# _dispatch_capability below.
# --------------------------------------------------------------------------- #
def run_capability(
    tenant_id: str,
    capability: str,
    intent: str,
    credential: Credential,
    *,
    db: Optional[DbWriter] = None,
    db_reader: Optional[DbReader] = None,
    options: Optional[Mapping[str, Any]] = None,
    inputs: Optional[Mapping[str, Any]] = None,
) -> CapabilityResult:
    """THE headless product entry (ADR D1 Agent-SDK runtime). See module docstring.

    ``inputs`` (mission BRANDBOOK, Cell A) is the OPTIONAL typed form payload per a
    capability's input_contract (the rich any-media seam -- uploads/URLs/text alongside
    scalars). It is RESOLVED (image -> palette, doc/url -> text) and handed to a STRUCTURED
    GENERATOR; ``intent`` stays the free-text fallback. 100% backward-compatible: omit it
    (or run a non-generator capability) and the behaviour is byte-identical to before.

    ``db_reader`` (arch-council B2) is the OPTIONAL EDIT->REFLECT read seam. When injected,
    an ad/catalog run whose inputs carry a product ref (sku/slug/record_id) has its
    inputs['product_record'] HYDRATED from the tenant's CURRENT product data (the SAME
    tenant_data the admin product-editor writes, read tenant-scoped via the audited adapter)
    BEFORE dispatch -- so editing a product makes the next ad reflect it. Omit it (or run a
    non-product capability / pass no ref) and the behaviour is byte-identical to before.

    FAIL-CLOSED: every deny raises CapabilityRefused (never a silent empty result).
    PERSIST is best-effort-after-pass: a DB failure is surfaced (persisted=False + an
    error appended) but does NOT discard the produced artifact. The api_key is never
    echoed back, never logged, never persisted.

    ACTION QUEUE (mission COMPLETE2 W2b): after the dispatch returns a result, the open-items
    / recommended next-actions are DERIVED from the result's own gate/score/run_mode/
    confidence_breakdown/endpoint_status and attached as ``result.action_queue``. Additive +
    degrade-never: a derivation failure leaves action_queue=None; the run is never affected.
    """
    result = _dispatch_capability(
        tenant_id, capability, intent, credential,
        db=db, db_reader=db_reader, options=options, inputs=inputs,
    )
    _attach_action_queue(result)
    return result


def _dispatch_capability(
    tenant_id: str,
    capability: str,
    intent: str,
    credential: Credential,
    *,
    db: Optional[DbWriter] = None,
    db_reader: Optional[DbReader] = None,
    options: Optional[Mapping[str, Any]] = None,
    inputs: Optional[Mapping[str, Any]] = None,
) -> CapabilityResult:
    """The capability dispatch (the body that was run_capability before the W2b wrapper split).

    Unchanged from the historical run_capability: RESOLVE -> SCOPE (deny-by-default) ->
    COMPOSE GATE -> ROUTE (universe / pesquisa / structured-generator / generic build) ->
    PERSIST -> RETURN. Every return path here flows back through the public ``run_capability``
    wrapper, which attaches the action queue once. A CapabilityRefused raised here propagates
    out of the wrapper unchanged (fail-closed). PRIVATE: callers use ``run_capability``.
    """
    # -- STEP 2a SCOPE: deny-by-default on the tenant (mirror the adapter rule). -------
    tid = (tenant_id or "").strip()
    if not tid:
        raise CapabilityRefused("missing_tenant", capability=capability)

    cap = (capability or "").strip()
    if not cap:
        raise CapabilityRefused(
            "unresolved_capability",
            tenant_id=tid,
            detail="empty capability string",
        )

    # -- STEP 2b SCOPE: deny a capability not enabled for this tenant (BEFORE building). -
    if not _capability_enabled(tid, cap, options):
        raise CapabilityRefused("capability_disabled", tenant_id=tid, capability=cap)

    # -- STEP 1 RESOLVE: capability -> (nucleus, kind, pillar, verb), OVERLAY-FIRST. ----
    nucleus, kind, pillar, _verb = _resolve_capability(tid, cap)

    # -- STEP 1a BRAND: resolve the unified per-tenant brand context ONCE (mission BRAND_MUSTACHE).
    # This is THE universal brand seam: the SAME template, filled with THIS tenant's brand
    # context, produces tenant-aligned output. It is threaded into the structured-generator
    # route below so EVERY capability output can be brand-personalized ({{brand_*}} mustache).
    # DEGRADE-NEVER: None when the kill-switch (CEX_BRAND_DIFFUSE=0) is off, the module is
    # absent, or any resolve surprise -> no diffusion, byte-identical to before (zero-regression).
    # No api_key is ever in scope (pure brand data). Resolved here (after the tenant scope is
    # confirmed) so every downstream route shares the one resolution.
    brand_context = _resolve_brand_context_for_run(tid)

    # -- STEP 1a2 EDIT->REFLECT: hydrate inputs['product_record'] from the tenant's CURRENT
    # product data (arch-council wave 0.5, B2). When a DbReader is injected AND this run
    # resolves to an ad/catalog capability AND the inputs carry a product ref (sku/slug/
    # record_id) AND no explicit product_record was passed, the tenant's current product (the
    # SAME tenant_data kind='products' the admin product-editor writes, read tenant-scoped via
    # the audited adapter -> the SAME isolation seam) is folded into inputs BEFORE dispatch.
    # The ad mold (cex_ad_mold_bind) already CONSUMES inputs['product_record'] (ADMAX W2b), so
    # wiring the hydration here makes the loop real: edit the product -> the next ad reflects
    # it. DEGRADE-NEVER + ZERO-REGRESSION: gate off / no reader / not a product cap / no ref /
    # an explicit record already present / no match -> _hydrate_product_record returns None and
    # ``inputs`` is left byte-identical (no behaviour change). Runs AFTER resolve (we need the
    # resolved kind) and BEFORE every dispatch route (so the hydrated inputs reach the
    # generator). No api_key is ever in scope (the reader reads only product data).
    _hydrated = _hydrate_product_record(tid, cap, kind, db_reader, inputs)
    if _hydrated is not None:
        inputs = _hydrated

    # -- STEP 1a3 LIVE LEADS: inject inputs['leads'] from the tenant's CURRENT managed leads
    # (tenant_data kind='contacts', founder-confirmed 2026-06-24). MIRRORS the product-
    # hydration seam above: when a DbReader is injected AND this run is a leads-consuming
    # capability (crm / sales_assistant, by SLUG) AND no explicit leads list was passed, the
    # tenant's current contacts rows (the SAME rows leadgen writes + the Data-tab CRUD manages,
    # read tenant-scoped via the audited adapter -> the SAME isolation seam) are folded into
    # inputs BEFORE dispatch. crm.build reads inputs['leads']; sales_assistant._select_lead
    # reads inputs['leads'] (+ lead_id) -- so wiring it here makes both operate on LIVE rows.
    # DEGRADE-NEVER + ZERO-REGRESSION: no reader / not a leads cap / explicit leads already
    # present / no rows / any reader surprise -> _inject_leads_entity returns None and
    # ``inputs`` is left byte-identical (honest-empty stays honest-empty). Runs AFTER resolve
    # and BEFORE every dispatch route (so the injected leads reach the generator). No api_key
    # is ever in scope (the reader reads only managed-entity data).
    _inj = _inject_leads_entity(tid, cap, db_reader, inputs)
    if _inj is not None:
        inputs = _inj

    # -- STEP 1.5 COMPOSE GATE: a declared-but-not-attached capability returns a CLEAN
    # not_attached result (mission DASHBOARD_COMPOSITION W1, spec SS3.2) -- NEVER a
    # raise, NEVER a generator/build dispatch. The per-tenant attach state lives in the
    # capability_map.yaml ``capabilities:{enabled,disabled}`` block (D2 git SoT), read via
    # the registry. Kill-switch CEX_COMPOSE_GATE=0 -> bypass. DEGRADE-NEVER: any gate error
    # -> attached (run). ADDITIVE + ZERO-REGRESSION: an absent block -> allow-all -> this
    # returns False from _capability_attached's negation never fires, so routing below is
    # byte-identical to pre-W1. Runs AFTER resolve (we need the resolved nucleus/kind/pillar
    # for the clean result) and BEFORE every dispatch route (universe/pesquisa/generator/build).
    if not _capability_attached(tid, cap):
        return _not_attached_result(tid, cap, nucleus, kind, pillar)

    # -- STEP 1b ROUTE: the Research Universe capability is NOT an LLM build (spec_dashboard
    # _roadmap W1). A capability whose RESOLVED kind is research_universe is run through the
    # 10-lane orchestrator (cex_research_universe.research_universe) -- it needs NO F5
    # credential (the lanes own their own network/keys/redaction). The deny-by-default
    # tenant + enabled gates above ALREADY ran, so this branch inherits the same scoping; it
    # ONLY skips the CREDENTIAL + CEXAgent.build path. Additive: every other kind falls
    # through to the unchanged STEP 3/4 build below (byte-identical routing). ----------------
    if kind == _ROUTE_RESEARCH_UNIVERSE_KIND:
        return _run_research_universe(
            tid, cap, nucleus, kind, pillar, intent, db=db, options=options,
        )

    # -- STEP 1c ROUTE: the marketplace flagship is the REAL research -> ads pipeline (dashboard
    # roadmap W2), NOT a generic 8F build. A capability whose RESOLVED kind is pesquisa_produto is
    # run through cex_run_pipeline.run_pipeline (research -> 30-field render+persist -> ads chain).
    # Unlike the universe route, the pipeline DOES need the F5 credential (it runs real builds), so
    # the credential is passed through -- the pipeline reuses THIS spine's credential/deny seam, so a
    # refusal (native_local / missing_credential / disabled) still propagates fail-closed. The
    # deny-by-default tenant + enabled gates above ALREADY ran (this branch inherits the same
    # scoping). Additive: every other kind falls through to the unchanged STEP 3/4 build below. ----
    if kind == _ROUTE_PESQUISA_PRODUTO_KIND and not _is_pesquisa_inner(options):
        return _run_pesquisa_produto(
            tid, cap, nucleus, kind, pillar, intent, credential, db=db, options=options,
        )

    # -- STEP 1c2 ROUTE: the lead-gen capability runs the REAL lane orchestrator (spec
    # 05_leadgen_suite Phase 1b), NOT the generic build. Keyed on the SLUG (``leadgen``): the
    # capability resolves to the SHARED, FROZEN kind research_pipeline, so a kind trigger would
    # collide / be a frozen-kind no-op -- the slug is the unambiguous route key (the same council
    # A4 lesson as the ads/product-hydration). cex_leadgen_run.leadgen_run maps the 7 inputs ->
    # the existing lanes (marketplace tier-router + research_universe cnpj/ibge/reddit/youtube),
    # fans out degrade-never, maps REAL results -> lead records, and returns the SAME
    # StructuredOutput shape as the 1a generator (mold_id="leadgen", the 5 frozen sections). It
    # MUST precede STEP 1d because ``leadgen`` ALSO has a registered structured generator (the 1a
    # offline scaffold) -- the REAL orchestrator wins here, with the scaffold as the degrade-never
    # fallback INSIDE _run_leadgen. The deny + enabled + compose gates above ALREADY ran. The
    # credential is passed through for parity (the lanes own their keys via the env). DEGRADE-
    # NEVER: a hard orchestrator surprise falls back to the offline scaffold; ALL channels blocked
    # -> honest-empty (gate REVISAR), never a crash, never a fabricated lead. Skipped for a
    # pesquisa-pipeline INNER sub-call (it never resolves to leadgen, but guard for symmetry). ---
    if cap == _ROUTE_LEADGEN_SLUG and not _is_pesquisa_inner(options):
        return _run_leadgen(
            tid, cap, nucleus, kind, pillar, intent, credential,
            db=db, options=options, form_inputs=inputs, brand_context=brand_context,
        )

    # -- STEP 1d ROUTE: a registered STRUCTURED GENERATOR (mission MOLDED_REAL_SEAM; council A4). A
    # capability whose SLUG has a generator in capability_generators emits a REAL ``structured``
    # payload (molded-real shape) instead of the generic mock. The SLUG is the SOLE generator key:
    # several BASE capabilities share one kind (knowledge_card x research/docs/content/
    # pesquisa_produto; prompt_template x ads/email_builder), so a kind lookup over the
    # last-write-wins registry silently routed the WRONG generator (a `content` run emitting a
    # `research` brief -- the A4 BLOCKING bug). _resolve_structured_generator looks up by slug, and
    # falls back to the kind ONLY for an OVERLAY-INTRODUCED novel kind (preserving the tenant-overlay
    # path, guarded). The deny + enabled gates above ALREADY ran (this branch inherits the same
    # scoping). DEGRADE-NEVER: if the generator raises / returns nothing usable,
    # _run_structured_generator returns None and we FALL THROUGH to the unchanged STEP 3/4 build
    # below. NO generator -> this whole block is skipped (byte-identical fall-through). -----------
    # Skip the structured route for a pesquisa-pipeline INNER sub-call (the inner flag): the
    # pipeline (cex_run_pipeline) owns its research(STORM)/ads GENERIC builds + the 30-field
    # downstream parse; a structured generator here would feed the wrong shape to
    # _extract_research_structured (zero-regression for the existing pesquisa_produto pipeline).
    _generator = (
        None
        if _is_pesquisa_inner(options)
        else _resolve_structured_generator(tid, cap, kind)
    )
    if _generator is not None:
        _routed = _run_structured_generator(
            tid, cap, nucleus, kind, pillar, intent, credential, _generator,
            db=db, options=options, form_inputs=inputs, brand_context=brand_context,
        )
        if _routed is not None:
            return _routed
        # generator unavailable/raised -> fall through to the generic build (degrade-never).

    # -- STEP 3 CREDENTIAL: select the F5 model/provider/key (native_local -> raise). ---
    # The nucleus default model is resolved lazily by CEXAgent when model="" -- we pass
    # the credential's model through, or "" to let the agent resolve per-nucleus.
    model, provider = _select_credential(credential, tid, cap, default_model="")

    # -- STEP 4 BUILD: run the EXISTING F1->F8 pipeline with the selected credential. ---
    # R-076/R-003 caller-side import guard. Mirrors _resolve_capability's treatment of
    # _import_registry (the bare lazy import stays bare; the CALLER owns the degrade):
    # Path A is the module-level CEXAgent seam (tests / embedders inject a fake); Path B
    # lazily imports the REAL cex_sdk.agent.cex_agent.CEXAgent -- which is STRUCTURALLY
    # ABSENT in a distilled tenant (sdk_choice='cexai_packaged' is the locked default;
    # the emitted repo carries the cexai package, NOT cex_sdk/), so the bare import
    # raises ModuleNotFoundError there. Unlike the registry caller (which degrades to
    # _BASE_CAPABILITIES), STEP 4 is the TERMINAL route -- there is no later path to
    # fall through to -- so the honest degrade is ONE actionable fail-closed refusal
    # naming the real cause, never an uncaught ModuleNotFoundError traceback.
    if CEXAgent is not None:
        agent_cls = CEXAgent
    else:
        try:
            agent_cls = _import_cex_agent()
        except Exception as exc:  # ModuleNotFoundError in a distilled tenant; any import surprise
            raise CapabilityRefused(
                "sdk_unavailable",
                tenant_id=tid,
                capability=cap,
                detail=(
                    "the generic F1->F8 build imports cex_sdk.agent.cex_agent.CEXAgent, "
                    "which is not importable in this deployment (%s: %s); a distilled "
                    "tenant does not carry cex_sdk/ by default (sdk_choice=cexai_packaged "
                    "is the locked default) -- run a structured-generator capability "
                    "instead, inject the CEXAgent seam for tests/embedders, or re-distill "
                    "this tenant with cex_distill.py --sdk cex_sdk_legacy (or --sdk both) "
                    "to vendor cex_sdk/ into the emitted repo"
                )
                % (type(exc).__name__, exc),
            )
    build_result: Any
    with _ProviderKeyScope(credential, provider):
        agent = agent_cls(nucleus=nucleus.lower(), kind=kind, model=model)
        build_result = agent.build(intent)

    # Normalise BuildResult fields (the real dataclass; a fake mimics the attrs).
    artifact = str(getattr(build_result, "artifact", "") or "")
    out_kind = str(getattr(build_result, "kind", kind) or kind)
    out_pillar = str(getattr(build_result, "pillar", pillar) or pillar)
    score = float(getattr(build_result, "score", 0.0) or 0.0)
    passed = bool(getattr(build_result, "passed", False))
    trace = str(getattr(build_result, "trace", "") or "")
    build_errors = list(getattr(build_result, "errors", []) or [])
    model_used = str(getattr(agent, "model", model) or model)

    result = CapabilityResult(
        tenant_id=tid,
        capability=cap,
        kind=out_kind,
        pillar=out_pillar,
        nucleus=nucleus,
        artifact=artifact,
        score=score,
        passed=passed,
        status="produced",
        model_used=model_used,
        trace=trace,
        errors=build_errors,
    )

    # -- SPEC 10 W4 DUAL2 (generic fallback): project the plain text artifact into the
    # dual-surface asset so EVERY capability -- not just the 16 structured ones -- now emits
    # the human+machine face (the founder's universal dual_output contract, completed). REUSES
    # the SAME cex_dual_output.to_dual_output emitter + envelope the structured route uses; no
    # generator -> the default empty hero slot (never fabricated media). FAIL-SAFE + ADDITIVE:
    # a None render (CEX_GENERIC_DUAL=0 / CEX_DUAL_OUTPUT=0 / any surprise) leaves dual_output
    # unset, so the generic run stays byte-identical to its pre-W4 behaviour (degrade-never).
    dual = _render_generic_dual_output(
        cap, artifact, passed=passed, score=score, tenant=tid,
    )
    if dual is not None:
        result.dual_output = dual

    # -- STEP 5 PERSIST: write the artifact INTO the tenant DB (tenant_id EXPLICIT). ----
    # Best-effort-after-pass: only persist a PASSED artifact, and never discard the
    # produced artifact if the DB call fails (surface persisted=False + an error).
    if db is not None and passed:
        meta: dict[str, Any] = {
            "table": _TENANT_DATA_TABLE,
            "pillar": out_pillar,
            "nucleus": nucleus,
            "score": score,
            "model_used": model_used,
        }
        if options and "meta" in options and isinstance(options["meta"], Mapping):
            meta.update(dict(options["meta"]))
        # DUAL2: persist the MACHINE face (.md + media ledger) tenant-scoped -- the canonical,
        # tenant-AI-readable surface (founder directive). The HUMAN html face is derivative
        # (re-renderable), so it is NOT stored -- keeps the row lean. Mirrors the structured
        # route's meta['dual_output'] exactly. None dual -> meta unchanged (zero-regression).
        if dual is not None:
            meta["dual_output"] = {
                "id": dual.get("id"),
                "machine_md": dual.get("machine_md"),
                "media_slots": dual.get("media_slots"),
            }
        try:
            record_id = db.persist_artifact(tid, cap, out_kind, artifact, meta)
            result.record_id = str(record_id) if record_id is not None else None
            result.persisted = result.record_id is not None
            result.status = "persisted" if result.persisted else "produced_unpersisted"
        except Exception as exc:  # DB failure: surface, never discard the artifact.
            result.persisted = False
            result.status = "produced_unpersisted"
            # Record only the error TYPE + message; never include any credential.
            result.errors.append("persist_failed: %s: %s" % (type(exc).__name__, exc))
    elif db is not None and not passed:
        # The gate failed: do not persist a sub-floor artifact (spec A.2 persist-after-pass).
        result.status = "produced_unpersisted"

    # -- STEP 6 RETURN: artifact + score + record_id + model_used (no api_key). --------
    return result


__all__ = [
    "Credential",
    "CapabilityResult",
    "CapabilityRefused",
    "DbWriter",
    "DbReader",
    "run_capability",
    "MODE_BYO_API_KEY",
    "MODE_NATIVE_LOCAL",
    "MODE_PLATFORM",
]

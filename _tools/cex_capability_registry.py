#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI capability registry -- the dashboard card catalog (mission CEXAI_PRODUCT_RUNTIME).

THE shared capability catalog consumed by BOTH the headless runtime
(_tools/cex_run_capability.py) and the dashboard backend. A capability is a stable
slug the dashboard sends (e.g. "research"); this module maps it to the full card
record: {capability, nucleus, kind, pillar, verb, title, label, description, icon,
default_intent_hint}. The runtime reads the (nucleus, kind, pillar, verb) tuple; the
dashboard reads the presentation fields. One source of truth for both.

Implements section B.5 (card -> nucleus map) + D (overlay -> dashboard binding) of
spec_cexai_product_build_v1, and answers OQ6 ("the base card table should be a
versioned artifact the platform ships, so cards stay consistent across tenants and
the overlay only EXTENDS it"). The versioned artifact is
_docs/compiled/cexai_capability_catalog.yaml, loaded here.

PUBLIC API
  list_capabilities(tenant_id=None) -> list[CapabilityRecord]
      The VISIBLE cards for a tenant. OVERLAY-FIRST: the tenant overlay's
      `enabled_capabilities` list (spec D.3) filters the base catalog
      (intersection); a tenant's overlay `kinds:` cards are appended as custom
      cards. No overlay / no enabled list -> ALL base cards (spec D.3 default:
      "omit => all base"). DEGRADE-NEVER: a missing/malformed overlay -> the
      global default base set (never an error).

  resolve_capability(slug, tenant_id=None) -> CapabilityRecord
      The full record for ONE slug, OVERLAY-FIRST: a tenant overlay card (from the
      overlay `kinds:` map) wins over a base card of the same slug; else the base
      catalog. CapabilityUnknown if the slug is in neither. A resolved card whose
      kind is in the 8F MOAT (frozen kinds) is REFUSED (CapabilityFrozen) -- belt
      -and-braces over the overlay loader, which already rejects frozen kinds.

OVERLAY-FIRST resolution MIRRORS cex_intent_resolver's overlay load: same
fail-closed cex_tenant_paths guard, same `kinds:`-map shape, same frozen-kind set,
same degrade-never posture. The enabled_capabilities filter is the additive MVP
field (spec D.3) read off the SAME overlay file -- one file drives both surfaces.

HARD RULES (task contract + .claude/rules/ascii-code-rule.md):
  * ASCII-only; fully type-hinted; stdlib + yaml only.
  * NO LLM, NO DB, NO network. Pure catalog + overlay file reads.
  * DEGRADE-NEVER: a missing catalog YAML falls back to an in-module base set; a
    missing/malformed/unreadable overlay falls back to the global default.
  * The single-tenant default (CEX_TENANT_ID unset, no explicit tenant_id) is
    byte-identical to "all base cards" -- no cex_tenant_paths import is attempted.

Spec: _docs/compiled/spec_cexai_product_build_v1.md (B.5, D, A.3; canonical 0b).
Catalog: _docs/compiled/cexai_capability_catalog.yaml.
Mirrors: _tools/cex_intent_resolver.py (overlay load + frozen guard).
"""

from __future__ import annotations

import contextlib
import datetime
import json
import os
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterator, List, Mapping, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "_docs" / "compiled" / "cexai_capability_catalog.yaml"

# The 8F MOAT (spec 0b): kinds a card / overlay can NEVER target. Kept in sync with
# cex_intent_resolver._FROZEN_KINDS and cex_run_capability._FROZEN_KINDS.
_FROZEN_KINDS = frozenset({
    "workflow",
    "pipeline_template",
    "prompt_compiler",
    "reasoning_trace",
    "quality_gate",
    "dispatch_rule",
    "handoff",
})

# Truthy-flag set (shared convention with the resolver). Unused by default but kept
# so an env-gated knob can be added without a second definition.
_TRUTHY = frozenset({"1", "true", "yes", "on"})

_ENV_TENANT_ID = "CEX_TENANT_ID"

# The presentation fields a record carries beyond the runtime tuple.
_PRESENTATION_FIELDS = ("title", "label", "description", "icon", "default_intent_hint")


# --------------------------------------------------------------------------- #
# Errors
# --------------------------------------------------------------------------- #
class CapabilityUnknown(KeyError):
    """Raised when a capability slug resolves to no card (neither tenant overlay
    nor base catalog). Carries ``.slug`` and ``.tenant_id`` for diagnostics.

    Subclasses KeyError so callers may catch it as a missing-key condition; the
    str() is human-readable (KeyError normally repr()s its arg, so we override).
    """

    def __init__(self, slug: str, *, tenant_id: str = "") -> None:
        self.slug = slug
        self.tenant_id = tenant_id
        msg = "unknown capability: %r" % slug
        if tenant_id:
            msg += " (tenant=%s)" % tenant_id
        super().__init__(msg)

    def __str__(self) -> str:  # KeyError repr()s its arg; we want the plain message.
        msg = "unknown capability: %r" % self.slug
        if self.tenant_id:
            msg += " (tenant=%s)" % self.tenant_id
        return msg


class CapabilityFrozen(ValueError):
    """Raised when a resolved card targets an 8F-moat frozen kind. Belt-and-braces:
    the overlay loader already rejects frozen kinds at load time, but resolution
    refuses again so a frozen target can never reach the runtime."""

    def __init__(self, slug: str, kind: str, *, tenant_id: str = "") -> None:
        self.slug = slug
        self.kind = kind
        self.tenant_id = tenant_id
        msg = ("capability %r resolves to frozen kind %r (8F moat -- a card can never "
               "target a frozen kind)" % (slug, kind))
        if tenant_id:
            msg += " (tenant=%s)" % tenant_id
        super().__init__(msg)


class CapabilityNotDeclared(ValueError):
    """Raised by the attach/detach WRITERS (mission DASHBOARD_COMPOSITION W2) when a slug
    is NOT in the tenant's DECLARED universe (base catalog + inherited_base + custom_capabilities).

    FAIL-CLOSED: you can only toggle a capability the tenant actually declares -- a stale, typo'd
    or foreign slug is REFUSED before any file write, never silently attached. Carries ``.slug``
    and ``.tenant_id`` for diagnostics; the str() is a plain human-readable message."""

    def __init__(self, slug: str, *, tenant_id: str = "") -> None:
        self.slug = slug
        self.tenant_id = tenant_id
        msg = ("capability %r is not declared for this tenant -- cannot attach/detach an "
               "undeclared capability (fail-closed)" % slug)
        if tenant_id:
            msg += " (tenant=%s)" % tenant_id
        super().__init__(msg)

    def __str__(self) -> str:  # ValueError repr()s its arg; we want the plain message.
        msg = ("capability %r is not declared for this tenant -- cannot attach/detach an "
               "undeclared capability (fail-closed)" % self.slug)
        if self.tenant_id:
            msg += " (tenant=%s)" % self.tenant_id
        return msg


class CapabilityLockBusy(RuntimeError):
    """Raised when the per-tenant overlay WRITE LOCK could not be acquired within the bounded
    retry window (arch-council C1 lockfile hardening, R-191). FAIL-CLOSED: attach_capability /
    detach_capability must NEVER mutate the overlay unlocked -- a refused attach/detach is
    recoverable (the caller retries); a silently lost update to a paid/sensitive capability's
    enabled/disabled set is not (that was the R-191 defect this replaces -- see
    ``_overlay_write_lock``).

    Carries ``.lock_path`` (the lockfile path) and ``.holder`` (the last-seen ``{pid,
    acquired_at}`` marker, or ``{}`` if unreadable) for diagnostics; ``.cause`` holds the
    underlying OSError when the failure was a hard I/O error (e.g. permissions) rather than a
    contention timeout."""

    def __init__(
        self,
        lock_path: Path,
        *,
        holder: Optional[Dict[str, Any]] = None,
        cause: Optional[OSError] = None,
    ) -> None:
        self.lock_path = lock_path
        self.holder = holder or {}
        self.cause = cause
        if cause is not None:
            msg = "could not create overlay lock %r (%s)" % (str(lock_path), cause)
        else:
            msg = ("could not acquire overlay write lock %r within the retry window"
                   % str(lock_path))
            if self.holder.get("pid"):
                msg += (" (held by pid=%s since %s)"
                        % (self.holder.get("pid"), self.holder.get("acquired_at", "?")))
        msg += " -- refusing to mutate unlocked (fail-closed); retry the request"
        super().__init__(msg)


# --------------------------------------------------------------------------- #
# The card record
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class CapabilityRecord:
    """One dashboard card. The runtime reads (nucleus, kind, pillar, verb); the
    dashboard reads (title, label, description, icon, default_intent_hint).

    ``source`` is "base" for a catalog card or "overlay" for a tenant-custom card
    (from the overlay `kinds:` map). ``enabled`` is set by list_capabilities to
    reflect the tenant's enabled_capabilities gate (always True for an overlay
    card that is present).
    """

    capability: str
    nucleus: str
    kind: str
    pillar: str
    verb: str
    title: str = ""
    label: str = ""
    description: str = ""
    icon: str = ""
    default_intent_hint: str = ""
    source: str = "base"
    enabled: bool = True
    # arch-council C1: a SENSITIVE/PAID capability (spends money / hits a paid provider or
    # external credits). The ATTACH gate fail-CLOSES these when the per-tenant capability_map
    # is PRESENT-but-unparseable (a corrupt gate file must never silently RE-ENABLE a paid cap).
    # Default False (additive: an un-flagged catalog row keeps today's behaviour). A catalog row
    # MAY set ``sensitive: true``; the module also holds a conservative default set (below).
    sensitive: bool = False

    def runtime_tuple(self) -> Tuple[str, str, str, str]:
        """The (nucleus, kind, pillar, verb) tuple the runtime resolves against
        (matches cex_run_capability._BASE_CAPABILITIES value order)."""
        return (self.nucleus, self.kind, self.pillar, self.verb)

    def to_card(self) -> Dict[str, Any]:
        """A JSON-friendly dashboard card dict (spec B.3 GET /api/cards row shape,
        extended). Never includes any credential -- there is none on this object."""
        return {
            "capability": self.capability,
            "label": self.label or self.title or self.capability,
            "title": self.title or self.label or self.capability,
            "description": self.description,
            "icon": self.icon,
            "nucleus": self.nucleus,
            "kind": self.kind,
            "pillar": self.pillar,
            "verb": self.verb,
            "default_intent_hint": self.default_intent_hint,
            "source": self.source,
            "enabled": self.enabled,
        }


# --------------------------------------------------------------------------- #
# In-module fallback base set (degrade-never if the catalog YAML is absent).
# Mirrors _BASE_CAPABILITIES in cex_run_capability.py + spec B.5, with minimal
# presentation. The YAML catalog is the source of truth; this is the safety net.
#
# R-186 (SHOKUNIN): this fallback used to carry only 9 of the catalog's 21 cards --
# untested against it -- so on ANY catalog-load failure (missing/malformed YAML)
# 12 capabilities silently vanished. Same bug class already fixed once for
# cex_run_capability._BASE_CAPABILITIES (see that module's matching comment); this
# module cannot import that fix directly (cex_run_capability imports THIS module,
# so the reverse import would cycle), and deriving from the YAML at import time
# would defeat the whole point of a degrade-never fallback -- so this stays a
# literal, kept in lockstep with the YAML by hand. Every catalog card now has a
# fallback entry here (same order as the YAML); parity is asserted by
# test_fallback_base_matches_catalog_slugs + test_fallback_base_tuples_match_
# catalog_rows + test_catalog_yaml_fallback_exposes_full_catalog
# (_tools/tests/test_cex_capability_registry.py) -- a card added to the catalog
# without a matching entry here will FAIL those tests.
# --------------------------------------------------------------------------- #
_FALLBACK_BASE: Tuple[Dict[str, Any], ...] = (
    {"capability": "research", "nucleus": "N01", "kind": "knowledge_card",
     "pillar": "P01", "verb": "analyze", "title": "Research", "label": "Research",
     "icon": "[search]", "description": "Structured sourced intelligence brief.",
     "default_intent_hint": "Research <topic>"},
    {"capability": "ads", "nucleus": "N02", "kind": "prompt_template",
     "pillar": "P03", "verb": "create", "title": "Ads and Copy", "label": "Ads / Copy",
     "icon": "[ad]", "description": "Brand-voice ad copy and campaign templates.",
     "default_intent_hint": "Write ad copy for <offer>"},
    {"capability": "pricing", "nucleus": "N06", "kind": "content_monetization",
     "pillar": "P11", "verb": "create", "title": "Pricing", "label": "Pricing",
     "icon": "[price]", "description": "Pricing tiers and monetization models.",
     "default_intent_hint": "Design pricing tiers for <product>"},
    # R-186 fix -- previously missing from the fallback (present in the catalog since
    # the "12 to build next" wave).
    {"capability": "roi_calc", "nucleus": "N06", "kind": "roi_calculator",
     "pillar": "P11", "verb": "create", "title": "ROI Calculator",
     "label": "ROI Calculator", "icon": "[roi]",
     "description": "Input-driven ROI case -- hours/money saved, payback, annual return.",
     "default_intent_hint": "Build an ROI case for <buyer/segment>"},
    {"capability": "funnel_diag", "nucleus": "N06", "kind": "tool_card",
     "pillar": "P11", "verb": "analyze", "title": "Funnel Diagnostic",
     "label": "Funnel Diagnostic", "icon": "[funnel]",
     "description": "Find the highest-ROI funnel leak, ranked by impact per effort.",
     "default_intent_hint": "Diagnose the funnel for <product>"},
    {"capability": "media_photo", "nucleus": "N02", "kind": "multimodal_prompt",
     "pillar": "P03", "verb": "create", "title": "Media and Photo",
     "label": "Media / Photo", "icon": "[photo]",
     "description": "Image / photo brief (multimodal prompt).",
     "default_intent_hint": "Create a photo brief for <scene>"},
    {"capability": "content", "nucleus": "N04", "kind": "knowledge_card",
     "pillar": "P01", "verb": "document", "title": "Content", "label": "Content",
     "icon": "[doc]", "description": "Knowledge / documentation capture.",
     "default_intent_hint": "Document <topic>"},
    {"capability": "docs", "nucleus": "N04", "kind": "knowledge_card",
     "pillar": "P01", "verb": "document", "title": "Knowledge and Docs",
     "label": "Knowledge / Docs", "icon": "[docs]",
     "description": "RAG-ready documentation capture.",
     "default_intent_hint": "Capture <subject> as docs"},
    {"capability": "landing", "nucleus": "N03", "kind": "landing_page",
     "pillar": "P05", "verb": "create", "title": "Landing Page",
     "label": "Landing Page", "icon": "[page]",
     "description": "Conversion-oriented landing page.",
     "default_intent_hint": "Build a landing page for <offer>"},
    # R-186 fix (below through leadgen) -- previously missing from the fallback; each
    # mirrors its catalog YAML row exactly (nucleus/kind/pillar/verb).
    {"capability": "tier_designer", "nucleus": "N06", "kind": "subscription_tier",
     "pillar": "P11", "verb": "create", "title": "Plan Matrix / Tier Designer",
     "label": "Plan Matrix", "icon": "[price]",
     "description": "Subscription plan matrix -- tiers, feature gating, price anchoring.",
     "default_intent_hint": "Design the plan matrix for <product>"},
    {"capability": "product_docs", "nucleus": "N04", "kind": "knowledge_card",
     "pillar": "P01", "verb": "document", "title": "Product Docs",
     "label": "Product Docs", "icon": "[docs]",
     "description": "RAG-ready product documentation -- features, setup, reference.",
     "default_intent_hint": "Document <product/feature>"},
    {"capability": "email_builder", "nucleus": "N02", "kind": "prompt_template",
     "pillar": "P03", "verb": "create", "title": "Email Builder",
     "label": "Email Builder", "icon": "[ad]",
     "description": "Responsive HTML email template -- subject, preheader, body blocks.",
     "default_intent_hint": "Write a marketing email for <campaign/audience>"},
    {"capability": "oauth_connect", "nucleus": "N03", "kind": "oauth_app_config",
     "pillar": "P04", "verb": "create", "title": "OAuth Connect",
     "label": "OAuth Connect", "icon": "[plug]",
     "description": "Typed OAuth app config -- client id/secret, scopes, redirect URIs.",
     "default_intent_hint": "Configure an OAuth connection to <provider>"},
    {"capability": "competitor_benchmark", "nucleus": "N01", "kind": "competitive_matrix",
     "pillar": "P01", "verb": "analyze", "title": "Competitor Benchmark Matrix",
     "label": "Competitor Benchmark", "icon": "[search]",
     "description": "Competitor benchmark matrix -- sourced cells, positioning read.",
     "default_intent_hint": "Benchmark <product> against <competitors>"},
    {"capability": "leadgen", "nucleus": "N01", "kind": "research_pipeline",
     "pillar": "P04", "verb": "analyze", "title": "Captacao de Leads (Lead-gen / scraping)",
     "label": "Captacao de Leads", "icon": "[funnel]",
     "description": "Typed lead list across channels, honest per-source status, never fabricates.",
     "default_intent_hint": "Encontre leads para <perfil> a partir de <seed>"},
    # CAPABILITY_LAYER W1 -- the pesquisa_produto research vertical (plan V1). Mirrors the
    # catalog YAML row; resolves to the knowledge_card kind (0 new kinds). The tenant_data
    # discriminator is the capability column + the persisted kind.
    {"capability": "pesquisa_produto", "nucleus": "N01", "kind": "knowledge_card",
     "pillar": "P01", "verb": "analyze", "title": "Pesquisa de Produto",
     "label": "Pesquisa de Produto", "icon": "[search]",
     "description": "Product research across marketplaces -- price, competitors, keywords.",
     "default_intent_hint": "Pesquise <produto> -- preco, concorrentes e palavras-chave"},
    # DASHBOARD ROADMAP W1 -- the Research Universe card (spec_dashboard_roadmap). Mirrors the
    # catalog YAML row; resolves to the synthetic kind ``research_universe`` (NOT a frozen kind,
    # NOT an 8F build -- the runtime routes it to the cex_research_universe orchestrator). The
    # tenant_data discriminator is the capability column + the persisted kind.
    {"capability": "research_universe", "nucleus": "N01", "kind": "research_universe",
     "pillar": "P01", "verb": "analyze", "title": "Research Universe",
     "label": "Research Universe", "icon": "[universe]",
     "description": "One seed -> 10 research lanes -> a unified multi-source report.",
     "default_intent_hint": "Pesquise <produto/marca/CNPJ> -- firmografia, social, reputacao, SEO"},
    # R-186 fix -- previously missing from the fallback (N06 BRANDBOOK Cell B card).
    {"capability": "brandbook", "nucleus": "N06", "kind": "brandbook",
     "pillar": "P05", "verb": "create", "title": "Brand Book",
     "label": "Brand Book", "icon": "[brand]",
     "description": "Complete brand book from brand materials -- 8 structured sections.",
     "default_intent_hint": "Build the brand book for <brand name>"},
    # R-186 fix (below through marketplace_listing) -- previously missing from the
    # fallback (W3 SOURCING contract cards + the S5-completeness marketplace_listing card).
    {"capability": "sourcing_opportunity", "nucleus": "N06", "kind": "opportunity_matrix",
     "pillar": "P11", "verb": "analyze", "title": "Sourcing Opportunity Matrix",
     "label": "Sourcing Opportunity", "icon": "[matrix]",
     "description": "Supplier cost vs market price/demand, ranked by margin, go/no-go verdict.",
     "default_intent_hint": "Find the best products to source from <supplier catalog>"},
    {"capability": "product_match", "nucleus": "N03", "kind": "product_match",
     "pillar": "P04", "verb": "analyze", "title": "Product Match + Catalog Audit",
     "label": "Product Match", "icon": "[match]",
     "description": "Match supplier items to marketplace listings by photo + dimension + code.",
     "default_intent_hint": "Match <supplier items> to marketplace listings"},
    {"capability": "marketplace_listing", "nucleus": "N06", "kind": "marketplace_listing",
     "pillar": "P05", "verb": "create", "title": "Marketplace Listing (Channel Projection)",
     "label": "Marketplace Listing", "icon": "[list]",
     "description": "Canonical product -> per-channel listing payload + readiness report.",
     "default_intent_hint": "Map <product> into a <marketplace> listing"},
)

# Required runtime keys every catalog record MUST carry (B.5 tuple).
_REQUIRED_KEYS = ("capability", "nucleus", "kind", "pillar", "verb")

# arch-council C1 -- the SENSITIVE/PAID capability set: capabilities that spend money (a paid
# LLM provider call) or burn external credits (firecrawl / marketplace scrapes / TTS). These
# are the caps the ATTACH gate must fail-CLOSE on a PRESENT-but-unparseable capability_map
# (a corrupt gate file must REFUSE the toggled-off paid set, never silently re-enable it).
# A catalog row may ALSO opt in via ``sensitive: true``; this is the conservative DEFAULT so
# the protection holds even before any row is annotated. Read-only VISIBILITY is unaffected --
# only the run-path ATTACH gate consults this (see cex_run_capability._capability_attached).
_DEFAULT_SENSITIVE_CAPABILITIES: "frozenset[str]" = frozenset({
    "research",            # paid LLM + web fetch
    "ads",                 # paid LLM (creative copy)
    "landing",             # paid LLM (creative copy)
    "media_photo",         # paid image/multimodal pipeline
    "pesquisa_produto",    # marketplace scrape (firecrawl credits) + LLM
    "research_universe",   # 10-lane orchestrator (external credits across lanes)
    "brandbook",           # paid LLM (full brand book)
})

# Truthy spellings a catalog ``sensitive:`` value may carry (additive; bool true also accepted).
_SENSITIVE_TRUE_STRINGS = frozenset({"true", "yes", "1", "paid", "sensitive"})


def _coerce_sensitive_flag(value: Any) -> bool:
    """Coerce a catalog ``sensitive`` value to a bool. TOTAL: a bool passes through; a string is
    matched case-insensitively against the truthy set; anything else -> False (un-flagged)."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in _SENSITIVE_TRUE_STRINGS
    return False


# --------------------------------------------------------------------------- #
# Catalog loader (cached). DEGRADE-NEVER: missing/malformed YAML -> fallback set.
# --------------------------------------------------------------------------- #
_catalog_cache: Optional["Tuple[CapabilityRecord, ...]"] = None


def _parse_catalog_text(text: str) -> Dict[str, Any]:
    """Parse the catalog YAML into a dict, degrade-never. PyYAML preferred; on any
    failure (absent dep, parse error) return {} so the caller uses the fallback set."""
    try:
        import yaml  # optional dep; absence must not break the registry
        data = yaml.safe_load(text)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _record_from_raw(raw: Mapping[str, Any], source: str) -> Optional[CapabilityRecord]:
    """Build a CapabilityRecord from a raw catalog/overlay mapping, or None if the
    required runtime keys are missing/blank. Pure + total: never raises.

    A frozen-kind target is left to the resolution-time guard (CapabilityFrozen) so
    list/resolve both enforce it consistently; here we only drop structurally
    invalid rows.
    """
    if not isinstance(raw, Mapping):
        return None
    vals: Dict[str, Any] = {}
    for key in _REQUIRED_KEYS:
        v = raw.get(key)
        if not isinstance(v, str) or not v.strip():
            return None
        vals[key] = v.strip()
    pres: Dict[str, Any] = {}
    for key in _PRESENTATION_FIELDS:
        v = raw.get(key)
        # YAML folded scalars may carry a trailing newline; normalise whitespace.
        pres[key] = " ".join(str(v).split()) if isinstance(v, str) else ""
    # arch-council C1: optional ``sensitive: true`` flag (additive; absent -> the module default
    # set below decides). Coerced loosely: a bool true OR the string "true"/"yes"/"1"/"paid".
    raw_sensitive = raw.get("sensitive")
    cap_slug = vals["capability"]
    flagged = _coerce_sensitive_flag(raw_sensitive) or (cap_slug in _DEFAULT_SENSITIVE_CAPABILITIES)
    return CapabilityRecord(
        capability=cap_slug,
        nucleus=vals["nucleus"],
        kind=vals["kind"],
        pillar=vals["pillar"],
        verb=vals["verb"],
        title=pres["title"],
        label=pres["label"],
        description=pres["description"],
        icon=pres["icon"],
        default_intent_hint=pres["default_intent_hint"],
        source=source,
        sensitive=flagged,
    )


def _load_catalog() -> "Tuple[CapabilityRecord, ...]":
    """Load the base capability catalog (cached). DEGRADE-NEVER: a missing or
    malformed catalog YAML falls back to the in-module _FALLBACK_BASE set.

    Returns an ordered tuple of base CapabilityRecords (display order preserved).
    Duplicate slugs in the YAML keep the FIRST (a later dup is dropped + ignored).
    """
    global _catalog_cache
    if _catalog_cache is not None:
        return _catalog_cache

    raw_records: List[Mapping[str, Any]] = []
    try:
        if CATALOG_PATH.exists():
            data = _parse_catalog_text(CATALOG_PATH.read_text(encoding="utf-8"))
            caps = data.get("capabilities")
            if isinstance(caps, list):
                raw_records = [c for c in caps if isinstance(c, Mapping)]
    except Exception:
        raw_records = []

    if not raw_records:
        raw_records = list(_FALLBACK_BASE)

    seen: set = set()
    records: List[CapabilityRecord] = []
    for raw in raw_records:
        rec = _record_from_raw(raw, source="base")
        if rec is None or rec.capability in seen:
            continue
        seen.add(rec.capability)
        records.append(rec)

    # Final safety net: if the YAML somehow produced zero valid rows, use fallback.
    if not records:
        for raw in _FALLBACK_BASE:
            rec = _record_from_raw(raw, source="base")
            if rec is not None and rec.capability not in seen:
                seen.add(rec.capability)
                records.append(rec)

    _catalog_cache = tuple(records)
    return _catalog_cache


def _base_index() -> Dict[str, CapabilityRecord]:
    """slug -> base CapabilityRecord (from the loaded catalog)."""
    return {r.capability: r for r in _load_catalog()}


# --------------------------------------------------------------------------- #
# Overlay read (MIRRORS cex_intent_resolver) -- enabled_capabilities + kinds map.
# --------------------------------------------------------------------------- #
def _effective_tenant_id(tenant_id: Optional[str]) -> Optional[str]:
    """The tenant to resolve against: explicit arg first, else CEX_TENANT_ID. None
    when neither is set -> single-tenant global mode (overlay inert, nothing read)."""
    if tenant_id is not None:
        return tenant_id
    raw = os.environ.get(_ENV_TENANT_ID)
    return raw if raw else None


def _read_overlay_raw(tenant_id: Optional[str]) -> Dict[str, Any]:
    """Read the tenant overlay YAML as a raw dict, DEGRADE-NEVER.

    Mirrors cex_intent_resolver._load_tenant_kind_overlay's IO posture: resolves
    the path via the fail-closed cex_tenant_paths guard (surface="overlay") and
    returns {} on ANY failure (no tenant, no file, malformed, unreadable, or a
    hostile CEX_TENANT_ID that makes the guard raise SystemExit). The single-tenant
    default never imports cex_tenant_paths.

    Returns the parsed top-level mapping (may carry `kinds:` and
    `enabled_capabilities:`), or {}.
    """
    eff = _effective_tenant_id(tenant_id)
    # 1) CENTRAL multi-tenant layout first: the tenant-scoped overlay at
    #    .cex/tenants/<tenant>/overlay/kinds_overlay.yaml (only when a tenant is set).
    if eff is not None:
        try:
            tools_dir = str(Path(__file__).resolve().parent)
            if tools_dir not in sys.path:
                sys.path.insert(0, tools_dir)
            import cex_tenant_paths as _tp  # type: ignore[import]
            path = _tp.resolve_tenant_path(
                "kinds_overlay.yaml", surface="overlay", tenant_id=tenant_id)
            if path.exists():
                raw = _parse_catalog_text(path.read_text(encoding="utf-8"))
                if isinstance(raw, dict) and raw:
                    return raw
        except (Exception, SystemExit):
            # SystemExit included deliberately (audit R3): the tenant-path guard
            # raises SystemExit on a malformed CEX_TENANT_ID -> degrade, never crash.
            pass
    # 2) SOVEREIGN / GLOBAL fallback: a distilled single-tenant repo keeps its
    #    overlay at the repo ROOT (overlay/kinds_overlay.yaml), NOT under
    #    .cex/tenants/. This is what makes the dashboard -- which passes the JWT's
    #    tenant_id -- actually resolve the tenant's custom cards (<tenant>_research /
    #    <tenant>_repricer). Fires for tenant_id=None (CLI) AND for an explicit
    #    tenant whose scoped overlay is absent (the sovereign case). Absent -> {}
    #    (byte-identical to the prior behavior on a repo with no root overlay).
    try:
        root_path = ROOT / "overlay" / "kinds_overlay.yaml"
        if not root_path.exists():
            root_path = ROOT / ".cex" / "overlays" / "kinds_overlay.yaml"
        if root_path.exists():
            raw = _parse_catalog_text(root_path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                return raw
    except Exception:
        pass
    return {}


def _enabled_capabilities(tenant_id: Optional[str]) -> Optional[List[str]]:
    """The tenant's enabled-capability allowlist (spec D.3), or None.

    Reads the additive top-level `enabled_capabilities:` list off the overlay file.
    Returns:
      * a list of slug strings -> the gate is ACTIVE (only these base cards show);
      * None -> no gate (overlay absent, key missing, or value malformed) => the
        spec D.3 default "omit => all base". DEGRADE-NEVER: a malformed value is
        treated as "no gate", not a crash.
    """
    raw = _read_overlay_raw(tenant_id)
    val = raw.get("enabled_capabilities")
    if val is None:
        return None
    if isinstance(val, (list, tuple)):
        slugs = [str(x).strip() for x in val if isinstance(x, str) and x.strip()]
        return slugs  # may be [] -> an explicit empty gate (show no base cards)
    # Malformed (e.g. a scalar) -> treat as no gate (degrade-never).
    return None


def _read_cap_map_for_cards(tenant_id: Optional[str]) -> Dict[str, Any]:
    """Read ``capability_map.yaml`` for custom card resolution (degrade-never, sovereign-aware).

    Tries two paths in order, mirroring ``_read_overlay_raw``'s two-path posture:
    1. CENTRAL multi-tenant: ``.cex/tenants/<slug>/overlay/capability_map.yaml``
       (via the fail-closed cex_tenant_paths guard; degrade on any failure).
    2. SOVEREIGN / GLOBAL fallback: ``ROOT/overlay/capability_map.yaml``
       (the distilled single-tenant layout; also fires when the tenant-scoped
       path is absent so the sovereign repo resolves its own emitted overlay).

    DEGRADE-NEVER: any read/parse/import failure -> {}. Used ONLY for the
    read-only card resolution path (``_cap_map_custom_cards``); the write path
    uses ``_read_capability_map_raw`` + ``_resolve_cap_map_write_path`` directly.
    """
    eff = _effective_tenant_id(tenant_id)
    # 1) CENTRAL multi-tenant layout (mirrors _read_capability_map_raw's try block).
    if eff is not None:
        try:
            tools_dir = str(Path(__file__).resolve().parent)
            if tools_dir not in sys.path:
                sys.path.insert(0, tools_dir)
            import cex_tenant_paths as _tp  # type: ignore[import]
            path = _tp.resolve_tenant_path(
                _CAP_MAP_FILENAME, surface="overlay", tenant_id=tenant_id)
            if path.exists():
                raw = _parse_catalog_text(path.read_text(encoding="utf-8"))
                if isinstance(raw, dict) and raw:
                    return raw
        except (Exception, SystemExit):
            pass
    # 2) SOVEREIGN / GLOBAL fallback (mirrors _read_overlay_raw's fallback for kinds_overlay).
    try:
        root_path = ROOT / "overlay" / _CAP_MAP_FILENAME
        if not root_path.exists():
            root_path = ROOT / ".cex" / "overlays" / _CAP_MAP_FILENAME
        if root_path.exists():
            raw = _parse_catalog_text(root_path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                return raw
    except Exception:
        pass
    return {}


def _cap_map_custom_cards(tenant_id: Optional[str]) -> List[CapabilityRecord]:
    """Tenant-CUSTOM cards from ``capability_map.yaml``'s top-level ``custom_capabilities`` list.

    Closes the AI-app link gap: the ``capability_map.yaml`` carries STRUCTURED cards with
    proper dashboard slugs (e.g. ``crm``) and kinds (e.g. ``demo_acme_crm``) -- fields that the
    ``kinds_overlay.yaml``'s ``kinds:`` map does NOT expose (it uses PHRASES as slugs). Calling
    ``resolve_capability('crm', tenant_id=<t>)`` would previously raise ``CapabilityUnknown``
    even though ``declared_capabilities`` already read the same slug from this file. This
    function fills the resolution gap so every declared custom card is also resolvable.

    Resolution order in ``resolve_capability``:
      1. kinds_overlay phrases (``_overlay_custom_cards``) -- unchanged.
      2. capability_map slugs (THIS function) -- the fix.
      3. base catalog.

    FROZEN-kind entries are skipped (the moat). DEGRADE-NEVER: a missing / malformed
    ``capability_map.yaml`` -> []. Source is 'overlay' (the card is tenant-custom).
    """
    raw = _read_cap_map_for_cards(tenant_id)
    cc = raw.get("custom_capabilities")
    if not isinstance(cc, list):
        return []
    cards: List[CapabilityRecord] = []
    seen: set = set()
    for entry in cc:
        if not isinstance(entry, Mapping):
            continue
        slug = str(entry.get("capability") or "").strip()
        kind = str(entry.get("kind") or "").strip()
        pillar = str(entry.get("pillar") or "").strip()
        nucleus = str(entry.get("nucleus") or "").strip()
        if not slug or not kind or not pillar or not nucleus:
            continue
        if slug in seen:
            continue
        if kind in _FROZEN_KINDS:
            continue  # moat: custom cards can never target a frozen kind
        verb = str(entry.get("verb") or "create").strip()
        label = str(entry.get("label") or slug).strip()
        description = str(entry.get("description") or "Tenant-custom capability (capability_map).").strip()
        icon = str(entry.get("icon") or "[custom]").strip()
        seen.add(slug)
        cards.append(CapabilityRecord(
            capability=slug,
            nucleus=nucleus,
            kind=kind,
            pillar=pillar,
            verb=verb,
            title=label,
            label=label,
            description=description,
            icon=icon,
            default_intent_hint=slug,
            source="overlay",
        ))
    return cards


def _overlay_custom_cards(tenant_id: Optional[str]) -> List[CapabilityRecord]:
    """Tenant-CUSTOM cards from the overlay `kinds:` map (spec B.4 overlay cards).

    Each `kinds:` entry is `"<intent phrase>": ["<kind>", "<pillar>", "<nucleus>"]`
    (the cex_intent_resolver overlay shape). It becomes a card whose ``capability``
    slug is the intent phrase. FROZEN-kind entries are skipped here (the resolver's
    loader already rejects them at load; resolution-time also refuses). DEGRADE-NEVER.

    The verb defaults to "create" (overlay entries carry no verb in the shared
    shape); presentation fields are derived from the phrase.
    """
    raw = _read_overlay_raw(tenant_id)
    kinds = raw.get("kinds")
    if not isinstance(kinds, Mapping):
        return []
    cards: List[CapabilityRecord] = []
    seen: set = set()
    for phrase, value in kinds.items():
        if not isinstance(phrase, str) or not phrase.strip():
            continue
        slug = phrase.strip()
        if slug in seen:
            continue
        parsed = _coerce_kinds_entry(value)
        if parsed is None:
            continue
        kind, pillar, nucleus = parsed
        if kind in _FROZEN_KINDS:
            continue  # the moat: overlay can never re-point a frozen kind
        seen.add(slug)
        cards.append(CapabilityRecord(
            capability=slug,
            nucleus=nucleus,
            kind=kind,
            pillar=pillar,
            verb="create",
            title=slug.title(),
            label=slug.title(),
            description="Tenant-custom capability (overlay).",
            icon="[custom]",
            default_intent_hint=slug,
            source="overlay",
        ))
    return cards


def _coerce_kinds_entry(value: Any) -> Optional[Tuple[str, str, str]]:
    """Validate ONE overlay `kinds:` value into (kind, pillar, nucleus), or None.

    Accepts a 3-element list/tuple of non-empty strings (the KIND_PATTERNS shape)
    OR a dict with kind/pillar/nucleus keys. Mirrors
    cex_intent_resolver._coerce_overlay_entry. Pure + total: never raises.
    """
    if isinstance(value, (list, tuple)) and len(value) == 3:
        k, p, n = value
        if all(isinstance(x, str) and x for x in (k, p, n)):
            return (k, p, n)
        return None
    if isinstance(value, Mapping):
        k = value.get("kind")
        p = value.get("pillar")
        n = value.get("nucleus")
        if all(isinstance(x, str) and x for x in (k, p, n)):
            return (str(k), str(p), str(n))
    return None


# --------------------------------------------------------------------------- #
# Composition control plane (mission DASHBOARD_COMPOSITION W1, decision D2).
#
# The per-tenant ATTACH state -- "is this capability module enabled (attached) for
# this tenant?" -- lives in a top-level ``capabilities:`` block in the tenant overlay
# ``capability_map.yaml`` (the SAME overlay file the dashboard reads for
# managed_entities; surface="overlay", git-versioned in the tenant's private config repo).
#
# THE SCHEMA (commented example -- the canonical shape authors write):
#   capabilities:
#     # authoritative attach/toggle state. A capability MUST be DECLARED (in
#     # inherited_base or custom_capabilities) AND enabled to run. `disabled` =
#     # attached-but-off. When `enabled` is non-empty it is the ALLOWLIST; when it is
#     # empty/absent every DECLARED capability is on except those in `disabled`.
#     enabled:  [research, marketplace_listing, crm]   # declared AND on
#     disabled: []                                      # declared but OFF
#     log:                                              # optional, append-only, NO PII
#       - { capability: marketplace_listing, action: attach, by: n07, at: "<iso>" }
#
# THIS IS DISTINCT from the kinds_overlay ``enabled_capabilities`` VISIBILITY gate
# (spec D.3, handled in list_capabilities above): that gates which BASE cards a tenant
# SEES; this gates which DECLARED capabilities are ATTACHED to RUN. The two are
# orthogonal and read different overlay files (kinds_overlay.yaml vs capability_map.yaml).
#
# BACK-COMPAT (HARD, zero regression): a tenant overlay with NO ``capabilities:`` block
# -> ALLOW-ALL (every declared capability runs, exactly as before W1). DEGRADE-NEVER:
# any read/parse error -> allow-all (the attach gate must never crash a dashboard).
# --------------------------------------------------------------------------- #
_CAP_MAP_FILENAME = "capability_map.yaml"


def _read_capability_map_raw(tenant_id: Optional[str]) -> Dict[str, Any]:
    """Read the tenant overlay ``capability_map.yaml`` as a raw dict, DEGRADE-NEVER.

    Mirrors _read_overlay_raw's IO posture -- the fail-closed cex_tenant_paths guard
    (surface="overlay", verified tenant) -- but reads ``capability_map.yaml`` (the overlay
    file that carries managed_entities + the ``capabilities:`` block) instead of
    ``kinds_overlay.yaml``. Two paths, in order (S5 fix -- this used to short-circuit to {}
    whenever ``eff is None``, which meant a SOVEREIGN single-tenant repo's own
    ``capability_map.yaml`` was NEVER readable by this reader -- the ATTACH gate
    (resolve_enabled/compose_gate_active) always saw {} and silently fell back to
    allow-all, independent of whatever the tenant actually declared. Now mirrors its
    sibling reader ``_read_cap_map_for_cards``, which already had this fallback):
      1. CENTRAL multi-tenant: ``.cex/tenants/<slug>/overlay/capability_map.yaml`` (only
         attempted when a tenant id is resolvable).
      2. SOVEREIGN / GLOBAL fallback: ``ROOT/overlay/capability_map.yaml`` (falling back to
         ``ROOT/.cex/overlays/capability_map.yaml``) -- the distilled single-tenant layout;
         also fires when the tenant-scoped path is absent, so a sovereign repo resolves its
         own emitted overlay.
    Returns {} on ANY failure (no tenant, no file, malformed, unreadable, absent PyYAML, or a
    hostile CEX_TENANT_ID that makes the guard raise SystemExit). DEGRADE-NEVER throughout."""
    eff = _effective_tenant_id(tenant_id)
    # 1) CENTRAL multi-tenant layout (only when a tenant id is resolvable).
    if eff is not None:
        try:
            tools_dir = str(Path(__file__).resolve().parent)
            if tools_dir not in sys.path:
                sys.path.insert(0, tools_dir)
            import cex_tenant_paths as _tp  # type: ignore[import]
            path = _tp.resolve_tenant_path(
                _CAP_MAP_FILENAME, surface="overlay", tenant_id=tenant_id)
            if path.exists():
                raw = _parse_catalog_text(path.read_text(encoding="utf-8"))
                if isinstance(raw, dict) and raw:
                    return raw
        except (Exception, SystemExit):
            # SystemExit included deliberately (mirrors _read_overlay_raw, audit R3): the
            # tenant-path guard raises SystemExit on a malformed CEX_TENANT_ID; the gate must
            # DEGRADE to allow-all, never crash a dashboard call.
            pass
    # 2) SOVEREIGN / GLOBAL fallback (mirrors _read_cap_map_for_cards's fallback).
    try:
        root_path = ROOT / "overlay" / _CAP_MAP_FILENAME
        if not root_path.exists():
            root_path = ROOT / ".cex" / "overlays" / _CAP_MAP_FILENAME
        if root_path.exists():
            raw = _parse_catalog_text(root_path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                return raw
    except Exception:
        pass
    return {}


def _capabilities_block(tenant_id: Optional[str]) -> Mapping[str, Any]:
    """The tenant's ``capabilities:`` block (enabled/disabled/log), or {} when absent or
    malformed. DEGRADE-NEVER (delegates to _read_capability_map_raw)."""
    raw = _read_capability_map_raw(tenant_id)
    block = raw.get("capabilities")
    return block if isinstance(block, Mapping) else {}


def _slug_list(value: Any) -> List[str]:
    """Coerce a YAML list value into a clean list of slug strings. A non-list (or a list
    with non-string/blank members) degrades to the valid subset (-> [] if none). Pure."""
    if not isinstance(value, (list, tuple)):
        return []
    return [str(x).strip() for x in value if isinstance(x, str) and x.strip()]


def resolve_enabled(tenant_id: Optional[str], declared: Any) -> "set[str]":
    """The ATTACH gate -- the subset of ``declared`` that is ENABLED for the tenant.

    Reads the tenant ``capability_map.yaml`` ``capabilities:{enabled,disabled}`` block and
    applies it on top of the caller-supplied ``declared`` universe:
      * absent / empty block  -> ``declared`` unchanged (ALLOW-ALL; back-compat, zero
        regression for every un-migrated tenant);
      * else                  -> ``((enabled or declared) - disabled)`` intersected with
        ``declared``. ``enabled`` (when non-empty) is the allowlist; ``disabled`` removes
        an attached-but-off capability; the final intersection with ``declared`` enforces
        "a capability must be DECLARED to be attachable" (you cannot enable an undeclared
        slug -- a stale/typo entry is dropped).

    TOTAL / DEGRADE-NEVER: ``declared`` is normalised to a set of non-blank slug strings;
    ANY read/parse error -> ``declared`` (allow-all). NEVER raises -- the attach gate must
    never block a tenant's dashboard on an error."""
    declared_set = {str(s).strip() for s in (declared or ()) if str(s).strip()}
    try:
        block = _capabilities_block(tenant_id)
        if not block:
            return set(declared_set)  # absent/empty -> allow-all (back-compat)
        enabled = _slug_list(block.get("enabled"))
        disabled = _slug_list(block.get("disabled"))
        base = set(enabled) if enabled else set(declared_set)  # (enabled or declared)
        return (base - set(disabled)) & declared_set
    except Exception:
        return set(declared_set)  # degrade-never: any failure -> allow-all


def compose_gate_active(tenant_id: Optional[str] = None) -> bool:
    """True iff the tenant declares a NON-EMPTY ``capabilities:`` block (``enabled`` or
    ``disabled`` carries at least one slug). False -> no compose gate (allow-all), which
    includes an absent block AND a present-but-both-empty block (the latter resolves to
    allow-all anyway). DEGRADE-NEVER -> False (no gate). Used by the edge (deps.py) to
    decide whether to layer the attach gate onto the run-options allowlist."""
    try:
        block = _capabilities_block(tenant_id)
        if not block:
            return False
        return bool(_slug_list(block.get("enabled")) or _slug_list(block.get("disabled")))
    except Exception:
        return False


# --------------------------------------------------------------------------- #
# arch-council C1 -- SENSITIVE-cap fail-closed primitives.
#
# The ATTACH gate (cex_run_capability._capability_attached) consults these to fail-CLOSE a
# SENSITIVE/PAID capability when the per-tenant capability_map.yaml is PRESENT-but-unparseable
# (a corrupt gate file must REFUSE the toggled-off paid set, never silently re-enable it). A
# read that simply RAISES (transient IO) is NOT "present-but-unparseable" -- that path keeps
# degrading to allow (visibility-degradation); only a file that EXISTS yet PyYAML cannot turn
# into a dict is the fail-closed trigger. An ABSENT file -> today's behaviour (allow-all).
# --------------------------------------------------------------------------- #
def is_sensitive_capability(capability: Optional[str]) -> bool:
    """True iff ``capability`` is SENSITIVE/PAID (the module default set OR a catalog row that
    set ``sensitive: true``). TOTAL + DEGRADE-NEVER: any lookup surprise -> the default-set
    membership (never raises). An empty/None slug -> False."""
    cap = (capability or "").strip()
    if not cap:
        return False
    if cap in _DEFAULT_SENSITIVE_CAPABILITIES:
        return True
    try:
        rec = _base_index().get(cap)
        return bool(rec is not None and rec.sensitive)
    except Exception:
        return cap in _DEFAULT_SENSITIVE_CAPABILITIES


def capability_map_unparseable(tenant_id: Optional[str] = None) -> bool:
    """True iff the tenant capability_map.yaml EXISTS on disk but PyYAML cannot parse it into a
    mapping (PRESENT-but-unparseable). False when the file is ABSENT, when it parses cleanly
    (even to an empty/odd-but-valid doc), OR when PyYAML is unavailable / the path guard refuses
    (those are NOT 'unparseable' -- they degrade to allow, never fail-closed). NEVER raises.

    This is the SOLE fail-closed trigger for the sensitive-cap ATTACH gate (C1). Distinguishing
    'corrupt file' from 'absent file' / 'transient error' is the whole point: a corrupt gate must
    deny the paid set; an absent gate is the zero-regression allow-all; a transient error degrades."""
    eff = _effective_tenant_id(tenant_id)
    if eff is None:
        return False
    try:
        tools_dir = str(Path(__file__).resolve().parent)
        if tools_dir not in sys.path:
            sys.path.insert(0, tools_dir)
        import cex_tenant_paths as _tp  # type: ignore[import]
        path = _tp.resolve_tenant_path(
            _CAP_MAP_FILENAME, surface="overlay", tenant_id=tenant_id)
    except (Exception, SystemExit):
        # Cannot even resolve the path (no PyYAML-independent guard / hostile id) -> treat as
        # NOT unparseable (degrade to allow; the corrupt-file signal needs a real readable path).
        return False
    try:
        if not path.exists():
            return False  # ABSENT -> not unparseable (allow-all, zero-regression)
        text = path.read_text(encoding="utf-8")
    except (Exception, SystemExit):
        return False  # cannot read -> transient; degrade to allow (not the fail-closed trigger)
    try:
        import yaml  # the parser whose FAILURE on a present file is the corrupt-file signal
    except Exception:
        return False  # no parser available -> cannot assert corruption -> degrade to allow
    try:
        data = yaml.safe_load(text)
    except Exception:
        return True  # PRESENT + PyYAML raised -> corrupt gate file -> FAIL-CLOSED trigger
    # Parsed without raising: a dict (even empty) or a None doc is VALID-but-empty, NOT corrupt.
    # A non-mapping top-level (e.g. a bare list/scalar where a mapping is required) IS corrupt:
    # the gate cannot be read from it, so a sensitive cap must not be silently re-enabled.
    if data is None or isinstance(data, dict):
        return False
    return True


def declared_capabilities(tenant_id: Optional[str] = None) -> "set[str]":
    """The tenant's DECLARED capability universe -- the set a ``capabilities:`` block may
    attach from. Union of: the base catalog slugs + the kinds_overlay custom (`kinds:`)
    cards + the capability_map ``inherited_base`` keys + ``custom_capabilities`` slugs.

    Liberal by design (a SUPERSET is safe -- it only widens the attach gate's
    intersection guard, never narrows it). DEGRADE-NEVER: each source is guarded; the
    base catalog is always present so the result is never empty for a real tenant."""
    declared: "set[str]" = {r.capability for r in _load_catalog()}
    try:
        for card in _overlay_custom_cards(tenant_id):
            declared.add(card.capability)
    except Exception:
        pass
    try:
        # LIST path: sovereign-aware reader (ROOT fallback) so a distilled repo's own
        # capability_map (custom_capabilities + inherited_base) enters the declared set.
        # The WRITE path keeps _read_capability_map_raw (tenant-scoped, for atomic writeback).
        raw = _read_cap_map_for_cards(tenant_id)
        ib = raw.get("inherited_base")
        if isinstance(ib, Mapping):
            declared |= {str(k).strip() for k in ib.keys() if str(k).strip()}
        cc = raw.get("custom_capabilities")
        if isinstance(cc, list):
            for entry in cc:
                if isinstance(entry, Mapping):
                    slug = entry.get("capability")
                    if isinstance(slug, str) and slug.strip():
                        declared.add(slug.strip())
    except Exception:
        pass
    return declared


# --------------------------------------------------------------------------- #
# Composition control plane -- WRITERS + state + intent seam (W2).
#
# These are the W2 WRITE/control surface on top of the W1 read gate (resolve_enabled). They
# are the ONLY mutation in this module -- the catalog/overlay READS above stay pure. The
# authoritative state is the ``capabilities:{enabled,disabled,log}`` block in the tenant's
# git-versioned ``capability_map.yaml`` (decision D2). A write loads the FULL overlay, mutates
# ONLY the ``capabilities:`` block, and replaces the file atomically -- preserving every other
# block (inherited_base/custom_capabilities/managed_entities/...).
#
# ATTACH SEMANTICS (the compose model, spec SS3.1): ``attach`` ADDS the slug to the ``enabled``
# allowlist (and removes it from ``disabled``); ``detach`` removes it from ``enabled`` (and adds
# it to ``disabled``). Once any capability is attached, ``enabled`` is the explicit allowlist
# (only enabled capabilities run) -- this is the intended "compose this tenant's dashboard from
# explicit modules" behavior. An un-composed tenant (no block) stays ALLOW-ALL (zero regression).
#
# FAIL-CLOSED (writes): a slug MUST be in the DECLARED universe (declared_capabilities) to be
# toggled -> CapabilityNotDeclared, raised BEFORE any file touch. A present-but-unparseable
# overlay is REFUSED (never clobbered). The tenant path is resolved through the fail-closed
# cex_tenant_paths guard. A write LOCK that cannot be acquired within the retry window ALSO
# refuses (CapabilityLockBusy, R-191) rather than proceeding unlocked -- see
# _overlay_write_lock.
# --------------------------------------------------------------------------- #
def _now_iso() -> str:
    """A UTC ISO-8601 timestamp (second precision) for a provenance log row. ASCII."""
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()


def _resolve_cap_map_write_path(tenant_id: Optional[str]) -> Path:
    """Resolve the WRITE path for the tenant ``capability_map.yaml`` via the fail-closed
    cex_tenant_paths guard (surface='overlay', create=True so the parent dir exists).

    Distinct from the degrade-never READ (_read_capability_map_raw): a write MUST resolve a
    real, guarded path -- a hostile / escaping CEX_TENANT_ID makes the guard raise SystemExit
    (fail-closed), which the caller surfaces as a write error rather than clobbering anything."""
    tools_dir = str(Path(__file__).resolve().parent)
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    import cex_tenant_paths as _tp  # type: ignore[import]
    return _tp.resolve_tenant_path(
        _CAP_MAP_FILENAME, surface="overlay", tenant_id=tenant_id, create=True)


def _load_overlay_for_write(path: Path) -> Dict[str, Any]:
    """Load the FULL overlay dict for a guarded WRITE -- FAIL-CLOSED (NOT degrade-never).

    An absent file -> {} (a fresh overlay is fine). A present-but-unparseable file, or a
    top-level that is not a mapping, RAISES -- the writer must never clobber an overlay it
    cannot round-trip. Requires PyYAML (a write dependency); its absence raises RuntimeError."""
    if not path.exists():
        return {}
    try:
        import yaml
    except Exception as exc:  # PyYAML is required to safely round-trip a write
        raise RuntimeError("PyYAML is required to write %s" % _CAP_MAP_FILENAME) from exc
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(
            "%s top-level is not a mapping; refusing to clobber" % _CAP_MAP_FILENAME)
    return data


def _replace_capabilities_block(original: str, block_text: str) -> str:
    """Return ``original`` with its top-level ``capabilities:`` block replaced by ``block_text``,
    keeping every OTHER line VERBATIM (comments + other top-level blocks survive). When no
    top-level ``capabilities:`` block exists, APPEND ``block_text`` at EOF without disturbing the
    existing text. ``block_text`` is the regenerated ``capabilities:\\n  ...`` YAML rendering.

    Block span: the line ``capabilities:`` at column 0 starts it; it ends at the next line at
    column 0 that is NON-BLANK -- whether a comment OR another top-level key. So a comment that
    sits 'elsewhere' (between the block and the next key, or anywhere outside the block) is NEVER
    inside the replaced span and is preserved. Trailing blank lines before the next token are
    pushed into the tail (a blank separator survives). Pure + total: never raises."""
    lines = original.splitlines(keepends=True)
    start: Optional[int] = None
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not s or s.startswith("#"):
            continue                       # blank or comment line
        if ln[:1].isspace():
            continue                       # indented -> inside some other block
        if ":" in s and s.split(":", 1)[0].strip() == "capabilities":
            start = i
            break
    blk = block_text if block_text.endswith("\n") else block_text + "\n"
    if start is None:
        # No capabilities block yet -> append at EOF (ensure the head ends with a newline).
        sep = "" if (not original or original.endswith("\n")) else "\n"
        return original + sep + blk
    end = len(lines)
    for j in range(start + 1, len(lines)):
        ln = lines[j]
        if not ln.strip():
            continue                       # blank: tentatively still in the span
        if not ln[:1].isspace():
            end = j                        # column-0 non-blank (key OR comment) -> span ends
            break
    # Keep blank lines that separate the block from the next token in the TAIL (preserve spacing).
    while end - 1 > start and not lines[end - 1].strip():
        end -= 1
    head = "".join(lines[:start])
    tail = "".join(lines[end:])
    return head + blk + tail


def _atomic_write(path: Path, text: str) -> None:
    """Write ``text`` to ``path`` atomically + RACE-SAFELY (no fixed-name tmp collision).

    A UNIQUE temp file in the SAME directory via ``tempfile.mkstemp`` (so two concurrent writers
    never clobber a shared ``<name>.tmp``) then ``os.replace`` (atomic on the same filesystem).
    The temp file is cleaned up on any failure so a half-written write never leaks. UTF-8 (the
    ASCII rule governs CODE, not the YAML data this writes -- accented labels round-trip)."""
    directory = path.parent
    directory.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(directory), prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp_name, str(path))
    except Exception:
        try:
            if os.path.exists(tmp_name):
                os.remove(tmp_name)
        except OSError:
            pass
        raise


# --------------------------------------------------------------------------- #
# arch-council C1 lockfile hardening (R-191, SHOKUNIN finding): the per-tenant overlay write-lock
# used to DEGRADE-NEVER proceed UNLOCKED on contention -- tolerable for an ordinary overlay edit,
# but a lost update on a SENSITIVE/PAID capability's enabled/disabled set can silently re-enable
# (or silently fail to disable) a capability that spends money. The fix keeps the SAME lockfile
# path/format (other readers may probe ``<overlay>.lock``) and the same 50x0.02s sleep-budget acquire
# window, but changes the FAILURE OUTCOME: acquisition that is never satisfied within the window
# now RAISES (CapabilityLockBusy) instead of continuing unlocked. To keep one crashed writer from
# wedging every future caller FOREVER, the lock marker now carries {pid, acquired_at} and a lock
# that looks abandoned -- too old, or owned by a pid that is no longer alive -- is reclaimed
# (removed + retried) rather than honored.
# --------------------------------------------------------------------------- #
_LOCK_ACQUIRE_ATTEMPTS = 50            # 50 * 0.02s sleep budget; WALL time is higher (stale-check
                                       # I/O per attempt: ~3s worst-case measured on Windows, R-191 judge)
_LOCK_POLL_SECONDS = 0.02
# A real read-modify-write of this small YAML file completes in low milliseconds; even a
# generously slow disk should never legitimately hold this lock for 30s -- so a marker older than
# that is reclaimable regardless of whether its pid is still alive (a hung-but-alive holder must
# not wedge the lock forever either).
_LOCK_STALE_SECONDS = 30.0


def _pid_alive(pid: int) -> bool:
    """Cross-platform best-effort liveness check for a lock marker's ``pid`` (mirrors
    cex_evolve._pid_alive / cex_lock._pid_alive's heuristic; duplicated -- not imported -- so this
    module keeps its own bespoke, same-directory lockfile scheme rather than adopting cex_lock's
    separate LOCK_DIR layout, which would break the 'same lockfile path/format' invariant other
    readers may rely on (module docstring: stdlib + yaml only, no cross-module lock-dir coupling).

    Any inability to determine liveness (tasklist unavailable, EPERM on os.kill) is treated as
    ALIVE -- failing toward 'do not reclaim' is the safe direction (reclaiming a genuinely live
    holder's lock would reintroduce the exact lost-update bug this hardening fixes). Exposed at
    module level (not nested) so tests can monkeypatch it directly for deterministic alive/dead
    cases, matching the cex_evolve.py test convention."""
    if pid <= 0:
        return False
    if sys.platform == "win32":
        import subprocess
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "PID eq %d" % pid, "/NH"],
                capture_output=True, text=True, timeout=5)
            return str(pid) in (result.stdout or "")
        except Exception:
            return True
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # exists, owned by another user
    except OSError:
        return True
    return True


def _write_lock_marker(lock_path: Path) -> None:
    """Exclusively CREATE ``lock_path`` (O_CREAT|O_EXCL|O_WRONLY) and write a small pid+timestamp
    JSON marker into it (enables ``_lock_is_stale`` to later tell a dead/expired holder from a
    live one). Raises FileExistsError when the lock is already held, or any other OSError on a
    hard I/O failure (e.g. permissions) -- both propagate to the caller, which decides whether the
    failure is retryable."""
    fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        os.write(fd, json.dumps({"pid": os.getpid(), "acquired_at": _now_iso()}).encode("ascii"))
    finally:
        os.close(fd)


def _read_lock_marker(lock_path: Path) -> Optional[Dict[str, Any]]:
    """Read + parse a lock marker written by ``_write_lock_marker``. None if the file is absent,
    unreadable, empty, unparseable, or not a JSON object (also covers a legacy 0-byte marker from
    before this hardening -- it reads back as None, same as any other corrupt marker). Never
    raises."""
    try:
        raw = lock_path.read_text(encoding="ascii")
    except OSError:
        return None
    if not raw.strip():
        return None
    try:
        data = json.loads(raw)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _lock_is_stale(lock_path: Path) -> bool:
    """True iff the lock at ``lock_path`` looks ABANDONED and is safe to reclaim: an unreadable /
    corrupt / legacy-empty marker, an ``acquired_at`` older than ``_LOCK_STALE_SECONDS``, or a
    recorded ``pid`` that is no longer alive. A marker that parses cleanly, is fresh, AND whose pid
    is confirmed (or assumed, on a liveness-check failure) alive is treated as LIVE (False) --
    every branch here fails toward 'still live' except a marker offering no evidence of one,
    because reclaiming a genuinely live holder's lock would reintroduce the exact lost-update bug
    this hardening fixes."""
    marker = _read_lock_marker(lock_path)
    if marker is None:
        return True
    try:
        age = (datetime.datetime.now(datetime.timezone.utc)
               - datetime.datetime.fromisoformat(str(marker.get("acquired_at")))).total_seconds()
    except Exception:
        return True  # missing/unparseable timestamp -- cannot prove freshness
    if age > _LOCK_STALE_SECONDS:
        return True
    pid = marker.get("pid")
    if isinstance(pid, int) and pid > 0 and not _pid_alive(pid):
        return True
    return False


@contextlib.contextmanager
def _overlay_write_lock(path: Path) -> "Iterator[None]":
    """A PER-TENANT write lock serializing the read-modify-write of ONE tenant's overlay (an
    operator toggle vs an N07 intent attach race -> a lost update otherwise).

    FAIL-CLOSED (arch-council C1 hardening, R-191): an exclusive lockfile (``os.open``
    O_CREAT|O_EXCL) next to the overlay, carrying a small pid+timestamp marker. Acquisition
    retries within the SAME 50-attempt bounded window as before (~3s wall worst-case incl. per-attempt
    stale-check I/O -- measured, not ~1s); a lock found STALE (age > 30s, a dead
    owner pid, or an unreadable/corrupt marker) is reclaimed (removed) and retried immediately,
    without spending a poll sleep. If the window is exhausted -- or the lockfile itself cannot
    even be created (a hard OSError, e.g. permissions) -- we RAISE ``CapabilityLockBusy`` instead
    of proceeding unlocked. A refused attach/detach is recoverable (the caller retries); a
    silently lost update to a paid/sensitive capability's enabled/disabled set is not (that was
    the R-191 defect this replaces).

    Always releases (removes the lockfile) on exit, even on error -- but ONLY when this call is
    the one that created it (a failed acquisition never touches a lock it does not own)."""
    lock_path = path.with_name(path.name + ".lock")
    acquired = False
    hard_error: Optional[OSError] = None
    for _ in range(_LOCK_ACQUIRE_ATTEMPTS):
        try:
            _write_lock_marker(lock_path)
            acquired = True
            break
        except FileExistsError:
            if _lock_is_stale(lock_path):
                try:
                    lock_path.unlink()
                except OSError:
                    pass
                continue        # retry acquisition immediately; a reclaim spends no poll sleep
            time.sleep(_LOCK_POLL_SECONDS)
        except OSError as exc:
            hard_error = exc
            break                # not contention -- retrying within the window would not help
    if not acquired:
        raise CapabilityLockBusy(lock_path, holder=_read_lock_marker(lock_path), cause=hard_error)
    try:
        yield
    finally:
        try:
            os.remove(str(lock_path))
        except OSError:
            pass


def _dump_overlay_atomic(path: Path, data: Mapping[str, Any]) -> None:
    """Persist the overlay after a ``capabilities:`` mutation -- SURGICAL + atomic.

    COMMENT-PRESERVING (no ruamel dependency): rather than re-dumping the WHOLE overlay (which
    would strip every ``#`` comment from the git-versioned, hand-authored file), read the file as
    TEXT and replace ONLY the ``capabilities:`` block with the regenerated block, keeping the rest
    VERBATIM (``_replace_capabilities_block``). A brand-new / empty overlay (no text to preserve)
    is rendered in full. Key ORDER + every non-capabilities block + comments survive. UTF-8 data
    values are kept verbatim (allow_unicode=True). The write itself is atomic + race-safe
    (``_atomic_write``); the caller holds ``_overlay_write_lock`` around the read-modify-write."""
    import yaml
    cap_block = {"capabilities": dict(data.get("capabilities", {}) or {})}
    block_text = yaml.safe_dump(
        cap_block, sort_keys=False, allow_unicode=True, default_flow_style=False)
    original = path.read_text(encoding="utf-8") if path.exists() else ""
    if original.strip():
        # Surgical: keep every other block + its comments exactly; swap only capabilities.
        text = _replace_capabilities_block(original, block_text)
    else:
        # Fresh / empty overlay -> render the full dict (no comments to lose).
        text = yaml.safe_dump(
            dict(data), sort_keys=False, allow_unicode=True, default_flow_style=False)
    _atomic_write(path, text)


def attach_state(tenant_id: Optional[str] = None) -> Dict[str, List[str]]:
    """The tenant's full ATTACH state: ``{declared, enabled, disabled}`` (sorted lists).

    * declared = the declared universe (declared_capabilities: base catalog + inherited_base +
      custom_capabilities);
    * enabled  = resolve_enabled(declared) -- the W1 gate applied to that universe;
    * disabled = declared - enabled (every declared capability that is currently OFF).
    declared is the clean partition enabled + disabled, so the compose UI (W3) can render every
    declared capability with its on/off toggle. DEGRADE-NEVER (a read; delegates to the
    degrade-never gate). NEVER raises."""
    declared = declared_capabilities(tenant_id)
    enabled = resolve_enabled(tenant_id, declared)
    disabled = set(declared) - set(enabled)
    return {
        "declared": sorted(declared),
        "enabled": sorted(enabled),
        "disabled": sorted(disabled),
    }


def _mutate_capabilities(
    tenant_id: Optional[str], capability: str, action: str, by: str
) -> Dict[str, List[str]]:
    """The shared attach/detach core: FAIL-CLOSED declared-check -> guarded YAML mutation.

    Raises CapabilityNotDeclared BEFORE any file touch when ``capability`` is not declared.
    Loads the FULL overlay (fail-closed parse), mutates ONLY the ``capabilities:`` block, appends
    a provenance log row, writes back atomically, and returns the new attach_state."""
    cap = (capability or "").strip()
    declared = declared_capabilities(tenant_id)
    if not cap or cap not in declared:
        raise CapabilityNotDeclared(cap or (capability or ""), tenant_id=tenant_id or "")

    path = _resolve_cap_map_write_path(tenant_id)
    # Serialize the read-modify-write per tenant: a concurrent operator toggle vs an N07 intent
    # attach must not lose an update. FAIL-CLOSED (R-191): a lock that cannot be acquired within
    # the retry window raises CapabilityLockBusy rather than proceeding unlocked -- see
    # _overlay_write_lock's docstring for the stale-lock reclaim + hard-error handling.
    with _overlay_write_lock(path):
        data = _load_overlay_for_write(path)

        block = data.get("capabilities")
        if not isinstance(block, dict):
            block = {}
        enabled = _slug_list(block.get("enabled"))
        disabled = _slug_list(block.get("disabled"))
        log = block.get("log")
        log = list(log) if isinstance(log, list) else []

        if action == "attach":
            if cap not in enabled:
                enabled.append(cap)
            disabled = [s for s in disabled if s != cap]
        else:  # detach
            enabled = [s for s in enabled if s != cap]
            if cap not in disabled:
                disabled.append(cap)
        log.append({"capability": cap, "action": action, "by": by, "at": _now_iso()})

        # Reassign in place so "capabilities" keeps its position in the file (zero-noise diff).
        data["capabilities"] = {"enabled": enabled, "disabled": disabled, "log": log}
        _dump_overlay_atomic(path, data)
    return attach_state(tenant_id)


def attach_capability(
    tenant_id: Optional[str], capability: str, *, by: str = "n07"
) -> Dict[str, List[str]]:
    """ATTACH ``capability`` for ``tenant_id`` (add to ``enabled``, remove from ``disabled``,
    log the action, write the overlay back). FAIL-CLOSED: ``capability`` MUST be declared
    (CapabilityNotDeclared otherwise -- you cannot attach what is not declared). Returns the new
    attach_state. ``by`` is the actor recorded in the log (default 'n07' for the intent-driven
    path; the dashboard PATCH path passes 'operator')."""
    return _mutate_capabilities(tenant_id, capability, "attach", by)


def detach_capability(
    tenant_id: Optional[str], capability: str, *, by: str = "n07"
) -> Dict[str, List[str]]:
    """DETACH ``capability`` for ``tenant_id`` (remove from ``enabled``, add to ``disabled``,
    log it, write back) -- the exact reverse of attach_capability. FAIL-CLOSED on an undeclared
    slug (CapabilityNotDeclared). Returns the new attach_state."""
    return _mutate_capabilities(tenant_id, capability, "detach", by)


def propose_attach(tenant_id: Optional[str], capability: str) -> Optional[Dict[str, Any]]:
    """The N07 intent auto-attach SEAM -- PURE + READ-ONLY (no write).

    Returns an attach PROPOSAL ``{capability, declared: True, attached: False, action: "attach"}``
    ONLY when ``capability`` is DECLARED for the tenant but NOT currently enabled; else None
    (None for an already-enabled capability AND for an undeclared one). N07 calls this after
    cex_intent_resolver resolves an intent: a proposal -> N07 confirms (GDP) -> calls
    attach_capability; None -> nothing to propose. DEGRADE-NEVER: any read failure -> None
    (no spurious proposal). NEVER raises, NEVER writes."""
    cap = (capability or "").strip()
    if not cap:
        return None
    try:
        declared = declared_capabilities(tenant_id)
        if cap not in declared:
            return None
        if cap in resolve_enabled(tenant_id, declared):
            return None
    except Exception:
        return None
    return {"capability": cap, "declared": True, "attached": False, "action": "attach"}


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def list_capabilities(tenant_id: Optional[str] = None) -> List[CapabilityRecord]:
    """The VISIBLE capability cards for a tenant (spec B.4 / D.2), OVERLAY-FIRST.

    Computation (spec B.4):
      base_cards    = the catalog base set (this file).
      enabled       = the tenant overlay's enabled_capabilities list (spec D.3),
                      or None (no gate => all base cards).
      overlay_cards = the tenant overlay `kinds:` cards (custom, always shown).
      VISIBLE       = (base_cards filtered by enabled) ++ overlay_cards

    DEGRADE-NEVER: a missing/malformed overlay -> enabled=None + no overlay cards
    -> ALL base cards (the global default). The single-tenant default (no tenant)
    is exactly the base catalog.

    Returns base cards in catalog order, then overlay cards. Each base card's
    ``enabled`` flag reflects the gate; a base card filtered OUT is omitted (not
    returned disabled) so the dashboard never renders a hidden card -- matching the
    spec B.4 "Cards NOT enabled are hidden".
    """
    base = _load_catalog()
    enabled = _enabled_capabilities(tenant_id)

    visible: List[CapabilityRecord] = []
    if enabled is None:
        # No gate: all base cards, enabled=True.
        visible.extend(base)
    else:
        allow = set(enabled)
        for rec in base:
            if rec.capability in allow:
                visible.append(rec)  # enabled=True by construction

    # Append tenant-custom overlay cards (always shown if present). A custom card
    # that shares a slug with a base card replaces the base card's visibility iff
    # the base one was filtered out; if both are present we keep both only when the
    # slugs differ. To avoid duplicate slugs in the output, drop a custom card whose
    # slug already appears in the visible base set.
    seen_slugs = {r.capability for r in visible}
    for card in _overlay_custom_cards(tenant_id):
        if card.capability in seen_slugs:
            continue
        seen_slugs.add(card.capability)
        visible.append(card)

    # Also append capability_map.yaml custom cards (slug-based, not phrase-based).
    # These close the AI-app link gap: the dashboard sends a proper slug like 'crm',
    # which resolves to kind='demo_acme_crm'. Phrases from kinds_overlay were already added
    # above; deduplicate against them so a slug that coincidentally matches a phrase
    # is not shown twice.
    for card in _cap_map_custom_cards(tenant_id):
        if card.capability in seen_slugs:
            continue
        seen_slugs.add(card.capability)
        visible.append(card)

    return visible


def resolve_capability(
    slug: str,
    tenant_id: Optional[str] = None,
) -> CapabilityRecord:
    """The full record for ONE capability slug (spec A.3), OVERLAY-FIRST.

    Resolution order:
      1. tenant overlay ``kinds:`` card whose slug matches -> wins (phrase-keyed custom).
      2. capability_map ``custom_capabilities`` card whose slug matches -> overlay card
         (closes the AI-app link gap: 'crm' resolves to demo_acme_crm even though
         ``kinds_overlay.yaml`` only carries intent PHRASES like 'leads b2b').
      3. base catalog card with that slug.
      4. neither -> CapabilityUnknown.
    A resolved card whose kind is in the 8F MOAT -> CapabilityFrozen (belt-and
    -braces; the overlay loader already rejects frozen kinds). DEGRADE-NEVER on the
    overlay read.

    NOTE: resolve_capability returns a record REGARDLESS of the enabled_capabilities
    gate -- that gate governs VISIBILITY (list_capabilities), not resolvability. The
    runtime (cex_run_capability) enforces the enabled gate separately BEFORE
    resolving (spec A.2 step 2b). This keeps the two concerns orthogonal.
    """
    key = (slug or "").strip()
    eff = _effective_tenant_id(tenant_id)
    if not key:
        raise CapabilityUnknown(slug, tenant_id=eff or "")

    # 1. kinds_overlay phrase-keyed custom card (overlay-first, unchanged).
    for card in _overlay_custom_cards(tenant_id):
        if card.capability == key:
            _assert_not_frozen(card, eff)
            return card

    # 2. capability_map slug-keyed custom card (AI-app link gap fix).
    #    The dashboard sends a proper slug ('crm'), not an intent phrase ('leads b2b').
    #    declared_capabilities() already reads this source; resolve_capability now does too.
    for card in _cap_map_custom_cards(tenant_id):
        if card.capability == key:
            _assert_not_frozen(card, eff)
            return card

    # 3. base catalog.
    rec = _base_index().get(key)
    if rec is not None:
        _assert_not_frozen(rec, eff)
        return rec

    # 4. unknown.
    raise CapabilityUnknown(key, tenant_id=eff or "")


def _assert_not_frozen(rec: CapabilityRecord, tenant_id: Optional[str]) -> None:
    """Refuse a record that targets an 8F-moat frozen kind (CapabilityFrozen)."""
    if rec.kind in _FROZEN_KINDS:
        raise CapabilityFrozen(rec.capability, rec.kind, tenant_id=tenant_id or "")


def base_capabilities() -> List[CapabilityRecord]:
    """All BASE catalog cards (tenant-agnostic), in display order. Convenience for
    the dashboard's 'all available' view and for tests."""
    return list(_load_catalog())


def reset_cache() -> None:
    """Clear the catalog cache. For tests that swap CATALOG_PATH at runtime. The
    overlay reads are not cached (they re-read per call), so only the base catalog
    needs a reset."""
    global _catalog_cache
    _catalog_cache = None


__all__ = [
    "CapabilityRecord",
    "CapabilityUnknown",
    "CapabilityFrozen",
    "CapabilityNotDeclared",
    "CapabilityLockBusy",
    "list_capabilities",
    "resolve_capability",
    "base_capabilities",
    "reset_cache",
    "CATALOG_PATH",
    # Composition control plane (mission DASHBOARD_COMPOSITION W1).
    "resolve_enabled",
    "declared_capabilities",
    "compose_gate_active",
    # arch-council C1 -- sensitive-cap fail-closed primitives.
    "is_sensitive_capability",
    "capability_map_unparseable",
    # Composition control plane WRITERS + state + intent seam (W2).
    "attach_state",
    "attach_capability",
    "detach_capability",
    "propose_attach",
]


# --------------------------------------------------------------------------- #
# CLI (read-only; for operator inspection). No mutation, no network.
# --------------------------------------------------------------------------- #
def _main(argv: List[str]) -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="CEXAI capability registry -- list / resolve dashboard cards")
    parser.add_argument("slug", nargs="?",
                        help="resolve ONE capability slug (omit to list)")
    parser.add_argument("--tenant", default=None,
                        help="tenant id (overlay-first; default CEX_TENANT_ID)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args(argv)

    if args.slug:
        try:
            rec = resolve_capability(args.slug, tenant_id=args.tenant)
        except CapabilityUnknown as exc:
            print("[FAIL] %s" % exc, file=sys.stderr)
            return 1
        except CapabilityFrozen as exc:
            print("[FAIL] %s" % exc, file=sys.stderr)
            return 2
        if args.json:
            print(json.dumps(rec.to_card(), indent=2))
        else:
            print("  [OK] %s -> %s/%s (%s) verb=%s  %s"
                  % (rec.capability, rec.nucleus, rec.kind, rec.pillar, rec.verb,
                     rec.title))
        return 0

    cards = list_capabilities(tenant_id=args.tenant)
    if args.json:
        print(json.dumps([c.to_card() for c in cards], indent=2))
    else:
        print("  Capabilities (%d) tenant=%s:"
              % (len(cards), args.tenant or os.environ.get(_ENV_TENANT_ID) or "(none)"))
        for c in cards:
            print("    %-12s %-22s %s/%s [%s]  %s"
                  % (c.capability, c.kind, c.nucleus, c.pillar, c.source, c.title))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))

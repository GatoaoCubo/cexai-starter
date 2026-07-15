"""The blueprint catalog -- the four CEXAI stack verticals + their disposition.

Two are APPLY-able template stacks (``company_stack`` 16, ``saas_stack`` 17): their
feature templates are packaged data and ``cexai blueprint apply`` freezes them
against a deployer config. Two are NOT apply-able:

  * ``aitmpl_stack`` (18) is a REFERENCE CATALOG -- 1,841 community items
    (davila7/claude-code-templates, MIT) that live in ``cexai-specs/18_aitmpl_stack``
    and are NEVER packaged into the wheel. The catalog describes its categories and
    points at ATTRIBUTION; it cannot be ``apply``-ed.
  * ``osb_stack`` (19) is a PROTOCOL -- the Open Service Broker provisioning
    lifecycle, distilled into the ``capability_provisioning_protocol`` artifact that
    ships as a single data file. It is shown, not frozen.

The counts for 18 are the documented values from
``cexai-specs/18_aitmpl_stack/{INDEX.md,ATTRIBUTION.md}`` (source SHA recorded), not
runtime-derived -- the corpus is intentionally out of the package. They are marked
approximate. This module is pure data + lookups; it imports nothing heavy so
``blueprint list`` stays dependency-free.

absorbs: cexai-specs/16_company_stack + 17_saas_stack + 18_aitmpl_stack + 19_osb_stack
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

__all__ = [
    "StackInfo",
    "STACKS",
    "STACK_IDS",
    "get_stack",
    "is_applyable",
    "OSB_LIFECYCLE",
]

# The OSB provisioning lifecycle phases (vertical 19). The protocol artifact in
# data/osb_stack/ is the full distillation; this ordered tuple is the summary the
# catalog renders for ``blueprint show osb_stack``.
OSB_LIFECYCLE: tuple[tuple[str, str], ...] = (
    ("catalog", "advertise the services + plans a broker offers (capability_registry)"),
    ("provision", "create a service instance from a (service, plan) selection"),
    ("bind", "issue credentials/endpoint that let a consumer use an instance"),
    ("unbind", "revoke a previously issued binding"),
    ("deprovision", "destroy a service instance and release its resources"),
)


@dataclass(frozen=True, slots=True)
class StackInfo:
    """One catalog entry. ``stack_id`` is the addressable id; ``vertical`` is its
    cexai-specs number; ``title`` is the display name; ``summary`` is the one-line
    ``list`` description; ``mode`` is ``apply`` | ``reference`` | ``protocol``;
    ``applyable`` is True only for the two template stacks; ``specs_path`` points at
    the cexai-specs source; ``detail`` carries mode-specific metadata (aitmpl
    categories, osb lifecycle pointer) rendered by ``show``."""

    stack_id: str
    vertical: str
    title: str
    summary: str
    mode: str
    applyable: bool
    specs_path: str
    detail: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))


_STACKS: dict[str, StackInfo] = {
    "company_stack": StackInfo(
        stack_id="company_stack",
        vertical="16_company_stack",
        title="Company Stack",
        summary=(
            "Apply-able: end-to-end company stack (frontend, admin console, CRM, "
            "content factory, commerce) as parameterized feature templates."
        ),
        mode="apply",
        applyable=True,
        specs_path="cexai-specs/16_company_stack/templates/",
        detail=MappingProxyType({"chain": ("constitution", "spec", "plan", "tasks", "analyze")}),
    ),
    "saas_stack": StackInfo(
        stack_id="saas_stack",
        vertical="17_saas_stack",
        title="SaaS Stack",
        summary=(
            "Apply-able: SaaS-specific feature templates (onboarding, subscriptions, "
            "tier gating, usage metering, API keys) + features inherited from "
            "company_stack via feature_ref."
        ),
        mode="apply",
        applyable=True,
        specs_path="cexai-specs/17_saas_stack/templates/",
        detail=MappingProxyType(
            {"inherits_from": "company_stack", "inherit_manifest": "cexai-specs/17_saas_stack/feature_refs.yaml"}
        ),
    ),
    "aitmpl_stack": StackInfo(
        stack_id="aitmpl_stack",
        vertical="18_aitmpl_stack",
        title="AITmpl Reference Catalog",
        summary=(
            "Reference-only: 1,841 community items (davila7/claude-code-templates, "
            "MIT) across 6 categories. Browse in cexai-specs; NOT apply-able."
        ),
        mode="reference",
        applyable=False,
        specs_path="cexai-specs/18_aitmpl_stack/",
        detail=MappingProxyType(
            {
                # Documented in cexai-specs/18_aitmpl_stack/INDEX.md (approximate) +
                # ATTRIBUTION.md (corpus size + provenance). NOT runtime-derived: the
                # corpus is intentionally never packaged into the wheel.
                "counts_are_approximate": True,
                "total_unique_items": 1841,
                "categories": MappingProxyType(
                    {
                        "agents": 434,
                        "commands": 341,
                        "skills": 847,
                        "hooks": 73,
                        "mcps": 86,
                        "settings": 70,
                    }
                ),
                "crew_templates": 7,
                "source_repo": "davila7/claude-code-templates",
                "source_license": "MIT",
                "source_sha": "8022acfc067c7b3214f0f90484908279effa87f2",
                "attribution": "cexai-specs/18_aitmpl_stack/ATTRIBUTION.md",
                "reason_not_applyable": (
                    "Vendored reference corpus, not parameterized templates. Use the "
                    "items directly from cexai-specs with cascade attribution."
                ),
            }
        ),
    ),
    "osb_stack": StackInfo(
        stack_id="osb_stack",
        vertical="19_osb_stack",
        title="OSB Provisioning Protocol",
        summary=(
            "Protocol: Open Service Broker capability provisioning lifecycle "
            "(catalog -> provision -> bind -> unbind -> deprovision) bound to "
            "capability_registry. Reuses existing kinds; not apply-able."
        ),
        mode="protocol",
        applyable=False,
        specs_path="cexai-specs/19_osb_stack/_meta/inventory_baseline.md",
        detail=MappingProxyType(
            {
                "artifact": "capability_provisioning_protocol",
                "artifact_file": "data/osb_stack/capability_provisioning_protocol.md",
                "lifecycle": OSB_LIFECYCLE,
                "source_repo": "openservicebrokerapi/servicebroker",
                "source_release": "v2.17",
                "source_license": "Apache-2.0",
                "reuses_kinds": ("openapi_spec", "interface", "pattern", "capability_registry", "workflow"),
                "reason_not_applyable": (
                    "A provisioning protocol bound to capability_registry, not a "
                    "parameterized artifact set. Shown, not frozen."
                ),
            }
        ),
    ),
}

STACKS: Mapping[str, StackInfo] = MappingProxyType(_STACKS)
# Stable display order: apply-able stacks first, then reference, then protocol.
STACK_IDS: tuple[str, ...] = ("company_stack", "saas_stack", "aitmpl_stack", "osb_stack")


def get_stack(stack_id: str) -> StackInfo:
    """Look up a catalog entry. Raises ``KeyError`` for an unknown stack id."""
    try:
        return STACKS[stack_id]
    except KeyError:
        raise KeyError(
            f"unknown stack {stack_id!r}; known stacks: {', '.join(STACK_IDS)}"
        ) from None


def is_applyable(stack_id: str) -> bool:
    """True only for the two template stacks (company_stack, saas_stack)."""
    return get_stack(stack_id).applyable

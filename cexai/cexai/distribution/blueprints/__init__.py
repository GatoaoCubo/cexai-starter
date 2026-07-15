"""CEXAI stack blueprints -- the executable layer over verticals 16/17/18/19.

A stack blueprint is a typed set of parameterized feature templates (Article XIX
``open_vars``) that a deployer FREEZES against their own ``brand_config`` to get a
runnable, brand-specific artifact set. This package is the v1.0 executable layer the
specs deferred:

  * ``catalog``  -- the four stacks + their disposition (apply / reference / protocol).
  * ``loader``   -- parse packaged feature templates (16/17) into typed ``FeatureTemplate``
        objects (REUSES ``open_vars.parse_open_var``).
  * ``freeze``   -- resolve open_vars from a config + write frozen artifacts
        (``_open_vars_frozen: true`` per ADR 022 FR-014; REUSES ``validate_open_var``).
  * ``cli``      -- the ``blueprint_app`` typer sub-app (list/show/apply), delegated
        from the foundation CLI as ``cexai blueprint`` (the spec-kit precedent).

Founder rule (taxonomy-neutral): ZERO new kinds, no ``.cex/kinds_meta.json`` edit.
Feature templates are validated by the open_vars protocol + this package's contract
tests; the vertical-19 ``capability_provisioning_protocol`` is a workflow/pattern
instance over EXISTING kinds. Vertical 18's 6,550-file corpus is NEVER packaged --
the catalog describes it and points at cexai-specs + ATTRIBUTION.

absorbs: cexai-specs/16_company_stack + 17_saas_stack + 18_aitmpl_stack + 19_osb_stack
"""

from cexai.distribution.blueprints.catalog import (
    STACK_IDS,
    STACKS,
    StackInfo,
    get_stack,
    is_applyable,
)
from cexai.distribution.blueprints.cli import blueprint_app
from cexai.distribution.blueprints.freeze import (
    ApplyResult,
    BlueprintApplyError,
    FrozenFeature,
    MissingVar,
    ResolvedVar,
    apply_stack,
    load_config,
    resolve_feature,
)
from cexai.distribution.blueprints.loader import (
    TEMPLATE_STACKS,
    FeatureTemplate,
    MalformedDecl,
    feature_count,
    feature_names,
    load_features,
)

__all__ = [
    # catalog
    "StackInfo",
    "STACKS",
    "STACK_IDS",
    "get_stack",
    "is_applyable",
    # loader
    "FeatureTemplate",
    "MalformedDecl",
    "TEMPLATE_STACKS",
    "load_features",
    "feature_names",
    "feature_count",
    # freeze
    "ResolvedVar",
    "MissingVar",
    "FrozenFeature",
    "ApplyResult",
    "BlueprintApplyError",
    "apply_stack",
    "resolve_feature",
    "load_config",
    # cli
    "blueprint_app",
]

"""CEXAI spec-kit subsystem -- native Spec-Driven Development tooling.

The v1.0 wave that turns absorbed spec-kit (cexai-specs/01_spec-kit, "the
methodology IS the deliverable") into NATIVE CEX tooling. spec-kit's chain is
``Constitution -> Spec -> Plan -> Tasks -> Analyze -> Implement``; CEX already has
``/spec`` and ``/plan`` skills (the scaffold steps) and an 8F ``Implement``, but the
retro (gap #2) identified two real missing capabilities, now built here:

  * ``analyze``     -- the cross-artifact consistency checker (spec vs plan vs tasks):
        orphan requirements, unimplemented user stories, dangling task references,
        unresolved clarification markers. CEX's F7 GOVERN gates ONE artifact; this is
        the comparator across the set. (analyze.py)
  * ``compliance``  -- the ADR 013 per-article constitution gate: the automatable
        article subset graded against the repo + the rest registered manual/ci-only.
        (compliance.py)
  * thin scaffolders -- ``init|spec|plan|tasks`` emit the spec-kit templates
        (templates.py); the lower-value steps CEX skills already cover, kept thin.

Founder rule (taxonomy-neutral): everything here is CODE. The spec-kit artifacts
reuse EXISTING kinds (Constitution -> axiom + constitutional_rule; Spec ->
decision_record; Plan -> mission_plan convention; Tasks -> handoff convention);
``analyze`` and ``compliance`` are checkers, NOT kinds. Zero ``.cex/kinds_meta.json``
edits; the CLI adds subcommands (no new console_script -- Article VII).

absorbs: 01_spec-kit + ADR 013
"""

from .analyze import (
    SEV_ADVISORY,
    SEV_CRITICAL,
    SEV_HIGH,
    VERDICT_CONDITIONAL,
    VERDICT_FAIL,
    VERDICT_PASS,
    AnalyzeReport,
    Finding,
    analyze_feature_dir,
    analyze_text,
)
from .cli import compliance_app, spec_kit_app
from .compliance import (
    ARTICLE_TITLES,
    ArticleResult,
    ComplianceReport,
    check_all,
    check_article,
    normalize_article,
)
from .templates import TEMPLATE_NAMES, TEMPLATES, emit

__all__ = [
    # analyze (the core value)
    "analyze_feature_dir",
    "analyze_text",
    "AnalyzeReport",
    "Finding",
    "SEV_CRITICAL",
    "SEV_HIGH",
    "SEV_ADVISORY",
    "VERDICT_PASS",
    "VERDICT_CONDITIONAL",
    "VERDICT_FAIL",
    # compliance (ADR 013 gate)
    "check_article",
    "check_all",
    "ComplianceReport",
    "ArticleResult",
    "ARTICLE_TITLES",
    "normalize_article",
    # scaffolders
    "emit",
    "TEMPLATE_NAMES",
    "TEMPLATES",
    # CLI sub-apps
    "spec_kit_app",
    "compliance_app",
]

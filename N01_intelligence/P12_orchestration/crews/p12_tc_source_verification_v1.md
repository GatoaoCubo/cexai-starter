---
id: p12_tc_source_verification_v1
kind: team_charter
pillar: P12
llm_function: COLLABORATE
charter_id: source_verification_template
crew_template_ref: p12_ct_source_verification.md
mission_statement: "Independently verify every factual claim in {{INPUT_ARTIFACT}}, corroborating each with >= 1 independent source, and produce a verification report with overall_confidence >= {{CONFIDENCE_FLOOR}}."
quality_gate: 8.5
deadline: "{{DEADLINE}}"
input_artifact: "{{INPUT_ARTIFACT}}"
deliverables:
  - "Sourced claims KC (knowledge_card P01) -- harvester output; >= 5 extracted claims with primary sources"
  - "Cross-check KC (knowledge_card P01) -- cross_checker output; corroboration matrix covering 100% of claims"
  - "Verification report -- confidence_scorer output; per-claim scores + overall_confidence + verdict"
budget:
  tokens: "{{BUDGET_TOKENS}}"
  wall_clock_seconds: "{{BUDGET_WALL_CLOCK_SECONDS}}"
  usd: "{{BUDGET_USD}}"
domain_focus: "{{INPUT_ARTIFACT}}"
stakeholders: ["n01_intelligence", "n07_orchestrator"]
escalation_protocol: "If any role crosses its token or wall-clock ceiling, or the input artifact yields zero verifiable claims, emit signal_{role}_escalate.json to .cex/runtime/signals/. N01 reads and either extends budget (with justification) or kills the crew and reports the artifact as unverifiable."
termination_criteria: "ANY of: (1) confidence_scorer emits a verdict (verified | partial | unverified) for every extracted claim; (2) token or wall-clock budget exhausted; (3) deadline passed; (4) harvester extracts zero factual claims (nothing to verify -- report immediately, do not proceed to cross_checker)."
quality: null
keywords: [knowledge_card, sourced_claims, verification_report, overall_confidence, a2a-task, token budget, wall-clock, escalation protocol, open_vars, template]
density_score: 0.90
title: "Team Charter Template -- Source Verification"
version: "1.0.0"
tags: [team_charter, source_verification, intelligence, template]
tldr: "Fill-in-the-blanks mission contract for the source_verification crew. Copy this file per instance and replace every {{open_var}} before dispatch."
domain: "source verification governance"
created: "2026-07-20"
updated: "2026-07-20"
related:
  - p12_ct_source_verification
  - p02_ra_harvester
  - p02_ra_cross_checker
  - p02_ra_confidence_scorer
---

## Mission Statement

Independently verify every factual claim in **{{INPUT_ARTIFACT}}**, corroborating
each claim with >= 1 independent source, and produce a verification report with
`overall_confidence >= {{CONFIDENCE_FLOOR}}` as scored by `confidence_scorer`.

## Open Variables (fill before dispatch)

| Variable | Type | Example | Notes |
|----------|------|---------|-------|
| `{{INPUT_ARTIFACT}}` | path or URL | "N01_intelligence/P05_output/output_swot_analysis.md" | The artifact whose claims get verified; becomes `domain_focus` |
| `{{CONFIDENCE_FLOOR}}` | float | `0.70` | Floor for `verified` verdict; below this the artifact is `partial` or `unverified` |
| `{{DEADLINE}}` | ISO-8601 datetime | `2026-08-10T18:00:00-03:00` | Hard stop; see Termination Criteria |
| `{{BUDGET_TOKENS}}` | integer | `90000` | Total across all 3 roles (recommend 30000/role ceiling) |
| `{{BUDGET_WALL_CLOCK_SECONDS}}` | integer | `1800` | 3 roles x 600s avg is a reasonable starting point |
| `{{BUDGET_USD}}` | float | `3.00` | Rough estimate at your provider's blended token pricing |

## Deliverables

1. Sourced claims KC (`knowledge_card` under P01) -- harvester output; >= 5 claims, primary source URLs required
2. Cross-check KC (`knowledge_card` under P01) -- cross_checker output; corroboration matrix, 100% claim coverage
3. Verification report -- confidence_scorer output; per-claim confidence + `overall_confidence` + `verdict`

## Success Metrics

- Every claim extracted by harvester receives a final verdict from confidence_scorer (no orphaned claims)
- `overall_confidence >= {{CONFIDENCE_FLOOR}}` required for a `verified` verdict
- Wall-clock under `{{BUDGET_WALL_CLOCK_SECONDS}}` for the full crew
- Token budget under `{{BUDGET_TOKENS}}` total
- All 3 a2a-task handoff signals present and archived

## Budget

- Tokens: `{{BUDGET_TOKENS}}` total (hard ceiling)
- Wall-clock: `{{BUDGET_WALL_CLOCK_SECONDS}}` seconds
- USD: `{{BUDGET_USD}}` (estimate at your provider's blended pricing)

## Configuration

- `input_artifact` / `{{INPUT_ARTIFACT}}`: the path or URL of the artifact to verify
- `{{CONFIDENCE_FLOOR}}`: default 0.70; raise for claims that will ship externally, lower for an internal sanity pass
- `quality_gate`: default 8.5; raise to 9.0 for a verification report that itself ships externally

## Stakeholders

- n01_intelligence (nucleus that owns the crew instance -- executes + monitors)
- n07_orchestrator (dispatches, monitors signals, consolidates on completion)
- Consumer of output: whichever nucleus requested verification of `{{INPUT_ARTIFACT}}` (N04 knowledge cards, N06 pricing data, N02 market claims, or a direct user)

## Escalation Protocol

If any role crosses its token or wall-clock ceiling, or the input artifact
yields zero verifiable claims, emit `signal_{role}_escalate.json` to
`.cex/runtime/signals/`. N01 reads and either extends budget (with
justification logged) or kills the crew and reports the artifact as
unverifiable rather than forcing a verdict.

## Termination Criteria

ANY of:
1. confidence_scorer emits a verdict for every extracted claim (normal completion)
2. Token or wall-clock budget exhausted (partial work archived)
3. `{{DEADLINE}}` passed
4. harvester extracts zero factual claims -- report immediately, do not proceed to cross_checker

## Instantiation (copy this file per run)

```bash
# 1. Copy this template and fill every {{open_var}}
cp N01_intelligence/P12_orchestration/crews/p12_tc_source_verification_v1.md \
   N01_intelligence/P12_orchestration/crews/p12_tc_source_verification_{{instance_slug}}.md

# 2. Dry run (inspect resolved plan)
python _tools/cex_crew.py show source_verification

# 3. Live run with the filled-in charter
python _tools/cex_crew.py run source_verification \
    --charter N01_intelligence/P12_orchestration/crews/p12_tc_source_verification_{{instance_slug}}.md \
    --execute
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p12_ct_source_verification]] | parent | 0.55 |
| [[p02_ra_harvester]] | related | 0.40 |
| [[p02_ra_cross_checker]] | related | 0.40 |
| [[p02_ra_confidence_scorer]] | related | 0.40 |

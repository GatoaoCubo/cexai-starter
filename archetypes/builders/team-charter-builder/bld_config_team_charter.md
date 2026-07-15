---
kind: config
id: bld_config_team_charter
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for team_charter production
quality: null
title: "Config Team Charter"
version: "1.0.0"
author: n06_wave8
tags: [team_charter, builder, config, governance]
tldr: "Naming, paths, limits for team_charter production"
domain: "team_charter construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for team_charter production, team_charter construction, config team charter, team_charter, builder, config, governance, "p12_tc_{{mission_slug}}_v{{n}}.md", p12_tc_brand_launch_v1.md, p12_tc_rag_pipeline_v2.md]
density_score: 0.85
related:
  - bld_config_agent_profile
  - bld_config_vc_credential
  - bld_config_code_of_conduct
  - bld_config_agents_md
  - bld_config_ab_test_config
---
## Naming Convention
Pattern: `p12_tc_`{{mission_slug}}`_v`{{n}}`.md`
Examples: `p12_tc_brand_launch_v1.md`, `p12_tc_rag_pipeline_v2.md`, `p12_tc_overnight_evolve_v1.md`

## Paths
Artifacts stored in: `P12_orchestration/charters/`{{mission_slug}}`/`
Archive path: `.cex/runtime/decisions/archive/tc_`{{charter_id}}`_`{{date}}`.md`

## Limits
max_bytes: 4096
max_turns: 3
effort_level: 2

## Hooks
pre_build: "Read GDP decision manifest (.cex/runtime/decisions/decision_manifest.yaml)"
post_build: "python _tools/cex_compile.py {path}"
on_error: "Write partial draft, flag missing fields, escalate to N07"
on_quality_fail: "Retry F6 once; if still < 8.0, output partial with TODO markers"

## Version Policy
- v1: initial charter (first GDP session)
- v2+: charter amended after mid-mission scope change (requires user approval)
- Amendments MUST preserve original budget ceiling and deadline UNLESS user explicitly overrides.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_agent_profile]] | sibling | 0.25 |
| bld_config_vc_credential | sibling | 0.25 |
| bld_config_code_of_conduct | sibling | 0.25 |
| bld_config_agents_md | sibling | 0.24 |
| bld_config_ab_test_config | sibling | 0.24 |

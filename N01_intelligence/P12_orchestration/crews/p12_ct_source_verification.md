---
id: p12_ct_source_verification
kind: crew_template
pillar: P12
llm_function: CALL
crew_name: source_verification
purpose: "3-role sequential crew that validates external source claims -- harvest sources, cross-check assertions, score confidence per claim"
process: sequential
crewai_equivalent: "Process.sequential"
autogen_equivalent: "GroupChat.round_robin"
swarm_equivalent: "harvester -> cross_checker -> confidence_scorer"
handoff_protocol_id: a2a-task-sequential
quality: null
keywords: [sourced_claims, corroborating source, source authority, regression_check, artifact_path, quality_score, claim_count, overall_confidence, verdict]
density_score: 0.90
title: "Source Verification Crew Template"
version: "1.0.0"
author: n01_intelligence
tags: [crew_template, source_verification, intelligence, composable, sequential, validation]
tldr: "3-role sequential crew: source harvesting -> cross-referencing -> confidence scoring"
domain: "source verification orchestration"
created: "2026-07-20"
updated: "2026-07-20"
related:
  - p02_ra_harvester
  - p02_ra_cross_checker
  - p02_ra_confidence_scorer
  - p12_tc_source_verification_v1
  - p12_ct_deep_research
---

## Overview

Instantiate when a set of claims or an existing artifact needs independent source
verification before publication or downstream consumption. Producer: N01. Consumers:
any nucleus that needs verified inputs (N04 knowledge cards, N06 pricing data, N02
market claims). This crew is a reusable quality layer -- it can verify output from
other crews (e.g., run source_verification on a deep_research brief).

Distinct from the `fact_checker` role embedded in `deep_research`: this crew operates
standalone on any input artifact, making it composable across the entire system --
you point it at a document and it tells you what to trust.

## Roles

| Role | Role Assignment ID | Reason |
|------|---------------------|--------|
| harvester | p02_ra_harvester.md | Extract all factual claims from input artifact, locate primary sources for each, produce sourced_claims KC |
| cross_checker | p02_ra_cross_checker.md | For each claim-source pair, find >= 1 independent corroborating source; flag contradictions and single-source claims |
| confidence_scorer | p02_ra_confidence_scorer.md | Score each claim 0.0-1.0 based on corroboration depth, source authority, and recency; produce final verification report |

## Process

Topology: `sequential`. Rationale: cross_checker needs the claim-source pairs from
harvester; confidence_scorer needs the corroboration evidence from cross_checker.

## Memory Scope

| Role | Scope | Retention |
|------|-------|-----------|
| harvester | shared | per-crew-instance (claim extraction is input-specific) |
| cross_checker | shared | per-crew-instance + source cache for reuse |
| confidence_scorer | shared | per-crew-instance + regression_check archive |

## Handoff Protocol

`a2a-task-sequential` -- each role emits `artifact_path` + `quality_score` +
`claim_count`. Confidence_scorer final signal adds `overall_confidence` (0.0-1.0) +
`verdict: verified | partial | unverified` + `low_confidence_claims` list.

## Success Criteria

- [ ] All 3 role deliverables exist under `.cex/runtime/crews/{instance_id}/`
- [ ] harvester extracts all factual claims from input artifact (>= 5 claims)
- [ ] cross_checker finds >= 1 corroborating source per claim (or flags explicitly)
- [ ] confidence_scorer overall confidence >= 0.70 for `verified` verdict
- [ ] Each claim has a numeric confidence score (not qualitative)
- [ ] Handoff protocol signals present for 3/3 roles

## Instantiation

```bash
# Dry run (inspect resolved plan)
python _tools/cex_crew.py show source_verification

# Fill every {{open_var}} in a copy of the charter, then run live
cp N01_intelligence/P12_orchestration/crews/p12_tc_source_verification_v1.md \
   N01_intelligence/P12_orchestration/crews/p12_tc_source_verification_{{instance_slug}}.md

python _tools/cex_crew.py run source_verification \
    --charter N01_intelligence/P12_orchestration/crews/p12_tc_source_verification_{{instance_slug}}.md \
    --execute
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p02_ra_harvester]] | child | 0.50 |
| [[p02_ra_cross_checker]] | child | 0.48 |
| [[p02_ra_confidence_scorer]] | child | 0.46 |
| [[p12_tc_source_verification_v1]] | related | 0.40 |
| [[p12_ct_deep_research]] | sibling | 0.35 |

---
id: p12_ct_deep_research
kind: crew_template
pillar: P12
llm_function: CALL
crew_name: deep_research
purpose: "4-role sequential crew: scan sources -> synthesize -> fact-validate -> produce research brief"
process: sequential
crewai_equivalent: "Process.sequential"
autogen_equivalent: "GroupChat.round_robin"
swarm_equivalent: "scout -> analyst -> fact_checker -> writer"
handoff_protocol_id: a2a-task-sequential
quality: null
keywords: [research report, fact-checking, confidence-scored, structured analysis, regression_check, artifact_path, quality_score, verdict: pass | block]
density_score: 0.93
title: "Deep Research Crew Template"
version: "1.0.0"
author: n01_intelligence
tags: [crew_template, deep_research, intelligence, composable, sequential]
tldr: "4-role sequential crew: source scan -> synthesis -> fact validation -> research brief"
domain: "deep research orchestration"
created: "2026-07-20"
updated: "2026-07-20"
related:
  - p02_ra_scout
  - p02_ra_deep_analyst
  - p02_ra_fact_checker
  - p02_ra_research_writer
  - p12_tc_deep_research_v1
---

## Overview

Instantiate when a topic requires a comprehensive, fact-validated research report --
not just a market scan, but any research domain with an added confidence-scored
fact-checking gate before the final brief. Producer: N01. Consumers: N07 (mission
planning), N06 (strategy), N02 (positioning).

This is the deeper sibling of `research_sprint` (3-role: scout -> analyst ->
synthesizer): same source-gathering discipline, plus a dedicated `fact_checker`
role that blocks the pipeline on low-confidence claims before the writer ever
sees them. Reuses the same `scout` role_assignment as `research_sprint` -- the
role is already generic enough to serve both crews without change.

## Roles

| Role | Role Assignment ID | Reason |
|------|---------------------|--------|
| scout | p02_ra_scout.md | Scan sources, find papers/data, produce raw findings KC with >= 5 citations |
| analyst | p02_ra_deep_analyst.md | Synthesize findings into structured analysis KC with patterns and gap identification |
| fact_checker | p02_ra_fact_checker.md | Validate all claims, score per-claim confidence, block passage if overall < 0.65 |
| writer | p02_ra_research_writer.md | Produce final research brief (executive summary + findings + recommendations) |

## Process

Topology: `sequential`. Rationale: each role strictly depends on the prior artifact;
parallelism breaks the confidence-scoring chain and produces ungrounded output.

## Memory Scope

| Role | Scope | Retention |
|------|-------|-----------|
| scout | shared | persistent (raw findings KC saved to P01) |
| analyst | shared | per-crew-instance |
| fact_checker | shared | per-crew-instance + regression_check archive |
| writer | shared | per-crew-instance |

## Handoff Protocol

`a2a-task-sequential` -- each role emits `artifact_path` + `quality_score`.
Fact_checker adds `confidence_score` + `verdict: pass | block` + `low_confidence_claims`.
On `block`, analyst revises before writer proceeds.

## Success Criteria

- [ ] All 4 role deliverables exist under `.cex/runtime/crews/{instance_id}/`
- [ ] scout raw findings KC cites >= 5 sources with URLs and access dates
- [ ] analyst KC quality >= 8.5 (pre-validation floor)
- [ ] fact_checker overall confidence score >= 0.65 (gate p11_qg_research_n01)
- [ ] writer brief quality >= 9.0 (final output gate)
- [ ] Handoff protocol signals present for 4/4 roles
- [ ] No role produced an artifact without reading upstream output

## Instantiation

```bash
# Dry run (inspect resolved plan)
python _tools/cex_crew.py show deep_research

# Fill every {{open_var}} in a copy of the charter, then run live
cp N01_intelligence/P12_orchestration/crews/p12_tc_deep_research_v1.md \
   N01_intelligence/P12_orchestration/crews/p12_tc_deep_research_{{instance_slug}}.md

python _tools/cex_crew.py run deep_research \
    --charter N01_intelligence/P12_orchestration/crews/p12_tc_deep_research_{{instance_slug}}.md \
    --execute
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p02_ra_scout]] | child | 0.55 |
| [[p02_ra_deep_analyst]] | child | 0.52 |
| [[p02_ra_fact_checker]] | child | 0.50 |
| [[p02_ra_research_writer]] | child | 0.48 |
| [[p12_tc_deep_research_v1]] | related | 0.40 |

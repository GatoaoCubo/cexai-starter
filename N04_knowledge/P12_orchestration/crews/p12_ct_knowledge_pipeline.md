---
id: p12_ct_knowledge_pipeline.md
kind: crew_template
8f: F2_become
pillar: P12
llm_function: CALL
crew_name: knowledge_pipeline
purpose: Coordinate a 3-role sequential crew that turns raw source material into curated, indexed knowledge -- ingestion through curation to retrieval indexing
process: sequential
crewai_equivalent: "Process.sequential"
autogen_equivalent: "GroupChat.round_robin"
swarm_equivalent: "ingester -> curator -> indexer"
handoff_protocol_id: a2a-task-sequential
quality: null
keywords: [a2a task, artifact, quality score, handoff protocol, sequential process, instance id, versioning, curator, ingester, indexer, knowledge_pipeline]
density_score: null
title: "Knowledge Pipeline Crew Template"
version: "1.0.0"
author: n04_knowledge
tags: [crew_template, knowledge_pipeline, knowledge, composable, P12]
tldr: "3-role sequential crew: raw source ingestion -> curated knowledge_cards -> retrieval index"
domain: "knowledge pipeline orchestration"
created: "2026-07-20"
updated: "2026-07-20"
related:
  - p02_ra_ingester.md
  - p02_ra_curator.md
  - p02_ra_indexer.md
  - team_charter_knowledge_pipeline_template.md
  - p12_wf_rag_ingestion_n04
---

## Overview
Instantiate when standing up a knowledge base for a new domain, absorbing a
batch of external sources into the corpus, or refreshing an existing library
against updated source material. Producer is N04 (knowledge); consumers are
every nucleus that queries the retrieval layer downstream. Three roles run in
strict sequence; each emits a typed artifact the next role grounds on.

## Roles
| Role | Role Assignment ID | Reason |
|------|---------------------|--------|
| ingester | p02_ra_ingester.md | Discover and load raw sources, normalize formats, emit a raw_source_log |
| curator | p02_ra_curator.md | Turn the raw_source_log into structured, deduplicated knowledge_cards -- never overwrites an existing memory fact without versioning it first |
| indexer | p02_ra_indexer.md | Build/update the retrieval index over curator output, emit a coverage_report |

## Process
Topology: `sequential`. Rationale: each role strictly depends on the previous
artifact -- curator cannot structure knowledge it has not received from
ingester, and indexer cannot index knowledge_cards that do not exist yet.
Parallelism would break the source-to-index provenance chain.

## Memory Scope
| Role | Scope | Retention |
|------|-------|-----------|
| ingester | shared | per-crew-instance (raw_source_log) |
| curator | shared | persistent (knowledge_cards committed to P01, versioned on overwrite) |
| indexer | shared | persistent (knowledge_index committed to P10) |

## Handoff Protocol
`a2a-task-sequential` -- each role writes a completion signal with
`artifact_path` + `quality_score`. Next role reads the prior artifact before
starting its own F1 CONSTRAIN.

## Governance Note
The curator role is the sole writer of persistent knowledge_cards in this
crew. It MUST NEVER overwrite an existing memory fact in place -- any change
to a previously-curated fact goes through consolidation-policy-style
versioning (supersede + link, not silent overwrite). This is enforced in
`p02_ra_curator.md`'s own responsibilities, not left to convention.

## Success Criteria
- [ ] All 3 role deliverables exist under `.cex/runtime/crews/{instance_id}/`
- [ ] ingester produced a raw_source_log with >= 3 sources (type + trust_level set)
- [ ] curator produced >= 3 knowledge_cards, quality >= 9.0, zero duplicate entries
- [ ] indexer produced a coverage_report with gap_resolution_rate >= 0.90
- [ ] No role produced an artifact without reading upstream output
- [ ] No memory fact was overwritten without a versioning trail

## Instantiation
```bash
python _tools/cex_crew.py run knowledge_pipeline \
    --charter N04_knowledge/P12_orchestration/team_charter_knowledge_pipeline_template.md
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p02_ra_ingester.md]] | upstream | 0.40 |
| [[p02_ra_curator.md]] | upstream | 0.38 |
| [[p02_ra_indexer.md]] | upstream | 0.36 |
| [[p12_wf_rag_ingestion_n04]] | sibling | 0.30 |

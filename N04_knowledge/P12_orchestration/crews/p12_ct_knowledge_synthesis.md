---
id: p12_ct_knowledge_synthesis.md
kind: crew_template
8f: F2_become
pillar: P12
llm_function: CALL
crew_name: knowledge_synthesis
purpose: Coordinate a 3-role sequential crew that converts raw sources into indexed, peer-validated knowledge cards
process: sequential
crewai_equivalent: "Process.sequential"
autogen_equivalent: "GroupChat.round_robin"
swarm_equivalent: "researcher -> curator -> indexer"
handoff_protocol_id: a2a-task-sequential
quality: null
keywords: [coordinate a, peer-validated knowledge cards, knowledge synthesis orchestration, knowledge synthesis crew template, role sequential crew, source scan, kc curation, retrieval indexing, crew_template, knowledge_synthesis]
density_score: null
title: "Knowledge Synthesis Crew Template"
version: "1.0.0"
author: n04_knowledge
tags: [crew_template, knowledge_synthesis, knowledge, composable, crewai, n04]
tldr: "3-role sequential crew: source scan -> KC curation -> retrieval indexing"
domain: "knowledge synthesis orchestration"
created: "2026-07-20"
updated: "2026-07-20"
related:
  - p02_ra_researcher.md
  - p02_ra_curator.md
  - p02_ra_indexer.md
  - p12_ct_taxonomy_audit.md
  - p12_ct_product_launch.md
---

## Overview
Instantiate for systematic knowledge capture: bulk source ingestion, gap
analysis, or library enrichment. Producer is N04; consumers are any nucleus
querying the P01 library. Three roles run in strict sequence; each emits a
typed artifact that the next role grounds on.

This crew shares 2 of its 3 roles (`curator`, `indexer`) with the sibling
`knowledge_pipeline` crew (see `p12_ct_knowledge_pipeline.md`) -- a role
assignment is reusable across multiple crew_templates as long as its goal
and inputs still fit the new pipeline's shape. `knowledge_synthesis` swaps
`knowledge_pipeline`'s `ingester` (loads raw sources) for `researcher`
(scans sources AND maps knowledge gaps against the existing library).

## Roles
| Role | Role Assignment ID | Reason |
|------|---------------------|--------|
| researcher | p02_ra_researcher.md | Scan sources, collect raw material, map knowledge gaps |
| curator | p02_ra_curator.md | Organize into structured KCs, apply vocabulary, deduplicate |
| indexer | p02_ra_indexer.md | Build retrieval index, cross-reference library, validate coverage |

## Process
Topology: `sequential`. Rationale: strict data dependency -- curator cannot
organize what researcher has not yet collected; indexer cannot reference KCs
that curator has not yet produced. Parallelism would break provenance chains
and introduce index-before-artifact race conditions.

## Memory Scope
| Role | Scope | Retention |
|------|-------|-----------|
| researcher | shared | persistent (raw_source_log saved to P01) |
| curator | shared | per-crew-instance (KC drafts promoted to P01 on success) |
| indexer | shared | persistent (index entries committed to P10) |

## Handoff Protocol
`a2a-task-sequential` -- each role writes a completion signal under
`.cex/runtime/signals/` with fields `artifact_path`, `quality_score`,
`gap_count`. Next role reads that signal before starting F1 CONSTRAIN.

## Success Criteria
- [ ] All 3 role deliverables exist under `.cex/runtime/crews/{instance_id}/`
- [ ] Every KC produced by curator has quality >= 9.0
- [ ] Indexer coverage report shows >= 90% of researcher-identified gaps addressed
- [ ] Handoff signals present for 3/3 roles with no quality_score below 8.0
- [ ] No artifact produced without reading upstream output (provenance enforced)

## Instantiation
```bash
python _tools/cex_crew.py show knowledge_synthesis

python _tools/cex_crew.py run knowledge_synthesis \
    --charter N04_knowledge/P12_orchestration/crews/team_charter_synthesis_template.md \
    --execute
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p02_ra_researcher.md]] | upstream | 0.42 |
| [[p02_ra_curator.md]] | upstream | 0.38 |
| [[p02_ra_indexer.md]] | upstream | 0.36 |
| [[p12_ct_taxonomy_audit.md]] | sibling | 0.37 |
| [[p12_ct_product_launch.md]] | sibling | 0.35 |

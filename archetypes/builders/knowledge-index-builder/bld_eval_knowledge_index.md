---
kind: quality_gate
id: p11_qg_knowledge_index
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of knowledge_index artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: knowledge_index"
version: "1.0.0"
author: "builder_agent"
tags:
  - "quality-gate"
  - "knowledge-index"
  - "P11"
  - "P10"
  - "governance"
  - "search"
  - "retrieval"
  - "hybrid-search"
tldr: "Gates for knowledge_index artifacts — search index configs combining BM25, FAISS, or hybrid retrieval."
domain: knowledge_index
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
keywords:
  - "gates for knowledge_index artifacts"
  - "or hybrid retrieval"
  - "quality-gate"
  - "knowledge-index"
  - "governance"
  - "search"
  - "retrieval"
density_score: 0.87
related:
  - p11_qg_agent
  - bld_instruction_knowledge_index
  - knowledge-index-builder
  - p11_qg_quality_gate
  - p11_qg_optimizer
---
## Quality Gate

# Gate: knowledge_index
## Definition
| Field     | Value                                                  |
|-----------|--------------------------------------------------------|
| metric    | algorithm completeness + freshness policy coverage     |
| threshold | 8.0                                                    |
| operator  | >=                                                     |
| scope     | all knowledge_index artifacts (P10)                        |
## HARD Gates
All must pass. Failure on any = final score 0.
| Gate | Check | Why |
|------|-------|-----|
| H01 | YAML frontmatter parses valid YAML | Broken YAML = index unreachable at query time |
| H02 | id matches `^p10_bi_[a-z][a-z0-9_]+$` | Namespace compliance |
| H03 | id == filename stem | Brain search relies on this |
| H04 | kind == "knowledge_index" | Type integrity |
| H05 | quality == null | Never self-score |
| H06 | All required fields present: id, kind, pillar, version, created, updated, author, algorithm, scope, corpus_type, rebuild_schedule, freshness_max_days, quality, tags, tldr | Completeness |
## SOFT Scoring
| Gate | Check | Weight |
|------|-------|--------|
| S01 | tldr <= 160 chars, non-empty | 1.0 |
| S02 | tags is list, len >= 3, includes "knowledge-index" | 0.5 |
| S03 | Algorithm Config section has parameters specific to chosen algorithm | 1.0 |
| S04 | Filters section has >= 2 entries with type and condition | 1.0 |
| S05 | Ranking section has >= 2 factors with explicit weights | 1.0 |
| S06 | Rebuild section specifies both schedule and trigger event | 1.0 |
Weights sum: 9.0. Normalize: divide each by 9.0 before scoring.
## Actions
| Score | Action |
|-------|--------|
| >= 9.5 | GOLDEN — pool as reference search index configuration |
| >= 8.0 | PUBLISH — active retrieval index |
| >= 7.0 | REVIEW — complete ranking weights or monitoring thresholds |
| < 7.0  | REJECT — algorithm config missing or scope undefined |
## Bypass
| Field | Value |
|-------|-------|
| conditions | Critical search gap requiring temporary index before full spec |
| approver | p10-chief |
| audit_trail | Log in records/audits/ with retrieval gap description and timestamp |
| expiry | 72h — full algorithm config required before expiry |
| never_bypass | H01 (YAML), H05 (quality null) |

## Examples

# Examples: knowledge-index-builder
## Golden Example
INPUT: "Create knowledge_index para search hibrida no pool de knowledge cards do CEX"
OUTPUT:
```yaml
id: p10_bi_knowledge_pool
kind: knowledge_index
pillar: P10
title: "Brain Index: Knowledge Pool"
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder_agent"
```
WHY THIS IS GOLDEN:
- quality: null (H06 pass)
- id matches p10_bi_ pattern (H02 pass)
- kind: knowledge_index (H04 pass)
- 19 frontmatter fields present (H08 pass)
## Anti-Example
INPUT: "Set up search"
BAD OUTPUT:
```yaml
id: search_index
kind: knowledge_index
title: "Search"
quality: 9.0
algorithm: elasticsearch

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)

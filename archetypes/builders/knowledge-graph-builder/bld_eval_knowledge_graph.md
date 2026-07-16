---
kind: quality_gate
id: p11_qg_knowledge_graph
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of knowledge_graph artifacts
pattern: few-shot learning -- LLM reads these before producing
quality: null
title: "Gate: knowledge_graph"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, knowledge-graph, GraphRAG, entities, relations, P11]
tldr: "Gates for knowledge_graph artifacts: validates entity/relation lists, relation source/target consistency, storage and traversal enums, extraction c..."
domain: "knowledge_graph -- graph-based knowledge schemas with entity types, relation types, extraction logic, storage backend, and traversal strategies"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F7_govern"
keywords: [relation types, extraction logic, storage backend, and traversal strategies, gates for knowledge_graph artifacts, validates entity, relation lists]
density_score: 0.92
related:
  - bld_config_knowledge_graph
  - knowledge-graph-builder
  - bld_schema_knowledge_graph
---
## Quality Gate
# Gate: knowledge_graph
## Definition
| Field | Value |
|-------|-------|
| metric | Composite score from SOFT dimensions + all HARD gates pass |
| threshold | >= 7.0 to publish; >= 9.5 golden |
| operator | AND (all HARD) + weighted_sum (SOFT) |
| scope | All artifacts where `kind: knowledge_graph` |
## HARD Gates
All must pass. Any single failure = REJECT regardless of SOFT score.
| ID | Check | Failure message |
|----|-------|----------------|
| H01 | Frontmatter parses as valid YAML | "Frontmatter YAML syntax error" |
| H02 | `id` matches `^p01_kg_[a-z][a-z0-9_]+$` | "ID fails knowledge_graph namespace regex" |
| H03 | `id` value equals filename stem | "ID does not match filename" |
| H04 | `kind` equals literal `"knowledge_graph"` | "Kind is not 'knowledge_graph'" |
| H05 | `quality` field is `null` | "Quality must be null at authoring time" |
| H06 | All required fields present: id, kind, pillar, domain, entity_types, relation_types, storage_backend, traversal_strategy, version, created, author, tags, tldr | "Missing required field(s)" |
## SOFT Scoring
Dimensions sum to 100%. Score each 0.0-10.0; multiply by weight.
| Dimension | Weight | What to assess |
|-----------|--------|----------------|
| Entity type specificity | 1.0 | Extraction hints and example instances provided per entity type |
| Relation type completeness | 1.0 | Source type, target type, directionality documented per relation |
| Extraction config quality | 1.5 | Extraction prompt template included; LLM and output format specified |
| Storage backend rationale | 0.5 | Storage choice justified against scale and query pattern requirements |
| Traversal strategy rationale | 0.5 | Strategy (local/global/hybrid) justified against use-case query types |
| Deduplication specification | 1.0 | Dedup strategy and threshold defined; entity resolution approach clear |
Weight sum: 1.0+1.0+1.5+0.5+0.5+1.0+1.0+0.5+1.0+1.0+1.0+0.5 = 10.0 (100%)
## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | GOLDEN | Publish to pool as golden exemplar |
| >= 8.0 | PUBLISH | Publish to pool |
| >= 7.0 | REVIEW | Flag for human review before publish |
| < 7.0 | REJECT | Return to author with failure report |
## Bypass
| Field | Value |
|-------|-------|
| conditions | Early-stage domain exploration where entity types are not yet finalized |
| approver | Domain expert or N03 builder approval required (written); H07/H08 (empty lists) never bypassed |
## Examples
# Examples: knowledge-graph-builder
## Golden Example
INPUT: "Create a knowledge graph schema for competitive intelligence -- companies, products, and market relationships"
OUTPUT:
```yaml
id: p01_kg_competitive_intel
kind: knowledge_graph
pillar: P01
version: "1.0.0"
created: "2026-04-13"
updated: "2026-04-13"
author: "builder_agent"
domain: "competitive intelligence"
```
## Overview
Covers competitive intelligence for technology markets -- organizations, their products,
the technologies they use, and the markets they compete in.
Graph enables multi-hop queries like "which companies use technology X and compete in market Y?"
Answers: competitor mapping, technology adoption patterns, M&A activity tracking.
## Entity Types
| Name | Description | Extraction Hint | Examples |
|------|-------------|----------------|----------|
| Organization | Company, startup, or institution | "Inc.", "Corp.", "Ltd.", capital name | OpenAI, Google, Anthropic |
| Product | Named product or service offering | product name, "platform", "API", "model" | GPT-4, Gemini, Claude |
| Technology | Technical capability or framework | tech noun, "framework", "model type" | Transformer, RLHF, RAG |
| Market | Industry vertical or use-case segment | "market", "sector", "vertical", "space" | Enterprise AI, EdTech, FinTech |
| Person | Named individual, founder, executive | person name + title context | Sam Altman, Demis Hassabis |
## Relation Types
| Name | Source Type | Target Type | Description | Directionality |
|------|-------------|-------------|-------------|----------------|
| acquired | Organization | Organization | Acquisition or merger event | directed |
| competes_with | Organization | Organization | Direct market competition | undirected |
| developed_by | Product | Organization | Who built the product | directed |
| operates_in | Organization | Market | Which market a company serves | directed |
| employs | Organization | Person | Employment relationship | directed |
| uses_technology | Product | Technology | Technical capability in a product | directed |

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)

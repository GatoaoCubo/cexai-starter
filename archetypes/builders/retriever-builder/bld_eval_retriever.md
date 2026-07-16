---
kind: quality_gate
id: p11_qg_retriever
pillar: P11
llm_function: GOVERN
version: 1.0.0
created: 2026-03-28
updated: 2026-03-28
author: builder_agent
quality: null
tags:
  - "quality_gate"
  - "retriever"
  - "P11"
  - "validation"
  - "RAG"
  - "vector-search"
8f: "F7_govern"
keywords:
  - "examples artifact construction"
  - "hard gates block delivery"
  - "soft dimensions score"
  - "quality_gate"
  - "retriever"
  - "validation"
  - "vector-search"
density_score: 1.0
domain: "examples artifact construction"
title: Quality Gate ISO - retriever
tldr: "10 HARD gates block delivery. 12 SOFT dimensions score 0-10. Threshold 7.0."
related:
  - retriever-builder
  - bld_tools_retriever
---
## Quality Gate
# Gate: retriever
## Definition
- Metric: composite score 0-10
- Threshold: >= 7.0 to deliver
- HARD gates: block delivery regardless of score
- SOFT gates: contribute to composite score
## HARD Gates (all must pass — any failure blocks delivery)
| ID | Check | Fail Action |
|----|-------|-------------|
| H01 | YAML frontmatter parses without errors | Fix syntax |
| H02 | id matches `^p04_retr_[a-z][a-z0-9_]+$` AND equals filename stem | Fix id or rename file |
| H03 | kind == "retriever" (exact string) | Fix kind field |
| H04 | quality == null (not a number, not absent) | Remove numeric score |
| H05 | All required fields present: id, name, store_type, embedding_model, similarity_metric, top_k | Add missing fields |
| H06 | store_type is valid enum: chroma, pinecone, faiss, qdrant, weaviate, milvus, elasticsearch, costm | Fix to valid value |
## SOFT Scoring (12 dimensions, each 0-1, sum * 10/12)
| ID | Dimension | Weight | Criteria |
|----|-----------|--------|----------|
| S01 | store_coverage | 1.0 | store_type matches real backend; version/tier noted if relevant |
| S02 | embedding_model_docs | 1.0 | model name, provider, dimension size documented |
| S03 | similarity_justification | 1.0 | metric choice explained relative to embedding model |
| S04 | hybrid_strategy | 0.8 | if hybrid: fusion method (RRF/weighted) and alpha specified |
| S05 | reranking_config | 0.8 | reranker null OR model named with trigger condition |
| S06 | metadata_filter_docs | 0.8 | filters listed with field names and types |
## Scoring Tiers
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | Golden | Pool as golden artifact |
| >= 8.0 | Skilled | Pool + remember pattern |
| >= 7.0 | Learning | Deliver with notes |
| < 7.0 | Rejected | Revise before delivery |
## Bypass
No bypass for HARD gates. SOFT gate threshold may be reduced to 6.0 only when:
- Prototype/draft explicitly requested by user
- store_type is "costm" with acknowledged unknowns
Document bypass reason in artifact description field.
## Examples
# Examples: retriever-builder
## Golden Example
**INPUT**: "Create a hybrid retriever for a Qdrant store using Cohere embed-v3 embeddings
with reranking for a technical documentation RAG system."
**OUTPUT**:
```markdown
---
id: p04_retr_qdrant_hybrid_docs
kind: retriever
pillar: P04
version: 1.0.0
created: 2026-03-28
updated: 2026-03-28
author: retriever-builder
```
**WHY GOLDEN**: H01-H10 all pass. S01-S12 average ~9.4 — qdrant+Cohere+RRF+reranker+metadata+SDK all documented.
---
## Anti-Example
**INPUT**: "Create retriever"
**BAD OUTPUT**:
```markdown
---
id: retriever_1
kind: retriever
store_type: vector
embedding_model: embeddings
top_k: 100
quality: 8.5
tags: [search]
---
Searches documents using vectors.
```
**FAILURES**:
- H01: parses but H02 fails — id "retriever_1" does not match `^p04_retr_[a-z][a-z0-9_]+$`
- H03: kind == "retriever" passes but H04 fails — quality: 8.5 (must be null)
- H05: missing name, similarity_metric; pillar, version, created, updated, author, tldr all absent
- H06: store_type "vector" is not a valid enum value
## Cross-References
- **Pillar**: P07 (Evals)
- **Kind**: `examples`
- **Artifact ID**: `bld_examples_retriever`
- **Tags**: [examples, retriever, P07, RAG, vector-search, hybrid-search]

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)

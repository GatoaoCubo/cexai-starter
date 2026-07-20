---
id: p04_cli_research_pipeline_n01
kind: cli_tool
pillar: P04
nucleus: n01
title: "Research Pipeline -- N01 Intelligence Tool"
version: 1.0.0
created: 2026-03-31
updated: 2026-03-31
author: research-pipeline-builder
domain: research_pipeline
quality: null
tags: [cli_tool, research_pipeline, n01, intelligence, multi_stage]
tldr: "Market intelligence pipeline for N01. 7-stage pipeline with 30+ sources, multi-model routing, budget-aware."
keywords: [intent classification, query planning, retrieval, entity dedup, scoring, synthesis, verification]
density_score: 0.90
related:
  - research-pipeline-builder
  - p03_ch_research_pipeline_n01
  - p05_parser_data_extractor_n01
  - p12_wf_intelligence
  - kc_research_methods
---

# Research Pipeline -- Intelligence Tool

## Purpose
Automated market intelligence for any business served by N01 Intelligence. Reads a research-scope config and executes a 7-stage research pipeline: classify intent, plan multi-perspective queries, retrieve from many sources in parallel with quality gates, deduplicate entities, score on multiple dimensions, synthesize with domain-aware prompting, and verify with a critique pass.

## Pipeline
```
QUERY -> S1 INTENT (classify domain, route)
           |
           v
         S2 PLAN (5 perspectives x 5-7 sub-questions)
           |
           v
         S3 RETRIEVE (parallel, quality score >= 0.7)
           |
           v
         S4 RESOLVE (entity dedup cross-source)
           |
           v
         S5 SCORE (multi-dimension quality)
           |
           v
         S6 SYNTHESIZE (domain-aware prompting)
           |
           v
         S7 VERIFY (critique pass, max 3 iter)
           |
     +-----+-----+
     v     v     v
   HTML  PPTX  JSON
```

## Usage
```bash
# Full research from config
python research_pipeline.py --config config.yaml --query "market for enterprise API documentation tools"

# Specific stages only
python research_pipeline.py --config config.yaml --query "..." --stages 1-3

# Dry run (plan only, no retrieval)
python research_pipeline.py --config config.yaml --query "..." --dry-run
```

## Source Categories
| Category | Purpose | Examples |
|----------|---------|---------|
| Inbound | Product/marketplace data | marketplaces, review sites |
| Outbound | Social intelligence | forums, video platforms, social listening |
| Search | Web search engines | general-purpose + AI-native search APIs |
| Trends | Price/trend tracking | trend indices, price history tools |
| RAG | Internal knowledge | company docs, embeddings |

## Config Reference
Pipeline config: `N01_intelligence/P09_config/research_pipeline_config.yaml`

## Quality Gates
- 7 stages complete
- Retrieval quality score >= 0.7 per result
- Verification pass max 3 iterations
- Budget caps enforced
- Zero plaintext secrets

## Nucleus Integration
| Direction | Target | Data |
|-----------|--------|------|
| N01 -> N02 | Marketing | Research insights for content strategy |
| N01 -> N06 | Commercial | Pricing intelligence, competitor data |
| N01 -> N03 | Engineering | Technical research for implementation |
| N01 -> N07 | Orchestrator | Research reports for decision-making |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[research-pipeline-builder]] | related | 0.45 |
| [[p03_ch_research_pipeline_n01]] | related | 0.40 |
| [[p05_parser_data_extractor_n01]] | downstream | 0.36 |
| [[p12_wf_intelligence]] | related | 0.34 |
| [[kc_research_methods]] | upstream | 0.28 |

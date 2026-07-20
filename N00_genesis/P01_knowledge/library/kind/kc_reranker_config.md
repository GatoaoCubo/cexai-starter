---
id: kc_reranker_config
kind: knowledge_card
8f: F3_inject
title: Reranker Configuration
version: 1.0.0
quality: null
pillar: P01
tldr: "Reranking model config with strategy, score threshold, max items, and weighted ranking criteria"
when_to_use: "When adding a second-stage reranker to re-score and filter retrieval results by relevance"
keywords: [reranking, confidence, diversity, relevance, threshold, weighting, model_name, model_version]
density_score: 1.0
updated: "2026-04-15"
related:
  - p01_qg_reranker_config
  - bld_output_template_reranker_config
  - n00_reranker_config_manifest
  - bld_collaboration_model_card
  - bld_knowledge_card_model_registry
---

## Reranker Configuration Parameters

**Model Configuration**
- `model_name`: Name of the reranking model (e.g., `rerank-1.0`)
- `model_version`: Version of the model (e.g., `v2.1`)
- `model_params`: Additional parameters for model initialization

**Strategy Parameters**
- `strategy`: Reranking strategy (e.g., `confidence`, `diversity`, `relevance`)
- `threshold`: Minimum score threshold for item inclusion
- `max_items`: Maximum number of items to return
- `weighting`: Weight distribution across ranking criteria

**Example Configuration**
```yaml
model_name: rerank-1.0
model_version: v2.1
strategy: confidence
threshold: 0.75
max_items: 10
weighting:
  relevance: 0.6
  diversity: 0.3
  confidence: 0.1
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_qg_reranker_config]] | downstream | 0.26 |
| [[bld_output_template_reranker_config]] | downstream | 0.24 |
| [[bld_collaboration_model_card]] | downstream | 0.22 |
| [[bld_knowledge_card_model_registry]] | sibling | 0.21 |

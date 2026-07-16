---
kind: output_template
id: bld_output_template_graph_rag_config
pillar: P05
llm_function: PRODUCE
purpose: Template with vars for graph_rag_config production
quality: null
title: "Output Template Graph Rag Config"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [graph_rag_config, builder, output_template]
tldr: "Template with vars for graph_rag_config production"
domain: "graph_rag_config construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [graph_rag_config construction, graph_rag_config, builder, output_template, example value, related artifacts, yaml grc_, grc_ yaml, max_depth maximum, traversal depth]
density_score: 0.85
related:
  - bld_output_template_reranker_config
  - graph-rag-config-builder
  - bld_config_graph_rag_config
  - kc_graph_rag_config
  - p11_fb_graph_rag_config
---
```yaml
---
id: p01_grc_{{id}}.yaml <!-- ^p01_grc_[a-z][a-z0-9_]+.yaml$ -->
name: {{name}} <!-- Configuration name (e.g., "knowledge_graph") -->
description: {{description}} <!-- Brief purpose of this config -->
quality: {{quality}} <!-- MUST be: null -->
version: {{version}} <!-- Semantic version (e.g., "1.0.0") -->
parameters:
  max_depth: {{max_depth}} <!-- Maximum traversal depth for graph -->
  llm_model: {{llm_model}} <!-- Model ID for RAG processing -->
data_sources:
  - {{source1}} <!-- Example: "internal_db" -->
  - {{source2}} <!-- Example: "external_api" -->
model_config:
  type: {{model_type}} <!-- "graph_rag" or "hybrid" -->
  temperature: {{temperature}} <!-- Float between 0-1 -->
```

| Parameter       | Example Value   | Description                     |
|-----------------|------------------|---------------------------------|
| max_depth       | 3                | Maximum graph traversal depth   |
| llm_model       | "llama3:8b"      | Model identifier for RAG        |
| temperature     | 0.7              | Creativity control (0-1)        |

```python
# Example data source config
data_sources = [
    {
        "type": "database",
        "connection": "postgresql://user:pass@host:port/db",
        "tables": ["entities", "relationships"]
    }
]
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_output_template_reranker_config]] | sibling | 0.32 |
| [[graph-rag-config-builder]] | upstream | 0.30 |
| [[bld_config_graph_rag_config]] | downstream | 0.28 |
| [[kc_graph_rag_config]] | upstream | 0.28 |
| [[p11_fb_graph_rag_config]] | downstream | 0.25 |

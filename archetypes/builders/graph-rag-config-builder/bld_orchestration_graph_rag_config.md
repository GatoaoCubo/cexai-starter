---
kind: collaboration
id: bld_collaboration_graph_rag_config
pillar: P12
llm_function: COLLABORATE
purpose: How graph_rag_config-builder works in crews with other builders
quality: null
title: "Collaboration Graph Rag Config"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [graph_rag_config, builder, collaboration]
tldr: "How graph_rag_config-builder works in crews with other builders"
domain: "graph_rag_config construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F8_collaborate"
keywords: [graph_rag_config construction, collaboration graph rag config, graph_rag_config, builder, collaboration, crew role  
orchestrates graph, receives from, knowledge engineer, data curator, system architect]
density_score: 0.85
related:
  - graph-rag-config-builder
---
## Crew Role  
Orchestrates Graph RAG pipeline configuration by defining schema, linking knowledge graphs to retrieval systems, and specifying query routing rules.  

## Receives From  
| Builder         | What                  | Format   |  
|-----------------|-----------------------|----------|  
| Knowledge Engineer | Graph schema        | YAML     |  
| Data Curator    | Document source specs | JSON     |  
| System Architect | Pipeline requirements | TOML     |  

## Produces For  
| Builder         | What                  | Format   |  
|-----------------|-----------------------|----------|  
| RAG Engine      | Config file           | YAML     |  
| Data Curator    | Validation report     | JSON     |  
| DevOps          | Deployment spec       | TOML     |  

## Boundary  
Does NOT handle graph instance construction (knowledge_graph_builder) or document ingestion (rag_source_builder). Those are managed by specialized builders.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[graph-rag-config-builder]] | upstream | 0.40 |

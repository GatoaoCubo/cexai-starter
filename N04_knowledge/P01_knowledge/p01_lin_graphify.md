---
id: p01_lin_graphify
kind: lineage_record
pillar: P01
version: 1.0.0
target_artifact: p01_kg_cexai_sdk_structure
sources_count: 2
activities_count: 3
derivation_type: wasDerivedFrom
domain: knowledge-provenance
created: "2026-06-24"
updated: "2026-06-24"
author: lineage-record-builder
quality: null
tags: [lineage_record, knowledge-provenance, graphify, MIT, assimilation]
tldr: "Provenance for p01_kg_cexai_sdk_structure: graphify MIT structural-graph lift, 5132 nodes/9231 links, commit 96485f5"
related:
  - p01_kg_cexai_sdk_structure
  - p01_kc_gstack_attribution_ledger
  - p01_lin_open_design
---

# Lineage: p01_kg_cexai_sdk_structure

## Canonical Provenance Frontmatter Schema

Derived artifacts MUST carry this block:

```yaml
provenance:
  source: "github.com/safishamsi/graphify"
  license: "MIT"
  lineage_record: "p01_lin_graphify"
  method: "structural_graph_lift"
  derived: "2026-06-24"
```

## Entities

| ID | Type | Location | Retrieved |
|----|------|----------|-----------|
| graphify_src | prov:Entity | github.com/safishamsi/graphify v0.8.47 | 2026-06-24T00:00:00Z |
| graph_json | prov:Entity | .cex/runtime/graphify/cexai/graphify-out/graph.json | 2026-06-24T00:00:00Z |

graph.json (verified, spec 07): 5132 nodes, 9231 links, 4 hyperedges; Leiden
communities; built_at_commit 96485f5; scope: cexai/ SDK package.

## Activities

| ID | Label | Used | Generated | Agent | Timestamp |
|----|-------|------|-----------|-------|-----------|
| act_graph_run | structural_graph_lift | graphify_src, cexai_sdk | graph_json | graphify_tool | 2026-06-24T00:00:00Z |
| act_summarize | N07_summarize | graph_json | kg_draft | N07 | 2026-06-24T00:00:00Z |
| act_curate | N04_curate | kg_draft | p01_kg_cexai_sdk_structure | N04 | 2026-06-24T00:00:00Z |

Method: tree-sitter AST -> graphify run -> Leiden communities -> graph.json ->
N07 summarize -> N04 KG artifact. Structural only; $0 (no LLM enrichment).

## Agents

| ID | Type | Role |
|----|------|------|
| graphify_tool | tool | structural graph generator (MIT, v0.8.47) |
| N07 | nucleus | orchestrator + graph.json summarizer |
| N04 | nucleus | knowledge curator + KG artifact producer |

## Derivation Relations

- p01_kg_cexai_sdk_structure wasDerivedFrom graphify_src
- p01_kg_cexai_sdk_structure wasDerivedFrom graph_json
- p01_kg_cexai_sdk_structure wasGeneratedBy act_curate
- p01_kg_cexai_sdk_structure wasAttributedTo N04
- graph_json wasGeneratedBy act_graph_run
- graph_json wasAttributedTo graphify_tool

## MIT Attribution

`Structural graph derived via graphify (safishamsi/graphify, MIT, v0.8.47,
commit 96485f5) -- structural-only lift, cexai/ SDK scope.`

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kg_cexai_sdk_structure]] | downstream | 0.90 |
| [[p01_kc_gstack_attribution_ledger]] | sibling | 0.55 |
| [[p01_lin_open_design]] | sibling | 0.50 |

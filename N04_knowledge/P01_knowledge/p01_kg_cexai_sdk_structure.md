---
id: p01_kg_cexai_sdk_structure
kind: knowledge_graph
pillar: P01
nucleus: N04
version: "1.0.0"
created: "2026-06-24"
updated: "2026-06-24"
author: "knowledge-graph-builder"
domain: "cexai/ SDK Python package -- structural code graph"
entity_types:
  - CodeNode
  - RationaleNode
  - Document
  - Concept
  - Community
relation_types:
  - calls
  - contains
  - rationale_for
  - references
  - uses
  - method
  - imports_from
  - inherits
  - conceptually_related_to
  - imports
  - part_of
storage_backend: json
traversal_strategy: hybrid
quality: null
tags: [knowledge_graph, cexai-sdk, graphify, structural-graph, P01, GraphRAG]
tldr: "Structural code graph of cexai/ SDK: 5132 nodes, 9231 edges, 11 relation types, 366 Leiden communities (graphify v0.8.47, commit 96485f5)"
description: "Typed knowledge graph lifted from cexai/ SDK via graphify structural analysis. Covers code, rationale, document, and concept nodes with 11 real edge relation types."
max_depth: 4
embedding_integration: false
dedup_strategy: exact
community_detection: leiden
extraction_prompt: "graphify structural AST + tree-sitter pass (no LLM triplet extraction; relations are EXTRACTED/INFERRED/AMBIGUOUS confidence-tagged)"
node_count_estimate: 5132
edge_count_estimate: 9231
provenance:
  source: "github.com/safishamsi/graphify"
  license: "MIT"
  lineage_record: "p01_lin_graphify"
  method: "structural_graph_lift"
  derived: "2026-06-24"
related:
  - p01_lin_graphify
  - p01_kc_sdk_coverage_gap
  - p01_kg_n04
---

## Overview

Curated lift of graphify's structural analysis of the `cexai/` Python SDK
(commit `96485f5`, graphify v0.8.47 MIT). Covers **5132 nodes**, **9231 edges**,
4 node types, 11 relation types, **366 Leiden communities**. Graph is required
because SDK call/rationale/reference chains are multi-hop -- flat vector search
cannot traverse `calls -> rationale_for -> references` or surface community
structure. Answers: which symbols are load-bearing god-nodes? which tests bridge
isolated communities? what are the largest integration clusters?

## Entity Types

| Name | Description | Extraction Hint | Examples |
|------|-------------|----------------|----------|
| CodeNode | Python class, function, or method symbol derived from AST | file_type="code"; 2967 nodes (57.8% of graph) | LlmRequest, KnowledgeGraph, CexaiError, AnthropicProvider |
| RationaleNode | Rationale annotation attached to code symbols (graphify-specific) | file_type="rationale"; 1892 nodes (36.9%) | rationale_for edges target; 1894 rationale_for edges in graph |
| Document | Markdown/config file-level node (blueprint, feature spec, README) | file_type="document"; 153 nodes (3.0%) | feature_*.md blueprints in cexai/distribution/blueprints/ |
| Concept | Abstract concept node not tied to a single file symbol | file_type="concept"; 120 nodes (2.3%) | integration_contracts, module_integration hyperedge members |
| Community | Leiden community cluster (grouping, not a stored node type) | community attribute on each node; 366 communities | community 0 (size 94), community 1 (size 90), community 2 (size 77) |

Note: no single `type` field in graph.json -- entity typing is via `file_type` attribute (code/rationale/document/concept) plus symbol shape.

## Relation Types

Source: real `relation` field distribution from graph.json. Top 11 of 23 distinct relation types shown (9231 edges total: 8979 in the top 11, 228 untyped/None, 24 in 11 rarer types -- last row).

| Name | Count | Source Type | Target Type | Description | Confidence Tags |
|------|-------|-------------|-------------|-------------|-----------------|
| calls | 2586 | CodeNode | CodeNode | Direct function/method invocation | EXTRACTED / INFERRED |
| contains | 1981 | CodeNode | CodeNode | Module or class contains a member symbol | EXTRACTED |
| rationale_for | 1894 | RationaleNode | CodeNode | Rationale annotation explains a code symbol | EXTRACTED |
| references | 1158 | CodeNode | CodeNode/Concept | Symbol explicitly references another symbol | EXTRACTED / INFERRED |
| uses | 596 | CodeNode | CodeNode | Symbol depends on / uses another | EXTRACTED / INFERRED |
| method | 493 | CodeNode | CodeNode | Method membership within a class | EXTRACTED |
| imports_from | 119 | CodeNode | CodeNode | from-import of a specific symbol | EXTRACTED |
| inherits | 91 | CodeNode | CodeNode | Class inheritance (subclass -> superclass) | EXTRACTED |
| conceptually_related_to | 31 | Concept | Concept/CodeNode | Semantic relatedness without direct code link | INFERRED |
| imports | 21 | CodeNode | CodeNode | Module-level import (whole module) | EXTRACTED |
| part_of | 9 | CodeNode/Concept | Concept | Symbol is part of an integration cluster | EXTRACTED |
| (11 rarer types) | 24 | various | various | long tail: re_exports(7), provides_to(3), consumes_from(3), produces_to(2), emits(2), provides_upgrade_cta_to(2), integrates_with/provides_analytics_event_to/audit_via/cites/absorbs(1 each) | EXTRACTED |
| (untyped/None) | 228 | any | any | Edge present but relation field is null | AMBIGUOUS |

Every edge carries a `confidence` tag (EXTRACTED / INFERRED / AMBIGUOUS) and a `confidence_score` float.

## Findings

### Communities (Leiden, 366 total)

Top community sizes (node count): 94, 90, 77, 75, 74, 68, 64, 62 (top 8;
remaining 358 not individually sized in graphify output). Cohesion scores
range 0.037 (community 0) to 0.117+ (community 22) -- from `cohesion` field
in `.graphify_analysis.json`.

### God-Nodes (graphify's 10 most-connected symbols)

Source: `.graphify_analysis.json` `gods` field -- real degree values.

| Rank | Label | Degree | Location (from id) |
|------|-------|--------|--------------------|
| 1 | LlmRequest | 75 | cexai/shared/types |
| 2 | KnowledgeGraph | 58 | cexai/graph_store |
| 3 | CexaiError | 55 | cexai/shared/errors |
| 4 | Topology | 55 | cexai/shared/types |
| 5 | StatusList | 48 | cexai/rbac |
| 6 | GenericTopologyInterpreter | 44 | cexai/topology_interpreter |
| 7 | verify_knowledge_bom() | 42 | cexai/exchange/knowledge_bom |
| 8 | EpisodicMemory | 41 | cexai/episodic_store |
| 9 | GitReverseSynthesizer | 39 | cexai/reposynth |
| 10 | LlmResponse | 38 | cexai/shared/types |

LlmRequest/LlmResponse (75/38) are the universal exchange envelope. KnowledgeGraph (58) is the central persistence hub. CexaiError and Topology (both 55) are pervasive shared types.

### Surprises (graphify's 5 inferred cross-community bridges)

Source: `.graphify_analysis.json` `surprises`. All 5 are INFERRED `calls` edges.

| Test (source) | Production hub (target) |
|---------------|------------------------|
| test_runner_satisfies_content_factory_protocol() | ContentFactoryRunner |
| test_get_provider_unknown_raises_provider_config_error() | get_provider() |
| test_anthropic_missing_key_raises() | AnthropicProvider |
| test_google_missing_key_raises() | GoogleProvider |
| test_openai_missing_key_raises() | OpenAIProvider |

Pattern: all 5 are test functions bridging to production hubs across community boundaries.

### Hyperedges (4, all EXTRACTED, confidence_score 1.0)

| Name | Members | Notes |
|------|---------|-------|
| module_integration | 8 | dashboard, catalog, crm, content_library, sales, integrations, b2b_orders, users_roles -- the SDK's top-level module integration surface |
| audit_event_emission | not individually listed in graphify output | EXTRACTED hyperedge; exact members not computed in structural pass |
| message_dispatch_audit_events | not individually listed | EXTRACTED hyperedge; exact members not computed in structural pass |
| integration_contracts | from cexai/distribution/blueprints/data/company_stack/feature_*.md Documents | Blueprint feature files form a contract cluster |

## Extraction Config

| Parameter | Value |
|-----------|-------|
| Method | graphify structural AST (tree-sitter; no LLM triplet extraction; $0 LLM cost) |
| Tool | graphify v0.8.47 MIT, commit 96485f5 |
| Scope | cexai/ Python SDK |
| Output | NetworkX node-link JSON (graph.json) + .graphify_analysis.json |
| Confidence | EXTRACTED / INFERRED / AMBIGUOUS per edge |
| Tokens | input=127943, output=66040 |

## Storage and Traversal

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Storage backend | json (NetworkX node-link) | graph.json is ephemeral, gitignored at .cex/runtime/graphify/cexai/graphify-out/; queryable graph DB deferred to grounding-aid (not yet provisioned) |
| Traversal strategy | hybrid | Local: symbol-centric (god-node neighbors, community members); Global: structural summaries (cluster themes, cross-community bridges) |
| Max depth | 4 | Covers calls -> contains -> rationale_for -> references (4-hop SDK chain) |
| Query language | python (NetworkX) | Cypher not applicable until graph DB provisioned |
| Pruning rule | prefer confidence != AMBIGUOUS | EXTRACTED = ground truth; AMBIGUOUS (subset of 228 untyped edges) deprioritized |

## Integration

| Component | Value |
|-----------|-------|
| Embedding model | not integrated (structural pass only; deferred to grounding-aid) |
| Dedup strategy | exact (canonical node IDs from AST symbol paths) |
| Community detection | leiden (366 communities; ~14 nodes/community avg) |
| Downstream consumers | cex_retriever.py (when graph DB provisioned), N04 curation, N07 reasoning, grounding-aid (planned) |

## References

- Graph source: `.cex/runtime/graphify/cexai/graphify-out/graph.json` (gitignored, ephemeral)
- Analysis: `.cex/runtime/graphify/cexai/graphify-out/.graphify_analysis.json`
- Tool: github.com/safishamsi/graphify v0.8.47 (MIT)
- Built at commit: `96485f5` (cexai/ SDK)
- Lineage record: [[p01_lin_graphify]] (full W3C PROV derivation chain)
- Graphify tokens consumed: input=127943, output=66040

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_lin_graphify]] | upstream-provenance | 0.90 |
| [[p01_kc_sdk_coverage_gap]] | related | 0.55 |
| [[p01_kg_n04]] | related | 0.50 |
| p01_kg_cex_system_architecture | sibling | 0.45 |

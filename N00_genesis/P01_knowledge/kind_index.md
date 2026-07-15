---
id: n00_p01_kind_index
kind: knowledge_card
8f: F3_inject
pillar: P01
nucleus: n00
title: "P01 Knowledge -- Kind Index"
version: 1.0
quality: null
tags: [index, p01, archetype, n00]
density_score: 1.0
related:
  - kc_knowledge_vocabulary
  - p02_ap_n04_knowledge
  - bld_architecture_supabase_data_layer
  - bld_collaboration_supabase_data_layer
updated: "2026-05-27"
---

<!-- 8F: F1=knowledge_card P01 F2=knowledge-card-builder F3=kinds_meta+schema F4=plan F5=scan F6=produce F7=gate F8=save -->

<!-- cex:kind_index:purpose:begin -->
## Purpose
Master index of all 30 kinds in pillar P01. Reference for /mentor, nucleus builders, and the 8F pipeline.
<!-- cex:kind_index:purpose:end -->

## Pillar: P01 Knowledge
Stores and retrieves enterprise knowledge: facts, RAG sources, domain-specific vertical taxonomies, graph schemas, and retrieval configurations. The epistemic foundation every nucleus reads before acting.

<!-- cex:kind_index:body:begin -->
## Kinds in P01

| Kind | Purpose | Primary Nucleus | Builder |
|------|---------|-----------------|---------|
| `agentic_rag` | Agent-driven retrieval augmented generation pattern | N04 | `agentic_rag-builder` |
| `changelog` | Product changelog entry with semver, features, fixes, breaking changes | N04 | `changelog-builder` |
| `chunk_strategy` | Chunking strategy | N04 | `chunk_strategy-builder` |
| `citation` | Structured source attribution with provenance, URL, date, and reliabil | N04 | `citation-builder` |
| `competitive_matrix` | Competitive feature matrix for sales battle cards and procurement eval | N01 | `competitive_matrix-builder` |
| `context_doc` | Domain context | N04 | `context_doc-builder` |
| `dataset_card` | Structured dataset documentation | N04 | `dataset_card-builder` |
| `discovery_questions` | MEDDIC/BANT discovery question bank per buyer persona and deal stage | N04 | `discovery_questions-builder` |
| `domain_vocabulary` | Governed registry of canonical terms for a bounded context, enforcing  | N04 | `domain_vocabulary-builder` |
| `ecommerce_vertical` | eCommerce industry vertical: cart/checkout, PCI-DSS, recommendation en | N04 | `ecommerce_vertical-builder` |
| `edtech_vertical` | Education/EdTech industry vertical: FERPA, COPPA, LMS integration (LTI | N04 | `edtech_vertical-builder` |
| `embedder_provider` | Text embedding provider for vector search | N04 | `embedder_provider-builder` |
| `embedding_config` | Embedding model configuration | N04 | `embedding_config-builder` |
| `faq_entry` | FAQ entry with question, canonical answer, related links, support defl | N04 | `faq_entry-builder` |
| `few_shot_example` | Exemplo input/output pra prompt | N04 | `few_shot_example-builder` |
| `fintech_vertical` | Fintech industry vertical: SOC2+PCI-DSS, KYC/AML, fraud detection, use | N04 | `fintech_vertical-builder` |
| `glossary_entry` | Term definition | N04 | `glossary_entry-builder` |
| `govtech_vertical` | Government/govtech industry vertical: FedRAMP, FISMA, GSA, CJIS, acces | N04 | `govtech_vertical-builder` |
| `graph_rag_config` | Graph-based RAG architecture configuration | N04 | `graph_rag_config-builder` |
| `healthcare_vertical` | Healthcare industry vertical: HIPAA, HL7/FHIR, PHI handling, use cases | N04 | `healthcare_vertical-builder` |
| `knowledge_card` | Fato atomico pesquisavel (densidade > 0.8) | N04 | `knowledge_card-builder` |
| `knowledge_graph` | Graph-based knowledge schema with entity types, relation types, and tr | N04 | `knowledge_graph-builder` |
| `legal_vertical` | Legal industry vertical: privilege, billable hour, contract analysis,  | N04 | `legal_vertical-builder` |
| `lineage_record` | Provenance chain documenting how a knowledge artifact was derived, tra | N04 | `lineage_record-builder` |
| `ontology` | Formal taxonomy and ontology definitions (OWL, SKOS, schema.org patter | N04 | `ontology-builder` |
| `rag_source` | Fonte externa indexavel | N04 | `rag_source-builder` |
| `repo_map` | Codebase context extraction strategy | N04 | `repo_map-builder` |
| `reranker_config` | Retrieval reranking model and strategy config | N04 | `reranker_config-builder` |
| `retriever_config` | Retrieval configuration (top_k, hybrid, reranker) | N04 | `retriever_config-builder` |
| `vector_store` | Vector database backend for similarity search | N04 | `vector_store-builder` |

## Usage
```python
# Build any of these via 8F:
python _tools/cex_8f_runner.py "your intent" --kind {kind} --execute
```

## CoC Hierarchy Note
These 30 kinds follow the convention-over-configuration hierarchy: each instance
(N01-N07) inherits this schema and fills the variables for its sin lens.
N00_genesis holds the canonical archetype; nuclei hold the instantiated versions.
<!-- cex:kind_index:body:end -->

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_knowledge_vocabulary]] | sibling | 0.43 |
| p02_ap_n04_knowledge | downstream | 0.39 |
| bld_architecture_supabase_data_layer | downstream | 0.39 |
| bld_collaboration_supabase_data_layer | downstream | 0.38 |

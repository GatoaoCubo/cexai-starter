---
id: p06_td_document_types
kind: type_def
8f: F1_constrain
pillar: P06
nucleus: n04
title: "Type Definition -- Document Type Taxonomy"
version: "1.0.0"
quality: null
tags: [type_def, document_types, taxonomy, rag, knowledge_card, n04, P06]
domain: knowledge management
status: active
created: "2026-07-20"
updated: "2026-07-20"
author: n04_knowledge
tldr: "Canonical type definitions for the document types that flow through a RAG pipeline: KnowledgeCard, ContextDoc, RAGSource, Artifact, Chunk. Includes field contracts and retrieval behavior per type."
keywords: [knowledge management, rag pipeline, field contracts, retrieval weight, type_def, document_types, taxonomy, knowledge_card, document]
density_score: null
related:
  - bld_schema_model_registry
  - bld_schema_experiment_tracker
  - p06_is_knowledge_query
  - p04_loader_n04_knowledge
slots:
  instance: "<the typed value to construct>"
  field_overrides: "<caller-supplied field values>"
---

# Type Definition: Document Type Taxonomy

## Overview

Every document in the retrieval pipeline has a type. Types determine:
- Which embedding model and chunking strategy to apply
- How the document is stored and indexed
- What metadata fields are required
- How retrieval results are formatted and scored

---

## Base Type: `Document`

All document types extend this base.

```typescript
interface Document {
  id: string;              // UUID v4
  type: DocumentType;      // enum (see below)
  content: string;         // raw text content
  metadata: Metadata;      // type-specific metadata
  embedding?: float[];     // vector, null until indexed
  created_at: datetime;
  updated_at: datetime;
  score?: float;           // only present in retrieval results (0.0-1.0)
}
```

## Enum: `DocumentType`

```typescript
enum DocumentType {
  KNOWLEDGE_CARD = "knowledge_card",
  CONTEXT_DOC    = "context_doc",
  RAG_SOURCE     = "rag_source",
  ARTIFACT       = "artifact",
  CHUNK          = "chunk",
}
```

---

## Type: `KnowledgeCard`

Primary knowledge unit. Typed, peer-reviewed, compiled.

```typescript
interface KnowledgeCard extends Document {
  type: DocumentType.KNOWLEDGE_CARD;
  metadata: {
    kind: string;           // from the kind taxonomy
    pillar: string;         // P01-P12
    nucleus: string;        // n01-n07
    domain: string;
    quality: float | null;  // null until peer-reviewed
    version: string;        // semver
    tldr: string;           // <= 200 chars
    tags: string[];
  };
}
```

**Chunking**: whole document if < 8KB; heading-based split for larger docs.
**Retrieval weight**: 1.2x boost (highest quality signal).

---

## Type: `ContextDoc`

Longer-form operational documentation: guides, specs, runbooks.

```typescript
interface ContextDoc extends Document {
  type: DocumentType.CONTEXT_DOC;
  metadata: {
    title: string;
    kind: string;           // context_doc, contributor_guide, quickstart_guide, etc.
    pillar: string;
    audience: string;       // "developer" | "operator" | "agent"
    version: string;
    toc?: string[];         // table of contents (section headings)
  };
}
```

**Chunking**: semantic chunks, split on H2/H3 boundaries.
**Retrieval weight**: 1.0x (standard).

---

## Type: `RAGSource`

External data source registered for ingestion into the corpus.

```typescript
interface RAGSource extends Document {
  type: DocumentType.RAG_SOURCE;
  metadata: {
    source_url?: string;
    source_type: string;    // "web", "pdf", "repo", "database", "api"
    ingestion_date: datetime;
    refresh_interval?: string; // ISO 8601 duration (e.g., "P7D" for weekly)
    corpus: string;         // target corpus namespace
    trust_level: integer;   // 1 (low) to 5 (high) -- affects retrieval weight
  };
}
```

**Chunking**: adaptive (PDF: 256-token; code: function-level; web: paragraph).
**Retrieval weight**: `trust_level / 5.0` (max 1.0x).

---

## Type: `Artifact`

Any typed artifact file (not necessarily a KC -- agents, configs, schemas).

```typescript
interface Artifact extends Document {
  type: DocumentType.ARTIFACT;
  metadata: {
    kind: string;           // any registered kind
    pillar: string;
    nucleus: string;
    path: string;           // relative path in repo
    quality: float | null;
  };
}
```

**Chunking**: whole document (artifacts are small enough, max 8KB).
**Retrieval weight**: 1.0x.

---

## Type: `Chunk`

Atomic retrieval unit. Produced by the chunking pipeline from any parent document.

```typescript
interface Chunk extends Document {
  type: DocumentType.CHUNK;
  metadata: {
    parent_id: string;      // source document ID
    parent_type: DocumentType;
    chunk_index: integer;   // position in parent
    token_count: integer;
    overlap_tokens: integer;
    heading_context?: string; // nearest H2/H3 above this chunk
  };
}
```

**Chunking**: N/A (is the chunk). **Retrieval weight**: inherits parent weight.

---

## Type Hierarchy

```
Document (base)
  |-- KnowledgeCard   (P01 primary type, highest retrieval weight)
  |-- ContextDoc      (P05 documentation, semantic chunks)
  |-- RAGSource       (external ingested data, trust-weighted)
  |-- Artifact        (any typed artifact, whole-doc embedding)
  |-- Chunk           (atomic retrieval unit, inherits parent)
```

---

## Serialization Rules

| Rule | Requirement |
|------|------------|
| IDs | UUID v4, lowercase, no hyphens in storage keys |
| Dates | ISO 8601 UTC (e.g., `2026-04-17T00:00:00Z`) |
| Content encoding | UTF-8 |
| Metadata | flat JSON (no nesting beyond 1 level) |
| Quality field | float 0.0-10.0 or null (never string "null") |

---

## Cross-References

| Type | Builder | Related Schema |
|------|---------|--------|
| KnowledgeCard | `knowledge-card-builder` | `kc_structure_contract.md` |
| RAGSource | `rag-source-builder` | `rag_source_knowledge.md` |
| Artifact | any kind builder | frontmatter schema per kind |
| Chunk | chunking pipeline | `chunk_strategy_knowledge.md` |

### How to use

```text
You are the consuming agent that acts on this type_def under F1 CONSTRAIN.
- Resolve the open slots (instance, field_overrides) from the caller request.
- Honor every constraint and field contract declared above.
- Emit the result in the shape this type_def defines; never improvise the schema.
```

### Procedure

```text
1. Load this artifact and read its contract under F1 CONSTRAIN.
2. Bind instance and field_overrides from the incoming request.
3. Validate the inputs against the constraints declared above.
4. Execute the type_def behavior; resolve each open slot at act-time.
5. Verify the output shape, then signal completion to the orchestrator.
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_model_registry]] | related | 0.42 |
| [[bld_schema_experiment_tracker]] | related | 0.39 |
| [[p06_is_knowledge_query]] | sibling | 0.36 |
| [[p04_loader_n04_knowledge]] | downstream | 0.30 |

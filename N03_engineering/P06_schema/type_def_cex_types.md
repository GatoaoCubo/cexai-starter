---
id: p06_td_cex_types
kind: type_def
8f: F1_constrain
pillar: P06
title: "Type Definitions -- CEX Core Types"
version: 1.1.0
created: 2026-04-17
updated: "2026-05-02"
author: n03_engineering
domain: artifact-construction
quality: null
strictness:
  frozen: true
  slots: true
  kw_only: true
  rationale: "Core structural types (Kind, Pillar, Nucleus, Quality, Pipeline, Signal) are ground truth for the whole taxonomy; any mutation post-construction breaks every artifact that references them"
tags: [type-def, core-types, kind, pillar, nucleus, quality, pipeline, N03, immutable, frozen, slots, kw_only]
tldr: "Canonical type definitions for the typed knowledge system: Kind, Pillar, Nucleus, Quality, Pipeline, BuildAction, Signal. The source of truth for structural contracts across all nuclei."
keywords: [typescript, kind, pillar, nucleus, schema_id, sin_lens, context_window, builder]
density_score: 0.91
related:
  - bld_schema_model_registry
  - bld_schema_experiment_tracker
  - bld_schema_multimodal_prompt
---

# Type Definitions: CEX Core Types

## Purpose

Defines the canonical structural types used throughout the system.
Every artifact, builder, nucleus, and signal maps to one or more of these types.
These definitions are the machine-readable ground truth for the kind taxonomy.

## Core Types

### Kind

```typescript
type Kind = {
  id: string;              // snake_case identifier, globally unique
  name: string;            // human-readable display name
  pillar: Pillar;          // canonical pillar assignment
  description: string;     // one-line purpose description
  max_bytes: number;       // maximum artifact size in bytes
  naming_pattern: string;  // regex for artifact filename
  builder: string;         // builder agent reference: {kind}-builder
  schema_id: string;       // input_schema artifact id for this kind
  tags: string[];          // classification tags
}
```

### Pillar

```typescript
type Pillar =
  | "P01"  // Knowledge -- storage, retrieval, KCs
  | "P02"  // Model -- agent definitions, providers
  | "P03"  // Prompt -- templates, actions, chains
  | "P04"  // Tools -- external capabilities
  | "P05"  // Output -- production artifacts
  | "P06"  // Schema -- data contracts
  | "P07"  // Evaluation -- quality, scoring, testing
  | "P08"  // Architecture -- system structure
  | "P09"  // Config -- runtime settings
  | "P10"  // Memory -- state, context, indexing
  | "P11"  // Feedback -- learning, correction
  | "P12"  // Orchestration -- workflows, dispatch
```

### Nucleus

```typescript
type Nucleus = {
  id: NucleusId;               // n00-n07
  name: string;                // display name (e.g. "N03_engineering")
  sin_lens: SinLens;           // cultural DNA driving optimization
  domain: string;              // primary domain
  model: "haiku" | "sonnet" | "opus";  // assigned model tier
  context_window: number;      // token limit
  primary_pillars: Pillar[];   // top priority pillars
  agent_card_path: string;     // path to agent_card artifact
}

type NucleusId = "n00" | "n01" | "n02" | "n03" | "n04" | "n05" | "n06" | "n07"

type SinLens =
  "analytical_envy" | "creative_lust" | "inventive_pride" | "knowledge_gluttony"
  | "gating_wrath" | "strategic_greed" | "orchestrating_sloth"
  // one per nucleus N01-N07, in order
```

### Quality

```typescript
type Quality = {
  score: number | null;       // null until peer-reviewed; range [0.0, 10.0]
  tier: QualityTier | null;   // derived from score
  dimensions: QualityDimension[];
  reviewer: string | null;    // nucleus that assigned quality
  reviewed_at: string | null; // ISO date
}

type QualityTier = "exemplary" | "excellent" | "good" | "acceptable" | "below_floor"
// exemplary >= 9.5, excellent >= 9.0, good >= 8.0, acceptable >= 7.0, below_floor < 7.0 (blocked)

type QualityDimension = {
  id: "D1" | "D2" | "D3" | "D4" | "D5";  // Structural, Rubric, Semantic, Coverage, Novelty
  name: string;
  weight: number;  // percentage, D1+D2+D3+D4+D5 = 100
  score: number;   // 0.0-10.0
}
```

### Pipeline

```typescript
type Pipeline = {
  id: string;
  nucleus: NucleusId;
  kind: string;           // artifact kind being built
  started_at: string;     // ISO timestamp
  functions: PipelineFunction[];  // F1-F8 execution records
  status: "running" | "complete" | "failed" | "retrying";
  artifact_path: string | null;   // set on complete
}

type PipelineFunction = {
  fn: "F1" | "F2" | "F3" | "F4" | "F5" | "F6" | "F7" | "F8";
  name: string;    // CONSTRAIN..COLLABORATE, one name per fn
  status: "pending" | "running" | "complete" | "skipped";
  output: string;
  bytes_consumed: number;
}
```

### BuildAction

```typescript
type BuildAction = "CREATE" | "REWRITE" | "MIGRATE" | "IMPROVE" | "VALIDATE"
```

| Action | Meaning |
|--------|---------|
| CREATE | produce from scratch, fail if exists (unless force=true) |
| REWRITE | discard existing, build fresh from same intent |
| MIGRATE | update structure/schema while preserving content |
| IMPROVE | enhance quality score of existing artifact (F7 loop) |
| VALIDATE | run F7 GOVERN only, do not produce/save |

### Signal

```typescript
type Signal = {
  nucleus: NucleusId;
  event: "complete" | "error" | "partial" | "ready";
  score: number | null;
  artifacts: string[];    // paths of produced artifacts
  timestamp: string;      // ISO timestamp
  session_id: string;     // orchestration session this belongs to
  wave: string | null;    // mission wave identifier
}
```

## Type Invariants

1. Every Artifact has exactly one Kind
2. Every Kind maps to exactly one Pillar
3. Quality.score is null until explicitly assigned by a peer nucleus (never self-assigned)
4. Pipeline.functions execute in strict order F1->F2->F3->F4->F5->F6->F7->F8
5. Signal.nucleus must match the nucleus that produced the artifact

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_model_registry]] | related | 0.39 |
| [[bld_schema_experiment_tracker]] | related | 0.36 |
| [[bld_schema_multimodal_prompt]] | related | 0.34 |

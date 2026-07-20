---
id: kc_synthetic_data_config
kind: knowledge_card
8f: F3_inject
title: Synthetic Data Config -- Training Data Generation Pipeline
version: 1.0.0
quality: null
pillar: P01
tags:
  - synthetic-data
  - data-generation
  - training
  - data-centric
  - P01
tldr: "Pipeline config for generating artificial training data -- seeds, augmentation, filtering, dedup"
when_to_use: "When manufacturing training examples at scale to overcome sparse or biased real-world data"
keywords: [seed selection, augmentation strategies, quality filtering, deduplication, format templates, temperature sweep, synthetic data generation, data-centric ai]
related:
  - bld_orchestration_synthetic_data_config
  - synthetic-data-config-builder
  - bld_architecture_synthetic_data_config
  - bld_memory_synthetic_data_config
  - bld_feedback_synthetic_data_config
density_score: 0.98
updated: "2026-05-27"
---

# Synthetic Data Config

A synthetic data config defines the pipeline for generating artificial training data from seed examples. In the data-centric AI paradigm, model performance is bounded by data quality more than architecture -- synthetic data generation is the systematic approach to breaking that bound by manufacturing high-quality training examples at scale.

## Description

Real-world training data is expensive, biased, sparse in edge cases, and often legally encumbered. Synthetic data generation addresses all four constraints: it scales cheaply, can be deliberately balanced, targets underrepresented scenarios, and carries no privacy burden (when done correctly).

The config governs the full pipeline: seed selection (what real examples bootstrap the generator), augmentation strategies (how to create variants), quality filtering (how to reject bad generations), deduplication (how to prevent memorization amplifiers), and format templates (how to structure the output for the training framework).

The core insight from data-centric AI: spending 10x on data quality beats spending 10x on model size. A synthetic data config operationalizes that insight.

## Key Concepts

| Concept | Definition | Importance |
|---------|-----------|------------|
| Seed Data | Real-world examples that bootstrap the generation process | High -- seed quality upper-bounds synthetic quality |
| Augmentation Strategy | Method for creating variants (paraphrase, backtranslation, perturbation) | High -- determines diversity of output |
| Quality Filter | Automated gate that rejects low-quality generations | Critical -- unfiltered synthetic data poisons training |
| Deduplication | Near-duplicate and exact-duplicate removal across the synthetic corpus | High -- duplicates cause memorization, not generalization |
| Format Template | Structural schema for generated examples (instruction/response, QA, etc.) | Medium -- must match the training framework's input spec |
| Temperature Sweep | Generating at multiple temperatures to balance diversity and coherence | Medium -- single temperature creates monotone distributions |
| Self-Consistency Check | Validating that generated answers are consistent across rephrasings | High -- inconsistent data teaches the model to be unreliable |
| Contamination Guard | Ensuring synthetic data does not leak test set information | Critical -- invalidates all downstream evaluation |

## Related Kinds

| Kind | Pillar | Relationship |
|------|--------|-------------|
| dataset_card | P01 | Sibling -- dataset_card documents a dataset; synthetic_data_config creates one |
| eval_dataset | P07 | Downstream -- synthetic data must never contaminate eval datasets |
| finetune_config | P02 | Downstream -- consumes the synthetic dataset for training |
| curriculum_config | P07 | Downstream -- orders the synthetic data for progressive training |
| chunk_strategy | P01 | Upstream -- chunking affects what seed data is available |
| prompt_template | P03 | Tool -- generation prompts drive the synthetic pipeline |
| quality_gate | P11 | Tool -- gates filter synthetic output |

## Anti-Patterns

- **Generate-and-ship**: Producing synthetic data without quality filtering. Even large language models generate nonsense, contradictions, and formatting errors at non-trivial rates.
- **Seed leakage**: Using test set examples as seeds. The synthetic data inherits test-set patterns, making evaluation meaningless.
- **Monoculture generation**: Using a single model at a single temperature. The synthetic distribution collapses to the generator's mode, teaching the student model to parrot one style.
- **No deduplication**: Near-duplicates cause the model to memorize specific phrasings rather than learn the underlying pattern. Use embedding-based dedup, not just exact string matching.
- **Ignoring provenance**: Not tracking which seed produced which synthetic examples. When downstream performance degrades, you cannot diagnose whether the problem is seed quality or augmentation strategy.

## How to use

You are a data engineer manufacturing training examples. Load this card to author a
`synthetic_data_config`. Pick seeds, set an augmentation strategy, and gate every batch
through quality + dedup + contamination guards. Tune the generation temperature across
`{{TEMPERATURE_RANGE}}` for diversity, and always track provenance from seed to output.

## Procedure (run the pipeline)

1. Select seed examples; seed quality upper-bounds everything downstream.
2. Choose an augmentation strategy (paraphrase, backtranslation, perturbation) for diversity.
3. Generate across `{{TEMPERATURE_RANGE}}` to avoid a monoculture distribution.
4. Filter: reject low-quality generations via the quality gate.
5. Deduplicate with embedding-based similarity, not just exact-string match.
6. Run the contamination guard so no test-set signal leaks into the corpus.
7. Emit in the format template the training framework expects; record seed->output provenance.

## Properties

| Property | Value |
|----------|-------|
| Kind | knowledge_card |
| Pillar | P01 |
| Domain | Training data engineering |
| Pipeline | 8F (F1-F8) |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_orchestration_synthetic_data_config]] | downstream | 0.57 |
| [[synthetic-data-config-builder]] | downstream | 0.53 |
| [[bld_architecture_synthetic_data_config]] | downstream | 0.52 |
| [[bld_memory_synthetic_data_config]] | downstream | 0.46 |
| [[bld_feedback_synthetic_data_config]] | downstream | 0.43 |

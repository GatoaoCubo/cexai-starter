---
id: p01_kc_synthetic_data_generation
kind: knowledge_card
card_type: domain_kc
tags: [synthetic data, large language models, prompt-based instruction following, iterative refinement, knowledge transfer, data distillation]
8f: F3_inject
primary_8f: INJECT
title: "Synthetic Data Generation for LLMs"
version: 1.0.0
quality: null
tldr: "Synthetic-data-generation knowledge card -- methods, quality controls, and use cases for generating training/eval data when real data is scarce."
when_to_use: "Inject when planning a synthetic dataset for fine-tuning or eval; consult for 'which generation method + quality gate fits this data need'."
long_tails:
  - "how do I generate synthetic training data safely"
  - "which synthetic data method and quality controls to use"
pillar: P01
language: English
keywords: [synthetic data, large language models, prompt-based instruction following, iterative refinement, knowledge transfer, data distillation, quality filtering, decontamination]
density_score: 1.0
updated: "2026-04-13"
related:
  - bld_knowledge_synthetic_data_config
  - synthetic-data-config-builder
  - bld_orchestration_synthetic_data_config
  - p01_kc_data_residency
  - p01_kc_ai_compliance_gdpr
---

# Synthetic Data Generation for LLMs

## Overview
Synthetic data generation creates artificial datasets to train and evaluate large language models. This technique addresses data scarcity, reduces bias, and enables controlled experimentation.

## Core Techniques

### 1. Self-Instruct
- **Description**: Generate data via prompt-based instruction following
- **Use Case**: Initial data creation when no real data exists
- **Pros**: Simple to implement, full control over data characteristics
- **Cons**: Risk of introducing human bias through prompts

### 2. Evol-Instruct
- **Description**: Iterative refinement through multiple instruction rounds
- **Use Case**: Complex data generation requiring gradual improvement
- **Pros**: Produces higher quality data through iterative optimization
- **Cons**: Computationally intensive and time-consuming

### 3. Distillation
- **Description**: Transfer knowledge from large models to smaller ones
- **Use Case**: Create compact models while preserving performance
- **Pros**: Efficient resource utilization, knowledge preservation
- **Cons**: Dependent on pre-trained models for knowledge transfer

### 4. Quality Filtering
- **Description**: Post-processing to remove low-quality/generated data
- **Use Case**: Clean up datasets after initial generation
- **Pros**: Improves data accuracy and reliability
- **Cons**: Time-consuming and requires quality metrics

### 5. Decontamination
- **Description**: Remove biases and artifacts from generated data
- **Use Case**: Ensure fair and unbiased model training
- **Pros**: Enhances model fairness and generalization
- **Cons**: Complex implementation with no guaranteed results

## Comparison Table

| Technique        | Description                     | Use Case               | Pros                     | Cons                     |
|------------------|---------------------------------|------------------------|--------------------------|--------------------------|
| Self-Instruct    | Prompt-based generation         | Initial data creation  | Simple, full control     | Risk of human bias       |
| Evol-Instruct    | Iterative refinement            | Complex data needs    | High quality output      | Computationally heavy    |
| Distillation     | Knowledge transfer              | Model compression      | Efficient resource use   | Dependent on pre-trained |
| Quality Filtering| Post-processing cleanup         | Data refinement        | Improves accuracy        | Time-consuming           |
| Decontamination  | Bias removal                    | Fairness assurance     | Enhances model fairness  | Complex implementation   |

## Boundary

Conhecimento destilado, estatico, versionado. NAO eh instrucao, template, ou configuracao.


## 8F Pipeline Function

Primary function: **INJECT**

### How to use

```text
ROLE: You are planning a synthetic dataset at F3/F6.
ACT:
  - Pick a generation method matched to the target task + fidelity need.
  - Apply the quality controls listed (dedup, distribution check, leakage guard).
  - Validate synthetic vs real distribution before training on it.
OUTPUT: a vetted synthetic dataset plan, not raw generated rows.
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_knowledge_synthetic_data_config | sibling | 0.27 |
| synthetic-data-config-builder | downstream | 0.27 |
| bld_orchestration_synthetic_data_config | downstream | 0.24 |
| p01_kc_data_residency | sibling | 0.22 |
| [[p01_kc_ai_compliance_gdpr]] | sibling | 0.22 |

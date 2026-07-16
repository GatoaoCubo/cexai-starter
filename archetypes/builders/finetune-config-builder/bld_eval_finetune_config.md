---
kind: quality_gate
id: p11_qg_finetune_config
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of finetune_config artifacts
pattern: few-shot learning -- LLM reads these before producing
quality: null
title: "Gate: finetune_config"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, finetune-config, training, lora, peft, P11]
tldr: "Gates for finetune_config: validates adapter completeness, hyperparameter coverage, dataset spec, eval metrics, and no credentials."
domain: "finetune_config -- LLM fine-tuning job specifications with base model, adapter, dataset, hyperparameters, and eval metrics"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F7_govern"
keywords: [and eval metrics, gates for finetune_config, validates adapter completeness, hyperparameter coverage, dataset spec, eval metrics, and no credentials]
density_score: 0.92
related:
  - bld_schema_finetune_config
---
## Quality Gate

# Gate: finetune_config
## Definition
| Field | Value |
|-------|-------|
| metric | Composite score from SOFT dimensions + all HARD gates pass |
| threshold | >= 7.0 to publish; >= 9.5 golden |
| operator | AND (all HARD) + weighted_sum (SOFT) |
| scope | All artifacts where `kind: finetune_config` |

## HARD Gates
All must pass. Any single failure = REJECT regardless of SOFT score.
| ID | Check | Failure message |
|----|-------|----------------|
| H01 | Frontmatter parses as valid YAML | "Frontmatter YAML syntax error" |
| H02 | `id` matches `^p02_ft_[a-z][a-z0-9_]+$` | "ID fails finetune_config namespace regex" |
| H03 | `id` value equals filename stem | "ID does not match filename" |
| H04 | `kind` equals literal `"finetune_config"` | "Kind is not 'finetune_config'" |
| H05 | `quality` field is `null` | "Quality must be null at authoring time" |
| H06 | All required fields present: id, kind, pillar, base_model, adapter_type, dataset, version, created, author, tags, tldr | "Missing required field(s)" |

## SOFT Scoring
Dimensions sum to 100%. Score each 0.0-10.0; multiply by weight.
| Dimension | Weight | What to assess |
|-----------|--------|----------------|
| Adapter config completeness | 1.5 | All adapter params specified; target_modules explicit, not default |
| Hyperparameter completeness | 1.5 | All 8 standard params present with explicit values, no TBD |
| Dataset specification quality | 1.0 | Format, field_mapping, size, preprocessing all documented |
| Evaluation strategy | 1.0 | eval_strategy, save_strategy, metric_for_best_model all set |
| Compute feasibility | 0.5 | VRAM requirement documented; max_seq_length consistent with compute |
| Effective batch size clarity | 1.0 | per_device_batch_size * gradient_accum * num_gpus documented |
Weight sum: 1.5+1.5+1.0+1.0+0.5+1.0+0.5+0.5+0.5+1.0+1.0+0.5 = 10.0 (100%)

## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | GOLDEN | Publish to pool as golden exemplar |
| >= 8.0 | PUBLISH | Publish to pool |
| >= 7.0 | REVIEW | Flag for human review before publish |
| < 7.0 | REJECT | Return to author with failure report |

## Bypass
| Field | Value |
|-------|-------|
| conditions | Exploratory configs where hyperparameters are intentionally under-specified for sweep |
| approver | ML lead approval required (written); H12 (no credentials) never bypassed |

## Examples

# Examples: finetune-config-builder
## Golden Example
INPUT: "Configure QLoRA fine-tuning of Llama-3-8B for instruction following on a custom dataset"
OUTPUT:
```yaml
id: p02_ft_llama3_8b_instruct_qlora
kind: finetune_config
pillar: P02
version: "1.0.0"
created: "2026-04-13"
updated: "2026-04-13"
author: "builder_agent"
base_model: "meta-llama/Meta-Llama-3-8B"
adapter_type: qlora
dataset: "data/instruct_train.jsonl"
quality: null
tags: [finetune_config, qlora, llama3, instruction-following, sft]
tldr: "QLoRA SFT on Llama-3-8B: rank=16, 4-bit NF4, 3 epochs, cosine LR, instruction dataset 50K rows"
description: "QLoRA fine-tune of Llama-3-8B for instruction following using a 50K-row Alpaca-format dataset"
task_type: sft
framework: trl
compute: "1x A10G 24GB or 1x RTX 4090 24GB"
eval_metrics:
  - eval_loss
  - perplexity
```
## Overview
Adapt Llama-3-8B to follow instructions in a custom domain using supervised fine-tuning.
QLoRA chosen to fit within 24GB VRAM while retaining near-full-fine-tune quality.
4-bit NF4 quantization of base model with LoRA adapters on attention and MLP projections.
## Base Model
| Field | Value |
|-------|-------|
| model_id | meta-llama/Meta-Llama-3-8B |
| architecture | llama3 |
| param_count | 8B |
| license | llama3 |
| quantization | 4bit (NF4, loaded for training) |
## Dataset
| Field | Value |
|-------|-------|
| path | data/instruct_train.jsonl |
| size | 50000 rows |
| format | alpaca |
| field_mapping | instruction / input / output |
| language | en |
| preprocessing | filter max_len=2048, deduplicate |
## Adapter Config
| Parameter | Value |
|-----------|-------|
| r (rank) | 16 |
| lora_alpha | 32 |
| lora_dropout | 0.05 |
| target_modules | q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj |
| bias | none |
| task_type | CAUSAL_LM |
## Hyperparameters
| Parameter | Value |
|-----------|-------|
| learning_rate | 2e-4 |
| per_device_train_batch_size | 2 |
| gradient_accumulation_steps | 8 |
| num_train_epochs | 3 |
| max_steps | -1 |
| warmup_ratio | 0.03 |
## Evaluation
| Parameter | Value |
|-----------|-------|
| eval_strategy | epoch |
| eval_steps | null |
| save_strategy | epoch |
| save_steps | null |
| save_total_limit | 3 |
| load_best_model_at_end | true |
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p02_ft_ pattern (H02 pass)
- kind: finetune_config (H04 pass)
- adapter_type from allowed enum (H06 pass)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)

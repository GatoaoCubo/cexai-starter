---
id: bld_feedback_marketplace_listing
kind: reward_signal
pillar: P11
llm_function: GOVERN
8f: F7_govern
version: 1.0.0
created: "2026-07-02"
updated: "2026-07-02"
author: n03_builder
title: "Feedback: marketplace_listing reward + regression signals"
domain: marketplace_listing
quality: null
tags: [marketplace_listing, builder, feedback, signals, P11]
tldr: "What to reward and what to flag across marketplace_listing builds: complete-on-first-try, correct auto-injection, honest gaps, and the known https/stock divergence vs the lower-level seam."
density_score: 0.88
related:
  - bld_eval_marketplace_listing
  - bld_memory_marketplace_listing
  - bld_knowledge_marketplace_listing
  - output-validator-builder
  - bld_architecture_marketplace_listing
---

# Feedback: marketplace_listing signals
## Reward signals (reinforce)
| Signal | Meaning |
|--------|---------|
| complete_first_try | all 3 gate fields (titulo_ml/categoria_ml/preco) present -> score 1.0, passed=true, zero retries |
| brand_sku_injected_clean | BRAND + SELLER_SKU appear in attributes[] exactly once, never duplicated when atributos already declared one |
| condition_mapped_correctly | novo/usado/recondicionado map to new/used/refurbished with no 4th value invented |
| honest_gap_noted | an absent optional field (fotos/marca/descricao) renders its exact `[WARN]` note, never a silent drop |
| dual_output_ready | the artifact's frontmatter carries score/passed/notes/real so `cex_dual_output.to_dual_output` needs zero guessing |

## Regression signals (flag)
| Signal | Meaning |
|--------|---------|
| section_retitled_or_reordered | breaks the FROZEN 6-section contract -> H05 hard gate fail |
| fabricated_photo_url | clean-room breach -> reject + rebuild from the real G1 row only |
| category_id_silently_empty | no `[FAIL]` note attached -- category resolution is a KNOWN TODO (needs a live ML token per `cex_channel_adapter.py`'s `category_source` comment) |
| https_filter_assumed | the SHIPPED generator does NOT filter non-https picture URLs (unlike the lower-level `cex_channel_adapter.py` seam) -- do not claim it does |
| stock_zero_assumed_blocking | the SHIPPED generator does NOT hard-block on `available_quantity<=0` (only the other seam's `buyability()` does) -- do not invent a block that is not there |
| quality_score_conflated | writing a number into `quality:` instead of `null`, or writing the readiness `score` into `quality:` -- two distinct fields |

## Loop hook
Peer-review approvals/rejections feed future builds; a rejection on
`category_id_silently_empty` or `https_filter_assumed` should update
[[bld_knowledge_marketplace_listing]] before the next build, not just this instance.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_eval_marketplace_listing]] | upstream | 0.48 |
| [[bld_memory_marketplace_listing]] | sibling | 0.42 |
| [[bld_knowledge_marketplace_listing]] | related | 0.42 |
| [[output-validator-builder]] | related | 0.38 |
| [[bld_architecture_marketplace_listing]] | related | 0.36 |

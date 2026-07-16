---
id: p01_dc_glue_brain_corpus
kind: dataset_card
pillar: P01
title: "CEXAI Glue-Brain FT Corpus"
version: "2.0.0"
created: "2026-06-10"
updated: "2026-06-10"
author: n01_intelligence
domain: fine-tuning/structured-routing
quality: null
tags: [dataset_card, ft, glue-brain, carteiro, rag, preflight, injetar, outcome_gold, b4_6]
tldr: "1050-pair Alpaca corpus (backfill/heuristic) + 3677-pair outcome-gold TRAIN set (B4.6, frontmatter-derived) for fine-tuning a ~3B structured router. TRAIN/EVAL disjoint proven. 49 multi-nucleus kinds in train = key FT signal."
license: MIT
schema_ref: _tools/cex_glue_logger.py
language: en
source: "_data/ft/glue/ (gitignored -- live ops + backfill replay + outcome_gold)"
---

## Dataset Overview

The CEXAI glue-brain corpus trains a ~3B structured router/retriever serving four
orchestration roles: **carteiro** (intent-to-kind routing), **rag** (artifact retrieval),
**preflight** (context source selection), and **injetar** (context assembly).

Two corpus components:
1. **Operational corpus** (1050 pairs, 8 JSONL files): live ops + backfill replay.
   Verified 2026-06-10 via cex_glue_validator.py: 0 fails.
2. **Outcome-gold train set** (3677 pairs, B4.6): frontmatter-derived labels from the
   full N01-N07 corpus, DISJOINT from the 171-pair eval set. 3609 validator-pass pairs.

Output tokens are SHORT STRUCTURED TOKENS by design -- carteiro outputs {kind, pillar,
nucleus, verb}; rag outputs a ranked list; preflight and injetar output dicts. The
G2 glue-specific validator enforces per-role structured-token rules (not char-length).

## Data Collection Methodology

**Component 1 -- Operational corpus** (logged at zero marginal cost):

| Source | Pairs | Description |
|--------|-------|-------------|
| heuristic | 581 | cex_intent_resolver output echoed as label; mirrors resolver decisions |
| backfill | 469 | Replayed from git log + archived dispatches; outcome-verified |

**Component 2 -- Outcome-gold train set (B4.6)** (NO SPEND, frontmatter extraction):

| Source | Pairs | Description |
|--------|-------|-------------|
| outcome_gold (train) | 3677 | Full N01-N07 corpus frontmatter, minus 171 eval held-out |

Labels from artifact frontmatter (kind/pillar/nucleus) are resolver-independent -- they
reflect what the human builder ACTUALLY declared. This breaks the circular 100% that
the backfill eval produced (backfill labels = heuristic output = self-referential).

No distilled (Opus/Sonnet) gold pairs in the operational corpus yet. Distilled manufacture
is gated behind G3 founder spend approval.

## Data Preprocessing & Cleaning

- **G2 validator** (cex_glue_validator.py): per-role structured-token validation; three
  verdicts: pass / abstain / fail. Current corpus: pass=1035, abstain=15, fail=0.
- **Taxonomy-currency filter**: every carteiro label verified against current
  kinds_meta.json; labels for renamed/removed kinds dropped.
- **Redaction at log time**: api_key, token, secret, password, email, authorization
  keys replaced with "[REDACTED]" before writing to disk.
- **Max record size**: 65536 bytes/pair; heavy fields truncated, pair retained.

## Annotation Process

Labels are structured tokens per role (Alpaca format: instruction/input/output).

| Role | Output token shape | Validation |
|------|--------------------|-----------|
| carteiro | {kind, pillar, nucleus, verb} | kind in kinds_meta; pillar match; verb canonical |
| rag | [{id, kind, score}...] descending | non-empty id; numeric score; descending order |
| preflight | {selected_isos, selected_kcs, needs_cloud} | list shape; bool needs_cloud |
| injetar | {injected_sources, compression} | list; compression in [0, 1] |

Label trust hierarchy (source field): **backfill** (outcome-verified, artifact committed)
> **heuristic** (resolver echo -- weakest; clones resolver errors).
Distilled (opus/sonnet) will outrank both when added.

## Statistical Properties

| Role | Total | Pass | Abstain | Fail | heuristic | backfill |
|------|-------|------|---------|------|-----------|----------|
| carteiro | 648 | 633 | 15 | 0 | 524 | 124 |
| rag | 348 | 348 | 0 | 0 | 55 | 293 |
| injetar | 27 | 27 | 0 | 0 | 1 | 26 |
| preflight | 27 | 27 | 0 | 0 | 1 | 26 |
| **TOTAL** | **1050** | **1035** | **15** | **0** | **581** | **469** |

rag/concrete_warn: 162 pairs (valid rankings where some items have non-canonical kinds --
real retrieval hits on rule/builder files; hard invariants pass). Abstain rate: 1.4%
(all carteiro, kind=None low-confidence escalation -- valid label, low training value).

Gold rate: 0.0% (no distilled pairs yet). Target: >=40% distilled gold.
heuristic dominance in carteiro: 524/648 = 80.9%.

## Usage Limitations & Bias

**Known gaps (not hidden):**
- preflight + injetar SHORT: 27 pairs each vs target >=150/role. Training on these roles
  will under-represent the inference distribution until manufacture runs.
- No distilled gold (0%): corpus is 100% heuristic+backfill. Model risks inheriting
  resolver errors at current gold rate. G1 gate (>=100 diverse/role) not yet cleared.
- carteiro heuristic dominance (80.9%): high-frequency kinds over-represented; long-tail
  routing accuracy will be lower than aggregate metrics suggest.

**Curation choices baked in:**
1. Real-distribution anchor: heuristic + backfill reflect actual inference traffic.
2. Trust hierarchy: backfill > heuristic; distilled gold (when added) will outrank both.
3. Coverage floor: 304-kind label space is skewed; realistic prior preserved, not flattened.
4. Short roles flagged explicitly -- manufacture gap is the correct fix, not suppression.
5. Eval slice carved from backfill-only (heuristic excluded -- no circular testing).
6. Taxonomy-currency enforced: stale labels dropped against current kinds_meta.json.

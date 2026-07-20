---
id: p10_bi_ops_hybrid_index
kind: knowledge_index
8f: F3_inject
pillar: P10
nucleus: N05
title: "N05 Operations Knowledge Index"
version: "1.0.0"
created: "2026-07-20"
updated: "2026-07-20"
quality: null
tags: [n05, operations, knowledge_index, gating_wrath, bm25, hybrid, P10]
keywords: [operations knowledge index, knowledge_index, gating_wrath, bm25, hybrid, n05_ops_hybrid_index]
density_score: 1.0
related:
  - kno_embedder_provider_n05
  - p01_retr_n05
  - kno_vector_store_n05
  - p10_em_n05
  - p01_chunk_n05
---

# N05 Operations Knowledge Index

## Intent

This memory artifact defines how N05 indexes and refreshes its operational corpus across
sparse and dense retrieval paths. The index is a memory concern because it captures
persistent search behavior, rebuild posture, freshness rules, and fallback routing across
sessions -- not the documents themselves.

## Properties

| Property | Value |
|----------|-------|
| Kind | `knowledge_index` |
| Pillar | `P10` |
| Nucleus | `N05` |
| Name | `n05_ops_hybrid_index` |
| Backend mode | `bm25 + dense-vector` |
| Hybrid alpha | `0.62 semantic / 0.38 lexical` |
| Rebuild threshold | `24h or source_hash drift` |
| Failure stance | `degrade_to_sparse_only_explicitly` |

## Corpus Scope

Indexed material:
- N05 knowledge artifacts (P01)
- N05 memory artifacts (P10)
- N05 schemas and config (P06, P09)
- curated operational examples relevant to deploy, CI, tests, and rollback

Excluded by default:
- raw vendor docs with no local operational relevance
- generated compiled outputs as primary retrieval targets
- long transient logs after incident close, unless converted into summaries

The index is for N05 judgment, not archival hoarding.

## Dense Branch

| Field | Value |
|-------|-------|
| vector backend | see [[kno_vector_store_n05]] |
| embedder | see [[kno_embedder_provider_n05]] |
| normalization | required |
| namespace split | `ops_runbook, ops_ci, ops_deploy, ops_schema, ops_memory` |
| freshness key | `source_hash` |

Dense retrieval handles semantic matching across paraphrased symptoms and repeated
patterns -- the case where the words differ but the underlying issue is the same one seen
before.

## Sparse Branch

| Field | Value |
|-------|-------|
| algorithm | `bm25` |
| token policy | preserve code tokens and path segments |
| boost fields | `title, tags, test_id, service, endpoint, env_key` |
| rebuild speed target | `< 2 minutes` |
| fallback role | authoritative exact-match path when dense is unavailable |

Sparse search is critical for exact test names, filenames, environment variables,
endpoint names, commands, and release IDs -- the case where the words matter exactly.

## Hybrid Policy

Fusion policy:
1. retrieve top candidates from both branches
2. fuse with reciprocal rank fusion
3. apply freshness decay
4. rerank toward evidence utility
5. emit only the strongest `6` results

N05 does not use a naive blended score because operational queries often have one exact
needle (a filename, an env var) and one semantic symptom (a paraphrased failure
description) in the SAME query. Rank fusion handles that mix more robustly than a single
weighted average.

## Freshness Rules

| Content class | Freshness posture |
|---------------|-------------------|
| schema/config | stable, low decay |
| runbook/checklist | stable, medium decay |
| deploy log | high decay |
| CI/test output | high decay |
| learning record | medium decay |

Freshness matters more in operations than in generic knowledge work: an old rollback note
can be actively harmful if followed as current.

## Rebuild Triggers

Trigger a rebuild when: any source hash changes in indexed artifacts, chunk strategy
changes, embedder model changes, vector dimension changes, or sparse tokenizer rules
change. Rebuild scope is per-namespace if the change is local, full index if the embedder
or dimension changes.

## Gating Wrath Controls

Hard controls for this index:
1. dense branch may not silently switch models
2. sparse-only degradation must be recorded in index state
3. stale namespaces may not remain queryable after a failed rebuild without warning
4. rebuild completion requires audit metadata
5. query responses must expose the active search mode when degraded

These controls prevent "it kind of worked" from becoming an accepted ops state.

## Failure Modes

| Failure mode | Symptom | Mitigation |
|--------------|---------|------------|
| stale dense namespace | old incidents retrieved | source_hash drift detection |
| sparse token collapse | filenames stop matching | token preservation tests |
| silent degraded mode | operators think hybrid is active | explicit mode flag |
| overwide corpus | noisy retrieval | strict corpus scope |
| no rebuild audit | unknown provenance | mandatory audit row |

## Integration

This index works with [[p01_chunk_n05]] chunking, [[kno_embedder_provider_n05]],
[[p01_retr_n05]], and [[kno_vector_store_n05]] -- it is the memory of how search is
supposed to BEHAVE, not just where the data happens to live.

## Decision Summary

Use a hybrid `bm25 + dense-vector` index with explicit rebuild audits, class-aware
freshness, and a visible degraded mode. That is the correct N05 posture because
operations memory must remain inspectable under pressure.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kno_embedder_provider_n05]] | upstream | 0.42 |
| [[p01_retr_n05]] | upstream | 0.39 |
| [[kno_vector_store_n05]] | upstream | 0.36 |
| [[p10_em_n05]] | sibling | 0.30 |

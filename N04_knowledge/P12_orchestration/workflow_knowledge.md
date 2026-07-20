---
id: p12_wf_knowledge
kind: workflow
8f: F8_collaborate
pillar: P12
title: "N04 Workflow -- Knowledge Lifecycle Pipeline"
version: 4.1.1
created: 2026-03-31
updated: "2026-07-20"
author: n07_orchestrator
domain: knowledge-management
step_count: 8
quality: null
tags: [workflow, n04, knowledge, lifecycle, pipeline, taxonomy, ingestion, indexing, export]
tldr: "8-step KC lifecycle: ingest -> classify -> distill -> structure -> validate -> index -> export -> monitor. Owned by N04; downstream tools wire each step."
keywords: [knowledge lifecycle pipeline, step kc lifecycle, workflow, knowledge, lifecycle, pipeline, taxonomy, export formats, usage guidelines, classification, distillation, validation, indexing, monitoring]
density_score: null
related:
  - agent_card_n04
  - bld_collaboration_knowledge_card
  - kc_validator_tool
---

# N04 Workflow -- Knowledge Lifecycle

## Pipeline
```
INGEST -> CLASSIFY -> DISTILL -> STRUCTURE -> VALIDATE -> INDEX -> EXPORT -> MONITOR
```

| Step | Action | Input | Output | Tool |
|------|--------|-------|--------|------|
| 1 | Ingest raw material | Docs, research, code, conversations | Raw text | markitdown MCP, manual |
| 2 | Classify | Raw text | kind x pillar x domain | kinds_meta.json, taxonomy_contract.md |
| 3 | Distill | Classified raw | Signal extracted, noise removed | kc_knowledge_distillation pattern |
| 4 | Structure | Distilled content | KC with frontmatter + sections | kc_structure_contract.md |
| 5 | Validate | Structured KC | Compile pass + density check | cex_compile.py, density >= 0.85 |
| 6 | Index | Validated KC | Search index updated | cex_index.py + cex_retriever.py |
| 7 | Export | Indexed KC | YAML + JSONL + SQL | export_format_contract.md |
| 8 | Monitor | All KCs | Freshness alerts, gap reports | freshness_contract.md, cex_evolve.py |

## Step Detail

### 1. Ingest
- Sources: web pages, PDFs, conversations, code, prior nuclei output
- Tools: `markitdown` MCP (documents), `fetch` MCP (web), `cex_preflight_mcp.py` (N07 only)
- Output: raw text in working memory

### 2. Classify
- Apply 5-question test from `taxonomy_contract.md` if intent doesn't match existing kind
- Output: `{kind, pillar, nucleus, domain, tags}` tuple
- Tool: `cex_intent_resolver.py` (zero-token fast path)

### 3. Distill
- Strip filler, extract entities, identify the irreducible knowledge unit
- Apply Knowledge Gluttony lens: keep depth, drop padding
- Output: distilled signal-only text

### 4. Structure
- Apply `kc_structure_contract.md` (frontmatter + section order)
- Use builder ISOs for the kind to enforce structure
- Output: `.md` artifact with valid frontmatter

### 5. Validate
- Run `cex_doctor.py` (BLOCKING gates)
- Run `kc_validator.py` (density, anti-patterns, cross-refs) -- (proposed, not yet implemented; design spec at `kc_validator_tool.md`, no `_tools/kc_validator.py` on disk today)
- Run `cex_compile.py` (YAML parse + frontmatter sanity)
- Output: PASS/FAIL with severity

### 6. Index
- Run `cex_compile.py {path}` (md -> yaml mirror)
- Run `cex_index.py` (rebuild wikilink graph)
- Run `cex_retriever.py --build` (TF-IDF index update)
- Output: searchable + queryable

### 7. Export
> **Implementation status** (verified 2026-07-17): no `cex_export.py` exists on disk or in git history -- the 3 formats below are design-only, not a shipped tool. `_tools/cex_export_agent.py` is a different, real tool (portable per-capability agent-package export for GPT Builder / Claude Project / MCP) and does not implement `--format`. Full format spec: `export_format_contract.md` (design reference; not present in this starter's curated subset today).
- For training datasets: `cex_export.py --format jsonl` (proposed, not yet implemented)
- For Supabase: `cex_export.py --format sql` (proposed, not yet implemented)
- For analytics: `cex_export.py --format csv` (proposed, not yet implemented)
- Output: format-specific files in `_reports/`

### 8. Monitor
- Daily: `git log --since` + freshness audit
- Weekly: `cex_evolve.py --pillar P10 --min-density 0.85`
- Quarterly: cross-pillar audit + vocabulary sync
- Output: gap reports, refresh queue

## Export Formats

| Format | Purpose | Consumer |
|--------|---------|----------|
| .yaml | CEXAI compiled artifact | All nuclei (compose_prompt) |
| .jsonl | Fine-tuning dataset | External LLM training |
| SQL | Database persistence | Supabase, vector search |
| .csv | ML feature datasets | Analytics, dashboards |

## Usage Guidelines

**When to use:**
- Converting messy research into structured knowledge cards
- Building systematic knowledge base for team/organization
- Preparing training data for fine-tuning models
- Creating searchable documentation from scattered sources

**Anti-patterns:**
- Skipping classification step (leads to wrong pillar placement)
- Accepting density < 0.85 (low information content)
- Manual indexing instead of using `cex_index.py`
- Creating KCs without monitoring freshness (stale knowledge)
- Skipping the distill step ("just dump research into a KC")
- Exporting before validation (poisons training data)
- Using one format when downstream needs another (no conversion guarantees)

## Failure Modes & Fallbacks

| Failure | Step | Fallback |
|---------|------|----------|
| Source unavailable | 1. Ingest | Skip + log; flag in gap report |
| Classification ambiguous | 2. Classify | GDP -> ask user; default to most-similar existing artifact |
| Density < 0.78 | 5. Validate | Return to step 3, re-distill once (max 2 retries) |
| Compile error | 5. Validate | Block commit; surface YAML diagnostics |
| Index rebuild slow | 6. Index | Defer to overnight; serve last-known-good index |
| Export fails | 7. Export | Quarantine artifact; partial export rest |
| Stale detection | 8. Monitor | Auto-queue for `cex_evolve.py` |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[agent_card_n04]] | upstream | 0.32 |
| [[bld_collaboration_knowledge_card]] | related | 0.28 |
| [[p04_cli_kc_validator_n04]] | downstream | 0.40 |

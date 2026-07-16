---
kind: quality_gate
id: p11_qg_batch_config
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of batch_config artifacts
pattern: few-shot learning -- LLM reads these before producing
quality: 9.1
title: "Gate: batch_config"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, batch-config, async-api, cost-controls, P11]
tldr: "Gates for batch_config artifacts: validates provider, cost cap, completion window, retry policy, credential hygiene, and body section completeness."
domain: "batch_config -- async bulk API job configuration with cost controls, retry policy, and I/O format"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F7_govern"
keywords: [retry policy, o format, gates for batch_config artifacts, validates provider, cost cap, completion window, credential hygiene]
density_score: 0.92
related:
  - bld_architecture_batch_config
  - bld_schema_batch_config
---
## Quality Gate
# Gate: batch_config
## Definition
| Field | Value |
|-------|-------|
| metric | Composite score from SOFT dimensions + all HARD gates pass |
| threshold | >= 7.0 to publish; >= 9.5 golden |
| operator | AND (all HARD) + weighted_sum (SOFT) |
| scope | All artifacts where `kind: batch_config` |
## HARD Gates
All must pass. Any single failure = REJECT regardless of SOFT score.
| ID | Check | Failure message |
|----|-------|----------------|
| H01 | Frontmatter parses as valid YAML | "Frontmatter YAML syntax error" |
| H02 | `id` matches `^p09_bc_[a-z][a-z0-9_]+$` | "ID fails batch_config namespace regex" |
| H03 | `id` value equals filename stem | "ID does not match filename" |
| H04 | `kind` equals literal `"batch_config"` | "Kind is not 'batch_config'" |
| H05 | `quality` field is `null` | "Quality must be null at authoring time" |
| H06 | All required fields present: id, kind, pillar, provider, model, endpoint, version, created, author, tags | "Missing required field(s)" |
## SOFT Scoring
Dimensions sum to 100%. Score each 0.0-10.0; multiply by weight.
| Dimension | Weight | What to assess |
|-----------|--------|----------------|
| Cost control completeness | 1.5 | cost_cap_usd, max_requests, token_budget, alert threshold all specified |
| Retry policy specificity | 1.5 | max_retries, backoff type, partial_failure behavior, dead_letter path defined |
| Provider accuracy | 1.0 | Provider enum valid, model confirmed batch-eligible, endpoint path correct |
| Completion window rationale | 1.0 | Window matches provider SLA, downstream use documented |
| I/O format clarity | 1.0 | JSONL schema summary for both input and output, storage paths specified |
| Credential hygiene | 1.0 | Env var name referenced, no embedded values, storage guidance noted |
Weight sum: 1.5+1.5+1.0+1.0+1.0+1.0+0.5+0.5+0.5+0.5 = 9.0 (normalized to 100%)
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
| conditions | Early-stage batch integration where provider SLA is unknown |
| approver | Engineering lead approval required (written); cost_cap_usd and credential hygiene gates never bypassed |
## Examples
# Examples: batch-config-builder
## Golden Example
INPUT: "Configure a batch job for bulk document classification using OpenAI"
OUTPUT:
```yaml
id: p09_bc_doc_classifier
kind: batch_config
pillar: P09
version: "1.0.0"
created: "2026-04-13"
updated: "2026-04-13"
author: "builder_agent"
provider: "openai"
```
## Overview
Classifies up to 5,000 documents per batch run using OpenAI Batch API at ~50% cost reduction vs sync.
Triggered by: scheduled pipeline after document ingestion completes.
Credential env var: `OPENAI_API_KEY`
## Job Parameters
| Parameter | Value | Description |
|-----------|-------|-------------|
| provider | openai | OpenAI Batch API |
| model | gpt-4o-mini | Cost-efficient model for classification |
| endpoint | /v1/chat/completions | Standard chat completions endpoint |
| max_requests | 5000 | Max documents per batch submission |
| completion_window | 24h | OpenAI SLA for batch completion |
| concurrency | 100 | Max in-flight requests at one time |
## Cost Controls
| Control | Value | Notes |
|---------|-------|-------|
| cost_cap_usd | $20.00 | Job halts if projected spend exceeds cap |
| sync_api_discount | ~50% | Batch pricing vs synchronous equivalent |
| token_budget | 1024 tokens | Max tokens per request (256 input + 768 output) |
| alert_threshold_usd | $15.00 | Alert when 75% of cap is reached |
## Retry and Error Policy
| Setting | Value | Description |
|---------|-------|-------------|
| max_retries | 3 | Retries per failed request |
| backoff | exponential | 2s, 4s, 8s wait before retries |
| backoff_base_s | 2 | Base wait in seconds |
| partial_failure | continue | Process remaining requests if some fail |
| dead_letter | s3://batch-errors/doc_classifier/ | Failed requests stored for manual review |
## Input/Output Format
- Input format: JSONL -- each line: `{"custom_id": "doc-001", "method": "POST", "url": "/v1/chat/completions", "body": {...}}`
- Output format: JSONL -- each line: `{"id": "batch_req_...", "custom_id": "doc-001", "response": {...}, "error": null}`
- Input path: `s3://batch-jobs/input/doc_classifier_`{{date}}`.jsonl`
- Output path: `s3://batch-jobs/output/doc_classifier_`{{date}}`.jsonl`
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p09_bc_ pattern (H02 pass)
- kind: batch_config (H04 pass)
- provider is valid enum value: openai (H06 pass)
---

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)

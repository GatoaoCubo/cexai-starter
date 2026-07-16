---
kind: quality_gate
id: p11_qg_embedder_provider
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of embedder_provider artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: Embedder Provider"
version: "1.0.0"
author: builder_agent
tags: [quality-gate, embedder-provider, embedding, P01, dimensions]
tldr: "Quality gate for embedder_provider artifacts: enforces dimensions, normalization, max_tokens, and provider authentication fields."
domain: embedder_provider
created: "2026-04-06"
updated: "2026-04-06"
8f: "F7_govern"
density_score: 0.87
related:
  - embedder-provider-builder
  - bld_memory_embedder_provider
---
## Quality Gate

# Gate: Embedder Provider
## Definition
An `embedder_provider` is a connection configuration for an embedding model: provider, model ID, dimensions, normalization, batch size, and authentication. Infrastructure artifact only — not a tutorial. Gates ensure dimension correctness, normalization explicitness, and traceability to official documentation.
## HARD Gates
All HARD gates must pass. Any single failure sets score to 0 and blocks publish.
| ID  | Check | Failure consequence |
|-----|-------|---------------------|
| H01 | YAML frontmatter parses without error | Artifact unparseable by tooling |
| H02 | `id` matches `^p01_emb_[a-z][a-z0-9_]+$` | Namespace violation — not discoverable |
| H03 | `id` equals filename stem exactly | Brain search failure — id/file mismatch |
| H04 | `kind` == literal string `"embedder_provider"` | Type integrity failure |
| H05 | `quality` == `null` | Self-scoring violation — pool metric corruption |
| H06 | Required fields present: `id`, `kind`, `pillar`, `version`, `created`, `updated`, `author`, `provider`, `model`, `dimensions`, `max_tokens`, `normalize`, `tags`, `tldr` | Incomplete artifact |
## SOFT Scoring
Weights sum to 100%. Each dimension scores 0 or its full weight.
| ID  | Dimension | Weight | Criteria |
|-----|-----------|--------|----------|
| S01 | tldr quality | 1.0 | `tldr` <= 160 chars, names provider + model + primary dimension |
| S02 | Pricing documented | 1.0 | `pricing.per_1m_tokens` present; `null` for local models |
| S03 | MTEB score referenced | 1.0 | At least one MTEB benchmark score (retrieval or STS) cited |
| S04 | Batch size documented | 1.0 | `batch_size` present with provider rate limit source |
| S05 | Matryoshka flag set | 0.5 | `matryoshka` boolean present if model supports MRL |
| S06 | Distance metric specified | 1.0 | `distance_metric` present with rationale |
## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | GOLDEN | Publish to pool + record in memory |
| >= 8.0 | PUBLISH | Commit to pool |
| >= 7.0 | REVIEW | Acceptable with documented improvement items |
| < 7.0 | REJECT | Revise and resubmit — do not publish |
| 0 (HARD fail) | REJECTED | Fix failing HARD gate(s) first |
## Bypass
Bypasses are logged and expire automatically.
| Field | Value |
|-------|-------|

## Examples

# Examples: embedder-provider-builder
## Golden Example
INPUT: "Configure OpenAI text-embedding-3-small for semantic search"
OUTPUT:
```yaml
id: p01_emb_openai_text_embedding_3_small
kind: embedder_provider
pillar: P01
version: "1.0.0"
created: "2026-04-06"
updated: "2026-04-06"
author: "builder_agent"
provider: "openai"
```python
from openai import OpenAI
client = OpenAI()  # uses OPENAI_API_KEY env var
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=["query text"],
    dimensions=1536  # or 512 for MRL reduction
)
vector = response.data[0].embedding  # len == dimensions
```
## Anti-Patterns
1. Mixing text-embedding-3-small with text-embedding-ada-002 in the same index — incompatible vector spaces
2. Setting dimensions=512 without matryoshka support verification — produces zero-padded garbage
3. Exceeding 8191 tokens without truncation — API silently truncates, losing document tail
4. Using dot_product distance with normalized vectors — cosine is correct for L2-normalized output

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)

---
kind: quality_gate
id: p11_qg_knowledge_card
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of knowledge_card artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: Knowledge Card"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, knowledge-card, density, fact, distillation, searchability]
tldr: "Gates ensuring knowledge_card artifacts contain concrete atomic facts with density >= 0.8, semantic frontmatter, and file size <= 5KB."
domain: "knowledge_card — atomic searchable facts with high information density"
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
density_score: 0.94
---
## Quality Gate

# Gate: Knowledge Card
## Definition
| Field     | Value |
|-----------|-------|
| metric    | weighted soft score + all hard gates pass |
| threshold | 7.0 to publish; 8.0 for pool; 9.5 for golden |
| operator  | AND (all hard) + weighted average (soft) |
| scope     | any artifact with `kind: knowledge_card` |
## HARD Gates
All must pass. Any failure = immediate reject.
| ID  | Check | Fail Condition |
|-----|-------|----------------|
| H01 | Frontmatter parses as valid YAML | Parse error on any field |
| H02 | ID matches `^KC_[A-Z0-9_]+$` | Lowercase, missing KC_ prefix, or non-alphanumeric chars |
| H03 | ID equals filename stem | `id: KC_REDIS_TTL` in file `KC_CACHE_TTL.md` |
| H04 | Kind equals literal `knowledge_card` | Any other kind value |
| H05 | Quality field is `null` | Any non-null value |
| H06 | All 19 required fields present | Missing: domain, tldr, density_score, sources, or card_type |
## SOFT Scoring
Total weights sum to 100%.
| ID  | Dimension | Weight | 10 pts | 5 pts | 0 pts |
|-----|-----------|--------|--------|-------|-------|
| S01 | Factual concreteness | 1.0 | Card contains specific values, numbers, or verifiable facts | Mix of facts and vague statements | Entirely vague or conceptual |
| S02 | Atomicity | 1.0 | Card covers exactly one concept with no scope creep | Mostly one concept; minor tangents | Multiple unrelated concepts |
| S03 | Searchability — tags | 1.0 | Tags cover domain, subtopic, and use-case angles (>= 4 distinct tags) | 3 tags | Fewer than 3 tags |
| S04 | Source attribution | 1.0 | At least one specific source (URL, paper, spec version, date) | Source mentioned but not specific | No sources |
| S05 | Card type classification | 0.5 | `card_type` is `domain_kc` or `meta_kc` with correct body structure for that type | Type present but body structure mismatches | Type absent |
| S06 | Density discipline | 1.0 | No padding, no restatements, no filler sentences in body | Minor padding present | More than 20% filler content |
**Score = sum(pts * weight) / sum(max_pts * weight) * 10**
## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | Golden | Publish to knowledge pool as authoritative reference card |
| >= 8.0 | Skilled | Publish to pool + log pattern |
| >= 7.0 | Learning | Use but flag for improvement |
| < 7.0 | Rejected | Return to author with gate report |
## Bypass
| Field | Value |
|-------|-------|
| Conditions | Rapidly evolving topic where sources are not yet stabilized (e.g., new library release, breaking API change) |
| Approver | Domain expert reviewer |

## Examples

# Examples: knowledge-card-builder
## Golden Example
INPUT: "Destila knowledge about prompt caching for optimize costs LLM"
OUTPUT:
```yaml
id: p01_kc_prompt_caching
kind: knowledge_card
pillar: P01
title: "Prompt Caching Patterns for LLM Cost Optimization"
version: "1.0.0"
created: "2026-03-24"
updated: "2026-03-24"
author: "builder"
```yaml
topic: prompt_caching
scope: LLM API optimization (Anthropic, OpenAI, Google)
owner: builder
criticality: high
```
## Key Concepts
- **Cache-Control**: Anthropic `cache_control: {kind: "ephemeral"}`; TTL 5 min
- **Prefix Matching**: cache hit when prefix identical byte-a-byte
- **Minimum Tokens**: Anthropic >= 1024; OpenAI >= 1024 (auto)
- **Pricing Split**: write 1.25x base, read 0.1x (90% savings on hit)
## Strategy Phases
1. **Audit**: identify prompts with >50% static content
2. **Reorder**: static first (system > few-shot > RAG), dynamic last
```text
[Request] -> [Hash Prefix] -> [Cache Lookup]
                                   |
                         HIT: 0.1x cost, 85% faster
                         MISS: 1.25x cost, normal speed
                                   |
                             [Generate] -> [Response]
```
## Comparativo
| Provider | Min Tokens | Config | Write | Read | TTL |
|----------|-----------|--------|-------|------|-----|
| Anthropic | 1024 | Explicit | 1.25x | 0.1x | 5 min |
| OpenAI | 1024 | Automatic | 1.0x | 0.5x | 5-60 min |
| Google | 32768 | Explicit | 1.0x | 0.25x | config |

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)

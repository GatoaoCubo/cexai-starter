---
kind: quality_gate
id: p11_qg_content_factory
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of content_factory briefs and produced bundles
pattern: few-shot learning -- LLM reads these before producing
quality: null
title: "Gate: content_factory"
version: 1.0.0
author: n03_engineering
tags: [quality-gate, content-factory, P11, content-fabric, governance]
tldr: "Gates for content_factory artifacts -- grounding, fan-out completeness, approval birth-state, and publish-seam safety."
domain: content_factory
created: 2026-07-03
updated: 2026-07-03
8f: "F7_govern"
keywords: [grounding, fan-out completeness, approval birth-state, and publish-seam safety, quality-gate, content-factory, content-fabric, governance]
density_score: 1.0
related:
  - content-factory-builder
  - bld_schema_content_factory
---
## Quality Gate

# Gate: content_factory

## Definition
| Field | Value |
|-------|-------|
| Kind | content_factory |
| Pillar | P04 (tools) |
| Function | PRODUCE (grounded brief -> N-row fan-out) |
| Threshold | 8.0 minimum |

## HARD Gates (fail = reject)
| # | Gate | Check |
|---|------|-------|
| H1 | Brief completeness | `topic` non-empty AND at least one grounding source present (`source_facts` or `canonical`) |
| H2 | Grounding traceability | Every caption claim traces to `source_facts`/`topic`; zero BLOCKING findings (G3/G4/G5) |
| H3 | Channel matrix validity | Every channel_matrix entry maps to a VALID_FORMATS value; an invalid entry is skipped, never emitted as a row |
| H4 | UNIQUE row key | No two rows in a bundle share (post_id, channel, format) |
| H5 | Approval birth-state | Every row starts `approved=False`, `approved_by=None`, `approved_at=None`, `publish_status="pending"` |
| H6 | Hashtag cap compliance | Every row's hashtags <= its platform's cap (instagram 5, tiktok 30, linkedin 8, twitter 3, facebook 30, pinterest 20, threads 5; default 30) |
| H7 | Publish-seam fail-closed | No real provider wired; the seam refuses every publish (published=False, refused=True) |

## SOFT Gates (warn, don't reject)
| # | Gate | Check | Weight |
|---|------|-------|--------|
| S1 | Writes-nothing | The artifact documents `writes_nothing=True` -- no DB, no network I/O | 1.0 |
| S2 | A11y alt_text | Media rows (asset_type != text) carry non-empty `alt_text` | 0.7 |
| S3 | Canonical enrichment | When the post is about a product, `canonical` is folded into the grounding source via `source_text_of()` | 0.6 |
| S4 | Multi-channel fan-out | channel_matrix covers >= 2 channels (the pattern's intent) | 0.6 |
| S5 | Degrade-never documented | The artifact states the deterministic fallback behavior when no llm/engine is injected | 0.6 |
| S6 | post_group meaningful | `post_group` is set to a real grouping label, not left at the bare "content" default | 0.5 |

## Scoring Formula
```
score = (HARD_pass_count / 7) * 6.0 + (SOFT_weighted_sum / max_weight) * 4.0
```
All 7 HARD must pass for score >= 6.0. SOFT gates add up to 4.0 bonus.

## Quality Tiers
| Tier | Score | Meaning |
|------|-------|---------|
| REJECT | < 8.0 | Missing grounding traceability, malformed row, or a pre-approved row |
| PUBLISH | 8.0-8.9 | Bundle complete, grounded, review/publish handoffs correct |
| EXEMPLARY | 9.0+ | Multi-channel, a11y-complete, canonical-enriched, degrade-never proven |

## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | GOLDEN | Publish as exemplar |
| >= 8.0 | PUBLISH | Ready for runtime |
| >= 7.0 | REVIEW | Flag for review |
| < 7.0  | REJECT | Rework required |

## Bypass
| Field | Value |
|-------|-------|
| conditions | Experimental content_factory artifact under active A/B testing of a new channel |
| approver | Nucleus lead (written approval required) |
| audit_trail | Log in records/audits/ with bypass reason and timestamp |
| expiry | 48h -- must pass all gates before expiry |
| never_bypass | H01 (YAML parse), H05 (quality null), H2 (grounding), H5 (approval birth-state), H7 (fail-closed seam) |

## Examples

# Examples: content-factory-builder

## Golden Example -- Pet Shop
INPUT: "Produce a content bundle for a donut-shaped cat bed post, grounded only in the
product's real facts, across Instagram + Facebook + TikTok"
OUTPUT (deterministic path, no llm):
```yaml
brief:
  topic: "Cama donut para gatos"
  post_id: "w03_demo_cama"
  source_facts:
    - "Cama donut macia para gatos, feita em pelucia, com base antiderrapante."
    - "A borda alta em formato donut da seguranca ao gato."
    - "Lavavel na maquina."
rows: 8   # one per default channel; ig_feed clamped to 5 hashtags, x is text_only
grounding.ok: true
all_rows.approved: false
```
WHY GOOD: caption traces 1:1 to `source_facts`; every row born unapproved; hashtags
clamped per platform; zero network calls.

## Anti-Example -- Fabricated + Pre-Approved
```python
# BAD: the caption invents a claim absent from source_facts, and the row ships pre-approved
row = {
    "caption_text": "Suporta gatos de ate 12kg, tecido atoxico certificado",  # INVENTED (G3/G4/G5)
    "approved": True,      # NEVER pre-approved -- breaks H5
    "publish_status": "published",   # NEVER at birth -- breaks H5 + H7
}
```
WHY BAD: violates H2 (invented weight-capacity + safety claim), H5 (pre-approved at
birth), H7 (a row cannot be "published" without passing through the review gate AND a
real provider, which does not exist).

## Anti-Patterns (PRODUCE-side; test-proven in `tests/test_content_fabric.py`, 14/14 passing)

| # | Anti-pattern | Correct contract | Proving test |
|---|--------------|-------------------|----------------|
| A1 | Fabricating LLM injects "12kg"/"atoxico" absent from `source_facts` | G1-G10 gate DROPS the unsupported claim | `test_fabricating_llm_cannot_inject_facts` |
| A2 | A row arrives pre-approved, or an unapproved row reaches the seam | `submit()` STAMPS `approved=False`; only `approved_for_publish()` output may reach the seam | `test_submitted_content_cannot_arrive_pre_approved`, `test_unapproved_content_cannot_reach_the_seam` |
| A3 | Inline edit silently approves a row | `edit()` touches only `caption_text`/`alt_text`, never `approved` | `test_inline_edit_never_auto_approves` |
| A4 | Hashtags exceed the platform cap | `build_library_rows()` routes tags through `clamp_hashtags(tags, platform)` | `test_hashtags_clamped_per_platform` |
| A5 | The factory performs a network call or DB write | WRITES-NOTHING by construction -- zero network imports in source | `test_full_flow_makes_zero_network_calls` |
| A6 | A real provider arm gets wired into the seam | Seam ships ONLY `NoOpPublisher`; a real arm is SEPARATE + config-gated | `test_no_provider_arm_is_built` |

> Naming-collision caution: covers THIS kind's produce->review->publish trio only -- NOT
> the unrelated `cexai/cexai/content_factory/` VIDEO package (see the knowledge ISO).

## Exemplar Requirements

1. Score 9.0+ to qualify as few-shot reference
2. Demonstrate ideal structure for this artifact kind
3. Populate all frontmatter fields with realistic values
4. Use domain-specific content not generic placeholders
5. Enable retrieval via tags and TF-IDF matching

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)

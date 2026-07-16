---
kind: quality_gate
id: p11_qg_user_model
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of user_model artifacts
pattern: few-shot learning -- LLM reads these before producing
quality: null
title: "Gate: user_model"
version: "1.0.0"
author: "n03_builder"
tags: [quality-gate, user-model, P10, memory, honcho, dialectic]
tldr: "Pass/fail gate for user_model artifacts: id pattern, collections minimum, dialectic config, storage declaration, boundary clarity vs entity_memory/..."
domain: "user model -- cross-session dialectic peer representation implementing Honcho pattern"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F7_govern"
keywords: [id pattern, collections minimum, dialectic config, storage declaration, boundary clarity vs entity_memory, quality-gate, user-model]
density_score: 0.91
related:
  - user-model-builder
  - bld_schema_user_model
---
## Quality Gate

# Gate: user_model

## Definition
| Field | Value |
|---|---|
| metric | user_model artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: user_model` |

## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^um_[a-z][a-z0-9_]+$` | ID has hyphens, uppercase, or missing `um_` prefix |
| H03 | Tags >= 3 items, includes "user_model" and "honcho" | Fewer than 3 tags, or missing required tags |
| H04 | Kind equals literal `user_model` | `kind: entity_memory` or `kind: user_memory` or any other value |
| H05 | Quality field is null | `quality: 8.0` or any non-null value |
| H06 | All required fields present | Missing `peer_id`, `workspace`, `dialectic`, `collections`, `storage`, `retention` |

## SOFT Scoring
Weights sum to 100%.
| Dimension | Weight | Criteria |
|---|---|---|
| Collection completeness | 1.0 | >= 3 collections covering preferences, working_style, context_history (or equivalent) |
| Dialectic config quality | 1.0 | All 3 dialectic fields present with sensible values; compaction_cadence positive int |
| Storage declaration | 1.0 | primary + fallback_chain + pgvector_enabled all declared explicitly |
| Retention policy | 0.75 | messages_ttl_days and derived_facts_ttl_days both declared |
| API surface completeness | 1.0 | All 5 API methods documented with signatures |
| Peer profile quality | 0.75 | 2-sentence peer profile with workspace context |

## Actions
| Score | Tier | Action |
|---|---|---|
| >= 9.5 | Golden | Publish to pool as golden reference |
| >= 8.0 | Publish | Publish to pool, add to routing index |
| >= 7.0 | Review | Flag for improvement before publish |
| < 7.0 | Reject | Return to author with specific gate failures |

## Bypass
| Field | Value |
|---|---|
| conditions | Stub peer record for new user with no interaction history yet |
| approver | Author self-certification with "cold_start_stub" note in frontmatter |
| audit_trail | Bypass note with expected promotion date |
| expiry | 7d -- stubs must be populated from real interactions or removed |
| never_bypass | H01 (unparseable YAML), H05 (self-scored), H10 (wrong kind pollutes memory index) |

## Examples

# Examples: user-model-builder

## Golden Example 1 -- Developer User Model

INPUT: "Create user model for alice, developer who uses N07 orchestrator daily"
OUTPUT:
```yaml
id: um_alice_main
kind: user_model
pillar: P10
title: "User Model: alice"
peer_id: alice
workspace: cex_default
storage:
  primary: sqlite
```
### Peer Profile
alice is a senior developer and CEX architect who uses N07 daily for artifact orchestration.
Workspace: cex_default (single-tenant development environment).

### Collections

#### preferences
| Key | Value | Confidence | Last Updated |
|-----|-------|------------|--------------|
| response_language | PT-BR | 0.95 | 2026-04-18 |
| response_length | terse | 0.93 | 2026-04-18 |
| execution_mode | autonomous | 0.90 | 2026-04-18 |
| commit_style | descriptive_body | 0.88 | 2026-04-18 |

#### working_style
| Key | Value | Confidence | Last Updated |
|-----|-------|------------|--------------|
| domain_expertise | senior_developer | 0.97 | 2026-04-18 |
| orchestration_model | opus_tier | 0.92 | 2026-04-18 |
| polling_preference | 60s_intervals | 0.85 | 2026-04-18 |

#### context_history
| Session ID | Key Insight | Derived At |
|------------|-------------|-----------|
| ses_20260418_001 | User prefers parallel dispatch over sequential; confirms terse responses | 2026-04-18 |

WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches `^um_` pattern (H02 pass)
- kind: user_model (H04 pass)
- collections: 3 named groups (H07 pass)

---

## Golden Example 2 -- Customer Support User Model

INPUT: "Track customer alice_smith for support agent context"
OUTPUT:
```yaml
id: um_alice_smith
kind: user_model
pillar: P10
title: "User Model: alice_smith"
peer_id: alice_smith
workspace: support_prod
storage:
  primary: sqlite
```

WHY THIS IS GOLDEN:
- Workspace scoped (support_prod) -- multi-tenancy correct
- compaction_cadence_turns=20 (shorter for support context)
- Custom collections (support_history, product_context) -- domain-appropriate
- Retention policy restricted (180d messages) -- GDPR-conscious

---

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)

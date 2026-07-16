---
kind: quality_gate
id: p11_qg_context_map
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of context_map artifacts
pattern: few-shot learning -- LLM reads these before producing
quality: null
title: "Gate: context_map"
version: "1.0.0"
author: "builder_agent"
tags:
  - "quality-gate"
  - "context-map"
  - "P08"
  - "ddd"
  - "bounded-context"
tldr: "Pass/fail gate for context_map: id pattern, contexts table, relationships with DDD patterns, team coupling."
domain: "context map -- DDD BC relationship diagram"
created: "2026-04-17"
updated: "2026-04-17"
8f: "F7_govern"
keywords:
  - "fail gate for context_map"
  - "id pattern"
  - "contexts table"
  - "relationships with ddd patterns"
  - "team coupling"
  - "quality-gate"
  - "context-map"
density_score: 0.90
related:
  - bld_config_context_map
  - bld_knowledge_card_context_map
  - bld_output_template_context_map
  - bld_instruction_context_map
  - kc_context_map
---
## Quality Gate
# Gate: context_map
## Definition
| Field | Value |
|---|---|
| metric | context_map artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: context_map` |
## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^p08_cm_[a-z][a-z0-9_]+$` | ID contains uppercase, hyphens, or missing prefix |
| H03 | ID equals filename stem | id: p08_cm_foo but file is p08_cm_bar.md |
| H04 | Kind equals literal `context_map` | kind: architecture_diagram or any other value |
| H05 | Quality field is null | quality: 8.0 or any non-null value |
| H06 | All relationships have upstream, downstream, pattern | Missing any of these three fields |
## SOFT Scoring
| Dimension | Weight | Criteria |
|---|---|---|
| Pattern completeness | 1.0 | Every relationship has a valid DDD pattern |
| Integration type | 1.0 | sync/async/batch declared for all relationships |
| Team ownership | 1.0 | Owning team identified for each BC |
| Team coupling documented | 1.0 | Coupling level + risk + mitigation per relationship |
| ACL translation layers | 1.0 | ACL relationships identify the translator owner |
| OHS protocol reference | 1.0 | OHS relationships reference the published language/API |
## Actions
| Score | Tier | Action |
|---|---|---|
| >= 9.5 | Golden | Publish to pool as golden reference |
| >= 8.0 | Publish | Publish to pool, add to routing index |
| >= 7.0 | Review | Flag for improvement before publish |
| < 7.0 | Reject | Return to author with specific gate failures |
## Examples
# Examples: context-map-builder
## Golden Example
INPUT: "Map the bounded contexts in our e-commerce platform"
WHY THIS IS GOLDEN:
- id matches `^p08_cm_[a-z][a-z0-9_]+$` -- H02 pass
- contexts_count matches actual count -- H03 pass
- All 4 required sections present -- H06 pass
- Every relationship has pattern, upstream, downstream -- H05 pass
```yaml
id: p08_cm_ecommerce_platform
kind: context_map
pillar: P08
version: "1.0.0"
created: "2026-04-17"
updated: "2026-04-17"
author: "builder_agent"
system_name: "E-Commerce Platform"
contexts_count: 5
quality: null
tags: [context_map, ecommerce, ddd, strategic-design]
tldr: "E-commerce platform: 5 BCs. Orders->Inventory ACL, Payments OHS, Catalog Conformist to Search."
```
## Bounded Contexts
| Context | Team | Core Domain? | Description |
|---------|------|-------------|-------------|
| Orders | Order Team | YES | Order lifecycle: placement, fulfillment, cancellation |
| Inventory | Warehouse Team | YES | Stock levels, reservation, replenishment |
| Payments | Payment Team | YES | Payment processing, refunds, reconciliation |
| Catalog | Content Team | SUPPORTING | Product data, descriptions, pricing |
| Search | Platform Team | GENERIC | Search index, faceting, ranking |
## Relationships
| Upstream (U) | Downstream (D) | Pattern | Integration Type | Notes |
|-------------|----------------|---------|-----------------|-------|
| Inventory | Orders | ACL | sync | Orders wraps Inventory calls through ACL; protects Order model from Inventory changes |
| Payments | Orders | OHS | sync | Payments exposes formal Payment API; Orders consumes it without translation |
| Catalog | Search | Conformist | async | Search adopts Catalog product model directly via Kafka events |
| Orders | Payments | Customer/Supplier | sync | Orders team negotiates payment requirements with Payments team |
## Integration Details
| Relationship | Translation Layer | Protocol | Sync/Async |
|-------------|-----------------|----------|-----------|
| Inventory -> Orders ACL | OrderInventoryTranslator (Orders-owned) | REST | sync |
| Payments -> Orders OHS | PaymentAPI v2 (published language) | REST | sync |
| Catalog -> Search | EventBus (Kafka topic: catalog.product.updated) | Kafka | async |
| Orders -> Payments C/S | PaymentRequestDTO (negotiated schema) | REST | sync |
## Team Coupling
| Relationship | Coupling Level | Risk | Mitigation |
|-------------|----------------|------|-----------|
| Inventory -> Orders (ACL) | Low | Inventory changes isolated by ACL | ACL translator owned by Orders team |
| Payments -> Orders (OHS) | Low | Formal versioned API | Payments team owns API versioning |
| Catalog -> Search (CF) | High | Search breaks if Catalog schema changes | Add ACL if Catalog evolves independently |
| Orders -> Payments (C/S) | Medium | Orders blocked on Payments backlog | Regular sync meetings; SLA for requests |
---

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)

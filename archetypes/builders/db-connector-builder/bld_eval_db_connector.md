---
kind: quality_gate
id: p11_qg_connector
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of connector artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: connector"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, connector, P04, bidirectional, integration, data-transform]
tldr: "Pass/fail gate for connector artifacts: bidirectional flow coverage, transform rules, health check, and protocol selection rationale."
domain: "bidirectional service integration — connectors exchanging data with external services via REST, WebSocket, gRPC, or MQTT"
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
keywords: [bidirectional service integration, or mqtt, bidirectional flow coverage, transform rules, health check, and protocol selection rationale, quality-gate]
density_score: 0.92
related:
  - bld_schema_connector
  - p10_lr_connector_builder
  - db-connector-builder
  - bld_instruction_connector
  - bld_collaboration_connector
---
## Quality Gate

# Gate: connector

This ISO addresses the database connector domain: connection pooling, query execution, and SQL dialect handling.
## Definition
| Field | Value |
|---|---|
| metric | connector artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: db_connector` |
## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^[a-z][a-z0-9_-]+$` | ID contains uppercase, spaces, or invalid chars |
| H03 | ID equals filename stem | `id: my_connector` but file is `other_connector.md` |
| H04 | Kind equals literal `connector` | `kind: client` or `kind: integration` or any other value |
| H05 | Quality field is null | `quality: 8.0` or any non-null value |
| H06 | All required fields present | Missing `service`, `protocol`, or `auth_strategy` |
## SOFT Scoring
Weights sum to 100%.
| Dimension | Weight | Criteria |
|---|---|---|
| Inbound endpoint completeness | 1.0 | All data the system receives from the external service is documented |
| Outbound endpoint completeness | 1.0 | All data the system sends to the external service is documented |
| Transform rule precision | 1.0 | Field mappings specify source field, target field, and transformation logic |
| Auth strategy depth | 1.0 | Auth scheme covers token lifecycle, rotation, and failure handling |
| Health check actionability | 0.5 | Health check endpoint and expected response documented; failure action defined |
| Retry policy | 1.0 | Retry conditions, max attempts, backoff strategy defined per endpoint direction |
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
| conditions | Connector for a third-party service whose webhook schema changes without versioning — inbound schema unstable |
| approver | Integration owner with written acknowledgment of unstable upstream schema |
| audit_trail | Bypass reason, external service name, and schema instability report link in frontmatter comment |

## Examples

# Examples: db-connector-builder

This ISO addresses the database connector domain: connection pooling, query execution, and SQL dialect handling.
## Golden Example
INPUT: "Create connector for an e-commerce platform with order sync and webhook notifications"
OUTPUT:
```yaml
id: p04_conn_ecommerce_platform
kind: db_connector
pillar: P04
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder_agent"
name: "E-Commerce Platform Connector"
```
## Overview
Bidirectional REST connector for e-commerce platform: pushes orders and pulls products outbound, receives status and inventory webhooks inbound.
Used by fulfillment agents and inventory sync pipelines.
## Endpoints
### push_order (outbound)
POST /v2/orders — Push new order to platform.
Data shape:
- `order_id` (string): CEX order identifier
- `items` (list): Line items with sku, qty, price
- `shipping` (object): Address and method
### get_product (outbound)
GET /v2/products/{sku} — Fetch product details by SKU.
Data shape:
- `sku` (string): Product SKU identifier
### receive_status_webhook (inbound)
POST /webhooks/status — Receive order status updates from platform.
Data shape:
- `event_id` (string): Dedup key
- `order_id` (string): Platform order ID
- `status` (enum): pending, shipped, delivered, cancelled
### receive_inventory_webhook (inbound)
POST /webhooks/inventory — Receive inventory level changes.
Data shape:
- `event_id` (string): Dedup key
- `sku` (string): Product SKU
- `quantity` (integer): New stock level
## Data Mapping
Inbound (external -> CEX): platform.order_id -> cex.external_order_ref; status enum direct map
Outbound (CEX -> external): cex.price_cents / 100 -> platform.price; cex.iso_date -> platform.date
Idempotency: event_id dedup on inbound webhooks (store last 24h)
## Health & Errors
Health: GET /api/health every 60s, alert if 3 consecutive failures
- 400: Bad request — log and skip, no retry
- 401: OAuth expired — refresh token, retry once
- 429: Rate limited — backoff per Retry-After header
- 5xx: Server error — retry with exponential backoff
Circuit breaker: open after 5 consecutive 5xx in 60s, half-open after 120s
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p04_conn_ pattern (H02 pass)
- kind: db_connector (H04 pass)
- 22 required+recommended fields present (H06 pass)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)

---
quality: null
id: bld_rules_event_stream
kind: knowledge_card
pillar: P04
title: "Event Stream Builder -- Rules"
version: 1.0.0
quality: null
tags: [builder, event_stream, rules]
llm_function: COLLABORATE
author: builder
tldr: "Event Stream tools: workflow coordination, handoffs, and lifecycle management"
8f: "F3_inject"
keywords: [event stream tools, workflow coordination, and lifecycle management, builder, event_stream, rules, absolute rules, soft rules, boundary rules, specific rules]
density_score: 0.82
created: "2026-04-17"
updated: "2026-04-17"
related:
  - bld_rules_process_manager
  - bld_rules_value_object
  - bld_rules_aggregate_root
  - bld_rules_data_contract
  - bld_rules_constitutional_rule
---
# Rules: event_stream
## Absolute Rules (HARD -- never violate)
1. Partition key must be defined: never use round-robin for entity-ordered events.
2. Retention must include both time (hours) and bytes: one alone is incomplete.
3. Delivery semantics must be explicit: ambiguous delivery causes data loss or duplication.
4. Every consumer that needs independent offset tracking must be a separate consumer group.
5. Schema format must be specified: untyped event streams are a maintenance hazard.
6. quality: null always -- never self-score.
## Soft Rules (RECOMMEND)
1. Use BACKWARD compatibility mode by default: allows adding optional fields without breaking consumers.
2. Monitoring lag threshold should be <= 10% of expected throughput-to-processing ratio.
3. Retention: default 168 hours (7 days) unless replay requirements dictate more.
4. Partition count: right-size to throughput estimate, not maximum possible.
## Boundary Rules
1. THIS BUILDER handles: event_stream (P04)
2. NOT this builder: webhook (single outbound HTTP push) -> webhook-builder
3. NOT this builder: signal (internal CEX nucleus signal) -> not a user-facing kind
4. NOT this builder: process_manager (event routing + state machine) -> process-manager-builder
5. NOT this builder: api_client (HTTP consumer) -> api-client-builder
## CEX-Specific Rules
1. id pattern: p04_es_{slug} -- always prefix p04_es_
2. Pillar: always P04 (Tools)
3. Producing nucleus: N05 (Operations) for infra config, N03 for domain design
4. max_bytes: 3072

## Orchestration Checklist

- Verify workflow topology matches dependency graph
- Validate handoff protocol between upstream and downstream
- Cross-reference with dispatch rules for routing correctness
- Test wave sequencing with dry-run before live dispatch

## Orchestration Pattern

```yaml
# Workflow validation
topology: verified
handoffs: validated
routing: checked
sequencing: tested
```

```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_doctor.py --scope orchestration
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_rules_process_manager]] | sibling | 0.40 |
| [[bld_rules_value_object]] | sibling | 0.34 |
| [[bld_rules_aggregate_root]] | sibling | 0.31 |
| [[bld_rules_data_contract]] | downstream | 0.30 |
| [[bld_rules_constitutional_rule]] | sibling | 0.30 |

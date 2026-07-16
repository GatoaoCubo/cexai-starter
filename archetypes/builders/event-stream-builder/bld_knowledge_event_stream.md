---
id: bld_knowledge_card_event_stream
kind: knowledge_card
pillar: P04
title: "Event Stream Builder -- Knowledge Card"
version: 1.0.0
quality: null
tags: [builder, event_stream, knowledge]
llm_function: INJECT
author: builder
tldr: "Event Stream tools: domain knowledge, terminology, and contextual background"
8f: "F3_inject"
keywords: [event stream tools, domain knowledge, and contextual background, builder, event_stream, knowledge, core concept
event stream, azure event hub, key configuration dimensions, knowledge injection checklist]
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-17"
related:
  - bld_architecture_event_stream
---
# Knowledge: event_stream
## Core Concept
Event Stream is a configuration artifact for real-time ordered event feeds.
It specifies how domain events are published, partitioned, retained, and consumed.
Industry: Kafka topic, Kinesis stream, Azure Event Hub.
## When to Use
- Multiple consumers need the same domain events independently
- Events must be replayed (audit, reprocessing, new consumer catch-up)
- Order matters within an entity's events (user actions, order updates)
- Real-time processing at high throughput (>100 events/sec)
## When NOT to Use
- Single HTTP push to one endpoint: use webhook
- Internal CEX nucleus coordination: use signal
- One-time notification: use webhook or direct command
- Scheduled batch: use schedule
## Key Configuration Dimensions
1. Partitioning: determines parallelism and ordering scope
2. Retention: determines replay window (how far back consumers can read)
3. Delivery: determines consumer idempotency requirements
4. Consumer groups: each group reads independently with its own offset
5. Schema: determines event shape and evolution policy
## CEX Integration
- Pillar: P04 (Tools)
- Builder: event-stream-builder (13 ISOs)
- Related: webhook (P04), signal (internal), process_manager (P12)
- Produced by: N05 (Operations) or N03 (Engineering)
- max_bytes: 3072

## Knowledge Injection Checklist

- Verify domain facts are sourced and citable
- Validate density_score >= 0.85 (no filler content)
- Cross-reference with related KCs for consistency
- Check for outdated facts that need refresh

## Injection Pattern

```yaml
# KC injection at F3
source: verified
density: 0.85+
cross_refs: checked
freshness: current
```

```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_retriever.py --query "{DOMAIN}"
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_architecture_event_stream]] | sibling | 0.36 |

---
id: bld_output_template_event_stream
kind: output_template
pillar: P04
title: "Event Stream Builder -- Output Template"
version: 1.0.0
quality: null
tags: [builder, event_stream, template]
llm_function: PRODUCE
author: builder
8f: "F5_call"
keywords: [builder, event_stream, template, output template, event stream, consumer groups, offset policy, lag tolerance, latest earliest, avro protobuf]
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-17"
related:
  - bld_schema_event_stream
  - bld_memory_event_stream
---
# Output Template: event_stream
```yaml
---
id: p04_es_{slug}
kind: event_stream
pillar: P04
title: "Event Stream: {Name}"
version: 0.1.0
event_types:
  - "{DomainEvent1}"
  - "{DomainEvent2}"
producer: "{ServiceOrAggregate}"
consumer_groups:
  - name: "{GroupName}"
    offset_policy: "{latest|earliest|timestamp}"
    lag_tolerance: "{N events or M seconds}"
partition_key: "{fieldName (e.g., orderId)}"
partition_count: {N}
retention_hours: {N}
retention_bytes: "{N}GB"
delivery: "{at_most_once|at_least_once|exactly_once}"
schema_format: "{avro|protobuf|json_schema|json}"
schema_registry: "{URL or service name}"
compatibility_mode: "{FULL|BACKWARD|FORWARD|NONE}"
throughput_estimate: "{N} events/sec"
ordering_guarantee: "{global|per_partition|none}"
monitoring:
  lag_threshold: "{N events}"
  alert_on: [consumer_lag, producer_error, retention_exceeded]
quality: null
tags: [event_stream, {domain_slug}, P04]
tldr: "{Name} stream: {N} event types, {partition_count} partitions, {retention_hours}h retention, {delivery}"
---

## Producer
**Service**: {ProducerName}
**Throughput**: {estimate events/sec}
**Encoding**: {schema_format} + {schema_registry}

## Consumer Groups
| Group | Offset Policy | Lag Tolerance | Purpose |
|-------|--------------|---------------|---------|
| {GroupName} | {latest/earliest} | {N events/sec} | {purpose} |

## Partitioning
**Key**: `{fieldName}` -- ensures ordered processing per {entity}
**Count**: {N} partitions
**Ordering**: {per_partition/global/none}

## Retention
**Time**: {N} hours ({M} days)
**Bytes**: {N} GB
**Replay window**: consumers can seek back up to {retention_hours} hours

## Schema
**Format**: {avro/protobuf/json}
**Registry**: {registry_url}
**Compatibility**: {FULL/BACKWARD} -- {implication for schema evolution}

## Operations
**Lag SLA**: consumer lag < {N} events; alert if exceeded {duration}
**Producer errors**: alert on > {N}% error rate
```

## Output Template Checklist

- Verify output format matches target kind schema
- Validate all frontmatter fields are present in template
- Cross-reference with eval gate for completeness
- Test template rendering with sample data before publishing

## Output Pattern

```yaml
# Output validation
format_match: true
frontmatter_complete: true
eval_gate_aligned: true
sample_rendered: true
```

```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_doctor.py --scope {BUILDER}
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_event_stream]] | related | 0.54 |
| [[bld_memory_event_stream]] | related | 0.32 |

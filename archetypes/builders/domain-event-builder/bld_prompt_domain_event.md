---
quality: null
id: bld_instruction_domain_event
kind: instruction
pillar: P03
llm_function: REASON
purpose: Step-by-step production process for domain_event
version: 1.0.0
quality: null
tags: [domain_event, builder, instruction]
title: "Instruction Domain Event Builder"
author: builder
tldr: "Step-by-step production process for domain_event"
8f: "F6_produce"
keywords: [instruction domain event builder, domain_event, builder, instruction, prompt construction checklist, prompt pattern, related artifacts, past tense, payload fields, python tools]
density_score: 0.81
created: "2026-04-17"
updated: "2026-04-17"
related:
  - bld_schema_domain_event
  - bld_instruction_data_contract
  - bld_instruction_aggregate_root
  - bld_instruction_bounded_context
  - p01_kc_domain_event
---
# Instructions: How to Produce a domain_event
## Phase 1: IDENTIFY
1. Name the event in past tense: OrderPlaced, PaymentFailed, UserRegistered
2. Identify the aggregate root that owns this event (Order, Payment, User)
3. Identify the bounded context (sales, billing, identity)
4. Determine event version (start at v1, increment on schema change)
5. Check: is this truly domain-significant, not a system heartbeat or log entry?
## Phase 2: COMPOSE
1. Read bld_schema_domain_event.md for required fields
2. Set id: de_{aggregate}_{past_tense_verb}_{version} (snake_case)
3. Fill payload fields: all data carried by the event at occurrence time
4. Record causation_id (what caused this), correlation_id (saga/trace)
5. Set occurred_at as ISO-8601 UTC timestamp (do NOT use processed_at)
6. Set quality: null -- never self-score
## Phase 3: VALIDATE
1. HARD gates (all must pass):
   - id follows pattern de_{aggregate}_{verb}
   - kind == domain_event
   - quality == null
   - occurred_at is present and ISO-8601
   - aggregate_root is named
   - bounded_context is named
   - payload section present with >= 1 field
2. SOFT gates:
   - causation_id and correlation_id present for traceability
   - event is named in past tense
   - payload fields are typed (string, int, uuid, etc.)
   - consumers array lists subscribing contexts


## Prompt Construction Checklist

- Verify prompt follows target kind's instruction template
- Validate variable placeholders use standard naming convention
- Cross-reference with chain dependencies for context completeness
- Test prompt with sample input before publishing

## Prompt Pattern

```yaml
# Prompt validation
template_match: true
variables_valid: true
chain_refs_checked: true
sample_tested: true
```

```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_prompt_optimizer.py --check
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_domain_event]] | downstream | 0.39 |
| [[bld_instruction_data_contract]] | sibling | 0.38 |
| [[bld_instruction_aggregate_root]] | sibling | 0.37 |
| [[bld_instruction_bounded_context]] | sibling | 0.36 |
| [[p01_kc_domain_event]] | upstream | 0.35 |

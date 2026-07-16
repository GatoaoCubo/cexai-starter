---
quality: null
id: bld_instruction_bounded_context
kind: instruction
pillar: P03
llm_function: REASON
purpose: Step-by-step production process for bounded_context
version: 1.0.0
quality: null
tags: [bounded_context, builder, instruction]
title: "Instruction Bounded Context Builder"
author: builder
tldr: "Step-by-step production process for bounded_context"
8f: "F6_produce"
keywords: [instruction bounded context builder, bounded_context, builder, instruction, corruption layer, open host service, prompt construction checklist, prompt pattern, related artifacts, integration patterns]
density_score: 0.84
created: "2026-04-17"
updated: "2026-04-17"
related:
  - bld_instruction_domain_vocabulary
  - bounded-context-builder
  - bld_instruction_aggregate_root
  - bld_instruction_domain_event
  - bld_instruction_data_contract
---
# Instructions: How to Produce a bounded_context
## Phase 1: SCOPE
1. Name the bounded context (noun phrase from domain language, not tech terms)
2. Write the scope statement: what domain model applies HERE (not in other BCs)
3. Identify the team/squad that owns this context
4. List the key aggregates and their relationships within this BC
5. Identify neighboring BCs and their integration patterns
## Phase 2: COMPOSE
1. Read bld_schema_bounded_context.md for required fields
2. Set id: bc_{context_name} (snake_case, domain language)
3. Set domain_vocabulary reference (dv_{context}_vocabulary.md)
4. Document integration patterns with neighboring contexts:
   - ACL (Anti-Corruption Layer): protecting this BC from upstream model
   - OHS (Open Host Service): publishing a public API for consumers
   - CF (Conformist): adopting upstream model as-is
5. Set quality: null -- never self-score
## Phase 3: VALIDATE
1. HARD gates:
   - id follows pattern bc_{context}
   - kind == bounded_context
   - quality == null
   - scope_statement present (what model applies here)
   - team_owner present
   - >= 1 aggregate listed
2. SOFT gates:
   - domain_vocabulary reference present
   - integration patterns documented with rationale
   - upstream_contexts and downstream_contexts listed
   - key invariants stated (business rules that hold within this BC)


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
| [[bld_instruction_domain_vocabulary]] | sibling | 0.38 |
| [[bounded-context-builder]] | downstream | 0.37 |
| [[bld_instruction_aggregate_root]] | sibling | 0.33 |
| [[bld_instruction_domain_event]] | sibling | 0.33 |
| [[bld_instruction_data_contract]] | sibling | 0.33 |
